# Step 02 — Define Epics

**Previous step:** `step-01-analyze.md`
**Next step:** `step-03-stories.md`

---

## 1. Create the Backlog File

Create `{planning_artifacts}/epics-stories/{project_name}-backlog.md`:

```markdown
---
project: {project_name}
prd_version: {prdVersion}
created: {date}
owner: {user_name}
stepsCompleted: ["step-01-analyze"]
status: draft
---

# {project_name} — Backlog
```

---

## 2. Write Each Epic

For each theme from step 01, write an epic. Present each one for approval before writing the next.

Epic template:

```markdown
## Epic E-{001}: {Epic Name}

**Goal:** One sentence — what user capability does this epic deliver?
**Personas:** [Which users benefit]
**PRD Coverage:** FR-{xxx}, FR-{yyy}
**Priority:** Core / Important / Nice-to-Have
**Dependencies:** [E-{xxx} must be complete first | None]
**Definition of Done:**
- [ ] All stories in this epic are implemented and accepted
- [ ] Integration tests pass
- [ ] Documentation updated
**Estimated Stories:** {rough count}
```

⏸️ **STOP after each epic** — confirm before writing the next.

---

## 3. Build Epic Dependency Graph

After all epics are defined, produce a visual dependency order:

```markdown
## Epic Dependency Order

\`\`\`
E-001 (Foundation) → E-002 (Auth) → E-003 (Core Feature)
                                  → E-004 (Admin Panel)
\`\`\`

**Recommended Sprint Order:**
- Sprint 1: E-001 (Foundation), E-002 (Auth)
- Sprint 2: E-003 (Core Feature) [stories 1–4]
- ...
```

⏸️ **STOP** — ask: "Does this ordering match your sprint goals?"

---

## 4. Save Progress

Update backlog file frontmatter:
```yaml
stepsCompleted: ["step-01-analyze", "step-02-epics"]
epicCount: {n}
```

Load and follow `./step-03-stories.md`.
