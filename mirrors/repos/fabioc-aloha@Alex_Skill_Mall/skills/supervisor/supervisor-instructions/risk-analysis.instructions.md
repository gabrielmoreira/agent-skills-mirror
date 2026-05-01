---
type: instruction
lifecycle: stable
inheritance: master-only
description: "Risk assessment for curation decisions — probability × impact scoring for skill acceptance, store pruning, and release gating"
application: "When making curation decisions that affect the Edition brain or Skill Mall"
applyTo: "**/*risk*,**/*plan*,**/*assess*,**/decisions/**,**/feedback/**"
currency: 2026-04-30
lastReviewed: 2026-01-01
---

# Curation Risk Analysis

> **ACT Tenet VI**: Match rigor to stakes. Reversible decisions deserve speed; irreversible ones deserve doubt.

Applied to Supervisor curation: accepting a bad skill is reversible (revert next patch). Shipping a broken release to 5+ heirs is expensive to undo.

## Risk Categories (Curation-Specific)

| Category | Examples |
|----------|----------|
| **Quality** | Skill has bugs, stale references, or misleading content |
| **Coherence** | New content conflicts with existing brain architecture |
| **Scope creep** | Feature belongs in AlexMaster or a different repo |
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
| High × High | Escalate to AlexMaster per escalation-rules |

## Risk Register (Running)

Maintained in `decisions/curation-log.md` — every entry carries implicit risk assessment via the Severity column. Explicit risk registers warranted only for:

- Release candidates (use `/cut-release` prompt)
- Store additions scoring <8/10 on store-evaluation
- Structural changes to Edition brain architecture
