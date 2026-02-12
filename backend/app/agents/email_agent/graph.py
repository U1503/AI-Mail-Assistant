from langgraph.graph import StateGraph, END

from app.agents.email_agent.state import AgentState
from app.agents.email_agent.nodes.llm_node import llm_node
from app.agents.email_agent.nodes.router_node import router_node
from app.agents.email_agent.nodes.tool_node import tool_node
from app.agents.email_agent.nodes.deadline_node import deadline_node
from app.agents.email_agent.nodes.upcoming_tasks_node import upcoming_tasks_node
from app.agents.email_agent.nodes.final_response_node import final_response_node


def build_email_agent():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("llm", llm_node)
    graph.add_node("router", router_node)   # ← ADD ROUTER AS NODE
    graph.add_node("tool", tool_node)
    graph.add_node("deadline", deadline_node)
    graph.add_node("tasks", upcoming_tasks_node)
    graph.add_node("final", final_response_node)

    # Entry
    graph.set_entry_point("llm")

    # LLM → Router
    graph.add_edge("llm", "router")

    # Router conditional routing
    graph.add_conditional_edges(
        "router",
        lambda state: state.get("_next"),   # 
        {
            "tool": "tool",
            "final": "final",
        },
    )

    # Tool flow
    graph.add_edge("tool", "deadline")
    graph.add_edge("deadline", "tasks")
    graph.add_edge("tasks", "final")

    graph.add_edge("final", END)

    return graph.compile()


_EMAIL_AGENT = build_email_agent()


def run_email_agent(state: AgentState) -> AgentState:
    return _EMAIL_AGENT.invoke(state)
