# Model Context Protocol Investigations

## About MCP (Model Context Protocol)

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). MCP provides a standardized way to connect AI models to different data sources and tools.

MCP follows a client-server architecture where:
- **Hosts/Clients**: Programs like Claude Desktop, IDEs, or AI tools that want to access data through MCP
- **MCP Servers**: Lightweight programs that expose specific capabilities through the standardized Model Context Protocol
- **MCP can provide**: Resources (data/files), Tools (functions), and Prompts (templates)

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