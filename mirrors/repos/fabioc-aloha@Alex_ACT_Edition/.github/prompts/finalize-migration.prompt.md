---
description: "Finalize a heir migration to Alex_ACT_Edition — semantic pass over the .github-old-*/ snapshot to port custom content into local/ slots and identity into copilot-instructions.local.md"
mode: agent
lastReviewed: 2026-04-30
---

# Finalize Migration

Run after `migrate-to-edition.cjs --apply` has completed. The script does the mechanical work (snapshot, fresh Edition install, marker, registry); this prompt does the semantic work that requires judgment.

## Pre-flight

1. Confirm the heir is on Edition: read `.github/.act-heir.json` — must exist and have `edition_version`.
2. Find the snapshot: `Get-ChildItem .github-old-*` — there must be exactly one. If zero, migration didn't run. If multiple, ask the user which one to finalize.
3. Run `node .github/muscles/heir-doctor.cjs` — should exit 0. If not, stop and ask the user to fix the warnings before proceeding.

## Pass 1 — Identity Extraction

The old `.github-old-*/copilot-instructions.md` mixed identity (project context, persona, preferences) with architecture (cognitive directives, skill routing). Edition split these: architecture lives in `.github/copilot-instructions.md` (edition-owned), identity lives in `.github/copilot-instructions.local.md` (heir-owned).

1. Read both:
   - `.github-old-*/copilot-instructions.md` (old, mixed)
   - `.github/copilot-instructions.md` (new, architecture only)
2. For each section in the old file, classify:
   - **Identity** (project context, domain vocab, persona, user preferences, North Star, constraints) → port to `copilot-instructions.local.md`
   - **Architecture** (skill routing rules, meta-cognitive protocols, safety imperatives) → drop, Edition has its own
   - **Mixed** → split, port only the identity portion
3. Append the ported sections to `.github/copilot-instructions.local.md` under the existing template headings (Project Context, Domain Vocabulary, My Preferences, Constraints). Don't overwrite the template — merge into it.
4. Show the diff to the user before writing.

## Pass 2 — Custom Content Port

Anything in the snapshot that's not in Edition is custom and belongs under `local/`. The migration script's triage table is the inventory.

For each file the script flagged as "port to local/":

| Old path | New path |
|---|---|
| `.github-old-*/instructions/<name>.instructions.md` | `.github/instructions/local/<name>.instructions.md` |
| `.github-old-*/skills/<name>/` | `.github/skills/local/<name>/` |
| `.github-old-*/prompts/<name>.prompt.md` | `.github/prompts/local/<name>.prompt.md` |
| `.github-old-*/muscles/<name>.cjs` | `.github/muscles/local/<name>.cjs` |

For each file:

1. Read it. Decide if it's still relevant. (Old custom content sometimes targets removed primitives — agents, hooks, extension UI. Drop those.)
2. If frontmatter has `inheritance: custom` or similar, strip it — Edition uses path-based ownership.
3. If it references `.github/agents/`, `.github/hooks/`, or extension-only configs (`loop-menu.json`, `taglines.json`, etc.), either fix the references or drop the file.
4. Copy to the `local/` destination.
5. If it's a muscle that other content references by path, update those references in the ported files.

## Pass 3 — Review Bucket

The script's triage table has a "review" bucket for files it couldn't confidently classify. For each:

1. Read the file. Decide: keep (port to `local/`), drop (extension-only or obsolete), or archive (interesting but no current use).
2. Document the decision briefly in the migration commit message so future-you knows why.

## Pass 3.5 — Episodic Memory

`.github/episodic/` is heir-owned by definition: meditations, post-mortems, calibration logs are all heir-specific writing.

1. Check `.github-old-*/episodic/` for any non-template files (anything beyond `INDEX.md`, `README.md`, `calibration-log.md`).
2. Copy heir-authored episodic files (meditations, dream reports, project-framing docs) to `.github/episodic/`, preserving filenames.
3. Do NOT skip this step. Episodic content is irreplaceable institutional memory.

## Pass 4 — Verification

1. Run `node .github/muscles/heir-doctor.cjs` — must exit 0.
2. Run `node .github/scripts/upgrade-self.cjs` (dry-run) — confirm your `local/` files appear in the "heir-owned files to recover" count, not in the "relocations" list. If relocations include files you already placed in `local/`, something is mispathed.
3. Spot-check a session: ask the AI a domain-specific question that the ported instructions should answer. Confirm the routing works.

## Pass 5 — Commit

```bash
git add -A
git commit -m "Migrate to Alex_ACT_Edition" \
  -m "" \
  -m "Mechanical: migrate-to-edition.cjs (snapshot in .github-old-*)" \
  -m "Semantic: identity extracted to copilot-instructions.local.md" \
  -m "Semantic: <N> custom files ported to .github/*/local/" \
  -m "Dropped: <list any notable extension-only files>"
```

Keep `.github-old-*/` in the commit. Delete it in a separate commit a week or two later, once you're confident nothing was lost.

## Anti-patterns

- **Don't restore wholesale**: the snapshot is a reference, not a starting point. Most of it is replaced or obsolete.
- **Don't restore agents or hooks**: Edition has no agent or hook primitive. Anything you depended on, port the *content* into a `prompts/local/*.prompt.md`.
- **Don't keep old `inheritance:` frontmatter**: it's meaningless in Edition's path-based model and confuses readers.
- **Don't skip Pass 4 verification**: silent path mistakes (missing `local/` segment) only surface on the next `upgrade-self.cjs` when your custom file gets relocated instead of recovered in-place.
