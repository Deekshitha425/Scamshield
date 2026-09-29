"""
Content Agent — looks for linguistic scam patterns (urgency, credential
requests, impersonation cues) in the raw text. Runs on every input type,
since even a URL-only submission may carry a caption or surrounding text.
"""
from __future__ import annotations
from src.agents.schemas import CaseState, Evidence
from src.agents.llm_client import llm_complete

SYSTEM_PROMPT = """You are a content-pattern analyst for a scam-detection system.
Given a message, identify whether it uses common scam tactics: urgency
("act now", "account will be closed"), credential/OTP requests, brand
impersonation, or too-good-to-be-true offers. Respond in this exact format:

SUPPORTS_SCAM: yes|no|unclear
CONFIDENCE: 0.0-1.0
SIGNAL: <one short phrase naming the strongest pattern found, or "none">
"""


def run(state: CaseState) -> CaseState:
    response = llm_complete(SYSTEM_PROMPT, state.raw_input)
    supports_scam, confidence, signal = _parse(response)

    state.evidence.append(
        Evidence(
            source="content_agent",
            signal=signal,
            value=response.strip(),
            supports_scam=supports_scam,
            confidence=confidence,
        )
    )
    return state


def _parse(response: str) -> tuple[bool | None, float, str]:
    """Parse the constrained LLM output format. Falls back safely if malformed."""
    supports_scam = None
    confidence = 0.5
    signal = "unparsed"
    for line in response.splitlines():
        line = line.strip()
        if line.upper().startswith("SUPPORTS_SCAM:"):
            val = line.split(":", 1)[1].strip().lower()
            supports_scam = {"yes": True, "no": False}.get(val)
        elif line.upper().startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.upper().startswith("SIGNAL:"):
            signal = line.split(":", 1)[1].strip()
    return supports_scam, confidence, signal
