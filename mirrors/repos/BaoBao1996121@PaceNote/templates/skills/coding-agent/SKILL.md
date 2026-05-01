---
name: coding-agent
description: |
  设计驱动自动编码 - 读取圆桌会议设计文档，按任务拆解逐任务自动编码，直接写入项目文件。
  触发关键词: 根据设计编码, 开始编码, 按设计实现, coding agent, 实现设计方案,
  按圆桌会议编码, 从设计文档编码, 执行编码任务, start coding, implement design
---

# 🔧 Coding Agent - 设计驱动自动编码

读取圆桌会议产出的设计文档，解析任务拆解表，**串行逐任务调用 subagent 编码**，直接写入项目文件。

> 🎯 **核心流程**：发现设计文档 → 解析任务表 → 逐任务编码（subagent）→ HUMAN_CHECK 暂停点 → 完成报告
>
> 🔴 **关键原则**：
> 1. **串行执行** — 用时间换质量，逐任务完成后再启动下一个
> 2. **精准提取** — 用 `CODING_IMPL` + `DESIGN_REVIEW` 标记精准获取上下文，不读全文
> 3. **不确定即分级标记** — 两级 HUMAN_CHECK 机制（见下方说明），避免频繁打断
> 4. **直接写文件** — create_file / replace_string_in_file 直接操作项目源码
>
> **HUMAN_CHECK 分级机制**：
> - `// 🔴 HUMAN_CHECK_CRITICAL: <原因>` — **影响功能正确性**的不确定项（算法逻辑、数据结构选择、业务规则）→ **即时暂停**，等用户确认后继续
> - `// 🟡 HUMAN_CHECK_REVIEW: <原因>` — **不影响功能正确性**的待审查项（命名规范、注释补充、代码风格、可选优化）→ **不暂停**，Step 3 统一汇总审查
> - 旧格式 `// 🔴 HUMAN_CHECK:` 按 CRITICAL 处理（向后兼容）

---

## 🔴 设计文档来源

本 Skill 消费**圆桌会议**（`#roundtable-debate`）的产出文件：

```
{project}/.copilot-temp/roundtable-{NNN}/
├── 01-architecture.md     # 架构派 → 接口定义、模块职责
├── 02-efficiency.md       # 效率派 → 文件结构、复用分析
├── 03-quality.md          # 质量派 → 异常处理、测试用例
├── 04-cost.md             # 成本派 → 任务拆解表(CODING_TASK_LIST)
├── 05-implementation.md   # 实施派 → 实现骨架(CODING_IMPL)、调用链
└── 06-design-review.md    # 设计评审文档
```

### 核心消费的标记

| 标记 | 来源文件 | 用途 |
|------|----------|------|
| `CODING_TASK_LIST` | `04-cost.md` | 解析任务条目+依赖+目标文件 |
| `CODING_IMPL:{taskId}` | `05-implementation.md` | 精准提取每个任务的实现骨架 |
| `DESIGN_REVIEW:2.3a/2.3b` | `01/05` | 按需提取接口定义 |
| `DESIGN_REVIEW:1.3` | `02-efficiency.md` | 按需提取文件结构 |

---

## 🔄 执行流程（4步）

```
┌─────────────────────────────────────────────────────────────┐
│  Step 0：发现与加载设计文档                                   │
├─────────────────────────────────────────────────────────────┤
│  扫描 .copilot-temp/roundtable-* → 选择工作目录              │
│  读取 05-implementation.md（全文 → 主上下文）                 │
│  验证 04-cost.md + 05-implementation.md 存在                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 1：构建执行计划                                        │
├─────────────────────────────────────────────────────────────┤
│  解析任务表 → 提取任务ID/描述/层级/目标文件/依赖/操作类型      │
│  拓扑排序（按依赖列）→ 确定执行顺序                           │
│  🔴 展示执行计划给用户确认                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2：逐任务串行编码（核心循环）                            │
├─────────────────────────────────────────────────────────────┤
│  对每个任务（按拓扑序）：                                     │
│  ├── 2a. 收集精准上下文                                      │
│  │   ├── grep CODING_IMPL:{taskId} → 实现骨架                │
│  │   ├── grep DESIGN_REVIEW → 接口/数据结构（按需）           │
│  │   ├── read_file(目标文件) → 现有代码（修改任务）            │
│  │   └── read_file(expert skill) → 项目规范                  │
│  ├── 2b. runSubagent 编码                                    │
│  │   ├── 新增文件 → create_file                              │
│  │   └── 修改文件 → 定位锚点 + replace_string_in_file        │
│  └── 2c. 检查点                                             │
│      ├── 验证文件已写入                                      │
│      ├── grep HUMAN_CHECK_CRITICAL 计数                      │
│      ├── 有CRITICAL → 暂停，展示给用户确认                    │
│      ├── 仅REVIEW → 计数记录，自动继续下一任务                │
│      └── 无标记 → 自动继续下一任务                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3：完成报告                                            │
├─────────────────────────────────────────────────────────────┤
│  修改/新增的文件清单 + diff 摘要                              │
│  CRITICAL 汇总 + REVIEW 统一审查表                           │
│  建议的验证命令（编译/测试）                                  │
│  任务完成率统计                                              │
└─────────────────────────────────────────────────────────────┘
```

📖 详细执行流程见 `references/execution-flow.md`

---

## 🔴 Step 0：发现设计文档（强制）

```javascript
// 0. 上游短路：如请求中含「[上游注入] roundtable_dir: {path}」，直接使用，跳过扫描和 askQuestions
// 如无上游注入 → 执行以下扫描逻辑

// 1. 扫描圆桌会议工作目录
const tempDir = `${projectRoot}/.copilot-temp`;
const roundtables = list_dir(tempDir)
    .filter(d => d.startsWith("roundtable-"))
    .sort()  // 按编号排序
    .reverse(); // 最新的在前

// 2. 如有多个 → 使用 ask_questions 对话框让用户选择，默认推荐最新的
//    header: "工作目录"
//    question: "检测到多个圆桌会议工作目录，请选择"
//    选项: 各目录名，最新的标记为 recommended
if (roundtables.length > 1) {
    // 使用 ask_questions 对话框展示选择列表
} else {
    workDir = `${tempDir}/${roundtables[0]}`;
}

// 3. 验证核心文件存在
const required = ["04-cost.md", "05-implementation.md"];
for (const file of required) {
    if (!exists(`${workDir}/${file}`)) {
        // ❌ 缺失关键文件，提示用户先运行圆桌会议
    }
}

// 4. 读取 05-implementation.md 全文（主上下文）
const implContent = read_file(`${workDir}/05-implementation.md`);
```

---

## 🔴 Step 1：解析任务表 + 拓扑排序

```javascript
// 1. 从 04-cost.md 提取 CODING_TASK_LIST
const taskListStart = grep_search("CODING_TASK_LIST:START", {
    includePattern: `${workDir}/04-cost.md`
});
const taskListEnd = grep_search("CODING_TASK_LIST:END", {
    includePattern: `${workDir}/04-cost.md`
});
const taskTable = read_file(`${workDir}/04-cost.md`, startLine, endLine);

// 2. 解析表格 → 任务数组
const tasks = parseMarkdownTable(taskTable);
// 结果: [{ id: "BE-01", desc: "...", hours: "2h", layer: "应用BE",
//          targetFile: "src/.../xxx.cs", depends: "无", operation: "新增" }, ...]

// 3. 拓扑排序（按依赖列）
const executionOrder = topologicalSort(tasks);
// 结果: ["BE-01", "BE-02", "FE-01", "FE-02"]

// 4. 🔴 展示执行计划给用户确认
```

### 展示格式

```markdown
📋 **编码执行计划**（共 X 个任务）

| 序号 | 任务ID | 描述 | 层级 | 操作 | 目标文件 | 依赖 |
|------|--------|------|------|------|----------|------|
| 1 | BE-01 | 实现xxx接口 | 应用BE | 新增 | src/.../IXxxService.cs | - |
| 2 | BE-02 | xxx平台层实现 | 平台BE | 新增 | src/.../XxxHelper.cpp | BE-01 |
| 3 | FE-01 | xxxViewModel | 应用FE | 修改 | src/.../XxxViewModel.cs | BE-01 |

⏱️ 预计总工时: Xh
📁 涉及文件: Y 个（新增 A + 修改 B）

> 展示执行计划表格后，使用 ask_questions 对话框让用户确认：
> - header: "编码确认"
> - question: "确认执行计划并开始编码？"
> - 选项A（推荐）: "确认，开始编码"
> - 选项B: "需要调整计划" (allowFreeformInput: true)
```

---

## 🔴 Step 2：逐任务编码（核心）

> 📖 编码 subagent prompt 模板见 `references/subagent-prompt.md`
> 📖 已有文件修改策略见 `references/modify-strategy.md`

### 2a. 为每个任务收集精准上下文

对每个任务，按以下步骤收集上下文：

**1. 精准提取该任务的实现骨架**：用 `grep_search("CODING_IMPL:{taskId}:START")` 定位 `05-implementation.md` 中的标记区段，`read_file` 读取标记之间的内容。

**2. 按需提取接口定义**：
- C# 任务（层级含"FE"或"应用"）→ 从 `01-architecture.md` 提取 `DESIGN_REVIEW:2.3a` 标记区段
- C++ 任务（层级含"平台"或"BE"）→ 从 `05-implementation.md` 提取 `DESIGN_REVIEW:2.3b` 标记区段

**3. 修改任务 → 读取目标文件现有代码**：`read_file(task.targetFile)`

**4. 提取质量/自测要求**：从 `03-quality.md` 提取 `DESIGN_REVIEW:4.1` 标记区段

**5. 读取相关 expert skill**：根据目标文件路径推断模块名，读取对应的 expert skill

### 🔴 2a-6. 平台层源码（涉及平台组件时强制执行，不可跳过）

> ⚠️ **当任务层级含"平台"，或任务描述含以下关键词时，此步骤为强制步骤：**
> `DataLoad` / `DataSave` / `ROI` / `VOI` / `TissueControl` / `MaskData` / `Volume` /
> `Layout` / `Cine` / `VRT` / `Palette` / `Density` / `SUV` / `DataLinkage` / `ImageTools`>
> **上游短路**：如 `.copilot-temp/roundtable-*/context-check.md` 已存在且含「平台源文件清单」，优先复用其中已读取的源码文件路径（直接 read_file），仅对未覆盖的接口做增量搜索。这避免了与 roundtable Step 5-7 的重复平台源码搜索。
**6a. 从平台域专家 skill 提取搜索关键词**

从步骤 5 读取的 {{PLATFORM_PREFIX}}-{领域}-expert skill 中，提取以下信息作为搜索关键词：
- **「核心接口速查」表**中的接口名/类名（如 `[你的平台接口名]`、`[你的平台接口名]`）
- **「关键数据类型」**中的类型名（如 `ExportConfig`、`Structure`）
- **「搜索策略」**中推荐的代码路径（如 `DataSave/BE/`）

🔴 **不要在应用代码里搜 using/include 来提取类名** — using 只有命名空间，没有类名。

**降级策略**：Tier 1 skill接口速查表 → Tier 2 skill代码搜索建议 → Tier 3 PBI英文关键词

**6b. 读取平台源码（本地优先 → MCP 降级）**

**路径A — 本地优先**（工作区包含 `{{PLATFORM_REPO}}` 文件夹时）：
1. `grep_search("接口名", { includePattern: "**/{{PLATFORM_REPO}}/**" })` 定位文件
2. `read_file("命中的头文件.h")` + `read_file("命中的实现文件.cpp")`

**路径B — MCP 降级**（本地没有 `{{PLATFORM_REPO}}` 时）：
1. `mcp_azuredevops_search_code({ searchText: "接口名", filters: { Repository: ["{{PLATFORM_REPO}}"] } })`
2. 取前 3 个结果，`mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "文件路径", versionType: "branch", version: "{{PLATFORM_BRANCH}}" })`

**6c. 验证检查点（硬阻断 — 不通过则禁止进入编码阶段）**

确认至少读取了 **1 个平台源文件**（.h / .cpp / .cs）。

**通过**：将读取到的源码保存为 `context.platformSource`，文件路径写入 `{workDir}/context-check.md`（如工作目录存在该文件）。

**未通过处理**：
1. 降级到下一 Tier 重试
2. 全部 Tier 失败 **且 MCP 不可用** → 标注「⚠️ 降级出口：未获取平台源码」，允许继续（降级通过）
3. 🔴 **MCP 可用但未搜索/未读取** → **禁止进入编码阶段**，必须重新执行步骤 6b

将读取到的源码保存为 `context.platformSource`，后续注入到编码 subAgent prompt 中。

> 🔴 **强制规则**：搜索关键词从 expert skill「核心接口速查」提取，但最终必须读取平台**完整源码**（头文件+实现），
> 不能仅停留在 skill 文档描述或设计文档伪代码层面。参考 `#platform-architecture` 搜索策略。

### 2a-7. 读取运行时配置文件（涉及 FE↔BE 通信时执行）

> ⚠️ **当任务涉及新增/修改 Operation、Widget、Model 注册或 BE↔FE 消息路由时，此步骤为强制步骤。**

**7a. 自动发现配置文件路径**

按以下优先级搜索：
1. 标准路径: `file_search("**/appdata/*/config/[你的配置目录]/[配置文件]")`
2. 拆分路径: `file_search("**/BE/appdata/*/config/[你的配置目录]/[配置文件]")`
3. 均未找到 → 跳过，标注「⚠️ 未找到运行时配置文件」

**7b. 读取与任务相关的配置文件**

| 任务类型 | 必读配置 | 关注内容 |
|----------|----------|----------|
| 新增/修改 Operation | `[后端配置文件]` | `<Item>` 条目中的 Operation 注册 |
| 修改 Operation 链 | `BE/WorkflowController.xml` | `<OperationName>` 链、线程模型 |
| 新增/修改 BE→FE 消息 | `[前端命令配置]` | `<Handler>` 条目（注意文件名拼写） |
| 新增 Widget/Model | `[后端配置文件]` | Widget/Model 注册条目 |

**7c. 编码时同步修改配置文件**

🔴 **强制规则**：如果任务需要新增 Operation/Widget/Model 注册或消息路由，编码 subAgent **必须同时修改对应的 XML 配置文件**，并标记 `// 🔴 HUMAN_CHECK: 新增 XML 配置条目，请确认注册信息正确`。

将读取到的配置条目保存为 `context.xmlConfig`，后续注入到编码 subAgent prompt 中。

### 2b. runSubagent 编码

```javascript
await runSubagent(`编码任务 ${task.id}: ${task.desc}`, `
    ${codingSubagentPrompt}
    
    ## 当前任务
    ${task.id}: ${task.desc}
    操作类型: ${task.operation}
    目标文件: ${task.targetFile}
    语言: ${task.layer.includes("BE") && task.layer.includes("平台") ? "C++" : "C#"}
    
    ## 实现骨架
    ${context.skeleton}
    
    ## 接口定义
    ${context.interface || context.cppInterface}
    
    ## 目标文件现有代码
    ${context.existingCode || "(新增文件，无现有代码)"}
    
    ## 项目规范
    ${context.expertKnowledge}
    
    ${context.platformSource ? `
    ## 平台层源码参考
    以下是涉及的平台层 API 完整源码，编码时必须以此为准：
    ${context.platformSource}
    ` : ''}
    
    ## 🔍 搜索指南（遇到未知信息时必须使用）
    
    🔴 **强制规则**: 编码中遇到不认识的枚举/类型/方法签名，
    必须先搜索确认，禁止凭记忆猜测。搜索后仍不确定才标记 HUMAN_CHECK。
    
    可用工具:
    1. grep_search("类名或枚举名") — 搜索本地工作区
    2. read_file("路径") — 读取本地文件
    3. mcp_azuredevops_search_code({ searchText: "类名", filters: { Repository: ["{{PLATFORM_REPO}}"] } }) — 搜索平台仓库
    4. mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "...", versionType: "branch", version: "{{PLATFORM_BRANCH}}" }) — 读取平台源码
    
    搜索策略: 本地 grep_search 优先 → MCP search_code 降级
    
    ## 🔴 输出要求
    直接 create_file / replace_string_in_file 写入项目文件。
    不确定的地方先搜索，仍不确定按以下分级标记：
    - 影响功能正确性（算法/业务逻辑/数据结构）→ // 🔴 HUMAN_CHECK_CRITICAL: <原因>
    - 不影响正确性（命名/注释/风格/可选优化）→ // 🟡 HUMAN_CHECK_REVIEW: <原因>
`);
```

### 2c. 检查点

```javascript
// 🔴 文件编辑熔断机制
// 追踪每个文件的连续编辑失败次数
if (!globalEditFailures) globalEditFailures = {};
const key = task.targetFile;

// 验证文件已写入
const fileExists = exists(task.targetFile);
if (!fileExists) {
    globalEditFailures[key] = (globalEditFailures[key] || 0) + 1;
    if (globalEditFailures[key] >= 3) {
        // 🔴 熔断：连续失败 ≥3 次，停止编辑，标记 CRITICAL 并暂停
        //    在目标文件（或报告中）标记: // 🔴 HUMAN_CHECK_CRITICAL: 文件编辑连续失败3次，需人工介入
        //    使用 ask_questions:
        //      header: "编辑熔断"
        //      question: "文件 {task.targetFile} 连续编辑失败 3 次，已自动停止。\n\n可能原因：文件路径错误、内容匹配失败、文件被锁定。\n\n请检查后选择操作："
        //      选项A: "跳过此任务，继续下一个"
        //      选项B: "我来手动修改，然后继续" (allowFreeformInput: true)
        //      选项C: "终止整个编码流程"
        continue; // 跳到下一个任务
    }
    // 未达熔断阈值，重试一次
    runSubagent(`重试 ${task.id}`, retryPrompt);
} else {
    globalEditFailures[key] = 0; // 成功则重置计数
}

// 检查 HUMAN_CHECK 标记（分级处理）
const criticals = grep_search("HUMAN_CHECK_CRITICAL", { includePattern: task.targetFile });
const reviews = grep_search("HUMAN_CHECK_REVIEW", { includePattern: task.targetFile });
// 兼容旧格式：匹配 "HUMAN_CHECK:" 但排除已匹配的 CRITICAL/REVIEW
const legacyChecks = grep_search("HUMAN_CHECK:", { includePattern: task.targetFile })
    .filter(m => !m.includes("CRITICAL") && !m.includes("REVIEW"));

const allCriticals = [...criticals, ...legacyChecks]; // 旧格式按 CRITICAL 处理

if (allCriticals.length > 0) {
    // 🔴 即时暂停：展示 CRITICAL 标记详情，使用 ask_questions 对话框
    //    header: "人工检查"
    //    question: "发现 {N} 个 CRITICAL 标记（影响功能正确性），需要确认：\n\n[列出每个标记的文件、行号、原因]\n\n另有 {M} 个 REVIEW 标记将在完成报告中统一审查。"
    //    选项A（推荐）: "确认，继续下一个任务"
    //    选项B: "需要修改" (allowFreeformInput: true)
    // 等待用户确认后继续下一任务
} else if (reviews.length > 0) {
    // 🟡 仅有 REVIEW 标记，记录计数，自动继续
    // 输出: "✅ 任务 {taskId} 完成，{N} 个 REVIEW 标记将在完成报告中统一审查"
} else {
    // ✅ 无需人工介入，自动继续
}
```

---

## 🔴 Step 3：完成报告

```markdown
🔧 **编码完成报告**

### 任务执行结果
| 任务ID | 状态 | 目标文件 | CRITICAL | REVIEW |
|--------|------|----------|----------|--------|
| BE-01 | ✅ 完成 | src/.../IXxxService.cs | 0 | 0 |
| BE-02 | ✅ 完成 | src/.../XxxHelper.cpp | 1 | 2 |
| FE-01 | ✅ 完成 | src/.../XxxViewModel.cs | 0 | 1 |

### 📁 文件变更清单
- **新增**: 2 个文件
  - `src/.../IXxxService.cs`
  - `src/.../XxxHelper.cpp`
- **修改**: 1 个文件
  - `src/.../XxxViewModel.cs`

### 🔴 CRITICAL 标记汇总（已在编码过程中逐个确认）
| 文件 | 行号 | 原因 | 确认状态 |
|------|------|------|----------|
| XxxHelper.cpp | L45 | 不确定坐标系转换算法 | ✅ 已确认 |

### 🟡 REVIEW 标记审查（统一审查）
> 以下标记不影响功能正确性，建议在代码审查时一并处理：

| 文件 | 行号 | 原因 |
|------|------|------|
| XxxHelper.cpp | L23 | 变量命名建议优化 |
| XxxHelper.cpp | L67 | 可添加性能优化注释 |
| XxxViewModel.cs | L112 | 建议补充 XML 文档注释 |

### 🔧 建议验证
1. 编译检查: `dotnet build` / `cmake --build`
2. 运行现有测试
3. 审查 REVIEW 标记处（非阻断，可稍后处理）
```

---

## ⚠️ 关键约束

| 约束 | 说明 |
|------|------|
| **串行执行** | 逐任务完成，不并行。用时间换质量 |
| **只消费圆桌会议** | 不兼容其他设计文档来源 |
| **不覆盖整文件** | 修改任务只改动需要变更的部分 |
| **HUMAN_CHECK 分级处理** | CRITICAL 即时暂停等确认；REVIEW 不暂停，Step 3 统一审查 |
| **subagent 必须写文件** | 不接受只返回上下文的结果 |

---

## ⚠️ 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 不解析 CODING_TASK_LIST | 无法确定任务边界和依赖 | grep + parse 标记区段 |
| 全文读取设计文档 | prompt 空间耗尽 | 用标记精准提取 |
| 修改文件时覆盖整文件 | 丢失现有代码 | 定位锚点 + replace_string_in_file |
| 跳过 HUMAN_CHECK | 不确定处可能出错 | CRITICAL 暂停确认，REVIEW 统一审查 |
| 不按拓扑序执行 | 依赖未满足导致编译错误 | 先排序再串行执行 |

---

## 执行进度提示

```markdown
🔧 **Coding Agent 启动**

📋 设计来源: roundtable-{NNN}
📊 任务总数: X 个

---
📂 **Step 0：加载设计文档**
✅ 发现 roundtable-{NNN}
✅ 读取 05-implementation.md
✅ 解析 CODING_TASK_LIST（X 个任务）

📋 **Step 1：执行计划**
✅ 拓扑排序完成
✅ 用户已确认执行计划

🔄 **Step 2：逐任务编码**
✅ BE-01: 实现xxx接口 → src/.../IXxxService.cs (新增)
⭕ BE-02: xxx平台层实现 → src/.../XxxHelper.cpp (新增)
⭕ FE-01: xxxViewModel → src/.../XxxViewModel.cs (修改)

📊 **进度: 1/X 完成**
```

---

## 相关资源

- 📖 [执行流程详解](references/execution-flow.md) - Step 0-3 完整伪代码
- 📋 [编码Prompt模板](references/subagent-prompt.md) - 编码subagent的prompt
- 🔧 [修改策略](references/modify-strategy.md) - 已有文件的定位+修改方法
- 🪑 [圆桌会议](../roundtable-debate/SKILL.md) - 上游设计文档生成
