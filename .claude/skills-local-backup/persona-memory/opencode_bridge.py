#!/usr/bin/env python3
import argparse
import json
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path.home() / ".behavior-memory"
RUNTIME = ROOT / ".runtime"
RUNTIME.mkdir(parents=True, exist_ok=True)
MARKER = RUNTIME / "opencode_hook_marker.json"
MESSAGES_FILE = RUNTIME / "opencode_last_messages.json"

DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
AUTO = ROOT / "auto_runtime.py"


def now_ms(cur: sqlite3.Cursor) -> int:
    row = cur.execute("select cast(strftime('%s','now') as integer) * 1000").fetchone()
    return int(row[0]) if row else 0


def pre(topic: str) -> None:
    if DB.exists():
        con = sqlite3.connect(str(DB))
        cur = con.cursor()
        t = now_ms(cur)
        con.close()
    else:
        t = 0
    MARKER.write_text(json.dumps({"time_ms": t, "topic": topic}, ensure_ascii=False), encoding="utf-8")
    subprocess.run(
        ["python", str(AUTO), "--session-start", topic],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _pick_session(con: sqlite3.Connection, marker_ms: int) -> str:
    cur = con.cursor()
    row = cur.execute(
        "select id from session where time_updated >= ? order by time_updated desc limit 1",
        (marker_ms,),
    ).fetchone()
    if row:
        return str(row[0])
    row = cur.execute("select id from session order by time_updated desc limit 1").fetchone()
    return str(row[0]) if row else ""


def _message_text(con: sqlite3.Connection, message_id: str) -> str:
    cur = con.cursor()
    rows = cur.execute(
        "select data from part where message_id = ? order by time_created asc",
        (message_id,),
    ).fetchall()
    chunks: List[str] = []
    for (raw,) in rows:
        try:
            data = json.loads(raw)
        except Exception:
            continue
        if data.get("type") == "text":
            txt = str(data.get("text", "")).strip()
            if txt:
                chunks.append(txt)
    return "\n".join(chunks).strip()


def _extract_messages(con: sqlite3.Connection, session_id: str) -> List[Dict[str, str]]:
    cur = con.cursor()
    rows = cur.execute(
        "select id, data from message where session_id = ? order by time_created asc",
        (session_id,),
    ).fetchall()
    out: List[Dict[str, str]] = []
    for msg_id, raw in rows:
        role = "assistant"
        try:
            data = json.loads(raw)
            role = str(data.get("role", "assistant"))
        except Exception:
            pass
        content = _message_text(con, msg_id)
        if role in ["user", "assistant"] and content:
            out.append({"role": role, "content": content})
    return out


def post() -> None:
    marker_ms = 0
    if MARKER.exists():
        try:
            marker_ms = int(json.loads(MARKER.read_text(encoding="utf-8")).get("time_ms", 0))
        except Exception:
            marker_ms = 0

    if not DB.exists():
        subprocess.run(
            ["python", str(AUTO), "--session-end"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return

    con = sqlite3.connect(str(DB))
    session_id = _pick_session(con, marker_ms)
    messages = _extract_messages(con, session_id) if session_id else []
    con.close()

    MESSAGES_FILE.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run(
        ["python", str(AUTO), "--session-end", "--messages-file", str(MESSAGES_FILE)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["pre", "post"])
    parser.add_argument("--topic", default="opencode chat")
    args = parser.parse_args()
    if args.mode == "pre":
        pre(args.topic)
    else:
        post()


if __name__ == "__main__":
    main()
