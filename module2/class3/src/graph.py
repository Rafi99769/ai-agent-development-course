from langgraph.graph import StateGraph, START, END
from .schemas import AgentState
from .nodes import agent_node, tool_node
from langgraph.checkpoint.memory import InMemorySaver


def router(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls and len(last_message.tool_calls) > 0:
        return "tool"
    else:
        return END


def create_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tool", tool_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", router, {"tool": "tool", END: END})
    graph.add_edge("tool", "agent")

    checkpointer = InMemorySaver()
    complied_graph = graph.compile(checkpointer=checkpointer)

    return complied_graph
