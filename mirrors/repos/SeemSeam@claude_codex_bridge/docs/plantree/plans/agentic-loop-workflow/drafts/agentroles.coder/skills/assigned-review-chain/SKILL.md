---
name: assigned-review-chain
description: Submit one node result to the assigned Reviewer and finish only after a bounded pass/rework chain.
---

# Assigned Review Chain

Use this skill only when the node task names one assigned Reviewer.

The only Coder terminal status enum is `done|blocked|needs_rework`.

## Submit

After implementation and verification, run exactly once per bounded review hop:

```bash
command ask --chain --artifact-reply <assigned-reviewer> <<'EOF'
Node: <node id>
Workgroup: <workgroup id>
Visible workspace identity: <controller-assigned workspace identity>
Canonical node work packet ref: <ref>
Allowed paths:
- <project-relative path>
Acceptance refs:
- <ref>
Verification refs:
- <ref>
Verification results:
- <command and result>
Changed paths:
- <path>
Blockers:
- <none or exact blocker>
Review the current node against the supplied work packet and acceptance refs.
Your first non-empty reply line must be exactly one of:
- status: pass
- status: rework_required
- status: blocked
- status: non_converged
Do not put a preamble or code fence before that machine line.
EOF
```

Replace `<assigned-reviewer>` with the literal Reviewer name supplied in the
node task. It is not an environment variable and must not be inferred.
The machine-line requirement is part of every Reviewer request; do not rely on
the Reviewer's remembered role instructions alone.

Then stop. Do not poll, watch, ping, wait, or set a timeout.

## Continuation

- `status: pass`: return Coder terminal `done` immediately.
- `status: rework_required`: apply only the requested bounded repair, rerun
  verification, ask the same Reviewer with `--chain` again, then stop.
- `status: blocked`: return Coder terminal `blocked`.
- `status: non_converged`: return Coder terminal `needs_rework`.
- `status: rework_required` remains bounded intermediate evidence only.

## Boundaries

- The same assigned Reviewer is the only allowed target for every bounded review hop.
- Do not use plain ask, `--silence`, multiple targets, another role, or another
  CCB command.
- Do not claim `done` before Reviewer pass.
- Do not create commits, integrate, promote, write task/runtime authority, or
  release agents.
