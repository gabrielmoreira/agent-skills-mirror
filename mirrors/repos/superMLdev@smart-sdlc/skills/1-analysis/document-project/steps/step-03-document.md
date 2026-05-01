# Step 03 — Produce Documentation

**Previous step:** `step-02-analyze.md`
**Next step:** (none — this is the final step)

---

## 1. Create `project-context.md`

Write `{project-root}/{project_knowledge}/project-context.md` with this structure:

```markdown
---
generated: {date}
project: {project_name}
stepsCompleted: ["step-01-discover", "step-02-analyze", "step-03-document"]
---

# {project_name} — Project Context

## Purpose
[1–2 sentences: what this project does and who it serves]

## Technology Stack
| Category | Technology |
|----------|------------|
| Language | ... |
| Framework | ... |
| Database | ... |
| ...      | ... |

## Architecture
[Architectural pattern, key layers, how they interact — 1 paragraph]

## Directory Structure
[Annotated tree of key directories]

## Core Domain Models
[List of primary entities with 1-line descriptions]

## API / Interface Surface
[Top entry points, endpoints, or public interface summary]

## Key Integration Points
[External systems, services, APIs consumed]

## Development Workflow
[How to build, test, run locally — commands]

## Known Technical Debt
[Notable TODOs, FIXMEs, or areas needing attention]

## What a New Developer Must Know
1. ...
2. ...
3. ...
```

---

## 2. Create Supporting Architecture Diagram

If the project is non-trivial, generate a Mermaid component diagram:

```markdown
## Architecture Diagram

\`\`\`mermaid
graph TD
  [components and connections]
\`\`\`
```

Append this to `project-context.md`.

---

## 3. Create Data Model Diagram

If domain entities are well-defined, generate a Mermaid ER diagram:

```markdown
## Data Model

\`\`\`mermaid
erDiagram
  [entities and relationships]
\`\`\`
```

Append this to `project-context.md`.

---

## 4. Offer to Push to Confluence

If Confluence is configured (`confluence.enabled: true` in config), ask:
> "Would you like me to push this documentation to Confluence? I can create a page in your `{confluence.space_key}` space."

If yes, invoke: `confluence-push-doc`

---

## 5. Confirm Completion

> "✅ Project documentation is ready at `{project_knowledge}/project-context.md`. This file will be auto-loaded by agents as persistent context going forward.
>
> **Suggested next step:** Talk to Leo (Product Manager) to start defining requirements, or Rex (Architect) if you already have requirements and need architecture design."
