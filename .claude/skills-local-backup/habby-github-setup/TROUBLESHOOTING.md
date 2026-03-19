# Habby GitHub 配置故障排查指南

本文档提供常见问题的快速修复方法。

---

## 目录

- [安装相关问题](#安装相关问题)
- [登录相关问题](#登录相关问题)
- [网络相关问题](#网络相关问题)
- [验证相关问题](#验证相关问题)
- [诊断信息收集](#诊断信息收集)

---

## 安装相关问题

### 问题 A：装完 gh 但终端找不到命令

**症状：**
```bash
$ gh --version
-bash: gh: command not found
```

**解决方案 1：重启终端**

关闭当前终端窗口，重新打开：

```bash
gh --version
```

**解决方案 2：手动刷新 shell 环境（M 系列 Mac）**

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
hash -r
gh --version
```

**解决方案 3：检查 PATH**

```bash
echo $PATH
```

应该包含：
- M 系列：`/opt/homebrew/bin`
- Intel：`/usr/local/bin`

如果不包含，执行：

```bash
# M 系列
export PATH="/opt/homebrew/bin:$PATH"

# Intel
export PATH="/usr/local/bin:$PATH"
```

---

### 问题 B：Homebrew 不存在或无法使用

**症状：**
```bash
$ brew --version
-bash: brew: command not found
```

**解决方案：安装 Homebrew**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

安装后，根据提示配置 PATH（M 系列必需）：

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

验证：

```bash
brew --version
```

---

### 问题 C：brew install gh 下载超时或 403 错误

**症状：**
```
Error: Failed to download resource "gh"
Error: Download failed on Homebrew
```

**解决方案 1：检查网络**

- 连接稳定的网络
- 如果在公司网络，可能需要连接 VPN

**解决方案 2：重试安装**

```bash
brew update
brew install gh
```

**解决方案 3：使用国内镜像（可选）**

如果持续失败，可以考虑配置 Homebrew 镜像源。

---

## 登录相关问题

### 问题 D：gh auth login 连接超时

**症状：**
```
error connecting to habby.ghe.com
failed to authenticate: connect timeout
```

**解决方案 1：检查网络连通性**

```bash
ping habby.ghe.com
curl -I https://habby.ghe.com
```

**解决方案 2：检查 VPN**

企业版 GitHub 可能需要 VPN 连接，确认：
- VPN 已连接
- 浏览器能打开 https://habby.ghe.com

**解决方案 3：检查代理设置**

```bash
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

如果设置了代理但无法连接，尝试临时取消：

```bash
unset HTTP_PROXY
unset HTTPS_PROXY
gh auth login --hostname habby.ghe.com
```

---

### 问题 E：gh auth login 卡住，等待很久

**症状：**
- 执行 `gh auth login` 后命令卡住
- 等待很久才有反应
- 浏览器迟迟不打开或根本不打开

**原因：**
`gh auth login` 是阻塞命令，会等待整个授权流程完成才返回。gh 的自动打开浏览器功能很慢且不可靠。

**解决方案：使用后台运行 + 立即打开浏览器（推荐）**

**步骤 1：后台运行 gh auth login**

```bash
# 使用后台运行（在 agent 中设置 run_in_background: true）
gh auth login --hostname habby.ghe.com --web --git-protocol https
```

**步骤 2：立即打开浏览器（不等待）**

```bash
open "https://habby.ghe.com/login/device"
```

**步骤 3：查看后台输出获取 device code**

如果需要查看 device code：
```bash
# 在 Claude Code 中使用 BashOutput tool
# 或者在终端中查看后台任务输出
```

**为什么这样做：**
- ✅ 命令在后台运行，不阻塞 agent
- ✅ 浏览器立即打开，用户体验流畅
- ✅ 不依赖 gh 的慢速自动打开功能

⚠️ **这是 Skill 中的强制步骤！**

---

### 问题 F：浏览器授权流程不清楚

**症状：**
- 浏览器打开了但不知道怎么操作
- 不确定在哪里输入 device code
- 不清楚授权步骤

**完整的浏览器授权步骤：**

**步骤 1：获取 device code**
```
查看终端输出，找到类似这样的内容：
! First copy your one-time code: 6F91-86D6

复制验证码：6F91-86D6
```

**步骤 2：浏览器操作流程**

1. **初始页面（Device Activation）**
   - 页面标题：Device Activation
   - 点击绿色的 **"Continue"** 按钮

2. **输入验证码页面**
   - 会看到一个输入框
   - 粘贴刚才复制的验证码（例如：6F91-86D6）
   - 点击 **"Continue"** 按钮

3. **授权请求页面**
   - 页面显示：Authorize GitHub CLI
   - 列出请求的权限（repo, workflow, read:org 等）
   - 点击绿色的 **"Authorize github-enterprise"** 按钮

4. **授权成功**
   - 页面显示："Congratulations, you're all set!"
   - 或者页面自动关闭/跳转

**如果卡在某个步骤：**
- 刷新页面重试
- 确认 device code 没有过期（15 分钟有效期）
- 检查是否已登录企业版 GitHub（需要先 SSO 登录）

---

### 问题 G：device code 输入后报错

**症状：**
```
Invalid device code
Device code expired
```

**解决方案：重新开始登录流程**

Device code 有时效限制（通常 15 分钟）：

```bash
# 取消当前登录（Ctrl+C）
gh auth login --hostname habby.ghe.com
```

获得新的 device code 后立即完成授权。

---

### 问题 H：identity 页面显示未开通

**症状：**
- identity.habby.com/github 页面显示"未开通"
- 或没有显示 GitHub Enterprise 信息

**解决方案：联系管理员开通**

企业版 GitHub 需要管理员为用户开通权限：

1. 确认用户已用公司 SSO 登录 identity
2. 检查页面是否有"开启/绑定 GitHub Enterprise"按钮
3. 如果没有，联系 IT 或平台管理员开通权限

⚠️ **在开通完成前，不要执行 gh auth login，一定会失败！**

---

### 问题 I：gh auth login 成功但 git 操作仍需密码

**症状：**
```bash
$ git clone https://habby.ghe.com/habby/repo.git
Username for 'https://habby.ghe.com':
```

**原因：**
未配置 git 使用 gh 作为 credential helper

**解决方案：**

```bash
gh auth setup-git --hostname habby.ghe.com
```

验证配置：

```bash
git config --global credential.helper
```

应该包含 `gh`。

---

## 网络相关问题

### 问题 J：无法访问 habby.ghe.com

**症状：**
```bash
$ curl https://habby.ghe.com
curl: (6) Could not resolve host: habby.ghe.com
```

**解决方案清单：**

1. **检查 DNS 解析**
   ```bash
   nslookup habby.ghe.com
   ```

2. **检查 VPN 连接**
   - 确认 VPN 已连接
   - 尝试断开重连

3. **检查代理设置**
   ```bash
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   echo $NO_PROXY
   ```

4. **测试浏览器访问**
   ```bash
   open "https://habby.ghe.com"
   ```

   如果浏览器能打开但 CLI 不行，可能是代理配置问题。

---

### 问题 K：代理环境下的配置

**症状：**
```
fatal: unable to access 'https://habby.ghe.com/...': SSL certificate problem
```

**解决方案 1：配置 git 代理**

```bash
# HTTP 代理
git config --global http.proxy http://proxy-server:port

# HTTPS 代理
git config --global https.proxy https://proxy-server:port
```

**解决方案 2：针对企业版配置**

```bash
git config --global http.https://habby.ghe.com.proxy http://proxy-server:port
```

**解决方案 3：信任企业 SSL 证书（仅在必要时）**

```bash
git config --global http.sslVerify false
```

⚠️ **注意：关闭 SSL 验证有安全风险，仅在企业内网环境使用！**

---

## 组织成员相关问题

### 问题 L：不是 habby 组织成员

**症状：**
```bash
$ git clone https://habby.ghe.com/habby/repo.git
fatal: repository 'https://habby.ghe.com/habby/repo.git/' not found
```

或者验证脚本显示：
```
✗ 你不是 habby 组织的成员
```

**原因：**
即使 gh 登录成功，如果你不是 habby 组织成员，也无法访问组织下的仓库。

**检查方法：**

```bash
# 方法 1：检查组织成员资格
gh api --hostname habby.ghe.com orgs/habby/memberships/$(gh api --hostname habby.ghe.com user --jq '.login')

# 方法 2：运行验证脚本
.claude/skills/habby-github-setup/scripts/verify-setup.sh
```

**预期输出：**
- 如果是成员：返回 membership 信息，`"state": "active"`
- 如果不是成员：返回 `404 Not Found`

**解决方案：**

1. **获取你的用户名**
   ```bash
   gh api --hostname habby.ghe.com user --jq '.login'
   ```

2. **联系运维同事**

   提供以下信息：
   - 企业版 GitHub 用户名：`<你的用户名>`
   - 需要加入的组织：`habby`

3. **等待添加完成后验证**
   ```bash
   # 验证组织成员资格
   gh api --hostname habby.ghe.com orgs/habby/memberships/$(gh api --hostname habby.ghe.com user --jq '.login')
   ```

   应该看到 `"state": "active"`

4. **测试仓库访问**
   ```bash
   git ls-remote https://habby.ghe.com/habby/hello-world.git
   ```

⚠️ **重要：在成为组织成员之前，所有对组织仓库的访问都会失败！**

---

### 问题 M：组织邀请待接受

**症状：**
验证脚本显示：
```
⚠ 你的组织成员状态为: pending
  可能需要接受组织邀请
```

**原因：**
你已被添加到组织，但还未接受邀请。

**解决方案：**

1. **查看待处理邀请**
   ```bash
   open "https://habby.ghe.com/orgs/habby"
   ```

2. **或通过 CLI 查看**
   ```bash
   gh api --hostname habby.ghe.com user/memberships/orgs
   ```

3. **接受邀请**
   - 在企业版 GitHub 页面接受邀请
   - 或使用命令行：
   ```bash
   gh api --hostname habby.ghe.com -X PATCH user/memberships/orgs/habby -f state=active
   ```

4. **验证状态**
   ```bash
   gh api --hostname habby.ghe.com orgs/habby/memberships/$(gh api --hostname habby.ghe.com user --jq '.login') --jq '.state'
   ```

   应该显示 `active`

---

## 验证相关问题

### 问题 N：gh auth status 显示未登录

**症状：**
```bash
$ gh auth status --hostname habby.ghe.com
You are not logged into any GitHub hosts
```

**解决方案：检查配置文件**

```bash
cat ~/.config/gh/hosts.yml
```

应该包含 `habby.ghe.com` 条目。如果没有，重新登录：

```bash
gh auth login --hostname habby.ghe.com
```

---

### 问题 O：gh api user 返回 401 错误

**症状：**
```bash
$ gh api --hostname habby.ghe.com user
gh: Bad credentials (HTTP 401)
```

**解决方案 1：Token 已过期，重新登录**

```bash
gh auth refresh --hostname habby.ghe.com
```

如果失败，重新登录：

```bash
gh auth logout --hostname habby.ghe.com
gh auth login --hostname habby.ghe.com
```

**解决方案 2：检查 Token scopes**

```bash
gh auth status --hostname habby.ghe.com
```

确认 Token 包含必要的 scopes（`repo`, `read:org`, `workflow`）。

---

### 问题 Q：Token 缺少 workflow 权限

**症状：**
```bash
$ gh auth status --hostname habby.ghe.com
Token scopes: 'gist', 'read:org', 'repo'
# 缺少 'workflow' scope
```

或者在使用 GitHub Actions 相关功能时报权限错误。

**原因：**
初次登录时可能没有请求 workflow 权限，导致无法操作 GitHub Actions。

**解决方案：刷新权限并添加 workflow scope**

```bash
gh auth refresh --hostname habby.ghe.com --scopes workflow
```

这会：
1. 在浏览器中打开授权页面
2. 请求添加 workflow 权限
3. 保留现有的其他权限

**验证：**

```bash
gh auth status --hostname habby.ghe.com
```

确认输出中 Token scopes 包含 `workflow`：
```
Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

**替代方案：完整重新授权所有权限**

如果需要确保所有权限都正确，可以重新登录并一次性请求所有权限：

```bash
gh auth logout --hostname habby.ghe.com
gh auth login --hostname habby.ghe.com --web --git-protocol https --scopes repo,read:org,workflow
```

---

### 问题 P：git ls-remote 报认证错误

**症状：**
```bash
$ git ls-remote https://habby.ghe.com/habby/repo.git
fatal: Authentication failed
```

**解决方案：重新配置 git credential helper**

```bash
gh auth setup-git --hostname habby.ghe.com
```

验证：

```bash
git credential-cache exit
git ls-remote https://habby.ghe.com/habby/repo.git
```

---

## 诊断信息收集

如果上述方法都无法解决问题，收集以下诊断信息：

### 系统信息

```bash
# 系统版本
sw_vers

# 芯片架构
uname -m

# Shell 类型
echo $SHELL
```

### 工具版本

```bash
# Homebrew
brew --version

# gh CLI
gh --version
which gh

# git
git --version
which git
```

### 配置信息

```bash
# PATH
echo $PATH

# gh 认证状态
gh auth status --hostname habby.ghe.com

# git 配置
git config --global --list | grep -E "(credential|proxy)"

# gh 配置文件
cat ~/.config/gh/hosts.yml
```

### 网络连通性

```bash
# DNS 解析
nslookup habby.ghe.com

# HTTPS 连接
curl -I https://habby.ghe.com

# 代理设置
env | grep -i proxy
```

---

## 快速诊断脚本

运行同目录下的验证脚本收集诊断信息：

```bash
.claude/skills/habby-github-setup/scripts/verify-setup.sh
```

将输出结果提供给支持人员。

---

## 仍然无法解决？

如果问题持续：

1. **检查是否为已知问题**
   - 查看企业版 GitHub 状态页面
   - 询问同事是否遇到相同问题

2. **联系内部支持**
   - IT 支持团队
   - 平台管理员

3. **提供诊断信息**
   - 上述所有诊断命令的输出
   - 错误信息的完整截图
   - 操作步骤的详细描述

---

## 常见坑总结（快速参考）

| 问题 | 快速修复 |
|------|---------|
| gh 找不到命令 | 重启终端或配置 PATH |
| brew 下载失败 | 检查网络/VPN |
| gh 登录超时 | 检查 VPN，手动 open 授权页 |
| identity 未开通 | 联系管理员开通权限 |
| **不是组织成员** | **联系运维添加到 habby 组织** |
| 组织邀请待接受 | 接受邀请或 `gh api -X PATCH user/memberships/orgs/habby -f state=active` |
| git 需要密码 | `gh auth setup-git --hostname habby.ghe.com` |
| API 401 错误 | `gh auth refresh --hostname habby.ghe.com` |
| Token 缺少 workflow 权限 | `gh auth refresh --hostname habby.ghe.com --scopes workflow` |
| M 系列 PATH | 配置 brew shellenv |
| 代理问题 | 配置 git/gh 代理或临时取消 |

---

**最后更新：** 2025-12-15
