#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from persona_core import BehaviorMemory


RUNTIME_DIR = Path.home() / ".behavior-memory" / ".runtime"
CURRENT_SESSION = RUNTIME_DIR / "current_session.json"
ACTIVE_PROMPT = RUNTIME_DIR / "active_prompt.txt"


def session_id() -> str:
    return datetime.now().strftime("sess_%Y%m%d_%H%M%S")


def start_session(topic: str) -> Dict[str, Any]:
    mem = BehaviorMemory()
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    sid = session_id()
    ctx = mem.build_session_context()
    payload = {
        "session_id": sid,
        "topic": topic,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "context": ctx,
    }
    with CURRENT_SESSION.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    ACTIVE_PROMPT.write_text(build_prompt(ctx), encoding="utf-8")
    return payload


def build_prompt(ctx: Dict[str, Any]) -> str:
    profile = ctx.get("profile", {})
    hints = ctx.get("adapter_hints", [])
    lines = [
        "[Persona Memory Context]",
        f"screenshot_path: {profile.get('screenshot_path')}",
        "apply these hints when answering:",
    ]
    if hints:
        for h in hints:
            lines.append(f"- {h}")
    else:
        lines.append("- no strong hint yet, keep concise and structured")
    return "\n".join(lines)


def end_session(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    mem = BehaviorMemory()
    if CURRENT_SESSION.exists():
        with CURRENT_SESSION.open("r", encoding="utf-8") as f:
            session = json.load(f)
        sid = session.get("session_id", session_id())
    else:
        sid = session_id()
    mem.write_conversation(sid, messages)
    result = {
        "session_id": sid,
        "written_messages": len(messages),
        "ended_at": datetime.now().isoformat(timespec="seconds"),
    }
    if CURRENT_SESSION.exists():
        CURRENT_SESSION.unlink()
    if ACTIVE_PROMPT.exists():
        ACTIVE_PROMPT.unlink()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-start", help="会话主题")
    parser.add_argument("--session-end", action="store_true")
    parser.add_argument("--messages-file", help="JSON消息文件路径")
    args = parser.parse_args()

    if args.session_start:
        print(json.dumps(start_session(args.session_start), ensure_ascii=False, indent=2))
        return

    if args.session_end:
        messages: List[Dict[str, str]] = []
        if args.messages_file:
            with open(args.messages_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
        print(json.dumps(end_session(messages), ensure_ascii=False, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
