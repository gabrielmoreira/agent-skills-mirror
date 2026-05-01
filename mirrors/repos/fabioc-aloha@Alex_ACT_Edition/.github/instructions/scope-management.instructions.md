---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Scope management and feature creep prevention — ship the right thing, not everything"
application: "When planning work, evaluating changes, or noticing scope expansion"
applyTo: "**/*scope*,**/*plan*,**/*mvp*,**/*feature*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Scope Management

> "A good project ships. A perfect project ships never."

Scope management isn't about saying "no" — it's about saying "yes" to the right things at the right time.

## Scope Creep Detection

| Signal | Example | Response |
|--------|---------|----------|
| **Feature addition** | "While we're at it..." | "Great for v2. Let's capture it." |
| **Perfectionism** | "It's not quite right yet..." | "What's the minimum that solves the problem?" |
| **Edge cases** | "What if someone does X?" | "How common is X? Handle the 80% first." |
| **Gold plating** | "Users might want..." | "Have users asked, or are we guessing?" |
| **Endless research** | "We should investigate more..." | "What decision does this enable?" |

## MoSCoW Prioritization

| Priority | Meaning | Criteria |
|----------|---------|----------|
| **Must** | Critical path | Won't work without it |
| **Should** | Important | Significant value, but workaround exists |
| **Could** | Nice to have | Adds polish, not essential |
| **Won't** | Out of scope | Explicitly excluded (for now) |

## Negotiation Patterns

### Capture & Defer
>
> "Great idea. Adding to Phase 2 backlog. Ship core first."

### Trade-Off
>
> "We can add X, but something comes out. Options: (A) Add X, defer Y. (B) Add X, extend timeline. (C) Keep scope, backlog X."

### MVP Challenge
>
> "If we shipped today with just this, would users get value? If yes, we're at MVP."

### 80/20 Cut
>
> "This handles 80%. The remaining 20% is complex. Ship, gather feedback, then decide."

## Definition of Done

Before starting, define what "done" means:

```markdown
## MVP: [Feature]

### Must Have (Ship-blocking)
- [ ] Core functionality

### Won't Have (Explicitly v2)
- [ ] Future ideas

### Done When
- [ ] Specific, measurable criteria
```

Without a definition of done, scope will expand to fill available time.
