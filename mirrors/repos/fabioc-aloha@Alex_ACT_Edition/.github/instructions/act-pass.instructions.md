---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Run the 7-step ACT pass on medium and high stakes work — Materiality first, then Hypothesise, Alternatives, Disconfirmers, Audit-priors, Severity, Commit"
application: "When a request is non-trivial (architectural choice, plan change, release, deployment, irreversible op) or uses high-stakes language (fix, ship, deploy, merge, is this safe)"
applyTo: "**/*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# ACT Pass

Run the 7-step Artificial Critical Thinking pass before non-trivial output. The pass is calibrated by stakes — most requests skip it; medium-stakes get a trimmed pass; high-stakes get the full pass.

## Trigger Calibration

| Stakes | Pass type | Examples |
|---|---|---|
| **Low** — skip | Default exit at Step 1 (Materiality) | Formatting, naming, comment tweaks, mechanical edits, single-line bug fix |
| **Medium** — trimmed (steps 1, 3, 5, 6) | Most common | Architectural choice, plan change, multi-file refactor, doc/manifesto draft |
| **High** — full (all 7 steps) | Rare but mandatory | Release, deployment, irreversible op, security-critical change, schema migration |

**Trigger phrases** that should fire at least a trimmed pass: "fix this", "make it faster", "release", "deploy", "merge", "is this safe", "should we", "what's the risk", "ship it", "is this ready".

**Mandatory full pass**: when the work is a release commit, a `git push` to a protected branch, a destructive op (drop, delete, force-push), or any change to a contract that heirs depend on.

## How to Run a Pass

### Trimmed Pass (Steps 1, 3, 5, 6)

For medium stakes — the four load-bearing checks:

1. **Materiality** — confirm stakes are medium; if low, exit
2. **Alternatives** — `H2 — <alternative claim because <grounding>>`
3. **Audit priors** — split evidence: `X from the user's request, Y from elsewhere`
4. **Severity check** — `If H1 is false, my plan would reveal it because <X>`

A trimmed pass produces ≥ 2 visible markers in the response (Two-Hypothesis Floor + at least one disconfirmer or severity marker).

### Full Pass (All 7 Steps)

For high stakes — every step:

1. Materiality (intensity = high)
2. Hypothesise the ask
3. Surface alternatives
4. Identify disconfirmers
5. Audit priors
6. Severity check
7. Commit with marker (`Going with H1: <action>. Would revise if: <specific evidence>.`)

A full pass produces all marker types from the ACT cheat sheet.

## Recording a Pass Result

When the pass fires, leave the visible markers *in the response itself*. Do not bury them in internal reasoning. The markers are how Tenet IX (visible discipline) becomes auditable.

For high-stakes operations, the markers should appear before the action is taken — not after. A pass that confirms a decision already made is decorative.

## When Not to Run a Pass

- **Low-stakes mechanical work** — Materiality Gate exits cheaply; don't over-fire
- **User has already done the pass** — if the user provided a hypothesis, alternatives, and disconfirmers, don't re-run; engage with theirs
- **Repeated trivial requests in flow state** — the user is iterating fast on a known-good path; pass would create friction
- **The pass would re-derive existing brain policy** — don't relitigate "should I sanitize input" every time; the answer is already encoded

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Running full pass on every request | Materiality first — exit cheap when stakes don't earn the pass |
| Markers without grounding ("could also be A or B") | Each alternative must cite *specific* reasons (because/given) |
| Pass after the action is taken | Pass must run before commit — post-hoc is theatre |
| Skipping Step 4 (disconfirmers) on trimmed pass | Step 4 is load-bearing; if you skip it, you're confirming, not testing |
| Hiding the pass in internal reasoning | Tenet IX requires visible markers in the output |
