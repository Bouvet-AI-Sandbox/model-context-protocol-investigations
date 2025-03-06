# Azure DevOps MCP Server

This is a Model Context Protocol (MCP) server for Azure DevOps integration. It provides tools to interact with Azure DevOps, including retrieving user stories, teams, and projects, as well as creating new user stories.

## Prerequisites

- Python 3.8 or higher
- An Azure DevOps account
- A Personal Access Token (PAT) with appropriate permissions

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the same directory as the server.py file with the following content:

```
AZURE_DEVOPS_ORG=your-organization-name
AZURE_DEVOPS_PAT=your-personal-access-token
```

Replace `your-organization-name` with your Azure DevOps organization name and `your-personal-access-token` with your Azure DevOps Personal Access Token.

## Running the Server

You can run the server using one of the following commands:

```bash
python server.py
```

or

```bash
mcp run server.py --transport sse
```

## Available Tools

The server provides the following tools:

### get_user_stories

Retrieves user stories from Azure DevOps for a specific team project.

Parameters:
- `team_project`: The team project name (required)
- `team`: The team name (optional)
- `state`: Filter by state (e.g., 'New', 'Active', 'Closed') (optional)
- `assigned_to`: Filter by assigned user email (optional)
- `top`: Number of work items to return (default: 100)

### get_teams

Gets teams from Azure DevOps.

Parameters:
- `team_project`: The team project name (optional)

### get_team_projects

Gets team projects from Azure DevOps.

No parameters required.

### create_user_story

Creates a new user story in Azure DevOps.

Parameters:
- `team_project`: The team project name (required)
- `title`: Title of the user story (required)
- `description`: Description of the user story (optional)
- `assigned_to`: Email of the user to assign the story to (optional)

## MCP Integration

To use this server with MCP, add it to your MCP settings file:

```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "python",
      "args": ["/path/to/mcp-server-azure-devops/server.py"],
      "env": {
        "AZURE_DEVOPS_ORG": "your-organization-name",
        "AZURE_DEVOPS_PAT": "your-personal-access-token"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Testing

You can test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```
