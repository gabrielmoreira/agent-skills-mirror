# Upstream Value Ledger

| Slug | Lane | Status | Primary Value | Owner | Next Action |
|---|---|---|---|---|---|
| `activepieces` | `connector_admission` | `shadow_governed` | connector template 与 automation action surface | `vco/connector-admission` | Freeze piece categories into connector allowlist/denylist mapping and keep write actions confirm-gated. |
| `agent-s` | `desktopops_shadow_source` | `shadow_governed` | desktop shadow contract、replay pattern、failure taxonomy source | `vco/desktopops` | Keep Agent-S in shadow-first posture and distill replay / failure-handling improvements into DesktopOps contracts only. |
| `agent-squad` | `role_pack_source` | `tracked_corpus` | multi-agent role vocabulary 与 handoff patterns | `vco/role-pack-governance` | Extract reusable role vocabulary without importing a second orchestrator. |
| `antigravity-awesome-skills` | `skill_catalog_source` | `partial_absorption` | 已有 selective skill harvest 的上游技能目录 | `vco/skill-corpus` | Keep upstream mirrored and promote only proven skills into canonical bundles. |
| `awesome-agent-skills` | `skill_catalog_source` | `tracked_corpus` | agent skill catalog reference | `vco/skill-corpus` | Review agent skill cards for reusable high-signal patterns before bundling. |
| `awesome-ai-agents-e2b` | `discovery_eval_corpus` | `tracked_corpus` | agent/eval discovery examples | `vco/discovery-corpus` | Mine eval and agent examples into discovery notes rather than runtime ownership. |
| `awesome-ai-tools` | `discovery_eval_corpus` | `tracked_corpus` | ecosystem discovery list | `vco/discovery-corpus` | Use as discovery feed only; do not expose it as a runtime surface. |
| `awesome-claude-code-subagents` | `role_pack_source` | `tracked_corpus` | subagent topology reference | `vco/role-pack-governance` | Review subagent layouts for XL patterns without replacing VCO control plane. |
| `awesome-claude-skills-composio` | `skill_catalog_source` | `partial_absorption` | skill harvest source with downstream reuse | `vco/skill-corpus` | Continue selective skill harvesting under canonical pack routing and connector guardrails. |
| `awesome-mcp-servers` | `connector_admission` | `catalog_governed` | MCP server catalog / scouting feed | `vco/connector-admission` | Curate catalog snapshots into the connector admission allowlist; never auto-install from the catalog. |
| `awesome-vibe-coding` | `discovery_eval_corpus` | `tracked_corpus` | workflow discovery corpus | `vco/discovery-corpus` | Harvest workflow references into discovery and eval notes only. |
| `browser-use` | `browserops_provider_source` | `shadow_governed` | provider candidate 与 open-world browsing eval source | `vco/browserops` | Keep browser-use candidate-only while documenting `search_page` vs `find_elements`, forbidding `read_long_content` assumptions, and treating gateway/auth drift as preview evidence only. |
| `claude-skills` | `skill_catalog_source` | `partial_absorption` | upstream inspiration library with partial downstream reuse | `vco/skill-corpus` | Import only contract-compatible skill fragments and keep the rest mirrored as reference. |
| `composio` | `connector_admission` | `shadow_governed` | connector templates and action surfaces | `vco/connector-admission` | Map connector templates to risk classes and secret profiles before any promotion. |
| `docling` | `document_plane_contract` | `canonical_contract` | document plane primary contract source | `vco/document-plane` | Keep the contract aligned through bounded OOXML intake rules, benchmark/taxonomy refresh, and packaged mirror sync after gate pass. |
| `letta` | `memory_policy_source` | `partial_absorption` | memory-policy vocabulary 与 conformance contract source | `vco/memory-governance` | Keep Letta as a contract-source-only policy vocabulary surface; current upstream drift is security/release hygiene and does not justify broader runtime or ownership intake. |
| `mem0` | `memory_policy_source` | `shadow_governed` | optional preference-memory backend candidate | `vco/memory-governance` | Keep mem0 opt-in and replayable while admitting OpenAI-compatible `baseURL`, durable SQLite path guidance, and fenced-payload preservation only inside the optional preference lane. |
| `prompt-engineering-guide` | `prompt_contract_source` | `partial_absorption` | prompt governance source for pattern cards and review heuristics | `vco/prompt-governance` | Keep Prompt-Engineering-Guide as a source for stable cards/checklists only; current upstream drift is site/repo hygiene and does not justify new canonical prompt assets. |
| `vibe-coding-cn` | `discovery_eval_corpus` | `tracked_corpus` | multilingual vibe-coding discovery corpus | `vco/discovery-corpus` | Keep as multilingual discovery corpus and summarize patterns instead of promoting it into runtime ownership. |

## 2026-03-17 Wave C/D Re-Audit Notes

| Source | Decision | Admission scope |
|---|---|---|
| `agent-squad` | `admit` | pattern-refresh-only |
| `awesome-agent-skills` | `admit` | role-card-overlay-only |
| `awesome-claude-code-subagents` | `admit` | team-template-and-review-archetype-refresh-only |
| `claude-skills` | `admit` | skill-distillation-rule-refresh-only |
| `antigravity-awesome-skills` | `metadata-only` | taxonomy-and-quality-evidence-only |
| `awesome-claude-skills-composio` | `admit` | curated-root-and-catalog-quarantine-rule-only |
| `awesome-vibe-coding` | `admit` | workflow-discovery-refresh-only |
| `vibe-coding-cn` | `admit` | localization-and-multilingual-eval-refresh-only |
| `awesome-ai-tools` | `metadata-only` | watchlist-and-gap-evidence-only |
| `awesome-ai-agents-e2b` | `metadata-only` | sandbox-eval-reference-only |

## Reading Rule

- `lane` 决定它走哪条制度化通道；
- `status` 说明当前成熟度，不代表默认 runtime ownership；
- `next_action` 必须是当前最直接、最小且可验证的收口动作；
- 所有 `Slug` 一律走 canonical alias registry，不再接受展示名直写。
