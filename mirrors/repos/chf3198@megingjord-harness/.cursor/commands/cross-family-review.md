---
name: "cross-family-review"
description: "Dispatch cross-family adversarial review at lifecycle points L2-L4."
argument-hint: "[ticket:#N] [--lifecycle L2|L3|L4] [--model qwen2.5-coder:32b|7b]"
---

# Cross-Family Review (Cursor)

Required **before COLLABORATOR_HANDOFF** (L2). See `skills/cross-family-review/SKILL.md`.

```bash
node scripts/global/fleet-red-team-dispatch.js \
  --artifact-type collaborator-handoff --ticket <N> \
  [--model qwen2.5-coder:32b|qwen2.5-coder:7b]
```

Or preflight bundle (lint + tests + changelog + receipt):

```bash
node scripts/global/collaborator-preflight.js --ticket <N> \
  --diff-files=<comma-separated paths>
```

Paste emitted `cross_family_*` + `cross_family_receipt:` into COLLABORATOR_HANDOFF.
Reviewer family MUST differ from Cursor (`cursor` / Anthropic-derived models).
