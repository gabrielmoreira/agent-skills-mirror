---
name: sharepoint-update-sharepoint-agent
description: Updates an existing local .agent source package's description, instructions, or knowledge sources in place, without recreating the whole package.
---

# update-sharepoint-agent

## Purpose

Previously missing entirely — there was no way to change an agent's instructions or grounding
sources without running `create-sharepoint-agent` again from scratch. Operates on the same local
`.agent` JSON package `create-sharepoint-agent` produces.

## Input boundaries

- `-AgentPath` (required) — must already exist; fails if not found (this skill updates, it does
  not create).
- `-AgentDescription`, `-AgentInstructionsPath`/`-AgentInstructions`, `-KnowledgeSourcePaths` —
  all optional, but at least one is required (no-op invocations are rejected).
- Empty `-KnowledgeSourcePaths` requires explicit `-AllowEmptyKnowledgeSources` — refuses to
  silently clear all grounding sources.

## Prohibited scope

- Zero tenant I/O.
- Does not deploy the updated package — same as `create-sharepoint-agent`, deployment is a
  separate, not-yet-built capability.

## Scripts

- `../../scripts/update-sharepoint-agent.ps1`

## Tests

`../../tests/unit/test_update_sharepoint_agent.py` — 5 executable tests via `pwsh` (description
update leaves instructions unchanged, knowledge-source replacement, missing-path rejection,
no-parameters rejection, empty-knowledge-sources-without-allow rejection).

