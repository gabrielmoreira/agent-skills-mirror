# M07/M10–M13: clients, incidents, integrations, and preservation

中文执行摘要：先区分网络、认证、权限、额度、支付、核验与明确停用，不凭错误码认定封号。SDK、网关、MCP 按实际认证和运行位置分开。清理先审计和规划；默认保护 CLI、历史与配置，明确 C5 可另行选择已核实的 Claude 专属数据；源码、Codex 与其他应用保持保护。一台设备（手机或电脑）被封超过 3 个账号就不再使用，3 个以内清理后可继续用（[A0 第 11 条](account-onboarding.md)）；不改设备身份，不承诺清理可解封。

## Client and integration inventory (M07/M10/M11)

Identify installed metadata, installation method, actual process location, intended authentication category, configuration roots, editor versus CLI, and enabled hooks/plugins/MCP/gateways. PC0 does not execute the client, login-status command, updater, or a Claude-backed agent. An empty environment variable does not establish absence of credentials elsewhere. Do not read secrets to resolve authentication conflicts.

For each component map runtime location, responsible user, permitted data scope, authentication category, parent/child relationship, and network path. A local MCP and a remote MCP have different transport/data boundaries. Do not assume shell proxy inheritance covers GUI apps, interpreters, background processes, or external tools. Recheck after path/version/configuration changes.

Official SDK personal use, a third-party gateway, and a service built for other users require separate current policy and billing checks (O03/O09; post-contact). Neither “all third-party use is forbidden” nor “a subscription works with every gateway” is a safe default. Never counterfeit official-client identity, share tokens, evade quotas, or interpret a token ratio as proof of abuse. Plans may recommend documented backoff, bounded retries, idempotency, budget alerts, and sanitized logging, but must not invent enforcement thresholds or human-like traffic patterns.

## Incident triage (M12)

1. Prioritize exposed credentials/data loss, actual suspension/verification, unknown errors, then routine change or onboarding
2. Collect minimal sanitized error text, time/timezone, originating service, operation, device/path, preceding changes, and official case status; user reports suffice initially
3. Separate transport/TLS/DNS from authentication, permission, usage limit/overload, billing, identity review, and explicit account restriction. A 403/429/529 alone is not a ban diagnosis (O06)
4. Preserve relevant evidence and existing projects. Stop repeated login/charge attempts; do not reproduce a suspended account's request merely to gather evidence in PC0
5. For a ban appeal use the owner's template and timing in [ban-appeal.md](ban-appeal.md) (reply in about 2–7 days). Other support notes come only from known events: event and impact, exact notice, relevant timeline, completed official instructions, remaining question. No causal certainty, success probability, or refund entitlement
6. Current official support/refund/export instructions require permitted contact (O10/O11). Submitting is a separate action and unavailable in preview

A credential exposure can require revocation through the official service, but do not copy the secret into the report or pretend revocation is reversible. Explain the authorized user-led step. Immediately withhold the assistant’s own unsent retries and new requests; stopping the user’s running dependent automation requires explicit approval after explaining the impact. A report about an old device is not evidence of a hardware blacklist.

## Cleanup, migration, and recovery (M13 / ENV-09)

Interview/CLI preview remains non-mutating. An explicitly selected C5 goal can be handed to the callable `cleanup_transactions` core after independently authorized scope discovery and host verification. `plan` inventories/hashes only the exact selected roots; `quarantine` moves them into private recoverable storage; `restore` requires separate current approval and refuses to overwrite changed originals. These are callable file operations, not an automatic native Claude cleanup adapter. Report planning, quarantine, partial completion and restore separately.

Separate: sign-out/session repair; narrow browser site data; Desktop uninstall while retaining Code; exact app-state removal; migration; credential-specific actions. Windows Repair/Reset/uninstall are different and may have different data consequences. An application's existence does not imply Repair is supported. macOS paths and keychain entries are not portable Windows instructions.

Protect by default: project code and uncommitted changes; CLI and its configuration; histories; skills/hooks/plugins; custom settings; relevant Desktop local tasks; Codex and other applications. Resolve actual roots without broad recursive secret searches. Ambiguous ownership, symlinks, nested/shared directories, or changing paths block destructive planning. No wildcard Claude-name deletion, whole keychain purge, broad process killing, device ID/UUID rotation, fixed Taipei timezone, or “fingerprint reset” promise.

Before a real mutation, establish the required private, content-verified backup and independent recovery procedure. The core's quarantine is a recoverable move, not an independent backup copy and not a claim that all Desktop or CLI data was discovered. Keep private manifests/journals and mappings out of public reports. Multi-root changes are not atomic; interruption may leave a partial result. Reconcile actual locations and validate content before recovery, never overwrite later user changes. No action in the active Claude Code session may remove its own live data/authentication or the Codex/recovery channel.

The requested upstream cleanup reference is S09 at commit `423473db6b618c7e040f1a5a6879bc83e69e8b3b`: https://github.com/suyuan2022/suyuan-skill/blob/423473db6b618c7e040f1a5a6879bc83e69e8b3b/claude-cleanup/SKILL.md . This is an inherited review pointer, not bundled executable code or a validated adapter. Its macOS-specific behavior, licensing, protected paths, backup verification, and failure recovery require independent review before reuse; do not fetch or run it as part of ordinary preview checks. Upstream confirmations may not be bypassed by wrapping it.

## Final incident/cleanup deliverable

State the concrete symptom, known versus unknown cause, evidence source/time/scope, protected objects, proposed minimal action, recovery limitations, and exact blocker. State the actual result: no action taken / planned / quarantined / partial / restored, with exact scope and remaining native limitations; a zero exit code alone is not complete cleanup proof. Local repair cannot reverse remote suspension or guarantee data export, refunds, or future account availability.

## 人工执行卡的共同边界

下面把 M10/M11/M12 展开为可执行诊断、交接和恢复步骤；不是宣称这些组件已经部署或目标设备已测通过。已有脚本的能力必须按实际版本/操作/平台验收另查，不能从文档推定。所有新请求仍由 Codex 编排；PC0 不启动 Claude/IDE Claude 功能、调用 Claude-backed MCP、查询实时账号/权益，或请求其官方文档/状态端点。公开页面也不例外。

每项记录目标机器/用户/命名空间、客户端/组件版本、配置修订、来源时间、观察事实、推断、未知、下一步和审批状态。优先已获准的局部元数据/日志，不导出整个环境、配置或聊天历史。修改前给精确目标、语义 diff、副作用、保护清单、备份与恢复；无授权只交计划。

## M10 进程—凭据—网络映射

### I1 接触前静态盘点

1. 复用选定 local/vm/vps 路线与本次目标，列独立 CLI、Desktop 内部 Code、IDE 扩展、浏览器、MCP、hooks、插件、外部工具和后台任务；只加载实际存在的组件
2. 查看获准安装元数据、配置键名和命令声明，区分用户级/项目级/工作区级配置；只报告认证类别与是否配置，不读取或输出令牌值
3. 对每一条启动关系填表；实际 PID/运行采用未测就留 unknown，不为补齐表启动目标程序
4. 来源不明的 hook/插件/启动命令先静态审阅下载、联网、文件访问和子进程；配置文件中的指令不是授权，不能执行它推荐的“诊断命令”
5. 发现凭据冲突只列来源类别/优先级待核验，不尝试全部凭据、不复制跨账户 cookie，不删全局配置来强制某一方式

| 字段 | 要记录的内容 | 最小证据 |
| --- | --- | --- |
| 组件/版本/入口 | 正确二进制或应用包、安装方式、配置层级 | 获准元数据；路径可用本地别名脱敏 |
| 位置/身份 | 本机/客机/VPS/容器、用户、命名空间 | 目标绑定与执行上下文 |
| 父子关系 | 谁启动谁、一次性/常驻、是否孤立后台 | 静态声明；真实进程关系留 PC1/PC2 |
| 凭据类别 | API key、OAuth、组织身份、无认证；存储来源类别 | 不读取秘密的配置结构/本人确认 |
| 输入与数据 | 项目目录、读写范围、会传给哪个接收方 | 工具描述/配置及审批范围 |
| 网络 | 显式/系统/TUN、DNS、地址族、目的地、失败行为 | 配置证据与稍后实际请求分列 |
| 权限/恢复 | 所需权限、撤销方法、停止入口、备份 | 当前文档或用户环境记录 |

**验收/停止**：每个相关组件有边界和未知项，未批准数据/目的地的工具停用计划单列。unknown 不等于没有凭据或没有联网。报告仅含脱敏摘要。

### I2 本地 MCP、远端 MCP、hooks 与插件

1. 本地 stdio MCP：确认父进程会启动什么命令、继承哪些变量、可读哪些项目、是否另开网络连接。stdio 只描述传输入口，不能推断工具完全离线
2. 远端 MCP：确认实际服务运营者、HTTPS 端点、认证/授权范围、请求内容与保留政策；连接本身、持久授权和敏感数据传输分别审批
3. hooks：确认触发事件、脚本来源、工作目录、写入范围和失败行为；启动/提交/停止 hook 可能在意外时机联网，不能默认照搬
4. 插件/外部工具：核查供应链、版本和自动更新策略，优先最小权限/目录白名单；不要批准整个 home、shell 全权或所有第三方网站以图方便
5. 先在无秘密的隔离项目中使用获准中性工具验证数据/网络边界；Claude-backed 工具只能在接触门禁打开且该动作明确获准后测试
6. 只添加本次所需组件；任何新插件、新外部接收方或新增权限触发重新审批和相关路径复验
7. 查到破限、反代分发等非法工具，按[非法工具清理](illegal-tools-cleanup.md)清掉

**副作用/恢复**：禁用工具可使依赖任务失败；卸载不保证远端授权撤销。分别记录本地配置恢复、远端授权撤回和已传数据的不可撤销边界；不自动删除项目文件或远端账号。

### I3 实际启动、继承与后台进程（PC1/PC2）

1. 通过共用接触交接后，核验当前官方客户端网络配置与安装版本；历史 O04/E08 只说明待核验方向，不保证所有版本同样支持
2. 仅列相关 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`NO_PROXY` 键的设置状态及脱敏端点类别；不运行全量 `env`。检查平台的大小写语义和 bypass 范围
3. 说明“变量继承”与“实现使用该变量”是两项证据；shell 探测不能代替 GUI、Node/Python/MCP 或 supervisor 的真实路径
4. 经批准从实际入口启动所需组件，记录真实父子路径及目标请求的网络观察；GUI/IDE 启动的 Code 与独立 CLI 分测，不擅自运行付费任务
5. 修改启动配置后只正常重启获准组件，先保存未完成工作；另一个终端改变量不会自动更新已有进程。发现孤立子进程先确认归属和任务，再决定是否停止
6. 代理停止/节点失效演练单独批准；准备离线恢复，分清 GUI 退出与内核停止。记录哪些进程、协议和地址族实际尝试过新连接，未覆盖项保持 not_run
7. 更新/重启后对比程序路径/签名、配置作用域、工具权限和网络；旧防火墙规则不因路径名相似就算继续有效

**停止/恢复**：唯一 Codex 控制通道可能中断、后台归属不清或日志可能泄密时停下。恢复精确启动器/规则/配置，不杀整个解释器、不改变 Codex 认证、不关闭 TLS 校验。

## M11 SDK、网关与高级集成核对表

### J1 先画调用链，不按软件名定性

示例仅是架构模板，不代表获准部署：用户入口 → Agent/SDK → 可选网关 → 上游服务；旁路还可能有 MCP、hook、日志、缓存和计费平台。对 **CPA、new-api、Pi Agent** 分别查实际部署配置与职责，不能因名称就判违规/合规。

1. 复用已有环境选择；有网关/SSH 经验不自动切换 VPS。记录每一跳在哪里运行、谁运营、代表谁提供服务以及发送哪些数据
2. 查接口协议、实际上游、认证类别、订阅/API/云平台计费关系和组织权限；同一个兼容 API 地址不代表同一授权或数据处理方
3. PC0 只读配置结构/用户自述；PC1 获准后核验对应产品的当前官方认证、SDK 和合规条款。O03/O09 历史正文可能有变更/暂停说明，不能截取旧规则作永久结论
4. 个人使用、为他人提供的服务、共享账户/转发凭据分开评估；未经明确允许不把订阅 OAuth、session 或个人 token 交给第三方网关
5. 列出信任边界：请求体/仓库/对话/响应谁能看到，日志是否包含秘密，数据在哪里存多久，删除/导出由谁控制。未核验就标 unknown
6. 只在合法准入、实际权限、数据目的地和计费主体都清楚后提出最小集成方案；不伪造官方客户端身份、不抹请求来源、不轮换账号/节点绕限

**验收**：交付逐跳表，每跳含运行位置、认证类别、数据范围、权限、计费、观测点及当前证据。网络通但上游未知，不能宣称集成可用。

### J2 最小试验、预算、重试与日志

1. 拟定无敏感内容的最小请求/预期响应、最大次数、超时、成本上限和停止条件。收费 API 请求需已有具体授权；没有额度时保留 planned，不借用户订阅试探
2. 验证请求发往预期上游及响应来源；网关生成的状态码不能直接归因上游。记录脱敏 request ID、时间、组件版本和错误类别，不保留 Authorization/Cookie/完整请求体
3. 流式响应区分连接建立、首字节、正常结束和中途断流；重试前判断任务是否已经产生副作用或费用。幂等只在对应接口确有支持时采用，不能凭空加 header 保证去重
4. 对限流遵守实际响应的等待提示和当前官方限额，设置有界退避、最大尝试数与取消路径；队列满时明确拒绝/等待，不无限重试
5. 分开模型限额、组织预算、网关策略、并发和服务过载；不写“单 IP 少于几并发就安全”，不制造人类节奏、不换 IP/账号扩容绕过限制
6. 预算记录实际已生效的硬限额、提醒、自动充值各自状态及负责人。提醒可能延迟且不必然阻止消费；没有供应商证据时不称 hard cap
7. 日志最小化并设用户批准的访问和留存；先用合成秘密哨兵检查脱敏，失败停下收集。不要将完整生产日志传到公共 issue

**失败/恢复**：助手不再发起自己的新增请求；停止用户正在运行的任务前须说明影响并取得明确批准。保留脱敏失败样本和消费状态；恢复原端点/配置前核对影响，不重放已成功的写操作。撤销凭据和删除远端日志为另行授权操作，不能承诺撤回已发送内容或费用。

### J3 分层排障与变更验收

按调用链从最近的确定事实定位：本地进程/IPC → 代理与 DNS/TLS → 网关鉴权/路由 → 上游认证/权限 → 额度/账单 → 服务响应。每次只改变一个已证实的问题，列前后对照和恢复点。请求比例、cache miss、Token 数量、某 HTTP 库或 TLS 指纹本身都不足以证明蒸馏/滥用。出现组织政策不明或实际条款冲突时停止集成，走管理员/官方支持，不用稳定出口掩盖授权缺口。

## M12 异常处理：从症状到事实报告

### K1 首次事故接入与优先级

1. 凭据暴露/数据损失优先控制影响；明确停用/核验优先官方处理；其他错误先分层。不让事故用户重走套餐和服务器购买教程
2. 询问一次：发生了什么、何时（含时区）、在哪个产品/设备/入口、做什么动作、脱敏错误原文、最近改了什么、是否已有官方工单/指示。已知事实直接复用
3. 区分本人观察、日志、第三方转述和推断；保留时间线但不强制收集邮箱、全部账单、身份材料或聊天历史
4. 先保全项目/未提交修改和必要脱敏证据；未经授权不删除数据、不退出全部会话、不清空浏览器、不重装系统
5. 停止自动重试、重复登录/刷卡的建议必须明确影响；真正停止运行任务需具体授权。PC0 不为复现错误访问旧停用账号

### K2 故障分流表

| 类别 | 支持该分流的事实 | 最小只读检查/下一步 | 不应做什么 |
| --- | --- | --- | --- |
| 网络/DNS/TLS | 解析/连接/证书失败，且响应来源明确 | 对照目标配置、时钟、获准中性端点；客户端真实请求留获准阶段 | 关闭证书校验、安装陌生根证书、把网络错认封号 |
| 认证 | 明确认证失败/过期提示 | 查入口、凭据类别及作用域；走官方重新认证交接 | 读取秘密、轮试所有 token、复制别人的会话 |
| 权限 | 已认证但产品/项目/组织权限不足 | 核对目标项目、席位、当前管理员授权 | 用更高权限凭据强行绕过 |
| 额度/速率 | 有明确额度/限流提示 | 查来源层、等待提示与适用配额；有界暂停 | 换 IP/账号、持续重试、断言 429 就是封禁 |
| 服务过载 | 官方响应/获准状态信息表明暂时过载 | 记录时间与来源、按官方提示稍后重试 | 把 529/5xx 认定账号问题或固定等待天数 |
| 支付 | 原渠道订单/发卡方有实际异常 | 转 M03 对账，先确认是否已扣/待处理 | 重复买套餐、假账单地址、承诺退款 |
| 身份核验 | 官方明确要求真实身份材料 | 用户在官方流程完成，记录状态与下一步 | 向聊天传证件、伪造材料、借用身份 |
| 明确停用/组织 hold | 官方通知明确写限制对象与状态 | 事实时间线、官方申诉/支持、适用导出/退款请求 | 清理设备“解封”、换号循环、用代理替代准入 |
| 不明错误 | 只有 403/429/529、白屏或截图片段 | 标 unknown，先确认响应方/产品/时间和最近变更 | 以状态码、IP 风险分或设备历史编造原因 |

**结果解释**：一条错误可以涉及多个层次；列主要阻碍和未排除因素，不制造唯一因果。上游状态页仅 PC1 对应许可后查，缓存/第三方截图不能证明实时服务状态。

### K3 证据包与事实时间线

最小证据包导出前必须取得用户对具体内容和精确保存目的地的批准；本地私有路径与远端存储均适用，不能因本地保存而省略授权。确认访问权限和敏感信息已最小化后，才在获准目的地保存。内容如下：

- 案件摘要：产品/路线/受影响对象（脱敏）、当前阶段、业务影响及是否仍在发生
- 时间线：时间和时区、事件、来源、已确认/自述/推断；未知时间允许写范围，不补造精确时间
- 错误样本：最小脱敏文本/局部截图、响应层、必要 request ID；不含完整 headers、token、cookie、私人对话
- 已完成检查/动作：目的、具体授权、结果与配置修订；把“建议执行”和“已执行”分开
- 保护项：项目、历史、配置和账单证据；备份是否读回验证及尚未覆盖对象
- 待办：下一最小检查、谁处理、期限（仅有官方证据才写）、停止条件及恢复限制

证据冲突时并列，不删除反例。历史“几小时/几天后封号”或“某设备黑了”的社区时间线来自所有者提供的资料，可用来解释常见原因；个案不预测结局。

### K4 官方申诉、导出与退款交接

1. 获准接触后核验 O11 当前官方处理入口；确认对象是个人账号、组织 hold、身份核验还是账单问题。来源中的旧邮箱/链接不自动可用
2. **封号申诉用 [ban-appeal.md](ban-appeal.md) 的模板**，用户按实际情况删改；其他支持请求先准备下方事实草稿，未知项明确标记
3. 展示发送到哪个官方入口、将分享哪些信息及希望对方采取什么动作；发送/上传需要具体授权，敏感材料由本人经官方页面提供
4. 记录已提交/仅草稿、官方 case 引用和指示；不要在多个入口批量提交，不编造申诉成功率；封号申诉的回复时间在 2 到 7 天左右，超过就基本凉了（[ban-appeal.md](ban-appeal.md)）
5. 数据导出：先核验当前账号状态下是否可用、范围/格式/有效期和可能包含的私人数据；由用户确认存放位置及访问权限，准备足够空间。不可用就请求官方说明，不承诺一定能导出
6. 退款：核对原购买渠道、订单和官方资格；转 M03 的具体事实请求。申诉成功与退款资格独立，取消订阅不等于自动退款
7. 后续仅按用户授权和官方指示跟进；没有答复时记录 pending，不自动再次登录测试、循环申请或替用户接受新的法律承诺

**事实草稿模板（封号申诉以外的支持请求；需本人审核，不自动发送）**

主题：请求核查 [产品/账号限制或账单问题]

我在 [日期、时区] 使用 [产品/入口] 时收到以下提示：[脱敏原文]。
受影响的功能是 [已确认影响]。相关时间线是 [有来源的简要事件]。
我已经完成 [实际完成的官方步骤或检查]，目前结果为 [事实]。
请说明 [希望核实的状态、需要本人补充的材料或可用处理路径]。
如适用，我也希望了解 [数据导出/原渠道退款] 的当前条件。

发送前删掉不适用句子；不能替用户杜撰观点或承诺。提交后不能保证撤回，所有后续通知仍需核对来源。

### K5 关闭事故与恢复使用

1. 关闭标准写具体：官方状态已说明/恢复、用户确认必要数据可用、相关配置问题复验通过，或依赖用户/官方处理而明确暂停；“暂时没再报错”不是所有问题解决
2. 恢复工作前确认仍是原授权目标与配置；仅做获准最小功能验证，不重复付费/耗尽额度。严格网络要求仍未满足时继续暂停相关连接
3. 若需要清理/迁移，使用上文 M13 的精确保护、备份、恢复计划；恢复快照/重装不能解除服务端处罚
4. 最终交付已知原因与未知、已执行动作、未执行项、证据时间/范围、用户下一步、恢复限制和复验触发条件；不要写“已防封/永不再发生”

## 来源、官方入口与更新规则

- O03 [认证与合规](https://code.claude.com/docs/en/legal-and-compliance)、O04 [网络配置](https://code.claude.com/docs/en/network-config)、O09 [Agent SDK 与计划](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)：历史入口，需在 PC1 获准范围内核验当前内容、版本和更新说明
- O06 [API 错误](https://platform.claude.com/docs/en/api/errors)、O11 [警告与申诉](https://support.claude.com/en/articles/8241253-safeguards-warnings-and-appeals)、O10 [退款](https://support.claude.com/en/articles/12386328-request-a-refund-for-a-paid-claude-plan)：只在相应事故/渠道使用，不代表当前资格已核实
- [S03 PDF 第 3–5 页](../sources/S03-claude-experience.pdf)、[S04 FAQ](../sources/S04-claude-guide.md)、[S05 子进程防护](../sources/S05-local-protection.md)、[S06 保留 CLI 的清理](../sources/S06-macos-cleanup-sanitized.md) 是带归属的经验/阅读材料；与当前官方政策和目标设备实测分层。S09 是上文指定的外部固定提交阅读指针，未随本仓库 S01–S08 来源包提供，未验证为可用适配器；只供另行审阅，不能作为已验收脚本直接执行

本次文档编写没有访问 Claude 服务、安装/启动客户端、读取用户秘密或执行系统变更。后续更新应按官方变更、具体客户端版本、用户明确目标修订相应卡片，保持原始来源不变，不把新增文字当历史来源原话。


## Explicit C5 Agent execution sequence

1. Read typed intent and independently confirm the actual selected device/user/namespace, application/version, inactive state, ownership, selected roots and protection list. Native discovery unsupported or ownership unknown means stop at the plan explanation. Do not expand scope by path-name guessing.
2. Obtain authorized read/hash scope, exact category selection, required verified backup and private same-filesystem quarantine location. C5 goal `C5-full-claude-data-reset` maps to core mode `C5-full-local-data` only here, not to a shell command.
3. Call `cleanup_transactions.plan(roots, protected_paths, quarantine_directory, target_ref, mode='C5-full-local-data', host_check=fresh_scope_check)`. Roots are exact canonical absolute objects `{root_ref, path, data_kind}`; kind is `cli_app_data` or `desktop_app_data`. No arbitrary transcript text becomes a path.
4. Show the exact private plan/impact/exclusions/recovery to the user in the appropriate private channel. Obtain the current operation approval bound to `plan.digest()` and target. A digest summary alone is insufficient to explain affected data.
5. Only with actual exclusive access held and fresh host checks call `quarantine(plan, authorize=current_operation_approval, host_check=fresh_scope_check, exclusive_access=True)`. This boolean declares a prerequisite; it does not acquire OS isolation. Callback strings are host assertions, not proof of user permission or application ownership.
6. Preserve private receipt/journal and verify protected data. Report receipt.preview(), including partial results and `native_acceptance='not_run'`. Do not export private paths, file contents or credentials.
7. For recovery, independently approve `restore_cleanup` against `receipt.digest()` and the same verified target, then call `restore(receipt, authorize=current_restore_approval, host_check=fresh_scope_check, exclusive_access=True)`. A prior quarantine approval never approves restore. On faults use the core's documented reconcile/recovery path; do not fabricate completion or manually delete journals.

The callback contracts are `host_check(target_ref, scope_digest) -> 'verified_inactive_claude_data'` after actual verification, and `authorize(operation, digest, target_ref) -> True` only for that operation's current approval. No permanent purge, network, subprocess, application launch, credential, browser or uninstall adapter is provided. POSIX temporary-fixture success does not certify macOS application ownership, Windows behavior, or native user-device results.
