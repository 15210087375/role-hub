---
name: opencode-gemini-vision-installer
description: Install the OpenCode Gemini vision captioner plugin from git, enabling automatic image caption injection.
---

# OpenCode Gemini Vision Installer

This skill installs the `vision-captioner` OpenCode plugin by cloning the repo:

`https://habby.ghe.com/habby/opencodetool-gemini-plugin`

It copies the plugin file into OpenCode's global plugins directory and writes a default config into `plugin-data`.

## What It Installs

- Plugin: `~/.config/opencode/plugins/vision-captioner.ts`
- Config: `~/.config/opencode/plugin-data/vision-captioner.json`

## Install

Run:

```bash
bash scripts/install.sh
```

Then restart `opencode`.

## Notes

- This does not store any API keys.
- You still need to connect Gemini in OpenCode: run `/connect` and set up the `google` provider.
