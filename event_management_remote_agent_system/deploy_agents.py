import os
import sys
import logging
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from google.adk.agents import Agent
from src.agents import (
    birthday_planner_agent,
    calendar_agent,
    organizer_agent,
)
from vertexai.preview import reasoning_engines


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [DeployWorkers] %(message)s",
)
logger = logging.getLogger(__name__)

# Define worker agents to deploy
AGENTS_TO_DEPLOY = [
    birthday_planner_agent,
    # calendar_agent,
    # organizer_agent
]

# Common Requirements
BASE_REQUIREMENTS = [
    "google-cloud-aiplatform[adk, agent_engines]==1.93.0",
    "anthropic[vertex]==0.51.0",
    "fastmcp==2.3.4",
    "nest-asyncio==1.6.0",
]


# Helper Function to Deploy a Single Agent
def deploy_single_agent(agent_object, requirements, display_name_prefix="adk"):

    if agent_object is None or not isinstance(agent_object, Agent):
        logger.error(
            f"Invalid agent object provided to deploy_single_agent: {agent_object}"
        )
        return None

    agent_name = getattr(agent_object, "name", "unknown-agent")
    display_name = f"{display_name_prefix}-{agent_name}"
    logger.info(f"Attempting to deploy agent '{agent_name}' as '{display_name}'...")
    logger.info(f"Using requirements: {requirements}")

    # Get agent path string for reporting purposes
    try:
        remote_app = agent_engines.create(
            agent_engine=reasoning_engines.AdkApp(
                agent=agent_object, enable_tracing=True
            ),
            requirements=list(set(requirements)),
            display_name=display_name,
            description=f"ADK worker agent: {agent_name}",
            extra_packages=["src"],
        )

        logger.info(f"Deployment submitted successfully for '{agent_name}'!")
        resource_name = remote_app.resource_name if remote_app.resource_name else None
        logger.info(f"Agent Engine Resource Name: {remote_app.name}")
        logger.info(f"App Name (Resource name): {resource_name}")

    except Exception as e:
        logger.error(f"Deployment failed for '{display_name}': {e}", exc_info=True)


# Main
def main():

    # Check if the script is being run directly
    logger.info("Starting Agent Deployment to Agent Engine")
    load_dotenv()

    # Set up environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_AE_REGION")
    staging_bucket = os.getenv("GOOGLE_CLOUD_BUCKET")

    print(f"Project ID: {project_id}")
    print(f"Location: {location}")
    print(f"Staging Bucket: {staging_bucket}")

    # Initialize Vertex AI SDK
    logger.info(
        f"Initializing Vertex AI: Project='{project_id}', Location='{location}', Staging='{staging_bucket}'"
    )
    vertexai.init(project=project_id, location=location, staging_bucket=staging_bucket)

    # Deploy the agent
    logger.info(f"Deploying {len(AGENTS_TO_DEPLOY)} worker agent(s)")
    for agent_obj in AGENTS_TO_DEPLOY:
        logger.info("-" * 40)
        agent_name = getattr(agent_obj, "name", "unknown")
        logger.info(f"Deploying worker agent: {agent_name}")
        deploy_single_agent(agent_obj, BASE_REQUIREMENTS)


if __name__ == "__main__":
    main()
