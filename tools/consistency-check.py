#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性检查工具
用于检查角色一致性、世界真实性和去AI味质量
"""

import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

@dataclass
class CheckResult:
    """检查结果"""
    category: str
    level: str  # error, warning, info
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    details: List[str] = field(default_factory=list)

@dataclass
class CharacterInfo:
    """角色信息"""
    name: str
    file: str
    age: Optional[int] = None
    gender: Optional[str] = None
    personality: List[str] = field(default_factory=list)
    abilities: List[str] = field(default_factory=list)
    relations: Dict[str, str] = field(default_factory=dict)
    timeline_events: List[Dict] = field(default_factory=list)

class ConsistencyChecker:
    """一致性检查器"""
    
    def __init__(self, project_dir: Optional[str] = None):
        """
        初始化一致性检查器
        
        Args:
            project_dir: 项目目录路径，默认为当前目录
        """
        if project_dir is None:
            self.project_dir = Path.cwd()
        else:
            self.project_dir = Path(project_dir)
        
        # 项目目录
        self.characters_dir = self.project_dir / "03-角色库" / "characters"
        self.timeline_dir = self.project_dir / "04-时间线"
        self.outline_dir = self.project_dir / "05-大纲"
        self.content_dir = self.project_dir / "06-正文"
        self.collaboration_dir = self.project_dir / "08-协作记录"
        
        # 加载数据
        self.timeline = self._load_timeline()
        self.characters = self._load_characters()
    
    def check_all(self) -> List[CheckResult]:
        """执行所有检查"""
        results = []
        
        # 角色一致性检查
        results.extend(self.check_character_consistency())
        
        # 世界真实性检查
        results.extend(self.check_world_reality())
        
        # 时间线一致性检查
        results.extend(self.check_timeline_consistency())
        
        # 去AI味检查
        results.extend(self.check_anti_ai_tone())
        
        # 协作记录检查
        results.extend(self.check_collaboration())
        
        return results
    
    def check_character_consistency(self) -> List[CheckResult]:
        """检查角色一致性"""
        results = []
        
        # 检查角色基本信息
        for char_name, char_info in self.characters.items():
            # 检查年龄合理性
            if char_info.age is not None:
                if char_info.age < 0:
                    results.append(CheckResult(
                        category="角色一致性",
                        level="error",
                        message=f"角色 '{char_name}' 年龄为负数: {char_info.age}",
                        file=char_info.file
                    ))
                elif char_info.age > 150:
                    results.append(CheckResult(
                        category="角色一致性",
                        level="warning",
                        message=f"角色 '{char_name}' 年龄过大: {char_info.age}",
                        file=char_info.file,
                        details=["除非是特殊设定，否则人类角色年龄不应超过150岁"]
                    ))
            
            # 检查性格描述
            if not char_info.personality:
                results.append(CheckResult(
                    category="角色一致性",
                    level="warning",
                    message=f"角色 '{char_name}' 缺少性格描述",
                    file=char_info.file
                ))
            else:
                # 检查性格是否过于完美
                perfect_traits = ["完美", "无缺", "全能", "无敌", "全知", "全善"]
                for trait in char_info.personality:
                    if any(pt in trait for pt in perfect_traits):
                        results.append(CheckResult(
                            category="角色一致性",
                            level="warning",
                            message=f"角色 '{char_name}' 性格描述过于完美: {trait}",
                            file=char_info.file,
                            details=["角色应有缺陷和弱点，避免完美主义"]
                        ))
            
            # 检查能力描述
            if char_info.abilities:
                # 检查能力是否过于强大
                overpowered_abilities = ["无敌", "不死", "全知", "全能", "创世", "灭世"]
                for ability in char_info.abilities:
                    if any(op in ability for op in overpowered_abilities):
                        results.append(CheckResult(
                            category="角色一致性",
                            level="warning",
                            message=f"角色 '{char_name}' 能力过于强大: {ability}",
                            file=char_info.file,
                            details=["过于强大的能力会破坏故事平衡，应有合理限制"]
                        ))
        
        # 检查角色关系
        for char_name, char_info in self.characters.items():
            for rel_name, rel_type in char_info.relations.items():
                # 检查关系是否双向
                if rel_name in self.characters:
                    target_char = self.characters[rel_name]
                    if char_name not in target_char.relations:
                        results.append(CheckResult(
                            category="角色一致性",
                            level="info",
                            message=f"角色关系不完整: '{char_name}' -> '{rel_name}' ({rel_type})",
                            file=char_info.file,
                            details=[f"建议在 '{rel_name}' 的角色档案中添加对 '{char_name}' 的关系定义"]
                        ))
        
        return results
    
    def check_world_reality(self) -> List[CheckResult]:
        """检查世界真实性"""
        results = []
        
        # 检查时间线中的世界变化
        if self.timeline:
            locations = set()
            location_changes = {}
            
            for time_period, events in self.timeline.items():
                if not isinstance(events, list):
                    continue
                
                for event in events:
                    if not isinstance(event, dict):
                        continue
                    
                    # 检查地点变化
                    if "location" in event:
                        location = event["location"]
                        locations.add(location)
                        
                        if location not in location_changes:
                            location_changes[location] = []
                        location_changes[location].append({
                            "time": time_period,
                            "event": event.get("description", str(event))
                        })
            
            # 检查地点是否有合理变化
            for location, changes in location_changes.items():
                if len(changes) < 2:
                    results.append(CheckResult(
                        category="世界真实性",
                        level="info",
                        message=f"地点 '{location}' 缺少变化记录",
                        details=["世界不应静止，地点应随时间有合理变化"]
                    ))
        
        # 检查角色随时间的变化
        for char_name, char_info in self.characters.items():
            if len(char_info.timeline_events) < 2:
                results.append(CheckResult(
                    category="世界真实性",
                    level="info",
                    message=f"角色 '{char_name}' 缺少时间线变化",
                    file=char_info.file,
                    details=["角色应随时间成长、变化，避免静态"]
                ))
        
        return results
    
    def check_timeline_consistency(self) -> List[CheckResult]:
        """检查时间线一致性"""
        results = []
        
        if not self.timeline:
            results.append(CheckResult(
                category="时间线一致性",
                level="warning",
                message="缺少时间线数据",
                details=["建议创建详细的时间线记录"]
            ))
            return results
        
        # 检查时间顺序
        time_periods = list(self.timeline.keys())
        
        # 简单的时间顺序检查（这里可以扩展为更复杂的逻辑）
        for i in range(len(time_periods) - 1):
            current = time_periods[i]
            next_period = time_periods[i + 1]
            
            # 检查时间标签是否合理
            if not self._is_time_progression(current, next_period):
                results.append(CheckResult(
                    category="时间线一致性",
                    level="warning",
                    message=f"时间顺序可能有问题: '{current}' -> '{next_period}'",
                    details=["检查时间标签是否按正确顺序排列"]
                ))
        
        return results
    
    def check_anti_ai_tone(self) -> List[CheckResult]:
        """检查去AI味质量"""
        results = []
        
        # 检查正文文件
        if self.content_dir.exists():
            for file_path in self.content_dir.glob("**/*.md"):
                if file_path.is_file():
                    results.extend(self._check_file_anti_ai_tone(file_path))
        
        # 检查大纲文件
        if self.outline_dir.exists():
            for file_path in self.outline_dir.glob("**/*.md"):
                if file_path.is_file():
                    results.extend(self._check_file_anti_ai_tone(file_path))
        
        return results
    
    def check_collaboration(self) -> List[CheckResult]:
        """检查协作记录"""
        results = []
        
        # 检查变化记录
        changes_file = self.collaboration_dir / "变化记录模板.md"
        if changes_file.exists():
            with open(changes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有变化记录
            if "### 变化记录" not in content or "暂无变化记录" in content:
                results.append(CheckResult(
                    category="协作记录",
                    level="info",
                    message="缺少变化记录",
                    file=str(changes_file),
                    details=["主笔在写作过程中应记录所有对世界观、角色的修改"]
                ))
        
        # 检查问题追踪
        issues_file = self.collaboration_dir / "问题追踪.md"
        if issues_file.exists():
            with open(issues_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有未解决的问题
            unresolved_issues = []
            lines = content.split('\n')
            current_issue = None
            
            for line in lines:
                if line.startswith('### ') and 'P0' in line:
                    current_issue = line[4:].strip()
                elif line.startswith('状态:') and current_issue:
                    if '未解决' in line or '待处理' in line:
                        unresolved_issues.append(current_issue)
                    current_issue = None
            
            if unresolved_issues:
                results.append(CheckResult(
                    category="协作记录",
                    level="warning",
                    message=f"有 {len(unresolved_issues)} 个未解决的P0问题",
                    file=str(issues_file),
                    details=unresolved_issues[:3]  # 只显示前3个
                ))
        
        return results
    
    def _load_characters(self) -> Dict[str, CharacterInfo]:
        """加载角色信息"""
        characters = {}
        
        if not self.characters_dir.exists():
            return characters
        
        # 加载角色索引
        index_file = self.characters_dir.parent / "index.yaml"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = yaml.safe_load(f)
                
                if isinstance(index_data, dict) and "characters" in index_data:
                    for char_data in index_data["characters"]:
                        if isinstance(char_data, dict) and "name" in char_data:
                            char_name = char_data["name"]
                            characters[char_name] = CharacterInfo(
                                name=char_name,
                                file=str(index_file),
                                age=char_data.get("age"),
                                gender=char_data.get("gender"),
                                personality=char_data.get("personality", []),
                                abilities=char_data.get("abilities", []),
                                relations=char_data.get("relations", {})
                            )
            except:
                pass
        
        # 从文件加载角色
        for file_path in self.characters_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 简单解析
                char_name = file_path.stem
                if char_name not in characters:
                    characters[char_name] = CharacterInfo(
                        name=char_name,
                        file=str(file_path)
                    )
            except:
                pass
        
        # 加载时间线中的角色事件
        if self.timeline:
            for char_name in characters.keys():
                characters[char_name].timeline_events = self._get_character_timeline_events(char_name)
        
        return characters
    
    def _load_timeline(self) -> Dict:
        """加载时间线"""
        timeline_file = self.timeline_dir / "大事件时间线.yaml"
        if not timeline_file.exists():
            return {}
        
        try:
            with open(timeline_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except:
            return {}
    
    def _get_character_timeline_events(self, character_name: str) -> List[Dict]:
        """获取角色的时间线事件"""
        events = []
        
        if not self.timeline:
            return events
        
        for time_period, period_events in self.timeline.items():
            if not isinstance(period_events, list):
                continue
            
            for event in period_events:
                if not isinstance(event, dict):
                    continue
                
                event_text = str(event)
                if character_name.lower() in event_text.lower():
                    events.append({
                        "time": time_period,
                        "event": event
                    })
        
        return events
    
    def _is_time_progression(self, current: str, next_period: str) -> bool:
        """检查时间是否在前进"""
        # 简单检查：如果包含数字，检查数字是否增加
        import re
        
        current_nums = re.findall(r'\d+', current)
        next_nums = re.findall(r'\d+', next_period)
        
        if current_nums and next_nums:
            try:
                current_num = int(current_nums[-1])
                next_num = int(next_nums[-1])
                return next_num >= current_num
            except:
                pass
        
        return True  # 默认通过
    
    def _check_file_anti_ai_tone(self, file_path: Path) -> List[CheckResult]:
        """检查文件的去AI味质量"""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # AI味特征检查
            ai_patterns = [
                (r"首先，|其次，|再次，|最后，", "使用'首先、其次、再次、最后'的AI式列举"),
                (r"总而言之，|综上所述，|总的来说，", "使用'总而言之、综上所述'的AI式总结"),
                (r"值得注意的是，|需要指出的是，|值得一提的是，", "使用'值得注意的是、需要指出的是'的AI式强调"),
                (r"一方面，|另一方面，", "使用'一方面、另一方面'的AI式对比"),
                (r"——[^，。！？]*——", "使用破折号进行解释说明"),
                (r"。\s*[他她它这那]的", "使用'。他的'式AI断句"),
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern, description in ai_patterns:
                    if re.search(pattern, line):
                        results.append(CheckResult(
                            category="去AI味",
                            level="warning",
                            message=f"检测到AI味特征: {description}",
                            file=str(file_path),
                            line=i,
                            details=[f"原文: {line.strip()[:100]}..."]
                        ))
            
            # 段落长度检查
            paragraph_lengths = []
            current_paragraph = 0
            
            for i, line in enumerate(lines, 1):
                if line.strip():
                    current_paragraph += 1
                else:
                    if current_paragraph > 0:
                        paragraph_lengths.append((i - current_paragraph, current_paragraph))
                        current_paragraph = 0
            
            # 检查最后一个段落
            if current_paragraph > 0:
                paragraph_lengths.append((len(lines) - current_paragraph + 1, current_paragraph))
            
            # 检查过长的段落
            for start_line, length in paragraph_lengths:
                if length > 8:  # 超过8行的段落
                    results.append(CheckResult(
                        category="去AI味",
                        level="info",
                        message=f"段落过长: {length}行",
                        file=str(file_path),
                        line=start_line,
                        details=["建议将长段落拆分为多个短段落，提高可读性"]
                    ))
            
            # 检查修饰词密度
            modifiers = ["非常", "极其", "特别", "十分", "相当", "颇为", "颇为", "颇为"]
            total_words = len(re.findall(r'[\u4e00-\u9fff]+', content))
            modifier_count = sum(content.count(mod) for mod in modifiers)
            
            if total_words > 0:
                modifier_density = modifier_count / total_words
                if modifier_density > 0.05:  # 超过5%的修饰词密度
                    results.append(CheckResult(
                        category="去AI味",
                        level="warning",
                        message=f"修饰词密度过高: {modifier_density:.2%}",
                        file=str(file_path),
                        details=["建议减少'非常、极其、特别'等修饰词，使用更具体的描述"]
                    ))
        
        except Exception as e:
            results.append(CheckResult(
                category="系统",
                level="error",
                message=f"检查文件时出错: {str(e)}",
                file=str(file_path)
            ))
        
        return results
    
    def print_results(self, results: List[CheckResult], show_info: bool = False):
        """打印检查结果"""
        if not results:
            print("✓ 所有检查通过！")
            return
        
        # 按类别和级别分组
        by_category = {}
        for result in results:
            if result.level == "info" and not show_info:
                continue
            
            if result.category not in by_category:
                by_category[result.category] = {"error": [], "warning": [], "info": []}
            
            by_category[result.category][result.level].append(result)
        
        # 打印结果
        for category, levels in by_category.items():
            print(f"\n{'='*60}")
            print(f"{category}")
            print(f"{'='*60}")
            
            for level in ["error", "warning", "info"]:
                level_results = levels[level]
                if level_results:
                    level_symbol = {"error": "[错误]", "warning": "[警告]", "info": "[提示]"}[level]
                    level_name = {"error": "错误", "warning": "警告", "info": "提示"}[level]
                    
                    print(f"\n{level_symbol} {level_name} ({len(level_results)}个):")
                    
                    for result in level_results:
                        location = ""
                        if result.file:
                            location = f" ({result.file}"
                            if result.line:
                                location += f":{result.line}"
                            location += ")"
                        
                        print(f"  - {result.message}{location}")
                        
                        if result.details:
                            for detail in result.details[:2]:  # 只显示前2个细节
                                print(f"    > {detail}")
        
        # 统计信息
        total = len(results)
        errors = sum(1 for r in results if r.level == "error")
        warnings = sum(1 for r in results if r.level == "warning")
        infos = sum(1 for r in results if r.level == "info")
        
        print(f"\n{'='*60}")
        print(f"检查完成: {total}个问题 (错误: {errors}, 警告: {warnings}, 提示: {infos})")
        
        if errors > 0:
            print("[错误] 存在错误，请修复后再继续")
            sys.exit(1)
        elif warnings > 0:
            print("[警告] 存在警告，建议修复")
        else:
            print("[通过] 检查通过")

def main():
    """主函数：命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='一致性检查工具')
    parser.add_argument('--project', '-p', help='项目目录路径')
    parser.add_argument('--show-info', '-i', action='store_true', help='显示提示信息')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--category', '-c', help='只检查特定类别', 
                       choices=['character', 'world', 'timeline', 'anti-ai', 'collaboration', 'all'])
    
    args = parser.parse_args()
    
    # 创建检查器
    checker = ConsistencyChecker(args.project)
    
    # 执行检查
    if args.category and args.category != 'all':
        # 执行特定检查
        check_methods = {
            'character': checker.check_character_consistency,
            'world': checker.check_world_reality,
            'timeline': checker.check_timeline_consistency,
            'anti-ai': checker.check_anti_ai_tone,
            'collaboration': checker.check_collaboration,
        }
        
        if args.category in check_methods:
            results = check_methods[args.category]()
        else:
            results = checker.check_all()
    else:
        results = checker.check_all()
    
    # 输出结果
    if args.json:
        import json
        output = []
        for result in results:
            output.append({
                "category": result.category,
                "level": result.level,
                "message": result.message,
                "file": result.file,
                "line": result.line,
                "details": result.details
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        checker.print_results(results, args.show_info)

if __name__ == "__main__":
    main()