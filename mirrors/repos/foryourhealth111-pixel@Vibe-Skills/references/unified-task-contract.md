# Unified Task Contract

## Required Contract Fields

| Field | Required | Meaning |
|---|---|---|
| `task_id` | yes | stable task-level identifier across planes |
| `plane_id` | yes | `browser`, `desktop`, `document`, or `connector` |
| `intent` | yes | human-readable statement of the requested outcome |
| `capability_class` | yes | VCO-native capability bucket |
| `risk_class` | yes | `read_only`, `confirm_write`, `destructive`, or `blocked` |
| `confirm_mode` | yes | explicit confirmation posture |
| `input_artifacts` | yes | inputs required by the plane adapter |
| `expected_outputs` | yes | outputs the operator expects to receive |
| `rollback_plan` | yes | stage fallback or revert command |
| `replay_handle` | yes | cross-plane replay correlation key |
| `operator_owner` | yes | accountable operator or owning function |
| `evidence_refs` | yes | governance docs, gate outputs, or release references |

## Canonical Examples

| plane_id | intent | confirm_mode | rollback_plan | replay_handle |
|---|---|---|---|---|
| `browser` | fetch governed browser evidence for a task | `not_required` | revert to browser baseline / shadow adapter | `replay.browser.task.v1` |
| `desktop` | perform supervised desktop action | `required` | disable desktop plane and revert to shadow | `replay.desktop.task.v1` |
| `document` | produce governed document extraction output | `not_required` | rerun previous reviewed extractor profile | `replay.document.task.v1` |
| `connector` | execute supervised external action | `required` | disable connector write path and revert to shadow | `replay.connector.task.v1` |

## Contract Invariants

- `confirm_mode` must never be inferred implicitly.
- `rollback_plan` must exist before stage expansion is discussed.
- `replay_handle` must survive board review and release packaging.
- Plane-specific fields are allowed only as extensions under the same canonical task envelope.
