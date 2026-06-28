---
name: lime-governance
description: Govern legacy cleanup and fact-source convergence. Use when Codex needs to reduce new/old coexistence, classify paths as current/compat/deprecated/dead, collapse compat or deprecated paths, centralize runtime paths or migration boundaries, add repository guardrails, or continue governance-driven subtraction instead of adding parallel implementations.
---

# 治理收口

先读取 `internal/aiprompts/governance.md`（仓库事实源）。
如果需要快速找入口，再看 `internal/aiprompts/README.md`。

如果任务涉及：

- Electron IPC / App Server / legacy adapter / Bridge / mock / 前端 API 网关：再读 `internal/aiprompts/commands.md`
- GUI 壳 / Workspace / 页面主路径：再读 `internal/aiprompts/quality-workflow.md`

如果当前任务本身是在更新治理规则，先改仓库里的 `internal/aiprompts/governance.md`，再视需要同步本 skill 的参考文件。

## Fast Path

用户问“结论 / 复核 / 是否能删 / 是否 dead”时，先用 `3-8` 行给结论和关键证据；不要自动展开成全量 inventory、文档清理或长 checklist。只有用户要求继续治理、修文档、补守卫或实现，才进入完整工作流。

目录级旧实现如果同时满足：已不在构建 / workspace manifest 中、当前工作树已物理删除或 staged delete、已有 current owner 承接、边界守卫能防回流，可直接按目录级 `dead / deleted / forbidden-to-restore` 判定；不要求逐文件证明业务语义无价值。`internal/exec-plans/**`、旧路线图和 git history 里的旧路径默认是历史 evidence，不是 current owner 残留。

## 何时使用

当任务涉及以下任一问题时，使用本 skill：

- 新旧 Hook、新旧组件、新旧命令并存
- compat / deprecated 路径长期存活
- 前端、Rust、数据、旁路系统没有收敛到同一事实源
- 需要为 legacy 路径补守卫、白名单、扫描规则
- 需要继续“做减法”，而不是新增平级实现

## Codex 工作流

### 0. 路线图任务先防跑偏

如果用户明确绑定某份路线图，或者反复强调“对齐目标 / 按顺序推进 / 继续主线”，先执行这 4 步：

1. 用一句话重述路线图主目标
2. 指出当前所在阶段和下一刀
3. 判断本轮候选动作里，哪一个最直接推进主线
4. 只有当治理减法能直接缩短这条主线时，才做删除 / 清退

不要把“仓库里还能继续收 dead surface”误判成默认优先级更高的工作。

如果本轮新增程序、目录、crate/package、命令、API 网关、类型、模块或脚本，默认不得添加 `Lime` / `lime_` / `lime-` 品牌前缀；使用领域名作为 current 事实源命名。只有历史兼容、对外品牌标识或外部生态固定名才允许例外，并写明退出条件。

如果本轮新增 AI Agent、runtime、host integration 或跨 App 复用能力，事实源默认是 App Server JSON-RPC current 主链；`agent_runtime_*` / Aster legacy adapter 只允许作为 Desktop 兼容适配层，不得继续承接新业务逻辑。

生产不能 mock，只有测试才 mock。如果生产入口需要靠 `defaultMocks`、`mockPriorityCommands`、`invokeMockOnly`、renderer mock fallback 或 App Server mock backend 才能跑通，该入口应判为 current 主链阻塞缺口，而不是可交付降级。

前端 `src/lib/dev-bridge/**` 必须按职责分类治理：`safeInvoke` / `http-client` / `app_server_handle_json_lines` 是 current renderer bridge；旧命令 truth / no-mock policy 是迁移期 `compat / deprecated`；已迁命令名是 `dead`，只能保留在负向测试、retired guard 或显式 fixture 中。不要把清旧命令误做成整目录删除；删不动且跨命令组长期存在的 legacy policy / mock residual 必须回挂 `internal/exec-plans/tech-debt-tracker.md` 的 `CCD-012`，不能只留在聊天、handoff 或临时计划里。

如果本轮涉及 Electron packaging / installer / signing / notarization / updater metadata，事实源只能继续向 `forge.config.mjs`、`electron-forge package`、`electron-forge make` 与 Forge 官方 maker 收敛。旧 builder 配置 / CLI、自定义 Windows installer maker 与旧 YAML / blockmap updater metadata 按 `dead` 处理；发现它们出现在 current 文档、CI、质量任务、i18n evidence 或守卫中，默认先判为旧路回流。运行时更新以 `electron/updateHost.ts` + Electron 内置 `autoUpdater` 为 current；Windows installer 必须走 Forge Squirrel。

如果本轮新增或治理仓库脚本，`scripts/` 根目录和一级领域目录默认视为冻结治理边界。新增可执行脚本必须优先放到已有 `scripts/<domain>/`、`scripts/lib/` 或所属 package；只有公开稳定入口且无法归入已有领域子目录时才允许根目录或新领域目录例外，并同步 `scripts/README.md`、`scripts/script-root-governance-baseline.json` 和执行计划退出条件。`scripts/**/__pycache__/` 与 `*.pyc` 只允许作为本地缓存提示，不能进入发布候选。相关验证至少运行 `npm run governance:scripts`。

如果用户已明确“上一版无人使用 / 不用兼容 / 旧实现阻碍主线”，额外遵守：

1. 优先把旧实现判成 `dead` 或带退出条件的 `deprecated`
2. 不要为了减少 diff 再补 compat 包装层
3. `legacy current reference` 只当历史锚点，不当续命许可

### 1. 先盘点，再修改

优先用 `rg` 盘点同一能力在 4 层中的分布：

- 入口层：页面、组件、Hook、前端 API
- 服务层：命令、Service、Workflow、事件入口
- 存储层：表、DAO、Repository、缓存、迁移
- 旁路层：统计、记忆、搜索、审计、报表、任务系统

不要在盘点前直接开始“顺手统一”。

### 2. 定义事实源并分类

先写出一句事实源声明，例如：

`后续新增服务化能力只允许向 App Server JSON-RPC + RuntimeCore + ExecutionBackend 收敛；agent_runtime_* 仅作为 Desktop 兼容适配入口。`

然后把实际路径标记为：

- `current`
- `compat`
- `deprecated`
- `dead`

如果脚本给出了 `dead-candidate`，把它当成删除候选信号，而不是最终分类。

如果无法明确唯一事实源，不要继续扩展功能。

### 3. 优先做减法

默认优先执行这些动作，而不是新增抽象：

- 把散落逻辑收回单一边界
- 把 legacy 判断收回 `Repository` / `Database` / `app_paths`
- 让 compat 层只做委托和适配
- 删除零引用入口
- 把运行时 fallback 改成启动期迁移或边界短路

除非用户明确要求保留兼容，否则不要新增新的 compat 层。

但如果当前任务是路线图主线推进，**“优先做减法”不高于“优先完成主链项”**。治理减法只能服务主链，不能替代主链。

如果当前主线已经被旧实现卡住，而用户又明确不需要兼容，默认动作应是：

- 删除旧入口
- 下线旧命名
- 清理旧文档与旧协议

而不是把旧实现继续平移成“临时 compat”。

### 4. 主链路和旁路一起治理

不要只看页面、Hook、主命令。每次都检查：

- 前端入口是否唯一
- 命令 / service 是否唯一
- 数据事实源是否唯一
- 旁路系统是否还在读旧表、旧目录、旧命令

如果只改主链路，不改旁路，说明治理还没完成。

### 5. 用仓库守卫封住老路

优先使用仓库已有脚本和规则，而不是假设外部 harness、reviewer 或 CI 已存在。

如果仓库有治理扫描脚本，先运行它；当前 Lime 仓库优先：

```bash
npm run governance:legacy-report
npm run test:contracts
```

常见守卫动作：

- 为旧入口、旧命令、旧路径增加扫描规则
- 为 compat / deprecated 边界限制允许引用路径
- 为重复样板或旧调用增加计数检测

如果改动触及命令边界，不要只看单侧调用。至少一起检查：

- 前端 `safeInvoke(...)` / `invoke(...)` 命令集合
- Electron Desktop Host bridge / preload 白名单与 App Server JSON-RPC protocol
- legacy desktop facade 注册集合，仅在触碰兼容层时检查
- `agentCommandCatalog` 中的 `deprecated` 命令与 `runtimeGatewayCommands`
- `mockPriorityCommands` 与 `src/lib/desktop-host/` / legacy `defaultMocks` 是否同步
- mock 是否只停留在测试夹具 / 契约守卫；生产入口不得把 mock 当 fallback

如果改动明显是 GUI 主路径风险，而不是纯代码收口，再补：

```bash
npm run verify:local
npm run verify:gui-smoke
```

### 6. 做最贴边界的验证

优先运行与改动边界最近的检查，不要无差别全量重跑。

至少包含：

- 治理扫描脚本
- 与改动相关的定向测试或检查

如果改动涉及 Electron IPC、App Server JSON-RPC、legacy adapter、bridge、mock、前端 API 网关，默认把 `npm run test:contracts` 也纳入最小验证集合。

## Codex 约束

- 不要假设存在外部 harness、GitHub reviewer、自动 hook 或 sub-agent。
- 如果仓库已经有 reviewer、hook 或额外 agent，只把它们当成执行器，不要把它们当成新的治理定义者。
- 治理标准始终以仓库内 `internal/aiprompts/governance.md` 为准；本 skill 只是帮助 Codex 执行。
- 汇报时必须回到 `current` / `compat` / `deprecated` / `dead` 这套分类语言。
- `dead-candidate` 只能作为辅助信号汇报，不能直接替代 `dead` 结论。

## 输出要求

汇报结果时，始终给出：

1. 本次收掉了哪些 surface
2. 当前改动分别属于 `current` / `compat` / `deprecated` / `dead` 中哪一类
3. 补了哪些守卫和验证
4. 剩余最值得继续优化的一刀是什么

如果任务来自路线图，再额外补一行：

- 这一步与路线图主目标的关系是什么；下一步应回到哪条主链继续推进

如果本次无法完成彻底收口，明确说明还差哪条旁路或哪条旧入口没有迁完。
如果仍保留延期白名单或临时例外，必须说明具体命令、当前原因和退出条件。
