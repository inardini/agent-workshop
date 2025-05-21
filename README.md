# Workshop: Building Advanced Conversational AI with ADK, MCP, and Vertex AI Agent Engine

Welcome to this hands-on workshop where you'll learn to build, deploy, and manage sophisticated conversational AI agents using Google's Agent Development Kit (ADK), Managed Cloud Platform (MCP) for tools, and Vertex AI Agent Engine.

## Workshop Overview

This workshop is divided into three progressive parts, each building upon the last. You will start by creating a simple local agent, then enhance it with external tools hosted on a cloud service, and finally deploy your agent to a fully managed cloud environment.

- **Part 1: Your First ADK Agent (`birthday_planner_agent`)**
  - Learn the fundamentals of the Agent Development Kit (ADK).
  - Build and run a standalone conversational agent locally.
  - Define agent behavior using LLM instructions.
- **Part 2: Hierarchical Agents & MCP Tools (`event_management_local_agent_system`)**
  - Explore creating a system of multiple agents (hierarchical agents).
  - Learn to expose Python functions as tools using FastMCP.
  - Deploy an MCP tool server to Google Cloud Run.
  - Integrate ADK agents with externally hosted MCP tools.
- **Part 3: Deploying to Vertex AI Agent Engine (`event_management_remote_agent_system`)**
  - Package ADK agents for cloud deployment.
  - Deploy an ADK agent as a service on Vertex AI Agent Engine.
  - Interact with your cloud-hosted agent remotely.

## Learning Objectives

By the end of this workshop, you will be able to:

- Develop conversational agents using the Google Agent Development Kit (ADK).
- Design agents with specific instructions, personalities, and goals.
- Create hierarchical agent systems where agents can delegate tasks to one another.
- Build and deploy tool servers using FastMCP to extend agent capabilities.
- Integrate ADK agents with external tools hosted on Managed Cloud Platform (MCP) services.
- Deploy ADK agents to Vertex AI Agent Engine for scalable, managed hosting.
- Interact with deployed agents as remote services.
- Understand the end-to-end workflow of developing and deploying advanced AI agents on Google Cloud.

## Prerequisites

Before you begin, please ensure you have the following:

- **Google Cloud Platform (GCP) Account:** With billing enabled. You can sign up for a [free trial](https://cloud.google.com/free).
- **GCP Project:** A dedicated project created in your GCP account.
- **Google Cloud SDK:** Installed and initialized. [Installation Guide](https://cloud.google.com/sdk/docs/install).
  - Ensure you've run `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`.
- **Python:** Version 3.9 or higher installed.
- **Git:** For cloning this repository.
- **Docker:** Installed and running (required for Part 2 and implicitly by some gcloud commands for Part 3). [Installation Guide](https://docs.docker.com/get-docker/).
- **Basic Familiarity:**
  - Comfort with the command line/terminal.
  - Basic Python programming knowledge.
  - A conceptual understanding of Large Language Models (LLMs) and AI agents.

**Note:** Each part of the workshop will have its own detailed `README.md` file with specific setup instructions and dependencies for that part.

## One-Time GCP Environment Setup

Before starting Part 1, ensure your Google Cloud project is configured correctly. Run the following commands in your terminal.

**Important:** The user account or service account executing these `gcloud` commands must have sufficient permissions to enable services and grant IAM roles in the target project (e.g., `Owner` or `Organization Administrator` for some of these).

1.  **Set Project ID Variable:**
    (Ensure `gcloud` is configured to your target project: `gcloud config set project YOUR_PROJECT_ID`)

    ```bash
    export PROJECT_ID=$(gcloud config get-value project)
    echo "PROJECT_ID is set to: $PROJECT_ID"
    ```

2.  **Enable Necessary Google Cloud APIs:**

    ```bash
    gcloud services enable \
        aiplatform.googleapis.com \
        cloudbuild.googleapis.com \
        artifactregistry.googleapis.com \
        run.googleapis.com \
        iam.googleapis.com \
        cloudresourcemanager.googleapis.com \
        storage.googleapis.com \
        compute.googleapis.com \
        serviceusage.googleapis.com --project=${PROJECT_ID}
    ```

    This command enables Vertex AI, Cloud Build, Artifact Registry, Cloud Run, IAM, Cloud Resource Manager, Cloud Storage, Compute Engine (useful for default service accounts), and Service Usage (for managing APIs).

3.  **Identify Default Compute Service Account:**
    This workshop will grant necessary permissions to the default Compute Engine service account, which is often used by deployed services for simplicity.

    ```bash
    export SERVICE_ACCOUNT_EMAIL=$(gcloud iam service-accounts list \
        --filter="displayName:'Compute Engine default service account'" \
        --format="value(email)" \
        --project=${PROJECT_ID})
    echo "Using Service Account: $SERVICE_ACCOUNT_EMAIL"
    ```

    If this command doesn't return an email (e.g., if the Compute Engine API was just enabled or the default SA was removed), you might need to ensure it exists or create/select another service account and update `SERVICE_ACCOUNT_EMAIL` accordingly. For most projects, it will exist.

4.  **Grant IAM Permissions to the Service Account:**
    These roles allow the service account (and services running as it, like Cloud Run or Agent Engine) to perform necessary actions.

    ```bash
    # Vertex AI Admin (Full control over Vertex AI resources, including Agent Engine deployment)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/aiplatform.admin"

    # Artifact Registry Admin (To manage repositories and images for containers)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/artifactregistry.admin"

    # Cloud Build Editor (To allow Cloud Build to execute builds for deployment)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/cloudbuild.builds.editor"

    # Cloud Run Admin (To deploy and manage Cloud Run services, e.g., for MCP tools)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/run.admin"

    # Service Account User (To allow services to run as this service account or impersonate it)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/iam.serviceAccountUser"

    # Storage Admin (Full control over GCS buckets, e.g., for Vertex AI staging)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/storage.admin"

    # Logging Writer (To allow services to write logs to Cloud Logging)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/logging.logWriter"
    ```

With these APIs enabled and permissions granted, your GCP project should be ready for the workshop activities.

## Repository Structure

This repository is organized into directories, each corresponding to a part of the workshop:

```
├── README.md # This main README file
├── birthday_planner_agent/ # Part 1: Your First ADK Agent
│ └── README.md
├── event_management_local_agent_system/ # Part 2: Hierarchical Agents & MCP Tools
│ └── README.md
└── event_management_remote_agent_system/ # Part 3: Deploying to Vertex AI Agent Engine
└── README.md
```

## Getting Started

1.  **Clone this Repository:**

    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Perform the One-Time GCP Environment Setup:** (As described in the section above).

3.  **Navigate to Part 1:**
    It is highly recommended to complete the workshop parts sequentially. Start with Part 1:

    ```bash
    cd birthday_planner_agent
    ```

4.  **Follow the Part-Specific README:**
    Open and follow the instructions in the `README.md` file located within the `birthday_planner_agent` directory. This will guide you through the setup and exercises for Part 1.

5.  **Proceed to Subsequent Parts:**
    Once you complete Part 1, move on to Part 2 (`event_management_local_agent_system`) and then Part 3 (`event_management_remote_agent_system`), following their respective `README.md` files.

## General Tips for the Workshop

- **Virtual Environments:** It's good practice to use Python virtual environments for each part to manage dependencies.
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```
- **Environment Variables:** Many parts will rely on environment variables (e.g., `GOOGLE_CLOUD_PROJECT`). These are typically managed using a `.env` file in each part's directory. Make sure to create and populate these files as instructed.
- **Regions:** Pay close attention to GCP regions. Use the same region consistently for your resources (GCS buckets, Cloud Run services, Vertex AI Agent Engine deployments) to avoid issues and potential costs.
- **Troubleshooting:**
  - Double-check API enablement and IAM permissions in your GCP project if you encounter errors.
  - Verify model names and their availability in your chosen Vertex AI region.
  - Read error messages carefully—they often provide clues!

We hope you find this workshop informative and engaging. Happy building!
