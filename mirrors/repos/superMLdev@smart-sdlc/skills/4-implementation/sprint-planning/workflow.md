# Sprint Planning Workflow

**Goal:** Select stories from the backlog for the sprint, assign ownership, and confirm the sprint goal.

---

## Activation

1. Read `{project-root}/_superml/config.yml`. Check `artifacts.epics_complete`.

   **If `artifacts.epics_complete: false`** (or key absent):
   > ⚠️ **Epics and stories not defined yet.** Sprint planning requires a populated backlog.
   >
   > Run Rex (Architect) to break down the work first:
   > - GitHub Copilot: `#file:skills/3-solutioning/create-epics-stories/SKILL.md`
   > - Other AI: `"Load the skill at skills/3-solutioning/create-epics-stories/SKILL.md"`
   >
   > Ask the user: *"The epics and stories backlog doesn't appear to be complete yet. Do you want to build the backlog first, or do you have stories in another system (e.g., JIRA) we should import?"*

2. Load backlog from `{planning_artifacts}/epics-stories/{project_name}-backlog.md`
3. Ask: "Which sprint number are we planning? What is the sprint duration (1 week / 2 weeks)?"
4. Ask: "What is the team capacity in story points this sprint?"

---

## Phase 1: Velocity Review

If previous sprints have data, show:
```
Sprint {n-1} velocity: {points completed} / {points planned}
Recommended capacity for Sprint {n}: {suggested based on history}
```

If first sprint, use team's estimate directly.

---

## Phase 2: Identify Sprint Candidates

From the backlog, show all unstarted stories ordered by:
1. Epic dependency order (stories that unblock others first)
2. Priority (Core > Important > Nice-to-Have)
3. Story points (smaller stories first within same priority)

```
Available Stories for Sprint {n}:
──────────────────────────────────────────
[Epic E-001]
  S-001 | {title} | 3 pts | Core
  S-002 | {title} | 2 pts | Core
[Epic E-002]
  S-003 | {title} | 5 pts | Important
  ...
──────────────────────────────────────────
Total available: {n} stories / {sum} points
Team capacity: {capacity} points
```

---

## Phase 3: Select Stories

Guide the user to select stories that fit within capacity. Enforce:
- Don't add a story that would exceed capacity by more than 2 points
- Stories with blocking dependencies cannot be selected unless their blockers are also in this sprint
- Don't start an epic mid-dependency-chain unless the blocking epic is complete

⏸️ **STOP** — wait for story selections.

---

## Phase 4: Sprint Goal

With stories selected, derive a sprint goal:
> "Based on the selected stories, the sprint goal is: **{concise outcome statement}**."

Ask: "Does this sprint goal capture what you want to achieve? Adjust?"

⏸️ **STOP** — confirm sprint goal.

---

## Phase 5: Assign Stories

For each selected story, ask: "Who is owning this?"

Update each story's frontmatter with:
```yaml
sprint: {n}
assignee: {name}
status: "ready"
```

---

## Phase 6: Generate Sprint Summary

Write sprint plan to `{implementation_artifacts}/sprints/sprint-{n}.md`:

```markdown
---
sprint: {n}
goal: "{sprint goal}"
start_date: {date}
end_date: {date}
capacity: {points}
committed: {sum}
team: {list}
---

# Sprint {n} Plan

**Goal:** {sprint goal}

## Stories

| ID | Title | Epic | Points | Owner | Status |
|----|-------|------|--------|-------|--------|
| S-001 | {title} | E-001 | 3 | {name} | Ready |
...

**Total committed:** {sum} / {capacity} points
```

---

## Phase 7: JIRA Sync Offer

> "Sprint plan saved. Would you like to sync this sprint to JIRA? This will:
> - Move selected stories to 'In Sprint'
> - Assign them in JIRA to the named owners
> - Create a Sprint board if not yet created"

| Option | Action |
|--------|--------|
| Yes | Invoke `jira-sync` for sprint {n} |
| No | Done |

⏸️ **STOP** — wait for choice.
