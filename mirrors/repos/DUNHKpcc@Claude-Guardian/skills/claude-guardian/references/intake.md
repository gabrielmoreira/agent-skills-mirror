# M00: adaptive intake and stable question registry

在任何目标检查或修复前，先取得明确的本机／VM／VPS 选择。原问题 ID、订阅与紧急分流继续保留；纯订阅说明不强迫环境问卷。先前未答而仍存在的本机建议可以被随后明确接受；撤回已选路线后，不得假设本机建议被接受。Q-C05 的 unknown/declined/stale/conflict 必须关闭旧确认，旧目标适用事实保留为待复核。

环境入口另用 `guardian-environment-entry-input/0.1` 记录严格枚举与安全别名：route、targets、network、local_entry、final_egress、client。资源存在、资源选择、配置导入和实际生效分别说明；不把字段填完当成原生证据或授权。VM 主客机分别声明与绑定。选择后缺资源允许原授权的离线预检，自动配置及外联核验仍需具体可用方案与独立操作许可。VPS 本轮只做基础非侵入检查，不展开选购部署。参见 SKILL 的环境入口顺序和 `environment_entry.py` 契约。


中文执行摘要：先问订阅阶段，再问系统与当前任务；复用已知答案，一轮一个决策。Q-C07 永久停用；Q-C08 只表示目标套餐；首次订阅无实际矛盾不问旧订阅。下表是稳定 ID 的技术索引，向用户提问时改写成简短中文，不逐行照问。未知、拒答和未适用不能当作通过。

## Scheduling

Read existing task facts first. Ask one decision per turn; at most a few related short facts together. Absorb all useful facts in a reply, skip known/not-applicable items, clarify an ambiguous answer once, then allow unknown, decline, pause, or a limited plan. Never display this entire registry as a form. Structured UI is optional and must obey the actual host's tool contract. Do not change host modes or approval settings to enable UI.

Normal subscription-preparation order: Q-J01 → OS/purpose/target plan → account history and route → relevant network/payment prerequisites → route resources/protection → short summary. An urgent compromise, data-loss issue, suspension, identity check, or duplicate charge takes priority. Technical skill changes explanation depth only.

`subscription_journey` is `first_subscription`, `returning_subscription`, `existing_subscriber`, or `unknown`. Explicit first/returning answers establish only reported absence of a current subscription; they do not verify billing. Current subscribers get Q-C11 only if their task is missing. First-time users are not asked whether they want a subscription. Q-C08 means the desired plan, never legacy entitlement. Q-P02/Q-A06 activate only for relevant existing-billing tasks or an actual contradiction. Pure technical diagnosis does not activate a payment survey.

### 已到期用户的相关旧账单（T76）

“以前订阅过，已到期，准备重订 Pro，但先处理旧 Apple 订单退款”仍记录 `returning_subscription` 和原 `none_reported` 的来源/时间，保留已选 Q-C08，不制造冲突或当前有效权益。宿主将明确的旧退款/恢复任务归一为 `set_context(task="billing_issue")`；明确的旧渠道迁移可用 `change_channel`。普通重订不展开旧账单；不要将 returning 的 renew/upgrade 组合自动解释成已确认任务。Q-C11 的整批矛盾校验不变，不能为通过校验伪造 existing_subscriber。

仅处理相关旧账单时，按缺口问 Q-P02 和 Apple 条件 Q-A06；不把新购设备、商店地区、礼品卡、续费、结账或运行方案问卷作为解释退款的前提。宿主一次吸收完整旧订单答复：Q-P02 可保存明确提供的旧 plan（相关时）、billing_channel、status、pending_issue 类别；后三项明确时覆盖 A06，不自动生成额外事实。例：`{"plan":"原套餐","billing_channel":"apple","status":"expired","pending_issue":"pending_refund"}`。未说明的项不能补造；自由文本仍兼容，可按同一真实答复分别记录 P02/A06，保留其真实来源/时间。P02 未知、拒答或延期后不换成 A06 重复同一追问，只给带缺口的说明。旧购买渠道来自旧账单自述，不能从拟用的新渠道推定；已明确的旧 Apple 渠道优先于未来网页/Google/未选渠道，仍按缺口走 A06。结构化但未完整的非 Apple 旧订单在 P02 最多澄清一次；不因 reported 部分对象就宣称依赖已齐。P02 描述的订单发生实质变化或被标为陈旧时，旧 A06 不得替新订单补缺口；同一答复用整批接口先处理 P02，再吸收新的 A06。明确新账单/渠道迁移任务会复核保留的旧订单事实。历史设备清理建议不成为退款说明的前提，当前事故和明确启用的清理任务仍优先。

完成这段问诊后回到同一任务的 `subscription_preparation`，复用已选目标和无有效订阅自述，继续真正重订前提；明确的新任务仍用 `begin_task`，不继承旧购买目标。`billing_issue` 的 payment_intent 为 troubleshoot，仅表示账单问题；不授权扣款、申请退款或访问账户。具体退款规则、状态和官方入口仍须在获准范围内核验，不能承诺退款。

### 已有订阅的明确升级与实际订阅冲突（T77/T80）

明确已有订阅且本次只解释升级时，直接复用开场与任务；只补 Q-P02 的当前套餐/原购买渠道和 Q-C08 的目标套餐。当前套餐可复用有效 Q-C13，不从目标套餐或拟用渠道推定；Q-P02 的当前 plan、billing_channel 不要求额外盘问旧订单状态才能解释升级。当前渠道保留 apple/google/web 区别，未来渠道仍独立。未决定目标时按需问用途 Q-C01 与预算 Q-P05，做有来源及时效限制的比较，不默认最高档或当前价格。缺少当前套餐或渠道时，P02 最多澄清一次，只说实际缺口；对这一个缺口的真实当前答复，复用仍有效的另一字段，不要求用户把已知渠道/套餐重说一遍；未知/拒答/延期后不换成 A06 重问。此支路的 G2 仅表示足以给升级说明或比较草案；生效时间、抵扣/按比例收费、当前渠道资格、冲突与含税总价仍未核验，实际升级继续走 B6/B5 与 G3/接触门禁。明确 compatibility_needed 时另保留系统 Q-C02 与客户端要求 Q-L02 的实际缺口；另行要求 environment/network/cleanup 时仍按其真实前提处理，不能仅因已有订阅就全局跳过这些检查。

实际完成购买、订阅阶段变化或明确套餐失效后，旧 P02 的 plan 不能再替代当前套餐；旧版保存状态已明确把 C13 标成 stale/conflict 时，也须保留这项义务；保留原订单值、渠道、来源和观察时间，只补当前套餐缺口。可选派生 context.current_order_plan_stale 保留此义务，不能由 set_context 手动清除。 真实当前 P02 套餐答复解除义务后保留派生 false，区分已刷新与缺少新字段的旧存档；此标记不是权益或操作授权。当前 Q-C13 答复可满足当前套餐缺口；P02 的真实当前套餐答复也可解除该项义务，均不能从目标套餐推定。历史 P02 重放、较新导入或 correction 不能恢复已有陈旧义务，也不重置澄清次数；同一完成事件重试不重开已回答的问题。新生命周期的实际套餐缺口有一次自己的澄清，不继承上次已经耗尽的次数。同账号换设备保留这些账号订单事实与义务，新账号不继承。真正中断的分组复核包含此当前套餐来源； 已由真实当前 P02 答复消除的 retained_keys 义务，不从历史 scope_keys 重新生成；未解决的复核不能通过 begin_task 复活旧 plan，已知渠道仍保留，旧到期退款历史不因此扩展成当前套餐问诊。晚到的历史完成报告也不能使更新的当前 P02 套餐答复失效。

只有实际矛盾才开启订阅复核：例如首次订阅自述与相关购买页的已有订阅/续费提示冲突。先保留两方来源和观察时间，只问该提示是否对应这次目标及相关订阅状态，不问账号归属、密码或全套新购问题。此处 P02 的最小详情是 status=active/none/expired 与 page_relation=same_target/other_target/outdated，只缺一项就只问该项；已有渠道不能替代这两项，也不为完成详情额外要求旧账单 pending_issue/渠道。完整描述 P02 不等于消除矛盾：可以 G1 覆盖结束而 G2 对依赖的购买/账单任务仍 blocked，给最小查证与条件说明；未解决不重复扣款、不换渠道再买。已回答的 Apple 登录/验证不可用仍是 reported 的否定前提；已到期的旧退款仍是 returning/none_reported，它们本身不构成订阅冲突。具体路线是否可行与覆盖、权限分别说明。

宿主以 `report_subscription_conflict(state, source=..., observed_at=..., current_reply=True)` 记录当前实际报告；已有 `set_context(subscription_conflict=True)` 兼容入口生成宿主标记。可选 `subscription_review` 保留当前 episode_id、原始账号/任务/设备绑定、来源/时间、原旅程/订单及首个相关详情快照和一份解决记录。未解决期间出现实际较新提示时，另保留一份有绑定、来源、时间和详情的 latest_report，推进解决证据的新鲜性边界，原始记录不变；不把新提示当作成功的空操作。相同来源/显式观测时间的精确重试保留原日期，省略时间则表示新当前回复，不用于旧证据重试。较旧或同时间但来源改变的提示拒绝。新 episode 或实际较新提示重置本处详情的澄清次数，旧 P02 留存但不能冒充本次详情；已真实提供且不早于本次提示的状态/目标关系则直接复用。旧 true 状态迁移为未解决记录，原标记时间不明保留 null；false 旧状态不新增字段。未知、拒答、延期和后续 P02 覆盖都不能清除复核。`set_context(subscription_conflict=False)` 不能清除未解决记录。

解决入口 `resolve_subscription_conflict` 必须给当前 episode_id、account_ref、target_ref、task_id、outcome、answers、source；带显式 observed_at 时必须是实际当前回复并标 current_reply=True，省略时间表示新的当前回复。answers 沿用问题/值/状态的归一化形状，但只接受本次 Q-J01、Q-P02 和相关 Q-C11 的 reported/observed 事实，来源/时间统一来自这次真实回复。支持三种有兼容事实的结果：

- existing_subscription：Q-J01=existing_subscriber；P02 的 status=active、page_relation=same_target、pending_issue=none_reported，已知的当前 plan 与原 billing_channel 一并复用，未给出则保留后续升级的真实缺口，不把无关套餐/渠道盘问作为确认已有订阅的前提；用户明确后续任务才记录 Q-C11。没有后续任务只问 Q-C11，不擅自升级/续费
- other_target_page / outdated_page：保持原 first_subscription 或 returning_subscription；P02 的 page_relation 分别为 other_target / outdated，当前目标的 status 为 none/expired，pending_issue=none_reported，只保留已明确的对应渠道（确实没有渠道可为 none），不猜测。这表示原页面不再与当前目标矛盾，不自动切换账号；只有实际选了新目标才用 begin_task
- unknown / declined / deferred：answers=[]，保留未解决状态并结束自动追问；之后实际给出新证据才能继续

当 P02 只剩一个相关缺口且实际当前回复明确补了该项时，P02 事实可另带一个 retained_fields 条目，保存互补字段的原 value/state/source/subject_ref/observed_at；本次 value 与本次来源/时间仍只描述新答复，不给旧字段刷新日期。此结构仅用于当前套餐/原渠道，或同次冲突的状态/目标关系，不是通用对象合并。实际当前回复对唯一所问缺口表示 unknown / declined / deferred 时，本次 value 仍为 null、state 仍为该终止结果，仅将已知互补项连同原来源/账号/时间保存在 retained_fields；不重问，不将互补项误记为未知，也不解除缺口的 G2/G3 阻断。之后主动补答或同一证据重试仍保留互补项原日期。若互补项是当前套餐，实际中断后的套餐复核义务仍保留，不能以渠道补答或拒答代替套餐的新鲜性复核。完整订单替换、correction、历史导入、没有唯一相关缺口、陈旧/新 episode 或跨账号信息不走补字段复用。实际新冲突或显式失效可使该 null 事实转为 stale / conflict；此时 retained_fields 只是历史证据，不满足当前套餐/渠道或新冲突详情。旧读档中缺失该字段完全兼容；严格旧读取器需要升级，不能删除保存的互补证据来伪装新鲜。

这只是可信宿主对实际回复的事实契约，不是自然语言解析器、网页观察器或实时账单验证器。不晚于最新实际冲突提示、早于较新订阅证据的回复，以及历史导入、错误目标、缺失/矛盾/不支持的结果均不改原状态。精确同 episode 的重试不刷新时间、重写后来事实或开启购买；新冲突有新标识，不能重用旧解决。原始快照在后来 P02 被覆盖后仍保留。真实中断的 resume_review 独立存在，解决订阅冲突不替其他保留事实完成复核。记录实际购买完成也不能自动解决重复订单/目标矛盾。

同账号切换任务或设备保留未解决记录；无关 environment/network/cleanup 只使其休眠，回到依赖购买时重新阻断。新账号不继承另一账号的记录。CLI 新增 `--subscription-conflict-file` 与 `--subscription-resolution-file`，其他回答、加载、显式私有保存和输出规则不变；stdout 只给不含原始来源的复核状态/episode_id，原证据只进获准私有状态。旧严格读取器可能拒绝新可选字段，需升级读取器，不能剥除记录以伪装就绪。所有事实、标记及重试都不构成 PC 接触、支付、清理、保存或其他真实操作授权。

### 仅在实际问题需要时确认当前套餐（T84）

Q-C13 是新增的派生实现 ID；原文 ID、Q-C08 目标套餐和 Q-L02 系统/架构问题不变。只有明确当前已有订阅，并且 network/environment/cleanup 的具体客户端功能问题确实依赖套餐时，宿主显式设置可选 `plan_compatibility_needed=true`。普通网络/清理没有这个条件，不问当前套餐，也不展开支付问卷。仅有技术熟练度、设备、付款渠道、目标套餐或此标志，都不能证明当前权益。

问一个短问题：“为判断这次具体客户端功能的套餐依赖，当前订阅是什么套餐，涉及哪项功能？”已明确的当前套餐直接复用，不能复制 Q-C08。Q-C13 使用标准事实信封、账号绑定、独立来源/观测时间；reported/observed 的非空套餐描述可补足这项信息，不验证套餐在售或该功能可用，禁止 inferred 权益，也不接受目标选择专用的 selected_unspecified 充当当前套餐；不知道名称用 unknown。未知/拒答/延期保持空值并停止自动重复；当前依赖仍为条件建议。只延期这项可用 `defer_branch(state, "compatibility")`；不阻断无关网络说明或清理清单规划，实际清理仍过自己的保护与操作门禁。not_applicable 不能在依赖标志仍为 true 时冒充套餐已知；若实际无此依赖，宿主应撤销该条件。

每次改变任务或 `begin_task` 都清除该标志，新问题由宿主重新确认是否相关；同账号换设备可保留有效套餐事实，新账号不继承。订阅阶段变化、订阅事实失效、实际订阅冲突或报告购买完成使旧 Q-C13 陈旧并保留原来源/时间，不能从新目标猜已生效套餐。历史相同证据重放不能恢复陈旧事实；更换来源或导入另一份较新快照也不能解除已有的陈旧义务，不重置已经消耗的澄清次数；早于最新订阅阶段观测的导入同样保持陈旧。当前新答复可按真实来源更新；不要将历史导入伪装成当前答复。精确重放同一购买完成来源/时间/状态时不重置随后已经给出的新套餐、任务或条件。真正中断后的分组复核包含已保留的当前套餐，即使依赖暂未展开，避免稍后打开条件就使用漏审的旧事实。新任务或同账号换设备不能通过丢弃未解决的复核来复活旧套餐：相关旧 Q-C13 保留但标为 stale。无需为此重新问整套订阅/支付问卷。

该上下文键在默认输出中省略，旧 schema-1 状态仍接受。`complete_purchase` 仅在实际报告完成后另留可选 `purchase_completion`，内容限账号别名、来源、观测时间和是否 observed；它是同账号生命周期去重记录，不是账单核验、交易号、订阅资格或权限。普通 J01 自述即使来源/时间相同，也不冒充已经处理过的完成事件。同一完成证据跨新任务/同账号设备重放不改变后来的任务、订阅或套餐；旧于已保留完成记录或同时间矛盾的元数据拒绝，不能复活已到期状态。新账号不继承；历史完成记录不能覆盖更晚的订阅/套餐观察。包含新键、Q-C13 或完成记录时，旧的严格读取器可能拒绝，须同步升级读取器，不能剥除未解决事实来假装就绪。CLI 直接沿用 `--context-file` 的布尔字段、`--answer-file` 的正常 Q-C13 回复和原有批准私有保存/续接路径，没有旁路。完成 Q-C13 不建立真实功能兼容性；在 PC0 只复用已提供自述/获准快照，不能让用户打开 Claude 查询权益，需实时资料时保留待获准核验。事故、no_cleanup、暂停始终优先，G3 和所有接触/操作权限不变。

用户说“套餐已选好”但未提供名称时，宿主将Q-C08记录为`reported`、保留值`selected_unspecified`，同时吸收本轮其他明确事实；不得猜成Pro/Max，也不把已选误写成尚未决定。仅在目标套餐适用且身份仍缺失时，同一Q-C08最多澄清一次：“你已经选好套餐；具体是哪一个套餐？”这不是重问是否选好。该值保留选择事实但不能满足套餐身份或G2就绪。直接调用接口的宿主在实际送达后调用`mark_asked`消耗既有澄清次数；CLI在完整有效的当前回复确实回答正在等待的Q-C08身份澄清时消耗次数，普通套餐问题或无关回复不消耗这次身份澄清。仅输出/读档不消耗或重置次数，重复未命名回复也不重启循环。之后明确给出名称则正常替换；若明确未知、拒答或延期，沿用该字段的空值状态替换契约并停止追问，不声称还保留先前完整值。若名称早已在有效上下文中明确，复用其原来源/时间，不用这句未命名回复覆盖它。宿主负责上述自然语言归一化；脚本不解析自由文本、不验证套餐当前可售或授权购买。

The local route is a proposal until accepted. Record `explicit_choice`, `task_context`, or `accepted_default`; an unaccepted default stays `default_proposal`. Do not infer a route from expertise or owned equipment.

Q-C05未回答、跳过、未知、拒答或延期时，保留未确认的候选；只给路线比较或带缺口的初步建议，不按本机开始部署，也不把停止追问当作已接受。仅说“我是老手/用过”由宿主标记`ambiguous_experience=true`，当前订阅仍unknown，用Q-J02简短澄清一次；熟练度只改变讲解深度。未知/拒答/延期后不重复追问，不能猜成当前付费。

明确已有订阅且只查本机环境时，一轮吸收订阅阶段、environment任务、系统与local选择，复用已知事实，不问新目标套餐或付款渠道。`purchase_intent=none`与`payment_intent=none`表示本次未处理购买，不表示没有订阅。旧保存记录中的任务标签按当前明确任务归一化，不改订阅证据的来源/时间；同任务的已完成购买仍保留completed，明确新任务由`begin_task`重置其任务标签，不拿旧目标套餐作新购买目标。

凭据泄露/当前停用优先进入最小事故分流；`emergency_deferred_branches`只列因事故暂缓的其他未完成主题，区别于用户主动延期的`deferred_branches`，不修改其已答事实。泄露使用原Q-H01—Q-H07的凭据语境，仅问类别、服务、脱敏迹象、受影响组件与已有保护状态，不问秘密值、无关账单或退款；未知/拒答/不适用可直接记录。发现泄露立即停止助手自己尚未发送的重试和新请求，说明官方保护入口与影响；不等七题答齐才给保护建议。实际撤销凭据、停止用户任务、退出会话或接触服务仍按独立权限处理，不能借紧急状态打开G3或接触门禁。按[事故处理卡](incidents-and-integrations.md#incident-triage-m12)先给最小必要指导，其他细节只在依赖它的步骤补充；只有明确报告本次事故已处理后才恢复此前任务，不把未知/拒答当作事故解决。

## Fact states and gates

Keep value, state, source, target alias, observation time, applicability, required gate, and missing-evidence reason together. States: `unasked`, `reported`, `observed`, `inferred`, `unknown`, `declined`, `conflict`, `stale`, `not_applicable`. Unknown/declined are not false. Never infer actual residence, payment eligibility, subscription status, bans, or authorization.

- **G1 interview coverage:** every applicable branch handled; unknowns visible. Complete, partial, paused, blocked, or emergency-deferred are distinct outcomes
- **G2 personalized plan:** enough current target, task, route, network/resource/payment/protection facts to plan; otherwise issue a conditional plan
- **G3 action:** exact proposed change or purchase, current prerequisites, scope/price, specific authorization, supported capability, and necessary recovery. Preview operations cannot satisfy execution capability simply by receiving approval

解释现有访谈辅助器的汇总时，分别说明字段覆盖、具体路线可行性与动作权限。`reported` 的明确否定仍是已回答事实；例如 Apple 登录/验证不可用可与 G1=`complete`、G2=`pass`、`conditional_plan_only=false` 同时出现，这不自相矛盾，也不验证 Apple 路线可行。保留原返回值和否定事实，说明缺失前提只阻断依赖它的购买步骤；不要改成 unknown、把 G2 重写为 blocked，或据此诊断自动购买/执行缺陷。G3、接触阶段及具体动作授权仍须分别满足；独立合成报告的 PC2 标签不能替代当前会话状态或真实交接。

These gates do not replace PC-G1/PC-G2. When a purchase is later completed, update the current state and stop treating the user as still awaiting purchase. Old Q-C08 answers must not silently become new target-plan answers.

## Interruption and resume

真正中断后继续同一任务时，Agent 必须先调用 `resume_interview(state, resume_id=...)`，CLI 使用 `--input <已批准保存的状态> --resume <本次事件别名>`。普通 `loads_state` / `--input` 只是读档或连续轮次，不代表发生中断；不得每轮重启审查。已有 `paused=true` 不能直接改为 false 绕过续接。

保留当前任务的 VM/VPS 选择、原事实来源/时间、保护要求和已发生接触阶段，不能恢复成本机默认值或“从未接触”。尚未接受的本机仍只是候选。事件别名只用于本次重试去重，不是秘密、用户授权或设备身份凭据；宿主为每次真正的新中断使用新别名。

向用户展示一次 `resume_review_prompt` 的相关分组摘要：还是同一目标设备/账号吗，已记录的系统/版本、网络与测试、当前路线资源/访问/共享/恢复、登录和使用地区是否变化；订阅阶段只在本次购买/账单任务相关时纳入；已保留的 Q-C13 当前套餐单独作为功能依赖复核，不开启支付问卷。范围包含本路线已记录但尚未展开的条件项，不能因稍后激活某个分支而把旧事实当成新事实；不询问详细地址、凭据或全部问卷。没有可复用的相关环境事实时不加空审查门槛。

当前回答通过 `record_resume_review` / `--resume-review-file` 归一化记录。回答没变保留旧观测时间，另存本次 reported 复核的来源和时间，不能升级成设备实测。回答变化时仅使所报、属于本次范围的稳定字段 ID 失效，再补相应原题；不得失效路线选择、已选套餐、保护选择或动作权限。未知、拒答、稍后再说都停止自动重复此提示，保留条件建议；后续由用户主动补充或更正。已知换目标需 `begin_task` 显式重新绑定；只有用户明确更正“刚才说错，仍是原设备/账号”才能用新的当前回复解除该状态。

未回答或未解决的审查阻止 G2 个性化就绪；通用/条件指导与紧急事故分流仍可进行，紧急事故优先。已完成购买的同会话状态转换不制造新中断；尚未解决的相关环境或目标变化仍保留。复核、路线选择和保存的记录都不能打开 G3、PC-G1/PC-G2 或任何实际操作许可。

宿主须区分当前回复与历史导入：`record_facts` 的整批输入、以及未提供 `observed_at` 的 `record_fact` 表示明确的当前回复；提供 `observed_at` 的 `record_fact` 默认是保留证据日期的历史导入，不能因记录更新就当作本次回复。只有宿主确实正在归一化一条新的当前答复时，才能显式用 `current_reply=True` 保留其真实观测时间；此严格布尔参数只是可信宿主对输入来源的区分，不验证用户、证明新鲜性或授权任何行为，不能将旧快照重标为当前答复。早于最新订阅阶段观测的 Q-C13 仍不得恢复当前性。不能把历史日志放进当前回复接口来伪造新鲜性。读档、输出或续接事件/复核回复的幂等重试不得刷新事实时间、重获保存同意或将旧记录自动标成已观察；不存在任意 TTL。CLI 先开始真正续接，再处理上下文和本次复核，再吸收本次字段答案，整轮验证失败不保存部分状态。

## Stable question IDs

The following are short prompts/field meanings, not a mandatory sequence. Preserve IDs in progress records. Q-C07 remains a retired tombstone only, never an active question or missing field.

### Core and OS

| ID | Ask or establish only when missing and relevant |
|---|---|
| Q-J01 | First-ever subscription, returning after expiry, currently subscribed, or uncertain? |
| Q-J02 | Clarify ambiguous “experienced/used it before” into current subscription stage |
| Q-C01 | Current goal and Web/Desktop/Code use |
| Q-C02 | Mac or Windows, after subscription stage; alias Q-OS01 |
| Q-C03 | Reported suspension history versus ordinary errors |
| Q-C04 | Existing registration and reported login state; do not open Claude in PC0 |
| Q-C05 | Accept local recommendation, choose VM/VPS, or compare |
| Q-C06 | Existing authentication category; skip unregistered users; no credentials |
| Q-C08 | Desired subscription plan or need for comparison |
| Q-C09 | Actual country/region of use and relevant travel; no street address |
| Q-C10 | Desired explanation depth |
| Q-C11 | Current subscriber's renewal, upgrade, environment, or incident task; explicit expired legacy-bill task uses host context |
| Q-C12 | Data, projects, clients, or settings that must be preserved |
| Q-C13 | Derived implementation ID: account-bound current plan only for an explicit actual plan-dependent technical/cleanup question; never the desired plan |
| Q-OS01 | Same fact as Q-C02, never ask twice |
| Q-OS02 | Windows version and Edition, distinguishing Single Language |
| Q-OS03 | macOS version; architecture only when needed |
| Q-OS04 | Display language, input method, locale, browser, or app language? |
| Q-OS05 | Exact single-language restriction message, only for display-language trouble |
| Q-OS06 | Timezone symptom: disabled control, error, or reverting value |
| Q-OS07 | Automatic-timezone setting and management/privilege constraints |
| Q-OS08 | Wrong absolute time versus timezone display |
| Q-OS09 | Actual need for a language/timezone change versus usability check |
| Q-OS10 | Windows 10 maintenance/ESU/migration arrangement when relevant |
| Q-OS11 | macOS system-wide versus app-specific setting goal |
| Q-OS12 | Out-of-scope desktop/mobile-only: general guidance (see mobile-guidance.md) or voluntary VM/VPS comparison |

### History and network

| ID | Conditional fact |
|---|---|
| Q-H01 | Which account/service/card/client is restricted? |
| Q-H02 | Relevant event date and recovery status |
| Q-H03 | Sanitized exact error or notice |
| Q-H04 | What action immediately preceded the symptom? Record sequence, not cause |
| Q-H05 | Relevant device/client/environment/billing channel |
| Q-H06 | Pending appeal, identity review, refund, or official request |
| Q-H07 | Prior cleanup/reinstall/configuration changes and data to protect |
| Q-H08 | Relevant reused/changed device/network/payment categories; no blacklist inference |
| Q-N01 | Direct, proxy/VPN, or organization network |
| Q-N02 | Browser, Code, and proxy locations and interception mode |
| Q-N03 | Network switching and intended stable workflow |
| Q-N04 | Other devices and their actual roles |
| Q-N05 | Existing test's date, program, target, and scope |
| Q-N06 | Organization network, certificate, security, or management constraints |

### Payment branches

| ID | Conditional fact |
|---|---|
| Q-P01 | Subscription versus API/third-party billing only if ambiguous |
| Q-P02 | Relevant old plan/channel/order; not a first-subscriber default |
| Q-P03 | Available payment device categories |
| Q-P04 | Available store balance/card/company payment category |
| Q-P05 | Budget when comparing or addressing a price conflict |
| Q-P06 | Choice among actually feasible channels |
| Q-P07 | Future renewal/billing/cancellation guidance |
| Q-A01 | Accessible iPhone/iPad versus Mac-only redemption capability |
| Q-A02 | Apple account sign-in/verification availability; no ownership survey |
| Q-A03 | Actual App Store storefront region |
| Q-A04 | Official app and desired in-app plan entry; defer live check until handoff |
| Q-A05 | Correct target Claude account correspondence, post-contact |
| Q-A06 | Conditional old-order issue; same gate as Q-P02 |
| Q-A07 | Gift-card status, formal type, issuing region; no code |
| Q-A08 | Checkout total coverage and additional payment requirement, post-contact |
| Q-A09 | Seller/source verification if buying a card |
| Q-A10 | Renewal and, only if changing region, effects on other Apple services |
| Q-G01 | Android plus usable official Play/store app |
| Q-G02 | Google sign-in availability, Play region, payment category |
| Q-G03 | Actual plan and payment entry, deferred until contact |
| Q-G04 | Target Claude account match; old-plan questions retain Q-P02 gate |
| Q-G05 | Renewal guidance; deduplicate Q-P07 |
| Q-W01 | Card category and issuing region; no number/BIN required |
| Q-W02 | Ability to supply truthful billing details privately at checkout |
| Q-W03 | Online/recurring support and relevant decline/verification symptom |
| Q-W04 | Actual total, billing period, and renewal commitment |
| Q-I01 | API platform and billed organization/project |
| Q-I02 | Specific project usage/payment authority, only for organization tasks |
| Q-I03 | Personal development versus service for others |
| Q-I04 | Budget, cap, and alert goals |
| Q-E01 | Actual enterprise settlement need |
| Q-E02 | Responsibility for enterprise verification/payment/maintenance |

### Environment and delivery

| ID | Conditional fact |
|---|---|
| Q-L01 | Existing client installation method/version, without launching it |
| Q-L02 | Relevant OS/architecture compatibility, reusing known OS |
| Q-L03 | Active MCP/plugins/hooks/gateway components |
| Q-L04 | Local project, software, GUI, or hardware dependencies |
| Q-L05 | Management and allowed changes; reuse Q-N06 |
| Q-V01 | Existing/new VM and hypervisor |
| Q-V02 | Separate host/guest OS and architecture |
| Q-V03 | VM resources and protected projects |
| Q-V04 | VM networking and proxy location |
| Q-V05 | Shared folders, clipboard, tool and credential mounts; no secret values |
| Q-V06 | Snapshot/backup and restore scope |
| Q-V07 | VM guest OS: omarchy / macos / other (default Omarchy; macOS guest on a Mac host); see [vm-guidance.md](vm-guidance.md) |
| Q-V08 | VM NIC mode: lan_bridged / shared_nat / other; the LAN independent NIC is preferred over host-shared NAT, chosen before the VM is created |
| Q-V09 | VM reachability: direct / remote_unreachable; remote_unreachable (target behind another network or NAT, managed through a reverse tunnel) attaches the advanced route, see [advanced-route.md](advanced-route.md) |
| Q-S01 | VPS as a development machine (Claude Code runs on it); a proxy-exit-only VPS belongs to the local route egress choice (egress-ip-options.md) |
| Q-S02 | Existing/new server, region, OS, and resources |
| Q-S03 | SSH access and independent rescue channel; no keys/passwords |
| Q-S04 | Production workloads and unbacked-up data |
| Q-S05 | Remote-data acceptability and local dependencies |
| Q-S06 | Server, traffic, and maintenance budget if needed |
| Q-S07 | Terminal/Remote-SSH/remote-browser workflow and maintenance |
| Q-S08 | VPS exit: vps_own_ip / residential_chain / undecided; selects the firewall script and whether R02 applies, see [vps-guidance.md](vps-guidance.md) |
| Q-Z01 | Explanation/plan versus authorized target read scope |
| Q-Z02 | Detailed preservation scope; reuse Q-C12 |
| Q-Z03 | Specific proposed changes and administrator requirements |
| Q-Z04 | Backup/rollback/rescue prerequisites |
| Q-Z05 | Permission for private sanitized persistence/export |


## Route, egress source and mobile (ADR-018)

Categorical facts that make the route-specific guidance deterministic instead of leaving it to the host alone. Values are listed in `interview_flow.ROUTE_EXIT_VALUES`; an unknown or declined answer is a fact state, not a value. An answer is never an action authorization.

| ID | Meaning and trigger | Binding and effect |
| --- | --- | --- |
| Q-X01 | Source of the fixed egress IP: airport / self_built / residential_carpool / existing_stable_exit / undecided. Asked after an explicit local or VM route choice. | Selects [egress-ip-options.md](egress-ip-options.md); airport and carpool get no tutorial, self-built gets the short prompt and the R01 VPS reports. Stale when the route changes. |
| Q-X02 | Self-built relay with a residential exit: with_residential_exit / own_vps_ip_only / undecided. Asked only after Q-X01 = self_built. | With a residential exit, attach R02 ([line-optimization.md](line-optimization.md)). |
| Q-T01 | Current line problem: none / evening_slow / drops / slow_transfer / desktop_lag / wrong_exit. Asked for an explicit VPS route, or after a self-built choice (Q-X01) on local or VM. | Anything but none attaches [line-optimization.md](line-optimization.md) and R02 (R01 for evening_slow or drops). |
| Q-M01 | Whether registration, login or in-app purchase happens on a phone: ios / android / both / none. Asked for Apple or Google in-app purchase, or when the OS is mobile only. | Attach [mobile-guidance.md](mobile-guidance.md) and S03 page 4; Android includes the SIM note. |

Q-V07, Q-V08 and Q-V09 (VM) and Q-S08 (VPS) in the tables above follow the same rules. Route-specific questions are asked only after the route is explicitly chosen, never from the default proposal.

Tiered authorization records (scope, tier-B plan approvals, tier-C confirmations) live in an optional `authorization` section of the state, written only through the `record_*` and `*_critical_confirmation` functions with a `user:` source; see [authorization-tiers.md](authorization-tiers.md). Interview answers never create them, and `assessment()` only summarizes them.

`assessment()` turns these answers into `required_references` (ADR-019): the ordered owner materials the answer must attach, computed by `required_references(state)` from the task, billing channel, journey, OS and the facts above. It mirrors the SKILL.md attachment table and is never an action authorization.

## Selected-device history and explicit cleanup task

| ID | Meaning and trigger | Binding and effect |
| --- | --- | --- |
| Q-D01 | Selected device's explicitly restricted-account use: current_restriction_on_target / past_restriction_on_target / ordinary_error_only / other_device_only / none_reported; unknown/declined are null-valued fact states. Automatically ask when Q-C03 past_suspension is reported and this device fact is absent; explicit reset does not depend on it. | Selected target alias, never inferred from account history or first subscription. A current device event requires bounded incident clarification; it does not mark the selected account suspended. When the device has a restricted-account history, the Agent also asks how many accounts were banned on it and applies [A0 item 11](account-onboarding.md) (more than 3: stop using the device). |
| Q-D02 | audit_only / full_claude_data_reset / other_scope / no_cleanup. Record an already explicit request without asking again. | Selected target and current task only. Fresh task/route/target checks and resume review apply. Goal selection grants no filesystem or operation permission. |

A cleanup-only task asks only relevant target/client/OS, goal, preservation and check/change/recovery scope. It does not require payment or general subscription answers. The sole current-plan exception is the separately scoped Q-C13 dependency above, only for an explicitly existing subscriber and an actually plan-dependent client question; it is never a prerequisite to unrelated cleanup planning. `no_cleanup` ends cleanup questions. Unknown/refusal/defer remains bounded; urgent incidents retain priority. Current selected-account status stays separate from the identity of an account previously used on the device.


### Device-only triage resolution

When D01 truthfully says this device used another account that is currently restricted, retain that category and the selected account's independent C04 status. After bounded clarification, the host may explicitly report `set_context(state, device_incident_resolved=True)`. This closes only device-episode triage; it is bound to the current D01 fact's target/provenance/time/category, and grants no action permission. New device/route/namespace or actual episode evidence invalidates it. A task-only change retains informational resolution for the unchanged bound episode, clears obsolete cleanup intent and suppresses re-offering that same episode; fresh history or an explicit cleanup request can reactivate planning. Account suspension, credential exposure and data-risk incidents remain governed by their separate existing resolution state. Exact old-evidence replay cannot reopen the episode; a fresh report can. Do not tell the user to falsify D01 as past merely to proceed.

<a id="topic-references"></a>
## Conversation topics without the questionnaire (#21)

For each new user reply, the host maps the actual subject to normalized topics and calls `references_for_topics(topics, os_name="windows")`, or runs:

```sh
python scripts/interview_cli.py --references-only --topics suspension trace_cleanup ip_quality --reference-os windows
```

This pure route needs no interview state, answers or network; reference-only mode never saves. Topics are payment, registration, suspension (封号), identity_review (KYC), cleanup (清理), trace_cleanup (旧 IP 痕迹), ip_quality (IP 质量), local_protection, whole_machine_egress, line_optimization, vps, vm, mobile, egress, remote_assistance and illegal_tools. The host identifies meaning, not blind substring matches. New topics trigger in emergencies and long conversations too. Payment stays first, duplicate paths and locators merge. Checklist references require an execution report; see [source-library.md](source-library.md).

With an existing interview, `--topics` retains normalized topics in optional `reference_topics`; `required_references` combines these with interview facts. The conversation router is independent of question scheduling, and remains usable when interview questions are skipped. Platform-specific cleanup follows the target OS; unknown OS lists candidates until clarified.

Optional target `capabilities` and `work_items` records, JSON fields and private persistence rules are documented in [agent-remediation.md](agent-remediation.md#handoff-and-follow-up). `assessment.follow_up` shows unfinished handoffs; the CLI sets `next_step: review_follow_up` before further planning and prioritizes `blocking_next_session` acceptance items whenever state is read or resumed. These are obligations to revisit, not permission to execute.

## Workflow record formats and dependency preparation

### Target capability observations

在目标机核对系统、架构、Python 版本及随包脚本是否齐全，不能用管理机结果代替。先读 [scripts-index.md](scripts-index.md)，有 Python 后运行：

```sh
python scripts/inventory_cli.py capabilities
python scripts/network_check.py --help
python scripts/egress_verifier.py --help
```

`inventory_cli.py capabilities` 主要报告配置盘点支持范围，不能据此断言 Windows 不支持网络检测。网络检测和判定脚本支持三平台。Python 要 3.10+；Windows 用 `py -3` 或已核实的解释器路径，确认不是仅打开商店的命令别名。

**目标机缺 Python 必须补齐，然后使用我们的脚本。**先说明官方安装来源、目标用户或全机安装范围、权限、磁盘与 PATH 影响、卸载恢复方法，按分级授权安装；未获准、安装失败或权限不足就记录检测未完成，解决依赖后重跑，不用手写 PowerShell/curl 替代验收。历史安装命令见 [S10 第十节](../sources/S10-windows-deployment-sanitized.md#network-evidence)，其中旧版本、第三方镜像、全机安装与 SYSTEM 不是默认方案；当前步骤核实 Python 官方安装方式和实际架构，不照搬历史命令。

能力结果用 `interview_cli.py --capabilities-file <私有JSON>` 写入可选 `capabilities` 段，即使跳过问卷也可新建仅用于记录的状态。字段为 `target_ref`、`platform`（macos/windows/linux/unknown）、`python`、`network_check`、`egress_verifier`（各 available/missing/unknown）、`source`（脱敏观察来源）。记录实际目标机观察；可用不表示检测已通过。路线、设备或依赖变化后重查。

检测固定链路为：目标机 `network_check.py run --evidence-output <私有证据JSON>` → 按 [whole-machine-ipv4.md](whole-machine-ipv4.md)补配置读回和浏览器证据 → `egress_verifier.py check --input <证据JSON>`。故障演练仍先核实授权与独立恢复，缺项保留 unknown/not_run。

### Handoff and acceptance records

任何动作交给用户手动执行前都给交接单：**准确范围、影响、前置依赖、完成后回传什么**，并带备份与恢复办法。前置依赖必须由 Agent 在转手前按原授权完成；做不了先说明阻塞，不让用户先卸载或删除导致检查机会丢失。例：卸载代理客户端前，先按 [trace-cleanup.md](trace-cleanup.md)核对旧出口痕迹，再交接卸载；原清理场景的备份和隔离要求继续见 [windows-cleanup.md](windows-cleanup.md)。

私有访谈状态新增可选 `work_items`，通过 `interview_cli.py --work-item-file <私有JSON>` 新增或以同一 ID 更新：

```json
{"id":"client-uninstall","target_ref":"device-a","kind":"manual_action","status":"pending","scope":"selected-client","impact":"remove selected client","prerequisites":[{"check":"inspect old exit traces","status":"pass"}],"return_evidence":["uninstall result"],"reason":"user handoff","blocking_next_session":false}
```

`kind` 为 manual_action/acceptance，`status` 为 pending/completed；前置项为 pass/not_run/blocked。只有实际完成才记 completed，前置项没通过不能记完成。完整交接内容只保存在用户批准的私有状态中，CLI 摘要只给 ID、类型、状态和提醒标志。

会话中事故、验收降级或跳过留下的验收／演练，收尾必须登记 acceptance 待办，写清范围、未做原因、恢复办法（写入 impact）和下一步需要的证据；未完成时自动设 `blocking_next_session: true`。开局、读档和恢复时先查看 `assessment.follow_up`，先提示并优先处理这些项；普通手动待办也要提醒。提醒不授权执行：可能断网、接触 Claude 等仍按对应档位确认；用户本轮不做就保留待办并说明相关验收未完成，不挡无关任务。完成后用同 ID 更新为 completed，不能靠确认提醒或重开会话清除。

仍须用户明确同意才通过 `--output` 保存，不自动写磁盘。没有获准保存，收尾把待办交给用户留存；新会话无旧记录时先索取待办摘要，不能声称已自动找回。旧状态没有这些字段仍可读取。
