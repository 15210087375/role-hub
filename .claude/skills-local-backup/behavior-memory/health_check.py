#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path.home() / ".behavior-memory"
SKILL = Path.home() / ".claude" / "skills" / "behavior-memory" / "persona_memory.py"


def run(cmd: List[str], timeout: int = 120) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def check_file(path: Path) -> Dict:
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file() if path.exists() else False,
    }


def check_task(name: str) -> Dict:
    code, out, err = run([
        "powershell",
        "-NoProfile",
        "-Command",
        f"schtasks /Query /TN '{name}' /V /FO LIST",
    ])
    ok = code == 0 and "TaskName:" in out
    last_result = None
    if ok:
        for line in out.splitlines():
            if line.strip().startswith("Last Result:"):
                last_result = line.split(":", 1)[1].strip()
                break
    return {
        "task": name,
        "ok": ok,
        "last_result": last_result,
        "error": err if not ok else "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Behavior memory health check")
    parser.add_argument("--full", action="store_true", help="run deeper checks (migration drill + e2e)")
    args = parser.parse_args()

    checks = []

    # Core status
    code, out, err = run(["python", str(ROOT / "persona_core.py"), "--status"])
    checks.append({"name": "core_status", "ok": code == 0, "detail": out if code == 0 else err})

    # Skill status
    code, out, err = run(["python", str(SKILL), "状态"])
    checks.append({"name": "skill_status", "ok": code == 0, "detail": out if code == 0 else err})

    # Policy and hit stats
    code_p, out_p, err_p = run(["python", str(ROOT / "persona_core.py"), "--policy"])
    checks.append({"name": "policy", "ok": code_p == 0, "detail": out_p if code_p == 0 else err_p})

    code_h, out_h, err_h = run(["python", str(ROOT / "persona_core.py"), "--hit-stats", "--hit-days", "30"])
    checks.append({"name": "hit_stats", "ok": code_h == 0, "detail": out_h if code_h == 0 else err_h})

    # Key files
    key_files = [
        ROOT / "persona_core.py",
        ROOT / "opencode_launcher.py",
        ROOT / "opencode_bridge.py",
        ROOT / "sync_memory.py",
        ROOT / "Meta" / "异常提醒.md",
        ROOT / "Meta" / "策略状态.yaml",
        ROOT / "Meta" / "命中监控.yaml",
    ]
    file_checks = [check_file(p) for p in key_files]
    checks.append({"name": "key_files", "ok": all(x["exists"] for x in file_checks), "detail": file_checks})

    # Command resolution
    code_c, out_c, err_c = run([
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-Command opencode | Format-List Source,CommandType,Path",
    ])
    checks.append({"name": "opencode_resolution", "ok": code_c == 0, "detail": out_c if code_c == 0 else err_c})

    # Scheduled tasks
    tasks = [
        "BehaviorMemoryWeeklyReview",
        "BehaviorMemoryMonthlyReport",
        "BehaviorMemoryDailyAnomalyReminder",
        "BehaviorMemoryGitSyncDaily",
        "BehaviorMemoryGitSyncWeekly",
    ]
    task_checks = [check_task(t) for t in tasks]
    checks.append({"name": "scheduled_tasks", "ok": all(x["ok"] for x in task_checks), "detail": task_checks})

    # Git status
    code_g, out_g, err_g = run(["python", str(ROOT / "sync_memory.py"), "status"])
    checks.append({"name": "git_sync_status", "ok": code_g == 0, "detail": out_g if code_g == 0 else err_g})

    if args.full:
        code_m, out_m, err_m = run(["python", str(ROOT / "migration_drill.py")], timeout=180)
        checks.append({"name": "migration_drill", "ok": code_m == 0 and "\"all_passed\": true" in out_m.lower(), "detail": out_m if code_m == 0 else err_m})

        code_e, out_e, err_e = run(["python", str(ROOT / "e2e_test.py")], timeout=240)
        checks.append({"name": "e2e_test", "ok": code_e == 0 and "ALL TESTS PASSED" in out_e, "detail": out_e if code_e == 0 else err_e})

    all_ok = all(c.get("ok", False) for c in checks)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "full" if args.full else "quick",
        "all_ok": all_ok,
        "checks": checks,
    }

    out_dir = ROOT / "Meta" / "health"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"all_ok": all_ok, "report": str(out_file)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
