---
type: skill
lifecycle: stable
inheritance: inheritable
name: "scope-management"
description: Recognize scope creep, suggest MVP cuts, and manage project boundaries
tier: standard
applyTo: '**/*scope*,**/*management*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Scope Management Skill


Recognize scope creep, suggest MVP cuts, and help maintain healthy project boundaries. The art of delivering the right thing, not everything.

## Core Philosophy

> "A good project ships. A perfect project ships never."

Scope management isn't about saying "no" — it's about saying "yes" to the right things at the right time.

## Scope Creep Detection

### Warning Signs

| Signal | Indicator | Response |
|--------|-----------|----------|
| **Feature addition** | "While we're at it, let's also..." | "That's a great idea — for v2. Let's capture it." |
| **Perfectionism** | "It's not quite right yet..." | "What's the minimum that solves the problem?" |
| **Edge cases** | "What if someone does X?" | "How common is X? Let's handle the 80% first." |
| **Gold plating** | "Users might want..." | "Have users asked for this, or are we guessing?" |
| **Unclear boundaries** | "This might be useful..." | "Let's define done before adding more." |
| **Endless research** | "We should investigate more..." | "What decision does this research enable?" |

### Scope Creep Patterns

```
HEALTHY SCOPE:
┌──────────────────────────────────────┐
│  ✅ Core Feature                     │
│  ✅ User Need                        │
│  ✅ MVP Requirement                  │
│  ----------------------------------- │
│  📋 Phase 2 (captured, not now)     │
└──────────────────────────────────────┘

SCOPE CREEP:
┌──────────────────────────────────────┐
│  ✅ Core Feature                     │
│  ⚠️ "Nice to have"                   │
│  ⚠️ Edge case handling               │
│  ⚠️ Extra polish                     │
│  ⚠️ "While we're here..."           │
│  ❌ Gold plating                     │
│  ❌ Premature optimization           │
└──────────────────────────────────────┘
```

## MVP Definition Framework

### The MoSCoW Method

| Priority | Meaning | Criteria |
|----------|---------|----------|
| **Must have** | Critical path | Won't work without it |
| **Should have** | Important | Significant value, but workaround exists |
| **Could have** | Nice to have | Adds polish, not essential |
| **Won't have** | Out of scope | Explicitly excluded (for now) |

### MVP Checklist

```markdown
## MVP Definition: [Feature/Project]

### Must Have (Ship-blocking)
- [ ] [Core functionality 1]
- [ ] [Core functionality 2]

### Should Have (Target for v1.0)
- [ ] [Important enhancement 1]
- [ ] [Important enhancement 2]

### Could Have (If time permits)
- [ ] [Nice to have 1]
- [ ] [Nice to have 2]

### Won't Have (Explicitly v2+)
- [ ] [Future idea 1]
- [ ] [Future idea 2]

### Definition of Done
[ ] [Specific, measurable completion criteria]
```

## Scope Negotiation Patterns

### 1. The Capture & Defer

When someone suggests additions:

```
"That's a great idea. Let me add it to the backlog for Phase 2 
so we don't lose it. For now, let's ship the core first."
```

### 2. The Trade-Off

When scope must grow:

```
"We can add X, but something needs to come out to keep the timeline.
Options:
A) Add X, defer Y to next release
B) Add X, extend timeline by Z days
C) Keep current scope, add X to backlog

Which works best for stakeholders?"
```

### 3. The MVP Challenge

When features keep adding:

```
"Quick check: If we shipped today with just what we have,
would users get value? If yes, maybe we're already at MVP."
```

### 4. The 80/20 Cut

When perfectionism strikes:

```
"This handles the 80% case. The remaining 20% is complex.
Ship now, gather feedback, then decide if the 20% is worth it?"
```

### 5. The Parking Lot

For good ideas at bad times:

```
"Great idea but out of scope for this sprint. 
Added to the parking lot — we'll prioritize it next planning."
```

## Complexity Assessment

### Scope Health Check

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| **Requirements** | Stable | 1-2 changes/week | Daily changes |
| **Timeline** | On track | Slipping | Blown |
| **Team confidence** | High | Uncertain | Low |
| **Stakeholder alignment** | Clear | Some confusion | Conflicting |
| **Done definition** | Specific | Vague | Missing |

### Complexity Score

Calculate scope complexity:

```
Base features:     ___ × 1 point  = ___
Integrations:      ___ × 2 points = ___
Edge cases:        ___ × 1 point  = ___
New technologies:  ___ × 3 points = ___
Dependencies:      ___ × 2 points = ___
                   ─────────────────────
                   TOTAL:           ___

0-10:  Simple — ship fast
11-25: Moderate — careful planning
26+:   Complex — consider splitting
```

## Scope Reduction Tactics

### When Scope Must Shrink

1. **Cut features, not quality**: Remove whole features vs. half-implementing many
2. **Reduce polish**: Good enough > perfect
3. **Hardcode first**: Configuration can come later
4. **Manual before automated**: Prove value, then optimize
5. **Single platform**: Ship on one, expand later
6. **Invite-only**: Smaller user base = smaller scope

### Questions to Ask

| Question | If Yes → |
|----------|----------|
| "Does this block launch?" | Keep it |
| "Can users workaround this?" | Defer it |
| "Is this proven valuable?" | Keep if proven |
| "Are we guessing about need?" | Validate first |
| "Can this be added later?" | Defer it |
| "Will this delay other must-haves?" | Defer it |

## Session Protocol

### When to Invoke Scope Management

1. **Project kickoff**: Define MVP boundaries upfront
2. **Feature requests**: Evaluate fit against scope
3. **Timeline pressure**: Identify cutting candidates
4. **Complexity growth**: Assess scope health
5. **Before release**: Final scope check

### Scope Check Command

```
/scopecheck

Output:
📊 Scope Health Report

Current scope: 12 features
- Must have: 5 ✅
- Should have: 4 🔄
- Could have: 3 ⏳

Complexity score: 18 (Moderate)
Recommendation: Consider deferring 2 "could have" items
to hit timeline with confidence.
```

## Integration Points

### With Other Skills

- **proactive-assistance**: Detect scope growth, offer check
- **status-reporting**: Include scope health in updates
- **alex-effort-estimation**: Scope impacts estimates
- **project-management**: Backlog management

### Triggers for This Skill

- "scope creep", "adding features"
- "what's MVP", "minimum viable"
- "can we cut", "reduce scope"
- "too much", "won't finish"
- Feature list growing
- Timeline pressure

## Red Flags (Automatic Alert)

Alert when:

- Requirements change > 2x per week
- "Must have" list grows after kickoff
- No explicit "Won't have" list
- Definition of done is missing/vague
- Same feature discussed > 3 times

## Metrics

- **Scope stability**: Changes per week
- **MVP adherence**: % of original scope shipped
- **Creep capture rate**: % of additions parked for later
- **Ship rate**: Projects that actually ship

---

## Related Skills

- [proactive-assistance](..\proactive-assistance/SKILL.md) — Detect scope growth early
- [status-reporting](..\status-reporting/SKILL.md) — Report scope health
- [alex-effort-estimation](..\alex-effort-estimation/SKILL.md) — Scope affects estimates
- [project-management](..\project-management/SKILL.md) — Overall project tracking

---

*Ship small, ship often, ship something.*
