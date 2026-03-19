#!/usr/bin/env python3
"""Check for updates to installed skills."""

import os
import sys
import json
import ssl
import urllib.request
import urllib.error

SKILLS_DIR = os.path.expanduser("~/.claude/skills")
API_BASE = "https://apps.habby.com/api/skills-hub"

SSL_CONTEXT = ssl.create_default_context()
try:
    import certifi

    SSL_CONTEXT.load_verify_locations(certifi.where())
except ImportError:
    pass


def load_skill_meta(skill_path):
    meta_path = os.path.join(skill_path, ".skill-meta.json")
    if not os.path.exists(meta_path):
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_remote_version(skill_id):
    url = f"{API_BASE}/skills/{skill_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("version", 1)
    except Exception:
        return None


def main():
    if not os.path.isdir(SKILLS_DIR):
        print("No skills directory found.", file=sys.stderr)
        sys.exit(1)

    skills_to_check = []
    for item in sorted(os.listdir(SKILLS_DIR)):
        item_path = os.path.join(SKILLS_DIR, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            meta = load_skill_meta(item_path)
            if meta and meta.get("skillId"):
                skills_to_check.append(
                    {
                        "folder": item,
                        "name": meta.get("name", item),
                        "skillId": meta.get("skillId"),
                        "localVersion": meta.get("version", 1),
                    }
                )

    if not skills_to_check:
        print("No skills with version tracking found.")
        print("(Skills installed before version tracking won't be checked)")
        return

    print(f"Checking {len(skills_to_check)} skills for updates...\n")

    updates_available = []
    up_to_date = []
    check_failed = []

    for skill in skills_to_check:
        remote_version = get_remote_version(skill["skillId"])
        if remote_version is None:
            check_failed.append(skill)
        elif remote_version > skill["localVersion"]:
            skill["remoteVersion"] = remote_version
            updates_available.append(skill)
        else:
            up_to_date.append(skill)

    if updates_available:
        print(f"{len(updates_available)} update(s) available:\n")
        for s in updates_available:
            print(f"[UPDATE] {s['name']}")
            print(f"  Local: v{s['localVersion']} -> Remote: v{s['remoteVersion']}")
            print(
                f"  Command: python3 scripts/download_skill.py {s['skillId']} --output ~/.claude/skills/ --force"
            )
            print()
    else:
        print("All skills are up to date.")

    if up_to_date:
        print(f"{len(up_to_date)} skill(s) up to date")

    if check_failed:
        print(f"\n{len(check_failed)} skill(s) could not be checked:")
        for s in check_failed:
            print(f"  - {s['name']} ({s['folder']})")


if __name__ == "__main__":
    main()
