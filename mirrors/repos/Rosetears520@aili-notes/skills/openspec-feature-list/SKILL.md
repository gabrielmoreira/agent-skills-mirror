---
name: openspec-feature-list
description: Generate openspec/changes/<id>/feature_list.json by parsing openspec/changes/<id>/tasks.md (one feature per unique [#R<n>] checkbox task).
metadata:
  short-description: Generate feature_list.json from OpenSpec tasks.md
---

# OpenSpec Feature List (Instruction-Only)

Follow these instructions when this skill is invoked to generate or update `openspec/changes/<change-id>/feature_list.json` by parsing `openspec/changes/<change-id>/tasks.md`.

Do not add scripts or code files. Do not modify `openspec/changes/<change-id>/tasks.md`. Do not run any git commands.

## Invocation

- Preferred: `$openspec-feature-list <change-id>`
- If `<change-id>` is missing, ask the user for it once, then proceed.

## Behavior (step-by-step)

1) Inputs and paths
- `change-id` = user-provided argument.
- `tasks.md` = `openspec/changes/<change-id>/tasks.md`
- Output JSON = `openspec/changes/<change-id>/feature_list.json`

2) Read `tasks.md`
- If `tasks.md` does not exist, stop and report an error. Do not create output.

3) Parse `tasks.md` into task blocks (checkbox-only)
- Consider ONLY GitHub-flavored checkbox task lines:
  - `- [ ] ...`
  - `- [x] ...` (case-insensitive `x` is allowed)
- A task block is: the checkbox line plus all following lines until the next checkbox line or EOF.

4) Hard validation (fail fast; do not write/overwrite output on failure)
- Every checkbox task line MUST contain EXACTLY ONE ref token of the form `[#R<n>]` (example: `[#R12]`).
  - If missing or more than one, error and point to the task line.
- Each `[#R<n>]` MUST be unique across the entire `tasks.md`.
  - If duplicates exist, error and list the duplicate refs.
- In each task block, BOTH fields must exist (case-insensitive; allow optional leading `-` bullet and indentation):
  - `ACCEPT: ...`
  - `TEST: ...`
  - If either is missing, error and include the ref key and the checkbox line number.

5) Derive per-feature fields (one feature per ref)
- `ref` key: `"R<n>"` from `[#R<n>]` (example: `[#R12]` => key `"R12"`).
- `task_id`:
  - If the first token after the checkbox marker looks like dot-numbered (example: `1.1`), store it.
  - Otherwise use `"?"`.
- `description`:
  - Start from the checkbox line text.
  - Remove the leading checkbox marker and `task_id` (if present).
  - Strip trailing bracket tokens (examples: `[#R1]`, `[@F_login]`, `[#REQ-...]`, `[#SCN-...]`, and any other trailing `[...]` tokens).
  - Keep a short, verb-led summary.
- `accept`: the text after `ACCEPT:` in the block (trim).
- `test`: the text after `TEST:` in the block (trim).
- `steps`:
  - If `TEST` starts with `Manual:` (case-insensitive), treat it as manual steps:
    - Split the remainder on newlines and/or semicolons.
    - Trim each step and remove leading numbering like `1)` or `1.`.
  - Otherwise treat `TEST` as runnable command(s):
    - Split on newlines.
    - Also split simple `&&` chains into separate commands.
    - Produce steps like: `Run: <command>`.
- `category` (simple heuristic from `description`, case-insensitive):
  - `docs` if contains: `doc`, `docs`, `readme`, `changelog`
  - `maintenance` if contains: `refactor`, `cleanup`, `lint`, `reformat`
  - `performance` if contains: `perf`, `performance`, `benchmark`
  - `testing` if contains: `test`, `pytest`, `jest`, `unit`, `integration`
  - else: `functional`
- `passes`: default `false` (see preservation rule below).

6) Preserve pass state if output exists
- If `feature_list.json` already exists, preserve `passes` for matching ref keys.
- Do not reset `passes` unless the user explicitly asks to reset (example: "reset passes").
- New refs start with `passes=false`.

7) Write output JSON (pretty, deterministic)
- Write to: `openspec/changes/<change-id>/feature_list.json`.
- Do not write anything if hard validation fails.
- Ensure determinism:
  - Sort features by ref number (R1, R2, R10, ...).
  - Pretty-print with `indent=2` and a trailing newline.
- Set:
  - `change_id` = `<change-id>`
  - `generated_at` = UTC ISO-8601 timestamp with `Z` suffix (example: `2026-01-06T02:30:00Z`)
- Output format MUST be a ref-keyed map (not a list), exactly:
```json
{
  "change_id": "<change-id>",
  "generated_at": "<UTC ISO-8601 Z timestamp>",
  "features": {
    "R1": {
      "category": "functional",
      "description": "New chat button creates a fresh conversation",
      "task_id": "1.1",
      "accept": "<ACCEPT value>",
      "test": "<TEST value>",
      "steps": [
        "Navigate to main interface",
        "Click the 'New Chat' button",
        "Verify a new conversation is created",
        "Check that chat area shows welcome state",
        "Verify conversation appears in sidebar"
      ],
      "passes": false
    }
  }
}
```

8) After writing, print a short summary
- Print: `change-id`, number of features generated, and output path.
