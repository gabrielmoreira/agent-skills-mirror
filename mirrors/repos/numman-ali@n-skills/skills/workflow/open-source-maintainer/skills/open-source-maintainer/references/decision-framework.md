# Decision Framework

## At a glance

- **Purpose:** Make consistent, explainable maintainer decisions (close/defer/ask/implement).
- **Use when:** You are about to recommend an action on an issue/PR, especially closing/declining/deferring.
- **Gate:** Before closure/deferral recommendations, load this file.
- **Output:** A decision + rationale + (if public) a draft response for approval.

## Maintainer Intent

Act as a steward who wants the project to succeed. Beyond triage, seek high‑leverage improvements (docs, onboarding, examples, releases, tests, CI, API ergonomics).
Apply CEV-style stewardship: optimize for what the project would want with better information and reflection.

## Issue Decisions

### Close Without Action
- Duplicate of existing issue (link to original)
- Support request better suited for discussions/Discord
- Feature explicitly out of scope per `context.md`
- Stale >90 days with no response to info request
- Already resolved by maintainer fix or release
- Cannot reproduce and reporter unresponsive

### Request More Information
- Bug without reproduction steps
- Environment-specific issue without details
- Vague feature request
- Unclear expected vs actual behavior

### Defer (Label + Acknowledge)
- Good idea but not current priority
- Needs design discussion first
- Blocked by external dependency
- Resource constrained

### Prioritize for Work
- Blocking users (security, crash, data loss)
- High engagement (reactions, comments)
- Aligns with current priorities in `context.md`
- Quick win with clear path

## PR Decisions

**PRs are intelligence sources, not merge candidates.** Extract insights and implement fixes yourself.

### Extract and Implement
When a PR addresses a real problem:
1. Read the PR code to understand the fix approach
2. Identify the root cause they diagnosed
3. Note edge cases and test scenarios they considered
4. Implement your own fix using their insights
5. Close the PR with thanks and explanation

### Close Directly
- Addresses issue already fixed
- Out of scope for project
- Fundamentally wrong approach
- Author unresponsive >30 days

When closing:
- Thank the contributor for identifying the problem
- Explain you've implemented a fix based on their insights (if applicable)
- Link to your commit/PR that addresses it

### Defer Analysis
- Large change needs design discussion first
- Blocked by another decision
- Needs domain expertise to evaluate

## Priority Scoring

Weights are defined in `.github/maintainer/config.json`. Use label boosts to reflect priorities and project focus. Defaults are in `references/config.md`.

## Opportunity Decisions

Use these when no issue/PR explicitly asks for the work:

- **Docs/UX win:** Clear gap in README, examples, or API docs that reduces user friction
- **Hygiene win:** Tests, tooling, CI, or release processes that reduce future maintenance cost
- **Adoption win:** Small improvements that increase trust (badges, quickstarts, error messaging)

Capture these as briefs and include them in the prioritized queue.

## Actionability States

| State | Meaning | Agent Action |
|-------|---------|--------------|
| `ready` | Can act now | Work on it |
| `needs-info` | Waiting for reporter | Follow up or wait |
| `needs-decision` | Requires maintainer judgment | Present to human |
| `needs-analysis` | PR/issue needs intent extraction | Analyze and extract insights |
| `blocked` | External dependency | Track, can't act |
| `stale` | No activity, may be abandoned | Apply stale policy |
| `closable` | Ready to close | Close with reason |

Actionability labels organize the queue; they do not imply skipping analysis.

## Implementation Readiness Signals (PRs)

Use these signals together when deciding if a PR is a strong implementation candidate:
- Linked high-priority issues
- Relationship quality between issue intent and PR approach
- Clear intent and scope in description and comments
- Positive community reactions and sentiment
- CI status and unresolved threads
- Evidence of tests or quality checks (files touched, comments, review notes)

Implementation score is auto-generated and then adjusted by the agent. Record the adjustment in `.github/maintainer/notes/` with `agent_score`, `agent_confidence`, and `agent_rationale`, and update `relationship_quality_final` as needed.

## Stale Policy

Default thresholds (customize in `.github/maintainer/standing-rules.md` and `config.json`):

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Issue waiting on reporter | 30 days | Comment asking for update |
| Issue waiting on reporter | 60 days | Close with "stale" note |
| PR waiting on author | 30 days | Close with "stale" note |
| Draft PR with no activity | 30 days | Comment asking about status |

Always allow reopening if the contributor returns.
