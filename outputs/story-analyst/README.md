# Story Analyst Outputs

This directory is the canonical storage for `role-story-analyst` artifacts.

## Folder Rule

- One task, one folder.
- Folder format: `<YYYYMMDD>-<task-id>`
- Example: `20260319-TASK-20260319-003`

## Required Files Per Task

- `01-sample-pool.md`
- `02-quant-metrics.csv`
- `03-patterns-and-failures.md`
- `04-role-archetype-pack.md`
- `05-handoff-sheet.md`
- `06-creator-sync-pack.md`

## Required Header Fields

Each artifact should include:

- `task_id`
- `pattern_version`
- `updated_at`
- `source_access` (`public` or `licensed`)

## Completion Marker

When handoff is complete, add `DONE.md` in the task folder with:

- `task_id`
- `delivered_at`
- `receiver`
- `pattern_version`

Receiver acknowledgment should be recorded in `05-handoff-sheet.md` or `DONE.md`.

## Archival

- Keep recent 90 days under `outputs/story-analyst/`.
- Move older task folders to `outputs/story-analyst/archive/`.
- Preserve core artifacts for traceability.
