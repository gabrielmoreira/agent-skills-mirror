---
name: planner-task-packet
description: Draft CCB workflow task packets, readiness recommendations, and candidate clarification questions without mutating authoritative state.
---

# Planner Task Packet

Use this skill when converting macro user intent or a frontdesk request into a
plan artifact for review.

## Inputs

- macro task request
- relevant plan-tree/source references
- explicit scope and non-goals
- current phase or prior round result if any

## Outputs

Produce these exact reply-visible sections. Do not replace them with prose,
tables, alternate headings, or "equivalent" sections.

Do not run shell commands, file searches, file reads, tests, builds, or CCB
commands before replying. Use only the intake evidence and compact artifacts
provided in the prompt.

- `task-packet.md`
- `readiness.json`
- `task-set.json` only for explicit independent deliverables, distinct routes,
  or route-mix intake
- `candidate-questions.jsonl` when user input may be needed

For single-slice work, use fenced blocks with these exact labels:

````markdown
**task-packet.md**
```markdown
# Task: <title>
Route: <direct_execution|needs_detail|macro_adjustment_request|blocked|partial_completion>
## Goal
<complete product outcome>
## Acceptance Criteria
- <observable behavior; preserve every intake requirement>
## Interface Contracts
- <concrete module/import path, callable/signature, CLI, data/error shape, or None declared>
## Constraints And Non-Goals
- <constraint or explicit non-goal>
## Execution Decomposition Inputs
- Independently reviewable surfaces: <surfaces or none>
- Stable interfaces available: <interfaces or none>
- Unresolved ordering constraints requiring predecessor output: <constraints or none>
Allowed paths:
- <relative path, or leave empty when route is needs_detail/blocked>
Verification:
- <direct executable argv command>
```

Every `Verification:` item is executed literally without a shell. Do not put
prose such as `Review docs...` in this list. Express documentation and contract
checks as executable tests, or keep them in acceptance criteria for Reviewer
inspection.

**readiness.json**
```json
{"readiness":"ready","route":"direct_execution","blockers":[],"allowed_paths":["path"],"verification":["command"]}
```
````

For task-set work, use exactly one fenced `**task-set.json**` section. Do not
also return single-task sections for the same reply.

For frontdesk single-task work, all five semantic `##` sections shown above
are mandatory and non-empty. Keep them inside the fenced task packet so the
script-owned artifact passed to the orchestrator preserves the user goal,
interfaces, constraints, and decomposition evidence.

A stable interface is parallelization evidence, not a predecessor edge. Only
put a constraint in `Unresolved ordering constraints requiring predecessor
output` when one unit needs a newly generated artifact, schema, data result, or
accepted predecessor evidence that is not already supplied by the intake.
Behavioral prose alone is not a stable interface. A cross-node consumer must
already have the exact module/import path and callable/signature, CLI contract,
or data/error shape it will use. If a test, example, or downstream module would
have to guess a new API name or result contract, record a predecessor-output
constraint instead of claiming that the units can run in parallel.

````markdown
**task-set.json**
```json
{
  "tasks": [
    {
      "task_id": "stable-bounded-task-id",
      "title": "Bounded task title",
      "route": "direct_execution",
      "readiness": "ready",
      "task_packet": "# Task: Bounded task title\nRoute: direct_execution\n",
      "execution_contract": "# Execution Contract\nRoute: direct_execution\n\nAllowed Change Paths:\n- relative/path\n",
      "allowed_paths": ["relative/path"],
      "verification": ["command or evidence review"],
      "blockers": []
    }
  ]
}
```
````

Readiness values are exactly:

- `ready`
- `needs_clarification`
- `blocked`
- `not_ready`

## Bounded Post-Detail Stop

An activation may optionally contain a controller-verified
`terminal_status_constraint`. Treat it as an authority constraint, not a
free-form suggestion, only when all of these fields are present and consistent
with the activation and compact artifact evidence:

- `schema_version=1`
- `status=detail_ready`
- `basis=verified_detail_ready_stop_contract`
- the current `task_id`, positive `task_revision`, and positive `state_version`
- lowercase SHA-256 `authority_digest` and `basis_digest`
- non-empty `required_reason` equal to the controller activation reason
- current post-detail task status `detail_ready` and route context
  `needs_detail`

For this one bounded case, `readiness=ready` means the planning artifacts are
complete; it does not authorize execution. Return a `needs_detail` task packet
and this matching readiness shape:

```json
{"readiness":"ready","route":"needs_detail","status_recommendation":"detail_ready","reason":"<required_reason>","allowed_paths":[],"verification":["<repo-independent verification>"],"blockers":[]}
```

Preserve `required_reason` exactly. Keep `allowed_paths` and `blockers` empty,
and use repo-independent verification rather than Git-only scope checks. The
reply must not authorize implementation, orchestrator, worker, checker, or
another route.

If any required constraint field is absent, stale, malformed, or conflicts with
the current artifacts, revision, task status, reason, or route, fail closed.
You must not guess or synthesize authority, and you must not fall back to
`ready_for_orchestration`. Return a blocker/invalid recommendation so the
controller rejects the reply.

Without `terminal_status_constraint`, this exception does not apply. Preserve
ordinary post-detail flow: after complete detail artifacts, the Planner may
recommend `ready` and `ready_for_orchestration` according to the existing
production rules. It does not make every `needs_detail` plus `ready` reply
terminal.

The provider reply is semantic evidence, not task-status authority. The
controller owns task-status authority, validates provenance/path/digest/revision
fences, and alone imports or settles the recommendation.

For `route: needs_detail`, use `readiness: needs_clarification`, include
specific `blockers`, include `verification` for the detail packet, and set
`allowed_paths` to an empty list. Do not authorize implementation paths until
detail is resolved. This ordinary rule remains in force unless the valid
bounded post-detail constraint above is present.

For `route: blocked`, use `readiness: blocked`, include specific `blockers`,
include verification evidence for the blocker, and set `allowed_paths` to an
empty list. Do not authorize implementation paths for blocked prerequisites.

For `route: direct_execution` or `route: partial_completion`, include non-empty
`allowed_paths`, concrete `verification`, and an `Allowed Change Paths` section
inside `execution_contract` matching `allowed_paths`. The runner uses this
section as the authority boundary when promoting isolated worker workspace
changes into the project root.

For Python unit tests stored under `tests/`, use unittest discovery commands
such as `python -m unittest discover -s tests -p test_example.py`. Do not use
file-path unittest commands such as `python -m unittest tests/test_example.py`;
those can resolve to an installed third-party `tests` package in inherited
provider environments.

Choose scope verification from the explicit project capability carried by the
intake:

- `Project capability: git_repository=true`: Git commands may be used when
  they are relevant to the requested work.
- `Project capability: git_repository=false` or
  `git_repository=not_guaranteed`: do not emit `git diff`, `git status`,
  `git diff --name-only`, or another Git-only scope check. Use `allowed_paths`
  with direct repo-independent file existence, content, test, or manifest
  checks.

Do not infer this capability from `lab`, a filesystem path, or an earlier
provider response. This is a per-activation constraint, not a global Git ban.
If no capability is declared and Git behavior is not itself part of the user
request, prefer repo-independent verification.

## Rules

- Do not mark task state directly.
- Do not start execution.
- Do not call workers, checkers, or orchestrator.
- Do not reduce acceptance criteria to make the task executable.
- Keep one cohesive product deliverable in one task envelope even when it spans
  multiple files or independently implementable surfaces. The orchestrator owns
  execution-node slicing, dependencies, parallelism, and reviewer assignment.
- Use `task_set` only for independent roadmap deliverables, distinct routes, or
  explicitly requested multiple tasks; do not use it to pre-slice one
  orchestrator workgraph.
- Questions must be current-phase questions; defer later-phase questions.
