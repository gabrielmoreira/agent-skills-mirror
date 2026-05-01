---
name: generate-context
description: "Generate a project-context.md file optimized for AI context loading. Use when the user says 'generate context file', 'create AI context', or 'update the project context'."
---

# Generate Project Context

## Goal

Produce a concise, information-dense `project-context.md` file that gives any AI assistant instant, accurate orientation to the project — without reading every file.

## Activation

1. Read `{project-root}/_superml/config.yml`
2. Scan available artifacts:
   - `project-context.md` (existing, if any — note its age)
   - PRD in `{planning_artifacts}/prd/`
   - Architecture doc in `{planning_artifacts}/architecture/`
   - Backlog in `{planning_artifacts}/epics-stories/`
   - Source code structure (if brownfield)

## Content to Include

The generated file must answer:
1. **What is this project?** (1 sentence)
2. **What is the current phase?** (Analysis / Planning / Solutioning / Implementation)
3. **What has been decided?** (Tech stack, architecture pattern, key ADRs)
4. **What is being built right now?** (Active sprint, in-progress stories)
5. **Where is everything?** (Key file paths an AI needs to know)
6. **What must an AI assistant NEVER do?** (Org constraints, off-limits decisions)

## Output Structure

Write to `{project-root}/_superml/project-context.md`:

```markdown
---
generated: {date}
project: {project_name}
phase: {current phase}
prd_version: {version}
architecture_version: {version}
---

# {project_name} — Project Context

## What This Is
[1–2 sentences]

## Current Phase & Status
[Phase name + what's happening now]

## Technology Stack
[Compact table]

## Architecture Summary
[2–3 sentences + link to full architecture doc]

## Key File Paths
| Artifact | Path |
|----------|------|
| PRD | {path} |
| Architecture | {path} |
| Backlog | {path} |
| Stories (active) | {path} |

## Active Work
[Current sprint goal + in-progress story IDs]

## Key Decisions (ADRs)
[Compact list of the most important architectural decisions]

## Constraints & Must-Know Rules
[Org rules, security requirements, off-limits tech choices]
```

## Completion

> "✅ Project context saved at `_superml/project-context.md`. This file is auto-loaded by all agents at session start."
