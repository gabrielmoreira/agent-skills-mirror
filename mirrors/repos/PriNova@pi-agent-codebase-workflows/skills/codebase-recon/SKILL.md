---
name: codebase-recon
description: Reconstruction workflow for unfamiliar or undocumented codebases. Use to create compact semantic artifacts for architecture, data model, invariants, dependency rules, risks, root AGENTS.md, change guide, consolidation, ADRs, and risk-to-test planning. Supports numbered passes and all-in-one mode for small/simple repos.
---

# Codebase Reconstruction

Goal: build durable, compact project understanding for future agents through bounded reconstruction passes.

## Core Rules

- Work in bounded passes.
- Prefer one session per pass for large or unfamiliar repos.
- Allow all-in-one mode when user asks for it and repo appears small/simple enough for reliable sequential reconstruction.
- Do not edit production code during reconstruction.
- Each pass produces or updates one compact artifact.
- Later passes read prior artifacts instead of re-reading whole repo.
- Mark uncertainty as `Observed` with confidence: low / medium / high.
- Cite evidence: files, symbols, commands, tests.
- Write/update project-root `AGENTS.md`; never write `docs/AGENTS.md` or `docs/agent/AGENTS.md`.
- Do not tell agent to read `AGENTS.md`; the harness injects it automatically in new sessions.
- Consolidation is part of this workflow.

## Target Artifacts

Unscoped/repo-level artifacts:

```text
AGENTS.md

docs/
  agent/
    REPO_INVENTORY.md
    ARCHITECTURE.md
    DATA_MODEL.md
    INVARIANTS.md
    DEPENDENCY_RULES.md
    DESIGN_ISSUES.md
    RISK_REGISTER.md
    CHANGE_GUIDE.md
    adr/
      0001-observed-architecture.md
```

Scoped artifacts, created only when a pass receives a focus argument:

```text
docs/
  agent/
    scopes/
      by-path/<repo-relative-path>/
        README.md              # optional local index for large/complex scopes
        REPO_INVENTORY.md
        ARCHITECTURE.md
        DATA_MODEL.md
        INVARIANTS.md
        DEPENDENCY_RULES.md
        DESIGN_ISSUES.md
        RISK_REGISTER.md
        CHANGE_GUIDE.md
        CONTRACTS.md
      by-domain/<domain-slug>/
        README.md              # optional local index for large/complex scopes
        ARCHITECTURE.md
        DATA_MODEL.md
        INVARIANTS.md
        DEPENDENCY_RULES.md
        DESIGN_ISSUES.md
        RISK_REGISTER.md
        CHANGE_GUIDE.md
        CONTRACTS.md
```

`docs/agent/SCOPES.md` is created when scoped artifacts exist and acts as their registry. Top-level docs remain valid and are used as repo-level summaries/fallbacks.

## Focus Argument and Scoped Artifacts

Pass prompts accept an optional `[focus]` argument. Use it to scope reconstruction to a module, package, app, service, directory, or bounded domain area, especially in monorepos.

Examples:
- `/recon-01-inventory packages/api`
- `/recon-02-architecture apps/mobile auth flow`
- `/skill:codebase-recon pass-03-data-invariants services/billing`

When focus is absent:
- run the pass in unscoped mode
- write/update the standard top-level `docs/agent/*.md` artifact for the pass
- if scoped artifacts already exist, use them only when the pass explicitly calls for consolidation

When focus is provided:
- inspect only the focused area plus immediate dependencies, entry points, tests, and external boundaries needed to understand it
- if focus is an existing repo-relative path, write to `docs/agent/scopes/by-path/<focus>/`
- if focus is not a path, write to `docs/agent/scopes/by-domain/<slug>/`
- update `docs/agent/SCOPES.md` with scope path, docs path, status, ownership, and external contracts
- optionally create/update scoped `README.md` only when helpful for large/complex scopes; otherwise rely on `SCOPES.md` as the index
- write pass findings into the scoped artifact for that pass, not into the top-level artifact
- include evidence paths that show the scoped boundary
- mark interactions with the rest of the repo as external dependencies/boundaries
- leave cross-scope reconciliation for Pass 8 consolidation

Scoped docs are additive and backward compatible. If a repository was reconstructed before scoped artifacts existed, keep existing top-level docs. Create `SCOPES.md` and scoped artifacts only when the first scoped pass runs. Later consolidation may summarize scoped findings into top-level docs.

This enables module/package-level reconstruction first, then later consolidation into repo-level artifacts.

## Scope Registry and Contracts

`docs/agent/SCOPES.md` should stay compact and act as the discovery index for future workflows.

Suggested columns:
- Scope
- Kind: `path` / `domain`
- Docs path
- Status: `partial` / `current` / `stale` / `deprecated`
- Owns
- External contracts
- Last observed evidence

Each scoped directory may include `CONTRACTS.md` for cross-module APIs, shared types, schemas, events, generated clients, persistence boundaries, or public internal contracts.

Contract rules:
- every cross-scope contract should have one owner scope
- owner scope documents source of truth, compatibility rules, tests, and consumers
- consumer scopes link to owner contract and document local usage/risk only
- do not duplicate full contract rules across scopes
- generated clients reference source schema owner
- if ownership is unclear, record it as a known unknown or drift risk

## Execution Modes

Default: numbered-pass mode.

Use numbered-pass mode for large, complex, or unfamiliar repositories. User invokes one pass at a time, e.g.:

```text
/skill:codebase-recon pass-01-inventory
/skill:codebase-recon pass-02-architecture
/skill:codebase-recon pass-03-data-invariants
```

Equivalent numbered prompt templates are available as `/recon-01-inventory`, `/recon-02-architecture`, etc. At start of each later pass, read only relevant prior docs named in that pass. Do not re-analyze whole repository unless evidence is missing.

Optional: all-in-one mode.

Use all-in-one mode when user asks for it and repository size/complexity makes sequential reconstruction practical.

All-in-one mode may be requested with:
- `/skill:codebase-recon all`
- `/skill:codebase-recon all-in-one`
- `/recon-all`

Before all-in-one execution:
1. Inspect repository tree, package/build files, and major entry points.
2. Decide whether all-in-one mode is reasonable.
3. If not reasonable, explain why and recommend starting with Pass 1 only unless user explicitly wants to proceed.

In all-in-one mode, run passes 1–10 sequentially.

Rules:
- Write/update each artifact immediately after its pass.
- Treat written artifacts as source of truth for later passes.
- Before each pass, read only artifacts required by that pass.
- Keep each artifact compact and evidence-based.
- If repository proves larger or more complex than expected, finish current pass and report next numbered pass user should run.

Switch from all-in-one to numbered-pass mode when:
- repository is a monorepo or has multiple apps/packages/services
- source tree is too large to inspect meaningfully in one pass
- generated/vendor/build output dominates search results
- a pass requires deeper investigation than planned
- prior artifact needs substantial correction before later passes
- evidence is insufficient for next pass without broad re-reading

## Pass 1 — Repository Inventory

Task: write/update `docs/agent/REPO_INVENTORY.md`, or scoped `REPO_INVENTORY.md` when focus is provided.

Rules:
- No source edits.
- No architecture judgments yet.
- Inspect build/config/package files, directory tree, entry points, tests, validation commands, external boundaries.

Output sections:
- Project summary
- Build/test commands
- Entry points
- Major directories
- External dependencies/boundaries
- Unknowns
- Next recommended analysis targets

## Pass 2 — Architecture Reconstruction

Read first: `docs/agent/REPO_INVENTORY.md`.

Task: write/update `docs/agent/ARCHITECTURE.md`, or scoped `ARCHITECTURE.md` when focus is provided.

Find:
- dominant architecture style: vertical slices, layered, MVC, clean/onion/hexagonal, framework-driven, mixed/unclear
- major modules/components
- dependency directions
- where domain logic lives
- side-effect boundaries: file I/O, network, DB, UI, shell/CLI, LLM/API
- 2–5 important execution flows from entry point to output

Output sections:
- Architecture overview
- Component map
- Dependency direction
- Main execution flows
- Side-effect boundaries
- Observed inconsistencies
- Confidence notes

## Pass 3 — Data Model and Invariants

Read first: `docs/agent/REPO_INVENTORY.md`, `docs/agent/ARCHITECTURE.md`.

Task: write/update `docs/agent/DATA_MODEL.md` and `docs/agent/INVARIANTS.md`, or scoped `DATA_MODEL.md` and `INVARIANTS.md` when focus is provided.

Focus only on semantically important data crossing module boundaries, persisted/serialized formats, configs, APIs, IDs, states, lifecycles.

Output sections:
- Core data model
- Data lifecycle
- Persisted/serialized formats
- Invariants
- Enforcement locations
- Unenforced assumptions
- Risk notes

## Pass 4 — Dependency Rules and Drift Detection

Read first: `docs/agent/REPO_INVENTORY.md`, `docs/agent/ARCHITECTURE.md`, `docs/agent/DATA_MODEL.md`, `docs/agent/INVARIANTS.md`.

Task: write/update `docs/agent/DEPENDENCY_RULES.md` and `docs/agent/DESIGN_ISSUES.md`, or scoped `DEPENDENCY_RULES.md` and `DESIGN_ISSUES.md` when focus is provided.

Find:
- observed module dependencies
- cycles
- cross-slice coupling
- shared/common/utils dumping-ground risks
- UI/CLI/framework code containing domain logic
- core logic with side effects
- unstable dependencies leaking into stable code

Output sections:
- Observed dependency rules
- Recommended dependency rules
- Violations
- Coupling hotspots
- Shared/common risk areas
- Drift risks
- Suggested future architecture tests

## Pass 5 — Bug-Risk and Subtle-Failure Analysis

Read first: `docs/agent/ARCHITECTURE.md`, `docs/agent/DATA_MODEL.md`, `docs/agent/INVARIANTS.md`, `docs/agent/DEPENDENCY_RULES.md`.

Task: write/update `docs/agent/RISK_REGISTER.md`, or scoped `RISK_REGISTER.md` when focus is provided.

Find high-signal risks only:
- inconsistent state transitions
- unchecked null/None/undefined
- shared mutable data
- ordering assumptions
- ID/reference mismatch
- error handling gaps
- concurrency/async/races
- persistence corruption
- API/schema mismatch
- missing tests around critical invariants

For each risk:
- Title
- Severity: low / medium / high / critical
- Confidence: low / medium / high
- Evidence
- Failure scenario
- Affected files
- Suggested test
- Suggested fix direction

## Pass 6 — Root Agent Operating Guide

Read first: `docs/agent/ARCHITECTURE.md`, `docs/agent/INVARIANTS.md`, `docs/agent/DATA_MODEL.md`, `docs/agent/DEPENDENCY_RULES.md`, `docs/agent/RISK_REGISTER.md`, `docs/agent/DESIGN_ISSUES.md`.

Task: write/update root `AGENTS.md`.

Rules:
- Keep compact and operational.
- Link to deeper docs; do not duplicate them.
- Focus on rules that prevent drift and bugs.
- Include design/implementation/verification workflow.
- If `docs/agent/SCOPES.md` exists, include scoped-doc discovery guidance: future agents should check `SCOPES.md`, use longest matching path scope first, then repo-level fallback.
- Merge with existing root `AGENTS.md` if present.
- Do not create `docs/AGENTS.md` or `docs/agent/AGENTS.md`.

Suggested sections:
- Project summary
- Architecture rules
- Data model rules
- Invariants not to violate
- Side-effect boundaries
- How to make a change
- How to validate a change
- When to update docs
- Forbidden shortcuts
- Current high-risk areas

## Pass 7 — Change Guide

Read first: `docs/agent/ARCHITECTURE.md`, `docs/agent/DATA_MODEL.md`, `docs/agent/INVARIANTS.md`, `docs/agent/DEPENDENCY_RULES.md`.

Task: write/update `docs/agent/CHANGE_GUIDE.md`, or scoped `CHANGE_GUIDE.md` when focus is provided.

Required sections:
- Before coding
- How to locate affected slice/module
- How to discover matching scoped docs through `docs/agent/SCOPES.md` when present
- How to trace data flow
- How to add/modify data structures
- How to add side effects safely
- How to add tests
- How to avoid architecture drift
- Documentation update checklist
- Final verification checklist

## Pass 8 — Consolidation

Read root `AGENTS.md` if it exists, all relevant top-level `docs/agent/*.md`, `docs/agent/SCOPES.md` if present, and relevant scoped docs under `docs/agent/scopes/**` created by previous passes.

Task: consolidate artifacts.

Rules:
- No source code edits.
- Reconcile contradictions; do not silently delete disagreement evidence.
- Read `docs/agent/SCOPES.md` first when present; use it to select relevant scoped summaries and changed/relevant scoped docs.
- When scoped passes disagree, resolve from source evidence where possible, assign/clarify ownership for shared contracts where evidence supports it, or record the disagreement as a drift risk / `Known Unknown` with cited evidence.
- Keep detailed scope-specific facts in scoped artifacts; summarize only stable repo-level guidance in top-level docs.
- Update `SCOPES.md` status/currentness when consolidation identifies stale, deprecated, or reconciled scopes.
- De-duplicate repeated facts only after preserving the strongest evidence paths and any materially different scope-specific observations.
- Keep root `AGENTS.md` short and operational.
- Ensure `ARCHITECTURE.md` describes structure, not line-by-line code.
- Ensure `INVARIANTS.md` contains rules, not implementation notes.
- Ensure `RISK_REGISTER.md` contains actionable risks.
- Preserve uncertainty markers where evidence incomplete.
- Add `Known Unknowns` where useful.

## Pass 9 — Observed-Architecture ADR

Read first: `docs/agent/ARCHITECTURE.md`, `docs/agent/DEPENDENCY_RULES.md`, `docs/agent/DATA_MODEL.md`, `docs/agent/INVARIANTS.md`, `docs/agent/DESIGN_ISSUES.md`.

Task: write `docs/agent/adr/0001-observed-architecture.md`.

Structure:
- ADR 0001: Observed Current Architecture
- Status: Accepted as observed baseline
- Context
- Decision
- Evidence
- Consequences
- Known Issues
- Follow-up Actions

## Pass 10 — Risk-to-Tests Plan

Read first: `docs/agent/RISK_REGISTER.md`, `docs/agent/INVARIANTS.md`, `docs/agent/DATA_MODEL.md`, `docs/agent/CHANGE_GUIDE.md`.

Task: select top 3–5 risks to convert into tests first.

Selection criteria:
- high severity
- high confidence
- central invariant affected
- likely regression risk
- cheap to test

For each selected risk:
- Risk title
- Why test first
- Existing/new test file
- Test type: unit / characterization / regression / integration
- Exact scenario
- Expected behavior
- Minimal implementation plan

Do not write production code in this pass.
