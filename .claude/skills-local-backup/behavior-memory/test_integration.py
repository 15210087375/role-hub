#!/usr/bin/env python3
"""
测试行为记忆系统集成
"""

import os
import sys
import subprocess

def test_command(command, args=None):
    """测试命令"""
    cmd = ["python", "persona_memory.py", command]
    if args:
        cmd.extend(args)
    
    print(f"\n测试命令: {' '.join(cmd[1:])}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ 命令执行成功")
            print(f"输出长度: {len(result.stdout)} 字符")
            # 显示前200字符
            preview = result.stdout[:200]
            if len(result.stdout) > 200:
                preview += "..."
            print(f"输出预览:\n{preview}")
        else:
            print("❌ 命令执行失败")
            print(f"错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return False

def main():
    """主测试函数"""
    
    print("=" * 60)
    print("行为记忆系统集成测试")
    print("=" * 60)
    
    # 切换到技能目录
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(skill_dir)
    
    print(f"测试目录: {skill_dir}")
    print(f"文件列表: {os.listdir(skill_dir)}")
    
    # 测试基本命令
    tests = [
        ("状态", []),
        ("配置", ["查看"]),
        ("配置", ["获取", "路径配置.screenshot_path"]),
        ("分析", ["测试行为记忆系统功能"]),
        ("帮助", [])
    ]
    
    success_count = 0
    for command, args in tests:
        if test_command(command, args):
            success_count += 1
    
    print(f"\n" + "=" * 60)
    print(f"测试结果: {success_count}/{len(tests)} 个测试通过")
    
    if success_count == len(tests):
        print("✅ 所有测试通过！系统集成正常。")
        print("\n现在可以在OpenCode中使用:")
        print("  /记忆系统 状态")
        print("  /记忆系统 配置 查看")
        print("  /记忆系统 分析 \"文本\"")
        print("  /记忆系统 帮助")
    else:
        print("⚠️  部分测试失败，需要检查集成。")
    
    # 额外测试：直接查询截图路径
    print(f"\n" + "=" * 60)
    print("直接查询截图路径:")
    
    try:
        import persona_core
        core = persona_core.BehaviorMemoryCore()
        screenshot_path = core.get_config("路径配置", "screenshot_path")
        print(f"✅ 截图路径: {screenshot_path}")
        
        # 验证路径存在
        if screenshot_path and os.path.exists(os.path.dirname(screenshot_path)):
            print(f"✅ 截图目录存在: {os.path.dirname(screenshot_path)}")
        else:
            print(f"⚠️  截图目录可能不存在: {screenshot_path}")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    print(f"\n" + "=" * 60)
    print("测试完成！")

if __name__ == "__main__":
    main()