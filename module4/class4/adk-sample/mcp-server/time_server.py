"""
Simple MCP Server for getting current time using FastMCP
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from fastmcp import FastMCP

# Create FastMCP server instance
mcp = FastMCP("time-server")


@mcp.tool()
def get_current_time(timezone: str = "UTC") -> dict:
    """
    Get the current time in a specified timezone.
    
    Args:
        timezone: Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo'). 
                 Defaults to 'UTC'.
    
    Returns:
        Dictionary containing timezone, datetime, formatted time, and unix timestamp
    """
    try:
        # Get current time in the specified timezone
        tz = ZoneInfo(timezone)
        current_time = datetime.now(tz)
        
        # Return structured response
        return {
            "timezone": timezone,
            "datetime": current_time.isoformat(),
            "formatted": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "unix_timestamp": int(current_time.timestamp())
        }
    except Exception as e:
        return {"error": f"Failed to get current time: {str(e)}"}


if __name__ == "__main__":
    # Run with stdio transport (default)
    mcp.run(transport="stdio")
