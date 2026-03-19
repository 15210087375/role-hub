#!/usr/bin/env python3
import argparse
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path.home() / ".behavior-memory"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(ROOT), check=check, text=True, capture_output=True)


def ensure_repo() -> None:
    if not (ROOT / ".git").exists():
        raise RuntimeError(f"not a git repo: {ROOT}")


def print_step(title: str) -> None:
    print(f"\n== {title} ==")


def git_status_short() -> str:
    r = run(["git", "status", "--short"], check=False)
    return (r.stdout or "").strip()


def sync(message: str | None = None) -> None:
    ensure_repo()

    print_step("Pull latest")
    r = run(["git", "pull", "--rebase", "--autostash"], check=False)
    print((r.stdout or r.stderr or "").strip())
    if r.returncode != 0:
        raise RuntimeError("git pull --rebase --autostash failed, please resolve manually")

    print_step("Stage changes")
    run(["git", "add", "-A"])

    changed = git_status_short()
    if not changed:
        print("No local changes, skip commit")
    else:
        print(changed)
        print_step("Commit")
        msg = message or f"memory sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        r = run(["git", "commit", "-m", msg], check=False)
        out = (r.stdout or r.stderr or "").strip()
        print(out)
        if r.returncode != 0 and "nothing to commit" not in out.lower():
            raise RuntimeError("git commit failed")

    print_step("Push")
    r = run(["git", "push"], check=False)
    print((r.stdout or r.stderr or "").strip())
    if r.returncode != 0:
        raise RuntimeError("git push failed")

    print("\nSync completed")


def status() -> None:
    ensure_repo()
    print_step("Repository")
    print(ROOT)
    print_step("Remote")
    print(run(["git", "remote", "-v"], check=False).stdout.strip())
    print_step("Branch")
    print(run(["git", "branch", "--show-current"], check=False).stdout.strip())
    print_step("Status")
    s = git_status_short()
    print(s if s else "clean")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync behavior memory repo")
    sub = parser.add_subparsers(dest="cmd")

    p_sync = sub.add_parser("sync", help="pull + add + commit + push")
    p_sync.add_argument("--message", help="commit message")

    sub.add_parser("status", help="show repo status")

    args = parser.parse_args()
    if args.cmd == "sync":
        sync(args.message)
    else:
        status()


if __name__ == "__main__":
    main()
