---
name: doa-apidoc
description: >
  从需求描述或后端代码生成专业的接口说明文档（API Specification）。
  支持 PDF（reportlab）和 Word（python-docx）两种输出格式，商务蓝色主题。
  完整工作流：
  (1) 用户提供需求描述/后端代码/接口定义
  (2) 使用 vscode_askQuestions 确认输出格式（PDF / Word / 都要）
  (3) AI 结构化整理为标准接口文档格式
  (4) 生成 Python 脚本并运行输出文档
  USE FOR: 生成接口文档、API文档、接口设计说明书、接口说明文档、
  API接口文档PDF、API接口文档Word、从代码生成接口文档、
  从需求生成接口文档、接口设计文档。
  DO NOT USE FOR: 会议纪要（使用 doa-metting skill）、PPT（使用 doa-ppt skill）、
  通用PDF处理（使用 pdf skill）。
---

# 接口说明文档生成

## 工作流

```
用户提供需求/代码 → 确认输出格式(PDF/Word/Both) → AI 结构化整理 → 生成 Python 脚本 → 运行输出文档
```

## Step 0: 确认输出格式

**必须在生成前使用 `vscode_askQuestions` 确认：**

```
问题: 文档输出格式
选项:
  - PDF（适合交付/归档）  ← recommended
  - Word（适合后续编辑）
  - 都要
```

## Step 1: 收集与整理接口信息

从用户提供的需求描述、后端代码、或接口定义中，提取并结构化为以下标准章节：

### 文档元信息（封面）

| 字段 | 说明 |
|------|------|
| 文档标题 | 如「接口说明文档」 |
| 副标题 | 项目名 + 文档类型描述 |
| 文档版本 | V1.0 |
| 编制方 | 默认「{vendor_name}」，用户可覆盖 |
| 接收方 | 文档接收方 |
| 编制日期 | 日期 |
| 文档状态 | 初版发布 / 评审中 / 定稿 |

### 标准章节结构

| 章节 | 内容要求 |
|------|----------|
| **一、接口总览** | 接口清单表格（#/名称/Method/Path/描述）+ 调用链路（ASCII 时序图） |
| **二、公共约定** | 协议、Base URL、鉴权方式、数据格式、公共响应结构、错误码表 |
| **三、接口详细定义** | 每个接口：调用场景 + 请求头 + 入参表 + 入参示例 + 出参表 + 出参示例 + 错误场景 |
| **四、调用时序总结** | 汇总表（步骤/调用方/接口/触发条件/备注） |

### 每个接口的标准子节

```
3.x  {METHOD} {path} — {接口名}
  ├─ 调用场景（ColorBox 高亮）
  ├─ 请求头（如需鉴权）
  ├─ 入参（表格：参数/类型/必填/说明）
  ├─ 入参示例（code_block）
  ├─ 出参（表格：参数/类型/说明）
  ├─ 出参示例 — 成功 / 失败 / 各状态（code_block）
  └─ 错误场景（表格：code/场景）
```

### 内容整理原则

- 从代码/需求中推导完整的入参出参，字段名用 camelCase
- 必填字段标记 ✅
- 嵌套对象用 `parent[].child` 格式展示
- 枚举值列出全部可选项及含义
- 错误码覆盖 400/401/404/422/500 等常见场景
- 示例 JSON 使用真实可读的模拟数据

## Step 2: 生成文档脚本

根据用户选择的格式，读取对应模板：

- **PDF**: 读取 [references/apidoc-pdf-template.py](references/apidoc-pdf-template.py)
- **Word**: 读取 [references/apidoc-word-template.py](references/apidoc-word-template.py)

基于模板生成定制化 Python 脚本，替换其中的内容数据。

### 设计规范

#### 颜色体系（商务蓝主题，PDF/Word 通用）

| 角色 | 色值 | 用途 |
|------|------|------|
| pri | `#1A365D` | 深蓝 - 主标题、表头、页眉线 |
| sec | `#2B6CB0` | 中蓝 - 章节标题(h2) |
| acc | `#3182CE` | 亮蓝 - 小节标题(h3)、强调 |
| lbg | `#EBF4FF` | 浅蓝背景 - 信息卡片、首列 |
| lgray | `#F7FAFC` | 极浅灰 - 交替行 |
| border | `#CBD5E0` | 边框灰 |
| txt | `#2D3748` | 正文色 |
| sub | `#718096` | 辅助文字、页眉页脚 |
| green | `#276749` | 成功/通过 |
| orange | `#C05621` | 警告/待确认 |
| red | `#C53030` | 紧急/重要 |

#### PDF 核心组件

模板提供以下 Flowable 组件：

- **`SectionBar(text, color)`** — 带色块的章节标题栏（白字 + 圆角深蓝底）
- **`InfoCard(rows)`** — 信息卡片（浅蓝底 + 边框，用于封面元信息）
- **`Divider()`** — 分隔线
- **`ColorBox(text, bg, bc)`** — 调用场景高亮框（浅蓝底 + 蓝色边框）
- **`make_table(headers, rows, col_widths)`** — 标准数据表格（深蓝表头 + 交替行）
- **`make_kv_table(rows)`** — 键值表格（左列浅蓝底粗体 + 右列正文）
- **`code_block(text)`** — 代码块（浅灰底 + 蓝色等宽字体）

#### Word 核心组件

模板提供以下函数：

- **`add_section_bar(doc, text, color)`** — 带色块的章节标题栏
- **`add_info_card(doc, rows)`** — 信息卡片
- **`add_divider(doc)`** — 分隔线
- **`add_color_box(doc, text)`** — 调用场景高亮框
- **`add_table(doc, headers, rows, col_widths_mm)`** — 标准数据表格
- **`add_kv_table(doc, rows)`** — 键值表格
- **`add_code_block(doc, text)`** — 代码块
- **`add_paragraph(doc, text, ...)`** — 段落（支持 `<b>` 标记）

#### 页眉页脚

根据实际项目名调整：
- 页眉左：`{项目名} · {文档类型}`
- 页眉右：`CONFIDENTIAL 机密`（可选）
- 页脚左：`{vendor_name}`（默认，用户可覆盖）
- 页脚右：`第 X 页`（PDF）/ `页码请在 Word 中查看`（Word）

## Step 3: 运行生成

输出目录：`output/{项目名称}-接口文档/`（每次新任务创建独立子文件夹）

**PDF:**
```bash
pip install reportlab
python generate_api_doc.py
```

**Word:**
```bash
pip install python-docx
python generate_api_doc_word.py
```

确认文档输出后告知用户文件路径。

## 注意事项

- PDF 字体注册使用 `register_fonts()` 函数，自动适配 Windows/macOS/Linux
- A4 纸张，左右上下边距 20mm
- 每个接口详细定义前使用 `PageBreak()`（PDF）或 `doc.add_page_break()`（Word）分页
- 表格列宽之和应为 ~166mm（PDF）/ 对应 Mm 值（Word），确保不溢出
- 代码块使用等宽字体：PDF 用 CF 蓝色 7.8pt，Word 用 Consolas 8.5pt
- Word 生成的 `.docx` 文件体积小、可继续编辑，适合需要后续调整的场景
- PDF 使用 `repeatRows=1` 让表头在跨页时重复显示
