#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / ".behavior-memory"
BRIDGE = ROOT / "opencode_bridge.py"
ACTIVE_PROMPT = ROOT / ".runtime" / "active_prompt.txt"
REAL_CMD = Path(r"D:\devTools\env\npm-global\opencode.real.cmd")
DEFAULT_AGENT = "behavior-memory-responder"
RUNTIME_DIR = ROOT / ".runtime"
LAUNCHER_LOG = RUNTIME_DIR / "launcher.log"


def log(msg: str) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n"
    LAUNCHER_LOG.write_text((LAUNCHER_LOG.read_text(encoding="utf-8") if LAUNCHER_LOG.exists() else "") + line, encoding="utf-8")


def build_prompt() -> str:
    if not ACTIVE_PROMPT.exists():
        return ""
    text = ACTIVE_PROMPT.read_text(encoding="utf-8").strip()
    if not text:
        return ""
    compact = " ".join([line.strip() for line in text.splitlines() if line.strip()])
    return compact[:1200]


def has_prompt_arg(args: list[str]) -> bool:
    return "--prompt" in args


def has_agent_arg(args: list[str]) -> bool:
    return "--agent" in args


def list_agents() -> list[str]:
    try:
        r = subprocess.run(["cmd", "/c", str(REAL_CMD), "agent", "list"], capture_output=True, text=True)
        out = r.stdout or ""
        names = []
        for line in out.splitlines():
            s = line.strip()
            if not s or s.startswith("[") or s.startswith("{"):
                continue
            if "(" in s:
                names.append(s.split("(", 1)[0].strip())
        return names
    except Exception:
        return []


def ensure_agent_file() -> None:
    target_dir = Path.home() / ".opencode" / "agent"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{DEFAULT_AGENT}.md"
    if target.exists():
        return

    candidates = [
        ROOT / "agent" / f"{DEFAULT_AGENT}.md",
        Path.home() / ".claude" / "skills" / "behavior-memory" / f"{DEFAULT_AGENT}.md",
    ]
    for c in candidates:
        if c.exists():
            target.write_text(c.read_text(encoding="utf-8"), encoding="utf-8")
            log(f"installed agent file from {c}")
            return


def select_agent() -> str:
    ensure_agent_file()
    agents = list_agents()
    if DEFAULT_AGENT in agents:
        return DEFAULT_AGENT
    log(f"default agent missing, fallback to build. agents={agents}")
    return "build"


def main() -> int:
    user_args = sys.argv[1:]

    if BRIDGE.exists():
        subprocess.run(["python", str(BRIDGE), "pre", "--topic", "opencode session"], check=False)

    final_args = list(user_args)
    # Keep new chat clean by default.
    # If you explicitly want visible prompt injection, set:
    #   OPENCODE_MEMORY_PROMPT_MODE=visible
    prompt_mode = os.environ.get("OPENCODE_MEMORY_PROMPT_MODE", "off").lower()
    if prompt_mode == "visible":
        prompt = build_prompt()
        if prompt and not has_prompt_arg(final_args):
            final_args.extend(["--prompt", prompt])

    if not has_agent_arg(final_args):
        final_args.extend(["--agent", select_agent()])

    cmd = ["cmd", "/c", str(REAL_CMD), *final_args]
    result = subprocess.run(cmd)

    if BRIDGE.exists():
        subprocess.run(["python", str(BRIDGE), "post"], check=False)

    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
