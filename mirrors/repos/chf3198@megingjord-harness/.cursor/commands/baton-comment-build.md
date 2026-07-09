---
name: "baton-comment-build"
description: "Generate structured markdown for baton handoff comments."
argument-hint: "--artifact <MANAGER_HANDOFF|COLLABORATOR_HANDOFF|ADMIN_HANDOFF|CONSULTANT_CLOSEOUT> --role <role> --ticket <N> --team-model cursor:<model>@cursor-ide"
---

# Baton Comment Build

```bash
node scripts/global/baton-comment-build.js \
  --artifact <artifact> --role <role> --ticket <N> \
  --team-model cursor:<model>@cursor-ide \
  [--fields-json <file.json>]
```

Structured path: `node scripts/global/baton-artifact-builder.js` via `--fields-json`.
See `.cursor/rules/baton-handoff.mdc` for Cursor-specific required fields beyond the builder schema.
