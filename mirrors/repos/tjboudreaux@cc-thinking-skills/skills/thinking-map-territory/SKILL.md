---
name: thinking-map-territory
description: Use when behavior contradicts the docs, tests, diagram, or your assumption — stop reasoning from the description, go verify the running code or data directly, and let the territory overrule the map.
---

# Map-Territory Thinking

## Overview

"The map is not the territory." Every representation — doc, test, diagram, comment, mental model — is a simplified view of reality. When behavior contradicts the description, the fastest path to resolution is to **stop reasoning from the map and go verify the territory directly**: read the actual code path, run it with instrumentation, query the real data, reproduce the behavior.

A bug *is* a map–territory mismatch. The README says X, the function name implies Y, the comment claims Z — but the code does something else. The skill is scoped to this specific agent-relevant domain: docs/tests/mental-model vs runtime/code reality. It is NOT a general philosophical framework.

**Core Principle:** The running code and actual data are the territory. The README, the test, the diagram, the comment, and your assumption are all maps. When the two disagree, the territory wins — go look at it before building a theory on top of the map.

## When to Use

- **Debugging:** behavior contradicts the docs, a test's expectation, a comment, a diagram, or "it should work" — go read/trace the real code path
- A claim about the system comes from a doc, a comment, or recall rather than from the current code or data
- Tests pass but the behavior is wrong (the test is a map of *expected* behavior, not all behavior)
- You're about to theorize about *why* something happens instead of looking at *what* happens

Decision flow:

```
Behavior ≠ what the doc/test/diagram/assumption says?
  → Yes → GO VERIFY THE REAL CODE/DATA, then theorize
  → No → Fine, but confirm before high-stakes action

Building a theory on a description rather than the thing itself?
  → Yes → CHECK THE TERRITORY FIRST
```

## When NOT to Use

- **The map IS the artifact you're being asked to change.** When editing the docs, the spec, or the diagram itself, that *is* the territory for that task — don't spiral into verifying everything.
- **You've already verified against the territory this session.** Re-checking the same code path repeatedly is wasted budget; trust the verification you just did.
- **The map is authoritative and current** (e.g., a generated type, a schema the code is derived from). Don't second-guess a source of truth.
- **The mismatch doesn't affect the decision.** If the abstraction leaks in a way that can't change your action, note it and move on.

## Procedure

### Step 1: Name the Map

When something is surprising, explicitly identify the *representation* the surprise is measured against:

```
Surprise: "This function should return the user, but the page is blank."

The map: the function name + a comment saying it returns the user
The territory: what the function body actually does on this input
```

Be specific about which map you were trusting — the doc, the test name, the variable name, the comment, the architectural diagram, or your own assumption.

### Step 2: Go to the Territory — Agent-Executable Verification

Don't reason about what the code *probably* does. Execute these verification actions:

1. **Read the actual function body and the path that runs** — not the summary of it, not the docstring, the actual code
2. **Run it / add a log / inspect the value** — instead of predicting the output from the signature
3. **Query the real data** — instead of trusting the schema's intent
4. **Reproduce the behavior** — instead of reasoning from the bug report's wording
5. **Check what changed recently** — `git log`, the deploy, the config change

Only theorize AFTER you've looked at the territory.

### Step 3: Let the Territory Overrule the Map

If the code does X and the doc says Y, the code is what ships and what breaks. Update your theory to match the territory — never the reverse.

```
Map: "The cache makes reads fast"
Territory (measured): 30% hit rate; most reads hit the DB
Conclusion: the mental model was wrong — fix the model, then the caching
```

### Step 4: Note What No Map Covers

Once verified, name the aspects no available map shows — that's where the next bug hides:

```
Have: the happy-path code, the passing tests
Don't have a map of: the error/timeout paths, contention behavior, the null case
Action: look at those before declaring it correct
```

### Step 5: Stop When Verified

Don't re-verify something you already confirmed this session. Trust the verification you just did and move on.

## Output Contract

A completed Map-Territory verification produces:

1. **Map Named** — which representation (doc/test/comment/assumption) was trusted
2. **Territory Verified** — what the actual code/data showed (specific observation, not interpretation)
3. **Delta Documented** — the gap between map and territory
4. **Model Updated** — the corrected understanding after territory observation
5. **Uncovered Aspects Noted** — what no available map covers (likely next bug site)

## Anti-Patterns

| Anti-Pattern | Symptom | Correction |
|---|---|---|
| **Theorizing before verifying** | Reasoning about what code *probably* does without looking | Go to the territory first — read/run/query/reproduce |
| **Trusting the map over the territory** | "The doc says X, so the code must be wrong" when the code is what ships | The territory wins; update the map |
| **Re-verifying known territory** | Checking the same code path repeatedly in one session | Trust what you just verified; note it and move on |
| **Map-territory on artifacts being edited** | Spiral into verification when the doc/diagram IS the thing you're changing | The edited artifact IS the territory for that task |
| **Over-applying to authoritative maps** | Second-guessing generated types or code-derived schemas | Authoritative/generated maps ARE the territory |
| **Verifying irrelevant mismatches** | Noting a doc-code gap that can't affect the decision | If it doesn't change your action, note it and move on |
