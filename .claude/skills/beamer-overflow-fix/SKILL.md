---
name: beamer-overflow-fix
description: Fix Overfull \hbox and \vbox warnings in a compiled Beamer .tex file. Parses the .log, locates offending lines, applies targeted fixes, and recompiles.
argument-hint: "[TEX filename in Slides/ directory]"
trigger-phrases: ["fix overflow", "fix overfull", "修复溢出", "beamer overflow"]
allowed-tools: ["Read", "Edit", "Bash", "Grep"]
---

# Beamer Overflow Fix

Parse the LaTeX `.log` file for overflow warnings, locate the offending content, apply fixes, and recompile.

## Input

`$ARGUMENTS` = `.tex` filename (with or without extension) in `Slides/`

## Steps

### 1. Parse the Log File

```bash
grep -n "Overfull" Slides/[BASENAME].log
```

Extract:
- Line numbers in the `.tex` file (from `l.NNN` in the log)
- Type: `\hbox` (horizontal overflow — text too wide) or `\vbox` (vertical overflow — slide too tall)
- Severity: badness value (higher = worse; >1000 is visible)

### 2. Categorize Each Warning

For each `Overfull` warning, read the surrounding context in the `.tex` file (±5 lines around the reported line).

| Warning Type | Likely Cause | Fix Strategy |
|-------------|-------------|-------------|
| `\hbox` in frame | Long line of text | Wrap in `\small` or break line |
| `\hbox` in `\includegraphics` | Image too wide | Add `width=0.85\textwidth,keepaspectratio` |
| `\hbox` in equation | Long formula | Use `\small` or split with `align` |
| `\vbox` in frame | Too much content | Split frame or reduce font size |
| `\hbox` in table | Wide table | Use `\resizebox{\textwidth}{!}{...}` |

### 3. Apply Fixes

**Fix A: Text overflow (`\hbox` in paragraph)**
```latex
% Before
This is a very long sentence that overflows the slide boundary.

% After
\small This is a very long sentence that overflows the slide boundary.
```

**Fix B: Image overflow**
```latex
% Before
\includegraphics{../Figures/table1.png}

% After
\includegraphics[width=0.85\textwidth,keepaspectratio]{../Figures/table1.png}
```

**Fix C: Vertical overflow (too much content)**
```latex
% Before: one frame with 6 bullet points

% After: split into two frames
\begin{frame}{Title (1/2)}
  \begin{itemize}
    \item Point 1
    \item Point 2
    \item Point 3
  \end{itemize}
\end{frame}

\begin{frame}{Title (2/2)}
  \begin{itemize}
    \item Point 4
    \item Point 5
    \item Point 6
  \end{itemize}
\end{frame}
```

**Fix D: Wide table**
```latex
% Before
\begin{tabular}{lcccc} ... \end{tabular}

% After
\resizebox{\textwidth}{!}{%
\begin{tabular}{lcccc} ... \end{tabular}
}
```

**Fix E: Long equation**
```latex
% Before
\[ Y_{it} = \alpha + \beta_1 X_{it} + \beta_2 Z_{it} + \gamma_i + \delta_t + \varepsilon_{it} \]

% After
{\small
\[ Y_{it} = \alpha + \beta_1 X_{it} + \beta_2 Z_{it} + \gamma_i + \delta_t + \varepsilon_{it} \]
}
```

### 4. Recompile

```bash
cd Slides
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode [BASENAME].tex
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode [BASENAME].tex
```

(Two passes sufficient for overflow-only fixes; no bibliography rerun needed unless citations changed.)

### 5. Verify

```bash
grep "Overfull" Slides/[BASENAME].log | wc -l
```

Compare count before and after. Report:
- Warnings fixed: N
- Warnings remaining: M (with reasons if unfixable)

### 6. Escalation (if fix fails)

If a warning persists after 2 fix attempts:
1. Note it in the summary with the line number and content
2. Suggest manual review
3. Do NOT loop more than 3 times on the same warning

## Priority Order

Fix in this order:
1. `\vbox` warnings (slide overflow — content cut off)
2. `\hbox` with badness > 10000 (visually obvious)
3. `\hbox` with badness 1000-10000 (noticeable)
4. `\hbox` with badness < 1000 (minor, may skip)

## Output

Summary table:

```
Overflow Fix Summary: [BASENAME].tex
=====================================
Before: N Overfull warnings
After:  M Overfull warnings

Fixed:
  Line 42: \hbox in frame "Results" — added keepaspectratio to image
  Line 87: \vbox in frame "Data" — split into two frames

Remaining (manual review needed):
  Line 103: \hbox badness 1234 — long URL in footnote (acceptable)
```
