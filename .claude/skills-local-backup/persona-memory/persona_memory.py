#!/usr/bin/env python3
"""
行为记忆系统 - OpenCode技能入口
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    
    try:
        from opencode_integration import BehaviorMemorySkill
        
        skill = BehaviorMemorySkill()
        
        if len(sys.argv) > 1:
            # 命令行模式
            command = sys.argv[1]
            args = sys.argv[2:] if len(sys.argv) > 2 else []
            result = skill.process_command(command, args)
            print(result)
        else:
            # 交互模式
            print(skill.process_command("帮助", []))
            
    except Exception as e:
        print(f"记忆系统错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
