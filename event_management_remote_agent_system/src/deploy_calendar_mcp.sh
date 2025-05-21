#!/bin/bash

# Script to deploy the FastMCP Calendar Server to Google Cloud Run
# and update the .env file with its URL.

# Configuration
DEFAULT_SERVICE_NAME="adk-calendar-mcp-service"
TOOLS_DIR="./tools" 
ENV_FILE=".env"

# Helper Functions
print_usage() {
  echo "Usage: $0 [GCP_PROJECT_ID] [GCP_REGION]"
  echo "If arguments are not provided, the script will try to use"
  echo "GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION environment variables,"
  echo "or prompt for them."
}

check_command() {
  if ! command -v "$1" &> /dev/null; then
    echo "Error: '$1' command not found. Please ensure it's installed and in your PATH."
    exit 1
  fi
}

# Pre-flight Checks
check_command "gcloud"

# Determine Project ID and Region
GCP_PROJECT_ID="${1:-${GOOGLE_CLOUD_PROJECT}}"
GCP_REGION="${2:-${GOOGLE_CLOUD_LOCATION}}"

if [ -z "$GCP_PROJECT_ID" ]; then
  read -r -p "Enter your Google Cloud Project ID: " GCP_PROJECT_ID
  if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP Project ID is required."
    print_usage
    exit 1
  fi
fi

if [ -z "$GCP_REGION" ]; then
  read -r -p "Enter your Google Cloud Region (e.g., us-central1): " GCP_REGION
  if [ -z "$GCP_REGION" ]; then
    echo "Error: GCP Region is required."
    print_usage
    exit 1
  fi
fi

echo "--------------------------------------------------"
echo "Deploying FastMCP Calendar Server to Cloud Run"
echo "Project: $GCP_PROJECT_ID"
echo "Region:  $GCP_REGION"
echo "Service: $DEFAULT_SERVICE_NAME"
echo "Source:  $TOOLS_DIR"
echo "--------------------------------------------------"

# Navigate to tools directory for deployment
if [ ! -d "$TOOLS_DIR" ]; then
    echo "Error: Tools directory '$TOOLS_DIR' not found. Make sure you are running this script from the 'event_management_system' directory."
    exit 1
fi
current_dir=$(pwd)
cd "$TOOLS_DIR" || exit

# Deploy to Cloud Run
echo "Deploying to Cloud Run... This may take a few minutes."
SERVICE_URL=$(gcloud run deploy "$DEFAULT_SERVICE_NAME" \
    --source . \
    --project "$GCP_PROJECT_ID" \
    --region "$GCP_REGION" \
    --platform "managed" \
    --allow-unauthenticated \
    --port 8080 \
    --format="value(status.url)") 

if [ -z "$SERVICE_URL" ]; then
    echo "Error: Cloud Run deployment failed or service URL not captured."
    cd "$current_dir" || exit
    exit 1
fi

echo "Cloud Run service deployed successfully."
echo "Service URL: $SERVICE_URL"

# Navigate back to the original directory
cd "$current_dir" || exit

# Update .env file
MCP_SERVICE_FULL_URL="${SERVICE_URL}/sse"
ENV_VAR_NAME="MCP_CALENDAR_SERVICE_URL"
EXPORT_LINE="export ${ENV_VAR_NAME}=\"${MCP_SERVICE_FULL_URL}\""

echo "Updating $ENV_FILE..."

# Create a temporary file for robust updating
TMP_ENV_FILE="${ENV_FILE}.tmp.$$"

# If .env file exists, filter out old definitions of the variable
if [ -f "$ENV_FILE" ]; then
    grep -vE "^export ${ENV_VAR_NAME}=|^${ENV_VAR_NAME}=" "$ENV_FILE" > "$TMP_ENV_FILE"
else
    touch "$TMP_ENV_FILE" # Create tmp file if .env doesn't exist
fi

# Append the new line with export
if [ -s "$TMP_ENV_FILE" ] && [ "$(tail -c1 "$TMP_ENV_FILE"; echo x)" != $'\nx' ]; then
    echo "" >> "$TMP_ENV_FILE"
fi
echo "${EXPORT_LINE}" >> "$TMP_ENV_FILE"

# Replace the old .env file with the new one
mv "$TMP_ENV_FILE" "$ENV_FILE"

echo "Ensured ${EXPORT_LINE} is in $ENV_FILE."

echo "--------------------------------------------------"
echo "Deployment complete!"
echo "FastMCP Calendar Server URL: ${MCP_SERVICE_FULL_URL}"
echo "This URL has been set as ${ENV_VAR_NAME} in your ${ENV_FILE}"
echo "If your shell session sources '.env', re-source it (e.g., 'source .env')"
echo "or restart your ADK Python application for changes to take effect."
echo "--------------------------------------------------"

exit 0