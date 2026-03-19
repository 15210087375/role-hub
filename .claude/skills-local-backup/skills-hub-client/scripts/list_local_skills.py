#!/usr/bin/env python3
"""List installed skills with their metadata (name + description)."""

import os
import sys
import re

SKILLS_DIR = os.path.expanduser("~/.claude/skills")


def extract_frontmatter(skill_path):
    """Extract name and description from SKILL.md frontmatter."""
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        return None, None

    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None, None

    if not content.startswith("---"):
        return None, None

    end = content.find("---", 3)
    if end == -1:
        return None, None

    frontmatter = content[3:end]

    name = None
    description = None

    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip().strip("\"'")

    desc_match = re.search(
        r"^description:\s*\|?\s*\n?([\s\S]*?)(?=\n[a-z]+:|\Z)",
        frontmatter,
        re.MULTILINE,
    )
    if desc_match:
        desc_lines = desc_match.group(1).strip()
        description = " ".join(
            line.strip() for line in desc_lines.split("\n") if line.strip()
        )
    else:
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        if desc_match:
            description = desc_match.group(1).strip().strip("\"'")

    return name, description


def main():
    if not os.path.isdir(SKILLS_DIR):
        print("No skills directory found.", file=sys.stderr)
        sys.exit(1)

    skills = []
    for item in sorted(os.listdir(SKILLS_DIR)):
        item_path = os.path.join(SKILLS_DIR, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            name, description = extract_frontmatter(item_path)
            if name:
                skills.append(
                    {
                        "folder": item,
                        "name": name,
                        "description": description or "(no description)",
                    }
                )

    if not skills:
        print("No skills installed.")
        return

    print(f"Found {len(skills)} installed skills:\n")
    print("=" * 60)
    for s in skills:
        print(f"📦 {s['name']}")
        print(f"   Folder: {s['folder']}")
        print(
            f"   Description: {s['description'][:200]}{'...' if len(s['description']) > 200 else ''}"
        )
        print("-" * 60)


if __name__ == "__main__":
    main()
