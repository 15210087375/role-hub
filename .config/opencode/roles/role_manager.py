#!/usr/bin/env python3
import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


BASE_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = BASE_DIR / "index.json"
DECISIONS_LOG_PATH = BASE_DIR / "decisions.log"


def now_iso_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def now_iso_datetime() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


def audit_enabled(args: argparse.Namespace) -> bool:
    if bool(getattr(args, "audit", False)):
        return True
    env_val = str(os.getenv("OPENCODE_ROLE_AUDIT", "")).strip().lower()
    return env_val in {"1", "true", "yes", "on"}


def tokenize(text: str) -> set:
    parts = re.findall(r"[a-z0-9]+", text.lower())
    return {p for p in parts if len(p) > 1}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a.intersection(b))
    union = len(a.union(b))
    return inter / union if union else 0.0


def load_registry() -> Dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(registry: Dict) -> None:
    registry["updated_at"] = now_iso_date()
    REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def normalize_code(code: str) -> str:
    return code.strip().lower()


def all_code_map(registry: Dict) -> Dict[str, str]:
    code_map: Dict[str, str] = {}
    for role in registry.get("roles", []):
        rid = role.get("id", "")
        for code in role.get("codes", []):
            key = normalize_code(str(code))
            if key:
                code_map[key] = rid
    return code_map


def ensure_codes_unique(registry: Dict, role_id: str, codes: List[str]) -> Tuple[bool, str]:
    existing = all_code_map(registry)
    for code in codes:
        key = normalize_code(code)
        if not key:
            continue
        owner = existing.get(key)
        if owner and owner != role_id:
            return False, code
    return True, ""


def find_role_by_code(registry: Dict, code: str) -> Dict:
    target = normalize_code(code)
    for role in registry.get("roles", []):
        for candidate in role.get("codes", []):
            if normalize_code(str(candidate)) == target:
                return role
    return {}


def normalize_text(text: str) -> str:
    raw = str(text or "").strip().lower()
    no_space = re.sub(r"\s+", "", raw)
    return re.sub(r"[^0-9a-z\u4e00-\u9fff-]", "", no_space)


def find_role_by_input(registry: Dict, user_input: str) -> Tuple[Dict, str, str]:
    raw = str(user_input or "").strip()
    if not raw:
        return {}, "", ""

    normalized = normalize_text(raw)
    suffixes = ["", "模式", "模式开启", "模式启动"]
    strong_prefixes = ["你好", "hi", "hello", "hey", "进入", "切换", "启用", "开启"]
    greeting_suffixes = ["你好"]

    for role in registry.get("roles", []):
        for code in role.get("codes", []):
            code_raw = str(code).strip()
            code_norm = normalize_text(code_raw)
            if not code_norm:
                continue
            for s in suffixes:
                if normalized == normalize_text(code_raw + s):
                    return role, "code", code_raw + s
            for p in strong_prefixes:
                if normalized == normalize_text(p + code_raw):
                    return role, "code", p + code_raw
                for s in suffixes[1:]:
                    if normalized == normalize_text(p + code_raw + s):
                        return role, "code", p + code_raw + s
            for s in greeting_suffixes:
                if normalized == normalize_text(code_raw + s):
                    return role, "code", code_raw + s

    for role in registry.get("roles", []):
        for trig in role.get("triggers", []):
            trig_raw = str(trig).strip()
            if not trig_raw:
                continue
            if normalized == normalize_text(trig_raw):
                return role, "trigger", trig_raw

    return {}, "", ""


def touch_role_if_needed(registry: Dict, role_id: str) -> Tuple[bool, bool]:
    today = now_iso_date()
    for role in registry.get("roles", []):
        if role.get("id") != role_id:
            continue
        changed = False
        if role.get("last_used_at") != today:
            role["last_used_at"] = today
            changed = True
        if role.get("status") == "draft":
            role["status"] = "active"
            changed = True
        return True, changed
    return False, False


def role_to_text_fields(role: Dict) -> Dict[str, str]:
    return {
        "mission": role.get("purpose", ""),
        "output": " ".join(role.get("outputs", [])),
        "guardrail": " ".join(role.get("guardrails", [])),
        "tooling": " ".join(role.get("tooling", [])),
    }


def candidate_to_text_fields(candidate: Dict) -> Dict[str, str]:
    return {
        "mission": candidate.get("purpose", ""),
        "output": " ".join(candidate.get("outputs", [])),
        "guardrail": " ".join(candidate.get("guardrails", [])),
        "tooling": " ".join(candidate.get("tooling", [])),
    }


def score_candidate(registry: Dict, candidate: Dict) -> Tuple[List[Dict], Dict, str]:
    settings = registry.get("settings", {})
    weights = settings.get(
        "weights",
        {"mission": 0.4, "output": 0.3, "guardrail": 0.2, "tooling": 0.1},
    )
    thresholds = settings.get("overlap_thresholds", {"reuse_gte": 0.82, "merge_gte": 0.65})

    cand_fields = candidate_to_text_fields(candidate)
    scored = []

    for role in registry.get("roles", []):
        role_fields = role_to_text_fields(role)
        axis = {}
        total = 0.0
        for key in ("mission", "output", "guardrail", "tooling"):
            sim = jaccard(tokenize(cand_fields[key]), tokenize(role_fields[key]))
            axis[key] = round(sim, 3)
            total += sim * float(weights.get(key, 0.0))
        scored.append(
            {
                "id": role.get("id"),
                "status": role.get("status", "active"),
                "scores": axis,
                "total": round(total, 3),
            }
        )

    scored.sort(key=lambda x: x["total"], reverse=True)
    best = scored[0] if scored else None

    if not best:
        decision = "create"
    elif best["total"] >= float(thresholds.get("reuse_gte", 0.82)):
        decision = "reuse"
    elif best["total"] >= float(thresholds.get("merge_gte", 0.65)):
        decision = "merge"
    else:
        decision = "create"

    return scored, best or {}, decision


def append_decision_log(record: Dict) -> None:
    with DECISIONS_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


def scaffold_role_file(role_id: str, title: str, purpose: str) -> Path:
    if not re.fullmatch(r"role-[a-z0-9-]+", role_id):
        raise ValueError("role id must match role-<ascii-id>")

    target = BASE_DIR / f"{role_id}.md"
    if target.exists():
        return target

    body = (
        f"# {role_id}\n\n"
        f"## Mission\n\n"
        f"{purpose or 'Define the role mission.'}\n\n"
        f"## Workflow\n\n"
        f"1. Intake\n"
        f"- Capture key inputs and constraints.\n\n"
        f"2. Plan\n"
        f"- Propose the shortest safe path to outcome.\n\n"
        f"3. Execute\n"
        f"- Perform role-scoped actions.\n\n"
        f"4. Validate\n"
        f"- Verify against acceptance criteria.\n\n"
        f"5. Report\n"
        f"- Return concise output and next step.\n\n"
        f"## Output Contract\n\n"
        f"1. Decision or recommendation\n"
        f"2. Key rationale\n"
        f"3. Concrete next action\n\n"
        f"## Guardrails\n\n"
        f"- Stay within role boundary.\n"
        f"- Escalate risky or ambiguous requests.\n"
    )
    target.write_text(body, encoding="utf-8")
    return target


def add_role_to_registry(registry: Dict, candidate: Dict) -> None:
    codes = candidate.get("codes", [])
    if not codes:
        codes = [candidate["id"].replace("role-", "").upper()]
    role = {
        "id": candidate["id"],
        "title": candidate.get("title") or candidate["id"],
        "status": candidate.get("status", "draft"),
        "created_at": now_iso_date(),
        "last_used_at": now_iso_date(),
        "purpose": candidate.get("purpose", ""),
        "triggers": candidate.get("triggers", []),
        "outputs": candidate.get("outputs", []),
        "guardrails": candidate.get("guardrails", []),
        "tooling": candidate.get("tooling", []),
        "owner": candidate.get("owner", "system"),
        "tags": candidate.get("tags", []),
        "codes": codes,
    }
    registry.setdefault("roles", []).append(role)


def update_last_used(registry: Dict, role_id: str) -> bool:
    for role in registry.get("roles", []):
        if role.get("id") == role_id:
            role["last_used_at"] = now_iso_date()
            if role.get("status") == "draft":
                role["status"] = "active"
            return True
    return False


def archive_stale(registry: Dict, days: int) -> List[str]:
    changed = []
    now = datetime.now(timezone.utc).date()
    for role in registry.get("roles", []):
        if role.get("status") == "archived":
            continue
        last_used = role.get("last_used_at") or role.get("created_at")
        if not last_used:
            continue
        try:
            date_val = datetime.fromisoformat(last_used).date()
        except ValueError:
            continue
        age = (now - date_val).days
        if age >= days:
            role["status"] = "archived"
            changed.append(role.get("id", ""))
    return [r for r in changed if r]


def build_candidate(args: argparse.Namespace) -> Dict:
    return {
        "id": args.id,
        "title": args.title,
        "status": args.status,
        "purpose": args.purpose,
        "triggers": args.triggers,
        "outputs": args.outputs,
        "guardrails": args.guardrails,
        "tooling": args.tooling,
        "owner": args.owner,
        "tags": args.tags,
        "codes": args.codes,
    }


def command_evaluate(args: argparse.Namespace) -> int:
    total_start = time.perf_counter()
    t0 = time.perf_counter()
    registry = load_registry()
    load_registry_ms = elapsed_ms(t0)

    candidate = build_candidate(args)

    t1 = time.perf_counter()
    scored, best, decision = score_candidate(registry, candidate)
    score_candidate_ms = elapsed_ms(t1)

    result = {
        "decision": decision,
        "candidate_role_id": candidate["id"],
        "target_role_id": best.get("id"),
        "best_score": best.get("total", 0.0),
        "top_matches": scored[:3],
        "timing": {
            "load_registry_ms": load_registry_ms,
            "score_candidate_ms": score_candidate_ms,
            "total_ms": elapsed_ms(total_start),
        },
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


def command_create(args: argparse.Namespace) -> int:
    total_start = time.perf_counter()
    t0 = time.perf_counter()
    registry = load_registry()
    load_registry_ms = elapsed_ms(t0)

    candidate = build_candidate(args)

    existing_ids = {r.get("id") for r in registry.get("roles", [])}
    if candidate["id"] in existing_ids:
        print(json.dumps({"error": "role id already exists", "id": candidate["id"]}, ensure_ascii=True))
        return 1

    ok, conflict_code = ensure_codes_unique(registry, candidate["id"], candidate.get("codes", []))
    if not ok:
        print(
            json.dumps(
                {
                    "error": "role code conflict",
                    "code": conflict_code,
                    "message": "code already assigned to another role",
                },
                ensure_ascii=True,
            )
        )
        return 1

    t1 = time.perf_counter()
    scored, best, decision = score_candidate(registry, candidate)
    score_candidate_ms = elapsed_ms(t1)
    if decision != "create" and not args.force:
        print(
            json.dumps(
                {
                    "decision": decision,
                    "candidate_role_id": candidate["id"],
                    "target_role_id": best.get("id"),
                    "best_score": best.get("total", 0.0),
                    "message": "not created; use --force to override",
                    "timing": {
                        "load_registry_ms": load_registry_ms,
                        "score_candidate_ms": score_candidate_ms,
                        "total_ms": elapsed_ms(total_start),
                    },
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 2

    t2 = time.perf_counter()
    path = scaffold_role_file(candidate["id"], candidate.get("title", ""), candidate.get("purpose", ""))
    scaffold_role_file_ms = elapsed_ms(t2)

    t3 = time.perf_counter()
    add_role_to_registry(registry, candidate)
    save_registry(registry)
    save_registry_ms = elapsed_ms(t3)

    record = {
        "timestamp": now_iso_datetime(),
        "candidate_role_id": candidate["id"],
        "decision": "create",
        "target_role_id": candidate["id"],
        "confidence": "high" if decision == "create" else "low",
        "scores": {
            "mission": best.get("scores", {}).get("mission", 0.0),
            "output": best.get("scores", {}).get("output", 0.0),
            "guardrail": best.get("scores", {}).get("guardrail", 0.0),
            "tooling": best.get("scores", {}).get("tooling", 0.0),
            "total": best.get("total", 0.0),
        },
        "top_matches": [{"id": s.get("id"), "score": s.get("total", 0.0)} for s in scored[:3]],
        "reason": "Role created by role_manager create command.",
        "next_action": "Use hr mode to route tasks to the new role.",
    }
    should_audit = audit_enabled(args)
    append_decision_log_ms = 0.0
    pre_log_total_ms = elapsed_ms(total_start)
    if should_audit:
        t4 = time.perf_counter()
        record["timing"] = {
            "load_registry_ms": load_registry_ms,
            "score_candidate_ms": score_candidate_ms,
            "scaffold_role_file_ms": scaffold_role_file_ms,
            "save_registry_ms": save_registry_ms,
            "pre_log_total_ms": pre_log_total_ms,
        }
        append_decision_log(record)
        append_decision_log_ms = elapsed_ms(t4)

    output_total_ms = elapsed_ms(total_start)

    print(
        json.dumps(
            {
                "created": candidate["id"],
                "file": str(path),
                "timing": {
                    "load_registry_ms": load_registry_ms,
                    "score_candidate_ms": score_candidate_ms,
                    "scaffold_role_file_ms": scaffold_role_file_ms,
                    "save_registry_ms": save_registry_ms,
                    "pre_log_total_ms": pre_log_total_ms,
                    "append_decision_log_ms": append_decision_log_ms,
                    "audit_logged": should_audit,
                    "total_ms": output_total_ms,
                },
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


def command_touch(args: argparse.Namespace) -> int:
    total_start = time.perf_counter()
    t0 = time.perf_counter()
    registry = load_registry()
    load_registry_ms = elapsed_ms(t0)

    t1 = time.perf_counter()
    ok = update_last_used(registry, args.id)
    update_last_used_ms = elapsed_ms(t1)
    if not ok:
        print(json.dumps({"error": "role not found", "id": args.id}, ensure_ascii=True))
        return 1

    t2 = time.perf_counter()
    save_registry(registry)
    save_registry_ms = elapsed_ms(t2)

    print(
        json.dumps(
            {
                "updated": args.id,
                "last_used_at": now_iso_date(),
                "timing": {
                    "load_registry_ms": load_registry_ms,
                    "update_last_used_ms": update_last_used_ms,
                    "save_registry_ms": save_registry_ms,
                    "total_ms": elapsed_ms(total_start),
                },
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


def command_archive_stale(args: argparse.Namespace) -> int:
    total_start = time.perf_counter()
    t0 = time.perf_counter()
    registry = load_registry()
    load_registry_ms = elapsed_ms(t0)

    stale_days = int(args.days or registry.get("settings", {}).get("stale_days", 90))

    t1 = time.perf_counter()
    archived = archive_stale(registry, stale_days)
    archive_stale_ms = elapsed_ms(t1)

    save_registry_ms = 0
    if archived:
        t2 = time.perf_counter()
        save_registry(registry)
        save_registry_ms = elapsed_ms(t2)

    print(
        json.dumps(
            {
                "archived": archived,
                "days": stale_days,
                "timing": {
                    "load_registry_ms": load_registry_ms,
                    "archive_stale_ms": archive_stale_ms,
                    "save_registry_ms": save_registry_ms,
                    "total_ms": elapsed_ms(total_start),
                },
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


def command_resolve(args: argparse.Namespace) -> int:
    total_start = time.perf_counter()
    t0 = time.perf_counter()
    registry = load_registry()
    load_registry_ms = elapsed_ms(t0)

    t1 = time.perf_counter()
    role = find_role_by_code(registry, args.code)
    resolve_code_ms = elapsed_ms(t1)
    if not role:
        print(
            json.dumps(
                {
                    "found": False,
                    "code": args.code,
                    "message": "no role mapped to this code",
                    "timing": {
                        "load_registry_ms": load_registry_ms,
                        "resolve_code_ms": resolve_code_ms,
                        "total_ms": elapsed_ms(total_start),
                    },
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 1

    print(
        json.dumps(
            {
                "found": True,
                "code": args.code,
                "role_id": role.get("id"),
                "title": role.get("title"),
                "status": role.get("status"),
                "codes": role.get("codes", []),
                "timing": {
                    "load_registry_ms": load_registry_ms,
                    "resolve_code_ms": resolve_code_ms,
                    "total_ms": elapsed_ms(total_start),
                },
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


def command_add_code(args: argparse.Namespace) -> int:
    total_start = time.perf_counter()
    t0 = time.perf_counter()
    registry = load_registry()
    load_registry_ms = elapsed_ms(t0)

    role_id = args.id
    new_code = args.code.strip()
    if not new_code:
        print(json.dumps({"error": "empty code"}, ensure_ascii=True))
        return 1

    t1 = time.perf_counter()
    ok, conflict_code = ensure_codes_unique(registry, role_id, [new_code])
    ensure_codes_unique_ms = elapsed_ms(t1)
    if not ok:
        print(
            json.dumps(
                {
                    "error": "role code conflict",
                    "code": conflict_code,
                    "message": "code already assigned to another role",
                    "timing": {
                        "load_registry_ms": load_registry_ms,
                        "ensure_codes_unique_ms": ensure_codes_unique_ms,
                        "total_ms": elapsed_ms(total_start),
                    },
                },
                ensure_ascii=True,
            )
        )
        return 1

    t2 = time.perf_counter()
    for role in registry.get("roles", []):
        if role.get("id") != role_id:
            continue
        codes = role.get("codes", [])
        if normalize_code(new_code) not in {normalize_code(c) for c in codes}:
            codes.append(new_code)
        role["codes"] = codes
        update_codes_ms = elapsed_ms(t2)

        t3 = time.perf_counter()
        save_registry(registry)
        save_registry_ms = elapsed_ms(t3)

        print(
            json.dumps(
                {
                    "updated": role_id,
                    "codes": codes,
                    "timing": {
                        "load_registry_ms": load_registry_ms,
                        "ensure_codes_unique_ms": ensure_codes_unique_ms,
                        "update_codes_ms": update_codes_ms,
                        "save_registry_ms": save_registry_ms,
                        "total_ms": elapsed_ms(total_start),
                    },
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 0

    print(
        json.dumps(
            {
                "error": "role not found",
                "id": role_id,
                "timing": {
                    "load_registry_ms": load_registry_ms,
                    "ensure_codes_unique_ms": ensure_codes_unique_ms,
                    "total_ms": elapsed_ms(total_start),
                },
            },
            ensure_ascii=True,
        )
    )
    return 1


def command_activate(args: argparse.Namespace) -> int:
    total_start = time.perf_counter()

    t0 = time.perf_counter()
    registry = load_registry()
    load_registry_ms = elapsed_ms(t0)

    t1 = time.perf_counter()
    role, match_type, matched_value = find_role_by_input(registry, args.input)
    resolve_input_ms = elapsed_ms(t1)

    if not role:
        print(
            json.dumps(
                {
                    "found": False,
                    "input": args.input,
                    "message": "no role mapped from this input",
                    "timing": {
                        "load_registry_ms": load_registry_ms,
                        "resolve_input_ms": resolve_input_ms,
                        "total_ms": elapsed_ms(total_start),
                    },
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 1

    save_registry_ms = 0.0
    touch_needed_ms = 0.0
    touched = False
    if args.touch:
        t2 = time.perf_counter()
        found, changed = touch_role_if_needed(registry, role.get("id", ""))
        touch_needed_ms = elapsed_ms(t2)
        if found and changed:
            t3 = time.perf_counter()
            save_registry(registry)
            save_registry_ms = elapsed_ms(t3)
            touched = True

    record = {
        "timestamp": now_iso_datetime(),
        "candidate_role_id": role.get("id"),
        "decision": "reuse",
        "target_role_id": role.get("id"),
        "confidence": "high",
        "scores": {
            "mission": 1.0,
            "output": 1.0,
            "guardrail": 1.0,
            "tooling": 1.0,
            "total": 1.0,
        },
        "top_matches": [{"id": role.get("id"), "score": 1.0}],
        "reason": f"User invoked role via {match_type} alias '{matched_value}'.",
        "next_action": "Enter role workflow and collect task scope.",
    }

    should_audit = audit_enabled(args)
    append_decision_log_ms = 0.0
    if should_audit:
        t4 = time.perf_counter()
        record["timing"] = {
            "load_registry_ms": load_registry_ms,
            "resolve_input_ms": resolve_input_ms,
            "touch_needed_ms": touch_needed_ms,
            "save_registry_ms": save_registry_ms,
            "pre_log_total_ms": elapsed_ms(total_start),
        }
        append_decision_log(record)
        append_decision_log_ms = elapsed_ms(t4)

    print(
        json.dumps(
            {
                "found": True,
                "input": args.input,
                "role_id": role.get("id"),
                "title": role.get("title"),
                "status": role.get("status"),
                "match_type": match_type,
                "matched_value": matched_value,
                "registry_touched": touched,
                "timing": {
                    "load_registry_ms": load_registry_ms,
                    "resolve_input_ms": resolve_input_ms,
                    "touch_needed_ms": touch_needed_ms,
                    "save_registry_ms": save_registry_ms,
                    "append_decision_log_ms": append_decision_log_ms,
                    "audit_logged": should_audit,
                    "total_ms": elapsed_ms(total_start),
                },
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Role hub management utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--id", required=True, help="role id, e.g. role-pm")
        p.add_argument("--title", default="", help="role title")
        p.add_argument("--status", default="draft", choices=["draft", "active", "archived"])
        p.add_argument("--purpose", default="", help="role purpose text")
        p.add_argument("--owner", default="system")
        p.add_argument("--triggers", nargs="*", default=[])
        p.add_argument("--outputs", nargs="*", default=[])
        p.add_argument("--guardrails", nargs="*", default=[])
        p.add_argument("--tooling", nargs="*", default=[])
        p.add_argument("--tags", nargs="*", default=[])
        p.add_argument("--codes", nargs="*", default=[])

    p_eval = sub.add_parser("evaluate", help="score overlap and suggest decision")
    add_common_flags(p_eval)
    p_eval.set_defaults(func=command_evaluate)

    p_create = sub.add_parser("create", help="create a role if overlap allows")
    add_common_flags(p_create)
    p_create.add_argument("--force", action="store_true", help="create even if reuse/merge is suggested")
    p_create.add_argument("--audit", action="store_true", help="append decision log for this command")
    p_create.set_defaults(func=command_create)

    p_touch = sub.add_parser("touch", help="update last_used_at for a role")
    p_touch.add_argument("--id", required=True)
    p_touch.set_defaults(func=command_touch)

    p_archive = sub.add_parser("archive-stale", help="archive roles unused for N days")
    p_archive.add_argument("--days", type=int, default=0)
    p_archive.set_defaults(func=command_archive_stale)

    p_resolve = sub.add_parser("resolve", help="resolve role by alias code")
    p_resolve.add_argument("--code", required=True, help="role code alias, e.g. HR or FG")
    p_resolve.set_defaults(func=command_resolve)

    p_add_code = sub.add_parser("add-code", help="add alias code to an existing role")
    p_add_code.add_argument("--id", required=True, help="target role id")
    p_add_code.add_argument("--code", required=True, help="alias code")
    p_add_code.set_defaults(func=command_add_code)

    p_activate = sub.add_parser("activate", help="fast role activation by raw user input")
    p_activate.add_argument("--input", required=True, help="raw user input, e.g. 主理人模式")
    p_activate.add_argument("--touch", action="store_true", help="update last_used_at and save registry")
    p_activate.add_argument("--audit", action="store_true", help="append decision log for this command")
    p_activate.set_defaults(func=command_activate)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
