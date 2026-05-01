# Per-Repo State Template

## At a glance

- **Purpose:** The canonical file layout for `.github/maintainer/` (project memory).
- **Use when:** First run bootstrapping, fixing missing state, or reshaping the maintainer folder.
- **Output:** Correct directory structure + templates copied, ready for customization.

Initialize `.github/maintainer/` in each repository with these files.

## Directory Structure

```
.github/maintainer/
├── config.json         # Machine-readable settings for triage
├── context.md         # Project identity, priorities, tone
├── decisions.md       # Decision log with reasoning
├── contributors.md    # Notes on specific contributors
├── patterns.md        # Observed patterns and learnings
├── standing-rules.md  # Automation policies
├── notes/             # Persistent per-item analysis
├── work/              # Working briefs/prompts/opportunities
├── index/             # Machine index + graph
├── semantics.generated.json # Agent-derived semantics/heuristics
├── runs.md            # Run ledger
└── state.json         # Technical state for scripts
```

## config.json

```json
{
  "schemaVersion": 1,
  "reportsDir": "reports",
  "stateFile": ".github/maintainer/state.json",
  "noMergeExternalPRs": true
}
```

For the full config template and options, see [config.md](config.md).

## context.md

```markdown
# Project Context

## Vision
[One paragraph: what is this project and why does it exist?]

## Current Priorities
1. [Top priority]
2. [Second priority]
3. [Third priority]

## Success Metrics
- [Adoption goal or usage signal]
- [Quality goal: reliability, docs, tests, etc.]

## Areas

| Area | Status | Notes |
|------|--------|-------|
| `src/core/` | Stable | High scrutiny for changes |
| `src/cli/` | Active | Moderate churn okay |
| `docs/` | Needs work | Contributions welcome |

## Contribution Guidelines
- [Key guideline 1]
- [Key guideline 2]

## Tone
[How should responses sound? Formal? Casual? Technical?]

## Out of Scope
- [Thing we explicitly don't want]
- [Another thing]
```

## decisions.md

```markdown
# Decision Log

## 2026-01

### [ISSUE:42] Deferred - Version requirements
**Date:** 2026-01-15
**Decision:** Defer to post-1.0
**Reasoning:** Good feature but adds complexity. Want to stabilize core first.

### [PR:38] Closed - Implemented fix
**Date:** 2026-01-16
**Decision:** Closed after maintainer implementation
**Reasoning:** Fixes critical bug affecting all Windows users. Tests pass.

### [ISSUE:30] Closed - Stale
**Date:** 2026-01-16
**Decision:** Closed without action
**Reasoning:** No response to info request for 60 days.
```

## contributors.md

```markdown
# Contributor Notes

## Active Contributors

### @username
- **First seen:** 2025-12-15
- **Contributions:** 3 PRs (2 implemented), 5 issues
- **Strengths:** Good tests, clear descriptions
- **Notes:** Offered to help maintain. Responsive.

### @another-user
- **First seen:** 2026-01-10
- **Contributions:** 1 PR (pending)
- **Notes:** First-time contributor. Needs guidance on tests.

## Former Contributors

### @past-contributor
- **Active:** 2025-06 to 2025-09
- **Notes:** Great work on CLI. Moved on to other projects.
```

## patterns.md

```markdown
# Observed Patterns

## Recurring Issues

### Windows Path Handling
- **First seen:** 2025-12-15
- **Frequency:** 8 duplicate reports
- **Root cause:** Hardcoded `/` instead of `path.sep`
- **Resolution:** Fixed in v1.3.1
- **Prevention:** Added Windows CI

### Version Display Mismatch
- **First seen:** 2025-12-19
- **Cause:** Hardcoded version string not updated
- **Resolution:** Read from package.json dynamically

## Contributor Patterns

- Chinese-speaking user base is significant (consider i18n)
- Contributors often submit multiple PRs for same issue (need faster review)

## Codebase Patterns

- Most bugs cluster in `src/cli/` (needs refactoring)
- Test coverage gaps in error handling paths
```

## standing-rules.md

```markdown
# Standing Rules

## Stale Policy

| Condition | Days | Action |
|-----------|------|--------|
| Issue waiting on reporter | 30 | Comment asking for update |
| Issue waiting on reporter | 60 | Close as stale |
| PR waiting on author | 30 | Close as stale |

## Auto-Labels

| Condition | Label |
|-----------|-------|
| PR touches `src/core/` | `core` |
| Issue mentions "windows" | `platform:windows` |
| First-time contributor | `first-contribution` |

## External PR Handling

- Never merge external PRs
- Extract intent and implement fixes directly
- Close PRs with explanation and credit
```

## state.json

```json
{
  "schemaVersion": 1,
  "lastRunAt": "2026-01-16T10:30:00Z",
  "lastReportDir": "reports/2026-01-16T10-30-00",
  "issueHashes": {
    "42": "abc123",
    "43": "def456"
  },
  "prHashes": {
    "38": "ghi789"
  }
}
```

The `*Hashes` fields store content hashes for detecting updates between runs.

## Initialization

When the skill detects no `.github/maintainer/` folder:

1. Create the directory structure
2. Copy templates from this file
3. Create `config.json` using the template (see `config.md`)
4. Prompt user to fill in `context.md` with project-specific information
5. Initialize `state.json` with empty state

The other files (`decisions.md`, `contributors.md`, `patterns.md`) start nearly empty and grow over time as the agent records observations.
