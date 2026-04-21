# SEC 报告工作流：技术详解

本文档从代码层面详细解读 BioClaw 中 SEC（尺寸排阻色谱）报告功能的完整实现。这套功能由两个 runtime skill 加上一层运行时路由共同组成，形成一条从"用户上传数据"到"交付 PDF 报告"的端到端自动化链路。

---

## 1. 两个 Skill 各自做什么

先用一句话讲清楚各自的角色，后面再展开细节。

| Skill | 一句话定位 | 类比 |
|---|---|---|
| `sec-report` | 面向 SEC 领域的完整分析引擎：读数据、找峰、打分、出图、组织报告正文 | "分析师" |
| `report-template` | 通用的 Typst 报告排版引擎：接收结构化内容，编译成 PDF | "排版工人" |

它们之间是**调用关系**，不是平级关系：

```
sec-report  ──调用──>  report-template
(领域分析)              (PDF 排版)
```

`sec-report` 知道 SEC 色谱的一切（怎么解析 AKTA 数据、怎么定义洗脱区间、怎么给 construct 打分），但它自己不知道怎么把内容排版成好看的 PDF。排版这件事全部委托给 `report-template`。

`report-template` 完全不懂 SEC。它只知道怎么接收标题、段落、表格、图片、callout，然后用 Typst 模板编译成带页眉页脚、分栏配色的学术风格 PDF。任何其他 skill 将来也可以调用它来生成报告。

---

## 2. `sec-report` Skill：内部模块结构

`sec-report` 不是单个脚本，而是由 **4 个 Python 模块 + 1 个 SKILL.md** 组成的模块群。理解每个模块的分工是理解整套系统的关键。

```
container/skills/sec-report/
├── SKILL.md                 # Skill 定义：触发条件、执行步骤、guardrails
├── sec_pipeline.py          # 主编排器：CLI 入口、数据发现、调度分析和出图、输出 JSON
├── sec_report_common.py     # 共享工具：cohort 检测、代表性 construct 选择
├── sec_report_typst.py      # Typst 报告构建器：用 report-template 组装正文
├── sec_report_pdf.py        # fpdf2 备用报告构建器：当 Typst 不可用时兜底
└── tests/
    └── run_test.sh           # 端到端测试脚本
```

### 2.1 `sec_pipeline.py` — 主编排器

这是整个 pipeline 的入口和总指挥。它**不做**报告排版，只负责编排以下 5 步：

```
[1/5] 输入解析     →  解压 ZIP 或扫描目录，发现数据文件和图片
[2/5] 逐样品分析   →  对每个数据文件：解析列 → 找峰 → 打分 → 画注释色谱图
[3/5] 比较图       →  生成 overlay、zone fraction、ranking 等跨样品比较图
[4/5] PDF 报告     →  委托给 sec_report_typst（优先）或 sec_report_pdf（兜底）
[5/5] JSON 摘要    →  输出 analysis_summary.json，包含所有数值结果和 renderer 元数据
```

Pipeline 的**核心类**（全部定义在 `sec_pipeline.py` 中）：

#### `SECDataParser`：数据解析器

负责把各种格式的 SEC 数据文件读成 `(volumes, absorbance)` 数组。

解析策略（按顺序尝试）：

1. **AKTA/UNICORN 多头格式**：UTF-16 编码、制表符分隔、有 3 行仪器头。Parser 会搜索含 `ml` 和 `mAU` 的 units 行，跳过上方的头，然后提取第一对 `(ml, mAU)` 列（即 UV 检测器），忽略电导等其他检测器列。
2. **标准 CSV/TSV**：UTF-8 编码，第一行即列头，通过正则匹配列名（`vol`, `ml`, `Ve`, `abs`, `mAU`, `A280` 等）。
3. **回退**：如果列名匹配失败，取前两个数值列分别作为 volume 和 absorbance。

支持的编码尝试顺序：UTF-8 → UTF-16 → UTF-16-LE → UTF-16-BE → Latin-1。

数据清洗：

- 丢弃全空行和全空列
- 强制转数值类型
- 截取 SEC 分离范围（0 ~ 28.8 mL），丢弃平衡和 CIP 阶段的数据点

#### `SECPeakAnalyzer`：峰检测与打分引擎

这是分析的核心。它对每个 construct 执行以下处理：

**第一步：平滑**

Savitzky-Golay 滤波器，窗口 15 点（约 0.75 mL），多项式阶数 3。如果数据点太少（< 20），跳过平滑。

**第二步：找峰**

调用 `scipy.signal.find_peaks()`，参数全部自适应：

| 参数 | 设定 | 含义 |
|---|---|---|
| `height` | 最大信号的 5% | 只检测有意义的峰 |
| `prominence` | 最大信号的 3% | 排除肩峰和噪声 |
| `distance` | 0.5 mL（按点距换算） | 避免在同一个峰上重复检测 |

**第三步：峰宽测量**

调用 `scipy.signal.peak_widths()` 在半高处测 FWHM（全宽半高）。

**第四步：面积计算**（关键细节）

不是简单地对每个峰取固定宽度积分，而是采用 **valley-based partition**：

1. 在相邻两峰之间找到信号最低点（valley）
2. 以 valley 为分界，每个峰"拥有"从左 valley 到右 valley 之间的全部面积
3. 用梯形积分（`numpy.trapezoid`）计算每段面积
4. 这样保证各峰面积之和 ≈ 100%，不会重叠也不会遗漏

**第五步：分类**

基于峰洗脱体积相对于空隙体积（V₀）的偏移量：

```
Ve - V₀ ≤ 0.5 mL   → aggregate        (被柱排阻的大颗粒)
          0.5–2.5    → large_oligomer   (环状候选)
          2.5–4.5    → oligomer         (三聚体、四聚体范围)
          4.5–6.5    → dimer            (二聚体范围)
          6.5–9.0    → monomer          (单体)
          > 9.0      → small_molecule   (缓冲液组分或降解产物)
```

**第六步：质量评分**（0–10 分制）

从满分 10 分开始扣分和加分：

| 条件 | 效果 |
|---|---|
| 聚集占比 × 0.1 | 最多扣 3.0 分 |
| 主峰是 aggregate | 额外扣 4.0 分 |
| 主峰是 small_molecule | 额外扣 1.5 分 |
| polydisperse（主峰 < 60%） | 扣 3.0 分 |
| heterogeneous（主峰 60–80%） | 扣 1.5 分 |
| predominantly_monodisperse（主峰 > 80%） | 扣 0.5 分 |
| 任一峰 FWHM > 3.0 mL | 扣 1.0 分 |
| 任一峰 FWHM > 2.0 mL | 扣 0.5 分 |
| 主峰 FWHM < 1.5 且占比 > 70% | **加** 1.0 分 |

最终 clamp 到 [0, 10]。

评分阈值：≥ 7 = Excellent，5–7 = Good，3–5 = Moderate，< 3 = Poor。

#### `SECPlotter`：出图引擎

生成 5 种标准图表：

| 图表 | 文件名 | 作用 |
|---|---|---|
| 注释色谱图 | `<name>_annotated.png` | 每个 construct 一张，标注峰位置、分类、面积占比、质量评分 |
| 归一化叠加图 | `comparison_overlay.png` | 所有 construct 的色谱曲线叠在一起，带区间着色 |
| 区间占比堆叠柱 | `zone_fractions.png` | 每个 construct 各区间面积占比的堆叠柱状图 |
| 多面板网格 | `individual_grid.png` | 所有 construct 的小图排列，带区间着色和主峰标记 |
| 质量排名柱 | `ranking_summary.png` | 所有 construct 按质量评分排序的水平柱状图 |

在 compact 模式下，还会额外生成 `_primary` 后缀的图表（仅含 primary cohort），以及 `selected_grid.png`（仅含代表性 construct 子集）。

#### 数据发现逻辑 `discover_files()`

不是简单地遍历目录取所有文件，而是有三层过滤：

1. **跳过非数据文件**：隐藏文件、临时文件、`__pycache__`、`__MACOSX`
2. **跳过已知非色谱文件**：校准文件（calibration）、汇总表（combined_、all_peak_metrics）、处理脚本（secprocess）
3. **去重**：如果同一样品同时存在原始数据和 `_normalized_curve` 版本，只保留原始数据

### 2.2 `sec_report_common.py` — 共享工具模块

提供两个关键功能，被 `sec_pipeline.py` 和 `sec_report_typst.py` 共同使用：

#### Cohort 检测 `assign_cohorts()`

从数据文件的路径中提取年份信息，区分"当前批次"和"历史对照"：

- 扫描路径的每一级目录名，找 4 位数字年份（如 `2025/data/...` 中的 `2025`）
- 也检查文件名前缀（如 `20250415_sample.csv` 中的 `2025`）
- 最新年份标记为 `primary`，更早年份标记为 `context`
- 如果只有一个年份或无法检测年份，全部标记为 `primary`

这决定了 compact 报告中哪些 construct 进入主分析、哪些降级为"历史参考"。

#### 代表性 construct 选择 `select_representative_constructs()`

在 compact 模式下，不是展示所有 construct，而是选择一个有信息密度的子集（默认最多 4 个）。选择策略：

按优先级从 4 个桶中各取 1 个：

| 桶 | 选择条件 | 目的 |
|---|---|---|
| ring | HMW 主峰 + Q ≥ 5 | 展示最有希望的环状装配候选 |
| control | 二聚体/单体 + 单分散 + Q ≥ 6 | 展示行为良好的对照 |
| heterogeneous | polydisperse 或有宽峰 + Q ≥ 3 + 聚集 < 30% | 展示异质样品 |
| failure | 聚集 ≥ 15% 或 Q < 4 | 展示失败案例 |

先每桶取 1 个，然后轮流补充直到达到 `max_items`。如果所有桶都空了，按质量评分从高到低补齐。选择是确定性的（给定相同输入，总是产出相同子集）。

### 2.3 `sec_report_typst.py` — Typst 报告构建器

这个模块的职责是：**把 `sec_pipeline.py` 产出的分析结果，通过调用 `report-template` 的 ReportBuilder API，组装成一份完整的 SEC 分析报告**。

它是"领域知识"和"排版引擎"之间的桥梁。它知道 SEC 报告应该包含哪些章节、每个章节应该写什么内容，但把具体的排版（字体、配色、页眉页脚）完全委托给 `report-template`。

#### 报告章节结构

主报告（`build_typst_report()`）固定包含以下章节：

```
标题页 + 元数据卡片
├── [compact] Executive Summary callout（自动生成的要点列表）
│
├── 1. Background
│   ├── 项目背景：链 A (~53 kDa) + 链 B (~27 kDa) 的异二聚体设计
│   ├── SEC 原理：大分子先洗脱，环状装配体应比二聚体早出
│   └── 声明：无绝对分子量校准
│
├── 2. Methods
│   ├── 2.1 仪器与柱子：Superdex 200 Increase 10/300 GL
│   ├── 2.2 数据处理：平滑参数、找峰参数、积分方法
│   └── 2.3 洗脱区间定义表
│
├── 3. Results
│   ├── 3.1 概览指标卡片（metric cards）
│   ├── 3.2 Construct 汇总表（带编辑化分类标签）
│   ├── 3.3 SEC 叠加图
│   ├── 3.4 区间占比图
│   ├── 3.5 质量排名图
│   ├── 3.6 代表性色谱图 [compact] / 全量网格 [full]
│   ├── 3.7 选定 Construct 亮点（每个一段解读 + 建议）
│   └── 3.8 历史对照表 [compact，仅当有 context cohort 时]
│
├── 4. Discussion
│   ├── 4.1 环状装配候选（如果有）
│   ├── 4.2 单分散装配体（如果有）
│   ├── 4.3 异质 HMW 装配体（如果有）
│   ├── 4.4 聚集问题（如果有）
│   └── 4.5 方法学注意事项
│
├── 5. Conclusions and Recommendations
│   ├── 5.1 排名汇总表
│   ├── 5.2 推荐下一步实验（callout boxes）
│   │   ├── [success] 环候选：cryo-EM, native MS, DLS
│   │   ├── [note] 单分散：SEC-MALS, AUC
│   │   └── [warning] 异质 HMW：buffer screen, 温度筛选
│   └── Disclaimer callout
│
└── [compact] 附录 PDF（build_typst_appendix）
    ├── A. 全量色谱图网格
    ├── B. 全量区间占比图
    └── C. 逐 Construct 峰表 + 注释色谱图 + 解读
```

#### 自动生成的文字内容

`sec_report_typst.py` 不只是把图表拼在一起，它还会根据分析结果**自动生成实质性的解读文字**。这些文字不是模板占位符，而是根据每个 construct 的具体数据生成的：

`_interpret(result)` 函数会为每个 construct 生成一段解读，包括：
- 主峰位置、区间、面积占比、FWHM
- 次级峰描述（如果有 ≥ 5% 面积的次峰）
- 聚集警告（区分 > 30% 的严重聚集和 > 5% 的轻微聚集）
- 均一性描述
- 宽峰提示（可能的构象异质性）
- HMW 区间的环状装配推测

`_recommend(result)` 函数会根据质量和主峰位置给出具体建议：
- Q ≥ 7 + HMW → "Priority: cryo-EM / native MS"
- Q ≥ 7 + dimer → "Use as positive control"
- 聚集 > 30% → "Redesign interface"
- polydisperse → "Buffer optimisation"

#### Compact vs Full 模式

| 维度 | `compact` | `full` |
|---|---|---|
| 汇总表范围 | 仅 primary cohort | 全部 |
| 图表 | 用 `_primary` 版本（仅含 primary） | 用全量版本 |
| 亮点展示 | 4 个代表性 construct | 所有 construct |
| 历史数据 | 单独一张表，标注"仅供参考" | 不区分 |
| 附录 | 自动生成包含全量细节的 Appendix PDF | 不生成 |
| Executive Summary | 自动生成要点 callout | 不生成 |

`_editorial_classification(result)` 为每个 construct 生成一个面向决策的短标签（而不是技术分类名），用于 compact 汇总表：

| 条件 | 标签 |
|---|---|
| HMW 主峰 + Q ≥ 7 + 聚集 ≤ 5% | "HMW lead" |
| HMW 主峰 + Q ≥ 5 + 聚集 ≤ 10% | "HMW follow-up" |
| 二聚体/单体 + Q ≥ 7 | "Best control" |
| 聚集 ≥ 15% | "Aggregation" |
| 其他 | "Mixed profile" |

### 2.4 `sec_report_pdf.py` — fpdf2 备用渲染器

这是 Typst 不可用时的完整兜底方案。它不调用 `report-template`，而是直接用 `fpdf2` 库从零构建 PDF。

它重现了 Typst 报告的所有章节结构（标题页、汇总表、背景、方法、逐 construct 结果、讨论、结论），但排版风格不同：
- 深蓝色头 (RGB 41, 65, 122)，白色文字
- DejaVu Sans 字体（从 matplotlib 数据目录加载）
- 交替行颜色的表格
- 支持 compact/full 双模式
- 支持独立生成 appendix PDF

---

## 3. `report-template` Skill：排版引擎详解

### 3.1 组件结构

```
container/skills/report-template/
├── SKILL.md                              # Skill 定义
├── report_builder.py                     # Python API
└── templates/
    └── scientific_report.typ             # Typst 样式模板
```

### 3.2 `ReportBuilder`：Python 构建器

`ReportBuilder` 是一个 dataclass，提供链式调用 API 来组装报告内容：

```python
report = ReportBuilder(
    title="SEC Analysis Report",
    subtitle="...",
    author="BioClaw",
)
report.heading(1, "Background")      # 一级标题
report.text("正文段落...")            # 段落
report.table(headers, rows, caption)  # 表格
report.image("figures/plot.png")      # 图片
report.callout("重要发现", kind="success")  # 提示框
report.metric_cards([...])            # 指标卡片
report.compile("output/report.pdf")   # 编译为 PDF
```

内部工作原理：

1. 每次调用 `heading()`, `text()`, `table()` 等方法时，将对应的 **Typst 标记** 追加到内部列表 `_parts`
2. 调用 `compile()` 时：
   - 创建临时目录
   - 将 `scientific_report.typ` 模板复制进去
   - 将 `_image_dir` 下的所有图片复制进去
   - 生成一个 `report.typ` 文件，内容为：`#import "template_lib.typ": *` + `#show: report-setup.with(...)` + 所有 `_parts`
   - 调用 Typst 编译器将 `report.typ` → PDF
   - 返回 PDF 路径

`T` 类提供了一组静态方法，返回原始 Typst 标记字符串，用于需要更精细控制的场景（如 `sec_report_typst.py` 中的复杂表格构建）。

### 3.3 `scientific_report.typ`：Typst 样式模板

这个文件定义了报告的全部视觉风格和可复用组件，由 Typst 标记语言编写。

#### 配色方案

| 名称 | 色值 | 用途 |
|---|---|---|
| primary | `#1a5276`（深海军蓝） | 一级标题背景、表头背景、标题文字 |
| accent | `#148f77`（青绿） | 二级标题、元数据键名、指标卡顶边 |
| light-bg | `#f0f4f5` | 表格隔行背景、元数据行背景 |
| note-bdr | `#17a2b8` | Note callout 左边框 |
| warn-bdr | `#ffc107` | Warning callout 左边框 |
| ok-bdr | `#28a745` | Success callout 左边框 |
| err-bdr | `#dc3545` | Danger callout 左边框 |

#### 页面设置

- **纸张**：A4
- **页边距**：上 2.45cm，下 2.2cm，左右各 2.0cm
- **字体**：Liberation Sans / Arial / Noto Sans / DejaVu Sans，9.8pt，两端对齐
- **页眉**（第 2 页起）：左=报告标题，右=日期 | 密级，底部有细线
- **页脚**：左="Generated by BioClaw"，右="Page X of Y"，顶部有细线

#### 标题层级样式

| 层级 | 样式 |
|---|---|
| H1 `= Title` | 全宽深蓝底块，白色粗体 13pt，上方 10pt 间距，下方 4pt |
| H2 `== Subtitle` | 青绿色 11.5pt 粗体，下方浅青绿色下划线 |
| H3 `=== Item` | 深蓝色 10.5pt 粗体 |

#### 组件函数

| 函数 | 效果 |
|---|---|
| `#callout(body, title, kind)` | 带彩色左边框（4pt）和浅色背景的提示框，可跨页 |
| `#data-table(headers, rows)` | 深蓝表头 + 隔行变色的表格，**不包裹在 figure() 中**（避免跨页时留白整页） |
| `#metadata-block(pairs)` | 圆角边框内的键值对列表，键名用 accent 色，35%:65% 分栏 |
| `#metric-cards(metrics)` | 指标卡片网格，顶部 accent 色边框，大号数值 + 小号标签 |

### 3.4 Typst 编译策略

`ReportBuilder.compile()` 有两级回退：

```
优先：import typst (Python 包)
  ↓ 不可用
回退：调用 typst CLI 二进制 (subprocess)
  ↓ 不可用
抛出 ImportError，由 sec_pipeline.py 决定是否再回退到 fpdf2
```

---

## 4. 完整数据流：从上传到 PDF

下面用一个具体例子走通整条链路。假设用户上传了一个 `SEC_data.zip`。

```
用户上传 SEC_data.zip 并发消息："分析这个 SEC zip 并生成 PDF 报告"
                │
                ▼
┌──────────────────────────────────────────────────────┐
│ agent-runner/src/task-routing.ts                      │
│                                                       │
│ extractLatestUserMessage() 提取最新用户消息            │
│ extractWorkspacePaths() 提取上传文件路径               │
│ looksLikeSecReportRequest() 启发式判断：               │
│   domainPatterns: "SEC" → 命中                        │
│   analysisPatterns: "分析", "报告" → 命中             │
│   hasUploadSignal: .zip 文件 → 命中                   │
│ → 判定为 SEC 报告任务                                  │
│                                                       │
│ detectTaskRouting() 生成强制性系统指令块，注入 agent：   │
│   - 必须读 SKILL.md                                    │
│   - 必须先发 SEC Analysis Plan                         │
│   - 必须运行 sec_pipeline.py                           │
│   - 禁止手写分析脚本                                   │
│   - 禁止手工拼 PDF                                     │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│ 容器内 agent 执行 SKILL.md 中的步骤                    │
│                                                       │
│ Step 1: pip install typst fpdf2                       │
│ Step 2: 定位上传文件                                   │
│ Step 3: 运行 sec_pipeline.py --input ... --output ... │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│ sec_pipeline.py [1/5] 输入解析                        │
│                                                       │
│ 检测到 .zip → 解压到 output/_extracted/               │
│ discover_files() 扫描目录树：                          │
│   - 按扩展名分类数据文件和图片                          │
│   - 过滤校准文件、汇总表、hidden 文件                   │
│   - 去重：raw 优先于 normalized_curve                  │
│ 结果：12 个数据文件 + 4 张图片                         │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│ sec_pipeline.py [2/5] 逐样品分析                      │
│                                                       │
│ 对每个数据文件（循环 12 次）：                          │
│   SECDataParser.parse(file)                           │
│     → volumes[], absorbance[]                         │
│   截取 SEC 范围（0–28.8 mL）                          │
│   SECPeakAnalyzer.detect(volumes, absorbance)          │
│     → 平滑 → find_peaks → peak_widths → valley 分区   │
│     → List[SECPeak]                                   │
│   SECPeakAnalyzer.assess(peaks)                       │
│     → quality_score, homogeneity, aggregation, dominant│
│   match_image() 匹配对应的原始色谱图图片               │
│   SECPlotter.plot_chromatogram()                      │
│     → figures/<name>_annotated.png                    │
│                                                       │
│ assign_cohorts(results)                               │
│   → 扫描路径年份，标记 primary / context               │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│ sec_pipeline.py [3/5] 比较图                          │
│                                                       │
│ 全量图（所有 construct）：                              │
│   comparison_overlay.png                               │
│   zone_fractions.png                                   │
│   individual_grid.png                                  │
│   ranking_summary.png                                  │
│                                                       │
│ Primary-only 图（compact 模式，仅 primary cohort）：   │
│   comparison_overlay_primary.png                       │
│   zone_fractions_primary.png                           │
│   ranking_summary_primary.png                          │
│   selected_grid.png (4 个代表性 construct)             │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│ sec_pipeline.py [4/5] PDF 报告                        │
│                                                       │
│ _build_sec_report() 选择渲染器：                       │
│                                                       │
│   renderer=auto?                                      │
│   ├── 尝试 Typst：                                    │
│   │   sec_report_typst.build_typst_report()           │
│   │     → ReportBuilder (from report-template)         │
│   │     → 组装 5 大章节 + 图表 + 解读文字              │
│   │     → report.compile()                             │
│   │       → 生成 .typ 源码 + 复制模板/图片到临时目录    │
│   │       → Typst 编译 → SEC_Analysis_Report.pdf       │
│   │   成功 → 完成                                      │
│   │                                                    │
│   └── Typst 失败：                                     │
│       sec_report_pdf.SECReportPDF.build()              │
│         → fpdf2 直接构建 PDF                           │
│         → SEC_Analysis_Report.pdf                      │
│         → 记录 fallback_used=true, fallback_reason     │
│                                                       │
│ compact 模式下额外生成附录：                            │
│   _build_sec_appendix()                               │
│     → SEC_Analysis_Appendix.pdf                       │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│ sec_pipeline.py [5/5] JSON 摘要                       │
│                                                       │
│ 写入 analysis_summary.json，包含：                     │
│   - 所有 construct 的峰数据和评分                      │
│   - renderer / requested_renderer / fallback_used      │
│   - report_profile                                     │
│   - selected_constructs (代表性子集)                    │
│   - appendix_path                                      │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│ agent 回到 SKILL.md 的后续步骤                         │
│                                                       │
│ Step 4: send_image → SEC_Analysis_Report.pdf          │
│ Step 5: send_image → ranking_summary.png              │
│ Step 6: 在聊天中总结关键发现                            │
└──────────────────────────────────────────────────────┘
```

---

## 5. 渲染器回退链

整个系统有三级渲染回退，确保始终能产出 PDF：

```
第一级：Python typst 包 (import typst)
  │
  │ 不可用（未安装或编译失败）
  ▼
第二级：typst CLI 二进制 (shutil.which("typst"))
  │
  │ 不可用（PATH 中找不到）
  ▼
第三级：fpdf2 (sec_report_pdf.py)
  │
  │ 不可用（未安装）
  ▼
报错退出
```

前两级由 `report_builder.py` 的 `compile()` 方法内部处理。第三级由 `sec_pipeline.py` 的 `_build_sec_report()` 在捕获异常后触发。

当 `--renderer=auto` 时走完整回退链。当 `--renderer=typst` 时，Typst 失败即报错，不回退。当 `--renderer=fpdf2` 时，直接跳过 Typst。

`analysis_summary.json` 中的 `renderer`、`requested_renderer`、`fallback_used`、`fallback_reason` 字段记录了实际使用的渲染路径，便于排查 PDF 质量问题。

---

## 6. 自动任务路由

### 6.1 路由在哪里运行

路由逻辑在 `container/agent-runner/src/task-routing.ts` 中，运行在**容器内的 agent-runner** 里，发生在 agent 开始执行任务之前。

### 6.2 判定逻辑

`looksLikeSecReportRequest()` 用启发式规则三重检测：

| 维度 | 要求 | 检测方式 |
|---|---|---|
| 领域信号 | ≥ 2 个命中 | 正则匹配：`\bsec\b`, `size-exclusion`, `chromatograph`, `oligomer`, `protein assembly`, `gel filtration` |
| 分析信号 | ≥ 1 个命中 | 正则匹配：`analyse`, `analysis`, `report`, `pdf`, `generate`, `classification` |
| 上传信号 | 至少 1 个 | 存在 `.zip/.csv/.tsv/.xlsx` 路径，或有 `Uploaded file:` / `Workspace path:` 标记 |

三个维度**同时满足**才触发。此外有一条快捷路径：如果用户消息直接包含 "sec report" 或 "size-exclusion...report" 或 "chromatograph...report"，直接触发，无需三重检测。

### 6.3 路由注入的内容

一旦触发，`detectTaskRouting()` 生成一段强制性系统指令，追加到 agent 的 prompt 中，包含：

- 检测到的输入文件路径列表
- 完整的 6 步执行流程（读 SKILL.md → 发 plan → 运行 pipeline → 发 PDF → 发 ranking 图 → 总结）
- 明确的禁止事项列表（不得手写脚本、不得手工拼 PDF）

### 6.4 为什么需要路由

没有路由时，agent 看到 ZIP 文件倾向于自己写一次性分析脚本。这导致：
- 报告格式每次不一致
- 缺少系统性文字分析（只有图）
- 缺少标准化评分和分类
- 生成的 PDF 只是图片堆砌，不像正式报告

路由强制将 SEC 任务导入标准化 pipeline，确保输出质量的一致性。

---

## 7. 输出物总览

默认输出目录为 `/workspace/group/sec_analysis/output/`。

```
sec_analysis/output/
├── SEC_Analysis_Report.pdf           # 主报告（compact 约 14+ 页）
├── SEC_Analysis_Appendix.pdf         # 附录（仅 compact 模式，含全量逐 construct 细节）
├── analysis_summary.json             # 机器可读结果 + renderer 元数据
└── figures/
    ├── <name>_annotated.png          # 逐 construct 注释色谱图（每个样品一张）
    ├── comparison_overlay.png        # 全量归一化叠加图
    ├── comparison_overlay_primary.png # Primary cohort 叠加图 [compact]
    ├── zone_fractions.png            # 全量区间占比柱状图
    ├── zone_fractions_primary.png    # Primary cohort 区间占比 [compact]
    ├── individual_grid.png           # 全量多面板网格
    ├── selected_grid.png             # 代表性 construct 网格 [compact]
    ├── ranking_summary.png           # 全量质量排名
    └── ranking_summary_primary.png   # Primary cohort 质量排名 [compact]
```

### `analysis_summary.json` 结构

```json
{
  "generated": "2026-04-16T...",
  "n_constructs": 12,
  "void_volume_mL": 8.0,
  "report_profile": "compact",
  "renderer": "typst",
  "requested_renderer": "auto",
  "fallback_used": false,
  "fallback_reason": null,
  "appendix_path": ".../SEC_Analysis_Appendix.pdf",
  "selected_constructs": ["Ring_01", "Dimer_03", "Mixed_07", "Agg_05"],
  "constructs": [
    {
      "name": "Ring_01",
      "quality_score": 8.5,
      "homogeneity": "predominantly_monodisperse",
      "has_aggregation": false,
      "aggregation_pct": 0.0,
      "dominant_species": "large_oligomer",
      "cohort": "primary",
      "cohort_year": 2026,
      "peaks": [
        {
          "peak_number": 1,
          "elution_volume_mL": 9.2,
          "height_mAU": 42.5,
          "fwhm_mL": 1.1,
          "relative_area_pct": 85.3,
          "classification": "large_oligomer",
          "confidence": "medium"
        }
      ]
    }
  ]
}
```

---

## 8. 运行参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--input` | （必填） | 输入 ZIP、目录或单个数据文件 |
| `--output` | （必填） | 输出目录 |
| `--void-volume` | `8.0` | SEC 柱空隙体积 (mL)，默认 Superdex 200 10/300 GL |
| `--report-profile` | `compact` | `compact`（精简主报告 + 附录）或 `full`（传统全量报告） |
| `--renderer` | `auto` | `auto`（Typst 优先，fpdf2 兜底）、`typst`（仅 Typst）、`fpdf2`（仅 fpdf2） |

---

## 9. 容器环境依赖

`container/Dockerfile` 中新增了以下 Python 包：

- `typst`：Typst 编译器的 Python 绑定
- `fpdf2`：纯 Python PDF 生成库

这些是 `sec-report` 和 `report-template` 正常工作所必需的。如果容器中未预装，SKILL.md 的 Step 1 会在运行时 `pip install`。

---

## 10. 测试

### 10.1 任务路由单元测试

文件：`tests/container-agent-runner/task-routing.test.ts`

测试内容：
- 从网页端 prompt 中正确提取 workspace 路径
- 正确识别 SEC 报告请求
- 不会把普通 "security report" 误判为 SEC
- 正确注入强制性系统指令

### 10.2 SEC Pipeline 端到端测试

文件：`container/skills/sec-report/tests/run_test.sh`

测试内容：
- 生成合成 SEC 数据
- 分别测试目录输入和 ZIP 输入
- 验证 PDF、JSON、figures 是否都生成
- 检查 JSON 中的 renderer 元数据
- 检查 compact 报告页数 < full 报告页数
- 验证 PDF 页面尺寸为 A4

---

## 11. Guardrails

`sec-report` SKILL.md 中定义了以下科学审慎性约束：

- **禁止**在没有校准曲线的情况下给出绝对分子量
- **禁止**仅凭 SEC 就声称确定了寡聚态
- **必须**使用保守语言："apparent"、"consistent with"、"suggests"
- **必须**明确标注不确定性
- **必须**推荐正交验证方法（SEC-MALS、AUC、cryo-EM、native MS）

---

## 12. 一句话总结

`sec-report` 是一个包含数据解析、峰检测、质量评分、cohort 分组、代表性选择、自动文字生成的完整 SEC 分析引擎；`report-template` 是一个通用的 Typst 报告排版引擎，提供 Python API 和学术风格模板。两者通过 `ReportBuilder` API 连接：`sec-report` 调用 `report-template` 将分析结果编排成 PDF。自动任务路由确保 SEC 类请求始终走标准化 pipeline 而不是让 agent 临时手写。
