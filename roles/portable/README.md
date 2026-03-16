# Cross-Device Role Hub

Use these scripts to install/update the role system on Windows and macOS.

## Expected Source Layout

```text
<source-root>/
  roles/
    index.json
    role-*.md
    role_manager.py
    role_sync.py
  skills/
    role-hr/SKILL.md
    role-master/SKILL.md
    role-planner/SKILL.md
    role-coder/SKILL.md
```

## Target Paths

- Roles: `~/.config/opencode/roles`
- Skills: `~/.claude/skills`

## Windows

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -SourceRoot "D:\role-hub"
powershell -ExecutionPolicy Bypass -File update.ps1 -RepoRoot "D:\role-hub"
```

## macOS / Linux

```bash
bash install.sh --source-root "$HOME/role-hub"
bash update.sh --repo-root "$HOME/role-hub"
```

## Notes

- `install` copies role definitions and role skills, then runs `role_sync.py sync` and `role_sync.py validate`.
- `update` runs `git pull` first, then executes install.
- Keep `roles/index.json` as the only source of truth.
