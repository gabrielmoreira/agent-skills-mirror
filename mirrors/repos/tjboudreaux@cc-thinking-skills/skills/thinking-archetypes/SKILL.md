---
name: thinking-archetypes
description: Use when the same problem keeps recurring despite fixes, growth stalled with no obvious cause, or a quick fix made things worse—match it to a known structural pattern instead of re-diagnosing.
---

# Systems Archetypes

## Overview

Systems archetypes (Peter Senge, "The Fifth Discipline") are recurring structural patterns. Like design patterns in software, once you recognize one you can predict where it leads and where to intervene. Most stubborn, recurring problems aren't unique—they're an instance of a known pattern, and the pattern names the leverage point.

**Core Principle:** A recurring problem usually has a structural pattern. Match the pattern and the intervention follows.

## Trigger Card

When the same problem keeps recurring despite multiple fixes:

1. **Describe the problem neutrally** — symptoms, what's been tried, what keeps coming back.
2. **Match to an archetype** using the Quick Reference Card below (Fixes That Fail, Shifting the Burden, Limits to Growth, Tragedy of the Commons, Escalation, Success to the Successful, Growth and Underinvestment).
3. **Intervene at the structure, not the symptom** — use the Key Question for that archetype.

If no archetype fits after a genuine look, don't force one — drop to `thinking-systems` and map from scratch. For a first-time one-off problem, just fix it.

## When to Use

- The same problem keeps recurring despite multiple "fixes"
- A quick fix made things worse over time
- Growth stalled without an obvious cause
- A shared resource (CI, staging, a cache, a service quota) keeps degrading
- Two efforts are escalating against each other (duplicated services, alert/threshold arms races)

```
Problem keeps recurring despite fixes?  → match an archetype
Quick fix made it worse?                → match an archetype
Growth hit an invisible ceiling?        → match an archetype
Shared resource degrading?              → match an archetype
```

## When NOT to Use

- **You need to map the system from scratch** (components, interactions, emergent behavior) — use `thinking-systems` instead. Archetypes are pattern-matching shortcuts for recurring structures; if the system is unfamiliar, map it first, then see if an archetype fits.
- **You've found the pattern and need to know where to intervene** — use `thinking-leverage-points` (Meadows' hierarchy). Archetypes name the structure; leverage-points tell you where in that structure to act for maximum effect.
- A first-time, one-off problem with a clear cause → just fix it; there's no recurring structure to match.
- No candidate archetype fits after a genuine look → don't force one. Drop to `thinking-systems` and map the actual structure from scratch.
- You need to localize a specific faulty codepath → use a hypothesis differential, not pattern-matching.

## Quick Reference Card

Match the symptom to the pattern; the Key Question points at the leverage.

| Archetype | Structure | Recognize it by | Key Question (leverage) |
|-----------|-----------|-----------------|-------------------------|
| **Fixes That Fail** | Quick fix relieves symptom but a delayed side effect makes it worse | "We fixed this last quarter, why is it back?"; the fix needs ever-larger doses | "What side effect will this fix create?" |
| **Shifting the Burden** | A symptomatic workaround is used instead of the fundamental fix, creating dependency | Permanent workarounds; "we know the real fix but have no time"; the real capability is atrophying | "What capability are we not building by leaning on this workaround?" |
| **Limits to Growth** | A reinforcing growth loop hits a balancing constraint | Strong growth that plateaued; more effort, diminishing returns; a resource maxed out | "What will limit us at 10x scale?" |
| **Tragedy of the Commons** | Each actor gains by using a shared resource; collective overuse depletes it | Shared CI/staging/cache/quota degrading; everyone optimizes locally; no clear owner | "Who owns the long-term health of this resource?" |
| **Escalation** | Two parties react to each other's moves in a competitive spiral | "They did X so we must do Y"; arms-race dynamics; each side feels defensive | "Can we change the game instead of playing it harder?" |
| **Success to the Successful** | Initial success grants more resources, compounding advantage and starving alternatives | Past success is the main predictor of new investment; experiments starved to feed the incumbent | "Are we starving future successes to feed current ones?" |
| **Growth and Underinvestment** | Demand grows toward a limit; capacity investment is delayed until performance degrades into crisis | Reactive investment after the incident; chronic "good enough for now" | "What fails if we grow 50% without adding capacity now?" |

## Software Examples (per archetype)

- **Fixes That Fail:** Adding servers to mask a memory leak → cost spirals, leak remains. Silencing alerts → system degrades until outage.
- **Shifting the Burden:** Ops manually intervening forever instead of automating; feature flags hiding bugs that never get fixed.
- **Limits to Growth:** Velocity drops as the codebase grows (complexity limit); adding engineers doesn't speed delivery (coordination overhead).
- **Tragedy of the Commons:** Teams overload shared CI → everyone's builds slow; cloud costs spike as nobody cleans up resources.
- **Escalation:** Microservice teams duplicating functionality in response to each other; ever-stricter alert thresholds chasing each other.
- **Success to the Successful:** Legacy monolith gets all attention so the new architecture never matures.
- **Growth and Underinvestment:** Database not upgraded until it crashes under load; security investment only after a breach.

## Diagnosis Process

1. **Describe the problem neutrally** — symptoms, who/what is involved, what's been tried, what keeps recurring. No blame.
2. **Sketch the loops** — what causes what; where reinforcing (amplifying) loops are, where balancing (limiting) loops are, and where the delays sit.
3. **Match to an archetype** using the Quick Reference Card. If two fit, the system may be layered—note both.
4. **Intervene at the structure, not the symptom** — use the Key Question to find the fundamental solution, the constraint to remove, or the missing/ delayed feedback to add. If none match, stop and use `thinking-systems`.

## Verification Checklist

- [ ] Problem described without blame
- [ ] Loops sketched (reinforcing, balancing, delays)
- [ ] Matched to a specific archetype (or escalated to `thinking-systems` because none fit)
- [ ] Intervention targets structure, not the recurring symptom
- [ ] Considered the side effects of the intervention

## Senge's Wisdom

"Structures of which we are unaware hold us prisoner. Once we can see them, they no longer have the same hold on us."

The pattern continues until someone sees it and changes the structure driving it—not the behaviors, but what produces them.
