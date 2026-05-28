---
name: doa-metting
description: >
  从会议概要或会议内容生成逻辑严谨、格式清晰、样式优美的专业 PDF 会议纪要。
  使用 Python reportlab 库，支持中文字体（跨平台自动适配），商务蓝色主题。
  完整工作流：
  (1) 用户提供会议概要/原始内容/录音文字稿
  (2) AI 结构化整理为标准会议纪要格式
  (3) 生成 Python 脚本并运行输出 PDF
  USE FOR: 生成会议纪要、会议记录PDF、meeting minutes、会议总结文档、
  会议纪要PDF、从会议内容生成PDF、整理会议记录。
  DO NOT USE FOR: 通用PDF处理（使用 pdf skill）、PPT生成（使用 doa-ppt skill）。
---

# 会议纪要 PDF 生成

## 工作流

```
用户提供会议内容 → AI 结构化整理 → 生成 Python 脚本 → 运行输出 PDF
```

## Step 1: 收集与整理会议内容

从用户输入中提取并结构化为以下标准章节：

### 必需章节

| 章节 | 内容要求 |
|------|----------|
| **基本信息** | 会议主题、参会方、核心目标、日期 |
| **会议核心内容** | 按议题分节，每节含标题 + 要点 |
| **达成共识** | 编号列表，明确已确认事项 |
| **待确认项** | 编号列表，标注风险/未决事项 |
| **后续行动计划** | 表格：责任方 + 行动项 + 时间节点 |
| **会议结论** | 一句话概括结论 |

### 可选章节

- **附录**：流程图、系统交互步骤、补充说明
- **参考资料**：相关文档链接

### 内容整理原则

- 去除口语化表达，用专业书面语
- 每个议题提炼 3-5 个核心要点
- Action Items 必须有明确负责人和时间节点
- 待确认项标注影响范围和紧急程度

## Step 2: 生成 PDF 脚本

读取 [references/pdf-template.py](references/pdf-template.py) 获取完整的生成模板。

基于模板生成定制化 Python 脚本，替换其中的内容数据。

### 设计规范

#### 颜色体系（商务蓝主题）

| 角色 | 色值 | 用途 |
|------|------|------|
| PRIMARY | `#1A365D` | 主标题、表头、页眉线 |
| SECONDARY | `#2B6CB0` | 章节标题 |
| ACCENT | `#3182CE` | 强调、流程编号 |
| SUCCESS | `#276749` | 达成共识（✅） |
| WARNING | `#C05621` | 待确认项（⚠️） |
| RED | `#C53030` | 紧急/重要时间节点 |
| LIGHT_BG | `#EBF4FF` | 信息卡片背景 |
| TEXT | `#2D3748` | 正文 |
| SUBTEXT | `#718096` | 辅助文字 |

#### 字体层级

| 元素 | 字体 | 字号 | 行距 |
|------|------|------|------|
| 大标题 | ChineseFontBold | 20pt | 28pt |
| 章节标题 | SectionHeader 组件 | 12pt | — |
| 小节标题 | ChineseFontBold | 12pt | 18pt |
| 正文 | ChineseFont | 10pt | 16pt |
| 列表项 | ChineseFont | 10pt | 16pt |
| 页眉/页脚 | ChineseFont | 7.5-8pt | — |

#### 核心组件

模板提供以下 Flowable 组件，直接复用：

- **`SectionHeader(text, color)`** — 带色块的章节标题栏（白字 + 圆角色底）
- **`InfoBox(data)`** — 信息卡片（浅蓝底 + 边框，用于基本信息展示）
- **`DividerLine()`** — 分隔线
- **页眉页脚** — `header_footer()` 回调，含蓝线 + 项目名 + 页码

#### 表格样式要点

- 表头：PRIMARY 背景 + 白色文字
- 首列：LIGHT_BG 背景 + PRIMARY 粗体文字
- 交替行色：`LIGHT_GRAY (#F7FAFC)`
- 边框：`BORDER (#CBD5E0)` 0.4-0.5pt
- 内边距：3mm 上下 + 3mm 左右

### 内容与样式映射

| 内容类型 | 实现方式 |
|----------|----------|
| 基本信息（主题/参会方/目标） | `InfoBox` 组件 |
| 章节标题（一、二、三…） | `SectionHeader` 组件，不同章节用不同颜色 |
| 议题小标题 | `h2` 样式（SECONDARY 粗体） |
| 要点列表 | `bullet` 样式（`•` 前缀，12mm 缩进） |
| 达成共识 | `consensus` 样式（`✅` 前缀，绿色） |
| 待确认项 | `warning` 样式（`⚠️` 前缀，橙色） |
| 行动计划 | Table（3列：责任方/行动项/时间） |
| 结论高亮 | Table 单行（LIGHT_BG + PRIMARY 边框） |
| 流程步骤 | Table（3列：序号/角色/操作） |

### 页眉页脚内容

根据会议实际项目名调整：
- 页眉左：`{项目名} · {文档类型}`
- 页眉右：`CONFIDENTIAL 机密`（或根据需要调整）
- 页脚左：`{公司名}`
- 页脚右：`第 X 页`

## Step 3: 运行生成

输出目录：`output/{会议主题或日期}/`（每次新任务创建独立子文件夹）

```bash
pip install reportlab
python generate_meeting_minutes.py
```

确认 PDF 输出后告知用户文件路径。

## 注意事项

- 字体注册使用 `register_fonts()` 函数，自动适配 Windows/macOS/Linux
- A4 纸张，左右上下边距 20mm/18mm/20mm
- 使用 `KeepTogether` 避免表格跨页断裂
- 长内容自动分页，`PageBreak` 仅在必要时手动插入
- `SimpleDocTemplate` 的 `onFirstPage` 和 `onLaterPages` 均绑定 `header_footer`
