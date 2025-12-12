from google.adk.agents.llm_agent import Agent
from datetime import datetime
from roaster_agent.agent import roaster_agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import os


def generate_jokes():
    return "ha ha , this is my joke!"

# Get the absolute path to the MCP server script
MCP_SERVER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "mcp-server",
    "time_server.py"
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge. You have access to time information through the get_current_time tool.',
    tools=[
        generate_jokes,
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python',
                    args=[MCP_SERVER_PATH],
                ),
            ),
        )
    ],
    sub_agents=[roaster_agent]
)
