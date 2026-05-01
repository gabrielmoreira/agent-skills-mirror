# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 开发命令

### 前端（React + TypeScript）

```bash
pnpm install              # 安装依赖
pnpm dev                  # 启动 Vite 开发服务器（端口 24200，单独前端调试用）
pnpm build                # TypeScript 编译 + Vite 构建
pnpm test                 # Vitest 运行全部测试（370+，含 3 个遗留的 Sidebar/Settings/PlatformIcon 失败，非本次改动引入）
pnpm test -- src/test/skillStore.test.ts  # 运行单个测试文件
pnpm test:watch           # Vitest 监听模式
pnpm typecheck            # tsc --noEmit 类型检查
pnpm lint                 # ESLint 检查
```

### Rust 后端（Tauri v2）

```bash
cd src-tauri && cargo test           # 运行全部 Rust 测试（214+）
cd src-tauri && cargo test db::      # 运行指定模块测试
cd src-tauri && cargo clippy -- -D warnings  # Lint 检查
```

### 完整应用

```bash
pnpm tauri dev             # 启动 Tauri 开发模式（含前端热重载）
pnpm tauri build           # 构建可分发的桌面应用
```

## 架构概述

跨平台 AI 技能管理桌面应用，三层架构：

```
React 前端 (src/)  ──Tauri IPC──▶  Rust 后端 (src-tauri/src/)  ──SQLx──▶  SQLite
```

- **前端**：React 18 + TypeScript + Tailwind CSS 4 + shadcn/ui，Zustand 状态管理，React Router v7 路由
- **后端**：Rust，通过 `#[tauri::command]` 宏暴露 40+ 个 IPC 命令，前端用 `invoke()` 调用
- **数据库**：SQLite（WAL 模式），位于 `~/.skillsmanage/db.sqlite`，SQLx 异步驱动，schema 在 `db.rs` 中定义并自动迁移
- **HTTP**：`reqwest` 用于 GitHub API 调用（Marketplace 源同步）和 AI API 调用（技能解释）

### 核心业务模型

- **技能（Skill）**：包含 YAML 前缀的 Markdown 文件（SKILL.md），是核心管理单元
- **中央目录**：`~/.agents/skills/` 是技能的唯一真实来源（canonical source）
- **平台安装**：通过符号链接（symlink）将中央技能安装到各平台目录（如 `~/.claude/skills/`）
- **自动中央化（Auto-centralize）**：安装仅存在于某平台的技能到其他平台时，`linker.rs` 的 `ensure_centralized` 会自动将其拷贝到中央目录并更新 DB 的 `canonical_path`/`is_central`，再走正常 symlink/copy 流程。调用方（包括 `install_skill_to_agent_impl` 和 `install_skill_to_agent_copy_impl`）对此透明
- **集合（Collection）**：技能分组，支持批量安装和 JSON 导入/导出
- **发现（Discover）**：递归扫描磁盘上的项目级技能文件，主从分离布局（左面板项目列表 + 右面板技能详情）；`is_already_central` 在 DB 加载时根据文件系统重新计算，不是静态快照
- **技能市场（Marketplace）**：从 GitHub 仓库远程浏览和安装技能，三 Tab 页面（推荐/官方源目录/我的源）

### 页面路由

| 路由 | 页面 | 布局模式 |
|------|------|---------|
| `/central` | 中央技能库 | 技能卡片列表（两列） |
| `/platform/:agentId` | 平台技能视图 | 技能卡片列表（两列） |
| `/skill/:skillId` | 技能详情 | **双栏布局**：左栏 SKILL.md 预览（全高），右栏 sidebar（metadata + 紧凑图标式安装状态 + collections） |
| `/collections` | 技能集合 | 上方卡片横排选中 + 下方技能列表 |
| `/discover`, `/discover/:projectPath` | 项目技能库 | 左面板项目列表 + 右面板技能详情 |
| `/marketplace` | 技能市场 | 三 Tab（推荐/官方源/我的源） |
| `/settings` | 设置 | 卡片分区 |

### IPC 命令模块（src-tauri/src/commands/）

| 模块 | 职责 |
|------|------|
| `scanner.rs` | 扫描目录并解析 SKILL.md 文件的 YAML 前缀 |
| `agents.rs` | 平台 CRUD（27 个内置 + 自定义），支持 coding/lobster 分类 |
| `linker.rs` | 符号链接/复制方式安装和卸载技能 |
| `skills.rs` | 技能查询和 Markdown 内容读取 |
| `collections.rs` | 集合管理、批量安装、导入导出 |
| `discover.rs` | 全磁盘项目扫描和导入，支持 /Applications 目录 |
| `settings.rs` | 扫描目录和应用设置的键值存储 |
| `marketplace.rs` | GitHub 源同步、远程技能安装、AI 技能解释（Claude/GLM/MiniMax/Kimi/DeepSeek/OpenRouter） |

### 前端静态数据（src/data/）

| 文件 | 内容 |
|------|------|
| `officialSources.ts` | 70+ 官方 publisher 元数据 + 24 个推荐 skills（含 tag 分类） |
| `aiProviders.ts` | 7 个 AI 提供商预设（含国内/国际区域端点） |

### 共享 UI 模式

- **`UnifiedSkillCard`**（`src/components/skill/UnifiedSkillCard.tsx`）：**所有页面的技能卡片唯一实现**。通过 props 自适应 5 种场景（central/platform/discover/marketplace/collection），不要在各页面重建内联卡片组件。统一样式：`rounded-xl` + `ring-1 ring-border` + `bg-card` + `shadow-sm`
- **`InstallDialog`**（`src/components/central/InstallDialog.tsx`）：默认**勾选已链接平台**（反映当前状态），宽度 `sm:max-w-2xl`，平台列表两列网格。`CollectionInstallDialog` 同宽度布局但默认勾选所有 detected 平台（批量首装场景）
- **平台图标切换**：`UnifiedSkillCard` 的 `platformIcons` prop 分 LOBSTER/CODING 两行显示，点击图标即时切换安装/卸载（symlink 方式），走 `centralSkillsStore.togglePlatformLink`

## 代码约定

- **路径别名**：`@/` 映射到 `src/`（在 vite.config.ts 和 tsconfig.json 中配置）
- **状态管理**：每个业务域一个独立的 Zustand store（`src/stores/`），store 内部直接调用 `invoke()` 与后端通信；不要在组件里直接 `invoke()`
- **技能卡片**：只用 `UnifiedSkillCard`，不要新建场景专用卡片组件
- **主题系统**：Catppuccin 3 种风格（Mocha/Frappe/Latte），14 种 accent 配色，通过 `data-theme` 和 `data-accent` HTML 属性切换
- **国际化**：中英双语（`src/i18n/`），所有用户可见文本必须走 i18n
- **测试**：Vitest + jsdom + React Testing Library，setup 在 `src/test/setup.ts`；Tauri `invoke` 在测试中通过 `window.__TAURI_INTERNALS__` mock
- **未使用变量**：ESLint 规则允许 `_` 前缀的未使用参数和变量
- **Rust 后端**：所有 IPC 命令函数签名中通过 `State<AppState>` 注入数据库连接池；不使用 `sqlx::query_as!` 宏（需要 DATABASE_URL），统一使用 `sqlx::query()` + 手动 `Row::get()` 映射
- **Marketplace GitHub 适配器**：扫描仓库根目录和 `skills/` 子目录，解析 SKILL.md frontmatter 获取 name/description；所有同步到的 skills 缓存在 `marketplace_skills` 表，复用 `sync_registry`/`search_marketplace_skills` 命令
- **AI 解释**：从 settings 表动态读取 provider/api_key/model/api_url，支持 Anthropic 格式和 OpenAI 格式响应，自动跳过 `thinking` 类型 content block
- **linker.rs 约束**：所有 install/uninstall 路径以中央目录为源。添加新的安装方式时，复用 `ensure_centralized` 保证非中央技能也能被分发
