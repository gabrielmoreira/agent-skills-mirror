# ChatClaw AGENTS.md

本文件为 ChatClaw 开发团队提供 AI 辅助开发指南。所有 AI 助手在帮助开发本项目时，应遵循本文档中的约定。

---

## 项目概述

ChatClaw 是一款开源的本地知识库 + OpenClaw 图形化桌面管家应用，基于 Wails v3 框架构建。

- **桌面框架**: Wails v3 (Go + WebView)
- **后端**: Go 1.26 + Bun ORM + SQLite + sqlite-vec (向量检索)
- **前端**: Vue 3 + TypeScript + Vite + Tailwind CSS v4 + shadcn-vue + Pinia
- **AI 框架**: Eino (字节跳动 CloudWeGo)
- **AI 供应商**: OpenAI / Claude / Gemini / Ollama / DeepSeek / 豆包 / 通义千问 / 智谱 / Grok 等
- **国际化**: go-i18n (后端) + vue-i18n (前端)，支持 17 种语言
- **构建工具**: Task (Taskfile.yml) + pnpm

---

## 通用开发规范

### 语言约定

- **回复语言**: 始终使用**中文**回复和思考。但生成的代码中的解释和注释使用英文。
- **i18n 文本**: 所有用户可见的文本必须走国际化，**禁止硬编码**。

### Codex Superpowers

- 如果当前助手运行在 **Codex**，且本机已安装 `superpowers` skills，则应优先按 `using-superpowers` 的技能发现与执行规则工作。
- 但 **本 AGENTS.md 与用户直接指令优先级更高**；若与 superpowers skill 冲突，以用户指令和本文件为准。
- 若任务触发 superpowers 中的流程型 skill（如 brainstorming、writing-plans、test-driven-development、requesting-code-review），应结合本项目既有规范执行，而不是覆盖项目约定。

### 禁止事项

- 不要在 `main.go` 写业务逻辑
- 不要创建循环依赖（services 之间不要互相 import）
- 不要直接 `log.Fatal`，除非是 `main.go` 中的启动失败
- 不要硬编码用户可见的文本，必须走 i18n
- 不要在函数体内裸调 `syscall.NewCallback` / `windows.NewCallback`

---

## 后端开发 (Go)

### 目录职责

| 目录 | 职责 |
|------|------|
| `main.go` | 只写启动逻辑，不写业务代码 |
| `internal/bootstrap/` | 应用组装、窗口创建、服务注册 |
| `internal/services/*/` | 业务服务，每个服务一个目录 |
| `internal/services/i18n/` | 多语言服务，翻译文件在 `locales/*.json` |
| `internal/services/windows/` | 窗口管理服务 |
| `internal/errs/` | 业务错误类型 |
| `internal/sqlite/` | 数据库连接和迁移 |
| `internal/define/` | 环境配置、内置常量、数据目录布局 |
| `internal/native/` | ChatClaw 原生边界，包 `native` 提供 `DataRootDir()` |
| `internal/openclaw/` | OpenClaw 集成边界（Gateway 生命周期、Agent 同步、运行时进程） |
| `internal/openclaw/agents/` | OpenClaw Agent 的 DB 与 Wails 暴露 |
| `internal/openclaw/runtime/` | Gateway 生命周期、RPC/WebSocket、bundle 解析、配置片段同步 |
| `internal/eino/` | AI/LLM 集成层（Agent、ChatModel、Embedding、Parser、Tools） |

### 用户数据目录划分

- `define.LegacyDataRootDir()` — `$HOME/.chatclaw`：旧版布局，仅迁移与兼容读取
- `define.NativeDataRootDir()` — `$HOME/.chatclaw/native`：原生 SQLite、应用日志、`skills/`、`mcp/` 等
- `define.OpenClawDataRootDir()` — `$HOME/.chatclaw/openclaw`：`openclaw.json`、Gateway 日志、`OPENCLAW_STATE_DIR` 内容、`workspace-*`、`agents/` 等

### 必须遵守

1. **新建业务服务时**：默认放在 `internal/services/[服务名]/`，用 `NewXxxService()` 构造函数。若服务仅服务于 OpenClaw Gateway 集成，应放在 `internal/openclaw/` 下合适子包。
2. **返回错误给前端时**：必须用 `errs.New()` / `errs.Newf()` / `errs.Wrap()`，不要直接返回 `error`。
3. **需要翻译的文本**：用 `i18n.T("key")` 或 `i18n.Tf("key", data)`，翻译 key 加到 `internal/services/i18n/locales/*.json`。
4. **新建数据库迁移**：放在 `internal/sqlite/migrations/`，文件名格式 `YYYYMMDDHHMM_描述.go`。
5. **错误处理**：用 `fmt.Errorf("context: %w", err)` 包装，不要吞掉错误。
6. **更新内置供应商/模型**：编辑 `internal/define/builtin_providers.go`，并在迁移文件中调用 `SyncBuiltinProvidersAndModels()`。

### 数据库模型时间戳

所有 bun 模型的 `created_at` / `updated_at` **必须**通过 `bun.BeforeInsertHook` 钩子自动设置，使用 `sqlite.NowUTC()` 生成 UTC 时间字符串。**禁止**依赖 bun tag 的 `default:current_timestamp` 或 `nullzero`。

```go
var _ bun.BeforeInsertHook = (*myModel)(nil)

func (*myModel) BeforeInsert(ctx context.Context, query *bun.InsertQuery) error {
    now := sqlite.NowUTC()
    query.Value("created_at", "?", now)
    query.Value("updated_at", "?", now)
    return nil
}
```

### Windows 回调模式

在 Windows 平台调用 `syscall.NewCallback` / `windows.NewCallback` 时，**必须**用 `sync.Once` 包裹，确保回调只创建一次。回调函数不能是闭包，需通过包级变量传参。

```go
var (
    myCBOnce sync.Once
    myCB     uintptr
    myMu     sync.Mutex
    myParam  string
)

func myEnumProc(hwnd uintptr, _ uintptr) uintptr {
    return 1
}

func myFunc(param string) uintptr {
    myMu.Lock()
    defer myMu.Unlock()
    myParam = param
    myCBOnce.Do(func() { myCB = syscall.NewCallback(myEnumProc) })
    procEnumWindows.Call(myCB, 0)
    return 0
}
```

### Windows 隐藏控制台窗口

在 Windows 上执行外部命令时（如 MCP stdio 模式），**必须**隐藏控制台窗口以避免弹窗闪烁。使用 `syscall.SysProcAttr` 设置 `HideWindow: true`。

```go
import "syscall"

if runtime.GOOS == "windows" {
    cmd.SysProcAttr = &syscall.SysProcAttr{
        HideWindow: true,
    }
}
```

### 数据库迁移时间戳冲突

修改已存在的迁移文件后，**不能**直接覆盖原文件，因为迁移系统不会重新执行已记录的迁移。解决方法是调整文件名时间戳使其成为"新"迁移（例如将 `202604161212` 改为 `202604170000`）。

---

## 前端开发 (Vue 3)

### 技术栈

Vue 3 + TypeScript + Vite + TailwindCSS v4 + shadcn-vue + Pinia + vue-i18n

### 目录职责

| 目录 | 职责 |
|------|------|
| `src/components/ui/` | shadcn-vue 组件（只能通过 CLI 添加，不要手写） |
| `src/components/layout/` | 布局组件 |
| `src/composables/` | 组合式函数 `useXxx` |
| `src/stores/` | Pinia stores，命名 `useXxxStore` |
| `src/locales/` | 语言包 `zh-CN.ts` / `en-US.ts` 等 |
| `src/lib/` | 工具函数 |
| `src/pages/assistant/` | ChatClaw 主助手（与 OpenClaw 隔离） |
| `src/pages/openclaw/` | OpenClaw Gateway 相关页面；Pinia 导航模块名为 `openclaw` |

### 必须遵守

1. **所有组件**：使用 `<script setup lang="ts">`，不用 Options API。
2. **导入路径**：始终用 `@/` 别名，如 `import { Button } from '@/components/ui/button'`。
3. **样式**：用 Tailwind 类名，颜色用 shadcn 语义变量（`bg-background`、`text-foreground`、`text-muted-foreground` 等）。
4. **条件类名**：用 `cn()` 函数合并，如 `cn('text-sm', disabled && 'opacity-50')`。
5. **添加 UI 组件**：运行 `npx shadcn-vue@latest add [组件名]`。
6. **翻译文本**：用 `const { t } = useI18n()`，key 格式 `模块.功能`。
7. **调用后端**：从 `@bindings/...` 导入，必须处理错误。
8. **ref 在模板中的使用**：在 `<template>` 中，ref 会自动解包，**不要**使用 `.value`。
9. **带缓存的页面刷新**：如果页面展示依赖本地缓存 + 后端同步（如先读本地 SQLite/文件缓存，再按时间戳或数量增量同步），手动“刷新”按钮**必须**走真实同步链路，至少触发一次后端对比与同步；禁止只重读前端内存态、Pinia store 或本地目录。
10. **行尾与格式噪音控制**：修改已有文件后，必须先检查 diff 是否出现整文件行尾/格式噪音；若 `git diff --ignore-space-at-eol` 明显小于普通 diff，说明引入了非业务改动，必须恢复原行尾风格并只保留真实逻辑修改。排查所需诊断代码也不得顺手格式化整文件。

### shadcn-vue 组件用法规范

shadcn-vue 组件基于 Radix Vue 封装，必须使用 Vue 标准的 `v-model` / `:model-value` + `@update:model-value` 来绑定值，**不要**使用 Radix 底层的原始 prop 名（如 `:checked`、`@update:checked`、`:pressed`、`@update:pressed` 等）。

```vue
<!-- BAD -->
<Switch :checked="value" @update:checked="value = $event" />

<!-- GOOD -->
<Switch v-model="value" />
```

### i18n 文件格式

翻译文件（`frontend/src/locales/*.ts`）中，**值必须使用单引号**，不要使用双引号。

```ts
export default {
  common: {
    ok: 'OK',
    cancel: 'Cancel',
  },
};
```

### 禁止事项

- 不要手动在 `src/components/ui/` 创建文件，必须用 shadcn CLI
- 不要写内联 style，用 Tailwind 类名
- 不要用相对路径 `../../`，用 `@/` 别名
- 不要硬编码用户可见文本，必须走 i18n
- 不要直接写颜色值如 `text-gray-500`，用语义变量 `text-muted-foreground`
- 不要使用 Radix 底层 prop，必须用 `v-model` 或 `:model-value`
- **不要在模板中使用 `ref.value`**：Vue 3 模板中 ref 会自动解包

### 多窗口入口

- 主窗口入口：`src/main.ts` + `index.html`
- 子窗口入口：`src/winsnap/main.ts` + `winsnap.html` 等
- 新窗口需要在 `vite.config.ts` 的 `rollupOptions.input` 添加入口

---

## UI 视觉规范

### SVG 图标

- **禁止写死颜色**：不要在 SVG 里使用 `stroke="#262626"` / `fill="#000"`。
- **统一改为 `currentColor`**：用 `stroke="currentColor"` / `fill="currentColor"`，让图标自动跟随文本颜色。

### Toast 提示

- **避免彩色大底与强烈阴影**：success/error 不要使用大面积绿/红背景。
- **统一基底**：使用 `bg-popover text-popover-foreground border-border`。
- **区分状态用"克制提示"**：可用左侧细边框或图标灰阶区分 success/error（不使用彩色）。
- **阴影策略**：用 `shadow-sm dark:shadow-none dark:ring-1 dark:ring-white/10`。

---

## 文档规范

### think_docs 文件夹

以下类型的文档应放入项目根目录的 `think_docs/` 文件夹：

- **规划文档**：功能设计、技术方案、架构演进计划等
- **思考文档**：需求分析、方案对比、决策记录等
- **AI 协作文档**：给 AI 辅助开发用的上下文说明、提示词草稿等
- **内部草稿**：任何非面向最终用户/客户的开发过程文档

`think_docs/` 已加入 `.gitignore`，不会被提交到 Git 仓库。

---

## 开发流程参考

### 构建命令 (Taskfile.yml)

- 前端开发：`task frontend:dev`
- 后端开发：`task backend:dev` 或 `task dev` (并发启动前后端)
- 打包构建：参考 `Taskfile.yml` 中的 `build:*` 任务

### 数据库迁移

新增或修改数据表时：

1. 在 `internal/sqlite/migrations/` 创建迁移文件，文件名格式 `YYYYMMDDHHMM_描述.go`
2. 在迁移的 `Up` 函数中编写 DDL/DML
3. 运行应用时 bun 会自动执行未执行的迁移

### 添加新页面

1. 在 `frontend/src/pages/` 下创建页面组件
2. 在 `frontend/src/stores/navigation.ts` 中注册路由
3. 在侧边栏 `frontend/src/components/layout/SideNav.vue` 中添加入口
4. 如需后端接口，在 `internal/services/` 下创建对应服务

---

## 参考资料

- [Wails v3 文档](https://wails.io/)
- [Vue 3 文档](https://vuejs.org/)
- [Tailwind CSS v4 文档](https://tailwindcss.com/)
- [Eino 文档](https://github.com/cloudwego/eino)
- [shadcn-vue 文档](https://www.shadcn-vue.com/)

---

## 归档与规则迭代

### 归档机制

本项目的 `AGENTS.md` 归档与迭代机制同时兼容 **Cursor** 与 **Codex**：

- **Cursor**：通过 `.cursor/hooks/archive-hook.js` 在任务完成后自动提示归档，并支持关键词手动触发
- **Codex**：没有 Cursor Hook 时，改为通过对话关键词**手动触发相同流程**

无论由哪种 AI 助手执行，只要触发“归档 / 迭代 AGENTS.md”，都应遵循同一套归档和迭代规则。

#### 触发方式

1. **Cursor 自动触发**：AI 完成任务后（检测到文件变更或多次工具调用），Cursor Hook 会自动询问"是否归档"
2. **统一手动触发**：在任意对话中输入"归档"、"迭代 AGENTS.md"、"archive"、"iterate" 等关键词即可立即触发
3. **Codex 触发方式**：Codex 遇到上述关键词时，应直接执行归档与迭代流程，不依赖 Hook 或额外插件
4. **超时行为**：仅 Cursor 的自动询问有 30 秒自动跳过；Codex 无此限制

#### 归档行为

归档触发后，AI 助手应执行：

1. **快照归档**：将当前 `AGENTS.md` 复制到 `.cursor/archive/AGENTS_YYYY-MM-DDTHH-MM-SS_xxxxxx.md`
2. **触发迭代**：检查以下内容，并在需要时更新 `AGENTS.md`：
   - 项目中新增或修改的 rules 文件（`.cursor/rules/*.mdc`）
   - 代码结构变化（新增目录、新服务、新页面等）
   - 开发约定变更
   - 技术栈更新
   - 缺失或过时的规范
3. **保持兼容**：更新后的内容必须同时适用于 Cursor 与 Codex；若某项能力仅存在于 Cursor（如 Hook），必须明确标注仅 Cursor 生效，并给出 Codex 下的替代执行方式

#### 归档存储位置

- 归档目录：`.cursor/archive/`
- 归档日志：`.cursor/archive/archive_log.json`
- 状态文件：`.cursor/archive/.archive_state.json`
- 仅保留最近 50 条归档记录

#### 手动迭代

如果需要主动迭代 `AGENTS.md`，可以：

1. 在对话中输入"归档"或"迭代 AGENTS.md"
2. AI 先执行归档，再检查规则文件、代码结构与开发约定
3. AI 根据检查结果更新 `AGENTS.md`
4. 若当前助手是 Codex，必须按本节规则直接执行，不应因为缺少 Cursor Hook 而跳过

#### 触发关键词

以下关键词均可触发归档与迭代（不区分大小写）：

- `归档`
- `archive`
- `迭代`
- `iterate`
- `更新规则`


