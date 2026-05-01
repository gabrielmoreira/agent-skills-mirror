# Reference Asset Taxonomy

## Why This Exists

`references/` 存放的是 VCO 的“支撑资产层”：不直接承担治理正文，但负责提供 contract、matrix、catalog、ledger、scenario、overlay reference 等可复用材料。

cleanup-first 的核心是把这些资产从“散列文本集合”整理为可识别的几类对象，而不是立即重命名所有文件。

## Asset Families

| Family | Purpose | Typical Files |
| --- | --- | --- |
| Contracts / Handbooks | 定义接口、边界、执行规则 | `memory-block-contract.md`, `tool-rule-contract.md`, `unified-task-contract.md`, `conflict-rules.md` |
| Registries / Catalogs | 描述当前拥有哪些能力 / 工具 / 角色 | `tool-registry.md`, `capability-catalog.md`, `role-pack-catalog.md` |
| Matrices / Scorecards | 做 admission、dedup、quality、plane 对比 | `connector-admission-matrix.md`, `capability-dedup-matrix.md`, `candidate-quality-scorecards.md`, `browser-provider-scorecard.md` |
| Ledgers / Changelog / Evidence | 记录时间序列证据或发布轨迹 | `release-ledger.jsonl`, `upstream-value-ledger.md`, `connector-action-ledger.md`, `changelog.md` |
| Scenarios / Checklists / Playbooks | 提供测试场景、手工步骤或例外流程 | `memory-eval-scenarios.md`, `openworld-eval-scenarios.md`, `manual-apply-checklist.md` |
| Overlay Packs | 存放按 overlay / provider / role pack 分层的参考资料 | `overlays/turix-cua/*`, `overlays/gitnexus/*`, `overlays/agency/*`, `overlays/ruc-nlpir/*` |

## Naming Conventions

| Pattern | Intended Meaning |
| --- | --- |
| `*-contract.md` | 可执行或可验证的合同 / 规则接口 |
| `*-registry.md` / `*-catalog.md` | 当前资产清单、能力目录、角色目录 |
| `*-matrix.md` | 准入、对比、去重、owner 分层矩阵 |
| `*-scorecard.md` / `*-scorecards.md` | 评估与评分资产 |
| `*-ledger.*` | 时间序列、流水、发布轨迹 |
| `*-scenarios.md` / `*-checklist.md` | 场景驱动验证与人工 SOP |

## Maintenance Rules

1. 新增 reference 资产必须进入 `references/index.md`。
2. 若 reference 对应某个治理文档或 verify gate，至少存在一条显式锚点。
3. `references/` 不承载 wave 执行正文；波次计划仍放在 `docs/plans/`。
4. overlay 参考资料优先放入 `references/overlays/<domain>/`，避免 root `references/` 继续平铺增长。
5. 长期证据优先写入 ledger / changelog，而不是新增“又一个 report”。

## Core Reading Path

- 从 `index.md` 进入总体导航；
- 先看 `tool-registry.md` / `capability-catalog.md` / `role-pack-catalog*.md` 了解资产面；
- 再看 `*matrix*.md` / `*scorecard*.md` 理解 admission、dedup、quality 规则；
- 最后进入具体 `*contract.md`、`*scenarios.md` 或 `overlays/*` 深挖实现细节。
