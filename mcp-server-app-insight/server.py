# server.py
"""MCP server for Application Insights data retrieval."""
import os
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field

# Load environment variables
load_dotenv()

# Get Application Insights credentials
APPLICATION_INSIGHT_APP_ID = os.getenv("APPLICATION_INSIGHT_APP_ID")
APPLICATION_INSIGHT_API_KEY = os.getenv("APPLICATION_INSIGHT_API_KEY")

# Validate environment variables
if not APPLICATION_INSIGHT_APP_ID or not APPLICATION_INSIGHT_API_KEY:
    raise ValueError("APPLICATION_INSIGHT_APP_ID and APPLICATION_INSIGHT_API_KEY must be set in .env file")

# Create an MCP server
mcp = FastMCP(
    name="AppInsightsServer", 
    log_level="DEBUG", 
    debug=True, 
    port=8080
)


@mcp.tool()
def user_activity(
    userId: str = Field(description="The email address of the user to get activity for"), 
    duration: str = Field(description="Duration to get activity for in ISO8601 format. Default: P1D (1 day)", default="P1D"),
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Get a list of all HTTP requests for a specific user in a given duration.
    
    Returns Application Insights data including requests, exceptions, and traces.
    """
    return _app_insight_call(userId, duration, ctx)


def _app_insight_call(userId: str, duration: str, ctx: Context) -> Optional[Dict[str, Any]]:
    """Make a query to Application Insights API.
    
    Args:
        userId: The email address of the user to get activity for
        duration: Duration to get activity for in ISO8601 format
        ctx: MCP context
        
    Returns:
        Dictionary containing the Application Insights data or None if the request failed
    """
    # Define KQL query - merging requests, exceptions, and traces into a single result
    query = f"""
        requests
        | where customDimensions['User.AuthenticatedUserId'] == "{userId}"        
        | join kind=leftouter (
            exceptions
            | project operation_Id, outerType, outerMessage, innermostType, innermostMessage, exceptionStackTrace=details[0].rawStack
        ) on operation_Id
        | join kind=leftouter (
            traces
            | project operation_Id, traceMessage = message, traceSeverityLevel = severityLevel, traceFromPath=customDimensions["code.filepath"], traceFromFunction=strcat(tostring(customDimensions["code.function"]), ":",tostring(customDimensions["code.lineno"]))
        ) on operation_Id
        | project timestamp, name, url, resultCode, duration, outerType, outerMessage, innermostType, innermostMessage, exceptionStackTrace, traceMessage, traceSeverityLevel, traceFromPath, traceFromFunction
    """

    # Construct the REST API URL
    url = f"https://api.applicationinsights.io/v1/apps/{APPLICATION_INSIGHT_APP_ID}/query"

    ctx.debug(f"Preparing request to {url}")

    # Set the parameters and headers, including the API key
    params = {
        "query": query,
        "timespan": duration
    }
    headers = {
        "x-api-key": APPLICATION_INSIGHT_API_KEY
    }

    # Make the GET request
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        ctx.error(f"Error: {response.status_code}, {response.text}")
        return None


if __name__ == "__main__":
    mcp.run(transport="sse")

# Alternatively run with: mcp run server.py --transport sse
# Open MCP Inspector with: npx @modelcontextprotocol/inspector