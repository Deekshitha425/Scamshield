"""Streamlit frontend for ScamShield — forward a message/URL, get a plain-language verdict."""
import requests
import streamlit as st

API_URL = "http://localhost:8000/analyze"

st.set_page_config(page_title="ScamShield", page_icon="🛡️")
st.title("🛡️ ScamShield")
st.caption(
    "Paste a suspicious email, SMS, URL, or UPI message below, or upload a QR code image. "
    "We'll explain what we find in plain language."
)

text_tab, qr_tab = st.tabs(["✍️ Text / URL / SMS / Email", "📷 QR code image"])

content_to_check = None

with text_tab:
    user_input = st.text_area("Paste the message or link here", height=180, key="text_input")
    if st.button("Check this", type="primary", key="check_text") and user_input.strip():
        content_to_check = user_input

with qr_tab:
    qr_image = st.file_uploader("Upload a QR code image", type=["png", "jpg", "jpeg"])
    if qr_image is not None:
        st.image(qr_image, caption="Uploaded QR code", width=200)
    if st.button("Check this QR code", type="primary", key="check_qr") and qr_image is not None:
        try:
            from pyzbar.pyzbar import decode as zbar_decode
            from PIL import Image

            decoded = zbar_decode(Image.open(qr_image))
            if not decoded:
                st.error("Couldn't read a QR code in that image. Try a clearer photo or screenshot.")
                st.stop()
            content_to_check = decoded[0].data.decode("utf-8")
            st.caption(f"Decoded QR content: `{content_to_check}`")
        except ImportError:
            st.error(
                "QR decoding isn't installed. Run: pip install pyzbar Pillow "
                "(Windows also needs the Visual C++ Redistributable for the zbar DLL)."
            )
            st.stop()

if content_to_check:
    with st.spinner("Checking..."):
        try:
            response = requests.post(API_URL, json={"content": content_to_check}, timeout=60)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Couldn't reach the analysis service: {e}")
            st.stop()

    verdict = result["verdict"]
    if verdict == "scam":
        st.error("⚠️ This looks like a scam.")
    elif verdict == "legitimate":
        st.success("✅ This looks legitimate.")
    else:
        st.warning("🤔 We're not confident either way — please have someone review this.")

    st.write(result["explanation"])

    with st.expander("Technical details (for reference)"):
        st.write(f"Confidence score: {result['confidence']}")
        st.write(f"Evidence points gathered: {result['evidence_count']}")
        st.write(f"Retrieval rounds used: {result['retrieval_rounds_used']}")

st.divider()
st.caption(
    "ScamShield is a research prototype. When in doubt, don't click links or share "
    "personal information, and ask someone you trust."
)
