# 南开大学论文汇报一键生成

上传论文PDF，自动生成课堂展示Beamer PPT。目前仓库里放的是南开大学的beamer模板，其它大学或者其他运用场合可自行更换为其他beamer模板。

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

运行后会提示选择页数：

| 选项 | 页数 | 适合场合 |
|------|------|---------|
| 精简版 | 12-15页 | 20-30分钟报告 |
| 标准版 | 23-25页 | 45分钟报告 |
| 详细版 | 33-35页 | 60分钟以上报告 |
| 自定义 | 任意 | 直接指定，如 `/paper-to-beamer paper.pdf 12` |

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
| `/paper-to-beamer [pdf]` | 完整流程：PDF → Beamer PPT（交互选择页数） |
| `/paper-to-beamer [pdf] [N]` | 直接指定页数，如 `paper.pdf 12` |
| `/beamer-overflow-fix [file]` | 修复编译后的溢出警告 |
| `/compile-latex [file]` | 3-pass XeLaTeX编译 |
| `/proofread [file]` | 语法/拼写/学术写作审查 |
| `/auto-publish [msg]` | 自动发布到GitHub并更新README/Pages |
| `/context-status` | 查看上下文使用情况 |
| `/learn [skill-name]` | 提取学习经验为持久化技能 |

## 质量控制

```bash
# 对生成的 .tex 文件打分（0-100）
python scripts/quality_score.py Slides/your_file.tex

# 质量门槛
# 80/100 - 可以 commit
# 90/100 - 可以发 PR
# 95/100 - 卓越
```

## License

MIT
