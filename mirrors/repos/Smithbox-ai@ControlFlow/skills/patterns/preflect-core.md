# PreFlect — Canonical Pre-Action Reflection Gate

## Purpose
Single source of truth for the PreFlect gate every ControlFlow agent applies before any action batch (planning, dispatch, coding, audit, review, write, test, report). Agent files reference this skill instead of restating the canonical risk classes.

## When to Apply
Before *each* batch of substantive output:
- Orchestrator: before each subagent dispatch / approval batch.
- Planner: before finalizing a plan revision.
- Implementation agents: before each edit/test cycle.
- Review/critic agents: before issuing a verdict, audit, or score.
- Read-only agents (CodeMapper, Researcher, TechnicalWriter, BrowserTester): before returning a report.

## Canonical Four Risk Classes

1. **Scope drift.** Am I about to act outside the assigned scope (extra files, features, refactors, or surfaces not requested by the plan/task)? Drift includes silently broadening file globs, adding "while I'm here" cleanups, or substituting a more general fix for the requested one.

2. **Schema / contract drift.** Will my output deviate from the contract that downstream consumers rely on (JSON schema fields, required headings, P.A.R.T. section order, status enums, classification taxonomy)? Drift includes inventing fields, renaming sections, dropping required keys, or emitting status values outside the declared enum.

3. **Missing evidence.** Do I have direct, verifiable evidence (file contents, test output, schema text, prior artifact) for every concrete claim I am about to make? Anything stated without evidence — even when "obvious" — is a fabrication risk and must be downgraded to ABSTAIN, NEEDS_INPUT, or removed.

4. **Safety / destructive action.** Could this batch perform an irreversible or shared-system change (delete files, rewrite contracts, mutate governance, push branches, drop tables, run destructive shell commands) without explicit approval or rollback? If yes, the action requires the Human Approval Gate before execution.

## Decision Output

Emit one of:

- `GO` — All four classes are clear (or risks are explicitly accepted by an upstream gate). Proceed with the batch.
- `REPLAN` — A risk is real and the agent is empowered to narrow scope, gather evidence, or restate the contract before retrying. Do *not* proceed with the original batch; re-enter the workflow with the corrected plan.
- `ABSTAIN` — A risk is real and cannot be resolved by this agent (ambiguous scope, inaccessible evidence, missing approval). Stop, return a structured status (`ABSTAIN` / `NEEDS_INPUT`) with reasons, and surface to the conductor.

The decision MUST be observable in the agent's output (gate event, execution-report status field, or inline note). Silent GO with unresolved risk is a contract violation.

## Domain Hooks

Agents MAY add up to 5 lines of agent-specific risk classes immediately after the pointer to this skill, under the heading `Agent-specific additions:`. Examples:
- Orchestrator: high-risk-destructive approval gate applies before dispatch.
- Planner: Idea Interview & Clarification Gates must precede Semantic Risk.
- Adversarial critics (PlanAuditor, AssumptionVerifier, ExecutabilityVerifier): adversarial stance — escalate any mirage.
- Implementers (Core / UI / Platform): build/test gate before reporting completion.
- BrowserTester: UX/accessibility checks within scope.

If an agent has no domain-specific risk beyond the canonical four, it writes `_none_` instead of bullets.

Agent files MUST NOT restate the canonical four risk classes locally; the pointer to this file is the contract.
