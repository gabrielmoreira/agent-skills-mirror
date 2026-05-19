---
description: "Read-only audit of user-level VS Code/Copilot settings compliance"
mode: agent
lastReviewed: 2026-05-18
---

# Welcome Verify

Use this to verify fleet policy compliance on a machine without changing any settings.

## Objective

Audit user-scope VS Code settings against the central baseline and report drift.

## Source of truth

The baseline lives in `.github/config/welcome-baseline.json` (`settings` object). Both `/welcome` (apply) and `/welcome-verify` (this audit) load from the same file — update once.

## Read-Only Steps

1. Load the baseline from `.github/config/welcome-baseline.json` (`settings` object).
2. Resolve the user settings path for the current OS.
3. Read `settings.json` as-is.
4. Compare each baseline key/value pair.
5. Classify each key:
   - `compliant` (value matches)
   - `drift` (key exists but value differs)
   - `missing` (key absent)
6. Report compliance summary and drift table.
7. Recommend running `/welcome` only if drift or missing keys are found.

## Output Format

```text
Compliance: <X>/<N> keys
Drift: <count>
Missing: <count>

Drifted keys:
- key: expected=<...>, actual=<...>

Missing keys:
- key: expected=<...>

Recommendation:
- No action required | Run /welcome to apply baseline
```

## Guardrails

- Do not modify files.
- User-scope only (never evaluate workspace `.vscode/settings.json` for policy compliance).
- Treat unknown extra keys as informational only, not non-compliance.
