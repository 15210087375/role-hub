#!/usr/bin/env python3
"""
Search skills from Skills Hub API.

Usage:
    python search_skills.py [query] [--tags TAG1,TAG2] [--sort FIELD] [--limit N]

Examples:
    python search_skills.py                     # List all skills
    python search_skills.py "pdf"               # Search for "pdf"
    python search_skills.py --tags automation   # Filter by tag
    python search_skills.py --sort downloads    # Sort by downloads
"""

import argparse
import json
import ssl
import sys
import urllib.request
import urllib.parse
import urllib.error

API_BASE = "https://apps.habby.com/api/skills-hub"

SSL_CONTEXT = ssl.create_default_context()
try:
    import certifi

    SSL_CONTEXT.load_verify_locations(certifi.where())
except ImportError:
    pass


def search_skills(query=None, tags=None, sort="downloads", limit=20, page=1):
    """Search skills from Skills Hub API."""
    params = {
        "page": page,
        "limit": limit,
        "sort": sort,
    }
    if query:
        params["q"] = query
    if tags:
        params["tags"] = tags

    url = f"{API_BASE}/skills?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def format_skill(skill, index):
    """Format a skill for display."""
    tags = ", ".join(skill.get("tags", [])) or "none"
    downloads = skill.get("downloadCount", 0)
    rating = skill.get("ratingAvg", skill.get("averageRating", 0)) or 0
    rating_count = skill.get("ratingCount", 0)

    author = skill.get("author")
    if author and isinstance(author, dict):
        author_name = author.get("name", "Unknown")
    else:
        author_name = skill.get("authorName", "Unknown")

    return f"""
{index}. {skill["name"]} (v{skill.get("version", "1.0.0")})
   ID: {skill["_id"]}
   Slug: {skill.get("slug", "N/A")}
   Description: {skill.get("description", "No description")[:100]}...
   Author: {author_name}
   Tags: {tags}
   Downloads: {downloads} | Rating: {rating:.1f}/5 ({rating_count} ratings)
""".strip()


def main():
    parser = argparse.ArgumentParser(description="Search skills from Skills Hub")
    parser.add_argument("query", nargs="?", default=None, help="Search query")
    parser.add_argument("--tags", "-t", help="Filter by tags (comma-separated)")
    parser.add_argument(
        "--sort",
        "-s",
        default="downloads",
        choices=["downloads", "rating", "createdAt", "updatedAt"],
        help="Sort field (default: downloads)",
    )
    parser.add_argument(
        "--limit", "-l", type=int, default=20, help="Number of results (default: 20)"
    )
    parser.add_argument("--page", "-p", type=int, default=1, help="Page number")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    result = search_skills(
        query=args.query,
        tags=args.tags,
        sort=args.sort,
        limit=args.limit,
        page=args.page,
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    skills = result.get("data", result.get("skills", []))
    pagination = result.get("pagination", {})

    if not skills:
        print("No skills found.")
        return

    print(f"Found {pagination.get('total', len(skills))} skills")
    print(
        f"Page {pagination.get('page', 1)}/{pagination.get('pages', 1)} "
        f"(showing {len(skills)})"
    )
    print("=" * 60)

    for i, skill in enumerate(skills, 1):
        print(format_skill(skill, i))
        print("-" * 60)

    if skills:
        print(f"\nTo download a skill, run:")
        print(f"  python download_skill.py <skill_id>")
        print(f"\nExample:")
        print(f"  python download_skill.py {skills[0]['_id']}")


if __name__ == "__main__":
    main()
