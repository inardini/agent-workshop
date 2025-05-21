FROM python:3.12-slim

WORKDIR /app

# Copy only the tools directory contents needed for the server
COPY requirements.txt calendar_tools.py calendar_mcp_server.py ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to run the FastMCP server
# Ensure calendar_mcp_server.py is executable or called via python
CMD ["python", "calendar_mcp_server.py"]