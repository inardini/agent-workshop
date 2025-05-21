import asyncio
import os
import logging
from fastmcp import FastMCP
from calendar_tools import create_calendar_event

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize FastMCP App
mcp = FastMCP("ADKCalendarMCPService")
logging.info(f"FastMCP server initialized")

# Register the Python functions as MCP tools
mcp.tool()(create_calendar_event)
logging.info("Tools registered with FastMCP server.")


# Entry point for Cloud Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logging.info(f"Starting FastMCP server on port {port}...")
    asyncio.run(mcp.run_sse_async(host="0.0.0.0", port=port))
