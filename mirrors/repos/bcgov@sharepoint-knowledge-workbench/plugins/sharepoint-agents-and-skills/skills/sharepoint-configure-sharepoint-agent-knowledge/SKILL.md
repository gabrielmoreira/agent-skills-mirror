---
name: sharepoint-configure-sharepoint-agent-knowledge
description: Read-only report of a deployed SharePoint agent's current knowledge-source bindings, plus resolution of the exact site_id/web_id/list_id/unique_id a new binding needs.
---

# configure-sharepoint-agent-knowledge

## Purpose

Two related, read-only capabilities:

1. **Inspect a deployed agent's current bindings** (`configure-sharepoint-agent-knowledge.ps1`) —
   downloads a deployed `.agent` file and reports what it's actually grounded on right now.
   Distinct from `update-sharepoint-agent`, which edits a *local* package.
2. **Resolve resource identifiers for a new binding** (`get-agent-resource-identifiers.ps1`) —
   extracts `site_id`/`web_id`/`list_id`/`unique_id` for a given site-relative folder, per the
   confirmed working method documented in `docs/research/phase-4-agent-format-learning-
   journal.md` and `PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md`: prior to this skill, these
   IDs were extracted from a working reference agent by hand, every time a new agent needed
   correct site isolation. This scripts that manual process.

## Correction from the Phase 6 plan (2026-08-03)

The plan named `task-9-retrieve-topic-metadata.ps1` as this capability's source. Direct reading
found that script inspects *topic item metadata field values* (`TopicID`, `PublicationOrder`,
`TopicContentSHA256`, `Status`, `ReviewDate`, `TransitionAction`, `TransitionTarget`) — unrelated
to agent knowledge-source configuration. It was not extracted from; it remains research-only in
`tools/`. Both scripts here are new builds addressing the actual capability gap.

## Input boundaries

- `-ConfigFile` — connection/authentication context only.
- `-AgentPath` / `-FolderSiteRelativePath` — explicit target, no default.
- **Read-only** — neither script performs any tenant write.

## Scripts

- `../../scripts/configure-sharepoint-agent-knowledge.ps1`
- `../../scripts/get-agent-resource-identifiers.ps1`

## Tests

No executable tests — both scripts require a live tenant connection with no dry-run mode
possible for a pure read query (consistent with this plugin's other tenant-diagnostic scripts,
e.g. `diagnose-sharepoint-library.ps1`, which also has no executable test suite).

