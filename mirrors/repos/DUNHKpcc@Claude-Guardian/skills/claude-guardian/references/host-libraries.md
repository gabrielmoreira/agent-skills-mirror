# 内置脚本与宿主库的契约说明

从 SKILL.md 移出（ADR-044）。这里是各内置入口和宿主库的精确边界：能做什么、要什么输入、哪里会阻塞。用户任务用到某个脚本或库时再读对应小节；只是做访谈、出方案、按分级授权在用户机器上操作时不需要读。脚本清单见 [scripts-index.md](scripts-index.md)。

## Agent内部修复入口（按动作能力分流）

已核实目标使用2.5.8且选定独占rules扩展时，可用 [Agent 应用编辑任务](agent-rules-task.md) 生成单个DOMAIN变更的私有候选和供给内容核验。实际保存／重载由Agent通过受支持应用界面执行，须具体许可；该辅助接口不执行写入或证明实际网络效果。

`scripts/repair_cli.py`提供精确文件的`preflight / plan / diff / execute`接口。`plan`显式指定`--plan-file`和`--backup-directory`才写入新的私有计划文件，不修改目标；`--private-review`可在获准的私有Agent会话中非交互展示选定规则及policy前后差异，不输出无关配置。私有差异不得混入公开报告。

已确认交互是Agent展示具体改动、目标、影响、备份及恢复路径，用户在对话确认后，由可信宿主核对该次授权并调用固定内部脚本；不要求第二次终端确认码。宿主将确切`retained_plan_digest`、目标与备份范围绑定到本次操作；摘要只是完整性检查，不是授权。不能用JSON布尔值、任意回调、临时shell改写或终端模拟绕过权限。

`scripts/repair_execution.py`保留计划有效期、请求摘要、原文件身份和内容、候选一致性复核、事务备份及读回链路；生产原生适配门禁只开放一个固定范围：macOS 上 Clash Verge Rev 2.5.8 的 `rules-prepend` 扩展（`native_clash_verge_mac.py`，要求 Clash Verge 应用已退出（后台的核心和服务可继续运行），写入前后复查，检测到变化即失败；macOS 无强制文件锁，这是发现并失败，不是阻止）。其他系统、产品、版本和 `merge-policy` 仍返回`NATIVE_REPAIR_ADAPTER_UNAVAILABLE`，不得宣称实际修复完成。该适配器在一台真实 Mac（macOS 15.7.4）上已验证：版本与归属、计划可复现、应用运行时拒绝写入、真实写入、重启后规则在场、`recovery_cli` 回滚回到基线哈希；那台 Mac 的 profile 有 script 与 merge 链，规则是否被后面的链改写要重启后探测，写入成功不等于生效；别的环境以实际核对为准。Linux临时夹具中替换适配器的测试不开放用户Mac/Windows能力。恢复仍遵循独立`recovery_cli.py`契约，不自动覆盖后续改动。

`scripts/clash_verge_258.py`只校验调用方提供的2.5.8应用plist、配置索引和扩展字节之间的声明一致性：current→活动profile→显式option.merge或option.rules→唯一同类型扩展及basename。拒绝跨profile共享扩展、全局默认UID及路径/文件别名歧义。该库不读取真实文件，不证明实际安装/运行归属；输出始终为supplied_metadata_only。merge的rules数组替换基础数组，不能将rules扩展的prepend/append/delete混当此格式；脚本/后续链、内核版本、真实写入者排除和验收仍阻塞，不能以该结果开启execute。

`--candidate-kind rules-prepend`提供独立的rules扩展候选：必须显式给出`--base-path`、`--app-info`、`--profile-index`及`--extension-uid`，经安全读取核对所提供的2.5.8声明链和当前基础profile路径。只向现有空`prepend: []`插入用户明确排序的DOMAIN/DOMAIN-SUFFIX规则；`delete`必须为空，`append`与其他字节保持不变。拒绝已知受保护规则冲突，不把调用方声明的控制路径或优先级当作验证。私有差异包含已知优先级影响；未知链和原生执行继续阻塞。

保留计划格式为`guardian-retained-repair/0.3`，绑定当前环境入口摘要、候选类型、UID和基础配置/plist/索引的精确路径、父目录及文件快照。执行参数必须一致，提交前与读回后复核；旧0.1/0.2计划必须重建并重新展示确认。完整输入格式及命令见仓库`docs/rules-extension-plan.md`。不得用此入口初始化空merge、替换完整rules数组或绕过xattr限制。

## 限定静态盘点入口

`scripts/inventory_cli.py capabilities` 查看实际开放范围。`static-audit` 只读取用户明确列出的本地配置，要求新的精确范围终端确认，拒绝保存的授权字段；目标身份/本地文件性质仍需可信宿主核实，终端输入不能代替宿主或操作系统权限。缺少可选PyYAML时停止，不自动安装。静态声明不代表运行时路由。

`scripts/remedy_plans.py` 提供四种方向的离线语义计划：保留现状、显式代理规则、TUN规则、限定兼容处理。它不生成可执行配置补丁，不开放apply；需要可信宿主提供私有快照绑定和公开别名。现有inventory CLI不能直接提供全部输入。结果中的DNS图、协议、控制路径和规则范围只依据投影事实；缺失或冲突保持阻塞，不推导已修复。

POSIX独立恢复入口为 `scripts/recovery_cli.py`，须与 `transactions.py` 预先保留在可信本地位置。inspect只读用户选定回执；preview/rollback仍只接纳已应用回执。reconcile须绑定独立确认的目标、备份批次与回执摘要，只读观察选定记录；仅v2 prepared的候选匹配状态可用restore-prepared另行恢复，并要求上次私有观察的完整摘要、实际排除其他写入者及真实终端逐阶段新确认。旧prepared或冲突状态不写入，不重放apply；摘要和回执不是授权，Windows不支持。Agent宿主的对应调用及失败处理见 [agent-remediation.md](#prepared-recovery)。仅验证精确文件字节，不代表应用/网络效果已恢复；生产原生修复门禁不因此开放。

单轮多个已明确事实可通过 `--answer-file` 的 `{"answers":[...]}` 批量提交；每项沿用 `question_id/value/state/source` 格式，旧单项格式仍支持。宿主负责从自然语言提取事实，CLI不做自由文本解析或猜测未给出的套餐。整批验证失败不保存部分状态；重复/别名冲突、订阅阶段与老用户任务矛盾须澄清。当前本机默认建议可用Q-C05值 `accepted_default` 接受，不再重复确认路线；不会覆盖已选VM/VPS，也不构成动作或保存许可。

## 本地环境状态面板

`scripts/status_dashboard.py --input <guardian.py 报告.json> --network <network_check.py 报告.json> --output <新HTML路径>` 生成离线面板，由用户自己打开。`--network` 附上的检测在 24 小时内通过的项显示“已验证”，有问题的显示“发现问题”，超过 24 小时的显示“未知”；没附的网络卡片显示“未执行”。只显示白名单字段，不含地址、路径和身份。

### 私有配置候选（不可应用）

`scripts/config_edit_plan.py` 在内存中把原始语义修复请求与精确哈希绑定的已拥有扩展配置，编译为有限规则policy token修改候选。仅支持keep-existing中的特定已有DOMAIN/DOMAIN-SUFFIX三字段规则，保留其他字节并重新解析核对；不读写文件、无CLI、无apply、不触发事务。重复/歧义选择、无效域名标签、已能证明的前置MATCH/DOMAIN-SUFFIX覆盖、未知版本和无效修订被拒绝；局部检查不证明完整规则图或合并后首次命中。版本声明仍不等于兼容验收。候选私有材料含原文与精确差异，只能在获准私有本地审查，不上传或混入公开报告。所有原生适配、版本/归属、实际路由和动作授权阻塞保留，apply_supported始终false。

## 环境入口校验

调用 `scripts/environment_entry.py` 的 `assess_entry` / `require_entry` 严格校验当前投影，再走原有目标、PC0、权限及逐动作授权门。入口资格不是许可或原生绑定证据，不把保存的报告恢复成许可。CLI 的 `--entry-file` 只读取明确提供的有界本地投影，Windows 此文件适配尚未开放；可信宿主可传已校验的字典。路线／资源改变必须使旧适用性和计划失效，不能复用旧检查结论。既有精确恢复义务仍按原回执、目标、保护和本次批准处理，不被新问卷阻断。

## 旧目标范围契约与整机结论

现有 `traffic_policy`、CLI、访谈评估和面板仍输出旧目标范围契约，不代表整机合规；不能改返回字段假装升级能力。规则声明、应用载入、进程采用和端到端观察分别报告；同一代理链不保证同一公网 IP，样本一致只支持测量范围。整机强制覆盖或持续保护未建立时如实标 unknown／unsupported／未建立，不能 pass，G2或单次curl成功也不能代证。PC0、具体动作许可、取消、拒绝及事故优先级保持不变。

<a id="environment-entry"></a>
## 环境入口：完整声明与实际调用

先确定当前任务，再显式选择执行路线，最后补所选网络资源和配置状态。已有 VPS、推荐默认值或旧访谈答案都不自动构成本轮选择；订阅解释、路线比较和不接触设备的纯内存计划无需先填环境问卷。当前没有把旧访谈自动转成入口声明的接口，宿主应依据本轮明确选择构造完整 `guardian-environment-entry-input/0.1` 对象，不能为通过校验把 unknown 改成 selected。

以下是完整、虚构的合法输入示例：已选择本地 `device-1`，资源和配置仍未知。只有 `offline_precheck` 具备进入原门禁的资格，配置／主动探测仍阻塞；不要求先购买代理。`client` 是本轮已明确的用途，不代表启动或访问 Claude Code。

```json
{
  "schema_version": "guardian-environment-entry-input/0.1",
  "route": {"choice": "local", "state": "selected"},
  "targets": [{"role": "local", "target_ref": "device-1"}],
  "network": {
    "possession": "unknown", "selection": "unknown",
    "configuration": "unknown", "path": "unknown"
  },
  "local_entry": {"kind": "unknown"},
  "final_egress": {"kind": "unknown", "protocol": "unknown"},
  "client": "claude_code"
}
```

声明只接收规定的枚举和非识别性别名。不得加入真实主机名、IP、订阅 URL、UUID、密码、token、原配置或授权布尔值；别名语法校验也不保证隐私，宿主仍须脱敏。`effective` 仅是报告的配置状态，不是原生观察。`eligible_for_existing_gate` 不证明设备／用户／命名空间，不授予读取、写入、联网或 PC0 接触权限。

### 文件与宿主入口

下面所有路径都是占位示例。先在获准的私有本地已水合目录准备 UTF-8 JSON，再替换成经过核实的规范绝对路径；不能从真实用户目录猜位置。入口文件安全读取复用 `inventory_cli.read_request`：最多 65,536 字节、拒绝重复 JSON 键及非有限数值、非普通文件、硬链接和包括祖先在内的符号链接；文件读取期间的身份／大小／时间变化会拒绝。文件的本地性、已水合状态及读取许可仍由宿主建立。

该文件读取器目前仅支持具备相应安全文件能力的 POSIX 环境，Windows 返回能力缺口，不能以改平台标记或不安全读取绕过。已审阅宿主可直接传当前 dict：`guardian.native_check(args, entry_request=entry_request)` 保留原有的平台、目标及许可校验。

已确认本地 macOS、真实读取许可及当前宿主绑定后，命令形式如下。`--confirm-target`、`--authorize-audit` 不是替用户做确认；只有真实前提成立才使用。

```sh
python /trusted/claude-guardian/scripts/guardian.py check --target-ref device-1 --target-os macos --target-kind local --namespace desktop --execution-location native_local --user-context same --confirm-target --authorize-audit --entry-file /private/guardian-task/entry.json
python /trusted/claude-guardian/scripts/repair_cli.py preflight --request /private/guardian-task/repair-request.json --target-path /private/guardian-task/selected-extension.yaml --target-ref device-1 --candidate-kind merge-policy --entry-file /private/guardian-task/entry.json
```

`guardian check` 缺 entry 默认禁止，不再隐含选择本机；`--target-kind local` 本身也不能替代 entry。

`repair_cli.py` 的 `plan`、`preflight`、`diff`、`execute` 都必需 `--entry-file`；前三者使用 `offline_precheck`，execute 使用 `configuration`。预检还要符合原请求格式、候选类型、精确路径、版本和所有权条件；合法 entry 不使生产写入可用，原生执行适配仍未准入。宿主 merge-policy 预检使用 `repair_cli.preflight(request_path, target_path, target_ref, entry_request=entry_request)`；不可把入口 JSON 当作 repair request。

### 静态 inventory 的 /2 信封

`inventory_cli.py static-audit` 不使用 `--entry-file`，而在完整 `guardian-static-cli-request/2` 请求的顶层嵌入 `entry_request`；旧 /1 不再接受。下面是完整虚构格式，文件路径也只是占位值：

```json
{
  "schema_version": "guardian-static-cli-request/2",
  "target_ref": "device-1",
  "entry_request": {
    "schema_version": "guardian-environment-entry-input/0.1",
    "route": {"choice": "local", "state": "selected"},
    "targets": [{"role": "local", "target_ref": "device-1"}],
    "network": {
      "possession": "unknown", "selection": "unknown",
      "configuration": "unknown", "path": "unknown"
    },
    "local_entry": {"kind": "unknown"},
    "final_egress": {"kind": "unknown", "protocol": "unknown"},
    "client": "claude_code"
  },
  "target_binding": {
    "target_ref": "device-1", "binding_state": "bound", "declared_os": "macos",
    "execution_location": "native_local", "desktop_user_relation": "same",
    "filesystem_namespace": "host_desktop"
  },
  "application": {
    "product": "clash-verge-rev", "gui_version": "2.5.5", "core_version": "1.19.0"
  },
  "files": [
    {"source_ref": "profile-1", "kind": "profile", "path": "/private/guardian-task/selected-profile.yaml"}
  ]
}
```

```sh
python /trusted/claude-guardian/scripts/inventory_cli.py static-audit --request /private/guardian-task/inventory-request.json --target-ref device-1
```

这个静态 CLI 当前仍限定上述 macOS／产品版本和原终端确认，字段中的 bound 只是调用者声明，不能伪造来补能力。全部请求先校验、范围确认后再复核；转入原 inventory 库时移除 entry 字段，不保存为授权。Windows 静态文件读取、自动发现和控制器访问不会因 /2 而开放。

### 路线与失败边界

- 本地执行配 VPS 出口仍是 `route.choice=local`；资源持有、选择、导入和生效分开记录。明确 direct 时无需购买代理：`selection=direct`、`path=direct`、`local_entry.kind=none`、`final_egress.kind=direct`、`protocol=unknown`，但不得凭格式修改来改变用户实际选路
- 本地和 VM 的入口评估建议适用的详细检查；VM 必须同时声明不同别名的 `vm_host` 与 `vm_guest`，分别绑定实际宿主和来宾，不能用宿主结果代表来宾。VPS 使用 `vps` 目标角色，仅基础、非侵入检查；不扩展到部署、配置变更或 quarantine。纯入口评估支持这些声明，不等于已有对应执行适配；当前 guardian native 和 static inventory 只接纳 local 角色，不能自动 SSH、套用本机结果或把 VM 改称 local 来通过
- 缺失／畸形 entry、路线未选、撤销、冲突、陈旧或目标不属于当前路线都阻塞相关新动作；保留固定错误并重新核对当前范围，不能退回隐含路线或自动复用旧确认。调用期间变化停止后续依赖步骤；已有材料只保留其真实历史状态，不能当作当前权限
- repair 与 cleanup 的保留计划跨调用绑定生成时的完整入口声明。路线、目标、所选资源或配置声明变化后，必须重新生成并审阅计划；新的合法 entry 不能继续执行旧计划，也不能手改计划中的绑定摘要来通过。未保留该入口绑定的历史清理计划仅可用于已有工作的精确 reconcile／恢复，不允许启动新 quarantine；保存的摘要始终不是许可
- 已有回执的精确恢复不要求重新建立这项新动作 entry；`recovery_cli.py` 的既有恢复及 cleanup 的 reconcile／restore 保留原回执、摘要、当前目标、单独恢复许可、冲突和备份核验。撤销路线不能让既有恢复义务消失，也不能把恢复例外用于新配置、扩大清理或主动探测

<a id="prepared-recovery"></a>
## 已替换但回执未完成：精确文件恢复

仅针对`transactions.py`既有POSIX精确文件范围，不处理系统设置、凭据撤销、删除、Windows或应用有效状态。实际变更前须把可信`recovery_cli.py`及`transactions.py`、原始备份和步骤保留在获准私有位置，并核实目标上的独立终端能运行；不能等Agent失联后再要求在线取得步骤。完整命令见仓库`docs/offline-recovery.md`。

1. 写入失败或中间状态不明，先停止自动重试。保留当前文件和私有批次，独立核对目标别名、精确目标路径、批次及选定回执来源；不扫描其他位置，不把备份、base64、完整文件或敏感摘要发到公开报告
2. `inspect --receipt`只读指定回执，摘要仅为未验证候选。经确认精确读取范围后，`reconcile`加`--receipt-digest / --target-ref / --target-path / --backup-batch`读取该范围；宿主库入口是`reconcile(recovery, receipt_path=..., target_ref=..., target_path=..., backup_batch=...)`。分类是当前观察，不是历史apply成功或恢复许可
3. 只有v2 prepared的`prepared_candidate_observed`能进入单独恢复。展示原字节/模式将覆盖的确切当前候选、经审阅语义影响、保留项和恢复风险；保留该完整观察的操作摘要。旧v1 prepared、原文件仍在、已恢复候选和冲突均不走此写入口；不能改schema、伪造applied回执或重建快照消除冲突
4. 可信宿主取得本次具体恢复许可并实际排除所有写入者后，调用`restore_prepared(recovery, observation, target_ref=..., authorize=..., exclusive_access=True)`。两次授权核对必须绑定`restore_prepared`、`digest({'recovery_digest': digest(recovery), 'observation': observation})`及目标；脚本复核回执、原备份、批次和完整当前快照。不能自行返回True、使用保存的JSON权限或模拟终端确认。独立普通终端用`restore-prepared`及`--reconciliation-digest`，要求真实用户分别完成排他条件和两次新的随机挑战确认
5. 观察摘要或任一快照变化就停止，重新调查并展示受影响差异；不自动换摘要重试。成功仅表示本次原字节/模式恢复，保留prepared及恢复结果，不补造历史applied。错误可能发生在已恢复后、结果日志落盘前；用返回的有界批次/尝试别名定位确切`restore-<attempt_id>.prepared.json`，存在时先inspect再按独立范围reconcile。没有日志不等于没有修改；`restored_candidate_observed`只读报告，不重复写入，别名也不证明日志必然存在

固定`cleanup_code`为`STAGING_RETAINED / STAGING_CLEANUP_FAILED / DESCRIPTOR_CLOSE_FAILED`时，主错误之外还存在保留材料或清理失败；按精确范围调查，不宣称没有残留或自动删除可能含秘密的暂存文件。

这使限定恢复路径可由可信宿主调用，并保留Agent不可用时的独立入口；这些恢复入口本身不是写入适配器；写入适配器仅放行 macOS Clash Verge Rev 2.5.8 的 `rules-prepend`（见下文“Mac 修复链”），其余范围 `NATIVE_REPAIR_ADAPTER_UNAVAILABLE` 不变。独立读取/恢复也不能绕过目标权限、PC0或操作系统拒绝。Linux合成临时文件/终端测试不代表Mac/Windows设备、实际断网、应用重载或规则命中通过。

## C5：限定清理宿主交接

选择器的 `cleanup.host_handoff` 是固定能力说明，不是已选择操作或执行授权；`target_mutation_supported=false` 和 `builtin_execution=not_available_for_target_mutation` 描述选择器本身。单独的 `cleanup_cli` / `cleanup_transactions` 已提供限定 POSIX 文件操作，但没有原生 Claude 数据发现、归属、停用或写入者排除适配。普通 `CLEANUP_REQUESTED`、事故或历史记录不能替用户选择 C5，也不能从报告中的布尔值恢复许可。

Agent先核对当前目标和独立明确的 `Q-D02=full_claude_data_reset`（评估为 `C5-full-claude-data-reset`）。这仅进入 `scope_inventory`：暂停、事故优先、延期、未完成续接复核或前提失败仍停止依赖步骤。先取得限定盘点许可，核实精确 Claude 专属根、保留项、独立备份及恢复，再准备 `mode=C5-full-local-data` 的私有操作清单。清单声明和摘要本身不证明归属或同意。

实际入口为 `cleanup_cli.main(argument_list, host=reviewed_live_host, entry_request=current_entry)`，使用受信任安装路径导入；选择器不会调用它。plan／quarantine 必须传与清理目标一致的本轮 entry；它只检查 `offline_precheck`，不代替逐操作清理许可，VPS quarantine 明确阻塞。已有计划／回执的 reconcile／restore 不要求新 entry，仍须全套恢复核验。现有参数如下，只能通过独立审阅的进程内宿主桥执行目标操作：

```text
plan --scope <private-scope> --plan-output <new-private-plan>
quarantine --plan-file <retained-plan> --expected-plan-digest <document_digest>
reconcile --plan-file <retained-plan> --expected-plan-digest <document_digest> --receipt-output <new-private-receipt>
restore --receipt-file <receipt> --expected-receipt-digest <document_digest>
```

普通 `cleanup_cli.py` 运行没有宿主，返回 `HOST_ADAPTER_UNAVAILABLE`；不存在注入宿主模块或“已授权/已核实”的命令行开关。macOS 上用内置宿主 `native_cleanup_mac.py`（固定清单、Claude 已退出、内容校验的备份、用户在真实终端输入确认短语），详见随包清理CLI用法；其他平台没有宿主。包装命令使用返回的 `document_digest`，不是核心 action digest；它只绑定材料，不授予权限。完整格式与回执恢复见随包[清理CLI用法](cleanup-cli-usage.md)，核心范围见[事故与清理指南](incidents-and-integrations.md#cleanup-migration-and-recovery-m13--env-09)。

宿主必须新鲜核实设备/用户/命名空间、独占 Claude 数据归属、应用与数据库停用、受保护/共享路径、独立内容备份，并在写入和校验期间保持真实写入者排除。`verify` 是获准的宿主核实；`approve` 逐次复核同一次仍有效的精确操作同意；`exclusive` 提供真实排除；`cancelled` 反映撤销或取消。不得用模型自行返回 True 的回调、保存的 JSON 或任意脚本绕过缺失前提。scope读/hash、保存计划、quarantine、reconcile、保存回执和restore各自按当前范围授权；隔离同意不包含恢复同意。

默认保护 CLI、配置、历史和扩展；独立选择且核实归属的 Claude 专属 C5 数据可另行纳入。源码、Codex、其他应用、共享对象和恢复通道继续保护。成功 quarantine 移除所有已选择并验证的活动根，隔离副本、日志及独立备份仍保留；这不是永久安全擦除，也不证明发现所有 Claude 对象。报告确切所选/排除范围和部分完成情况，不声称卸载、清除远程限制或免封。

失败可能发生在真实移动之后，按 recovery_id、moved_count 和 stage 报告，不能因错误码断言未修改。保留计划与隔离批次；重新核实宿主、获准 reconcile 并保存新回执后，另行展示并批准 restore，不覆盖后续改动。永久 purge 未实现，未来需要独立实现和逐动作批准。
