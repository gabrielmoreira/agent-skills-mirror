# Intake And Output

Use this checklist before building or validating mappings.

## TOC

- [Intake Checklist](#intake-checklist)
- [Required Follow-up Questions](#required-follow-up-questions)
- [Output Contract — Workflow A (Suggestion)](#output-contract--workflow-a-suggestion)
- [Output Contract — Workflow B (Validation)](#output-contract--workflow-b-validation)
- [Confidence Tiers](#confidence-tiers)

---

## Intake Checklist

1. Collect vendor raw API payload samples (JSON).
2. Confirm sample count per finding type:
   - Minimum recommended: 5 samples per finding type.
   - Better: 20+ samples including edge cases (nulls, partial payloads, each severity).
3. Confirm event.type coverage scoped to finding class:
   - Detections: `DETECTION_FINDING` samples.
   - Vulnerabilities: `VULNERABILITY_FINDING` AND `VULNERABILITY_SCAN` samples.
   - Compliance: `COMPLIANCE_FINDING` AND `COMPLIANCE_SCAN` samples.
4. Confirm provider metadata values:
   - `event.provider`
   - `product.vendor`
   - `product.name`
5. Collect all expected `object.type` values from the vendor.
6. Confirm presence or absence of scan references (`scan.id`, `scan.name`) for V/C findings.
7. Ask for known null/missing field behavior from vendor docs.
8. Ask for at least one payload per severity band if available.
9. For vulnerability findings: confirm whether `component.name` / `software_component.name` are provided.
10. For code artifact findings: confirm `artifact.path`, `artifact.repository`, `code.filepath` availability.
11. For container image findings: confirm `container_image.name` / `container_image.id` availability.
12. For Workflow B (validation): classify validation target:
   - Final ingested event
   - Theoretical mapping (pre-ingestion)
13. If validating a final ingested event, identify where the raw vendor payload is recoverable. Note that `dt.raw_data` is **always** populated by OpenPipeline (full ingested envelope), so its presence alone is not a mapping signal — the question is which field carries raw *vendor* content:
   - `event.original_content` for **extension-based / pull integrations** (carries the original vendor API response separately from the SD-mapped envelope)
   - `dt.raw_data` for **push-based integrations** (the envelope itself is the raw ingested vendor payload)
14. If validating a theoretical mapping, confirm that `event.original_content` is not expected as an explicit mapping. (`dt.raw_data` is platform-generated and is never an explicit mapping in any mode.)
15. Ask whether to run optional real-environment validation queries.
16. If yes, collect:
   - `event.provider` to validate
   - time window (start with `24h`)
   - execution method: live DQL execution

## Required Follow-up Questions

Ask these when information is missing:

1. "Please provide 5-20 raw JSON payloads per finding type from the source product."
2. "Which fields are guaranteed by the vendor, and which are optional or context-dependent?"
3. "What are all possible `object.type` values in the payload?"
4. "What `finding.type` values are used and what do they mean?"
5. "How does the vendor severity string map to your expected risk model?"
6. "Do scan findings (`VULNERABILITY_SCAN` or `COMPLIANCE_SCAN`) carry the same `scan.id` as the corresponding findings?"
7. "Do you have examples of payloads with missing or null values from production?"
8. "Are you validating a final ingested event or a theoretical mapping draft?"
9. "If final ingested event: is original API data in `dt.raw_data` or `event.original_content`?"
10. "Do you want optional runtime validation against real tenant data?"
11. "Which provider and time window should runtime queries use?"

## Output Contract — Workflow A (Suggestion)

**Phase 1** (present first, wait for approval):

1. Mapping table: `Source Field | Target Field | Transform | Required | Sample Value | Notes`.
2. Gap summary: required fields that could not be mapped and why.
3. Discrepancy list grouped by severity: critical → major → minor.
4. Confidence tier + missing-evidence note.

**Phase 2** (only after user approves Phase 1):

1. One sample mapped JSON object per `finding.type`.
2. Inline annotations for every applied transform.
3. Note any fields populated with hardcoded constants or auto-derived values.
4. Document any vendor-specific namespace fields (e.g., `wiz.*`, `qualys.*`) included, showing source field and value rationale.

## Output Contract — Workflow B (Validation)

1. Diff-highlighted mapping table: `Source Field | Current Target | Suggested Target | Transform | Status (✅/⚠/➕/❌) | Reason`.
2. Event-type coverage matrix.
3. Required-field pass/fail matrix (see `validation-rules.md`).
4. Scan reference check for V/C findings.
5. `object.type` namespace pass/fail matrix (see `object-type-expectations.md`).
6. `finding.type` namespace pass/fail matrix.
7. Sample-value comparison notes against `samples/` (conditional — include only when samples were consulted to resolve a specific doubt; omit when primary references were sufficient).
8. Discrepancy list grouped by severity: critical → major → minor.
9. Confidence tier and missing-evidence note.
10. Validation source note:
   - Final ingested event: include which raw-content field was used (`dt.raw_data` or `event.original_content`).
   - Theoretical mapping: explicitly state that platform-generated raw-content fields were not required.
   - Theoretical mapping: explicitly state that ingest-generated fields (`event.id`, `timestamp`) were not required as explicit mappings.
11. Vendor-specific namespace validation:
   - Confirm all vendor-namespace fields (e.g., `wiz.*`) are properly namespaced and documented.
   - List any valuable vendor-specific enrichments included in the mapping.
   - Vendor-namespace fields are not flagged as "unknown" — they represent the expected pattern.
12. Optional runtime validation section (when enabled):
   - provider and window used
   - query result summary (counts)
   - non-zero mismatch/orphan/invalid checks with `warning` vs `fail` classification and suggested fixes
   - scan-related runtime checks (`missing scans`, `orphans`, `missing scan-reference coverage`) are warning-tier unless a stricter policy is explicitly requested
   - sample events per relevant `object.type` fetched with `| limit 1`
   - sample-event structure validation outcome
   - raw-payload-backed mapping suggestions for missing required fields (for example `object.name`)
   - runtime status section title must be `Validation Summary`
   - runtime status output must be a table, not a list
13. If required fields are missing, include a mapping-backfill table with:
   - missing target field
   - source evidence (in order: `dt.raw_data`, then `event.original_content`, then vendor sample if neither payload field is available)
   - candidate source path
   - transform rule
   - confidence and notes

## Confidence Tiers

- `high`: Required fields complete, object.type rules pass, finding.type rules pass, scan references present for V/C, value consistency passes across broad samples.
- `medium`: Core mapping complete but gaps in optional namespaces or type-specific fields, or fewer than 5 samples per type.
- `low`: Missing required fields, absence of scan events for V/C, or too few representative samples.
