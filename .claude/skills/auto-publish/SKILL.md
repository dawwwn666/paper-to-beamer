---
name: auto-publish
description: 自动检测本地改动，commit到GitHub，并同步更新README和GitHub Pages。手动触发。
argument-hint: "[optional: commit message]"
trigger-phrases: ["发布到github", "自动发布", "publish to github", "auto publish"]
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]
---

# Auto-Publish to GitHub

自动检测本地改动，智能生成 commit message，推送到 GitHub，并同步更新 README.md 和 docs/index.html。

## 工作流程

```
检测改动 → 排除私人文件 → 生成commit message
         → 提取关键更新 → 更新README/Pages → commit → push
```

## Steps

### 1. 检测改动

```bash
git status --short
git diff --stat
```

**排除规则（不提交）：**
- `Slides/*.tex` — 用户私人论文内容
- `Slides/*.pdf` — 编译产物
- `Papers/*.pdf` — 用户论文PDF
- `Figures/*/page-*.png` — 临时渲染图片
- `Figures/*/page*_*.png` — 临时裁剪图片
- `.claude/state/` — 本地状态
- `.claude/settings.local.json` — 本地配置

**允许提交：**
- `.claude/skills/` — 技能更新
- `scripts/` — 脚本更新
- `Preambles/` — 主题文件
- `CLAUDE.md` — 配置更新
- `README.md` — 文档更新
- `docs/index.html` — Pages更新
- `.gitignore` — 规则更新

### 2. 分析改动类型

根据 `git diff --name-only` 判断改动类型：

| 文件模式 | 改动类型 | Commit前缀 |
|---------|---------|-----------|
| `.claude/skills/*/SKILL.md` | 新增/修改技能 | `feat(skill):` 或 `fix(skill):` |
| `scripts/*.py` | 脚本更新 | `feat(script):` 或 `fix(script):` |
| `Preambles/*.sty` | 主题更新 | `style(theme):` |
| `CLAUDE.md` | 配置更新 | `chore(config):` |
| `README.md` | 文档更新 | `docs:` |
| `docs/index.html` | Pages更新 | `docs(pages):` |
| 多种类型 | 混合改动 | `chore:` |

### 3. 生成 Commit Message

如果 `$ARGUMENTS` 提供了 message，直接使用。否则自动生成：

**格式：**
```
<type>(<scope>): <subject>

<body>
- 详细改动1
- 详细改动2

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

**示例：**
```
feat(skill): Add auto-publish skill for GitHub workflow

- Auto-detect local changes and exclude private files
- Generate semantic commit messages
- Sync updates to README and GitHub Pages
- Support manual trigger via /auto-publish

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

### 4. 提取关键更新（用于README/Pages）

如果改动包含新功能或重要修改，提取关键信息：

**新增技能：**
- 技能名称
- 功能描述
- 触发命令

**脚本更新：**
- 脚本名称
- 新增功能

**主题更新：**
- 主题名称
- 视觉改进

### 5. 更新 README.md（如果需要）

**触发条件：**
- 新增 skill
- 修改 skill 的核心功能
- 新增 script
- 修改工作流程

**更新位置：**
- `## 技能` 表格 — 新增技能行
- `## 工作流程` — 如果流程改变
- `## 环境要求` — 如果依赖改变

**不更新的情况：**
- 仅修复 bug
- 仅调整内部逻辑
- 仅更新文档

### 6. 更新 docs/index.html（如果需要）

**触发条件：** 与 README.md 相同

**更新位置：**
- `<h2>技能</h2>` 下的表格
- `<h2>工作流程</h2>` 下的流程图（如果改变）

### 7. Stage 文件

```bash
git add .claude/skills/ scripts/ Preambles/ CLAUDE.md README.md docs/index.html .gitignore
```

**验证排除：**
```bash
git status --short | grep -E "(Slides/.*\.tex|Papers/.*\.pdf|Figures/.*/page)"
```

如果上述命令有输出，说明有私人文件被误加入，需要 `git reset` 移除。

### 8. Commit

```bash
git commit -m "$(cat <<'EOF'
[生成的commit message]
EOF
)"
```

### 9. Push

```bash
git pull --rebase origin main
git push origin main
```

### 10. 报告结果

输出：
- Commit hash
- 改动文件数
- README/Pages 是否更新
- GitHub 链接

## 示例

### 示例 1：新增技能

**改动：**
- 新增 `.claude/skills/auto-publish/SKILL.md`

**执行：**
```bash
/auto-publish
```

**结果：**
- Commit message: `feat(skill): Add auto-publish skill for GitHub workflow`
- README 新增一行：`| /auto-publish | 自动发布到GitHub并更新文档 |`
- Pages 新增一行：`<tr><td><code>/auto-publish</code></td><td>自动发布到GitHub并更新文档</td></tr>`
- Push 到 GitHub

### 示例 2：修复 bug

**改动：**
- 修改 `.claude/skills/paper-to-beamer/SKILL.md` 第 87 行

**执行：**
```bash
/auto-publish "Fix table extraction error handling"
```

**结果：**
- Commit message: `fix(skill): Fix table extraction error handling`
- README/Pages **不更新**（仅 bug 修复）
- Push 到 GitHub

### 示例 3：更新主题

**改动：**
- 修改 `Preambles/beamerthemeNankaiBeamer.sty`

**执行：**
```bash
/auto-publish
```

**结果：**
- Commit message: `style(theme): Update NankaiBeamer color scheme`
- README/Pages **不更新**（主题改动不影响用户文档）
- Push 到 GitHub

## 安全检查

**在 commit 前必须验证：**

1. **没有私人文件：**
   ```bash
   git diff --cached --name-only | grep -E "(Slides/.*\.tex|Papers/.*\.pdf)"
   ```
   如果有输出 → 报错并停止

2. **没有敏感信息：**
   ```bash
   git diff --cached | grep -iE "(password|token|secret|api_key)"
   ```
   如果有输出 → 警告用户

3. **README/Pages 语法正确：**
   - README.md 表格对齐
   - index.html 标签闭合

## Error Handling

| 错误 | 处理 |
|------|------|
| 没有改动 | 提示 "No changes to commit" |
| 私人文件被加入 | 自动 `git reset`，重新 stage |
| Push 冲突 | 自动 `git pull --rebase`，重试 |
| README 更新失败 | 跳过 README，仅 commit 其他文件 |
| Pages 更新失败 | 跳过 Pages，仅 commit 其他文件 |

## 输出格式

```
✓ 检测到 3 个文件改动
✓ 排除私人文件：Slides/test.tex
✓ 生成 commit message
✓ 更新 README.md（新增技能）
✓ 更新 docs/index.html（新增技能）
✓ Commit: abc1234 "feat(skill): Add auto-publish skill"
✓ Push 成功

GitHub: https://github.com/dawwwn666/paper-to-beamer/commit/abc1234
```
