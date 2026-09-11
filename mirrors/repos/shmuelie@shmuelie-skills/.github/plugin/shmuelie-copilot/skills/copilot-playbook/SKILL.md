---
name: copilot-playbook
description: "Generate a Copilot CLI Playbook — a teaching guide for how you drive the agent (plan→implement, commit granularity, delegated-work supervision, ask-before-act, terse corrections, PR lifecycle, verification), with copyable real prompts pulled from session history. Use when asked to create a playbook, write a prompting playbook, produce a 'how I use Copilot' teaching guide, or document your agent-driving style."
---

When asked to generate a Copilot CLI **playbook** (a teaching guide for how the user drives the agent), apply this domain knowledge.

# Copilot CLI Playbook — Domain Knowledge

## Purpose

Produce a **qualitative teaching guide** — "how I drive the agent" — that someone else could read and adopt. It is the narrative sibling of the `copilot-usage-report` skill:

| | `copilot-usage-report` | `copilot-playbook` (this skill) |
|---|---|---|
| Output | Metrics: session shape, timing, prompt-length distributions, model/file fingerprint | Lessons: working-style principles with copyable prompts |
| Audience | You, tracking your own patterns over time | Someone learning to work the way you do |
| Shape | Tables + ASCII charts + "Key Behavioral Patterns" | `principle → why it works → real prompts → teaching point` + a checklist |

A playbook teaches a **style**, not a feature list. Every lesson must include real, copyable prompts drawn from actual session history — not invented examples.

## Data Sources (use both)

### 1. The latest usage report (quantitative backing)

Read the newest `Reports/<date>-copilot-usage-report.md` first. Use it for:
- The **volume line** in the intro ("distilled from ~N sessions / M+ prompts").
- **Which patterns are prominent** — the report's verb-pattern table and "Key Behavioral Patterns" tell you which lessons matter most for *this* user (e.g. if `create a plan…` and `implement…` are the top two verbs, the plan→implement lesson leads).

```powershell
Get-ChildItem Reports\*-copilot-usage-report.md | Sort-Object Name | Select-Object -Last 1
```

If no usage report exists, generate one first (see the `copilot-usage-report` skill) or derive the volume numbers from a session-count query.

### 2. Session history (the copyable prompts)

Mine `session_store_sql` for **verbatim real prompts** per behavioral pattern. These become the "Real prompts" bullets in each lesson.

**IMPORTANT — query one pattern at a time.** A single query that `UNION`s many `ILIKE` patterns over a wide window **times out**. Run each pattern as its own small, time-filtered, `LIMIT`ed query, and `ORDER BY RANDOM()` for a representative sample:

```sql
-- Plan-first
SELECT substr(user_message,1,90) msg FROM turns
WHERE timestamp > now() - INTERVAL '30 days'
  AND user_message ILIKE 'create a plan%'
  AND length(user_message) BETWEEN 12 AND 90
ORDER BY RANDOM() LIMIT 6
```

Pattern filters (one query each):
- **Plan → implement:** `ILIKE 'create a plan%'`; separately `ILIKE 'implement%' AND length < 40`.
- **Commit granularity:** `ILIKE '%commit%' AND (ILIKE '%per todo%' OR ILIKE '%per step%' OR ILIKE '%one commit%' OR ILIKE '%don''t commit%')`.
- **Delegated-work supervision:** one short query per phrase — `ILIKE '%sub agent%'`, `ILIKE '%status update%'`, `ILIKE '%blocker%'`, `ILIKE '%next step%'`, `ILIKE '%stuck%'`, `ILIKE '%going off course%'`, `ILIKE '%while that runs%'`.
- **Investigate before directing (questions):** one query per opener — `ILIKE 'does%'`, `'is %'`, `'what%'`, `'why%'`, `'how%'`.
- **Terse corrections / redirects:** `ILIKE 'no %'`, `ILIKE 'don''t%'`, `ILIKE 'instead%'`, `ILIKE '%should be%'`, `ILIKE '%not %use%'`.
- **PR lifecycle:** `ILIKE '%draft PR%'`, `ILIKE '%PR description%'`, `ILIKE '%resolve%comment%'`, `ILIKE '%rebase conflict%'`.
- **Skills / memory:** `ILIKE '%skill%'`, `ILIKE '/skill%'`, `ILIKE '%remember%'`.
- **Verification:** `ILIKE '%check that%'`, `ILIKE '%docs are up to date%'`, `ILIKE '%what is remaining%'`, `ILIKE '%dry-run%'`, `ILIKE '%what are the local changes%'`.

Prefer short prompts (`length BETWEEN 12 AND 90`) so the examples are clean and copyable. Dedupe near-identical results; quote **verbatim** (don't paraphrase).

### 3. Equipped & used plugins / MCPs (the toolset)

A playbook should show *what the agent is equipped with* and *which of it actually gets reached for* — the toolset is part of the working style.

**Installed (the equipped set):**
```powershell
copilot plugin list
copilot plugin marketplace list
$mcpPath = Join-Path $HOME '.copilot\mcp-config.json'
if (Test-Path $mcpPath) {
    (Get-Content $mcpPath -Raw | ConvertFrom-Json).mcpServers.PSObject.Properties.Name
}
```
List installed plugins and registered marketplaces by name, not just as a count.
Separate always-installed plugins from repository-local plugins loaded for a
specific task.

**Used (what actually gets invoked)** — from `session_store_sql`'s `tool_requests`:
```sql
-- Top tools; MCP tools are prefixed (github-mcp-server-, Playwright-, NuGet-, ...)
SELECT name, COUNT(*) c FROM tool_requests
WHERE session_id IN (SELECT id FROM sessions WHERE updated_at > now() - INTERVAL '30 days')
GROUP BY name ORDER BY c DESC LIMIT 40
```
**Bucket the top-N by MCP prefix in-memory** — a wide `CASE`-by-prefix aggregate can time out; pull the top list and sum prefixes such as `github-mcp-server-*`, `Playwright-*`, and `NuGet-*` yourself. The `skill` tool count is your skill-invocation total. Report the handful that dominate, not an exhaustive list.

### 4. Delegation / background work (notification-aware supervision)

When the history supports it, include a lesson about **how the user supervises
delegated work** — especially longer-running background agents. This lesson
should teach delegation as a contract, not as "fire and forget."

- Bound the work up front: state the objective, allowed scope, non-goals,
  completion criteria, and expected evidence.
- Distinguish **brief synchronous tasks** from **longer background work**.
  Inline tasks that finish in one turn usually do not need a supervision ritual;
  background work does.
- For background work, ask for milestone updates that name **completed work**,
  **concrete blockers**, and the **next step**.
- Treat supported runtime signals as the source of truth: completion
  notifications, unread agent output, or an explicitly supported delayed check-in
  when the task genuinely needs one. Do **not** recommend tight polling,
  repeated agent discovery, or duplicate investigation just to "make sure."
- Honor the runtime's read contract. If it requires a completion notification
  before consuming final output, wait for that notification; a scheduled
  check-in does not override the requirement.
- Running status or elapsed time alone does **not** prove healthy progress, and
  silence alone does **not** prove a stall.
- A queued follow-up is **not** an immediate progress report. If live progress
  is unavailable, say that plainly instead of inventing dashboards, heartbeats,
  or other unsupported signals.
- If updates show drift or repeated blockers, redirect the **same** agent with a
  narrower objective or a sharper evidence request. Escalate consequential
  decisions back to the user instead of letting the agent freelance.
- Stop the monitoring loop once the work completes, fails, or becomes obsolete,
  then compare the final handoff against the original completion criteria.

Keep this lesson concise and operational. It should help another agent supervise
real background work safely, without turning into a generic policy dump.

## Report Structure

Mirror `Reports/2026-06-10-copilot-playbook.md`:

1. **Title + intro** — `# A Copilot CLI Playbook — How I Drive the Agent`, then an italic line citing the volume and pointing at the usage reports for the underlying data. One sentence framing it as an adoptable *style*, not a feature list.
2. **Lessons** — one `##` section per pattern, `---`-separated, each with:
   - **Principle** — a one-line imperative (the habit).
   - **Why it works** — 2-3 sentences on the payoff.
   - **Real prompts:** — 3-5 **copyable** bullets in backticks, pulled verbatim from history.
   - **> Teaching point:** — a blockquote with the transferable takeaway.
3. **Quick-Start Checklist** — a numbered list distilling every lesson into one actionable line each, for someone adopting the style cold.
4. **Closing pointer** — italic line: *"Want the numbers behind these patterns? See `Reports/<date>-copilot-usage-report.md`."*

Order the lessons by prominence for *this* user (from the usage report), but the durable core set is: Plan→Review→Implement, commit granularity, **supervise delegated work**, investigate-before-direct, terse corrections, short prompts, own-the-PR-lifecycle, skills+memory, **equip-the-agent (plugins/MCPs)**, verify-don't-trust.

The **Equip the Agent** lesson is where plugins and MCP data lands: teach keeping
a curated plugin set and enabling repository-specific tools only when needed.
List the actual plugins and cite used MCP categories such as code search or
browser automation as evidence of which tools earn their keep.

The **Supervise Delegated Work** lesson is where bounded, notification-aware
subagent habits land: how to set the contract, which progress signals are
trustworthy, and how to react safely to success, blockers, drift, or unavailable
live progress.

Use concrete scenarios inside this lesson, each with an observable report and
a safe supervisory response. For example, consider this **fictional assignment**:
add missing-field, empty-input, and malformed-value cases in `tests/parser/`;
change no production code or configuration; return the case names, changed
paths, and output from the existing test command. These illustrations are not
quotes from the user's history and must never be presented as mined prompts.

| Scenario | Observable report | Safe supervisory response |
|---|---|---|
| Successful | All three named cases are added; the handoff lists only `tests/parser/` files and includes successful test output. | Compare the diff, cases, and results to the original contract before accepting completion; stop obsolete monitoring. |
| Blocked | The missing-field case is written, but the declared test runner is unavailable; no test results exist. The delegate proposes restoring the project's declared dependencies. | Resolve the environment blocker within existing authorization or ask the user; retain the completed work and explicitly report tests as not run. Do not spawn a duplicate implementation or invent results. |
| Drifting | The delegate reports replacing the production parser and changing shared configuration instead of adding tests. | Redirect the same agent to the three test cases and original file boundary. Preserve unrelated user work and escalate any claim that a production change is necessary. |
| Unavailable live progress | The runtime exposes only an eventual completion notification. A follow-up asking for case names is queued, with no reply yet. | State that progress is unknown, continue independent work, and await the supported notification. Do not treat the queued message as a checkpoint or infer health or a stall from time alone. |

## Writing Guidance

- **Teach the style, not the tool.** No feature dumps — each lesson is a habit with a rationale.
- **Every lesson needs real prompts.** If a pattern has no good real examples in history, drop the lesson rather than invent prompts.
- **Keep it adoptable.** Write for a reader who wants to work this way, not for the original author. Parameterize volume/patterns from the data — don't hardcode another user's numbers.
- **Cross-reference, don't duplicate.** The playbook cites the usage report for numbers; it doesn't reproduce the tables.
- **Keep supervision guidance runtime-real.** Name only supported notifications,
  status reads, or delayed check-ins that the runtime actually exposes; do not
  invent universal polling intervals or product features.

## Output

Save to `Reports/<YYYY-MM-DD>-copilot-playbook.md` (date format `YYYY-MM-DD`).

## Refreshing an Existing Playbook

When a prior `*-copilot-playbook.md` exists:
- Keep the **durable lessons** (the core set rarely changes).
- **Refresh the prompts** with newer verbatim examples and update the volume line from the latest usage report.
- **Add lessons for newly-emerged patterns** (e.g. a new ritual that now recurs) and drop any that no longer show up in history.
- Note at the top that it supersedes the prior dated playbook.
