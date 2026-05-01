# Capability Catalog Contract

## 1. 设计目标

`config/capability-catalog.json` 同时承担两件事：

1. 继续给 Deep Discovery 提供轻量 capability hit / skill recommendation 信号；
2. 升级为可治理的 capability ledger，承接 discovery / eval / material-layer 资产。

因此 schema 必须 **向后兼容**，同时补足治理字段。

## 2. Top-level schema

| Field | Required | Meaning |
|---|---|---|
| `version` | yes | 人类可读版本号 |
| `schema_version` | yes | schema 演进版本 |
| `updated` | yes | 最近更新时间 |
| `catalog_purpose` | yes | catalog 的治理目的 |
| `governance` | yes | kind、兼容性、禁止事项 |
| `corpus_sources` | yes | 语料来源登记表 |
| `default_interview_questions` | yes | Deep Discovery 的兜底提问 |
| `capabilities` | yes | capability slice 列表 |

## 3. 兼容性合同

以下字段必须永久保留，供 `scripts/router/modules/21-capability-interview.ps1` 消费：

- `id`
- `display_name`
- `task_allow`
- `keywords`
- `skills`

这些字段不能被别名替换，也不能改成嵌套结构。

## 4. Capability entry schema

每个 `capabilities[]` 条目都必须包含：

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | 稳定 capability id |
| `display_name` | yes | 人类可读名称 |
| `summary` | yes | 一句话解释 retained value |
| `catalog_kind` | yes | `productized_capability` / `discovery_corpus` / `eval_corpus` / `reference_only` |
| `task_allow` | yes | 允许匹配的 task type |
| `keywords` | yes | Deep Discovery 触发关键词 |
| `skills` | yes | 现有 canonical skills 作为消费侧 |
| `problem_domains` | yes | 该 slice 解决的问题域 |
| `inputs` | yes | 典型输入 |
| `outputs` | yes | 典型输出 |
| `applicable_planes` | yes | control / capability / governance / discovery / eval 等平面 |
| `upstream_sources` | yes | 来源列表；原生能力可写 `native` |
| `dedup_with` | yes | 与哪些已有能力 / pack / template 重叠 |
| `retirement_conditions` | yes | 何时淘汰或合并 |
| `materialization` | yes | runtime/material 层边界 |
| `evaluation_hooks` | yes | 关联 gate / audit |
| `evidence_artifacts` | yes | docs / pilot / gate artifact 路径 |

## 5. `catalog_kind` 语义

### `productized_capability`

- 已进入 canonical runtime 邻接面；
- `materialization.mode` 应为 `runtime_recommendation`；
- `materialization.runtime_surface` 应为 `vco-native`。

### `discovery_corpus`

- 只作为 discovery / terminology / watchlist 语料；
- `materialization.mode` 必须是 `material_only`；
- `materialization.runtime_surface` 必须是 `none`。

### `eval_corpus`

- 只作为 pilot / eval / benchmark 试点输入；
- 不得直接扩成新的 skill / tool runtime。

### `reference_only`

- 仅保留为背景材料；
- 可被 future wave 引用，但不进入推荐逻辑。

## 6. `materialization` object

| Field | Required | Meaning |
|---|---|---|
| `mode` | yes | `runtime_recommendation` / `material_only` |
| `canonical_owner` | yes | 哪个 canonical surface 持有最终解释权 |
| `runtime_surface` | yes | `vco-native` / `none` |
| `promotion_stage` | yes | `shadow` / `soft` / `strict` / `n/a` |

## 7. Source / dedup 规则

1. 任何来自 curated list / community repo 的 retained value，必须先声明 `upstream_sources`。
2. 任何 `discovery_corpus` / `eval_corpus` 条目都必须显式写出 `dedup_with`。
3. 如果一个条目无法解释它与现有 capability 的关系，则它不应进入 catalog。

## 8. 明确禁止事项

- 删除或改名 Deep Discovery 兼容字段。
- 把 `discovery_corpus` / `eval_corpus` 标成新的 runtime surface。
- 为 curated list 新增 runtime-only skill id。
- 用 capability catalog 替代 team template / pack manifest 的职责。

## 9. 推荐说明口径

推荐统一使用下面这句话解释 catalog 条目：

> 这个条目描述的是一个 **capability slice**，而不是一个新的 runtime surface；它说明了 retained value、适用平面、去冗余关系与淘汰条件。

## 10. 2026-03-17 Discovery Re-Audit Addendum

| Source | Decision | Why |
|---|---|---|
| `awesome-vibe-coding` | `admit` | active workflow discovery feed; material-only refresh justified |
| `vibe-coding-cn` | `admit` | active localized Codex/vibe phrasing and multilingual eval value |
| `awesome-ai-tools` | `metadata-only` | broad watchlist value remains, but runtime value is too diffuse |
| `awesome-ai-agents-e2b` | `metadata-only` | stale but still useful as sandbox/eval reference corpus |

All four remain `material_only` with `runtime_surface = none`.
