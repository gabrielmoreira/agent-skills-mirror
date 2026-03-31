---
name: gemini-diagram-prompt-zh
description: "PaperBanana-inspired (Retriever→Planner→Stylist→Critic) prompt-only workflow that outputs ONE paste-ready Gemini Web prompt for: (1) a publication-ready methodology diagram, or (2) a publication-ready plot via Python (pandas+seaborn+matplotlib). Chinese/English in-figure text. No API calls."
---

# Gemini 学术图提示词生成 v2（diagram + plot｜中文/English｜PaperBanana 深度复刻）

## 目标与约束

目标：
- `diagram`：把用户粘贴的 **Methodology** 与 **Figure Caption** 转化为一段**详细的自然语言图描述 + 精确视觉参数**，可直接粘贴到 Gemini Web 生成白底、矢量感、论文级的方法/框架图。
- `plot`：把用户粘贴的 **Raw Data** 与 **Figure Caption** 转化为一段**绘图描述 + 代码规格**，可直接粘贴到 Gemini Web 让其**只输出**一段可运行的 `Python (pandas + seaborn + matplotlib)` 脚本，导出论文级 `PDF/SVG` 矢量图。

约束：
- **不调用任何外部 API**。
- 对用户：只输出 **一段**最终提示词（+ 使用提示）；不输出解释、不输出多候选版本。
- 缺信息时：最多只问 **1 个问题**。
- 核心思路：用"启发式模板检索（Retriever）→ 自然语言详细描述（Planner）→ NeurIPS 风格量化（Stylist）→ 结构化自检修订（Critic）"生成**高质量 description**。PaperBanana 的 Visualizer 提示词极简（一句话），因为所有智能前置到 description 质量中——本 Skill 遵循同一哲学。

## 用户输入格式

字段顺序随意；未写就自动推断：

```
任务类型: diagram | plot                    （可选，自动推断）
参考图: <上传1张优秀的论文图截图>             （可选，仅用于风格迁移，不复刻内容）
领域: Agent/LLM | 视觉/CV/3D | 理论/优化 | 其他  （可选，自动推断）
图型: <见下方子类型>                         （可选，自动推断）
宽高比: 16:9                                （可选，默认16:9）
语言: 中文 | English                         （可选，默认中文）

Figure Caption: <一句话图注/意图>

Methodology:                                 （diagram 时提供）
<方法部分全文（可 Markdown）>

Raw Data:                                    （plot 时提供）
<CSV/TSV、Markdown 表格、或 JSON records>
```

图型子类型：
- Diagram：流程/管线 | 系统框架 | 训练-推理泳道 | 模块放大 | 对比/消融
- Plot：柱状图 | 折线图 | 散点图 | 热力图 | 雷达图 | 甜甜圈图 | 组合图

自动推断规则：
- 提供 `Raw Data` ⇒ 默认 `plot`；提供 `Methodology` ⇒ 默认 `diagram`
- 两者都提供且未显式指定 ⇒ 只问 1 个问题：你这次要生成 `diagram` 还是 `plot`？

语言规则：
- 默认 `中文`。`diagram` 的图内文字按 `语言` 输出：中文用**简体中文**为主；允许常见缩写与数学符号（首次出现写成"中文（缩写）"，例如"大语言模型（LLM）""损失 \mathcal{L}""变量 x"）。
- `plot` 的轴标签/图例/注释按 `语言` 输出；若无法可靠翻译（例如列名语义不清），保留原列名，禁止胡乱翻译。

### 常用术语（建议写法）

- 编码器（Encoder）、解码器（Decoder）、主干网络（Backbone）、任务头（Head）
- 特征提取（Feature Extraction）、特征融合（Fusion）、注意力模块（Attention）
- 数据增强（Augmentation）、归一化（Normalization）、采样器（Sampler）
- 检索器（Retriever）、检索增强生成（RAG）、知识库（Knowledge Base）
- 记忆库（Memory）、工具调用（Tool Use）、规划器（Planner）、批判器（Critic）
- 监督信号（Supervision）、损失函数（Loss \mathcal{L}）、优化器（Optimizer）
- 训练（Training）、推理（Inference）、部署（Deployment）

---

## NeurIPS 2025 Style Guide（源自 PaperBanana style_guides/）

> 以下规则在 Step 3（Stylist）中使用，确保生成的 Description 符合顶会审美标准。

### 总体美学：Soft Tech & Scientific Pastels

2025 年的审美核心：**高明度背景用于组织结构，高饱和色严格保留给关键元素**。拒绝刺眼的原色和粗黑边框。整体追求"干净模块化"与"叙事流"的平衡。

### 形状语义规则

**核心原则："尖角用于数据，圆角用于处理"**

| 形状 | 用途 | 占比 |
|------|------|------|
| 圆角矩形（r=5-10px） | 处理节点（Encoder/MLP/Attention/任何计算步骤） | ~80% |
| 3D 堆叠/立方体 | 张量/特征图（暗示 B×H×W 维度深度） | 需要时 |
| 扁平方格/网格 | 矩阵、token 序列、注意力图 | 需要时 |
| 圆柱体 | **仅用于**数据库/缓冲区/记忆存储 | 严格 |

分组与层级（"宏观-微观"模式）：
- 浅色大容器展示全局视图；通过连线链接到放大的细节框
- 实线边框 = 物理组件
- 虚线边框 = 逻辑阶段/可选路径/作用域（极常见）

### 图标语义约定

**模型状态图标**（语义约定，不可随意替换）：
- 可训练 / 正在训练：🔥火焰 / ⚡闪电（暖色调：红/橙/深粉）
- 冻结 / 不可训练：❄️雪花 / 🔒锁 / 🛑停止标志（冷色调：灰/冰蓝/青，灰化处理）

**操作图标**：
- 检索/搜索：🔍放大镜
- 处理/计算：⚙️齿轮 / 🖥️显示器
- 文本/提示：📄文档 / 💬聊天气泡
- 图像：🖼️实际缩略图（而非简单方块）

**使用原则**：
- 每个关键模块最多 1 个小图标
- 图标必须服务语义，禁止纯装饰
- 技术约定类图标（雪花=冻结、火焰=可训练）遇到时，必须参考原文 Methodology 确认语义再决定
- 纯装饰/象征性图标可自由美化
- Agent 论文可用可爱 2D 矢量机器人头像/人物头像表示 agent
- 禁止：Logo / 水印 / 作者标识 / 独特插画角色

### 调色板

**Zone 策略（背景填充分区）**——极浅柔和粉彩，10-15% 不透明度：

| 色调 | HEX | 适用感觉 |
|------|-----|---------|
| Cream/Beige | `#F5F5DC` | 温暖学术感 |
| Pale Blue/Ice | `#E6F3FF` | 干净技术感 |
| Mint/Sage | `#E0F2F1` | 柔和有机感 |
| Pale Lavender | `#F3E5F5` | 现代独特感 |

约 20% 的论文用白底 + 彩色虚线边框替代（极简高对比，多见于理论论文）。

**功能性颜色编码**——颜色编码**状态**而非组件类型：
- 可训练元素：暖色调（红/橙/深粉）
- 冻结/静态元素：冷色调（灰/冰蓝/青）
- 高饱和色（原色红/亮金）**严格保留给**：Error/Loss 信号、Ground Truth、最终输出

**推荐默认调色板**（无参考图时）：
- 深灰线条/文字：`#111827`
- 主强调色：`#2563EB`（蓝）
- 次强调色：`#10B981`（绿）
- 分区底色：由强调色取高亮度+低饱和版本

**有参考图时**：从参考图中估计 3-6 个 HEX 值替换上述默认。

### 连线语义

**走线风格暗示含义**：
- **正交/肘形（直角折线）**：网络架构图首选（暗示精密、工程感）
- **曲线/贝塞尔**：系统逻辑图、反馈循环、高层数据流（暗示叙事）

**线型语义**（业界普遍约定）：
- **实线黑/灰**：标准前向传播数据流
- **虚线**：**普遍认定为"辅助流"**——梯度更新、跳连接、损失计算、可选路径
- **颜色编码**：可用强调色区分不同语义的流

**数学算子**放置：
- ⊕（Add）、⊗（Concat/Multiply）等直接放在连线或交叉点上
- 不要写成独立的处理节点

**推荐默认参数**：
- 线宽：`1.8–2.0px`
- 箭头头部宽度：≈线宽×4
- 虚线：`dash 6px / gap 4px`
- 折线转角：直角或轻微圆角

### 排版规则

**核心原则：标签用无衬线，数学变量用衬线斜体**

- 模块标签（"Encoder""注意力模块"）：**无衬线字体**（Arial/Roboto/Helvetica），粗体表头，常规体细节
- 数学变量（x, θ, \mathcal{L}）：**衬线字体**（Times New Roman/LaTeX），**必须斜体**
- 严禁混用：用衬线字体写 "Encoder" 被视为"1990 年代风格"的标志

**字号层级**：
- 主标签：18-22pt（加粗或半粗）
- 副标签：12-14pt
- 连线注释：11-12pt
- 行距紧凑，留白充足；单个框内文字不超过 3 行

### 领域风格

**Agent/LLM**（更"UI 叙事"，但保持学术干净）
- 风格：illustrative, narrative, 友好
- 允许使用：对话气泡（提示/指令）、文档/检索（RAG）、工具/插件（工具调用）、记忆/数据库（圆柱体）、可爱 2D 矢量机器人头像
- 常用布局：输入→（检索/记忆）→智能体编排→工具调用→输出
- 多角色/多代理：并行小框或泳道，最后汇聚到输出

**视觉/CV/3D**（更"几何/张量/模块化"）
- 风格：spatial, dense, 几何感
- 允许使用：特征图/张量（网格或 stack）、相机锥体/点云/体素的简洁几何符号、RGB 编码
- 常用布局：Backbone→Neck→Head；旁路展示损失/监督/后处理
- 连线建议更多用直角/折线，显得更"工程精密"

**理论/优化**（极简、结构优先）
- 风格：minimalist, abstract, "教科书"感
- 颜色：灰度为主 + 单强调色（金或蓝）
- 元素：图节点（圆形）+ 流形（平面/曲面）+ 关键变量/算子
- 连线：尽量直角/简洁；避免图标与装饰

**自动推断**（若用户未提供 `领域:`）：
- prompt/agent/tool/retrieval/memory/chat ⇒ Agent/LLM
- image/feature/encoder/backbone/3D/point cloud/camera ⇒ 视觉/CV/3D
- convex/optimization/theorem/gradient descent/proof ⇒ 理论/优化

### Plot 专属 Style Guide

**总体**：precision, accessibility, high contrast。白底用于印刷/PDF 对比度；浅灰（Seaborn 式）可接受。

**调色板**：
- 分类变量：柔和粉彩（salmon/sky blue/mint/lavender）或哑光大地色（olive/beige/slate grey/navy）
- 连续/热力图：Viridis / Magma / Plasma 为标准；Coolwarm 用于发散数据。**禁止 Jet/Rainbow**
- 无障碍：数据必须同时用纹理/形状区分，不能仅靠颜色

**网格与坐标轴**：
- 网格：细虚线（`--`）或点线（`:`），浅灰色，始终在数据后面
- 坐标轴：可"四面封闭"或"开放式"（移除上/右轴线）
- 刻度：subtle, 朝内，或完全移除

**按图型的专属规则**：

| 图型 | 关键规则 |
|------|---------|
| 柱状图 | 组内紧凑，组间留白；误差线统一黑色平帽；可加黑色描边 |
| 折线图 | **几乎总是**需要几何标记点（圆/方/菱形）；虚线=baseline/理论极限，实线=实验数据；不确定性用**半透明填充带**而非误差线 |
| 散点图 | 不同标记形状编码分类维度（配合颜色）；标记实心不透明 |
| 热力图 | 单元格**严格正方形**；内写精确数值（白或黑字）；无边框或极细白线分隔 |
| 雷达图 | 半透明多边形填充（alpha ~0.2）；外边界用实心深色线 |
| 甜甜圈图 | 优于传统饼图；厚白色边框分隔切片；可"爆开"一个切片强调 |
| 组合图 | 使用 subplot 或 facet；各子图共享坐标轴风格 |

**排版**：
- 字体：exclusively 无衬线（Helvetica/Arial/DejaVu Sans）
- 标签旋转：45° 仅在防重叠时使用，优先水平
- 图例：图内（左上/右上）或横排在上方
- 直接标注在线/柱上优于强制引用图例

**避免的坑**（"Excel 默认风"）：
- 3D 效果 / 阴影 / 衬线字体轴标签
- Jet/Rainbow 色图
- 折线图无标记点
- 仅靠颜色区分（需纹理/形状辅助）
- 粗实线网格

---

## 输出规则（必须严格遵守）

- 只输出 **一段**"可直接粘贴到 Gemini Web"的最终提示词 + 使用提示
- 不输出解释、不输出多候选版本
- `diagram`：**不要把 Methodology 原文粘进最终提示词**（避免 Gemini 把长段文字画进图里），只输出你生成的 Figure Description + Visual Spec
- `plot`：必须把 `Raw Data` **原样包含**在最终提示词中，并要求 Gemini 把它**嵌入脚本字符串并解析**

---

## 工作流（执行时在脑中完成，不要暴露推理过程）

### Step 0: 缺信息检查

当缺少关键信息导致无法可靠生成时，只问 **1 个**最关键问题再继续（其余缺失信息用默认值补齐）：
- 若无法判断要做 `diagram` 还是 `plot`：**"你这次要生成方法/框架图（diagram）还是数据图（plot）？"**
- 若为 `diagram` 且无法判断阶段：**"你要画的是训练流程、推理流程，还是整体系统框架图？"**
- 若为 `plot` 且无法判断映射：**"plot 的 x 轴用哪一列？y 轴用哪一列（或哪些列）？"**

### Step 1: Retriever（启发式"检索"＝选择最合适的模板/图型）

优先级：用户显式给的 `任务类型` / `图型` > 关键词与（plot 的）数据形状匹配 > 默认。

默认值：
- `diagram`：默认图型 `流程/管线`
- `plot`：默认图型 `柱状图`（论文里更常见、更可读）

#### Diagram 图型匹配（择一为主）

- 出现 预训练/微调/蒸馏/优化器/梯度/参数更新/在线/离线/部署/推理 ⇒ `训练-推理泳道`
- 强调整体组成（Backbone/Encoder/Decoder/Head/Adapter/Router/MoE） ⇒ `系统框架`
- 典型 step-by-step、pipeline、数据处理→建模→输出 ⇒ `流程/管线`
- 出现 "模块细节/放大/zoom-in/attention block" ⇒ `模块放大`
- Caption 明确 compare/ablation/baseline ⇒ `对比/消融`（方法主图为主体，对比放侧栏）

#### Plot 图型匹配（择一为主，优先论文常用）

- 含"准确率/精度/召回/F1/loss/epoch/step/iter/训练曲线/时间" ⇒ `折线图`
- 含"对比/模型比较/消融实验/baseline/百分比" ⇒ `柱状图`
- 含"相关性/分布/聚类/二维投影/embedding" ⇒ `散点图`
- 含"混淆矩阵/注意力权重/相似度/相关矩阵"，或数据呈矩阵网格 ⇒ `热力图`
- 含"多维评估/能力雷达/多指标对比（≥3 维）" ⇒ `雷达图`
- 含"占比/组成/份额"且用户明确要求 ⇒ `甜甜圈图`（否则优先改成柱状图）
- 需要多子图/多任务并排/多数据源对齐 ⇒ `组合图`（subplot 或 facet）

### Step 2: Planner（生成自然语言 Figure Description）

> 核心步骤。PaperBanana 的 Planner 要求："Your description should be as detailed as possible. Semantically, clearly describe each element and their connections. Include various details such as background style, colors, line thickness, icon styles. Vague or unclear specifications will only make the generated figure worse."

#### 2.1) diagram：生成详细的 Figure Description

把 Methodology + Caption 转化为一段**详细的自然语言描述**，像写给专业插画师的设计 brief。必须包含：

**内容层面**（从 Methodology 提取，用 Caption 约束范围）：
- 整体结构：几个阶段/分区？从左到右的主线叙事是什么？
- 逐模块描述：每个模块的功能、在图中的位置、与前后模块的关系
- 数据流：什么数据从哪流到哪？经历了什么变换？
- 训练要素（若存在）：损失函数、监督信号、优化目标、参数更新路径
- 可选/条件分支（若存在）：何时触发、如何表示

**视觉层面**（必须补齐，不能留空——模糊的规格只会让生成结果更差）：
- 每个模块的形状（遵循形状语义规则）、大致填充色、描边色
- 每条连线的起终点、线型（实线/虚线）、语义（数据流/梯度/可选）
- 分区/泳道的布局方式、底色
- 关键图标（遵循图标语义约定，每模块最多 1 个）
- 整体从哪个方向阅读（默认左→右）

**禁止**：
- 不要把 Methodology 原文段落粘进 Description
- 不要在 Description 中写"图1""Figure 1"或任何标题/图注
- 不要引入 Methodology 中不存在的模块（幻觉）

#### 2.2) plot：生成 Plot Description

把 Raw Data + Caption 转化为一段自然语言描述，说明图的视觉设计：

- 选择此图型的理由（简要）
- 变量→视觉通道的映射：x/y/hue/style/facet/排序
- 预期的视觉效果：颜色分组如何帮助对比、标记点如何辅助阅读
- 特殊处理需求：是否需要旋转刻度、外置图例、使用 facet/subplot
- 数据保真声明：明确指出只用 Raw Data，不臆造

### Step 3: Stylist（NeurIPS 风格量化 + Description 修润）

> PaperBanana 的 Stylist："Preserve semantic content. Preserve high-quality aesthetics and intervene only when necessary. Respect diversity. Enrich details. Handle icons with care."

#### 3.1) 应用 NeurIPS 2025 Style Guide

对 Step 2 输出的 Description 进行风格审查和量化：

- **检查形状语义**：处理节点是否用圆角矩形？数据/张量是否用方格/堆叠？数据库是否用圆柱？
- **检查图标约定**：可训练/冻结的图标是否符合约定？是否有纯装饰的无意义图标？
- **量化调色板**：把"浅蓝色""较深的绿色"替换为精确 HEX 值
- **量化几何参数**：线宽、圆角、虚线规格、箭头大小
- **量化字号层级**：主标签、副标签、连线注释
- **应用领域风格**：根据 Agent/LLM 或 CV/3D 或理论/优化的领域特点微调

#### 3.2) 参考图风格迁移（若有参考图）

- ✅ 可迁移：配色、线宽、圆角、箭头形状、虚线样式、分区底色、阴影/描边习惯、字体层级、图标风格
- ✅ 可借鉴：通用可生成小图标（文档/数据库圆柱/齿轮/放大镜/对话气泡/神经网络小块/张量 stack）
- ❌ 禁止复刻：Logo / 水印 / 作者标识 / 独特插画角色 / 原图专有模块命名与内容

从参考图提取并量化为精确参数：
- 调色板（3-6 个 HEX）：背景、文字、主强调色、次强调色、Zone 底色
- 几何（px）：描边线宽、圆角半径、虚线样式
- 排版（pt）：主标签、副标签、注释
- 图标策略：单线稿 / 双色扁平 / 填充 / illustrative

#### 3.3) Stylist 保守原则

- **保留已有的高质量美学**：如果 Planner 的描述已经包含了好的视觉设计（如 3D 图标、丰富纹理、好的色彩搭配），保留它们。只在缺乏细节或视觉过时/拥挤时才干预
- **尊重多样性**：不同领域有不同风格。如果描述中有特定风格且效果好，保留
- **审慎处理图标**：技术约定类图标（雪花=冻结）必须参考原文确认语义

### Step 4: Critic（结构化自检与修订）

> PaperBanana 的 Critic 输出 JSON：`{"critic_suggestions": "...", "revised_description": "..."}`。修改应基于原始描述的微调，而非从头重写。

输出前做 1 轮自检。在脑中生成以下 JSON（不输出给用户）：

```json
{
  "content_issues": ["问题1", "问题2", ...],
  "presentation_issues": ["问题1", "问题2", ...],
  "action": "revise" | "pass",
  "revised_description": "修订后的 Description（仅当 action=revise）"
}
```

#### Diagram Critic 检查维度

**内容轴**：
- **Fidelity & Alignment**：是否忠实反映 Methodology + Caption？合理简化可以，但不能遗漏关键组件或歪曲含义。不能包含幻觉内容。与 Methodology + Caption 的一致性始终是最重要的
- **Text QA**：是否有错别字、乱码、过长标签（>2 行）？缩写首次出现是否写成"中文（缩写）"？
- **示例验证**：若包含具体示例（分子式/注意力图/数学表达式），是否事实正确且逻辑一致？
- **Caption 排除**：图内是否意外包含"图1/Figure 1/方法概述/本图展示…"等标题性文字？

**呈现轴**：
- **Clarity & Readability**：流程方向是否清晰？布局是否拥挤混乱？是否需要结构改进？
- **图例冗余**：是否有多余的文字图例/颜色编码说明？若有则删除（PaperBanana 特别强调这一点）
- **Style 一致性**：是否白底、低饱和、线宽/字体层级统一？图标是否克制且服务语义？形状语义是否正确？

#### Plot Critic 检查维度

**数据轴**：
- **Data Fidelity & Alignment**：是否只使用 Raw Data 中的值？所有定量结果必须准确。不能幻觉/遗漏/歪曲任何数据
- **Column QA**：x/y/hue/style/facet 指定的列是否真实存在？类型是否匹配？
- **Value Validation**：所有数值、坐标轴刻度、数据点是否正确？

**代码轴**：
- **可运行**：描述是否可能导致代码执行失败？若有复杂语法或缺失数据引用，主动简化
- **产物**：是否导出 `figure.pdf` 与 `figure.svg`（tight layout）？
- **中文**：若语言=中文，是否配置字体回退并设置 `axes.unicode_minus=False`？

**可读性**：
- **Overlap & Layout**：标签/点/柱是否拥挤重叠？文字标签是否被填充/网格遮挡？必要时旋转刻度、外置图例或使用 facet/subplot
- **规范**：是否避免 3D/重阴影/高饱和渐变？是否色盲友好？

**修订原则**（与 PaperBanana 一致）：
- 修订应基于原始描述的调整，而非从头重写
- 若原始描述某部分有明显问题需要重新描述，修订后的描述应尽可能详细
- 模糊或不清楚的规格只会让生成结果更差

---

## 最终输出模板

你最终只输出下面两个模板中的 **一个**（根据 `任务类型` 选择）。`{...}` 替换成 Step 2-4 生成的具体值。

### 模板 A：diagram（生图）

````
你是一名资深学术图示绘制专家。
请根据以下详细描述生成一张高分辨率、论文发表级的学术图。

生成前请先在内部校验：
1. 内容是否忠实于 Figure Description 中列出的每个模块和连线？
2. 是否有未在描述中提及的多余元素？
3. 图内是否意外包含标题、图注或编号（如"图1""Figure 1"）？
若发现问题，在内部修正后再输出最终图像。

{若用户上传参考图，加入此段：}如果同一消息中有参考图，请只迁移其视觉风格（配色/线宽/圆角/留白/图标风格），禁止复刻参考图的具体内容、模块命名、Logo、水印或独特角色。

【Figure Description】
{Step 2-4 生成的自然语言详细描述段落：从整体结构开始，
然后逐分区/逐模块描述每个元素的外观、标签、颜色、形状、
位置、连接方式。像写给专业插画师的设计 brief，
不能有任何模糊或留空。}

【Visual Spec】
- 画布：纯白底，宽高比 {宽高比，默认16:9}
- 语言：图中所有文字使用{语言，默认中文}。若中文：简体中文，首次出现的缩写写成"中文（缩写）"；数学变量用衬线斜体
- 调色板（HEX）：文字/线条 `{默认#111827}`；主强调色 `{#2563EB}`；次强调色 `{#10B981}`；Zone 底色 `{极浅色 10-15%}`
- 几何：圆角 `{默认14}px`；线宽 `{默认1.9}px`；虚线 `dash {默认6}px / gap {默认4}px`；箭头头部宽度≈线宽×4
- 字号：主标签 `{默认20}pt` 加粗无衬线；副标签 `{默认13}pt`；连线注释 `{默认11}pt`
- 禁止：图标题/图注/编号/水印/渐变/重阴影/衬线字体标签
````

### 模板 B：plot（让 Gemini 输出 Python 脚本）

````
你是一名资深科研数据可视化工程师。
请根据以下规格生成一段可直接运行的 Python 脚本（使用 pandas + seaborn + matplotlib；可选 numpy）。

生成前请先在内部校验：
1. 脚本中的数据点数值是否与 Raw Data 完全一致？
2. 是否存在臆造/补全/猜测的数据点或列名？
3. 代码是否可自包含运行（无外部文件依赖）？
若发现问题，在内部修正后再输出最终代码。

硬性要求：
- 你必须**只输出代码**：用一个 ```python``` 代码块包裹脚本，除此之外不要任何解释文字。
- 只能使用 Raw Data：禁止臆造/补全/猜测任何数据点、列名或聚合结果。
- 脚本必须自包含：把 Raw Data 原样嵌入脚本字符串中解析（不要读外部文件）。

【Plot Description】
{Step 2-4 生成的自然语言描述：图型选择理由、变量映射、
视觉通道分配、预期效果、特殊处理}

【Plot Spec】
- 图型：{柱状图/折线图/散点图/热力图/雷达图/甜甜圈图/组合图}
- 宽高比：{宽高比，默认16:9}
- 语言：{中文/English，默认中文}
- x 轴：{列名}
- y 轴：{列名 或 列名列表}
- 分组/颜色(hue)：{列名 或 无}
- 线型/marker(style)：{列名 或 无}
- 子图(facet/subplot)：{列名 或 无}
- 排序规则：{按 x 原顺序/按数值降序/按自定义列表…}
- 标记点：{折线图几何标记（圆/方/菱形）/柱状图黑色描边/散点图实心不透明/…}
- 不确定性：{半透明填充带/误差线帽/无}（仅在 Raw Data 里存在相应列时启用）
- 图例位置：{右上/外置右侧/下方居中/图内直接标注…}
- 论文风格：seaborn context="paper"；色盲友好调色板；despine()
- 导出：figure.pdf + figure.svg（tight_layout()）
- 中文字体：{若语言=中文} Microsoft YaHei/SimHei 回退 + axes.unicode_minus=False
- 禁止：3D效果/重阴影/Figure 1/标题/Jet彩虹色图/仅靠颜色区分

Raw Data（必须原样嵌入脚本，不要改动任何字符）：
```text
{Raw Data 原文}
```
````

### 使用提示（在提示词之后输出，非提示词本身的一部分）

在输出最终提示词后，紧跟输出以下使用提示：

```
---
💡 提升效果的技巧：
1. 将上方提示词完整复制粘贴到 Gemini Web，可点击"重新生成"获取 2-3 个候选结果，挑选最佳
2. 如果结果不满意，可以把生成的图片截图和原始提示词一起发给 Gemini，要求它针对性改进
3. 若有参考图，确保参考图和提示词在同一条消息中发送
4. (diagram) Gemini 偶尔会在图中写入标题/Figure 1——如果出现，在对话中追加"请去掉图中的标题和编号"即可
```
