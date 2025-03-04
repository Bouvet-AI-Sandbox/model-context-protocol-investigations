# server.py
from mcp.server.fastmcp import FastMCP, Context
import requests
from dotenv import load_dotenv
import os

# Create an MCP server
mcp = FastMCP("Demo",log_level="DEBUG",debug=True, port=8080)

load_dotenv()
APPLICATION_INSIGHT_APP_ID = os.getenv("APPLICATION_INSIGHT_APP_ID")
APPLICATION_INSIGHT_API_KEY = os.getenv("APPLICATION_INSIGHT_API_KEY")

# Define a tool for the MCP server
@mcp.tool()
def user_activity(userId: str, duration: str, ctx: Context) -> str:
    """Get a list of all http requests for a specific user in a given duration. The duration should be in ISO8601 format and has default value P1D (1 day)"""
    return _app_insight_call(userId, duration,ctx)


def _app_insight_call(userId: str, duration: str, ctx: Context) -> str:
    # Define your KQL query and timespan (e.g., last 1 day)
    query = f"""
    requests 
    | where customDimensions['User.AuthenticatedUserId'] == "{userId}"
    | project timestamp, name, url, resultCode, duration
    """
    timespan = "P1D"  # ISO 8601 duration format for 1 day


    # Construct the REST API URL
    url = f"https://api.applicationinsights.io/v1/apps/{APPLICATION_INSIGHT_APP_ID}/query"

    ctx.info(f"Preparing request to {url}")

    # Set the parameters and headers, including the API key
    params = {
        "query": query,
        "timespan": timespan
    }
    headers = {
        "x-api-key": APPLICATION_INSIGHT_API_KEY
    }

    # Make the GET request
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error:", response.status_code, response.text)
        return None

#if __name__ == "__main__":
#    mcp.run()
# Run with mcp run server.py --transport sse
# Open MCP Inspector with npx @modelcontextprotocol/inspector