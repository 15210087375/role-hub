#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色查询工具
用于查询角色信息、关系和变化记录
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

class CharacterQuery:
    """角色查询器"""
    
    def __init__(self, project_dir: Optional[str] = None):
        """
        初始化角色查询器
        
        Args:
            project_dir: 项目目录路径，默认为当前目录
        """
        if project_dir is None:
            self.project_dir = Path.cwd()
        else:
            self.project_dir = Path(project_dir)
        
        # 检查项目结构
        self.characters_dir = self.project_dir / "03-角色库" / "characters"
        self.timeline_dir = self.project_dir / "04-时间线"
        self.collaboration_dir = self.project_dir / "08-协作记录"
        
        if not self.characters_dir.exists():
            print(f"错误: 角色库目录不存在: {self.characters_dir}")
            sys.exit(1)
    
    def query_character(self, character_name: str, show_relations: bool = True, 
                       show_timeline: bool = True, show_changes: bool = True) -> Dict[str, Any]:
        """
        查询角色信息
        
        Args:
            character_name: 角色名称
            show_relations: 是否显示关系
            show_timeline: 是否显示时间线
            show_changes: 是否显示变化记录
            
        Returns:
            角色信息字典
        """
        result = {
            "character": None,
            "relations": [],
            "timeline_events": [],
            "changes": [],
            "found": False
        }
        
        # 查找角色文件
        character_file = self._find_character_file(character_name)
        if not character_file:
            print(f"未找到角色: {character_name}")
            return result
        
        result["found"] = True
        
        # 读取角色信息
        character_info = self._read_character_file(character_file)
        result["character"] = character_info
        
        # 查询关系
        if show_relations:
            result["relations"] = self._query_relations(character_name, character_info)
        
        # 查询时间线事件
        if show_timeline:
            result["timeline_events"] = self._query_timeline_events(character_name)
        
        # 查询变化记录
        if show_changes:
            result["changes"] = self._query_changes(character_name)
        
        return result
    
    def _find_character_file(self, character_name: str) -> Optional[Path]:
        """查找角色文件"""
        # 首先尝试精确匹配
        possible_files = [
            self.characters_dir / f"{character_name}.md",
            self.characters_dir / f"{character_name}.yaml",
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                return file_path
        
        # 尝试模糊匹配
        for file_path in self.characters_dir.glob("*.md"):
            if character_name.lower() in file_path.stem.lower():
                return file_path
        
        for file_path in self.characters_dir.glob("*.yaml"):
            if character_name.lower() in file_path.stem.lower():
                return file_path
        
        return None
    
    def _read_character_file(self, file_path: Path) -> Dict[str, Any]:
        """读取角色文件"""
        try:
            if file_path.suffix == '.md':
                return self._read_markdown_character(file_path)
            elif file_path.suffix == '.yaml':
                return self._read_yaml_character(file_path)
            else:
                return {"file": str(file_path), "error": "不支持的文件格式"}
        except Exception as e:
            return {"file": str(file_path), "error": str(e)}
    
    def _read_markdown_character(self, file_path: Path) -> Dict[str, Any]:
        """读取Markdown格式的角色文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析Markdown中的YAML frontmatter
        lines = content.split('\n')
        info = {
            "name": file_path.stem,
            "file": str(file_path),
            "format": "markdown"
        }
        
        if lines and lines[0] == '---':
            yaml_lines = []
            i = 1
            while i < len(lines) and lines[i] != '---':
                yaml_lines.append(lines[i])
                i += 1
            
            if yaml_lines:
                try:
                    frontmatter = yaml.safe_load('\n'.join(yaml_lines))
                    if frontmatter:
                        info.update(frontmatter)
                except:
                    pass
        
        return info
    
    def _read_yaml_character(self, file_path: Path) -> Dict[str, Any]:
        """读取YAML格式的角色文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            data = {}
        
        data.update({
            "name": file_path.stem,
            "file": str(file_path),
            "format": "yaml"
        })
        
        return data
    
    def _query_relations(self, character_name: str, character_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查询角色关系"""
        relations = []
        
        # 从角色信息中提取关系
        if "relations" in character_info:
            for rel_name, rel_type in character_info["relations"].items():
                relations.append({
                    "character": rel_name,
                    "type": rel_type,
                    "source": "character_info"
                })
        
        # 从关系图中查询
        relation_file = self.characters_dir / "角色关系图.md"
        if relation_file.exists():
            try:
                with open(relation_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 简单的关系图解析
                for line in content.split('\n'):
                    if character_name in line and '->' in line:
                        parts = line.split('->')
                        if len(parts) == 2:
                            left = parts[0].strip()
                            right = parts[1].strip()
                            
                            if character_name in left:
                                target = right
                                direction = "outgoing"
                            else:
                                target = left
                                direction = "incoming"
                            
                            # 提取关系类型
                            rel_type = "unknown"
                            if '[' in line and ']' in line:
                                start = line.find('[') + 1
                                end = line.find(']')
                                if start < end:
                                    rel_type = line[start:end]
                            
                            relations.append({
                                "character": target,
                                "type": rel_type,
                                "direction": direction,
                                "source": "relation_graph"
                            })
            except:
                pass
        
        return relations
    
    def _query_timeline_events(self, character_name: str) -> List[Dict[str, Any]]:
        """查询时间线事件"""
        events = []
        
        timeline_file = self.timeline_dir / "大事件时间线.yaml"
        if not timeline_file.exists():
            return events
        
        try:
            with open(timeline_file, 'r', encoding='utf-8') as f:
                timeline_data = yaml.safe_load(f)
            
            if not isinstance(timeline_data, dict):
                return events
            
            for time_period, period_events in timeline_data.items():
                if not isinstance(period_events, list):
                    continue
                
                for event in period_events:
                    if not isinstance(event, dict):
                        continue
                    
                    # 检查事件是否涉及该角色
                    event_text = str(event)
                    if character_name.lower() in event_text.lower():
                        events.append({
                            "time": time_period,
                            "event": event,
                            "source": "timeline"
                        })
        except:
            pass
        
        return events
    
    def _query_changes(self, character_name: str) -> List[Dict[str, Any]]:
        """查询变化记录"""
        changes = []
        
        changes_file = self.collaboration_dir / "变化记录模板.md"
        if not changes_file.exists():
            return changes
        
        try:
            with open(changes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析变化记录
            lines = content.split('\n')
            current_change = None
            
            for line in lines:
                if line.startswith('### '):
                    if current_change and character_name.lower() in str(current_change).lower():
                        changes.append(current_change)
                    current_change = {"title": line[4:].strip(), "details": []}
                elif current_change and line.strip():
                    if character_name.lower() in line.lower():
                        current_change["details"].append(line.strip())
            
            # 检查最后一个变化记录
            if current_change and character_name.lower() in str(current_change).lower():
                changes.append(current_change)
                
        except:
            pass
        
        return changes
    
    def print_result(self, result: Dict[str, Any], verbose: bool = False):
        """打印查询结果"""
        if not result["found"]:
            print(f"角色 '{result.get('search_name', 'unknown')}' 未找到")
            return
        
        character = result["character"]
        print(f"\n{'='*60}")
        print(f"角色: {character.get('name', '未知')}")
        print(f"{'='*60}")
        
        # 基本信息
        print(f"\n基本信息:")
        print(f"  文件: {character.get('file', '未知')}")
        
        for key, value in character.items():
            if key not in ['name', 'file', 'format', 'relations']:
                if isinstance(value, (str, int, float, bool)):
                    print(f"  {key}: {value}")
                elif isinstance(value, list) and len(value) <= 3:
                    print(f"  {key}: {', '.join(str(v) for v in value)}")
        
        # 关系信息
        if result["relations"]:
            print(f"\n关系网络 ({len(result['relations'])}个):")
            for rel in result["relations"]:
                direction = f"({rel.get('direction', '')})" if rel.get('direction') else ""
                print(f"  • {rel['character']} - {rel['type']} {direction}")
        
        # 时间线事件
        if result["timeline_events"]:
            print(f"\n时间线事件 ({len(result['timeline_events'])}个):")
            for event in result["timeline_events"]:
                print(f"  • {event['time']}: {event['event']}")
        
        # 变化记录
        if result["changes"]:
            print(f"\n变化记录 ({len(result['changes'])}个):")
            for change in result["changes"]:
                print(f"  • {change['title']}")
                if verbose and change['details']:
                    for detail in change['details'][:3]:  # 只显示前3个细节
                        print(f"    - {detail}")
        
        print(f"\n{'='*60}")

def main():
    """主函数：命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='角色查询工具')
    parser.add_argument('character_name', help='角色名称')
    parser.add_argument('--project', '-p', help='项目目录路径')
    parser.add_argument('--no-relations', action='store_true', help='不显示关系')
    parser.add_argument('--no-timeline', action='store_true', help='不显示时间线')
    parser.add_argument('--no-changes', action='store_true', help='不显示变化记录')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    # 创建查询器
    query = CharacterQuery(args.project)
    
    # 查询角色
    result = query.query_character(
        args.character_name,
        show_relations=not args.no_relations,
        show_timeline=not args.no_timeline,
        show_changes=not args.no_changes
    )
    
    result["search_name"] = args.character_name
    
    # 输出结果
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        query.print_result(result, args.verbose)

if __name__ == "__main__":
    main()