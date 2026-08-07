---
name: continual-learn
description: Persist learning across turns by actively maintaining MENTAL_MODEL.md in the workspace. Use for iterative coding, debugging, benchmarking, or any feedback-driven task; read and update the file with actual filesystem writes before every response, never just hidden/internal memory.
---

You must maintain a real workspace file, `MENTAL_MODEL.md`, as your durable scratchpad for this task.

## Non-negotiable file workflow

- Use `./MENTAL_MODEL.md` in the current workspace; create it if it does not exist.
- At the start of each turn, consult the current file when possible.
- Before every final answer or structured task response, perform an actual filesystem write that creates or updates `MENTAL_MODEL.md`.
- This file write is required even when the task says the final response must contain only JSON or another strict schema. The write happens before the final response; the final response must still obey the requested schema exactly.
- If a dedicated file-write/edit operation is available, use it. Otherwise, use any available shell/filesystem operation to write the file.

## What to record

Keep notes terse, high-signal, and actionable:

- Task goal, current plan, and open assumptions.
- Feedback received and what it changes.
- Durable lessons, repo/task quirks, commands tried, and observed failures.
- Hypotheses being tested and evidence for/against them.
- Current state and the next concrete action.
- If nothing meaningful changed, still update a short "latest turn" line so the file write occurs.

## Hygiene

- Keep the file compact; rewrite or prune stale notes as needed.
- Do not store secrets, raw datasets, large traces, or unrelated transcript dumps.

**Always write `MENTAL_MODEL.md` before responding.**
