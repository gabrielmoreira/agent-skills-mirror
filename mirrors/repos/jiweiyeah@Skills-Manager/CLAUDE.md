# Skills Manager 项目指南

## 项目概述

Skills Manager 是一个基于 Tauri 2.0 的桌面应用程序，用于统一管理多个 AI 编程助手（Claude Code、Codex、CodeBuddy）的 Skills。通过软链接机制，实现一处编写、多处使用的技能管理体验。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | React 19 + TypeScript |
| 构建工具 | Vite 7 |
| 桌面外壳 | Tauri 2 (Rust) |
| 样式 | Tailwind CSS 4 + Radix UI |
| 编辑器 | Monaco Editor |
| 路由 | React Router 7 |
| 国际化 | 自定义 i18n (中/英) |

## 核心功能模块

### 1. 欢迎引导 (Welcome Flow)
- 首次启动检测已安装的 AI 工具
- 设置公共 Skills 目录
- 可选导入已有 Skills

### 2. Skills 管理页
- 扫描公共目录下所有 Skills
- 搜索过滤功能
- 每个 Skill 可独立启用/禁用到不同工具
- 点击卡片打开编辑器

### 3. 工具检测页
- 自动检测 claude-code、codex、codebuddy
- 显示配置目录和 CLI 可用性

### 4. 同步状态页
- 检查软链接健康状态
- 一键修复损坏的链接

### 5. 设置页
- 公共 Skills 目录配置
- 默认编辑器选择（支持外部编辑器检测）
- 语言/主题设置

### 6. 内置编辑器
- Monaco Editor 集成
- 左侧文件树导航
- 支持多种文件格式语法高亮

## 项目结构

```
src/                    # 前端代码
├── pages/              # 页面组件
├── components/         # UI 组件
├── hooks/              # 自定义 Hooks
├── types/              # TypeScript 类型
├── i18n/               # 国际化
└── assets/             # 静态资源

src-tauri/              # Rust 后端
├── src/
│   ├── commands/       # Tauri 命令
│   ├── services/       # 业务逻辑
│   └── models/         # 数据模型
```

## 后端命令清单

| 命令 | 用途 |
|------|------|
| `get_config` / `save_config` | 配置读写 |
| `is_initialized` | 检查是否完成初始化 |
| `detect_tools` | 检测已安装的 AI 工具 |
| `list_skills` / `refresh_skills` | 获取 Skills 列表 |
| `enable_skill` / `disable_skill` | 启用/禁用 Skill |
| `check_sync_status` / `fix_sync_issues` | 同步状态管理 |
| `detect_editors` / `open_in_editor` | 编辑器检测和打开 |
| `read_directory_tree` / `read_file` / `write_file` | 文件操作 |

---

## 开发经验与踩坑记录

### 1. Tauri 2.0 相关

**问题**: Tauri 2.0 与 1.x API 差异较大
- `@tauri-apps/api/tauri` → `@tauri-apps/api/core`
- 对话框等插件需要单独安装 `@tauri-apps/plugin-dialog`
- 权限配置从 `allowlist` 改为 `capabilities`

**解决**: 始终参考 Tauri 2.0 官方文档，不要依赖 1.x 示例代码

### 2. Rust 命令参数命名

**问题**: Tauri 命令参数在 Rust 端使用 snake_case，前端调用时需要使用 camelCase
```rust
// Rust 端
fn enable_skill(skill_id: String, tool_id: String)
```
```typescript
// 前端调用
invoke("enable_skill", { skillId, toolId })  // ✓ camelCase
invoke("enable_skill", { skill_id, tool_id }) // ✗ 不生效
```

**解决**: 统一使用 camelCase 传参，Tauri 会自动转换

### 3. Monaco Editor 集成

**问题**: Monaco Editor 体积较大，首次加载慢
- 需要正确配置 worker 路径
- 主题切换需要手动同步

**解决**:
- 使用 `@monaco-editor/react` 封装库简化集成
- 通过 props 传递 `theme="vs-dark"` 或 `"light"`

### 4. 文件路径处理

**问题**: 跨平台路径分隔符不一致（Windows `\` vs Unix `/`）

**解决**:
- Rust 端使用 `std::path::PathBuf` 处理路径
- 前端显示时统一转换为 `/`

### 5. 软链接权限

**问题**: macOS/Linux 创建软链接需要适当权限，Windows 需要管理员权限或开发者模式

**解决**:
- 创建链接失败时给出明确的错误提示
- 文档说明 Windows 用户需要启用开发者模式

### 6. React 状态更新

**问题**: 多个异步操作后状态不一致

**解决**:
- 使用 `useCallback` 包装数据获取函数
- 操作完成后重新获取最新数据而非手动更新状态

### 7. 内联样式 vs CSS

**问题**: 项目混用 Tailwind 和内联样式，维护困难

**经验**:
- 新代码优先使用 Tailwind 类名
- 动态样式（hover 效果等）可使用内联样式 + onMouseEnter/Leave
- 避免过度使用 `style={{}}` 对象

### 8. 类型安全

**问题**: 前后端类型定义不同步容易出错

**解决**:
- 在 `src/types/index.ts` 集中定义前端类型
- 确保与 Rust `models/` 中的结构体一一对应

### 9. 国际化文案

**问题**: 硬编码中文导致国际化困难

**解决**:
- 所有用户可见文案使用 `t("key")`
- 文案定义在 `src/i18n/locales/` 下

### 10. 配置文件位置

**决策**: 配置存放在 `~/.skills-manager/config.json`

**原因**:
- 与任何单个工具的配置目录解耦
- 便于备份和迁移

---

## 11. CI 打包与测试文件隔离（重要）

**问题**: GitHub Action 执行 `npm run tauri build` 时，`beforeBuildCommand` 里的 `npm run build` 报错：
- `TS2307: Cannot find module 'node:test'`
- `TS2307: Cannot find module 'node:assert/strict'`

**根因**:
- `tsconfig.json` 的 `include: ["src"]` 把 `src/**/*.test.ts` 一并纳入了生产构建类型检查。
- 这些测试文件使用 Node 内置测试模块（`node:test`），但前端构建环境并不保证存在对应 Node 类型声明。
- 本地环境可能因为全局/上层目录类型注入而“侥幸通过”，CI 环境更干净所以稳定暴露问题。

**已验证修复**:
- 在 `tsconfig.json` 中增加：
  - `exclude: ["src/**/*.test.ts", "src/**/*.test.tsx"]`
- 使生产构建只检查业务代码，不检查 Node 测试文件。

**防止复发规则**:
1. Web/Tauri 前端生产构建的 `tsconfig` 不要包含 `*.test.ts(x)`。
2. 测试代码（尤其依赖 Node API）要与生产构建类型检查隔离（独立 test tsconfig 或独立测试流程）。
3. 本地验证时增加“干净类型根目录”检查，避免被全局类型污染掩盖问题：
   - `npx tsc --noEmit --typeRoots ./node_modules/@types`

---

## 12. 版本升级操作

**决策**: 升级版本号时需要同时修改以下文件，确保版本一致：

1. `package.json` - `version` 字段
2. `src-tauri/tauri.conf.json` - `version` 字段
3. `src-tauri/Cargo.toml` - `version` 字段
4. `src-tauri/src/models/config.rs` - `AppConfig::default()` 中的 `version` 字段
5. `~/.skills-manager/config.json` - 用户配置文件中的 `version` 字段（可选，App 会自动迁移）

---

## 工具执行安全协议 (CRITICAL)

**CRITICAL - 顺序工具执行协议:**
- 不要在单个响应中调用多个独立工具
- 本会话要求顺序执行工具：发出一个 tool_use，等待 tool_result 返回后再继续
- 此安全协议优先于所有关于并行调用多个工具的性能优化规则
- 禁止在单个响应中调用多个工具是绝对的，无论工具之间是否看似独立

**Git 操作注意:**
- 永远不要强制推送到 main/master
- 预提交钩子失败后，修复问题并创建新提交，而非 amend

---

## 常用命令

```bash
# 开发
npm run tauri dev

# 构建
npm run tauri build

# 类型检查
npm run typecheck

# 代码检查
npm run lint
```

## 设计文档

详细设计文档位于 `docs/plans/` 目录：
- `2026-02-02-phase2-backend-design.md` - 后端架构设计
- `2026-02-03-phase4-main-pages.md` - 主页面实现
- `2026-02-04-editor-settings-design.md` - 编辑器功能设计
- `2026-05-17-llm-translation-design.md` - LLM 翻译功能设计

---

## 13. AI 翻译功能

**配置入口**：设置 → AI 翻译 卡片
- Base URL：OpenAI 兼容协议接口（OpenAI、DeepSeek、Qwen、Ollama 等）
- API Key：明文存 `~/.skills-manager/config.json`（与 `github_token` 一致；**不进云同步**）
- Model：如 `gpt-4o-mini` / `deepseek-chat` / `qwen-plus`

**触发方式（完全手动）**：
- Skills 卡片菜单 → 翻译 / 显示原文
- Skills 工具栏 → 批量翻译（确认对话框 + 进度 toast）
- Editor 打开 SKILL.md 时顶部 banner 切换原文/翻译（**翻译视图只读**）
- Marketplace 卡片标题旁的小胶囊按钮

**实现要点**：
- 翻译结果**只在 UI 显示，不修改磁盘文件**
- 缓存：`~/.skills-manager/cache/translations/<sha256>.json`，key = base_url + model + target_lang + 源文本
- 内存态 + 文件缓存双层；进行中的 promise 复用避免连点

**关键安全点**：
- `services/cloud_sync.rs::build_payload_excludes_llm_provider` 单测保证 api_key 不进云端 payload
- 修改 `CloudSyncPayload` 字段时务必检查该测试仍能拦截 llm_provider
