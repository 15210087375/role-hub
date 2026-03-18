#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).resolve().parent
SSOT_REGISTRY_PATH = BASE_DIR / "index.json"
SKILLS_DIR = Path.home() / ".claude" / "skills"
HR_MIRROR_PATH = SKILLS_DIR / "role-hr" / "roles" / "index.json"


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def role_scope(role: Dict) -> List[str]:
    tags = [str(t).strip() for t in role.get("tags", []) if str(t).strip()]
    if tags:
        return tags
    outputs = [str(o).strip() for o in role.get("outputs", []) if str(o).strip()]
    if outputs:
        return outputs[:5]
    return ["general"]


def build_hr_mirror(ssot: Dict) -> Dict:
    roles = []
    for role in ssot.get("roles", []):
        roles.append(
            {
                "id": role.get("id", ""),
                "status": role.get("status", "active"),
                "purpose": role.get("purpose", ""),
                "triggers": role.get("triggers", []),
                "scope": role_scope(role),
            }
        )
    return {
        "version": ssot.get("version", 1),
        "updated_at": ssot.get("updated_at", ""),
        "generated_from": str(SSOT_REGISTRY_PATH).replace("\\", "/"),
        "roles": roles,
    }


def collect_missing_skills(ssot: Dict) -> List[str]:
    missing = []
    for role in ssot.get("roles", []):
        role_id = str(role.get("id", "")).strip()
        if not role_id:
            continue
        skill_file = SKILLS_DIR / role_id / "SKILL.md"
        if not skill_file.exists():
            missing.append(role_id)
    return missing


def validate(ssot: Dict) -> int:
    missing = collect_missing_skills(ssot)
    result = {
        "ssot": str(SSOT_REGISTRY_PATH).replace("\\", "/"),
        "skills_dir": str(SKILLS_DIR).replace("\\", "/"),
        "role_count": len(ssot.get("roles", [])),
        "missing_skill_count": len(missing),
        "missing_skills": missing,
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 1 if missing else 0


def command_sync(_: argparse.Namespace) -> int:
    ssot = load_json(SSOT_REGISTRY_PATH)
    missing = collect_missing_skills(ssot)
    if missing:
        print(
            json.dumps(
                {
                    "error": "missing role skills",
                    "missing_skills": missing,
                    "message": "create missing SKILL.md files before sync",
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 1

    mirror = build_hr_mirror(ssot)
    save_json(HR_MIRROR_PATH, mirror)
    print(
        json.dumps(
            {
                "synced": True,
                "source": str(SSOT_REGISTRY_PATH).replace("\\", "/"),
                "target": str(HR_MIRROR_PATH).replace("\\", "/"),
                "role_count": len(mirror.get("roles", [])),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


def command_validate(_: argparse.Namespace) -> int:
    ssot = load_json(SSOT_REGISTRY_PATH)
    return validate(ssot)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync and validate role SSOT and skill mirrors")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sync = sub.add_parser("sync", help="sync HR role index mirror from SSOT")
    p_sync.set_defaults(func=command_sync)

    p_validate = sub.add_parser("validate", help="validate role-to-skill mapping")
    p_validate.set_defaults(func=command_validate)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
