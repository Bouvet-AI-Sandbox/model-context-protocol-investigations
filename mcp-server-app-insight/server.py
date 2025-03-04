# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server

mcp = FastMCP("Demo",log_level="DEBUG",debug=True, port=8080)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


#if __name__ == "__main__":
#    mcp.run()
# Run with mcp run server.py --transport sse
# Open MCP Inspector with npx @modelcontextprotocol/inspector