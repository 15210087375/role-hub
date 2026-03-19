---
name: skills-hub-client
description: |
  Search and download Claude Code skills from Skills Hub. 
  Triggers: "find skill", "search skills", "download skill", "install skill", 
  "skills hub", "skill marketplace", "搜索skill", "下载skill", "安装skill"
---

# Skills Hub Client

Interactive workflow for searching, selecting, and installing skills.

## Workflow

### Step 1: Search

```bash
python3 scripts/search_skills.py "<keyword>" --limit 10
```

### Step 2: Let User Select

Use `question` tool with search results:

```yaml
header: "搜索结果"
question: "找到以下 skills，请选择要安装的："
multiple: false
options:
  - label: "[Skill Name] (vX.X.X)"
    description: "[Description] | 下载: N"
  # ... for each result
```

Store selected skill's `ID`, `name`, `slug`.

### Step 3: Analyze Local Skills (Agent Intelligence)

**Semantic analysis, not file matching.**

1. Get all installed skills with metadata:
```bash
python3 scripts/list_local_skills.py
```

Output shows each skill's `name`, `folder`, and `description`.

2. Compare against the skill user wants to install:

| Conflict | Criteria | Action |
|----------|----------|--------|
| **Exact** | Same name/folder | Ask: update or skip |
| **Similar** | Descriptions overlap in functionality | Warn, ask to proceed |
| **None** | No overlap | Proceed |

Example: User wants `grok-mcp-installer` ("install Grok MCP")
- Sees `opencode-mcp-installer` ("install MCP servers in OpenCode")
- Both install MCPs → **Similar**, warn user

### Step 4: Ask User About Conflicts

**Exact match:**
```yaml
header: "Skill 已存在"
question: "已安装 [skill-name]，如何处理？"
options:
  - label: "更新到最新版本"
    description: "覆盖现有版本"
  - label: "跳过"
    description: "保留现有版本"
```

**Similar function:**
```yaml
header: "发现类似 Skill"
question: "已安装类似的 [similar-skill]，是否继续？"
options:
  - label: "继续安装"
    description: "两个 skill 共存"
  - label: "取消"
    description: "不安装"
```

### Step 5: Install

```bash
python3 scripts/download_skill.py <skill_id> --output ~/.claude/skills/ --force
```

### Step 6: Report

Read the installed skill's SKILL.md frontmatter and tell user:
- Skill name
- What it does (from description)
- Trigger phrases (if mentioned in description)

### Step 7: Offer Immediate Use (Based on Metadata)

After installation, check for `.skill-meta.json` in the installed skill directory.

**Read metadata:**
```bash
cat ~/.claude/skills/<skill-name>/.skill-meta.json 2>/dev/null || echo "{}"
```

**Decision logic:**

| Condition | Action |
|-----------|--------|
| File missing or invalid JSON | Skip auto-run, end normally |
| `runAfterInstall` is `false` or missing | Skip auto-run, end normally |
| `runAfterInstall` is `true` | Ask user (see below) |

**If `runAfterInstall` is `true`**:

Ask user with `question` tool:

```yaml
header: "安装完成"
question: "[skill-name] 已安装成功！作者建议安装后立即使用，是否继续？"
options:
  - label: "是，立即使用"
    description: "现在执行该 skill 完成配置"
  - label: "否，稍后手动触发"
    description: "可以用 /[skill-name] 触发"
```

**If user selects "是，立即使用"**:

Invoke the `skill` tool to load and execute the newly installed skill:

```
skill(name="<skill-name>")
```

The newly loaded skill takes over and executes its workflow.

**If user declines or `runAfterInstall` is false/missing**:

End with report. User can trigger later with `/[skill-name]`.

## Rollback

If an updated skill has issues, rollback to the previous version.

### List Available Backups

```bash
python3 scripts/rollback_skill.py
```

### Rollback a Skill

```bash
python3 scripts/rollback_skill.py <skill-name> -y
```

This will:
1. Remove current version
2. Extract backup
3. Delete backup file

## Scripts

| Script | Purpose |
|--------|---------|
| `search_skills.py` | Search hub: `"<keyword>"`, `--tags`, `--sort`, `--limit` |
| `list_local_skills.py` | List installed skills with name + description |
| `download_skill.py` | Download: `<id>`, `--output`, `--force`, `--no-extract` |
| `check_updates.py` | Check for available updates (requires metadata) |
| `bootstrap_metadata.py` | Create metadata for manually installed skills |
| `rollback_skill.py` | Rollback: `<skill-name>`, `-y` (skip confirm), `-l` (list) |

## Bootstrapping (First-time Setup)

Skills installed manually (not via this client) lack `.skill-meta.json` and can't check for updates.

To fix, run:
```bash
python3 scripts/bootstrap_metadata.py
```

This searches Skills Hub for matching skills and creates metadata.

## .skill Format

ZIP archive → extract to `~/.claude/skills/<name>/` to use.
