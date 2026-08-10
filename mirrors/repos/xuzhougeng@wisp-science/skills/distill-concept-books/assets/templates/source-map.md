# {{distillation_id}} Source Map

> 私有治理视图。实际书目身份仅在 private sources manifest 或必要权利记录中单点保存；
> 本视图只显示 opaque ID、hash、locator 状态和读取范围，不重复渲染身份或载体文件名。

## 私有来源绑定

- `source_id`: `{{source_id}}`
- 私有身份核验状态：{{source_identity_verification_status}}
- 完整身份记录：仅见 private sources manifest / 必要权利记录，不在本视图展开
- 版本与完整性：{{version_completeness}}
- 原始 SHA-256：`{{sha256}}`
- 权利边界：{{rights}}
- 恢复/新建：{{resume_mode}}

## Source-quality preflight

| 检查 | 结果 | 证据 | 处置 |
|---|---|---|---|
| 身份与版本 | {{result}} | {{evidence}} | {{disposition}} |
| 文本层 | {{result}} | {{evidence}} | {{disposition}} |
| 结构与目录 | {{result}} | {{evidence}} | {{disposition}} |
| 分页与 locator | {{result}} | {{evidence}} | {{disposition}} |
| 图表与公式 | {{result}} | {{evidence}} | {{disposition}} |
| 元数据 | {{result}} | {{evidence}} | {{disposition}} |
| adapter/bundle 支持 | {{result}} | {{evidence}} | {{disposition}} |
| OCR 全图像/全页覆盖 | {{ocr_result}} | {{ocr_evidence}} | {{ocr_disposition}} |

本表的“证据”只写状态、hash 或 opaque locator 引用，不粘贴题名、章节标题、身份、引文或具名案例。

- 总体处置：`{{usable_status}}`
- correction overlay：{{overlay_path_or_none}}
- 全局阻断项：{{global_blockers}}
- 局部阻断项及影响范围：{{local_blockers}}

## Locator 契约

- 载体类型：{{carrier}}
- adapter/bundle：{{adapter_or_bundle}}
- 自动支持级别：{{supported_or_preflight_only}}
- 主 locator：{{primary_locator}}
- 辅助 locator：{{auxiliary_locator}}
- 已知限制：{{locator_limitations}}
- OCR runner/engine/languages：{{ocr_runtime}}
- OCR coverage：{{ocr_coverage}}
- OCR bundle/checksum：{{ocr_bundle_identity}}

## 来源结构索引（不渲染标题）

| 顺序 | opaque section ID | heading/content hash | 稳定范围 | 图表 | 读取状态 | 备注 |
|---:|---|---|---|---|---|---|
| {{order}} | {{section_id}} | {{heading_or_content_hash}} | {{locator_range}} | {{media}} | {{reading_status}} | {{notes}} |

## 范围与留出隔离

- 精读：{{deep_read_ranges}}
- 快读：{{fast_read_ranges}}
- 未读：{{unread_ranges}}
- 结构扫描专用：{{structure_only_ranges}}
- 留出：{{holdout_ranges}}
- 防泄漏方法：{{holdout_isolation}}

## Gate 2 权威决定

- decision ID：{{gate_2_decision_id}}
- decision：{{gate_2_decision}}
- scope/conditions：{{gate_2_scope_conditions}}

本节从 `gate-decisions.yml` 生成；只改本 Markdown 不构成批准。

## 冻结任务可支持性

| 任务 | 当前可支持性 | 缺口 | Gate 2 决定 |
|---|---|---|---|
| {{task}} | {{supportability}} | {{gaps}} | {{decision}} |
