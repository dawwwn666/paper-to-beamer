---
name: paper-to-beamer
description: Convert a research paper PDF into a Beamer presentation. Extracts tables, analyzes structure, generates .tex with NankaiBeamer theme, compiles, and fixes overflow.
argument-hint: "[PDF filename in Papers/ directory]"
trigger-phrases: ["paper to beamer", "论文转PPT", "制作课堂展示", "从论文生成PPT", "paper to slides"]
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Agent"]
---

# Paper-to-Beamer Workflow

Convert a research paper PDF into a complete Beamer presentation using the NankaiBeamer theme.

## Input

`$ARGUMENTS` = PDF filename (with or without `.pdf` extension) located in `Papers/`

## Steps

### 1. Locate the PDF

```bash
ls Papers/
```

Confirm the file exists. If not found, list available PDFs and ask the user to clarify.

### 2. Extract Tables with pdfplumber

Run the table extraction script:

```bash
python scripts/extract_tables.py "Papers/$ARGUMENTS"
```

If `scripts/extract_tables.py` does not exist, create it inline:

```python
import pdfplumber
import json
import sys
import os

pdf_path = sys.argv[1]
base = os.path.splitext(os.path.basename(pdf_path))[0]
out_dir = f"Figures/{base}_tables"
os.makedirs(out_dir, exist_ok=True)

results = []
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.find_tables()
        for j, table in enumerate(tables):
            bbox = table.bbox  # (x0, y0, x1, y1)
            data = table.extract()
            results.append({
                "page": i + 1,
                "table_index": j,
                "bbox": bbox,
                "rows": len(data) if data else 0,
                "cols": len(data[0]) if data and data[0] else 0,
                "preview": data[:3] if data else []
            })

out_file = f"{out_dir}/tables.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Found {len(results)} tables. Saved to {out_file}")
for r in results:
    print(f"  Page {r['page']}, Table {r['table_index']}: {r['rows']}x{r['cols']} at {r['bbox']}")
```

### 3. Render High-Resolution PNGs

For each page containing a table, render a PNG:

```bash
pdftoppm -r 200 -png "Papers/$ARGUMENTS" "Figures/${BASE}_tables/page"
```

Then crop each table region using the bounding boxes from Step 2.

If `pdftoppm` is unavailable, use `pdf2image` (Python):

```python
from pdf2image import convert_from_path
pages = convert_from_path("Papers/file.pdf", dpi=200)
for i, page in enumerate(pages):
    page.save(f"Figures/base_tables/page-{i+1}.png")
```

### 4. Analyze Paper Structure

Read the PDF text to identify:
- **Title, authors, journal/year**
- **Abstract** (1-2 key sentences)
- **Research question / hypothesis**
- **Data and sample** (N, time period, geography)
- **Identification strategy** (IV, DiD, RD, etc.)
- **Main results** (sign, magnitude, significance)
- **Robustness checks**
- **Conclusion / policy implications**

Use pdfplumber for text extraction:

```python
import pdfplumber
with pdfplumber.open("Papers/file.pdf") as pdf:
    text = "\n".join(p.extract_text() or "" for p in pdf.pages[:5])
print(text[:3000])
```

### 5. Plan the Slide Deck

Based on the analysis, plan a 12-20 slide deck:

| Slide | Content |
|-------|---------|
| 1 | Title slide |
| 2 | Motivation / Research Question |
| 3 | Literature Position |
| 4 | Data & Sample |
| 5 | Identification Strategy |
| 6-8 | Main Results (tables/figures) |
| 9-10 | Robustness Checks |
| 11 | Mechanism / Heterogeneity |
| 12 | Conclusion |

### 6. Generate Beamer .tex File

Create `Slides/[BASENAME].tex` using the NankaiBeamer theme:

```latex
\documentclass[aspectratio=169]{beamer}
\usepackage{../Preambles/nankai-header}
% or: \usetheme{NankaiBeamer} if NankaiBeamer.sty is available

\title{[Paper Title]}
\subtitle{[Journal, Year]}
\author{[Authors] \\ \small Presented by [Your Name]}
\date{\today}

\begin{document}
\maketitle

% --- Motivation ---
\begin{frame}{Research Question}
...
\end{frame}

% --- Data ---
\begin{frame}{Data \& Sample}
...
\end{frame}

% --- Main Results ---
\begin{frame}{Main Results}
\begin{figure}
  \includegraphics[width=0.85\textwidth,keepaspectratio]{../Figures/[BASE]_tables/table1_crop.png}
\end{figure}
\end{frame}

% ... more slides ...

\end{document}
```

**Rules for table slides:**
- Use `\includegraphics[width=0.85\textwidth,keepaspectratio]{...}` for cropped table images
- Never paste raw LaTeX tables from the paper (formatting will break)
- Add 1-2 bullet points below each table explaining the key finding

**Rules for text slides:**
- Max 5 bullet points per slide
- Use `\small` for dense content
- Use `resultbox`, `methodbox`, `definitionbox` environments for key findings

### 7. Compile (3-pass XeLaTeX)

```bash
cd Slides
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode [BASENAME].tex
BIBINPUTS=..:$BIBINPUTS bibtex [BASENAME]
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode [BASENAME].tex
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode [BASENAME].tex
```

### 8. Check for Overflow

Parse the `.log` file:

```bash
grep -n "Overfull" Slides/[BASENAME].log | head -30
```

If overflow warnings exist, invoke `/beamer-overflow-fix [BASENAME].tex` automatically.

### 9. Present Results

Report:
- Number of slides generated
- Tables extracted and included
- Any overflow issues found and fixed
- Path to compiled PDF: `Slides/[BASENAME].pdf`

## Error Handling

| Error | Action |
|-------|--------|
| `pdfplumber` not installed | `pip install pdfplumber` |
| `pdftoppm` not found | Use `pdf2image` fallback |
| NankaiBeamer.sty missing | Fall back to `\usetheme{Madrid}` and note the limitation |
| Compilation fails | Read first 50 lines of `.log`, fix the error, retry |
| No tables found | Proceed with text-only slides, note in summary |

## Output

- `Slides/[BASENAME].tex` — Beamer source
- `Slides/[BASENAME].pdf` — Compiled presentation
- `Figures/[BASENAME]_tables/` — Cropped table images
- `Figures/[BASENAME]_tables/tables.json` — Table metadata
