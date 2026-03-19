---
name: opencode-notebooklm-mcp-installer
description: Install notebooklm MCP from git and configure OpenCode shared gateway mode.
license: MIT
metadata:
  audience: habby
  compatibility: opencode
---

## What I do

- Clone or update `habby/opencode-notebooklm-mcp` from `habby.ghe.com`.
- Ask the user to choose Python mode: `local` or `standalone`.
- Run repo script `scripts/install_shared_gateway.sh` from the cloned repo.
- Configure OpenCode to use remote MCP at `http://127.0.0.1:<port>/mcp` with bearer auth.

This skill does not embed runtime scripts/templates. All install logic is pulled from git.

## Prereqs

- You can `git clone` the repo: `https://habby.ghe.com/habby/opencode-notebooklm-mcp.git`
- macOS with `launchctl` (shared gateway installer writes a LaunchAgent)
- `npx` available on PATH

## Default paths

- Install dir: `$HOME/mcp-servers/notebooklm`
- OpenCode config: `$HOME/.config/opencode/opencode.jsonc`

## Install / Update workflow

Before running install, ask the user to choose mode:

- `local`: use system Python >= 3.10
- `standalone` (recommended): download isolated Python into repo `.python/`

Then run:

```bash
set -euo pipefail

REPO_URL="https://habby.ghe.com/habby/opencode-notebooklm-mcp.git"
INSTALL_DIR="${HOME}/mcp-servers/notebooklm"
PYTHON_MODE="${PYTHON_MODE:?Set PYTHON_MODE to local or standalone}"

mkdir -p "$(dirname "$INSTALL_DIR")"
if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" fetch --all --prune
  git -C "$INSTALL_DIR" pull --ff-only
else
  rm -rf "$INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

bash "$INSTALL_DIR/scripts/install_shared_gateway.sh" --mode "$PYTHON_MODE"
```

## IMPORTANT: Post-install

Tell the user to fully restart OpenCode after install.

## Verify

After restarting OpenCode:

- Run `opencode mcp list` and confirm `notebooklm` is connected.
- Confirm `~/.config/opencode/opencode.jsonc` has `mcp.notebooklm.type = "remote"`.
- In OpenCode, call `notebooklm.status`.

## Recommended post-install ask settings (lightweight)

When users see intermittent ask failures under load, suggest these defaults first:

- OpenCode MCP client timeout: `240000` ms (avoid 15s client-side cancellations)
- `timeout: 120`
- `queue_timeout: 0`
- `fail_fast: false`
- `retry: 1`
- `retry_backoff: 0.5`
- `fallback_cli: true` (optional, resilience-first for `-32001`)
- `fallback_timeout: 180`

Then tune by symptom:

- `-32002` (busy / queue timeout): reduce concurrent asks, raise `queue_timeout` (for example `0.5 -> 1.0 -> 2.0`), keep `retry` enabled.
- `-32001` (ask timeout): raise `timeout` (for example `90 -> 120 -> 180`), narrow scope (`source_ids`, split large prompts), and optionally enable `fallback_cli=true`.

If `notebooklm` CLI works but MCP keeps failing, inspect shared gateway logs (`~/Library/Logs/notebooklm-mcp-gateway.out.log` and `.err.log`) for cancellation patterns.

## Uninstall

```bash
bash "$HOME/mcp-servers/notebooklm/scripts/uninstall_shared_gateway.sh"
```
