"""
URL / Domain Agent — gathers real, tool-based evidence about any URL found
in the input: domain age (WHOIS), Google Safe Browsing verdict, VirusTotal
reputation. This agent never asks the LLM to "guess" about a domain — it
only reports what the tools actually returned; the Judge decides what it means.
"""
from __future__ import annotations
import re
from src.agents.schemas import CaseState, Evidence
from src.tools import whois_tool, safe_browsing_tool, virustotal_tool

_URL_RE = re.compile(r"https?://[^\s\)\]\"']+")


def run(state: CaseState) -> CaseState:
    urls = _URL_RE.findall(state.raw_input)
    if not urls:
        state.evidence.append(
            Evidence(source="url_agent", signal="no_url_found", value="", confidence=1.0)
        )
        return state

    for url in urls[:3]:  # cap to avoid excessive tool calls on pathological input
        age_days = whois_tool.domain_age_days(url)
        state.evidence.append(
            Evidence(
                source="url_agent",
                signal="domain_age_days",
                value=str(age_days) if age_days is not None else "unknown",
                supports_scam=(age_days < 30) if age_days is not None else None,
                confidence=0.7 if age_days is not None else 0.3,
                raw={"url": url},
            )
        )

        sb_flagged = safe_browsing_tool.is_flagged(url)
        state.evidence.append(
            Evidence(
                source="url_agent",
                signal="safe_browsing_flagged",
                value=str(sb_flagged),
                supports_scam=sb_flagged,
                confidence=0.9 if sb_flagged is not None else 0.2,
                raw={"url": url},
            )
        )

        vt_score = virustotal_tool.malicious_vote_ratio(url)
        state.evidence.append(
            Evidence(
                source="url_agent",
                signal="virustotal_malicious_ratio",
                value=f"{vt_score:.2f}" if vt_score is not None else "unknown",
                supports_scam=(vt_score > 0.1) if vt_score is not None else None,
                confidence=0.8 if vt_score is not None else 0.2,
                raw={"url": url},
            )
        )

    return state
