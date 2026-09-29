from src.agents.schemas import CaseState, Evidence, Verdict
from src.agents import judge_agent


def _make_state_with_evidence(evidence_list):
    state = CaseState(raw_input="test")
    state.evidence = evidence_list
    return state


def test_agreeing_evidence_yields_scam_verdict(monkeypatch):
    # Avoid hitting the real vector store if the sufficiency loop ever retries.
    monkeypatch.setattr(judge_agent, "_retrieve_more_evidence", lambda state: None)

    evidence = [
        Evidence(source="url_agent", signal="domain_age_days", value="2", supports_scam=True, confidence=0.7),
        Evidence(source="url_agent", signal="safe_browsing_flagged", value="True", supports_scam=True, confidence=0.9),
        Evidence(source="content_agent", signal="urgency", value="high", supports_scam=True, confidence=0.8),
    ]
    state = _make_state_with_evidence(evidence)
    result = judge_agent.run(state)

    assert result.verdict == Verdict.SCAM
    assert result.sufficient_evidence is True


def test_conflicting_evidence_with_no_more_rounds_flags_human_review(monkeypatch):
    monkeypatch.setattr(judge_agent, "_retrieve_more_evidence", lambda state: None)

    evidence = [
        Evidence(source="url_agent", signal="domain_age_days", value="2000", supports_scam=False, confidence=0.7),
        Evidence(source="content_agent", signal="urgency", value="high", supports_scam=True, confidence=0.8),
    ]
    state = _make_state_with_evidence(evidence)
    # Force the retrieval cap to 0 so the loop can't retry — isolates the
    # "insufficient evidence -> human review" fallback behavior.
    from src.config import settings
    original_cap = settings.max_retrieval_rounds
    settings.max_retrieval_rounds = 0
    try:
        result = judge_agent.run(state)
    finally:
        settings.max_retrieval_rounds = original_cap

    assert result.verdict == Verdict.NEEDS_HUMAN_REVIEW
    assert result.sufficient_evidence is False


def test_judge_never_exceeds_max_retrieval_rounds(monkeypatch):
    calls = {"count": 0}

    def fake_retrieve(state):
        calls["count"] += 1

    monkeypatch.setattr(judge_agent, "_retrieve_more_evidence", fake_retrieve)

    # Only one weak, inconclusive piece of evidence -> never becomes "sufficient".
    evidence = [Evidence(source="content_agent", signal="unclear", value="", supports_scam=None)]
    state = _make_state_with_evidence(evidence)

    from src.config import settings
    result = judge_agent.run(state)

    assert calls["count"] <= settings.max_retrieval_rounds
    assert result.verdict == Verdict.NEEDS_HUMAN_REVIEW
