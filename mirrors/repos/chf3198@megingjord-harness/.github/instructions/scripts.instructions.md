---
applyTo: "scripts/**"
---

# Scripts Development Instructions

## Shell Scripts (.sh)

- Use `#!/usr/bin/env bash` shebang
- `set -euo pipefail` at top
- Quote all variables: `"$var"`
- Log actions to stdout with timestamps
- Exit codes: 0 success, 1 error, 2 warning

## Node Scripts (.js)

- CommonJS (require/module.exports) for CLI scripts
- Use `process.exit()` codes consistently
- Minimal dependencies — prefer built-in Node modules
- JSON output option for machine parsing

## Deploy Scripts Safety

- Always create backup before overwriting
- Dry-run mode by default (require `--apply` flag)
- Show diff before applying changes
- Log all actions to `scripts/logs/`
