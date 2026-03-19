#!/usr/bin/env python3
import argparse
import hashlib
import json
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


def classify(repo_skill: Path, local_skill: Path) -> Dict:
    repo_exists = repo_skill.exists()
    local_exists = local_skill.exists()

    if not repo_exists and not local_exists:
        status = "both_missing"
        return {"status": status, "repo_exists": False, "local_exists": False}

    if repo_exists and not local_exists:
        return {"status": "repo_newer", "repo_exists": True, "local_exists": False}

    if not repo_exists and local_exists:
        return {"status": "local_newer", "repo_exists": False, "local_exists": True}

    repo_hash = sha256_file(repo_skill)
    local_hash = sha256_file(local_skill)

    if repo_hash == local_hash:
        return {
            "status": "in_sync",
            "repo_exists": True,
            "local_exists": True,
            "repo_hash": repo_hash,
            "local_hash": local_hash,
        }

    repo_mtime = repo_skill.stat().st_mtime
    local_mtime = local_skill.stat().st_mtime
    if repo_mtime > local_mtime:
        status = "repo_newer"
    elif local_mtime > repo_mtime:
        status = "local_newer"
    else:
        status = "conflict"

    return {
        "status": status,
        "repo_exists": True,
        "local_exists": True,
        "repo_hash": repo_hash,
        "local_hash": local_hash,
        "repo_mtime": repo_mtime,
        "local_mtime": local_mtime,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check skill drift between repository and local skills directory")
    parser.add_argument("--repo-root", default=".", help="Role hub repository root")
    parser.add_argument("--local-skills", default=str(Path.home() / ".claude" / "skills"), help="Local skills directory")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    registry_path = repo_root / "roles" / "index.json"
    repo_skills_dir = repo_root / "skills"
    local_skills_dir = Path(args.local_skills).expanduser().resolve()

    role_ids = load_role_ids(registry_path)
    rows = []
    counts: Dict[str, int] = {}

    for role_id in role_ids:
        repo_skill = repo_skills_dir / role_id / "SKILL.md"
        local_skill = local_skills_dir / role_id / "SKILL.md"
        info = classify(repo_skill, local_skill)
        status = info["status"]
        counts[status] = counts.get(status, 0) + 1
        rows.append({"role_id": role_id, **info})

    payload = {
        "repo_root": str(repo_root),
        "registry": str(registry_path),
        "repo_skills": str(repo_skills_dir),
        "local_skills": str(local_skills_dir),
        "role_count": len(role_ids),
        "counts": counts,
        "results": rows,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    # non-zero when any drift exists
    drift_states = {"repo_newer", "local_newer", "conflict", "repo_missing", "local_missing", "both_missing"}
    has_drift = any(r.get("status") in drift_states and r.get("status") != "in_sync" for r in rows)
    return 1 if has_drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
