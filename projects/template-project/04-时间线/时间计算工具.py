#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间计算工具
用于计算时间间隔、推断变化、检查时间一致性
"""

import re
import yaml
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class TimeCalculator:
    """时间计算器"""
    
    def __init__(self, timeline_file: str = "大事件时间线.yaml"):
        """
        初始化时间计算器
        
        Args:
            timeline_file: 时间线文件路径
        """
        self.timeline_file = timeline_file
        self.time_system = self._load_time_system()
        
    def _load_time_system(self) -> Dict:
        """加载时间体系配置"""
        try:
            with open(self.timeline_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('time_system', {})
        except FileNotFoundError:
            print(f"警告: 时间线文件 {self.timeline_file} 未找到，使用默认时间体系")
            return {
                'calendar': '天元历',
                'time_units': {'year': '年', 'month': '月', 'day': '日'},
                'start_year': '元年',
                'current_year': '元年'
            }
    
    def parse_time(self, time_str: str) -> Dict:
        """
        解析时间字符串
        
        Args:
            time_str: 时间字符串，如 "元年3月"、"二年5月"
            
        Returns:
            解析后的时间字典
        """
        pattern = r'([零一二三四五六七八九十百千万]+|[0-9]+)年([零一二三四五六七八九十]+|[0-9]+)月'
        match = re.match(pattern, time_str)
        
        if not match:
            raise ValueError(f"时间格式错误: {time_str}，应为 'X年X月' 格式")
        
        year_str, month_str = match.groups()
        
        # 转换中文数字
        year = self._chinese_to_number(year_str)
        month = self._chinese_to_number(month_str)
        
        return {
            'year': year,
            'month': month,
            'original': time_str
        }
    
    def _chinese_to_number(self, chinese_num: str) -> int:
        """中文数字转阿拉伯数字"""
        chinese_nums = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
            '十': 10, '百': 100, '千': 1000, '万': 10000
        }
        
        # 如果是阿拉伯数字，直接转换
        if chinese_num.isdigit():
            return int(chinese_num)
        
        # 简单中文数字转换（支持个位和十位）
        if len(chinese_num) == 1:
            return chinese_nums.get(chinese_num, 0)
        elif len(chinese_num) == 2 and chinese_num[0] == '十':
            return 10 + chinese_nums.get(chinese_num[1], 0)
        elif len(chinese_num) == 2 and chinese_num[1] == '十':
            return chinese_nums.get(chinese_num[0], 0) * 10
        else:
            # 复杂中文数字，暂时返回序号
            return 1
    
    def calculate_interval(self, start_time: str, end_time: str) -> Dict:
        """
        计算时间间隔
        
        Args:
            start_time: 起始时间
            end_time: 结束时间
            
        Returns:
            间隔信息字典
        """
        start = self.parse_time(start_time)
        end = self.parse_time(end_time)
        
        # 计算月份差
        total_months_start = start['year'] * 12 + start['month']
        total_months_end = end['year'] * 12 + end['month']
        
        month_diff = total_months_end - total_months_start
        
        years = month_diff // 12
        months = month_diff % 12
        
        return {
            'start': start_time,
            'end': end_time,
            'years': years,
            'months': months,
            'total_months': month_diff,
            'description': self._format_interval(years, months)
        }
    
    def _format_interval(self, years: int, months: int) -> str:
        """格式化时间间隔描述"""
        parts = []
        if years > 0:
            parts.append(f"{years}年")
        if months > 0:
            parts.append(f"{months}个月")
        
        if not parts:
            return "不到1个月"
        
        return "".join(parts)
    
    def infer_changes(self, time_interval: Dict, location: Optional[str] = None) -> List[str]:
        """
        推断时间间隔内可能的变化
        
        Args:
            time_interval: 时间间隔信息
            location: 地点名称（可选）
            
        Returns:
            可能的变化列表
        """
        changes = []
        years = time_interval['years']
        months = time_interval['months']
        
        # 根据时间跨度推断变化
        if years >= 1:
            changes.append(f"外貌变化：角色可能显老，可能有新疤痕或特征变化")
            changes.append(f"技能提升：有足够时间修炼新技能或提升等级")
            changes.append(f"关系发展：人际关系可能发生显著变化")
            
        if years >= 3:
            changes.append(f"身份变化：可能升职、转行或改变社会地位")
            changes.append(f"家庭变化：可能结婚、生子或家庭成员变化")
            changes.append(f"地点变化：建筑可能翻新、扩建或损坏")
            
        if years >= 5:
            changes.append(f"性格变化：可能更加成熟或改变价值观")
            changes.append(f"经济变化：可能积累财富或遭遇经济困难")
            changes.append(f"势力变化：所属势力可能发生重大变化")
        
        # 特定地点变化
        if location:
            changes.append(f"地点'{location}'：居民可能有搬入搬出")
            changes.append(f"地点'{location}'：建筑可能有新建或拆除")
            changes.append(f"地点'{location}'：经济状况可能发生变化")
        
        return changes
    
    def get_events_between(self, start_time: str, end_time: str) -> List[Dict]:
        """
        获取两个时间点之间的大事件
        
        Args:
            start_time: 起始时间
            end_time: 结束时间
            
        Returns:
            期间发生的事件列表
        """
        try:
            with open(self.timeline_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            return []
        
        events = []
        start = self.parse_time(start_time)
        end = self.parse_time(end_time)
        
        # 检查各卷时间线
        for volume_key in ['volume_1_timeline', 'volume_2_timeline', 'volume_3_timeline']:
            if volume_key in data:
                for event in data[volume_key]:
                    event_time = self.parse_time(event.get('time', ''))
                    if self._is_time_between(event_time, start, end):
                        events.append(event)
        
        # 检查世界发展事件
        if 'world_development_events' in data:
            for event in data['world_development_events']:
                event_time = self.parse_time(event.get('time', ''))
                if self._is_time_between(event_time, start, end):
                    events.append(event)
        
        return events
    
    def _is_time_between(self, check_time: Dict, start: Dict, end: Dict) -> bool:
        """检查时间是否在区间内"""
        check_months = check_time['year'] * 12 + check_time['month']
        start_months = start['year'] * 12 + start['month']
        end_months = end['year'] * 12 + end['month']
        
        return start_months <= check_months <= end_months
    
    def check_character_consistency(self, character_data: Dict) -> List[str]:
        """
        检查角色时间一致性
        
        Args:
            character_data: 角色数据，包含时间线记录
            
        Returns:
            不一致问题列表
        """
        issues = []
        
        if 'timeline_records' not in character_data:
            return issues
        
        records = character_data['timeline_records']
        if not records:
            return issues
        
        # 检查时间顺序
        times = []
        for record in records:
            time_str = record.get('time', '')
            try:
                parsed = self.parse_time(time_str)
                times.append((parsed['year'] * 12 + parsed['month'], time_str, record))
            except ValueError:
                continue
        
        # 按时间排序
        times.sort(key=lambda x: x[0])
        
        # 检查时间跳跃合理性
        for i in range(1, len(times)):
            prev_time, prev_str, prev_record = times[i-1]
            curr_time, curr_str, curr_record = times[i]
            
            month_diff = curr_time - prev_time
            
            # 检查地点跳跃合理性
            prev_location = prev_record.get('location', '')
            curr_location = curr_record.get('location', '')
            
            if prev_location and curr_location and prev_location != curr_location:
                if month_diff < 1:  # 一个月内出现在不同地方
                    issues.append(f"时间矛盾：{prev_str}在{prev_location}，{curr_str}在{curr_location}，时间间隔太短")
        
        return issues

def main():
    """主函数：命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='时间计算工具')
    parser.add_argument('start_time', help='起始时间，如"元年3月"')
    parser.add_argument('end_time', help='结束时间，如"二年6月"')
    parser.add_argument('--location', '-l', help='地点名称，用于推断地点变化')
    parser.add_argument('--events', '-e', action='store_true', help='显示期间发生的事件')
    parser.add_argument('--timeline', '-t', default='大事件时间线.yaml', help='时间线文件路径')
    
    args = parser.parse_args()
    
    calculator = TimeCalculator(args.timeline)
    
    try:
        # 计算时间间隔
        interval = calculator.calculate_interval(args.start_time, args.end_time)
        print(f"时间间隔: {interval['description']}")
        print(f"详细: {interval['years']}年{interval['months']}个月 ({interval['total_months']}个月)")
        print()
        
        # 推断变化
        changes = calculator.infer_changes(interval, args.location)
        if changes:
            print("可能的变化:")
            for change in changes:
                print(f"  • {change}")
            print()
        
        # 显示期间事件
        if args.events:
            events = calculator.get_events_between(args.start_time, args.end_time)
            if events:
                print("期间发生的事件:")
                for event in events:
                    print(f"  • {event.get('time')}: {event.get('event')} - {event.get('description', '')}")
            else:
                print("期间没有记录的大事件")
        
    except ValueError as e:
        print(f"错误: {e}")
        print("时间格式应为 'X年X月'，如 '元年3月'、'二年6月'")

if __name__ == "__main__":
    main()