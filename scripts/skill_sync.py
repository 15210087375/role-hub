#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_role_ids(registry_path: Path) -> List[str]:
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    return [str(r.get("id", "")).strip() for r in payload.get("roles", []) if str(r.get("id", "")).strip()]


def different(a: Path, b: Path) -> bool:
    if not a.exists() or not b.exists():
        return True
    return sha256_file(a) != sha256_file(b)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync role skills between repository and local skills directory")
    parser.add_argument("--repo-root", default=".", help="Role hub repository root")
    parser.add_argument("--local-skills", default=str(Path.home() / ".claude" / "skills"), help="Local skills directory")
    parser.add_argument(
        "--from",
        dest="source",
        required=True,
        choices=["repo", "local"],
        help="Source side for synchronization",
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    repo_skills = repo_root / "skills"
    local_skills = Path(args.local_skills).expanduser().resolve()
    registry = repo_root / "roles" / "index.json"

    role_ids = load_role_ids(registry)
    actions: List[Dict] = []

    for role_id in role_ids:
        repo_file = repo_skills / role_id / "SKILL.md"
        local_file = local_skills / role_id / "SKILL.md"

        if args.source == "repo":
            src = repo_file
            dst = local_file
            reason_base = "repo_to_local"
        else:
            src = local_file
            dst = repo_file
            reason_base = "local_to_repo"

        if not src.exists():
            actions.append(
                {
                    "role_id": role_id,
                    "action": "skip",
                    "reason": f"{reason_base}:source_missing",
                    "source": str(src),
                    "target": str(dst),
                }
            )
            continue

        if not dst.exists() or different(src, dst):
            actions.append(
                {
                    "role_id": role_id,
                    "action": "copy",
                    "reason": f"{reason_base}:target_missing_or_different",
                    "source": str(src),
                    "target": str(dst),
                }
            )
            if args.apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
        else:
            actions.append(
                {
                    "role_id": role_id,
                    "action": "skip",
                    "reason": f"{reason_base}:already_in_sync",
                    "source": str(src),
                    "target": str(dst),
                }
            )

    payload = {
        "repo_root": str(repo_root),
        "registry": str(registry),
        "source": args.source,
        "applied": bool(args.apply),
        "total_roles": len(role_ids),
        "copy_count": sum(1 for a in actions if a["action"] == "copy"),
        "skip_count": sum(1 for a in actions if a["action"] == "skip"),
        "actions": actions,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
