---
name: thinking-reversibility
description: Before deliberating over a decision, ask if it's a one-way door (costly to undo) or two-way (cheap to undo) — decide two-way doors fast, and look for moves that make one-way doors reversible.
---

# Reversibility Thinking

## Overview

Jeff Bezos distinguishes between Type 1 (irreversible, one-way door) and Type 2 (reversible, two-way door) decisions. The key insight: most decisions are Type 2 but get treated as Type 1, causing analysis paralysis. Match your decision process to the reversibility of the decision.

**Core Principle:** Reversible decisions should be made quickly by individuals. Irreversible decisions deserve deliberation. Most decisions are more reversible than they appear.

## When to Use

- Technology choices
- Architecture decisions
- Process changes
- Hiring decisions
- Feature implementations
- Organizational changes
- Any decision where you're uncertain how much analysis is warranted

Decision flow:

```
Decision to make?
  → Is it easily reversible? → yes → DECIDE QUICKLY (Type 2)
  → Is it hard/impossible to reverse? → yes → DELIBERATE CAREFULLY (Type 1)
  → Unsure of reversibility? → ANALYZE REVERSIBILITY FIRST
```

## When NOT to Use
- You've already classified the door — don't re-run the analysis; just decide at the matched depth.
- Trivial, clearly two-way calls (variable names, which test to write first) — deciding is faster than classifying.
- The decision is being forced by a hard external constraint (deadline, contract, regulation) with no real optionality — reversibility doesn't change the available move.
- An irreversible action is genuinely required and the upside justifies it — name it, accept it, and proceed deliberately rather than stalling.

## Trigger Card

Before deliberating over a decision:

1. **Classify the door** — is it one-way (costly to undo) or two-way (cheap to undo)? If you're not sure, it's probably one-way.
2. **Two-way door?** → Decide fast. The cost of delay exceeds the cost of a wrong choice you can reverse.
3. **One-way door?** → Ask: can I make it more reversible? (Feature flag, canary, small rollout, decouple the irreversible part.) Then deliberate — but only on what's actually irreversible.

If the decision is forced by an external constraint with no optionality, reversibility doesn't change the available move. If an irreversible action is genuinely required and the upside justifies it, name it and proceed.

## Type 1 vs Type 2 Decisions

### Type 1: One-Way Doors

**Characteristics:**
- Irreversible or very costly to reverse
- Consequences are significant and lasting
- Changing course means starting over

**Examples:**
- Fundamental architecture choices (monolith vs microservices for core systems)
- Major technology platform (cloud provider for critical infra)
- Hiring for leadership positions
- Shutting down a product line
- Major acquisitions or contracts
- Public commitments or promises

**Process:**
- Extensive analysis before acting
- Explicitly argue the opposing choice (steel-man the alternative)
- Document the reasoning and the assumptions it rests on
- Escalate / surface to the human owner before committing

### Type 2: Two-Way Doors

**Characteristics:**
- Easily reversed if wrong
- Limited blast radius
- Can iterate and adjust

**Examples:**
- Most feature implementations
- UI/UX changes
- Internal tool selection
- Process experiments
- Meeting cadences
- Individual hiring decisions
- Marketing campaigns

**Process:**
- Decide quickly
- Pick the most reasonable option now
- Monitor results
- Adjust as needed
- Don't over-analyze

## The Reversibility Analysis

### Step 1: Assess True Reversibility

| Factor | Question | Impact on Reversibility |
|--------|----------|------------------------|
| Technical cost | How hard to undo technically? | High cost = less reversible |
| Time cost | How long to reverse? | Months = less reversible |
| Financial cost | How expensive to change? | High cost = less reversible |
| Reputation cost | Will reversal damage trust? | Yes = less reversible |
| Learning cost | Will we lose the learning? | Critical learning = more complex |
| Dependency cost | Have others built on this? | Many dependents = less reversible |

### Step 2: Categorize the Decision

```
Reversibility Score:
- Can undo in days with minimal cost: TYPE 2 (two-way door)
- Can undo in weeks with moderate cost: TYPE 2 with monitoring
- Can undo in months with significant cost: TYPE 1.5 (evaluate carefully)
- Cannot realistically undo: TYPE 1 (one-way door)
```

### Step 3: Match Process to Type

| Decision Type | Process | Effort | Who decides |
|---------------|---------|--------|-------------|
| Type 1 | Full analysis, argue the alternative, document | High | Surface to human owner before committing |
| Type 1.5 | Structured analysis, document rationale | Moderate | Flag to owner if stakes are high |
| Type 2+ | Quick analysis, note rationale | Low | Decide and proceed |
| Type 2 | Just decide | Minimal | Decide and proceed |

## Common Reversibility Misclassifications

### Treating Type 2 as Type 1

```
Decision: Which logging library to use
Common mistake: Extensive evaluation, committee decision, weeks of analysis
Reality: Can swap libraries in a day; dependencies are isolated
Correct approach: Engineer picks one, team evaluates after 2 weeks

Cost of over-deliberation: Weeks of productivity lost
```

### Treating Type 1 as Type 2

```
Decision: Database technology for core product
Common mistake: Quick decision because "we can always change later"
Reality: Changing databases means rewriting queries, data migration, retraining
Correct approach: Thorough evaluation, prototype, stakeholder alignment

Cost of under-deliberation: Months of migration pain later
```

### Hidden Reversibility

Some seemingly irreversible decisions are actually reversible:

```
"We can't change our API because clients depend on it"
Reality: Versioning makes this reversible
       v1 continues, v2 adds improvements

"We can't change the architecture"
Reality: Strangler pattern enables gradual change
        Migrate piece by piece
```

### Hidden Irreversibility

Some seemingly reversible decisions lock you in:

```
"It's just a prototype, we can rewrite later"
Reality: Prototypes often become production
        "Temporary" code lives for years

"We can always switch cloud providers"
Reality: Deep integration creates massive switching cost
        Proprietary services create lock-in
```

## Reversibility Patterns

### The Pilot Pattern

Turn Type 1 into Type 2 through limited rollout:

```
Type 1: "Adopt new framework for entire codebase"
Piloted: "Use new framework for one service"
         → Now it's Type 2: Can abandon pilot with limited impact
         → If successful, expand incrementally
```

### The Abstraction Pattern

Create reversibility through interfaces:

```
Type 1: "Choose between Postgres and MySQL"
With abstraction: "Define data layer interface, start with Postgres"
                  → Can swap implementation later
                  → Cost of reversal dramatically reduced
```

### The Time-Box Pattern

Make long commitments into short experiments:

```
Type 1: "Commit to vendor for 3 years"
Time-boxed: "Start with 6-month pilot"
            → Can exit at known cost
            → Full commitment only after validation
```

### The Feature Flag Pattern

Deploy with reversibility built in:

```
Type 1: "Launch new pricing model"
With flags: "Launch to 5% of users, flag-controlled"
            → Can disable instantly
            → Expand only when confident
```

## Decision Speed Guidance

### Decide Immediately (Type 2)

- Which test to write first
- Variable naming
- Which task to pick up next
- Local refactors within a single module

### Quick Analysis (Type 2+)

- Library choices (within approved options)
- Implementation approach for a feature
- Code organization within a module
- Bug fix approach

### Structured Analysis (Type 1.5)

- Design patterns for new components
- API contract changes (if unversioned)
- Tool adoption
- Architectural changes to non-critical services

### Full Deliberation, Surface to Owner (Type 1)

- Core architecture decisions
- Platform/infrastructure choices
- Irreversible data migrations / deletions
- Public API contracts with external consumers

## Reversibility Template

```markdown
# Reversibility Analysis: [Decision]

## The Decision
[What we're deciding]

## Reversibility Assessment

| Factor | Assessment | Score (1-5) |
|--------|------------|-------------|
| Technical effort to reverse | [Details] | |
| Time to reverse | [Duration] | |
| Financial cost to reverse | [Cost] | |
| Reputation impact of reversal | [Impact] | |
| Dependencies affected | [Count/scope] | |
| Learning lost if reversed | [Value] | |

Average: [X]
- 1-2: Clear Type 2
- 3: Type 1.5
- 4-5: Type 1

## Decision Type: [Type 1 / 1.5 / 2]

## Appropriate Process
- Analysis depth: [Minimal / Moderate / Extensive]
- Surface to human owner before committing? [No / Yes if high-stakes / Yes]
- Documentation: [None / Brief / Full]

## Can We Increase Reversibility?
- Pilot: [Option]
- Abstraction: [Option]
- Time-box: [Option]
- Feature flag: [Option]

## Decision
[The choice made]

## Reversal Plan (if needed)
[How we would reverse if this proves wrong]
```

## Verification Checklist

- [ ] Assessed reversibility across multiple factors
- [ ] Categorized as Type 1, 1.5, or 2
- [ ] Matched decision process to decision type
- [ ] Explored options to increase reversibility
- [ ] Not over-analyzing Type 2 decisions
- [ ] Not under-analyzing Type 1 decisions
- [ ] Have a reversal plan for non-trivial decisions

## Key Questions

- "How hard would it be to undo this?"
- "Are we treating this like a one-way door when it's actually two-way?"
- "Can we pilot this to make it more reversible?"
- "What's the cost of being wrong vs. the cost of delay?"
- "Who else would be affected if we reverse?"
- "Is this actually irreversible, or does it just feel that way?"

## Bezos' Wisdom

"Some decisions are consequential and irreversible or nearly irreversible – one-way doors – and these decisions must be made methodically, carefully, slowly, with great deliberation and consultation."

"But most decisions aren't like that – they are changeable, reversible – they're two-way doors. If you've made a suboptimal Type 2 decision, you don't have to live with the consequences for that long. You can reopen the door and go back through."

"As organizations get larger, there seems to be a tendency to use the heavy-weight Type 1 decision-making process on most decisions, including many Type 2 decisions. The end result of this is slowness, unthoughtful risk aversion, failure to experiment sufficiently, and consequently diminished invention."

Speed matters. Most decisions are reversible. Decide, learn, adjust.
