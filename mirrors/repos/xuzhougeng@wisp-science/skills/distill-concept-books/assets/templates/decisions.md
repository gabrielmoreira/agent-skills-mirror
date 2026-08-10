# Distillation Decisions

> 本文件是人工审阅视图。Gate 决定以 `gate-decisions.yml` 为权威；记录状态、T3/T4、
> inferred relation 与 lifecycle 决定以各 YAML 的 decision/history 为权威。不得只改本表。
> 本视图属于私有 provenance；不得把其中的来源身份、引文、文件名或命名案例复制进
> candidate/public output。

## 门禁决定

| decision_id | gate | 日期 | reviewer type/决定者 | 决定 | 范围 | 条件 | eval run IDs | 理由 |
|---|---|---|---|---|---|---|---|---|
| {{decision_id}} | {{gate}} | {{date}} | {{reviewer_type}} / {{reviewer}} | {{decision}} | {{scope}} | {{conditions}} | {{eval_run_ids}} | {{rationale}} |

## 知识记录处置

| record_id | 原状态 | 新状态 | 决定者 | 依据 | 理由 |
|---|---|---|---|---|---|
| {{record_id}} | {{from_status}} | {{to_status}} | {{reviewer}} | {{evidence_or_issue}} | {{rationale}} |

## T3/T4 决定

| record_id | transformation | decision | reviewer | date | rationale |
|---|---|---|---|---|---|
| {{record_id}} | {{T3_or_T4}} | {{decision}} | {{reviewer}} | {{date}} | {{rationale}} |

## Implicit / inferred relation 决定

| relation_id | relation_status | decision | reviewer | date | rationale |
|---|---|---|---|---|---|
| {{relation_id}} | {{relation_status}} | {{decision}} | {{reviewer}} | {{date}} | {{rationale}} |

## 冲突与修正 overlay

| issue_id | 原始值 | 候选修正 | 依据 | 决定 | 是否阻断规则 |
|---|---|---|---|---|---|
| {{issue_id}} | {{raw_value}} | {{proposed_value}} | {{basis}} | {{decision}} | {{blocking}} |

## Skill 生命周期

| candidate_id | 原 lifecycle | 新 lifecycle | Gate | 决定者 | 理由 |
|---|---|---|---|---|---|
| {{candidate_id}} | {{from_lifecycle}} | {{to_lifecycle}} | {{gate}} | {{reviewer}} | {{rationale}} |

`approved-for-eval` 是 Gate 3 decision，不是 lifecycle；物化和评测期间 lifecycle 仍为
`review`。Gate 4 accepted 必须引用 completed/pass eval runs。

## 拒绝项保留

| record/candidate | 拒绝理由 | 不适用边界 | 重新开启条件 |
|---|---|---|---|
| {{id}} | {{reason}} | {{boundary}} | {{reopen_condition}} |
