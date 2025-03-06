# Installation

`curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash`


### .env for LLM and MCP servers
```
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://futurumopenai-eastus.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_...
```

Add to environment variable through
```
set +a
source .env
set -a
```

## Configure LLM
`goose configure`



## Add MCP servers
### mcp-server-app-insight
`goose configure`

```
This will update your existing config file
  if you prefer, you can edit it directly at /home/vscode/.config/goose/config.yaml

┌   goose-configure 
│
◇  What would you like to configure?
│  Add Extension 
│
◇  What type of extension would you like to add?
│  Remote Extension 
│
◇  What would you like to call this extension?
│  user-activity
│
◇  What is the SSE endpoint URI?
│  http://127.0.0.1:8080/sse
│
◇  Please set the timeout for this tool (in secs):
│  300
```

### mcp-server-github
`goose configure`

```
This will update your existing config file
  if you prefer, you can edit it directly at /home/vscode/.config/goose/config.yaml

┌   goose-configure 
│
◇  What would you like to configure?
│  Add Extension 
│
◇  What type of extension would you like to add?
│  Command-line Extension 
│
◇  What would you like to call this extension?
│  github
│
◇  What command should be run?
│  npx -y @modelcontextprotocol/server-github
│
◇  Please set the timeout for this tool (in secs):
│  300
│
◇  Would you like to add environment variables?
│  Yes 
│
◇  Environment variable name:
│  GITHUB_PERSONAL_ACCESS_TOKEN
│
◇  Environment variable value:
│  ...
│
◇  Add another environment variable?
│  No
```

# Run
`goose session`

### Attempt at secure storage in docker devcontainer - SKIP THIS!
`sudo apt-get update && sudo apt-get install -y dbus dbus-x11 libdbus-1-3 gnome-keyring`
`dbus-launch --sh-syntax` or `eval $(dbus-launch --auto-syntax)` (not sure which is best)

`gnome-keyring-daemon --component=secrets --daemonize --unlock`
(ctrl+d)
Troubleshooting
- sessions
`dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply / org.freedesktop.DBus.ListNames`

Does https://github.com/t1m0thyj/unlock-keyring/blob/main/index.js help?

Does https://github.com/block/goose/blob/3b8d986a668065d821dbb51d63d0510d4d2e8ca0/.github/workflows/ci.yaml#L28C12-L28C87 help