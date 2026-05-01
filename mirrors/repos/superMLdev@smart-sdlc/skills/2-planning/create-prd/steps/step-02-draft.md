# Step 02 — Draft PRD Sections

**Previous step:** `step-01-requirements.md`
**Next step:** `step-03-finalize.md`

---

## 1. Create PRD File

Create or open `{planning_artifacts}/prd/{project_name}-prd.md` with this header:

```markdown
---
project: {project_name}
version: 1
status: draft
created: {date}
owner: {user_name}
stepsCompleted: ["step-01-requirements"]
---

# {project_name} — Product Requirements Document

> **Status:** Draft | **Version:** 1 | **Owner:** {user_name}
```

---

## 2. Write Each Section

Write sections one at a time. After each section, present it to the user and ask: "Does this look right? Any changes?"

⏸️ **STOP after each section** — do not continue until the user approves or requests changes.

### Section: Overview

Write a 2–3 sentence summary: what this product/feature is, who it serves, and why it matters now.

### Section: Goals and Non-Goals

From step 01 context, format as:

```markdown
## Goals
- [Primary goal]
- [Secondary goal 1]
- [Secondary goal 2]

## Non-Goals
- [Explicit out-of-scope item 1]
- [Explicit out-of-scope item 2]
```

### Section: User Personas

For each persona identified:

```markdown
## User Personas

### {Persona Name}
- **Role:** ...
- **Primary Goal:** ...
- **Pain Point Today:** ...
- **Success Definition:** ...
```

### Section: Functional Requirements

For each feature in the prioritized list, write a requirement block:

```markdown
## Functional Requirements

### FR-001: {Feature Name}
**Priority:** Core / Important / Nice-to-Have
**User Story:** As a {persona}, I want to {action} so that {outcome}.
**Acceptance Criteria:**
- [ ] AC1: Given {context}, when {action}, then {result}
- [ ] AC2: ...
**Notes / Open Questions:**
- ...
```

Number requirements FR-001, FR-002, etc. Use the prioritization from step 01.

### Section: Non-Functional Requirements

Capture from step 01 constraints:

```markdown
## Non-Functional Requirements

### NFR-001: Performance
...

### NFR-002: Security
...

### NFR-003: Scalability
...
```

### Section: Technical Constraints

```markdown
## Technical Constraints
- [Constraint 1]
- [Constraint 2]
```

### Section: Dependencies

```markdown
## Dependencies
- [System or team dependency 1]
- [System or team dependency 2]
```

### Section: Open Questions

```markdown
## Open Questions
| # | Question | Owner | Due |
|---|----------|-------|-----|
| 1 | ... | ... | ... |
```

---

## 3. Update PRD Status

After all sections are drafted and approved:

Update frontmatter:
```yaml
stepsCompleted: ["step-01-requirements", "step-02-draft"]
status: "draft-complete"
```

Say: "Draft is complete. Let's do a final review."

Load and follow `./step-03-finalize.md`.
