# Report Structure

## At a glance

- **Purpose:** Know where the triage script writes data, and which files to read first.
- **Use when:** You just ran triage or you’re onboarding a new maintainer workflow run.
- **Start here:** `executive-summary.md` → `triage.md` → `agent-briefs.md` → item files in `items/`.

## Output Layout

```
<reportsDir>/YYYY-MM-DDTHH-MM-SS/
├── README.md              # Navigation and run metadata
├── executive-summary.md   # Counts, actionability breakdown, top priorities
├── triage.md              # Prioritized queue with reasoning
├── agent-briefs.md        # Ready-to-work task briefs
├── agent-prompts.md       # Prompt drafts derived from briefs
├── run-summary.md         # Work files, notes, git summary
├── delta.md               # Changes since last run (if --delta)
├── contributors.md        # Contributor profiles for this run
├── data/
│   ├── issues.json        # Raw issue data
│   ├── prs.json           # Raw PR data
│   ├── contributors.json  # Contributor stats
│   └── state.json         # Run metadata for delta
└── items/
    ├── issues/
    │   └── ISSUE-<num>.md # Per-issue analysis
    └── prs/
        └── PR-<num>.md    # Per-PR analysis
```

`<reportsDir>/LATEST` contains the latest report path.

## File Purposes

| File | Purpose |
|------|---------|
| `executive-summary.md` | Quick overview: counts, actionability states, top items |
| `triage.md` | Prioritized list with citations, recommended actions, and an opportunity backlog |
| `agent-briefs.md` | Task briefs for items ready for agent work |
| `agent-prompts.md` | Prompt drafts derived from briefs |
| `run-summary.md` | Work files, notes, git summary |
| `delta.md` | What changed since last run (new, updated, closed, stale) |
| `contributors.md` | Contributor profiles with activity and notes |
| `ISSUE-*.md` | Per-issue: comments, intent, actionability, relationships |
| `PR-*.md` | Per-PR: comments, intent, files, review status, relationships |

First-time contributors are listed in `executive-summary.md` and detailed in `contributors.md`.

`triage.md` should include an "Opportunity Backlog" section for work not tied to a specific issue/PR (docs, onboarding, hygiene, UX).

## Item Markdown Structure

### Issues
```markdown
# ISSUE-42: Title

**State:** open | **Actionability:** ready | **Priority:** 85
**Author:** @username | **Created:** 2026-01-15 | **Comments:** 5
**Type:** bug | feature | question | support | meta
**Relationships:** mentions [ISSUE:40], mentioned by [PR:48]

## Summary
[Brief summary of what the issue is about]

## Intent
[Extracted intent - what does the reporter actually want?]

## Comment Analysis
| # | Author | Date | Intent | Tone | Actionable |
|---|--------|------|--------|------|------------|
| 1 | @user  | 1/15 | Report | Neutral | Yes - needs triage |

## Relationships
- Possible duplicate of [ISSUE:28]
- May be addressed by [PR:38]

## Notes
[Agent notes, blockers, next steps]

## Signals
- Sentiment Score: 2
- Needs-Info Score: 2 (missing-repro, missing-environment)

## Agent Review Prompt
[Checklist for the agent to validate intent, sentiment, and next actions]
```

### Pull Requests
```markdown
# PR-48: Title

**State:** open | **Actionability:** needs-analysis | **Priority:** 90
**Author:** @username | **Created:** 2026-01-15 | **Comments:** 3
**Files:** 5 | **Additions:** +120 | **Deletions:** -45
**Relationships:** addresses [ISSUE:42], [ISSUE:28]

## Summary
[Brief summary of what the PR does]

## Intent
[Extracted intent - what problem is this solving and why this approach?]

## Files Changed
| File | Changes | Risk |
|------|---------|------|
| src/core/loader.ts | +45/-12 | HIGH |
| tests/loader.test.ts | +60/-0 | LOW |

## Review Status
- CI: passing | failing
- Approvals: 0
- Changes requested: no

## Implementation Signals
- Implementation Score (auto): 24
- Agent Score: 6
- Agent Confidence: medium
- Implementation Score (final): 30
- Implementation Tier: medium
- Needs-Info Score: 1 (missing-test-plan)
- Relationship Score: 18
- Relationship Quality: medium
- Relationship Overlap: 0.32
- Sentiment Score: 4
- Linked issues: #42, #28 (priority sum: 55)
- Reactions: THUMBS_UP:3
- Touches tests: yes

## Comment Analysis
| # | Author | Date | Intent | Tone | Actionable |
|---|--------|------|--------|------|------------|

## Notes
[Agent notes, blockers, quality assessment]

## Agent Review Prompt
[Checklist for the agent to validate intent, sentiment, relationship quality, and implementation approach]
```

## Datetime Behavior

- Folder names use filesystem-safe ISO format: `YYYY-MM-DDTHH-MM-SS`
- Each run creates a new folder (no overwrites)
- Use `--datetime` to specify a custom timestamp
- `state.json` tracks run metadata for delta computation

## Delta Report

When `--delta` flag is used, `delta.md` contains:

```markdown
# Delta Report

**Previous run:** 2026-01-15T18-30-00
**Current run:** 2026-01-16T10-00-00
**Period:** 15.5 hours

## New Items
- [ISSUE:52] Feature request: skill templates (6h ago)

## Updated Items
- [ISSUE:45] New comment from @user
- [PR:48] CI now passing (was failing)

## Closed Items
- [ISSUE:30] Closed by maintainer

## Stale Items (>7 days no activity)
- [PR:38] No activity for 12 days
```
