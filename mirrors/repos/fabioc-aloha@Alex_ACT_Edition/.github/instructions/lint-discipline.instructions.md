---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Fix lint always — if I edited a file, I own its lint state on exit, even for pre-existing findings"
application: "Whenever get_errors or a linter reports findings in a file I touched in the current change"
applyTo: "**"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Lint Discipline

If I edited a file, I own its lint state on exit. Pre-existing findings are not an excuse — once I touch a file, every reported error in it is mine to fix in the same change.

## Rule

When `get_errors` (or any linter) reports problems in a file I modified this turn:

1. Fix every reported error before declaring the change done.
2. Do not write "pre-existing, not my edit" or "out of scope" as a reason to leave a finding.
3. If a fix is genuinely risky or out of scope, **name the risk and ask** — do not silently ship with a disclaimer.

The user reads my touch on the file as ownership. That contract is not negotiable on a per-finding basis.

## Why

Lint findings degrade silently. Each "not mine" leaves a longer tail for the next edit. The cheapest moment to fix a finding is when the file is already open and the context is already loaded — this turn.

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| "That MD060 isn't from my edit" | Fix it. One-character delimiter spacing. |
| "Pre-existing in the file" | Pre-existing is exactly when it's cheapest to fix. |
| "Out of scope" on a one-line lint fix | Out of scope means architectural change. Lint isn't that. |
| Shipping with a disclaimer ("known issue") | Either fix it, or name the specific risk and ask. |

## Trigger Origin

Burned in 2026-04-30 on a changelog edit that shipped with 10 MD060 findings called "pre-existing." User pushback: "NEVER. fix lint even if its not yours." Fixed in a follow-up commit. The follow-up should not have been needed.
