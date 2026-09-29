from src.agents.router import detect_input_type, route
from src.agents.schemas import CaseState, InputType


def test_detects_email():
    text = "From: bank@example.com\nSubject: Verify your account\nClick here."
    assert detect_input_type(text) == InputType.EMAIL


def test_detects_url_only():
    text = "http://suspicious-link.tk/verify"
    assert detect_input_type(text) == InputType.URL


def test_detects_qr_hint():
    text = "Scan this qr code to claim your prize"
    assert detect_input_type(text) == InputType.QR


def test_detects_sms_fallback():
    text = "Your UPI PIN has been used. Reply STOP to cancel."
    assert detect_input_type(text) == InputType.SMS


def test_router_only_invokes_relevant_agents():
    state = CaseState(raw_input="Just checking in, are we still on for lunch?")
    agents = route(state)
    assert "content_agent" in agents
    assert "url_agent" not in agents
    assert "qr_agent" not in agents
    assert "email_agent" not in agents


def test_router_invokes_url_agent_when_link_present():
    state = CaseState(raw_input="Verify now at http://fake-bank.tk")
    agents = route(state)
    assert "url_agent" in agents
