---
name: task-detail-packet
description: Draft task-scoped detail artifacts and a detail packet as reply content for script-owned workflow import.
---

# Task Detail Packet

Use this skill when a macro task packet needs task-local execution detail before
orchestrator dispatch.

## Workflow

1. Read only the controller-supplied macro task refs, plan-tree refs, accepted
   decisions, source files, tests, and durable evidence for this immaculate
   activation.
2. Draft task-scoped detail design and source-evidence map.
3. Produce detailed acceptance, verification, and worker handoff notes.
4. Return `task-detail-design.md`, `brief-update-summary.md`, and exactly one
   canonical `detail-packet.manifest.json:` section immediately followed by a
   literal `json` fence. The packet is JSON, never Markdown.
5. Classify the result as exactly `local_detail_ready`,
   `planner_replan_required`, `needs_clarification`, or `blocked`.
6. In the brief update, classify `global impact: none|bounded|macro`, give a
   compact rationale, and state planner backfill evidence.
7. For `planner_replan_required` only, author the versioned request and submit
   exactly one direct silent inline ask to resident `planner` through the
   managed capability. For every other result, submit no Planner ask.

The manifest must contain exactly `schema`, `detail_result`, `readiness`, and
`global_impact`. Set `schema` to `ccb.detail_packet_manifest.v1`. Legal tuples
are `local_detail_ready/detail_ready/none`,
`planner_replan_required/planner_replan_required/macro`,
`needs_clarification/needs_clarification/none|bounded`, and
`blocked/blocked/none|bounded|macro`. Do not use an old label, a schema-named
fence, a second manifest, or a cross-outcome tuple.

## Boundaries

- Do not rewrite roadmap or accepted decisions directly.
- Do not lower acceptance criteria.
- Do not dispatch runtime agents.
- Never dispatch workers or submit downstream asks except the one restricted
  `ccb.detailer.replan_request.v1` Planner replan handoff.
- Do not directly edit authoritative CCB state or runtime files.
- Do not run `ccb plan`, `ccb loop`, generic `ccb ask`, `ccb_test`, or wrapper
  commands. The sole managed Planner handoff is the only routing exception.
- Do not write detail artifacts into the project tree for later self-import;
  put artifact content in the reply.
- Do not add `--chain`, wait, watch, poll, use arbitrary targets, or run a
  generic shell/CCB command.
- Provider and model selection remain project configuration concerns.
