# fetch-violations

Query S360 Kusto for SFI-TI3.2.2 tenant isolation violations, classify by ViolationTitle, flag autofix-eligible items for downstream remediation

## Quick Facts

| Field | Value |
| --- | --- |
| **Category** | security-privacy |
| **Shape** | `.S..` |
| **Tier** | standard |
| **Token cost** | ~3356 tokens |
| **Engines** | copilot |
| **Requires Edition** | >=1.0.0 |
| **Keywords** | fetch, violations, query, s360, kusto, sfi-ti322, tenant, isolation |

## Installation

From ACT Edition:

```text
/mall install fetch-violations
```

Or manually copy the plugin contents to `.github/skills/local/fetch-violations/`.

## Artifacts

- **skill**: `SKILL.md`

## Shape: `.S..`

Skill only -- domain knowledge loaded when pattern matches.
