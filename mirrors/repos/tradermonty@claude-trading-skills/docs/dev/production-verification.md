# Production Verification Criteria

`status: production` is the catalog lifecycle label. It is not, by itself, proof that a skill's
trading logic is correct. Every production skill therefore has a separate `verification` block in
`skills-index.yaml`. The block records what has actually been verified and exposes gaps without
changing the existing lifecycle status.

## Values

- `passed`: the criterion is fully satisfied by skill-specific, auditable evidence.
- `not_verified`: the criterion is applicable or its applicability has not been cleared, but the
  repository does not contain enough evidence to claim it passed.
- `not_applicable`: the criterion clearly does not apply. The baseline must record why.

`passed` is an AND claim: every requirement listed for that axis must be satisfied. Test presence,
a high documentation score, aggregate green CI, or a repository-wide scan is not sufficient on its
own.

## Axis criteria

| Axis | `passed` requires | `not_applicable` is allowed when |
|---|---|---|
| `instruction_contract` | Complete trigger, prerequisites, input/output and failure semantics; every JSON/YAML output has a referenced schema; executable entry points and operator steps are unambiguous. | Normally never for a production skill. |
| `unit_tests` | Every executable helper script has automated happy-path, boundary, and error-path fixtures; fail-closed behavior and output-schema conformance are demonstrated; the recorded command exits 0. | The skill has no executable helper scripts. |
| `workflow_contract` | Every canonical workflow handoff involving the skill is exercised by a contract test, including schema and decision-gate behavior. | The skill is not referenced by a canonical workflow. |
| `end_to_end_replay` | Applicable workflows have deterministic required-only and full-path replays plus relevant failure-mode fixtures, with no partial state writes on failure. | The skill is not referenced by a canonical workflow. |
| `data_provenance` | Applicable outputs record source identifiers or URLs and an as-of timestamp, and tests cover missing/stale provenance. | The skill makes no external or market-data claim. |
| `financial_logic_review` | Money, price, quantity, date, unit, and currency semantics are reviewed; NaN, Infinity, negative, and extreme values are rejected where invalid; formulas and fail-closed behavior are independently checked. | The skill contains no trading or financial logic. |
| `empirical_validation` | Predictive or performance claims have reproducible, point-in-time, cost-aware validation with assumptions and evidence pinned to the assessed revision. | The skill makes no predictive or performance claim. |
| `security_review` | Skill-specific input/output, credential, dependency, path, and data-exposure review is recorded; relevant security checks pass. | Exceptional only; repository-wide SAST or secret scanning alone does not make this `passed`. |

The production criteria in issue #292 map to these axes as follows:

- Script test inventory, happy/boundary/error fixtures, fail-closed tests, and schema validation:
  `unit_tests` (with the schema itself also required by `instruction_contract`).
- Numeric, date, unit, and currency validation: `financial_logic_review` and `unit_tests`.
- Source and as-of recording: `data_provenance`.
- Canonical handoffs and executable workflow replay: `workflow_contract` and
  `end_to_end_replay`.
- No open high-severity issue: the live release gate described below.

## Interpreting readiness

`all_applicable_axes_passed` means, and only means:

1. all eight declarations are present and valid;
2. every value is `passed` or `not_applicable`; and
3. no axis is `not_verified`.

It is not a complete production release decision. Before release, query the current GitHub issue
state and confirm that no open high-severity issue applies to the skill. This live gate is recorded
under `external_release_gates` in the baseline but is not frozen into an axis or added to reviewer
scores.

## Baseline and evidence

[`production-verification-baseline.yaml`](production-verification-baseline.yaml) records the audited
Git commit/date, shared conservative profiles, and the complete production-skill mapping. Profiles
may reuse `not_verified` and clearly justified `not_applicable` decisions. A `passed` value must be
a skill-specific override with evidence such as:

- command, exit status, and target paths;
- test or schema paths tied to the assessed commit; or
- manual reviewer, date, and exact files reviewed.

The parity test in `scripts/tests/test_production_verification_baseline.py` requires the baseline to
cover exactly the current production IDs and to resolve to the same eight values stored in
`skills-index.yaml`.

## Keeping evidence current

Verification is valid only for the repository revision it accompanies. When a skill's scripts,
tests, workflow contracts, schemas, data sources, or financial logic change, re-run the recorded
evidence and update it. If the evidence is not re-established in the same change, reset the affected
axis to `not_verified`. New production skills must add both the complete index block and a baseline
mapping.

The dual-axis reviewer displays these declarations in a separate non-scoring section. It does not
treat index metadata as independently verified fact and does not add verification values or gaps to
the auto, LLM, or final score.
