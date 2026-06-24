---
name: thinking-ooda
description: Use under time pressure (incident, outage, debugging a moving target) when you must act before you have certainty—cycle Observe→Orient→Decide→Act on ~70% confidence, then re-observe.
---

# OODA Loop

## Overview
The OODA Loop (Observe, Orient, Decide, Act) is a framework for acting in fast-moving, uncertain situations. The core decision rule: don't wait for certainty—act on the best current understanding, then immediately observe the result and loop again. Speed through the loop beats a perfect plan that arrives too late.

**Core Principle:** Act on ~70% confidence for reversible moves, then re-observe. Cycle faster than the situation changes.

## When to Use
- Incident response and outages
- Debugging a moving target (intermittent failure, ongoing degradation)
- Any time-sensitive decision where the situation is still changing

```
Situation changing rapidly AND need to act before certainty? → yes → APPLY OODA
                                                              → no  → use deliberate analysis / a hypothesis differential
```

## When NOT to Use
- The situation is static and you have time → deliberate analysis beats fast looping.
- The action is irreversible/high-blast-radius → gather more information before acting; 70% confidence isn't enough.
- You can cheaply and directly localize the cause (read the diff/log) → use `thinking-scientific-method` (hypothesis differential) instead of looping in the dark.

## Trigger Card

When under time pressure (incident, outage, debugging a moving target) and you must act before certainty:

1. **Observe** — what is happening right now? Gather the cheapest, highest-signal data available.
2. **Orient** — what does it mean given your mental model? Update the model if the data contradicts it.
3. **Decide** — pick an action on ~70% confidence. Don't wait for 100%.
4. **Act** — execute, then immediately re-observe. The loop is the point; speed beats precision.

If the action is irreversible or high-blast-radius, gather more information before acting. If you can cheaply localize the cause (read the diff/log), use `thinking-scientific-method` instead.

## The Four Phases

### 1. OBSERVE — gather current state fast
- Current metrics, logs, alerts, error rates
- What changed recently (deploys, config, traffic)
- Feedback from your last action
- Cast wide, then narrow as a pattern emerges. Time-box it—don't observe forever.

```
Incident: error rate 10x normal; affects API gateway + user service;
started 5 min ago; a deploy went out 15 min ago; users report login failures.
```

### 2. ORIENT — make sense of it (the critical phase)
Match the observations to a pattern and form a hypothesis. This is where most loops go wrong: don't lock onto the first framing. Hold ≥2 candidate explanations and let new evidence shift you.

```
Pattern resembles last month's connection-pool exhaustion, BUT no DB anomaly this time.
The deploy touched auth rate-limiting.
Hypothesis: rate-limit config is too aggressive.
```

### 3. DECIDE — pick an action under uncertainty
- State the action and the hypothesis it tests.
- 70% confidence now beats 90% too late, for a reversible action.
- Decide what you'll observe next to confirm or refute.

```
Decision: roll back the auth deploy.
Hypothesis: this restores normal error rates.
Will watch: error rate for 2 minutes; fallback = investigate DB connections.
```

### 4. ACT — execute, then immediately re-observe
Execute decisively and go straight back to OBSERVE. The action creates new information; don't wait blindly for it to "settle."

```
Action: roll back deployment/auth-service.
Immediate observe: error rate, response times, 2-minute window.
```

The loop restarts until the system is stable.

## What Speeds the Loop
| Speeds it up | Stalls it |
|--------------|-----------|
| Pre-planned responses for known scenarios | Waiting for certainty (stuck at Observe/Decide) |
| Good observability (fast, trustworthy signals) | Information overload (Observe never ends) |
| Clear hypotheses (fast Orient) | Locking onto one hypothesis (Orient lock) |
| Reversible actions you can undo | Seeking the perfect fix (Decide never ends) |

## Application Patterns

### Incident Response
```
OBSERVE: metrics, logs, alerts, recent changes
ORIENT:  match pattern, form ≥2 hypotheses, assess blast radius
DECIDE:  mitigation (rollback, scale, disable feature)
ACT:     execute, immediately observe results
LOOP:    continue until stable
```

### Debugging Under Pressure
```
OBSERVE: errors, stack traces, recent changes
ORIENT:  form a hypothesis about the cause
DECIDE:  test the most likely hypothesis first
ACT:     add logging / try the fix / eliminate the possibility
LOOP:    update the hypothesis from the result
```

## Common Failure Modes
| Failure | Symptom | Fix |
|---------|---------|-----|
| Observation overload | Can't process all data | Filter to key indicators |
| Orientation lock | Stuck on one hypothesis | Force a second framing |
| Decision paralysis | Waiting for certainty | Set a decision deadline; act on 70% |
| Action without observation | Blind execution | Mandate observe-after-act |
| Not actually looping | Stuck in one phase | Time-box each phase |

## Key Questions
- "What do I observe RIGHT NOW?" (not 5 minutes ago)
- "What pattern does this match—and what's my second hypothesis?"
- "What's my best reversible action given current understanding?"
- "How will I know in the next 2 minutes whether it worked?"
- "Am I cycling, or stuck in one phase?"

## Boyd's Insight
"He who can handle the quickest rate of change survives." The goal isn't just making decisions—it's making and revising them faster than the situation compounds. Speed creates options; delay eliminates them.
