# skills-v2 (CCG Multi-Model Collaboration System)

> [根目录](../CLAUDE.md) > **skills-v2**

**Last Updated**: 2026-04-10 (v2.1.16)

---

## 变更记录 (Changelog)

> 完整变更历史请查看 [CHANGELOG.md](./CHANGELOG.md)

### 2026-04-10 (v2.1.16)
- ✨ **Init 交互状态机**：`init` 重构为状态机，每步首个 list 内嵌 `← 返回上一步` 和 `× 取消` 哨兵；Step 3 MCP 因首 prompt 是 checkbox，加前导 list 守门；解决"填错要 Ctrl+C 全部重来"痛点
- ✨ **摘要页跳回菜单**：最终确认页改 list 菜单，支持"改 API / 改模型 / 改 MCP / 改性能"任意跳回，跑完自动回摘要
- ✨ **API 跳过选项**（用户反馈）：Step 1/4 新增"跳过 — 我已通过 cc-switch / 其他工具自行配置"选项，不写 `settings.json` 的 `ANTHROPIC_*`
- 🔄 **`src/commands/init.ts`**：Step 1-4 抽取闭包函数 + 主循环状态机，net +200 行；i18n 新增 `nav`/`summaryMenu`/`api.skipOption` 等 key

### 2026-04-10 (v2.1.15)
- 🐛 **`--gemini-model` 泄漏到纯 codex 调用行修复**（#130）：`injectConfigVariables()` 改为行级感知替换，纯 `--backend codex/claude` 行清除 flag，`--backend gemini` 和条件行 `<codex|gemini>` 保留。新增 11 个单元测试。

### 2026-04-10 (v2.1.14)
- 📝 **CLAUDE.md 全量同步**：命令 29、提示词 19（claude/6+codex/6+gemini/7）、Agent 7、子模块文档建立（src/CLAUDE.md、templates/CLAUDE.md、codeagent-wrapper/CLAUDE.md 三个子索引）

### 2026-04-07 (v2.1.14)
- 🐛 **模型路由硬编码修复**：21 个模板 ROLE_FILE 路径 + 表头 + 执行指令全部动态化，`{{BACKEND_PRIMARY}}/{{FRONTEND_PRIMARY}}` 替代硬编码 `codex/gemini`

### 2026-04-05 (v2.1.13)
- 🐛 **Windows Gemini 多行参数截断**（#129）：Windows 上 cmd.exe 截断多行 `-p` 参数，改用 stdin pipe；binary `5.9.0` → `5.10.0`

### 2026-04-03 (v2.1.12)
- ✨ **302.AI 赞助商集成**（#126）：init + 菜单 API 配置新增 302.AI 选项，自动填入 baseUrl，CLI 显示返现链接
- ✨ **README 赞助商 Banner**：中英文 README 顶部新增 302.AI 可点击 Banner + 产品介绍

### 2026-03-31 (v2.1.11)
- 🐛 **更新后 MCP 提示词显示未配置**（#124）：`update` 无条件传 `--skip-mcp` 导致 `mcpProvider` 被覆盖，修复为从已有配置恢复
- ✨ **Impeccable 命令可选安装**（#125）：init 新增 confirm 提示，20 个前端设计命令默认不安装
- ✨ **X (Twitter) 社区入口**：README 加 `@CCG_Workflow` 徽章 + demo 推文 + Contact 区

### 2026-03-31 (v2.1.1)
- 🐛 **Skill Registry 命令 frontmatter 修复**：`generateCommandContent()` 生成的 27 个 command 文件补上 YAML frontmatter，修复 CC 命令索引级联失败

### 2026-03-31 (v2.1.0)
- ✨ **模型路由可配置**（Issue #121）：init Step 2/4 选前端/后端模型（gemini/codex/claude），Gemini 型号可选
- ✨ **菜单模型路由配置**：`6. 配置模型路由`，切换后自动重装模板
- 🔄 **20+ 模板去硬编码**：`--backend gemini`/`--backend codex` 替换为 `{{FRONTEND_PRIMARY}}`/`{{BACKEND_PRIMARY}}`
- 🔄 **`{{GEMINI_MODEL_FLAG}}` 安装时替换**：不再留给运行时解释

### 2026-03-31 (v2.0.0)
- ✨ **Skill Registry 机制**：SKILL.md frontmatter 驱动自动命令生成，新增技能只需写一个 SKILL.md
- ✨ **域知识秘典全量导入**：10 大领域 61 个知识文件（安全/架构/DevOps/AI/开发/前端设计/基础设施/移动端/数据工程/编排）
- ✨ **Impeccable 工具集**：20 个 UI/UX 精打磨技能（polish/audit/harden/clarify/critique 等）
- ✨ **Override-Refusal**：`/hi` 命令，会话级反拒绝覆写器
- ✨ **Scrapling 技能**：网页抓取，支持 Cloudflare/WAF 绕过
- ✨ **3 个新输出风格**：冷刃简报 + 铁律军令 + 祭仪长卷，总数 8 种
- 🏗 **`skill-registry.ts`**：新模块，frontmatter 解析 + 技能发现 + 命令生成

### 2026-03-30 (v1.8.3)
- ✨ **`/ccg:team` 统一工作流**：第 28 个斜杠命令，8 阶段企业级工作流（需求→架构→规划→开发→测试→审查→修复→集成），7 角色 Agent Teams 自动编排
- ✨ **3 个新 Agent**：`team-architect`（架构师）、`team-qa`（QA 工程师）、`team-reviewer`（代码审查员）
- ✨ **Evaluator-Optimizer 反馈环**：最多 2 轮自动修复 Critical 问题
- ✨ **多模型交叉**：架构阶段 Codex∥Gemini 并行分析，审查阶段双模型交叉验证

### 2026-03-27 (v1.8.2)
- 🐛 **Windows ccline 状态栏修复**：路径从 `%USERPROFILE%` 改为 `~`，Claude Code 统一支持

### 2026-03-27 (v1.8.1)
- 🐛 **WORKDIR 路径推断修复**：20 个命令模板强制 `pwd`/`cd` 获取工作目录，禁止从 `$HOME` 推断，修复沙箱/云端环境路径错误
- 🐛 **spec-init 目录防御**：Step 3 禁止 `cd` 到其他路径
- 🐛 **Windows 兼容**：WORKDIR 获取支持 `pwd`（Unix）+ `cd`（Windows CMD）

### 2026-03-26 (v1.8.0)
- 🐛 **Gemini session_id 解析修复**：修复 Gemini CLI init 事件前 MCP 文本导致 JSON 解析失败，恢复 session_id 捕获
- 🐛 **Gemini 会话复用恢复**：所有模板恢复 `resume <SESSION_ID>`，支持并行多会话
- ✨ **spec-impl 跨阶段会话复用**：原型→审查复用 `CODEX_PROTO_SESSION` / `GEMINI_PROTO_SESSION`

### 2026-03-26 (v1.7.97)
- 🐛 **Gemini `-p -` 显示修正**：`Command:` 行显示真实任务文本而非 `-p -`，消除误导
- 🐛 **Session-ID 早期输出**：wrapper 在 `session_started` 时立即输出 `Session-ID:` 到 stderr，防止超时后 Claude 误用 PID resume
- 🔄 **Binary 版本升级**：`5.8.0` → `5.9.0`

### 2026-03-25 (v1.7.92)
- ✨ **初始化交互重构**：3 步流程（API 提供方 → MCP 多选 → 性能模式），赞助商预留位，MCP 多选共存
- 🐛 **第三方 API 修复**：`ANTHROPIC_API_KEY` → `ANTHROPIC_AUTH_TOKEN`，修复 `/login` 问题
- 🐛 **Gemini CLI stdin 修复**：`-p -` → `-p "任务文本"`，修复 Gemini 无法调用

### 2026-03-25 (v1.7.91)
- 🐛 **Gemini CLI stdin 兼容性修复**：`-p -` 改为 `-p "任务文本"` 直接传递，修复 Gemini 无法调用的问题

### 2026-03-23 (v1.7.90)
- ✨ **`--progress` 进度输出**：codeagent-wrapper 新增 `--progress` 参数，后台任务 stderr 输出精简进度行，告别黑箱等待（PR #112）
- 🐛 **全模板 `--progress` 覆盖**：补漏 `debug.md`、`spec-review.md`、`codex-exec.md` review 调用

### 2026-03-20 (v1.7.89)
- 🐛 **权限规则匹配修复**：`Bash(*codeagent-wrapper*)` 加前导通配符，修复 Windows/macOS 完整路径不匹配
- 🐛 **spec-init `<<<` 拦截修复**：改用管道替代 here-string
- 🔄 **全平台 permissions.allow**：macOS/Linux 不再依赖 Hook + jq，升级自动迁移清理

### 2026-03-19 (v1.7.88)
- 🐛 **TS 类型错误修复**：`installer-mcp.ts` 参数类型收紧为 `McpServerConfig`，修复 `tsc --noEmit` 报错
- 🔄 **发版流程加固**：`pnpm typecheck` + `pnpm test` 列为发版必检项

### 2026-03-19 (v1.7.87)
- 🐛 **Gemini 失败重试**：20 个命令模板新增 Gemini 调用失败重试规则（最多 2 次，间隔 5s），3 次全败才降级单模型
- 🐛 **Codex 结果必须等待**：20 个命令模板新增 Codex 等待规则，禁止在 Codex 未返回时跳过下一阶段
- 🐛 **team-exec Agent Teams 修正**：明确使用 TeamCreate + TaskCreate + Agent(team_name=...) 创建真正的 Agent Teams，禁止退化为普通 Agent

### 2026-03-18 (v1.7.86)
- 🐛 **Skills 路径修正**：`SKILL.md` 中 `run_skill.js` 路径从 `~/.claude/skills/` 修正为 `~/.claude/skills/ccg/`，对齐 v1.7.75 命名空间迁移

### 2026-03-17 (v1.7.85)
- ✨ **Binary 双源下载**：GitHub（8s 超时）→ Cloudflare R2 镜像（60s），国内用户友好
- 🐛 **更新跳过 binary 重复下载**：`preserveBinary` + `verifyBinary()` / `showBinaryDownloadWarning()`
- 🐛 **更新失败显示 binary 提示**：与初始化一致的红框警告 + 手动修复指引

### 2026-03-12 (v1.7.83)
- 🔄 **安装器重构**：1878 行单文件 → 5 个聚焦模块（-25%），`cmd()` 构建器 + `MCP_PROVIDERS` 注册表 + 共享管线，零功能变更

### 2026-03-12 (v1.7.82)
- ✨ **fast-context MCP 集成**：Windsurf Fast Context 作为第四个代码检索选项（推荐），支持 API Key 可选 + FC_INCLUDE_SNIPPETS
- ✨ **三端搜索提示词**：自动注入 Claude Code rules + Codex AGENTS.md + Gemini GEMINI.md，卸载自动清理
- ✨ **Gemini MCP 同步**：`syncMcpToGemini()` 镜像 MCP 到 `~/.gemini/settings.json`

### 2026-03-11 (v1.7.81)
- 🔄 **`/ccg:commit` Context 自动归档**：从 git diff 自动生成 ContextEntry，不再依赖手动 session.log
- 🔄 **`/ccg:context log` 降为可选**：init 一次 → 正常开发 → commit 全自动

### 2026-03-11 (v1.7.80)
- ✨ **`/ccg:context` 命令**：第 27 个斜杠命令，`.context/` 目录初始化 + 决策日志 + 压缩归档 + 历史查看
- ✨ **Context Compress Phase**：`/ccg:commit` 提交时自动压缩 session.log → history/commits.jsonl
- ✨ **13 个角色提示词 `.context Awareness`**：Codex/Gemini 提示词注入 `.context/prefs/` 读取指令
- ✨ **Quality Gate Rules**：`~/.claude/rules/ccg-skills.md` 定义质量关卡自动触发规则，安装时自动写入

### 2026-03-11 (v1.7.79)
- 🐛 **Binary 下载容错**：3 次重试 + 60s 超时 + 失败醒目告警（红框 + 手动修复指引）+ 不阻塞安装
- 🐛 **Update 流程加固**：binary 备份/恢复 + subprocess 超时 120s→300s

### 2026-03-11 (v1.7.78)
- 🐛 **Windows Hook exit 255 修复**：Windows 自动授权改用 `permissions.allow`，不再依赖 jq/grep

### 2026-03-10 (v1.7.77)
- 🏗 **二进制迁移至 GitHub Release**：npm 包 16.3MB→161KB，Actions CI 交叉编译，installer 按需下载

### 2026-03-10 (v1.7.76)
- 📝 **README 重构**：命令分组（7 类）、新增 Why CCG? + CONTRIBUTING.md + Issue 模板 x3、配置章节去重折叠

### 2026-03-10 (v1.7.75)
- 🐛 **Skills 命名空间隔离**：`skills/` → `skills/ccg/`，卸载不再误删用户自建 skill + 旧版自动迁移

### 2026-03-09 (v1.7.74)
- 🔄 **spec 模板 guardrail**：`spec-research`/`spec-plan`/`spec-impl` 添加 USER GUIDANCE RULE + TASKS FORMAT RULE，内部 `/opsx:*` 调用标注 internal，失败引导至 `/ccg:spec-*`
- 🐛 **Gemini CLI `.env` 隔离**：`cmd.Dir=$HOME` + `--include-directories` 避免项目 `.env` 覆盖全局 API Key
- 🐛 **Codex 测试修正**：环境变量名 `CODEX_BYPASS_SANDBOX` → `CODEX_REQUIRE_APPROVAL`

### 2026-03-09 (v1.7.73)
- ✨ **`/ccg:codex-exec` 命令**：第 26 个斜杠命令，Codex 全权执行 + 多模型审核，Claude token 极低消耗
- ✨ **Skills 体系**：6 个原生 skill（verify-security/quality/change/module + gen-docs + multi-agent）
- ✨ **context7 MCP 自动安装**：免费库文档查询，无需 API Key
- ✨ **Codex MCP 同步**：`syncMcpToCodex()` 镜像同步到 `~/.codex/config.toml`
- 🐛 **修复 `--skip-mcp` / 安装卸载路径 / 模板替换 / 计数 / 失败反馈**

### 2026-03-09 (v1.7.70)
- ✨ **菜单 UI 大改版**：ASCII Art Logo + 双线边框 + 编号快捷键 + CJK 宽度感知对齐
- 🔄 **MCP 推荐调整**：ace-tool 恢复为默认推荐（`enhance_prompt` 已不可用），中转推荐 https://acemcp.heroman.wtf/
- 🗑️ **仓库清理**：移除 11 个临时/缓存文件，更新 `.gitignore`

### 2026-03-09 (v1.7.69)
- ✨ **国际化 (i18n)**：首次安装语言选择，CLI 全路径 i18n 化，README 英文版
- ✨ **codeagent-wrapper Hook 自动授权**：解决 `permissions.allow` 不生效问题，需 `jq`

### 2026-03-09 (v1.7.68)
- 🐛 **修复 update 命令全局安装死循环**：npm 全局安装用户本地工作流过旧时不再错误推荐 `npm install -g`
- ✅ **测试覆盖率 38 → 130**：新增 version/config/platform/installer 四组测试，模板变量完整性检查

### 2026-03-07 (v1.7.67)
- 🐛 **修复 spec 工作流完全对齐 OPSX**：修复状态持久化问题，确保用户切换上下文后可以正确恢复
- 🔄 **多模型协作成果采纳**：在调用 OPSX 前输出结构化总结，确保 Codex/Gemini 的分析结果被正确传递
- 🗑️ **移除 spec-init ace-tool 检查**：ace-tool MCP 为可选项，不作为必需检查

### 2026-03-06 (v1.7.66)
- 🐛 **修复 `spec-research` 并行调用缺失**：补全 Step 4 多模型并行探索模板，添加 `run_in_background: true` 和完整 Bash 并行调用示例

### 2026-03-01 (v1.7.63)
- 🔄 **适配 OpenSpec 1.2**：`spec-init` 支持 Profile 系统 + 自动检测，`spec-review` 修复过时引用，保持 CCG 封装纯粹性

### 2026-02-27 (v1.7.62)
- 🔄 **Gemini 模型升级**：`gemini-3-pro-preview` → `gemini-3.1-pro-preview`（PR #65 by @23q3）

### 2026-02-10 (v1.7.60)
- ✨ **Agent Teams 系列**：新增 4 个独立命令（`team-research`/`team-plan`/`team-exec`/`team-review`）
- 🏗️ **并行实施**：利用 Claude Code Agent Teams spawn Builder teammates 并行写代码
- 📋 **完整链路**：需求→约束 → 消除歧义→计划 → 并行实施 → 双模型审查
- 🔒 **完全独立**：Team 系列不依赖现有 ccg 命令，自成体系

### 2026-02-08 (v1.7.57)
- ✨ **MCP 工具扩展**：新增 ContextWeaver（推荐）+ 辅助工具（Context7/Playwright/DeepWiki/Exa）
- ✨ **API 配置**：初始化和菜单新增 API 配置，自动添加优化配置和权限白名单
- ✨ **实用工具**：新增 ccusage（用量分析）+ CCometixLine（状态栏）
- ✨ **Claude Code 安装**：支持 npm/homebrew/curl/powershell/cmd 多种方式

### 2026-01-26 (v1.7.52)
- 🚀 **OpenSpec 升级**：迁移到 OPSX 架构，废弃 `/openspec:xxx`，启用 `/opsx:xxx`
- 🔄 **命令更新**：更新 `spec-*` 系列命令以支持新的 `/opsx` 命令
- 🗑️ **清理**：移除过时的 OpenSpec 指导块和旧命令

### 2026-01-25 (v1.7.51)
- 🌏 **修复默认语言为英文的问题**：将 CLI 所有命令描述从硬编码英文改为中文

### 2026-01-21 (v1.7.47)
- 🐛 **修复 `gemini/architect.md` 缺失**：新增前端架构师角色提示词
- ✅ **专家提示词数量**：12 → 13 个（Codex 6 + Gemini 7）

---

## 模块职责

**CCG (Claude + Codex + Gemini)** - 多模型协作系统的核心实现，提供：

1. **多模型协作编排**：可配置路由 Gemini（前端）+ Codex（后端）+ Claude（编排），v2.1.0+ 支持切换
2. **29 个斜杠命令**：开发工作流 + Git 工具 + 项目管理 + OPSX + Agent Teams + Codex 执行 + Prompt 增强 + Skill Registry 自动生成
3. **19 个专家提示词**：Claude 6 个 + Codex 6 个 + Gemini 7 个
4. **7 个子智能体**：planner / ui-ux-designer / init-architect / get-current-datetime / team-architect / team-qa / team-reviewer
5. **Skill Registry**：SKILL.md frontmatter 驱动，user-invocable 技能自动生成 slash commands
6. **100+ 技能文件**：6 质量关卡 + 10 域知识秘典（61 文件）+ 20 impeccable 工具 + scrapling + override-refusal
7. **跨平台 CLI 工具**：一键安装（支持 macOS、Linux、Windows）
8. **MCP 集成**：fast-context（推荐）/ ace-tool / ContextWeaver + context7（自动安装）+ Codex & Gemini MCP 同步
9. **Agent Teams 并行实施**：Team 系列 5 个命令（含统一工作流），spawn Builder teammates 并行写代码
10. **8 种输出风格**：默认 + 专业工程师 + 猫娘 + 老王 + 大小姐 + 邪修 + 冷刃简报 + 铁律军令 + 祭仪长卷

---

## 模块索引

| 子模块 | 文档 | 职责 |
|--------|------|------|
| TypeScript CLI 源码 | [src/CLAUDE.md](./src/CLAUDE.md) | CLI 主入口、命令实现、安装器、i18n、工具链 |
| 模板文件 | [templates/CLAUDE.md](./templates/CLAUDE.md) | 斜杠命令、提示词、子智能体、技能、规则模板 |
| codeagent-wrapper | [codeagent-wrapper/CLAUDE.md](./codeagent-wrapper/CLAUDE.md) | Go 二进制包装器，多模型调用桥接，v5.10.0 |

---

## 入口与启动

### 用户安装入口

```bash
# 一键安装（推荐）
npx ccg-workflow

# 交互式菜单
npx ccg-workflow menu
```

### CLI 入口点

- **主入口**：`bin/ccg.mjs` → `src/cli.ts`
- **核心命令**：
  - `init` - 初始化工作流（`src/commands/init.ts`）
  - `update` - 更新工作流（`src/commands/update.ts`）
  - `menu` - 交互式菜单（`src/commands/menu.ts`）
  - `config` - MCP 配置管理（`src/commands/config-mcp.ts`）
  - `diagnose-mcp` - MCP 诊断（`src/commands/diagnose-mcp.ts`）

### codeagent-wrapper 入口

- **主入口**：`codeagent-wrapper/main.go`
- **当前版本**：v5.10.0
- **调用语法**：
  ```bash
  codeagent-wrapper --backend <codex|gemini|claude> - [工作目录] <<'EOF'
  <任务内容>
  EOF
  ```
- 详见 [codeagent-wrapper/CLAUDE.md](./codeagent-wrapper/CLAUDE.md)

---

## 对外接口

### CLI 命令接口

| 命令 | 用途 |
|------|------|
| `npx ccg-workflow` | 一键安装/菜单 |
| `npx ccg-workflow menu` | 交互式菜单 |
| `npx ccg-workflow update` | 更新到最新版本 |
| `npx ccg-workflow diagnose-mcp` | 诊断 MCP 配置 |

### Slash Commands 接口（29 个）

**开发工作流**：
| 命令 | 用途 | 模型 |
|------|------|------|
| `/ccg:workflow` | 完整 6 阶段工作流 | Codex ∥ Gemini |
| `/ccg:plan` | 多模型协作规划（Phase 1-2） | Codex ∥ Gemini |
| `/ccg:execute` | 多模型协作执行（Phase 3-5） | Codex ∥ Gemini + Claude |
| `/ccg:codex-exec` | Codex 全权执行计划（MCP + 代码 + 测试） | Codex + 多模型审核 |
| `/ccg:context` | 项目上下文管理（.context 初始化/日志/压缩/历史） | Claude |
| `/ccg:enhance` | 内置 Prompt 增强，将模糊需求转化为结构化任务描述 | Claude |
| `/ccg:frontend` | 前端专项（快速模式） | Gemini |
| `/ccg:backend` | 后端专项（快速模式） | Codex |
| `/ccg:feat` | 智能功能开发 | 规划 → 实施 |
| `/ccg:analyze` | 技术分析（仅分析） | Codex ∥ Gemini |
| `/ccg:debug` | 问题诊断 + 修复 | Codex ∥ Gemini |
| `/ccg:optimize` | 性能优化 | Codex ∥ Gemini |
| `/ccg:test` | 测试生成 | 智能路由 |
| `/ccg:review` | 代码审查（自动 git diff） | Codex ∥ Gemini |

**项目管理**：
| 命令 | 用途 |
|------|------|
| `/ccg:init` | 初始化项目 CLAUDE.md |

**Git 工具**：
| 命令 | 用途 |
|------|------|
| `/ccg:commit` | 智能提交（conventional commit） |
| `/ccg:rollback` | 交互式回滚 |
| `/ccg:clean-branches` | 清理已合并分支 |
| `/ccg:worktree` | Worktree 管理 |

**OpenSpec (OPSX) 封装**：
| 命令 | 用途 |
|------|------|
| `/ccg:spec-init` | 初始化 OpenSpec 环境 + 验证多模型 MCP |
| `/ccg:spec-research` | 需求 → 约束集（并行探索 + OPSX 提案） |
| `/ccg:spec-plan` | 多模型分析 → 消除歧义 → 零决策可执行计划 |
| `/ccg:spec-impl` | 按规范执行 + 多模型协作 + 归档 |
| `/ccg:spec-review` | 双模型交叉审查（独立工具，随时可用） |

**Agent Teams 并行实施**（v1.7.60+，需启用 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）：
| 命令 | 用途 | 说明 |
|------|------|------|
| `/ccg:team` | **统一工作流（推荐）** | 8 阶段全流程：需求→架构→规划→开发→测试→审查→修复→集成，7 角色自动编排 |
| `/ccg:team-research` | 需求 → 约束集 | 并行探索代码库，Codex + Gemini 双模型分析 |
| `/ccg:team-plan` | 约束 → 并行计划 | 消除歧义，拆分为文件范围隔离的独立子任务 |
| `/ccg:team-exec` | 并行实施 | spawn Builder teammates（Sonnet）并行写代码 |
| `/ccg:team-review` | 双模型审查 | Codex + Gemini 交叉审查，分级处理 Critical/Warning/Info |

---

## 固定 / 可配置项

| 项目 | 默认值 | 可配置 | 说明 |
|------|--------|--------|------|
| 语言 | 中文 | ✗ | 所有模板为中文 |
| 前端模型 | Gemini | ✓ (v2.1.0+) | init Step 2/4 / 菜单 6 |
| 后端模型 | Codex | ✓ (v2.1.0+) | init Step 2/4 / 菜单 6 |
| Gemini 型号 | gemini-3.1-pro-preview | ✓ (v2.1.0+) | 选 gemini 时可配 |
| 协作模式 | smart | ✗ | 最佳实践 |
| 命令数量 | 29 个 | ✗ | 全部安装 |

---

## 关键依赖与配置

### TypeScript 依赖

**运行时依赖**：
- `cac@^6.7.14` - CLI 框架
- `inquirer@^12.9.6` - 交互式提示
- `ora@^9.0.0` - 加载动画
- `ansis@^4.1.0` - 终端颜色
- `fs-extra@^11.3.2` - 文件系统工具
- `smol-toml@^1.4.2` - TOML 解析

**开发依赖**：
- `typescript@^5.9.2`
- `unbuild@^3.6.1` - 构建工具
- `tsx@^4.20.5` - TypeScript 执行器

### Go 依赖

- Go 标准库（无外部第三方依赖）

### 配置文件

**用户配置**：
- `~/.claude/.ccg/config.toml` - CCG 主配置

**MCP 配置**：
- `~/.claude.json` - Claude Code MCP 服务配置

---

## 相关文件清单

### 核心源码

```
src/
├── cli.ts                       # CLI 入口
├── cli-setup.ts                 # 命令注册
├── index.ts                     # 模块导出
├── commands/
│   ├── init.ts                  # 初始化命令
│   ├── update.ts                # 更新命令
│   ├── menu.ts                  # 交互式菜单
│   ├── config-mcp.ts            # MCP 配置管理
│   └── diagnose-mcp.ts          # MCP 诊断
├── i18n/
│   └── index.ts                 # 国际化（v1.7.69+）
├── types/
│   ├── cli.ts                   # CLI 类型定义
│   └── index.ts                 # 类型导出
└── utils/
    ├── installer.ts             # 安装器主入口（v1.7.83 重构后）
    ├── installer-data.ts        # 安装数据流
    ├── installer-mcp.ts         # MCP 安装子模块
    ├── installer-prompt.ts      # 提示词安装子模块
    ├── installer-template.ts    # 模板安装子模块
    ├── skill-registry.ts        # Skill Registry（v2.0.0 frontmatter 驱动）
    ├── migration.ts             # 版本迁移
    ├── version.ts               # 版本检查/下载
    ├── config.ts                # 配置管理
    ├── mcp.ts                   # MCP 工具集成
    ├── platform.ts              # 平台检测
    └── __tests__/               # 单元测试
        ├── installer.test.ts
        ├── installWorkflows.test.ts
        ├── injectConfigVariables.test.ts
        ├── version.test.ts
        ├── config.test.ts
        └── platform.test.ts
```

详见 [src/CLAUDE.md](./src/CLAUDE.md)

### 模板文件

```
templates/
├── commands/                    # 29 个斜杠命令
│   ├── workflow.md              # 完整 6 阶段工作流
│   ├── plan.md                  # 多模型协作规划
│   ├── execute.md               # 多模型协作执行
│   ├── codex-exec.md            # Codex 全权执行计划
│   ├── context.md               # 项目上下文管理（.context）
│   ├── enhance.md               # 内置 Prompt 增强
│   ├── frontend.md              # 前端专项
│   ├── backend.md               # 后端专项
│   ├── feat.md                  # 智能功能开发
│   ├── analyze.md               # 技术分析
│   ├── debug.md                 # 问题诊断 + 修复
│   ├── optimize.md              # 性能优化
│   ├── test.md                  # 测试生成
│   ├── review.md                # 代码审查
│   ├── init.md                  # 初始化项目 CLAUDE.md
│   ├── commit.md                # 智能 Git 提交
│   ├── rollback.md              # 交互式回滚
│   ├── clean-branches.md        # 清理已合并分支
│   ├── worktree.md              # Worktree 管理
│   ├── spec-init.md             # 初始化 OpenSpec 环境
│   ├── spec-research.md         # 需求 → 约束集
│   ├── spec-plan.md             # 多模型分析 → 执行计划
│   ├── spec-impl.md             # 按规范执行 + 归档
│   ├── spec-review.md           # 双模型交叉审查
│   ├── team.md                  # Agent Teams 统一工作流
│   ├── team-research.md         # Agent Teams 需求→约束
│   ├── team-plan.md             # Agent Teams 规划
│   ├── team-exec.md             # Agent Teams 并行实施
│   ├── team-review.md           # Agent Teams 审查
│   └── agents/                  # 7 个子智能体
│       ├── planner.md           # 任务规划师
│       ├── ui-ux-designer.md    # UI/UX 设计师
│       ├── init-architect.md    # 初始化架构师
│       ├── get-current-datetime.md  # 日期时间获取
│       ├── team-architect.md    # 团队架构师（v1.8.3+）
│       ├── team-qa.md           # QA 工程师（v1.8.3+）
│       └── team-reviewer.md     # 代码审查员（v1.8.3+）
├── prompts/                     # 19 个专家提示词
│   ├── claude/                  # 6 个 Claude 提示词
│   │   ├── analyzer.md
│   │   ├── architect.md
│   │   ├── debugger.md
│   │   ├── optimizer.md
│   │   ├── reviewer.md
│   │   └── tester.md
│   ├── codex/                   # 6 个 Codex 提示词
│   │   ├── analyzer.md
│   │   ├── architect.md
│   │   ├── debugger.md
│   │   ├── optimizer.md
│   │   ├── reviewer.md
│   │   └── tester.md
│   └── gemini/                  # 7 个 Gemini 提示词
│       ├── analyzer.md
│       ├── architect.md
│       ├── debugger.md
│       ├── frontend.md
│       ├── optimizer.md
│       ├── reviewer.md
│       └── tester.md
├── output-styles/               # 8 种输出风格
│   ├── engineer-professional.md
│   ├── nekomata-engineer.md
│   ├── laowang-engineer.md
│   ├── ojousama-engineer.md
│   ├── abyss-cultivator.md
│   ├── abyss-concise.md
│   ├── abyss-command.md
│   └── abyss-ritual.md
├── rules/                       # 全局规则（→ ~/.claude/rules/）
│   ├── ccg-skills.md            # 质量关卡自动触发规则
│   └── ccg-skill-routing.md     # 域知识自动路由规则
└── skills/                      # 100+ 技能文件（质量关卡 + 域知识 + impeccable + 工具）
    ├── run_skill.js
    ├── SKILL.md
    ├── tools/
    │   ├── verify-security/     # 安全漏洞扫描
    │   ├── verify-quality/      # 代码质量检测
    │   ├── verify-change/       # 变更影响分析
    │   ├── verify-module/       # 模块完整性校验
    │   ├── gen-docs/            # 文档自动生成
    │   ├── override-refusal/    # /hi 反拒绝覆写器
    │   └── lib/                 # 共享工具库
    ├── domains/                 # 10 大领域知识秘典（61 文件）
    │   ├── security/            # 红队/蓝队/渗透/审计/逆向/威胁情报
    │   ├── architecture/        # API/缓存/云原生/消息队列/安全架构
    │   ├── devops/              # Git/测试/数据库/性能/可观测性/成本优化
    │   ├── ai/                  # Agent/RAG/LLM安全/Prompt工程
    │   ├── development/         # Go/Python/Rust/TS/Java/C++/Shell
    │   ├── frontend-design/     # UI美学/组件/UX + 4种设计风格
    │   ├── infrastructure/
    │   ├── mobile/
    │   ├── data-engineering/
    │   └── orchestration/
    ├── impeccable/              # 20 个 UI/UX 精打磨技能
    ├── scrapling/               # 网页抓取技能（Cloudflare/WAF 绕过）
    └── orchestration/
        └── multi-agent/
```

详见 [templates/CLAUDE.md](./templates/CLAUDE.md)

### 预编译产物

```
bin/
├── ccg.mjs                              # CLI 入口脚本
├── codeagent-wrapper-darwin-amd64       # macOS Intel
├── codeagent-wrapper-darwin-arm64       # macOS Apple Silicon
├── codeagent-wrapper-linux-amd64        # Linux x64
├── codeagent-wrapper-linux-arm64        # Linux ARM64
├── codeagent-wrapper-windows-amd64.exe  # Windows x64
└── codeagent-wrapper-windows-arm64.exe  # Windows ARM64
```

---

## 架构图

```mermaid
graph TD
    User["用户"] --> CLI["npx ccg-workflow"]
    CLI --> Init["一键安装"]

    Init --> Commands["~/.claude/commands/ccg/<br/>29 个命令"]
    Init --> Agents["~/.claude/agents/ccg/<br/>7 个子智能体"]
    Init --> Skills["~/.claude/skills/ccg/<br/>100+ 技能文件"]
    Init --> Prompts["~/.claude/.ccg/prompts/<br/>19 个专家提示词"]
    Init --> Binary["~/.claude/bin/<br/>codeagent-wrapper v5.10.0"]
    Init --> MCP["~/.claude.json<br/>MCP 配置（可选）"]

    User2["Claude Code 用户"] --> SlashCmd["/ccg:workflow<br/>/ccg:frontend<br/>..."]
    SlashCmd --> Commands

    Commands --> Wrapper["codeagent-wrapper"]
    Wrapper --> Codex["Codex CLI<br/>(后端)"]
    Wrapper --> Gemini["Gemini CLI<br/>(前端)"]

    style CLI fill:#90EE90
    style Wrapper fill:#87CEEB
```

---

## 发版规则（必须严格遵守）

每次发版必须完成以下所有步骤，缺一不可：

### 1. 更新版本号
- 编辑 `package.json` 中的 `version` 字段

### 2. 更新 CHANGELOG.md
- 在顶部添加新版本条目
- 格式：`## [x.y.z] - YYYY-MM-DD`
- 按类别分组：`✨ 新功能` / `🐛 修复` / `🔄 变更` / `🗑️ 移除`

### 3. 更新 README.md
- 更新命令表（如有新增命令）
- 更新使用说明（如有新功能）
- 更新底部版本号

### 4. 更新 CLAUDE.md
- 更新顶部 `Last Updated` 日期和版本号
- 添加变更记录条目
- 更新命令数量、接口表等受影响的章节

### 5. 构建 + 发布 + 推送

```bash
# 类型检查（必须在 build 之前通过）
pnpm typecheck

# 构建
pnpm build

# 测试
pnpm test

# 发布 npm 包
npm publish

# 提交到 Git
git add -A
git commit -m "chore: bump version to x.y.z"
git push origin main
```

### 检查清单
- [ ] package.json 版本号已更新
- [ ] CHANGELOG.md 已添加新版本条目
- [ ] README.md 已更新（命令表 + 使用说明 + 底部版本号）
- [ ] CLAUDE.md 已更新（Last Updated + 变更记录 + 受影响章节）
- [ ] **⚠ 若修改了 `codeagent-wrapper/` 下的 Go 代码，必须同步 bump 两处版本号：**
  - [ ] `codeagent-wrapper/main.go` → `version = "x.y.z"`
  - [ ] `src/utils/installer.ts` → `EXPECTED_BINARY_VERSION = 'x.y.z'`
  - 两边版本必须一致，否则用户 update 时无法触发 binary 重新下载
  - **⛔ 禁止手动 `gh release upload`！** 推送 Go 代码后 CI（`.github/workflows/build-binaries.yml`）会自动编译 + 上传 GitHub Release + 同步 Cloudflare R2 镜像。手动上传会覆盖 CI 产物且 R2 不会同步
- [ ] `pnpm typecheck` 通过（tsc --noEmit，不可跳过）
- [ ] `pnpm build` 通过
- [ ] `pnpm test` 通过
- [ ] `npm publish` 成功
- [ ] `git push origin main` 成功

---

**扫描覆盖率**: 95%+
**最后更新**: 2026-04-10
