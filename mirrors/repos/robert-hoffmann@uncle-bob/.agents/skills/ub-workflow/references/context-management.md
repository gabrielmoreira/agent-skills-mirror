# Context Management

Use this reference when interpreting context tiers, read budgets, atlas routing,
frontmatter, receipts, retained-context reads, evidence routing, or broader
writeback decisions.

## Purpose

Workflow context management keeps durable workflow artifacts useful without
turning every resume into a full archive read. It defines what must be loaded
by default, what is conditional, and what stays retained until a concrete
trigger makes it relevant.

## Core Rule

Retrieval proposes context. Owner artifacts commit durable truth.

Do not treat search results, source packs, old closeouts, or raw evidence as
live operating state. Promote only the facts that change current direction into
the current owner: `status.md`, `vision.md`, `wave.md`, `initiative.md`,
`roadmap.md`, `index.md`, or the active sprint pack.

## Design Basis

The tier model is a `ub-workflow` retrieval policy, not an external industry
standard. It exists to apply common product and documentation principles:

1. make important work visible enough for inspection and adaptation;
2. keep policies explicit, sparse, simple, visible, and easy to revise;
3. reduce work in progress and context switching by loading only the context
   needed for the current decision;
4. optimize documentation for clarity, findability, and reliability;
5. record meaningful decisions with enough context to avoid repeating the same
   debate later.

Use the least context that preserves truth. Exceed the normal read set when the
work needs it, then record why.

Context tiers may change over an artifact's lifecycle. Draft or active
discoveries and sprint packs are normally T2. Accepted discoveries, passed
sprint packs, closeouts, decision logs, and initiative indexes are normally T3
because they are triggered lookup and history surfaces, not routine route
steering surfaces.

## Context Tiers

| Tier | Name | Default load | Examples | Use |
| --- | --- | --- | --- | --- |
| T0 | Startup spine | Yes | root `AGENTS.md`, `.ub-workflows/status.md`, compact current state, `vision.md` when product direction matters | Resume orientation and next allowed action |
| T1 | Route maps and policy | Conditional | `WORKFLOW_ATLAS.md`, `SOURCE_PACK_ATLAS.md`, `SOURCE_ATLAS.md`, this reference | Decide where to look and which contract applies |
| T2 | Active work package | Conditional | active `wave.md`, `initiative.md`, `roadmap.md`, active discovery, active sprint pack | Execute or steer current work |
| T3 | Retained memory | Triggered | initiative `index.md`, source packs, retained notes, accepted discoveries, passed sprint packs, old closeouts | Recover background without polluting startup |
| T4 | Detailed evidence | Triggered | evidence indexes, validation records, live-smoke notes, audit logs | Verify specific claims |
| T5 | Raw or archive detail | Rare | raw logs, long transcripts, archived research, original captures | Inspect only when necessary and safe |

## Atlas Roles

`WORKFLOW_ATLAS.md` routes workflow artifacts: waves, initiatives,
discoveries, sprints, current owners, initiative indexes, and retained
workflow notes.

`SOURCE_PACK_ATLAS.md` routes retained research packs. Search the atlas before
opening source packs, then open the pack readme before any detailed section.

`SOURCE_ATLAS.md` routes project source code. It is created during bootstrap by
a one-time scan, then updated only when source boundaries, package lanes, or
test topology change.

## Phase Read Budgets

These are steering budgets, not hard caps. If a phase needs more, record a
budget exception in the context receipt.

| Phase | Normal read set | Warn when |
| --- | --- | --- |
| Resume | T0 plus directly named files | More than 5 files |
| Workflow artifact work | T0, relevant atlas, active owner, touched artifact | More than 10 files |
| Discovery creation | T0, owner artifacts, routed source/source-pack context | More than 12 files or more than 3 source-pack files |
| Sprint preview | Accepted discovery or route, owner artifacts, target source routes | More than 10 files before source verification |
| Sprint implementation | Sprint pack plus routed source/tests | Broad source traversal lacks a route reason |
| Sprint closeout | Sprint pack, evidence index, changed owners | Broader writebacks lack owner-change reasons |
| Final audit | Roadmap, triggered index, retained note, latest closeouts, evidence summaries, wave criteria | Startup owners are reread without a routing reason |
| Wave transition | Status, current wave, next wave candidate, latest index/closeout, vision if direction changes | Source packs are read without a transition trigger |

## Frontmatter Contract

Current workflow artifacts should start with compact metadata:

```yaml
---
artifact_id          : w11-i01-d01-example
artifact_type        : discovery_brief
status               : draft
context_tier         : T2
updated_at           : 2026-05-28
summary_budget_lines : 24
---
```

Fields:

1. `artifact_id`: stable local identifier, usually matching wave, initiative,
   discovery, or sprint IDs.
2. `artifact_type`: portable role of the artifact.
3. `status`: current lifecycle state for this artifact, not project state.
4. `context_tier`: retrieval tier from T0 through T5.
5. `updated_at`: last meaningful owner update date.
6. `summary_budget_lines`: expected compact-read size for summaries and
   resumes. It is role-based advisory retrieval metadata, not a hard lint gate,
   full-file ceiling, or truncation instruction for validation reads.

## Budget Calibration

Use role-based budget bands instead of forcing every artifact toward the same
size:

1. product vision: generous enough for the full editable product PRD;
2. status and route maps: compact enough for routine startup or routing;
3. wave and initiative charters: concise owner truth, not chronology;
4. roadmaps: enough for live route, forecast control, and candidate briefs;
5. initiative indexes: triggered lookup/history, not route planning;
6. discoveries and sprint plans: enough for decision context and execution
   detail after a routed trigger;
7. closeouts and decision logs: enough for result, learning, and carry-forward;
8. evidence indexes and proof notes: enough for claim verification.

Line budgets may be above current line count when the artifact intentionally
has room to grow within its role. If an artifact regularly needs far more than
its role band, split ownership before merely raising the number.

Common artifact types:

```text
workflow_status
product_vision
workflow_atlas
source_pack_atlas
source_atlas
wave_charter
discovery_brief
initiative
initiative_roadmap
initiative_index
retained_note
sprint_plan
sprint_decision_log
sprint_closeout
evidence_index
source_pack_readme
research_claim_registry
workflow_reference
```

Historical captures may keep old artifact types as capture-time truth. Do not
rewrite raw historical evidence only to normalize metadata.

## Source-Pack Readme Metadata

Every source pack includes `00-readme.md` with the standard frontmatter fields
and:

1. status;
2. date basis;
3. read triggers;
4. do-not-read triggers;
5. default section limit;
6. promotion rule;
7. last reviewed date when known.

Source packs preserve retained context. They do not authorize delivery by
themselves.

## Trace Tokens

Trace-token lookup policy lives in `references/trace-tokens.md`. Trace tokens
are owner-only anchors for workflow lookup, not closeout summaries or metadata
payloads.

## Context Receipt

Include a receipt when context choice affects confidence.

Required receipt triggers:

1. discovery acceptance;
2. sprint preview or closeout;
3. final audit or wave transition;
4. retained context was opened;
5. the normal read budget was exceeded;
6. a broader writeback decision is being made.

```text
Context receipt:
- Loaded: <files intentionally read>
- Skipped: <nearby files intentionally not read>
- Source-pack fanout: <none | files read and why>
- Budget exception: <none | reason>
```

Good receipts explain the route, not every incidental search result. For small
owner-only edits, do not create receipt boilerplate unless one of the triggers
applies.

## Retained-Context Read Receipt

Use this when source packs, retained notes, historical discoveries, or old
closeouts shape current work:

```text
Retained-context read receipt:
- Trigger: <why retained context was needed>
- Search: <query or route used>
- Opened: <readme and at most one section by default>
- Promoted: <fact promoted into current owner artifact>
- Not promoted: <retained facts left as background>
```

If retained context changes current direction, promote the changed fact into
the owner artifact before accepting the discovery or closeout.

## Evidence Index Shape

Sprint evidence belongs behind `evidence/index.md` unless a host deliberately
chooses a stricter evidence store. The index is a claim-to-proof router, not a
second closeout or a raw evidence dump:

```text
State:
<sprint status, date, and validation posture>

Validated Claims:
| Claim | Evidence | Gate | Status | Consumed By |
| --- | --- | --- | --- | --- |
| <claim> | <file or command pointer> | <validation/live/audit gate> | <passed/blocked/deferred/not triggered> | <closeout/index/roadmap/status/etc.> |

Evidence Files:
| File | Type | Status | Open When |
| --- | --- | --- | --- |
| <path> | <validation/live/audit/proof/no-secret/etc.> | <status> | <specific trigger> |

Live Gates And Deferred Evidence:
<required, conditional, not-triggered, out-of-scope, or deferred gates>

Redaction And Retention:
<what is allowed, what is excluded, and whether raw/archive evidence exists>

Promotion:
<owners updated by closeout or intentionally left unchanged>

Read Policy:
<when to open the index or focused evidence files>
```

The evidence index is T4. It should be opened through a specific validation or
audit trigger, not as normal startup context. Material closeout claims must be
backed by the validated-claims table; unresolved or unavailable proof must be
recorded as blocked, deferred, not triggered, or out of scope.

Generated runtime state under sprint evidence (any project-specific
scratch directory) is local scratch by default. Do not commit it unless the
sprint explicitly approves a no-secret export; commit redacted evidence files
and summarize scratch-state disposition in the evidence index instead.

## Broader Writeback Decision

Closeout must decide whether work changed broader owners:

```text
Broader writeback:
- status.md: <yes/no and owned truth changed>
- vision.md: <yes/no and owned truth changed>
- wave.md: <yes/no and owned truth changed>
- initiative roadmap/index: <yes/no and owned truth changed>
- source packs: <yes/no and retained doctrine changed>
```

Writebacks update owned facts by replacement. Do not append chronology just to
record that a sprint happened.

## Live Validation Matrix

Sprint previews and closeouts use a live validation matrix when external
systems, credentials, UI checks, provider behavior, or timing-sensitive claims
matter:

```text
| Gate | Required? | Owner | Evidence path | Status |
| --- | --- | --- | --- | --- |
| <gate> | yes/no/conditional | agent/operator | <path or none> | pending/passed/failed/deferred |
```

Missing credentials or operator action is `blocked pending operator action`
unless the operator explicitly postpones the live gate.

## Research Claim Registries

When discovery relies on outside research or retained source packs, keep claims
traceable:

```text
| Claim | Source | Checked at | Confidence | Promoted to |
| --- | --- | --- | --- | --- |
| <claim> | <source pack or URL> | <date> | high/medium/low | <owner or none> |
```

Do not preserve long quotes or raw captures in current owner artifacts. Keep
capture-time truth in source packs or evidence records.

## Manual Checks

Useful repository checks:

```text
rg -n "Context receipt|Broader writeback|Retained-context read" .ub-workflows
rg -n "context_tier|summary_budget_lines" .ub-workflows
rg --files .ub-workflows/waves -g "**/sprints/**/evidence/index.md"
```
