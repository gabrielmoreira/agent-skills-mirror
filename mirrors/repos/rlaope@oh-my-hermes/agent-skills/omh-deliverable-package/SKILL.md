---
name: "omh-deliverable-package"
description: "[omh] Hermes deliverable package workflow: track PPT, PDF, XLSX, DOCX, HWP, Markdown, and attachments through prepared, generated, QA, approved, and attached states. Use when the user says: deliverable-package, deliverable mode, file attachment, attach file, attachment status, file delivery, file deliverable status, generated file."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, deliverables]
    category: deliverables
    phase: package-status
    role: operator
    quality_tier: workflow-surface-gated
---

# Deliverable Package

This is an OMH `deliverable-package` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`deliverable-package` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: deliverable-package turn this research into PPT and PDF with attachment status.
- Expected behavior: Produce `prepare_deliverable_package` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: deliverable-package claim the PDF was attached without observed file evidence.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The deliverable type, audience, source inputs, QA ladder, and delivery boundary are named.
- Prepared generation, generated file, render QA, approval, attachment, and delivery are separate states.
- The next action says whether to generate, revise, QA, approve, attach, or deliver.

## Recovery Notes

- If generation tooling is missing, prepare a prompt or package handoff and mark file output not_observed.
- If QA or attachment evidence is missing, keep generated/delivered states separate and show the next check.



## Use When

Use when Hermes should prepare, request generation, QA, and report attachment status for user-visible file deliverables.

    Strong routing signals: `deliverable-package`, `deliverable mode`, `file attachment`, `attach file`, `attachment status`, `file delivery`, `file deliverable status`, `generated file`, `첨부`, `첨부 상태`, `전달 상태`

## Catalog Metadata

Category: `deliverables`
Phase: `package-status`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- deliverable-package/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- deliverable-package/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A deliverable package card is not binary generation, render QA, formula recalculation, approval, upload, attachment, or delivery evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Use the current host's own tools and subagent/task mechanism when available;
otherwise run the same lanes sequentially or name the unavailable capability.
A prepared plan, handoff, checklist, or skill installation is not execution,
review, CI, merge-readiness, or merge evidence. Report actual tool results or
`not_observed` / `not_available`; never invent dispatch or host accounting.
Treat supplied context as advisory, not proof of hidden memory reads or writes.
State scope, constraints, verification, and the stop condition before work.
Supporting paths are relative to this skill directory; sibling skill paths are
relative to its parent. Resolve them from the host-provided skill base directory
(`{baseDir}` on hosts that provide it), never a hardcoded install location.
A named workflow not installed here is unavailable, not permission to emulate
its host-specific capabilities. Verify through the real surface before done.
