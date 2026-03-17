#!/usr/bin/env python3
import argparse
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_FRAGMENT_PATH = BASE_DIR / "agents" / "role-hub-runtime.md"
DEFAULT_AGENTS_PATH = Path.home() / ".config" / "opencode" / "AGENTS.md"

BEGIN = "<!-- ROLE_HUB_RUNTIME:BEGIN -->"
END = "<!-- ROLE_HUB_RUNTIME:END -->"


def upsert_block(target_path: Path, runtime_fragment: str) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        content = target_path.read_text(encoding="utf-8")
    else:
        content = "# Global OpenCode Rules\n\n"

    block = f"{BEGIN}\n{runtime_fragment.rstrip()}\n{END}\n"

    if BEGIN in content and END in content:
        start = content.index(BEGIN)
        end = content.index(END, start) + len(END)
        new_content = content[:start] + block + content[end:]
    else:
        if not content.endswith("\n"):
            content += "\n"
        if content.strip():
            content += "\n"
        new_content = content + block

    target_path.write_text(new_content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync role runtime block into AGENTS.md")
    parser.add_argument("--target", default=str(DEFAULT_AGENTS_PATH), help="target AGENTS.md path")
    args = parser.parse_args()

    runtime_fragment = RUNTIME_FRAGMENT_PATH.read_text(encoding="utf-8")
    target = Path(args.target).expanduser().resolve()
    upsert_block(target, runtime_fragment)
    print(f"synced role runtime to: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
