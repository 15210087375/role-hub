#!/usr/bin/env bash
set -euo pipefail

REPO="https://habby.ghe.com/habby/opencodetool-gemini-plugin.git"
REF=""
PLUGIN_PATH="plugins/vision-captioner.ts"
CONFIG_PATH="config/vision-captioner.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2;;
    --ref) REF="$2"; shift 2;;
    --plugin-path) PLUGIN_PATH="$2"; shift 2;;
    --config-path) CONFIG_PATH="$2"; shift 2;;
    -h|--help)
      cat <<'EOF'
Usage: install.sh [--repo <git-url>] [--ref <branch|tag|sha>] [--plugin-path <path-in-repo>] [--config-path <path-in-repo>]

Installs OpenCode vision-captioner plugin by cloning the repo and copying:
  - plugins/vision-captioner.ts -> ~/.config/opencode/plugins/vision-captioner.ts
  - config/vision-captioner.json -> ~/.config/opencode/plugin-data/vision-captioner.json
EOF
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "git is required" >&2
  exit 2
fi

XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
OPENCODE_DIR="$XDG_CONFIG_HOME/opencode"
PLUGIN_DIR="$OPENCODE_DIR/plugins"
DATA_DIR="$OPENCODE_DIR/plugin-data"

mkdir -p "$PLUGIN_DIR" "$DATA_DIR"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "[1/3] Cloning repo: $REPO"
git clone --depth 1 "$REPO" "$tmp/repo" >/dev/null
if [[ -n "$REF" ]]; then
  echo "[1/3] Checking out ref: $REF"
  git -C "$tmp/repo" fetch --depth 1 origin "$REF" >/dev/null 2>&1 || true
  git -C "$tmp/repo" checkout -q "$REF"
fi

echo "[2/3] Installing plugin + config"
src_plugin="$tmp/repo/$PLUGIN_PATH"
src_cfg="$tmp/repo/$CONFIG_PATH"

if [[ ! -f "$src_plugin" ]]; then
  echo "Plugin file not found in repo: $PLUGIN_PATH" >&2
  echo "Tip: ensure the repo contains plugins/vision-captioner.ts" >&2
  exit 3
fi
if [[ ! -f "$src_cfg" ]]; then
  echo "Config not found in repo: $CONFIG_PATH" >&2
  echo "Tip: ensure the repo contains config/vision-captioner.json" >&2
  exit 4
fi

cp -f "$src_plugin" "$PLUGIN_DIR/vision-captioner.ts"
cp -f "$src_cfg" "$DATA_DIR/vision-captioner.json"

echo "[3/3] Done"
echo "Installed plugin: $PLUGIN_DIR/vision-captioner.ts"
echo "Wrote config:     $DATA_DIR/vision-captioner.json"
echo
echo "Next steps:"
echo "- Restart OpenCode"
echo "- Connect Gemini in OpenCode: /connect (provider: google)"
