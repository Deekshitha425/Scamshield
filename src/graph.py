"""
Orchestration graph — wires Router -> Evidence Agents -> Judge -> Calibration
-> Explainer using LangGraph, implementing the dynamic routing described in
docs/architecture.md. This is the single entry point the API/frontend calls.
"""
from __future__ import annotations
from langgraph.graph import StateGraph, END
from src.agents.schemas import CaseState
from src.agents import router, email_agent, url_agent, qr_agent, content_agent, judge_agent, explainer_agent
from src.agents.calibration import ConfidenceCalibrator, calibrate

_AGENT_FUNCS = {
    "email_agent": email_agent.run,
    "url_agent": url_agent.run,
    "qr_agent": qr_agent.run,
    "content_agent": content_agent.run,
}

_calibrator = ConfidenceCalibrator()  # replace with a fitted instance in production


def _router_node(state: CaseState) -> CaseState:
    state.agents_to_run = router.route(state)
    return state


def _evidence_node(state: CaseState) -> CaseState:
    for agent_name in state.agents_to_run:
        state = _AGENT_FUNCS[agent_name](state)
    return state


def _judge_node(state: CaseState) -> CaseState:
    return judge_agent.run(state)


def _calibration_node(state: CaseState) -> CaseState:
    return calibrate(state, _calibrator)


def _explainer_node(state: CaseState) -> CaseState:
    return explainer_agent.run(state)


def build_graph():
    graph = StateGraph(CaseState)
    graph.add_node("router", _router_node)
    graph.add_node("evidence_agents", _evidence_node)
    graph.add_node("judge", _judge_node)
    graph.add_node("calibration", _calibration_node)
    graph.add_node("explainer", _explainer_node)

    graph.set_entry_point("router")
    graph.add_edge("router", "evidence_agents")
    graph.add_edge("evidence_agents", "judge")
    graph.add_edge("judge", "calibration")
    graph.add_edge("calibration", "explainer")
    graph.add_edge("explainer", END)

    return graph.compile()


def analyze(raw_input: str) -> CaseState:
    """Convenience entry point: run the full pipeline on a single input."""
    compiled_graph = build_graph()
    initial_state = CaseState(raw_input=raw_input)
    final_state = compiled_graph.invoke(initial_state)
    # LangGraph returns a plain dict for dataclass states; convert back so
    # callers (the API) can use attribute access.
    if isinstance(final_state, dict):
        final_state = CaseState(**final_state)
    return final_state
