# Release Evidence Bundle Contract

Bundle v3 must expose the following required fields.

| Field | Why it is required |
|---|---|
| `bundle_version` | proves the contract schema that the bundle follows |
| `version` | ties the bundle to version governance |
| `updated` | captures the release cut review date |
| `git_head` | links evidence to a concrete repository state |
| `evidence_refs` | points back to board, dashboard, release docs, and verify artifacts |
| `ledger_tail` | makes ledger continuity visible to operators |
| `anti_drift_governance_mode` | declares the anti-drift policy posture carried by the bundle |
| `completion_honesty_summary` | states what completion can honestly be claimed at release time |
| `report_only_warning_codes` | exposes any anti-drift warnings without silently promoting them to hard failure |
| `specialization_notes` | preserves legitimate bounded specialization instead of flattening everything into generalized completion |

Bundle v3 is valid only if these fields are present and non-empty.

Anti-drift bundle rules:

- the bundle may summarize report-only warnings, but it must not reinterpret them as automatic release denial,
- if release is blocked, the bundle must cite the separate approved policy or failed gate that caused the block,
- a bounded specialization may be released as bounded specialization when the contract says so; that is not a governance defect.
