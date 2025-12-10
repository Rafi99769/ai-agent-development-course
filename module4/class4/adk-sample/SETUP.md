# Setup Guide

## Installation

Install the project dependencies using uv:

```bash
uv sync
```

This will install:
- `google-adk` - Google Agent Development Kit
- `fastmcp` - Fast, Pythonic MCP server framework

## Project Structure

```
adk-sample/
├── main_agent/
│   └── agent.py          # Main agent with MCP integration
├── roaster_agent/
│   └── agent.py          # Roaster sub-agent
├── mcp-server/
│   ├── time_server.py    # FastMCP time server
│   └── README.md         # MCP server documentation
├── test_mcp_integration.py  # Integration test script
└── pyproject.toml        # Project dependencies
```

## Running the Application

### Test the MCP Integration

```bash
python test_mcp_integration.py
```

This will test:
1. Getting current time in UTC
2. Getting current time in a specific timezone (New York)
3. Testing the joke function

### Run with ADK Web (Development)

```bash
adk web
```

Then interact with the agent through the web interface.

## MCP Server Details

The time MCP server is built with FastMCP and provides:
- **get_current_time** tool: Get current time in any timezone

The server runs via stdio transport and is automatically managed by the main agent through `McpToolset`.

## How It Works

1. **MCP Server** (`mcp-server/time_server.py`):
   - Built with FastMCP
   - Exposes `get_current_time` tool
   - Runs via stdio transport

2. **Main Agent** (`main_agent/agent.py`):
   - Uses `McpToolset` to connect to the MCP server
   - Automatically discovers and exposes MCP tools to the LLM
   - Manages the MCP server lifecycle

3. **Integration**:
   - Agent spawns the MCP server as a subprocess
   - Communicates via stdin/stdout
   - Tools are seamlessly available to the LLM
