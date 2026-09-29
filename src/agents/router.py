"""
Dynamic Agent Router — classifies the raw input type and decides which
evidence agents actually need to run, instead of invoking every agent on
every input (the design flaw this project explicitly avoids).
"""
from __future__ import annotations
import re
from src.agents.schemas import CaseState, InputType

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_QR_HINT_RE = re.compile(r"qr[-_ ]?code", re.IGNORECASE)
_EMAIL_HEADER_RE = re.compile(r"^(from|subject|to):", re.IGNORECASE | re.MULTILINE)


def detect_input_type(raw_input: str) -> InputType:
    """Best-effort detection of what kind of content was submitted."""
    if _QR_HINT_RE.search(raw_input):
        return InputType.QR
    if _EMAIL_HEADER_RE.search(raw_input):
        return InputType.EMAIL
    if _URL_RE.search(raw_input) and len(raw_input.strip()) < 300:
        return InputType.URL
    if len(raw_input.strip()) > 0:
        return InputType.SMS
    return InputType.UNKNOWN


def route(state: CaseState) -> list[str]:
    """
    Return the list of evidence-agent names that should run for this input.
    This is the core of "dynamic routing" — QR agent never runs on plain
    text, URL/domain agent never runs unless a URL is actually present.
    """
    state.input_type = detect_input_type(state.raw_input)
    agents_to_run = ["content_agent"]  # content signals are always relevant

    if state.input_type == InputType.EMAIL:
        agents_to_run.append("email_agent")
    if state.input_type in (InputType.URL, InputType.QR) or _URL_RE.search(state.raw_input):
        agents_to_run.append("url_agent")
    if state.input_type == InputType.QR:
        agents_to_run.append("qr_agent")

    return agents_to_run
