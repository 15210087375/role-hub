#!/usr/bin/env bash
set -euo pipefail

XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
OPENCODE_DIR="$XDG_CONFIG_HOME/opencode"
PLUGIN_FILE="$OPENCODE_DIR/plugins/vision-captioner.ts"
CONFIG_FILE="$OPENCODE_DIR/plugin-data/vision-captioner.json"

echo "Removing: $PLUGIN_FILE"
rm -f "$PLUGIN_FILE"

echo "Removing: $CONFIG_FILE"
rm -f "$CONFIG_FILE"

echo "Done. Restart OpenCode."
