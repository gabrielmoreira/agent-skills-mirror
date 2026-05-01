---
name: elicitation
description: "Advanced requirements elicitation using five-whys, assumption surfacing, and stakeholder mapping. Use when the user says 'help me think this through', 'I'm not sure what I want', or 'elicitation'."
---

# Requirements Elicitation

## Goal

Surface the real requirements, unstated assumptions, and true stakeholders behind a vague or partially-formed idea — before committing to building the wrong thing.

---

## Activation

Ask: "What do you want to explore? Share whatever you have — even rough notes or vague ideas."

---

## Technique 1: Five Whys

For every stated goal or requirement, apply:
1. "Why do you want {X}?"
2. "And why is {answer} important?"
3. "Why is that the case?"
4. "What drives that need?"
5. "If you could only solve one underlying problem, what is it?"

Present the chain:
```
Why? → {answer}
  Why? → {answer}
    Why? → {answer}
      Root cause: {core need}
```

⏸️ **STOP** — confirm the root cause resonates.

---

## Technique 2: Assumption Surfacing

Generate assumptions behind the stated need:

**Prompt**: "Let me surface the assumptions embedded in what you've described."

Categories:
- **Customer assumptions**: Who actually has this problem? How many? How often?
- **Solution assumptions**: Does {proposed solution} actually solve the root cause?
- **Market assumptions**: Are competitors already solving this? Why would users switch?
- **Technical assumptions**: Can this be built with current tech? At what cost?
- **Business assumptions**: Will this generate value? How?

For each assumption, rate:
- Certainty: Proven / Likely / Uncertain / Unknown
- Impact if wrong: High / Medium / Low

Highlight: "Your riskiest assumption is: {assumption}. How would you test it cheaply?"

⏸️ **STOP** — walk through the assumptions together.

---

## Technique 3: Stakeholder Mapping

Ask: "Who is affected by this — directly or indirectly?"

Map:
| Stakeholder | Interest | Power | Concern |
|-------------|----------|-------|---------|
| [Primary User] | High | Low | ... |
| [Decision Maker] | Medium | High | ... |
| [Affected Party] | Low | Low | ... |

Identify:
- **Champions**: who will advocate for this?
- **Blockers**: who might resist or veto?
- **Forgotten voices**: who are you not thinking about?

⏸️ **STOP** — confirm stakeholder list is complete.

---

## Technique 4: Boundary Conditions

Push on the limits of the requirement:
- "What's the minimum version that would be useful?" (MVP)
- "What would make this fail completely?"
- "What's explicitly out of scope?"
- "What happens at 10x scale?"
- "What happens when the user does something unexpected?"

---

## Output

Produce a requirements elicitation summary:

```markdown
## Elicitation Summary — {topic}

### Root Need
[The real underlying problem, found through five-whys]

### Key Assumptions to Validate
| Assumption | Certainty | Impact if Wrong | Validation Approach |
|------------|-----------|-----------------|---------------------|

### Stakeholders
| Role | Interest | Key Concern |
|------|----------|-------------|

### Scope Boundaries
- In scope: ...
- Out of scope: ...
- MVP: ...
```

Offer:
> "Should I turn this into a Product Brief (`product-brief`) or a PRD (`create-prd`)?"
