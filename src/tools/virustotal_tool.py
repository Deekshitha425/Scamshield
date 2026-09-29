"""
VirusTotal URL reputation lookup. Free tier is rate-limited to ~4
requests/minute — batch evaluation runs accordingly (see docs/evaluation_plan.md).
"""
from __future__ import annotations
import base64
import requests
from src.config import settings

_API_URL = "https://www.virustotal.com/api/v3/urls/{url_id}"


def malicious_vote_ratio(url: str) -> float | None:
    """Returns the fraction of AV engines flagging the URL as malicious, or None."""
    if not settings.virustotal_key:
        return None
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        resp = requests.get(
            _API_URL.format(url_id=url_id),
            headers={"x-apikey": settings.virustotal_key},
            timeout=10,
        )
        resp.raise_for_status()
        stats = resp.json()["data"]["attributes"]["last_analysis_stats"]
        total = sum(stats.values())
        return stats.get("malicious", 0) / total if total else None
    except Exception:
        return None
