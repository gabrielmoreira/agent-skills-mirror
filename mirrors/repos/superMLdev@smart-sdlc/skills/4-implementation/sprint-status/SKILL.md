---
name: sprint-status
description: "Report on current sprint progress — stories complete, in-progress, blocked, and remaining. Use when the user says 'sprint status', 'how is the sprint going', 'show blockers', or 'burn-down update'."
---

# Sprint Status Workflow

## Goal

Produce a concise, accurate sprint status report covering completed work, work in progress, blockers, and burn-down trajectory. Surface risks the team needs to act on now.

---

## Step 1: Load Sprint Context

Read `_superml/config.yml` for sprint information.

Ask if not present:
1. Sprint name / number?
2. Sprint start date and end date?
3. Total story points committed?

---

## Step 2: Story Status Sweep

For each story in the current sprint, classify:

| Status | Description |
|--------|-------------|
| ✅ Done | Implemented, reviewed, and meets ACs |
| 🔄 In Progress | Currently being worked on |
| ⚠️ Blocked | Cannot proceed — dependency or external blocker |
| ⏳ Not Started | Committed but not yet picked up |

Collect:
- Points done: `{X}` of `{total}` committed
- Days remaining in sprint: `{N}`
- Projected completion rate (points/day) vs. required rate

---

## Step 3: Blocker Analysis

For each blocked story:
- What is the blocker? (technical, dependency, access, decision needed)
- Who needs to act to unblock?
- How many story points are blocked?
- What is the risk to sprint goal?

---

## Step 4: Risk Assessment

Evaluate:
- Is the sprint on track? (current velocity vs. needed velocity)
- Is the sprint goal at risk?
- Should any stories be descoped? Which ones are lowest priority?
- Are any blockers escalation-worthy?

---

## Step 5: Output

Report format:

```
Sprint: {name}  |  Day {N} of {total}  |  {X}/{total} pts done

✅ Done ({X} pts)
  - S-001: [Story title]
  - S-003: [Story title]

🔄 In Progress ({Y} pts)
  - S-002: [Story title] — {owner}

⚠️ Blocked ({Z} pts)
  - S-004: [Story title] — BLOCKER: {description} — Needs: {owner}

⏳ Not Started ({W} pts)
  - S-005: [Story title]

📊 Burn-down: {X}/{total} pts done, {days} days left
   Needed: {required_rate} pts/day  |  Current: {actual_rate} pts/day
   Status: {ON TRACK / AT RISK / OFF TRACK}

🚨 Risks:
  1. {risk description} — Recommended action: {action}
```

Save to `{docsPath}/planning/sprint-status-{sprint}.md`.
