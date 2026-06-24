---
name: thinking-scientific-method
description: Use when a symptom could have several causes and you must find the faulty code by ranking falsifiable hypotheses and checking the cheapest discriminating observation first.
---

# Hypothesis-Differential Debugging

## Overview

The scientific method's payoff for an agent is not narrating "observe -> question." It is the **differential**: when a symptom could come from several places, enumerate competing falsifiable hypotheses and spend your cheapest observation on the one that best discriminates between them.

This is the proven replacement for the old broad scientific-method skill. In SWE-bench fault localization, the original was flat; this agent-native version turned it into the strongest measured debugging lift in the current eval set.

**Core Principle:** Don't guess-and-patch. Enumerate competing causes, then make the cheapest observation that would falsify the most likely one.

## When to Use

- A bug or incident symptom could plausibly come from more than one place
- You have read access to code, logs, diffs, traces, or tests
- You need to localize the faulty file, function, branch, config, or invariant before fixing

```
Symptom has several plausible causes?
  -> no  -> test or fix the obvious cause directly
  -> yes -> can you make cheap observations now?
       -> no  -> gather access/evidence first
       -> yes -> apply hypothesis-differential debugging
```

## When NOT to Use

- The cause is already obvious from a single trace, failing test, or recent diff -> fix directly.
- Only one plausible hypothesis exists -> test it directly.
- You cannot make any observation -> get access first; don't speculate.
- You are designing an A/B test, canary, or multi-week experiment -> this skill is for observations an agent can make now.

## The Procedure

### Step 1: Enumerate competing hypotheses

List 3-5 specific, falsifiable hypotheses. Name the likely file, function, subsystem, input condition, or invariant. Avoid vague buckets like "backend issue" or "race condition somewhere."

```markdown
| # | Hypothesis | Why plausible? |
|---|------------|----------------|
| H1 | `auth/session.py:refresh` drops rotated tokens | failures start after token rotation |
| H2 | cache TTL mismatch in `session_cache` | stale sessions persist across deploys |
| H3 | frontend retries reuse expired cookie | only browser flow is affected |
```

If you can only think of one hypothesis, you are guessing. Force alternatives before inspecting deeper.

### Step 2: Name the cheapest discriminating observation

For each hypothesis, name one observation you can make now that would separate it from the others.

Good observations:
- read the function the stack trace names
- grep callers of a parser or config key
- inspect the recent diff touching the failing path
- compare two log lines across working and broken cases
- check a test fixture or schema invariant

Bad observations:
- deploy a canary
- run a long experiment
- ask users to wait
- inspect every file in the subsystem

### Step 3: State falsifiers before looking

For each hypothesis, write what result would make you drop it. This prevents confirmation search.

```markdown
| Hypothesis | Falsified if... |
|------------|-----------------|
| H1 token refresh | refresh path never reads rotated token state |
| H2 cache TTL | cache entry expires before the observed stale window |
| H3 frontend retry | same failure occurs in API-only reproduction |
```

### Step 4: Rank by likelihood x cheapness

Test the observation with the best expected information per unit of effort. Start with the cheapest observation that separates your top hypotheses, not the most elaborate investigation.

```
For each hypothesis → name falsifier → rank by likelihood x cheapness → observe → update/drop → localize fault
```

### Step 5: Stop on direct localization

Stop when one hypothesis is supported by direct evidence and the key alternatives are ruled out. Name the file/function/config to change and the evidence that localizes it.

## Investigation Template

```markdown
## Symptom
[Specific failing behavior, scope, timing, and known constraints]

## Hypotheses
| # | Hypothesis | Why plausible? | Cheapest observation | Falsified if... |
|---|------------|----------------|----------------------|-----------------|
| H1 | [specific file/function/config cause] | [evidence] | [read/grep/diff/check] | [drop condition] |
| H2 | [specific alternate cause] | [evidence] | [read/grep/diff/check] | [drop condition] |
| H3 | [specific alternate cause] | [evidence] | [read/grep/diff/check] | [drop condition] |

## Test Order
1. [Cheapest discriminating observation]
2. [Next observation if H1 is falsified]
3. [Deferred only if cheap observations do not localize]

## Localization
[Supported hypothesis, ruled-out alternatives, and the file/function/config to change]
```

## Worked Shape

```markdown
Symptom: intermittent 500s on /export, only eu-west, started three days ago.

Hypotheses:
1. recent diff to export serializer
   Observation: inspect commits touching `export_serializer`
   Falsified if: no diff touches the failing codepath
2. eu-west Redis rotation broke a cache key
   Observation: read cache key construction + region config
   Falsified if: key and TTL match healthy regions
3. upstream timeout under load
   Observation: compare timeout logs during failure window
   Falsified if: no upstream latency spike

Test order: H1, H2, H3.
Result: H1 diff changed nested export handling and matches stack trace.
Localized fault: `app/export/serializer.py`.
```

## Anti-Patterns

- Narrating the scientific method without proposing competing causes
- Looking only for evidence that supports your first guess
- Calling an expensive experiment a "test" when a cheap observation exists
- Stopping at a plausible explanation before ruling out alternatives
- Continuing to analyze after the faulty file/function is localized

## Verification Checklist

- [ ] Listed 3-5 specific hypotheses
- [ ] Each hypothesis has a cheap observation available now
- [ ] Each hypothesis has a stated falsifier
- [ ] Observations are ranked by likelihood x cheapness
- [ ] Final answer names the localized file/function/config and the evidence

## Key Questions

- What would I see if this hypothesis were false?
- Which observation best separates the top two hypotheses?
- Am I testing a hypothesis or confirming my first guess?
- Can I localize the fault with a cheaper observation?

## Feynman's Wisdom

"The first principle is that you must not fool yourself - and you are the easiest person to fool." Your intuition generates hypotheses; the differential tests them.
