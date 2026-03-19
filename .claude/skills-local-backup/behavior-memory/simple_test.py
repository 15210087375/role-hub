#!/usr/bin/env python3
"""
行为记忆系统简化测试
"""

import os
import sys
import json

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_core_system():
    """测试核心系统"""
    print("=" * 60)
    print("测试核心系统")
    print("=" * 60)
    
    from persona_core import BehaviorMemoryCore
    
    # 初始化
    core = BehaviorMemoryCore()
    
    # 检查配置
    screenshot_path = core.get_config("路径配置", "screenshot_path")
    print(f"1. 截图路径: {screenshot_path}")
    
    # 系统状态
    status = core.get_system_status()
    storage = status.get('storage_usage', {})
    print(f"2. 存储使用: {storage.get('file_count', 0)} 文件, {storage.get('total_size_mb', 0)} MB")
    
    # 更新配置
    print("\n3. 测试配置更新...")
    success = core.update_config("路径配置", "screenshot_path", "E:\\ai\\snapshot")
    print(f"配置更新: {'成功' if success else '失败'}")
    
    # 验证更新
    updated_path = core.get_config("路径配置", "screenshot_path")
    print(f"更新后路径: {updated_path}")
    
    print("\n核心系统测试完成!")

def test_conversation():
    """测试对话功能"""
    print("\n" + "=" * 60)
    print("测试对话功能")
    print("=" * 60)
    
    from persona_core import BehaviorMemoryCore
    
    core = BehaviorMemoryCore()
    
    # 开始对话
    conv_id = core.start_conversation("测试对话")
    print(f"1. 对话开始: {conv_id}")
    
    # 添加消息
    core.add_message("user", "如何设计分层记忆系统？")
    core.add_message("assistant", "分层记忆系统可以从L0原始对话到L4核心价值观层层抽象")
    
    core.add_message("user", "L1层应该记录什么？")
    core.add_message("assistant", "L1情境层记录对话场景、情感基调、环境信息")
    
    # 结束对话
    saved_id = core.end_conversation()
    print(f"2. 对话保存: {saved_id}")
    
    # 检查文件
    l0_file = os.path.join(core.memory_root, f"Memory/L0_状态层/{conv_id}.json")
    if os.path.exists(l0_file):
        print(f"3. L0文件已创建: {os.path.getsize(l0_file)} 字节")
    
    print("\n对话功能测试完成!")

def test_skill_commands():
    """测试技能命令"""
    print("\n" + "=" * 60)
    print("测试技能命令")
    print("=" * 60)
    
    # 由于编码问题，我们直接测试功能
    from persona_core import BehaviorMemoryCore
    
    core = BehaviorMemoryCore()
    
    print("1. 测试配置获取:")
    configs = list(core.configs.keys())
    print(f"可用配置: {', '.join(configs)}")
    
    print("\n2. 测试路径配置:")
    paths = core.get_config("路径配置")
    if paths:
        print(f"截图路径: {paths.get('screenshot_path', '未设置')}")
        print(f"项目根目录: {paths.get('project_root', '未设置')}")
    
    print("\n3. 测试设备配置:")
    device = core.get_config("设备配置")
    if device:
        print(f"设备名称: {device.get('device_name', '未设置')}")
        print(f"平台: {device.get('platform', '未设置')}")
    
    print("\n技能命令测试完成!")

def test_export():
    """测试导出功能"""
    print("\n" + "=" * 60)
    print("测试导出功能")
    print("=" * 60)
    
    from persona_core import BehaviorMemoryCore
    
    core = BehaviorMemoryCore()
    
    # 创建测试备份目录
    backup_dir = os.path.join(core.memory_root, "Backups", "test")
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_file = os.path.join(backup_dir, "test_export.json")
    
    print(f"1. 导出到: {backup_file}")
    success = core.export_memory(backup_file, ["config"])
    
    if success and os.path.exists(backup_file):
        file_size = os.path.getsize(backup_file)
        print(f"2. 导出成功: {file_size} 字节")
        
        # 读取验证
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"3. 导出数据验证:")
            print(f"   - 导出时间: {data.get('export_time', '未知')}")
            print(f"   - 包含配置: {list(data.get('configs', {}).keys())}")
        except Exception as e:
            print(f"3. 读取导出文件失败: {e}")
    else:
        print("2. 导出失败")
    
    print("\n导出功能测试完成!")

def main():
    """主测试函数"""
    print("开始行为记忆系统测试...")
    
    try:
        test_core_system()
        test_conversation()
        test_skill_commands()
        test_export()
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
        
        # 显示最终状态
        from persona_core import BehaviorMemoryCore
        core = BehaviorMemoryCore()
        
        print("\n系统信息:")
        print(f"记忆根目录: {core.memory_root}")
        print(f"会话ID: {core.session_id}")
        
        # 目录结构
        print("\n目录结构:")
        for item in os.listdir(core.memory_root):
            item_path = os.path.join(core.memory_root, item)
            if os.path.isdir(item_path):
                file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
                print(f"  {item}/ ({file_count} 文件)")
            else:
                print(f"  {item}")
        
        print("\n" + "=" * 60)
        print("使用说明:")
        print("=" * 60)
        print("1. 核心系统: python persona_core.py --status")
        print("2. 更新配置: python persona_core.py --config 路径配置.screenshot_path=E:\\ai\\snapshot")
        print("3. 开始对话: python persona_core.py --start-conv '测试对话'")
        print("4. 添加意图: python persona_core.py --add-intent 目标与规划 '完成项目'")
        print("5. 导出记忆: python persona_core.py --export backup.json")
        
    except Exception as e:
        print(f"测试错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()