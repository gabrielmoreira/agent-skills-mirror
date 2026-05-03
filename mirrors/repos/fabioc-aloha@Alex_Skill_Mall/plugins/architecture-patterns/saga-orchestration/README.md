# saga-orchestration

Implement saga patterns for distributed transactions and cross-aggregate workflows. Use this skill when implementing distributed transactions across microservices where 2PC is unavailable, designing compensating actions for failed order workflows that span inventory, payment, and shipping services, building event-driven saga coordinators for travel booking systems that must roll back hotel, flight, and car rental reservations atomically, or debugging stuck saga states in production where compensation steps never complete.

## Quick Facts

| Field | Value |
| --- | --- |
| **Category** | architecture-patterns |
| **Shape** | `.S..` |
| **Tier** | standard |
| **Token cost** | ~4331 tokens |
| **Engines** | copilot |
| **Requires Edition** | >=1.0.0 |
| **Keywords** | saga, orchestration, implement, patterns, distributed, transactions, cross-aggregate, workflows |

## Installation

From ACT Edition:

```text
/mall install saga-orchestration
```

Or manually copy the plugin contents to `.github/skills/local/saga-orchestration/`.

## Artifacts

- **skill**: `SKILL.md`

## Shape: `.S..`

Skill only -- domain knowledge loaded when pattern matches.
