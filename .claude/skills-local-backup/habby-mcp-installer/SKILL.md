---
name: habby-mcp-installer
description: Install and configure Habby MCP in OpenCode. Provides access to Habby platform tools and APIs. Triggers on "install habby mcp", "add habby mcp", "configure habby", "setup habby mcp", "habby mcp", or Chinese equivalents like "安装habby mcp", "配置habby", "添加habby mcp".
---

# Habby MCP Installer

Configure Habby MCP server in OpenCode to access Habby platform tools.

## Workflow

### Step 1: Get API Key

Prompt user to obtain their API key:

```
To configure Habby MCP, you need an API key.

Get your API key from: https://identity.habby.com/keys

Please provide your API key once you have it.
```

Wait for user to provide the API key before proceeding.

### Step 2: Configure opencode.jsonc

Once user provides the API key, update or create `opencode.jsonc` in the project root:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "habby-mcp": {
      "type": "remote",
      "url": "https://api.habby.com/mcp",
      "headers": {
        "X-API-Key": "<USER_PROVIDED_API_KEY>"
      },
      "enabled": true
    }
  }
}
```

**If opencode.jsonc already exists:**
- Read the existing file
- Merge the habby-mcp configuration into the existing `mcp` section
- Preserve all other existing configurations

**If opencode.jsonc does not exist:**
- Create a new file with the complete configuration

### Step 3: Confirm Success

After configuration:

```
Habby MCP has been configured successfully.

Restart OpenCode to start using Habby MCP tools.
```
