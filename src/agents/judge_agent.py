"""
Judge / Meta-Reasoning Agent — the core of this project's architecture.

Owns two responsibilities as a single, non-redundant process (see
docs/architecture.md for why these are NOT split into separate agents):

  1. Evidence Verification — do the collected evidence signals agree?
  2. Sufficiency Check — is there enough evidence to decide confidently?
     If not, retrieve more from the RAG corpus (sufficiency-gated,
     Self-RAG / Corrective RAG style), capped at MAX_RETRIEVAL_ROUNDS.
     If still insufficient after the cap, the Judge does NOT force a
     verdict — it flags the case for human review instead.
"""
from __future__ import annotations
from src.agents.schemas import CaseState, Evidence, Verdict
from src.rag.retriever import retrieve_similar_scams
from src.config import settings

# Below this ratio of agreeing signals, evidence is considered "conflicting".
_AGREEMENT_THRESHOLD = 0.6
# Below this many *conclusive* opinions (not just evidence items — see
# _is_sufficient), evidence is considered "insufficient".
_MIN_EVIDENCE_COUNT = 1
# Only trust a retrieved neighbor enough to vote if it's at least this similar.
_RETRIEVAL_SIMILARITY_THRESHOLD = 0.5


def run(state: CaseState) -> CaseState:
    while True:
        agreement_ratio, conflict_notes = _verify_evidence(state)
        state.verification_notes = conflict_notes

        if _is_sufficient(state, agreement_ratio):
            state.sufficient_evidence = True
            break

        if state.retrieval_rounds_used >= settings.max_retrieval_rounds:
            state.sufficient_evidence = False
            break

        _retrieve_more_evidence(state)
        state.retrieval_rounds_used += 1

    state.verdict = _decide_verdict(state, agreement_ratio if state.sufficient_evidence else 0.0)
    return state


def _verify_evidence(state: CaseState) -> tuple[float, str]:
    """
    Cross-source Evidence Verification. Returns the fraction of evidence
    points that agree with the majority direction, plus a human-readable
    note about any conflict found — this is what makes disagreement
    visible instead of silently averaged away.
    """
    opinions = [e.supports_scam for e in state.evidence if e.supports_scam is not None]
    if not opinions:
        return 0.0, "No conclusive evidence signals yet."

    scam_votes = sum(1 for o in opinions if o)
    legit_votes = sum(1 for o in opinions if not o)
    majority = max(scam_votes, legit_votes)
    agreement_ratio = majority / len(opinions)

    if agreement_ratio < _AGREEMENT_THRESHOLD:
        note = (
            f"Conflicting evidence: {scam_votes} signal(s) suggest scam, "
            f"{legit_votes} suggest legitimate. Treating as unresolved disagreement."
        )
    else:
        note = f"Evidence agrees: {majority}/{len(opinions)} signals point the same direction."

    return agreement_ratio, note


def _is_sufficient(state: CaseState, agreement_ratio: float) -> bool:
    # Count only CONCLUSIVE opinions (supports_scam is not None). An
    # inconclusive lookup (e.g. WHOIS/VirusTotal with no key/network) must
    # not count toward "enough evidence" just by existing.
    conclusive_count = sum(1 for e in state.evidence if e.supports_scam is not None)
    has_enough_evidence = conclusive_count >= _MIN_EVIDENCE_COUNT
    has_clear_agreement = agreement_ratio >= _AGREEMENT_THRESHOLD
    return has_enough_evidence and has_clear_agreement


def _retrieve_more_evidence(state: CaseState) -> None:
    """The sufficiency-gated retrieval step — only runs when the Judge
    decides current evidence isn't enough, not on every case.

    Turns retrieved neighbors into an actual evidence vote (majority
    label among similar-enough examples), instead of only storing them
    for display. Without this, retrieval could spin up to the round cap
    and never change the outcome."""
    examples = retrieve_similar_scams(state.raw_input, top_k=3)
    state.retrieved_examples.extend(examples)

    relevant = [e for e in examples if e.similarity >= _RETRIEVAL_SIMILARITY_THRESHOLD]
    if not relevant:
        return  # nothing similar enough to vote on this round

    scam_votes = sum(1 for e in relevant if e.label == "scam")
    legit_votes = len(relevant) - scam_votes
    avg_similarity = sum(e.similarity for e in relevant) / len(relevant)
    state.evidence.append(Evidence(
        source="rag_retriever",
        signal="similar_known_examples",
        value=f"{scam_votes} scam-like / {legit_votes} legitimate-like among {len(relevant)} similar examples",
        supports_scam=(scam_votes > legit_votes) if scam_votes != legit_votes else None,
        confidence=avg_similarity,
    ))


def _decide_verdict(state: CaseState, agreement_ratio: float) -> Verdict:
    if not state.sufficient_evidence:
        return Verdict.NEEDS_HUMAN_REVIEW

    scam_signals = sum(1 for e in state.evidence if e.supports_scam)
    legit_signals = sum(1 for e in state.evidence if e.supports_scam is False)

    if scam_signals > legit_signals:
        return Verdict.SCAM
    if legit_signals > scam_signals:
        return Verdict.LEGITIMATE
    return Verdict.NEEDS_HUMAN_REVIEW