# role-hub

Cross-device role governance and skill execution bundle.

## 网文创作协作系统

我们已经成功建立了一个完整的网文创作协作系统，包含三个核心角色、标准化项目模板和配套工具集。

### 核心功能
- **三个专业角色**: 架构师、主笔、责编
- **标准化项目模板**: 8层目录结构
- **自动化工具集**: 项目初始化、角色查询、一致性检查
- **质量控制体系**: 去AI味、角色一致性、世界真实性

### 快速开始
```bash
# 创建新项目
cd tools
python project-init.py 我的小说

# 进入项目
cd ../projects/我的小说

# 检查一致性
python ../../tools/consistency-check.py
```

详细使用指南请查看 [USAGE.md](USAGE.md)

---

## 原始role-hub功能

### Structure

- `roles/`: source of truth registry, role definitions, management scripts.
- `skills/`: executable role skills for OpenCode.

## Quick Start

- Windows: `powershell -ExecutionPolicy Bypass -File roles/portable/install.ps1 -SourceRoot "<repo-root>"`
- macOS/Linux: `bash roles/portable/install.sh --source-root "<repo-root>"`

## Validation

- `python roles/role_sync.py validate`
- `python roles/role_sync.py sync`
- `python roles/role_agents_sync.py`

## Skill Drift Maintenance

- Check drift between repository and local installed skills:
  - `python scripts/skill_drift_check.py --repo-root .`
- Sync from repository to local installation (apply):
  - `python scripts/skill_sync.py --repo-root . --from repo --apply`
- Sync from local edits back to repository (apply):
  - `python scripts/skill_sync.py --repo-root . --from local --apply`

## Role/Skill Alignment Check

- Check key role-to-skill alignment rules:
  - `python scripts/role_skill_alignment_check.py --repo-root .`

## Memory Backup And Sync

- Backup local non-repo memory into repository (AGENTS + local-only skills backup):
  - `python scripts/memory_sync.py backup-local --repo-root . --apply`
- Sync latest repository memory to local (managed scope only):
  - `python scripts/memory_sync.py sync-to-local --repo-root . --apply`
- Scope note: device-specific settings (e.g., screenshot paths, machine-local absolute paths) are intentionally excluded.
