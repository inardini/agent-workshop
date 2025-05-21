import asyncio
import os
from dotenv import load_dotenv
import logging
import uuid
from google.adk.agents import LlmAgent
from google.adk.models.anthropic_llm import Claude
from google.adk.models.registry import LLMRegistry
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Function to interact with the agent
async def interact_with_agent(
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


# Environment Setup (User needs to ensure these are set)
load_dotenv()
logging.info(f"Using GCP Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
logging.info(f"Using GCP Location: {os.getenv('GOOGLE_CLOUD_LOCATION')}")
logging.info(f"Using Vertex AI: {os.getenv('GOOGLE_GENAI_USE_VERTEXAI')}")

# Register Claude Model for ADK
LLMRegistry.register(Claude)
logging.info("Claude model registered with LLMRegistry.")

# Define the Birthday Planner Agent
root_agent = LlmAgent(
    name="BirthdayPlannerAgent",
    model="claude-3-7-sonnet@20250219",
    description="Helps plan birthday party themes and activities.",
    instruction=(
        "You are a friendly and creative Birthday Planner assistant.\n"
        "Your goal is to help the user brainstorm ideas for a birthday party.\n"
        "1. First, ask for the age of the birthday person.\n"
        "2. After receiving the age, ask about their interests or hobbies.\n"
        "3. Once you have both age and interests, provide 3-5 suitable and creative "
        "birthday party theme or activity suggestions.\n"
        "4. Maintain a cheerful and helpful tone throughout the conversation.\n"
        "5. If the user provides both age and interests in their first message, "
        "you can skip asking and directly provide suggestions."
    ),
    tools=[],
)
logging.info("BirthdayPlannerAgent initialized.")

if __name__ == "__main__":
    app_name = f"BirthdayPlannerApp-{uuid.uuid4()}"
    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service,
    )
    logging.info("Runner initialized with InMemorySessionService.")

    # Main conversation
    async def main_conversation():
        user = f"test_user_{uuid.uuid4()}"
        session_id = f"birthday_session_{uuid.uuid4()}"

        # Start the conversation
        await interact_with_agent(
            app_name, user, session_id, "Hi! Can you help me plan a birthday?", session_service, runner
        )
        await interact_with_agent(app_name, user, session_id, "They are turning 10.", session_service, runner)
        await interact_with_agent(
            app_name, user, session_id, "They love superheroes and space.", session_service, runner)
        await interact_with_agent(app_name, user, session_id, "Great ideas! Thanks!", session_service, runner)

    asyncio.run(main_conversation())
