---
name: obsidian-wiki-ingest
description: >
  Automates ingestion of documents into the Obsidian wiki (obsidian-wiki) using the wiki-ingest pipeline. Handles deduplication via manifest, frontmatter, and cross-links; triggers on user request within the obsidian-wiki project context.
---

# Obsidian Wiki Ingest — Automation Skill

You are the automation layer that ingests documents into the Obsidian wiki project. This skill orchestrates the ingestion workflow, ensuring deduplication, proper frontmatter, and cross-linking with existing pages.

## Trigger
- User says: "ingest to wiki", "add to wiki", or any phrasing that targets the obsidian-wiki repository.
- Context: active in the /home/ubuntu/projects/obsidian-wiki workspace.

## Responsibilities
- Validate target vault path from the environment and manifest state.
- Decide between Append, Full, or Raw ingest modes based on user input or changes in the source.
- Invoke the wiki-ingest workflow to process new/modified sources.
- Update manifest and log files with ingest metadata.
- Create or update project overview pages and cross-links as needed.

## Inputs
- Source documents (Markdown, PDFs, text, images) from OBSIDIAN_SOURCES_DIR or _raw/
- Vault path from OBSIDIAN_VAULT_PATH
- Optional: ingest mode (append|full|raw)

## Outputs
- Updated wiki pages with distilled knowledge
- Updated .manifest.json and log entries
- Optional: new/updated project overview pages

## Probing and Safety
- Do not ingest secrets or sensitive data.
- Respect existing page structure and avoid duplicating content.
- Mark inferred/ambiguous knowledge with provenance notes.

## Example Workflow (high level)
1) Determine ingest mode and target paths
2) Run wiki-ingest with the chosen mode
3) Update manifest/log and refresh wiki index
4) Return a brief summary of changes

## Next Steps
- If you approve, I’ll create a small wrapper script (scripts/ingest-wiki.sh) that kicks off the ingest for the current project and updates the manifest. Then wire a simple command alias to trigger this skill from the CLI.

## QMD Refresh After Vault Writes

QMD is a search index, not the source of truth. If `$QMD_WIKI_COLLECTION` is empty or unset, skip this step. Run it only after this skill has written or rewritten vault markdown. If QMD refresh fails, do not roll back the vault changes; report the QMD status separately.

Use `$QMD_CLI` if set; otherwise use `qmd`.

```bash
${QMD_CLI:-qmd} update
```

If the output says vectors are needed or embeddings may be stale, run:

```bash
${QMD_CLI:-qmd} embed
```

Verify the collection with either:

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

or, when a specific page path is known:

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

Record one of:
- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <short error summary>`