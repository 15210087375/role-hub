---
name: habby-github-setup
description: 配置 Habby 企业版 GitHub 环境（habby.ghe.com）。当用户需要配置企业版 GitHub、遇到 gh 登录问题、提到 habby.ghe.com 或需要设置 GitHub Enterprise 时使用此 Skill。
allowed-tools: Bash, AskUserQuestion, Read
---

# Habby 企业版 GitHub 配置助手

这个 Skill 帮助你配置 Habby 企业版 GitHub 环境，确保 gh CLI 和 git 能正确连接到企业版服务器。

## 目标环境

- **企业版地址**：`https://habby.ghe.com/habby`
- **Hostname**：`habby.ghe.com`
- **支持系统**：macOS（优先）
- **工具**：gh CLI、git

---

## ⚠️ 关键优化要求（必读！）

**在阶段 3 执行 `gh auth login` 时：**

```
🚨 必须使用 Bash tool 的 run_in_background: true 参数！
🚨 必须自动提取 device code 并写入粘贴板！
```

**为什么：**
- `gh auth login` 是阻塞命令，会等待 30+ 秒
- 不后台运行 = agent 卡住，无法打开浏览器
- 后台运行 + 自动提取 = 用户体验最佳

**完整的优化流程：**

**第 1 步：后台启动登录**
```
Tool: Bash
Parameters:
  command: "gh auth login --hostname habby.ghe.com --web --git-protocol https"
  run_in_background: true    ← 必须！
  description: "启动 GitHub 登录"
```

**第 2 步：等待并提取 device code**
```bash
# 等待 gh 生成输出
sleep 2

# 使用 TaskOutput 获取后台输出并提取 device code
# 使用正则：! First copy your one-time code: ([A-Z0-9]{4}-[A-Z0-9]{4})
# 最多重试 3 次，每次间隔 1 秒
```

**第 3 步：写入粘贴板并打开浏览器**
```bash
# 将 device code 写入系统粘贴板（-n 参数避免添加换行符）
echo -n "DEVICE_CODE" | pbcopy

# 立即打开浏览器
open "https://habby.ghe.com/login/device"
```

**第 4 步：告诉用户验证码已复制**
```
✅ 登录流程已启动！
🔑 你的验证码是：XXXX-XXXX
✨ 验证码已自动复制到粘贴板，直接 Cmd+V 粘贴即可！
```

---

## 配置流程

### 阶段 0：开始前的说明

在开始配置前，向用户说明：
- 这是配置 Habby 企业版 GitHub 的完整流程
- 需要浏览器交互和用户确认
- 整个流程包含 5 个阶段，每个阶段都有验证

---

### 阶段 1：检查并安装 gh CLI

#### 1.1 检查 gh 是否已安装

```bash
gh --version
```

**判断：**
- 能看到版本号 → 跳到阶段 2
- `command not found` → 继续 1.2

#### 1.2 安装 gh（仅 macOS，使用 Homebrew）

**首先检查 Homebrew：**

```bash
brew --version
```

**如果 Homebrew 不存在，安装它：**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Apple Silicon (M 系列) 需要配置 PATH：**

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**安装 gh：**

```bash
brew install gh
```

**验证安装：**

```bash
gh --version
which gh
```

**预期输出：**
- `gh version x.y.z`
- M 系列：`/opt/homebrew/bin/gh`
- Intel：`/usr/local/bin/gh`

⚠️ **如果这一步失败，查看 TROUBLESHOOTING.md**

---

### 阶段 2：预检查 - 验证企业版账号已开通（关键！）

⚠️ **这是最容易被忽略但最关键的步骤！**

在执行 `gh auth login` 之前，必须确认企业版 GitHub 账号已为用户开通。

#### 2.1 打开 identity 检查页面

**macOS 执行：**

```bash
open "https://identity.habby.com/github"
```

#### 2.2 使用 AskUserQuestion 确认开通状态

询问用户：

```
你在 identity.habby.com/github 页面上看到了什么？

选项 1：已开通 - 页面显示"GitHub Enterprise 已开通"或显示账号信息
选项 2：未开通 - 页面显示需要开通或报错
选项 3：无法访问 - 页面无法打开或需要 VPN
```

**根据用户回答：**
- **已开通** → 继续阶段 3
- **未开通** → 引导用户联系管理员开通企业版权限，**暂停流程**
- **无法访问** → 检查网络/VPN 配置，查看 TROUBLESHOOTING.md

---

### 阶段 3：登录企业版 GitHub

⚠️ **关键优化：使用后台运行 + 自动提取 device code + 写入粘贴板**

#### 3.1 启动登录流程（后台运行）

⚠️ **强制要求：必须使用 Bash tool 的 `run_in_background: true` 参数！**

**第 1 步：执行以下 Bash tool 调用**

```
Tool: Bash
Parameters:
  command: "gh auth login --hostname habby.ghe.com --web --git-protocol https"
  run_in_background: true    ← 必须设置为 true！
  description: "启动 Habby GitHub 登录流程"
```

**命令参数说明：**
- `--hostname habby.ghe.com` - 指定企业版域名
- `--web` - 使用浏览器认证（非交互式）
- `--git-protocol https` - 使用 HTTPS 协议

**为什么必须后台运行：**
- ❌ 如果不设置 `run_in_background: true`，命令会阻塞 30+ 秒
- ❌ Agent 无法执行后续的命令
- ✅ 设置后台运行，agent 可以立即提取 device code 并打开浏览器

**保存任务 ID**：记录返回的任务 ID，后续步骤需要用它获取输出

#### 3.2 等待并提取 Device Code

**第 2 步：等待 gh 生成 device code**

```bash
sleep 2
```

**第 3 步：使用 TaskOutput 工具获取后台任务输出**

⚠️ **重试机制：最多重试 3 次，每次间隔 1 秒，直到成功提取 device code**

```
Tool: TaskOutput
Parameters:
  task_id: <第 1 步返回的任务 ID>
  block: false
  timeout: 5000
```

**第 4 步：从输出中提取 device code**

在输出中查找这样的行：
```
! First copy your one-time code: XXXX-XXXX
```

使用正则表达式提取：`! First copy your one-time code: ([A-Z0-9]{4}-[A-Z0-9]{4})`

**提取逻辑：**
- 如果成功提取到 device code → 继续步骤 3.3
- 如果未找到 → 等待 1 秒后重试（最多重试 3 次）
- 如果 3 次后仍未找到 → 报错并停止流程

⚠️ **必须成功提取 device code 才能继续！** 用户明确表示不需要降级方案。

#### 3.3 写入粘贴板并打开浏览器

**第 5 步：将 device code 写入 macOS 系统粘贴板**

```bash
echo -n "XXXX-XXXX" | pbcopy
```

> 将 `XXXX-XXXX` 替换为从步骤 3.2 提取到的实际 device code
>
> ⚠️ **必须使用 `-n` 参数**：避免在末尾添加换行符，否则在 GitHub 页面无法正常粘贴

**第 6 步：立即打开浏览器**

```bash
open "https://habby.ghe.com/login/device"
```

⚠️ **关键规则：**
- 在写入粘贴板后**立即**执行 open 命令
- **不要等待** gh 的其他输出
- 浏览器会打开授权页面，等待用户粘贴 device code

#### 3.4 指导用户完成浏览器授权

**第 7 步：告诉用户详细操作步骤**

在 Agent 的消息中输出（用户可见）：

```
验证码: XXXX-XXXX （已自动复制到粘贴板）

请在打开的浏览器页面中完成以下步骤：
  1) 点击 "Continue" 按钮
  2) 粘贴验证码（Cmd+V）或手动输入
  3) 点击 "Continue" 按钮
  4) 在授权页面点击 "Authorize github-enterprise"
  5) 等待显示"授权成功"

完成后请回到这里确认。
```

> 将 `XXXX-XXXX` 替换为实际的 device code

#### 3.5 使用 AskUserQuestion 等待用户完成

**第 8 步：询问用户确认**

使用 AskUserQuestion：

```
你在浏览器中完成授权了吗？

选项 1：已完成 - 页面显示授权成功
选项 2：遇到问题 - 描述具体错误
```

**根据用户回答：**
- **已完成** → 继续阶段 4
- **遇到问题** → 根据错误信息查看 TROUBLESHOOTING.md

**只有用户确认"已完成"后，才继续阶段 4。**

#### 3.4 Token（PAT）登录方式（仅在无浏览器时）

如果用户选择了 Token 方式：
- 需要创建 Personal Access Token (PAT)
- 至少包含 scopes：`repo`, `read:org`, `workflow`
- 按 gh 提示粘贴 Token

---

### 阶段 4：配置 git 与企业版集成

登录成功后，必须配置 git：

```bash
gh auth setup-git --hostname habby.ghe.com
```

这会配置 git 使用 gh 作为 credential helper，实现 HTTPS 免密拉取/推送。

---

### 阶段 5：最终验证（三项必过）

⚠️ **只有三项验证全部通过，才算配置成功！**

#### 5.1 验证 gh 登录状态

```bash
gh auth status --hostname habby.ghe.com
```

**预期输出关键点：**
- `Logged in to habby.ghe.com as <your-username>`
- `Git operations protocol: https`
- Token scopes 包含 `repo`, `workflow` 等

**如果缺少 workflow 权限：**
```bash
# 刷新权限并添加 workflow scope
gh auth refresh --hostname habby.ghe.com --scopes workflow
```
按照提示在浏览器中重新授权，然后重新验证

#### 5.2 验证 API 连通性

```bash
gh api --hostname habby.ghe.com user
```

**预期输出：**
- 返回 JSON 格式的用户信息
- 包含 `login`, `id`, `name` 等字段

#### 5.3 验证 habby 组织成员资格（关键！）

⚠️ **这是最容易被忽略的检查，但非常重要！**

```bash
gh api --hostname habby.ghe.com orgs/habby/members --jq '.[].login' | grep -q "$(gh api --hostname habby.ghe.com user --jq '.login')" && echo "✓ 你是 habby 组织成员" || echo "✗ 你不是 habby 组织成员"
```

**或者更简单的检查：**

```bash
gh api --hostname habby.ghe.com orgs/habby/memberships/$(gh api --hostname habby.ghe.com user --jq '.login')
```

**预期输出：**
- 如果是成员：返回 membership 信息（包含 `"state": "active"`）
- 如果不是成员：返回 404 错误

⚠️ **如果不是 habby 组织成员：**

告诉用户（用高亮/强调）：

```
🚨 重要：你还不是 habby 组织的成员！

即使 gh 登录成功，你也无法访问 habby 组织下的仓库。

请联系运维同事，将你的账号添加到 habby 组织中。

需要提供的信息：
- 你的企业版 GitHub 用户名：<username>
- 需要加入的组织：habby
```

**只有确认是组织成员后，才继续下一步验证。**

#### 5.4 验证 git 仓库访问

```bash
git ls-remote https://habby.ghe.com/habby/hello-world.git
```

> 将 `hello-world` 替换为用户实际需要访问的仓库名称

**预期输出：**
- 列出 refs（如 `refs/heads/main`）
- 不报认证错误

⚠️ **如果报 404 或权限错误：**
- 首先确认你已经是 habby 组织成员（5.3）
- 确认仓库名称正确
- 确认你有该仓库的访问权限

---

## 成功标准

✅ **配置成功的标志：**
1. `gh auth status` 显示已登录 habby.ghe.com
2. `gh api user` 返回用户信息
3. **你是 habby 组织成员**（新增）
4. `git ls-remote` 能访问企业版仓库

当三项全部通过时，告诉用户：

```
✅ Habby 企业版 GitHub 配置完成！

你现在可以：
- 使用 gh 命令操作企业版仓库
- 使用 git clone/pull/push 访问 habby.ghe.com 仓库
- 无需手动输入密码（通过 gh credential helper）
```

---

### 阶段 6：清理 - 删除本 skill ⚠️

**⚠️ 重要：此步骤在所有验证通过后执行**

由于本 skill 是一次性配置工具，配置完成后不再需要，应当删除以避免残留。

#### 6.1 确认所有验证已通过

在删除前，确认以下所有验证都已通过：
- ✅ `gh auth status` 显示已登录
- ✅ `gh api user` 返回用户信息
- ✅ habby 组织成员检查通过
- ✅ `git ls-remote` 能访问企业版仓库

#### 6.2 删除 skill 目录

使用 Bash 工具删除本 skill 的目录：

```bash
rm -rf .claude/skills/habby-github-setup
```

#### 6.3 确认删除成功

验证目录已被删除：

```bash
ls -la .claude/skills/
```

确认输出中不再包含 `habby-github-setup` 目录。

#### 6.4 告知用户

```
✅ Habby 企业版 GitHub 配置完成！

🧹 清理工作：
- 已删除一次性 skill：habby-github-setup
- 配置已保存在系统中，不需要保留此 skill

你现在可以：
- 使用 gh 命令操作企业版仓库
- 使用 git clone/pull/push 访问 habby.ghe.com 仓库
- 无需手动输入密码（通过 gh credential helper）
```

**注意：** 配置信息已保存在 gh CLI 中，即使删除 skill 也不影响使用。如果未来需要为其他机器配置，可以从参考项目重新获取此 skill。

---

## 故障排查

如果任何步骤失败，引导用户查看：
- 同目录下的 `TROUBLESHOOTING.md` 文件
- 或运行 `scripts/verify-setup.sh` 收集诊断信息

---

## 关键原则（agent 必须遵守）

1. ✅ **登录前必须检查 identity 页面**
   - 未开通就登录 = 100% 失败

2. ✅ **gh auth login 必须后台运行！**
   - **强制使用** `run_in_background: true` 参数
   - 否则命令会阻塞 30+ 秒，无法立即打开浏览器
   - 这是最关键的性能优化点

3. ✅ **必须自动提取并展示 device code**
   - 使用 TaskOutput 从后台任务中提取 device code
   - 使用正则表达式：`! First copy your one-time code: ([A-Z0-9]{4}-[A-Z0-9]{4})`
   - 有重试机制（最多 3 次，每次间隔 1 秒）
   - 必须成功提取才能继续，不提供降级方案

4. ✅ **必须将 device code 写入系统粘贴板**
   - 使用 `echo -n "code" | pbcopy` 写入 macOS 系统粘贴板（**必须加 -n 参数**）
   - -n 参数避免在末尾添加换行符，否则 GitHub 页面无法正常粘贴
   - 在消息中明确告诉用户"已自动复制到粘贴板"
   - 同时在消息中展示 device code，作为备份
   - 让用户直接 Cmd+V 粘贴，无需手动复制

5. ✅ **必须立即主动 open 授权页**
   - 在写入粘贴板后**立即**执行 open 命令
   - 不依赖 gh 的自动行为（慢且不可靠）
   - 避免用户等待

6. ✅ **使用 AskUserQuestion 确认用户操作**
   - identity 检查后确认
   - 浏览器授权后确认
   - 不要假设用户已完成操作

7. ✅ **四项验证必须全部通过**
   - gh auth status
   - gh api user
   - **habby 组织成员检查**（新增）
   - git ls-remote
   - 缺一不可

8. ✅ **遇到问题立即查看 TROUBLESHOOTING.md**
   - 不要猜测解决方案
   - 使用已知的修复方法

---

## 适用场景

这个 Skill 会在以下情况自动触发：
- 用户说"配置 GitHub 企业版"
- 用户提到 "habby.ghe.com"
- 用户遇到 gh 登录错误
- 用户说"配置 gh"或"GitHub Enterprise"
- 用户说"无法访问企业版仓库"

---

## 参考文档

- `TROUBLESHOOTING.md` - 常见问题快速修复
- `scripts/verify-setup.sh` - 自动验证脚本
