---
name: "omh-product-brief"
description: "[omh] Turn product evidence into a decision-ready PRD, prioritization frame, and roadmap brief. Use when the user says: product requirements document, PRD, roadmap prioritization, 제품 요구사항 문서, 제품 기획서, 로드맵 우선순위."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, planning]
    category: planning
    phase: product-brief
    role: planner
    quality_tier: planning-gated
---

# Product Brief

This is an OMH `product-brief` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`product-brief` turns product evidence into a reviewable PRD and prioritization frame before delivery planning without treating a draft as an accepted roadmap commitment.

## Do Not Use When

- The input is unprocessed feedback, bug reports, or feature asks that first need clustering and evidence boundaries; use `feedback-triage`.
- The product evidence is unvalidated, synthetic, or a founder belief and the problem gate has not returned validated; use `product-discovery-validation` before a PRD.
- The input is a growth hypothesis that still needs an experiment and readout before it becomes a product requirement; use `lifecycle-growth`.
- The user needs a company or product strategy decision across high-level options rather than a requirements or roadmap artifact; use `strategy-brief`.
- The request is an accepted, code-ready change with repository constraints and verification needs; use `ralplan` or `ultrawork` rather than recreating a PRD.
- The user asks to create or update Jira, Linear, Aha!, or a roadmap system directly; use `connector-operator` with explicit target, approval, and observed evidence.

## Examples

Good example:

- Prompt: Create a PRD and prioritization options for reducing first-time user drop-off in onboarding.
- Expected behavior: Prepare the product problem, user and metric brief, PRD, roadmap options, tradeoffs, and downstream prerequisites.
- Why: The request needs a decision-ready requirements and prioritization artifact before delivery planning.

Bad example:

- Prompt: Implement the accepted onboarding PRD and open a PR.
- Expected behavior: Route to `ultrawork` or `ralplan`, not `product-brief`.
- Why: Accepted implementation work should move into planning or delivery rather than recreate a PRD.

## Completion Checklist

- The plan names goals, non-goals, assumptions, acceptance criteria, and verification shape.
- Draft recommendations, accepted decisions, and executor handoffs are separate states.
- Rejected options or unresolved tradeoffs are recorded before handoff.

## Recovery Notes

- If acceptance criteria or verification are missing, route back to clarification before handoff.
- If assumptions materially affect the plan, keep them visible and avoid treating the plan as accepted.



## Use When

Use when a product owner needs a problem frame, user/outcome definition, PRD, prioritization/roadmap options, dependencies, acceptance shape, and decision record before delivery planning.

    Strong routing signals: `product requirements document`, `PRD`, `roadmap prioritization`, `제품 요구사항 문서`, `제품 기획서`, `로드맵 우선순위`

## Catalog Metadata

Category: `planning`
Phase: `product-brief`
Quality tier: `planning-gated`
Reasoning demand: `standard`

Quality bar:

- Name problem, user, metric, goals, non-goals, requirements, dependencies, risks, and acceptance shape.
- Preserve decision owner and downstream prerequisite boundaries.

Required inputs:

- product evidence
- problem and user
- goal and non-goals
- decision owner

Expert clarification questions:
- `product evidence`
  - English: What product evidence should anchor this brief?
  - Korean: 이 브리프의 근거가 될 제품 증거는 무엇인가요?

Expected outputs:

- problem, user, evidence, metric, goal, and non-goal brief
- PRD with requirements, open questions, risks, dependencies, and acceptance shape
- prioritization/roadmap options with tradeoffs and decision owner
- explicit downstream route to ralplan, strategy-brief, or ultrawork only when its prerequisite is satisfied

Artifact expectations:

- prepared product brief or PRD when a wrapper captures it

Safety rules:

- Separate product evidence, assumptions, prioritization options, and stakeholder acceptance.
- Do not claim roadmap-system mutation, implementation, test evidence, delivery, or market commitment.

## Runtime Evidence

Use the current host's own tools and subagent/task mechanism when available;
otherwise run the same lanes sequentially or name the unavailable capability.
A prepared plan, handoff, checklist, or skill installation is not execution,
review, CI, merge-readiness, or merge evidence. Record actual tool results, or
`not_observed` / `not_available`, in the record; never invent dispatch or host
accounting.
Treat supplied context as advisory, not proof of hidden memory reads or writes.
State scope, constraints, verification, and the stop condition before work.
Reply in the user's own words and the host's own voice: OMH's record terms
(surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in
records and tool calls, never in the sentence the user reads unless they ask
about one; and when a stop condition or a decision the user owns ends the turn,
offer the next action as a question rather than declaring what will not be done.
Supporting paths are relative to this skill directory; sibling skill paths are
relative to its parent. Resolve them from the host-provided skill base directory
(`{baseDir}` on hosts that provide it), never a hardcoded install location.
A named workflow not installed here is unavailable, not permission to emulate
its host-specific capabilities. Verify through the real surface before done.
