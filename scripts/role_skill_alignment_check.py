#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


REQUIRED_KEYWORDS = {
    "role-master": [
        "orchestrate",
        "gate",
        "主理人",
        "调度编排",
        "最终验收",
        "orchestrate must not output release pass/fail decisions",
        "gate must not skip evidence fields",
    ]
}


def load_role_ids(repo_root: Path):
    payload = json.loads((repo_root / "roles" / "index.json").read_text(encoding="utf-8"))
    return [str(r.get("id", "")).strip() for r in payload.get("roles", []) if str(r.get("id", "")).strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check role-to-skill keyword alignment")
    parser.add_argument("--repo-root", default=".", help="Role hub repository root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    role_ids = set(load_role_ids(repo_root))
    result = {
        "repo_root": str(repo_root),
        "checked": [],
        "failed": [],
    }

    for role_id, keywords in REQUIRED_KEYWORDS.items():
        if role_id not in role_ids:
            continue
        skill_file = repo_root / "skills" / role_id / "SKILL.md"
        if not skill_file.exists():
            result["failed"].append({"role_id": role_id, "reason": "missing_skill_file"})
            continue

        content = skill_file.read_text(encoding="utf-8")
        def norm(s: str) -> str:
            t = s.lower()
            t = t.replace("`", "")
            t = re.sub(r"\s+", " ", t)
            return t

        ncontent = norm(content)
        missing = [kw for kw in keywords if norm(kw) not in ncontent]
        item = {
            "role_id": role_id,
            "skill_file": str(skill_file),
            "required_count": len(keywords),
            "missing_count": len(missing),
            "missing": missing,
        }
        result["checked"].append(item)
        if missing:
            result["failed"].append({"role_id": role_id, "reason": "missing_keywords", "missing": missing})

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
