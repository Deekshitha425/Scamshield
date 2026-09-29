"""
Explainer Agent — this is the actual point of the project. Converts the
Judge's verdict and evidence into a plain-language, action-oriented
explanation for a non-technical reader, instead of a terse technical label.
"""
from __future__ import annotations
from src.agents.schemas import CaseState, Verdict
from src.agents.llm_client import llm_complete

SYSTEM_PROMPT = """You are explaining a scam-detection result to someone with
no technical background — imagine explaining it to a family member who has
never heard the word "phishing." Rules:
- No jargon. Never say things like "SPF failure", "domain age", or "confidence score".
- Say clearly whether the message is safe or dangerous.
- Say exactly what the person should do next, in one or two sentences.
- Keep the whole explanation under 80 words.
"""


def run(state: CaseState) -> CaseState:
    if state.verdict == Verdict.NEEDS_HUMAN_REVIEW:
        state.explanation = (
            "We couldn't confidently tell whether this message is safe or a scam. "
            "To be safe, don't click any links or share any personal information "
            "until someone you trust has taken a look at it."
        )
        return state

    evidence_summary = "; ".join(f"{e.signal}: {e.value}" for e in state.evidence[:6])
    user_prompt = (
        f"Verdict: {state.verdict.value}\n"
        f"Evidence found: {evidence_summary}\n"
        f"Explain this result to a non-technical user."
    )
    state.explanation = llm_complete(SYSTEM_PROMPT, user_prompt, max_tokens=200)
    return state
