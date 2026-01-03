from langgraph.graph import StateGraph, START, END

from .nodes import agent_node, tool_node
from .schemas import AgentState
from langgraph.checkpoint.memory import InMemorySaver


def create_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=InMemorySaver())