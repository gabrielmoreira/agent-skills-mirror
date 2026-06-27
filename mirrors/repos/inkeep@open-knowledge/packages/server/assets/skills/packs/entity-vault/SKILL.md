---
name: open-knowledge-pack-entity-vault
version: "0.18.0"
description: "How to work in an Entity vault project (the `entity-vault` starter pack, GBrain-compatible): a typed-entity vault of people, companies, meetings, and concepts, each a dossier with a rewritable summary plus an append-only timeline. Read when the project has these folders. Carries the dossier convention and entity-extraction behaviors so that guidance does not live inside template bodies or folder descriptions. Complements the platform `open-knowledge` skill; does not replace it."
compatibility: "Claude Code, Claude Desktop, Claude Cowork, Claude.ai web. Requires OpenKnowledge MCP server. Installed project-local by `ok seed --pack entity-vault`."
metadata:
  pack: "entity-vault"
  author: "Inkeep"
  repository: "https://github.com/inkeep/open-knowledge"
---
# Entity vault pack (GBrain-compatible) — how to work here

A typed-entity vault inspired by Garry Tan's gbrain. Each entity is a dossier; the agent keeps dossiers current by extracting entities from meeting notes and original thinking. This skill holds those behaviors so templates and folder descriptions stay clean. The Markdown shape is **GBrain-compatible**: if the external `gbrain` CLI is installed, it can import/sync the same vault.

> Pack guidance. The platform `open-knowledge` skill still governs every markdown operation.

## The dossier convention (the load-bearing rule)

Every dossier in `people/`, `companies/`, and `concepts/` has two parts, split by an explicit `--- timeline ---` separator:

1. **Compiled truth** (above `--- timeline ---`) — your current best understanding. Rewrite it as new evidence changes the synthesis.
2. **Timeline** (below `--- timeline ---`) — append-only dated bullets in the parseable form `- **YYYY-MM-DD** | source | @author — evidence. Confidence: …`. **Never edit existing timeline entries; only append.**

When a new fact arrives, route it: update **compiled truth** if it changes current understanding, or append a timeline bullet if it's raw evidence. The explicit separator and dated-bullet shape are what keep the vault parseable by GBrain's import/sync.

## Folders

- **`people/`**, **`companies/`**, **`concepts/`** — dossiers (compiled truth + timeline). Frontmatter `type: person|company|concept`.
- **`meetings/`** — meeting notes (`YYYY-MM-DD-<slug>.md`); `attendees:` should match dossier filenames in `people/`. The verbatim record — do NOT rewrite it.
- **`originals/`** — your own untransformed thinking; authoritative source material. Frontmatter `type: original`.
- **`media/`** — bulk transcripts, voice notes, large attachments; often `.okignore`-d to keep the index light.

## Links

Prefer path-qualified wikilinks when entity identity matters: `[[companies/acme|Acme]]`, `[[people/jane-founder|Jane Founder]]`, `[[concepts/agent-runtime-observability|agent-runtime observability]]`. Path-qualified links resolve to the right dossier under GBrain's typed extraction.

## Agent behaviors

- After a meeting note lands, extract entity mentions and append timeline bullets to each referenced dossier (cite the meeting by markdown link). Stub any mentioned entity not yet captured.
- Treat `originals/` as authoritative (the user's own words, not inferences).
- Surface entity-to-entity edges (person ↔ company, concept hubs) when both ends exist.

## gbrain CLI (optional)

This pack ships the Markdown half (folders + templates + this skill); OK is the cockpit/editor/review layer. If the external `gbrain` CLI is installed (`~/.gbrain/`), it adds scheduled enrichment: `gbrain dream` (nightly maintenance), `gbrain briefing`, `gbrain soul-audit`, and `gbrain import`/`gbrain sync --repo` for DB-backed indexing. The root files (`USER.md`, `SOUL.md`, `ACCESS_POLICY.md`, `HEARTBEAT.md`) are read by those skills; fill them in by hand or via `gbrain soul-audit`. None of it is required to use the vault — interop is plain Markdown + Git.

## Templates

Create with `write({ document: { path: "<path>", template: "<name>" } })`. Templates carry the structure (including the compiled-truth / `--- timeline ---` separator) plus short inline reminders at the point of use; this skill holds the full convention, so prefer it as the canonical reference if the two ever disagree.
