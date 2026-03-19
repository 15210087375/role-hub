#!/usr/bin/env python3
"""
Download a skill from Skills Hub.

Usage:
    python download_skill.py <skill_id_or_slug> [--output DIR] [--force] [--no-extract]

Examples:
    python download_skill.py 6789abc123def456
    python download_skill.py my-awesome-skill --output ~/.claude/skills/
    python download_skill.py my-skill --force  # Overwrite existing
    python download_skill.py my-skill --no-extract  # Download only, don't extract
"""

import argparse
import json
import os
import ssl
import sys
import urllib.request
import urllib.error
import zipfile
import shutil
from datetime import datetime, timezone

API_BASE = "https://apps.habby.com/api/skills-hub"

SSL_CONTEXT = ssl.create_default_context()
try:
    import certifi

    SSL_CONTEXT.load_verify_locations(certifi.where())
except ImportError:
    pass


def get_skill_name_from_filename(filename):
    """Extract skill name from filename (remove .skill extension)."""
    if filename.endswith(".skill"):
        return filename[:-6]
    return filename


def check_existing_skill(output_dir, filename):
    """
    Check if skill already exists locally.
    Returns tuple: (skill_file_exists, skill_dir_exists, skill_dir_path)
    """
    skill_file_path = os.path.join(output_dir, filename)
    skill_name = get_skill_name_from_filename(filename)
    skill_dir_path = os.path.join(output_dir, skill_name)

    skill_file_exists = os.path.exists(skill_file_path)
    skill_dir_exists = os.path.isdir(skill_dir_path)

    return skill_file_exists, skill_dir_exists, skill_dir_path


def get_installed_skill_version(skill_dir_path):
    """Try to read version from installed skill's SKILL.md frontmatter."""
    skill_md_path = os.path.join(skill_dir_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        return None

    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Simple frontmatter parsing for version
            if content.startswith("---"):
                end = content.find("---", 3)
                if end != -1:
                    frontmatter = content[3:end]
                    for line in frontmatter.split("\n"):
                        if line.strip().startswith("version:"):
                            return line.split(":", 1)[1].strip().strip("\"'")
    except Exception:
        pass
    return None


def extract_skill(skill_file_path, output_dir, force=False):
    """Extract .skill file (ZIP archive) to output directory."""
    skill_name = get_skill_name_from_filename(os.path.basename(skill_file_path))
    extract_path = os.path.join(output_dir, skill_name)

    if os.path.isdir(extract_path):
        if not force:
            return False, f"Directory already exists: {extract_path}"
        # Backup existing directory as zip (ensures Claude won't load it)
        backup_path = f"{extract_path}.backup.zip"
        if os.path.exists(backup_path):
            os.remove(backup_path)
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(extract_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zf.write(file_path, arcname)
        shutil.rmtree(extract_path)
        print(f"  Backed up existing skill to: {backup_path}")

    try:
        with zipfile.ZipFile(skill_file_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        return True, extract_path
    except zipfile.BadZipFile:
        return False, "Invalid .skill file (not a valid ZIP archive)"
    except Exception as e:
        return False, f"Extraction failed: {str(e)}"


def get_skill_info(skill_id):
    """Get skill details including runAfterInstall flag."""
    url = f"{API_BASE}/skills/{skill_id}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        return None
    except urllib.error.URLError:
        return None


def get_download_url(skill_id):
    """Get the download URL for a skill."""
    url = f"{API_BASE}/skills/{skill_id}/download"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Skill not found: {skill_id}", file=sys.stderr)
        else:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def download_file(url, output_path):
    """Download file from URL to output path."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=120, context=SSL_CONTEXT) as response:
            total_size = response.headers.get("Content-Length")
            total_size = int(total_size) if total_size else None

            with open(output_path, "wb") as f:
                downloaded = 0
                block_size = 8192

                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    f.write(buffer)

                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(
                            f"\rDownloading: {percent:.1f}% ({downloaded}/{total_size} bytes)",
                            end="",
                            flush=True,
                        )

                print()
        return True
    except urllib.error.HTTPError as e:
        print(f"Download failed - HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"Download failed - URL Error: {e.reason}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Download a skill from Skills Hub")
    parser.add_argument("skill_id", help="Skill ID or slug")
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force overwrite if skill already exists",
    )
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="Download only, don't extract the .skill file",
    )

    args = parser.parse_args()

    print(f"Getting skill info for: {args.skill_id}")
    skill_info = get_skill_info(args.skill_id)

    print(f"Getting download URL for: {args.skill_id}")
    result = get_download_url(args.skill_id)

    download_url = result.get("downloadUrl")
    filename = result.get("fileName", f"{args.skill_id}.skill")
    file_size = result.get("fileSize")
    # Version comes from skill info (detail API), not download API
    remote_version = skill_info.get("version", "unknown") if skill_info else "unknown"
    run_after_install = result.get("runAfterInstall", False)

    if not download_url:
        print("Error: No download URL returned", file=sys.stderr)
        sys.exit(1)

    output_dir = os.path.expanduser(args.output)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    skill_file_exists, skill_dir_exists, skill_dir_path = check_existing_skill(
        output_dir, filename
    )

    if skill_file_exists or skill_dir_exists:
        print(f"\n⚠️  Skill already exists locally:")
        if skill_file_exists:
            print(f"   - File: {output_path}")
        if skill_dir_exists:
            local_version = get_installed_skill_version(skill_dir_path)
            version_info = f" (v{local_version})" if local_version else ""
            print(f"   - Installed: {skill_dir_path}{version_info}")

        print(f"   - Remote version: v{remote_version}")

        if not args.force:
            print(
                f"\nUse --force to overwrite, or choose a different output directory."
            )
            print(f"Example: python download_skill.py {args.skill_id} --force")
            sys.exit(0)
        else:
            print(f"\n--force specified, proceeding with overwrite...")

    print(f"\nFilename: {filename}")
    if file_size:
        print(f"Size: {file_size:,} bytes")
    print(f"Saving to: {output_path}")
    print()

    success = download_file(download_url, output_path)

    if not success:
        sys.exit(1)

    print(f"\n✅ Downloaded: {output_path}")

    if args.no_extract:
        print(f"\n--no-extract specified. To install manually:")
        print(f"  cd {output_dir} && unzip -o {filename}")
        return

    print(f"\nExtracting skill...")
    extract_success, extract_result = extract_skill(
        output_path, output_dir, force=args.force
    )

    if extract_success:
        skill_name = get_skill_name_from_filename(filename)
        meta_path = os.path.join(extract_result, ".skill-meta.json")
        meta_data = {
            "skillId": args.skill_id,
            "slug": skill_info.get("slug", skill_name) if skill_info else skill_name,
            "version": remote_version,
            "runAfterInstall": run_after_install,
            "installedAt": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
        try:
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta_data, f, indent=2)
            print(f"✅ Created metadata: {meta_path}")
        except Exception as e:
            print(f"⚠️  Failed to create metadata: {e}", file=sys.stderr)

        print(f"✅ Installed: {extract_result}")
        print(f"\nSkill is ready to use!")

        if run_after_install:
            print(f"\n💡 This skill is marked for auto-run after install.")
    else:
        print(f"❌ Extraction failed: {extract_result}", file=sys.stderr)
        print(f"\nTo extract manually:")
        print(f"  cd {output_dir} && unzip -o {filename}")
        sys.exit(1)


if __name__ == "__main__":
    main()
