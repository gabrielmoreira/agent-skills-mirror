---
name: lime-quality-workflow
description: Choose Lime validation commands for GUI, command/bridge, config, version, and PR-readiness changes.
---

# Lime 工程质量

先读取 `internal/aiprompts/quality-workflow.md`（仓库事实源）。
如果需要快速找入口，再看 `internal/aiprompts/README.md`。

如果任务涉及：

- Electron IPC / App Server / legacy desktop facade / Bridge / mock / 前端 API 网关：再读 `internal/aiprompts/commands.md`
- 新旧并存、兼容层收口、旧入口回流：再读 `internal/aiprompts/governance.md`
- GUI 续测、页面交互验证：再读 `internal/aiprompts/playwright-e2e.md`

如果当前任务本身是在更新工程质量规则，先改仓库里的 `internal/aiprompts/quality-workflow.md`，再视需要同步本 skill 的参考文件。

## Fast Path

用户问“结论 / 复核 / 是否能删 / 是否 dead”时，先用 `3-8` 行给结论和关键证据；不要自动升级成 `verify:local`、`test:contracts`、GUI smoke 或全量质量矩阵。只有用户要求继续实现、修文档、补守卫、提交前验证，或改动已经真实触达 GUI / 命令 / bridge / 配置边界时，才进入完整质量工作流。

目录级旧实现若已脱离构建 / workspace manifest、当前工作树已物理删除或 staged delete、已有 current owner 承接，且边界守卫能防回流，可直接按目录级 `dead / deleted / forbidden-to-restore` 判定；不要求逐文件证明业务语义无价值。`internal/exec-plans/**`、旧路线图和 git history 里的旧路径默认是历史 evidence，不是当前质量缺口。

## 何时使用

当任务涉及以下任一问题时，使用本 skill：

- 不确定这次改动最少该跑哪些校验
- 改了 GUI 壳、DevBridge、Workspace、前端主路径
- 改了 Electron IPC、App Server JSON-RPC、legacy desktop facade、Bridge、mock、`safeInvoke` / `invoke`
- 改了配置结构、版本文件、依赖或发布相关边界
- 需要判断“代码通过检查”是否已经等于“可以交付”

## Codex 工作流

### 0. 路线图任务先校准目标

如果用户明确要求对齐路线图主线，先在脑内完成这三个判断，再决定跑什么校验：

1. 本轮改动对应路线图哪一节
2. 它推进的是主链，还是只是从属清理
3. 本轮最低门槛校验是否能证明这一步真的在向目标收敛

如果答案只是“代码没报错”，但无法证明主线前进了，就要先纠偏，再谈校验。

如果当前改动只是让已经过时、且明确无需兼容的旧实现继续通过校验，不要把这轮验证当成有效进展；应先回到主线，删除或下线旧实现后再验证 current 路径。

校验前同时检查新增命名：新程序、目录、crate/package、命令、API 网关、类型、模块和脚本默认不得添加 `Lime` / `lime_` / `lime-` 品牌前缀；除非属于历史兼容、对外品牌标识或外部生态固定名，并已在计划中说明。

如果新增的是 AI Agent / runtime / host integration / 跨 App 复用能力，质量检查还必须确认它走 App Server JSON-RPC current 主链；Electron 只能作为 Desktop Host bridge；`agent_runtime_*` / Aster legacy facade 只能作为 Desktop 兼容适配层，不能成为新业务逻辑事实源。

质量检查还必须确认生产路径没有 mock fallback。`safeInvoke` / `invoke`、Electron Host、App Server sidecar、GUI smoke 和业务 E2E 不能回退 `mockPriorityCommands`、`defaultMocks`、`invokeMockOnly`、renderer mock fallback 或 mock backend；这些只允许测试夹具显式使用。

如果本轮涉及 Agent Runtime / Claw chat 主路径、历史恢复、流式事件、工具终态、消息列表完成态、代码产物工作台或 Plugin task read model，进入 GUI smoke / Playwright 前先跑 `npm run smoke:agent-runtime-current-fixture`。该入口必须保持非 live Provider、非 App Server mock backend、非 renderer mock fallback，只作为 current fixture 回归门槛，不替代真实 Electron / Playwright 闭环。修 streaming 卡住、无法停止、输入框不可用、用户消息 / assistant 输出不可见时，terminal 回归必须覆盖 App Server current `turn.completed` 投影后的 `turn_completed`，不能靠固定 timeout / grace timer 合成 `final_done`。若问题直接涉及历史详情 hydrate、最近对话恢复或归档 / 反归档后的 read model 读取，聚合 guard 通过后再显式跑 `npm run smoke:agent-session-history-electron-fixture`；该入口启动真实 Electron，但使用 `APP_SERVER_BACKEND_MODE=unavailable`，不调用模型后端。若问题直接涉及代码产物、artifact snapshot、从历史打开工作台或工作台面板渲染，聚合 guard 通过后再显式跑 `npm run smoke:code-artifact-workbench-electron-fixture`；该入口启动真实 Electron 并使用 external fixture backend，不调用正式模型。若问题直接涉及 Claw 输入框不可见、用户输入不显示、assistant 输出卡住、自然语言新闻请求或 `agentSession/turn/start` GUI 链路，聚合 guard 通过后再显式跑 `npm run smoke:claw-chat-current-fixture`；该入口启动真实 Electron 但仍使用 external fixture backend，不调用正式模型，且应覆盖 `message.delta + turn.completed` 单终态完成态，不要求 `turn.final_done`。

如果涉及 Electron packaging / installer / signing / notarization / updater metadata，质量检查必须确认 current 事实源是 `forge.config.mjs`、`electron-forge package`、`electron-forge make` 与 Forge 官方 maker；旧 builder 配置 / CLI、自定义 Windows installer maker 与旧 YAML / blockmap updater metadata 按 `dead` 处理，不得继续作为文档、CI、质量任务、i18n evidence 或守卫输入。运行时更新以 `electron/updateHost.ts` + Electron 内置 `autoUpdater` 为 current；Windows installer 必须走 Forge Squirrel。

如果涉及新增脚本或 `scripts/` 目录治理，质量检查必须确认 `scripts/` 根目录和一级领域目录没有继续膨胀。新增可执行脚本默认进入已有 `scripts/<domain>/`、`scripts/lib/` 或所属 package；根目录或新领域目录例外必须同步 `scripts/README.md`、`scripts/script-root-governance-baseline.json` 和执行计划。最低校验包含 `npm run governance:scripts`。

如果本轮要继续前端全量 Vitest，先检查 `.lime/test/vitest-smart-last-run.json`。已有失败、中断、running 或 pending 批次时，默认用 `npm run test:resume`，或用 `npm test -- --from-batch <N>` / `npm test -- --only-batch <N>` 精确补批次；不要无理由从第 1 批重跑。局部源码改动优先用 `npm run test:related -- <files>` 或 `npm run test:changed -- <ref>` 缩小反馈环，再按发布 / GUI 风险决定是否扩大验证。CI 横向压缩前端全量时可用 Vitest `--shard=<index>/<count>` 做分片；本地失败续跑仍以 `.lime/test/` 状态为准。

### 1. 先判断改动类型

先把当前改动归到最接近的一类：

- 普通前端改动
- Electron IPC / App Server / legacy desktop facade / Bridge / mock 改动
- GUI 壳 / Workspace / 页面主路径改动
- 配置结构改动
- 版本相关改动
- Rust 模块改动
- 需要真实交互验证的 GUI 改动

如果改动同时落在多类，按最高风险边界组合校验，不要只跑最轻的一层。

### 2. 先跑最贴边界的最低门槛

默认参考仓库里的最低门槛矩阵：

- 普通前端改动：`npm run verify:local`
- Electron IPC / App Server / legacy desktop facade / Bridge / mock 改动：`npm run verify:local` + `npm run test:contracts`
- GUI 壳 / Workspace / 页面主路径改动：`npm run verify:local` + `npm run verify:gui-smoke`
- Agent Runtime / Claw chat 主路径改动：先跑 `npm run smoke:agent-runtime-current-fixture`，再按 GUI / bridge 风险补 `verify:gui-smoke`、`test:contracts` 或 Playwright
- 配置结构改动：`npm run verify:local`
- 版本相关改动：`npm run verify:app-version`
- Rust 模块改动：先跑受影响 crate / 模块定向测试，再决定是否全量 `cargo test`
- 真实交互验证：先跑 `npm run verify:gui-smoke`，再进入 Playwright MCP

### 3. GUI 产品不要只看“代码通过”

如果改动影响 GUI 壳、Bridge、Workspace、主页面路径，不要把以下结果当成交付结论：

- `lint` 通过
- `typecheck` 通过
- 前端单测通过
- Rust 单测通过

至少还要确认：

- `DevBridge` 已就绪
- 默认 workspace 准备态可用
- 最小 GUI smoke 已跑通或明确说明为什么当前环境不能跑

### 4. 边界类改动必须成组检查

如果改动涉及命令、桥接、配置、版本或依赖，至少检查这些成组事项有没有同步：

- 命令边界：前端调用、Electron host / preload、App Server protocol / client、legacy Rust 注册、治理目录册、mock 集合
- 配置结构：schema、校验器、消费者、文档
- 版本相关：`package.json`、Electron 配置、`lime-rs/Cargo.toml`、App Server manifest
- 依赖相关：`package-lock.json`、`lime-rs/Cargo.lock`

Electron packaging / release 相关改动还必须成组检查：`forge.config.mjs`、`electron/forge/*`、`package.json` / `package-lock.json`、release workflows、`scripts/run-electron-package-dir.mjs`、`scripts/stage-electron-release-assets.mjs`、`scripts/verify-electron-package-resources.mjs`、entrypoint/docs guards、contract guard 和 `internal/roadmap/appserver/release-updater.md`。

脚本目录治理相关改动还必须成组检查：`scripts/README.md`、`scripts/script-root-governance-baseline.json`、`scripts/check-scripts-governance.mjs`、`scripts/lib/scripts-governance-core.mjs` 与 `package.json#scripts`，并运行 `npm run governance:scripts`。

不要只改实现，不补文档或锁文件。

### 5. UI 改动必须补稳定回归

如果改动是用户可见 UI：

- 优先补 `*.test.tsx` 里的关键文案、状态、交互断言
- 如果目标区域已有 snapshot 或结构化快照机制，沿用现有机制
- 不要因为“只是 UI 细节”就跳过回归

新增或重写前端逻辑时，先判断测试分层：

- 筛选、分组、formatter、request builder、runtime 参数投影、状态机、reducer 等可纯化逻辑，必须优先抽到 View Model / projection / selector / helper，并用 `*.unit.test.ts` 覆盖。
- `*.test.tsx` / component 测试只保留 React 渲染、真实 DOM 事件、hook 生命周期和少量关键接线回归；不要把大量业务分支继续塞进挂载测试。
- 如果暂时无法抽成纯单元，必须在路线图或执行计划写明原因、风险层级和退出条件，避免后续 Agent 把临时组件测试当成新规范。
- 跑 `npm run test:layers:stats` 时关注 `Component unit-migration candidates`，把它作为后续抽 VM 的候选名单，而不是当前失败门禁。

### 6. 本地入口与 CI 口径保持一致

优先使用仓库已有统一入口，而不是手工拼临时命令：

```bash
npm run verify:local
npm run verify:local:full
```

如果需要解释为什么 CI 触发某个检查，回到：

- `.github/workflows/quality.yml`
- `scripts/quality-task-planner.mjs`
- `scripts/quality-task-selector.mjs`
- `scripts/local-ci.mjs`

不要在汇报里发明一套独立于仓库实际脚本之外的“建议流程”。

### 7. 交付结论必须明确

汇报时不要只说“我跑了测试”。

必须明确说明：

- 本次改动属于哪类风险
- 实际跑了哪些最低门槛命令
- 哪些命令因环境限制没跑，限制是什么
- GUI 主路径是否已验证
- 还差哪一步才算可交付

## Codex 约束

- Lime 是 GUI 桌面产品，不要把“静态检查通过”等同于“产品可交付”。
- 优先使用仓库已有脚本，不要临时发明平级校验脚本。
- 命令 / Bridge / mock 改动，默认把 `npm run test:contracts` 纳入最小验证集合。
- 生产路径如果靠 mock 才通过，不得标为可交付；只能记录为 current 主链阻塞缺口。
- GUI 壳 / Workspace / 主路径改动，默认把 `npm run verify:gui-smoke` 纳入最小验证集合。
- Rust 校验默认先小后大，不要一上来无差别全量 `cargo test`。优先用 `npm run test:rust:changed`、`npm run test:rust:related -- <paths...>`、`npm run test:rust:unit -- -p <crate> <filter>`、`npm run test:rust:integration -- -p <crate> --test <target>` 收缩范围；`changed/related` 会按 `lime-rs` 路径推导 workspace crate 并用 `cargo metadata` 扩展反向依赖，workspace manifest / lockfile 边界自动扩大到 `--workspace`，无法映射 crate 时 fail closed；冷编译慢时优先复用 `lime-rs/target`、增量缓存和可选 `RUSTC_WRAPPER=sccache`，只有工具链和 CI 已配置后才把 `cargo nextest run` 作为默认门禁。
- `verify:local` 的 smart 模式遇到 Rust 路径改动应走 `test:rust:changed`，`--staged` 走 `test:rust:related -- <staged-rust-paths>`；`--full`、无改动兜底和 workflow 全局风险才保留 workspace 全量 `cargo test`。
- 如果因为环境限制无法完成 GUI smoke 或交互验证，必须在结果里明确写出来，不能假装已经验证。
- 过时实现即使校验通过，也不等于 current 路线图可交付；对已判 `dead` / `deprecated` 且明确无需兼容的路径，不要为了“测过”继续保留。

## 输出要求

汇报结果时，始终给出：

1. 本次改动属于哪类风险
2. 实际执行了哪些校验
3. 哪些校验因为环境限制未执行
4. 当前是否达到 Lime 的可交付门槛
5. 如果还未达到，下一步最该补哪一项

如果任务来自路线图，再额外说明：

6. 这轮校验证明了哪条路线图主线在前进，而不是只证明局部代码可运行
