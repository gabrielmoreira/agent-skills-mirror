# Cross-Plane Replay Ledger Contract

## Canonical Fields

| Field | Required | Meaning |
|---|---|---|
| `replay_id` | yes | unique identifier for the replay chain |
| `task_id` | yes | task envelope identifier from the unified task contract |
| `plane_id` | yes | plane that emitted the record |
| `action_id` | yes | plane-local action or connector action identifier |
| `checkpoint` | yes | `request`, `confirm`, `execute`, `verify`, `rollback`, or `replay` |
| `confirm_token` | conditional | required whenever the task used `confirm_mode = required` |
| `artifact_hash` | yes | stable reference to the reviewed evidence snapshot |
| `rollback_token` | conditional | required whenever rollback is defined or executed |
| `outcome` | yes | `pass`, `fail`, `blocked`, or `rolled_back` |
| `evidence_refs` | yes | doc paths, gate outputs, or release evidence pointers |

## Canonical Checkpoint Flow

| checkpoint | Required behavior |
|---|---|
| `request` | captures the requested intent and the task envelope |
| `confirm` | proves that risky work was confirmed or explicitly blocked |
| `execute` | records the plane-local action that actually ran |
| `verify` | records post-execution verification or operator review |
| `rollback` | records rollback command, token, and result when fallback is needed |
| `replay` | records that the prior chain can be replayed deterministically |

## Minimal Example

| replay_id | task_id | plane_id | action_id | checkpoint | outcome |
|---|---|---|---|---|---|
| `replay.vco.browser.001` | `task.browser.001` | `browser` | `browser.fetch.snapshot` | `request` | `pass` |
| `replay.vco.connector.007` | `task.connector.007` | `connector` | `connector.write.composio.email.send` | `confirm` | `pass` |
| `replay.vco.connector.007` | `task.connector.007` | `connector` | `connector.write.composio.email.send` | `execute` | `pass` |
| `replay.vco.connector.007` | `task.connector.007` | `connector` | `connector.write.composio.email.send` | `verify` | `pass` |

## Ledger Invariants

- replay chains must remain linkable across `task_id`, `action_id`, and evidence artifacts;
- `confirm` and `rollback` checkpoints cannot be implied from prose alone;
- release packaging may summarize replay evidence, but cannot replace the ledger contract.
