---
name: roundtable-debate
description: "圆桌会议 - 多子Agent协作生成高质量设计文档。触发关键词：圆桌会议、设计文档、生成设计、详细设计、架构设计、plus design、出设计、写设计、深度设计、给我出一份设计、设计评审、圆桌会议plus。输入：PBI需求、设计方案、技术选型。输出：可直接编码的设计文档。核心机制：必须使用runSubagent启动5个独立子Agent，分层执行（4并行+实施派依赖），主Agent组装设计评审文档，6个文件交付。"
---

# 🪑 圆桌会议 v2.0 - 多子Agent协作生成设计文档

通过5个独立子Agent**分层执行**，输出**可直接编码的高质量设计文档**。

> 🎯 **核心流程**：收集上下文 → 4角色并行分析 → 实施派依赖执行（参考前4个产出）→ 设计评审文档组装 → 发布到飞书（默认）→ 交付
>
> 🔴 **v2.0 核心改进**：
> 1. **分层执行** — 实施派参考前4个角色产出，天然校准质量
> 2. **KEY_OUTPUT 标记** — 前4个角色自总结关键信息，实施派精准获取
> 3. **强制检查点** — 每阶段验证文件存在，防止 subagent 不写文件
> 4. **取消核查循环** — 分层执行本身就是最好的校准，省去 40-50% 耗时

---

## 🔴 文件持久化机制（避免上下文截断，强制）

> ⚠️ **所有分析过程必须持久化到文件，不依赖上下文传递！**
>
> 🔴 **核心机制**：5个subagent的分析报告可能超过上下文限制，必须写入文件。

📖 详见 `references/workspace.md`

### 工作目录

```
{project}/.copilot-temp/roundtable-{NNN}/   # NNN = 001-999
```

### 产出文件（6个文件）

| 文件 | 来源 | 目标读者 |
|------|------|----------|
| `01-architecture.md` | 架构派🧠 subagent | 开发者 + AI编码Agent |
| `02-efficiency.md` | 效率派⚡ subagent | 开发者 + AI编码Agent |
| `03-quality.md` | 质量派🛡️ subagent | 测试人员 + 开发者 |
| `04-cost.md` | 成本派💰 subagent | 管理层 + 开发者 + coding-agent（CODING_TASK_LIST） |
| `05-implementation.md` | 实施派👨‍💻 subagent | 开发者 + AI编码Agent（核心参考）+ coding-agent（CODING_IMPL） |
| `06-design-review.md` | 主Agent组装（Phase C） | 评审会议 + 团队文档 |

> ⚠️ **01-05 由 subagent 生成，06 由主Agent从 DESIGN_REVIEW 标记组装**。
> 不使用融合 subagent（实测每次丢失内容），主Agent用 grep 精准提取。

### 🔴 关键规则

| 规则 | 说明 |
|------|------|
| **subagent必须写文件** | `create_file("${workDir}/0X-xxx.md", content)` |
| **禁止从上下文读取** | 上下文会截断，只有文件是完整的 |
| 🚫 **禁止询问删除** | 任何阶段都不得询问用户是否删除/清理工作目录或中间文件 |

---

## 🔴 必须收集项目上下文（强制，第0步）

> ⚠️ **开始设计前，必须读取相关expert skill了解现有架构**

### 0.0 检查需求返讲文档（首先执行）

在收集项目上下文之前，先确认是否有最新的需求返讲文档：

```
检查方式（按优先级）：0. 上游注入 → 如请求中含「[上游注入] 返讲文档: {path}」，直接 read_file(path)，跳过下方所有检查和 askQuestions1. 用户在请求中直接提供了返讲文档内容 → 直接使用
2. 用户提供了返讲文档路径 → 读取文件
3. 用户提到了 PBI ID → 自动检查 .copilot-temp/pbi-{ID}-review.md 是否存在
   - 存在 → 读取文件，提示用户确认："已找到 PBI {ID} 的返讲文档，是否使用？"
   - 不存在 → 进入下一步
4. 以上都没有 → 使用 ask_questions 对话框询问用户：
   - header: "返讲文档"
   - question: "是否有最新的需求返讲文档？"
   - 选项A: "有，我提供内容或文件路径"  (allowFreeformInput: true)
   - 选项B（推荐）: "没有，直接基于 PBI 描述进行设计"
```

> 将返讲文档内容（如有）作为 `contextBlock` 的一部分，注入后续所有 subAgent prompt。

### 0.0b 需求澄清状态检查（ask_questions 引导）

**获取到返讲文档后**，按以下优先级检查待确认问题：

**上游短路**：如请求中含「[上游注入] 澄清状态: 全部已确认」→ 跳过此步骤。含「[上游注入] 澄清状态: {N}条待确认(用户已接受风险)」→ 记录为 accepted_risk 并跳过 askQuestions。

**检测方式（优先级从高到低）**：
1. **结构化标记**（优先）：搜索 `CLARIFICATION_LIST_START` 标记 → 解析表格中状态为 `🔴待确认` 的行 → 精确统计未确认数量
2. **文本搜索**（降级）：无结构化标记时，搜索「待确认」「待澄清」「需与 PM 确认」关键词

如果发现未澄清问题，使用 `ask_questions` 对话框提醒用户：

```
header: "需求澄清"
question: "检测到返讲文档中有 {N} 个待确认问题（{M} 个已确认）：\n\n[列出🔴待确认的问题，含 ID]\n\n⚠️ 未澄清的需求问题可能导致设计方案偏离实际需求，建议先与 PM/相关人士沟通确认。"
options:
  - label: "这些问题已经确认过了，继续设计"
    description: "口头/线下已确认但文档未更新，可以继续"
  - label: "跳过，基于当前理解出设计"
    description: "接受风险，后续有偏差再修订"
    recommended: true
  - label: "暂停，我先去确认这些问题"
    description: "先与 PM 沟通，确认后再启动圆桌会议"
```

> 🔴 如果没有待确认问题（全部已确认或无问题），或者用户没有提供返讲文档，跳过此步骤。

### 0.1 检测修订模式

检查同 PBI 是否已有圆桌会议产出：

1. 执行 `list_dir("{projectRoot}/.copilot-temp")`，筛选以 `roundtable-` 开头的目录
2. 如果存在这样的目录，对每个目录：
   - 执行 `read_file("{目录}/01-architecture.md", 1, 10)` 读取文件头几行
   - 检查文件内容是否包含当前 PBI ID
   - 如果匹配 → 发现同 PBI 已有产出，进入**修订模式**
3. 如果没有匹配 → **首次模式**，分配新编号

**修订模式 vs 首次模式**：

| 项目 | 首次模式 | 修订模式 |
|------|---------|----------|
| 工作目录 | 新建 `roundtable-{NNN+1}` | 复用已有目录 |
| 执行流程 | Phase A → B → C → D 完整执行 | 定向修改受影响文档 |
| 触发方式 | 默认 | 检测到同 PBI 已有产出时自动询问 |

**修订模式询问**（使用 ask_questions 对话框）：

先向用户展示已有产出文档列表，然后弹出对话框：
```
检测到 PBI {id} 已有圆桌会议产出（{workDir}），包含以下文档：
- 01-architecture.md
- 02-efficiency.md
- ...
```

ask_questions 参数：
- header: "修订模式"
- question: "检测到同 PBI 已有圆桌会议产出，请选择操作方式"
- 选项A（推荐）: "基于已有产出进行修订"  (allowFreeformInput: true，用户可输入修改意见)
- 选项B: "重新执行完整圆桌会议（创建新版本）"

#### 修订模式执行流程

```
读取已有 01-06 文档
    ↓
分析用户修改意见 → 识别受影响的文档
    ↓
🔍 如修改意见涉及新的平台API/类/枚举，先搜索获取完整信息
    ↓
定向修改受影响文档（直接编辑，不重跑整个圆桌）
    ↓
检查级联影响（如改了01架构，05实施方案可能也要调整）
    ↓
更新 06-design-review.md 的变更记录
    ↓
Phase D: 默认重新发布到飞书
```

> ⚠️ 修订时保留原文件的 KEY_OUTPUT / DESIGN_REVIEW / CODING 标记结构，仅修改内容。

### 必须执行的收集步骤（首次模式，共7步）

> ⚠️ **以下7个步骤全部为自然语言指令，AI 必须按顺序逐步执行，不是示例代码！**
> 🔴 **步骤4/5/7 是 Phase 9 新增的核心步骤，禁止跳过。**

**步骤1：分析 PBI 涉及哪些模块**

根据 PBI 标题和描述中的关键词，判断涉及的功能模块（如 [你的平台组件名] 等）。

**步骤2：读取涉及模块的 expert skill（了解现有架构）**

对每个涉及的模块，执行 `read_file("{project}/.github/skills/{模块名}-expert/SKILL.md")`。
例如 PBI 涉及 VOI 和 Save → 读取 `voi-expert/SKILL.md` 和 `save-export-expert/SKILL.md`。

**步骤3：读取平台层 expert skill（了解平台能力）**

执行 `read_file("{project}/.github/skills/{{PLATFORM_PREFIX}}-{领域}-expert/SKILL.md")`。
例如涉及数据保存 → 读取 `{{PLATFORM_REPO}}-datasave-expert/SKILL.md`。

**步骤3B：读取运行时配置文件（了解 FE↔BE 通路映射）**

> 💡 当 PBI 涉及 FE↔BE 通信（如新增 Operation、Widget、消息路由）时，读取 XML 配置文件可精准了解现有通路注册。

**3B-1. 自动发现配置文件路径**

按以下优先级搜索项目中的 XML 配置目录：

1. **标准路径**: `file_search("**/appdata/*/config/[你的配置目录]/[配置文件]")`
   - 匹配 → 配置根目录 = `appdata/{appname}/config/`
2. **拆分路径**: `file_search("**/BE/appdata/*/config/[你的配置目录]/[配置文件]")`
   - 匹配 → BE 配置 = `BE/appdata/{appname}/config/BE/`，FE 配置 = `FE/appdata/{appname}/config/FE/`
3. **均未找到** → 跳过步骤3B，在 contextBlock 标注「⚠️ 未找到运行时配置文件」

**3B-2. 读取核心配置文件**（找到路径后，读取以下 3 个核心文件）

| 文件 | 包含信息 | 提取重点 |
|------|----------|----------|
| `[后端配置文件]` | FE→BE Operation 路由、Widget/Model 注册 | 与 PBI 模块相关的 `<Item>` 条目 |
| `BE/WorkflowController.xml` | Controller 级 Operation 链、线程模型 | 与 PBI 相关的 `<OperationName>` 链 |
| `[前端命令配置]` | BE→FE 消息路由（注意文件名拼写） | 与 PBI 模块相关的 `<Handler>` 条目 |

可选读取（如 PBI 涉及初始化或 IoC）：`[前端配置文件]`、`FE/EventHandler.xml`、`[前端容器配置]`

**3B-3. 提取模块相关条目**

从 XML 中筛选与步骤1识别的模块相关的条目（按模块关键词/命名空间匹配），写入 contextBlock 的「运行时配置映射」区段。

### 🔴 步骤4：判断 PBI 是否涉及平台组件（必须执行）

**上游短路**：如请求中含「[上游注入] 平台组件涉及: 是({keywords})」→ 直接标记「涉及平台组件 = 是」， 跳过平台特有的继承分析步骤4b 工作区检测和 askQuestions。

检查 PBI 标题/描述是否包含以下任一关键词：
`DataLoad` / `DataSave` / `ROI` / `VOI` / `TissueControl` / `MaskData` / `Volume` /
`Layout` / `Cine` / `VRT` / `Palette` / `Density` / `SUV` / `DataLinkage` / `ImageTools`

- **匹配** → 标记 `涉及平台组件 = 是`，继续步骤4b
- **不匹配** → 标记 `涉及平台组件 = 否`，步骤5写N/A，步骤7整体跳过

### 步骤4b：平台项目工作区检测（涉及平台组件时执行）

> 当步骤4判定「涉及平台组件 = 是」时，检测用户是否具备平台代码访问能力。

**检测流程**:
1. 检查工作区是否包含 `{{PLATFORM_REPO}}` 文件夹: `list_dir` 查看工作区根目录
2. 检查 `.github/copilot-instructions.md` 中是否配置了 Azure DevOps MCP 仓库（搜索 `{{PLATFORM_REPO}}` 关键词）

**判定**:
- 本地有 `{{PLATFORM_REPO}}` → ✅ 可以本地搜索平台代码，继续步骤5
- 无本地但有 DevOps MCP 配置 → ✅ 可以远程搜索，继续步骤5
- **两者都没有** → 使用 `ask_questions` 提示用户：

```
header: "平台项目"
question: "检测到此 PBI 涉及平台组件修改（匹配关键词: {匹配到的关键词}），但当前工作区未打开平台项目且未配置 DevOps 远程仓库读取。\n\n缺少平台代码访问将导致设计文档中的平台接口分析不完整，可能遗漏关键依赖。\n\n建议操作："
options:
  - label: "我来添加平台项目到工作区"
    description: "将 {{PLATFORM_REPO}} 添加到多根工作区后重新执行"
  - label: "跳过平台分析，继续设计"
    description: "接受风险，设计文档中平台相关分析将基于 Skill 文档描述"
    recommended: true
```

- 用户选择「添加平台项目」→ 暂停执行，输出添加指引（使用 GUI 工具的多根工作区管理功能，或手动打开 `.code-workspace` 文件添加）
- 用户选择「跳过」→ 在 context-check.md 中标注「⚠️ 未配置平台代码访问」，继续步骤5

### 🔴 步骤5：提取接口名列表 + 创建 context-check.md（必须执行）

**5a.** 如果步骤4判定涉及平台组件：从步骤3读取的 平台域专家 Skill 中，提取「核心接口速查」表中的**所有接口名和类名**，形成接口名列表。
例如：`[你的平台接口名], IExportService, ExportConfig, SaveOptions`

**5b.** 执行 `create_file("{workDir}/context-check.md", 内容)`，写入以下结构：

```markdown
# 上下文收集检查记录

## PBI 信息
- PBI ID: {id}
- 涉及平台组件: {是/否}
- 匹配关键词: {匹配到的关键词列表，或"无"}

## 接口名列表（步骤5提取）
{从平台域专家 skill 提取的接口名/类名列表，每行一个}
{如不涉及平台组件，写"N/A — PBI 不涉及平台组件"}

## 平台源文件清单（步骤7填写）
{待步骤7完成后填写}
```

🔴 **阻断点**：确认 context-check.md 已创建（含PBI信息+接口名列表或N/A），否则不得继续步骤6。

**步骤6：搜索项目中的相似实现（发现复用机会）**

执行 `grep_search("相似功能关键词")` 搜索本地项目代码中的相似实现。

### 🔴 步骤7：搜索平台层源码（涉及平台组件时强制执行，不可跳过）

> ⚠️ **步骤4标记「涉及平台组件 = 是」时，此步骤为强制步骤，必须执行。**
> **步骤4标记「涉及平台组件 = 否」时，跳过步骤7，直接进入检查点0。**

**7a. 使用步骤5提取的接口名列表作为搜索关键词**

从 `{workDir}/context-check.md`「接口名列表」区段获取接口名/类名，用于搜索平台源码。

如果接口名列表为空或不足，降级提取：
- **Tier 1（首选）**：skill「核心接口速查」表中的接口/类名 → 直接使用
- **Tier 2（skill 无速查表）**：skill「代码搜索建议」或「搜索策略」中的推荐关键词 → 使用
- **Tier 3（skill 缺失或极简）**：用 PBI 标题/描述中的英文技术术语（如 `DataSave`、`ROI`、`Export`）搜索 {{PLATFORM_REPO}}

🔴 **不要在应用代码里搜 平台 引用来提取类名** — `using`/`import` 语句只有命名空间（如 `{{PLATFORM_NAMESPACE}}.DataSave`），没有类名。

**7b. 读取平台源码（本地优先 → MCP 降级）**

对 7a 中的每个接口名/类名，按以下优先级搜索并读取源码：

**路径A — 本地优先**（工作区包含 `{{PLATFORM_REPO}}` 文件夹时）：

1. 执行 `grep_search("接口名", { includePattern: "**/{{PLATFORM_REPO}}/**" })` 定位文件
2. 执行 `read_file("命中的头文件.h")` — 读取完整头文件签名
3. 执行 `read_file("命中的实现文件.cpp")` — 读取完整实现代码

**路径B — MCP 降级**（本地没有 `{{PLATFORM_REPO}}` 时，`search_code` 在 On-Premise 不可用）：

1. 从 expert skill 获取**模块路径**（如 `BitmapPalette/`），浏览模块根目录：
   `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名", versionType: "branch", version: "{{PLATFORM_BRANCH}}" })`
2. 浏览 `BE/src/` 和 `BE/include/` 子目录，定位 `.h` 和 `.cpp` 文件：
   `mcp_azuredevops_get_file_content({ ..., path: "/模块名/BE/src" })`
   `mcp_azuredevops_get_file_content({ ..., path: "/模块名/BE/include" })`
3. 读取**头文件 + 实现文件**（两者都必须读取，仅读头文件不够）：
   `mcp_azuredevops_get_file_content({ ..., path: "/模块名/BE/include/{{PLATFORM_PREFIX}}-component-xxx/yyy.h" })`
   `mcp_azuredevops_get_file_content({ ..., path: "/模块名/BE/src/yyy.cpp" })`

> 🔴 **头文件只有签名，必须读取 .cpp 实现文件才能理解逻辑**

**7c. 验证检查点（硬阻断 — 不通过则禁止进入检查点0）**

确认步骤 7 至少读取了 **1 个 {{PLATFORM_REPO}} 平台源文件**（.h / .cpp / .cs）。

**通过** → 将文件路径列表追加到 `{workDir}/context-check.md`「平台源文件清单」区段：

```markdown
## 平台源文件清单（步骤7填写）
- ✅ 已读取 {N} 个平台源文件
- 文件列表:
  - {文件路径1} (来源: 本地/MCP)
  - {文件路径2} (来源: 本地/MCP)
```

**未通过处理**：
1. 降级到下一 Tier 的关键词重试 7b
2. 如果所有 Tier 均失败 **且 MCP 也不可用**：
   - 在 context-check.md 标注「⚠️ 降级出口：MCP 不可用，平台源码搜索分数 5/15」
   - 允许继续（降级通过），上下文中标注「⚠️ 未能获取平台源码，以下分析基于 skill 文档描述」
3. 🔴 **如果 MCP 可用但未执行搜索、或执行了但未读取任何文件**：
   - **禁止进入检查点0**，必须重新执行步骤 7b
   - 显示：`❌ 步骤7c未通过：PBI 涉及平台组件但未读取任何平台源文件，正在重试...`

> 🔴 **强制规则**：搜索关键词从步骤5接口名列表提取，但最终必须读取平台**完整源码**（头文件+实现），
> 不能仅停留在 skill 文档描述层面。参考 `#platform-architecture` 了解完整搜索策略（本地优先 → MCP DevOps）。

🔴 **阻断点**：步骤7完成（或因不涉及平台而跳过）后，必须进入检查点0评分，禁止直接启动 runSubagent。

---

### 检查点0：上下文收集评分（进入 Phase A 前 — 强制评分）

> 🔴 **在启动任何 subAgent 之前，必须先完成检查点0评分。评分不通过则禁止进入 Phase A。**

读取 `{workDir}/context-check.md`，对照以下评分卡自评：

| 评分项 | 满分 | 评分标准 | 得分 |
|--------|------|----------|------|
| Expert Skill 阅读 | 5 | 读取了 ≥1 个相关 expert skill（步骤2） | ？ |
| 接口名列表 | 10 | context-check.md 中有从 平台域专家 Skill 提取的接口名列表（步骤5）；不涉及平台=N/A满分 | ？ |
| 平台源码阅读 | 15 | context-check.md 中有 ≥1 个平台源文件路径（路径含 `{{PLATFORM_REPO}}/` 或来源标注 MCP:{{PLATFORM_REPO}}）；应用层文件不计分；不涉及平台=N/A满分；降级出口=5分 | ？ |
| 上下文注入准备 | 5 | contextBlock 已构建，包含所有收集的内容 | ？ |
| **总分** | **35** | | **？** |

**判定规则**：
- 总分 ≥ 25 → ✅ 通过，进入 Phase A
- 总分 < 25 → ❌ 阻断，返回补充缺失步骤
- 不涉及平台组件的 PBI → 接口名列表(10) + 平台源码(15) = N/A，按满分计算

**输出格式**（必须显示给用户）：
```markdown
📊 **检查点0：上下文收集评分**
| 评分项 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| Expert Skill 阅读 | 5 | {分} | {读取了哪些skill} |
| 接口名列表 | 10 | {分} | {列出接口名数量，或N/A} |
| 平台源码阅读 | 15 | {分} | {读取了N个文件，或N/A，或降级5分} |
| 上下文注入准备 | 5 | {分} | {contextBlock是否就绪} |
| **总分** | **35** | **{总分}** | {通过/阻断} |
```

---

### 上下文收集产出

| 收集项 | 来源 | 用途 |
|--------|------|------|
| 现有架构 | expert skill（步骤2） | 确保设计与现有架构一致 |
| 平台能力 | 平台域专家（步骤3） | 避免重复造轮子 |
| 运行时配置 | XML 配置文件（步骤3B） | 了解现有 FE↔BE Operation/消息路由注册 |
| 🔴 接口名列表 | 平台域专家 → context-check.md（步骤5） | 步骤7搜索关键词 |
| 相似实现 | grep_search（步骤6） | 复用现有代码模式 |
| 🔴 平台源码 | 步骤5接口名 → 步骤7 read_file 或 MCP（步骤7） | 了解平台 API 实际签名和内部实现 |
| 项目规范 | expert skill | 遵循命名/组织规范 |

### 上下文复用原则（提高效率，不限制深入）

> 💡 **主Agent收集的上下文完整注入到每个subAgent的prompt中**

### 上下文注入到 subAgent prompt（强制格式）

> ⚠️ **主Agent 必须按以下结构构建 contextBlock，注入到每个 subAgent 的 prompt 中。**

构建一个 `contextBlock` 字符串，包含以下内容，用于拼接到每个 subAgent prompt 中：

```markdown
## 项目上下文（主Agent已收集）

> 💡 **使用原则**：
> 1. 优先使用：以下内容已收集，避免重复搜索相同内容
> 2. 按需搜索：如果你的分析需要更深入的细节，请使用下方搜索工具主动补充

### 现有架构
{步骤2-3读取的 expert skill 内容}

### 相似实现
{步骤6 grep_search 发现的代码片段}

### 运行时配置映射（XML）
{步骤3B 读取的 FE↔BE 配置条目（Operation 注册、消息路由、Widget/Model 绑定）；如未找到配置文件则填"⚠️ 未找到运行时配置文件"}

### 平台源码（{{PLATFORM_REPO}}）
{步骤7读取到的平台层完整源码（头文件签名+关键方法实现）；如不涉及则填"本 PBI 不涉及平台层组件"}
```

🔴 **特别注意**：步骤7搜索到的平台源码**必须填入上述"平台源码"区域**，不能遗漏！
如果步骤5执行了但结果未注入 contextBlock，subAgent 将无法参考平台 API 签名。

搜索指南（附加到 contextBlock 末尾）：

```markdown
## 🔍 搜索指南（遇到未知信息时必须使用）

🔴 **强制规则**: 你在分析中引用的任何类型、接口、枚举、方法，
如果不在上方"项目上下文"中，**必须先搜索确认**，禁止凭记忆猜测。

可用工具:
1. grep_search("关键词") — 搜索本地工作区代码
2. read_file("路径") — 读取本地文件
3. mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名", versionType: "branch", version: "{{PLATFORM_BRANCH}}" }) — 浏览平台仓库目录（path="/目录" 返回目录列表）
4. mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名/BE/src/xxx.cpp", ... }) — 读取平台源码文件

搜索策略: 本地 grep_search 优先 → MCP get_file_content 目录浏览降级
⚠️ search_code 在 On-Premise 不可用，禁止使用
```

将 contextBlock 注入每个 runSubagent 调用：`runSubagent("角色分析", 角色Prompt + contextBlock)`

**subAgent 行为**：
- ✅ 优先基于已有上下文分析
- ✅ 如需更深入细节，主动补充搜索
- ⚠️ 避免重复搜索已有的 expert skill、相似代码等

---

## 🔴 必须使用 runSubagent（强制）

```javascript
// ❌ 严禁：单Agent模拟多角色
"假设我是架构师...现在切换为效率派..."

// ✅ 正确：每个角色独立子Agent
runSubagent("架构派独立分析", prompt_with_context)
runSubagent("效率派独立分析", prompt_with_existing_code)
runSubagent("质量派独立分析", prompt)  
runSubagent("成本派独立分析", prompt)
```

---

## 🔄 分层执行流程

> 🔴 **核心原则**：实施派依赖前4个角色的产出，天然形成质量校准。无需额外核查循环。
> 🔴 **强制加载**：执行第0步前，必须 `read_file("references/context-collection.md")` 获取完整收集步骤。

```
┌─────────────────────────────────────────────────────────────┐
│            第0步：收集项目上下文（强制，7个步骤）              │
├─────────────────────────────────────────────────────────────┤
│  0.0 检查需求返讲文档（用户提供/询问）                        │
│  0.1 检测修订模式（同PBI已有产出？→ 修订 or 新建）            │
│  步骤1-3: 分析模块 + 读取 expert skill + 读取平台域专家 Skill    │
│  步骤3B: 读取运行时配置文件（FE↔BE XML 通路映射）            │
│  🔴 步骤4: 判断是否涉及平台组件（15关键词匹配）              │
│  🔴 步骤5: 提取接口名列表 → 创建 context-check.md            │
│  步骤6: grep_search(相似实现) → 发现复用机会                  │
│  🔴 步骤7: 搜索平台源码（本地优先→MCP降级）→ 硬阻断验证      │
└─────────────────────────────────────────────────────────────┘
                              ↓
               🔴 检查点0：上下文评分卡 ≥25/35 → 通过
                              ↓
                   修订模式？→ 定向修改已有文档 → Phase D
                              ↓ (首次模式)
┌─────────────────────────────────────────────────────────────┐
│       Phase A：4角色独立分析（因工具限制按顺序启动）       │
├─────────────────────────────────────────────────────────────┤
│  runSubagent(架构派🧠) → 01-architecture.md + KEY_OUTPUT     │
│  runSubagent(效率派⚡) → 02-efficiency.md + KEY_OUTPUT      │
│  runSubagent(质量派🛡️) → 03-quality.md + KEY_OUTPUT         │
│  runSubagent(成本派💰) → 04-cost.md + KEY_OUTPUT            │
│  🔴 各角色互相隔离，禁止读取对方文件（prompt级硬阻断）  │
└─────────────────────────────────────────────────────────────┘
                              ↓
          🔴 检查点A：验证 01-04 文件存在且 > 100 bytes + KEY_OUTPUT
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase B：实施派依赖执行（参考 Phase A 产出）                 │
├─────────────────────────────────────────────────────────────┤
│  主Agent提取 01-04 的 KEY_OUTPUT 标记内容                     │
│  runSubagent(实施派👨‍💻) → 05-implementation.md             │
│    prompt 包含：KEY_OUTPUT 摘要 + 完整需求上下文              │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ✅ 检查点B：验证 05 文件存在且 > 100 bytes
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase C：设计评审文档组装（主Agent直接执行，非subagent）      │
├─────────────────────────────────────────────────────────────┤
│  grep_search(DESIGN_REVIEW标记) → 从01-05提取各区段          │
│  按 design-review-template.md 结构组装                       │
│  create_file → 06-design-review.md                          │
│  🔴 Phase C 后处理检查（4项验证，详见下方）                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
               🔴 检查点C：后处理验证通过
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase D：发布到飞书（默认执行）                              │
├─────────────────────────────────────────────────────────────┤
│  调用 #lark-doc-generator 批量导入模式                       │
│  逐个上传 01-06 + 创建索引文档 → 返回 7 个飞书链接            │
│  ❌ 飞书不可用时降级为本地交付                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    🎯 交付：6个文件 + 飞书链接
```

---

## 🔴 KEY_OUTPUT 标记机制

> 前4个角色必须在文件末尾添加 KEY_OUTPUT 标记，供实施派精准提取。

### 标记格式

```markdown
<!-- KEY_OUTPUT_FOR_IMPL_START -->
## 🎯 关键产出摘要（供实施派参考）

### 核心结论
- [本角色的核心设计结论，3-5条]

### 实施约束
- [影响编码的关键约束，如技术选型、接口规范等]

### 建议关注
- [实施时需要特别注意的点]
<!-- KEY_OUTPUT_FOR_IMPL_END -->
```

### 提取方法（主Agent在 Phase B 前执行）

对以下4个文件逐一执行提取：`01-architecture.md`、`02-efficiency.md`、`03-quality.md`、`04-cost.md`

1. 执行 `grep_search("KEY_OUTPUT_FOR_IMPL_START", { includePattern: "{workDir}/{文件名}" })` 定位标记的行号
2. 执行 `read_file("{workDir}/{文件名}", 标记起始行, 标记结束行)` 读取标记之间的内容（通常 50-80 行）
3. 将4份 KEY_OUTPUT 拼接为一个字符串，注入到实施派 prompt 中

> 🔴 **为什么用标记而不是读全文？** 因为每个文件可能 500-1000+ 行，
> 全文注入会压缩实施派 prompt 空间。KEY_OUTPUT 提供精准摘要。

---

## 🔴 检查点机制

> 检查点0 已移至「收集步骤」区域（步骤7之后），紧邻其验证对象。
> 实测发现 subagent 有时不写文件（如 roundtable-001 只生成 3/5），必须强制检查。

### 🔴 检查点A（Phase A 完成后，强制执行）

对以下4个文件逐一执行 `read_file` 读取前10行，确认文件存在且内容 > 100 bytes：
- `{workDir}/01-architecture.md`
- `{workDir}/02-efficiency.md`
- `{workDir}/03-quality.md`
- `{workDir}/04-cost.md`

对每个文件执行 `grep_search("KEY_OUTPUT_FOR_IMPL_START")`，确认标记存在。

如果任何文件缺失、内容太少、或不含 KEY_OUTPUT 标记 → 重新启动对应 subAgent。

🔴 **必须显示检查结果**：
`✅ 检查点A：01 ✓ | 02 ✓ | 03 ✓ | 04 ✓ — KEY_OUTPUT 标记 4/4 存在`

### 🔴 检查点B（Phase B 完成后，强制执行）

执行 `read_file("{workDir}/05-implementation.md", 1, 10)` 确认文件存在且内容 > 100 bytes。

如果 05 文件缺失或内容太少 → 重新执行实施派 subAgent。

🔴 **必须显示检查结果**：
`✅ 检查点B：05-implementation.md ✓ — 文件存在且内容完整`

### 🔴 检查点C（Phase C 组装后，强制执行）

组装 `06-design-review.md` 后，执行以下 4 项后处理验证：

**C1. Mermaid 时序图验证**：
- 执行 `grep_search("sequenceDiagram", { includePattern: "06-design-review.md" })`
- 缺失 → 从 `05-implementation.md` 全文搜索 `sequenceDiagram` 代码块，补充到 §2.1
- 仍无 → 基于已有文字描述就地生成 Mermaid `sequenceDiagram` 代码块

**C2. Mermaid 类图验证**：
- 执行 `grep_search("classDiagram", { includePattern: "06-design-review.md" })`
- 缺失 → 从 `01-architecture.md` 全文搜索 `classDiagram` 代码块，补充到 §2.2
- 仍无 → 基于已有类设计描述就地生成 Mermaid `classDiagram` 代码块

**C3. 角色标注清理**：
- 执行 `grep_search("来源:\ |来源标记:", { includePattern: "06-design-review.md", isRegexp: true })`
- 命中 → 删除所有 `> 来源:` / `> 来源标记:` 开头的行（这些是 AI 组装参考，不应出现在最终文档）

**C4. XML 注释验证**：
- 执行 `grep_search("/// <summary>", { includePattern: "06-design-review.md" })`
- 文档中有接口/类定义代码块但无 `/// <summary>` 注释 → 就地补充 XML 注释

🔴 **必须显示检查结果**：
```
✅ 检查点C：后处理验证
  C1 Mermaid sequenceDiagram: ✓ 存在 / ⚠️ 已从05补充 / ⚠️ 已就地生成
  C2 Mermaid classDiagram:    ✓ 存在 / ⚠️ 已从01补充 / ⚠️ 已就地生成
  C3 角色标注清理:             ✓ 无残留 / ⚠️ 已清理 {N} 处
  C4 XML注释:                  ✓ 完整 / ⚠️ 已补充 {N} 处
```

---

## 执行进度提示

```markdown
🪑 **圆桌会议 v2.0 启动**

📋 议题: {需求描述}
⏱️ 预计耗时: 1-3分钟

---
📚 **第0步：收集项目上下文**
✅ 读取 xxx-expert → 了解模块架构
✅ 读取 {{PLATFORM_REPO}}-xxx-expert → 提取接口名列表
✅ 搜索现有相关代码 → 发现可复用组件
✅ 搜索平台源码 → 读取 N 个源文件（或 N/A 不涉及平台）

📊 **检查点0：上下文收集评分**
{显示评分卡表格，见检查点0输出格式}
✅ 总分 {X}/35 → 通过

🔄 **Phase A：4角色并行分析**
⭕ runSubagent: 架构派🧠 → 01-architecture.md
✅ 架构派🧠 完成
⭕ runSubagent: 效率派⚡ → 02-efficiency.md
✅ 效率派⚡ 完成
⭕ runSubagent: 质量派🛡️ → 03-quality.md
✅ 质量派🛡️ 完成
⭕ runSubagent: 成本派💰 → 04-cost.md
✅ 成本派💰 完成

✅ **检查点A：01-04文件全部存在**

🔄 **Phase B：实施派依赖执行**
⭕ 提取 KEY_OUTPUT 标记...
✅ 已提取 4份关键产出摘要
⭕ runSubagent: 实施派👨‍💻 → 05-implementation.md
✅ 实施派👨‍💻 完成

✅ **检查点B：05文件存在**

🔄 **Phase C：组装设计评审文档**
⭕ 读取 design-review-template.md 模板...
✅ 模板结构已加载
⭕ grep_search DESIGN_REVIEW 标记...
✅ 从01-05提取15个区段
⭕ 组装 06-design-review.md...
✅ 设计评审文档已生成

✅ **检查点C：后处理验证**
  C1 Mermaid sequenceDiagram: ✓ 存在
  C2 Mermaid classDiagram:    ✓ 存在
  C3 角色标注清理:             ✓ 无残留
  C4 XML注释:                  ✓ 完整

🔄 **Phase D：发布到飞书**
⭕ 逐个上传 01-06 共 6 篇文档...
✅ 6 篇文档上传成功
⭕ 创建索引文档...
✅ 索引文档已创建

📊 **交付评分卡**
{显示评分卡表格}

🎯 **交付完成：6个文件已生成 + 飞书已发布**
├── 01-architecture.md  (架构派🧠)
├── 02-efficiency.md   (效率派⚡)
├── 03-quality.md      (质量派🛡️)
├── 04-cost.md         (成本派💰)
├── 05-implementation.md (实施派👨‍💻) ← 编码核心参考
└── 06-design-review.md (主Agent组装) ← 评审文档
```

---

## 5个子Agent角色

| 角色 | 执行阶段 | 核心产出 |
|------|----------|----------|
| 🧠 **架构派** | Phase A (独立) | 架构设计、模块划分、类图、分层定义 |
| ⚡ **效率派** | Phase A (独立) | 实现策略、代码骨架、复用分析、文件组织 |
| 🛡️ **质量派** | Phase A (独立) | 质量设计、验收标准、异常处理、测试用例 |
| 💰 **成本派** | Phase A (独立) | 任务拆解(2-8h)、优先级、任务ID、依赖链 |
| 👨‍💻 **实施派** | Phase B (依赖) | **时序图、数据结构、实现骨架、调用链、可编码性检查** |

> 🔴 实施派在 Phase B 执行，参考前4个角色的 KEY_OUTPUT，天然校准质量。
> 🔴 Phase A 的4个角色逻辑上相互独立，因工具限制按顺序启动，每个角色的 prompt 中注入隔离规则禁止读取其他角色的已有文件。
>
> 📖 Plus模式主控见 `references/plus-mode.md`（流程概览 + 检查点 + 输出要求）
> 📖 详细Prompt模板已拆分：`references/context-collection.md`（第0步）| `references/prompts-phase-a.md`（Phase A）| `references/prompt-phase-b.md`（Phase B）
> 📖 核查清单（参考材料）见 `references/checklist.md`

---

## 输出：可编码设计文档

> 🎯 **标准**：开发者可直接按文档编码，无需额外澄清

### 🔴 输出原则（强制）

> ⚠️ **最终输出的设计文档必须是干净的、可直接使用的**

**禁止包含**（任一出现即不合格）：
- ❌ 生成信息：`工具: GitHub Copilot`、`文档生成时间:`
- ❌ 角色标注：`来源: 🧠 架构派贡献`
- ❌ 中间状态：`改进状态: ✅ 已整合`
- ❌ 任何 "原本有问题" "已修改" 等描述

**必须包含**（缺一不可）：
- ✅ Mermaid时序图（`sequenceDiagram`代码块）
- ✅ Mermaid类图（`classDiagram`代码块）
- ✅ 接口定义含`/// <summary>`注释
- ✅ 文件组织结构（树形目录）
- ✅ 任务拆解粒度2-8h（如`BE-1 (3h): xxx`）
- ✅ 数据结构完整字段定义（所有Context/Result类）
- ✅ 实现骨架（核心类方法体含步骤注释）

### 文档结构（8章节）

1. **概述** - 背景、目标、范围
2. **架构设计** - 模块划分、数据流（含架构图）
3. **详细设计** - 接口定义（完整签名）、数据结构
4. **实现策略** - 开发顺序、代码骨架
5. **质量保障** - 异常处理、边界条件、测试用例
6. **资源与约束** - 工时、依赖、风险
7. **开发任务拆解** - 可直接分配的任务条目
8. **验收标准** - 功能/性能交付标准

### 接口定义标准

```csharp
// ✅ 正确：完整签名 + 注释
public interface IExporter
{
    /// <summary>导出VOI到ExportFormat格式</summary>
    /// <param name="voi">VOI数据</param>
    /// <param name="outputPath">输出路径</param>
    /// <exception cref="IOException">写入失败</exception>
    ExportResult Export(VOIData voi, string outputPath);
}

// ❌ 错误："提供导出接口"
```

### 任务拆解标准

```markdown
✅ 正确（每条2-8h）：
- [ ] **BE-1** (2h): 实现IExporter.Export，包含ExportFormat头构建
- [ ] **BE-2** (4h): ExportFormat文件写入，含gzip压缩
- [ ] **FE-1** (3h): SavePanel ViewModel，绑定格式选择

❌ 错误（粒度太粗）：
- [ ] 后端实现导出
- [ ] Phase 1: 40h (5天)
- [ ] 基础架构: 5天
```

> 📖 完整模板见 `references/output-templates.md`

---

## Phase D: 发布到飞书（默认）

### 触发条件

**默认执行**。检查点B通过后自动进入 Phase D。

仅在以下情况**跳过**：
- 用户明确说「不要发飞书」「只要本地」「--local-only」
- 飞书 MCP 不可用 → 降级为本地交付 + 提示用户配置飞书 MCP

> 💡 参照 pbi-reviewer 步骤5 的「飞书优先、不可用时降级」模式。

### 🔴 内容完整性规则（禁止截断）

> ⚠️ **实测教训**：AI 曾将设计文档"手动精简/摘要"后再上传飞书，导致关键细节丢失。

上传飞书的内容**必须**是本地 .md 文件的完整原始内容，禁止以下行为：
1. **禁止**手动摘要/精简/截断文档内容
2. **禁止**选择性上传部分章节
3. **必须**对每个文件执行 `read_file("{workDir}/{文件名}")` 读取完整内容，然后直接传递给飞书 API
4. 如果内容超过飞书 API 单次限制，分段上传，**不要删减内容**
5. **禁止**改写/浓缩 Mermaid 代码块（`sequenceDiagram`、`classDiagram`、`flowchart` 等），必须原样传递

### 执行流程

```
检查点B通过
    ↓
Phase D: 发布到飞书
    ↓
1. 确认文件: 扫描 .copilot-temp/roundtable-{id}/ 下 01~06 的 .md 文件
    ↓
1.5 🔴 询问用户上传策略（ask_questions）:
   - 选项A（推荐）: 「完整上传全部 6 篇」— 仅移除 HTML 注释标记行，保留全部正文
   - 选项B: 「仅上传设计评审主文档（06-design-review.md）」
   - 选项C: 「上传全部 6 篇，过滤内部标记段落（KEY_OUTPUT / DESIGN_REVIEW 区段内容）」
   > 用户选择 A → 调用 #lark-doc-generator 时传递 filterMode=strip-comments-only
   > 用户选择 B → 只上传 06
   > 用户选择 C → 调用 #lark-doc-generator 时使用默认过滤规则
    ↓
2. 逐个上传文档（调用 #lark-doc-generator）:
   - 🔴 必须上传 01-06 共 6 篇文档（含 06-design-review.md）（选项B时仅上传06）
   - 对每个文件执行 read_file 获取完整内容
   - 将完整内容传递给飞书文档创建 API
   - file_name 规则: {PBI_ID}_{序号}{简称}（≤27字符）
   - 🔴 禁止手动摘要/精简/改写文档内容，必须原文传递
    ↓
3. 创建索引文档:
   - file_name: {PBI_ID}_圆桌会议
   - 内容: PBI 基本信息 + 6篇文档的飞书链接 + 每篇文档一句话摘要 + 阅读建议
   - 格式: 索引文档包含直接链接，用户点击即可跳转
    ↓
4. 向用户返回完整链接列表（索引文档 + 6篇子文档）
```

### 索引文档模板

```markdown
# {PBI_ID} 圆桌会议设计文档

## 需求信息
- PBI: {PBI_ID} - {PBI标题}
- 生成时间: {时间}

## 文档列表
| 序号 | 文档 | 链接 | 简介 |
|------|------|------|------|
| 01 | 架构设计 | [查看]({飞书链接}) | {一句话摘要} |
| 02 | 效率分析 | [查看]({飞书链接}) | {一句话摘要} |
| 03 | 质量设计 | [查看]({飞书链接}) | {一句话摘要} |
| 04 | 成本规划 | [查看]({飞书链接}) | {一句话摘要} |
| 05 | 实施方案 | [查看]({飞书链接}) | {一句话摘要} |
| 06 | 设计评审 | [查看]({飞书链接}) | {一句话摘要} |

## 阅读建议
- 评审重点看 06(设计评审文档)
- 开发同学重点看 01(架构) + 05(实施方案)
- 任务拆分看 04(成本规划)
```

### 产出物

| 序号 | 文档 | 来源 |
|------|------|------|
| 📋 | 索引文档（目录+链接） | 自动生成 |
| 01 | 架构设计 | 01-architecture.md |
| 02 | 效率分析 | 02-efficiency.md |
| 03 | 质量设计 | 03-quality.md |
| 04 | 成本规划 | 04-cost.md |
| 05 | 实施方案 | 05-implementation.md |
| 06 | 设计评审文档 | 06-design-review.md |

### 交付评分卡（Phase D 完成后，必须显示）

| 评分项 | 满分 | 评分标准 | 得分 |
|--------|------|----------|------|
| 本地文件 + KEY_OUTPUT | 20 | 01-05 全部存在且含 KEY_OUTPUT 标记 | ？ |
| 05 实施方案 + CODING_IMPL | 20 | 05 包含 CODING_TASK_LIST 和 CODING_IMPL 标记 | ？ |
| 飞书上传 | 15 | 6 篇文档全部成功上传（01-06，每篇2.5分） | ？ |
| 索引文档 | 10 | 索引文档已创建，包含所有 6 篇链接 | ？ |
| **总分** | **65** | | **？** |

**判定规则**：
- 总分 ≥ 50 → ✅ 交付完成
- 总分 < 50 → ❌ 检查缺失项，修复后重新评分
- 飞书 MCP 不可用 → 飞书上传(15) + 索引文档(10) = N/A，按满分计算

> 🔴 **圆桌会议完成后，工作目录永久保留，禁止询问用户是否清理。** 详见 `references/workspace.md`。

**输出格式**（必须显示给用户）：
```markdown
📊 **交付评分卡**
| 评分项 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 本地文件 + KEY_OUTPUT | 20 | {分} | {5/5文件存在，KEY_OUTPUT完整} |
| 05 + CODING_IMPL | 20 | {分} | {CODING标记存在/缺失} |
| 飞书上传 | 15 | {分} | {N/6成功，或N/A} |
| 索引文档 | 10 | {分} | {已创建/未创建，或N/A} |
| **总分** | **65** | **{总分}** | {交付完成/需修复} |
```

### 注意事项

- Phase D **不影响** Phase A/B 的执行，即使 Phase D 失败，设计文档仍然完整交付在本地
- 飞书 MCP 不可用时，提示用户参考 `#lark-doc-generator` 的备选方案（本地保存/手动复制）
- 如需单独上传已有的圆桌会议文档，可直接使用 `#lark-doc-generator` 的批量导入模式

### 标准结尾（交付评分卡之后，自动输出）

```markdown
---

💡 **下一步 & 对话建议**:
- 设计文档已保存到: `.copilot-temp/roundtable-{NNN}/`
- 如需基于设计文档开始编码，建议**新开对话**输入:
  `根据圆桌会议 {NNN} 的设计文档开始编码`
- 在新对话中，AI 会自动读取 `05-implementation.md` 中的 CODING_TASK_LIST 和 CODING_IMPL 标记
- 本次对话已包含大量上下文，继续在此对话中操作可能影响 AI 输出质量

> ⚠️ 新对话不需要重复提供 PBI 描述或返讲文档，所有必要信息已持久化到文件中。
```

---

## 相关资源

- ⭐ [Plus模式主控](references/plus-mode.md) - 流程概览、runSubagent规则、检查点、输出要求
- � [上下文收集](references/context-collection.md) - 第0步：工作目录 + **7步**上下文收集（**强制加载**，含步骤4/5/7平台检查）
- 📖 [Phase A Prompt](references/prompts-phase-a.md) - 4角色并行分析 Prompt 模板
- 📖 [Phase B Prompt](references/prompt-phase-b.md) - 实施派 Prompt 模板
- 📋 [输出模板](references/output-templates.md) - 设计文档模板
- 📖 [角色设定](references/roles.md)
- 📝 [示例](references/examples.md)
- 📎 [工作区定义](references/workspace.md) - 文件持久化、KEY_OUTPUT/DESIGN_REVIEW/CODING标记格式
- 📄 [设计评审模板](references/design-review-template.md) - Phase C 组装模板
- ☑️ [核查清单](references/checklist.md) - 参考材料，非强制流程
- 🔧 [coding-agent](../coding-agent/SKILL.md) - 下游编码代理，消费 CODING_TASK_LIST/CODING_IMPL 标记自动编码
- 📤 [飞书文档生成器](../lark-doc-generator/SKILL.md) - Phase D 飞书发布，批量导入模式
