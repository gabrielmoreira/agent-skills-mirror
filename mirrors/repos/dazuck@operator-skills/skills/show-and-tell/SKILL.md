---
name: show-and-tell
description: Prepare a demo artifact for daily team show & tell. Aggregates work from the last 24 hours into a presentable format with evidence (command output, screenshots). Use when asked to "prep for show and tell", "what did I do today", or "prepare my demo".
---

# Show & Tell

Aggregate a day's work into a presentation-ready artifact for team show & tell.
Not a status report — a demonstration. Show what was built, prove it works, share
what was learned.

## When to Use

- Before daily show & tell meeting
- User says "prep for show and tell", "prepare my demo", "what did I ship today"
- End of day when user wants to capture the day's outcomes

## When NOT to Use

- Mid-session check-ins (use handoff instead)
- Written documents for async consumption (use create-briefing instead)
- Commit-level summaries (use recall-commit instead)

## Philosophy

**Show, don't tell.** A show & tell is not a standup. Nobody wants to hear "I
worked on the auth module." They want to see the login flow working, the test
suite passing, the before/after performance numbers.

The agent's job: help the human prepare a compelling 3-5 minute demo by
gathering evidence, curating highlights, and assembling a clean artifact the
human can walk through with the team.

**Curate ruthlessly.** A day might have 15 commits across 3 repos. The show &
tell should cover 2-4 highlights. More than that and it's a status report.

**Evidence > description.** For every highlight, include at least one piece of
evidence: command output, a screenshot, a test run, a before/after comparison.
If you can't demonstrate it, it's not a show & tell item — it's a bullet point.

## Invocation

`/show-and-tell` — Prepare demo for today's work (default: last 24 hours)
`/show-and-tell 2d` — Cover the last 2 days (after weekends, sick days)
`/show-and-tell [repo-path]` — Scope to a specific repo

## Procedure

### Phase 1: Gather

Collect from four sources: git, local session history, Atlas (Slack + team
context), and Notion. Run independent queries in parallel.

#### 1a. Git & GitHub

```bash
# Commits in the period (all branches)
git log --all --oneline --since="24 hours ago" --author="$(git config user.email)"

# Branches touched
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:relative) %(subject)' refs/heads/ | head -20

# PRs created/merged (if gh available)
gh pr list --author @me --state all --search "created:>=$(date -v-24H +%Y-%m-%d)" 2>/dev/null

# Current AGENT-LEARNINGS.md entries from the period
# (read the file and filter by date)
```

Also check:

- `AGENT-LEARNINGS.md` for today's entries (filter by Author if present)
- `.claude/project-diary.md` for decisions made
- Any open PRs with review status

#### 1b. Local Session History

Work that never became a commit still leaves traces in Claude Code's session
logs and auto-memory. Scan for non-commit work from the period:

```bash
# Find recent session transcript files (last 24h)
find ~/.claude/projects/ -name "*.jsonl" -mtime -1 2>/dev/null
```

For each recent transcript, use Grep to search for high-signal patterns:

- `"tool":"Write"` or `"tool":"Edit"` — files the agent worked on
- `"tool":"WebFetch"` or `"tool":"WebSearch"` — research performed
- `"tool":"Bash"` — commands run (builds, tests, deploys, investigations)

Also check the project's auto-memory directory (`~/.claude/projects/*/memory/`)
for any notes saved during the period.

**Don't read full transcripts** — they're huge. Grep for patterns, extract
summaries. The goal is to surface work the user might have forgotten: a research
session that didn't produce code, a debugging investigation, a design discussion.

Present anything found that isn't already in git:

> "I also found these sessions not reflected in commits:
>
> - [Time] Research on [topic] (web searches, file reads)
> - [Time] Debugging [issue] (no fix committed yet)
>
> Include any of these in the demo?"

#### 1c. Atlas — Team Context & Slack Activity

If Atlas MCP is available, run these queries:

```
# Team context — what others shipped (for framing your own work)
get_daily_summary

# Your Slack activity — messages, links shared, discussions
search_all_summaries with query: "[user's name] [today's date]"

# Recent updates that might include your Slack messages, threads, shared artifacts
get_recent_updates
```

Slack often captures work that doesn't land in git: sharing a finding with the
team, answering a question, posting a link to a resource, discussing architecture
in a thread. These are legitimate show & tell material — especially when the
work was helping _others_ rather than shipping code.

#### 1d. Notion — Recently Created Pages

If Notion MCP is available, search for pages the user created or modified in the
period:

```
API-post-search with query: "[user's name]"
  — filter by last_edited_time in the past 24 hours
```

Look for: design docs, RFCs, meeting notes, project pages, research notes. If
the user created or substantially edited a Notion page, that's work worth
surfacing — it may be more demo-worthy than the code that preceded it.

### Phase 2: Curate

From the raw material, identify the **2-4 most demo-worthy items**. Rank by:

1. **Visible impact** — Can you show it? UI changes, new CLI commands, API
   responses, test output. Prioritize things the team can see.
2. **Significance** — Does this unblock others? Ship a feature? Fix a painful
   bug? Resolve a hard technical problem?
3. **Interest** — Would the team find this interesting, surprising, or useful
   for their own work? A clever debugging approach counts.

**Cut mercilessly.** Dependency upgrades, config tweaks, and routine refactors
are not show & tell material unless they solved a real problem worth sharing.

Present the curated highlights to the user for confirmation before proceeding:

> "I found these as today's highlights:
>
> 1. [Item] — [one-line why it's interesting]
> 2. [Item] — [one-line why it's interesting]
>
> Want me to adjust before I gather evidence?"

### Phase 3: Evidence

For each highlight, capture at least one piece of concrete evidence. Choose the
most appropriate type:

**Command output** — Run a command, capture the result:

- Test suite passing: `pnpm test` or equivalent
- CLI tool working: run it with sample input
- Build succeeding: `pnpm build` output
- API response: `curl` or equivalent

**Screenshot** — For visual/UI work, use chrome-devtools MCP:

- Navigate to the relevant page
- Take a screenshot
- If before/after matters, capture both (use git stash to show the before state,
  then pop to show after)

**Diff summary** — For architectural or refactoring work:

- Key file diffs that show the shape of the change
- Metric improvements (bundle size, test count, coverage delta)

**Test output** — For bug fixes and reliability work:

- Show the specific test that now passes
- Show coverage improvement

**Keep evidence gathering fast.** If a demo requires spinning up infrastructure
or complex setup, describe what would be shown and note it as a live demo
candidate. Don't burn 10 minutes on evidence for a 3-minute slot.

### Phase 4: Compose

Assemble the artifact. Write to file using the output format below.

Embed evidence inline — command output in code blocks, screenshots as image
references, diffs as collapsed details.

### Phase 5: Deliver

Save the artifact:

```
docs/show-and-tell/YYYY-MM-DD.md
```

Create the directory if it doesn't exist. If multiple repos were involved,
save to the primary repo (where the skill was invoked).

Offer next steps:

> "Demo artifact saved to `docs/show-and-tell/YYYY-MM-DD.md`.
> Want me to also publish this to Notion?"

If user confirms Notion publication and Notion MCP is available, create a page
under the team's show & tell database/page.

## Output Format

```markdown
# Show & Tell — YYYY-MM-DD

**[Your Name]** · [Repo(s)] · [N commits, N PRs]

---

## 1. [Highlight Title]

[2-3 sentences: What this is, why it matters, who it affects.]

**Evidence:**

\`\`\`
$ [command that demonstrates it]
[actual output]
\`\`\`

<!-- Or for screenshots: -->
<!-- ![Description](path/to/screenshot.png) -->

<!-- Or for diffs: -->
<!-- <details><summary>Key changes</summary> ... </details> -->

---

## 2. [Highlight Title]

[2-3 sentences: What this is, why it matters, who it affects.]

**Evidence:**

\`\`\`
$ [command]
[output]
\`\`\`

---

## Learnings

[1-2 key insights from AGENT-LEARNINGS.md that the team would benefit from.
Skip if nothing team-relevant was captured today.]

- **[Insight]**: [One sentence directive — "Do X, not Y" or "X works because Y"]

---

## Up Next

[1-2 sentences on what's planned for tomorrow. Helps team see the trajectory
and flag dependencies or coordination needs.]
```

### Format Principles

- **Headlines that stand alone.** A teammate scanning should get the gist from
  titles and opening sentences without reading evidence blocks.
- **Evidence is optional to read.** It's there to support claims during the live
  demo, not to be read line-by-line. Use collapsible sections for long output.
- **No filler sections.** If there are no team-relevant learnings, omit the
  section. If there's only one highlight, that's fine — one strong demo beats
  four weak ones.
- **Present tense.** "This adds..." not "I added..." — focus on the work, not
  the narrator.

## Rules

- Always confirm highlight selection with the user before gathering evidence.
- Never fabricate evidence. If a command fails, show the failure or skip the
  evidence.
- Never include sensitive data in evidence (API keys, credentials, PII). Redact
  before embedding.
- Keep the artifact under 200 lines. This is a presentation aid, not
  documentation.
- Don't capture evidence for items the user plans to demo live — just note
  "[Live demo]" in the evidence section.
- Screenshots go in `docs/show-and-tell/assets/` alongside the artifact.
- If `git log` shows no commits in the period, check session history, Slack,
  and Notion before concluding it was a quiet day. Research, design work, and
  helping teammates are legitimate highlights. But don't stretch nothing into
  something — a quiet day is fine to say plainly.

## Integration Points

**Inputs:**

- `recall-commit` → git log with conventional commit messages (structured, parseable)
- `AGENT-LEARNINGS.md` → team-relevant insights (with Author attribution)
- `handoff` → session summaries in project diary
- Claude Code session transcripts → non-commit work (research, debugging, design)
- Atlas MCP → team context, Slack activity, what others shipped
- Notion MCP → recently created/edited pages, docs, RFCs

**Outputs to:**

- `docs/show-and-tell/` → persistent archive of demos
- Notion (optional) → team-accessible page
- Team meeting → the human presents, the artifact supports them

## Anti-Patterns

- **The status report**: Listing every commit. Nobody cares about "chore: update
  lockfile" in a show & tell.
- **The essay**: Paragraphs of explanation without evidence. Show it working.
- **The humble-brag**: "Just a small thing but..." — state what it does and why
  it matters, plainly.
- **The apology**: "I didn't get much done but..." — if it was a research/planning
  day, say what you learned. If nothing happened, say that in one sentence.
- **The screenshot dump**: 8 screenshots with no narrative. Each piece of evidence
  needs context.
