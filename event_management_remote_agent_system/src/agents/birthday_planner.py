from google.adk.agents import LlmAgent
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create the Birthday Planner Agent
birthday_planner_agent = LlmAgent(
    name="BirthdayPlannerAgent",
    model="gemini-2.0-flash",
    description="Generates creative birthday party themes and activity suggestions based on age and interests.",
    instruction=(
        "You are a specialized Birthday Party Idea Generator.\n"
        "Given the age and interests of the birthday person, provide 3-5 creative and distinct "
        "theme or activity suggestions suitable for them. Be descriptive and fun!\n"
        "Do NOT ask any further questions. Only provide suggestions based on the input given.\n"
        "Present your suggestions clearly."
    ),
    tools=[],
)
logging.info("Birthday Planner Agent initialized.")
