#!/usr/bin/env python3
"""MCP server for Azure DevOps data retrieval."""
import os
from typing import Dict, Any, List, Optional

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field

# Load environment variables
load_dotenv()

# Get Azure DevOps credentials
AZURE_DEVOPS_ORG = os.getenv("AZURE_DEVOPS_ORG")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

# Validate environment variables
if not AZURE_DEVOPS_ORG or not AZURE_DEVOPS_PAT:
    raise ValueError("AZURE_DEVOPS_ORG and AZURE_DEVOPS_PAT must be set in .env file")

# Create an MCP server
mcp = FastMCP(
    name="AzureDevOpsServer",
    log_level="DEBUG",
    debug=True,
    port=8081
)

def _get_auth_header():
    """Create the authorization header for Azure DevOps API."""
    import base64
    auth_str = f":{AZURE_DEVOPS_PAT}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    return {"Authorization": f"Basic {encoded_auth}"}

@mcp.tool()
def get_user_stories(
    team_project: str = Field(description="The team project name"),
    team: Optional[str] = Field(description="The team name (optional)", default=None),
    state: Optional[str] = Field(description="Filter by state (e.g., 'New', 'Active', 'Closed')", default=None),
    assigned_to: Optional[str] = Field(description="Filter by assigned user email", default=None),
    top: int = Field(description="Number of work items to return", default=100),
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Get user stories from Azure DevOps for a specific team project.
    
    Returns a list of user stories with details like ID, title, state, and assigned to.
    """
    # Construct the base URL for Azure DevOps API
    base_url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}"
    
    # Build the WIQL query
    wiql_query = {
        "query": "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.CreatedDate], [System.Description] "
                 "FROM WorkItems "
                 "WHERE [System.WorkItemType] = 'User Story' "
    }
    
    # Add filters if provided
    conditions = []
    if team_project:
        conditions.append(f"[System.TeamProject] = '{team_project}'")
    if state:
        conditions.append(f"[System.State] = '{state}'")
    if assigned_to:
        conditions.append(f"[System.AssignedTo] = '{assigned_to}'")
    
    # Add conditions to the query
    if conditions:
        wiql_query["query"] += "AND " + " AND ".join(conditions)
    
    # Add order by
    wiql_query["query"] += " ORDER BY [System.CreatedDate] DESC"
    
    ctx.debug(f"WIQL Query: {wiql_query['query']}")
    
    # Make the WIQL API request
    wiql_url = f"{base_url}/_apis/wit/wiql?api-version=6.0"
    headers = _get_auth_header()
    headers["Content-Type"] = "application/json"
    
    wiql_response = requests.post(wiql_url, json=wiql_query, headers=headers)
    
    if wiql_response.status_code != 200:
        ctx.error(f"Error in WIQL query: {wiql_response.status_code}, {wiql_response.text}")
        return {"error": f"Failed to query work items: {wiql_response.text}"}
    
    wiql_data = wiql_response.json()
    
    # Extract work item IDs
    work_item_ids = [item["id"] for item in wiql_data.get("workItems", [])]
    
    if not work_item_ids:
        return {"user_stories": []}
    
    # Limit the number of work items
    work_item_ids = work_item_ids[:top]
    
    # Get work item details
    work_items_url = f"{base_url}/_apis/wit/workitems?ids={','.join(map(str, work_item_ids))}&api-version=6.0&$expand=all"
    work_items_response = requests.get(work_items_url, headers=headers)
    
    if work_items_response.status_code != 200:
        ctx.error(f"Error fetching work items: {work_items_response.status_code}, {work_items_response.text}")
        return {"error": f"Failed to fetch work items: {work_items_response.text}"}
    
    work_items_data = work_items_response.json()
    
    # Process and return the work items
    user_stories = []
    for item in work_items_data.get("value", []):
        fields = item.get("fields", {})
        user_story = {
            "id": item.get("id"),
            "title": fields.get("System.Title"),
            "state": fields.get("System.State"),
            "assigned_to": fields.get("System.AssignedTo", {}).get("displayName") if fields.get("System.AssignedTo") else None,
            "created_date": fields.get("System.CreatedDate"),
            "description": fields.get("System.Description"),
            "url": item.get("url")
        }
        user_stories.append(user_story)
    
    return {"user_stories": user_stories}

@mcp.tool()
def get_teams(
    team_project: Optional[str] = Field(description="The team project name (optional)", default=None),
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Get teams from Azure DevOps.
    
    If team_project is provided, returns teams for that project.
    Otherwise, returns all teams in the organization.
    """
    # Construct the base URL for Azure DevOps API
    base_url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}"
    
    # API URL for teams
    if team_project:
        teams_url = f"{base_url}/_apis/projects/{team_project}/teams?api-version=6.0"
    else:
        teams_url = f"{base_url}/_apis/teams?api-version=6.0"
    
    headers = _get_auth_header()
    
    teams_response = requests.get(teams_url, headers=headers)
    
    if teams_response.status_code != 200:
        ctx.error(f"Error fetching teams: {teams_response.status_code}, {teams_response.text}")
        return {"error": f"Failed to fetch teams: {teams_response.text}"}
    
    teams_data = teams_response.json()
    
    # Process and return the teams
    teams = []
    for team in teams_data.get("value", []):
        team_info = {
            "id": team.get("id"),
            "name": team.get("name"),
            "description": team.get("description"),
            "project_name": team.get("projectName"),
            "url": team.get("url")
        }
        teams.append(team_info)
    
    return {"teams": teams}

@mcp.tool()
def get_team_projects(
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Get team projects from Azure DevOps.
    
    Returns a list of all team projects in the organization.
    """
    # Construct the base URL for Azure DevOps API
    base_url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}"
    
    # API URL for projects
    projects_url = f"{base_url}/_apis/projects?api-version=6.0"
    
    headers = _get_auth_header()
    
    projects_response = requests.get(projects_url, headers=headers)
    
    if projects_response.status_code != 200:
        ctx.error(f"Error fetching projects: {projects_response.status_code}, {projects_response.text}")
        return {"error": f"Failed to fetch projects: {projects_response.text}"}
    
    projects_data = projects_response.json()
    
    # Process and return the projects
    projects = []
    for project in projects_data.get("value", []):
        project_info = {
            "id": project.get("id"),
            "name": project.get("name"),
            "description": project.get("description"),
            "url": project.get("url"),
            "state": project.get("state"),
            "visibility": project.get("visibility")
        }
        projects.append(project_info)
    
    return {"projects": projects}

@mcp.tool()
def create_user_story(
    team_project: str = Field(description="The team project name"),
    title: str = Field(description="Title of the user story"),
    description: Optional[str] = Field(description="Description of the user story", default=None),
    assigned_to: Optional[str] = Field(description="Email of the user to assign the story to", default=None),
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Create a new user story in Azure DevOps.
    
    Returns the created user story details.
    """
    # Construct the base URL for Azure DevOps API
    base_url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}"
    
    # API URL for creating work item
    create_url = f"{base_url}/{team_project}/_apis/wit/workitems/$User Story?api-version=6.0"
    
    headers = _get_auth_header()
    headers["Content-Type"] = "application/json-patch+json"
    
    # Prepare the document for creating a work item
    document = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title
        }
    ]
    
    if description:
        document.append({
            "op": "add",
            "path": "/fields/System.Description",
            "value": description
        })
    
    if assigned_to:
        document.append({
            "op": "add",
            "path": "/fields/System.AssignedTo",
            "value": assigned_to
        })
    
    ctx.debug(f"Creating user story: {document}")
    
    create_response = requests.post(create_url, json=document, headers=headers)
    
    if create_response.status_code not in (200, 201):
        ctx.error(f"Error creating user story: {create_response.status_code}, {create_response.text}")
        return {"error": f"Failed to create user story: {create_response.text}"}
    
    created_item = create_response.json()
    
    # Process and return the created work item
    fields = created_item.get("fields", {})
    user_story = {
        "id": created_item.get("id"),
        "title": fields.get("System.Title"),
        "state": fields.get("System.State"),
        "assigned_to": fields.get("System.AssignedTo", {}).get("displayName") if fields.get("System.AssignedTo") else None,
        "created_date": fields.get("System.CreatedDate"),
        "description": fields.get("System.Description"),
        "url": created_item.get("url")
    }
    
    return {"user_story": user_story}

if __name__ == "__main__":
    mcp.run(transport="sse")

# Alternatively run with: mcp run server.py --transport sse
# Open MCP Inspector with: npx @modelcontextprotocol/inspector