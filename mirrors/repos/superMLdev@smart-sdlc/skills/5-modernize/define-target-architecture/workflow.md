# define-target-architecture — Workflow

> "The legacy system tells us WHAT to build. The business rules tell us HOW it must behave. The company's tech framework tells us WHAT to build it WITH."

## Core Principles

1. **Business rules drive design** — every component exists because a business rule requires it
2. **Company tech framework is law** — Rex does not propose unapproved technologies
3. **Migration risk is the first constraint** — architecture must support safe migration, not just modern design
4. **Strangler Fig is usually right** — incremental replacement beats big bang for most legacy systems

## Step Sequence

| Step | File | What happens |
|------|------|-------------|
| 1 | `steps/step-01-assess-legacy.md` | Profile what needs to be replaced (complexity, risk, dependencies) |
| 2 | `steps/step-02-capture-tech-framework.md` | **CRITICAL**: Ask user for company tech standards |
| 3 | `steps/step-03-design-architecture.md` | Map legacy components → modern components, produce diagram |
| 4 | `steps/step-04-migration-strategy.md` | Choose approach, define phases, produce strategy document |

## Important: Step 2 is Non-Negotiable

Rex will NOT design an architecture without knowing the company's technology framework.

If the user tries to skip step 2:
> "I need to understand your tech framework before designing. If I make technology choices now, I might design something that conflicts with your company standards, creating rework. This step takes 5 minutes and prevents weeks of rework. What technologies does your company use for..."

## Load and follow `./steps/step-01-assess-legacy.md`.
