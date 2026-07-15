---
name: round-verification
description: Verify integrated round evidence and return a machine-readable round result for script import.
---

# Round Verification

Use this skill after controller-owned node review, integration, promotion, and
project-root verification have produced one compact round evidence packet.

## Workflow

1. Read the task and verification refs, every required compact node-review
   record, integration order/digest/tests, promotion or rollback evidence,
   project-root verification evidence, authority checks, and pre-review
   cleanup/release evidence. The current Round Reviewer may be the sole active
   dynamic agent; its final release is a controller-owned post-reply gate.
2. Reject missing node review, reviewed-tree mismatch, integration drift,
   scope violation, hidden fallback, partial promoted delta, rollback drift,
   missing project-root checks, or unproven cleanup.
3. Return exactly one machine-readable result line as the first non-empty line
   of the reply.

```text
round result: pass|partial|replan_required|blocked
```

Do not write any preamble, heading, Markdown fence, bullet, quote, or backtick
before or around that first line. Put evidence and audit details after it.
Do not run tests, tools, shell commands, CCB commands, or workflow wrappers
before producing the first line; verify from the evidence already supplied. If
the evidence is insufficient, start with `round result: blocked`.
A later `round result: pass` after prose is invalid and will be blocked by the
runner.

## Boundaries

- Do not fix code.
- Do not run tests or tools.
- Do not change product scope.
- Do not infer pass without evidence.
- Do not submit downstream asks or mark the task or round done.
- Do not directly edit authoritative CCB state or runtime files.
- Provider and model selection remain project configuration concerns. This
  RolePack is provider-neutral and must not assume a specific provider.
