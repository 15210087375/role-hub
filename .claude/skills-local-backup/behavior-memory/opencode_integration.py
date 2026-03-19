#!/usr/bin/env python3
import json
import re
from datetime import datetime
from typing import Any, List

from persona_core import BehaviorMemory


class BehaviorMemorySkill:
    def __init__(self) -> None:
        self.mem = BehaviorMemory()

    def process_command(self, command: str, args: List[str]) -> str:
        if command == "状态":
            return self._status()
        if command == "配置":
            return self._config(args)
        if command == "添加意图":
            return self._add_intent(args)
        if command == "构建上下文":
            return self._build_context()
        if command == "分析":
            return self._analyze(args)
        if command == "记录对话":
            return self._write_conversation(args)
        if command == "导出":
            return self._export(args)
        if command == "导入":
            return self._import_data(args)
        if command == "会话开始":
            return self._session_start(args)
        if command == "会话结束":
            return self._session_end(args)
        if command == "周复盘":
            return self._weekly_review(args)
        if command == "月报":
            return self._monthly_report(args)
        if command == "异常":
            return self._anomaly(args)
        if command == "偏好":
            return self._preference(args)
        if command == "策略":
            return self._policy(args)
        if command == "命中":
            return self._hit(args)
        if command == "帮助":
            return self._help()
        return "未知命令，使用 /记忆系统 帮助"

    def _status(self) -> str:
        s = self.mem.status()
        return (
            "行为记忆系统状态\n"
            f"- 根目录: {s['root']}\n"
            f"- 文件数: {s['files']}\n"
            f"- 存储大小(MB): {s['size_mb']}\n"
            f"- 截图路径: {s['screenshot_path']}\n"
            f"- 时间: {s['generated_at']}"
        )

    def _config(self, args: List[str]) -> str:
        if not args:
            return "用法: /记忆系统 配置 获取|设置|查看 ..."
        op = args[0]
        if op == "查看":
            out = {
                "路径配置": self.mem.get_config("路径配置"),
                "设备配置": self.mem.get_config("设备配置"),
                "工具配置": self.mem.get_config("工具配置"),
            }
            return json.dumps(out, ensure_ascii=False, indent=2)
        if op == "获取":
            if len(args) < 2 or "." not in args[1]:
                return "用法: /记忆系统 配置 获取 配置名.键路径"
            c, k = args[1].split(".", 1)
            return json.dumps(self.mem.get_config(c, k), ensure_ascii=False)
        if op == "设置":
            if len(args) < 3 or "." not in args[1]:
                return "用法: /记忆系统 配置 设置 配置名.键路径 值"
            c, k = args[1].split(".", 1)
            self.mem.set_config(c, k, self._parse_value(" ".join(args[2:])))
            return "ok"
        return "未知配置操作"

    def _add_intent(self, args: List[str]) -> str:
        if len(args) < 2:
            return "用法: /记忆系统 添加意图 类型 内容 [优先级]"
        intent_type = args[0]
        if len(args) >= 3 and args[-1] in ["low", "medium", "high"]:
            priority = args[-1]
            content = " ".join(args[1:-1])
        else:
            priority = "medium"
            content = " ".join(args[1:])
        intent_id = self.mem.add_intent(intent_type, content, priority)
        return f"ok {intent_id}"

    def _build_context(self) -> str:
        ctx = self.mem.build_session_context()
        return json.dumps(ctx, ensure_ascii=False, indent=2)

    def _analyze(self, args: List[str]) -> str:
        if not args:
            return "用法: /记忆系统 分析 文本"
        text = " ".join(args)
        return json.dumps(self.mem.analyze_text(text), ensure_ascii=False, indent=2)

    def _write_conversation(self, args: List[str]) -> str:
        if len(args) < 2:
            return "用法: /记忆系统 记录对话 会话ID JSON消息数组"
        conv_id = args[0]
        raw = " ".join(args[1:])
        try:
            messages = json.loads(raw)
            self.mem.write_conversation(conv_id, messages)
            return "ok"
        except Exception as e:
            return f"error: {e}"

    def _export(self, args: List[str]) -> str:
        if not args:
            return "用法: /记忆系统 导出 文件路径"
        self.mem.export_all(args[0])
        return "ok"

    def _import_data(self, args: List[str]) -> str:
        if not args:
            return "用法: /记忆系统 导入 文件路径 [merge|replace]"
        mode = args[1] if len(args) > 1 else "merge"
        if mode not in ["merge", "replace"]:
            return "导入模式只支持 merge 或 replace"
        self.mem.import_all(args[0], mode)
        return f"ok imported {mode}"

    def _session_start(self, args: List[str]) -> str:
        topic = " ".join(args).strip() if args else "new chat"
        ctx = self.mem.build_session_context()
        return json.dumps(
            {
                "session_id": datetime.now().strftime("sess_%Y%m%d_%H%M%S"),
                "topic": topic,
                "context": ctx,
            },
            ensure_ascii=False,
            indent=2,
        )

    def _session_end(self, args: List[str]) -> str:
        if len(args) < 2:
            return "用法: /记忆系统 会话结束 会话ID JSON消息数组"
        conv_id = args[0]
        raw = " ".join(args[1:])
        try:
            messages = json.loads(raw)
            self.mem.write_conversation(conv_id, messages)
            return "ok"
        except Exception as e:
            return f"error: {e}"

    def _weekly_review(self, args: List[str]) -> str:
        days = 7
        if args and str(args[0]).isdigit():
            days = max(1, int(args[0]))
        report = self.mem.generate_weekly_review(days=days)
        return json.dumps(report, ensure_ascii=False, indent=2)

    def _monthly_report(self, args: List[str]) -> str:
        months = 1
        if args and str(args[0]).isdigit():
            months = max(1, int(args[0]))
        report = self.mem.generate_monthly_report(months=months)
        return json.dumps(report, ensure_ascii=False, indent=2)

    def _anomaly(self, args: List[str]) -> str:
        if not args:
            items = self.mem.list_anomalies(limit=10, status="open")
            return json.dumps({"open_count": len(items), "items": items}, ensure_ascii=False, indent=2)

        op = args[0]
        if op == "查看":
            limit = 10
            if len(args) > 1 and str(args[1]).isdigit():
                limit = max(1, int(args[1]))
            items = self.mem.list_anomalies(limit=limit, status="open")
            return json.dumps({"open_count": len(items), "items": items}, ensure_ascii=False, indent=2)
        if op == "处理":
            if len(args) < 2:
                return "用法: /记忆系统 异常 处理 <anomaly_id>"
            ok = self.mem.resolve_anomaly(args[1])
            return "ok" if ok else "not_found"
        if op == "刷新":
            self.mem.refresh_anomaly_reminder()
            return "ok"
        if op == "建议":
            days = 30
            if len(args) > 1 and str(args[1]).isdigit():
                days = max(1, int(args[1]))
            result = self.mem.suggest_preference_updates(days=days, auto_apply=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        if op == "应用建议":
            days = 30
            if len(args) > 1 and str(args[1]).isdigit():
                days = max(1, int(args[1]))
            result = self.mem.suggest_preference_updates(days=days, auto_apply=True)
            return json.dumps(result, ensure_ascii=False, indent=2)
        return "用法: /记忆系统 异常 查看 [n] | 处理 <id> | 刷新 | 建议 [days] | 应用建议 [days]"

    def _preference(self, args: List[str]) -> str:
        if not args:
            return "用法: /记忆系统 偏好 去重 | 应用去重 | 评分 | 重写建议 | 应用重写"
        op = args[0]
        if op == "去重":
            result = self.mem.normalize_preferences(apply_changes=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        if op == "应用去重":
            result = self.mem.normalize_preferences(apply_changes=True)
            return json.dumps(result, ensure_ascii=False, indent=2)
        if op == "评分":
            result = self.mem.preference_quality_report()
            return json.dumps(result, ensure_ascii=False, indent=2)
        if op == "重写建议":
            result = self.mem.suggest_preference_rewrites(auto_apply=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        if op == "应用重写":
            result = self.mem.suggest_preference_rewrites(auto_apply=True)
            return json.dumps(result, ensure_ascii=False, indent=2)
        return "用法: /记忆系统 偏好 去重 | 应用去重 | 评分 | 重写建议 | 应用重写"

    def _policy(self, args: List[str]) -> str:
        return json.dumps(self.mem.build_response_policy(), ensure_ascii=False, indent=2)

    def _hit(self, args: List[str]) -> str:
        days = 7
        if args and str(args[0]).isdigit():
            days = max(1, int(args[0]))
        return json.dumps(self.mem.hit_stats(days=days), ensure_ascii=False, indent=2)

    def _help(self) -> str:
        return (
            "可用命令:\n"
            "/记忆系统 状态\n"
            "/记忆系统 配置 查看\n"
            "/记忆系统 配置 获取 路径配置.screenshot_path\n"
            "/记忆系统 配置 设置 路径配置.screenshot_path E:/ai/snapshot\n"
            "/记忆系统 添加意图 偏好与要求 回答更精炼 high\n"
            "/记忆系统 构建上下文\n"
            "/记忆系统 分析 我想设计分层记忆系统\n"
            "/记忆系统 导出 C:/temp/persona_backup.json\n"
            "/记忆系统 导入 C:/temp/behavior_backup.json merge\n"
            "/记忆系统 会话开始 新对话主题\n"
            "/记忆系统 会话结束 sess_001 [{\"role\":\"user\",\"content\":\"...\"}]\n"
            "/记忆系统 周复盘 7\n"
            "/记忆系统 月报 1\n"
            "/记忆系统 异常 查看 10\n"
            "/记忆系统 异常 处理 anomaly_xxx\n"
            "/记忆系统 异常 建议 30\n"
            "/记忆系统 异常 应用建议 30\n"
            "/记忆系统 偏好 去重\n"
            "/记忆系统 偏好 应用去重\n"
            "/记忆系统 偏好 评分\n"
            "/记忆系统 偏好 重写建议\n"
            "/记忆系统 偏好 应用重写\n"
            "/记忆系统 策略\n"
            "/记忆系统 命中 7"
        )

    def process_natural_language(self, text: str) -> str:
        if "截图路径" in text:
            m = re.search(r"([A-Za-z]:[\\/][^\s]+)", text)
            if m:
                path = m.group(1).replace("\\", "/")
                self.mem.set_config("路径配置", "screenshot_path", path)
                return f"ok 已更新截图路径为 {path}"
        if "状态" in text:
            return self._status()
        if "帮助" in text:
            return self._help()
        if "复盘" in text:
            return self._weekly_review([])
        if "月报" in text:
            return self._monthly_report([])
        if "异常" in text:
            return self._anomaly(["查看", "10"])
        return "无法识别自然语言指令，试试 /记忆系统 帮助"

    def _parse_value(self, raw: str) -> Any:
        t = raw.strip()
        if t.lower() in ["true", "false"]:
            return t.lower() == "true"
        if t.isdigit():
            return int(t)
        try:
            return float(t)
        except ValueError:
            return t


PersonaMemorySkill = BehaviorMemorySkill
