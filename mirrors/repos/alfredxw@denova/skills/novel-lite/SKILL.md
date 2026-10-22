---
name: novel-lite
description: Fast continuation, exploratory drafts, and low-latency prose generation performed directly by the main Agent without review or revision subprocesses.
category: writing
capabilities:
  - writing-workflow
agent: ide
---

# novel-lite

Use this Skill for fast prose generation by the Writing Agent.

## Determine the writing scope

- Infer the scope from the user's actual request, such as continuing a passage, writing a scene, one chapter, three chapters, a story arc, or a custom target.
- Do not assume the task is the next chapter unless the user explicitly asks for it.
- There is no `writing_scope` field. The user message is the sole source for scope, goal, constraints, and output form.
- When the user requests multiple chapters, do only a lightweight internal breakdown: determine the overall direction and chapter boundaries, then write at the requested scale.

## Workflow

main Agent -> final output

## Tool requirements

- When continuity matters, first use `read` for the relevant workspace files, such as `CREATOR.md`, `setting/outline.md`, `setting/progress.md`, `setting/character-states.md`, the current chapter-group plan, and recent chapters. For lore, use `query_lore_items` with exact `ids`/`names` or search filters and `detail=full` to load complete bodies. Follow `next_offset` for additional pages; the default `index` only returns briefs.
- If the user asks only for a passage, exploratory draft, or example in chat, output the prose directly and do not write workspace files.
- When the user asks to create or update workspace prose, use `write` for a new file or complete rewrite and `edit` for localized replacement. `old_string` must match the current file exactly and uniquely and must not contain line-number prefixes returned by `read`.
- Inspect every `write` or `edit` result. If it contains `[tool error]`, invalid JSON arguments, `string not found`, a non-unique match, a path error, or a truncation notice, do not claim completion. Reread the target, correct the arguments, and retry, or clearly report that the write did not succeed.
- After user-visible file changes, use `read` to verify key excerpts from the final file. If verification is impossible, say so in the final response.
- After writing a complete chapter or materially changing its plot, finish the prose self-review and final revision, then update `setting/progress.md` and `setting/character-states.md` in the same turn. Chapter status in the UI does not affect synchronization. Pure typo, punctuation, or wording edits that do not change narrative facts need no state update.
- Treat `setting/progress.md` only as a summary. Determine the next chapter from actual chapter paths and non-empty prose, and correct progress in the same turn when they conflict.

## Rules

- The main Agent produces the final result directly.
- Do not start reviewer, fixer, task, General SubAgent, or configured subagent workflows.
- Before drafting, continuing, rewriting, or polishing narrative prose, load `novel-craft` with the `skill` tool unless it is already loaded in this turn. Follow its scenario routing and read only the references it names for the current task; for a chapter or scene, start with `scene-and-payoff.md`; for serial continuity, also read the `记忆与衔接` section of `long-form.md`. Do not load every reference. If the `skill` tool is unavailable, continue with the rules here. Skip this for non-narrative edits such as typos, punctuation, formatting, or metadata. Loading `novel-craft` is a Skill read, not a review subprocess.
- A lightweight internal check for continuity, user requirements, and obvious prose issues is allowed, but do not expose the review process.
- For prose, silently remove obvious AI patterns: summary or realization endings, emotion labels, identical reactions across characters, and paragraphs of uniform length and information density. Preserve intentional style and do not add new events just to sound human.
- Classify fact changes before committing them to continuity. Incidental unnamed details need no record. New named characters, locations, items, relationships, promises, new uses of established abilities, and new hard numbers should be written and then recorded in the existing chapter-group plan, progress, character state, or lore as appropriate. Changes to established rules, core abilities, protagonist identity, major-character death, timeline contradictions, or confirmed outline promises require author confirmation first. Do not create a separate fact registry.
- Preserve user control. Do not over-plan, over-explain, or turn the requested draft into a different story.
- Use workspace context, selected text, lore references, and style rules only when relevant to this turn's writing scope.

## Output

- Return the creative result the user requested directly.
- Add a brief explanation only when the user asks for one or an important constraint cannot be satisfied.
