# Runbook: [failure mode, specific — "payments-api elevated 5xx", not "payments issues"]

**Severity when firing:** [P1/P2] · **Last verified:** [date] by [name] · **Owner:** [team]

## Confirm you're in THIS failure (before acting)
1. `[exact command]` → expect: `[output]`
2. `[exact command]` → expect: `[output]`
*If these don't match → you're in a different incident: see [lookalike runbook links].*

## Impact while firing
[who/what is degraded, in user terms]

## Remediation
**Step 1 — [name]**
```
[exact command]
```
Expect: `[output]` · Blast radius: [what this restarts/loses/risks]
**If A → step 2. If B → step 4. Neither → escalate now.**

*(continue, every fork explicit)*

## Escalate (a path, not a failure)
- Time-box: if not resolved in [n] min → page [role] via [how]
- Have ready: [the outputs from the confirm step + what you tried]

## Verify resolution (both required)
- [ ] Confirmation checks now pass: [which]
- [ ] User-facing symptom gone: [how checked]

## After
Log to [incident channel] · If this runbook lied anywhere, fix it NOW: [edit link]
