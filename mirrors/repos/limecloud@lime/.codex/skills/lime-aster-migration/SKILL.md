---
name: lime-aster-migration
description: Migrate or delete Aster/runtime/tool/session/provider surfaces under Lime's Codex-first architecture and guardrails.
---

# Aster 迁移

先读取 `internal/aiprompts/governance.md`，再读取 `internal/roadmap/astermigration/README.md` 和当前执行计划。若任务影响 refactor v1，同时读取 `internal/roadmap/astermigration/refactor-v1-impact-audit.md` 与 `internal/research/refactor/v1/README.md`。

## 判定口径

一句话：**Codex 有则迁，Codex 没有则删。**

- 对照 `/Users/coso/Documents/dev/rust/codex` 的 current 工具面、runtime crate 分层、Thread / Turn / Item 归属和命名。
- Codex 有的能力必须迁入 Lime current owner，并让 App Server、前端 GUI、Evidence / replay / analysis 或运行时主链至少一条真实消费链用起来。
- Codex 没有的 Aster-only 能力默认 `dead / deleted / forbidden-to-restore`，同步删除 vendor 实现、catalog alias、前端 normalization/display/summary、测试正向断言和 active checklist。
- `agent-compat` 只能作为待迁出 staging / compat blocker；它不是 current owner，也不能作为迁移完成证据。仍被生产 `use aster::...` 命中的文件必须继续迁到 `agent-runtime`、`agent-protocol`、`model-provider`、`tool-runtime`、`thread-store`、`lime-mcp`、`lime-skills`、`media-runtime` 或 App Server；Codex 无对应能力时直接删除。`agent-compat` 现存指向 Lime current owner 的依赖只允许作为 burn-down allowlist，禁止新增 owner 依赖来给旧 reply loop / provider / tool / session 续命。
- 同名不同义按 Codex 语义重建。例如 Codex `clock.sleep` / `sleep` 不是 Aster `SleepTool`。
- 文件写入 / 编辑要单独判定：Codex 有文件修改能力，模型侧 current 入口是 `apply_patch`，App Server / exec-server 还有受控 `write_file` / `fs_write_file` API；删除范围只限 Aster `WriteTool` / `EditTool` / `write_file` / `edit_file` 旧模型工具面，不能删除 Lime current Artifact / workspace 写入链。

## 命名规则

- 优先短、领域化、可读，贴近 Codex 工具名：`apply_patch`、`web_search`、`tool_search`、`view_image`、`update_plan`、`request_user_input`。
- Aster 的简洁命名可以作为品味参考，但 Aster 不能作为 current 实现事实源。
- 不把 `lime_*`、`aster_*`、`agent_runtime_*` 或冗长历史词带进 current API。
- `Tool` / `*Tool` 后缀只允许留在历史 alias、测试夹具或迁移期 adapter 内；current 工具/API 优先使用 Codex 风格短领域名。
- 只有对外品牌、历史兼容或第三方生态固定名允许保留品牌前缀，并在计划里写明原因和退出条件。

## 工作流

1. 先盘点 Codex 是否有对应能力。用 `rg` 查 Codex 的 `codex-rs/tools/src`、`codex-rs/core/src/tools`、App Server protocol schema 和相关 handlers。
2. 给能力分类：`codex-current`、`codex-current-different-semantics`、`aster-only-dead`、`compat-blocker`、`valuable-reference-only`。
3. 选择 current owner：`tool-runtime`、`agent-runtime`、`agent-protocol`、`model-provider`、`thread-store` 或 App Server JSON-RPC。不要默认塞进 `lime-core`、`services` 或 `agent-compat`。
4. Codex 有的能力先做可用骨架，再接入真实消费链；只搬 DTO、只留 wrapper、只写文档不算迁移完成。
5. Codex 没有的 Aster-only 能力直接删除旧实现和旧展示，补 forbidden-to-restore 守卫。
6. 更新 `internal/roadmap/astermigration/aster-capability-intake-execution-plan.md` 的进度日志和退出条件；影响 refactor v1 时同步 `refactor-v1-impact-audit.md`。
7. 运行贴边验证：Rust 定向测试 / `cargo check`、`src/lib/governance/asterMigrationBoundary.test.ts`、相关前端 display / normalization 测试。

## 必查清单

- Rust：vendor 实现、Lime current owner、Aster compat adapter、Cargo dependency。
- 前端：tool catalog、normalization、display config、process summary、copy/i18n、GUI evidence/read model。
- 守卫：deleted file list、forbidden imports、catalog alias 禁止、frontend exact config 禁止。
- 文档：迁移计划、refactor v1 影响、验证结果、剩余 blocker、整体完成度。

## 输出要求

汇报必须包含：

- `current`：本轮迁入并被真实主链消费的能力。
- `dead`：本轮删除或禁止恢复的 Aster-only 能力。
- `compat / deprecated`：仍存在的最小退场边界和退出条件。
- 验证命令与结果。
- 本轮完成度和整体目标完成度。
