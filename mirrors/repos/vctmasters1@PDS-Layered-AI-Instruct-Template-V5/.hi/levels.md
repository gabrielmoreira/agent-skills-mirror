# LEVELS — Adoption Tiers

> **Role**: META. Defines the *minimum viable subset* of this template at three adoption depths. Adopters should start at **T1** and only graduate when a tier's pain points show up in their workflow. Skipping ahead is allowed but not recommended.
>
> **Last Updated**: 2026-06-04

---

## Why tiers exist

This template ships ~23 agents, ~24 slash commands, 5 registries, deployment modes, plugins, an autonomous layer, observability, and a knowledge base. That is the **ceiling**, not the floor. Most projects never need most of it.

The depth-priority hierarchy itself (one `.hi/instruct.md` per scope, deepest wins) is the only non-negotiable primitive. Everything else is opt-in.

---

## Contents

| Section | What's here |
|---|---|
| [Tier 1 — Core](#tier-1--core) | The depth-priority hierarchy, naming, and credential safety |
| [Tier 2 — Pipeline & Governance](#tier-2--pipeline--governance) | The agent SDLC and surface watchers |
| [Tier 3 — Autonomy & Observability](#tier-3--autonomy--observability) | Autonomous orchestration, evals, plugins |
| [How to disable a tier's surface](#how-to-disable-a-tiers-surface) | Pruning instructions |
| [Promotion criteria](#promotion-criteria) | When to move up a tier |

---

## Tier 1 — Core

**Goal**: One coherent set of rules per directory, enforced at commit time. Nothing else.

| Component | Path | Why |
|---|---|---|
| Meta-instructions (how layering works) | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Required so any agent understands precedence |
| Project specs | [`.hi/dev-specs.md`](../.hi/dev-specs.md) | First read — sets project mode, OS, stack |
| Root authority | [`.hi/instruct.md`](instruct.md) | Workspace-level rules |
| Per-module authority | `<module>/.hi/instruct.md` | Deepest-wins precedence |
| Conventions | [`.hi/conventions.md`](conventions.md) | Naming, TOC, no-duplication |
| Maintenance rules | [`.hi/maintenance.md`](maintenance.md) | Archive-first, never-delete, never-reset-db |
| Credential safety | [`.hi/credentials.md`](credentials.md) | `.env` discipline, `.gitignore` rules |
| Pre-commit hook | [`.hi/hooks/`](../.hi/hooks/) | Mechanical credential leak check |
| Index | [`.hi/index.md`](index.md) | Navigation surface |

**Slash commands at T1**: `/hip-onboard`, `/hip-update-index`, `/hip-archive`, `/hip-validate`, `/hip-git commit`.

**Agents at T1**: none required. The rules are sufficient on their own.

**You stay at T1 if**: a single developer or a small team is building a focused codebase and the discipline of "read the deepest `.hi/instruct.md` before acting" is enough to prevent drift.

---

## Tier 2 — Pipeline & Governance

**Goal**: Multi-agent SDLC with mechanical drift control. Adopt when T1 starts producing inconsistent artifacts (mismatched naming, registries that fall out of sync, modules that diverge from conventions).

Adds, on top of T1:

| Component | Path | Why |
|---|---|---|
| Naming registries (5) | [`.hi/coding-prefixes.md`](coding-prefixes.md), [`.hi/api-conventions.md`](api-conventions.md), [`.hi/database-schema.md`](database-schema.md), [`.hi/error-codes.md`](error-codes.md), [`.hi/config-vars.md`](config-vars.md) | Prevents identifier entropy |
| Naming agent (must be consulted before any artifact) | [`.hi/agents/hia-naming.agent.md`](agents/tier-2/specialists/hia-naming.agent.md) | Gate on creation |
| Pipeline agents (SDLC) | `.hi/agents/hia-*.agent.md` | scaffolder → generator → validator → tester → reviewer → cleanup, under `hia-super` |
| Surface-watcher agents | `.hi/agents/hia-*.agent.md` | curator, deployment, environment, prompt, ports, todo, workflow |
| Drift validator (CI) | [`.hi/engine/`](engine/) + [`.hi/scripts/`](../.hi/scripts/) | Mechanical enforcement of conventions |
| Deployment modes | [`.hi/deployment/`](../.hi/deployment/) | `DEPLOY_MODE`-keyed depth-priority scopes |

**Slash commands at T2 (additions)**: `/hip-route`, `/hip-new-module`, `/hip-deploy-mode`, `/hip-audit-registries`, `/hip-foresight`, `/hip-reflect`, `/hip-ports-check`, `/hip-env-check`.

**You stay at T2 if**: the team coordinates work across multiple modules, registries are real, and the pipeline agents are doing the work. You do **not** need autonomy to be at T2 — agents can be invoked manually.

---

## Tier 3 — Autonomy & Observability

**Goal**: Agents act in loops, learn from runs, and surface metrics. Adopt only when T2 has been stable for long enough that you trust the rules, and only with the autonomous layer's safety contract (`.hi/PAUSE`, hard ceilings, human approval).

Adds, on top of T2:

| Component | Path | Why |
|---|---|---|
| Autonomous orchestrator | [`.hi/autonomous/`](autonomous/) | Opt-in; disabled by default |
| Knowledge base (descriptive, not prescriptive) | [`.hi/knowledge/`](knowledge/) | Empirical learning separated from rules |
| Foresight engine | [`.hi/engine/foresight_engine.py`](engine/foresight_engine.py) | Pre-flight gap/risk analysis |
| Heartbeat | [`.hi/heartbeat.md`](heartbeat.md) | Periodic re-alignment |
| Observability metrics | [`.hi/logs/`](logs/), [`.hi/engine/show_metrics.py`](engine/show_metrics.py) | Run-time visibility |
| Behavioral evals | [`.hi/evals/`](evals/) | Trace-level regression tests for agents |
| Plugins | [`.hi/plugins/`](plugins/) | Optional capability modules |
| MCP server | [`.hi/mcp/`](mcp/) | Tool-neutral protocol layer |
| Meta agents | `.hi/agents/hia-*.agent.md` | router, observer, learner, explorer, compliance |

**Slash commands at T3 (additions)**: `/hip-autonomous-start`, `/hip-observe`, `/hip-metrics`, `/hip-plugin-discover`, `/hip-check-yourself`.

**You stay at T3 if**: agents are routinely running multi-step work, you need behavioral regression coverage, and you want metrics you can act on. T3 is the design ceiling of this template.

---

## How to disable a tier's surface

The template is additive: removing a tier's components does not break shallower tiers, because shallower tiers never reference deeper ones.

To prune:

| Pruning | Action |
|---|---|
| Drop T3 → T2 | Delete (or leave empty) `.hi/autonomous/`, `.hi/plugins/`, `.hi/evals/`. Remove `hia-*` agents you do not use. The remaining T2 surface is self-contained. |
| Drop T2 → T1 | Remove `hia-*`, `hia-*` agents. Keep registries only if your project still references them; otherwise delete. T1 rules continue to apply. |
| Drop a slash command | Move its `.prompt.md` file to `.archive/` (per [`.hi/maintenance.md`](maintenance.md)). Do not delete. |

Every removal must follow the **archive-first** rule. See [`.hi/archive-protocol.md`](archive-protocol.md).

---

## Promotion criteria

Move up a tier when you observe the symptom, not before:

| Symptom | Promote to |
|---|---|
| "Two modules use different naming for the same concept." | T2 (registries + naming agent) |
| "Agents produce code that violates a rule the validator could check." | T2 (drift validator) |
| "We keep doing the same multi-step workflow by hand." | T2 (pipeline agents) |
| "We need to run agents while we sleep." | T3 (autonomous, with guardrails) |
| "An agent silently regressed and we did not catch it." | T3 (behavioral evals) |
| "We cannot tell which agents are spending tokens or failing." | T3 (observability) |

If the symptom is not present, the lower tier is correct — extra surface area is a liability, not an asset.
