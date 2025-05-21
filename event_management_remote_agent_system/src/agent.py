import asyncio
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv
import logging
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.genai.types import Content, Part
from .agents.event_organizer import organizer_agent
import uuid


# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


# Define helper functions
async def interact(
    app_name: str,
    user_id: str,
    session_id: str,
    query: str,
    session_service: InMemorySessionService,
    runner: Runner,
) -> str:
    """Sends a query to the agent and returns the final text response."""
    logging.info(f"User ({user_id}) query: {query}")
    print(f"\n> User ({user_id}): {query}")

    session = session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    if not session:
        session = session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        logging.info(f"New session created: {session_id}")

    user_message = Content(parts=[Part(text=query)], role="user")
    final_response_text = "Agent did not provide a response."

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=user_message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = (
                    event.content.parts[0].text or "Agent sent non-text content."
                )
    except Exception as e:
        logging.error(f"Error during agent run: {e}")
        return f"Error: {e}"

    logging.info(f"Agent response: {final_response_text}")
    return final_response_text


root_agent = organizer_agent

if __name__ == "__main__":
    # Main conversation flow (for programmatic execution)
    async def main():

        actual_root_agent = organizer_agent

        # Setup Runner and Session Service
        app_name = f"EventManagementSystemApp_{uuid.uuid4()}"
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        memory_service = InMemoryMemoryService()

        runner = Runner(
            agent=actual_root_agent,
            app_name=app_name,
            session_service=session_service,
            artifact_service=artifact_service,
            memory_service=memory_service,
        )
        logger.info(f"Runner initialized for agent")

        user_id = f"mcp_user_{uuid.uuid4()}"
        current_session_id = f"mcp_session_{uuid.uuid4()}"

        # --- Conversation ---
        logger.info("Starting Event Management Conversation")
        logger.info("=" * 50)

        await interact(
            query="Hello! I need some cool ideas for a 12-year old's birthday. They like video games and art.",
            app_name=app_name,
            user_id=user_id,
            session_id=current_session_id,
            session_service=session_service,
            runner=runner,
        )

        await interact(
            query="Okay, those are great. Let's schedule the 'Digital Art & Gaming Fest' for August 10th, 2025, at 3 PM for 4 hours. Description: Pixel party time!",
            app_name=app_name,
            user_id=user_id,
            session_id=current_session_id,
            session_service=session_service,
            runner=runner,
        )

        await interact(
            query="Thank you for your help!",
            app_name=app_name,
            user_id=user_id,
            session_id=current_session_id,
            session_service=session_service,
            runner=runner,
        )

        logger.info("=" * 50)
        logger.info("Conversation Ended. Cleaning up MCP Connections.")
        logger.info("MCP Connections closed.")
        logger.info("Exiting Event Management System.")

    # Run the main function
    asyncio.run(main())
