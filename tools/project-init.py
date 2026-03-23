#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目初始化工具
用于创建新的创作项目文件夹结构
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Optional

class ProjectInitializer:
    """项目初始化器"""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化项目初始化器
        
        Args:
            template_dir: 模板目录路径，默认为projects/template-project
        """
        if template_dir is None:
            # 默认模板目录
            self.template_dir = Path(__file__).parent.parent / "projects" / "template-project"
        else:
            self.template_dir = Path(template_dir)
        
        if not self.template_dir.exists():
            print(f"错误: 模板目录不存在: {self.template_dir}")
            sys.exit(1)
    
    def create_project(self, project_name: str, target_dir: Optional[str] = None) -> bool:
        """
        创建新项目
        
        Args:
            project_name: 项目名称
            target_dir: 目标目录，默认为projects目录下
            
        Returns:
            是否创建成功
        """
        # 确定目标目录
        if target_dir is None:
            target_dir_path = Path(__file__).parent.parent / "projects" / project_name
        else:
            target_dir_path = Path(target_dir) / project_name
        
        # 检查目标目录是否已存在
        if target_dir_path.exists():
            print(f"错误: 项目目录已存在: {target_dir_path}")
            return False
        
        try:
            # 创建项目目录
            target_dir_path.mkdir(parents=True, exist_ok=True)
            print(f"创建项目目录: {target_dir_path}")
            
            # 复制模板文件
            self._copy_template_files(self.template_dir, target_dir_path)
            
            # 替换模板变量
            self._replace_template_variables(target_dir_path, project_name)
            
            # 创建gitignore文件
            self._create_gitignore(target_dir_path)
            
            # 创建README文件
            self._create_readme(target_dir_path, project_name)
            
            print(f"\n项目 '{project_name}' 创建成功!")
            print(f"项目路径: {target_dir_path}")
            print("\n下一步:")
            print("1. 编辑项目信息: projects/{}/01-项目信息/project-info.md".format(project_name))
            print("2. 开始世界观设计: projects/{}/02-世界观/".format(project_name))
            print("3. 创建角色库: projects/{}/03-角色库/".format(project_name))
            print("4. 规划时间线: projects/{}/04-时间线/".format(project_name))
            print("5. 制定大纲: projects/{}/05-大纲/".format(project_name))
            
            return True
            
        except Exception as e:
            print(f"创建项目失败: {e}")
            # 清理已创建的目录
            if target_dir_path.exists():
                shutil.rmtree(target_dir_path)
            return False
    
    def _copy_template_files(self, src_dir: Path, dst_dir: Path) -> None:
        """复制模板文件"""
        print("复制模板文件...")
        
        for root, dirs, files in os.walk(src_dir):
            # 计算目标路径
            rel_path = Path(root).relative_to(src_dir)
            target_path = dst_dir / rel_path
            
            # 创建目录
            target_path.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            for file in files:
                src_file = Path(root) / file
                dst_file = target_path / file
                
                # 跳过某些文件
                if file.endswith('.pyc') or file == '__pycache__':
                    continue
                
                shutil.copy2(src_file, dst_file)
                print(f"  复制: {rel_path / file}")
    
    def _replace_template_variables(self, project_dir: Path, project_name: str) -> None:
        """替换模板变量"""
        print("替换模板变量...")
        
        # 需要替换的变量映射
        replacements = {
            "[填写作品名称]": project_name,
            "[项目名称]": project_name,
            "[YYYY-MM-DD]": self._get_current_date(),
            "[主角姓名]": "待填写",
            "[重要反派]": "待填写",
            "[重要盟友]": "待填写",
            "[导师/长辈]": "待填写",
            "[重要女性角色]": "待填写",
        }
        
        # 遍历所有文件进行替换
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith('.md') or file.endswith('.yaml') or file.endswith('.txt'):
                    file_path = Path(root) / file
                    self._replace_in_file(file_path, replacements)
    
    def _replace_in_file(self, file_path: Path, replacements: dict) -> None:
        """在文件中替换文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 执行替换
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except UnicodeDecodeError:
            # 跳过二进制文件
            pass
        except Exception as e:
            print(f"  警告: 处理文件 {file_path} 时出错: {e}")
    
    def _get_current_date(self) -> str:
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def _create_gitignore(self, project_dir: Path) -> None:
        """创建.gitignore文件"""
        gitignore_content = """# 创作项目gitignore

# 临时文件
*.tmp
*.temp
*.bak
*.swp
*.swo
*~

# 编辑器文件
.vscode/
.idea/
*.sublime-*

# 系统文件
.DS_Store
Thumbs.db

# 日志文件
*.log

# 备份文件
backup/
*.backup

# 个人笔记
personal-notes.md
todo.md

# 大型媒体文件
*.mp4
*.avi
*.mov
*.wav
*.mp3

# 压缩文件
*.zip
*.rar
*.7z

# 可执行文件
*.exe
*.dll
*.so
*.dylib

# Python缓存
__pycache__/
*.pyc
*.pyo
*.pyd

# 环境文件
.env
.env.local
.env.*.local

# 测试文件
test-*.md
draft-*.md
"""
        
        gitignore_path = project_dir / ".gitignore"
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print(f"创建: .gitignore")
    
    def _create_readme(self, project_dir: Path, project_name: str) -> None:
        """创建项目README文件"""
        current_date = self._get_current_date()
        readme_content = f"""# {project_name}

## 项目简介
[在这里填写项目简介]

## 项目结构

```
{project_name}/
├── 01-项目信息/          # 项目基础信息和团队信息
├── 02-世界观/           # 世界观设定文档
├── 03-角色库/           # 角色档案和关系图
├── 04-时间线/           # 大事件时间线和地点发展
├── 05-大纲/             # 主线大纲和分章细纲
├── 06-正文/             # 章节正文文件
├── 07-资产库/           # 从设定师获取的资产卡
└── 08-协作记录/         # 变化记录和检查记录
```

## 快速开始

### 1. 填写项目信息
编辑 `01-项目信息/project-info.md` 文件，填写项目基础信息。

### 2. 设计世界观
在 `02-世界观/` 目录中创建世界观设定文档。

### 3. 创建角色库
在 `03-角色库/characters/` 目录中创建角色档案。

### 4. 规划时间线
在 `04-时间线/` 目录中规划大事件时间线。

### 5. 制定大纲
在 `05-大纲/` 目录中制定主线大纲和分章细纲。

### 6. 开始写作
在 `06-正文/` 目录中开始章节写作。

## 工具使用

### 时间计算工具
```bash
cd {project_name}/04-时间线
python 时间计算工具.py "元年3月" "二年6月" --events
```

### 角色查询工具
```bash
cd {project_name}
python ../tools/character-query.py [角色名]
```

### 项目初始化工具
```bash
python tools/project-init.py 新项目名称
```

## 协作规范

### 文件命名规范
- 使用中文命名，明确含义
- 统一使用小写字母和连字符
- 避免特殊字符和空格

### 版本控制规范
- 每次修改提交有意义的commit message
- 定期同步到远程仓库
- 使用分支进行功能开发

### 协作流程
1. 架构师规划 → 提供基础库和摘要
2. 主笔写作 → 查询库信息 + 记录变化
3. 责编检查 → P0/P1/P2分级检查
4. 架构师更新 → 整合变化，更新正式库

## 联系方式

- 项目负责人: [填写姓名]
- 架构师: [填写姓名]
- 主笔: [填写姓名]
- 责编: [填写姓名]
- 设定师: [填写姓名]

## 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|----------|--------|
| {current_date} | 1.0 | 项目创建 | 项目初始化工具 |
"""
        
        readme_path = project_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"创建: README.md")

def main():
    """主函数：命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='项目初始化工具')
    parser.add_argument('project_name', help='项目名称')
    parser.add_argument('--template', '-t', help='模板目录路径')
    parser.add_argument('--target', '-d', help='目标目录路径')
    
    args = parser.parse_args()
    
    # 创建初始化器
    initializer = ProjectInitializer(args.template)
    
    # 创建项目
    success = initializer.create_project(args.project_name, args.target)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()