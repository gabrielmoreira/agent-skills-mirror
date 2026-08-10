# 结构验证契约

## 契约版本与权威

当前权威 validator 是 deployed `skills/distill-concept-books/scripts/validate_distillation.py`，
其 Gate 3 approval snapshot 契约固定为 **`gate3-approval-snapshot:v2`**（绑定最终候选树、
三份权威知识 YAML、current Gate 1、task contract、coverage 与 candidate stable task IDs）。

历史冻结 lineage `distillations/concept-book-distiller-v1/distill-concept-books/scripts/validate_distillation.py`
使用 **`gate3-approval-snapshot:v1`**（仅绑定候选树与三份知识 YAML）。它是旧 lineage 的
历史契约，**不随 deployed skill 自动升级**；任何沿用 v1 快照的已有审批记录仍按其 v1
语义解释，不强制改写为 v2。

规则：

- 新建或恢复蒸馏、且要获得当前 Gate 3 批准的候选，一律使用 deployed v2 契约；
- 已存在的 v1 lineage 记录保持 v1 语义，作为历史冻结，不静默改写；
- 两套脚本字节不同、契约版本不同，是**预期的版本分层**，不是冲突；谁在运行就以谁的
  版本为准，且版本必须与目标 distillation 的既有 snapshot 契约一致。
- 任何对 deployed validator 的修改都必须登记到其 owning distillation 的治理记录中，
  否则视为未授权漂移。

## 文件布局

完整治理契约包含：

- `evidence-ledger.yml`：`schema_version`、`distillation_id`、`evidence`、`claims`；
- `concept-map.yml`：`schema_version`、`distillation_id`、`relations`；
- `capability-rules.yml`：`schema_version`、`distillation_id`、`capability_rules`，以及可选 `skill_candidates`。
- Gate 1 snapshot 指向的 `task-contract.yml` 或 `task-contract.vN.yml`：不可变产品任务合同；
- `task-coverage.yml`：stable task 到 candidate/rule/eval/holdout/rubric 的覆盖矩阵；
- `gate-decisions.yml`：`schema_version`、`distillation_id`、`gate_decisions`、`materializations`；
- `eval-runs.yml`：`schema_version`、`distillation_id`、`eval_runs`；
- `correction-overlay.yml`：仅在存在缺字、OCR、转换、翻译或术语 issue 时必需。

所有存在文件的 `distillation_id` 必须相同。`schema_version` 必须是整数 `1`；字符串
`"1"`、浮点数 `1.0` 和布尔值 `true` 都不合格。每个列表可以暂时为空，但键必须
存在。`skill_candidates` 只能出现在 `capability-rules.yml`。YAML 中不得使用自定义
对象标签、重复 mapping key 或递归 alias；评测 JSON 同样拒绝重复 object key 与
`NaN`/`Infinity` 等非标准常量。

项目 validator 必须读取 Gate decisions、eval runs 和适用的 correction overlay，并将
缺失或不一致作为错误。即使 PASS，也不得声称知识真假、语义支持充分性、版权许可或
行为效果已经由机器证明。

## ID 与外键

所有 `evidence_id / claim_id / relation_id / rule_id / candidate_id / decision_id /
materialization_id / eval_run_id / correction_id` 必须为非空、无空白的稳定字符串，
首尾不得带空白，并在整个蒸馏目录中唯一。验证：

- claim → evidence；
- relation → claim/evidence；
- rule → claim/relation；
- skill candidate → rule；
- Gate decision → candidate/eval run/rule decision，以及同系列被取代的决定；
- materialization → candidate/Gate 3 decision/rule；
- eval run → candidate/materialization/rule；
- claim → correction（若使用修正解释）。

## Locator

每个 evidence 只使用一个主 `locator`，并只锚定一个 block、figure 或 table。跨块主张应拆成多个 evidence，再由 claim 引用多个 `evidence_ids`；不使用复数 `locators`。

`locator` 必须包含与 evidence 相同的 `source_id` 和 `locator_type`。`ooxml-block` 还必须包含 `heading_path`、`ooxml_block_index` 和 `content_hash`。其他类型必须提供非空 `anchor` 和 `content_hash`。出现 `locators` 或 `related_locators` 时验证失败，不得同时保留单数和复数字段。

显式提供来源 manifest 时，`markdown-section` locator 还会按
`path:N[-M][#heading]` 解析。`path` 必须是项目内相对路径，并且必须逐项出现在该
`source_id` 的 `local_path` 或 `related_local_paths`；绝对路径、`..`、未登记路径、
symlink 逃逸和全项目模糊搜索均不允许。目标必须是可读取的 UTF-8 普通文件。

`raw_text` 与 `normalized_text` 必须分别逐字符存在于该文件；指定 heading 时还必须位于
对应 ATX Markdown section。验证不 strip、不折叠空白、不做近似匹配，只采用文本读取时
的通用换行归一。重复文本必须能由 section 与 line hint 唯一消歧，否则返回
`LOCATOR_TEXT_AMBIGUOUS`。`content_hash` 是精确匹配到的 `normalized_text` 来源片段之
UTF-8 SHA-256 前缀，而不只是 ledger 字段之间的自洽检查。heading、来源文本或 hash
漂移均为错误；唯一内容仍可解析但行号发生插入漂移时只报告
`LOCATOR_LINE_HINT_DRIFT` warning，非法或越界行号仍为错误。

显式 manifest 以及实际参与上述 locator 校验的 allowlisted Markdown 源文件必须经
stable、no-follow 读取进入同一私有不可变 bytes snapshot；validator 与状态检查器只消费
该 snapshot。manifest 或源文件为 symlink、读取中变化，或发生 A→B→A 回切时均 fail
closed，不能把不同时间点的治理、manifest 与来源内容拼成一次 PASS。

## 状态与人工决定

知识状态限定为 `candidate / accepted / reference-only / needs-verification / rejected`；Skill 生命周期限定为 `draft / review / accepted / deployed / deprecated / rejected`。

T3/T4 claim 或 rule 必须具有：

```yaml
human_decision:
  decision: pending | accepted | revised | rejected
  reviewer_type: null | user | human-delegate
  reviewer: null | string
  decided_at: null | string
  rationale: string
  gate_decision_id: null | string  # capability rule 必需；claim 不使用此字段
```

pending 决定保留空 reviewer metadata；非 pending 决定必须记录人工 reviewer type、
reviewer、时间和理由。处置为 `accepted` 时，decision 必须为 `accepted` 或 `revised`。
accepted T3/T4 rule 还必须回链当前 Gate 3 `approved-for-eval` 决定。

验证器检查 `status_history` 和 `lifecycle_history` 事件连续、转换合法、最终状态等于当前状态。所有 accepted evidence/claim/relation/rule 必须具有完整 `status_history`；所有非 draft Skill candidate 必须具有完整 `lifecycle_history`。其他记录没有 history 表示未声明历史转换，不会由工具臆造。

`implicit` 或 `inferred` relation 处置为 accepted 时也必须具有非 pending 的
`human_decision`，包括 reviewer、decided_at 和 rationale。`reviewer` 字符串本身不能
证明是人工；此类 accepted 推断关系要求 `reviewer_type: user`，自动 agent 或仅受托的
human-delegate 都不能替用户接受该推断。

## Semantic support

每条 capability rule 使用：

```yaml
semantic_support:
  checks:
    - item_index: 0
      claim_ids: [claim-001]
      relation_ids: []
  action: []
  output: []
  stop_conditions: []
```

四个列表必须与对应 rule 文本列表等长，`item_index` 从 0 开始且不重不漏；每项至少
引用一个存在的 claim 或 relation。accepted rule 的 semantic-support 依赖也必须满足
accepted 追溯约束。该检查证明“声明了逐项支持”，不判断支持是否在语义上充分；后者
仍需人工审核。

## Accepted rule 追溯

每条 accepted rule 必须：

1. 至少引用一个 claim；
2. 所有直接 claim 为 accepted；
3. 每个 claim 至少引用一个 evidence；
4. 所有支撑 evidence 为 accepted 且 locator 有效；
5. 所有支撑 evidence 的 `quality_flags` 为空。任何非空 flag 都会阻止 accepted rule，不根据 flag 名称猜测“不阻断”。

accepted 或 deployed Skill candidate 必须至少引用一条 rule，且所有引用 rule 均为 accepted。should-trigger 和 should-not-trigger 各自不得重复，两组不得交叉。rule 的 `trigger` 和 `output` 不得为空。

## 来源中立投影的审核边界

来源中立方法蒸馏继续使用当前 T3/T4 字段、`semantic_support` 和
`gate3-approval-snapshot:v2`；不增加 Gate 版本或权威 YAML。Gate 3 snapshot 已绑定完整
candidate tree，因而来源中立修订会改变 candidate hash，并必须重新取得精确匹配的 Gate 3
决定。

Gate 3 人工 review package 必须并排展示私有 `rule → claim → evidence` 闭包和候选投影，
检查第一性原理重建是否完整、候选是否无需读取方法来源即可执行，以及 candidate/public
output 是否排除来源身份、出版信息、ISBN、系列/文件名、归因句、引文、locator、私有 ID 和
可识别命名案例。结构 validator 只验证已有字段、外键和 hash，不能自动证明语义重建充分或
发现所有去标识泄漏；人工未确认或发现残留时保持 review/revise，禁止物化和 Gate 4。
manifest 中的方法来源必须显式分类为 method-source/primary-book/supplementary-book 或 book
类型；lint 只从这些记录派生禁用身份，不把 target-material 与 project-policy 身份混入。分类
缺失或冲突时先阻断并修复 Gate 2 来源登记。

若存在译名、转写/romanization、旧或来源派生 slug、系列别名、特有术语或具名案例，完整
private extra-terms 必须同时参与 Gate 3 与 Gate 5 lint；它不是可选增强。manifest 未声明的
语义别名无法自动发现，仍需人工审阅；缺失或覆盖不完整时 fail closed。
详见 [source-neutral-method-distillation.md](source-neutral-method-distillation.md)。

## Gate decisions

`gate-decisions.yml` 每项使用：

```yaml
decision_id: gate-decision-001
sequence: 3
supersedes: null
is_current: true
gate: gate-3
candidate_id: candidate-001
decision: approved-for-eval
scope: [candidate-001]
reviewer_type: user
reviewer: local-user
decided_at: "2026-08-04T00:00:00+08:00"
rationale: 允许物化候选并取得 Gate 4 资格；只有 matching completed materialization 后才可执行，不表示接受。
conditions: []
eval_run_ids: []
rule_decisions:
  - rule_id: rule-001
    decision: accepted
    rationale: 该规则获准进入受控评测。
approval_snapshot:
  contract: gate3-approval-snapshot:v2
  candidate_path: example-skill
  candidate_hash: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  governance_hashes:
    evidence-ledger.yml: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    concept-map.yml: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    capability-rules.yml: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  current_gate1_decision_id: gate-decision-001
  task_contract:
    path: task-contract.yml
    sha256: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    task_contract_id: task-contract-001
    contract_version: 1
    active_stable_task_ids: [stable-task-001]
  task_coverage:
    path: task-coverage.yml
    sha256: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  candidate_stable_task_ids: [stable-task-001]
```

decision 可为 `pending / approved / approved-with-conditions / approved-for-eval / accepted /
revise / rejected / blocked`。pending 可保留空 reviewer/date；其他决定必须具有
`user | human-delegate` reviewer type、reviewer、时间和理由；Gate 3 的
`approved-for-eval` 必须由 `reviewer_type: user` 作出。

`sequence` 在整个文件中从 1 连续递增，记录按此顺序存放。每个 `(gate,
candidate_id)` 系列只有末项 `is_current: true`；系列内后续决定必须用 `supersedes`
指向紧邻的前一决定。Gate 2/3/4/5 只有在当前前置 Gate 为正向决定且顺序更早时才有效。
Gate 3 `approved-for-eval` 必须在 `rule_decisions` 中对该候选的每条当前 rule 恰好决定
一次，并把结果同步写回 rule 的 status、human decision 和 history；pending Gate 3 的
`rule_decisions` 保持空列表。

current Gate 3 `approved-for-eval` 必须绑定 `gate3-approval-snapshot:v2`：候选路径必须是
规范的蒸馏根相对 POSIX 路径，候选 tree hash 使用下述 `candidate-tree:v1`，三份
`governance_hashes` 则是对应权威 YAML 原始 bytes 的完整 SHA-256；还必须绑定 current
Gate 1 decision、task contract path/hash/ID/version/active IDs、task-coverage hash 和 candidate
stable task IDs。validator 会现场复算；
缺失、路径/name 不一致、symlink、文件或 candidate tree 漂移均使 current approval 无效。
历史上已被 supersede 的 approval 可以保留旧 schema，但不能再次提供运行资格。
current `gate3-approval-snapshot:v1` 返回 `LEGACY_TASK_CONTRACT_REVIEW_REQUIRED`，只允许
review/repair；不得原地改写或继续新物化/Gate 4。

Gate 3 只有当前 `approved-for-eval` 才授权 materialization；它只建立 eval 资格，实际执行
仍须 matching completed materialization。Gate 4 `accepted` 必须在记录创建时已经引用
满足下述全部要求的 completed/pass runs；不能先接受再补评测。

`pending / revise / rejected` 和被 supersede 的旧 approval 均按无 approval 处理。review
package 可以包含建议，但不能由 agent 代用户写入权威 accepted 决定。

## Materializations

`gate-decisions.yml` 的 `materializations` 是候选物化的权威记录，而不是从目录存在性推断：

```yaml
materializations:
  - materialization_id: materialization-001
    candidate_id: candidate-001
    gate3_decision_id: gate-decision-001
    status: completed
    candidate_path: example-skill
    candidate_hash: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    materialized_at: "2026-08-04T00:10:00+08:00"
    rule_ids: [rule-001]
    quick_validation:
      status: pass
      validator: quick_validate.py
      validated_at: "2026-08-04T00:11:00+08:00"
      candidate_hash: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

status 只能为 `planned / completed / failed / invalidated / legacy-quarantined`。completed
记录必须绑定当前 Gate 3 approval、完整候选路径/hash/时间、获准的全部且仅这些 rules，
并与 approval snapshot 的 path/hash 完全相同，且具有由 `quick_validate.py` 产生、绑定
同一完整 candidate hash 的 quick-validation pass。Gate 3 前已经存在的旧审阅原型必须登记为
`legacy-quarantined`；它不回填虚假的 approval，也不能支撑 completed eval。

每个 completed candidate 还必须有 UTF-8 `SKILL.md`，frontmatter 恰好只有 `name` 和
`description`，name 与候选记录及目录名一致，正文非空；并包含严格 JSON 的
`evals/trigger-cases.json` 与 `evals/task-cases.json`。前者至少各 3 个唯一 trigger/nontrigger，
每项必须有 prompt 与 expected reason；后者至少 3 个唯一 task、一个 holdout、可执行 request、
输入画像、预期/失败信号，并定义结构化 comparison protocol 与 rubric。case IDs 在三种类型间
不得重复；每个 case 使用规范 JSON 的完整 SHA-256 作为 `case_definition_hash`。

Gate 3 v2 的 eval definition 使用 schema v2：每个 case 明确 stable task/input type IDs 和
`positive_example_ids`/`negative_example_ids`；trigger/nontrigger 只填对应极性，task case
两类都填。所有 example 必须回指同一 stable task 的合同正/反例；rubric dimensions 与 fatal failures 使用稳定
ID。method-transfer 额外要求 provenance-layer-separation、anti-forced-analogy 与
method-source-fact-as-target-fact。

### 输入处理能力声明（method-transfer 强制，其余候选建议）

method-transfer 候选必须在其 task contract（`input_types` 与 `stable_tasks.required_input_types`）
或 candidate 规格中声明**输入处理能力边界**，且该声明必须在 `task-contract.yml` 或候选
规格中可定位。至少包含：

1. **目标材料输入类型**：与 `input_type_ids` 一一对应，明确是 PDF（文本层/扫描）、正文、
   摘要、figure 图像、panel 截图、caption 或组合；仅标题/DOI 不构成可分析输入。
2. **执行模态策略**：当前执行环境是单模态（仅文本）还是多模态（文本+图像）；PDF 需要先
   提取文本才能分析，figure 图像解析依赖视觉能力与用户提供的截图/高分辨率图像。
3. **图像不可读时的降级规则**：当图像分辨率不足、panel 边界不清或仅提供 legend/摘要/正文
   时，figure 细节判断降级为基于文本推断并显式声明，禁止用模型记忆补出目标论文未展示结果。

该声明影响评测设计与激活后行为：fixture 的输入类型必须落在已声明范围内，且
`input_type_ids` 与声明一致。缺少该声明时，method-transfer 候选的 Gate 3 审阅应把此列为
未决项；validator 对已声明的 `execution_capability` 字段（若有）做结构校验，不强制要求
非 method-transfer 候选填写。

### Completed candidate tree hash v1

`completed` materialization 的 `candidate_path` 必须是相对于该蒸馏目录的规范 POSIX
路径：不得是绝对路径，不得含 `..`、`.`、空组件、反斜杠、首尾空白或 symlink 路径组件。
路径最后一个组件必须与所链接 `skill_candidate.name` 完全一致。目标必须是目录；遍历中
出现 symlink、FIFO/socket/device 等非普通条目、`__pycache__` 目录或 `*.pyc` 文件时立即
失败，不跟随也不静默排除。除这些明确拒绝项外，所有普通文件都纳入 hash，包括隐藏
文件；空目录本身不产生记录。

确定性 hash 算法固定为 `candidate-tree:v1`：

1. 每个普通文件使用相对于 candidate 目录的 UTF-8 POSIX 路径；按路径的 UTF-8 bytes
   升序排列。
2. 初始化 SHA-256，依次输入：
   - ASCII domain separator `distill-concept-books:candidate-tree:v1` 后接一个 NUL byte；
   - 文件数的 unsigned 64-bit big-endian 表示；
   - 对每个排序后的文件，输入 `F` 后接 NUL、路径 byte 长度的 unsigned 64-bit
     big-endian、路径 bytes、文件 byte 长度的 unsigned 64-bit big-endian、原始文件
     bytes。
3. 输出必须是小写完整值 `sha256:<64 hex>`。路径、长度和内容均在 framing 中，因此
   文件重命名与 byte 变化都会改变结果；mtime、权限和目录顺序不参与 hash。

validator 对每条 `completed` 记录从本地 candidate tree 只读复算，并与
`candidate_hash` 严格逐字符比对。树在扫描/读取期间变化、不可完整读取或含上述拒绝项
时验证失败。`planned / failed / invalidated / legacy-quarantined` 不触发该复算；特别是
不得借此给旧原型补写一个伪 completed hash。

Activation guard 使用三种正常状态和一个 fail-closed 状态：

1. 无 current Gate 3 approval：仅 review/maintenance；
2. 有 approval、无 matching completed materialization：仅 materialization + quick validate；
3. approval 与**唯一一个** completed materialization 的 candidate ID/path/hash、完整 rules 和
   quick-validation pass 匹配：才允许 Gate 4。存在多个完全匹配记录时也应 fail closed，
   先消除 materialization ID 选择歧义，不能由执行者任意挑选。
4. snapshot、治理、候选、manifest 或匹配关系无效/歧义：`invalid`，只允许修复状态。

候选随附的 `scripts/inspect_distillation_state.py` 只读复用结构 validator 与 candidate-tree
hash，输出 `review-only / materialization-required / gate4-eligible / invalid` 及允许动作。
它只判断 Gate 3/materialization 路由，不判断知识真假、版权许可或行为有效性。输出
`gate4-eligible` 只表示可以开始获准评测，不表示已有 completed/pass eval 或 Gate 4 accepted。

## Eval runs

`eval-runs.yml` 的 run 至少包含：

- `eval_run_id`、`candidate_id`、`materialization_id`、`candidate_hash` 和 `rule_ids`；
- `case_type: trigger | nontrigger | task` 和对应 `case_id`；
- `status: planned | blocked | completed | invalidated`；
- `outcome: null | pass | fail | inconclusive`；
- `fixture_id`、`fixture_path`、`fixture_hash`、`source_ids`、`holdout` 与 `case_definition_hash`；
- 执行环境以及 baseline/with-Skill 输出路径和 hash；
- `rubric_id`、score、max score、pass threshold、逐维 `dimension_scores` 与 fatal failures；
- holdout/答案隔离、两组上下文差异和例外组成的 `leakage_controls`；
- reviewer type/identity、completed time 和 limitations。

completed run 必须具有可重放 fixture、candidate/output hashes、rubric、评分、人工 reviewer
与完成时间；pass 还必须达到阈值。它必须绑定当前 Gate 3 approval 派生出的 completed
materialization，candidate、candidate hash 和完整 rule 集合必须一致。

completed run 的 `fixture_path`、`baseline_output_path` 和 `with_skill_output_path` 必须是
蒸馏根内三个不同的规范相对 POSIX 普通文件；拒绝绝对路径、空/`.`/`..` 组件、反斜杠与
symlink。三个 hash 现场稳定复算。fixture 必须是严格 JSON，并把 fixture/run 的 ID、type、
request、source IDs、holdout 与 canonical `case_definition_hash` 逐项绑定；两份输出也必须是严格
JSON，绑定 eval run、case 与 baseline/with_skill condition。run 的 rubric ID、阈值、最大分、
逐维评分和 fatal failures 必须与物化定义完全一致，pass 不得包含 fatal failure。
planned/blocked run 不伪装执行，因此不触发这些 completed-only artifact 检查。

Gate 4 accepted decision 引用的 runs 必须全部属于同一个 completed materialization，且至少
覆盖 3 个不同 trigger、3 个不同 nontrigger 和 3 个不同 task case；task 中至少一个
`holdout: true`。planned、blocked、invalidated、not-run、legacy-quarantined materialization
或只有测试定义的记录都不能支持 Gate 4。

### Rubric 跨 case 类型适用性契约

rubric 必须能对 trigger、nontrigger 与 task 三类 case 诚实评分。候选在 Gate 3 审阅时
必须显式选择并声明以下两种路径之一（写入 task contract 或 eval definition）：

1. **统一 rubric（全适用）**：同一套 rubric 维度对三类 case 都语义适用；即每个维度都能
   对"路由型"case（是否触发、是否边界内）与"任务型"case（是否完成分析）给出有区分度的
   评分。选择此路径时，Gate 4 的 trigger/nontrigger run 使用与 task run 相同的
   `rubric_id`、`max_score` 与 `pass_threshold`。
2. **分级 rubric（推荐用于 method-transfer）**：trigger/nontrigger 使用独立轻量 rubric
   （如 pass/fail + 范围匹配、边界诚实、安全停止等少量维度），task 使用完整分析 rubric。
   两条 rubric 都必须有唯一 `rubric_id` 并在 eval definition 中定义；run 记录的
   `rubric_id` 必须与对应 case 类型匹配。

禁止"用任务型完整 rubric 硬评路由型 case 并凑出通过分"的做法。若同一 rubric 对某类
case 的维度不适用（例如任务型"因果与 rescue 克制"无法对仅有触发请求的 case 评分），
必须使用分级 rubric，而不是给不适用维度强行打高分。

fixture 缺失、不可重放、权利不足、holdout 污染、泄漏边界不清或未授权的数据目的地是
对应 run 的 blocker。3/3/3/holdout 覆盖不足、拟引用 run 非 completed/pass、无人工评分
或混用 materialization 是 Gate 4 acceptance blocker。一个局部 blocked run 不应使其他
独立 completed run 失去历史。DOCX run 使用 DOCX locator resolver；兼容非 DOCX bundle
必须使用其已验证 locator checker，不得把 DOCX resolver 结果冒充通用验证。

## Correction overlay

每条 correction 保留 evidence 或 source locator、原始值、候选/结果值、依据、状态、
`applies_to_claim_ids`、`resolved_quality_flags` 与 `human_decision`。completed correction 必须
显式记录 `reviewer_type: user | human-delegate`；仅有 reviewer 字符串或 agent 署名不构成人工决定。claim 使用
`correction_ids` 时，ID 必须存在且 correction decision 为 accepted/revised。validator
还必须拒绝用清空 `quality_flags` 代替 overlay 决定的 accepted 支撑链。

## 运行

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/validate_distillation.py /path/to/distillation
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/validate_distillation.py /path/to/distillation \
  --sources-manifest /path/to/manifests/sources.yml
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verify_normalized_locators.py \
  /path/to/distillation /path/to/sources/normalized \
  --sources-manifest /path/to/manifests/sources.yml
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/hash_candidate_tree.py \
  /path/to/distillation relative/path/to/candidate
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/inspect_distillation_state.py \
  /path/to/distillation --candidate-id candidate-001 \
  --candidate-path relative/path/to/candidate \
  --sources-manifest /path/to/manifests/sources.yml
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s scripts -p 'test_*.py'
```

只有显式提供 `--sources-manifest` 时，脚本才读取该 manifest、检查 evidence
`source_id` 存在性，并解析上述本地 `markdown-section` locator；缺省时不扫描项目
来源，也不得声称这些 locator 已对当前政策文件解析成功。Gate 4 和 Gate 5 必须显式
提供 manifest，并另行人工检查 privacy、license、`allow_public_quotes` 和上传/发布
边界；source ID membership 与本地 locator 解析都不是版权审核。当 accepted rule 数为
0 时，`accepted_rule_traceability`
输出 `null`，且 `accepted_rule_traceability_applicable: false`，不将无适用对象伪报为
100%。

对 OOXML evidence，结构 validator 只检查 locator schema。来源解析检查器会稳定、no-follow
读取 `blocks.jsonl` 与 `checksums.yml`，复算每个 generated file 的完整 SHA-256、从
`normalized_text` 复算 block hash，并把 normalization 的 before/after source checksum 与显式
manifest checksum 绑定，再核对 locator、heading、excerpt 和 figure。没有使用 manifest 运行该
解析检查时，不得声称 locator 或原始来源绑定已通过。

OCR evidence 使用 `capture_mode: ocr` 与 `ocr-region` locator。结构 validator 检查 source、
carrier、image hash、run/record/region、bbox 和 page/figure identity；`verify_ocr_locators.py`
再对私有 OCR bundle、全图片/全页覆盖、generated-file hash 与 region 文本做现场复算。
这些检查不判断 OCR 是否识别正确，也不推断图中关系或公式语义。

脚本只检查结构、自洽性和追溯链。通过不表示主张为真、最新、外部共识或已通过人工知识审核。
