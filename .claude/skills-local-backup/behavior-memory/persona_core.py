#!/usr/bin/env python3
import argparse
import json
import os
import uuid
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter

import yaml


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def read_yaml(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return default if data is None else data


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@dataclass
class Paths:
    root: Path
    memory: Path
    intent: Path
    meta: Path
    config: Path
    backups: Path
    l0: Path
    l1: Path
    l2: Path
    l3: Path
    l4: Path
    intent_goals: Path
    intent_pref: Path
    intent_constraints: Path
    cfg_paths: Path
    cfg_device: Path
    cfg_tools: Path
    cfg_workflow: Path
    cfg_sync: Path
    cfg_storage: Path
    meta_insight_queue: Path
    meta_evolution: Path
    meta_alert_md: Path
    meta_hit_monitor: Path
    meta_policy_state: Path


class BehaviorMemory:
    def __init__(self, root: Optional[str] = None) -> None:
        base = Path(root) if root else (Path.home() / ".behavior-memory")
        self.paths = Paths(
            root=base,
            memory=base / "Memory",
            intent=base / "Intent",
            meta=base / "Meta",
            config=base / "Config",
            backups=base / "Backups",
            l0=base / "Memory" / "L0_状态层",
            l1=base / "Memory" / "L1_情境层.yaml",
            l2=base / "Memory" / "L2_行为层.yaml",
            l3=base / "Memory" / "L3_认知层.yaml",
            l4=base / "Memory" / "L4_核心层.yaml",
            intent_goals=base / "Intent" / "目标与规划.yaml",
            intent_pref=base / "Intent" / "偏好与要求.yaml",
            intent_constraints=base / "Intent" / "约束与边界.yaml",
            cfg_paths=base / "Config" / "路径配置.yaml",
            cfg_device=base / "Config" / "设备配置.yaml",
            cfg_tools=base / "Config" / "工具配置.yaml",
            cfg_workflow=base / "Config" / "工作流配置.yaml",
            cfg_sync=base / "Config" / "同步配置.yaml",
            cfg_storage=base / "Config" / "存储配置.yaml",
            meta_insight_queue=base / "Meta" / "洞察队列.yaml",
            meta_evolution=base / "Meta" / "框架演变.yaml",
            meta_alert_md=base / "Meta" / "异常提醒.md",
            meta_hit_monitor=base / "Meta" / "命中监控.yaml",
            meta_policy_state=base / "Meta" / "策略状态.yaml",
        )
        self._ensure_structure()
    def _ensure_structure(self) -> None:
        for d in [
            self.paths.root,
            self.paths.memory,
            self.paths.intent,
            self.paths.meta,
            self.paths.config,
            self.paths.backups,
            self.paths.l0,
            self.paths.meta / "复盘记录",
        ]:
            d.mkdir(parents=True, exist_ok=True)

        if not self.paths.cfg_workflow.exists():
            write_yaml(
                self.paths.cfg_workflow,
                {
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                    "screenshot_workflow": {
                        "auto_save": True,
                        "path_key": "路径配置.screenshot_path",
                    },
                    "memory_workflow": {
                        "auto_load_on_session_start": True,
                        "auto_write_on_session_end": True,
                    },
                },
            )

        if not self.paths.cfg_sync.exists():
            write_yaml(
                self.paths.cfg_sync,
                {
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                    "enabled": False,
                    "method": "manual_export_import",
                },
            )

        if not self.paths.cfg_storage.exists():
            write_yaml(
                self.paths.cfg_storage,
                {
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                    "schema_version": "2.0",
                    "root": str(self.paths.root),
                },
            )

        for p in [self.paths.l1, self.paths.l2, self.paths.l3, self.paths.l4]:
            if not p.exists():
                write_yaml(p, [])

        for p in [
            self.paths.intent_goals,
            self.paths.intent_pref,
            self.paths.intent_constraints,
        ]:
            if not p.exists():
                write_yaml(p, [])

        if not self.paths.meta_insight_queue.exists():
            write_yaml(self.paths.meta_insight_queue, [])
        if not self.paths.meta_evolution.exists():
            write_yaml(self.paths.meta_evolution, [])
        if not self.paths.meta_hit_monitor.exists():
            write_yaml(self.paths.meta_hit_monitor, [])
        if not self.paths.meta_policy_state.exists():
            write_yaml(self.paths.meta_policy_state, {"updated_at": now_iso(), "policy": {}, "conflicts": []})

    def _config_file(self, name: str) -> Path:
        mapping = {
            "路径配置": self.paths.cfg_paths,
            "设备配置": self.paths.cfg_device,
            "工具配置": self.paths.cfg_tools,
            "工作流配置": self.paths.cfg_workflow,
            "同步配置": self.paths.cfg_sync,
            "存储配置": self.paths.cfg_storage,
        }
        if name not in mapping:
            raise KeyError(f"unknown config: {name}")
        return mapping[name]

    def get_config(self, config_name: str, key_path: Optional[str] = None) -> Any:
        data = read_yaml(self._config_file(config_name), {})
        if not key_path:
            return data
        cur: Any = data
        for key in key_path.split("."):
            if not isinstance(cur, dict) or key not in cur:
                return None
            cur = cur[key]
        return cur

    def set_config(self, config_name: str, key_path: str, value: Any) -> None:
        path = self._config_file(config_name)
        data = read_yaml(path, {})
        if not isinstance(data, dict):
            data = {}
        cur = data
        keys = key_path.split(".")
        for k in keys[:-1]:
            if k not in cur or not isinstance(cur[k], dict):
                cur[k] = {}
            cur = cur[k]
        cur[keys[-1]] = value
        data["updated_at"] = now_iso()
        write_yaml(path, data)

    def add_intent(self, intent_type: str, content: str, priority: str = "medium") -> str:
        mapping = {
            "目标与规划": self.paths.intent_goals,
            "偏好与要求": self.paths.intent_pref,
            "约束与边界": self.paths.intent_constraints,
        }
        if intent_type not in mapping:
            raise ValueError("invalid intent type")
        path = mapping[intent_type]
        items: List[Dict[str, Any]] = read_yaml(path, [])
        intent_id = f"intent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:6]}"
        items.append(
            {
                "id": intent_id,
                "content": content,
                "priority": priority,
                "status": "active",
                "created_at": now_iso(),
            }
        )
        write_yaml(path, items)
        return intent_id

    def build_session_context(self) -> Dict[str, Any]:
        prefs = read_yaml(self.paths.intent_pref, [])
        constraints = read_yaml(self.paths.intent_constraints, [])
        goals = read_yaml(self.paths.intent_goals, [])
        l2 = read_yaml(self.paths.l2, [])
        l3 = read_yaml(self.paths.l3, [])
        screenshot_path = self.get_config("路径配置", "screenshot_path")
        policy_bundle = self.build_response_policy()

        return {
            "generated_at": now_iso(),
            "profile": {
                "screenshot_path": screenshot_path,
                "active_preferences": prefs[-5:],
                "active_constraints": constraints[-5:],
                "active_goals": goals[-5:],
            },
            "recent_patterns": {
                "behavior": l2[-5:],
                "cognition": l3[-5:],
            },
            "adapter_hints": self._adapter_hints(prefs, constraints, l3),
            "effective_policy": policy_bundle.get("effective_policy", {}),
            "policy_conflicts": policy_bundle.get("conflicts", []),
        }

    def build_response_policy(self) -> Dict[str, Any]:
        prefs = read_yaml(self.paths.intent_pref, [])
        if not isinstance(prefs, list):
            prefs = []
        active = [x for x in prefs if isinstance(x, dict) and str(x.get("status", "active")) == "active"]

        axis_entries: Dict[str, List[Dict[str, Any]]] = {}
        for p in active:
            content = str(p.get("content", "")).strip()
            tag = self._classify_pref_axis(content)
            if not tag:
                continue
            axis, value = tag
            axis_entries.setdefault(axis, []).append(
                {
                    "id": str(p.get("id", "")),
                    "content": content,
                    "value": value,
                    "priority": str(p.get("priority", "medium")).lower(),
                    "created_at": str(p.get("created_at", "")),
                }
            )

        effective_policy: Dict[str, Any] = {}
        conflicts: List[Dict[str, Any]] = []

        for axis, rows in axis_entries.items():
            values = sorted(list(set([str(r.get("value", "")) for r in rows if str(r.get("value", ""))])))
            if len(values) > 1:
                conflicts.append(
                    {
                        "axis": axis,
                        "values": values,
                        "candidates": rows,
                        "resolution": "priority_then_recency",
                    }
                )
            winner = self._resolve_policy_winner(rows)
            if winner:
                effective_policy[axis] = winner

        state = {
            "updated_at": now_iso(),
            "effective_policy": effective_policy,
            "conflicts": conflicts,
        }
        write_yaml(self.paths.meta_policy_state, state)
        return state

    def _classify_pref_axis(self, text: str) -> Optional[tuple[str, str]]:
        t = text.lower()
        if "先给结论" in text or "结论" in text or "tl;dr" in t:
            return ("answer_order", "conclusion_first")
        if "先澄清" in text or "先提问" in text:
            return ("answer_order", "clarify_first")
        if "结构化" in text or "要点" in text or "编号" in text:
            return ("format", "structured")
        if "自然段" in text or "叙述" in text:
            return ("format", "narrative")
        if "简洁" in text or "简短" in text:
            return ("verbosity", "concise")
        if "详细" in text or "深入" in text:
            return ("verbosity", "detailed")
        if "路径" in text or "配置" in text:
            return ("fact_source", "memory_first")
        if "可执行" in text or "命令" in text or "代码" in text:
            return ("technical_style", "executable")
        return None

    def _resolve_policy_winner(self, rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        priority_rank = {"high": 3, "medium": 2, "low": 1}

        def key_fn(r: Dict[str, Any]) -> tuple[int, str]:
            p = priority_rank.get(str(r.get("priority", "medium")), 2)
            ts = str(r.get("created_at", ""))
            return (p, ts)

        if not rows:
            return None
        return sorted(rows, key=key_fn, reverse=True)[0]

    def _adapter_hints(
        self,
        prefs: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        l3: List[Dict[str, Any]],
    ) -> List[str]:
        hints: List[str] = []
        for p in prefs[-3:]:
            c = str(p.get("content", "")).strip()
            if c:
                hints.append(f"偏好: {c}")
        for c in constraints[-3:]:
            t = str(c.get("content", "")).strip()
            if t:
                hints.append(f"边界: {t}")
        if l3:
            last = l3[-1]
            pattern = last.get("data", {}).get("thinking_pattern")
            if pattern:
                hints.append(f"认知模式: {pattern}")
        return hints

    def analyze_text(self, text: str) -> Dict[str, Any]:
        s = text.lower()
        context_type = "general"
        if any(k in s for k in ["如何", "怎么", "why", "how"]):
            context_type = "learning"
        if any(k in s for k in ["选择", "决策", "建议", "which"]):
            context_type = "decision"
        question_pattern = "open_ended" if "?" in s or "？" in text else "statement"
        thinking_pattern = "systematic" if any(k in text for k in ["步骤", "框架", "分层", "结构"]) else "exploratory"
        return {
            "context_type": context_type,
            "question_pattern": question_pattern,
            "thinking_pattern": thinking_pattern,
            "keywords": [k for k in ["记忆", "系统", "决策", "偏好", "配置"] if k in text],
        }

    def write_conversation(self, conversation_id: str, messages: List[Dict[str, str]]) -> None:
        write_json(
            self.paths.l0 / f"{conversation_id}.json",
            {
                "conversation_id": conversation_id,
                "timestamp": now_iso(),
                "messages": messages,
            },
        )

        full_text = "\n".join([m.get("content", "") for m in messages])
        analyzed = self.analyze_text(full_text)
        self._append_layer(self.paths.l1, conversation_id, {
            "context_type": analyzed["context_type"],
            "keywords": analyzed["keywords"],
        })
        self._append_layer(self.paths.l2, conversation_id, {
            "question_pattern": analyzed["question_pattern"],
        })
        self._append_layer(self.paths.l3, conversation_id, {
            "thinking_pattern": analyzed["thinking_pattern"],
        })

        self._update_l4_core_model(conversation_id)
        self._record_memory_hit(conversation_id, messages)

        self._detect_and_record_anomalies(conversation_id, messages)
        self.refresh_anomaly_reminder()

    def _append_layer(self, path: Path, conv_id: str, data: Dict[str, Any]) -> None:
        rows: List[Dict[str, Any]] = read_yaml(path, [])
        rows.append({"conversation_id": conv_id, "timestamp": now_iso(), "data": data})
        write_yaml(path, rows)

    def _update_l4_core_model(self, conversation_id: str) -> None:
        l3 = read_yaml(self.paths.l3, [])
        l3 = l3 if isinstance(l3, list) else []
        last = l3[-200:]
        pattern_counter = Counter([str(x.get("data", {}).get("thinking_pattern", "unknown")) for x in last if isinstance(x, dict)])

        prefs = read_yaml(self.paths.intent_pref, [])
        prefs = [x for x in (prefs if isinstance(prefs, list) else []) if isinstance(x, dict) and str(x.get("status", "active")) == "active"]
        policy = self.build_response_policy().get("effective_policy", {})

        def confidence(counter: Counter, key: str) -> float:
            total = sum(counter.values())
            if total <= 0:
                return 0.0
            return round(counter.get(key, 0) / total, 3)

        traits = {
            "dominant_thinking": pattern_counter.most_common(1)[0][0] if pattern_counter else "unknown",
            "thinking_confidence": confidence(pattern_counter, pattern_counter.most_common(1)[0][0]) if pattern_counter else 0.0,
            "prefers_conclusion_first": any("先给结论" in str(p.get("content", "")) for p in prefs),
            "prefers_structured": any("结构化" in str(p.get("content", "")) or "要点" in str(p.get("content", "")) for p in prefs),
            "prefers_executable": any("可执行" in str(p.get("content", "")) or "命令" in str(p.get("content", "")) for p in prefs),
            "policy": policy,
        }
        self._append_layer(self.paths.l4, conversation_id, traits)

    def _record_memory_hit(self, conversation_id: str, messages: List[Dict[str, str]]) -> None:
        user_text = "\n".join([m.get("content", "") for m in messages if m.get("role") == "user"])
        assistant_text = "\n".join([m.get("content", "") for m in messages if m.get("role") == "assistant"])

        policy_bundle = self.build_response_policy()
        policy = policy_bundle.get("effective_policy", {})
        hits: List[str] = []
        misses: List[str] = []

        screenshot_path = str(self.get_config("路径配置", "screenshot_path") or "")
        if self._is_path_question(user_text):
            if screenshot_path and screenshot_path.replace("\\", "/") in assistant_text.replace("\\", "/"):
                hits.append("path_memory_hit")
            else:
                misses.append("path_memory_miss")

        if policy.get("answer_order", {}).get("value") == "conclusion_first":
            if self._assistant_has_conclusion_first(assistant_text):
                hits.append("conclusion_first_hit")
            else:
                misses.append("conclusion_first_miss")

        if policy.get("format", {}).get("value") == "structured":
            if self._assistant_is_structured(assistant_text):
                hits.append("structured_hit")
            else:
                misses.append("structured_miss")

        if policy.get("technical_style", {}).get("value") == "executable" and self._is_technical_request(user_text):
            if self._assistant_has_executable_signal(assistant_text):
                hits.append("executable_hit")
            else:
                misses.append("executable_miss")

        rows = read_yaml(self.paths.meta_hit_monitor, [])
        rows = rows if isinstance(rows, list) else []
        rows.append(
            {
                "conversation_id": conversation_id,
                "timestamp": now_iso(),
                "hits": hits,
                "misses": misses,
                "hit_rate": round((len(hits) / (len(hits) + len(misses))) if (hits or misses) else 1.0, 3),
            }
        )
        write_yaml(self.paths.meta_hit_monitor, rows)

    def hit_stats(self, days: int = 7) -> Dict[str, Any]:
        rows = read_yaml(self.paths.meta_hit_monitor, [])
        rows = rows if isinstance(rows, list) else []
        cutoff = datetime.now() - timedelta(days=max(1, int(days)))

        recent = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            ts = self._parse_iso(str(r.get("timestamp", "")))
            if ts and ts >= cutoff:
                recent.append(r)

        all_hits = Counter()
        all_misses = Counter()
        rates = []
        for r in recent:
            all_hits.update(r.get("hits", []))
            all_misses.update(r.get("misses", []))
            rates.append(float(r.get("hit_rate", 0)))

        avg_rate = round(sum(rates) / len(rates), 3) if rates else 1.0
        return {
            "generated_at": now_iso(),
            "window_days": max(1, int(days)),
            "sample_count": len(recent),
            "avg_hit_rate": avg_rate,
            "top_hits": all_hits.most_common(10),
            "top_misses": all_misses.most_common(10),
        }

    def _detect_and_record_anomalies(self, conversation_id: str, messages: List[Dict[str, str]]) -> None:
        user_text = "\n".join([m.get("content", "") for m in messages if m.get("role") == "user"])
        assistant_text = "\n".join([m.get("content", "") for m in messages if m.get("role") == "assistant"])

        prefs = read_yaml(self.paths.intent_pref, [])
        active_pref_text = [str(x.get("content", "")) for x in prefs if str(x.get("status", "active")) == "active"]

        screenshot_path = str(self.get_config("路径配置", "screenshot_path") or "")
        if self._is_path_question(user_text) and screenshot_path:
            if screenshot_path.replace("\\", "/") not in assistant_text.replace("\\", "/"):
                self._push_anomaly(
                    anomaly_type="path_mismatch",
                    severity="high",
                    conversation_id=conversation_id,
                    detail="用户询问路径类问题时，回答未命中记忆中的截图路径。",
                    recommendation=f"优先回答记忆路径: {screenshot_path}",
                )

        if any("先给结论" in p for p in active_pref_text):
            if assistant_text.strip() and not self._assistant_has_conclusion_first(assistant_text):
                self._push_anomaly(
                    anomaly_type="style_no_conclusion_first",
                    severity="medium",
                    conversation_id=conversation_id,
                    detail="回答未明显遵循“先给结论”偏好。",
                    recommendation="首行使用“结论：...”后再展开步骤。",
                )

        if any("结构化输出" in p for p in active_pref_text):
            if assistant_text.strip() and not self._assistant_is_structured(assistant_text):
                self._push_anomaly(
                    anomaly_type="style_not_structured",
                    severity="low",
                    conversation_id=conversation_id,
                    detail="回答结构化程度不足。",
                    recommendation="使用编号或短要点输出。",
                )

        if any("可执行方案" in p for p in active_pref_text) and self._is_technical_request(user_text):
            if assistant_text.strip() and not self._assistant_has_executable_signal(assistant_text):
                self._push_anomaly(
                    anomaly_type="tech_not_executable",
                    severity="medium",
                    conversation_id=conversation_id,
                    detail="技术问题回答缺少可执行命令/代码信号。",
                    recommendation="至少给出命令、代码块或明确执行步骤。",
                )

    def _is_path_question(self, text: str) -> bool:
        t = text.lower()
        keys = ["路径", "在哪", "目录", "screenshot", "snapshot", "path", "位置"]
        return any(k in t for k in keys)

    def _assistant_has_conclusion_first(self, text: str) -> bool:
        first = text.strip().splitlines()[0].strip() if text.strip() else ""
        first_lower = first.lower()
        return first.startswith("结论") or first_lower.startswith("conclusion") or first_lower.startswith("tl;dr")

    def _assistant_is_structured(self, text: str) -> bool:
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        if len(lines) >= 3:
            return True
        markers = ["- ", "* ", "1.", "2.", "3."]
        return any(m in text for m in markers)

    def _is_technical_request(self, text: str) -> bool:
        t = text.lower()
        keys = ["代码", "命令", "脚本", "api", "python", "node", "数据库", "部署", "调试"]
        return any(k in t for k in keys)

    def _assistant_has_executable_signal(self, text: str) -> bool:
        t = text.lower()
        keys = ["```", "python", "bash", "cmd", "powershell", "npm", "pip", "git ", "运行", "执行"]
        return any(k in t for k in keys)

    def _push_anomaly(
        self,
        anomaly_type: str,
        severity: str,
        conversation_id: str,
        detail: str,
        recommendation: str,
    ) -> None:
        queue = read_yaml(self.paths.meta_insight_queue, [])
        if not isinstance(queue, list):
            queue = []
        item = {
            "id": f"anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:6]}",
            "type": anomaly_type,
            "severity": severity,
            "conversation_id": conversation_id,
            "detail": detail,
            "recommendation": recommendation,
            "status": "open",
            "created_at": now_iso(),
        }
        queue.append(item)
        write_yaml(self.paths.meta_insight_queue, queue)

    def list_anomalies(self, limit: int = 20, status: str = "open") -> List[Dict[str, Any]]:
        queue = read_yaml(self.paths.meta_insight_queue, [])
        if not isinstance(queue, list):
            return []
        rows = [x for x in queue if isinstance(x, dict)]
        if status:
            rows = [x for x in rows if str(x.get("status", "")) == status]
        return rows[-limit:]

    def resolve_anomaly(self, anomaly_id: str) -> bool:
        queue = read_yaml(self.paths.meta_insight_queue, [])
        if not isinstance(queue, list):
            return False
        changed = False
        for item in queue:
            if isinstance(item, dict) and str(item.get("id", "")) == anomaly_id:
                item["status"] = "resolved"
                item["resolved_at"] = now_iso()
                changed = True
        if changed:
            write_yaml(self.paths.meta_insight_queue, queue)
            self.refresh_anomaly_reminder()
        return changed

    def refresh_anomaly_reminder(self) -> None:
        open_items = self.list_anomalies(limit=200, status="open")
        high = [x for x in open_items if str(x.get("severity", "")) == "high"]
        medium = [x for x in open_items if str(x.get("severity", "")) == "medium"]
        low = [x for x in open_items if str(x.get("severity", "")) == "low"]

        lines = [
            "# 异常提醒",
            "",
            f"- 生成时间: {now_iso()}",
            f"- 开放异常总数: {len(open_items)}",
            f"- high/medium/low: {len(high)}/{len(medium)}/{len(low)}",
            "",
            "## 最近异常（最多10条）",
        ]
        for item in open_items[-10:]:
            lines.append(
                f"- [{item.get('severity')}] {item.get('type')} ({item.get('conversation_id')}) -> {item.get('detail')}"
            )
            lines.append(f"  建议: {item.get('recommendation')} | id={item.get('id')}")
        if not open_items:
            lines.append("- 无开放异常")

        self.paths.meta_alert_md.write_text("\n".join(lines), encoding="utf-8")

    def suggest_preference_updates(self, days: int = 30, auto_apply: bool = False) -> Dict[str, Any]:
        cutoff = datetime.now() - timedelta(days=max(1, int(days)))
        queue = read_yaml(self.paths.meta_insight_queue, [])
        if not isinstance(queue, list):
            queue = []

        recent = []
        for item in queue:
            if not isinstance(item, dict):
                continue
            ts = self._parse_iso(str(item.get("created_at", "")))
            if ts and ts >= cutoff:
                recent.append(item)

        type_counter = Counter([str(x.get("type", "unknown")) for x in recent])
        prefs = read_yaml(self.paths.intent_pref, [])
        existing_pref_text = set([str(x.get("content", "")).strip() for x in prefs if isinstance(x, dict)])

        rules = {
            "path_mismatch": "涉及路径/配置问题时，必须先读取记忆配置并优先给出记忆值。",
            "style_no_conclusion_first": "回答首行必须先给结论（结论：...），再展开细节。",
            "style_not_structured": "默认使用结构化输出（编号或要点），避免大段无结构文本。",
            "tech_not_executable": "技术问题必须提供可执行方案（命令、代码或明确步骤）。",
        }

        suggestions: List[Dict[str, Any]] = []
        for typ, count in type_counter.items():
            if count < 2:
                continue
            if typ not in rules:
                continue
            text = rules[typ]
            if text in existing_pref_text:
                continue
            suggestions.append(
                {
                    "anomaly_type": typ,
                    "count": count,
                    "suggested_preference": text,
                    "priority": "high" if count >= 3 else "medium",
                }
            )

        applied_ids: List[str] = []
        if auto_apply:
            for s in suggestions:
                intent_id = self.add_intent("偏好与要求", s["suggested_preference"], s["priority"])
                applied_ids.append(intent_id)
                self._append_evolution(
                    {
                        "type": "auto_preference_added",
                        "source": "anomaly_suggestion",
                        "anomaly_type": s["anomaly_type"],
                        "count": s["count"],
                        "intent_id": intent_id,
                        "content": s["suggested_preference"],
                        "created_at": now_iso(),
                    }
                )

        return {
            "generated_at": now_iso(),
            "window_days": max(1, int(days)),
            "recent_anomaly_count": len(recent),
            "type_counter": type_counter.most_common(),
            "suggestions": suggestions,
            "applied": auto_apply,
            "applied_intent_ids": applied_ids,
        }

    def _append_evolution(self, entry: Dict[str, Any]) -> None:
        rows = read_yaml(self.paths.meta_evolution, [])
        if not isinstance(rows, list):
            rows = []
        rows.append(entry)
        write_yaml(self.paths.meta_evolution, rows)

    def normalize_preferences(self, apply_changes: bool = False) -> Dict[str, Any]:
        prefs = read_yaml(self.paths.intent_pref, [])
        if not isinstance(prefs, list):
            prefs = []

        active = [x for x in prefs if isinstance(x, dict) and str(x.get("status", "active")) == "active"]
        groups: List[List[Dict[str, Any]]] = []
        used = set()

        for i, a in enumerate(active):
            if i in used:
                continue
            g = [a]
            used.add(i)
            ta = str(a.get("content", "")).strip()
            na = self._norm_text(ta)
            for j in range(i + 1, len(active)):
                if j in used:
                    continue
                b = active[j]
                tb = str(b.get("content", "")).strip()
                nb = self._norm_text(tb)
                if self._is_similar_pref(ta, tb, na, nb):
                    g.append(b)
                    used.add(j)
            if len(g) > 1:
                groups.append(g)

        suggestions = []
        for g in groups:
            canonical = sorted(g, key=lambda x: len(str(x.get("content", ""))), reverse=True)[0]
            merged_ids = [str(x.get("id", "")) for x in g if str(x.get("id", "")) != str(canonical.get("id", ""))]
            suggestions.append(
                {
                    "canonical_id": str(canonical.get("id", "")),
                    "canonical_content": str(canonical.get("content", "")),
                    "merge_ids": merged_ids,
                    "count": len(g),
                }
            )

        applied = 0
        if apply_changes and suggestions:
            merge_id_set = set()
            for s in suggestions:
                for mid in s["merge_ids"]:
                    merge_id_set.add(mid)
            for item in prefs:
                if not isinstance(item, dict):
                    continue
                iid = str(item.get("id", ""))
                if iid in merge_id_set and str(item.get("status", "active")) == "active":
                    item["status"] = "merged"
                    item["merged_at"] = now_iso()
                    applied += 1
            write_yaml(self.paths.intent_pref, prefs)
            self._append_evolution(
                {
                    "type": "preference_dedup",
                    "created_at": now_iso(),
                    "applied_count": applied,
                    "group_count": len(suggestions),
                    "details": suggestions,
                }
            )

        return {
            "generated_at": now_iso(),
            "active_count": len(active),
            "group_count": len(suggestions),
            "suggestions": suggestions,
            "applied": apply_changes,
            "applied_count": applied,
        }

    def _norm_text(self, text: str) -> str:
        t = text.lower().strip()
        t = re.sub(r"[\s\-_,.;:!?，。；：！？（）()\[\]{}]+", "", t)
        return t

    def _is_similar_pref(self, a: str, b: str, na: str, nb: str) -> bool:
        if not na or not nb:
            return False
        if na == nb:
            return True
        if na in nb or nb in na:
            return True
        sa = set(na)
        sb = set(nb)
        inter = len(sa & sb)
        union = len(sa | sb)
        score = inter / union if union else 0
        return score >= 0.85

    def preference_quality_report(self) -> Dict[str, Any]:
        prefs = read_yaml(self.paths.intent_pref, [])
        if not isinstance(prefs, list):
            prefs = []
        active = [x for x in prefs if isinstance(x, dict) and str(x.get("status", "active")) == "active"]

        rows = []
        total = 0
        for p in active:
            content = str(p.get("content", "")).strip()
            detail = self._score_pref_text(content)
            total += detail["total"]
            rows.append(
                {
                    "id": p.get("id", ""),
                    "content": content,
                    "priority": p.get("priority", "medium"),
                    "score": detail,
                }
            )

        avg = round(total / len(active), 2) if active else 0
        weak = [r for r in rows if r["score"]["total"] < 70]
        return {
            "generated_at": now_iso(),
            "active_count": len(active),
            "avg_score": avg,
            "weak_count": len(weak),
            "weak_items": weak,
            "all_items": rows,
        }

    def suggest_preference_rewrites(self, auto_apply: bool = False) -> Dict[str, Any]:
        prefs = read_yaml(self.paths.intent_pref, [])
        if not isinstance(prefs, list):
            prefs = []
        active = [x for x in prefs if isinstance(x, dict) and str(x.get("status", "active")) == "active"]

        existing = set([str(x.get("content", "")).strip() for x in active])
        suggestions = []
        for p in active:
            content = str(p.get("content", "")).strip()
            score = self._score_pref_text(content)
            if score["total"] >= 70:
                continue
            rewrite = self._rewrite_pref_text(content)
            if rewrite in existing:
                continue
            suggestions.append(
                {
                    "source_id": str(p.get("id", "")),
                    "source_content": content,
                    "source_score": score["total"],
                    "priority": str(p.get("priority", "medium")),
                    "rewrite": rewrite,
                }
            )

        applied = []
        if auto_apply:
            id_to_item = {str(x.get("id", "")): x for x in prefs if isinstance(x, dict)}
            for s in suggestions:
                new_entry = self._make_intent_entry(s["rewrite"], s["priority"])
                new_id = str(new_entry["id"])
                prefs.append(new_entry)
                applied.append(new_id)
                src_id = s["source_id"]
                if src_id in id_to_item:
                    id_to_item[src_id]["status"] = "rewritten"
                    id_to_item[src_id]["rewritten_at"] = now_iso()
                    id_to_item[src_id]["rewritten_to"] = new_id
                self._append_evolution(
                    {
                        "type": "preference_rewrite",
                        "created_at": now_iso(),
                        "source_id": src_id,
                        "new_id": new_id,
                        "source_content": s["source_content"],
                        "rewrite": s["rewrite"],
                    }
                )
            if suggestions:
                write_yaml(self.paths.intent_pref, prefs)

        return {
            "generated_at": now_iso(),
            "suggestion_count": len(suggestions),
            "suggestions": suggestions,
            "applied": auto_apply,
            "applied_ids": applied,
        }

    def _make_intent_entry(self, content: str, priority: str) -> Dict[str, Any]:
        return {
            "id": f"intent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:6]}",
            "content": content,
            "priority": priority,
            "status": "active",
            "created_at": now_iso(),
        }

    def repair_preference_integrity(self) -> Dict[str, Any]:
        prefs = read_yaml(self.paths.intent_pref, [])
        if not isinstance(prefs, list):
            prefs = []

        by_id = {str(x.get("id", "")): x for x in prefs if isinstance(x, dict)}
        evo = read_yaml(self.paths.meta_evolution, [])
        evo = evo if isinstance(evo, list) else []

        repaired = 0
        for item in prefs:
            if not isinstance(item, dict):
                continue
            if str(item.get("status", "")) != "rewritten":
                continue
            target = str(item.get("rewritten_to", ""))
            if target and target in by_id:
                continue

            src_id = str(item.get("id", ""))
            matched = None
            for e in reversed(evo):
                if not isinstance(e, dict):
                    continue
                if str(e.get("type", "")) == "preference_rewrite" and str(e.get("source_id", "")) == src_id:
                    matched = e
                    break

            if matched:
                new_entry = self._make_intent_entry(str(matched.get("rewrite", item.get("content", ""))), str(item.get("priority", "medium")))
                prefs.append(new_entry)
                item["rewritten_to"] = new_entry["id"]
                item["integrity_repaired_at"] = now_iso()
                repaired += 1

        if repaired:
            write_yaml(self.paths.intent_pref, prefs)

        return {"repaired": repaired, "total": len(prefs)}

    def _score_pref_text(self, text: str) -> Dict[str, int]:
        t = text.strip()
        if not t:
            return {"clarity": 0, "actionability": 0, "testability": 0, "total": 0}

        vague_words = ["尽量", "适当", "可以", "可能", "最好", "尽快", "大概", "差不多"]
        trigger_words = ["涉及", "当", "如果", "遇到", "对于", "在"]
        action_words = ["必须", "先", "使用", "提供", "读取", "给出", "输出", "检查"]
        measurable_words = ["首行", "至少", "编号", "要点", "命令", "代码", "路径", "步骤"]

        clarity = 60
        if len(t) >= 12:
            clarity += 20
        if any(w in t for w in vague_words):
            clarity -= 20
        clarity = max(0, min(100, clarity))

        actionability = 50
        if any(w in t for w in trigger_words):
            actionability += 20
        if any(w in t for w in action_words):
            actionability += 20
        if any(w in t for w in vague_words):
            actionability -= 15
        actionability = max(0, min(100, actionability))

        testability = 40
        if any(w in t for w in measurable_words):
            testability += 35
        if "结论" in t:
            testability += 15
        if any(w in t for w in vague_words):
            testability -= 10
        testability = max(0, min(100, testability))

        total = round(clarity * 0.35 + actionability * 0.35 + testability * 0.30)
        return {
            "clarity": int(clarity),
            "actionability": int(actionability),
            "testability": int(testability),
            "total": int(total),
        }

    def _rewrite_pref_text(self, text: str) -> str:
        t = text.strip()
        if "先给结论" in t or "结论" in t:
            return "回答首行必须先给结论（结论：...），再给步骤细节。"
        if "结构化" in t or "要点" in t:
            return "默认使用结构化输出（编号或要点），避免大段无结构文本。"
        if "路径" in t or "配置" in t:
            return "涉及路径/配置问题时，必须先读取记忆配置并优先给出记忆值。"
        if "技术" in t or "代码" in t or "命令" in t:
            return "技术问题必须提供可执行方案（命令、代码或明确步骤）。"
        return f"当用户提出相关请求时，助手必须执行可验证动作：{t}"

    def export_all(self, out_file: str) -> None:
        payload = {
            "exported_at": now_iso(),
            "root": str(self.paths.root),
            "configs": {
                "路径配置": self.get_config("路径配置"),
                "设备配置": self.get_config("设备配置"),
                "工具配置": self.get_config("工具配置"),
                "工作流配置": self.get_config("工作流配置"),
                "同步配置": self.get_config("同步配置"),
                "存储配置": self.get_config("存储配置"),
            },
            "intent": {
                "目标与规划": read_yaml(self.paths.intent_goals, []),
                "偏好与要求": read_yaml(self.paths.intent_pref, []),
                "约束与边界": read_yaml(self.paths.intent_constraints, []),
            },
            "memory": {
                "L1": read_yaml(self.paths.l1, []),
                "L2": read_yaml(self.paths.l2, []),
                "L3": read_yaml(self.paths.l3, []),
                "L4": read_yaml(self.paths.l4, []),
            },
        }
        write_json(Path(out_file), payload)

    def import_all(self, in_file: str, mode: str = "merge") -> None:
        payload = read_json(Path(in_file), {})
        if not isinstance(payload, dict):
            raise ValueError("invalid import file")

        configs = payload.get("configs", {})
        for cfg_name, cfg_data in configs.items():
            if cfg_data is None:
                continue
            target = self._config_file(cfg_name)
            if mode == "replace":
                write_yaml(target, cfg_data)
            else:
                local = read_yaml(target, {})
                merged = self._merge_dict(local if isinstance(local, dict) else {}, cfg_data if isinstance(cfg_data, dict) else {})
                merged["updated_at"] = now_iso()
                write_yaml(target, merged)

        intent = payload.get("intent", {})
        self._import_list_yaml(self.paths.intent_goals, intent.get("目标与规划", []), mode)
        self._import_list_yaml(self.paths.intent_pref, intent.get("偏好与要求", []), mode)
        self._import_list_yaml(self.paths.intent_constraints, intent.get("约束与边界", []), mode)

        memory = payload.get("memory", {})
        self._import_list_yaml(self.paths.l1, memory.get("L1", []), mode)
        self._import_list_yaml(self.paths.l2, memory.get("L2", []), mode)
        self._import_list_yaml(self.paths.l3, memory.get("L3", []), mode)
        self._import_list_yaml(self.paths.l4, memory.get("L4", []), mode)

    def _import_list_yaml(self, path: Path, incoming: Any, mode: str) -> None:
        incoming_list = incoming if isinstance(incoming, list) else []
        if mode == "replace":
            write_yaml(path, incoming_list)
            return
        local = read_yaml(path, [])
        local_list = local if isinstance(local, list) else []
        write_yaml(path, self._merge_list(local_list, incoming_list))

    def _merge_dict(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(a)
        for k, v in b.items():
            if k in out and isinstance(out[k], dict) and isinstance(v, dict):
                out[k] = self._merge_dict(out[k], v)
            else:
                out[k] = v
        return out

    def _merge_list(self, local: List[Any], incoming: List[Any]) -> List[Any]:
        key_fields = ["id", "conversation_id", "timestamp"]
        index = set()
        merged: List[Any] = []
        for item in local + incoming:
            if isinstance(item, dict):
                signature = None
                for k in key_fields:
                    if k in item:
                        signature = (k, str(item.get(k)))
                        break
                if signature is None:
                    signature = ("raw", json.dumps(item, ensure_ascii=False, sort_keys=True))
            else:
                signature = ("raw", str(item))

            if signature in index:
                continue
            index.add(signature)
            merged.append(item)
        return merged

    def status(self) -> Dict[str, Any]:
        size = 0
        count = 0
        for p in self.paths.root.rglob("*"):
            if p.is_file():
                count += 1
                size += p.stat().st_size
        return {
            "root": str(self.paths.root),
            "files": count,
            "size_mb": round(size / (1024 * 1024), 3),
            "screenshot_path": self.get_config("路径配置", "screenshot_path"),
            "generated_at": now_iso(),
        }

    def generate_weekly_review(self, days: int = 7, save: bool = True) -> Dict[str, Any]:
        cutoff = datetime.now() - timedelta(days=days)

        l1 = self._filter_recent_rows(read_yaml(self.paths.l1, []), cutoff)
        l2 = self._filter_recent_rows(read_yaml(self.paths.l2, []), cutoff)
        l3 = self._filter_recent_rows(read_yaml(self.paths.l3, []), cutoff)

        context_counter = Counter()
        question_counter = Counter()
        thinking_counter = Counter()

        for row in l1:
            context_counter.update([str(row.get("data", {}).get("context_type", "unknown"))])
        for row in l2:
            question_counter.update([str(row.get("data", {}).get("question_pattern", "unknown"))])
        for row in l3:
            thinking_counter.update([str(row.get("data", {}).get("thinking_pattern", "unknown"))])

        prefs = read_yaml(self.paths.intent_pref, [])
        high_prefs = [x for x in prefs if str(x.get("priority", "")).lower() == "high" and str(x.get("status", "active")) == "active"]
        open_anomalies = self.list_anomalies(limit=500, status="open")
        anomaly_counter = Counter([str(x.get("type", "unknown")) for x in open_anomalies])
        hit = self.hit_stats(days=days)
        policy_state = self.build_response_policy()

        report = {
            "generated_at": now_iso(),
            "window_days": days,
            "summary": {
                "l1_records": len(l1),
                "l2_records": len(l2),
                "l3_records": len(l3),
                "top_context_types": context_counter.most_common(3),
                "top_question_patterns": question_counter.most_common(3),
                "top_thinking_patterns": thinking_counter.most_common(3),
                "active_high_preferences": [p.get("content", "") for p in high_prefs[-8:]],
                "open_anomaly_count": len(open_anomalies),
                "top_open_anomalies": anomaly_counter.most_common(5),
                "avg_hit_rate": hit.get("avg_hit_rate", 1.0),
                "policy_conflict_count": len(policy_state.get("conflicts", [])),
            },
            "insights": self._build_weekly_insights(context_counter, question_counter, thinking_counter, high_prefs),
            "next_actions": self._build_weekly_actions(context_counter, question_counter, thinking_counter),
        }

        if save:
            self._save_weekly_review(report)
        return report

    def _parse_iso(self, ts: str) -> Optional[datetime]:
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts)
        except ValueError:
            return None

    def _filter_recent_rows(self, rows: Any, cutoff: datetime) -> List[Dict[str, Any]]:
        if not isinstance(rows, list):
            return []
        out: List[Dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            ts = self._parse_iso(str(row.get("timestamp", "")))
            if ts and ts >= cutoff:
                out.append(row)
        return out

    def _build_weekly_insights(
        self,
        context_counter: Counter,
        question_counter: Counter,
        thinking_counter: Counter,
        high_prefs: List[Dict[str, Any]],
    ) -> List[str]:
        insights: List[str] = []
        if context_counter:
            insights.append(f"本周主要对话场景: {context_counter.most_common(1)[0][0]}")
        if question_counter:
            insights.append(f"本周提问模式: {question_counter.most_common(1)[0][0]}")
        if thinking_counter:
            insights.append(f"本周认知模式: {thinking_counter.most_common(1)[0][0]}")
        if high_prefs:
            insights.append(f"当前高优先级偏好数: {len(high_prefs)}")
        if not insights:
            insights.append("本周暂无足够数据，建议继续自然使用并积累对话。")
        return insights

    def _build_weekly_actions(
        self,
        context_counter: Counter,
        question_counter: Counter,
        thinking_counter: Counter,
    ) -> List[str]:
        actions: List[str] = [
            "每周检查一次高优先级偏好，删除重复项并保留最清晰表达。",
            "对经常出现的问题类型建立固定回答模板。",
        ]
        if question_counter and question_counter.most_common(1)[0][0] == "statement":
            actions.append("你本周陈述型输入较多，建议在关键问题中显式提出期望输出格式。")
        if thinking_counter and thinking_counter.most_common(1)[0][0] == "exploratory":
            actions.append("探索型思考较多，建议对重要任务补充结构化检查清单。")
        return actions

    def _save_weekly_review(self, report: Dict[str, Any]) -> None:
        dt = datetime.now()
        week_key = f"{dt.strftime('%Y')}-W{dt.strftime('%W')}"
        base = self.paths.meta / "复盘记录"
        yaml_path = base / f"{week_key}.yaml"
        md_path = base / f"{week_key}.md"

        write_yaml(yaml_path, report)

        summary = report.get("summary", {})
        lines = [
            f"# 周复盘 {week_key}",
            "",
            f"- 生成时间: {report.get('generated_at', '')}",
            f"- 统计窗口: 最近 {report.get('window_days', 7)} 天",
            f"- L1/L2/L3 记录: {summary.get('l1_records', 0)}/{summary.get('l2_records', 0)}/{summary.get('l3_records', 0)}",
            "",
            "## 关键洞察",
        ]
        for i in report.get("insights", []):
            lines.append(f"- {i}")
        lines.append("")
        lines.append("## 下周动作")
        for a in report.get("next_actions", []):
            lines.append(f"- {a}")
        md_path.write_text("\n".join(lines), encoding="utf-8")

    def generate_monthly_report(self, months: int = 1, save: bool = True) -> Dict[str, Any]:
        m = max(1, int(months))
        now = datetime.now()
        first_day_current = datetime(now.year, now.month, 1)
        start = self._shift_month(first_day_current, -(m - 1))

        l1 = self._filter_recent_rows(read_yaml(self.paths.l1, []), start)
        l2 = self._filter_recent_rows(read_yaml(self.paths.l2, []), start)
        l3 = self._filter_recent_rows(read_yaml(self.paths.l3, []), start)

        context_counter = Counter()
        question_counter = Counter()
        thinking_counter = Counter()

        for row in l1:
            context_counter.update([str(row.get("data", {}).get("context_type", "unknown"))])
        for row in l2:
            question_counter.update([str(row.get("data", {}).get("question_pattern", "unknown"))])
        for row in l3:
            thinking_counter.update([str(row.get("data", {}).get("thinking_pattern", "unknown"))])

        prefs = read_yaml(self.paths.intent_pref, [])
        high_prefs = [x for x in prefs if str(x.get("priority", "")).lower() == "high" and str(x.get("status", "active")) == "active"]
        open_anomalies = self.list_anomalies(limit=1000, status="open")
        anomaly_counter = Counter([str(x.get("type", "unknown")) for x in open_anomalies])
        hit = self.hit_stats(days=30 * m)
        policy_state = self.build_response_policy()

        trend = self._monthly_trend_series(l3, months=m)

        report = {
            "generated_at": now_iso(),
            "window_months": m,
            "window_start": start.isoformat(timespec="seconds"),
            "summary": {
                "l1_records": len(l1),
                "l2_records": len(l2),
                "l3_records": len(l3),
                "top_context_types": context_counter.most_common(5),
                "top_question_patterns": question_counter.most_common(5),
                "top_thinking_patterns": thinking_counter.most_common(5),
                "active_high_preferences": [p.get("content", "") for p in high_prefs[-12:]],
                "thinking_trend": trend,
                "open_anomaly_count": len(open_anomalies),
                "top_open_anomalies": anomaly_counter.most_common(8),
                "avg_hit_rate": hit.get("avg_hit_rate", 1.0),
                "policy_conflict_count": len(policy_state.get("conflicts", [])),
            },
            "insights": self._build_monthly_insights(context_counter, question_counter, thinking_counter, trend, high_prefs),
            "next_actions": self._build_monthly_actions(context_counter, question_counter, thinking_counter, trend),
        }

        if save:
            self._save_monthly_report(report)
        return report

    def _shift_month(self, dt: datetime, offset: int) -> datetime:
        y = dt.year
        m = dt.month + offset
        while m <= 0:
            y -= 1
            m += 12
        while m > 12:
            y += 1
            m -= 12
        return datetime(y, m, 1)

    def _month_key(self, dt: datetime) -> str:
        return f"{dt.year:04d}-{dt.month:02d}"

    def _monthly_trend_series(self, rows_l3: List[Dict[str, Any]], months: int) -> List[Dict[str, Any]]:
        now = datetime.now()
        first_current = datetime(now.year, now.month, 1)
        buckets: Dict[str, Counter] = {}
        for i in range(months - 1, -1, -1):
            d = self._shift_month(first_current, -i)
            buckets[self._month_key(d)] = Counter()

        for row in rows_l3:
            ts = self._parse_iso(str(row.get("timestamp", "")))
            if not ts:
                continue
            key = self._month_key(datetime(ts.year, ts.month, 1))
            if key not in buckets:
                continue
            pat = str(row.get("data", {}).get("thinking_pattern", "unknown"))
            buckets[key].update([pat])

        series: List[Dict[str, Any]] = []
        for key, counter in buckets.items():
            series.append({"month": key, "patterns": counter.most_common(3)})
        return series

    def _build_monthly_insights(
        self,
        context_counter: Counter,
        question_counter: Counter,
        thinking_counter: Counter,
        trend: List[Dict[str, Any]],
        high_prefs: List[Dict[str, Any]],
    ) -> List[str]:
        insights: List[str] = []
        if context_counter:
            insights.append(f"月度主要场景: {context_counter.most_common(1)[0][0]}")
        if question_counter:
            insights.append(f"月度提问模式: {question_counter.most_common(1)[0][0]}")
        if thinking_counter:
            insights.append(f"月度认知模式: {thinking_counter.most_common(1)[0][0]}")
        if trend:
            latest = trend[-1]
            if latest.get("patterns"):
                insights.append(f"本月主导思考模式: {latest['patterns'][0][0]}")
        if high_prefs:
            insights.append(f"高优先级偏好累计: {len(high_prefs)}")
        if not insights:
            insights.append("月度数据不足，建议继续使用并保持真实任务对话。")
        return insights

    def _build_monthly_actions(
        self,
        context_counter: Counter,
        question_counter: Counter,
        thinking_counter: Counter,
        trend: List[Dict[str, Any]],
    ) -> List[str]:
        actions: List[str] = [
            "合并同义偏好，确保偏好库短小且无重复。",
            "将高频问题沉淀为固定提问模板，提高稳定性。",
        ]
        if question_counter and question_counter.most_common(1)[0][0] == "open_ended":
            actions.append("开放式提问较多，建议为关键决策补充量化标准。")
        if thinking_counter and thinking_counter.most_common(1)[0][0] == "systematic":
            actions.append("系统化思考占优，可建立月度决策复盘清单。")
        if trend and len(trend) >= 2:
            prev = trend[-2].get("patterns", [])
            cur = trend[-1].get("patterns", [])
            if prev and cur and prev[0][0] != cur[0][0]:
                actions.append("本月主导思考模式发生变化，建议回看变化原因。")
        return actions

    def _save_monthly_report(self, report: Dict[str, Any]) -> None:
        now = datetime.now()
        month_key = f"{now.year:04d}-{now.month:02d}"
        base = self.paths.meta / "复盘记录"
        yaml_path = base / f"{month_key}.monthly.yaml"
        md_path = base / f"{month_key}.monthly.md"

        write_yaml(yaml_path, report)

        summary = report.get("summary", {})
        lines = [
            f"# 月报 {month_key}",
            "",
            f"- 生成时间: {report.get('generated_at', '')}",
            f"- 统计窗口: 最近 {report.get('window_months', 1)} 个月",
            f"- L1/L2/L3 记录: {summary.get('l1_records', 0)}/{summary.get('l2_records', 0)}/{summary.get('l3_records', 0)}",
            "",
            "## 趋势",
        ]
        for point in summary.get("thinking_trend", []):
            lines.append(f"- {point.get('month')}: {point.get('patterns', [])}")
        lines.append("")
        lines.append("## 关键洞察")
        for i in report.get("insights", []):
            lines.append(f"- {i}")
        lines.append("")
        lines.append("## 下月动作")
        for a in report.get("next_actions", []):
            lines.append(f"- {a}")
        md_path.write_text("\n".join(lines), encoding="utf-8")


PersonaMemory = BehaviorMemory


def parse_value(v: str) -> Any:
    lower = v.lower()
    if lower in ["true", "false"]:
        return lower == "true"
    if v.isdigit():
        return int(v)
    try:
        return float(v)
    except ValueError:
        return v


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--get", help="配置名.键路径")
    parser.add_argument("--set", nargs=2, metavar=("配置名.键路径", "值"))
    parser.add_argument("--add-intent", nargs=3, metavar=("类型", "内容", "优先级"))
    parser.add_argument("--build-context", action="store_true")
    parser.add_argument("--analyze", help="分析文本")
    parser.add_argument("--write-conversation", help="会话ID")
    parser.add_argument("--messages-json", help="消息JSON数组")
    parser.add_argument("--export", help="导出文件路径")
    parser.add_argument("--import-file", help="导入文件路径")
    parser.add_argument("--import-mode", choices=["merge", "replace"], default="merge")
    parser.add_argument("--weekly-review", action="store_true")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--monthly-report", action="store_true")
    parser.add_argument("--months", type=int, default=1)
    parser.add_argument("--anomalies", type=int, help="查看开放异常，参数为条数")
    parser.add_argument("--resolve-anomaly", help="按ID标记异常为resolved")
    parser.add_argument("--refresh-anomaly-reminder", action="store_true")
    parser.add_argument("--anomaly-suggest", action="store_true")
    parser.add_argument("--suggest-days", type=int, default=30)
    parser.add_argument("--apply-suggestions", action="store_true")
    parser.add_argument("--normalize-prefs", action="store_true")
    parser.add_argument("--apply-normalize", action="store_true")
    parser.add_argument("--pref-quality", action="store_true")
    parser.add_argument("--pref-rewrite", action="store_true")
    parser.add_argument("--apply-pref-rewrite", action="store_true")
    parser.add_argument("--repair-pref-integrity", action="store_true")
    parser.add_argument("--policy", action="store_true")
    parser.add_argument("--hit-stats", action="store_true")
    parser.add_argument("--hit-days", type=int, default=7)
    args = parser.parse_args()

    mem = BehaviorMemory()

    if args.status:
        print(json.dumps(mem.status(), ensure_ascii=False, indent=2))
        return

    if args.get:
        if "." not in args.get:
            print("格式错误: 配置名.键路径")
            return
        config_name, key_path = args.get.split(".", 1)
        print(json.dumps(mem.get_config(config_name, key_path), ensure_ascii=False, indent=2))
        return

    if args.set:
        spec, val = args.set
        if "." not in spec:
            print("格式错误: 配置名.键路径")
            return
        config_name, key_path = spec.split(".", 1)
        mem.set_config(config_name, key_path, parse_value(val))
        print("ok")
        return

    if args.add_intent:
        t, c, p = args.add_intent
        print(mem.add_intent(t, c, p))
        return

    if args.build_context:
        print(json.dumps(mem.build_session_context(), ensure_ascii=False, indent=2))
        return

    if args.analyze:
        print(json.dumps(mem.analyze_text(args.analyze), ensure_ascii=False, indent=2))
        return

    if args.write_conversation:
        if not args.messages_json:
            print("需要 --messages-json")
            return
        messages = json.loads(args.messages_json)
        mem.write_conversation(args.write_conversation, messages)
        print("ok")
        return

    if args.export:
        mem.export_all(args.export)
        print("ok")
        return

    if args.import_file:
        mem.import_all(args.import_file, args.import_mode)
        print("ok")
        return

    if args.weekly_review:
        print(json.dumps(mem.generate_weekly_review(days=max(1, int(args.days))), ensure_ascii=False, indent=2))
        return

    if args.monthly_report:
        print(json.dumps(mem.generate_monthly_report(months=max(1, int(args.months))), ensure_ascii=False, indent=2))
        return

    if args.anomalies is not None:
        print(json.dumps(mem.list_anomalies(limit=max(1, int(args.anomalies))), ensure_ascii=False, indent=2))
        return

    if args.resolve_anomaly:
        print("ok" if mem.resolve_anomaly(args.resolve_anomaly) else "not_found")
        return

    if args.refresh_anomaly_reminder:
        mem.refresh_anomaly_reminder()
        print("ok")
        return

    if args.anomaly_suggest:
        print(
            json.dumps(
                mem.suggest_preference_updates(days=max(1, int(args.suggest_days)), auto_apply=bool(args.apply_suggestions)),
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.normalize_prefs:
        print(json.dumps(mem.normalize_preferences(apply_changes=bool(args.apply_normalize)), ensure_ascii=False, indent=2))
        return

    if args.pref_quality:
        print(json.dumps(mem.preference_quality_report(), ensure_ascii=False, indent=2))
        return

    if args.pref_rewrite:
        print(json.dumps(mem.suggest_preference_rewrites(auto_apply=bool(args.apply_pref_rewrite)), ensure_ascii=False, indent=2))
        return

    if args.repair_pref_integrity:
        print(json.dumps(mem.repair_preference_integrity(), ensure_ascii=False, indent=2))
        return

    if args.policy:
        print(json.dumps(mem.build_response_policy(), ensure_ascii=False, indent=2))
        return

    if args.hit_stats:
        print(json.dumps(mem.hit_stats(days=max(1, int(args.hit_days))), ensure_ascii=False, indent=2))
        return

    print(json.dumps(mem.status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
