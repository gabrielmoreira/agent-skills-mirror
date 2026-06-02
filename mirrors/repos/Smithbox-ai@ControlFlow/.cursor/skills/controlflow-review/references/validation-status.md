# Validation Status Labels

## confirmed

- Use when you verified the problem directly from code, tests, or command output.
- These are the strongest candidates for blocking findings.

## likely

- Use when the reasoning is strong, but you did not fully reproduce or execute it.
- Good for advisory or near-blocking issues when evidence is still concrete.

## unvalidated

- Use when the concern is plausible but not yet proven.
- State what would validate it. Do not present these as blockers unless the risk is extreme and clearly explained.
