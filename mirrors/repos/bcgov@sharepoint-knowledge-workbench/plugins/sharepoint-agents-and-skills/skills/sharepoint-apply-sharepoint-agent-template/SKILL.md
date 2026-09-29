---
name: sharepoint-apply-sharepoint-agent-template
description: Applies an existing agent template to a specific target, producing a concrete .agent package via create-sharepoint-agent.
---

# apply-sharepoint-agent-template

## Purpose

Fills a template's knowledge-source placeholders with real URLs, assembles the final
instructions from the template's sections, and delegates to `create-sharepoint-agent` to write
the resulting `.agent` package. Rejects a mismatched knowledge-source count rather than silently
truncating or padding.

## Input boundaries

- `-TemplatePath` (required) — must exist.
- `-AgentName`, `-AgentDescription` (required) — the concrete agent's identity; the template has
  none of its own.
- `-KnowledgeSourcePaths` (required) — must contain **exactly** the template's
  `KnowledgeSourcePlaceholderCount`.
- `-OutputPath` (required); `-Overwrite` passed through to `create-sharepoint-agent.ps1`.

## Prohibited scope

- Zero tenant I/O.
- Does not deploy the produced package.

## Scripts

- `../../scripts/apply-sharepoint-agent-template.ps1` (delegates to
  `create-sharepoint-agent.ps1`)

## Tests

`../../tests/unit/test_agent_templates.py` — includes exact-source-count enforcement.

**Note on multi-value array parameters:** invoking a script with a multi-value array parameter
(e.g. 2+ `-KnowledgeSourcePaths`) followed by additional named parameters is unreliable via
`pwsh -File`'s positional binding (confirmed via direct reproduction) — use `-Command` with an
explicit `@(...)` array literal instead. Single-value arrays work fine under `-File`.

