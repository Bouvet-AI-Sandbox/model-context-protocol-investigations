# Claude code as MCP client

[claude code overview](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)

Note: Claude Code is research preview and requires an invitation to use.

## Install
`npm install -g @anthropic-ai/claude-code`

## Add MCP server

### Prerequisite - Add env variables for MCP server
```
GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_...
APPLICATION_INSIGHT_APP_ID=...
APPLICATION_INSIGHT_API_KEY=...
```

Add to environment variable through
```
set +a
source .env
set -a
```

### GitHub - MCP server
[GitHub MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)

`claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PERSONAL_ACCESS_TOKEN -- npx -y @modelcontextprotocol/server-github`

### GitHub - Bouvet user activity with Azure applicaton insight
[Bouvet user activity with Azure applicaton insight](https://github.com/Bouvet-AI-Sandbox/mcp-bug-triage/tree/main/mcp-server-app-insight)

`claude mcp add user-activity -e APPLICATION_INSIGHT_APP_ID=$APPLICATION_INSIGHT_APP_ID -e APPLICATION_INSIGHT_API_KEY=$APPLICATION_INSIGHT_API_KEY -- mcp run /workspaces/mcp-bug-triage/mcp-server-app-insight/server.py --transport stdio`