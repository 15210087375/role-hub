#!/usr/bin/env python3
"""
Rollback a skill to its previous version from backup.

Usage:
    python rollback_skill.py                    # List available backups
    python rollback_skill.py <skill-name>       # Rollback specific skill
    python rollback_skill.py <skill-name> -y    # Rollback without confirmation
"""

import argparse
import os
import shutil
import sys
import zipfile

SKILLS_DIR = os.path.expanduser("~/.claude/skills")


def get_backups():
    backups = []
    if not os.path.isdir(SKILLS_DIR):
        return backups

    for item in sorted(os.listdir(SKILLS_DIR)):
        if item.endswith(".backup.zip"):
            skill_name = item.removesuffix(".backup.zip")
            backup_path = os.path.join(SKILLS_DIR, item)
            current_exists = os.path.isdir(os.path.join(SKILLS_DIR, skill_name))
            backups.append(
                {
                    "skill_name": skill_name,
                    "backup_file": item,
                    "backup_path": backup_path,
                    "current_exists": current_exists,
                    "size": os.path.getsize(backup_path),
                }
            )
    return backups


def list_backups():
    backups = get_backups()

    if not backups:
        print("No backups found.")
        print("\nBackups are created when you update a skill with --force.")
        return

    print(f"Found {len(backups)} backup(s):\n")
    print("=" * 60)
    for b in backups:
        status = (
            "✓ current version exists"
            if b["current_exists"]
            else "⚠ no current version"
        )
        size_kb = b["size"] / 1024
        print(f"📦 {b['skill_name']}")
        print(f"   Backup: {b['backup_file']} ({size_kb:.1f} KB)")
        print(f"   Status: {status}")
        print("-" * 60)

    print("\nTo rollback: python rollback_skill.py <skill-name>")


def rollback(skill_name, skip_confirm=False):
    backup_path = os.path.join(SKILLS_DIR, f"{skill_name}.backup.zip")
    skill_path = os.path.join(SKILLS_DIR, skill_name)

    if not os.path.exists(backup_path):
        print(f"❌ No backup found for '{skill_name}'", file=sys.stderr)
        print(f"   Expected: {backup_path}")
        sys.exit(1)

    if not zipfile.is_zipfile(backup_path):
        print(f"❌ Backup file is corrupted: {backup_path}", file=sys.stderr)
        sys.exit(1)

    current_exists = os.path.isdir(skill_path)

    print(f"Rollback: {skill_name}")
    print(f"  Backup: {backup_path}")
    print(f"  Target: {skill_path}")
    if current_exists:
        print(f"  ⚠️  Current version will be DELETED")

    if not skip_confirm:
        confirm = input("\nProceed? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            sys.exit(0)

    if current_exists:
        print(f"\nRemoving current version...")
        shutil.rmtree(skill_path)

    print(f"Extracting backup...")
    with zipfile.ZipFile(backup_path, "r") as zip_ref:
        zip_ref.extractall(SKILLS_DIR)

    print(f"Removing backup file...")
    os.remove(backup_path)

    print(f"\n✅ Rolled back '{skill_name}' successfully!")
    print(f"   Location: {skill_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Rollback a skill to its backup version"
    )
    parser.add_argument("skill_name", nargs="?", help="Name of skill to rollback")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    parser.add_argument(
        "-l", "--list", action="store_true", help="List available backups"
    )

    args = parser.parse_args()

    if args.list or not args.skill_name:
        list_backups()
    else:
        rollback(args.skill_name, skip_confirm=args.yes)


if __name__ == "__main__":
    main()
