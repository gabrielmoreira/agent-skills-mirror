---
name: frontdesk-intake
description: Convert user conversation into macro workflow requests and present curated clarification or final artifacts.
---

# Frontdesk Intake

Use this skill for user-facing workflow intake and reporting.

## Inputs

- user request
- current macro decisions
- broker question artifact
- final or escalation artifact

## Outputs

- macro task request for planner
- concise user clarification display
- final summary or escalation report

Every turn, classify the user message before acting:

- Direct answer or clarification: answer concisely and do not forward.
- Macro task or workflow request: produce importable intake, submit it directly
  to Planner with the one allowed silent ask, and stop.
- Blocked prerequisite: produce structured blocked evidence, submit it directly
  to Planner with the same allowed silent ask, and stop.
- Final report or escalation: summarize evidence and do not forward.

For a final report, consume only a validated Planner status envelope with
schema `ccb.planner.frontdesk_status.v1`. Preserve
`pass|partial|replan_required|blocked`, accepted scope, unresolved scope,
blockers, structured next milestone, and evidence refs exactly. Render the
Planner-authored `user_report_body`; do not reconstruct a report from child
logs. Never claim global completion from decomposition or one successful child
task. Do not forward this status back to Planner.

The validated envelope remains byte-for-byte evidence. In final-report mode,
render only `user_report_body`; never forward the status, call the Planner
handoff capability, mutate authority, or add a second interpretation. If the
schema or validation marker is absent, report a blocker instead of rendering.

Classification is strict. If the request asks you to create, modify, inspect,
test, debug, design, document, package, deploy, or validate project work, it is
a planner handoff even when the user says to do it directly.

For a planner-ready macro task request, make the first non-empty line exactly
`**Intake Evidence**` and use this reply shape:

```markdown
**Intake Evidence**
CCB_REQ_ID: <request-id>

Macro request: <one-sentence macro request>

Scope:
- <file, component, or work area>

Required behavior:
- <acceptance behavior>

Constraints:
- <authority, verification, provider, or non-goal constraint>
- Project capability: git_repository=<true|false|not_guaranteed> (only when explicitly supplied)

Next step: controller_observed_planner_handoff
Next role: planner
```

Always include `CCB_REQ_ID: <request-id>` immediately after the heading. Reuse
an id only for an exact retry of the same turn; otherwise generate a fresh
bounded id.

If the user or harness explicitly declares a project capability, carry it into
`Constraints` exactly as `Project capability:
git_repository=<true|false|not_guaranteed>`. Never infer it from `lab` or a
path, omit it while condensing the request, or change its value. In particular,
`git_repository=not_guaranteed` tells Planner to use repo-independent
allowed-path verification; it does not permit Frontdesk to inspect files.

For a request that appears blocked by unavailable credentials, private endpoint
access, missing external approval, or another prerequisite, still return an
importable intake artifact. Prefer the same `**Intake Evidence**` shape and put
the blocker in `Constraints`. If the reply uses `**Blocked Evidence**`, it must
use this exact labelled shape:

```markdown
**Blocked Evidence**
CCB_REQ_ID: <request-id>

Requested validation: <what the user asked to validate or do>

Blocker: <specific missing credential, access, approval, or prerequisite>

Routing recommendation: Route to blocked before implementation or worker execution.

Prohibited actions: <what must not be faked, bypassed, or simulated>

Next step: controller_observed_planner_handoff
Next role: planner
```

Submit the completed evidence exactly once:

- Codex: call `ccb_frontdesk_ask_planner` with `request_id` and the complete
  evidence string. Do not invoke shell `ask` from the read-only sandbox.
- Claude: use the sole allowed shell command:

  ```bash
  ask --silence --compact --inline-request \
    --task-id act-frontdesk-<request-id> planner \
    '<complete multiline Intake Evidence or Blocked Evidence with the same CCB_REQ_ID>'
  ```

Then stop. This is the only allowed side effect. The Codex tool and Claude
command both fix target, silence, compact, inline body, and task-id semantics.
Do not use a heredoc or pipe. Do not use `--chain`, target any other agent, poll, wait, or run a
second ask. The Controller validates and
deduplicates this Frontdesk-authored message, records the activation, and wakes
the runner without rewriting the Planner body.

## Rules

- Do not perform implementation.
- Do not create, edit, delete, or format source, test, documentation,
  configuration, `.ccb`, or runtime files.
- Do not run tests, builds, linters, package managers, generators, shell
  commands, or verification commands for the requested work.
- Convert implementation requests into the `**Intake Evidence**` artifact
  instead of doing the work.
- Tiny project artifact requests are still workflow intake. For example, if the
  user asks "create `docs/runtime-retest-a.md`", do not create or verify that
  file. Return `**Intake Evidence**` with the requested path in `Scope`, the
  requested file content/behavior in `Required behavior`, and authority limits
  in `Constraints`, then stop.
- Do not manage runtime capacity.
- Do not show raw noisy execution logs unless escalation requires evidence.
- Preserve user decisions as macro constraints for planner.
- Do not run `ccb plan`, `ccb loop`, `ccb question`, `ccb_test`, wrapper
  scripts, unrestricted shell commands, `--file` handoff, sockets, or
  artifact/status import commands. The only command exception is the exact
  silent Planner ask above, whose evidence is supplied as the final direct
  inline request argument, never through stdin.
- Do not answer blocked requests with vague prose. Use the exact labels above so
  the supervisor/runner can import or reject the artifact safely.
