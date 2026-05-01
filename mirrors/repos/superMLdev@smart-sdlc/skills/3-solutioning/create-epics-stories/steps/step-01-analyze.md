# Step 01 — Analyze PRD and Identify Epic Themes

**Previous step:** (none)
**Next step:** `step-02-epics.md`

---

## 1. Load and Review PRD

Load the PRD document. Note:
- PRD version number (embed in all stories for traceability)
- Number of functional requirements
- Priority distribution (Core / Important / Nice-to-Have)
- User personas

---

## 2. Identify Epic Themes

Read through all functional requirements and group them by user value theme. An epic should represent a coherent capability the user can USE, not an internal system task.

Grouping heuristics:
- All FRs serving the same user journey → one epic candidate
- All FRs around a single domain entity → one epic candidate
- All infrastructure FRs → one "Foundation" epic
- Authentication / authorization → usually its own epic
- Third-party integrations → typically separate epics

---

## 3. Identify Cross-Cutting Concerns

Flag requirements that affect multiple epics:
- Authentication (affects all user-facing epics)
- Error handling standards
- Logging and monitoring
- Performance budgets
- Security controls

These become story acceptance criteria inherited by all stories in affected epics.

---

## 4. Map Dependencies

Identify epic dependencies:
- Which epics cannot start until another epic (or part of it) is complete?
- Which epics have external dependencies (third-party API, another team)?
- Draw a simple dependency graph (list form is fine)

---

## 5. Present Theme Analysis

Present:
```
Epic Theme Candidates:
1. {Theme}: covers FR-001, FR-002, FR-005 — [personas served]
2. {Theme}: covers FR-003, FR-004 — [personas served]
...

Cross-cutting concerns: [list]
Dependencies: [list]

Total FR coverage: {X}/{total} requirements mapped to themes
Unmapped FRs: {list any that don't fit a theme}
```

⏸️ **STOP** — ask: "Does this grouping make sense? Any themes to split, merge, or rename?"

---

## 6. Save Progress

Update output file frontmatter:
```yaml
stepsCompleted: ["step-01-analyze"]
prdVersion: "{version}"
epicThemes: {count}
```

Load and follow `./step-02-epics.md`.
