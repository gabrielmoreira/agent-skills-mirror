# Skill Candidates

> 私有 Gate 审阅视图。可记录内部 rule/claim/evidence 外键，但不得把来源身份、引文、
> 文件名或命名案例复制进 candidate tree 或公开输出。

## 拆分总览

| candidate_id | 稳定任务 | 主要规则 | 与其他候选的边界 | lifecycle | 建议 |
|---|---|---|---|---|---|
| {{candidate_id}} | {{stable_task}} | {{rule_ids}} | {{boundary}} | review | {{recommendation}} |

## 候选：{{candidate_name}}

- `candidate_id`: `{{candidate_id}}`
- `name`: `{{candidate_name}}`
- 稳定任务：{{stable_task}}
- stable task IDs：{{stable_task_ids}}
- 生命周期：`review`
- 当前形态：{{specification_or_materialized}}
- candidate hash：{{candidate_hash_or_pending}}

### Should trigger

1. {{trigger_1}}
2. {{trigger_2}}
3. {{trigger_3}}

### Should not trigger

1. {{nontrigger_1}}
2. {{nontrigger_2}}
3. {{nontrigger_3}}

### 输入、输出与停止

- 输入：{{inputs}}
- 输出：{{outputs}}
- rule IDs：{{rule_ids}}
- 停止条件：{{stop_conditions}}
- 风险与限制：{{risks}}

### 第一性原理重建与来源中立投影

| problem | premises | invariant | derivation | assumptions | boundaries / falsifiers / stops | T3 claim / human decision |
|---|---|---|---|---|---|---|
| {{problem}} | {{premises}} | {{invariant}} | {{derivation}} | {{assumptions}} | {{boundaries_falsifiers_stops}} | {{t3_claim_and_decision}} |

- 私有 `rule → claim → evidence` 闭包：{{private_traceability_closure}}
- 运行时读取方法来源：`forbidden`
- candidate/public output 禁项检查：{{source_neutral_projection_check}}
- private extra-terms（存在译名、转写、slug、系列别名、特有术语或具名案例时必需）：
  {{private_extra_terms_coverage_and_lint}}
- 禁项：题名、人物、出版信息、ISBN、系列/原文件名、归因句、引文、locator、私有 ID、
  可识别命名案例
- 无法中立重建时的处置：`review/revise; no materialization`

### 评测

- 代表性任务：{{task_cases}}
- 留出材料：{{holdout_case}}
- 防泄漏：{{leakage_control}}
- 有/无 Skill 对照：{{comparison_plan}}
- fixture IDs/hashes：{{fixture_ids_hashes}}
- rubric/阈值：{{rubric_threshold}}
- coverage matrix：{{task_coverage_summary}}
- provenance contract：{{provenance_contract}}
- deferred/rejected tasks 与用户决定：{{deferred_rejected_tasks}}

### Gate 3 与物化

- Gate 3 decision ID：{{gate_3_decision_id}}
- 决定：{{gate_3_decision}}
- 条件：{{gate_3_conditions}}
- current/supersedes 校验：{{gate_3_current_chain_check}}
- 逐条 rule decisions：{{gate_3_rule_decisions}}
- approval snapshot：{{gate_3_approval_snapshot}}
- Gate 1/task contract/coverage 对齐：{{task_contract_alignment}}
- 物化允许：只有 current `approved-for-eval`、逐条 rule decisions 完整一致且 snapshot
  精确匹配候选 tree 与权威 YAML
- Gate 3 前最终 review-only 文件：{{materialization_files}}
- 已有文件与覆盖处置：{{existing_file_disposition}}
- candidate path/hash 与完整 rule 集：{{materialization_identity}}
- quick validation：{{quick_validation_result}}

Gate 3 前本文件描述 candidate specification 和最终 review-only tree。没有权威
`approved-for-eval` 时不执行 pending T4；批准后也不得静默修改 snapshot 绑定的 bytes，
只能对同一 tree quick-validate 并登记 materialization。lifecycle 始终保持 `review`。
