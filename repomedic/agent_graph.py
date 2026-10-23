"""One decision, at most one investigation, then one final diagnosis."""
from typing import Any

from langgraph.graph import END, START, StateGraph

from repomedic.agent_nodes import decision_node, diagnosis_node, investigation_node
from repomedic.agent_state import AgentState


def route_decision(state: AgentState) -> str:
    if state.get("error_message"):
        return "end"
    decision = state.get("investigation_decision")
    return "investigate" if decision and decision.needs_investigation else "diagnose"


def build_agent_graph(model: Any = None):
    graph = StateGraph(AgentState)
    graph.add_node("decision", lambda state: decision_node(state, model))
    graph.add_node("investigate", investigation_node)
    graph.add_node("diagnose", lambda state: diagnosis_node(state, model))
    graph.add_edge(START, "decision")
    graph.add_conditional_edges("decision", route_decision,
                               {"end": END, "investigate": "investigate", "diagnose": "diagnose"})
    graph.add_edge("investigate", "diagnose")
    graph.add_edge("diagnose", END)
    return graph.compile()


def run_agent(project_root: str, error_info: dict[str, Any], model: Any = None) -> AgentState:
    return build_agent_graph(model).invoke(
        {"project_root": project_root, "error_info": error_info},
        config={"recursion_limit": 8},
    )
