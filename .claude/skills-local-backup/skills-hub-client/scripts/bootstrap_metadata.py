#!/usr/bin/env python3
"""
Bootstrap metadata for skills installed without .skill-meta.json.

This script finds skills that are missing metadata (e.g., manually installed
or installed before version tracking), searches Skills Hub for matching skills
by name, and creates .skill-meta.json so they can be checked for updates.

Usage:
    python bootstrap_metadata.py [--dry-run]
"""

import os
import sys
import json
import ssl
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

SKILLS_DIR = os.path.expanduser("~/.claude/skills")
API_BASE = "https://apps.habby.com/api/skills-hub"

SSL_CONTEXT = ssl.create_default_context()
try:
    import certifi

    SSL_CONTEXT.load_verify_locations(certifi.where())
except ImportError:
    pass


def extract_skill_name(skill_path):
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        return None

    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    if not content.startswith("---"):
        return None

    end = content.find("---", 3)
    if end == -1:
        return None

    frontmatter = content[3:end]
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        return name_match.group(1).strip().strip("\"'")
    return None


def search_skill_on_hub(skill_name):
    url = f"{API_BASE}/skills?q={urllib.parse.quote(skill_name)}&limit=10"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            data = json.loads(response.read().decode("utf-8"))
            skills = data.get("data", data.get("skills", []))

            for skill in skills:
                if (
                    skill.get("slug") == skill_name
                    or skill.get("name", "").lower() == skill_name.lower()
                ):
                    return skill

            if skills:
                return skills[0]
            return None
    except Exception as e:
        print(f"  Error searching: {e}", file=sys.stderr)
        return None


def create_metadata(skill_path, skill_info):
    meta_path = os.path.join(skill_path, ".skill-meta.json")
    meta_data = {
        "skillId": skill_info["_id"],
        "slug": skill_info.get("slug", ""),
        "version": 0,  # Always 0 for bootstrapped skills to ensure update check works
        "runAfterInstall": skill_info.get("runAfterInstall", False),
        "installedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "bootstrapped": True,
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)

    return meta_path


def main():
    import urllib.parse

    dry_run = "--dry-run" in sys.argv

    if not os.path.isdir(SKILLS_DIR):
        print("No skills directory found.", file=sys.stderr)
        sys.exit(1)

    skills_without_meta = []

    for item in sorted(os.listdir(SKILLS_DIR)):
        item_path = os.path.join(SKILLS_DIR, item)
        if not os.path.isdir(item_path) or item.startswith("."):
            continue

        meta_path = os.path.join(item_path, ".skill-meta.json")
        if os.path.exists(meta_path):
            continue

        skill_name = extract_skill_name(item_path)
        if skill_name:
            skills_without_meta.append(
                {"folder": item, "name": skill_name, "path": item_path}
            )

    if not skills_without_meta:
        print("All skills already have metadata. Nothing to bootstrap.")
        return

    print(f"Found {len(skills_without_meta)} skill(s) without metadata:\n")

    bootstrapped = 0
    failed = 0

    for skill in skills_without_meta:
        print(f"📦 {skill['name']} ({skill['folder']})")
        print(f"   Searching Skills Hub...")

        remote_skill = search_skill_on_hub(skill["folder"])

        if not remote_skill:
            remote_skill = search_skill_on_hub(skill["name"])

        if remote_skill:
            print(
                f"   Found: {remote_skill.get('name')} (v{remote_skill.get('version', 1)})"
            )
            print(f"   ID: {remote_skill['_id']}")

            if dry_run:
                print(f"   [DRY-RUN] Would create .skill-meta.json")
            else:
                try:
                    meta_path = create_metadata(skill["path"], remote_skill)
                    print(f"   ✅ Created: {meta_path}")
                    bootstrapped += 1
                except Exception as e:
                    print(f"   ❌ Failed to create metadata: {e}")
                    failed += 1
        else:
            print(f"   ⚠️  Not found on Skills Hub (may not be published)")
            failed += 1

        print()

    print("=" * 50)
    if dry_run:
        print(f"[DRY-RUN] Would bootstrap {len(skills_without_meta) - failed} skill(s)")
    else:
        print(f"Bootstrapped: {bootstrapped}")
        print(f"Not found/failed: {failed}")

        if bootstrapped > 0:
            print(f"\nYou can now run check_updates.py to see available updates.")


if __name__ == "__main__":
    main()
