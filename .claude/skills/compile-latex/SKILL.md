---
name: compile-latex
description: Compile a Beamer LaTeX slide deck with XeLaTeX (3 passes + bibtex). Use when compiling lecture slides.
argument-hint: "[filename without .tex extension]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Compile Beamer LaTeX Slides

Compile a Beamer slide deck using XeLaTeX with full citation resolution.

## Steps

1. **Navigate to Slides/ directory** and compile with 3-pass sequence:

```bash
cd Slides
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode $ARGUMENTS.tex
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode $ARGUMENTS.tex
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

**Note:** Use semicolon (`;`) for Windows, colon (`:`) for Mac/Linux.

**Alternative (latexmk):**
```bash
cd Slides
TEXINPUTS="../Preambles;$TEXINPUTS" latexmk -xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

2. **Check for warnings:**
   - Grep output for `Overfull \\hbox` warnings
   - Grep for `undefined citations` or `Label(s) may have changed`
   - Report any issues found

3. **Open the PDF** for visual verification:
   ```bash
   open Slides/$ARGUMENTS.pdf          # macOS
   # xdg-open Slides/$ARGUMENTS.pdf    # Linux
   ```

4. **Report results:**
   - Compilation success/failure
   - Number of overfull hbox warnings
   - Any undefined citations
   - PDF page count

## Why 3 passes?
1. First xelatex: Creates `.aux` file with labels and references
2. Second xelatex: Resolves cross-references
3. Third xelatex: Finalizes all references with correct page numbers

## Important
- **Always use XeLaTeX**, never pdflatex
- **TEXINPUTS** is required: your Beamer theme lives in `Preambles/`
- Use semicolon (`;`) path separator on Windows, colon (`:`) on Mac/Linux
