# Digging to Root Cause — Without Landing on a Person

The Root Cause section fails in two directions: stopping too early ("the deploy broke it") or landing on a human ("engineer pushed without testing"). This reference is the digging technique and the language that keeps the analysis systemic.

## Five whys, done properly

Ask "why" until the answer is a *system property someone can change* — then ask once more.

> Checkout was down 40 minutes.
> **Why?** The payments service OOM-crashed.
> **Why?** A deploy doubled per-request memory.
> **Why did that reach production?** Load tests don't measure memory, only latency. ← *first system gap*
> **Why don't they?** The perf suite was built for a latency SLO; memory was never a stated concern. ← *root cause candidate*
> **Why 40 minutes?** The OOM alert paged, but the runbook didn't cover this failure mode. ← *a second, independent chain*

Rules that make it work:
- **Stop at changeable-system-property, not at "human error".** A person appearing in the chain is a signpost, not a destination — ask *why the system let that action have that consequence*.
- **Branch, don't force one chain.** Real incidents have 2-3 independent chains (cause, detection, response). Follow each; they produce different action items.
- **"Why did our safeguards not catch it?" is mandatory.** If the answer is "we had none for this class," that's the finding. If "we had one and it didn't fire," dig into that as its own chain.
- **Beware the plausible first answer.** "Config change caused it" is a *trigger*. The root cause is whatever made a config change capable of taking production down unreviewed.

## Contributing-factor taxonomy

Sweep these categories so factors don't get missed — most incidents have one from each row:

| Category | Prompt |
|---|---|
| Change management | What changed, and what review/canary/rollback did the change path lack? |
| Detection | What signal existed but wasn't alerted on? What alert existed but was tuned wrong / ignored as noisy? |
| Knowledge | What did responders have to figure out live that a runbook/diagram should have held? |
| Design | What single point of failure, missing limit, or absent degradation mode turned a fault into an outage? |
| Process/pressure | What deadline, on-call gap, or ownership ambiguity shaped the human decisions? |

## Blameless language rewrites

| Blame-shaped | Systemic |
|---|---|
| "X deployed without running tests" | "The deploy pipeline allows promotion without the integration suite passing" |
| "The on-call missed the alert" | "The alert fired into a channel that averages 40 notifications/hour" |
| "Y misconfigured the load balancer" | "Load-balancer config has no validation or peer-review step before apply" |
| "The intern dropped the table" | "Production credentials permitted destructive DDL from a developer workstation" |
| "Support didn't escalate fast enough" | "Escalation criteria for this failure class weren't defined, so severity was judged ad hoc" |

The rewrite test: could the sentence still be true with a different person in the seat? If renaming the human fixes nothing, the sentence is about the system — which is the one you can repair.

## From chains to action items

Each why-chain should emit at most 1-2 actions at the *deepest changeable* point — not one action per "why". Fixing the deepest point usually obsoletes the shallower ones; if it doesn't, the shallow fix (e.g. "add the missing alert") is a separate *detection* item, and both are worth keeping.
