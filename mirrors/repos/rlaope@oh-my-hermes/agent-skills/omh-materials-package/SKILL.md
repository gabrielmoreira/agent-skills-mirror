---
name: "omh-materials-package"
description: "[omh] Hermes Materials Package workflow: decks, PDFs, spreadsheets, documents, HWP, Markdown, and binary export handoffs. Use when the user says: materials-package, material package, materials package, document package, deck file, binary export, file export, render qa."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, materials]
    category: materials
    phase: material-plan
    role: operator
    quality_tier: material-gated
---

# Materials Package

This is an OMH `materials-package` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`materials-package` exists so Hermes can handle document, deck, spreadsheet, PDF, Word, Keynote, HWP, and Markdown work as a first-class material-processing workflow without becoming a hidden file generator.

## Do Not Use When

- The user only needs a weekly/monthly report outline; use `report-package`.
- The user asks for recurring meeting minutes or scrum history; use `operating-rhythm`.
- The request is code documentation, README, or project wiki maintenance; use the docs/wiki workflow.

## Examples

Good example:

- Prompt: materials-package 엑셀 매출 리포트를 PDF로 공유할 수 있게 준비해줘.
- Expected behavior: Create a material plan with xlsx/pdf target formats, source inputs, missing metrics, QA checks, and a generation handoff boundary.
- Why: The request is about material processing and binary export evidence, not just a text report outline.

Bad example:

- Prompt: materials-package prove the PDF was sent to leadership.
- Expected behavior: Ask for observed delivery evidence or record the delivery as not_observed instead of claiming it happened.
- Why: A prepared material artifact cannot prove export, approval, or delivery.

## Completion Checklist

- The material source, target format, audience, structure, and QA expectation are named.
- Binary export, rendering, formula recalculation, attachment, and delivery stay observed-only.
- The next action identifies whether the package is planned, generated, QA-ready, or blocked.

## Recovery Notes

- If a renderer or file tool is missing, keep the package prepared and expose the generation handoff.
- If render QA is unavailable, mark the artifact unverified and request the smallest visual/file check.



## Use When

Use when Hermes should turn source inputs into a material plan for decks, PDFs, Word/documents, spreadsheets, HWP, Markdown, office-file summaries, comparisons, table extraction plans, or binary export handoff without claiming file generation.

    Strong routing signals: `materials-package`, `material package`, `materials package`, `document package`, `deck file`, `binary export`, `file export`, `render qa`, `layout qa`, `ppt and pdf`, `pdf and ppt`, `ppt/pdf`, `pdf/ppt`, `spreadsheet to pdf`, `excel to pdf`, `monthly report pdf`, `attached spreadsheet`, `word document`, `word doc`, `document action items`, `compare pdfs`, `pdf differences`, `extract tables from pdf`, `pdf to csv`, `spreadsheet analysis brief`, `clean analysis brief`, `pdf`, `pptx`, `keynote`, `keynote deck`, `docx`, `xlsx`, `csv report`, `spreadsheet`, `excel`, `hwp`, `korean hwp`, `proposal document`, `PDF`, `HWP`, `첨부한 엑셀`, `첨부한 워드`, `워드 문서`, `PDF 두 개 비교`, `PDF 표를 CSV`, `PDF 표 추출`, `분석 브리프`, `엑셀을 월간 보고서`, `자료 패키지`, `자료 처리`, `자료 생성`, `문서 패키지`, `문서 생성`, `제안서 문서`, `엑셀`, `스프레드시트`, `피디에프`, `한글 문서`, `키노트`, `파일 export`, `파일 생성`, `렌더 QA`, `PDF랑 PPT`, `PPT랑 PDF`, `PDF와 PPT`, `PPT와 PDF`, `PDF랑 PPT로`

## Catalog Metadata

Category: `materials`
Phase: `material-plan`
Quality tier: `material-gated`
Reasoning demand: `standard`

Quality bar:

- Name audience, source inputs, requested extraction/comparison task, target formats, outline sections, assumptions, missing inputs, and output owner.
- Attach format-specific QA expectations before preparing a binary-generation handoff.
- Record binary export, render QA, formula checks, approvals, and delivery only from observed evidence.

Required inputs:

- audience or recipient
- source inputs
- target format(s)
- deadline or delivery context
- missing data or assumptions

Expected outputs:

- material_artifact/v1 plan
- format-specific QA ladder
- executor-neutral generation handoff when needed
- observed export boundary

Artifact expectations:

- material_artifact/v1 under .omh/materials when a wrapper or CLI records it

Safety rules:

- Do not claim PPTX, PDF, Keynote, DOCX, XLSX, HWP, or upload output without observed file evidence.
- Do not claim render QA, formula recalculation, approval, or delivery from a prepared material plan.
- Keep source facts, assumptions, missing inputs, and generated output evidence separate.

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
