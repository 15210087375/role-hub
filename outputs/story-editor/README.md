# Story Editor Outputs

This directory is the canonical storage for `role-story-editor` artifacts.

## Folder Rule

- One task, one folder.
- Folder format: `<YYYYMMDD>-<task-id>`

## Required Files Per Task

- `01-review-notes.md`
- `02-polished-draft.md`
- `03-continuity-report.md`
- `04-pacing-suggestions.md`
- `05-handoff-to-writer.md`
- `DONE.md`

## Required Header Fields

Each artifact should include:

- `task_id`
- `source_task_id`
- `updated_at`
- `owner`

## Archival

- Keep recent 90 days under `outputs/story-editor/`.
- Move older task folders to `outputs/story-editor/archive/`.
- Preserve core artifacts for traceability.
