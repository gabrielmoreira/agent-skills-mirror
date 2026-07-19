---
name: install-verification
description: "Use before claiming that the package can be installed or published. Verifies structure, adapters, schemas, executable scripts, and public-safety boundaries."
---

# Install Verification

Run:

```bash
scripts/verify-package.sh
scripts/public_safety_check.sh
```

Then inspect:

- root `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`;
- `.agents/`;
- `.agentlas/`;
- `.claude/`;
- `codex/`;
- `scripts/install.sh`.

Do not claim completion if any required file is missing.
