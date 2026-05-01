# Maintenance Workflow

## At a glance

- **Purpose:** Deep, step-by-step workflow details behind the SKILL.md runbook.
- **Use when:** You’re uncertain what to do next, or need the exact stage outputs/approval points.
- **Note:** SKILL.md is the canonical runbook; this file is the deeper reference.

## Core Philosophy: Agent-Implemented Fixes

**PRs are intelligence sources, not merge candidates.**

External PRs reveal:
- What problems exist
- How contributors attempted to solve them
- Edge cases and platform-specific issues

The agent's job is to:
1. Extract intent and insights from PRs
2. Understand the problem and approach
3. **Implement the fix yourself** using the PR as guidance
4. Thank contributors and close their PRs with explanation

Never merge external PRs directly. The agent writes all code.

## Maintainer Mindset

Act as a project steward who wants the repo to succeed. In addition to fixes, look for:
- Documentation gaps and onboarding friction
- UX or API rough edges
- Maintenance hygiene (tests, tooling, CI, release notes)
- Small improvements that increase adoption and trust
Apply CEV-style stewardship: optimize for what the project would want with better information and reflection, not just what is loudest.

## Pre-requisites

The triage script automatically initializes `.github/maintainer/` with template files on first run. After running, review and customize `context.md` with project-specific information. See [repo-state-template.md](repo-state-template.md) for template details.
The script also creates `.github/maintainer/config.json` with defaults if missing. See [config.md](config.md).
The agent maintains `.github/maintainer/semantics.generated.json` from templates/docs; do not edit manually.
Persistent notes live in `.github/maintainer/notes/` and are merged into each report.

## Workflow Stages

### Stage 0: Scope
- Confirm repo, date range, and scope (open items by default)
- Check `.github/maintainer/context.md` for project priorities and tone
- Determine approval policy (default: draft everything, ask before public actions)

### Stage 1: Capture
Run triage script from repo root:
```bash
npx tsx path/to/triage.ts [--delta] [--datetime YYYY-MM-DDTHH-MM-SS] [--config path]
```

Flags:
- `--delta`: Compare with previous run, generate delta.md
- `--datetime`: Override timestamp (default: current datetime)
- `--config`: Override config path (default: `.github/maintainer/config.json`)

Outputs to `<reportsDir>/YYYY-MM-DDTHH-MM-SS/` (default `reports/`).

### Stage 2: Analyze
For each item:
1. Read item markdown (e.g., `items/issues/ISSUE-42.md`)
2. Extract intent using [intent-extraction.md](intent-extraction.md)
3. Classify actionability (ready, needs-info, needs-decision, needs-analysis, blocked, stale, closable)
4. Score priority using config weights and label boosts from `.github/maintainer/config.json`
5. Review sentiment and relationship signals (PRs)
6. Map relationships to other items
7. Update item markdown with analysis
8. Update persistent note frontmatter for PRs (`agent_score`, `agent_confidence`, `agent_rationale`, `relationship_quality_final`)

Actionability is not a gate. Review every item. Use implementation score/tier to surface the best candidates.

Update `triage.md` with prioritized queue and `agent-briefs.md` with ready tasks. Draft per-task prompts in `agent-prompts.md` after synthesis.

### Stage 3: Synthesize Opportunities
Create an explicit opportunity list (docs, onboarding, hygiene, UX, release tasks) and fold the highest-impact items into the prioritized queue.

### Stage 4: Align
Present to human:
- Executive summary with actionability breakdown
- Top priorities with citations (e.g., `[ISSUE:42]`)
- Proposed actions (close, respond, implement, defer) plus opportunity work
- Items needing human decision

Wait for explicit approval before public actions.

### Stage 5: Execute
With approval:
- **Implement fixes yourself** using PR insights as guidance
- Draft responses thanking contributors
- Close PRs with explanation (agent implemented the fix)
- Close resolved issues with references
- Get approval before posting any public response

### Stage 6: Record
Update per-repo state:
- Log decisions to `.github/maintainer/decisions.md`
- Update `.github/maintainer/contributors.md` with notes
- Record patterns in `.github/maintainer/patterns.md`
- Update `state.json` with run metadata

## Delta Mode

When using `--delta`:
1. Script reads `.github/maintainer/state.json` to find last run
2. Compares current state with previous snapshot
3. Generates `delta.md` showing:
   - New items since last run
   - Updated items (new comments, status changes)
   - Closed items
   - Stale items (no activity threshold)

Focus analysis on delta items first, then review full backlog as needed.

## Human-in-the-Loop Points

Never automate without approval:
- Posting comments
- Closing issues/PRs
- Rejecting contributions

Draft all public-facing content first, present for review.
