# The 3AM Test: Runbooks for Degraded Humans

A runbook's reader is stressed, half-awake, and possibly seeing this system for the first time. Every writing rule follows from that reader — write for the worst plausible operator, because that's who's on call when it matters.

## The rules

1. **Diagnosis before action.** The #1 runbook failure is assuming the diagnosis. Open with "how to confirm you're in THIS failure" — the 2-3 checks (exact commands, expected outputs shown) that distinguish this incident from its lookalikes. A runbook without a confirmation step causes confident wrong treatment.
2. **Exact commands, expected output, no placeholders requiring thought.** `kubectl get pods -n payments | grep -c Running` with "expect: 12" — not "check the pods are healthy". Every `<FILL_ME>` at 3am is a coin flip; pre-resolve what can be pre-resolved and link a lookup for the rest.
3. **Decision points as explicit forks.** "If output is A → step 4. If B → step 7. If neither → escalate (below)." Prose that embeds branching logic gets misread; make the tree visible.
4. **Escalation is a first-class path, not an admission of failure.** Every runbook states: when to stop self-serving (time-boxed: "if not resolved in 20 min"), who to page (role + how), and what to have ready when they answer. Runbooks without escalation timing produce heroes at hour three of a ten-minute problem.
5. **State the blast radius of every remediation.** "This restarts the worker pool: in-flight jobs (~2 min of work) will retry; user impact none / brief 500s." An operator who doesn't know the cost of the fix will either fear it or fire it blind.
6. **Verify at the END, explicitly.** "Resolved" means the confirmation checks now pass AND the user-facing symptom is gone — list both. Many incidents get "fixed" into a quieter failure mode.

## Freshness or danger

A stale runbook is worse than none — it commands confident wrong actions. Mechanics that work: `last-verified: [date] by [name]` at the top (staleness visible at a glance) · runbook review as a standing post-incident action ("did the runbook work? fix it NOW while the pain is fresh") · game-day exercises that execute runbooks verbatim, no improvisation allowed — where the operator improvised, the runbook lied.
