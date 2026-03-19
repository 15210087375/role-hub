# Character Designer Outputs

This directory is the canonical storage for `role-character-designer` artifacts.

## Folder Rule

- One task, one folder.
- Folder format: `<YYYYMMDD>-<task-id>`
- Example: `20260319-TASK-20260319-004`

## Required Files Per Task

- `01-character-reforge-cards.md`
- `02-relationship-map.md`
- `03-character-index.csv`
- `04-ooc-boundary-checklist.md`
- `05-handoff-to-writer.md`
- `DONE.md`

## Required Header Fields

Each artifact should include:

- `task_id`
- `source_task_id`
- `updated_at`
- `owner`

## Archival

- Keep recent 90 days under `outputs/character-designer/`.
- Move older task folders to `outputs/character-designer/archive/`.
- Preserve core artifacts for traceability.
