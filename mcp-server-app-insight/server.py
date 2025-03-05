# server.py
from mcp.server.fastmcp import FastMCP, Context
import requests
from dotenv import load_dotenv
import os
from pydantic import Field

# Create an MCP server
mcp = FastMCP("Demo",log_level="DEBUG",debug=True, port=8080)

load_dotenv()
APPLICATION_INSIGHT_APP_ID = os.getenv("APPLICATION_INSIGHT_APP_ID")
APPLICATION_INSIGHT_API_KEY = os.getenv("APPLICATION_INSIGHT_API_KEY")

# Define a tool for the MCP server
@mcp.tool()
def user_activity(
        userId: str = Field(description="The email adress of the user to get activity for"), 
        duration: str= Field(description="Duration to get activity for in ISO8601 format. Has default value P1D (1 day)", default="P1D"),
        ctx: Context= Field(description=""),
    ) -> str:
    """Get a list of all http requests for a specific user in a given duration. """
    return _app_insight_call(userId, duration,ctx)


def _app_insight_call(userId: str, duration: str, ctx: Context) -> str:
    # Define KQL query. We're merging in exception and traces into a single line item
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
        | project timestamp, name,url, resultCode, duration, outerType, outerMessage, innermostType, innermostMessage, exceptionStackTrace, traceMessage, traceSeverityLevel, traceFromPath, traceFromFunction
    """

    # Old simple query 
    #query = f"""
    #requests 
    #| where customDimensions['User.AuthenticatedUserId'] == "{userId}"
    #| project timestamp, name, url, resultCode, duration
    #"""

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
        data = response.json()
        return data
    else:
        print("Error:", response.status_code, response.text)
        return None

if __name__ == "__main__":
    mcp.run(transport="sse")

# alternatively run with Run with mcp run server.py --transport sse
# and Open MCP Inspector with npx @modelcontextprotocol/inspector