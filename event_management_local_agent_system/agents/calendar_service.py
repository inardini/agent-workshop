import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.models.anthropic_llm import Claude
from google.adk.models.registry import LLMRegistry
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load and set environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
MCP_CALENDAR_SERVER_URL = os.getenv(
    "MCP_CALENDAR_SERVICE_URL", "http://0.0.0.0:8080/sse"
)

# Register Claude Model for ADK
LLMRegistry.register(Claude)
logging.info("Claude model registered with LLMRegistry.")


async def create_calendar_service_agent():
    """
    Creates the CalendarServiceAgent, asynchronously fetching tools from the MCP server.
    """

    logging.info(
        f"Attempting to connect to MCP Calendar Service at: {MCP_CALENDAR_SERVER_URL}"
    )

    # Fetch tools from the MCP Calendar Service
    mcp_tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(url=MCP_CALENDAR_SERVER_URL)
    )

    logging.info(f"Fetched {len(mcp_tools)} tools from MCP Calendar Service.")

    agent = LlmAgent(
        name="CalendarServiceAgent",
        model="claude-3-7-sonnet@20250219",
        description="Manages calendar operations like checking availability and creating events by connecting to an MCP Calendar Service.",
        instruction=(
            "You are a Calendar Assistant connected to an external calendar service.\n"
            "Use the tool 'check_calendar_availability' to check for free time slots.\n"
            "Use the tool 'create_calendar_event' to schedule new events.\n"
            "Ensure you have all necessary details (date, time, duration, title, description) before creating an event.\n"
            "Confirm actions with the user."
        ),
        tools=mcp_tools,
    )
    logging.info(
        "Calendar Service Agent initialized with tools from MCP Calendar Service."
    )
    return agent, exit_stack
