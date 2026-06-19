# CLAUDE.md — ControlFlow for Claude Code

ControlFlow for Claude Code is a lightweight, standalone plugin: 3 skills, 0 subagents. It produces high-quality plans in the shared ControlFlow plan format, verifies them inline with adversarial framing, and reviews code as a layer over the native Claude Code toolset — without duplicating or shadowing native capabilities.

This file is a routing stub. The full plan-format detail lives in the skills (loaded lazily on invoke), not here.

## Plan Contract Anchors

These header fields are the machine-enforced contract. `evals/tests/controlflow-contract-drift.test.mjs` asserts they do not drift from `schemas/planner.plan.schema.json`, `governance/project-context-registry.json`, and `governance/runtime-policy.json`.

```yaml
Status: READY_FOR_EXECUTION | ABSTAIN | REPLAN_REQUIRED
Agent: Planner
Schema Version: 1.2.0
Complexity Tier: TRIVIAL | SMALL | MEDIUM | LARGE
Confidence: 0.0–1.0 (computed; below 0.9 auto-NEEDS_REVISION)
Abstain: is_abstaining: false or [ true, reasons: [...] ]
Summary: One paragraph describing task and approach
```

Every phase declares exactly one `executor_agent` from: `CodeMapper-subagent`, `Researcher-subagent`, `CoreImplementer-subagent`, `UIImplementer-subagent`, `PlatformEngineer-subagent`, `TechnicalWriter-subagent`, `BrowserTester-subagent`, `CodeReviewer-subagent`. Quality gates use only: `tests_pass`, `lint_clean`, `schema_valid`, `safety_clear`, `human_approved_if_required`.

## When to Plan

Generate a structured plan before implementation when the task is SMALL or larger (3+ files, multiple concerns, public-API change, architecture change, new dependency, or ambiguous requirements). TRIVIAL (1–2 files, single concern, low blast radius) needs no plan artifact.

## Workflow (tier-gated)

| Tier | Plan | Verify (inline phases) | Review |
|------|------|------------------------|--------|
| TRIVIAL | skip | skip | skip |
| SMALL | `/controlflow-claude-code:controlflow-plan` | phase 1 (structural audit) | `/controlflow-claude-code:controlflow-review` |
| MEDIUM | `controlflow-plan` | phases 1–2 (audit + assumption/mirage) | `controlflow-review` |
| LARGE | `controlflow-plan` | phases 1–3 (audit + mirage + executability cold-start) | `controlflow-review` |

Any unresolved HIGH-impact semantic risk forces LARGE regardless of file count.

- **Plan** — `/controlflow-claude-code:controlflow-plan`: single-sources the format from `schemas/planner.plan.schema.json` and `plans/templates/plan-document-template.md`; writes the artifact to `plans/<task-slug>-plan.md` and never inlines the plan in chat.
- **Verify** — `/controlflow-claude-code:controlflow-verify`: runs inline in the main context (zero subagents) with adversarial framing; emits a verdict of APPROVED / NEEDS_REVISION / REJECTED and the findings that justify it.
- **Review** — `/controlflow-claude-code:controlflow-review`: after implementation; layers evidence discipline, proactive vulnerability/error search, and plan-vs-implementation scope-drift comparison over native `/code-review`.

Do not begin implementation on SMALL+ work until the plan is APPROVED.

## Semantic Risk Review

Every non-TRIVIAL plan MUST include all 7 categories exactly once: `data_volume`, `performance`, `concurrency`, `access_control`, `migration_rollback`, `dependency`, `operability`. If a category is not applicable, set it `not_applicable` with justification — never skip a row.

## Native Toolset Coexistence

ControlFlow does not override Claude Code native tools. Use native `/code-review`, `security-review`, `Explore`, `Plan`, and the `code-reviewer` subagent directly when they fit. ControlFlow skills add plan-format discipline, adversarial verification, and evidence-backed review; they do not duplicate native capabilities. When a fresh-context review is wanted, spawn a native `code-reviewer` or `Explore` subagent manually — ControlFlow keeps no plugin subagents of its own.

## Plan Format

The full plan format — YAML header, the 10 sections in order, the 5 lifecycle sections (Progress, Discoveries, Decision Log, Outcomes, Idempotence & Recovery), the 7-category semantic risk table, and the Mermaid diagram rules (`flowchart TD` DAG for MEDIUM+; `sequenceDiagram` added for LARGE, and for MEDIUM with non-trivial orchestration; each ≤30 lines) — is defined once in the `controlflow-plan` skill, which reads `schemas/planner.plan.schema.json` and `plans/templates/plan-document-template.md` as the single source of truth. Refer there rather than restating it.