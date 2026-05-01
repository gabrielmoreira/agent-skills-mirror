---
name: retrospective
description: "Facilitate a sprint retrospective — what went well, what to improve, and concrete action items. Use when the user says 'run a retrospective', 'retro', or 'reflect on the sprint'."
---

# Retrospective Workflow

## Goal

Run a structured, blame-free retrospective that produces clear, owned action items the team will actually execute. Not a venting session — a problem-solving session.

---

## Step 1: Set the Stage

Establish ground rules:
- This is a blame-free session — we discuss systems and processes, not people
- Everything said here stays in the retro doc unless explicitly agreed otherwise
- We focus on actionable improvements, not just complaints

Ask:
1. Sprint name / number?
2. Who is participating? (list personas or team members)
3. Any topics to explicitly put on the table?

---

## Step 2: What Went Well?

Go around — each participant shares at least one positive:
- Something that worked better than expected
- A process or decision that paid off
- A collaboration or communication win

Capture all positives. Group related ones into themes.

---

## Step 3: What to Improve?

Go around — each participant shares their main friction point:
- Something that slowed the team down
- A process that caused confusion or rework
- A missing artifact, decision, or communication

Capture all points. Group into themes. Vote (or let the Team Lead choose) the top 2 to dig into.

---

## Step 4: Root Cause — Five Whys

For each top-2 improvement area, run a five-whys:

```
Problem: [description]
Why 1: [answer]
Why 2: [answer]
Why 3: [answer]
Why 4: [answer]
Root cause: [answer]
```

Stop when you reach a root cause the team can actually address.

---

## Step 5: Action Items

For each root cause, define ONE action item:

| Action | Owner | Due Date | Success Criterion |
|--------|-------|----------|-------------------|
| ...    | ...   | ...      | ...               |

Rules:
- One owner per action (not "the team")
- Due date is no later than end of next sprint
- Success criterion is observable — you can verify it happened

---

## Step 6: Appreciation Round

Each participant thanks one other participant for something specific this sprint.

---

## Step 7: Output

Save to `{docsPath}/planning/retro-{sprint}.md` with:
- Sprint metadata
- Went well (grouped themes)
- To improve (grouped themes)
- Root cause analysis for top 2
- Action items table
- Appreciation notes
