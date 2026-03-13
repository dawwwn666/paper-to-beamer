---
name: paper-to-beamer
description: Convert a research paper PDF into a Beamer presentation. Extracts tables, analyzes structure, generates .tex with NankaiBeamer theme, compiles, and fixes overflow.
argument-hint: "[PDF filename in Papers/ directory] [optional: number of slides, e.g. 10]"
trigger-phrases: ["paper to beamer", "论文转PPT", "制作课堂展示", "从论文生成PPT", "paper to slides"]
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Agent"]
---

# Paper-to-Beamer Workflow

Convert a research paper PDF into a complete Beamer presentation using the NankaiBeamer theme.

## Input

`$ARGUMENTS` = `[PDF filename] [optional slide count]`

Examples:
- `/paper-to-beamer paper.pdf` → ask user for slide count
- `/paper-to-beamer paper.pdf 15` → generate exactly 15 slides
- `/paper-to-beamer paper.pdf 8-12` → generate 8 to 12 slides

## Steps

### 1. Locate the PDF

```bash
ls Papers/
```

Confirm the file exists. If not found, list available PDFs and ask the user to clarify.

### 2. Ask for Slide Count (if not provided)

If no slide count is given in `$ARGUMENTS`, ask the user:

> 您希望生成多少页幻灯片？
> - 精简版（12-15页）：适合20-30分钟报告
> - 标准版（23-25页）：适合45分钟报告
> - 详细版（33-35页）：适合60分钟以上报告
> - 自定义：请输入具体页数

Use the answer to determine the slide count target (`TARGET_SLIDES`).

### 2.5. Ask for Generation Mode

**Always ask the user to choose generation mode:**

> 请选择生成模式：
> 1. **全自动生成** (auto) — 我根据论文内容和最佳实践自动生成（推荐）
> 2. **个性化定制** (custom) — 通过多轮对话确定重点和风格

Store the user's choice as `GEN_MODE` (default: `auto`).

### 2.6. Ask for Table Extraction Mode

**Always ask the user to choose a table extraction mode:**

> 请选择表格处理方式：
> 1. **全自动截图** (auto) — 使用 pdfplumber + pdftoppm 自动提取表格图片（默认）
> 2. **手动截图** (manual) — 您自己截图，我会告诉您需要截哪些表格
> 3. **纯文本提取** (text) — 我用 pdfplumber 提取表格数据，用 LaTeX 重新排版（无图片）

Store the user's choice as `TABLE_MODE` (default: `auto`).

**Slide count guidelines:**

| Target | Slides | Coverage |
|--------|--------|---------|
| 精简版 | 12-15 | 动机、数据、主要结果、结论 |
| 标准版 | 23-25 | 上述 + 文献、识别策略、稳健性、机制 |
| 详细版 | 33-35 | 上述 + 异质性、政策含义、附录 |

### 3. Extract Tables (mode-dependent)

#### If `TABLE_MODE == "auto"`:

```bash
python scripts/extract_tables.py "Papers/[FILENAME]"
python scripts/render_pages.py "Papers/[FILENAME]" 200
```

#### If `TABLE_MODE == "manual"`:

1. First, scan the PDF to identify tables:
```python
import pdfplumber
with pdfplumber.open("Papers/[FILENAME]") as pdf:
    for i, page in enumerate(pdf.pages, 1):
        tables = page.find_tables()
        if tables:
            print(f"Page {i}: {len(tables)} table(s)")
```

2. Tell the user:
> 我检测到以下页面有表格：
> - 第 X 页：Y 个表格
> - 第 Z 页：W 个表格
>
> 请您手动截图并保存到 `Figures/[BASENAME]_tables/` 文件夹，命名规范：
> - `table-1.png` — 第一个表格
> - `table-2.png` — 第二个表格
> - ...
>
> 截图建议：使用高 DPI（200+），PNG 格式，裁剪掉多余空白。
>
> 完成后请回复"完成"或"done"。

3. Wait for user confirmation before proceeding.

#### If `TABLE_MODE == "text"`:

Extract table data as text and store in JSON:
```bash
python scripts/extract_tables.py "Papers/[FILENAME]" --text-only
```

This will create `Figures/[BASENAME]_tables/tables_text.json` with raw table data.

### 4. Analyze Paper Structure

Read the PDF text to identify:
- Title, authors, journal/year
- Abstract (1-2 key sentences)
- Research question / hypothesis
- Data and sample
- Identification strategy
- Main results
- Robustness checks
- Conclusion / policy implications

```python
import pdfplumber
with pdfplumber.open("Papers/file.pdf") as pdf:
    text = "\n".join(p.extract_text() or "" for p in pdf.pages[:5])
print(text[:3000])
```

### 4.5. Customization Planning (if `GEN_MODE == "custom"`)

**If user chose custom mode, conduct multi-round planning dialogue:**

#### Round 1: Identify Focus Areas

Ask the user:
> 我已分析论文结构。请告诉我您希望在报告中：
> 1. **重点强调**哪些方面？（可多选）
>    - 理论贡献
>    - 识别策略的创新性
>    - 数据的独特性
>    - 实证结果的稳健性
>    - 政策含义
>    - 机制分析
> 2. **可以略谈**哪些部分？
> 3. **目标听众**是谁？（学术会议/课堂教学/政策制定者）

Store responses as `FOCUS_AREAS`, `SKIP_AREAS`, `AUDIENCE`.

#### Round 2: Content Prioritization

Based on `TARGET_SLIDES` and user's focus, propose a slide allocation:

> 根据您的需求，我建议以下幻灯片分配：
> - 动机与研究问题: X 页
> - 文献定位: Y 页
> - 数据: Z 页
> - 识别策略: W 页
> - 主要结果: V 页
> - [用户强调的重点]: U 页
> - 结论: T 页
>
> 是否需要调整？

Allow user to adjust allocation.

#### Round 3: Style Preferences

Ask:
> 展示风格偏好：
> 1. 表格展示：图片 / LaTeX重排 / 混合
> 2. 方程展示：完整数学公式 / 简化直觉解释 / 两者结合
> 3. 结果强调：用彩色框 / 用加粗 / 最小化格式
> 4. 是否需要动画效果？（不推荐学术报告）

Store as `STYLE_PREFS`.

#### Round 4: Final Outline Confirmation

Generate and present detailed outline:

> **最终大纲** (共 N 页):
> 1. 标题页
> 2-3. 研究问题与动机 (强调: [用户指定])
> 4-5. [根据用户需求定制]
> ...
>
> 确认后我将开始生成 LaTeX 代码。

Wait for user confirmation before proceeding.

### 5. Plan the Slide Deck

Based on `TARGET_SLIDES`, select which sections to include:

**Always include (core):**
1. Title slide
2. Research question / motivation
3. Data & sample
4. Main results (1-3 slides depending on target)
5. Conclusion

**Add for standard/detailed:**
- Literature position
- Identification strategy
- Robustness checks

**Add for detailed only:**
- Mechanism / heterogeneity
- Policy implications
- Additional results

### 6. Generate Beamer .tex File (mode-dependent)

**IMPORTANT: Before generating, read the best practices prompt:**
```bash
cat .claude/prompts/beamer-generation-prompt.md
```

Apply all principles from the prompt file, especially:
- Use assertion-evidence approach (conclusion-based titles)
- Follow cognitive load principles (max 5 bullets per slide)
- Add visual hierarchy (colored boxes for key results)
- Provide economic interpretation, not just statistical significance

**If `GEN_MODE == "custom"`, strictly follow the user's:**
- `FOCUS_AREAS` - allocate more slides and detail
- `SKIP_AREAS` - minimize or omit
- `AUDIENCE` - adjust technical depth
- `STYLE_PREFS` - apply formatting preferences

Create `Slides/[BASENAME].tex` using the NankaiBeamer theme:

```latex
\documentclass[aspectratio=169]{beamer}
\usepackage{xeCJK}
\setCJKmainfont{SimSun}
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}
\usetheme{NankaiBeamer}

% Custom box environments
\usepackage{tcolorbox}
\tcbuselibrary{skins}
\newenvironment{resultbox}{\begin{tcolorbox}[colframe=nankai,colback=nankai!5]}{\end{tcolorbox}}
\newenvironment{methodbox}{\begin{tcolorbox}[colframe=orange!80!black,colback=orange!5]}{\end{tcolorbox}}
\newenvironment{highlightbox}{\begin{tcolorbox}[colframe=nankai!40,colback=nankai!8]}{\end{tcolorbox}}

\title{[Paper Title]}
\subtitle{[Journal, Year]}
\author{[Authors]}
\date{\today}

\begin{document}
\maketitle
% ... slides ...
\end{document}
```

**Rules for table slides (mode-dependent):**

#### If `TABLE_MODE == "auto"` or `TABLE_MODE == "manual"`:
- Use `\includegraphics[width=0.85\textwidth,height=0.55\textheight,keepaspectratio]{...}` for table images
- Add 1-2 bullet points explaining the key finding

#### If `TABLE_MODE == "text"`:
- Generate LaTeX `tabular` environment from extracted JSON data
- Use `\small` or `\footnotesize` for dense tables
- Add caption and label
- Example:
```latex
\begin{table}[h]
\centering
\small
\begin{tabular}{lcc}
\toprule
Variable & Coefficient & SE \\
\midrule
Treatment & 0.45*** & (0.12) \\
Control & -0.23* & (0.10) \\
\bottomrule
\end{tabular}
\caption{Main Results}
\end{table}
```

**Rules for text slides:**
- Max 5 bullet points per slide
- Use `\small` for dense content

### 7. Compile (automatically via /compile-latex)

Invoke `/compile-latex [BASENAME]` which handles:
- 3-pass XeLaTeX compilation
- Windows/Mac path separator detection
- Error reporting

### 8. Check and Fix Overflow (automatically)

After compilation, automatically invoke `/beamer-overflow-fix [BASENAME].tex` if overflow warnings exist.

### 9. Quality Scoring (automatically)

Run quality check:
```bash
python scripts/quality_score.py Slides/[BASENAME].tex --summary
```

Report the score. If score < 80, list critical issues and offer to fix.

### 10. Proofread (automatically if score < 90)

If quality score is below 90, automatically invoke `/proofread [BASENAME].tex` to check:
- Grammar and typos
- Academic writing quality
- Notation consistency

Apply fixes if user approves.

### 11. Present Results

Report:
- Number of slides generated (vs. target)
- Table extraction mode used: [auto/manual/text]
- Tables extracted and included
- Quality score: [N]/100 ([GATE])
- Any issues found and fixed
- Path to compiled PDF: `Slides/[BASENAME].pdf`

**Quality Gates:**
- 95-100: EXCELLENCE ⭐
- 90-94: PR-ready ✓
- 80-89: Commit-ready
- <80: Needs improvement (list issues)

## Error Handling

| Error | Action |
|-------|--------|
| `pdfplumber` not installed | `pip install pdfplumber` |
| `pdf2image` not installed | `pip install pdf2image` |
| `\kaishu` undefined | Add `\providecommand{\kaishu}{\rmfamily}` to theme file |
| NankaiBeamer.sty missing | Fall back to `\usetheme{Madrid}` |
| Compilation fails | Read first 50 lines of `.log`, fix the error, retry |

## Output

- `Slides/[BASENAME].tex` — Beamer source
- `Slides/[BASENAME].pdf` — Compiled presentation
- `Figures/[BASENAME]_tables/` — Cropped table images
