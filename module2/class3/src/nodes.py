from src.tools import create_todo, read_todos, update_todo
from .agents import get_agent
from .schemas import AgentState
from langgraph.prebuilt import ToolNode


def agent_node(state: AgentState):
    agent = get_agent()

    response = agent.invoke({"messages": state["messages"]})

    return {"messages": [response]}


tool_node = ToolNode(tools=[create_todo, read_todos, update_todo])
