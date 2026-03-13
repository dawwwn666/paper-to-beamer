# Beamer 学术报告生成提示词

## 核心设计原则

### 1. Assertion-Evidence 方法
- **标题用结论,不用描述**: "Treatment increases earnings by 15%" 而非 "Treatment Effects"
- 每页幻灯片传达一个清晰的主张
- 用证据(表格/图表)支撑主张

### 2. 认知负荷优化
- 每页最多 5 个要点
- 避免完整句子,用短语
- 减少动画和过渡效果
- 字体大小: 标题 ≥24pt, 正文 ≥18pt

### 3. 视觉层次
- 用 `\textbf{}` 突出关键数字和发现
- 用彩色框(`resultbox`, `methodbox`)突出核心结果
- 表格后紧跟 1-2 条解读要点

### 4. 学术报告结构

**精简版 (12-15页):**
1. 标题页
2. 研究问题 (1页) - 用问句形式
3. 为什么重要? (1页) - 政策/理论意义
4. 数据概览 (1页) - 样本量、时间跨度、关键变量
5. 识别策略 (1-2页) - 核心方程 + 直觉解释
6. 主要结果 (2-3页) - 每个表格一页
7. 稳健性检查 (1页) - 列表形式
8. 结论 (1页) - 3条要点

**标准版 (23-25页):**
- 增加: 文献定位 (1-2页)、机制分析 (2-3页)、异质性 (1-2页)

**详细版 (33-35页):**
- 增加: 详细文献综述、数据构建细节、更多稳健性检查、政策含义

## LaTeX 代码规范

### 结果展示框
```latex
\begin{resultbox}
\textbf{核心发现:} 处理效应为 0.45 (SE=0.12), 统计显著
\end{resultbox}
```

### 表格幻灯片模板
```latex
\begin{frame}{处理效应提升收入15\%}
\begin{center}
\includegraphics[width=0.85\textwidth,height=0.55\textheight,keepaspectratio]{...}
\end{center}
\begin{itemize}
\item 基准回归: 系数 0.15*** (p<0.01)
\item 控制固定效应后结果稳健
\end{itemize}
\end{frame}
```

### 方法幻灯片模板
```latex
\begin{frame}{识别策略: 双重差分}
\begin{methodbox}
$$Y_{it} = \alpha + \beta (Treat_i \times Post_t) + \gamma_i + \delta_t + \epsilon_{it}$$
\end{methodbox}
\textbf{核心假设:} 平行趋势
\begin{itemize}
\item 处理组与对照组在政策前趋势相同
\item 下页展示事件研究图
\end{itemize}
\end{frame}
```

## 经济学/金融学特定规范

1. **回归表格**: 突出系数、标准误、显著性星号
2. **因果推断**: 明确说明识别假设和潜在威胁
3. **经济显著性**: 不仅报告统计显著性,还要解释经济含义
4. **文献定位**: 用 2x2 表格展示本文与现有文献的差异

## 避免的常见错误

❌ 标题: "Regression Results" → ✅ "Treatment Raises Earnings by 15%"
❌ 每页超过 7 个要点 → ✅ 最多 5 个要点
❌ 完整句子 → ✅ 简洁短语
❌ 表格无解读 → ✅ 表格下方 1-2 条关键发现
❌ 方法页过于技术化 → ✅ 提供直觉解释
