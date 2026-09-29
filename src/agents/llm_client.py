"""
Thin LLM client wrapper so agents don't care which provider is configured.
Uses Groq's free-tier API (Llama / gpt-oss models) — agents call
`llm_complete()` and never touch the provider HTTP details directly.
"""
from __future__ import annotations
import re
import time
import requests
from src.config import settings

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_MAX_RETRIES = 5


def llm_complete(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
    """Send a single-turn completion request to Groq, retrying on rate limits."""
    api_key = settings.groq_api_key.strip().strip('"').strip("'")
    model = settings.groq_model.strip().strip('"').strip("'")
    if not api_key:
        raise RuntimeError(
            "No LLM provider configured. Set GROQ_API_KEY in .env "
            "(get a free key at https://console.groq.com/keys)"
        )
    return _call_groq(api_key, model, system_prompt, user_prompt, max_tokens)


def _call_groq(api_key: str, model: str, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if model.startswith("openai/gpt-oss"):
        # gpt-oss are reasoning models: keep thinking short and leave token
        # headroom so the visible answer isn't cut off / empty.
        payload["reasoning_effort"] = "low"
        payload["max_tokens"] = max_tokens + 1000

    for attempt in range(_MAX_RETRIES):
        resp = requests.post(
            _GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=60,
        )
        if resp.status_code == 429 and attempt < _MAX_RETRIES - 1:
            wait_s = _parse_retry_after(resp)
            time.sleep(wait_s)
            continue
        if not resp.ok:
            raise RuntimeError(f"Groq API error {resp.status_code} (model='{model}'): {resp.text}")
        content = resp.json()["choices"][0]["message"].get("content") or ""
        if not content.strip():
            raise RuntimeError(f"Groq returned an empty answer (model='{model}'). Try raising max_tokens.")
        return content

    raise RuntimeError(f"Groq rate limit persisted after {_MAX_RETRIES} retries (model='{model}').")


def _parse_retry_after(resp: requests.Response) -> float:
    """Wait as long as Groq's error/header says, plus a safety margin."""
    header = resp.headers.get("retry-after")
    if header:
        try:
            return float(header) + 0.5
        except ValueError:
            pass
    match = re.search(r"try again in ([\d.]+)s", resp.text)
    if match:
        return float(match.group(1)) + 0.5
    return 5.0  # fallback if Groq doesn't say