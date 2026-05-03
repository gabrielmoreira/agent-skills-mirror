---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Universal creative loop — Ideate, Plan, Build, Test, Release, Improve — applies to all creative work"
application: "When creating anything: code, documents, designs, solutions"
applyTo: "**/*creat*,**/*ideate*,**/*design*,**/*build*,**/*plan*,**/*scope*,**/*project*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Creative Loop

All creative work follows the same loop. Know where you are; do the right work for that stage.

## The Loop

```
IDEATE → PLAN → BUILD → TEST → RELEASE → IMPROVE
   ↑                                         │
   └─────────────────────────────────────────┘
```

| Stage | Question | Output |
|-------|----------|--------|
| **IDEATE** | What problem are we solving? | Problem statement, goals, constraints |
| **PLAN** | How will we solve it? | Architecture, approach, phases, trade-offs |
| **BUILD** | Does it work? | Working implementation |
| **TEST** | Does it work correctly? | Verified behavior, edge cases covered |
| **RELEASE** | Is it ready for users? | Deployed, documented, announced |
| **IMPROVE** | What did we learn? | Retrospective, next iteration seeds |

## Stage Detection

Before acting, identify which stage the work belongs to:

| User Signal | Likely Stage |
|-------------|--------------|
| "I want to...", "What if...", "How might we..." | IDEATE |
| "How should we...", "Design...", "Architect..." | PLAN |
| "Implement...", "Build...", "Create...", "Code..." | BUILD |
| "Test...", "Verify...", "Does this work...", "Debug..." | TEST |
| "Ship...", "Deploy...", "Publish...", "Release..." | RELEASE |
| "What went wrong...", "How can we improve...", "Next time..." | IMPROVE |

## Stage Discipline

**Don't skip stages.** Each stage produces artifacts the next stage needs.

| Skip | Consequence |
|------|-------------|
| IDEATE → BUILD | Building the wrong thing |
| PLAN → BUILD | Rework, scope creep, dead ends |
| BUILD → RELEASE | Shipping bugs |
| RELEASE → IDEATE | Repeating mistakes |

**Don't mix stages.** Ideation is divergent; building is convergent. Mixing them produces paralysis.

| Anti-Pattern | Fix |
|--------------|-----|
| Planning while building | Finish the plan first; build to the plan |
| Testing while building | Build the feature, then test it systematically |
| Improving while releasing | Ship first, retrospect after |

## Stage-Appropriate Behaviors

### IDEATE

- Diverge: generate many options
- Don't commit: ideas are cheap
- Question assumptions
- Research before deciding

### PLAN

- Converge: pick an approach
- Document trade-offs
- Define success criteria
- Identify risks

### BUILD

- Execute the plan
- Don't redesign mid-build
- Note issues for IMPROVE, don't fix everything now
- Commit frequently

### TEST

- Systematic verification
- Cover edge cases
- Don't add features
- Document failures

### RELEASE

- Final validation
- Documentation complete
- Announce to users
- Monitor for issues

### IMPROVE

- Retrospect honestly
- Capture learnings
- Feed insights back to IDEATE
- Update processes

## Integration with ACT

The creative loop is where ACT applies:

| Stage | ACT Application |
|-------|-----------------|
| IDEATE | Generate alternative problem framings (Tenet I) |
| PLAN | Question your assumptions (Tenet IV) |
| BUILD | Calibrate confidence on implementation (Tenet III) |
| TEST | Falsifiability — what would prove this wrong? (Tenet V) |
| RELEASE | Self-correct before shipping (Tenet VI) |
| IMPROVE | Apply ACT to ACT itself (Tenet X) |
