# CLAUDE.md — Paper-to-Beamer 工作流

**项目:** 论文PDF → Beamer课堂展示
**机构:** 南开大学 (Nankai University)

---

## 核心工作流

把论文PDF放入 `Papers/`，运行 `/paper-to-beamer [文件名]`，自动完成：

1. pdfplumber 提取表格坐标 → `Figures/[论文名]_tables/tables.json`
2. pdftoppm / pdf2image 渲染高清PNG → `Figures/[论文名]_tables/page-*.png`
3. 分析论文结构（假说、数据、识别策略、结论）
4. 生成 Beamer `.tex`（NankaiBeamer主题）→ `Slides/[论文名].tex`
5. XeLaTeX 3-pass 编译 → `Slides/[论文名].pdf`
6. 解析 `.log` 溢出警告，自动修复

---

## 目录结构

```
paper-to-beamer/
├── Papers/          # 放入论文PDF（不提交到git）
├── Slides/          # 输出的 .tex 和 .pdf
├── Figures/         # 提取的表格图片
├── Preambles/       # NankaiBeamer.sty + nankai-header.tex
├── scripts/         # extract_tables.py, render_pages.py
└── .claude/skills/  # paper-to-beamer, beamer-overflow-fix
```

---

## 编译命令

```bash
# 3-pass XeLaTeX（Windows用分号，Mac/Linux用冒号）
cd Slides
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode file.tex
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode file.tex
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode file.tex
```

---

## 技能

| 命令 | 功能 |
|------|------|
| `/paper-to-beamer [pdf]` | 论文PDF → Beamer PPT（完整流程） |
| `/beamer-overflow-fix [file]` | 解析log溢出警告并自动修复 |

---

## Beamer模板规范

**必须遵循的格式（参考 `CAPM_Size_Factor.tex`）：**

```latex
\documentclass{beamer}
\usepackage{amsfonts,amsmath}
\usetheme{nankai}

\usefonttheme[onlymath]{serif}
\titlebackground*{assets/background}  % 必须设置背景

\title{标题}
\subtitle{副标题}
\author{作者}
\date{日期}

\begin{document}

\maketitle  % 使用 \maketitle，不要用 \titlepage

\begin{frame}{Outline}
\tableofcontents
\end{frame}

% ... 正文内容 ...

\backmatter  % 使用 \backmatter，不要手动写"谢谢"

\end{document}
```

**关键点：**
1. 首页必须用 `\maketitle`（不是 `\begin{frame}\titlepage\end{frame}`）
2. 必须设置 `\titlebackground*{assets/background}`
3. 尾页必须用 `\backmatter`（不是手动frame）
4. `beamerthemenankai.sty` 的 `\ProvidesPackage` 必须是 `beamerthemenankai`
