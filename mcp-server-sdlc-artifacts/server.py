"""MCP server for important templates in the Software Delivery Lifecycle (SDLC) for the team."""
import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field

# Load environment variables
#load_dotenv()


# Create an MCP server
mcp = FastMCP(
    name="SDLCTemplates", 
    log_level="DEBUG", 
    debug=True, 
    port=8080
)

template_file_map = {
    "decision-log": "decision-log.md",
    "incident-report-postmortem": "incident-report-postmortem.md",
    "user-story": "user-story.md"
}
    

# The templates could be implemented in MCP with resources and prompts. As support for this is generally lacking, we use tools instead.

@mcp.tool()
def get_template_decision_log(
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Get the template used for decision logs in the Software delivery lifecycle of this IT delivery.
    The template is mainly used for Architecture Decision Records (ADRs), but can also be used for other decisions within the delivery.
    """
    return _read_template("decision-log", ctx)

@mcp.tool()
def get_template_incident_report(
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Get the template used for incident reports (aka. postmortem) in the Software delivery lifecycle of this IT delivery.
    The incident report captures the details of an incident, including the timeline, root cause analysis, and action items.
    It is used to document the incident and share the learnings with the team and stakeholders.
    """
    return _read_template("incident-report-postmortem", ctx)    

@mcp.tool()
def get_template_user_story(
    ctx: Context = Field(description="MCP context"),
) -> Dict[str, Any]:
    """Get the template used for user stories in the Software delivery lifecycle of this IT delivery.
    The user story template is used to capture the requirements and acceptance criteria for a feature or functionality.
    It is used to communicate the needs of the users and stakeholders to the development team.
    """
    return _read_template("user-story", ctx)    

def _read_template(template_id: str, ctx: Context):   
    ctx.debug(f"Preparing reading template {template_id}")  


    # Get the file name for the requested template type
    file_name= template_file_map.get(template_id)

    if not file_name:
        ctx.error(f"Unknown template type: {template_id}")
        return f"Error: Template type '{template_id}' not supported"
    
    # Build the file path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", file_name)
    
    ctx.debug(f"Reading template from {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        ctx.error(f"Template file not found: {template_path}")
        return f"Error: Template file '{file_name}' not found"
    except Exception as e:
        ctx.error(f"Error reading template: {str(e)}")
        return f"Error reading template: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

# Alternatively run with: mcp run server.py --transport sse
# Open MCP Inspector with: npx @modelcontextprotocol/inspector mcp run server.py --transport stdio