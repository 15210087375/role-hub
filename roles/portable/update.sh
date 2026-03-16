#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=""
TARGET_ROLES="${HOME}/.config/opencode/roles"
TARGET_SKILLS="${HOME}/.claude/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="$2"
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

if [[ -z "$REPO_ROOT" ]]; then
  echo "--repo-root is required" >&2
  exit 2
fi

[[ -d "$REPO_ROOT" ]] || { echo "repo root not found: $REPO_ROOT" >&2; exit 1; }

git -C "$REPO_ROOT" pull

bash "$(dirname "$0")/install.sh" \
  --source-root "$REPO_ROOT" \
  --target-roles "$TARGET_ROLES" \
  --target-skills "$TARGET_SKILLS"

echo "Update completed."
