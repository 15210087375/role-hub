#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path.home() / ".behavior-memory"
SKILL = Path.home() / ".claude" / "skills" / "behavior-memory" / "persona_memory.py"
AUTO = ROOT / "auto_runtime.py"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd)}\n{r.stderr}\n{r.stdout}")
    return r.stdout.strip()


def main() -> None:
    print("[1] status")
    out = run(["python", str(SKILL), "状态"])
    assert "截图路径" in out

    print("[2] read screenshot path")
    out = run(["python", str(SKILL), "配置", "获取", "路径配置.screenshot_path"])
    assert "snapshot" in out.lower()

    print("[3] add intent and build context")
    run(["python", str(SKILL), "添加意图", "偏好与要求", "回答先给结论", "high"])
    out = run(["python", str(SKILL), "构建上下文"])
    ctx = json.loads(out)
    assert ctx["profile"]["screenshot_path"]

    print("[4] session start -> prompt file")
    run(["python", str(AUTO), "--session-start", "e2e test session"])
    active_prompt = ROOT / ".runtime" / "active_prompt.txt"
    assert active_prompt.exists()

    print("[5] session end -> layer write")
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8") as f:
        json.dump(
            [
                {"role": "user", "content": "请基于偏好回答"},
                {"role": "assistant", "content": "结论：可以。"},
            ],
            f,
            ensure_ascii=False,
        )
        msg_file = f.name
    run(["python", str(AUTO), "--session-end", "--messages-file", msg_file])
    os.unlink(msg_file)
    assert not active_prompt.exists()

    print("[6] export/import")
    backup = Path(tempfile.gettempdir()) / "persona_e2e_backup.json"
    run(["python", str(SKILL), "导出", str(backup)])
    assert backup.exists()
    run(["python", str(SKILL), "导入", str(backup), "merge"])

    print("[7] verify L3 has data")
    l3 = ROOT / "Memory" / "L3_认知层.yaml"
    text = l3.read_text(encoding="utf-8")
    assert "thinking_pattern" in text

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
