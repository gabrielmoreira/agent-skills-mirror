# ControlFlow — Copilot Routing Stub

ControlFlow is a thin layer over native Copilot capabilities: three skills (`controlflow-plan`, `controlflow-verify`, `controlflow-review`) and one planner agent (`@controlflow-planner`). It produces high-quality plans in the shared ControlFlow plan format, verifies them inline with adversarial framing, and reviews code as a layer over native Copilot code review — without duplicating or shadowing native capabilities.

This file is the always-on routing stub. The full plan-format detail lives in the skills (loaded lazily on invoke), not here.

## When to Plan

Generate a structured plan before implementation when the task is SMALL or larger (3+ files, multiple concerns, public-API change, architecture change, new dependency, or ambiguous requirements). TRIVIAL (1–2 files, single concern, low blast radius) needs no plan artifact.

## Workflow (tier-gated)

| Tier | Plan | Verify (inline phases) | Review |
|------|------|------------------------|--------|
| TRIVIAL | skip | skip | skip |
| SMALL | `/controlflow-plan` | phase 1 (structural audit) | `/controlflow-review` |
| MEDIUM | `/controlflow-plan` | phases 1–2 (audit + assumption/mirage) | `/controlflow-review` |
| LARGE | `/controlflow-plan` | phases 1–3 (audit + mirage + executability cold-start) | `/controlflow-review` |

Any unresolved HIGH-impact semantic risk forces LARGE regardless of file count.

- **Plan** — `/controlflow-plan` (or invoke the `@controlflow-planner` agent from the agents dropdown): single-sources the format from `schemas/planner.plan.schema.json` and `plans/templates/plan-document-template.md`; writes the artifact to `plans/<task-slug>-plan.md` and never inlines the plan in chat.
- **Verify** — `/controlflow-verify`: runs inline in the main context (zero subagents) with adversarial framing; emits a verdict of APPROVED / NEEDS_REVISION / REJECTED and the findings that justify it.
- **Review** — `/controlflow-review`: after implementation; layers evidence discipline, proactive vulnerability/error search, and plan-vs-implementation scope-drift comparison over native Copilot code review.

Do not begin implementation on SMALL+ work until the plan is APPROVED.

## Semantic Risk Review

Every non-TRIVIAL plan MUST include all 7 categories exactly once: `data_volume`, `performance`, `concurrency`, `access_control`, `migration_rollback`, `dependency`, `operability`. If a category is not applicable, set it `not_applicable` with justification — never skip a row.

## Native Toolset Coexistence

ControlFlow does not override native Copilot capabilities. Use native Copilot code review, security review, and exploration tools directly when they fit. ControlFlow skills add plan-format discipline, adversarial verification, and evidence-backed review; they do not duplicate native capabilities. When a fresh-context review is wanted, delegate the mechanical pass to native Copilot code review — ControlFlow keeps no agents of its own beyond the planner.

## Plan Format

The full plan format — YAML header, the 10 sections in order, the 5 lifecycle sections (Progress, Discoveries, Decision Log, Outcomes, Idempotence & Recovery), the 7-category semantic risk table, and the Mermaid diagram rules (`flowchart TD` DAG for MEDIUM+; `sequenceDiagram` added for LARGE, and for MEDIUM with non-trivial orchestration; each ≤30 lines) — is defined once in the `controlflow-plan` skill, which reads `schemas/planner.plan.schema.json` and `plans/templates/plan-document-template.md` as the single source of truth. Refer there rather than restating it.

## Shared Policies

### Continuity

Use `plans/project-context.md` as the stable reference for complexity tiers, semantic risk taxonomy, and shared conventions.

### Build and Test

```sh
cd evals && npm test              # full offline suite: structural + behavior + drift + parity + contract-drift
npm run test:structural           # structural validation only (faster)
npm run test:behavior             # prompt-behavior + drift regressions only
```

Scenarios are in `evals/scenarios/`. Validate against matching schemas in `schemas/`.

### Failure Classification

When status is `FAILED`, `NEEDS_INPUT`, `NEEDS_REVISION`, or `REJECTED`, include `failure_classification`:

- `transient` — Flaky test, network timeout, or temporary tool unavailability; retry with identical scope.
- `fixable` — Small correctable issue (typo, missing import, config value); retry with fix hint.
- `needs_replan` — Architecture mismatch or missing dependency; delegate to the planner for a targeted replan.
- `escalate` — Security vulnerability, data integrity risk, or unresolvable blocker; stop and await human approval.
- `model_unavailable` — the routed/primary model is unavailable or unreachable; retry with a native Copilot model substitution, then escalate on exhaustion.

### Memory Hygiene

Maintain/update `NOTES.md` for persistent state across context resets:

- Active objective and current phase.
- Blockers and unresolved risks.
- Remove stale entries when superseded.
- Keep within the 20-line budget (enforced by `evals/validate.mjs` Pass 7, style drift checked via `validateNotesMdStyle` in `evals/drift-checks.mjs`).

See `docs/agent-engineering/MEMORY-ARCHITECTURE.md` for the canonical three-layer memory model (session / task-episodic / repo-persistent). `NOTES.md` holds repo-persistent active-objective state only; task-specific history lives in `plans/artifacts/<task-slug>/`.

Before writing to `/memories/repo/` or updating `NOTES.md` at a phase boundary, load and follow `skills/patterns/repo-memory-hygiene.md` (dedup checklist + prune routine).

To identify plans ready for archival: `cd evals && npm run archive:dry`. To execute: `npm run archive:apply`.

## Knowledge Graph (graphify-out/)

A graphify knowledge graph of this repo lives in `graphify-out/` (gitignored — generated analysis artifact, not shipped). Rebuild with `/graphify`. If `graphify-out/graph.json` already exists, query it with `/graphify query "<question>"` instead of rebuilding. Use it to navigate cross-file relationships before planning work that spans the plugin.