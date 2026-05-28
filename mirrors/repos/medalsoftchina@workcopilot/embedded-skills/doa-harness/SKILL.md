---
name: doa-harness
description: >
  自动为项目搭建 Harness Engineering 工程轨道。一键生成 copilot-instructions.md、AGENTS.md、
  tasks.json、CODEOWNERS、rules/*.md 五大配置文件，让 GitHub Copilot 从"碰运气"变成"稳定交付"。
  USE FOR: 初始化 harness、搭建 copilot 工程轨道、配置 agent 约束、创建 instructions、
  创建验证链、配置审批钩子、setup harness、init harness、harness engineering。
  DO NOT USE FOR: 生成 PPT（使用 doa-ppt）、写代码逻辑、调试 bug。
argument-hint: '可选参数: --update (增量更新) | --dry-run (预览模式) | 指定技术栈如 "react + dotnet"'
---

# DOA Harness — 一键搭建 Copilot 工程轨道（团队版）

## 核心理念

Copilot 的上限不取决于提示词，而取决于它运行在怎样的**工程轨道**上。
三层公式：**Context**（给什么）→ **Constraints**（守什么）→ **GC**（清什么）。

## 运行模式

| 模式 | 触发方式 | 行为 |
|------|---------|------|
| **初始化** | 首次运行（默认） | 完整探测 → 交互确认 → 生成全部 5 类文件 |
| **增量更新** | 参数含 `--update` | 扫描已有文件 → 仅 patch 新增部分（如新模块），保留用户自定义内容 |
| **预览模式** | 参数含 `--dry-run` | 执行探测和模板渲染，输出预览但不写入文件 |

## 工作流

```
调用 skill
  → Step 0: 判断运行模式（初始化 / 增量更新 / 预览）
  → Step 1: 深度探测项目结构与技术栈
  → Step 2: 交互确认关键信息
  → Step 3: 生成 / 更新 5 类配置文件
  → Step 4: 注入 GC 指令
  → Step 5: 验证完整性 & 一致性
  → Step 6: 输出 Day-1 验证指令
```

---

## Step 0: 判断运行模式

1. 检查参数中是否含 `--update` 或 `--dry-run`
2. 扫描工作区，检查 `.github/copilot-instructions.md` 是否已存在
   - 已存在且未指定 `--update`：提示用户 "Harness 已初始化，是否切换到增量更新模式？"
   - 不存在：进入初始化模式

---

## Step 1: 深度探测项目结构与技术栈

### 1.1 递归扫描子项目

**不再只看根目录**。用 `list_dir` 递归扫描根目录及一级子目录，收集所有包含信号文件的子项目：

```
扫描策略：
1. list_dir 根目录 → 识别子目录
2. 对每个子目录 list_dir → 查找信号文件
3. 构建子项目列表: [{name, path, stack, signals}]
```

### 1.2 信号文件匹配表

| 信号文件 | 技术栈大类 | 需要进一步读取 |
|----------|-----------|---------------|
| `package.json` + `tsconfig.json` | Node/TypeScript | 读 package.json → 判断具体框架 |
| `*.csproj` / `*.sln` | .NET | 读 .csproj → 判断 SDK 版本和项目类型 |
| `pyproject.toml` / `requirements.txt` | Python | 读依赖列表 → 判断框架 |
| `go.mod` | Go | 读 go.mod → 判断主要依赖 |
| `Cargo.toml` | Rust | 读 Cargo.toml |
| `pom.xml` / `build.gradle` | Java/Kotlin | 读构建文件 |

### 1.3 前端框架深度探测

当检测到 `package.json` 时，**必须读取其 dependencies / devDependencies** 来判断：

| 依赖关键字 | 识别为 | 典型配套 |
|-----------|--------|---------|
| `umi` / `@umijs/*` | UmiJS | Ant Design Pro · dva · umi-request |
| `next` | Next.js | App Router / Pages Router |
| `nuxt` | Nuxt | Vue 3 |
| `vue` (无 nuxt) | Vue SPA | Vue Router · Pinia · Axios |
| `react` (无 umi/next) | React SPA | React Router · 状态管理待探测 |
| `@angular/core` | Angular | RxJS · NgRx |
| `svelte` / `@sveltejs/kit` | Svelte/SvelteKit | — |

同时检测：
- **包管理器**: 检查 `yarn.lock` → Yarn | `pnpm-lock.yaml` → pnpm | `package-lock.json` → npm
- **CSS 方案**: 检查 `tailwind.config.*` → Tailwind | `.less` 文件 → Less | `*.module.css` → CSS Modules
- **状态管理**: 检查依赖中的 `zustand` / `dva` / `redux` / `pinia` / `vuex` / `ahooks`
- **请求层**: 检查 `axios` / `umi-request` / `@tanstack/react-query` / `swr`
- **测试框架**: 检查 `vitest` / `jest` / `@testing-library/*` / `cypress`
- **Lint 工具**: 检查 `eslint` / `prettier` / `biome`

### 1.4 后端框架深度探测

**.NET 项目**（检测到 `.csproj` / `.sln`）：
- 读取 `.csproj` 的 `<TargetFramework>` → 判断 .NET 版本
- 读取 `<Sdk>` 属性 → `Microsoft.NET.Sdk.Web` 为 Web 项目，`Microsoft.NET.Sdk.Worker` 为后台服务
- 扫描 `Program.cs` / `Startup.cs` → 判断 Minimal API / MVC / 传统分层
- 扫描 NuGet 依赖 → EF Core / Dapper / MediatR / FluentValidation 等
- 检查认证方式 → Azure AD / JWT / IdentityServer

**Python 项目**：
- 读取 `pyproject.toml` 或 `requirements.txt` → FastAPI / Django / Flask
- 检测 ORM → SQLAlchemy / Django ORM / Tortoise

### 1.5 CI/CD 探测

扫描以下文件以识别 CI 平台：

| 信号文件 | CI 平台 |
|----------|--------|
| `.github/workflows/*.yml` | GitHub Actions |
| `azure-pipelines.yml` | Azure DevOps |
| `.gitlab-ci.yml` | GitLab CI |
| `Jenkinsfile` | Jenkins |
| `.circleci/config.yml` | CircleCI |

### 1.6 代码托管平台探测

通过 `.git/config` 或目录特征推断：

| 信号 | 平台 |
|------|------|
| 存在 `.github/` 目录 | GitHub |
| 存在 `.gitlab/` 目录 | GitLab |
| remote URL 含 `dev.azure.com` | Azure DevOps |
| 无法确定 | 在 Step 2 交互中询问 |

### 1.7 探测结果数据结构

将所有探测结果汇总为结构化数据，供后续步骤使用：

```
project:
  name: "{项目名}"
  type: "monorepo" | "single"
  hosting: "github" | "gitlab" | "azure-devops"
  ci: "github-actions" | "azure-pipelines" | "gitlab-ci"
  subprojects:
    - name: "{子项目名}"
      path: "{相对路径}"
      stack: "react-ts" | "vue-ts" | "dotnet" | "python" | ...
      framework: "{具体框架}"
      package_manager: "yarn" | "pnpm" | "npm" | null
      css: "less" | "tailwind" | "css-modules" | null
      state: "dva" | "zustand" | "pinia" | null
      request: "umi-request" | "axios" | "react-query" | null
      test: "vitest" | "jest" | "xunit" | "pytest" | null
      lint: "eslint" | "prettier" | "biome" | "dotnet-format" | null
      entry: "{入口文件路径}"
      verify_chain: ["{cmd1}", "{cmd2}", "{cmd3}"]
```

---

## Step 2: 交互确认

使用 `vscode_askQuestions` 向用户确认以下关键信息（一次性收集）：

### 必填项

1. **项目描述**: 一句话概括项目（用于 copilot-instructions.md 项目概述）
2. **确认探测结果**: 展示探测到的子项目列表和技术栈，让用户确认或修正
3. **代码托管平台**: GitHub / GitLab / Azure DevOps（影响 CODEOWNERS 路径和语法）

### 可选项（有默认值）

4. **团队 Owner 列表**: 输入格式 `@user1 @user2`，默认 `@todo-fill-team`
5. **额外编码规则**: 是否有团队特有的编码规约需要生成为 rules/ 文件
6. **是否将 `.vscode/tasks.json` 纳入版本控制**: 默认 Yes

**增量更新模式下**：跳过已确认的信息，仅询问新增部分（如新发现的子项目）

---

## Step 3: 生成配置文件

按以下顺序依次生成 5 类文件。

**初始化模式**：生成前检查是否已存在，已存在则跳过并提示。
**增量更新模式**：读取已有文件，仅 patch 新增内容（如新模块加入模块地图），不覆盖用户自定义段落。
**预览模式**：渲染模板内容输出到聊天窗口，不写入文件。

每个生成的文件头部加注版本标记：
```
# Generated by doa-harness v2.0 on {YYYY-MM-DD}
```

### 3.1 copilot-instructions.md

路径：`.github/copilot-instructions.md`

读取 [templates/copilot-instructions.md](./templates/copilot-instructions.md) 获取骨架模板。

**模板采用骨架 + 占位符模式**，不硬编码任何特定框架：

```
段落结构（固定）：
1. 项目概述 — {project.name} + 各子项目入口
2. 技术栈 — 按子项目分段，每段由探测结果填充
3. 安全边界 — 按子项目分段
4. 前后端联动（仅 monorepo）
5. 验证命令 — 从 verify_chain 生成
6. 代码约定 — 按语言生成
7. 操作安全 — 合并 CI 平台 + 核心目录
8. 垃圾回收（固定段落）
```

占位符清单：
- `{project_description}` — 用户输入的项目描述
- `{sub.name}` / `{sub.entry}` — 子项目名和入口
- `{sub.framework}` — 具体框架（UmiJS / Next.js / ASP.NET Core...）
- `{sub.state}` — 状态管理方案
- `{sub.css}` — CSS 方案
- `{sub.request}` — 请求层方案
- `{sub.package_manager}` — 包管理器
- `{ci_platform}` — CI 平台名及配置文件路径
- `{hosting_platform}` — 代码托管平台

### 3.2 AGENTS.md

路径：`.github/AGENTS.md`

读取 [templates/agents-md.md](./templates/agents-md.md) 获取骨架模板。

生成规则：
- **快速入口**: 自动探测 `docs/`、`README.md`、`CHANGELOG.md` 等是否存在并列出
- **关键约束**: 自动扫描 `rules/` 目录列出
- **模块地图**: 对每个子项目，扫描其目录结构并按下表标注

权限标注规则（按目录名模式匹配）：

| 目录名模式 | 标注 | 含义 |
|-----------|------|------|
| `core` `kernel` `foundation` `framework` `Framework` | 🔒 需审批 | 核心 / 底层框架 |
| `auth` `security` `identity` `Authorization` `License` | 🔒 需审批 | 认证 / 安全 |
| `infra` `infrastructure` `deploy` `ActionFilter` | 🔒 需审批 | 基础设施 |
| `migrations` `database` `SQL_Script` | 🔒 需审批 | 数据库变更 |
| `app` `layouts` (前端配置目录) | 🔒 需审批 | 前端核心配置 |
| `Program.cs` `Startup.cs` (入口文件) | 🔒 需审批 | 启动入口 |
| `shared` `common` `lib` `tools` `components` | ⚠️ 注意复用 | 共享模块 |
| `api` `contracts` `interfaces` `Controllers` `ExternalApi` `ExternalService` | ⚠️ 有契约约束 | 接口层 |
| `config` `settings` `appsettings` `ScheduleJobs` | ⚠️ 需确认 | 配置 / 定时任务 |
| `features` `modules` `pages` `Service` | ✅ 可自由修改 | 业务功能 |
| `components` (非共享) `views` `Dto` `Model` | ✅ 可自由修改 | UI / 数据模型 |
| `tests` `__tests__` `spec` | ✅ 可自由修改 | 测试文件 |
| `assets` `public` `static` `locales` | ✅ 可自由修改 | 静态资源 |

生成后通过交互让用户**确认或修正权限标注**，避免误判。
总行数控制在 200 行以内。

### 3.3 tasks.json

路径：`.vscode/tasks.json`

读取 [templates/tasks-json.md](./templates/tasks-json.md) 获取骨架模板。

**支持 N 个子项目**，生成逻辑：

```
对每个子项目 sub:
  1. 根据 sub.verify_chain 生成对应 task 列表
  2. 每个 task 的 label 格式: "{sub.name}:{step}"
  3. 每个 task 添加 options.cwd = "${workspaceFolder}/{sub.path}"
  4. 生成子验证任务: "verify:{sub.name}" dependsOn 该子项目所有 step
最后生成总验证任务:
  "verify" dependsOn 所有 "verify:{sub.name}"
```

**包管理器感知**：
- 检测到 `yarn.lock` → 命令用 `yarn`
- 检测到 `pnpm-lock.yaml` → 命令用 `pnpm`
- 默认 → 命令用 `npm run`

**problemMatcher 映射**：
- TypeScript 编译 → `["$tsc"]`
- ESLint → `["$eslint-stylish"]`
- .NET build → `["$msCompile"]`
- 其他 → `[]`

### 3.4 CODEOWNERS

路径：根据代码托管平台决定

| 平台 | 默认路径 | 说明 |
|------|---------|------|
| GitHub | `CODEOWNERS`（项目根目录） | 也支持 `.github/CODEOWNERS` 和 `docs/CODEOWNERS` |
| GitLab | `CODEOWNERS`（项目根目录） | 支持 `[Section]` 分组语法 |
| Azure DevOps | 不生成 | 提示用户通过分支策略配置审阅者规则 |

读取 [templates/codeowners.md](./templates/codeowners.md) 获取骨架模板。

生成规则：
- 扫描项目所有子项目的核心目录，自动标注 owner
- 使用用户在 Step 2 提供的团队 Owner 列表（未提供则用 `@todo-fill-team`）
- CI/CD 配置文件自动纳入 CODEOWNERS
- Agent 配置文件（`copilot-instructions.md`、`AGENTS.md`）纳入 CODEOWNERS
- GitLab 项目使用 `[Section]` 分组语法增强可读性

### 3.5 rules/*.md

路径：`rules/` 目录

读取 [templates/rules.md](./templates/rules.md) 获取各技术栈的规则模板。

每条规则文件包含：
- **规则名称** + **原因**
- **正确示例 ✅**
- **错误示例 ❌**
- **检测方式**

根据技术栈生成核心规则 + 通用规则：

**按技术栈生成**：

| 技术栈 | 规则文件 |
|--------|----------|
| React/TS | `react-patterns.md`、`no-direct-fetch.md` |
| Vue/TS | `vue-patterns.md`、`no-direct-fetch.md` |
| .NET | `dotnet-data-access.md`、`no-lazy-load.md` |
| Python | `python-imports.md`、`no-raw-sql.md` |
| Go | `go-error-handling.md` |

**通用规则（所有项目都生成）**：

| 规则文件 | 内容 |
|---------|------|
| `no-secrets-in-code.md` | 禁止硬编码密钥、token、连接字符串 |

**用户自定义规则**：
如果用户在 Step 2 提供了额外规约，为每条生成一个独立 `rules/{name}.md` 文件。

---

## Step 4: 注入 GC 指令

在 `copilot-instructions.md` 的末尾追加 GC 段落：

```markdown
# 垃圾回收

每次完成任务后，检查是否有：
- 临时文件、未使用的 import / using
- 重复代码或重复函数
- 过期的 TODO / FIXME 注释
如有，顺手清理。
```

---

## Step 5: 验证完整性 & 一致性

生成完成后执行以下检查：

### 5.1 文件存在性

确认 5 类文件全部存在（Azure DevOps 项目跳过 CODEOWNERS）。

### 5.2 内容一致性校验

| 校验项 | 检查逻辑 |
|--------|---------|
| 验证链一致 | tasks.json 的 verify 链 ↔ copilot-instructions.md 的验证命令段落，两者引用的命令必须匹配 |
| 模块地图覆盖 | AGENTS.md 模块地图 ↔ 实际目录结构，不遗漏核心目录 |
| CODEOWNERS 语法 | 根据平台校验语法格式（GitHub: `path @owner`，GitLab: `[Section]` + `path @owner`） |
| rules 引用 | AGENTS.md 关键约束段落引用的 rules/ 文件 ↔ 实际生成的 rules/*.md 文件 |

### 5.3 生成 harness 自检 task

在 `tasks.json` 中追加一个 `verify:harness` 任务，检查 5 类文件的存在性：

```json
{
  "label": "verify:harness",
  "type": "shell",
  "command": "echo Checking harness files... && test -f .github/copilot-instructions.md && test -f .github/AGENTS.md && test -f .vscode/tasks.json && test -f CODEOWNERS && test -d rules/ && echo 'All harness files OK' || echo 'MISSING harness files!'",
  "problemMatcher": []
}
```

---

## Step 6: 输出 Day-1 验证指令

输出生成文件清单，并给出 Day-1 验证指令：

```
打开 Copilot Agent 模式，输入：
"读一下项目指令，然后告诉我：
 1. 哪些目录不能修改？
 2. 验证命令是什么？
 3. 哪些操作需要先确认？"
```

如果 Copilot 能准确回答这 3 个问题，说明 Harness 已生效。

---

## 增量更新行为说明

当以 `--update` 模式运行时：

1. **copilot-instructions.md**: 读取已有文件，仅更新探测到变化的段落（如新子项目的技术栈段），保留用户手动添加的自定义段落
2. **AGENTS.md**: 重新扫描目录结构，将新目录追加到模块地图末尾，保留已有目录的标注和用户修正
3. **tasks.json**: 检测新子项目，追加对应的 task，更新 verify 的 dependsOn 列表
4. **CODEOWNERS**: 追加新目录的 owner 映射，不修改已有行
5. **rules/*.md**: 仅生成不存在的规则文件，已有文件不动

---

## 快速参考

| 文件 | 用途 | 核心内容 |
|------|------|----------|
| `copilot-instructions.md` | Agent 指令 | 技术栈 + 安全边界 + 验证命令 |
| `AGENTS.md` | 知识索引 | 快速入口 + 模块地图 + 约束清单 |
| `tasks.json` | 验证链 | 每子项目独立链 → verify 总汇 |
| `CODEOWNERS` | 审批钩子 | 核心目录 → 团队 owner（多平台适配） |
| `rules/*.md` | 编码规则 | 正例 + 反例 + 检测方式 |
