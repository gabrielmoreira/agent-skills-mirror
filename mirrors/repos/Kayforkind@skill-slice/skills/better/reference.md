# /better — scorecard template

Copy into the session. Rank 1 = fix first.

| Rank | Gap | Impact (user-visible / correctness / craft) | Fix |
|------|-----|-----------------------------------------------|-----|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## Fan-out (load only if the gap matches)

| Gap class | Load |
|-----------|------|
| Mush / filler | `deslop` under cursor-team-kit `skills\` (latest hash) |
| “Does this hold?” | `verify-this` same kit |
| TS/JS errors after edit | `check-compiler-errors` same kit |
| UI behavior | `control-ui` / project UI verify |
| Sensory pack | `/reviewresults` (`review-results`), not this skill |
| `/better ship` | Bugbot; security-review if auth/money/secrets/PII |

Plugin skills live under `~\.cursor\plugins\cache\cursor-public\cursor-team-kit\` — **latest** hash folder `skills\`. Do not pin a stale hash.

## Verdicts

| Tag | Meaning |
|-----|---------|
| `improved` | Top gaps moved; verify ran; remaining is named |
| `partial` | Some gaps blocked (deps, missing gold, unpaid API) |
| `blocked` | Cannot improve honestly — say why |
