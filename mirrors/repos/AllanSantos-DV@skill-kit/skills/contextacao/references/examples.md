# Analysis Examples — Good vs. Bad

Reference for distinguishing real context analysis from shallow analysis (compliance theater).

---

## Scenario: "Create a skill for automated deployment"

### ❌ BAD Analysis (theater)

#### Assumptions
| # | Assumed premise | Verified? | Risk if false |
|---|-----------------|-----------|---------------|
| 1 | The team needs automated deployment | No | Low |
| 2 | They use CI/CD | No | Medium |

**Why it's bad**: generic questions that could apply to any subject. Didn't question ANYTHING specific to the context. "Low risk" without justification. Filled the table to comply with the protocol.

---

### ✅ GOOD Analysis (real)

#### Assumptions
| # | Assumed premise | Verified? | Risk if false |
|---|-----------------|-----------|---------------|
| 1 | The problem is deployment itself, not configuration drift between environments | ❌ | **High** — if the real problem is config drift, the skill should be about environment standardization, not deployment |
| 2 | The team already has a working CI/CD pipeline and wants to automate the last stretch | ❌ | **High** — if they don't have CI/CD, a deployment skill is premature |
| 3 | The environments (dev/staging/prod) have infrastructure parity | ❌ | **Medium** — if they don't, automated deployment will fail in prod even if it works in dev |

**Why it's good**: questions whether the original request ("deployment") is really the problem. Identifies that the root cause may be something else (5 Whys). Each assumption has a justified risk with concrete consequences.

---

## Scenario: "I need an authentication API"

### ❌ BAD Analysis

> Dependencies: JWT, database, web framework.
> Confidence: 🟢 — I know authentication well.

**Why it's bad**: listed generic technologies without questioning context. "I know it well" is exactly the overconfidence that leads to errors. Didn't ask: OAuth2 or API Key? Multi-tenant? GDPR/LGPD compliance? Is there existing legacy authentication?

---

### ✅ GOOD Analysis

> **Assumptions**:
> - I'm assuming this is a new authentication system (greenfield), but it could be a legacy system migration — if so, the scope changes completely
> - I'm assuming JWT is acceptable, but if there's a requirement for instant session revocation, pure JWT doesn't meet the need
>
> **Knowledge**:
> | Knowledge | Source | Confidence | Action |
> |---|---|---|---|
> | OAuth2/OIDC standards | Training | 🟡 | Specs update — check latest RFC |
> | Compliance requirements (GDPR, SOC2) | Unknown | 🔴 | Ask user if there are regulatory requirements |
> | Existing infrastructure (API Gateway, IdP) | Unknown | 🔴 | Without this info, any architecture is a guess |

**Why it's good**: questions whether the obvious assumption (greenfield) is correct. Flags a concrete technical limitation (JWT vs. revocation). Classifies confidence with specific justification, not generic. Identifies that without knowing the current infrastructure, proposing architecture is guesswork.

---

## Signs of bad analysis (checklist)

- [ ] Tables filled with generic text that could apply to any subject
- [ ] All risks classified as "Low" or "Medium" without justification
- [ ] Confidence 🟢 everywhere without mentioning model limitations
- [ ] No questions asked to the user
- [ ] No assumption that, if false, would change the approach
- [ ] Zero mention of "I don't know" or "I need to consult"

## Signs of good analysis (checklist)

- [x] At least 1 assumption that, if false, invalidates the entire approach
- [x] At least 1 item classified as 🔴 (if everything is 🟢, it's probably overconfidence)
- [x] Context-specific questions, not generic ones
- [x] Explicit declaration of what the model doesn't know
- [x] Concrete consequences for each risk (not just "could cause problems")
- [x] Recommendation to stop or consult when confidence is low

---

## Real Cases

Examples captured from real usage of the skill. These progressively replace the hypothetical examples above as the skill is used.

_No real cases recorded yet._

<!-- Format per case:
### [DATE] — [SUBJECT] — ✅ Good / ❌ Bad
**Context**: [what was requested]
**What the analysis did well / poorly**: [detail]
**Relevant excerpt from the analysis**: [copy the part that exemplifies]
-->
