# 四层知识模型

## 1. Evidence

记录来源当前载体实际提供的可定位材料。至少包含 `evidence_id`、`source_id`、`locator`、
`evidence_type`、内容载体、`capture_mode`、`extraction_confidence`、`limitations`、
`quality_flags` 和处置 `status`。图、图注和正文分别记录并显式关联。`normalized_text`
只保存无语义变化的规范化结果，不得写成摘要、翻译或纠错文本。受版权限制的 raw
payload 可放在被忽略的私有记录中；Git-safe ledger 可以只保存最短摘录或
`content_summary`。

OCR evidence 使用 `capture_mode: ocr` 与 `ocr-region` locator，绑定 DOCX figure/occurrence
或 PDF page、图片 hash、OCR run/record/region、bbox 和文本 hash。初始保留
`ocr-unreviewed`；accepted OCR evidence 必须有显式 human `ocr_review`。OCR 文字不得被当作
图中箭头、结构关系或公式语义。

## 2. Claim

把来源含义拆成原子主张。至少包含陈述、知识类型、书中地位、evidence 外键、
transformation、范围、局限、重要性、状态和人工决定。若 statement 使用已审定的 OCR、
缺字或术语解释，增加 `correction_ids`；没有该外键时不得静默使用 overlay 中的候选值。
区分：

- `book-assertion`：图书直接陈述；
- `author-view`：作者解释、偏好或评价；
- `teaching-simplification`：教学简化或类比；
- `quoted-source`：图书转述的外部来源；
- `project-policy`：用户已冻结的本项目控制规范，不是图书主张；
- `distiller-synthesis`：蒸馏者归纳；
- `task-transfer`：迁移到新任务的规则。

## 3. Relation

使用 `subject / predicate / object` 表达概念关系，同时记录限定条件、claim 外键、可选
evidence 外键以及 `explicit / implicit / inferred`。相关不得升级为因果，可能不得升级
为必然。`implicit` 或 `inferred` relation 若要 accepted，必须由 `reviewer_type: user`
记录 `human_decision` 和推理理由；只标 relation status 或由自动 agent 署名不能代替审核。

## 4. Capability Rule

把已审阅知识转成待验证的任务行为。记录触发信号、必需上下文、检查、动作、输出、
停止条件以及 claim/relation 外键。规则必须从上游记录生成，不得为补全工作流而创造
来源没有支持的事实。`semantic_support` 为 checks、action、output、stop_conditions 中
每个文本项逐项登记 `item_index` 及支撑它的 claim/relation；名义上引用一个上游 ID
不等于整条规则被支持。

rule 与 candidate 都声明 `stable_task_ids`。`method-transfer` candidate 还声明
`provenance_contract`，输出严格区分 `method-source-evidence`、`target-material-evidence` 和
`analogy-hypothesis`；缺少目标材料证据时停止或降低结论强度。

## 来源中立的第一性原理重建

私有 evidence、来源 claim、locator 和书中地位保持原样。下游候选不得直接把这些记录的
题名、人物、出版信息、归因句、引文、文件名或命名案例投影到 candidate/public output。
在 T4 rule 前，先用现有 `source_position: distiller-synthesis` 与 `transformation: T3` 形成
来源中立的原子 principle claim，并在审阅视图中显式列出 problem、premises、invariant、
derivation、assumptions、boundaries、falsifiers 和 stops。T3 仍需人工决定，不能把重建写成
来源明示或领域共识。

每个 T4 check/action/output/stop item 仍通过现有 `semantic_support` 回链 accepted
claim/relation/evidence；来源中立只改变候选投影，不删除私有追溯。method-transfer 的
`method-source-evidence` 层保留在私有 canonical 记录中，公开结果只呈现目标观察、分析、
假设、限制和停止理由。详见
[source-neutral-method-distillation.md](source-neutral-method-distillation.md)。

## T0–T4

| 级别 | 含义 | 约束 |
|---|---|---|
| `T0` | 必要且适量的直接引用 | 保持原文和 locator |
| `T1` | 忠实近义改写 | 不提高确定性 |
| `T2` | 同一语义章节内多处归纳 | 列出主要 evidence；不得覆盖跨文件/跨节综合 |
| `T3` | 跨章节、跨文档或跨独立政策段综合 | 标为蒸馏综合并记录人工决定 |
| `T4` | 转换为新任务规则 | 标为任务迁移并记录人工决定 |

T3/T4 的 `human_decision.decision` 使用 `pending / accepted / revised / rejected`，并记录
`reviewer_type`。capability rule 还使用 `gate_decision_id` 绑定其 Gate 3 决定。处置为
`accepted` 时不得仍为 `pending`，也不得脱离当前 Gate 3 approval 单独接受 rule。

## 两套状态

知识记录状态：

```text
candidate / accepted / reference-only / needs-verification / rejected
```

Skill 生命周期：

```text
draft / review / accepted / deployed / deprecated / rejected
```

两者不得混用。各层 accepted 的含义也不同：evidence 表示提取与 locator 已审核，claim
表示对 evidence 忠实，relation 表示关系强度与推断地位已审核，rule 表示 T4 获准进入
评测。accepted rule 不表示行为已经验证；只有 completed/pass eval run 加 Gate 4 人工
接受才能把 Skill lifecycle 变为 accepted。任何层的 accepted 都不自动表示外部共识。

## 审计历史与质量标记

- 任何 `status: accepted` 的 evidence、claim、relation 或 rule 必须提供完整 `status_history`；只写最终状态不足以证明经过审核。
- 任何非 `draft` 的 Skill candidate 必须提供完整 `lifecycle_history`。
- `quality_flags` 是机器可读的未解决质量信号。只要列表非空，该 evidence 就不得支撑 accepted rule；先解决并记录决定，再清空标记。
- `project-policy` 只能指向已获用户冻结的控制规范 evidence，不得用它伪装成 `book-assertion` 或 `quoted-source`。

## Gate decision

`gate-decisions.yml` 是门禁权威日志。每条记录至少包含稳定 `decision_id`、全局连续
`sequence`、同系列 `supersedes`、`is_current`、gate、相关 candidate（若适用）、decision、
scope、reviewer type/identity、时间、理由、条件、关联 eval run IDs 和 `rule_decisions`。
每个 gate/candidate 系列只有末项 current，不能用文件中“最后看到的一项”或 Markdown
文字替代显式 current 链。Gate 3 用当前 `approved-for-eval` 表示允许物化并取得评测资格，
且须逐条决定候选 rules；只有随后存在完全匹配的 completed materialization 才可实际执行
Gate 4。该值不改变 lifecycle。Gate 4 的 accepted 必须引用已完成且通过的 eval runs。

`pending / revise / rejected` 与已被 supersede 的旧 approval 都不授权物化。agent 可以
生成 review package，但不得把推荐意见写成替用户作出的 authoritative decision。

## Materialization

`gate-decisions.yml.materializations` 保存 candidate specification 到可运行候选目录的
权威物化事件。completed 物化必须绑定当前 Gate 3 approval，记录 candidate 路径/hash、
时间、获准 rules 和 quick-validation pass。Gate 3 前已存在的审阅原型记为
`legacy-quarantined`：它可以留作审核证据，但不等于获批物化，不能参加评测。

materialization 的匹配条件、唯一性要求和 activation 状态统一由
[validation-contract.md](validation-contract.md) 定义；本模型不从候选目录存在性推断状态。

## Eval run

`eval-runs.yml` 保存实际执行，不保存空泛计划。每个 run 至少绑定 candidate ID、
materialization ID、candidate hash、rule IDs、case type/ID、canonical case-definition hash、
fixture ID/path/hash、source IDs、holdout、执行环境、两组严格 JSON 输出及 hash、物化 rubric、
逐维评分、fatal failures、泄漏控制、人工 reviewer、outcome 和 limitations。completed run 必须绑定当前 Gate 3
approval 派生出的 completed materialization，并与其 candidate/hash/完整 rule 集合一致。
`planned` 或 `blocked` 可以留痕，但不能支持 Gate 4 acceptance。Gate 4 接受引用的
completed/pass runs 必须来自同一 materialization，至少覆盖 3 trigger、3 nontrigger 和
3 task，且 task 中至少一个为 holdout。

区分 **run blocker** 与 **Gate 4 acceptance blocker**：fixture 缺失、不可重放、权利不足、
泄漏或未授权数据目的地阻断对应 run；3/3/3/holdout 覆盖不足、拟引用 run 非
completed/pass、无人工评分或混用 materialization 阻断 Gate 4 接受。局部 blocked run
不应抹除其他独立 completed run。

## Correction overlay

overlay 保持载体原值不变，记录 issue、候选值、依据、影响 claim、待解除 quality flags
和人工决定。completed 决定必须有显式 `user | human-delegate` reviewer type，不能用 agent
署名冒充人工。只有 accepted/revised correction 才能被 claim 的 `correction_ids` 使用；
删除 active quality flag 必须保留对应 correction 决定和历史。
