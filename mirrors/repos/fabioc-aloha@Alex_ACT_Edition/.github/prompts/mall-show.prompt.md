---
description: "Show full metadata + trust signal breakdown for a single Plugin Mall entry"
lastReviewed: 2026-05-29
---

# /mall-show

Show the full metadata + trust signal breakdown for a single plugin from the Mall catalog. Use after `/mall-search` to drill into a specific candidate.

Per [PLAN-mall-automation v3 / ADR-008](https://github.com/fabioc-aloha/Alex_ACT_Supervisor/blob/main/docs/adrs/ADR-008-mall-self-curation.md), the Mall publishes all trust signals alongside every score (trust without provenance is worse than no trust). This prompt is how heirs read those signals.

## Steps

1. **Get the plugin name** from the user. If the name appears in multiple stores (Mall-curated + third-party alternatives), use the same name and disambiguate via the store. The user may have used `--from-store <store>` from `/mall-search` results.

2. **Fetch the catalog** (try in order):
   - **Local clone (fast)**: read `C:/Development/Alex_ACT_Plugin_Mall/catalog/index.json` and the specific `catalog/stores/<store>.json`
   - **GitHub raw (fallback)**:
     - `https://raw.githubusercontent.com/fabioc-aloha/Alex_Skill_Mall/main/catalog/index.json` (to find which stores carry the name)
     - `https://raw.githubusercontent.com/fabioc-aloha/Alex_Skill_Mall/main/catalog/stores/<store>.json` (for full metadata)

3. **Disambiguate** if the name appears in multiple stores:
   - If exactly one match: proceed
   - If multiple: present a table ordered by trust_score and ask the user to pick (`/mall-show <name> --from-store <store>`)

4. **Display the full plugin entry** as a structured report:

   ```text
   🏆 plugin-mall/code-review · trust 94 · v1.0.0 · shape: skill

   Description:
     Systematic code review for correctness, security, and growth — not just style enforcement

   Trust signals (94/100):
     store:           82  (provenance 50 + maintenance 15 + adoption 10 + license 7)
     plugin_frontmatter: 7  (description ✓ + version ✗ + lastReviewed ✓)
     plugin_readme:     5  (README ≥ 50 chars)

   Store signals (plugin-mall, score 82):
     provenance:   50  (first-party Mall-curated)
     maintenance:  15  (continuous curation flow)
     adoption:     10  (fleet's primary marketplace)
     license:       7  (PolyForm-Noncommercial-1.0.0; clear non-permissive)
     contributors:  -   (self-entry; not applicable)
     stars:         -   (self-entry; not applicable)

   Adapted from:
     awesome-copilot/skills/code-review @ v1.0.0
     <link to upstream>
     Adaptation notes: Trimmed Microsoft-specific examples; added falsifiability section.

   Other versions available in the catalog:
     awesome-copilot/code-review @ v1.1.0   (trust 90, upstream newer — not yet adapted)
     composio-awesome.../code-review        (trust 85, alternative author)

   Frontmatter (standard layer):
     name: code-review
     description: Systematic code review for correctness, security, and growth
     version: -
     lastReviewed: 2026-05-26
     shape: skill

   Frontmatter (extended layer):
     applyTo: -
     tools: -
     category: code-quality
     tags: -
     license: -
     requires: -

   Source URL: https://github.com/fabioc-aloha/Alex_Skill_Mall/tree/<sha>/plugins/code-quality/code-review

   Available refs:
     default:     main
     default_sha: <40-char SHA>
     tags:        [list, descending semver]
   ```

5. **Surface next actions**:

   ```text
   To install (when shipped):    /mall-install <name>[@<version>]
   To compare against upstream:  open the source_url
   To switch store:              /mall-show <name> --from-store <other>
   ```

## Key fields to surface

- **`trust_score`** — the headline number (0-100)
- **`trust_signals`** — every signal that fed the score (load-bearing per ADR-008)
- **`adapted_from`** — only on Mall-curated entries; names the upstream + ref the curated version was derived from
- **`frontmatter.standard`** + **`frontmatter.extended`** — normalized fields for portability
- **`frontmatter.raw`** — verbatim source frontmatter, never modified by normalization (use this when the standard/extended layers don't surface a field the user asks about)
- **`available_refs`** — default branch + SHA + tags; what the user can pin with `@<version>`
- **`source_url`** — direct upstream link at the resolved SHA

## Boundaries

- Don't paraphrase the trust signals. The exact numbers and signal names matter — heirs use them to compare entries.
- Don't fabricate `adapted_from` data for third-party entries. The field is populated only for first-party (Mall-curated) entries; third-party entries do not have it.
- Don't suggest the user "trust the Mall recommendation blindly." The published signals are what they should evaluate.

## Would Revise If

By **2026-08-29** (90 days) or sooner:

- Heirs report the trust signal breakdown is unread or unread fields cause confusion ≥3 times in a quarter (display format wrong shape)
- The `adapted_from` field is missing on Mall-curated entries that DO have a clear upstream ≥2 times (Phase 7 backfill incomplete)
- Multi-store disambiguation produces wrong-default selections ≥2 times (resolution rule needs sharpening)
