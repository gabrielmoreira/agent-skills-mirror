# Document Project — Workflow

**Goal:** Analyze an existing codebase or project and produce structured documentation that both humans and AI assistants can use as persistent context.

**Output:** `{project-root}/{project_knowledge}/project-context.md` plus supporting docs.

---

## Workflow Architecture

This workflow uses sequential steps. Load and complete one step at a time. Never load a future step until the current one is complete.

**Step Processing Rules:**
1. Read the entire step before taking any action
2. Execute all numbered items in order
3. Halt at any `⏸️ STOP` marker and wait for user input or confirmation
4. Save progress notes in the output file's frontmatter as `stepsCompleted`
5. Load the next step only when directed

---

## Activation

1. Read `{project-root}/_superml/config.yml` and extract: `user_name`, `project_knowledge`, `project_name`, `communication_language`
2. Confirm the target project path with the user if not already clear
3. Begin: Read and follow `./steps/step-01-discover.md`

---

## Steps

- `steps/step-01-discover.md` — Discover project structure and technology
- `steps/step-02-analyze.md` — Deep analysis: architecture, patterns, dependencies
- `steps/step-03-document.md` — Produce documentation artifacts
