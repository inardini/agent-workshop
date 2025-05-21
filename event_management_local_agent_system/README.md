# ADK Event Management System with MCP Tools - Workshop Part 2

Welcome to the second part of our workshop! This section demonstrates a more complex agent system using the Google Agent Development Kit (ADK), featuring hierarchical agents and integration with tools hosted on a Managed Cloud Platform (MCP) service.

## Overview

This directory (`event_management_local_agent_system`) contains the source code for an "Event Management System." This system is composed of multiple agents working together:

1.  **Event Organizer Agent (Root Agent):**
    - Acts as the main coordinator.
    - Delegates tasks to specialized sub-agents based on the user's request.
2.  **Birthday Planner Agent (Sub-Agent):**
    - Generates birthday party ideas (similar to Part 1 but now integrated as a tool).
3.  **Calendar Service Agent (Sub-Agent):**
    - Manages calendar operations (e.g., creating events).
    - This agent dynamically fetches its tools from an external MCP service.
4.  **Calendar MCP Service:**
    - A separate Python service built with `FastMCP`.
    - Exposes calendar-related Python functions (e.g., `create_calendar_event`) as tools that the `CalendarServiceAgent` can consume.
    - This service is designed to be deployed to Google Cloud Run.

The system showcases how to build a multi-agent architecture where a primary agent orchestrates tasks by delegating to specialized agents, some of which can leverage externally hosted tools via MCP.

## Learning Objectives

- Understand how to create a hierarchical agent system with a root agent and sub-agents using `AgentTool`.
- Learn how to expose Python functions as tools using `FastMCP`.
- See how an ADK agent (`CalendarServiceAgent`) can dynamically discover and use tools from an MCP service (`MCPToolset.from_server`).
- Understand the deployment process of an MCP tool server to Google Cloud Run.
- Learn about asynchronous initialization of agents, especially when fetching external resources like MCP tools.
- Reinforce concepts of ADK runners, session management, and agent instruction design.

## Prerequisites

Ensure you have everything from Part 1, plus:

1.  **Python:** Version 3.9 or higher (due to `nest_asyncio` and modern `asyncio` usage).
2.  **Google Cloud SDK:** Installed and configured (`gcloud auth login`, `gcloud config set project YOUR_PROJECT_ID`).
3.  **Google Cloud Project:**
    - A Google Cloud Project with billing enabled.
    - The Vertex AI API and Cloud Run API enabled in your project.
4.  **Model Access:**
    - Ensure the models specified in the agents (`gemini-1.5-flash`, `claude-3-7-sonnet@20250219` or equivalents) are available in Vertex AI for your project. Verify and update model names in `agents/birthday_planner.py`, `agents/calendar_service.py`, and `agents/event_organizer.py` if necessary.
5.  **Docker:** Installed and running, if you plan to build and push the MCP service container image manually (the `gcloud run deploy --source .` command can often handle this automatically).
6.  **Bash Shell:** For running the `deploy_calendar_mcp.sh` script (available on Linux, macOS, and Windows via WSL or Git Bash).

## Setup Instructions

1.  **Clone the Repository (if you haven't already):**

    ```bash
    # git clone <repository-url>
    # cd <repository-name>/event_management_local_agent_system
    ```

    If you received the files directly, navigate to the `event_management_local_agent_system` directory.

2.  **Create a Python Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Root Level Dependencies:**
    Create a `requirements.txt` file in the `event_management_local_agent_system` directory (or add to an existing one if this is part of a larger project) with the following:

    ```txt
    google-adk
    python-dotenv
    google-generativeai
    # anthropic (if direct claude integration needed, here using Vertex)
    nest_asyncio
    ```

    Then, install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    _(Note: The `tools/requirements.txt` is for the MCP server and will be handled during its deployment)._

4.  **Set Up Environment Variables (Initial):**
    Create a file named `.env` in the `event_management_local_agent_system` directory. Add your GCP project details:

    ```env
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="your-gcp-region"  # e.g., us-central1
    GOOGLE_GENAI_USE_VERTEXAI="True"
    # ANTHROPIC_API_KEY="sk-ant-..." # Not strictly needed if GOOGLE_GENAI_USE_VERTEXAI is True

    # This will be populated by the deployment script later
    # MCP_CALENDAR_SERVICE_URL="http://your-mcp-service-url/sse"
    ```

5.  **Deploy the Calendar MCP Service:**
    This step deploys the `FastMCP` server from the `tools/` directory to Google Cloud Run.
    Make the deployment script executable:

    ```bash
    chmod +x deploy_calendar_mcp.sh
    ```

    Run the script. You can provide your GCP Project ID and Region as arguments, or the script will attempt to use environment variables or prompt you:

    ```bash
    ./deploy_calendar_mcp.sh [your-gcp-project-id] [your-gcp-region]
    ```

    For example:

    ```bash
    ./deploy_calendar_mcp.sh my-gcp-project us-central1
    ```

    This script will:

    - Build and deploy the Docker container defined in `tools/Dockerfile` (which runs `tools/calendar_mcp_server.py`) to Google Cloud Run.
    - Once deployed, it will capture the **Service URL** of the Cloud Run service.
    - It will then **automatically update your `.env` file** with the `MCP_CALENDAR_SERVICE_URL`, pointing to the `/sse` endpoint of your deployed service.

    **Verify:** After the script completes, check your `.env` file. It should now contain a line similar to:

    ```env
    export MCP_CALENDAR_SERVICE_URL="https://adk-calendar-mcp-service-xxxxxx-uc.a.run.app/sse"
    ```

    _(The exact URL will be unique to your deployment)._

    **Important:** If you are running the Python script (`agent.py`) in a terminal session that was active _before_ the `.env` file was updated by the script, you might need to `source .env` or restart your terminal/IDE for the new `MCP_CALENDAR_SERVICE_URL` environment variable to be picked up by the Python script. The `agent.py` script attempts to load it dynamically, but shell environments may cache variables.

## Running the Code

Once the setup is complete and the Calendar MCP Service is deployed and its URL is in your `.env` file, you can run the main agent system:

```bash
python agent.py
```

You will see console output showing:

- Initialization of specialist agents.
- The `CalendarServiceAgent` attempting to connect to your deployed MCP service and fetch tools.
- A simulated conversation where the `EventOrganizerAgent` delegates tasks to the `BirthdayPlannerAgent` and the `CalendarServiceAgent`.
- The `CalendarServiceAgent` using the MCP tool (which in turn calls the `create_calendar_event` function running on Cloud Run).
- Cleanup of MCP connections at the end.

Example interaction flow you might observe:

1.  User asks for birthday ideas.
2.  `EventOrganizerAgent` delegates to `BirthdayPlannerAgent`.
3.  `BirthdayPlannerAgent` provides ideas.
4.  User asks to schedule one of the ideas.
5.  `EventOrganizerAgent` gathers details and delegates to `CalendarServiceAgent`.
6.  `CalendarServiceAgent` uses the `create_calendar_event` tool (from MCP) to "create" the event.

## Code Structure and Key ADK/MCP Concepts

- **`event_management_local_agent_system/__init__.py`**: Standard Python package initializer.

- **`event_management_local_agent_system/agent.py` (Main Script)**:

  - **`interact` function**: Similar to Part 1, simulates user interaction.
  - **`get_root_agent`**: Asynchronously initializes all agents. This is crucial because `create_calendar_service_agent` needs to perform an `await` operation to fetch MCP tools.
  - **`initialize_root_agent`**: Handles the global initialization of the root agent using `nest_asyncio` to allow `asyncio.run` within environments that might already have an event loop (like Jupyter notebooks, though not directly used here).
  - **Main Execution Block (`if __name__ == "__main__":`)**:
    - Calls `get_root_agent` to set up the agent hierarchy.
    - Initializes ADK services: `InMemorySessionService`, `InMemoryArtifactService`, `InMemoryMemoryService`.
    - Creates the `Runner`.
    - Runs a predefined multi-turn conversation using `interact`.
    - Crucially, uses `await exit_stack.aclose()` to properly close connections established by `MCPToolset.from_server`.

- **`event_management_local_agent_system/agents/`**:

  - **`birthday_planner.py`**:
    - A simple `LlmAgent` focused on generating birthday ideas. It does not ask questions and directly provides suggestions.
  - **`calendar_service.py`**:
    - **`create_calendar_service_agent` (async function)**:
      - Loads `MCP_CALENDAR_SERVICE_URL` from the environment.
      - Uses `MCPToolset.from_server()` to asynchronously connect to the deployed `FastMCP` service and retrieve the available tools. This returns the tools and an `AsyncExitStack` for cleanup.
      - Defines an `LlmAgent` (`CalendarServiceAgent`) that uses these fetched `mcp_tools`. Its instructions guide it on how to use tools like `create_calendar_event`.
  - **`event_organizer.py`**:
    - **`create_event_organizer_agent` function**:
      - Takes instances of the planner and calendar agents as arguments.
      - Defines the root `LlmAgent` (`EventOrganizerAgent`).
      - **Key Concept: `agent_tool.AgentTool`**: It uses `AgentTool` to wrap the `planner_agent_instance` and `calendar_agent_instance`, making them available as tools for the `EventOrganizerAgent`.
      - The `instruction` for this agent tells it _how and when_ to delegate tasks to these specialist agent-tools.

- **`event_management_local_agent_system/tools/`**:

  - **`calendar_tools.py`**:
    - Contains the actual Python function `create_calendar_event` that performs the "work" of creating a calendar event (in this demo, it logs and returns a success message). This is the function exposed as an MCP tool.
  - **`calendar_mcp_server.py`**:
    - Uses `FastMCP` to create an HTTP server.
    - `mcp = FastMCP("ADKCalendarMCPService")`: Initializes the `FastMCP` application.
    - `mcp.tool()(create_calendar_event)`: Registers the `create_calendar_event` function from `calendar_tools.py` as a tool discoverable by ADK agents connecting to this server's `/sse` (Server-Sent Events) endpoint.
    - Runs an `asyncio` server, typically on port 8080 (as configured for Cloud Run).
  - **`Dockerfile`**: Standard Dockerfile to package the `FastMCP` server and its dependencies (`requirements.txt` specific to tools) into a container image for deployment.
  - **`requirements.txt`**: Lists dependencies for the `FastMCP` server (e.g., `fastmcp`, `uvicorn`).

- **`deploy_calendar_mcp.sh`**:
  - A shell script that automates the deployment of the `tools/` directory to Google Cloud Run.
  - Uses `gcloud run deploy --source .` which typically handles Docker image building and pushing.
  - Captures the deployed service URL and updates the `.env` file.

## What's Next?

This example significantly expands on the single-agent concept by introducing:

- Agent hierarchy and delegation.
- Dynamic tool loading from remote MCP services.
- Deployment of tool-hosting services.

Further exploration could involve:

- Adding more complex tools to the MCP service (e.g., actually interacting with Google Calendar API).
- Implementing more sophisticated error handling and state management across agents.
- Exploring persistent session and memory services instead of `InMemory...` for more robust applications.
- Integrating these agents into a larger Vertex AI Agent Engine setup.

Happy experimenting with multi-agent systems and MCP!
