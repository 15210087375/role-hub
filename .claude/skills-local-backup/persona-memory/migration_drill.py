#!/usr/bin/env python3
import json
import shutil
import tempfile
from pathlib import Path

from persona_core import BehaviorMemory, read_yaml


def count_yaml_list(path: Path) -> int:
    data = read_yaml(path, [])
    return len(data) if isinstance(data, list) else 0


def snapshot(mem: BehaviorMemory) -> dict:
    return {
        "screenshot_path": mem.get_config("路径配置", "screenshot_path"),
        "intent_goals": count_yaml_list(mem.paths.intent_goals),
        "intent_prefs": count_yaml_list(mem.paths.intent_pref),
        "intent_constraints": count_yaml_list(mem.paths.intent_constraints),
        "l1": count_yaml_list(mem.paths.l1),
        "l2": count_yaml_list(mem.paths.l2),
        "l3": count_yaml_list(mem.paths.l3),
        "l4": count_yaml_list(mem.paths.l4),
    }


def main() -> None:
    source = BehaviorMemory()
    temp_dir = Path(tempfile.gettempdir())
    export_file = temp_dir / "persona_migration_drill_export.json"
    drill_root = temp_dir / "persona_memory_drill"

    if drill_root.exists():
        shutil.rmtree(drill_root)

    source.export_all(str(export_file))

    target = BehaviorMemory(str(drill_root))
    target.import_all(str(export_file), mode="replace")

    src = snapshot(source)
    dst = snapshot(target)

    checks = {
        "screenshot_path": src["screenshot_path"] == dst["screenshot_path"],
        "intent_goals": src["intent_goals"] == dst["intent_goals"],
        "intent_prefs": src["intent_prefs"] == dst["intent_prefs"],
        "intent_constraints": src["intent_constraints"] == dst["intent_constraints"],
        "l1": src["l1"] == dst["l1"],
        "l2": src["l2"] == dst["l2"],
        "l3": src["l3"] == dst["l3"],
        "l4": src["l4"] == dst["l4"],
    }

    result = {
        "export_file": str(export_file),
        "drill_root": str(drill_root),
        "source_snapshot": src,
        "target_snapshot": dst,
        "checks": checks,
        "all_passed": all(checks.values()),
    }

    out = temp_dir / "persona_migration_drill_result.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"result_file: {out}")


if __name__ == "__main__":
    main()
