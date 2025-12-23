from .agents import get_agent, tools
from .schemas import AgentState
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langgraph.graph import END

tool_node = ToolNode(tools)

def agent_node(state: AgentState):
    agent = get_agent()

    response = agent.invoke({"messages": state["messages"]})

    goto = END
    if response.tool_calls and len(response.tool_calls) > 0:
        goto = "tools"

    return Command(
        goto=goto,
        update={"messages": [response]}
    )

