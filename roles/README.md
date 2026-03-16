# Role Hub Files

- `index.json`: role registry and runtime thresholds.
- `role-hr.md`: HR role definition and output contract.
- `role-template.md`: scaffold template for new roles.
- `role_manager.py`: helper CLI for evaluate/create/touch/archive workflows.
- `role_sync.py`: SSOT sync and role-skill validation helper.
- `portable/`: cross-device install and update scripts for Windows/macOS.
- `decisions.log`: audit log file (written only in audit mode).

## Source Of Truth

- Canonical registry (SSOT): `C:/Users/Administrator/.config/opencode/roles/index.json`
- HR local mirror (generated): `C:/Users/Administrator/.claude/skills/role-hr/roles/index.json`
- Rule: edit SSOT first, then run sync.

## Quick Commands

```bash
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" evaluate --id role-pm --purpose "product planning" --outputs prd roadmap --guardrails "clarify scope" --tooling read write
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" create --id role-pm --title "Product Manager" --purpose "turn vague requirements into executable plans" --triggers "pm mode" "product mode" --outputs prd acceptance-criteria --guardrails "ask constraints" "mvp first" --tooling read write apply_patch --tags product planning --codes PM PROD
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" touch --id role-hr
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" archive-stale --days 90
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" resolve --code FG
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" activate --input 主理人模式
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" activate --input 主理人模式 --touch --audit
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" add-code --id role-final-gatekeeper --code GO-NOGO
python "C:/Users/Administrator/.config/opencode/roles/role_sync.py" validate
python "C:/Users/Administrator/.config/opencode/roles/role_sync.py" sync
```

## Quick Experience Checklist

Use this checklist when role routing feels slow.

Default runtime is lightweight now:
- No decision log append unless `--audit` (or env `OPENCODE_ROLE_AUDIT=1`).
- No registry write on `activate` unless `--touch`.

1. Verify direct alias routing first
- Use a role code alias (for example `PM` or `FG`) and compare response speed to generic `hr mode` prompts.

2. Check decision log size
- Large `decisions.log` can slow down append/read operations.
- Command:

```bash
powershell -NoProfile -Command "Get-Item 'C:/Users/Administrator/.config/opencode/roles/decisions.log' | Select-Object FullName,Length,LastWriteTime"
```

3. Rotate decision log if too large
- Keep one active file and archive old records by date.
- Example:

```bash
powershell -NoProfile -Command "Copy-Item 'C:/Users/Administrator/.config/opencode/roles/decisions.log' 'C:/Users/Administrator/.config/opencode/roles/decisions-archive-$(Get-Date -Format yyyyMMdd-HHmmss).log'; Clear-Content 'C:/Users/Administrator/.config/opencode/roles/decisions.log'"
```

4. Check role registry and target role file size
- Very long role definitions increase prompt processing latency.
- Keep mission, outputs, and guardrails concise.

5. Reduce extra runtime context
- Disable unneeded skills and avoid stacking multiple role-like prompts in one request.

6. Re-test with a fixed prompt
- Run the same prompt twice and compare first-response latency before/after each change.

## Timing Instrumentation

`role_manager.py` now returns a `timing` block in command output so you can see where time is spent.

- `evaluate`: `load_registry_ms`, `score_candidate_ms`, `total_ms`
- `resolve`: `load_registry_ms`, `resolve_code_ms`, `total_ms`
- `activate`: `load_registry_ms`, `resolve_input_ms`, `touch_needed_ms`, `save_registry_ms`, `append_decision_log_ms`, `audit_logged`, `total_ms`
- `create`: `load_registry_ms`, `score_candidate_ms`, `scaffold_role_file_ms`, `save_registry_ms`, `append_decision_log_ms`, `total_ms`

Quick checks:

```bash
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" resolve --code 主理人
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" activate --input 主理人模式
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" activate --input 主理人模式 --touch --audit
python "C:/Users/Administrator/.config/opencode/roles/role_manager.py" evaluate --id role-probe --purpose "final acceptance gate" --outputs report decision --guardrails "evidence first" --tooling read grep bash
```
