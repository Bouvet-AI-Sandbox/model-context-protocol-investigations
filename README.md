# Model Context Protocol Investigations

## About MCP (Model Context Protocol)

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). MCP provides a standardized way to connect AI models to different data sources and tools.
It was [introduced by Anthropic in November 2024](https://www.anthropic.com/news/model-context-protocol) and has seen quick adoption in the open source community. Anthropic is in [dialog with other foundational AI companies](https://youtu.be/kQmXtrmQ5Zg?si=pYwsJmTo7DPKiP3t&t=5310) such as OpenAI and [GitHub Copilot is evaluating it](https://github.com/microsoft/vscode-copilot-release/issues/5004).

MCP follows a client-server architecture where:
- **MCP client**: Different types such as LLM chat clients, Code copilots in IDEs and agent frameworks
- **MCP Servers**: Lightweight programs that expose specific capabilities through the standardized Model Context Protocol

![MCP overview](https://github.com/user-attachments/assets/b91c3aa8-3f83-4464-b86b-f547454d5c65)
Overview image from [Building Agents with Model Context Protocol - Full Workshop with Mahesh Murag of Anthropic](https://youtu.be/kQmXtrmQ5Zg?si=iX_eDzF3byUmEVuU&t=287)

Note: The MCP client is configured to use one or more LLMs (not shown in the overview image) and the LLM recommends to the MCP client which MCP server tool to use.

### MCP Servers
MCP servers can provide:
- [Tools](https://modelcontextprotocol.io/docs/concepts/tools) - This is the core functionality and provides a set of function call the LLM used by the MCP client can choose to use
- [Resources](https://modelcontextprotocol.io/docs/concepts/resources) - Similar to tools, but not focused on function calling from an LLM
- [Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) - Templates suggestions an MCP client expose to the end-user

There are SDKs available to help build MCP servers in different languages, including [Python](https://github.com/modelcontextprotocol/python-sdk), [TypeScript](https://github.com/modelcontextprotocol/typescript-sdk), [Java](https://github.com/modelcontextprotocol/java-sdk) and [Kotlin](https://github.com/modelcontextprotocol/kotlin-sdk). We've explored the [Python SDK](https://github.com/modelcontextprotocol/python-sdk) and recommend it.


The [MCP protocol transport layer](https://modelcontextprotocol.io/docs/concepts/transports) consists of Standard Input/Output (stdio) and Server-Sent Events (SSE), but can easily be extended. Today most MCP client mainly use stdio as transport layer but this will likely change in the near future as reflected in the [MCP roadmap](https://modelcontextprotocol.io/development/roadmap).

As MCP servers are lightweight and often require secrets related to actual end-user, we recommend deploying it locally on a developer computer. It should support stdio and sse and be possible to run in a docker container. 

Services such as GitHub and Slack will in the future expose MCP servers over HTTPS and use OAuth for authentication and authorization.

Anthropic is [actively working](https://youtu.be/kQmXtrmQ5Zg?si=UY8DM5LAgO6xfq--&t=4955) on an Official MCP Registry API for discovery of MCP servers.

#### Example MCP Server
The following show the key elements of an MCP server implementation
```
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field

# Load environment variables
load_dotenv()

# Get secrets used by the MCP Server
MY_SECRET = os.getenv("MY_SECRET")

# Validate environment variables
if not MY_SECRET :
    raise ValueError("MY_SECRET must be set in .env file")

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
    #internal method doing the performing the tool call
    return None

# Allow run directly from python
# Alternatively run with: mcp run server.py --transport sse
# or through MCP Inspector with: npx @modelcontextprotocol/inspector
if __name__ == "__main__":
    mcp.run(transport="sse")
```

This results in the follow functional calling definition provided to the LLM choosen by the MCP client
```
{
  "tools": [
    {
      "name": "user_activity",
      "description": "Get a list of all HTTP requests for a specific user in a given duration.\n    \n    Returns Application Insights data including requests, exceptions, and traces.\n    ",
      "inputSchema": {
        "type": "object",
        "properties": {
          "userId": {
            "description": "The email address of the user to get activity for",
            "title": "Userid",
            "type": "string"
          },
          "duration": {
            "default": "P1D",
            "description": "Duration to get activity for in ISO8601 format. Default: P1D (1 day)",
            "title": "Duration",
            "type": "string"
          }
        },
        "required": [
          "userId"
        ],
        "title": "user_activityArguments"
      }
    }
  ]
}
```

### MCP Clients
MCP Clients control the LLM and the end-user interaction (if any). The MCP client is configured with a relevant set of MCP servers. It's up to the LLM to recommend a tool from an MCP server to be used and the MCP client will typically ask the end-user to confirm before initiating the tool call through the MCP server.

Additionally, the MCP clients can provide:
- [Sampling](https://modelcontextprotocol.io/docs/concepts/sampling) - This allows MCP servers to request LLM completions through the MCP client  (not commonly used today)

We've investigated the following MCP clients:
- LLM chat clients - [Codename Goose](https://block.github.io/goose/)
- Code copilots in IDEs -  [Cline](https://github.com/cline/cline), [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- Agent frameworks - Lanchain (through [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters))


## Project Components

### [App GitHub Issues](./app-github-issues/)
A Python application for retrieving GitHub issues and using LLMs to suggest solutions. 
- Fetches issues from a GitHub repository
- Sends issue content to an LLM for analysis
- Being updated to leverage MCP integration

### [App Insight Data Generator](./app-insight-data-generator/)
A tool for generating test data for Azure Application Insights.
- Creates simulated web requests with various status codes and response times
- Logs errors and exceptions
- Configurable through command line arguments

### [App Insight Query for User](./app-insight-query-for-user/)
A simple Python utility to query Azure Application Insights for user activity.
- Retrieves data for a specific user from Application Insights
- Uses a predefined KQL query
- Accessible via REST API

### [MCP Client: Claude Code](./mcp-client-claude-code/)
Implementation of a client using Claude Code (Anthropic's command-line tool).
- Seamless integration with MCP servers
- Configured to connect to GitHub and Application Insights MCP servers
- Uses environment variables for API authentication

### [MCP Client: Goose](./mcp-client-goose/)
Implementation using Goose (an open-source AI agent platform) as an MCP client.
- Configuration for connecting to multiple MCP servers
- Setup instructions for both GitHub and Application Insights servers
- Environment management for secure API key handling

### [MCP Server: App Insight](./mcp-server-app-insight/)
A server providing MCP capabilities for Azure Application Insights data.
- Exposes tools for retrieving user activity data
- Supports querying across requests, exceptions, and traces
- Uses the FastMCP framework for easy implementation

### [MCP Server: DateTime JavaScript](./mcp-server-datetime-javascript/)
A TypeScript implementation of an MCP server for date and time operations.
- Provides current date/time information in various formats
- Supports timezone specification
- Built using the TypeScript MCP SDK

## MCP Recommendations

MCP brings significant benefits to AI application development:

1. **Standardized Integration**: Common interface for AI models to connect with tools and data sources
2. **Enhanced Context**: LLMs can access relevant information on demand
3. **Extensible Framework**: Easy to build new servers for different data sources
4. **Vendor Flexibility**: Switch between different LLM providers maintaining the same MCP tools
5. **Security by Design**: Localized processing with clear permission boundaries
6. **Developer Productivity**: Reusable components across different AI applications
7. **Human-in-the-Loop**: Explicit permission flows for sensitive operations

For organizations building AI solutions, MCP offers a future-proof way to structure AI integrations, reduce development time, and maintain control over AI capabilities.
