# role-hub

Cross-device role governance and skill execution bundle.

## Structure

- `roles/`: source of truth registry, role definitions, management scripts.
- `skills/`: executable role skills for OpenCode.

## Quick Start

- Windows: `powershell -ExecutionPolicy Bypass -File roles/portable/install.ps1 -SourceRoot "<repo-root>"`
- macOS/Linux: `bash roles/portable/install.sh --source-root "<repo-root>"`

## Validation

- `python roles/role_sync.py validate`
- `python roles/role_sync.py sync`
- `python roles/role_agents_sync.py`
