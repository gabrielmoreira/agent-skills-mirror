---
name: "omh-report-package"
description: "[omh] Hermes Report Package workflow: weekly/monthly reports, executive briefs, PPT-ready outlines, and upload packages. Use when the user says: report-package, report package, weekly report, monthly report, executive report, exec brief, leadership deck, status package."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, reporting]
    category: reporting
    phase: package-outline
    role: operator
    quality_tier: report-gated
---

# Report Package

This is an OMH `report-package` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`report-package` exists to make reporting a first-class operations surface: Hermes can produce clean report and slide outlines while keeping approvals, delivery, and binary deck export as separate evidence.

## Do Not Use When

- The user needs SLO, incident, or error-budget review; use `reliability-review`.
- The user asks for a live `.pptx` deck file rather than a PPT-ready outline.
- The request is meeting minutes, scrum history, or action-item tracking.

## Examples

Good example:

- Prompt: report-package 월간 리더십 보고서 PPT outline 만들어줘.
- Expected behavior: Prepare a report package with sections, assumptions, missing inputs, and Markdown/JSON outline scope.
- Why: The request is packaging known information for reporting, not reliability validation or code work.

Bad example:

- Prompt: report-package prove our SLO passed and close the incident.
- Expected behavior: Route to `reliability-review` and require metric or incident evidence.
- Why: Report packaging cannot satisfy reliability closure evidence.

## Completion Checklist

- The reporting window, inputs, audience, narrative, and evidence gaps are named.
- Draft report, generated package, approval, and delivery are separate states.
- The next action says whether to gather evidence, generate, revise, approve, or deliver.

## Recovery Notes

- If input evidence is incomplete, mark the section as pending rather than fabricating a report claim.
- If delivery or attachment is unavailable, keep the report package prepared_not_observed.



## Use When

Use when Hermes should turn supplied inputs into a report, executive brief, PPT-ready outline, or upload package without claiming presentation delivery.

    Strong routing signals: `report-package`, `report package`, `weekly report`, `monthly report`, `executive report`, `exec brief`, `leadership deck`, `status package`, `ppt outline`, `presentation outline`, `slide outline`, `upload package`, `PPT`, `보고서 패키지`, `주간 보고서`, `월간 보고서`, `경영진 보고`, `리더십 보고`, `피피티`, `슬라이드`, `발표자료`, `업로드 패키지`

## Catalog Metadata

Category: `reporting`
Phase: `package-outline`
Quality tier: `report-gated`
Reasoning demand: `standard`

Quality bar:

- Name audience, reporting period, sections, supplied facts, assumptions, and missing data.
- Keep report packaging independent from reliability review unless explicitly requested.
- Export only Markdown/JSON outlines unless a separate presentation tool produces a binary deck.

Required inputs:

- audience
- reporting period or scope
- supplied facts
- missing data or assumptions

Expected outputs:

- report package
- PPT-ready Markdown or JSON outline
- assumptions and missing-input list
- Optional supplied achievements summary when requested; plugin-backed badge retrieval is unavailable in this projection.

Artifact expectations:

- operation_artifact/v1 report-package artifact when a wrapper or CLI records it

Safety rules:

- Do not claim source review completion from a prepared report package.
- Do not claim stakeholder approval or presentation delivery without observed evidence.
- Do not couple report packages to SLO, incident, or error-budget evidence by default.

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
