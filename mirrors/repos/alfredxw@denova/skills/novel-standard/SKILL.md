---
name: novel-standard
description: Standard writing workflow in which the main Agent drafts and revises while the built-in general-purpose SubAgent reviews, balancing quality and speed.
category: writing
capabilities:
  - writing-workflow
agent: ide
---

# novel-standard

Use this standard Writing Agent workflow to balance quality and speed.

## Determine the writing scope

- Infer the scope from the user's actual request, such as continuing a passage, writing a scene, one chapter, three chapters, a short story arc, or a custom target.
- Do not assume the task is the next chapter unless the user explicitly asks for it.
- There is no `writing_scope` field. The user message is the sole source for scope, goal, constraints, and output form.
- When the user requests N chapters or another multi-part deliverable, first make a concise overall and per-chapter plan to guide the draft.

## Workflow

main Agent drafts -> general-purpose SubAgent reviews -> main Agent revises and updates state -> final output

Use only the main Agent and the built-in `general-purpose` SubAgent. Do not assume other named SubAgents exist or start additional writing subprocesses. If the `task` tool is unavailable or `general-purpose` cannot be used, the main Agent performs the same review itself and must not fabricate delegation or review results.

## Tool requirements

- Before writing, use `read` for the necessary context: `CREATOR.md`, `setting/outline.md`, `setting/progress.md`, `setting/character-states.md`, the relevant chapter-group plan, and recent chapters. For lore, use `query_lore_items` with exact `ids`/`names` or search filters and `detail=full` to load complete bodies. Follow `next_offset` for additional pages; the default `index` only returns briefs.
- After drafting, use `write` to create the correctly named chapter file under `chapters/`. For a localized revision to an existing chapter, use `edit`; `old_string` must match the current file exactly and uniquely and must not contain line-number prefixes returned by `read`.
- When available, delegate review to `general-purpose` through `task`. Its description must state the user's goal, chapter path, necessary context sources, review focus, output format, and that the SubAgent reviews only and must not modify files.
- After review, use `write` for a complete chapter replacement or `edit` for a few localized changes. Apply the same localized-edit versus complete-rewrite rule to `setting/progress.md` and `setting/character-states.md`.
- Inspect every `write` or `edit` result. If it contains `[tool error]`, invalid JSON arguments, `string not found`, a non-unique match, a path error, or a truncation notice, do not claim completion. Reread the target, correct the arguments, and retry, or clearly report that the write did not succeed.
- Before the final response, use `read` to verify key excerpts from every new or revised chapter and from any updated state files.

1. Before drafting, load `novel-craft` with the `skill` tool unless it is already loaded in this turn. Follow its scenario routing and read only the references it names for the current task; for a chapter or scene, start with `scene-and-payoff.md`; for chapter-group or volume planning, use `premise-and-outline.md`. If the `skill` tool is unavailable, continue with the rules here. Then draft at the scope and under the constraints requested by the user, and write the draft to the correctly named chapter file under `chapters/`. Do not update progress or character state yet.
2. When available, use `task` to start a `general-purpose` SubAgent review and provide the new chapter path, user requirements, necessary context, and rules that require particular attention. Include the reader-contract, hook, payoff, continuity, and hard-fact checks relevant to this chapter in the review focus; the reviewer does not need to load `novel-craft` itself. Otherwise, perform the review in the main Agent.
3. The review returns structured issues only and does not edit prose. It must rigorously check continuity, lore grounding, pacing, prose style, character motivation, plot logic, and compliance with every creative rule. Do not include praise.
4. Revise the chapter directly from the review, fixing only genuine issues while preserving the original story, strong passages, effective plot beats, character voices, and continuity.
5. After the final revision, update `setting/progress.md` and `setting/character-states.md` in the same turn without waiting for separate chapter confirmation. Chapter status is only a UI editing marker. Suggest or perform lore updates only when an explicitly established, long-lived fact changes and the user request authorizes it. Classify fact changes before recording them: incidental unnamed details need no record; new named characters, locations, items, relationships, promises, new uses of established abilities, and new hard numbers belong in the existing chapter-group plan, progress, character state, or lore; changes to established rules, core abilities, protagonist identity, major-character death, timeline contradictions, or confirmed outline promises require author confirmation first. Do not create a separate fact registry.

## Review requirements

The `general-purpose` review or main-Agent self-review may read the necessary preceding prose, `CREATOR.md`, outline, progress, character state, and lore for comparison. Check the new chapter against the task, user prompt, `CREATOR.md`, long-term outline, character canon and current state, world rules, and established continuity. Evaluate plot progression, character motivation, setting consistency, pacing, language quality, and readability. Also check agency and payoff ownership: the key outcome should follow from the central character's choice, preparation, or irreplaceable contribution, and the character who set up the payoff should receive it; supporting characters may assist but must not silently take the core result. Return issues by severity with evidence locations, impact, and actionable fixes.

Treat these as blocking: an explicit promise from the previous chapter is completely ignored; the chapter changes none of goal, risk, information, relationship, resources, identity, or emotional stance; an established rule or timeline is contradicted; a POV character uses knowledge they do not have; future outline events leak into prose; the chapter contains placeholders, truncation, or clearly unfinished text. Report weak openings, summary endings, missing micro-payoff, repetitive payoff patterns, emotion labels, and identical reactions across characters as non-blocking unless they make the chapter unreadable. If no material issue exists, return no issues; do not invent problems to justify the review. If the execution mode does not allow writes, return only the review and revision plan.

## Final output

- Return the final prose or other writing artifact requested by the user.
- Do not expose the review report or internal revision notes unless requested.
- If a critical constraint cannot be satisfied, briefly report the blocker or ask for confirmation.
