# Create Epics and Stories — Workflow

**Goal:** Transform PRD requirements and architecture decisions into a complete, JIRA-ready backlog of epics and user stories with detailed acceptance criteria, story points estimates, and dependency mapping.

**Output:** `{planning_artifacts}/epics-stories/{project_name}-backlog.md`

---

## Workflow Architecture

Sequential step-file execution. One step at a time. State tracked in output file frontmatter.

**Critical Rules:**
- 🛑 Never load multiple step files simultaneously
- ⏸️ Always halt at STOP markers
- 💾 Update `stepsCompleted` before moving to next step
- 🔢 Assign sequential IDs (E-001, S-001) — never reuse

---

## Activation

1. Read `{project-root}/_superml/config.yml`
2. Load PRD and architecture doc (ask which if multiple)
3. Note PRD version — embed in stories for Confluence version traceability
4. Say: "I'll break your PRD into epics and stories. We'll work through it together section by section."
5. Begin: read and follow `./steps/step-01-analyze.md`

---

## Steps

- `steps/step-01-analyze.md` — Analyze PRD and identify epic themes
- `steps/step-02-epics.md` — Define epics with goals and boundaries
- `steps/step-03-stories.md` — Break epics into detailed stories
