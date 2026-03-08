# 南开大学学术PPT自动生成工具

上传论文PDF，自动生成课堂展示Beamer PPT。

## 快速开始

### 1. 安装依赖

```bash
pip install pdfplumber pdf2image
```

还需要：
- **XeLaTeX**：Windows 用 [MiKTeX](https://miktex.org/)，Mac 用 `brew install --cask mactex`，Linux 用 `sudo apt install texlive-xetex`
- **pdftoppm**（可选，pdf2image的备选）：Mac 用 `brew install poppler`，Linux 用 `sudo apt install poppler-utils`，Windows 用 [Xpdf tools](https://www.xpdfreader.com/download.html)

### 2. 放入论文PDF

```bash
cp ~/Downloads/your_paper.pdf Papers/
```

### 3. 在Claude Code中运行

```bash
claude
/paper-to-beamer your_paper.pdf
```

## 工作流程

```
PDF → 提取表格坐标 → 渲染高清PNG → 分析论文结构
    → 生成Beamer .tex → XeLaTeX编译 → 溢出修复 → PDF输出
```

## 目录说明

| 目录 | 用途 |
|------|------|
| `Papers/` | 放入论文PDF（不提交到git） |
| `Slides/` | 生成的 `.tex` 和 `.pdf` |
| `Figures/` | 提取的表格图片 |
| `Preambles/` | NankaiBeamer.sty 主题文件 |
| `scripts/` | Python辅助脚本 |

## 技能

| 命令 | 功能 |
|------|------|
| `/paper-to-beamer [pdf]` | 完整流程：PDF → Beamer PPT |
| `/beamer-overflow-fix [file]` | 修复编译后的溢出警告 |

## License

MIT
