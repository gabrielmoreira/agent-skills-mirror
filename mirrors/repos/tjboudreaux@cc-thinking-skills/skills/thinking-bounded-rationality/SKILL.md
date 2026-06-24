---
name: thinking-bounded-rationality
description: Use when a search or investigation could run indefinitely and you need a stopping rule. Set an explicit "good enough" threshold and stop at the first option that clears it.
---

# Bounded Rationality and Satisficing

## Overview

Herbert Simon's Bounded Rationality recognizes that any agent operating under finite resources cannot exhaustively optimize: the search space is too large, information is incomplete, and acting has a cost. Rather than pursuing the optimal solution, Simon proposed "satisficing"—a portmanteau of satisfy + suffice—choosing the first solution good enough to meet an explicit threshold, then stopping.

For an autonomous coding agent the binding constraint is a **budget**: tool calls, search/read operations, context window, and wall-clock time per turn. A grep that could keep matching, a file tree you could keep traversing, a doc set you could keep reading — each has steeply diminishing returns. Satisficing converts "search until certain" (which never terminates) into "search until the threshold is met, then act."

**Core Principle:** Define "good enough" *before* you search, and stop at the first option that clears the bar. Optimizing is correct only when the gap between good and best is worth more than the budget it costs to close it.

## When to Use

- An investigation or search has no natural endpoint (greps, file reads, doc crawls, candidate solutions) and could consume the whole budget.
- Multiple options would all clear the requirement and you're tempted to keep comparing.
- You're gathering more context than the decision actually needs.
- A reversible, low-stakes choice is consuming optimization-level effort.
- You need to commit and ship before the turn/budget runs out.

Decision flow:

```
Search/investigation that could run indefinitely? → yes → Is closing the gap to "best" worth the budget? → no → SATISFICE (threshold + stop)
                                                                                                          ↘ yes → Optimize (and cap the budget)
                                                  ↘ no → just answer
```

## When NOT to Use

- **Irreversible or high-stakes choices** (data deletion, security boundaries, schema/migration decisions, public commitments) — the gap between good and best is worth the budget; optimize and verify.
- **Correctness gates** — tests, security checks, and "did the fix actually work?" are not satisficeable; you need the right answer, not a sufficient-looking one.
- **The answer is cheaply knowable** — if one more grep or a single file read would settle it definitively, just do it; don't satisfice your way past a quick fact.
- **The threshold can't be stated** — if you can't articulate what "good enough" means, you can't satisfice responsibly; clarify the requirement first.

## Trigger Card

When a search or investigation could run indefinitely and you need to ship:

1. **Set an explicit aspiration level** — what does "good enough" look like? Define a concrete, measurable threshold.
2. **Search sequentially** — evaluate options one at a time in the order you encounter them. Do not enumerate exhaustively.
3. **Stop at the first option that clears the threshold.** Commit and move on.

If the threshold can't be articulated or the cost of a wrong choice is catastrophic, don't satisfice — run the full procedure. For a single cheaply-knowable fact, just look it up.

## The Three Constraints

### 1. Information Bounds

**What you can know is limited**

- Complete information rarely exists
- Gathering more information has costs
- Information has diminishing returns
- Future states are inherently uncertain

```
Example: Choosing a technology stack
Reality: You can't test every option in production
         You can't predict 5-year industry shifts
         You can't know your future team composition
Satisfice: Pick a well-supported option that meets current needs
```

### 2. Processing Bounds (the budget)

**What you can compute and attend to is limited**

- Each turn has a finite budget of tool calls, reads, and context-window tokens
- Adding more options/criteria to a comparison degrades signal, not improves it — past ~3-5 criteria, marginal context rarely flips the decision
- Long, sprawling investigations crowd out the context needed to act on what you found
- More search reduces uncertainty with sharply diminishing returns

```
Example: Choosing among architecture options
Reality: Reading every doc and modeling every interaction effect
         burns the budget before you produce an answer
Satisfice: Fix the 3-5 criteria that actually decide it, evaluate
           against those, and stop at the first option that clears them
```

### 3. Action-Cost Bounds

**Deciding and re-deciding both cost budget and time**

- Every additional search/read consumes budget that can't be spent elsewhere
- The user is waiting; an answer now usually beats a marginally better answer later
- Re-opening a settled, reversible decision is rarely worth the cost
- Perfect is the enemy of shipped

```
Example: Picking a library for a reversible internal task
Reality: You could compare ten options across a dozen dimensions
         Reversibility means a wrong-but-adequate pick is cheap to swap
Satisfice: Pick the first well-supported option that meets the requirement, move on
```

## Satisficing vs. Optimizing

### When to Satisfice

| Signal | Why Satisfice |
|--------|---------------|
| Reversible decision | Can adjust later with more information |
| Time pressure | Cost of delay exceeds value of more analysis |
| Diminishing returns | 80% solution found, 100% would take 10x effort |
| High uncertainty | More analysis won't reduce uncertainty meaningfully |
| Many acceptable options | Several solutions meet requirements adequately |
| Low stakes | Consequences of suboptimal choice are minor |

### When to Optimize

| Signal | Why Optimize |
|--------|--------------|
| Irreversible decision | Mistakes are permanent or very costly to undo |
| High stakes | Wrong choice has severe consequences |
| Clear criteria | You know exactly what "best" means |
| Bounded search space | All options can actually be evaluated |
| Available time | Deadline allows for thorough analysis |
| Clear value of optimal | Difference between good and best is significant |

## The Satisficing Process

### Step 1: Define Aspiration Level

Set the minimum acceptable threshold for each criterion:

```
Example: Hiring a senior engineer
Optimizing: Find the absolute best candidate
Satisficing: Find a candidate who:
- Has 5+ years relevant experience ✓
- Can pass technical interview ✓
- Salary expectations fit budget ✓
- Available to start within 4 weeks ✓
- Culture fit (team confirms) ✓

First candidate who meets all criteria → Hire
```

### Step 2: Search Sequentially

Evaluate options one at a time against aspiration level:

```
Option A: Meets 4/5 criteria → Continue search
Option B: Meets 3/5 criteria → Continue search  
Option C: Meets 5/5 criteria → STOP, choose this one
```

Key insight: You don't compare options against each other, you compare each option against your threshold.

### Step 3: Adjust Aspiration If Needed

If search is too long or too short, recalibrate:

```
Too many options qualify → Raise aspiration level
Nothing qualifies after reasonable search → Lower aspiration level
```

### Step 4: Commit and Move On

Once threshold is met:

- Stop searching
- Accept the decision
- Resist second-guessing
- Redirect energy to execution

## Application Patterns

### For Technical Design

```
Scenario: Choose a message queue for new service

Satisficing approach:
1. Define requirements (aspiration level):
   - At-least-once delivery ✓
   - Handles 10k msg/sec ✓
   - Team familiarity or fast learning curve ✓
   - Managed option available ✓
   - Within cost budget ✓

2. Evaluate sequentially:
   - RabbitMQ: Meets all → STOP, use RabbitMQ

3. Don't continue researching Kafka, SQS, etc.
   unless RabbitMQ fails threshold
```

### For Code Review

```
Scenario: Reviewing a PR under time pressure

Satisficing approach:
1. Define "good enough" criteria:
   - No security vulnerabilities ✓
   - Tests pass ✓
   - No obvious performance issues ✓
   - Code is readable ✓
   - Follows project conventions ✓

2. Stop when criteria met
   Don't perfect every line if shipping matters
```

### For Research/Investigation

```
Scenario: Debugging production issue

Satisficing approach:
1. Define stopping criteria:
   - Root cause identified ✓
   - Fix verified in staging ✓
   - Rollback plan exists ✓

2. Stop investigating once you can fix
   Don't exhaustively trace every code path
   if you have a working solution
```

### For Feature Scope

```
Scenario: MVP feature set decisions

Satisficing approach:
1. Define "enough to learn":
   - Core user job addressed ✓
   - Measurable success metric exists ✓
   - Usable enough for feedback ✓
   - Can ship within sprint ✓

2. First scope that meets criteria → Ship it
   Don't polish what you might throw away
```

## Setting Appropriate Aspiration Levels

### Too High → Analysis Paralysis

Symptoms:

- Nothing ever meets the bar
- Endless research and comparison
- Decisions perpetually delayed
- Perfect becomes enemy of good

Fix: Ask "What's the minimum that would be acceptable?"

### Too Low → Poor Outcomes

Symptoms:

- Frequent rework required
- Quality issues in production
- Technical debt accumulation
- Stakeholder dissatisfaction

Fix: Ask "What past decisions do I regret? What threshold would have prevented them?"

### Calibration Heuristics

```
Reversibility Check:
- Easily reversible → Lower aspiration OK
- Hard to reverse → Raise aspiration

Consequence Check:
- Minor consequences → Lower aspiration OK
- Major consequences → Raise aspiration

Time Check:
- Tight deadline → Accept lower aspiration
- Ample time → Can afford higher aspiration
```

## Common Traps

### Trap 1: Satisficing Feels Like Settling

**Reality:** Satisficing is rational under constraints, not lazy.

```
Optimizing with infinite time = mathematically correct
Optimizing with real constraints = often irrational
Satisficing = adapted to actual world
```

### Trap 2: Post-Decision Regret

**Reality:** Finding a better option later doesn't mean the decision was wrong.

```
You chose Option B (met threshold)
Later discovered Option D was "better"
This is expected—you stopped searching at B
Regret is only valid if B didn't meet your threshold
```

### Trap 3: Creeping Aspiration

**Reality:** Moving goalposts prevent closure.

```
Original: "Need 100ms response time"
After meeting it: "Actually, 50ms would be better"
After that: "Hmm, 25ms would be ideal..."

Fix: Lock aspiration level before search begins
```

### Trap 4: Satisficing the Wrong Things

**Reality:** Some decisions warrant optimization.

```
Wrong to satisfice:
- Security critical systems
- Legal compliance
- Safety-critical code
- Irreversible architectural choices

Right to satisfice:
- Internal tooling
- Reversible experiments
- Style preferences
- Low-stakes choices
```

## Integration with Other Thinking Models

### With First Principles

```
Use First Principles to determine:
- What constraints are real vs assumed?
- What is the fundamental requirement?
Then satisfice against those fundamentals
```

### With Inversion

```
Use Inversion to set aspiration level:
- "What would make this solution unacceptable?"
- Avoid those failure modes
- Any option avoiding them satisfices
```

### With Circle of Competence

```
Outside your circle:
- You can't evaluate "optimal" anyway
- Satisficing is your only realistic option
- Set thresholds based on expert input

Inside your circle:
- You can choose when to optimize vs satisfice
- Trust your calibrated aspiration levels
```

### With Pre-Mortem

```
Run pre-mortem to validate aspiration level:
- "If this satisficed solution fails, why?"
- Adjust thresholds to prevent likely failures
- Don't over-engineer against unlikely failures
```

## Verification Checklist

- [ ] Identified whether this decision warrants optimizing or satisficing
- [ ] Set clear aspiration level before searching
- [ ] Defined explicit stopping criteria
- [ ] Evaluated options against threshold, not against each other
- [ ] Stopped when threshold was met (or adjusted threshold rationally)
- [ ] Committed to decision without continued comparison shopping
- [ ] Documented reasoning for future reference

## Key Questions

- "What's the minimum acceptable solution here?"
- "What would 'good enough' look like for this decision?"
- "Is more research likely to change my decision?"
- "What's the cost of continued analysis vs acting now?"
- "Can I reverse this decision if I learn more later?"
- "Am I searching for best, or searching to avoid deciding?"
- "What threshold would I set for someone else in my position?"

## Simon's Insight

"A wealth of information creates a poverty of attention."

In a world of infinite information and finite attention, satisficing isn't settling—it's adapting to reality. The goal isn't to make perfect decisions, but to make good decisions efficiently, preserving cognitive resources for the problems that truly require optimization.

The satisficer who ships beats the optimizer who's still researching.
