# Asset rights and provenance

Use this reference for generated, purchased, commissioned, open, or remixed assets. This is a
production recordkeeping workflow, not legal advice.

## Record per shipped asset

- stable asset ID and repository path
- creator/source URL or vendor order
- acquisition or generation date
- source tool/model/version when generated
- original prompt/reference IDs when available
- license name/version and a saved copy or link to the terms
- attribution text and placement requirements
- whether commercial use, modification, redistribution, or AI training is restricted
- edits, derivatives, and the person/tool responsible
- approval status and reviewer

The bundled `assets/asset-manifest.json` has fields for these records. Keep proof of purchase and
license snapshots outside a public repository when they contain personal or account data.

## Decision rules

1. Do not treat “free,” “royalty-free,” search-engine-visible, or model-generated as a license.
2. Verify terms at the original source, not a repost or aggregator preview.
3. Keep attribution through atlas packing, renaming, conversion, and derivative edits.
4. Check whether a marketplace license permits redistribution of raw source files; shipping a game
   and publishing editable source assets can have different permissions.
5. Do not request direct imitation of a living artist. Describe visual properties or use references
   the project has permission to edit.
6. Preserve content credentials/provenance metadata where the file pipeline supports it. If
   optimization strips metadata, retain the corresponding manifest record.
7. Review each store/platform's current disclosure rules before submission; rules change faster
   than this skill.

## Useful primary references

- [Creative Commons license chooser](https://creativecommons.org/chooser/)
- [SPDX license list](https://spdx.org/licenses/)
- [OpenAI content provenance](https://openai.com/index/advancing-content-provenance/)
- [Steamworks documentation](https://partner.steamgames.com/doc/home)

When terms are unclear or the release is commercially important, flag the ambiguity for a human
rights review rather than guessing.
