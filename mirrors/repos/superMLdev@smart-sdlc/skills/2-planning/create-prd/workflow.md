# Create PRD — Workflow

**Goal:** Produce a complete, implementation-ready Product Requirements Document with user stories, acceptance criteria, and prioritization.

**Output:** `{planning_artifacts}/prd/{project_name}-prd.md`

---

## Workflow Architecture

Sequential step-file execution. One step at a time. Never load future steps until the current step is complete.

**Critical Rules:**
- 🛑 Never load multiple step files simultaneously
- ⏸️ Always halt at STOP markers and wait for user input
- 💾 Update `stepsCompleted` in output frontmatter before moving to next step
- 📋 Never create a mental to-do list from future steps

---

## Activation

1. Read `{project-root}/_superml/config.yml`
2. Check if a product brief exists at `{planning_artifacts}/briefs/`. If yes, load it as context.
3. Check if a `project-context.md` exists — load if present.
4. Say: "Let's write your PRD. I'll guide you through each section. Answer what you know; I'll flag gaps as open questions."
5. Begin: Read and follow `./steps/step-01-requirements.md`

---

## Steps

- `steps/step-01-requirements.md` — Gather context, goals, and high-level requirements
- `steps/step-02-draft.md` — Write PRD sections with the user
- `steps/step-03-finalize.md` — Review, validate, and finalize
