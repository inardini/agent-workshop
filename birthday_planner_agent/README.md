# ADK Birthday Planner Agent - Workshop Part 1

Welcome to the first part of our workshop on ADK, MCP, and Vertex AI Agent Engine! This section focuses on building a simple conversational agent using the Google Agent Development Kit (ADK).

## Overview

This directory (`birthday_planner_agent`) contains the source code for a "Birthday Planner Agent". This agent is designed to:

1.  Interact with a user in a conversational manner.
2.  Ask for the age of the person whose birthday is being planned.
3.  Inquire about their interests or hobbies.
4.  Provide 3-5 creative birthday party theme or activity suggestions based on the age and interests.
5.  Maintain a cheerful and helpful tone.

The agent is built using the `LlmAgent` class from the ADK and leverages a Claude model (specifically `claude-3-7-sonnet@20250219`) for its conversational logic.

## Learning Objectives

- Understand the basic structure of an ADK-based agent.
- Learn how to define an agent's behavior using instructions and an LLM.
- See how to register and use an LLM (Claude via Vertex AI) with ADK.
- Understand how to run and interact with an ADK agent locally using `InMemorySessionService`.
- Get familiar with key ADK components like `LlmAgent`, `Runner`, and `SessionService`.

## Prerequisites

Before you begin, ensure you have the following:

1.  **Python:** Version 3.8 or higher.
2.  **Google Cloud SDK:** Installed and configured (`gcloud auth login`, `gcloud config set project YOUR_PROJECT_ID`).
3.  **Google Cloud Project:**
    - A Google Cloud Project with billing enabled.
    - The Vertex AI API enabled in your project.
4.  **Model Access:**
    - Ensure the Claude model (`claude-3-7-sonnet@20250219`) is available and enabled for use in Vertex AI within your specified GCP project and location. You might need to request access to Claude models in Vertex AI.
    - _Note_: Model availability and names can change. Verify the exact model identifier in the Vertex AI Model Garden. If `claude-3-7-sonnet@20250219` is not available, you may need to substitute it with an available Claude model (e.g., `claude-3-sonnet@20240229`) in `agent.py`.
5.  **Git:** For cloning the repository (if applicable).

## Setup Instructions

1.  **Clone the Repository (if you haven't already):**

    ```bash
    # git clone <repository-url>
    # cd <repository-name>/birthday_planner_agent
    ```

    If you received the files directly, navigate to the `birthday_planner_agent` directory.

2.  **Create a Python Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Create a `requirements.txt` file in the `birthday_planner_agent` directory with the following content:

    ```txt
    google-adk
    python-dotenv
    google-generativeai
    # anthropic (if direct claude integration needed, but here using Vertex)
    ```

    Then, install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Create a file named `.env` in the `birthday_planner_agent` directory. Add the following environment variables, replacing the placeholder values with your actual GCP project details:

    ```env
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="your-gcp-region"  # e.g., us-central1
    GOOGLE_GENAI_USE_VERTEXAI="True"
    # ANTHROPIC_API_KEY="sk-ant-..." # Not strictly needed if GOOGLE_GENAI_USE_VERTEXAI is True and Claude is accessed via Vertex
    ```

## Running the Code

Once the setup is complete, you can run the agent simulation:

```bash
python agent.py
```

You should see output in your console that simulates a conversation with the Birthday Planner Agent. It will look something like this:

```
INFO:__main__:Using GCP Project: your-gcp-project-id
INFO:__main__:Using GCP Location: your-gcp-region
INFO:__main__:Using Vertex AI: True
INFO:__main__:Claude model registered with LLMRegistry.
INFO:__main__:BirthdayPlannerAgent initialized.
INFO:__main__:Runner initialized with InMemorySessionService.
INFO:__main__:User (test_user_...) query: Hi! Can you help me plan a birthday?

> User (test_user_...): Hi! Can you help me plan a birthday?
INFO:__main__:Agent response: Hello! I'd be delighted to help you plan a birthday! To start, could you please tell me the age of the birthday person?
INFO:__main__:User (test_user_...) query: They are turning 10.

> User (test_user_...): They are turning 10.
INFO:__main__:Agent response: Great! And what are some of their interests or hobbies? Knowing this will help me suggest some fun themes or activities!
INFO:__main__:User (test_user_...) query: They love superheroes and space.

> User (test_user_...): They love superheroes and space.
INFO:__main__:Agent response: Wonderful! For a 10-year-old who loves superheroes and space, here are a few party ideas:
1.  **Superhero Training Academy:** ...
2.  **Intergalactic Space Mission:** ...
3.  **Cosmic Superhero Mashup:** ...
INFO:__main__:User (test_user_...) query: Great ideas! Thanks!

> User (test_user_...): Great ideas! Thanks!
INFO:__main__:Agent response: You're most welcome! I'm glad you liked the ideas. Happy planning, and I hope it's a fantastic birthday celebration!
```

## Code Structure and Key ADK Concepts

The main logic is concentrated in `agent.py`.

- **`__init__.py`**: An empty file that makes Python treat the `birthday_planner_agent` directory as a package. This is a standard Python convention.

- **`agent.py`**: This file contains all the core logic for the Birthday Planner Agent.
  - **Imports**:
    - Includes necessary ADK components: `LlmAgent`, `Claude`, `LLMRegistry`, `Runner`, `InMemorySessionService`.
    - Standard Python libraries like `asyncio`, `os`, `logging`, `uuid`, and `dotenv`.
    - Google GenAI types: `Content`, `Part`.
  - **`interact_with_agent` function**:
    - A helper asynchronous function designed to simulate sending user queries to the agent.
    - It prints the conversation flow to the console for easy debugging and understanding.
    - Demonstrates how to retrieve an existing session or create a new one using `session_service.get_session()` and `session_service.create_session()`.
    - Shows the usage of the `runner.run_async()` method to process a new user message and stream agent events.
    - Extracts the final text response from the agent's events.
  - **Environment Setup**:
    - Uses `load_dotenv()` to load environment variables from a `.env` file (e.g., GCP project ID, location).
    - Logs the GCP project, location, and Vertex AI usage status for clarity.
  - **Model Registration (`LLMRegistry.register(Claude)`)**:
    - This crucial line makes the `Claude` model implementation available within the ADK framework.
    - The ADK's `Claude` class provides the necessary interface to interact with Anthropic's Claude models, particularly when accessed via Vertex AI (as indicated by `GOOGLE_GENAI_USE_VERTEXAI="True"`).
  - **`LlmAgent` Definition (`root_agent`)**:
    - This is where the agent itself is defined and configured.
    - **`name`**: A string identifier for the agent (e.g., `"BirthdayPlannerAgent"`).
    - **`model`**: Specifies the identifier of the Large Language Model the agent will use (e.g., `"claude-3-7-sonnet@20250219"`). This model identifier must correspond to a model registered in `LLMRegistry` and be available in your Vertex AI environment.
    - **`description`**: A human-readable description of what the agent does.
    - **`instruction`**: This is the core "prompt" or set of directives given to the LLM. It defines:
      - The agent's persona (e.g., "friendly and creative Birthday Planner assistant").
      - Its primary goal (e.g., "help the user brainstorm ideas for a birthday party").
      - A step-by-step process or rules for interaction (e.g., "1. First, ask for age... 2. Ask about interests...").
      - Desired tone and behavior.
    - **`tools`**: An empty list (`[]`) for this simple agent. In more advanced agents, this list would contain definitions of tools (functions) that the LLM can decide to call to perform actions or retrieve information.
  - **`InMemorySessionService`**:
    - ADK uses session services to manage the state and history of conversations.
    - `InMemorySessionService` is a basic implementation that stores all session data in the computer's memory.
    - It's suitable for local development, testing, and simple scenarios, but not for production environments where persistence and scalability are required.
  - **`Runner`**:
    - The `Runner` class (`runner = Runner(...)`) is a central component in ADK for executing an agent.
    - It takes the defined `agent` (`root_agent`), the `app_name`, and the `session_service` as input.
    - It orchestrates the flow of information: receives user messages, passes them to the agent (which interacts with the LLM), and manages the conversation state through the session service.
  - **`main_conversation` function**:
    - An asynchronous function (`async def`) that serves as the entry point for the example script when run directly (`if __name__ == "__main__":`).
    - It simulates a multi-turn conversation by:
      - Generating unique user and session IDs.
      - Calling `interact_with_agent` multiple times with sequential user queries.
    - This demonstrates how a typical interaction with the agent might unfold.

## What's Next?

This example provides a foundational understanding of building a simple conversational agent using the Google Agent Development Kit (ADK). In subsequent parts of the workshop, we will explore:

- More complex agent behaviors, including the use of **tools**.
- Integration with external services and APIs.
- Deployment strategies, potentially touching upon **MCP (Managed Cloud Platform)** concepts.
- Leveraging more advanced features of **Vertex AI Agent Engine** for building and managing sophisticated agents.

Feel free to experiment with this agent:

- **Modify Instructions**: Change the agent's `instruction` string in `agent.py` to alter its personality, rules, or the type of suggestions it provides.
- **Simulate Different Conversations**: Alter the queries in the `main_conversation()` function in `agent.py` to test various interaction scenarios.
- **Try a Different Model**: If you have access to other Claude models in Vertex AI (or other compatible models registered in ADK), try changing the `model` parameter in the `LlmAgent` definition. Ensure the model identifier is correct and the model is available in your GCP project/location.

Happy coding!
