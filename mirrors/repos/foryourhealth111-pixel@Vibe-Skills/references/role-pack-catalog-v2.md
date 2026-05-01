# Role Pack Catalog v2

The catalog captures reusable roles after deduplication against existing VCO governance roles.

| Role | Upstream pattern | Required boundary note |
|---|---|---|
| `planner` | agent-squad planning lead | cannot own routing or release decisions |
| `implementer` | coding worker / builder | bounded write scope and explicit done definition |
| `critic` | review / challenge role | advisory only, no merge authority |
| `handoff-coordinator` | subagent topology helper | packages handoff envelope, not orchestration authority |
| `verifier` | quality gate role | evidence collection only, no auto-promote authority |

Catalog rows are valid only when their no-go boundary is explicit.
