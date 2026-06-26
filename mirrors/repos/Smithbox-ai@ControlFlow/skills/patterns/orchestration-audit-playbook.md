# Orchestration Audit Playbook

## Purpose

Reusable checklist for project-wide ControlFlow orchestration audits. Use when the task spans agent prompts, schemas, governance manifests, eval fixtures, documentation, skills, memory surfaces, or approval/retry behavior.

This playbook complements `completeness-traceability.md`, `integration-validator.md`, and `llm-behavior-guidelines.md`. It focuses on audit-specific coordination risks rather than general requirement coverage, dependency graph checks, or prompt style cleanup.

## Inputs

- Approved plan path, trace_id, and phase scope.
- Changed-file set and planned-file set.
- Current canonical sources: `plans/project-context.md`, `governance/runtime-policy.json`, `governance/tool-grants.json`, `governance/agent-grants.json`, `schemas/`, `evals/`, `docs/agent-engineering/`, and `skills/index.md`.
- Prior phase CodeReviewer verdicts when auditing final-review novelty behavior.

## Checklist A - Traceability

1. Map each user requirement and acceptance criterion to a file group and verification gate.
2. Confirm every P0/P1 finding from the audit ledger is either fixed, covered by a later phase, or explicitly deferred with `needs_replan` rationale.
3. Check reverse trace: every edited file must map to the phase scope or to a required registry/documentation update.
4. Flag unplanned prompt/schema/governance/test edits as scope risks unless the plan explicitly authorized them.

## Checklist B - Schema, Prompt, And Grant Alignment

1. For every changed agent behavior, cross-check the prompt, schema, eval scenario, and governance grant surface.
2. Verify failure classifications are aligned: `model_unavailable` routes through `retry_budgets.model_unavailable_max`; PlanAuditor and AssumptionVerifier exclude `transient`; ExecutabilityVerifier can use all five values.
3. Verify Planner `risk_review` semantics: all seven categories appear exactly once, including `not_applicable` entries.
4. Verify runtime-policy schema enums match live policy for `batch_approval.approval_per`, `batch_approval.exception_destructive_phases`, and `final_review_gate.auto_trigger_tiers`.
5. Verify tool feasibility: BrowserTester is script/harness-based and abstains without an executable harness; CodeReviewer final review uses injected `prior_phase_findings[]` rather than self-sourcing `plans/artifacts/`.

## Checklist C - Hidden-Defect Triage

1. Separate confirmed defects from useful feature ideas before assigning remediation phases.
2. Look for silent mismatches between prose requirements and machine-enforced schema rules.
3. Look for positive-only tests where a negative fixture would catch regression.
4. Look for stale documentation claims about live-agent execution, strict validator mode, browser control, or approval cadence.
5. Escalate security, destructive action, or data-integrity risks instead of folding them into ordinary cleanup.

## Checklist D - Validation Gates

1. Treat `cd evals && npm test` as the canonical offline gate; do not describe it as live-agent execution.
2. Confirm structural validation covers schema compilation, scenarios, references, grants, P.A.R.T order, skill index registration, memory discipline, drift checks, final-review coupling, and canonical-source checks.
3. Confirm the full suite also includes prompt-behavior, orchestration-handoff, drift, NOTES.md, archive-script, and fingerprint regression harnesses.
4. Confirm `evals/validate.mjs` uses Ajv 2020-12 with `strict: false` and `allErrors: true` before documenting validator behavior.
5. If validation is delegated to Orchestrator, report validation as not run by the acting documentation agent.

## Checklist E - Phase-Boundary Memory Hygiene

1. Keep `NOTES.md` limited to active objective, blockers, and pending high-level state.
2. Do not store phase history, verdict details, iteration logs, or artifact paths in `NOTES.md`.
3. Before any `/memories/repo/` write or `NOTES.md` update, load `skills/patterns/repo-memory-hygiene.md` and perform dedup/prune checks.
4. Put task-specific history under `plans/artifacts/<task-slug>/` instead of repo-persistent memory.
5. At final handoff, report whether memory files were untouched, updated by Orchestrator, or require follow-up.

## Output Shape

Return structured text with these sections:

- Traceability coverage: covered requirements, deferred items, and scope leaks.
- Alignment findings: schema/prompt/grant/eval mismatches and their severity.
- Hidden-defect triage: confirmed defects, feature ideas, and rejected false positives.
- Validation status: gates run, gates delegated, gates not run, and residual risk.
- Memory hygiene status: `NOTES.md` and repo-memory disposition.

## Completion Criteria

- Every finding cites local evidence.
- Every recommended fix maps to an approved file group or returns `needs_replan`.
- Documentation claims match current implementation, not planned intent.
- No raw JSON is emitted to chat.
