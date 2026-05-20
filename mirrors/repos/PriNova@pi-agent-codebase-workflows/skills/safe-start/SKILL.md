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

## Artifact Compatibility Contract

Safe-start artifacts must be compatible with later `safe-change` work and with `codebase-recon` consolidation.

Baseline repo-level artifacts:

```text
README.md
AGENTS.md
.env.example                    # when env/config exists

docs/agent/
  REPO_INVENTORY.md
  PROJECT_INTENT.md
  ARCHITECTURE.md
  DATA_FLOW.md
  DATA_MODEL.md
  INVARIANTS.md
  DEPENDENCY_RULES.md
  DESIGN_ISSUES.md
  RISK_REGISTER.md
  CHANGE_GUIDE.md
  TESTING_STRATEGY.md
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

Artifact header guidance for durable docs:

```text
Status: current | partial | stale
Evidence: planned | observed | mixed
Last validated: unknown | <date>
```

Use `planned` before scaffold/implementation exists. Update to `observed` or `mixed` after validation against real files and commands.

Rules:
- Project operating instructions stay at root `AGENTS.md`.
- Do not create `docs/AGENTS.md` or `docs/agent/AGENTS.md`.
- Keep docs compact and operational.
- Docs should describe durable semantics, not tutorial prose, except in Freshman mode where short teaching notes are allowed.
- Avoid duplicate source-of-truth facts: `AGENTS.md` stays short and operational; semantic docs hold durable detail; `CHANGE_GUIDE.md` holds workflow.

## Context Budget and Non-Duplication

Each artifact should be either a source of truth for one semantic category or an index/router to other docs. Do not make every artifact a summary of every other artifact.

Artifact ownership:
- `AGENTS.md`: injected operating rules, forbidden shortcuts, validation expectations, and links only.
- `CHANGE_GUIDE.md`: workflow and doc-routing guide; link to semantic docs instead of repeating them.
- `SCOPES.md`: routing table for scoped docs; no detailed architecture or contract prose.
- `REPO_INVENTORY.md`: file tree, entry points, commands index, external boundaries; no architecture judgments.
- `PROJECT_INTENT.md`: product/user goals, non-goals, constraints, assumptions.
- `ARCHITECTURE.md`: components, boundaries, side-effect boundaries, high-level execution flows.
- `DEPENDENCY_RULES.md`: allowed/forbidden dependency direction and import boundaries.
- `DATA_FLOW.md`: input -> transformation -> output lifecycles, events, request paths, error states.
- `DATA_MODEL.md`: entities, schemas, IDs, relationships, persisted/serialized formats.
- `INVARIANTS.md`: rules, forbidden states, lifecycle constraints, enforcement locations.
- `DESIGN_ISSUES.md`: design drift, unresolved design problems, deferred decisions.
- `RISK_REGISTER.md`: failure modes with severity, evidence, failure scenario, suggested test/fix.
- `TESTING_STRATEGY.md`: test approach, coverage gaps, risk-to-test priorities.
- `VALIDATION_BASELINE.md`: exact commands, last status, blockers, next best checks.
- `CONTRACTS.md`: cross-scope APIs, schemas, events, generated clients, persistence/deployment interfaces.

Duplication rules:
- Prefer links/references over copied detail.
- If `VALIDATION_BASELINE.md` exists, `REPO_INVENTORY.md` may list command names but should link to baseline for status/blockers.
- If `TESTING_STRATEGY.md` exists, `CHANGE_GUIDE.md` should link to it for testing details.
- Top-level docs summarize stable repo-wide truths; scoped docs hold local detail.
- If a required artifact has little content, create a compact stub with `No known ...`, `Unknown`, or `Not yet validated`, not boilerplate prose.

## Scope/Focus Arguments

Prompt arguments may include a target, focus, scope, domain, service, package, app, tool, or environment. Use these to limit a pass to one planned boundary while keeping repo-level docs as summary/fallback.

When a scope/focus is provided:
- define whether it is path-based (`apps/web`, `packages/sdk`, `infra/prod`) or domain-based (`billing`, `identity`, `plugin-system`)
- create/update `docs/agent/SCOPES.md` before writing scoped docs
- write detailed findings to matching scoped artifacts, not only top-level docs
- update top-level docs only with stable repo-level summary or cross-scope guidance
- identify owner/consumer contracts when the scope exposes APIs, shared types, events, schemas, generated clients, persistence formats, deployment interfaces, CLIs, SDKs, plugins, or infra modules

## Scoped Artifacts

Use scoped safe-start artifacts for monorepos, enterprise-grade systems, dev-tools platforms, infra/IaC repos, multi-service systems, or any project where one repo-level summary would hide ownership boundaries.

Scoped artifacts mirror `codebase-recon` scope layout:

```text
docs/agent/
  SCOPES.md
  scopes/
    by-path/<repo-relative-path>/
      README.md              # optional local index for large/complex scopes
      REPO_INVENTORY.md
      PROJECT_INTENT.md
      ARCHITECTURE.md
      DATA_FLOW.md
      DATA_MODEL.md
      INVARIANTS.md
      DEPENDENCY_RULES.md
      DESIGN_ISSUES.md
      RISK_REGISTER.md
      CHANGE_GUIDE.md
      TESTING_STRATEGY.md
      VALIDATION_BASELINE.md
      CONTRACTS.md           # when scope owns cross-scope APIs/schemas/events
    by-domain/<domain-slug>/
      README.md              # optional local index for large/complex scopes
      PROJECT_INTENT.md
      ARCHITECTURE.md
      DATA_FLOW.md
      DATA_MODEL.md
      INVARIANTS.md
      DEPENDENCY_RULES.md
      DESIGN_ISSUES.md
      RISK_REGISTER.md
      CHANGE_GUIDE.md
      TESTING_STRATEGY.md
      VALIDATION_BASELINE.md
      CONTRACTS.md
```

`docs/agent/SCOPES.md` is required when scoped artifacts exist. Suggested columns:
- Scope
- Kind: `path` / `domain`
- Docs path
- Status: `planned` / `partial` / `current` / `stale` / `deprecated`
- Owns
- External contracts
- Last validated evidence

When to introduce scopes:
- monorepo with apps/packages/services under separate paths
- enterprise codebase with independently owned domains or bounded contexts
- dev-tools repo with CLI, SDK, server, extension, plugin, or template surfaces
- infra repo with environments, modules, deployment pipelines, policy, or runtime ops boundaries
- cross-scope contracts exist: APIs, shared types, events, generated clients, persistence formats, deployment interfaces

Scope rules:
- Prefer `by-path` when source path is known or will be scaffolded.
- Use `by-domain` for business/platform domains before final paths exist.
- Every cross-scope contract should have one owner scope documented in `CONTRACTS.md`.
- Consumer scopes link to owner contracts and record local usage/risk only.
- Top-level docs remain repo-level summaries and fallback guidance; scope docs hold detailed local truth.
- Safe-start handoff must explain whether future `safe-change` work should use top-level docs, scoped docs, or both.

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
1. Capture intent, guidance level, and whether scoped artifacts are needed.
2. Produce data-first design and scaffold plan.
3. Stop for approval before writing files unless user explicitly requested implementation.
4. Scaffold, validate, implement first vertical slice if approved/requested.
5. Report validation and handoff status, including whether future work should use scoped docs.

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
- `docs/agent/REPO_INVENTORY.md` with planned/observed scaffold inventory, entry points, validation commands, and external boundaries
- `docs/agent/SCOPES.md` when scoped artifacts are needed
- matching scoped `PROJECT_INTENT.md` / `REPO_INVENTORY.md` when a focus or scope is in play
- initial `README.md` summary if creating files now

Required sections for `PROJECT_INTENT.md`:
- Product goal
- Target users
- Primary user journeys
- Must-have features
- Non-goals
- Runtime/platform/deployment target
- Constraints and preferences
- Guidance level
- Scope model: unscoped repo, path scopes, domain scopes, or deferred
- Assumptions
- Open questions

Required sections for `REPO_INVENTORY.md`:
- Planned/observed project summary
- Planned/observed build and validation commands
- Planned/observed entry points
- Planned/observed major directories
- External dependencies/boundaries
- Scope registry summary when scoped artifacts exist
- Unknowns
- Next recommended design/scaffold targets

## Pass 2 — Data Flow Design

Prompt template: `/safe-start-02-data-flow`.

Read first: `docs/agent/PROJECT_INTENT.md` if present; `docs/agent/SCOPES.md` and matching scoped intent/inventory when scoped artifacts are in play.

Task: design data-first system shape.

Output/update:
- `docs/agent/DATA_FLOW.md`
- `docs/agent/DATA_MODEL.md`
- `docs/agent/INVARIANTS.md`
- matching scoped `DATA_FLOW.md`, `DATA_MODEL.md`, and `INVARIANTS.md` when a focus or scope is in play

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

Read first: project intent, data flow, data model, invariants, and `docs/agent/SCOPES.md` / matching scoped docs when scoped artifacts are in play.

Task: choose initial architecture after data shape is known.

Output/update:
- `docs/agent/ARCHITECTURE.md`
- `docs/agent/DEPENDENCY_RULES.md`
- `docs/agent/DESIGN_ISSUES.md`
- `docs/agent/RISK_REGISTER.md`
- `docs/agent/adr/0001-initial-architecture.md`
- matching scoped artifacts when a focus or scope is in play

Required sections:
- Architecture overview
- Module boundaries derived from data flow
- Dependency direction
- Side-effect boundaries
- Stack/framework/library decisions
- Configuration/secrets approach
- Error handling strategy
- Security/privacy basics
- Known design issues, deferred decisions, and drift risks
- Key risks and mitigations
- ADR with context, decision, alternatives, consequences

## Pass 4 — Project Contract Docs

Prompt template: `/safe-start-04-contract-docs`.

Read first: intent, data flow/model, architecture, dependency rules, and `docs/agent/SCOPES.md` / matching scoped docs when scoped artifacts are in play.

Task: create operational docs for future agents and developers.

Output/update:
- `README.md`
- `AGENTS.md`
- `docs/agent/CHANGE_GUIDE.md`
- `docs/agent/TESTING_STRATEGY.md`
- optional `docs/agent/CONTRACTS.md`, `SECURITY.md`, `DEPLOYMENT.md`
- matching scoped artifacts and owner `CONTRACTS.md` files when scoped artifacts are in play

Required content:
- How to understand project quickly
- Architecture rules
- Data flow and data model rules
- Invariants not to violate
- How to discover matching scoped docs through `docs/agent/SCOPES.md` when present
- How to add/modify features
- How to validate changes
- Documentation update rules, including planned/observed/status header updates when useful
- Freshman-friendly command explanations when guidance level is Freshman

## Pass 5 — Scaffold Plan

Prompt template: `/safe-start-05-scaffold-plan`.

Read first: all prior design docs, including `docs/agent/SCOPES.md` and matching scoped docs when scoped artifacts are in play.

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

Task: make baseline checks green before real feature depth. For scoped projects, validate repo-level commands plus independently runnable scope commands where practical.

Output/update:
- `docs/agent/VALIDATION_BASELINE.md`
- matching scoped `VALIDATION_BASELINE.md` for independently validated apps/packages/services/tools/infra scopes

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

Read first: prior docs and validation baseline, including matching scoped docs when scoped artifacts are in play.

Task: implement one small end-to-end feature crossing real boundaries. In scoped projects, choose one scope or one owner/consumer contract path for the first slice unless the user explicitly asks for a broader enterprise scaffold.

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
- `docs/agent/REPO_INVENTORY.md`
- `docs/agent/DESIGN_ISSUES.md`
- `docs/agent/SCOPES.md` when scoped artifacts exist
- optional `docs/agent/BACKLOG.md`

Checklist:
- root `AGENTS.md` exists and is operational
- `REPO_INVENTORY.md` exists and reflects planned vs observed scaffold state
- `DESIGN_ISSUES.md` exists, even if it says no known issues/deferred decisions
- docs/agent artifacts cover architecture, data flow, data model, invariants, dependency rules, tests, risks, validation baseline
- `CHANGE_GUIDE.md` links or points to `PROJECT_INTENT.md`, `DATA_FLOW.md`, `TESTING_STRATEGY.md`, and `VALIDATION_BASELINE.md` when relevant
- validation baseline commands are known and recently run
- first slice is implemented or explicitly deferred
- scoped docs exist when repo complexity warrants them, with `SCOPES.md` identifying owners and contracts
- next work items are small enough for `safe-change`

Final note should say whether future work should use `safe-change`, whether scoped docs should be read, and which docs to read first.
