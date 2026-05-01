# Connector Action Ledger Contract

## Canonical Row Shape

| Field | Required | Meaning |
|---|---|---|
| `action_id` | yes | stable identifier for the governed connector action |
| `provider_id` | yes | provider surface such as `composio`, `activepieces`, or catalog-backed connector family |
| `capability_id` | yes | VCO-native capability name, not a provider-owned marketing label |
| `risk_class` | yes | `read_only`, `confirm_write`, or `deny` |
| `confirm_mode` | yes | `required`, `not_required`, or `blocked` |
| `requested_by` | yes | operator, route, or scenario that requested the action |
| `execution_owner` | yes | should remain `vco` or `vco-supervised` |
| `rollback_command` | yes | explicit rollback / disable / revert instruction |
| `replay_handle` | yes | stable replay key that can be linked into cross-plane replay governance |
| `evidence_refs` | yes | doc paths, artifact paths, or board references proving the action was governed |
| `notes` | optional | operator context, caveats, or provider-specific nuance |

## Canonical Event Classes

| Event class | Allowed in ledger | Rule |
|---|---|---|
| `catalog_snapshot` | yes | catalog discovery evidence may be stored, but never treated as execution evidence |
| `read_execution` | yes | must remain bounded by governance owner and replay handle |
| `write_execution` | yes | only when `confirm_mode = required` and rollback exists |
| `blocked_action` | yes | useful for deny / policy rejections and audit trails |
| `provider_takeover` | no | must never appear as a governed event |

## Example Rows

| action_id | provider_id | capability_id | risk_class | confirm_mode | execution_owner | rollback_command | replay_handle |
|---|---|---|---|---|---|---|---|
| `connector.read.catalog.sync` | `awesome-mcp-servers` | `connector_catalog_refresh` | `read_only` | `not_required` | `vco` | `revert catalog snapshot to prior reviewed export` | `replay.connector.catalog.refresh.v1` |
| `connector.write.composio.email.send` | `composio` | `external_message_send` | `confirm_write` | `required` | `vco-supervised` | `disable connector write path and revert to shadow` | `replay.connector.composio.email.send.v1` |
| `connector.write.activepieces.crm.update` | `activepieces` | `external_record_update` | `confirm_write` | `required` | `vco-supervised` | `set provider mode to shadow and use operator rollback SOP` | `replay.connector.activepieces.crm.update.v1` |

## Promotion-Grade Minimum

A connector action ledger is promotion-grade only when:

- every executed write action uses `confirm_mode = required`;
- every row includes `rollback_command` and `replay_handle`;
- denied actions are represented as `blocked_action` rows instead of silently disappearing;
- evidence references point back to governance docs and gates.
