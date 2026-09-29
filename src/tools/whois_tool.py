"""WHOIS-based domain age lookup — real evidence, not LLM guesswork."""
from __future__ import annotations
from datetime import datetime, timezone
import tldextract


def domain_age_days(url: str) -> int | None:
    """
    Returns the domain's age in days, or None if the lookup fails.
    Requires the `python-whois` package and network access.
    """
    try:
        import whois  # python-whois

        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        record = whois.whois(domain)
        creation_date = record.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date is None:
            return None
        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - creation_date).days
    except Exception:
        # WHOIS lookups fail often (rate limits, privacy-protected records,
        # network issues) — return None rather than raising, so the Judge
        # simply treats this as an inconclusive signal.
        return None
