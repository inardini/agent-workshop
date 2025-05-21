from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_calendar_event(
    date: str, time: str, duration_hours: int, title: str, description: str
) -> Dict[str, Any]:
    """
    Creates a new event in the calendar.
    Args:
        date (str): The date of the event (e.g., '2025-07-20').
        time (str): The start time of the event (e.g., '10:00').
        duration_hours (int): The duration of the event in hours.
        title (str): The title of the event.
        description (str): A brief description of the event.
    Returns:
        dict: Indicating success or failure of event creation.
    """
    logging.info(
        f"[MCP Calendar Tool Server] Creating event: {title} on {date} at {time} for {duration_hours} hours"
    )
    event_id = f"mcp_event_{hash(title + date + time)}"
    logging.info(f"[MCP Calendar Tool Server] Event ID: {event_id}")
    return {
        "status": "success",
        "event_id": event_id,
        "message": f"Event '{title}' created via MCP.",
    }
