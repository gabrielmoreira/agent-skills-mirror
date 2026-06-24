---
name: thinking-theory-of-constraints
description: Use when optimizing latency or throughput in a pipeline and one stage dominates—focus all effort on that single bottleneck, since speeding up the others changes nothing until it's fixed.
---

# Theory of Constraints

## Overview

The Theory of Constraints (TOC), from Eliyahu Goldratt's "The Goal," says a throughput-limited system has exactly one constraint setting its rate. Optimizing anything else is wasted effort—often counterproductive. Find the bottleneck, exploit it, subordinate everything else to it, and only then elevate it.

**Core Principle:** A chain is only as strong as its weakest link. Strengthening any other link does nothing.

## When to Use

- Latency optimization where one stage dominates the time budget
- Throughput optimization where one stage caps the rate
- A pipeline where work piles up before one specific stage

```
Trying to improve latency/throughput?
  → Have you identified the constraint? → no → FIND THE CONSTRAINT FIRST
  → Are you optimizing a non-constraint? → yes → STOP, FOCUS ON CONSTRAINT
  → Is the constraint working at 100%?   → no → EXPLOIT BEFORE ELEVATING
```

## When NOT to Use

- **No single stage dominates** (latency/load is spread roughly evenly, or many stages are near 100%) → there is no one constraint to exploit. Use `thinking-systems` to model the interactions instead.
- The problem is correctness, not throughput → this is the wrong lens; debug the fault.
- The bottleneck is already obvious and cheap to fix → just fix it; skip the five steps.
- "Bottleneck" shifts every run (it's contention/coupling, not a fixed stage) → that's a systems problem, not a constraint.

## The Five Focusing Steps

### Step 1: Identify the Constraint

Find the one thing limiting the system:

```markdown
## Constraint Identification

System: Software delivery pipeline

Potential constraints:
| Stage | Capacity | Utilization | Queue Time |
|-------|----------|-------------|------------|
| Requirements | 10/week | 60% | 0 days |
| Development | 8/week | 95% | 3 days |
| Code Review | 5/week | 100% | 5 days |←CONSTRAINT
| Testing | 12/week | 40% | 0 days |
| Deployment | 20/week | 20% | 0 days |

Constraint: Code Review
Evidence: 100% utilization, 5-day queue, lowest throughput
```

**How to find the constraint:**
- Highest utilization
- Longest queue/wait time
- Lowest throughput rate
- Where work piles up
- What people complain about waiting for

### Step 2: Exploit the Constraint

Get maximum output from the constraint without spending money:

```markdown
## Exploiting the Constraint

Constraint: Code Review (5/week capacity)

Exploitation strategies:
| Strategy | Effort | Impact |
|----------|--------|--------|
| Never let reviewers wait for reviewable PRs | Low | +10% |
| Batch small PRs together | Low | +15% |
| Clear review criteria to reduce back-and-forth | Low | +20% |
| Prioritize reviews over other reviewer work | Medium | +10% |
| Remove unnecessary review requirements | Low | +15% |

Total potential: 5/week → 8/week (60% increase, no new resources)
```

**Exploitation questions:**
- Is the constraint ever idle? Why?
- Is the constraint doing any unnecessary work?
- Is the constraint's output ever wasted downstream?
- Can we reduce setup/changeover time?
- Can we improve quality at the constraint (less rework)?

### Step 3: Subordinate Everything Else

Non-constraints should serve the constraint:

```markdown
## Subordination

Every other stage should optimize FOR code review, not for itself.

Requirements:
- DON'T: Maximize requirement throughput
- DO: Pace requirements to match code review capacity
- DO: Ensure requirements are clear (reduce review iterations)

Development:
- DON'T: Maximize development output
- DO: Produce review-ready code at the rate review can handle
- DO: Spend extra time on clarity (save reviewer time)

Testing:
- DON'T: Maximize testing efficiency
- DO: Be ready to test immediately when reviews complete
- DO: Provide feedback that helps reviewers learn

Counter-intuitive: Keeping developers busy beyond review capacity
                   creates work-in-progress that HURTS throughput
```

**Subordination principle:**
Local optimization of non-constraints often hurts global throughput. A 100% utilized developer feeding a 100% utilized reviewer creates a queue that slows everything.

### Step 4: Elevate the Constraint

If exploitation isn't enough, invest in increasing constraint capacity:

```markdown
## Elevating the Constraint

Current constraint capacity: 8/week (after exploitation)
Required capacity: 12/week

Elevation options:
| Option | Cost | Capacity Gain |
|--------|------|---------------|
| Hire dedicated reviewer | $150K/year | +4/week |
| Train more reviewers | $10K training | +2/week |
| Adopt review tooling | $5K/year | +1/week |
| Pair reviewing | Process change | +3/week |

Recommendation: Training + tooling first ($15K for +3/week)
                Then hire if still insufficient
```

**Elevation timing:**
Only elevate after exploitation is maxed out. Elevating is expensive; exploitation is cheap.

### Step 5: Prevent Inertia (Go Back to Step 1)

When you elevate, the constraint often moves:

```markdown
## Constraint Movement

Before: Code Review was constraint (5/week)
After elevation: Code Review does 12/week

New constraint search:
| Stage | Capacity | Utilization |
|-------|----------|-------------|
| Requirements | 10/week | 100% | ←NEW CONSTRAINT
| Development | 15/week | 80% |
| Code Review | 12/week | 80% |
| Testing | 12/week | 100% | ←OR THIS ONE |

System bottleneck moved—repeat the process.
```

## Finding Constraints

### Types of Constraints

| Type | Examples | How to Find |
|------|----------|-------------|
| Physical | Machine capacity, server limits | Utilization metrics |
| Policy | Approval requirements, rules | Process analysis |
| Market | Customer demand | Sales/pipeline data |
| Time | Fixed deadlines | Schedule analysis |
| Knowledge | Expert availability | Skill matrix |

### Constraint Indicators

```
Signs of a constraint:
✓ Work queues up before this stage
✓ Downstream stages have idle time
✓ Increasing input doesn't increase output
✓ This stage is always at full capacity
✓ Small improvements here have large system effects

Signs of a non-constraint:
✓ Often has idle time
✓ Improvement has no system effect
✓ Work flows through without queuing
```

## TOC Application Patterns

### Performance Optimization

```markdown
## System Performance Analysis

Request flow:
API Gateway → Auth → App Logic → Database → Response

Latency breakdown:
| Component | Latency | % of Total |
|-----------|---------|------------|
| API Gateway | 5ms | 2% |
| Auth | 10ms | 4% |
| App Logic | 30ms | 12% |
| Database | 200ms | 80% | ←CONSTRAINT
| Response | 5ms | 2% |

Constraint: Database

Wrong approach: Optimize app logic (12% of latency)
Right approach: Focus 100% on database optimization
                Query optimization, caching, indexing, read replicas
```

### Batch/Data Pipeline Throughput

```markdown
## Pipeline Throughput Analysis

Stage flow:
Ingest → Parse → Transform → Enrich (external API) → Write

Throughput analysis:
| Stage | Rate (rec/s) | Utilization |
|-------|--------------|-------------|
| Ingest | 50,000 | 20% |
| Parse | 30,000 | 35% |
| Transform | 20,000 | 50% |
| Enrich (external API) | 2,000 | 100% | ←CONSTRAINT
| Write | 40,000 | 25% |

System throughput is capped at 2,000 rec/s by the enrichment call.
Parallelizing parse/transform does nothing—it just grows the queue before Enrich.

Exploit: batch the API calls, cache repeat lookups, drop redundant enrichments.
Subordinate: pace upstream stages to 2,000 rec/s; don't build WIP.
Elevate (only if exploit insufficient): add API concurrency / a second provider.
```

### Concurrency / Lock Contention

```markdown
## Contention Analysis

Symptom: throughput plateaus far below CPU capacity.

| Resource | Wait time | Notes |
|----------|-----------|-------|
| CPU | low | cores idle |
| Global mutex | HIGH | every request serializes here | ←CONSTRAINT
| DB pool | low | |

The single hot lock is the constraint; adding workers makes contention worse.
Exploit: shorten the critical section to the minimum.
Elevate: shard the lock / switch to a lock-free or per-key structure.
```

## Theory of Constraints Template

```markdown
# TOC Analysis: [System/Process]

## System Definition
What flows through this system: [Work items, requests, features]
Goal: [What throughput matters]

## Constraint Identification

| Stage | Capacity | Utilization | Queue Time | Throughput |
|-------|----------|-------------|------------|------------|
| | | | | |

**Identified Constraint:** [Stage]
**Evidence:** [Why this is the constraint]

## Step 2: Exploit

How to maximize constraint output without investment:
| Exploitation | Effort | Expected Gain |
|--------------|--------|---------------|
| | | |

## Step 3: Subordinate

How should non-constraints support the constraint?
| Stage | Current Behavior | Should Change To |
|-------|------------------|------------------|
| | | |

## Step 4: Elevate (if needed)

If exploitation isn't sufficient:
| Elevation Option | Cost | Capacity Gain |
|------------------|------|---------------|
| | | |

## Step 5: Next Constraint

After elevation, where will the constraint move?
[Prediction]
```

## Verification Checklist

- [ ] Identified the single constraint (not multiple "bottlenecks")
- [ ] Have data supporting the constraint identification
- [ ] Maximized exploitation before considering elevation
- [ ] Non-constraints are subordinated (not locally optimized)
- [ ] Not investing in non-constraint improvements
- [ ] Monitoring for constraint movement

## Key Questions

- "What's the ONE thing limiting throughput?"
- "Is the constraint ever idle? Why?"
- "Are we improving a non-constraint while ignoring the constraint?"
- "Are non-constraint improvements building inventory?"
- "What should the rest of the system do to serve the constraint?"
- "If we improve this, where will the constraint move?"

## Goldratt's Wisdom

"Every action that brings the company closer to its goal is productive. Every action that does not bring a company closer to its goal is not productive."

"An hour lost at a bottleneck is an hour lost forever. An hour saved at a non-bottleneck is a mirage."

"The sum of local optimums is not equal to the global optimum."

Optimizing everywhere is the same as optimizing nowhere. Find the constraint. Make it work. That's all that matters until the constraint moves.
