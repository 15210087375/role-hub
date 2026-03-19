---
name: grok-mcp-installer
description: |
  Install and configure Grok MCP (xAI search) in OpenCode. Provides web search and X/Twitter search via Grok API.
  
  Triggers: "install grok mcp", "add grok search", "configure grok", "setup xai search", 
  "grok mcp", "xai mcp", "install xai", "add web search mcp", "add x search",
  "安装grok", "配置grok", "添加grok搜索"
---

# Grok MCP Installer

## Workflow

### Step 1: Clone and Build

Run these commands:

```bash
mkdir -p ~/mcp-servers
git clone https://habby.ghe.com/habby/grokmcp.git ~/mcp-servers/grok-search
```

**If git clone fails (permission denied / authentication error):**

### Step 1.1 自动安装 GitHub 配置助手

首先检查是否已安装 skills-hub-client：

```bash
ls ~/.claude/skills/skills-hub-client/SKILL.md 2>/dev/null && echo "HAS_HUB" || echo "NO_HUB"
```

**如果输出 `HAS_HUB`：**

输出消息：
```
❌ Git clone 失败，需要配置 Habby 企业版 GitHub 权限。
🔄 正在自动安装 habby-github-setup skill...
```

然后调用 skill 工具安装：
```
Tool: skill
Parameters:
  name: "skills-hub-client"
```

加载 skills-hub-client 后，执行搜索和安装流程：
```bash
python3 ~/.claude/skills/skills-hub-client/scripts/search_skills.py "habby-github-setup" --limit 5
```

根据搜索结果，下载安装 skill：
```bash
python3 ~/.claude/skills/skills-hub-client/scripts/download_skill.py <skill_id> --output ~/.claude/skills/ --force
```

安装完成后，调用 habby-github-setup skill 完成 GitHub 配置，然后重新执行 Step 1 的 git clone。

**如果输出 `NO_HUB`：**

停止执行，输出以下消息：

```
❌ Git clone 失败，你需要先配置 Habby 企业版 GitHub 权限。

请说「安装 habby-github-setup skill」或「download skill habby-github-setup」来安装配置助手。
```

**If clone succeeds**, continue with build:

### Step 1.2: Check npm availability

```bash
command -v npm >/dev/null 2>&1 && echo "HAS_NPM" || echo "NO_NPM"
```

**If output is `NO_NPM`:**

Install Node.js via nvm (official recommended method from nodejs.org):

```bash
# Download and install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# Load nvm without restarting shell
\. "$HOME/.nvm/nvm.sh"

# Install Node.js LTS
nvm install 24

# Verify installation
node -v  # Should print "v24.13.1"
npm -v   # Should print "11.8.0"
```

**If nvm install succeeds**, continue. If it fails, stop and report the error to user.

**If output is `HAS_NPM`** or after nvm installation, run build:

```bash
cd ~/mcp-servers/grok-search && npm install && npm run build
```

### Step 2: Get API Key

Use `question` tool:

```yaml
header: "XAI API Key"
question: "请输入你的 xAI(Grok) API Key（在 https://identity.habby.com/vibe-coding 获取）："
options: []  # custom input only
```

Store user input as `API_KEY`.

### Step 3: Select Model

Use `question` tool:

```yaml
header: "选择模型"
question: "请选择要使用的 Grok 模型："
options:
  - label: "grok-4-1-fast-reasoning（推荐）"
    description: "最新模型，高级推理，2M 上下文"
  - label: "grok-3-mini"
    description: "经济实惠，简单搜索"
  - label: "grok-4-fast-non-reasoning"
    description: "快速响应，无深度推理"
  - label: "grok-code-fast-1"
    description: "代码搜索优化"
```

Map selection to model ID:

| User Selection | Model ID |
|----------------|----------|
| grok-4-1-fast-reasoning（推荐） | `grok-4-1-fast-reasoning` |
| grok-3-mini | `grok-3-mini` |
| grok-4-fast-non-reasoning | `grok-4-fast-non-reasoning` |
| grok-code-fast-1 | `grok-code-fast-1` |

### Step 4: Update Config

1. Read `~/.config/opencode/opencode.jsonc`
2. Get user home path: `echo $HOME` (e.g., `/Users/john`)
3. Add to `mcp` object with **all required fields**:

```json
"grok-search": {
  "type": "local",
  "command": [
    "node",
    "{HOME}/mcp-servers/grok-search/dist/index.js"
  ],
  "environment": {
    "XAI_API_KEY": "{API_KEY}",
    "XAI_MODEL": "{MODEL_ID}"
  },
  "enabled": true
}
```

Replace:
- `{HOME}` → user's home directory path
- `{API_KEY}` → value from Step 2
- `{MODEL_ID}` → mapped model ID from Step 3

### Step 5: Complete

Tell user: **"配置完成！请重启 OpenCode 以加载 Grok MCP。"**

## Available Tools After Install

| Tool | Function |
|------|----------|
| `grok-search_web_search` | Web search |
| `grok-search_x_search` | X/Twitter search |
| `grok-search_grok_search` | Combined search |

## Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `XAI_API_KEY` | Yes | - |
| `XAI_MODEL` | No | `grok-4-1-fast-reasoning` |
| `XAI_API_BASE` | No | `https://api.x.ai/v1` |
