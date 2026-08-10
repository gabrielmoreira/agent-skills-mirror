# {{distillation_id}} 蒸馏 Brief

> 私有治理视图。来源身份和权利在此保持可审计，但不得复制进 downstream candidate 或
> public output。

## 状态

- `distillation_id`: `{{distillation_id}}`
- 当前门禁：`{{gate}}`
- 记录语言：`{{language}}`
- 目标运行时：`{{runtime}}`
- 目录模式：`{{new_or_resume}}`
- 已有记录保护：{{existing_artifact_protection}}

## 受众与稳定任务

- 权威 task contract：`{{task_contract_path}}`
- `task_contract_id` / version：`{{task_contract_id}}` / `{{contract_version}}`
- task contract SHA-256：`{{task_contract_sha256}}`
- active stable task IDs：{{active_stable_task_ids}}
- 受众：{{audience}}
- 要完成的任务：{{stable_tasks}}
- 不覆盖：{{exclusions}}

## 来源、载体与权利边界

| source_id | 角色 | 版本/完整性 | 本地载体 | adapter/bundle | 本地处理 | 上传 | 公开引用 | 衍生发布 |
|---|---|---|---|---|---|---|---|---|
| {{source_id}} | {{source_role}} | {{version_completeness}} | {{carrier}} | {{adapter_support}} | {{local_processing_right}} | {{upload_right}} | {{public_quote_right}} | {{derivative_publication_right}} |

## 阅读范围

- 全书结构扫描：{{scan_scope}}
- 精读：{{deep_read_scope}}
- 快读：{{fast_read_scope}}
- 未读：{{unread_scope}}
- 留出：{{holdout_scope}}

## 来源政策

- 图书中心模式：{{book_centered_policy}}
- 允许的补充来源：{{external_sources}}
- 联网/上传/依赖安装：{{tool_boundaries}}
- 不受支持载体的处置：{{unsupported_carrier_disposition}}

## 产物

- 权威 YAML：{{authoritative_outputs}}
- 人工审阅视图：{{review_outputs}}
- 候选边界：{{candidate_boundary}}
- 来源中立投影：{{source_neutral_projection_boundary}}

## 验收、失败与停止

- 验收问题：{{acceptance_questions}}
- 失败条件：{{failure_conditions}}
- 停止条件：{{stop_conditions}}
- 人工门禁：{{human_gates}}
- 权威 Gate 记录：`gate-decisions.yml`
- 实际评测记录：`eval-runs.yml`
- correction overlay：{{correction_overlay_path_or_none}}

## Gate 1 批准

- 当前状态：`pending-user-approval`
- 展示给用户的冻结项：{{gate_1_frozen_items}}
- 用户明确决定：{{gate_1_user_decision}}
- 决定日期：{{gate_1_decided_at}}
- 限定条件：{{gate_1_conditions}}

`gate_1_user_decision` 未明确记录为批准时，不得进入 Gate 2。
本 Markdown 是审阅视图；Gate 1 只有同步写入 `gate-decisions.yml` 才生效。恢复已有目录
时不得用本模板覆盖原 brief。任务权威来自 Gate 1 snapshot 绑定的 task contract；brief、
阶段目标或 checkpoint 都不得替代它。
