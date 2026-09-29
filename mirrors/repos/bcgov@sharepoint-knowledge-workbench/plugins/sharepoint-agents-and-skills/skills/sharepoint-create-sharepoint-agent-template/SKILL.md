---
name: sharepoint-create-sharepoint-agent-template
description: Authors a reusable SharePoint agent template (purpose, instruction structure, boundaries, refusal behavior, citation expectations, knowledge-source placeholders, governance metadata) distinct from a concrete .agent package.
---

# create-sharepoint-agent-template

## Purpose

Captures the reusable *shape* of an agent — governance metadata, boundary rules, and knowledge-
source placeholder count — separately from any concrete deployment target. Template creation is
distinct from agent creation: `create-sharepoint-agent` produces a concrete `.agent` file for one
target; this produces a reusable template `apply-sharepoint-agent-template` later fills in.

## Input boundaries

- `-TemplateName`, `-Purpose`, `-TemplateVersion`, `-KnowledgeSourcePlaceholderCount`
  (`>= 1`) — required.
- `-InstructionsTemplatePath` **or** `-InstructionsTemplate` — exactly one required.
- `-AnswerBoundary`, `-RefusalBehavior`, `-CitationExpectations` — optional, appended as their
  own sections when supplied.
- `-OutputPath` (required); `-Overwrite` required to replace an existing file.

## Prohibited scope

- Zero tenant I/O.
- Does not produce a deployable `.agent` file — use `apply-sharepoint-agent-template` for that.

## Scripts

- `../../scripts/create-sharepoint-agent-template.ps1`

## Tests

`../../tests/unit/test_agent_templates.py` (shared with `apply-sharepoint-agent-template`) — 4
executable tests via `pwsh`.

