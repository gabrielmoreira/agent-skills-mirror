# Coding Profile 架构

> 状态：active
> 更新时间：2026-06-13

## 目标架构

Coding profile 是 Agent Workbench 标准下的一个运行剖面。它拥有更强的文件、命令、补丁、测试和审阅能力，但不拥有独立 runtime。

```text
Product intent
  -> AgentRuntimeClient
  -> Desktop Host bridge / App Server JSON-RPC
  -> RuntimeCore
      -> CodingProfile resolver
      -> Provider / model slot resolver
      -> Tool inventory / policy resolver
      -> Thread / Turn / Task / Action / Event store
  -> ExecutionBackend
      -> file tool
      -> patch tool
      -> shell / test tool
      -> search / context tool
      -> MCP / browser tool
  -> RuntimeEvent stream + ReadModel
  -> AgentUI projection
  -> Coding Workbench UI
```

## 分层职责

| 层                  | 职责                                                            | 不负责                               |
| ------------------- | --------------------------------------------------------------- | ------------------------------------ |
| Product App         | 提供用户意图、项目上下文、业务 refs。                           | 写 runtime facts、拼 Provider 请求。 |
| AgentRuntimeClient  | 统一传输、订阅事件、读取 read model、响应 action。              | UI 投影和 Provider 调用。            |
| App Server          | JSON-RPC current API、Provider store、RuntimeCore owner。       | Electron 壳能力和产品页本地状态。    |
| RuntimeCore         | session/thread/turn/task/action/event truth。                   | 具体 shell/文件副作用执行。          |
| ExecutionBackend    | 文件、补丁、命令、测试、MCP、浏览器等工具执行。                 | 保存 UI 状态或解释产品文案。         |
| Policy service      | sandbox、permission、approval、network、filesystem 决策。       | 让工具绕过 action.required。         |
| AgentUI projection  | 把 facts 转为 messages/timeline/graph/tools/actions/artifacts。 | 从正文猜测执行结果。                 |
| Coding Workbench UI | 渲染预览、文件、变更、输出、日志、审批、证据。                  | 写事实、调 Provider、执行 shell。    |

## Current crate / package 落点

新增实现默认落在 current owner，不能恢复旧目录或把 compat facade 当新业务入口。

| 能力                                         | 首选落点                                                            | 说明                                                                   |
| -------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| JSON-RPC 方法、session 读写、fixture backend | `lime-rs/crates/app-server`                                         | App Server 是 coding turn 的 current API owner。                       |
| 协议结构、schema、生成客户端输入             | `lime-rs/crates/app-server-protocol` + `packages/app-server-client` | 协议改动必须同步 Rust schema、generated TS type 和 client contract。   |
| prompt / context / model turn envelope       | `lime-rs/crates/agent`                                              | 只放 coding profile 所需 envelope，不把所有逻辑塞进中心 runtime 文件。 |
| 文件 / patch / command / test 工具执行       | App Server runtime backend 子模块或独立 execution domain crate      | 文件接近 800 行先拆模块；中心文件只 dispatch。                         |
| policy / sandbox / approval                  | policy domain module + RuntimeCore action owner                     | 需要用户决策时先写 `action.required`。                                 |
| projection / conformance                     | `packages/agent-ui-contracts`、`packages/agent-runtime-projection`  | 前端只能消费 derived state。                                           |
| shared React surface                         | `packages/agent-runtime-ui` 或现有 Workspace surface adapter        | 先复用成熟工作台壳，再逐步抽 shared surface。                          |

禁止落点：

- `lime-rs/src/**` 或旧 Tauri command wrapper。
- legacy desktop facade 作为新 coding API。
- `src/lib/dev-bridge` 旧 command policy / mock fallback 作为生产主链。
- 产品页面本地 Provider key、shell runner 或 patch runner。

## CodingProfile

后续实现应把 coding 需要的运行配置显式建模为 profile，而不是散落在 prompt、前端按钮和工具白名单里。

```ts
interface CodingProfile {
  profileId: "coding";
  modelSlots: {
    base?: string;
    coding?: string;
    review?: string;
    fast?: string;
    local?: string;
  };
  toolSurface: {
    file: boolean;
    patch: boolean;
    shell: boolean;
    test: boolean;
    search: boolean;
    browser: boolean;
    mcp: boolean;
  };
  policyProfile: {
    sandbox: "read_only" | "workspace_write" | "danger_full_access";
    approval: "never" | "on_request" | "on_failure" | "untrusted";
    network: "blocked" | "allowed" | "managed";
  };
}
```

字段名可按 Lime App Server 现有协议调整，但语义必须稳定：模型槽位、工具面和权限面是三组不同事实。

## Turn 执行状态机

Coding turn 的状态机必须由 RuntimeCore 或 Runtime provider core 拥有，UI 只能投影。

```text
turn.submitted
  -> profile.resolved
  -> model_slot.resolved | provider.blocked
  -> tool_inventory.resolved
  -> plan / reasoning / model events
  -> tool/action loop
      -> action.required?
      -> file/patch/command/test/tool facts
      -> artifact/evidence refs
  -> turn.completed | turn.failed | turn.canceled
  -> snapshot.updated?
```

规则：

- 同一 session 只能有一个 active turn owner；并发输入必须 queue、steer、cancel 或结构化拒绝。
- 工具执行不能跳过 `tool.started` 或对应 coding family start event。
- action pending 时，相关工具暂停；拒绝后不能继续执行同一个副作用。
- turn 终态后不允许同 turn 继续追加执行流事件。
- `snapshot.updated` 只能修复 read model / projection，不得改写历史事实。

## 模型与 Provider

Coding 能力必须继续走 Lime 多模型主链。

| 能力        | 规则                                                                |
| ----------- | ------------------------------------------------------------------- |
| 模型选择    | 通过 Provider Store / Model Registry / profile slot 解析。          |
| 自定义端点  | 作为 Provider Store 的 provider/model entry，不写进产品页本地 key。 |
| coding 模型 | 是一个模型槽位，不等于固定供应商或固定协议。                        |
| review 模型 | 可独立槽位，用于代码审阅、测试失败解释、补丁风险总结。              |
| fast 模型   | 可用于标题、摘要、轻量分类，不接管执行主 turn。                     |
| fallback    | 必须产生 routing / provider diagnostics，不能静默改走 mock。        |

Provider readiness 至少要表达：

| 状态                  | Runtime 行为                                       | UI 行为                            |
| --------------------- | -------------------------------------------------- | ---------------------------------- |
| `ready`               | 正常发起 coding turn。                             | 只显示轻量状态。                   |
| `needs_setup`         | 不发起模型请求，返回可恢复 diagnostics 或 action。 | 提供配置入口，不伪装成模型失败。   |
| `capability_mismatch` | 可按 policy fallback，或 blocked。                 | 显示槽位能力不足和 fallback 原因。 |
| `rate_limited`        | 结构化失败或等待重试 action。                      | 显示可恢复动作和 evidence ref。    |
| `blocked`             | turn blocked / failed，不能 mock。                 | 主状态显示 blocked。               |

## 工具与执行

Coding profile 的最小工具面：

| 工具     | Runtime facts                            | UI 投影                    |
| -------- | ---------------------------------------- | -------------------------- |
| 读取文件 | `tool.started/result` + file ref         | 文件查看、上下文引用。     |
| 写入文件 | `file.changed` + artifact/checkpoint ref | 变更列表、diff、恢复入口。 |
| 应用补丁 | `patch.started/applied/failed`           | patch viewer、失败原因。   |
| 命令执行 | `command.started/output/exited`          | 输出 / 日志 tab。          |
| 测试执行 | `test.started/completed`                 | 测试结果、继续修复入口。   |
| 搜索     | `tool.result` + context refs             | 上下文来源和引用。         |
| 审批     | `action.required/resolved`               | 审批卡，不进入正文。       |
| 沙箱阻断 | `sandbox.blocked`                        | 阻断状态和可恢复动作。     |

所有副作用都必须有 stable id：`toolCallId`、`actionId`、`artifactId`、`checkpointId` 或等价 owner id。

### ExecutionBackend 子域

| 子域      | 输入                                    | 输出                                                  | 失败分类                                                                             |
| --------- | --------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `file`    | workspace root、path、mode、content/ref | `file.read`、`file.changed`、artifact/checkpoint refs | `not_found`、`outside_workspace`、`permission_denied`、`encoding_error`。            |
| `patch`   | patch text/ref、base checkpoint、policy | `patch.started/applied/failed`、diff refs             | `parse_error`、`context_mismatch`、`conflict`、`permission_denied`。                 |
| `command` | argv、cwd、env policy、timeout          | `command.started/output/exited`、output refs          | `approval_denied`、`sandbox_blocked`、`spawn_failed`、`timed_out`、`non_zero_exit`。 |
| `test`    | command ref、framework hint、timeout    | `test.started/completed`、summary/output refs         | `failed`、`canceled`、`timed_out`、`unparseable`。                                   |
| `search`  | query、roots、limits                    | `tool.result`、source refs                            | `outside_workspace`、`too_many_results`、`index_unavailable`。                       |
| `preview` | artifact/app server ref、port policy    | artifact/diagnostics refs                             | `port_blocked`、`build_failed`、`preview_unavailable`。                              |

每个子域必须先把大输出写成 ref，再把 ref 放入事件；不得把长日志、完整文件 bytes 或 secret-bearing payload 塞进 RuntimeEvent / projection。

## RuntimeEvent 合约边界

Coding facts 必须在进入 ReadModel / UI 前通过 schema gate 和 sequence gate。

| Event family               | 必需 scope                                      | 必需 payload / refs                       | 配对                                            |
| -------------------------- | ----------------------------------------------- | ----------------------------------------- | ----------------------------------------------- |
| `file.read`                | `payload.path`                                  | `contentRef` 或 file ref                  | 可独立出现。                                    |
| `file.changed`             | `artifactId` 或 `artifactRefs` + `payload.path` | `checkpointRef` / `diffRef` / preview ref | 可独立出现，但写入必须有 artifact owner。       |
| `patch.started`            | `payload.patchId` 或 `toolCallId`               | `path` 可选                               | 必须由 `patch.applied` 或 `patch.failed` 收口。 |
| `patch.failed`             | patch scope                                     | `failureCategory`，可选 `recoveryHintRef` | 关闭 active patch。                             |
| `command.started`          | `payload.commandId` 或 `toolCallId`             | `command`、`cwd`                          | 必须由 `command.exited` 收口。                  |
| `command.output`           | command scope                                   | `outputRef` 或 `refIds`                   | 只能在 active command 内出现。                  |
| `command.exited`           | command scope                                   | `exitCode` 或 status                      | 关闭 active command。                           |
| `test.started`             | `payload.testRunId` 或 `toolCallId`             | `commandId` 可选                          | 必须由 `test.completed` 收口。                  |
| `test.completed`           | test scope                                      | `result` / `status` + output refs         | 关闭 active test。                              |
| `sandbox.blocked`          | runtime / command scope                         | `reasonCode` + recovery hint              | 触发 blocked UI。                               |
| `action.required/resolved` | `actionId`                                      | controls / decision                       | 审批状态只从 action facts 派生。                |

终态 `turn.completed / turn.failed / turn.canceled` 出现后，不允许再出现同 turn 的 file/patch/command/test/tool/action/model 执行流事件。

## ReadModel / Evidence join

ReadModel 不是 UI cache，而是断流恢复和历史回放事实源。Coding read model 至少要能回答：

- 当前 active turn、active tool、active command/test/patch/action。
- 本轮 changed files、latest checkpoint、diff refs。
- command/test output refs 与 exit/test status。
- provider/profile/policy diagnostics。
- artifact/evidence refs 与 replay cursor。
- `stale` 或 repair 状态。

Evidence join 规则：

- 每个文件写入、patch 应用、命令输出、测试结果都应能关联 turn/task/tool/action ids。
- review / export 只消费 refs，不重新解析 UI 文本。
- Evidence Pack 为空时 UI 显示 unavailable，不伪造 verdict。

## 可借鉴并迁入的运行时能力

这些能力值得优先按 Lime 命名和边界重写或迁入：

- Thread / Turn / Item 生命周期。
- 输入队列与 active turn 状态机。
- 工具调用 start/progress/result/failure 配对。
- 补丁应用和 diff 归档。
- 命令执行 policy 和 approval 规则。
- sandbox / filesystem / network 权限 profile。
- 工作区上下文、项目规则和 instruction discovery。
- 大输出截断、spill ref、event projection。
- headless fixture replay 和 JSON event 输出思想。

迁入时必须落到 `lime-rs/crates/**` current owner，不能恢复旧目录或外部 crate 命名。

## 可直接迁移的实现素材

本地参考仓库中以下模块可作为实现素材，迁入时必须改为 Lime owner 和 Lime 命名：

| 参考素材                           | Lime 落点                      | 迁移方式                                              |
| ---------------------------------- | ------------------------------ | ----------------------------------------------------- |
| patch parser / streaming parser    | ExecutionBackend patch service | 可复制算法结构，输出 `patch.*` + `file.changed`。     |
| exec policy prefix / network rule  | Policy service                 | 可复制规则模型，接 Lime approval / sandbox profile。  |
| command JSONL event processor      | RuntimeEvent adapter           | 可复制事件分发思想，不复制协议名。                    |
| file search session                | search / context tool          | 可复制异步增量搜索结构，输出 source refs。            |
| sandbox policy transforms          | sandbox manager                | 按 macOS / Linux / Windows 分平台重写 owner。         |
| code-mode protocol session framing | external harness adapter       | 只用于 compat adapter，不能替代 App Server JSON-RPC。 |

迁入前必须确认许可证、依赖、平台行为和 secret redaction；迁入后必须有 Lime 侧单测。

## 参考实现迁入流程

每次复制或重写参考实现前，执行计划必须登记：

1. 来源路径和许可证。
2. Lime owner 和目标文件。
3. 是否会形成第二套 Runtime、Provider、Artifact 或 Evidence truth。
4. 重命名和 API shape 变更。
5. 平台差异：macOS / Windows / Linux。
6. secret redaction 和大输出 spill 策略。
7. 定向测试和 GUI / contract 验证入口。

只要任一项无法回答，本轮只能 reference，不能 copy。

## 不可迁入的产品壳

以下内容只能参考，不应迁入：

- 原 CLI / TUI / terminal prompt 壳。
- 原 app-server protocol 作为 Lime protocol 替代品。
- 原 home/config 目录作为 Lime 数据根。
- 原单 Provider 认证路径。
- 外部产品的品牌命名、命令名、UI 组件名。
- 任何会让 UI 绕过 RuntimeCore 的本地状态机。

## 与既有 Lime 能力关系

| Lime 现有能力                        | 分类                      | Coding 目标                                                                                 |
| ------------------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `code_orchestrated`                  | compat legacy input       | 只在单一 compat helper 中归一为 `react`；不得作为 coding profile current 入口或独立状态机。 |
| Project Shell                        | current execution surface | 接入 RuntimeEvent / policy / projection。                                                   |
| file checkpoint                      | current artifact support  | 作为 patch/file change 的 checkpoint owner。                                                |
| AgentUI sequence gate                | current guard             | 扩展覆盖 coding command/patch/test/action 配对。                                            |
| Workspace Harness 局部面板           | compat UI                 | 迁到 Coding Workbench shared surfaces。                                                     |
| Plugin runtime projection         | current consumer          | 可复用 coding task/read model，不复制执行事实。                                             |
| `CanvasWorkbenchLayout` coding mode  | compat/current UI surface | 可以保留壳和视觉，但事实解释必须来自 `CodingWorkbenchView`。                                |
| thread item / checkpoint change view | compat migration input    | 只能先 adapter 成 RuntimeEvent，不能直接驱动最终 UI。                                       |

## 旧实现清理边界

允许短期保留：

- 历史 thread item 到 RuntimeEvent 的 migration adapter。
- 旧 `code_orchestrated` 值作为历史 session / 偏好 / 旧命令包的 compat 输入，且只能归一到 `react`。
- 旧 checkpoint summary 作为 artifact/checkpoint owner 的历史数据来源。
- `CanvasWorkbenchLayout` 的视觉壳，只要事实解释来自 `CodingWorkbenchView`。

必须清退：

- React 组件内的 command/test/patch 状态机。
- 从 assistant prose 解析文件、测试结果、补丁状态、审批状态。
- Workspace/Harness 局部状态直接驱动 output/log/action/diagnostics。
- 生产 mock fallback 或 legacy command 作为 coding turn 可用性前提。

清退完成后，compat adapter 只服务历史 hydrate；新 turn 必须直接由 App Server / RuntimeCore 输出 coding events。

## 架构验收

一次 coding turn 至少能证明：

1. Provider/model 由 App Server current 主链解析。
2. 文件和命令工具执行有 RuntimeEvent。
3. 审批和沙箱阻断不进入正文状态机。
4. 变更、输出、证据能从 read model 恢复。
5. 前端刷新后可通过 hydration 恢复同一工作台状态。
6. 多模型槽位、policy、tool inventory 和 evidence refs 都可在诊断抽屉解释。
7. 不安装外部 CLI、不启用 mock fallback 时，current fixture 仍能跑通 coding 主闭环。
