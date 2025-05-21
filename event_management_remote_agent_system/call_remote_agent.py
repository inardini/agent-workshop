import os
import logging
import uuid
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

# Configuration
load_dotenv(".env")

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
AGENT_ENGINE_RESOURCE_NAME = os.getenv(
    "AGENT_ENGINE_RESOURCE_NAME",
)


# Helper function
def get_text_from_final_response(events) -> str:
    """Extracts text from the final agent response event."""
    final_text = "Agent did not provide a text response."
    for event in events:
        if event.get("type") == "FINAL_RESPONSE" and event.get("outputs"):
            parts = event.get("outputs", {}).get("llm_response", {}).get("parts", [])
            if parts and "text" in parts[0]:
                final_text = parts[0]["text"]
                break
        elif "parts" in event and isinstance(event["parts"], list):
            for part in event["parts"]:
                if "text" in part:
                    final_text = part["text"]
    return final_text


# Main
def main():
    logger.info(
        f"Initializing Vertex AI for project '{GOOGLE_CLOUD_PROJECT}' in '{GOOGLE_CLOUD_LOCATION}'"
    )
    vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

    try:
        logger.info(f"Connecting to remote agent engine: {AGENT_ENGINE_RESOURCE_NAME}")
        remote_agent_app = agent_engines.get(AGENT_ENGINE_RESOURCE_NAME)
        logger.info("Successfully connected to the remote agent.")

        # Define a unique user ID and a query for the agent
        user_id = f"remote_user_{uuid.uuid4()}"
        query = "I need some cool ideas for a 10-year old's birthday. They like space exploration and robots."

        logger.info(f"Creating remote session for user_id: {user_id}")
        remote_session_info = remote_agent_app.create_session(user_id=user_id)
        session_id = remote_session_info["id"]
        logger.info(f"Remote session created with ID: {session_id}")

        print(f"\n> You: {query}")
        logger.info(f"Sending query to remote agent (session: {session_id}): '{query}'")

        response_events = []
        for event in remote_agent_app.stream_query(
            user_id=user_id, session_id=session_id, input={"text": query}
        ):
            logger.info(f"Received event: {event}")
            response_events.append(event)

        agent_reply_text = "Could not extract a clear text reply."
        if response_events:
            for event_item in reversed(response_events):
                if (
                    isinstance(event_item, dict)
                    and "parts" in event_item
                    and event_item.get("role") == "model"
                ):
                    parts = event_item["parts"]
                    if parts and "text" in parts[0]:
                        agent_reply_text = parts[0]["text"]
                        break

        print(f"\n< Agent: {agent_reply_text}")
        logger.info(f"Agent's final reply: {agent_reply_text}")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
