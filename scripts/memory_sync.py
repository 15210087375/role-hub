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


def hash_directory(path: Path) -> str:
    files = sorted([p for p in path.rglob("*") if p.is_file()])
    h = hashlib.sha256()
    for f in files:
        rel = f.relative_to(path).as_posix().encode("utf-8")
        h.update(rel)
        h.update(b"\0")
        h.update(sha256_file(f).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def load_role_ids(registry_path: Path) -> List[str]:
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    return [str(r.get("id", "")).strip() for r in payload.get("roles", []) if str(r.get("id", "")).strip()]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path, apply: bool) -> Dict:
    action = {
        "type": "copy_file",
        "source": str(src),
        "target": str(dst),
        "status": "planned",
    }
    if apply:
        ensure_parent(dst)
        shutil.copyfile(src, dst)
        action["status"] = "copied"
    return action


def copy_entry(src: Path, dst: Path, apply: bool) -> Dict:
    action = {
        "type": "copy_entry",
        "source": str(src),
        "target": str(dst),
        "entry_type": "dir" if src.is_dir() else "file",
        "status": "planned",
    }
    if apply:
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            ensure_parent(dst)
            shutil.copyfile(src, dst)
        action["status"] = "copied"
    return action


def backup_local(repo_root: Path, local_agents: Path, local_skills: Path, apply: bool) -> Dict:
    registry = repo_root / "roles" / "index.json"
    role_ids = set(load_role_ids(registry))

    actions: List[Dict] = []

    repo_agents = repo_root / ".config" / "opencode" / "AGENTS.md"
    if local_agents.exists():
        actions.append(copy_file(local_agents, repo_agents, apply))
    else:
        actions.append(
            {
                "type": "copy_file",
                "source": str(local_agents),
                "target": str(repo_agents),
                "status": "skip_source_missing",
            }
        )

    backup_root = repo_root / ".claude" / "skills-local-backup"
    manifest_path = repo_root / ".claude" / "skills-local-backup-manifest.json"
    manifest_items: List[Dict] = []

    if local_skills.exists():
        for entry in sorted(local_skills.iterdir(), key=lambda p: p.name.lower()):
            name = entry.name
            managed = name in role_ids
            if managed:
                continue

            target = backup_root / name
            actions.append(copy_entry(entry, target, apply))

            if entry.is_dir():
                digest = hash_directory(entry)
                kind = "dir"
            else:
                digest = sha256_file(entry)
                kind = "file"

            manifest_items.append(
                {
                    "name": name,
                    "kind": kind,
                    "sha256": digest,
                    "source": str(entry),
                    "target": str(target),
                }
            )
    else:
        actions.append(
            {
                "type": "scan_local_skills",
                "source": str(local_skills),
                "status": "skip_source_missing",
            }
        )

    manifest = {
        "repo_root": str(repo_root),
        "local_agents": str(local_agents),
        "local_skills": str(local_skills),
        "managed_role_count": len(role_ids),
        "local_only_skill_count": len(manifest_items),
        "items": manifest_items,
        "note": "Device-specific settings (e.g., screenshot paths, machine-local paths) are intentionally excluded from sync scope.",
    }

    actions.append(
        {
            "type": "write_manifest",
            "target": str(manifest_path),
            "status": "planned" if not apply else "written",
        }
    )
    if apply:
        ensure_parent(manifest_path)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "mode": "backup-local",
        "applied": apply,
        "actions": actions,
        "manifest": manifest,
    }


def sync_to_local(repo_root: Path, local_agents: Path, local_skills: Path, apply: bool) -> Dict:
    registry = repo_root / "roles" / "index.json"
    role_ids = load_role_ids(registry)

    actions: List[Dict] = []

    repo_agents = repo_root / ".config" / "opencode" / "AGENTS.md"
    if repo_agents.exists():
        actions.append(copy_file(repo_agents, local_agents, apply))
    else:
        actions.append(
            {
                "type": "copy_file",
                "source": str(repo_agents),
                "target": str(local_agents),
                "status": "skip_source_missing",
            }
        )

    for role_id in role_ids:
        src = repo_root / "skills" / role_id / "SKILL.md"
        dst = local_skills / role_id / "SKILL.md"
        if not src.exists():
            actions.append(
                {
                    "type": "copy_file",
                    "source": str(src),
                    "target": str(dst),
                    "status": "skip_source_missing",
                }
            )
            continue
        actions.append(copy_file(src, dst, apply))

    return {
        "mode": "sync-to-local",
        "applied": apply,
        "managed_role_count": len(role_ids),
        "note": "Device-specific settings are excluded; only AGENTS and managed role skills are synced.",
        "actions": actions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backup non-repo local memory into repository and sync managed memory to local"
    )
    parser.add_argument("mode", choices=["backup-local", "sync-to-local"])
    parser.add_argument("--repo-root", default=".", help="Role hub repository root")
    parser.add_argument(
        "--local-agents",
        default=str(Path.home() / ".config" / "opencode" / "AGENTS.md"),
        help="Local AGENTS.md path",
    )
    parser.add_argument(
        "--local-skills",
        default=str(Path.home() / ".claude" / "skills"),
        help="Local skills directory",
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes (default dry-run)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    local_agents = Path(args.local_agents).expanduser().resolve()
    local_skills = Path(args.local_skills).expanduser().resolve()

    if args.mode == "backup-local":
        payload = backup_local(repo_root, local_agents, local_skills, args.apply)
    else:
        payload = sync_to_local(repo_root, local_agents, local_skills, args.apply)

    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
