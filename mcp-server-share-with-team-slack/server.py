"""MCP server for sharing information with team slack channel. Requires workflow setup on slack side."""
import os
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field

# Load environment variables
load_dotenv()

# Get Application Insights credentials
SLACK_WORKFLOW_SECRET_URI = os.getenv("SLACK_WORKFLOW_SECRET_URI")
MY_SLACK_MEMBER_ID = os.getenv("MY_SLACK_MEMBER_ID")

# Validate environment variables
if not SLACK_WORKFLOW_SECRET_URI or not MY_SLACK_MEMBER_ID:
    raise ValueError("SLACK_WORKFLOW_SECRET_URI and MY_SLACK_MEMBER_ID must be set in .env file")

# Create an MCP server
mcp = FastMCP(
    name="ShareWithTeamSlack", 
    log_level="DEBUG", 
    debug=True, 
    port=8080
)


@mcp.tool()
def share_with_team_slack(
    content: str = Field(description="The content to share with the team slack channel. It could be a quick message or a more technical analysis. Use markdown subset mrkdown from slack and strive for high readability on slack. Emojis are ok to use"), 
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Share content with the team slack channel. 
    The team slack channel is used to communicate with the team members in our delivery for all parts of the Software Delivery Lifecycle. 
    The team has solid technical knowledge and understanding.
    Use short precise content with high readability on slack (slack uses mrkdown which is a subset of markdown)
    """
    return _slack_workflow_call(content, ctx)


def _slack_workflow_call(content: str, ctx: Context):

    # Construct the REST API URL
    url = SLACK_WORKFLOW_SECRET_URI

    ctx.debug(f"Preparing request to slack webhook")

    # Set the parameters and headers, including the API key
    payload = {
        "content": content,
        "posted-by": MY_SLACK_MEMBER_ID
    }

    # Make the POST request - using json parameter to send JSON data in the request body
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        ctx.error(f"Error: {response.status_code}, {response.text}")
        return None


if __name__ == "__main__":
    mcp.run(transport="stdio")

# Alternatively run with: mcp run server.py --transport sse
# Open MCP Inspector with: npx @modelcontextprotocol/inspector