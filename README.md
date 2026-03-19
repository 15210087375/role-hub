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

## Skill Drift Maintenance

- Check drift between repository and local installed skills:
  - `python scripts/skill_drift_check.py --repo-root .`
- Sync from repository to local installation (apply):
  - `python scripts/skill_sync.py --repo-root . --from repo --apply`
- Sync from local edits back to repository (apply):
  - `python scripts/skill_sync.py --repo-root . --from local --apply`

## Role/Skill Alignment Check

- Check key role-to-skill alignment rules:
  - `python scripts/role_skill_alignment_check.py --repo-root .`

## Memory Backup And Sync

- Backup local non-repo memory into repository (AGENTS + local-only skills backup):
  - `python scripts/memory_sync.py backup-local --repo-root . --apply`
- Sync latest repository memory to local (managed scope only):
  - `python scripts/memory_sync.py sync-to-local --repo-root . --apply`
- Scope note: device-specific settings (e.g., screenshot paths, machine-local absolute paths) are intentionally excluded.
