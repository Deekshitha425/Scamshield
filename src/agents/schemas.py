"""Shared data structures passed between agents in the graph."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class InputType(str, Enum):
    EMAIL = "email"
    URL = "url"
    SMS = "sms"
    QR = "qr"
    UNKNOWN = "unknown"


class Verdict(str, Enum):
    LEGITIMATE = "legitimate"
    SCAM = "scam"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


@dataclass
class Evidence:
    """A single piece of evidence produced by one evidence agent."""
    source: str            # e.g. "url_domain_agent", "content_agent"
    signal: str             # short label, e.g. "domain_age_days"
    value: str               # human-readable value, e.g. "2"
    supports_scam: Optional[bool] = None   # None = inconclusive
    confidence: float = 0.5
    raw: Optional[dict] = None


@dataclass
class RetrievedExample:
    """A similar example pulled from the RAG corpus (scam or legitimate)."""
    text: str
    similarity: float
    source: str
    label: str = "scam"  # "scam" | "legitimate" — back-compat default for old corpora


@dataclass
class CaseState:
    """The full state object that flows through the agent graph."""
    raw_input: str
    input_type: InputType = InputType.UNKNOWN
    evidence: list[Evidence] = field(default_factory=list)
    retrieved_examples: list[RetrievedExample] = field(default_factory=list)
    retrieval_rounds_used: int = 0
    verification_notes: str = ""
    sufficient_evidence: bool = False
    confidence_score: float = 0.0
    verdict: Verdict = Verdict.NEEDS_HUMAN_REVIEW
    explanation: str = ""
    agents_to_run: list[str] = field(default_factory=list)