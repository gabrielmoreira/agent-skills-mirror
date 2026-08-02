---
name: risk-analysis
description: Probability × impact risk assessment for curation and planning decisions. Categorize risks (quality, coherence, scope creep, token budget, breaking change, staleness), score by likelihood × impact, and route by risk score to ship / gate / ADR. Use before shipping a change, when accepting an external artifact, when running a pre-release gate, or when triaging findings.
lastReviewed: 2026-07-31
---

# Curation Risk Analysis

> **ACT Tenet VI**: Match rigor to stakes. Reversible decisions deserve speed; irreversible ones deserve doubt.

Applied to curation work: accepting a bad skill is reversible (revert next patch). Shipping a broken release to consumers is expensive to undo.

## Risk Categories (Curation-Specific)

| Category | Examples |
|----------|----------|
| **Quality** | Skill has bugs, stale references, or misleading content |
| **Coherence** | New content conflicts with existing brain architecture |
| **Scope creep** | Feature belongs in a different repo or surface (not Edition / Mall / Supervisor) |
| **Token budget** | Addition pushes Edition past 25K instruction budget |
| **Breaking change** | Rename/remove that breaks heir upgrades |
| **Staleness** | Store/skill stays past its useful life, misleading by presence |

## Risk Matrix for Curation Decisions

| | Low Impact | Medium Impact | High Impact |
|---|-----------|---------------|-------------|
| **High Likelihood** | Ship with note | Gate on review | Full ACT pass + ADR |
| **Medium Likelihood** | Ship | Ship with note | Gate on review |
| **Low Likelihood** | Ship | Ship | Ship with note |

### Impact Calibration for This Repo

| Level | Curation Impact |
|-------|-----------------|
| **High** | Breaks heir upgrades, violates Cardinal Rule, token budget breach |
| **Medium** | Quality gap ships to heirs, coherence drift, stale reference |
| **Low** | Cosmetic issue, suboptimal wording, minor inconsistency |

### Likelihood Calibration

| Level | Probability | Curation Signal |
|-------|-------------|-----------------|
| **High** | >60% | Multiple heirs affected, or same issue seen before |
| **Medium** | 20-60% | Plausible failure mode, no prior occurrence |
| **Low** | <20% | Theoretical risk, strong mitigations in place |

## Decision Routing by Risk Score

| Score (L×I) | Route |
|-------------|-------|
| Low × Low | Ship immediately, log in curation-log |
| Any Medium | Ship with trimmed ACT pass visible in curation-log |
| Any High | Full ACT pass, write ADR, require explicit approval |
| High × High | Surface as ADR + direct Fabio conversation before acting |

## Risk Register (Running)

Maintained in your project's audit trail (Alex ACT itself uses `operations/ledgers/brain-qa-changelog.md`) — every entry carries implicit risk assessment via the Severity column. Explicit risk registers warranted only for:

- Release candidates (per your project's release process)
- Adopting an external artifact that scored below your project's acceptance bar
- Structural changes to your project's brain architecture

## Would Revise If

Revise by **2026-08-26** (90 days) or sooner if any of the following fires:

- The risk matrix produces no differentiation (everything routes to "Ship with note") across 10+ curation decisions in a quarter
- A curation decision that scored Low×Low ships and produces fleet-breaking impact ≥1 time (impact calibration too lax)
- A High×High decision is over-routed to ADR when a trimmed pass would have sufficed ≥3 times in a quarter (rigor calibration too tight)
- The Likelihood/Impact tables drift from observed reality (most "High Likelihood" rows turn out Low) ≥3 times in a quarter
