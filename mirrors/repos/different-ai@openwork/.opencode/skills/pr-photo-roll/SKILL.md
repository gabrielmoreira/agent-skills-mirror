---
name: pr-photo-roll
description: Post the photo roll, put the screenshots on the PR, or show me the photo roll. Curate recorded eval screenshots and publish one sticky PR gallery.
---

# PR photo roll

Use this skill when asked to "post the photo roll", "put the screenshots on the PR", or "show me the photo roll".

## Choose the evidence

1. Scan `evals/results/rolls/` newest-first and read each candidate's `roll.json`.
2. Pick the newest roll relevant to the requested spec or change.
3. Only publish images attributed by that roll's `roll.json`; never add loose screenshots by hand.
4. Publish at most one roll per PR comment.
5. If more than one roll is plausibly relevant, ask which roll to use.

## Commands

Browse the local collection:

```bash
pnpm --dir evals run roll -- --open
```

Publish the newest roll, or select one by directory/name:

```bash
pnpm --dir evals run publish:pr -- --pr <n> [--roll <dir|name>] [--dry-run]
```

The publisher reads `BLOB_READ_WRITE_TOKEN` from the environment, then falls back to `infisical secrets get BLOB_READ_WRITE_TOKEN --plain --silent`. Without a token it still posts verdicts, explicitly noting that screenshots were not uploaded.

Publishing creates one comment containing `<!-- photo-roll -->`. Later runs update that sticky comment instead of adding comment noise.
