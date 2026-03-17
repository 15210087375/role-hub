# Role Hub 自动安装说明（给 AI 执行）

结论：可行。

你可以把本文件直接发给 AI，让它在新设备上按步骤执行安装。

---

## 0. 目标

把本仓库的角色系统安装到本机：

- `~/.config/opencode/roles`
- `~/.claude/skills`

并完成同步与校验。

安装脚本还会把 Role Hub runtime 规则自动写入本机 `~/.config/opencode/AGENTS.md`（幂等更新）。

---

## 1. AI 执行前提

请先确保：

1. 已安装 `git`
2. 已安装 `python`（macOS/Linux 可用 `python3`）
3. 机器可访问仓库：`https://github.com/15210087375/role-hub`
4. AI 具备执行终端命令权限

---

## 2. 给 AI 的执行指令（可直接复制）

请让 AI 严格按下列步骤执行，不要改路径规则：

1. 克隆仓库到当前用户目录。
2. 进入仓库根目录。
3. 根据系统执行安装脚本：
   - Windows: `roles/portable/install.ps1`
   - macOS/Linux: `roles/portable/install.sh`
4. 安装完成后执行校验命令。
5. 执行 AGENTS 规则同步命令并确认成功。
5. 输出最终检查结果：
   - 角色数量
   - 缺失 skill 数量
   - 是否可激活 `策划模式 / 编程模式 / 主理人模式`

---

## 3. 标准命令

### Windows (PowerShell)

```powershell
git clone https://github.com/15210087375/role-hub.git
cd role-hub
powershell -ExecutionPolicy Bypass -File roles/portable/install.ps1 -SourceRoot "$PWD"
python "$HOME/.config/opencode/roles/role_sync.py" validate
python "$HOME/.config/opencode/roles/role_agents_sync.py"
```

### macOS / Linux

```bash
git clone https://github.com/15210087375/role-hub.git
cd role-hub
bash roles/portable/install.sh --source-root "$PWD"
python3 "$HOME/.config/opencode/roles/role_sync.py" validate
python3 "$HOME/.config/opencode/roles/role_agents_sync.py"
```

---

## 4. 更新命令（后续使用）

### Windows

```powershell
cd role-hub
powershell -ExecutionPolicy Bypass -File roles/portable/update.ps1 -RepoRoot "$PWD"
```

### macOS / Linux

```bash
cd role-hub
bash roles/portable/update.sh --repo-root "$PWD"
```

---

## 5. 验收标准（AI 必须回传）

AI 执行后必须回传以下结果：

1. `role_sync.py validate` 的 JSON 输出全文。
2. `missing_skill_count` 必须为 `0`。
3. 说明已安装路径：
   - `~/.config/opencode/roles`
   - `~/.claude/skills`
4. 说明已同步 AGENTS：`~/.config/opencode/AGENTS.md`
5. 提醒你重启会话（让新 skill 列表生效）。

---

## 6. 常见问题

1. Python 命令不存在：
   - Windows 改用 `py`
   - macOS/Linux 确认 `python3`

2. PowerShell 策略拦截：
   - 使用 `-ExecutionPolicy Bypass`（文档命令已包含）

3. 新角色看不到：
   - 先跑 `role_sync.py sync`
   - 再重开会话

4. 私有仓库拉取失败：
   - 先登录 GitHub（`gh auth login`）

---

## 7. 让 AI 执行时的一句话提示词

你可以直接发这句话给 AI：

"请按仓库 `INSTALL_FOR_AI.md` 完整执行安装，严格使用文档命令，不要自行改路径。执行后回传 validate JSON、安装路径和触发词激活结果。"
