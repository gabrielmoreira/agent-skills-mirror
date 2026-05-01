# Step 03 — Break Epics into Stories

**Previous step:** `step-02-epics.md`
**Next step:** (none — final step)

---

## 1. Story Writing Approach

Process one epic at a time. For each epic, ask:
> "Ready to break down E-{001}: {Epic Name}? Or skip to a specific epic?"

For each story within an epic:
- Write the story
- Present it
- ⏸️ **STOP** — wait for approval or edits
- Move to next story

---

## 2. Story Template

```markdown
### Story S-{001}: {Story Title}

**Epic:** E-{xxx}
**PRD Ref:** FR-{xxx}
**PRD Version:** {prdVersion}   ← version traceability for Confluence conflict detection
**Priority:** Core / Important / Nice-to-Have
**Story Points:** {1 | 2 | 3 | 5 | 8 | 13} (Fibonacci)

**User Story:**
As a {persona}, I want to {action} so that {outcome}.

**Context:**
[Any background the developer needs to understand why this story exists]

**Acceptance Criteria:**
- [ ] AC-1: Given {precondition}, when {action}, then {result}
- [ ] AC-2: Given {precondition}, when {action}, then {result}
- [ ] AC-3 (Error): Given {invalid input / error condition}, when {action}, then {graceful handling}

**Technical Notes:**
[Architecture hints, API references, relevant ADRs, data model notes]

**Dependencies:**
- Requires: S-{xxx} (if blocked on another story)
- Blocks: S-{yyy} (if other stories depend on this)

**Definition of Done:**
- [ ] Code implemented and peer-reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Acceptance criteria verified
- [ ] PR merged to main branch
- [ ] JIRA ticket updated to Done
```

---

## 3. Story Points Guide

| Points | Meaning |
|--------|---------|
| 1 | Trivial change, < 2 hours |
| 2 | Small, well-understood, < half day |
| 3 | Medium, mostly clear, 1 day |
| 5 | Larger, some unknowns, 2–3 days |
| 8 | Complex, significant uncertainty, ~1 week |
| 13 | Too large — split this story |

Any story estimated at 13 must be split before proceeding. Prompt the user.

---

## 4. Coverage Check

After all epics are broken down, verify:
- Every FR from the PRD is covered by at least one story
- No story references an FR that doesn't exist in the PRD
- Dependencies are all resolvable (no circular deps)
- Total story points per epic are reasonable for planned sprints

Present coverage matrix:
```
Coverage Check:
  FR-001: S-001, S-002 ✅
  FR-002: S-003 ✅
  FR-003: (not covered) ❌
```

⏸️ **STOP** — resolve gaps before finalizing.

---

## 5. Finalize Backlog

Update backlog file frontmatter:
```yaml
stepsCompleted: ["step-01-analyze", "step-02-epics", "step-03-stories"]
status: "approved"
storyCount: {n}
totalPoints: {sum}
```

---

## 6. Offer Integration Actions

> "✅ Backlog complete: {epicCount} epics, {storyCount} stories, {totalPoints} total story points.
>
> Saved at `{planning_artifacts}/epics-stories/{project_name}-backlog.md`.
>
> What would you like to do next?"

| # | Action |
|---|--------|
| 1 | Create all epics and stories in JIRA (`jira-sync`) |
| 2 | Push backlog to Confluence (`confluence-push-doc`) |
| 3 | Start sprint planning (`sprint-planning`) |
| 4 | Talk to Nova to start implementing the first story |
| 5 | Done for now |

⏸️ **STOP** — wait for choice.
