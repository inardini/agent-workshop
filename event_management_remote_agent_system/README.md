# ADK Event Management System - Deploying to Vertex AI Agent Engine - Workshop Part 3

Welcome to the third part of our workshop! This section demonstrates how to deploy an Agent Development Kit (ADK) agent to Google Cloud's Vertex AI Agent Engine and interact with it as a remote service.

## Overview

This directory (`event_management_remote_agent_system`) contains the code and scripts to:

1.  **Package ADK Agents:** The agent logic (e.g., `BirthdayPlannerAgent` from previous parts) is organized within a `src/` directory.
2.  **Deploy to Vertex AI Agent Engine:** A script (`deploy_agents.py`) uses the Vertex AI SDK to deploy a specified ADK agent (in this example, the `BirthdayPlannerAgent`) as a manageable, scalable "Agent Engine."
3.  **Interact Remotely:** Another script (`call_remote_agent.py`) shows how to connect to this deployed Agent Engine, create a session, and send queries to it from a client application.

This part transitions from local agent execution to cloud-hosted agent services.

## Learning Objectives

- Understand how to prepare ADK agents for deployment to Vertex AI Agent Engine.
- Learn to use the Vertex AI SDK (`vertexai.agent_engines`) to deploy an ADK agent.
- Understand the concept of an `AdkApp` within Vertex AI Reasoning Engines.
- Learn how to interact with a deployed Agent Engine:
  - Getting a reference to the remote agent.
  - Creating sessions.
  - Streaming queries and receiving responses.
- Become familiar with the necessary GCP configurations for Agent Engine deployment (e.g., Staging Bucket, IAM permissions).

## Prerequisites

Ensure you have everything from Part 1 and Part 2, plus:

1.  **Python:** Version 3.9 or higher.
2.  **Google Cloud SDK:** Installed and configured (`gcloud auth login`, `gcloud config set project YOUR_PROJECT_ID`).
3.  **Google Cloud Project:**
    - A Google Cloud Project with billing enabled.
    - The following APIs enabled in your project:
      - Vertex AI API
      - Cloud Build API
      - Artifact Registry API (or Container Registry API)
      - Cloud Run API (if you plan to re-deploy or manage the MCP Calendar service from Part 2).
      - IAM API.
4.  **Permissions:** Ensure your user account or service account has sufficient permissions in the GCP project (e.g., Vertex AI User, Cloud Build Editor, Artifact Registry Writer, Storage Object Admin for the staging bucket).
5.  **Google Cloud Storage Bucket:** A GCS bucket in the same region as your Agent Engine deployments. This will be used by Vertex AI as a staging bucket.
6.  **Model Access:** Ensure the LLM models specified in your agent definitions (e.g., `gemini-1.5-flash` for `BirthdayPlannerAgent`) are available and enabled for use in Vertex AI within your specified GCP project and location.

## Setup Instructions

1.  **Clone the Repository (if you haven't already):**

    ```bash
    # git clone <repository-url>
    # cd <repository-name>/event_management_remote_agent_system
    ```

    If you received the files directly, navigate to the `event_management_remote_agent_system` directory.

2.  **Create a Python Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Root Level Dependencies:**
    Create a `requirements.txt` file in the `event_management_remote_agent_system` directory with the following:

    ```txt
    google-cloud-aiplatform[adk,agent_engines]>=1.93.0 # Use a version supporting ADK App deployment
    python-dotenv
    # anthropic[vertex]>=0.51.0 # If using Claude models directly via Anthropic SDK
    # fastmcp>=2.3.4 # If running MCP components locally from here
    nest-asyncio>=1.6.0
    ```

    Then, install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Create a file named `.env` in the `event_management_remote_agent_system` directory. Add your GCP project details. **Leave `AGENT_ENGINE_RESOURCE_NAME` commented out or blank for now; it will be populated after deployment.**

    ```env
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="your-gcp-region-for-vertex-ai-general" # e.g., us-central1
    GOOGLE_CLOUD_AE_REGION="your-gcp-region-for-agent-engine" # e.g., us-central1, ensure it supports Agent Engine
    GOOGLE_CLOUD_BUCKET="your-gcs-staging-bucket-name" # e.g., my-adk-staging-bucket

    # This will be populated after running deploy_agents.py
    # AGENT_ENGINE_RESOURCE_NAME="projects/your-gcp-project-id/locations/your-gcp-region/agentEngines/your-agent-engine-id"
    ```

    - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID.
    - `GOOGLE_CLOUD_LOCATION`: The GCP region for general Vertex AI operations (can be same as AE_REGION).
    - `GOOGLE_CLOUD_AE_REGION`: The GCP region where you'll deploy the Agent Engine. Check Vertex AI documentation for supported regions.
    - `GOOGLE_CLOUD_BUCKET`: The name of your GCS bucket (without `gs://`) to be used for staging by Vertex AI.

5.  **Deploy the ADK Agent to Vertex AI Agent Engine:**
    Run the `deploy_agents.py` script. This script is currently configured to deploy only the `birthday_planner_agent` defined in `src/agents/birthday_planner.py`.

    ```bash
    python deploy_agents.py
    ```

    This script will:

    - Initialize Vertex AI with your project, location, and staging bucket.
    - Package the `src/` directory (containing agent definitions) and its dependencies.
    - Deploy the `BirthdayPlannerAgent` to Vertex AI Agent Engine. This process can take several minutes as it involves building a container image and provisioning resources.

    **After successful deployment, the script will output information including the "App Name (Resource name)". This is your `AGENT_ENGINE_RESOURCE_NAME`.**

6.  **Update `.env` file with Agent Engine Resource Name:**
    Copy the "App Name (Resource name)" output from the previous step (it will look something like `projects/your-project/locations/your-region/agentEngines/12345...`) and add it to your `.env` file:
    ```env
    AGENT_ENGINE_RESOURCE_NAME="projects/your-gcp-project-id/locations/your-gcp-region/agentEngines/your-agent-engine-id"
    ```

## Interacting with the Deployed Agent

Once the agent is deployed and your `.env` file is updated with `AGENT_ENGINE_RESOURCE_NAME`, you can interact with it using `call_remote_agent.py`:

```bash
python call_remote_agent.py
```

Example output:

```log
INFO:__main__:Initializing Vertex AI for project 'your-gcp-project-id' in 'your-gcp-region-for-vertex-ai-general'
INFO:__main__:Connecting to remote agent engine: projects/your-gcp-project-id/locations/your-gcp-region/agentEngines/your-agent-engine-id
INFO:__main__:Successfully connected to the remote agent.
INFO:__main__:Creating remote session for user_id: remote_user_xxxx
INFO:__main__:Remote session created with ID: yyyyy
INFO:__main__:Sending query to remote agent (session: yyyyy): 'I need some cool ideas for a 10-year old's birthday. They like space exploration and robots.'
> You: I need some cool ideas for a 10-year old's birthday. They like space exploration and robots.
INFO:__main__:Received event: {...}
...
INFO:__main__:Agent's final reply: For a 10-year-old who loves space exploration and robots, here are a few ideas:
1.  **Cosmic Robot Build-Off:** ...
2.  **Space Explorer Training Academy:** ...
3.  **Alien Encounter Escape Room:** ...
< Agent: For a 10-year-old who loves space exploration and robots, here are a few ideas: ...
```

## Code Structure and Key Concepts

- **`deploy_agents.py`**:

  - `vertexai.init(project=..., location=..., staging_bucket=...)`: Initializes the Vertex AI SDK, specifying a GCS bucket for staging deployment artifacts.
  - `AGENTS_TO_DEPLOY = [birthday_planner_agent]`: Defines which agent object(s) from `src.agents` to deploy.
  - `BASE_REQUIREMENTS`: Lists Python dependencies required by the deployed agent in its runtime environment.
  - `agent_engines.create(...)`: The core function for deploying an agent.
    - `agent_engine=reasoning_engines.AdkApp(agent=agent_object, enable_tracing=True)`: Wraps your ADK agent object (`Agent`) into an `AdkApp`, making it deployable as a Reasoning Engine (which Agent Engine is built upon).
    - `requirements=...`: Specifies runtime dependencies for the agent.
    - `display_name=...`: A user-friendly name for the deployed agent in the GCP console.
    - `extra_packages=["src"]`: Crucial for including your `src` directory (containing all agent code and submodules) in the deployment package. Agent Engine will then be able to import and run your agent logic.

- **`call_remote_agent.py`**:

  - `vertexai.init(project=..., location=...)`: Initializes Vertex AI SDK for client-side operations.
  - `AGENT_ENGINE_RESOURCE_NAME = os.getenv("AGENT_ENGINE_RESOURCE_NAME")`: Retrieves the identifier of your deployed agent.
  - `remote_agent_app = agent_engines.get(AGENT_ENGINE_RESOURCE_NAME)`: Gets a client object to interact with the specified deployed Agent Engine.
  - `remote_agent_app.create_session(user_id=...)`: Creates a new conversation session with the remote agent.
  - `remote_agent_app.stream_query(user_id=..., session_id=..., input={"text": query})`: Sends the user's query to the agent within the context of a session and streams back events (including partial and final responses).
  - **Response Parsing**: The script includes logic to extract the final text from the stream of events.

- **`src/` Directory**:

  - This directory is structured as a Python package.
  - `src/agents/`: Contains the actual ADK agent definitions (e.g., `birthday_planner.py`). These are plain ADK agents like those developed in Part 1 and 2.
  - When `deploy_agents.py` runs with `extra_packages=["src"]`, this entire directory is packaged and made available to the Agent Engine runtime.

- **`.env` File and Environment Variables**:
  - `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_CLOUD_AE_REGION`, `GOOGLE_CLOUD_BUCKET`: Essential for configuring the Vertex AI SDK for deployment.
  - `AGENT_ENGINE_RESOURCE_NAME`: Identifies your deployed agent for remote interaction.

## What's Next?

You've now seen how to deploy an ADK agent to Vertex AI Agent Engine and call it remotely! This opens up possibilities for:

- Building robust, scalable AI applications.
- Integrating ADK agents into larger cloud architectures.
- Managing and versioning agents using cloud infrastructure.

Explore deploying the full `EventOrganizerAgent` (addressing the points above), or try creating and deploying new agents with different capabilities.
