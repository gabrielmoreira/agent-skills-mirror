---
type: skill
lifecycle: stable
inheritance: inheritable
name: inclusive-language
description: >-
tier: standard
applyTo: '**/*deployment*,**/*inclusive*,**/*language*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Inclusive Language Guide

## Banned Terms — Replace Immediately

| Banned Term | Preferred Alternative | Context |
|-------------|----------------------|---------|
| whitelist | **allowlist**, permit list | Access control, filtering |
| blacklist | **blocklist**, deny list | Access control, filtering |
| master/slave | **primary/replica**, leader/follower | Databases, distributed systems |
| master (branch) | **main**, default, trunk | Git branches |
| grandfathered | **legacy**, pre-existing, exempt | Policy exceptions |
| sanity check | **smoke test**, confidence check | Testing |
| dummy (value) | **placeholder**, sample, stub | Test data |
| man-hours | **person-hours**, engineering hours | Estimation |

## Collaborative Framing

When extracting content from meetings, reframe competitive language:

| Avoid | Use Instead |
|-------|-------------|
| "competitive advantage" | "opportunity to lead", "differentiation" |
| "first-mover advantage" | "early adoption", "iteration speed" |
| "out-innovate" | "move quickly", "iterate faster" |
| "beat [team X]" | "lead in", "set the standard for" |
| "protect our work" | "share our approach", "make it easy to adopt" |

## AI Agent Rules

- **Never generate** code, comments, or docs containing banned terms
- **When editing files** containing banned terms, replace them in the same edit
- **When reviewing PRs**, flag banned terms with same severity as security concerns
- **Variable/function/class names** must use inclusive alternatives

