from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.models.anthropic_llm import Claude
from google.adk.models.registry import LLMRegistry
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Create the Event Organizer Agent
def create_event_organizer_agent(
    planner_agent_instance: LlmAgent, calendar_agent_instance: LlmAgent
) -> LlmAgent:
    """
    Creates the EventOrganizerAgent which orchestrates other specialist agents.

    Args:
        planner_agent_instance: An initialized instance of the BirthdayPlannerAgent.
        calendar_agent_instance: An initialized instance of the CalendarServiceAgent.
    """
    organizer = LlmAgent(
        name="EventOrganizerAgent",
        model="gemini-2.0-flash",
        description="Main coordinator for event planning. Delegates birthday planning to a specialist and calendar tasks to another.",
        instruction=(
            "You are an expert Event Organizer.\n"
            "You have a team of specialist agents:\n"
            f"- '{planner_agent_instance.name}': This agent is an expert at brainstorming birthday party ideas, themes, or activities. Delegate to it ONLY for generating these ideas.\n"
            f"- '{calendar_agent_instance.name}': This agent handles all calendar-related tasks, specifically creating calendar events using the 'create_calendar_event' tool. Delegate to it for scheduling.\n"
            "Your primary job is to understand the user's request and delegate to the correct specialist agent.\n"
            "If the user asks for birthday ideas, delegate to the BirthdayPlannerAgent.\n"
            "If the user asks to create a calendar event, delegate to the CalendarServiceAgent. Ensure you have all details like date, time, duration, title, and description before asking CalendarServiceAgent to create an event.\n"
            "If the request is unclear, ask clarifying questions to determine which specialist to use or what information is missing for a task."
        ),
        tools=[
            agent_tool.AgentTool(agent=planner_agent_instance),
            agent_tool.AgentTool(agent=calendar_agent_instance),
        ],
    )
    logging.info(f"Organizer Agent defined")
    return organizer
