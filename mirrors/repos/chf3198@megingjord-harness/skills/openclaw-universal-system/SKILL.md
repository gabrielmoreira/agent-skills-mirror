---
name: openclaw-universal-system
description: Make OpenClaw a reusable machine-global execution system for all VS Code Copilot agent chats, regardless of repository, by standardizing routing, observability, and decision checkpoints.
argument-hint: "[mode: activate|route|observe|audit] [task-summary]"
user-invocable: true
disable-model-invocation: false
---

# OpenClaw Universal System

## Purpose

This skill makes OpenClaw a **machine-global capability** instead of a repository-local convention.
It applies across all VS Code Copilot agent chats on this machine, regardless of the current folder or project.

## Global Scope

The canonical shared assets live here:
- Strategy: `~/.copilot/openclaw/OPENCLAW_UNIVERSAL_SYSTEM.md`
- Quick reference: `~/.copilot/openclaw/OPENCLAW_UNIVERSAL_QUICK_REF.md`
- Routing map: `~/.copilot/openclaw/task-router-profile-map.json`
- Bootstrap command: `~/.local/bin/openclaw-bootstrap-repo`

Repository docs may add overlays, but they should not redefine the global policy.

To connect a repository to this system, run:
- `global-skills-bootstrap-repo /absolute/path/to/repo init`
- `global-skills-bootstrap-repo /absolute/path/to/repo audit`

`openclaw-bootstrap-repo` remains available as a compatibility wrapper and delegates to the higher-level global-skills bootstrap.

The bootstrap keeps OpenClaw organized within the wider global-skills stack by updating or creating the repository's `global-skills.instructions.md` contract and then maintaining a dedicated OpenClaw overlay file.

## Activation Rule

Load this skill whenever a task involves one or more of:
- multi-file implementation
- architecture analysis or planning
- heavy testing or browser automation
- performance or static analysis
- long sessions where compute pressure may grow

For tiny edits, local execution is acceptable unless another repository policy overrides it.

## Universal Control Loop

Use this sequence in every project:

`CLASSIFY -> PRECHECK -> ROUTE -> EXECUTE -> OBSERVE -> VERIFY -> AUDIT`

1. **CLASSIFY**
   - Map the task to a universal task type using the routing map.
2. **PRECHECK**
   - Reuse `openclaw-availability-utilization` for gateway health and utilization checks.
3. **ROUTE**
   - Prefer OpenClaw for complex, long-running, high-memory, or multi-step work.
4. **EXECUTE**
   - Run the selected slice on the chosen lane.
5. **OBSERVE**
   - Emit or preserve decision evidence: task type, rationale, model/profile, confidence, lane.
6. **VERIFY**
   - Run repo-local tests or validation gates.
7. **AUDIT**
   - Compare actual usage against the target pattern and adapt the next slice.

## Universal Checkpoints

For substantive implementation work, evaluate OpenClaw at three checkpoints:
- **Design**: planning, decomposition, trade-off analysis
- **Implementation**: heavy coding, test generation, large refactors
- **Verification**: broad test suites, regression checks, release validation

Each checkpoint should produce a short rationale:
- why OpenClaw was used, or
- why local execution remained sufficient

## Task Routing Defaults

Use the shared routing map to classify work into:
- `code-generation`
- `analysis`
- `reasoning-advanced`
- `documentation`
- `testing`

Default guidance:
- `code-generation`, `analysis`, `reasoning-advanced`, `testing` -> prefer OpenClaw when scope is medium or heavy
- `documentation` -> local is acceptable unless the session already benefits from OpenClaw continuity

## Observability Minimum

Every project should capture at least this lightweight evidence in progress updates or logs:
- lane used
- task type
- confidence or complexity estimate
- rationale summary
- verification outcome

## Integration

Load together with:
- `operator-identity-context`
- `repo-standards-router`
- `openclaw-availability-utilization`
- `network-platform-resources` when remote/offloaded execution matters
- `workflow-self-anneal` after repeated drift or failures

## Success Standard

Global success means:
- the policy is reusable across repositories
- canonical guidance is stored under `~/.copilot`
- repository docs reference the global system instead of acting as the only source
- future projects can adopt the same operating model without copying the TSV Ledger docs
