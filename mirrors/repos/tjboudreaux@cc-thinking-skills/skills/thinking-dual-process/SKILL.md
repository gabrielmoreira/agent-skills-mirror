---
name: thinking-dual-process
description: Use when an answer arrives too fast on a high-stakes or unfamiliar task. Force one explicit verification pass before committing instead of shipping the first plausible answer.
---

# Dual-Process Thinking

## Overview
A language model produces a first answer by fast pattern-completion: the most statistically likely continuation given the prompt. That fast path is excellent for routine, well-trodden tasks and dangerous for high-stakes or unfamiliar ones, where the most *plausible-sounding* answer and the *correct* answer diverge. This skill is the deliberate counterweight: when an answer arrives too easily on a task that matters, force one explicit verification pass before committing.

The framing comes from Kahneman's fast/slow distinction, but the operative idea here is mechanical, not psychological: **fast generation** (the immediate completion) vs. a **deliberate check** (re-deriving, testing, or sourcing the answer).

**Core Principle:** Fluency is not correctness. When the answer came easily *and* the cost of being wrong is high, that combination is the trigger to slow down and verify — not a signal you're done.

## Trigger Card

When an answer arrives instantly on a high-stakes or unfamiliar task, run one verification pass before committing:

1. **Notice:** Did the answer form immediately, with no intermediate steps? High confidence but nothing checked?
2. **Check triggers:** Is the task high-stakes/irreversible OR the domain unfamiliar? If neither, ship the fast answer.
3. **Verify:** Re-state the claim → re-derive or test it a second, independent way → check against ground truth (code, docs, data) → reconcile any disagreement → commit.

The trigger is **easy answer + real cost of error.** If the answer was hard-won, you already deliberated. If the task is trivial and reversible, don't over-verify.

## When to Use
- The task is high-stakes or irreversible (data migration, security, deletion, public commitment) and the answer felt obvious.
- The domain is unfamiliar or the task is novel — no well-worn pattern to rely on.
- The answer requires statistical or quantitative reasoning (where fast completion is reliably miscalibrated).
- You're reviewing work and it "looks fine" on a quick pass.
- A claim is plausible and convenient but you haven't actually checked it against the code/docs/data.

Decision flow:
```
Answer arrived fast? → High stakes OR unfamiliar? → yes → RUN A VERIFICATION PASS
                                                  ↘ no → fast answer is fine, ship it
                     ↘ no (had to work for it) → you already deliberated
```

## When NOT to Use
- **Routine, reversible, low-stakes tasks.** Renaming a variable, a trivial edit, an obvious lookup — re-verifying everything is wasted budget and invites analysis paralysis.
- **You already worked through it deliberately.** If the answer was hard-won, a second pass is redundant; the trigger is *easy answer + high stakes*, not every answer.
- **The verification pass would cost more than the error it prevents.** Match the depth of the check to the cost of being wrong.
- **You can just run it.** If a test or a quick execution would settle it, do that instead of more reasoning.

## The Two Modes

### Fast generation (the default)
| Characteristic | Description |
|----------------|-------------|
| **Speed** | Immediate — the answer is just the first plausible completion |
| **Basis** | Pattern-matching to similar prompts seen in training |
| **Confidence** | Often high *regardless* of correctness — fluency masquerades as certainty |

Fast generation is reliable for:
- Well-trodden, conventional tasks with a clear standard answer
- Reformatting, summarizing, and other low-ambiguity transforms
- Recall of common, stable facts
- Routine code in a familiar language/framework

Fast generation is unreliable for:
- Arithmetic and multi-step quantitative reasoning
- Statistical reasoning and base-rate problems
- Novel or unfamiliar problems with no template to match
- Anything where a plausible-sounding answer can be subtly wrong (APIs, version-specific behavior, edge cases)

### Deliberate verification (the override)
| Characteristic | Description |
|----------------|-------------|
| **Speed** | Slower — re-derive, test, or source the answer |
| **Basis** | Explicit steps, checks against ground truth |
| **Confidence** | Earned — tied to what was actually verified |

Deliberate verification is worth its cost when:
- Re-deriving a result a second, independent way
- Running or tracing the code instead of predicting its output
- Checking a claim against the actual file/doc/data rather than memory
- Enumerating edge cases the fast answer glossed over

Its only failure mode is over-use: applying it to trivial, reversible work where the check costs more than the error.

## The Process

### Step 1: Notice the fast answer
A fast answer announces itself: it's the response forming immediately, before any explicit work. That's normal and usually fine. The thing to notice is *how* you got it.

- Answer formed immediately, no intermediate steps
- It "obviously" follows from the prompt
- Confidence is high but nothing was actually checked

```
Example: "Does this regex match leading zeros?"
A confident yes/no forms instantly → fast generation.
Before answering: is this high-stakes or am I sure? If either is shaky, test the regex.
```

### Step 2: Check the two trigger conditions
A verification pass is warranted only when BOTH are true enough:

**The answer came easily** (Step 1), AND **the cost of being wrong is real:**
- Stakes are high or the action is irreversible
- The domain is unfamiliar or the problem novel
- It requires arithmetic / statistical reasoning
- A wrong-but-plausible answer would slip through review

If the answer was hard-won, you already deliberated — stop. If stakes are trivial and reversible, the fast answer is fine — stop.

### Step 3: Run the verification pass
When both conditions hold, do exactly one disciplined check:

```
1. RE-STATE  - Write the claim/answer explicitly
2. RE-DERIVE - Reach it a second, independent way (or test/run it)
3. CHECK     - Against ground truth: the code, the docs, the data, the math
4. RECONCILE - If the two paths disagree, the fast answer was wrong — find out why
5. COMMIT    - Ship the verified answer
```

Watch for these fast-answer red flags specifically:
- It's the most common/canonical answer but the prompt has an unusual twist
- It depends on a version, config, or edge case you didn't actually confirm
- It's the convenient answer that lets you stop early
- It restates the user's assumption back to them without testing it

### Step 4: Match effort to stakes

| Situation | Process |
|--------|---------|
| Fast answer + low stakes | Ship it; don't manufacture doubt |
| Fast answer + high stakes | Run the verification pass above |
| Already deliberated | Done — no second pass needed |

## Fast-Generation Failure Modes

### Question substitution
Fast generation answers an easier nearby question instead of the one asked:
```
Asked: "Is this O(n) or O(n log n)?"
Answered: "Does this look like efficient code?"  (vibe, not analysis)

Asked: "Does this migration preserve all rows?"
Answered: "Does this migration look correct?"  (plausibility, not verification)
```
The fix is to re-state the *exact* question (Step 3) so the substitution becomes visible.

### Pattern-matched errors

| Pattern | What it does | When it fails |
|-----------|--------------|---------------|
| Canonical-answer pull | Returns the textbook answer | The prompt has a non-standard twist |
| Base-rate neglect | Reasons from the salient detail | Ignores how common the outcome actually is |
| Anchoring | Builds on a number in the prompt | The anchor was arbitrary or wrong |
| Confirmation | Surfaces support for the framing given | Misses evidence the framing is wrong |
| Sycophantic agreement | Echoes the user's stated assumption | The assumption was the bug |

### WYSIATI (What You See Is All There Is)
Fast generation builds the most coherent answer from *only* what's in the prompt, and does not flag what's missing:
```
Given: "the function returns the user"
Concludes: "so the happy path works"
Missing: the 404 path, the timeout, the null case — none mentioned, so none considered
```
Coherence of the answer is not coverage of the territory. Explicitly ask "what would I need to look at that isn't in front of me?"

## Fluency Is Not Correctness

A smooth, confident, well-formatted answer *feels* more trustworthy — to the reader and in the generation itself. That fluency signal is independent of whether the answer is right.

| Fluent answer | Verified answer |
|---|---|
| Reads cleanly, high apparent confidence | Confidence tied to a specific check that passed |
| Risk: accepted without scrutiny | Risk: only over-use on trivial tasks |

**The trap:** the more polished the fast answer, the *less* it gets challenged — exactly backwards from what stakes should dictate. On a high-stakes task, treat a too-clean answer as a reason to run the verification pass, not a reason to ship.

## Application Examples

### Code Review
```
Fast answer: "This looks fine" (matches familiar-looking code)
Verification pass (high-stakes change):
- Trace the actual logic line by line, don't pattern-match the shape
- Enumerate the edge/error paths the diff doesn't mention
- Check the change against the contract it must uphold (callers, tests)
```

### Reporting a Fact or API Behavior
```
Fast answer: "Use method X, it takes these args" (canonical recall)
Verification pass (unfamiliar/version-sensitive):
- Confirm the method exists in the version in this repo
- Check the signature in the actual source/docs, not from memory
- If unsure, say so or look it up rather than assert
```

### Architecture / Tech Choice
```
Fast answer: "Use [the obvious default]" (most-common completion)
Verification pass (high-stakes):
- State the actual requirements, then check the default against them
- Name one alternative and why it loses, so the choice is reasoned not reflexive
```

### Debugging
```
Fast answer: "It's probably X" (first plausible hypothesis)
Verification pass:
- List the candidate causes, not just the first
- Find the evidence that would distinguish them, and look at it
- Resist committing to X until the logs/repro actually point there
```

## Integration with Other Thinking Skills

### With Debiasing
Fast generation is where most bias-shaped errors enter; the verification pass is where you catch them. Run the debiasing checklist as the content of Step 3 on high-stakes calls.

### With Bayesian Reasoning
Fast answers neglect base rates; the verification pass restores them:
```
Fast: "Positive test result = probably has the condition"
Verified: state the base rate first, then update (see thinking-bayesian)
```

### With First Principles
The fast answer reasons by analogy ("everyone does X"); the verification pass asks whether the constraint is real:
```
Fast: "Competitors do X, so we should too"
Verified: "What's the fundamental requirement? Does X actually meet it?"
```

### With Pre-Mortem
The fast answer is optimistic by default; the verification pass adds the failure view:
```
Fast: "This plan will work"
Verified: "Assume it failed — what's the most likely reason?"
```

### With OODA Loop
Under genuine time pressure (an incident), act on the fast answer at ~70% confidence and re-observe — don't stall on verification. Reserve the full pass for after, or for the irreversible step within the incident.

## When the Fast Answer Is Trustworthy

The fast path is not the enemy — it's correct most of the time, and over-verifying is its own failure. Lean on the fast answer when:

1. **The task is conventional** — a standard transform or a common, stable fact
2. **The pattern fits cleanly** — no unusual twist in the prompt
3. **It's cheaply reversible** — a wrong answer is caught and fixed at near-zero cost
4. **You can confirm it trivially if challenged** — the check is one step away

```
Fine to ship fast:
- "Convert this JSON to YAML"
- "What HTTP status means 'not found'?"
- A rename or a comment fix

Verify first:
- "Will this SQL touch every shard?"
- "Is this auth check actually enforced on the server?"
- Anything version-, edge-case-, or money-sensitive
```

Ask: "If this is wrong, how and when do I find out — and how much does it cost?"

## Verification Checklist
- [ ] Noticed whether the answer arrived fast or was worked through
- [ ] Checked BOTH triggers: easy answer AND real cost of error
- [ ] If both true, ran one disciplined verification pass against ground truth
- [ ] Re-derived or tested the result a second, independent way
- [ ] Did NOT over-verify a trivial, reversible task
- [ ] Confirmed version/edge-case-sensitive claims rather than asserting from memory
- [ ] Matched the depth of the check to the cost of being wrong

## Key Questions
- "Did this answer come too easily — and does that matter here?"
- "Is this a conventional task or one with an unusual twist?"
- "What would a second, independent derivation show?"
- "Is my confidence tied to an actual check, or just to how clean the answer reads?"
- "What's missing that isn't in front of me (WYSIATI)?"
- "If this is wrong, how and when do I find out?"

## The Core Warning
A fluent, confident answer reflects the coherence of the completion, not the quality of the evidence behind it. The most polished answers get challenged the least — which is exactly backwards when the stakes are high. When an answer comes easily on something that matters, that ease is the trigger to verify, not the signal you're done.
