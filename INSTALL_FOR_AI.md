# Role Hub 安装与更新说明（给 AI 直接执行）

结论：本文件可直接作为 AI 执行手册。

你可以把这份文档发给 AI，让它自动完成：

- 首次安装（新设备）
- 后续更新（人员新增、角色变更、规则变更）

---

## 0. 执行目标

将本仓库内容同步到本机运行目录，并完成校验：

- 角色目录：`~/.config/opencode/roles`
- 技能目录：`~/.claude/skills`

并确保运行规则已同步到：

- `~/.config/opencode/AGENTS.md`

---

## 1. AI 执行前提

执行前请确认：

1. 已安装 `git`
2. 已安装 `python`（macOS/Linux 可用 `python3`）
3. 可访问仓库：`https://github.com/15210087375/role-hub.git`
4. AI 有终端命令执行权限

---

## 2. 路径规则（必须遵守）

统一使用环境变量 `OPENCODE_ROLES_DIR`：

- 优先使用显式设置的 `OPENCODE_ROLES_DIR`
- 未设置时回退到：`~/.config/opencode/roles`

AI 不要硬编码机器绝对路径（如 `C:/Users/Administrator/...`）。

---

## 3. Windows 安装（首次）

当设备从未安装过 Role Hub 时，执行以下命令。

```powershell
git clone https://github.com/15210087375/role-hub.git
cd role-hub
$env:OPENCODE_ROLES_DIR = "$HOME/.config/opencode/roles"
powershell -ExecutionPolicy Bypass -File roles/portable/install.ps1 -SourceRoot "$PWD"
python "$env:OPENCODE_ROLES_DIR/role_sync.py" validate
python "$env:OPENCODE_ROLES_DIR/role_agents_sync.py"
```

---

## 4. Windows 更新（后续）

当仓库已有新角色/新人员/新规则时，在新设备执行更新：

```powershell
cd role-hub
git pull origin main
$env:OPENCODE_ROLES_DIR = "$HOME/.config/opencode/roles"
powershell -ExecutionPolicy Bypass -File roles/portable/update.ps1 -RepoRoot "$PWD"
python "$env:OPENCODE_ROLES_DIR/role_sync.py" validate
python "$env:OPENCODE_ROLES_DIR/role_agents_sync.py"
```

---

## 5. macOS/Linux（如需）

### 首次安装

```bash
git clone https://github.com/15210087375/role-hub.git
cd role-hub
export OPENCODE_ROLES_DIR="$HOME/.config/opencode/roles"
bash roles/portable/install.sh --source-root "$PWD"
python3 "$OPENCODE_ROLES_DIR/role_sync.py" validate
python3 "$OPENCODE_ROLES_DIR/role_agents_sync.py"
```

### 后续更新

```bash
cd role-hub
git pull origin main
export OPENCODE_ROLES_DIR="$HOME/.config/opencode/roles"
bash roles/portable/update.sh --repo-root "$PWD"
python3 "$OPENCODE_ROLES_DIR/role_sync.py" validate
python3 "$OPENCODE_ROLES_DIR/role_agents_sync.py"
```

---

## 6. 验收标准（AI 执行后必须回传）

AI 必须输出以下结果：

1. `role_sync.py validate` 的 JSON 结果全文
2. `missing_skill_count` 必须为 `0`
3. 最终生效路径（`OPENCODE_ROLES_DIR` 实际值）
4. 说明已同步 `~/.config/opencode/AGENTS.md`
5. 激活测试结果：
   - `主理人模式`
   - `你好主理人`
   - `编程模式`
   - `策划模式`
6. 提醒重开会话，使新规则完全生效

---

## 7. 常见问题

1. `python` 不可用：
   - Windows 试 `py`
   - macOS/Linux 使用 `python3`

2. PowerShell 被策略拦截：
   - 确保命令包含 `-ExecutionPolicy Bypass`

3. 拉取失败（私有权限问题）：
   - 先完成 `gh auth login` 或配置 Git 凭证

4. 更新后看不到新增角色：
   - 重新执行 `role_sync.py sync` 与 `role_sync.py validate`
   - 重开会话后再测试触发词

---

## 8. 一句话给 AI 的指令（安装）

请读取并严格执行 `INSTALL_FOR_AI.md` 的 Windows 首次安装流程，不要改路径策略。执行后回传 validate JSON、生效路径、AGENTS 同步结果和触发词激活结果。

## 9. 一句话给 AI 的指令（更新）

请读取并严格执行 `INSTALL_FOR_AI.md` 的 Windows 更新流程（含 git pull + update + validate + AGENTS 同步），并回传完整结果。

## 10. 可选：Skill 一致性维护

如需处理多设备 skill 版本漂移，可使用：

```powershell
python scripts/skill_drift_check.py --repo-root .
python scripts/skill_sync.py --repo-root . --from repo --apply
python scripts/skill_sync.py --repo-root . --from local --apply
python scripts/role_skill_alignment_check.py --repo-root .
```
