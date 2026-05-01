# Relearn Codebase — Workflow

**Goal:** Produce a complete, accurate, living documentation suite for an existing codebase — by reading the code, not by asking what it's "supposed to do."

**Outputs** (all written to `{project-root}/docs/` unless config specifies otherwise):
| Document | File | Purpose |
|----------|------|---------|
| README | `README.md` | Project overview, quick start |
| Architecture | `docs/ARCHITECTURE.md` | System design + Mermaid diagrams |
| Data Model | `docs/DATA_MODEL.md` | Entities, schemas, relationships |
| API Reference | `docs/API_REFERENCE.md` | All endpoints / operations |
| Developer Guide | `docs/DEVELOPER_GUIDE.md` | Setup, run, test, debug |
| Operations | `docs/OPERATIONS.md` | Deploy, monitor, scale |
| Decisions | `docs/DECISIONS.md` | Reverse-engineered ADRs |
| Onboarding | `docs/ONBOARDING.md` | New team member guide |

---

## Workflow Architecture

Sequential step-file execution. State tracked in `_superml/relearn-state.yml`.

**Critical Rules:**
- 🔍 Scout is read-only — NEVER modify source files
- ⏸️ Always halt at STOP markers for confirmation
- 📎 Every claim must cite a source file (never invent behavior)
- 🧩 Context window is finite — read strategically, not exhaustively
- 🔴 When docs contradict code, flag the contradiction — do not silently pick one

---

## Activation

1. Confirm the project root: "I'll scan `{project-root}`. Is this the correct directory?"
2. Ask: "Which documents do you need?"
   - **A** — Full suite (all 8 documents)
   - **B** — Quick set: README + Architecture + Developer Guide
   - **C** — AI context only: project-context.md + ARCHITECTURE.md
   - **D** — Custom: pick documents from the table above
3. Ask: "What is the documentation audience?" (internal devs / external API consumers / new team members / all)
4. Note any existing docs to update vs. create from scratch.

⏸️ **STOP** — confirm scope before scanning.

---

## Steps

- `steps/step-01-scan.md` — Map project structure and detect tech stack
- `steps/step-02-architecture.md` — Reverse-engineer component architecture
- `steps/step-03-data-api.md` — Extract data models and API surface
- `steps/step-04-patterns.md` — Identify conventions, debt, and ops config
- `steps/step-05-document.md` — Produce all selected documentation artifacts
