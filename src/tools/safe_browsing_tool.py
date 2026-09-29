"""Google Safe Browsing lookup — free-tier API, real threat-list evidence."""
from __future__ import annotations
import requests
from src.config import settings

_API_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"


def is_flagged(url: str) -> bool | None:
    """Returns True if flagged, False if clean, None if the lookup failed."""
    if not settings.safe_browsing_key:
        return None
    body = {
        "client": {"clientId": "scamshield", "clientVersion": "0.1.0"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        resp = requests.post(
            _API_URL, params={"key": settings.safe_browsing_key}, json=body, timeout=10
        )
        resp.raise_for_status()
        return bool(resp.json().get("matches"))
    except Exception:
        return None
