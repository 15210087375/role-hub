# Habby GitHub 配置 Skill

这个 Skill 帮助自动化配置 Habby 企业版 GitHub 环境。

## 🚀 关键优化

**后台运行 + 立即打开浏览器**：避免 `gh auth login` 阻塞导致的等待卡顿，提供流畅的用户体验。

## 文件结构

```
habby-github-setup/
├── SKILL.md                  # 主配置文件（Claude 自动读取）
├── TROUBLESHOOTING.md        # 故障排查指南
├── README.md                 # 本文件
└── scripts/
    └── verify-setup.sh       # 诊断验证脚本
```

## 自动触发条件

当用户提到以下内容时，Claude 会自动使用此 Skill：
- "配置 GitHub 企业版"
- "habby.ghe.com"
- "gh 登录问题"
- "GitHub Enterprise"
- "配置 gh"

## 手动测试

你可以通过以下方式测试此 Skill：

```
帮我配置 Habby 企业版 GitHub
```

或

```
我需要配置 habby.ghe.com 的访问
```

## 诊断工具

如果配置出现问题，运行诊断脚本：

```bash
.claude/skills/habby-github-setup/scripts/verify-setup.sh
```

## 适用范围

- **系统**: macOS（优先）
- **工具**: gh CLI, git, Homebrew
- **目标**: habby.ghe.com

## 维护

如果企业版 GitHub 配置流程发生变化，请更新：
1. `SKILL.md` - 主流程
2. `TROUBLESHOOTING.md` - 新增问题解决方案
3. `scripts/verify-setup.sh` - 验证逻辑

---

**最后更新**: 2025-12-15
