# Time MCP Server

A minimalistic Model Context Protocol (MCP) server built with FastMCP that provides current time functionality.

## Features

- **get_current_time**: Get the current time in any timezone

## Tool Details

### get_current_time

Returns the current time in a specified timezone.

**Parameters:**
- `timezone` (optional): Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo'). Defaults to 'UTC'.

**Returns:**
```json
{
  "timezone": "UTC",
  "datetime": "2024-12-09T15:44:00+00:00",
  "formatted": "2024-12-09 15:44:00 UTC",
  "unix_timestamp": 1702137840
}
```

## Usage

This MCP server is integrated with the main agent in `main_agent/agent.py` using Google ADK's `McpToolset`.

### Running the server standalone

```bash
python mcp-server/time_server.py
```

### Testing the integration

```bash
python test_mcp_integration.py
```

## Implementation Details

- Built using **FastMCP** - a fast, Pythonic way to build MCP servers
- Communicates via **stdio** (standard input/output) transport
- Minimalistic implementation with decorator-based tool definition
- Integrated with Google ADK using `McpToolset` and `StdioConnectionParams`

## Why FastMCP?

FastMCP provides:
- Clean, decorator-based API (`@mcp.tool()`)
- Automatic schema generation from type hints and docstrings
- Built-in stdio transport support
- Minimal boilerplate code
