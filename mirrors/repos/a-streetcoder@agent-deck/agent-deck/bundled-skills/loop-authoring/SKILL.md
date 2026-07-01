---
name: loop-authoring
description: Use when creating, refining, or validating Agent Deck loops, especially to guide users iteratively through loop goal, structure, agents, write target, and safety choices.
---

# Agent Deck Loop Authoring

Use this skill when the user wants to create, refine, review, save, or troubleshoot an Agent Deck loop.

Your job is to guide the user iteratively. Do not dump every option at once. Ask one focused question at a time, explain the practical tradeoff, and state your recommended default before asking when there is a sensible default.

## Core mental model

An Agent Deck loop is a reusable run recipe with:

- a goal or task prompt
- a structure kind
- one or more explicitly selected agents
- a write target
- stopping or validation criteria
- optional project availability metadata when saved to the Loop Bank

User-authored loops are typically saved as `*.loop.md` under `~/.pi/agent/loops` in the current user-level Loop Bank storage. Built-in loop templates are currently disabled, so do not tell users that bundled loop templates are available unless the product changes.

## Iterative authoring workflow

Move through these steps in order. Stop and ask only for the next missing decision.

1. Clarify the outcome
   - Ask what the loop should accomplish and what “done” means.
   - Help turn vague requests into an actionable goal prompt.
   - Recommended default: artifact/report output unless the user clearly wants code edits.

2. Choose the loop structure
   - Recommend the simplest structure that fits the work.
   - Ask the user to confirm the structure before choosing agents.

3. Select agents explicitly
   - Agent fields must stay blank until the user chooses an agent.
   - Never invent fallback agent names such as `Maker` or `Checker`.
   - If the available agent list is unknown, ask the user to choose from Agent Deck or inspect the global/imported catalog plus the project’s Agent Deck assignments if tools/context allow it. Do not offer project-local `.pi/agents` or legacy `.agents` files; import/catalog entries are by reference, not copy.

4. Choose the write target
   - Prefer `artifactMarkdown` for planning, research, review, and safe reports.
   - Use `newWorktree` for implementation that should avoid touching the current checkout.
   - Use `currentCheckout` only when the user explicitly confirms direct edits to the current project tree.

5. Define validation and stop conditions
   - Ask what evidence should decide success: tests passing, reviewer approval, checklist completion, no findings, or a human approval checkpoint.
   - Keep max iterations low unless the user asks for longer autonomous work.

6. Decide whether to save it
   - If the user wants reuse, save to the Loop Bank with a clear name and description.
   - Ask whether it should be available to all projects, only the current project, or kept unassigned/catalog-style.

7. Review before launch or save
   - Summarize the loop in a compact checklist.
   - Call out any risky write target, missing agent, vague goal, or missing validation.
   - If several decisions are still missing, summarize them briefly but ask for only the highest-priority missing decision in the current turn.
   - Ask for confirmation before launch when the loop can modify project files.

## Structure guide

Choose the most direct structure:

- Single Agent: one agent repeats work until validation passes or the iteration limit is reached. Best for focused reports or bounded implementation by one specialist.
- Maker + Checker: one maker produces work and a checker approves or rejects against a rubric. Best when quality gates matter.
- Agent Pipeline: ordered stages where each stage hands off to the next. Best for research → plan → implementation → review workflows.
- Parallel Agents: multiple branches run independently and then summarize. Best for independent investigations or comparing approaches.
- Discovery/Triage: one triage agent classifies or routes findings using a classification prompt. Best for bug intake, repo sweeps, or issue sorting.
- Human Approval: pauses for explicit user approval at a checkpoint. Best when a human must decide before continuing.

If multiple structures fit, recommend the simplest safe option and explain why in one sentence.

## Write target guidance

Use these names and safety expectations consistently:

- `artifactMarkdown`: safest; writes loop artifacts/reports, not project files.
- `newWorktree`: safer for code changes; uses an isolated git worktree.
- `currentCheckout`: riskiest; writes directly to the current checkout and requires explicit user confirmation.

Never quietly upgrade a loop to `currentCheckout`. If direct edits are required, ask a focused confirmation question.

## Loop Bank and bundled-resource rules

- User loop definitions are saved as `*.loop.md` under `~/.pi/agent/loops`.
- Built-in bundled loop templates are disabled for now.
- Bundled resources must not be edited in place by ordinary user customization flows.
- If a future built-in loop exists and the user wants to customize it, duplicate it first and edit the user copy.

## Good authoring questions

Ask one at a time:

- “What outcome should this loop produce, and how will we know it is done?”
- “I recommend a Maker + Checker loop because you want an explicit quality gate. Should we use that structure?”
- “Which agent should be the maker? I will leave it blank until you choose one.”
- “Should the loop write only an artifact report, use a new worktree, or directly edit the current checkout? I recommend artifact report unless you need code changes.”
- “What should the checker use as the approval rubric?”
- “Should this be saved for all projects, only this project, or left unassigned in the Loop Bank?”

## Validation checklist

Before considering a loop ready, verify:

- Goal is specific enough for an agent to act on.
- Structure matches the desired workflow and is not overcomplicated.
- Every required agent field is explicitly selected.
- Write target is explicit and safe for the task.
- `currentCheckout`, if used, has explicit user confirmation.
- Review rubric, classification prompt, checkpoint prompt, or validation criteria are present when the structure needs them.
- Iteration/review limits are bounded.
- Saved loop name and description are clear enough to recognize later.
