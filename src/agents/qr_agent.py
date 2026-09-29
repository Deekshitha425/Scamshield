"""
QR Agent — decodes a QR code (given as an image path or an already-decoded
string) and hands the resulting payload to the URL/Domain agent, since a
malicious QR code is almost always just a URL in disguise.
"""
from __future__ import annotations
from src.agents.schemas import CaseState, Evidence
from src.agents import url_agent

try:
    from pyzbar.pyzbar import decode as _zbar_decode
    from PIL import Image
    _HAS_ZBAR = True
except ImportError:
    _HAS_ZBAR = False


def run(state: CaseState) -> CaseState:
    decoded_text = _decode_qr(state.raw_input)

    if decoded_text is None:
        state.evidence.append(
            Evidence(source="qr_agent", signal="qr_decode_failed", value="", confidence=0.2)
        )
        return state

    state.evidence.append(
        Evidence(source="qr_agent", signal="qr_decoded_payload", value=decoded_text, confidence=0.9)
    )

    # Hand the decoded payload to the URL agent by temporarily swapping raw_input.
    original_input = state.raw_input
    state.raw_input = decoded_text
    state = url_agent.run(state)
    state.raw_input = original_input
    return state


def _decode_qr(raw_input: str) -> str | None:
    """
    If raw_input looks like an image file path, decode it with pyzbar.
    If it's already plain text (e.g. the frontend decoded it client-side),
    just pass it through. Returns None if decoding isn't possible.
    """
    if raw_input.lower().endswith((".png", ".jpg", ".jpeg")):
        if not _HAS_ZBAR:
            return None
        try:
            image = Image.open(raw_input)
            results = _zbar_decode(image)
            return results[0].data.decode("utf-8") if results else None
        except Exception:
            return None
    # Already-decoded text passed in directly.
    return raw_input if raw_input.strip() else None
