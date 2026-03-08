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

**Slide count guidelines:**

| Target | Slides | Coverage |
|--------|--------|---------|
| 精简版 | 12-15 | 动机、数据、主要结果、结论 |
| 标准版 | 23-25 | 上述 + 文献、识别策略、稳健性、机制 |
| 详细版 | 33-35 | 上述 + 异质性、政策含义、附录 |

### 3. Extract Tables with pdfplumber

```bash
python scripts/extract_tables.py "Papers/[FILENAME]"
```

### 4. Render High-Resolution PNGs

```bash
python scripts/render_pages.py "Papers/[FILENAME]" 200
```

### 5. Analyze Paper Structure

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

### 6. Plan the Slide Deck

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

### 7. Generate Beamer .tex File

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

**Rules for table slides:**
- Use `\includegraphics[width=0.85\textwidth,height=0.55\textheight,keepaspectratio]{...}` for table images
- Add 1-2 bullet points explaining the key finding

**Rules for text slides:**
- Max 5 bullet points per slide
- Use `\small` for dense content

### 8. Compile (automatically via /compile-latex)

Invoke `/compile-latex [BASENAME]` which handles:
- 3-pass XeLaTeX compilation
- Windows/Mac path separator detection
- Error reporting

### 9. Check and Fix Overflow (automatically)

After compilation, automatically invoke `/beamer-overflow-fix [BASENAME].tex` if overflow warnings exist.

### 10. Quality Scoring (automatically)

Run quality check:
```bash
python scripts/quality_score.py Slides/[BASENAME].tex --summary
```

Report the score. If score < 80, list critical issues and offer to fix.

### 11. Proofread (automatically if score < 90)

If quality score is below 90, automatically invoke `/proofread [BASENAME].tex` to check:
- Grammar and typos
- Academic writing quality
- Notation consistency

Apply fixes if user approves.

### 12. Present Results

Report:
- Number of slides generated (vs. target)
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
