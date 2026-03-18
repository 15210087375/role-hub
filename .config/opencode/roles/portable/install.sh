#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT=""
TARGET_ROLES="${HOME}/.config/opencode/roles"
TARGET_SKILLS="${HOME}/.claude/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-root)
      SOURCE_ROOT="$2"
      shift 2
      ;;
    --target-roles)
      TARGET_ROLES="$2"
      shift 2
      ;;
    --target-skills)
      TARGET_SKILLS="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$SOURCE_ROOT" ]]; then
  echo "--source-root is required" >&2
  exit 2
fi

FROM_ROLES="${SOURCE_ROOT}/roles"
FROM_SKILLS="${SOURCE_ROOT}/skills"

[[ -d "$FROM_ROLES" ]] || { echo "roles directory not found: $FROM_ROLES" >&2; exit 1; }
[[ -d "$FROM_SKILLS" ]] || { echo "skills directory not found: $FROM_SKILLS" >&2; exit 1; }

mkdir -p "$TARGET_ROLES" "$TARGET_SKILLS"

cp -f "$FROM_ROLES/index.json" "$TARGET_ROLES/index.json"
cp -f "$FROM_ROLES/role_manager.py" "$TARGET_ROLES/role_manager.py"
cp -f "$FROM_ROLES/role_sync.py" "$TARGET_ROLES/role_sync.py"

for f in "$FROM_ROLES"/role-*.md "$FROM_ROLES/role-template.md" "$FROM_ROLES/README.md"; do
  [[ -f "$f" ]] && cp -f "$f" "$TARGET_ROLES/"
done

for d in "$FROM_SKILLS"/role-*; do
  [[ -d "$d" ]] || continue
  name="$(basename "$d")"
  mkdir -p "$TARGET_SKILLS/$name"
  cp -Rf "$d/"* "$TARGET_SKILLS/$name/"
done

python3 "$TARGET_ROLES/role_sync.py" sync
python3 "$TARGET_ROLES/role_sync.py" validate

echo "Install completed. Roles and skills are synchronized."
