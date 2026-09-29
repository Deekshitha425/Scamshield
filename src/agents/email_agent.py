"""
Email Agent — inspects header-style fields present in a submitted email
(From/Subject/To lines) for spoofing hints. This is a lightweight,
rule-based pass; SPF/DKIM verification against a live mail server is out
of scope for a forwarded-text submission and is noted as a limitation.
"""
from __future__ import annotations
import re
from src.agents.schemas import CaseState, Evidence

_FROM_RE = re.compile(r"^From:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_DISPLAY_NAME_MISMATCH_RE = re.compile(r'"?([\w .]+)"?\s*<([^>]+)>')


def run(state: CaseState) -> CaseState:
    from_match = _FROM_RE.search(state.raw_input)
    if not from_match:
        state.evidence.append(
            Evidence(source="email_agent", signal="no_from_header", value="", confidence=0.3)
        )
        return state

    from_line = from_match.group(1).strip()
    name_match = _DISPLAY_NAME_MISMATCH_RE.search(from_line)

    if name_match:
        display_name, address = name_match.group(1).strip(), name_match.group(2).strip()
        mismatch = _looks_like_brand_mismatch(display_name, address)
        state.evidence.append(
            Evidence(
                source="email_agent",
                signal="display_name_address_mismatch",
                value=f"{display_name} <{address}>",
                supports_scam=mismatch,
                confidence=0.6,
            )
        )
    else:
        state.evidence.append(
            Evidence(source="email_agent", signal="from_header_present", value=from_line, confidence=0.4)
        )

    return state


def _looks_like_brand_mismatch(display_name: str, address: str) -> bool:
    """Very simple heuristic: does a well-known brand name in the display
    name fail to appear in the actual sending domain? Extend this list as
    the RAG corpus grows with more regional brand-impersonation examples."""
    known_brands = ["bank", "amazon", "paypal", "microsoft", "google", "irs", "upi"]
    lowered_name = display_name.lower()
    lowered_addr = address.lower()
    for brand in known_brands:
        if brand in lowered_name and brand not in lowered_addr:
            return True
    return False
