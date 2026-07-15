---
name: bounded-work-item
description: Execute one scoped implementation or investigation item and return evidence without changing workflow authority.
---

# Bounded Work Item

Use this skill when the controller supplies one canonical node work packet
with declared refs, scope, non-goals, dependency evidence, acceptance refs,
allowed paths, and verification refs.

The only Coder terminal status enum is `done|blocked|needs_rework`.

## Workflow

1. Read only the canonical node work packet and its declared refs.
2. Inspect relevant files before editing. Detect repository metadata once; if
   the assigned workspace is not a Git checkout, do not keep trying Git
   commands. Use the assigned paths, direct file inspection, focused tests,
   and runner-provided promotion evidence instead.
3. Make the smallest change that satisfies the packet inside its allowed
   paths. Do not expand scope or inspect sibling packets.
4. Run focused verification when possible.
5. After verification, use only the assigned-review chain skill to submit the
   evidence to the assigned Reviewer, then stop for continuation.
6. Apply bounded requested rework when returned. After Reviewer pass, perform
   no more file/tool mutation and immediately return changed paths,
   verification evidence, blockers, and `done`.

## Boundaries

- Do not lower acceptance criteria.
- Do not silently substitute fallback behavior.
- Do not claim whole-round success.
- Do not directly edit authoritative CCB state or runtime files.
- Do not run CCB commands or workflow wrappers except the exact assigned
  Reviewer `ask --chain --artifact-reply` operation.
- Do not submit other downstream asks, create authority commits, integrate sibling
  work, promote project-root state, or release agents.
- Provider and model selection remain project configuration concerns. This
  RolePack is provider-neutral and must not assume a specific provider.
