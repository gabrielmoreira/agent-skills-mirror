---
name: doa-workcopilot
description: >
  项目全生命周期工作站。统一编排所有 Agent 和 Skill，从项目初始化到交付的一站式工作流。
  自动识别新项目/老项目，引导需求分析、系统设计、任务拆解、脚手架搭建和工程轨道配置。
  USE FOR: 开始新项目、接手老项目、初始化工作流、workcopilot、工作站、项目启动、
  新建项目、项目脚手架、scaffold project、init project、start project、work copilot。
  DO NOT USE FOR: 单个文档生成（直接用 doa-ppt / doa-metting 等）、纯代码调试（用 systematic-debugging）。
argument-hint: '可选: "new" (新项目) | "existing" (老项目) | 留空则交互引导'
---

# DOA WorkCopilot — 项目全生命周期工作站

## 核心理念

一个项目的成功从**第一行配置**开始，而非第一行代码。
WorkCopilot 统一编排所有 Agent 和 Skill，确保每一步都有正确的角色、正确的约束、正确的产出。

> 🔒 **自动持久化契约**：每次会话结束时，WorkCopilot 自动更新 `.workcopilot/` 下的项目状态文件（state.json、changelog.md、decisions.md、tech-debt.md），确保项目记忆永不丢失。无需用户手动触发。

---

## 🚀 团队部署（首次使用必读）

本 Skill 是**完全自包含**的，包含全部 Agent 定义、工作流和脚手架模板。
团队成员只需获取 `doa-workcopilot/` 目录即可上手。

### 方式一：自动部署（推荐）

```powershell
# 在 PowerShell 中执行
& "path/to/doa-workcopilot/scripts/deploy.ps1"
```

脚本会自动：
1. 将 skill 安装到 `~/.claude/skills/doa-workcopilot/`
2. 在 `~/.claude/agents/` 安装 6 个 Agent 文件（已存在则跳过）
3. 在 `~/.claude/skills/` 安装 12 个附属 Skill（已存在则跳过）

### 方式二：手动部署

1. 复制 `doa-workcopilot/` 到 `~/.claude/skills/`
2. 复制 `embedded-agents/` 下的6个 `.md` 文件到 `~/.claude/agents/`
3. 复制 `embedded-skills/` 下的12个子目录到 `~/.claude/skills/`（已存在同名则跳过）

### 内置资源清单

```
doa-workcopilot/
├── SKILL.md                              ← 主编排逻辑（本文件）
├── scripts/
│   └── deploy.ps1                        ← 团队一键部署脚本
├── references/                           ← 脚手架模板 & 内嵌工作流
│   ├── agents.md                         ← 6 个 Agent 精简角色定义
│   ├── embedded-harness.md               ← Harness 工程轨道工作流
│   ├── embedded-spec-flow.md             ← Spec-Flow 结构化开发流程
│   ├── dotnet-scaffold.md                ← .NET 8 脚手架模板
│   ├── python-scaffold.md                ← FastAPI 脚手架模板
│   └── react-scaffold.md                 ← React + Vite 脚手架模板
├── embedded-agents/                      ← 完整 Agent 定义文件（项目注入用）
│   ├── requirements-analyst.md
│   ├── system-architect.md
│   ├── backend-engineer.md
│   ├── frontend-engineer.md
│   ├── test-engineer.md
│   └── mermaid-diagram.md
├── embedded-hooks/                       ← PreToolUse Hook（项目注入用）
│   ├── update-workcopilot.json           ← Hook 配置（commit/build/docker 前拦截）
│   └── scripts/
│       └── check-workcopilot.ps1         ← 拦截脚本（检查 .workcopilot 是否已更新）
├── embedded-prompts/                     ← Prompt 模板（项目注入用）
│   ├── code-review.prompt.md             ← 全面 Code Review（安全+性能+规范+逻辑）
│   └── generate-tests.prompt.md          ← 生成 xUnit + Moq 单元测试
└── embedded-skills/                      ← 完整 Skill 包（项目注入用）
    ├── doa-ppt/          (SKILL.md + 2 模板)
    ├── doa-metting/      (SKILL.md + 1 模板)
    ├── doa-apidoc/       (SKILL.md + 2 模板)
    ├── doa-image/        (SKILL.md)
    ├── doa-quotation/    (SKILL.md + 3 模板)
    ├── doa-testreport/   (SKILL.md)
    ├── doa-e2etest/      (SKILL.md + 3 参考文档)
    ├── doa-harness/      (SKILL.md + 5 模板)
    ├── spec-flow-main/   (SKILL.md + 模板 + 参考 + 脚本)
    ├── brainstorming/    (SKILL.md)
    ├── frontend-design/  (SKILL.md)
    └── ui-ux-pro-max/    (SKILL.md + data + scripts)
```

### 项目级注入机制

初始化项目时，WorkCopilot 会自动将 Agent、Skill、Hook 和 Prompt **注入到项目目录**：

```
{project-root}/
├── .github/
│   ├── hooks/                 ← 从 embedded-hooks/ 注入
│   │   ├── update-workcopilot.json
│   │   └── scripts/
│   │       └── check-workcopilot.ps1
│   └── prompts/               ← 从 embedded-prompts/ 注入
│       ├── code-review.prompt.md
│       └── generate-tests.prompt.md
└── .claude/
    ├── agents/                ← 从 embedded-agents/ 注入
    │   ├── requirements-analyst.md
    │   ├── system-architect.md
    │   ├── backend-engineer.md
    │   ├── frontend-engineer.md
    │   ├── test-engineer.md
    │   └── mermaid-diagram.md
    └── skills/                ← 从 embedded-skills/ 注入
        ├── doa-ppt/
        ├── doa-metting/
        ├── doa-apidoc/
        ├── doa-image/
        ├── doa-quotation/
        ├── doa-e2etest/
        ├── doa-harness/
        ├── doa-testreport/
        ├── spec-flow-main/
        ├── brainstorming/
        ├── frontend-design/
        └── ui-ux-pro-max/
```

**优先级规则**：项目级 `.claude/` > 用户级 `~/.claude/`。
当项目目录和用户目录下存在同名 Agent 或 Skill 时，**优先使用项目里的版本**。
这意味着团队可以对项目级的 Agent/Skill 做定制化修改，不会受到个人配置的干扰。

## 编排资源清单

### Agent 矩阵

读取 [references/agents.md](./references/agents.md) 获取精简角色定义（调度用摘要），完整版位于 `embedded-agents/` 目录。

| Agent | 角色 | 调度时机 | 核心职责 |
|-------|------|---------|---------|
| `requirements-analyst` | 需求分析师 | Phase 2 | 业务拆解→EARS 需求→验收标准 |
| `system-architect` | 系统架构师 | Phase 3 | 架构设计→API 设计→数据建模 |
| `backend-engineer` | 后端工程师 | Phase 5 | API 实现→数据库→认证→安全 |
| `frontend-engineer` | 前端工程师 | Phase 5 | 组件设计→状态管理→路由→UI |
| `test-engineer` | 测试工程师 | Phase 5 | 测试策略→自动化→覆盖率 |
| `mermaid-diagram` | 时序图架构师 | Phase 3 | 交互流程→Mermaid 时序图 |

> **Agent 调度方式**：使用 `runSubagent` 调度对应 Agent，并在 prompt 中注入 `references/agents.md` 中该 Agent 的角色定义作为系统提示。

### Skill 工具箱

以下 Skill 的核心工作流已内置，无需额外安装即可使用：

| Skill | 用途 | 调度时机 | 内置位置 |
|-------|------|---------|---------|
| `harness` | 搭建工程轨道 | 老项目首步 / 新项目收尾 | [embedded-harness.md](./references/embedded-harness.md) |
| `spec-flow` | 结构化需求-设计-任务流 | 新代码项目 Phase 2-4 | [embedded-spec-flow.md](./references/embedded-spec-flow.md) |
| `brainstorming` | 创意探索与需求澄清 | 任何创作性工作之前 | embedded-skills/brainstorming/ |
| `frontend-design` | 高质量前端界面设计 | Phase 5 / 按需 | embedded-skills/frontend-design/ |
| `ui-ux-pro-max` | UI/UX 专业设计系统 | Phase 5 / 按需 | embedded-skills/ui-ux-pro-max/ |

以下 Skill 已内嵌在 `embedded-skills/` 中，项目初始化时自动注入，按需调度：

| Skill | 用途 | 调度时机 |
|-------|------|---------|
| `doa-ppt` | 生成方案PPT | 按需 |
| `doa-metting` | 生成会议纪要 | 按需 |
| `doa-apidoc` | 生成接口文档 | Phase 3 后 |
| `doa-image` | 生成可视化页面 | 按需 |
| `doa-quotation` | 生成报价单 | 按需 |
| `doa-testreport` | 基于截图生成测试报告（HTML/PDF/Excel） | 按需 |
| `doa-e2etest` | Playwright E2E 测试全流程 → HTML/PDF 报告 | Phase 5.5 / 按需 |


---

## 主工作流

```
调用 WorkCopilot
  → Step 0: 项目类型判定（新 / 老）
  ┌─ 老项目路线 ──────────────────────────────────────┐
  │ → Step E1: 运行 Harness（探测 + 生成工程轨道）       │
  │ → Step E2: 生成/更新 docs/README.md                   │
  │ → Step E3: 注入项目级 Agent & Skill & Hook（6+12+1）          │
  │ → Step E4: 输出 Day-1 验证 & 可用命令清单            │
  │ → Step E5: 状态持久化 + 初始化项目记忆               │
  └──────────────────────────────────────────────────────┘
  ┌─ 新项目路线 ──────────────────────────────────────────┐
  │ → Step N1: 项目子类型判定（代码 / 非代码）             │
  │   ┌─ 非代码项目 ─────────────────────────────────────┐│
  │   │ → 运行 Harness（生成工程轨道）                    ││
  │   │ → 引导选择合适 Skill（PPT/文档/报价/图片等）      ││
  │   │ → 调度 Skill 执行，产出存入 output/{名称}/        ││
  │   │ → 状态持久化（state.json + changelog.md）         ││
  │   └──────────────────────────────────────────────────┘│
  │   ┌─ 代码项目 ───────────────────────────────────────┐│
  │   │ → Phase 1: 技术栈 + 规模 + CI/CD + 环境选型      ││
  │   │ → Phase 2-4: 委托 spec-flow-main skill           ││
  │   │   （需求分析/系统设计/任务拆解，可跳过/可导入）    ││
  │   │ → Phase 5: 脚手架搭建（支持完整/空项目模式）       ││
  │   │   ├── 5.0 脚手架模式判定 + 参考图导入             ││
  │   │   ├── 5.1 后端（完整/空项目 + 多模块/微服务）     ││
  │   │   ├── 5.2 前端（完整/空项目 + 可导入参考图）      ││
  │   │   ├── 5.3 数据库                                  ││
  │   │   ├── 5.4 Docker                                  ││
  │   │   ├── 5.5 测试框架                                ││
  │   │   ├── 5.6 Git 初始化                              ││
  │   │   ├── 5.7 CI/CD 管线                              ││
  │   │   ├── 5.8 多环境配置                              ││
  │   │   └── 5.9 安全基线                                ││
  │   │ → Phase 6: 工程轨道（Harness）                     ││
  │   │ → Phase 6.5: 注入项目级 Agent & Skill & Hook             ││
  │   │ → Phase 7: Day-1 验证                             ││
  │   │ → Phase 8: 项目状态持久化                         ││
  │   │ → Phase 9: 迭代开发（持续循环入口）↺              ││
  │   └──────────────────────────────────────────────────┘│
  └───────────────────────────────────────────────────────┘
  ┌─ 迭代入口（已初始化项目再次调用）──────────────────────┐
  │ → 检测 .workcopilot/state.json                        │
  │ → 自动跳过初始化，直接进入 Phase 9 迭代开发            │
  └───────────────────────────────────────────────────────┘
```

---

## Step 0: 项目类型判定

**前置检查**：先检测当前工作区是否存在 `.workcopilot/state.json`。

如存在：
- 读取 `source` 字段判断来源（`"existing"` 老项目 / `"non-code"` 非代码项目 / 无则为新代码项目）
- 如果是非代码项目（`source: "non-code"`），**直接询问用户本次要做什么**（复用非代码项目 Q2 选项），调度对应 Skill，完成后追加迭代记录
- 检查初始化阶段是否全部完成（新项目: phase1-7 / 老项目: E1-E4）
- 如全部完成，**直接跳转 Phase 9 迭代开发模式**，不再询问项目类型
- 如有未完成阶段，提示用户是否继续未完成的初始化
- 同时加载 `.workcopilot/decisions.md` 和 `.workcopilot/tech-debt.md` 作为上下文

如不存在，使用 `vscode_askQuestions` 交互：

```
Q1: 项目类型
  - "🆕 新创建的项目" (recommended)
  - "📂 已存在的老项目"
```

如果参数中已含 `new` 或 `existing`，跳过交互直接进入对应路线。

---

## 老项目路线

### Step E1: 运行 Harness 工程轨道

读取 [references/embedded-harness.md](./references/embedded-harness.md) 获取完整流程，执行探测-确认-生成流程。
如 harness 文件已存在，自动切换到增量更新模式。

同时执行**代码质量快速扫描**：
- 是否存在测试文件 / 测试框架
- 是否配置了 lint / formatter
- 是否存在 CI/CD 配置
- 是否存在 `.gitignore`

扫描结果纳入 `docs/README.md` 的“待改进项”段落。

### Step E2: 生成/更新 docs/README.md

基于 harness 探测到的项目信息，生成或更新 `docs/README.md`：

**README 结构**：
```markdown
# {项目名称}

{用户在 harness Step 2 输入的项目描述}

## 技术栈

{从 harness 探测结果填充，按子项目分段}

## 快速开始

### 环境要求
{根据技术栈列出 Node/dotnet/Python 版本要求}

### 安装 & 运行
{根据包管理器和框架生成具体命令}

## 项目结构

{从 AGENTS.md 模块地图提炼，简化展示}

## 开发规范

- 工程轨道：`.github/copilot-instructions.md`
- Agent 约束：`.github/AGENTS.md`
- 编码规则：`docs/rules/*.md`
- 验证命令：参见 `.vscode/tasks.json`
```

如果 `docs/README.md` 已存在：
1. 读取现有内容
2. 仅更新技术栈、快速开始、项目结构段落
3. 保留用户自定义段落（如 License、Contributing 等）

> **注意**：项目根目录的 `README.md` 不做任何修改，WorkCopilot 的文档统一放在 `docs/` 目录。

### Step E3: 注入项目级 Agent、Skill、Hook & Prompt

将内嵌的 Agent、Skill、PreToolUse Hook 和 Prompt 注入到项目目录，使其成为项目级配置。

执行操作：

```
1. 在项目根目录创建 .claude/agents/ 和 .claude/skills/ 目录
2. 复制 embedded-agents/ 下的 6 个 Agent 文件 → {project}/.claude/agents/
3. 复制 embedded-skills/ 下的 12 个 Skill 目录 → {project}/.claude/skills/
4. 复制 embedded-hooks/ 下的 Hook 配置 → {project}/.github/hooks/
   - update-workcopilot.json → .github/hooks/
   - scripts/check-workcopilot.ps1 → .github/hooks/scripts/
5. 复制 embedded-prompts/ 下的 Prompt 文件 → {project}/.github/prompts/
   - code-review.prompt.md → .github/prompts/
   - generate-tests.prompt.md → .github/prompts/
6. 如果目标位置已存在同名文件，询问用户是否覆盖
```

> **Hook 说明**：`check-workcopilot.ps1` 是 PreToolUse 拦截脚本，在执行 `git commit/push`、`dotnet build/publish`、`docker build` 前自动检查 `.workcopilot/changelog.md` 是否已更新。如未更新，将阻止操作并提示先执行会话持久化。

> **Prompt 说明**：`code-review.prompt.md` 和 `generate-tests.prompt.md` 注入到 `.github/prompts/`，团队成员在 Chat 中输入 `/` 即可调用全面 Code Review 或生成 xUnit 单元测试。

注入后项目结构：
```
{project}/
├── .github/
│   ├── hooks/
│   │   ├── update-workcopilot.json
│   │   └── scripts/
│   │       └── check-workcopilot.ps1
│   └── prompts/
│       ├── code-review.prompt.md
│       └── generate-tests.prompt.md
└── .claude/
    ├── agents/
    │   ├── requirements-analyst.md
    │   ├── system-architect.md
    │   ├── backend-engineer.md
    │   ├── frontend-engineer.md
    │   ├── test-engineer.md
    │   └── mermaid-diagram.md
    └── skills/
        ├── doa-ppt/
        ├── doa-metting/
        ├── doa-apidoc/
        ├── doa-image/
        ├── doa-quotation/
        ├── doa-e2etest/
        ├── doa-harness/
        ├── spec-flow-main/
        ├── brainstorming/
        ├── frontend-design/
        └── ui-ux-pro-max/
```

> **优先级**：项目级 `.claude/` > 用户级 `~/.claude/`。团队成员本地的同名 Agent/Skill 不会干扰项目。

### Step E4: 输出验证 & 命令清单

输出：
1. harness Day-1 验证指令
2. 已注入的 Agent（6个）& Skill（12个）清单
3. 可用 Skill 操作提醒（PPT/会议纪要/接口文档/报价/E2E测试/脑暴/结构化需求等）

### Step E5: 老项目状态持久化

老项目完成 E1-E4 后，同样生成 `.workcopilot/state.json`，使后续调用可进入迭代模式。

```json
{
  "version": "1.0",
  "source": "existing",
  "createdAt": "...",
  "updatedAt": "...",
  "project": {
    "name": "{从 harness 探测到的项目名}",
    "description": "{用户在 E1 输入的描述}",
    "detectedStack": {
      "backend": "dotnet | python | node | other",
      "frontend": "react | vue | angular | h5 | other",
      "database": "sqlserver | postgresql | mysql | other"
    }
  },
  "phases": {
    "E1": { "status": "completed", "completedAt": "..." },
    "E2": { "status": "completed", "completedAt": "..." },
    "E3": { "status": "completed", "completedAt": "..." },
    "E4": { "status": "completed", "completedAt": "..." }
  },
  "iterations": [],
  "services": []
}
```

同时初始化项目记忆文件（同 Phase 8.1）：
- `.workcopilot/decisions.md`（空模板）
- `.workcopilot/tech-debt.md`（空模板，可从 E1 扫描结果中预填已知问题）
- `.workcopilot/changelog.md`（空模板）

> **E1 扫描结果转化**：如果 E1 代码质量扫描发现缺少测试框架、缺少 lint 等问题，自动写入 `tech-debt.md` 作为初始技术债记录。

---

## 新项目路线

### Step N1: 项目子类型判定

使用 `vscode_askQuestions`：

```
Q1: 项目子类型
  - "💻 代码项目（Web应用/API/系统）" (recommended)
  - "📄 非代码项目（PPT/文档/报价/设计稿）"
```

#### 非代码项目分流

如果选择非代码项目，进一步询问：

```
Q2: 要做什么？
  - "📊 PPT / 方案演示" → 调用 doa-ppt
  - "📋 会议纪要" → 调用 doa-metting
  - "💰 项目报价" → 调用 doa-quotation
  - "📝 接口文档" → 调用 doa-apidoc
  - "🎨 可视化页面/长图" → 调用 doa-image
  - "📄 Word 文档" → 调用 docx skill
  - "🖼️ 前端设计稿" → 调用 frontend-design
```

#### 非代码项目 Harness 工程轨道

非代码项目在调度 Skill 之前，先运行 Harness 生成工程轨道（同老项目 Step E1 逻辑）：

读取 [references/embedded-harness.md](./references/embedded-harness.md) 执行探测-确认-生成流程，生成：
- `.github/copilot-instructions.md`
- `.github/AGENTS.md`
- `CODEOWNERS`

> **简化规则**：非代码项目不生成 `.vscode/tasks.json` 和 `docs/rules/*.md`（无代码构建/测试需求）。如 harness 文件已存在，自动跳过。

#### 非代码项目产出目录约定

所有非代码项目的产出文件（PPT、Excel、PDF、Word、图片等）统一存放在 `output/` 目录下，按产出名称建立子文件夹：

```
{project-root}/
└── output/
    ├── {产出名称A}/              # 如 "Q3季度汇报PPT"
    │   ├── Q3季度汇报.pptx
    │   └── generate_ppt.py       # 生成脚本（如有）
    ├── {产出名称B}/              # 如 "项目报价单"
    │   ├── 报价单_v1.xlsx
    │   └── generate_quotation.py
    └── {产出名称C}/              # 如 "API接口文档"
        ├── 接口说明书.pdf
        └── generate_apidoc.py
```

**命名规则**：
- 子文件夹名称 = 用户描述的产出名称（中文或英文均可），简洁明了
- 如用户未指定名称，使用 `vscode_askQuestions` 询问
- 生成脚本（Python 等中间文件）与最终产出放在同一子文件夹内
- 同一产出的多个版本用 `_v1`、`_v2` 后缀区分

**调度 Skill 时的产出路径传递**：
- 调用对应 Skill 前，先创建 `output/{产出名称}/` 目录
- 在 Skill 调度的 prompt 中明确指定产出输出路径为 `output/{产出名称}/`
- 确保 Skill 生成的所有文件都写入该目录

选择后调度对应 Skill 执行，产出文件存入 `output/{产出名称}/`。

#### 非代码项目状态持久化

非代码项目完成后，同样生成 `.workcopilot/state.json` 及记忆文件，确保项目记忆一致性。

执行操作：

1. 使用 `vscode_askQuestions` 收集项目名称和描述（如尚未收集）
2. 创建 `.workcopilot/` 目录及以下文件：

```json
// .workcopilot/state.json
{
  "version": "1.0",
  "source": "non-code",
  "timezone": "Asia/Shanghai",
  "createdAt": "...",
  "updatedAt": "...",
  "project": {
    "name": "{项目名}",
    "description": "{项目描述}",
    "type": "non-code",
    "skill": "doa-ppt | doa-metting | doa-quotation | doa-apidoc | doa-image | docx | frontend-design"
  },
  "outputs": [
    {
      "name": "{产出名称}",
      "skill": "doa-ppt",
      "path": "output/{产出名称}/",
      "createdAt": "..."
    }
  ],
  "iterations": [
    {
      "id": "iter-001",
      "date": "...",
      "scope": "{首次调度的 Skill 及产出摘要}"
    }
  ]
}
```

3. 初始化记忆文件：
   - `.workcopilot/decisions.md`（空模板）
   - `.workcopilot/changelog.md`（记录首次产出）

> **后续调用**：非代码项目再次调用 WorkCopilot 时，检测到 `source: "non-code"`，直接询问用户本次要做什么（复用上方 Q2 选项），新产出继续存入 `output/{新产出名称}/`，并在完成后追加 `outputs` 数组和迭代记录到 `state.json` 和 `changelog.md`。Harness 已存在则自动跳过。

---

### 代码项目 Phase 1: 技术栈选型

使用 `vscode_askQuestions` 一次性收集：

```
Q1: 项目名称
  [自由输入]

Q2: 一句话描述项目
  [自由输入]

Q3: 后端技术栈
  - ".NET 8 (WebAPI + SqlSugar)" (recommended)
  - ".NET 8 (WebAPI + EF Core)"
  - "Python (FastAPI + SQLAlchemy)"
  - "其他（请说明）"

Q4: 前端技术栈
  - "React + TypeScript + Ant Design" (recommended)
  - "纯 HTML5 + CSS + JS (轻量级)"
  - "其他（请说明）"

Q5: 数据库
  - "SQL Server" (recommended)
  - "PostgreSQL"
  - "MySQL"
  - "SQLite (开发/轻量)"
  - "其他（请说明）"

Q6: 认证方式
  - "JWT Token 认证" (recommended)
  - "Azure AD / Entra ID"
  - "Cookie Session"
  - "暂不需要"

Q7: 是否需要 Docker 支持
  - "是" (recommended)
  - "否"

Q8: 项目规模 & 架构
  - "🏠 单体应用（单后端 + 单前端）" (recommended)
  - "📦 多模块单体（共享代码库，多个功能模块）"
  - "🔗 微服务架构（多个独立后端服务 + API 网关）"

Q9: CI/CD 管线
  - "GitHub Actions" (recommended)
  - "Azure DevOps Pipelines"
  - "暂不配置"

Q10: 多环境配置
  - "dev + prod（两套环境）" (recommended)
  - "dev + staging + prod（三套环境）"
  - "仅 dev（开发环境）"

Q-scaffold: 脚手架生成模式
  header: "后端和前端分别选择脚手架模式"

  Q-scaffold-backend: 后端脚手架模式
    - "🏗️ 完整脚手架（包含业务代码骨架 + 示例）" (recommended)
    - "📦 空项目（仅项目结构 + 基础配置，不含业务代码）"

  Q-scaffold-frontend: 前端脚手架模式
    - "🏗️ 完整脚手架（包含页面骨架 + 路由 + 状态管理）" (recommended)
    - "📦 空项目（仅项目结构 + 基础配置，不含页面代码）"
    - "🖼️ 完整脚手架 + 参考设计图（导入 UI 参考图辅助生成）"
```

> **规模说明**：
> - **单体应用**：适合中小型项目，一个后端 + 一个前端，快速启动
> - **多模块单体**：适合中大型项目，单个解决方案内按模块拆分（.NET Multi-Project / Python Package），共享数据库
> - **微服务架构**：适合大型项目，每个服务独立部署、独立数据库，通过 API 网关统一入口

收集完成后，将信息汇总为 `project-config` 数据结构，供后续 Phase 使用：

```yaml
project:
  name: "{项目名}"
  description: "{项目描述}"
  backend:
    stack: "dotnet" | "python"
    framework: "webapi" | "fastapi"
    orm: "sqlsugar" | "efcore" | "sqlalchemy"
  frontend:
    stack: "react" | "h5"
    ui: "antd" | "none"
  database: "sqlserver" | "postgresql" | "mysql" | "sqlite"
  auth: "jwt" | "azure-ad" | "cookie" | "none"
  docker: true | false
  scale: "monolith" | "modular" | "microservice"
  cicd: "github-actions" | "azure-devops" | "none"
  environments: "dev-prod" | "dev-staging-prod" | "dev-only"
  docs: "generate" | "import" | "skip"
  scaffold:
    backend: "full" | "empty"
    frontend: "full" | "empty" | "full-with-ref-image"
    ref_image: "{path}" | null      # 前端参考设计图路径（仅 full-with-ref-image 时有值）
```

---

### 代码项目 Phase 2-4 前置：文档策略判定

Phase 2（需求分析）、Phase 3（系统设计）、Phase 4（任务拆解）均支持三种模式：

使用 `vscode_askQuestions` 询问：

```
Q11: 需求 & 设计文档策略
  - "📝 AI 生成（逐阶段引导生成需求/设计/任务文档）" (recommended)
  - "📂 我有现成资料（上传或粘贴，AI 整理为标准格式）"
  - "⏭️ 跳过（直接进入脚手架搭建，后续按需补充）"
```

#### 模式说明

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| **AI 生成** | 按原流程逐阶段引导生成 proposal → requirements → design → tasks | 从零开始的新项目 |
| **导入现有资料** | 用户提供需求文档/PRD/设计稿/会议纪要等，AI 整理为标准格式写入 `.spec-flow/` | 已有产品经理或客户提供的资料 |
| **跳过** | Phase 2-4 全部跳过，直接进入 Phase 5 脚手架搭建 | 快速原型、已有明确方案 |

#### 导入模式流程

当用户选择"我有现成资料"时：

```
1. 提示用户提供资料（支持以下方式）：
   - 直接在对话中粘贴文本
   - 指定工作区中的文件路径（.md / .docx / .pdf / .txt）
   - 提供多份资料，逐份处理

2. AI 读取并分析资料内容

3. 调用 spec-flow-main skill，将资料作为输入：
   - spec-flow 自动按其标准格式在 .spec-flow/active/{project-name}/ 下
     生成 proposal.md、requirements.md、design.md、tasks.md
   - WorkCopilot 不自行创建这些文件，完全复用 spec-flow 的产出

4. 展示整理结果摘要，用户确认或修改
```

> **提示**：导入模式下，如果用户资料只覆盖部分阶段（如只有需求没有设计），AI 会对已有部分做整理，缺失部分询问用户是"AI 补充生成"还是"暂时跳过"。

#### 跳过模式

跳过后：
- Phase 2-4 状态标记为 `skipped`（写入 state.json）
- 直接进入 Phase 5 脚手架搭建
- 后续可通过 Phase 9 迭代开发中选择"补充需求/设计文档"来补做

---

### 代码项目 Phase 2: 需求分析

> **前置条件**：仅在文档策略选择"AI 生成"时执行。"导入"模式在上方统一处理，"跳过"模式直接进入 Phase 5。

**委托 Skill**: `spec-flow-main`

直接调用 spec-flow-main skill 的 Phase 1-2 流程，由 spec-flow 在 `.spec-flow/active/{project-name}/` 下生成 `proposal.md` 和 `requirements.md`。

WorkCopilot 不自行定义文档结构，完全复用 spec-flow 的文档格式和交互流程。

**⏸️ 阶段确认**：spec-flow 会在每个阶段完成后自动请求用户确认。

---

### 代码项目 Phase 3: 系统设计

> **前置条件**：仅在文档策略选择"AI 生成"时执行。

**委托 Skill**: `spec-flow-main`

直接调用 spec-flow-main skill 的 Phase 3 流程，由 spec-flow 在 `.spec-flow/active/{project-name}/` 下生成 `design.md`。

WorkCopilot 不自行定义文档结构，完全复用 spec-flow 的设计文档格式和交互流程。

> **上下文传递**：将 Phase 1 的技术选型（`project-config`）作为上下文传递给 spec-flow，确保设计文档与技术栈选型一致。

**⏸️ 阶段确认**：spec-flow 会在阶段完成后自动请求用户确认。

---

### 代码项目 Phase 4: 任务拆解

> **前置条件**：仅在文档策略选择"AI 生成"时执行。

**委托 Skill**: `spec-flow-main`

调用 spec-flow-main skill 的 Phase 4 流程，由 spec-flow 在 `.spec-flow/active/{project-name}/` 下生成 `tasks.md`。WorkCopilot 在 spec-flow 生成的基础上，补充以下增强信息：

#### 4.1 任务分组与拆解

按以下阶段拆解任务，每阶段对应一个**里程碑**：

```
里程碑 M1: 基础设施搭建（Sprint 1）
  T-001: 创建后端项目结构          [Low]  [4h]  backend-engineer
  T-002: 创建前端项目结构          [Low]  [4h]  frontend-engineer
  T-003: 配置数据库连接            [Med]  [4h]  backend-engineer
  T-004: 搭建认证模块              [Med]  [8h]  backend-engineer
  T-005: 配置 Docker（如需）       [Low]  [4h]  backend-engineer

里程碑 M2: 核心功能开发（Sprint 2-N）
  T-00x: （根据需求文档 FR 列表生成，每个 FR 至少拆为 1 个任务）

里程碑 M3: 集成 & 测试（Sprint N+1）
  T-0xx: 单元测试                  [Med]  [8h]  test-engineer
  T-0xx: 集成测试                  [High] [8h]  test-engineer
  T-0xx: 端到端测试                [High] [8h]  test-engineer

里程碑 M4: 文档 & 部署（Sprint N+2）
  T-0xx: API 文档                  [Low]  [4h]  backend-engineer
  T-0xx: 部署配置                  [Med]  [4h]  backend-engineer
```

#### 4.2 任务卡片结构

每个任务包含以下字段：

```markdown
### T-001: {任务标题}
- **里程碑**：M1 基础设施搭建
- **Sprint**：Sprint 1
- **复杂度**：Low / Medium / High
- **预估工时**：4h / 8h / 16h / 24h
- **Agent**：backend-engineer / frontend-engineer / test-engineer
- **文件**：`src/Controllers/...`, `src/Services/...`
- **依赖**：无 / T-003, T-004
- **验收标准**：AC-001（关联 requirements.md）
- **状态**：⏳ 待开始
```

#### 4.3 关键路径分析

任务拆解完成后，自动分析并标注**关键路径**：

```markdown
## 关键路径

T-001 → T-003 → T-004 → T-010（首个核心功能）→ T-020（集成测试）

⏱️ 关键路径总工时：48h
📅 预计总工期：{根据工时 ÷ 每日有效编码时间 6h 估算}

⚠️ 瓶颈任务：T-004（认证模块），阻塞所有需要鉴权的后续任务
```

#### 4.4 任务汇总表

在 tasks.md 末尾生成汇总：

```markdown
## 📊 汇总

| 里程碑 | 任务数 | 总工时 | 建议 Sprint |
|--------|-------|--------|------------|
| M1 基础设施 | 5 | 24h | Sprint 1 |
| M2 核心功能 | {n} | {x}h | Sprint 2-{n} |
| M3 测试 | {n} | {x}h | Sprint {n+1} |
| M4 文档部署 | {n} | {x}h | Sprint {n+2} |
| **合计** | **{total}** | **{total}h** | **{sprints} 个 Sprint** |

按 Agent 分配：
| Agent | 任务数 | 工时 |
|-------|-------|------|
| backend-engineer | {n} | {x}h |
| frontend-engineer | {n} | {x}h |
| test-engineer | {n} | {x}h |
```

> **工时估算原则**：
> - Low 复杂度：4h（半天）
> - Medium 复杂度：8h（1 天）
> - High 复杂度：16-24h（2-3 天）
> - 一个 Sprint = 5 个工作日 = 40h 有效编码时间（按每日 8h × 有效率 80% ≈ 6h 估算）

**⏸️ 阶段确认**：展示任务清单和关键路径，等待用户确认后继续。

---

### 代码项目 Phase 5: 脚手架搭建

根据 Phase 1 技术选型，**调度对应 Agent** 创建项目骨架。

> **规模感知**：Phase 5 的产出结构取决于 Phase 1 的 `scale` 选项：
> - `monolith` → 标准单体结构（下方 5.1 默认方案）
> - `modular` → 多模块单体（见 5.1.1）
> - `microservice` → 微服务架构（见 5.1.2）

#### 5.0 脚手架模式判定 & 参考图导入

根据 Phase 1 `Q-scaffold` 的选择，决定后端/前端各自的生成策略：

| 模式 | 后端产出 | 前端产出 |
|------|---------|--------|
| **完整脚手架** | 项目结构 + 业务代码骨架 + 示例接口 + 中间件 + 测试 | 项目结构 + 页面骨架 + 路由 + 状态管理 + Layout |
| **空项目** | 项目结构 + 基础配置（入口文件 + 依赖声明 + .gitignore），不含业务代码 | 项目结构 + 基础配置（入口文件 + 依赖声明），不含页面代码 |
| **完整 + 参考图** | — | 同完整脚手架，但参考设计图辅助生成 UI 布局 |

##### 前端参考设计图导入

当前端选择「完整脚手架 + 参考设计图」时：

```
1. 使用 vscode_askQuestions 请用户提供参考图：
   - 提示用户将设计图/截图/原型图放入项目目录（如 docs/design-refs/）
   - 支持格式：PNG / JPG / JPEG / WEBP
   - 可提供多张图（不同页面/模块各一张）

2. 使用 view_image 逐张读取参考图，分析并提取：
   - 页面布局结构（Header / Sidebar / Content / Footer）
   - 色彩方案（主色/辅助色/背景色/文字色）
   - 组件类型识别（表格/表单/卡片/图表/导航）
   - 页面数量与导航结构

3. 将分析结果保存为 docs/design-refs/analysis.md：
   ```markdown
   # 参考设计图分析

   ## 页面清单
   | 页面 | 参考图 | 布局类型 | 核心组件 |
   |------|--------|---------|----------|
   | 首页 | home.png | 侧边栏布局 | 数据卡片 ×4, 折线图, 表格 |
   | ... |

   ## 色彩方案
   - 主色：#1890FF
   - 辅助色：...

   ## 布局模式
   - 整体布局：左侧边栏 + 顶部导航 + 内容区
   - 响应式：...
   ```

4. 在 5.2 前端脚手架生成时，将 analysis.md 作为上下文传递给 frontend-engineer：
   - 页面结构参照参考图布局
   - 配色方案与参考图保持一致
   - 组件选型匹配参考图中识别到的类型
```

> **注意**：参考图仅作为 UI 风格和布局的参考，不会 1:1 像素级复制。AI 会根据参考图风格 + Ant Design 组件库生成符合设计意图的代码。

##### 空项目模式说明

选择空项目模式时，后端/前端仅生成最小化可运行的项目结构：

**后端空项目**（.NET 示例）：
```
backend/
├── src/
│   └── {ProjectName}.Api/
│       ├── Program.cs              # 最小 Minimal API 入口（仅健康检查端点）
│       ├── appsettings.json
│       ├── appsettings.Development.json
│       └── {ProjectName}.Api.csproj
├── {ProjectName}.sln
├── .editorconfig
└── Directory.Build.props
```

**后端空项目**（Python 示例）：
```
backend/
├── app/
│   ├── __init__.py
│   └── main.py                    # 最小 FastAPI 入口（仅健康检查端点）
├── requirements.txt
├── pyproject.toml
└── .env.example
```

**前端空项目**（React 示例）：
```
frontend/
├── src/
│   ├── main.tsx                   # 入口
│   ├── App.tsx                    # 空白根组件
│   └── vite-env.d.ts
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .eslintrc.cjs
```

**前端空项目**（H5 示例）：
```
frontend/
├── index.html                     # 空白 HTML 骨架
├── css/
│   └── style.css
├── js/
│   └── app.js
└── assets/
```

> **空项目后续补充**：在 Phase 9 迭代开发中选择「新增功能模块」时，根据需求逐步添加业务代码。适合需求尚不明确或想边做边定义的项目。

#### 5.1 后端脚手架

**调度 Agent**: `backend-engineer`

> **模式判定**：当 `scaffold.backend = "empty"` 时，仅生成上方「空项目模式」中的最小结构，跳过下方的完整脚手架内容，直接进入 5.2。

##### .NET 方案（推荐）

读取 [references/dotnet-scaffold.md](./references/dotnet-scaffold.md) 获取完整模板。

项目结构：
```
backend/
├── src/
│   └── {ProjectName}.Api/
│       ├── Program.cs                  # Minimal API 入口
│       ├── appsettings.json            # 配置文件
│       ├── appsettings.Development.json
│       ├── Controllers/                # API 控制器
│       │   └── HealthController.cs     # 健康检查
│       ├── Services/                   # 业务服务层
│       ├── Repositories/              # 数据访问层
│       ├── Models/                     # 实体模型
│       │   └── Entities/
│       ├── DTOs/                       # 数据传输对象
│       ├── Infrastructure/            # 基础设施
│       │   ├── Auth/                  # 认证模块
│       │   ├── Database/              # SqlSugar 配置
│       │   ├── Middleware/            # 中间件
│       │   └── Extensions/           # 服务扩展
│       └── {ProjectName}.Api.csproj
├── tests/
│   └── {ProjectName}.Tests/
│       ├── {ProjectName}.Tests.csproj
│       └── Controllers/
├── {ProjectName}.sln
├── .editorconfig
├── Directory.Build.props
└── Dockerfile (如需)
```

核心功能：
- 统一异常处理中间件
- JWT / Azure AD 认证配置
- SqlSugar ORM 配置 + Code First 就绪
- Swagger/OpenAPI 文档
- 健康检查端点
- CORS 配置
- Serilog 日志

##### Python 备选方案

项目结构：
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 入口
│   ├── core/
│   │   ├── config.py                # 配置管理
│   │   ├── security.py              # 认证模块
│   │   └── database.py              # 数据库连接
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/           # API 路由
│   │       └── deps.py              # 依赖注入
│   ├── models/                      # SQLAlchemy 模型
│   ├── schemas/                     # Pydantic Schema
│   ├── services/                    # 业务逻辑
│   └── repositories/               # 数据访问
├── tests/
├── alembic/                         # 数据库迁移
├── requirements.txt
├── pyproject.toml
├── Dockerfile (如需)
└── .env.example
```

##### 5.1.1 多模块变体（scale = modular）

当项目选择多模块单体时，在单体结构基础上扩展为多项目/多 Package 结构：

**.NET 多模块**：
```
backend/
├── src/
│   ├── {ProjectName}.Api/              # API 入口（网关层）
│   ├── {ProjectName}.Core/             # 核心业务逻辑（共享）
│   │   ├── Interfaces/                 # 服务接口定义
│   │   ├── Entities/                   # 领域实体
│   │   └── DTOs/                       # 共享 DTO
│   ├── {ProjectName}.Module.{ModuleA}/ # 功能模块 A
│   │   ├── Controllers/
│   │   ├── Services/
│   │   └── Repositories/
│   ├── {ProjectName}.Module.{ModuleB}/ # 功能模块 B
│   └── {ProjectName}.Infrastructure/   # 基础设施（数据库/缓存/消息）
├── tests/
│   ├── {ProjectName}.Core.Tests/
│   ├── {ProjectName}.Module.{ModuleA}.Tests/
│   └── {ProjectName}.Module.{ModuleB}.Tests/
├── {ProjectName}.sln
└── Directory.Build.props               # 统一版本管理
```

**Python 多模块**：
```
backend/
├── app/
│   ├── main.py
│   ├── core/                            # 共享核心
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── shared_schemas.py            # 共享 Schema
│   ├── modules/
│   │   ├── {module_a}/                  # 功能模块 A
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   └── {module_b}/                  # 功能模块 B
│   └── infrastructure/                  # 基础设施
├── tests/
│   ├── test_{module_a}/
│   └── test_{module_b}/
└── pyproject.toml
```

> **模块拆分依据**：根据 Phase 2 需求分析的领域边界自动建议模块划分。用户可在 Phase 4 任务拆解时调整。

##### 5.1.2 微服务变体（scale = microservice）

当项目选择微服务架构时，每个服务独立项目、独立数据库、通过 API 网关统一入口。

**整体 Monorepo 结构**：
```
{project-root}/
├── backend/
│   ├── services/
│   │   ├── gateway/                     # API 网关（YARP/.NET 或 Kong）
│   │   │   ├── src/
│   │   │   ├── Dockerfile
│   │   │   └── README.md
│   │   ├── {service-a}/                 # 业务服务 A
│   │   │   ├── src/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   └── README.md
│   │   └── {service-b}/                 # 业务服务 B
│   ├── shared/
│   │   └── {ProjectName}.Contracts/     # 共享契约（DTO/事件/接口）
│   └── {ProjectName}.sln               # 或 pyproject.toml（全局）
├── frontend/                            # 前端
├── docs/                                # 项目文档
├── infra/
│   ├── docker-compose.yml               # 全部服务编排
│   ├── docker-compose.override.yml      # 本地开发覆盖
│   └── k8s/                             # Kubernetes 部署文件（可选）
│       ├── namespace.yaml
│       ├── {service-a}-deployment.yaml
│       └── {service-b}-deployment.yaml
├── .github/
│   └── workflows/                       # 每个服务独立 CI/CD
└── README.md
```

**网关配置**：
- .NET 推荐 YARP（Yet Another Reverse Proxy），自动生成 `yarp.json` 路由配置
- Python 推荐 FastAPI Gateway 模式或独立 Nginx/Kong

**服务间通信**：
- 同步调用：HTTP + 共享契约 DTO（`shared/Contracts/`）
- 异步消息：预留 RabbitMQ / Azure Service Bus 集成点（不强制安装）

**数据库隔离**：
- 每个服务独立数据库 Schema 或独立数据库实例
- docker-compose 中为每个服务配置独立的 DB 连接字符串

> **注意**：微服务脚手架默认只创建 gateway + 2 个占位服务（根据需求文档命名），用户可在后续迭代中增加服务。

#### 5.2 前端脚手架

**调度 Agent**: `frontend-engineer`

> **模式判定**：
> - `scaffold.frontend = "empty"` → 仅生成上方「空项目模式」中的最小结构，跳过下方完整脚手架内容
> - `scaffold.frontend = "full-with-ref-image"` → 先执行 5.0 中的参考图分析，将 `docs/design-refs/analysis.md` 传递给 `frontend-engineer` 作为设计上下文，再按下方完整脚手架流程生成
> - `scaffold.frontend = "full"` → 正常走完整脚手架流程

##### React 方案（推荐）

读取 [references/react-scaffold.md](./references/react-scaffold.md) 获取完整模板。

项目结构：
```
frontend/
├── src/
│   ├── main.tsx                     # 入口
│   ├── App.tsx                      # 根组件
│   ├── routes/                      # 路由配置
│   │   └── index.tsx
│   ├── pages/                       # 页面
│   │   ├── Login/
│   │   ├── Dashboard/
│   │   └── NotFound/
│   ├── components/                  # 通用组件
│   │   └── Layout/
│   ├── hooks/                       # 自定义 Hooks
│   ├── services/                    # API 调用层
│   │   ├── api.ts                   # Axios 实例
│   │   └── auth.ts                  # 认证 API
│   ├── stores/                      # 状态管理 (zustand)
│   │   └── useAuthStore.ts
│   ├── types/                       # TypeScript 类型
│   └── utils/                       # 工具函数
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── .eslintrc.cjs
└── .prettierrc
```

核心功能：
- Vite + React 18 + TypeScript
- React Router v6 路由
- Ant Design 组件库
- Axios 请求封装 + 拦截器
- JWT Token 管理（自动刷新）
- zustand 状态管理
- 登录页 + Layout 骨架
- ESLint + Prettier 配置

##### H5 备选方案

轻量级单页面结构：
```
frontend/
├── index.html
├── css/
│   └── style.css
├── js/
│   ├── app.js
│   ├── api.js                      # API 调用封装
│   └── auth.js                     # 认证逻辑
└── assets/
```

#### 5.3 数据库脚手架

根据后端选型自动生成：

- **.NET + SqlSugar**：生成 `SqlSugarClient` 配置、基础 `Entity`（User 等）、Code First 初始化
- **Python + SQLAlchemy**：生成 `Base` 模型、`User` 模型、Alembic 初始配置

#### 5.4 Docker 支持（如选择）

生成：
- 后端 `Dockerfile`（多阶段构建）
- 前端 `Dockerfile`（Node 构建 + Nginx 托管）
- 各项目 `.dockerignore`
- `docker-compose.yml`（后端 + 前端 + 数据库，含 healthcheck）
- `.env.docker`（环境变量模板，复制为 `.env` 后使用）

> **注意**：docker-compose 中的数据库镜像根据技术栈自动适配：
> - .NET 默认 SQL Server (`mcr.microsoft.com/mssql/server:2022-latest`)
> - Python 默认 PostgreSQL (`postgres:16-alpine`)
> - nginx.conf 中的 `proxy_pass` 端口根据后端自动匹配（.NET → 8080 / Python → 8000）

#### 5.5 测试框架

**调度 Agent**: `test-engineer`

- **.NET**：xUnit + FluentAssertions + Moq
- **Python**：pytest + httpx（AsyncClient）
- **React**：Vitest + React Testing Library
- **H5**：不生成测试框架

#### 5.6 Git 初始化 & .gitignore

在项目根目录执行：
1. 生成 `.gitignore`（根据技术栈组合前后端规则）
2. `git init`
3. `git add .`
4. `git commit -m "chore: initial project scaffold"`

`.gitignore` 核心规则：
- **.NET**：`bin/` `obj/` `.vs/` `*.user` `logs/`
- **Python**：`__pycache__/` `venv/` `.env` `*.pyc`
- **React**：`node_modules/` `dist/` `.env.local`
- **通用**：`.DS_Store` `Thumbs.db` `*.log`

#### 5.7 CI/CD 管线（如选择）

根据 Phase 1 的 `cicd` 选项生成对应管线配置。

##### GitHub Actions

生成 `.github/workflows/ci.yml`：

```yaml
# 触发条件: push 到 main/develop，PR 到 main
# 矩阵策略: 后端构建 + 前端构建 + 测试并行

jobs:
  backend:
    - checkout
    - 安装依赖（dotnet restore / pip install）
    - 编译（dotnet build / 语法检查）
    - 单元测试（dotnet test / pytest）
    - 代码覆盖率报告
  frontend:
    - checkout
    - npm ci
    - lint（eslint）
    - 单元测试（vitest）
    - 构建（vite build）
  docker: (if docker enabled)
    - needs: [backend, frontend]
    - 构建 Docker 镜像
    - 推送到容器注册表（标签: commit SHA + latest）
```

微服务架构时，为每个服务生成独立 workflow 文件，并添加路径过滤：
```yaml
on:
  push:
    paths: ['backend/services/{service-name}/**', 'backend/shared/**']
```

##### Azure DevOps Pipelines

生成 `azure-pipelines.yml`，结构同上但使用 Azure Pipelines 语法（`stages` / `jobs` / `steps`）。

#### 5.8 多环境配置

根据 Phase 1 的 `environments` 选项生成环境配置文件。

##### 后端环境配置

**.NET**：
```
appsettings.json                    # 通用配置（不含敏感信息）
appsettings.Development.json        # 开发环境
appsettings.Staging.json            # 预发布环境（如选三套）
appsettings.Production.json         # 生产环境（仅结构，值用环境变量）
```

**Python**：
```
.env.example                        # 环境变量模板（提交到 Git）
.env.development                    # 开发环境
.env.staging                        # 预发布环境（如选三套）
.env.production                     # 生产环境（仅结构，值用环境变量）
```

##### 前端环境配置

```
.env                                # 通用
.env.development                    # VITE_API_BASE_URL=http://localhost:8080
.env.staging                        # VITE_API_BASE_URL=https://staging-api.example.com
.env.production                     # VITE_API_BASE_URL=https://api.example.com
```

##### Docker 环境隔离

```
docker-compose.yml                  # 基础定义
docker-compose.override.yml         # 本地开发覆盖（端口映射、卷挂载、热重载）
docker-compose.staging.yml          # 预发布覆盖（如选三套）
docker-compose.prod.yml             # 生产覆盖（资源限制、日志驱动、重启策略）
```

> **安全原则**：生产环境配置文件只包含 key 名和占位符，实际值通过 CI/CD 的 Secrets / 环境变量注入，绝不提交到 Git。

#### 5.9 安全基线

在脚手架中默认嵌入安全防护措施：

##### 后端安全

| 项 | .NET 实现 | Python 实现 |
|----|----------|------------|
| 安全 Headers | `SecurityHeadersMiddleware`（X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security） | `starlette-security-headers` 或自定义中间件 |
| CORS 白名单 | 仅允许前端域名，禁止 `AllowAnyOrigin` + `AllowCredentials` | `CORSMiddleware` 配置 `allow_origins` 列表 |
| 速率限制 | `AspNetCoreRateLimit` 中间件 | `slowapi` 库 |
| 输入验证 | FluentValidation / DataAnnotations | Pydantic 模型自动验证 |
| SQL 注入防护 | SqlSugar 参数化查询（禁止拼接 SQL） | SQLAlchemy 参数化（禁止 `text()` 拼接） |
| 敏感数据脱敏 | 日志中不输出 Password/Token/ConnectionString | 同左 |
| 依赖漏洞扫描 | CI 中添加 `dotnet list package --vulnerable` | CI 中添加 `pip-audit` 或 `safety check` |

##### 前端安全

- **XSS 防护**：React 默认转义 + 禁止 `dangerouslySetInnerHTML`（规则文件中约束）
- **CSP 策略**：Nginx 配置 `Content-Security-Policy` header
- **敏感信息**：`.env` 中仅存放 `VITE_` 前缀的公开配置，禁止嵌入 API Key / Secret

##### 安全检查清单（写入 `docs/rules/security.md`）

生成规则文件供 Harness 和 Agent 引用，确保后续开发持续遵守安全要求。

---

### 代码项目 Phase 6: 工程轨道

读取 [references/embedded-harness.md](./references/embedded-harness.md) 获取完整流程。

在项目脚手架创建完成后，运行 Harness 工作流生成完整的工程轨道文件：
- `.github/copilot-instructions.md`
- `.github/AGENTS.md`
- `.vscode/tasks.json`
- `CODEOWNERS`
- `docs/rules/*.md`

同时生成/更新 `docs/README.md`（同老项目 Step E2 逻辑）。

---

### 代码项目 Phase 6.5: 注入项目级 Agent、Skill、Hook & Prompt

同老项目 Step E3 逻辑，将内嵌的 6 个 Agent、12 个 Skill、PreToolUse Hook 和 2 个 Prompt 复制到项目目录：

```
1. 创建 {project}/.claude/agents/ 和 {project}/.claude/skills/
2. 复制 embedded-agents/* → .claude/agents/
3. 复制 embedded-skills/* → .claude/skills/
4. 复制 embedded-hooks/* → .github/hooks/（含 scripts/ 子目录）
5. 复制 embedded-prompts/* → .github/prompts/
6. 将 .claude/ 加入 .gitignore 的考量项（提示用户确认）
```

注入完成后，后续在该项目工作时，所有 Agent 和 Skill 均优先使用项目级版本。
PreToolUse Hook 会在 git commit/push、dotnet build/publish、docker build 前自动拦截，确保 `.workcopilot/` 已更新。

> **提示**：团队希望对某个 Agent/Skill 做定制化修改时，直接编辑项目里的版本即可，不影响其他项目。

---

### 代码项目 Phase 7: Day-1 验证

输出最终交付清单：

```
📦 项目创建完成！

📂 项目结构:
├── backend/                 ← 后端 (.NET / Python)
├── frontend/                ← 前端 (React / H5)
├── docs/                    ← 项目文档 (README + rules)
├── .claude/                 ← 项目级 Agent & Skill（6+10）
├── docker-compose.yml       ← Docker 编排 (如有)
├── .env.docker              ← Docker 环境变量模板 (如有)
├── .github/                 ← 工程轨道
├── .vscode/tasks.json       ← 验证链
├── .workcopilot/            ← 项目状态 & 记忆
└── .spec-flow/              ← 需求 & 设计文档

🚀 快速启动:
  后端: cd backend && dotnet run --project src/{ProjectName}.Api
  前端: cd frontend && npm install && npm run dev

🐳 Docker 启动 (如有):
  cp .env.docker .env && docker compose up -d
  访问: http://localhost (前端) | http://localhost:8080/swagger (后端API)

✅ 验证命令:
  Ctrl+Shift+P → "Run Task" → "verify"

🛠️ 后续可用 Skill（已注入项目 .claude/skills/）:
  - doa-apidoc   → 生成接口文档
  - doa-ppt      → 生成方案PPT
  - doa-quotation → 生成报价单
  - doa-metting  → 生成会议纪要
  - doa-image    → 生成可视化页面/长图
  - doa-harness  → 更新工程轨道
  - spec-flow-main → 结构化需求-设计-任务流
  - brainstorming → 创意探索与需求澄清
  - frontend-design → 高质量前端界面设计
  - ui-ux-pro-max → UI/UX 专业设计系统

🤖 项目级 Agent（已注入 .claude/agents/，优先于用户级）:
  - requirements-analyst / system-architect / backend-engineer
  - frontend-engineer / test-engineer / mermaid-diagram
```

---

### 代码项目 Phase 8: 项目状态持久化

在 Phase 7 完成后，将 `project-config` 和项目元数据持久化到文件，支持跨会话恢复上下文。

生成 `.workcopilot/state.json`：

```json
{
  "version": "1.0",
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-01-01T00:00:00Z",
  "project": {
    "name": "{项目名}",
    "description": "{项目描述}",
    "backend": { "stack": "dotnet", "framework": "webapi", "orm": "sqlsugar" },
    "frontend": { "stack": "react", "ui": "antd" },
    "database": "sqlserver",
    "auth": "jwt",
    "docker": true,
    "scale": "monolith",
    "cicd": "github-actions",
    "environments": "dev-staging-prod"
  },
  "phases": {
    "phase1": { "status": "completed", "completedAt": "..." },
    "phase2": { "status": "completed", "completedAt": "..." },
    "phase3": { "status": "completed", "completedAt": "..." },
    "phase4": { "status": "completed", "completedAt": "..." },
    "phase5": { "status": "completed", "completedAt": "..." },
    "phase6": { "status": "completed", "completedAt": "..." },
    "phase7": { "status": "completed", "completedAt": "..." }
  },
  "iterations": [],
  "services": []
}
```

**跨会话恢复**：当用户在已有项目中再次调用 WorkCopilot 时：
1. 检查 `.workcopilot/state.json` 是否存在
2. 如存在，读取项目配置和已完成的阶段
3. 自动跳过已完成的初始化阶段，直接进入**迭代开发**模式

#### 8.1 项目记忆体系

除 `state.json` 外，在 `.workcopilot/` 目录下维护以下长期记忆文件：

```
.workcopilot/
├── state.json              ← 项目配置 + 阶段状态 + 迭代记录
├── decisions.md            ← 架构决策记录（ADR）
├── tech-debt.md            ← 技术债 & 已知问题追踪
└── changelog.md            ← 变更日志（自动维护）
```

##### decisions.md — 架构决策记录（ADR）

记录项目中的重要技术决策，避免重复讨论。每次做出架构性选择时追加：

```markdown
# 架构决策记录

## ADR-001: 选择 SqlSugar 作为 ORM
- **日期**：2025-01-01
- **状态**：已采纳
- **背景**：需要一个轻量级 ORM，支持 Code First 和多数据库
- **决策**：使用 SqlSugar 而非 EF Core
- **原因**：SqlSugar 更轻量、API 更简洁、支持更多数据库方言
- **后果**：团队需要学习 SqlSugar API，不能使用 EF Core 的 Migration 工具
- **关联**：Phase 1 技术选型

## ADR-002: 用户认证采用 JWT + Refresh Token
- **日期**：...
```

**触发时机**：
- Phase 1 技术选型时，每项选择自动生成一条 ADR
- Phase 3 系统设计中的关键架构选择
- Phase 9 迭代中遇到需要权衡的技术选择
- 用户主动说"记录这个决策"

##### tech-debt.md — 技术债追踪

记录已知但暂未处理的技术问题和改进点：

```markdown
# 技术债 & 已知问题

| ID | 类型 | 描述 | 优先级 | 来源 | 状态 |
|----|------|------|--------|------|------|
| TD-001 | 性能 | 用户列表接口未分页 | P2 | iter-001 | ⏳ 待处理 |
| TD-002 | 安全 | 文件上传未做类型校验 | P1 | iter-003 | 🔄 处理中 |
| TD-003 | 重构 | UserService 过大需拆分 | P3 | iter-005 | ⏳ 待处理 |
```

**触发时机**：
- 迭代实现中发现但不阻塞当前功能的问题
- 代码审查中识别的改进点
- 用户主动说"记一个技术债"
- 迭代验证时发现的非阻塞性问题

##### changelog.md — 变更日志

每次迭代完成后自动追加：

```markdown
# 变更日志

## [iter-003] 2025-02-15 — 订单管理模块
### 新增
- 订单 CRUD API（FR-010 ~ FR-015）
- 订单列表页面 + 详情页面
### 修改
- 用户模型增加 `lastOrderAt` 字段
### 技术债
- TD-003: UserService 职责过多，需拆分
```

#### 8.2 跨会话上下文加载

当 Phase 9 迭代开发开始时，自动加载以下文件作为上下文：

```
必读：
  1. .workcopilot/state.json        → 项目配置 & 历史迭代
  2. .workcopilot/decisions.md      → 技术决策（避免矛盾选择）
  3. .workcopilot/tech-debt.md      → 已知问题（可能关联本次迭代）

按需读取：
  4. .spec-flow/active/*/tasks.md   → 当前任务状态
  5. .spec-flow/active/*/design.md  → 现有架构（增量设计时参考）
```

> **记忆协作**：团队成员在同一项目工作时，`.workcopilot/` 目录提交到 Git，共享技术决策和技术债记录。

---

### 代码项目 Phase 9: 迭代开发（持续入口）

项目初始化完成后，后续开发通过此阶段循环执行。

#### 触发方式

用户在已初始化的项目中调用 WorkCopilot 时：
- 如果检测到 `.workcopilot/state.json` 且所有初始化 Phase 已完成
- 自动进入迭代开发模式，使用 `vscode_askQuestions`：

```
Q1: 本次迭代要做什么？
  - "🆕 新增功能模块"
  - "🐛 修复 Bug"
  - "♻️ 重构已有模块"
  - "🧪 补充测试"
  - "📦 新增微服务（仅微服务架构）"
  - "� 补充/更新需求 & 设计文档"
  - "📄 生成文档（API文档/PPT/会议纪要）"
  - "🔧 更新工程轨道（Harness）"
```

#### 补充需求 & 设计文档

当初始化时跳过了 Phase 2-4，或需要更新已有文档时：

```
1. 检查 .spec-flow/active/{project-name}/ 目录下已有文件
2. 询问用户本次要补充哪些文档：
   - 提案文档（proposal.md）
   - 需求文档（requirements.md）
   - 系统设计（design.md）
   - 任务拆解（tasks.md）
3. 调用 spec-flow-main skill 执行对应阶段的文档生成/更新
   - spec-flow 负责 proposal.md、requirements.md、design.md、tasks.md 的创建和更新
   - WorkCopilot 不自行创建这些文件
4. 更新 state.json 中对应 Phase 的状态
```

#### 新增功能模块流程

```
迭代流程图:
  用户描述功能 → brainstorming 探索需求
    → 可选：用户提供参考设计图（同 5.0 参考图导入流程）
    → 调用 spec-flow-main skill 更新 requirements.md（追加 FR/NFR）
    → 调用 spec-flow-main skill 更新 design.md（增量设计）
    → 调用 spec-flow-main skill 更新 tasks.md（追加任务，分配里程碑 & 工时）
    → backend-engineer / frontend-engineer 实现
      （如有参考图，frontend-engineer 参照 analysis.md 生成 UI）
    → test-engineer 编写测试
    → 迭代验证（测试 + lint + 构建检查）
    → 双向同步（tasks.md 状态 + state.json 记录）
```

#### 任务状态双向同步

**核心规则**：`tasks.md` 和 `state.json` 必须保持一致，任何任务状态变更同时更新两处。

**实施期间**：
1. 开始执行任务前：将 tasks.md 中该任务状态从 ⏳ 改为 🔄
2. 任务完成后：将 tasks.md 中该任务状态改为 ✅，同时更新 state.json

**tasks.md 状态标记**：
```
⏳ 待开始 → 🔄 进行中 → ✅ 完成
                       → ❌ 阻塞（标注阻塞原因）
                       → ⏭️ 跳过（标注跳过原因）
```

**state.json 迭代记录**（增强版）：
```json
{
  "iterations": [
    {
      "id": "iter-001",
      "type": "feature",
      "description": "用户管理模块",
      "milestone": "M2",
      "sprint": "Sprint 2",
      "startedAt": "...",
      "completedAt": "...",
      "tasks": [
        { "id": "T-010", "status": "completed", "actualHours": 6 },
        { "id": "T-011", "status": "completed", "actualHours": 10 },
        { "id": "T-012", "status": "completed", "actualHours": 4 }
      ],
      "estimatedHours": 24,
      "actualHours": 20,
      "filesChanged": ["src/Controllers/UserController.cs", "..."],
      "decisions": ["ADR-003"],
      "verification": { "tests": "pass", "lint": "pass", "build": "pass" }
    }
  ]
}
```

#### 迭代验证闭环

每次迭代的代码实现完成后，**必须执行验证步骤**：

```
迭代验证清单:
  1. 运行测试：dotnet test / pytest / vitest
  2. 运行 lint：eslint / dotnet format --verify-no-changes
  3. 构建检查：dotnet build / vite build（确保无编译错误）
  4. 安全检查：对新增代码检查 docs/rules/security.md 中的约束
  5. 更新文档：如有新 API，提醒用户是否需要更新 API 文档
```

验证结果写入 state.json 的 `verification` 字段。如有失败项，输出修复建议后等待用户确认。

#### 🔒 会话结束自动持久化（强制规则）

**每次会话/迭代完成后，在调用 `task_complete` 之前，必须自动执行以下持久化操作**：

> ⚠️ 这不是可选步骤。无论会话中做了什么（新功能、修 Bug、重构、补测试、处理技术债），只要产生了代码变更或状态变更，都必须执行。

> 🔧 **PreToolUse Hook 强制保障**：项目中的 `.github/hooks/update-workcopilot.json` 注册了 PreToolUse 拦截脚本，在执行 `git commit/push`、`dotnet build/publish`、`docker build` 前会自动检查 `.workcopilot/changelog.md` 的最近更新时间（2分钟内）。如果未及时更新，操作将被阻止并注入提示消息，确保持久化契约不可绕过。

##### 必更新文件清单

| 文件 | 更新内容 | 触发条件 |
|------|---------|---------|
| `.workcopilot/state.json` | `updatedAt` 时间戳、里程碑进度、迭代记录、技术债状态 | **每次会话必更新** |
| `.workcopilot/changelog.md` | 追加本次变更摘要（新增/修改/删除/技术债） | 有代码或配置变更时 |
| `.workcopilot/decisions.md` | 追加架构决策记录（ADR） | 做出了技术选型或架构变更时 |
| `.workcopilot/tech-debt.md` | 新增/关闭/更新技术债条目 | 发现新技术债或解决了已有技术债时 |
| `docs/README.md` | Docker 版本/Digest/构建命令、技术栈变更、快速开始命令 | 有 Docker 构建推送、依赖变更、配置变更时 |
| `.spec-flow/active/*/tasks.md` | 任务状态标记（⏳→🔄→✅） | 有任务状态变更时 |

##### 变更检测矩阵

在会话结束前，AI 必须回顾本次会话的所有操作，按以下矩阵自动判定需要更新哪些文件：

| 会话中做了什么 | state.json | changelog.md | README.md | tech-debt.md | decisions.md |
|---------------|:----------:|:------------:|:---------:|:------------:|:------------:|
| 任何代码/配置变更 | ✅ updatedAt | ✅ 追加条目 | — | — | — |
| Docker 构建 & 推送 | ✅ +迭代记录 | ✅ 部署段 | ✅ 版本+Digest+构建命令 | — | — |
| 新增/修改 API 接口 | ✅ | ✅ | ✅ 如有接口列表段 | — | — |
| 修复 Bug | ✅ | ✅ 修复段 | — | ✅ 如来自已知TD则关闭 | — |
| 技术选型/架构变更 | ✅ | ✅ | ✅ 如涉及技术栈段 | — | ✅ 追加ADR |
| 新增依赖/升级版本 | ✅ | ✅ | ✅ 技术栈表格 | — | — |
| 发现但未修的问题 | ✅ | — | — | ✅ 新增TD | — |
| 解决已有技术债 | ✅ | ✅ | — | ✅ 状态→✅ | — |
| 配置变更(appsettings等) | ✅ | ✅ | ✅ 如涉及环境配置段 | — | — |

##### docs/README.md 自动更新规则

当检测到 Docker 构建/推送操作时，自动更新 `docs/README.md` 中的以下字段：

```markdown
# 需要更新的字段（按实际 README 结构定位）：
1. Docker 版本表格中的「最新标签」→ 新版本号
2. Docker 版本表格中的「完整镜像地址」→ 新完整地址
3. Docker 版本表格中的「镜像 Digest」→ 新 Digest（从 docker push 输出中提取）
4. 构建 & 推送命令示例中的版本号 → 新版本号
```

**Digest 提取方式**：从 `docker push` 的终端输出中匹配 `sha256:` 开头的完整哈希值。

当检测到技术栈变更（新增依赖、升级框架版本等）时，更新 README 中的技术栈表格。

当检测到新增 API 端点时，如 README 中有接口概览段，追加新接口。

##### 时间格式

所有时间戳使用北京时间，格式为 `yyyy-MM-dd HH:mm:ss`（不带时区后缀）。
`state.json` 顶层须包含 `"timezone": "Asia/Shanghai"` 声明。

##### 执行顺序

```
会话工作完成
  → 0. 回顾本次会话操作清单，对照「变更检测矩阵」判定需更新的文件
  → 1. 更新 state.json（updatedAt + 里程碑进度 + 新迭代记录）
  → 2. 追加 changelog.md（本次变更摘要）
  → 3. 更新 docs/README.md（Docker 版本/Digest、技术栈、接口等）
  → 4. 如有决策：追加 decisions.md
  → 5. 如有技术债变更：更新 tech-debt.md
  → 6. 如有任务状态变更：更新 tasks.md
  → 7. 输出更新摘要（列出实际更新了哪些文件及关键变更）
```

##### state.json 更新模板

每次会话至少更新以下字段：

```json
{
  "updatedAt": "2026-05-07 10:30:00",
  "milestones": {
    "M{x}": { "tasksCompleted": "{更新后的数量}" }
  },
  "iterations": [
    {
      "id": "iter-{下一个编号}",
      "date": "2026-05-07 10:30:00",
      "scope": "{本次会话做了什么的一句话摘要}"
    }
  ]
}
```

##### changelog.md 追加模板

```markdown
## [iter-{id}] {yyyy-MM-dd HH:mm:ss} — {范围描述}
### 新增
- {新增的功能/文件}
### 修改
- {修改的内容}
### 修复
- {修复的问题}
### 技术债
- {新增或关闭的技术债}
```

> **关键约束**：即使用户没有主动要求更新这些文件，AI 也必须在会话结束前自动执行。这是 WorkCopilot 的核心契约——项目记忆永不丢失。

#### 新增微服务（仅 scale = microservice）

```
1. 询问服务名称和职责描述
2. 在 backend/services/ 下创建新服务目录（复用 5.1 后端脚手架模板）
3. 更新 gateway 路由配置（YARP / Nginx）
4. 更新 docker-compose.yml 添加新服务
5. 生成该服务的独立 CI/CD workflow
6. 更新 shared/Contracts/ 添加新的契约
7. 更新 state.json 的 services 列表
```

---

## ⚠️ Harness 意识贯穿全程

每个 Phase 的产出都必须满足 Harness 三层约束：

| 层 | 要求 | 检查点 |
|----|------|--------|
| **Context** | 所有文件结构、命名、分层符合 copilot-instructions.md | Phase 5 脚手架生成后 |
| **Constraints** | 核心目录标注权限、rules 规则已覆盖 | Phase 6 harness 生成后 |
| **Security** | 安全基线检查通过、`docs/rules/security.md` 已生成 | Phase 5.9 安全基线后 |
| **CI/CD** | 管线配置正确、所有 job 可解析 | Phase 5.7 CI/CD 生成后 |
| **GC** | 无残留临时文件、无冗余代码 | Phase 7 验证时 |

---

## 交互规则

1. **逐阶段确认**：每个 Phase 完成后必须等待用户确认才能继续
2. **中文输出**：所有生成的文档使用中文
3. **Agent 标注**：每个阶段开始时明确标注当前调度的 Agent
4. **进度可视**：使用 `manage_todo_list` 跟踪整体进度
5. **可中断**：用户可随时说"跳过"某个 Phase
6. **可回溯**：用户可说"回到 Phase X"重新执行某阶段
7. **🔒 自动持久化（最高优先级）**：**无论会话中做了什么**，在会话结束或用户明确表示完成时，必须执行以下步骤：
   1. 回顾本次会话所有操作
   2. 对照「变更检测矩阵」逐行判定哪些文件需要更新
   3. 按「必更新文件清单」逐个更新（state.json → changelog.md → README.md → 其他）
   4. 向用户确认更新结果

   > **强制触发点**：用户说"完成"/"done"/"结束"/"好了"/"推送 Docker 后"等结束性话语时，立即启动持久化流程，不需要用户显式要求。

### 快速模式

如果用户明确要求跳过逐步确认：
- “快速模式” / “fast mode”
- “一口气执行” / “跳过确认”
- “generate all at once”

则可连续执行所有 Phase，但仍在最后输出完整交付清单供用户确认。

### 异常恢复

当某个 Phase 执行失败时：
1. **记录失败点**：输出失败的 Phase 和具体错误
2. **回滚产物**：删除当前 Phase 的不完整产物
3. **提供选项**：
   - “重试” — 重新执行失败的 Phase
   - “跳过” — 跳过当前 Phase 继续
   - “中止” — 保留已完成的产物，结束流程