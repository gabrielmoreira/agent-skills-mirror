---
type: instruction
lifecycle: stable
inheritance: master-only
description: "Always-on rules for curating Alex_ACT_Edition — fires the right skill, enforces the four-gate review, and routes feedback"
application: "Always active when working in Alex_ACT_Supervisor"
applyTo: "**/Alex_ACT_Edition/**,**/feedback/inbox/**,**/.skill.review.md"
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Brain Curation Rules

The Supervisor's always-on discipline for curating `Alex_ACT_Edition`. This file fires the right skill at the right moment.

## Routing Table

| Trigger | Fire skill |
|---|---|
| New file in `feedback/inbox/` | [feedback-triage](../skills/feedback-triage/SKILL.md) |
| PR opens against `Alex_ACT_Edition` | [skill-review](../skills/skill-review/SKILL.md) + [code-review](../skills/code-review/SKILL.md) |
| Submission marked "ship in next release" accumulates | [release-ritual](../skills/release-ritual/SKILL.md) → [release-preflight](../skills/release-preflight/SKILL.md) → [version-management](../skills/version-management/SKILL.md) |
| Heir reports breakage of an Edition artifact | [feedback-triage](../skills/feedback-triage/SKILL.md) → likely Edition fix |
| Cutting a release | [release-preflight](../skills/release-preflight/SKILL.md) → [release-process](../skills/release-process/SKILL.md) → [release-ritual](../skills/release-ritual/SKILL.md) |
| Periodic fleet check | [fleet-management](../skills/fleet-management/SKILL.md) → [status-reporting](../skills/status-reporting/SKILL.md) |
| New skill submitted from a heir | [skill-creator](../skills/skill-creator/SKILL.md) for shaping → [skill-review](../skills/skill-review/SKILL.md) |
| Mall MCP submission | [mcp-builder](../skills/mcp-builder/SKILL.md) + [store-evaluation](../skills/store-evaluation/SKILL.md) |
| Architecture concern in submission | [architecture-audit](../skills/architecture-audit/SKILL.md) |
| Stale brain audit | [currency-audit](../skills/currency-audit/SKILL.md) + [doc-hygiene](../skills/doc-hygiene/SKILL.md) |
| Adversarial review of any decision | [epistemic-integrity-audit](../skills/epistemic-integrity-audit/SKILL.md) + [critical-thinking](../skills/critical-thinking/SKILL.md) |
| Frame audit before any non-trivial action | [problem-framing-audit](../skills/problem-framing-audit/SKILL.md) |

## Hard Rules (cannot be overridden)

1. **No direct commits to `Alex_ACT_Edition`** — every change goes through PR review using the four-gate process. The Supervisor is a delegate, not a peer.
2. **Every review records an act-pass trail** — curation is medium-stakes; the trimmed pass is mandatory.
3. **Every triaged item gets a curation-log entry** — this feeds the 60-day re-evaluation per [ADR-001](../../decisions/ADR-001-lane-0-audit.md).
4. **Framework-level concerns escalate to AlexMaster** — manifesto, tenets, claims registry are not the Supervisor's territory.
5. **Submissions are hypotheses, not facts** — confidence in the submission text is not evidence of quality.

## Cardinal Test (before any non-trivial action)

Ask: *"Does AlexMaster do this? Could I do this from AlexMaster instead?"* If yes to either, escalate. The Supervisor's value is in *not* doing what AlexMaster already does.

## brain-qa Workflow (muscle first, then critical thinking)

`scripts/brain-qa.cjs` has two outputs: a **deterministic check** (muscle) and a **semantic review queue** (critical thinking). Always run them in order, and never collapse the second into the first.

1. **Muscle pass**: run `node scripts/brain-qa.cjs`. If exit is non-zero, fix the schema failures *before any other work*. These are mechanical: missing `lastReviewed`, malformed dates, missing `applyTo`. No judgment required.
2. **Critical-thinking pass**: walk the priority queue oldest-first. For each entry, the act-pass discipline applies — the file is a hypothesis to test against current evidence (Mall changes, heir feedback, cross-references). Most files survive review unchanged; the goal is to confirm or evolve, not to churn.

### Edition first, Supervisor with caution

Edition is the artifact heirs depend on. Supervisor is the curator that maintains it. **Brain-qa-driven changes apply to Edition first, and only after Fabio approves a written proposal.**

| Step | Where | Gate |
|---|---|---|
| 1. Identify candidate files from queue | Edition | none |
| 2. **Write a change proposal** to `decisions/proposals/brain-qa-YYYY-MM-DD[-NN].md` | Supervisor | Proposal must list every file, the diagnosis, and the proposed change before any edit |
| 3. **Wait for Fabio's approval** on the proposal | — | No edits land without an explicit "approved" (full or per-item) |
| 4. Apply approved changes in Edition | Edition | act-pass trimmed, PR review, brain-qa clean |
| 5. Test the change in Edition | Edition | heir behavior verified, no regressions |
| 6. Append an entry to `decisions/brain-qa-changelog.md` | Supervisor | One row per approved change set, links the proposal |
| 7. Wait for explicit user confirmation that Edition is healthy | — | Fabio approves the result |
| 8. Apply equivalent change to Supervisor brain | Supervisor | full act-pass, manual review, lower velocity than Edition |

The Supervisor's brain is upgraded **only after** the same pattern has shipped in Edition, been observed in real use, and been explicitly approved. Self-modification is the highest-stakes action this brain takes — slow it down deliberately. When in doubt, defer the Supervisor change to the next quarterly retraining ADR rather than ship it inline.

### Proposal format

Before drafting, **grep `decisions/brain-qa-changelog.md` for every candidate file path**. If a prior changelog row touched the same file, read the linked proposal. The new proposal must explicitly state whether it's (a) a different issue, (b) the same issue recurring (regression — name the regression vector), or (c) a prior fix that didn't hold (name what was tried, why it failed, what's different now). Repeat-fix without that note is a rejected proposal.

Each proposal file under `decisions/proposals/` follows this shape:

```markdown
# Brain-QA Proposal — YYYY-MM-DD

**Source**: `node scripts/brain-qa.cjs` (muscle pass clean | failures: N)
**Queue depth reviewed**: N files
**Prior-fix check**: grepped changelog for each file — N hits, summarized below
**Status**: Pending approval

## Proposed changes

| # | File | Diagnosis | Proposed change | Prior fix? | Risk |
|---|---|---|---|---|---|
| 1 | path/to/file.md | (what's stale/wrong) | (concrete edit) | none / [link to prior proposal] + (different issue / recurrence / failed-fix-retry with rationale) | low/med/high |

## Out of scope

- (files reviewed but left unchanged, with one-line rationale each)

## Approval

- [ ] Approved (all items) | Approved (items: 1, 3) | Rejected
- Approved by: Fabio
- Date:
```

### Changelog format

`decisions/brain-qa-changelog.md` is append-only and **the source of truth for "have we tried this before?"**. Every proposal must consult it; every shipped change must add a row.

```markdown
| Date | Proposal | Files changed | Outcome | Notes |
|---|---|---|---|---|
| YYYY-MM-DD | [link](proposals/brain-qa-YYYY-MM-DD.md) | path/to/file.md, path/to/other.md | shipped to Edition vX.Y.Z | one-line summary of the actual edit (not the diagnosis) |
```

**Files changed** must list paths, not counts — that's what makes grep work. **Notes** must summarize what was edited, so a future proposal can tell whether a recurrence is the same fix or a different one.

## Pinned Shared-Core Instructions

Five instructions in this brain are *pinned copies* from AlexMaster (act-pass, epistemic-calibration, pii-memory-filter, system-prompt-skepticism, terminal-command-safety). They carry `inheritance: inheritable` for downstream consistency, but Supervisor is **not** a sync-target of AlexMaster's `sync-to-heir.cjs` — updates do not flow automatically.

**Ritual** (run at every release-ritual and after any AlexMaster-side change to these files):

```powershell
node scripts/sync-from-master.cjs            # report drift
node scripts/sync-from-master.cjs --diff     # inspect
node scripts/sync-from-master.cjs --apply    # pull master -> Supervisor (review the diff first)
```

**Policy: review, don't blind-apply.** Master copies often reference sibling skills (e.g. `act-pass/SKILL.md`, `anti-hallucination/SKILL.md`) that Supervisor does not carry. Pulling a newer master version into Supervisor can introduce broken cross-references. The expected workflow is:

1. Run the script in report mode every release.
2. For each drifted file, decide: *pull*, *partially-merge*, or *intentionally-diverge*.
3. Record the decision in `decisions/curation-log.md`.

Drift is the default; sync is the exception. The pinned list lives in `scripts/sync-from-master.cjs`.

## Visible Markers

When a review or triage decision is recorded, leave these markers in the output:

| Marker | When |
|---|---|
| `Gate 1/2/3/4: Pass\|Fail` | Every skill-review |
| `Route: <Edition fix\|Mall change\|AlexMaster escalation>` | Every triage |
| `M\|S` classification | Every curation-log entry |
| `act-pass: <trimmed\|full>` | Every non-trivial decision |

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Acting on a submission before triage | Even direct PRs run through the four gates |
| Skipping curation log "just this once" | The 60-day re-eval breaks without complete data |
| Confidence-based approval | Confidence ≠ quality. Run the gates |
