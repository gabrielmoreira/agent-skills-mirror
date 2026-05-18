---
name: safe-start
description: Safe greenfield project creation workflow. Use when starting a new project from scratch, bootstrapping a repo, choosing initial architecture, scaffolding baseline tooling, creating project-agent docs, and implementing the first thin vertical slice. Adapts guidance for freshman, standard, and expert developers.
---

# Safe Start

Goal: create new projects safely by defining data-first project truth before code, scaffolding the smallest validated baseline, then handing future work to `safe-change`.

## Core Principles

- Create durable project truth before feature depth.
- Design data flow first: input data -> transformations -> output data.
- Derive module boundaries from data and side-effect boundaries, not from early framework guesses.
- Keep architecture simple enough for current needs; record intentional extension points only.
- Build validation harness before real features.
- Implement one thin vertical slice before expanding scope.
- After baseline and first slice are validated, future changes should use `safe-change`.

## Guidance Levels

At start, determine guidance level from user preference or ask once:

```text
Preferred guidance level?
1. Freshman: explain decisions and commands.
2. Standard: concise but guided.
3. Expert: compact, assumption-driven.
```

Default: `Standard`.

Same safety gates apply at every level. Only communication and artifact density change:

- Freshman: more explanation, glossary, command notes, simpler questions, explicit file tree, starter tests, minimal jargon.
- Standard: concise decisions, enough rationale to maintain project safely.
- Expert: terse assumptions, ADRs, contracts, risk gates, extension points, fewer explanations.

## Target Artifacts

Create/update these before or during scaffold as appropriate:

```text
README.md
AGENTS.md
.env.example                    # when env/config exists

docs/agent/
  PROJECT_INTENT.md
  DATA_FLOW.md
  DATA_MODEL.md
  INVARIANTS.md
  ARCHITECTURE.md
  DEPENDENCY_RULES.md
  RISK_REGISTER.md
  TESTING_STRATEGY.md
  CHANGE_GUIDE.md
  VALIDATION_BASELINE.md
  adr/
    0001-initial-architecture.md
```

Optional when useful:

```text
docs/agent/BACKLOG.md
docs/agent/CONTRACTS.md
docs/agent/DEPLOYMENT.md
docs/agent/SECURITY.md
```

Rules:
- Project operating instructions stay at root `AGENTS.md`.
- Do not create `docs/AGENTS.md` or `docs/agent/AGENTS.md`.
- Keep docs compact and operational.
- Docs should describe durable semantics, not tutorial prose, except in Freshman mode where short teaching notes are allowed.

## Execution Modes

Default: numbered-pass mode.

Use one pass at a time for uncertain, high-risk, large, commercial, regulated, or multi-service projects:

```text
/safe-start-all
/safe-start-01-intent
/safe-start-02-data-flow
/safe-start-03-architecture
/safe-start-04-contract-docs
/safe-start-05-scaffold-plan
/safe-start-06-validation
/safe-start-07-vertical-slice
/safe-start-08-handoff
```

Optional all-in-one mode may be used when user explicitly asks and project is small/simple enough:

```text
/skill:safe-start all
```

In all-in-one mode:
1. Capture intent and guidance level.
2. Produce data-first design and scaffold plan.
3. Stop for approval before writing files unless user explicitly requested implementation.
4. Scaffold, validate, implement first vertical slice if approved/requested.
5. Report validation and handoff status.

## Approval Gates

Stop for approval after these outputs unless user explicitly requested implementation now:

1. Intent summary and assumptions.
2. Data-flow design and core data model.
3. Architecture/scaffold plan and validation commands.
4. First vertical-slice plan.

Never perform destructive actions, remote deployments, credential setup, paid service provisioning, production database changes, or publishing without explicit permission.

## Pass 1 — Intent Capture

Prompt template: `/safe-start-01-intent`.

Task: define project purpose, constraints, guidance level, scope, and non-goals.

Output/update:
- `docs/agent/PROJECT_INTENT.md`
- initial `README.md` summary if creating files now

Required sections:
- Product goal
- Target users
- Primary user journeys
- Must-have features
- Non-goals
- Runtime/platform/deployment target
- Constraints and preferences
- Guidance level
- Assumptions
- Open questions

## Pass 2 — Data Flow Design

Prompt template: `/safe-start-02-data-flow`.

Read first: `docs/agent/PROJECT_INTENT.md` if present.

Task: design data-first system shape.

Output/update:
- `docs/agent/DATA_FLOW.md`
- `docs/agent/DATA_MODEL.md`
- `docs/agent/INVARIANTS.md`

Required sections:
- External inputs
- User inputs
- Files/events/API payloads
- Core entities/value objects
- Identifiers and relationships
- Lifecycle/state transitions
- Validation and normalization
- Transformation pipeline
- Outputs: UI states, API responses, reports, side effects
- Error states
- Invariants and forbidden states
- Persistence/serialization draft if needed

## Pass 3 — Architecture Decisions

Prompt template: `/safe-start-03-architecture`.

Read first: project intent, data flow, data model, invariants.

Task: choose initial architecture after data shape is known.

Output/update:
- `docs/agent/ARCHITECTURE.md`
- `docs/agent/DEPENDENCY_RULES.md`
- `docs/agent/RISK_REGISTER.md`
- `docs/agent/adr/0001-initial-architecture.md`

Required sections:
- Architecture overview
- Module boundaries derived from data flow
- Dependency direction
- Side-effect boundaries
- Stack/framework/library decisions
- Configuration/secrets approach
- Error handling strategy
- Security/privacy basics
- Key risks and mitigations
- ADR with context, decision, alternatives, consequences

## Pass 4 — Project Contract Docs

Prompt template: `/safe-start-04-contract-docs`.

Read first: intent, data flow/model, architecture, dependency rules.

Task: create operational docs for future agents and developers.

Output/update:
- `README.md`
- `AGENTS.md`
- `docs/agent/CHANGE_GUIDE.md`
- `docs/agent/TESTING_STRATEGY.md`
- optional `docs/agent/CONTRACTS.md`, `SECURITY.md`, `DEPLOYMENT.md`

Required content:
- How to understand project quickly
- Architecture rules
- Data model rules
- Invariants not to violate
- How to add/modify features
- How to validate changes
- Documentation update rules
- Freshman-friendly command explanations when guidance level is Freshman

## Pass 5 — Scaffold Plan

Prompt template: `/safe-start-05-scaffold-plan`.

Read first: all prior design docs.

Task: propose minimal file tree and tooling before writing project code.

Output:
- concise scaffold plan
- package/build/test/lint/typecheck choices
- exact commands to create/install/run
- generated files list
- risks/assumptions

Scaffold should include only:
- package/build config
- formatter/linter/typecheck where suitable
- test runner
- app entrypoint
- minimal runtime health/hello path
- config/env example if needed
- CI only if requested or clearly expected

Avoid:
- speculative abstractions
- unused frameworks
- premature auth/payment/admin systems
- mock complexity beyond first slice needs

## Pass 6 — Validation Baseline

Prompt template: `/safe-start-06-validation`.

Task: make baseline checks green before real feature depth.

Output/update:
- `docs/agent/VALIDATION_BASELINE.md`

Required validations when applicable:
- install/bootstrap works
- format/lint command works
- typecheck/build works
- tests run
- app starts
- one smoke test proves runtime path

If any validation cannot run, record exact blocker and next best check.

## Pass 7 — Thin Vertical Slice

Prompt template: `/safe-start-07-vertical-slice`.

Read first: prior docs and validation baseline.

Task: implement one small end-to-end feature crossing real boundaries.

Slice should include:
- input adapter: UI/API/CLI/event/file as relevant
- validation/schema if relevant
- domain/core operation
- output adapter/rendering/API response
- persistence adapter or explicit in-memory/mock choice if persistence is deferred
- tests around core invariant and runtime path
- docs update only if durable semantics change

Stop at one slice. Do not build broad feature set.

## Pass 8 — Handoff to Safe Change

Prompt template: `/safe-start-08-handoff`.

Task: verify project is ready for normal documented-codebase workflow.

Output/update:
- `docs/agent/CHANGE_GUIDE.md`
- `docs/agent/RISK_REGISTER.md`
- optional `docs/agent/BACKLOG.md`

Checklist:
- root `AGENTS.md` exists and is operational
- docs/agent artifacts cover architecture, data, invariants, dependency rules, tests, risks
- validation baseline commands are known and recently run
- first slice is implemented or explicitly deferred
- next work items are small enough for `safe-change`

Final note should say whether future work should use `safe-change`, and which docs to read first.
