#!/usr/bin/env python3
"""
简单测试行为记忆系统
"""

import os
import sys

def main():
    print("Testing Persona Memory System Integration")
    print("=" * 50)
    
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(skill_dir)
    
    print(f"Skill directory: {skill_dir}")
    
    # 测试导入
    sys.path.append(skill_dir)
    
    try:
        import persona_core
        print("[OK] Core module imported")
        
        # 创建实例
        core = persona_core.BehaviorMemoryCore()
        print("[OK] Core instance created")
        
        # 测试配置
        screenshot_path = core.get_config("路径配置", "screenshot_path")
        print(f"[OK] Screenshot path: {screenshot_path}")
        
        # 测试技能
        import opencode_integration
        skill = opencode_integration.BehaviorMemorySkill()
        print("[OK] Skill instance created")
        
        # 测试命令
        result = skill.process_command("状态", [])
        print(f"[OK] Status command: {len(result)} characters")
        
        # 测试配置查看
        result = skill.process_command("配置", ["获取", "路径配置.screenshot_path"])
        print(f"[OK] Config command executed")
        
        print("\n" + "=" * 50)
        print("All tests passed!")
        print("\nNow you can use in OpenCode:")
        print("  /记忆系统 状态")
        print("  /记忆系统 配置 查看")
        print("  /记忆系统 分析 \"text\"")
        print("  /记忆系统 帮助")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)