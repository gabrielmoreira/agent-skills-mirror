# Validation Rules

Apply all rules to both user-provided mappings and generated mappings. Rules are grouped by topic.

## TOC

- [Validation Rules](#validation-rules)
	- [TOC](#toc)
	- [Event-Type Coverage](#event-type-coverage)
		- [Alternative — Reclassification Path](#alternative--reclassification-path)
	- [Required Fields — All Findings](#required-fields--all-findings)
	- [Risk Fields and Auto-Mapping](#risk-fields-and-auto-mapping)
	- [Scan Reference Requirement (Static Mapping Validation)](#scan-reference-requirement-static-mapping-validation)
	- [Scan Event Field Scope](#scan-event-field-scope)
	- [Vulnerability Findings — Component Namespace](#vulnerability-findings--component-namespace)
		- [`software_component.supplier.name` — User-Friendly Supplier Name](#software_componentsuppliername--user-friendly-supplier-name)
	- [External Compliance Integration — Field Conventions](#external-compliance-integration--field-conventions)
	- [Object-Type Namespace Requirements](#object-type-namespace-requirements)
	- [finding.type Namespace Requirements](#findingtype-namespace-requirements)
	- [Known SD Discrepancies and Unknown Fields](#known-sd-discrepancies-and-unknown-fields)
		- [Acceptable Discrepancies](#acceptable-discrepancies)
		- [Unknown Fields](#unknown-fields)
		- [Vendor-Specific Extensions (Expected and Valued)](#vendor-specific-extensions-expected-and-valued)
		- [Vendor Namespace Duplication Check](#vendor-namespace-duplication-check)
	- [Value and Type Checks](#value-and-type-checks)
		- [Provider-Vendor Canonicalization Check](#provider-vendor-canonicalization-check)
	- [Cross-Integration Comparison](#cross-integration-comparison)
	- [Validation Input Mode And Raw Content Fields](#validation-input-mode-and-raw-content-fields)
	- [Optional Runtime Validation Checks](#optional-runtime-validation-checks)
	- [Discrepancy Severity](#discrepancy-severity)
	- [Acceptance Criteria](#acceptance-criteria)

---

## Event-Type Coverage

Validate that the integration supports the correct `event.type` values:

| Finding class | Required event.type | Scan event.type |
|---|---|---|
| Detection | `DETECTION_FINDING` | — (not applicable) |
| Vulnerability | `VULNERABILITY_FINDING` | `VULNERABILITY_SCAN` |
| Compliance | `COMPLIANCE_FINDING` | `COMPLIANCE_SCAN` |

- Detections are push-based; they have no scan cycle. Flag a mapping critical if it adds scan events for detections.
- Vulnerability and compliance integrations that omit scan events are missing coverage signals — flag as **major**.

### Alternative — Reclassification Path

When a detection-class mapping incorrectly emits `*_SCAN` events, do not stop at "remove the scan events." Investigate whether the integration class itself is wrong before recommending the fix.

If the vendor's "scan-complete" / "system-scan-summary" / "assessment" payload is actually a **vulnerability assessment** (per-asset vulnerability state at a point in time), the integration class is **vulnerability**, not detection. In that case:

1. Reclassify: `event.type` for the underlying records becomes `VULNERABILITY_FINDING`, paired with `VULNERABILITY_SCAN` coverage events.
2. Do **not** drop the scan-style payload — it carries real coverage data, just on the wrong event-type.
3. Re-derive the finding mapping from the vendor's assessment records (one finding per (asset × vulnerability) row).
4. Emit one `VULNERABILITY_SCAN` per scan cycle × scanned object, not per finding.

If the vendor really is a detection engine (alerts on observed adversary behavior, not vulnerability state), then the original "remove the scan events" guidance applies and the heartbeat/coverage signal should be routed to a non-`security.events` channel (operational telemetry or vendor-namespaced product metrics).

The validator must offer both branches in the discrepancy report so the integration owner picks the correct one.

---

## Required Fields — All Findings

Fail validation (`critical`) if any of these are absent and cannot be derived:

| Field | Notes |
|---|---|
| `event.id` | Unique event identity. **Auto-generated on ingest** — not required in the mapping. Ingestion platform (OpenPipeline) generates UUID if absent. |
| `event.kind` | Should be `SECURITY_EVENT` |
| `event.type` | One of the values in the event-type coverage table |
| `event.provider` | Integration name |
| `product.name` | Product within provider |
| `product.vendor` | Vendor name |
| `timestamp` | Ingestion time. **Auto-populated on ingest** — not required as an explicit mapping in theoretical mapping validation. |
| `finding.id` | Provider-specific finding identity; must be stable and non-null |
| `finding.title` | Human-readable description |
| `finding.time.created` | Detection occurrence timestamp — when the finding was most recently detected in the current scan run. Map from the vendor's `last_updated`/`updateDate`/`updated_at`/`last_seen`/scan date. **Not** from `creationDate`/`created_at`/`first_seen_at` (immutable after initial creation, not updated on re-detection). |
| `finding.type` | Sub-classification (e.g. `DEPENDENCY_VULNERABILITY`, `CODE_ISSUE`, `EXPOSED_SECRET`) |
| `finding.severity` | Vendor severity string — used as input to risk auto-mapping if `dt.security.risk.level` is absent |
| `object.id` | ID of the affected object |
| `object.name` | Name of the affected object |
| `object.type` | Type of the affected object |

---

## Risk Fields and Auto-Mapping

`dt.security.risk.level` and `dt.security.risk.score` MAY be absent if `finding.severity` carries standard values that enable auto-mapping.

**Auto-mapping rule** (Dynatrace OpenPipeline behavior):

- `finding.severity` values `critical|CRITICAL|BLOCKER` → `dt.security.risk.level = CRITICAL`
- `high|HIGH|MAJOR` → `HIGH`
- `medium|MEDIUM|WARNING` → `MEDIUM`
- `low|LOW|MINOR|INFO|INFORMATIONAL` → `LOW`
- `dt.security.risk.score` is auto-derived from `dt.security.risk.level` when absent.

If `finding.severity` uses non-standard values or is absent and `dt.security.risk.level` is also absent, flag as **critical**.

If `dt.security.risk.score` is provided as a string instead of a number, flag as **major** (type mismatch).

---

## Scan Reference Requirement (Static Mapping Validation)

For `VULNERABILITY_FINDING` and `COMPLIANCE_FINDING` events in static mapping validation:

- `scan.id` — **required** (flag as major if absent)
- `scan.name` — recommended (flag as minor if absent)

Detection findings (`DETECTION_FINDING`) do **not** require scan references.

---

## Scan Event Field Scope

Scan events (`VULNERABILITY_SCAN`, `COMPLIANCE_SCAN`) are **coverage events** — they record that a specific object (code artifact, container image, host, etc.) was assessed at a point in time. They are not finding containers.

**Allowed on scan events:**

- Standard event fields: `event.id`, `event.kind`, `event.type`, `event.provider`, `event.description`
- Scan identity: `scan.id`, `scan.name`, `scan.status`, `scan.time.started`, `scan.time.completed`
- Object identity: `object.id`, `object.name`, `object.type`, plus the object-type namespace fields (`artifact.*`, `container_image.*`, `host.*`, etc.)
- Provider / product: `product.vendor`, `product.name`
- Vendor-namespace project/scan-level context: e.g. `checkmarx.project.*`, `wiz.scan.*` (NOT severity-derived — see below)
- Total finding count for the scanned object (e.g. `scan.findings.total`) — acceptable as a coverage stat **only when scoped to the same object the scan event covers**

**Not allowed on scan events:**

- Per-finding identity or characteristic fields: `finding.id`, `finding.title`, `finding.time.created`, `finding.type`, `finding.severity`, `finding.score`, `finding.url`, `finding.status`
- Vendor-namespace per-finding fields: `*.finding.*` sub-namespaces (e.g. `checkmarx.finding.*`) — these encode per-finding metadata and belong on finding events only
- Vulnerability-specific fields: `vulnerability.*`, `dt.security.risk.level`, `dt.security.risk.score`
- Component fields: `component.*`, `software_component.*`
- **Severity-derived insights of any granularity** — including aggregate severity-broken counts (`scan.findings.critical`, `scan.findings.high`, `scan.findings.medium`, `scan.findings.low`, `scan.summary.severity.*`), "highest severity found" indicators, or any vendor-namespace mirror of these (e.g. `<vendor>.scan.highest_severity.*`, `<vendor>.scan.severity_breakdown.*`). Severity insights belong on the corresponding finding events; to derive them for a scan, query the finding events joined on `scan.id`.

**Validation rule:**

When `finding.*`, `*.finding.*`, or any severity-derived field appears on a scan event, inspect each field individually:

| Observed field | Classification | Action |
|---|---|---|
| Per-finding identity or characteristic (ID, title, type, severity of a specific finding) | **major** | Flag and suggest removal |
| Vendor `*.finding.*` sub-namespace on a scan event | **major** | Flag and suggest removal; these fields belong on finding events |
| Severity-derived aggregate counts on a scan event (`scan.findings.critical`, `scan.findings.high`, `<vendor>.scan.severity_breakdown.*`, etc.) | **major** | Flag and suggest removal. Severity insights live on finding events; consumers derive them by joining finding events on `scan.id`. Do not propose moving these under a vendor namespace — that just relocates the same problem |
| "Highest severity found" / single-most-severe-finding indicators on a scan event (whether canonical or vendor-namespaced) | **major** | Flag and suggest removal — same reasoning |
| Total scanned-object finding count (e.g. `scan.findings.total`, no severity breakdown) scoped to the same object as the scan event | acceptable | Note as informational coverage stat; flag as **minor** if field naming is ambiguous |
| Aggregate scan-level summary spanning multiple objects (e.g. project-wide or tenant-wide totals) on a per-object scan event | **minor** | Suggest moving under `<vendor>.scan.summary.*` or removing — does not match per-object coverage model. Severity-broken multi-object aggregates remain disallowed under the rule above |

---

## Vulnerability Findings — Component Namespace

For `event.type = VULNERABILITY_FINDING`, the mapping must include at minimum:

- `component.name` — **required** (major if absent)

Highly recommended:

- `component.version`
- `software_component.name` (for `DEPENDENCY_VULNERABILITY` finding.type — see below)
- `software_component.purl` — SD-canonical experimental field (SD 1.320.0); validates as a proper PURL string (e.g. `pkg:maven/...`, `pkg:npm/...`, `pkg:go/...`). Do **not** flag as unknown or extension.
- `vulnerability.references.cve` when the vendor provides CVE data

### `software_component.supplier.name` — User-Friendly Supplier Name

`software_component.supplier.name` carries a user-friendly supplier / project / publisher label. It is acceptable for this value to overlap with `component.name` or `software_component.name` when the supplier is the same logical organization that ships the package — for example, Black Duck's `componentName = "Netty Project"` is simultaneously the SCA group label *and* the supplier identifier.

Do **not** flag this overlap as duplication. Flag as **minor** only when:

- The supplier value is set to a literal copy of the package coordinates (e.g. `software_component.supplier.name = "io.netty:netty-buffer"`) rather than a human-readable supplier label, **or**
- The vendor exposes a distinct supplier / maintainer / publisher field that would be a better source than the package name.

---

## External Compliance Integration — Field Conventions

`compliance.result.*` and `compliance.standard.*` are **reserved for Dynatrace SPM internal events**. External (non-DT) compliance integrations MUST NOT use these namespaces. Rule identity, by contrast, uses the **generic `rule.*` namespace** for all compliance findings (external and SPM) — see `data-model-notes.md § Rule Identity Namespace`.

### Rule Fields (External Compliance)

External compliance integrations MUST use the generic `rule.*` namespace for rule identity and context:

| Target Field | Required | Notes |
|---|---|---|
| `rule.id` | yes | Stable unique rule identifier |
| `rule.name` | yes | Rule name. Use `rule.name`, **not** `rule.title`. (Canonical rule-identity field, aligned to OTel/OCSF/ECS.) |
| `rule.description` | recommended | Full rule description |
| `rule.type` | optional | Rule category or type classification |

`compliance.rule.id` / `compliance.rule.title` are the **legacy** form of `rule.id` / `rule.name`. On a new mapping, propose the generic `rule.*` fields. When validating an already-ingested or live event, accept legacy `compliance.rule.id` / `compliance.rule.title` (still emitted in current runtime) but recommend migration — do **not** flag them as major. Flag `compliance.result.*`, `compliance.standard.*`, or `compliance.rule.severity.*` on an external integration event as **major** — those remain SPM-internal.

### Status Fields (External Compliance)

External compliance integrations MUST use finding-level fields for result status:

| Target Field | Required | Notes |
|---|---|---|
| `finding.severity` | yes | Standard SD severity string (e.g. `HIGH`, `MEDIUM`, `LOW`, `NONE`) — also drives `dt.security.risk.level` auto-mapping |
| `finding.result` | recommended | Per-finding result status from the vendor (`PASS`, `FAIL`, `MANUAL`, etc.). Source from the vendor `result` field. |
| `finding.status` | optional | Workflow state (e.g. `OPEN`, `RESOLVED`) |

Flag any `compliance.result.*` field on an external integration event as **major** — these fields are SPM-internal.

### Acceptable Compliance Extensions (Cross-Integration Standard)

The following fields are **not** in the Semantic Dictionary but are an established cross-integration extension pattern for compliance findings. Do **not** flag them as unknown:

| Field | SD status | Pattern | Notes |
|---|---|---|---|
| `compliance.control` | absent | cross-integration extension | Vendor rule short-ID or control reference (e.g. Wiz `shortId`). Confirm field name is consistent across integrations. |
| `compliance.standards` | absent | cross-integration extension | Array of compliance framework names associated with the finding. |
| `compliance.requirements` | absent | cross-integration extension | Array of requirement/sub-category references within the frameworks. |

`compliance.standard.name`, `compliance.standard.short_name`, and `compliance.standard.url` are **SPM-only** SD fields — do not use them in external integrations. Flag as **major** if present.

---

## Object-Type Namespace Requirements

For each observed `object.type`, validate the presence of its expected namespace:

| object.type | Required namespace | Minimum expected fields | Severity if missing |
|---|---|---|---|
| `CODE_ARTIFACT` | `artifact.*` | `artifact.name` or `artifact.id`, `artifact.path`, `artifact.repository` | major |
| `CONTAINER_IMAGE` | `container_image.*` | `container_image.digest` (primary — immutable identity, required for deduplication and Smartscape enrichment); `container_image.name` (supplementary) | major |
| `HOST` | `host.*` | `host.name` or `host.ip` | major |
| `K8S_POD` | `k8s.*` | `k8s.pod.name`, `k8s.namespace.name`, `k8s.cluster.name` | major |
| `AwsEc2Instance` | `aws.*` | `aws.resource.id`, `aws.region` | major |
| `AwsEksCluster` | `aws.*` | `aws.resource.id`, `aws.region` | major |
| `URL` | URL fields | `url.domain` or `url.path` | major |
| `PROCESS` / `PROCESS_GROUP` | none required for static mapping | `dt.entity.*` / `dt.smartscape.*` / `dt.source_entity` are post-ingest enrichment, not mapping inputs (see `object-type-expectations.md § Smartscape Enrichment Fields Are Post-Ingest`); validate at runtime in Workflow B2 only | n/a (not flagged in static validation) |

See `object-type-expectations.md` for full companion field tables and samples.

---

## finding.type Namespace Requirements

For each observed `finding.type`, validate the presence of its expected namespace:

| finding.type | Required namespace | Minimum expected fields | Severity if missing |
|---|---|---|---|
| `DEPENDENCY_VULNERABILITY` | `software_component.*` | `software_component.name` | major |
| `CODE_ISSUE` | `code.*` | `code.filepath` or `code.line.number` | major |
| `CODE_VULNERABILITY` | `code.*` | `code.filepath` or `code.line.number` | major |
| `CODE` | `code.*` | `code.filepath` | major |
| `EXPOSED_SECRET` (in code artifact) | `code.*` | `code.filepath` | major |
| `CONFIGURATION_ISSUE` | none mandatory | — | info only |

---

## Known SD Discrepancies and Unknown Fields

### Acceptable Discrepancies

Fields listed in `references/known-discrepancies.md` are **acceptable** deviations.
Do not raise critical or major issues for them.

Examples of acceptable absences: `event.start`, `event.end`.
Examples of acceptable extensions: `finding.severity`, `event.category`, `actor.*`.

### Unknown Fields

Classify a field by working through this resolution order — stop as soon as one step resolves it:

1. **Local references** (`known-discrepancies.md`, `data-model-notes.md`) — if listed as acceptable or documented, it is **not unknown**.
2. **Live SD** (`dt.semantic_dictionary.fields`) — if present there (even if absent from local references), it is **not unknown**; note the drift in the validation report and flag a PR follow-up. See `mapping-workflow.md § Shared: Verifying Against the Live Semantic Dictionary` for DQL patterns.
3. **Baseline samples** (`samples/`) — consult **only** when steps 1 and 2 leave the field unresolved. If the field appears in any local sample it is a likely known pattern; verify against the live SD before accepting it and note the gap in local references.
4. **Genuinely unknown** — absent from all three sources above: raise a **major** discrepancy and ask:

- What is the purpose of this field?
- Does it overlap with any existing SD field?
- Should it be namespaced under the vendor name (e.g. `vendorname.field`)?

### Vendor-Specific Extensions (Expected and Valued)

Vendor-namespace fields (`wiz.*`, `snyk.*`, `qualys.*`, `tenable.*`, etc.) are an expected and valued extension pattern — **not** "unknown" fields. See `known-discrepancies.md § Vendor-Specific Namespaces (Expected & Valued)` for the canonical pattern, criteria, and per-finding-class examples.

Apply the *Vendor Namespace Duplication Check* below to detect the one actionable case: when the SD field is absent or empty while the vendor field carries the value.

### Vendor Namespace Duplication Check

Vendor-namespace fields may carry the same value as SD-canonical fields — this is acceptable to keep (users may be accustomed to querying by vendor field names), but it should be flagged as **redundant** at `info` severity because the SD field already carries the value and the vendor field adds no new information. Every vendor-namespace field should be compared against the SD field that carries the same semantic meaning. Apply this rule in **all validation modes** — Workflow A (mapping suggestion), Workflow B1 (static), and Workflow B2 (runtime).

For each `<vendor>.<path>` field in the mapping (or in the live event), classify against its SD counterpart:

| Relationship to SD field | Verdict | Severity |
|---|---|---|
| Vendor field value is **identical** to the SD field value (exact match) | Redundant — SD field is populated with the same value; vendor field adds no new information. Acceptable to keep for query familiarity but flag as redundant. | `info` |
| Vendor field is a **trivial transformation** of the SD field (case change, whitespace, simple cast) | Redundant — same reasoning as identical match. Flag as redundant. | `info` |
| Vendor field carries **strictly more detail** than the SD field (richer structure, additional sub-keys) | Acceptable — keep, document the additive value | `pass` |
| Vendor field is a **subset / summary** of the SD field | Redundant — the SD field is richer; vendor field adds no new information. Flag as redundant. | `info` |
| Vendor field carries data **the SD field does not capture at all** (e.g., vendor-internal IDs, vendor-specific tags) | Acceptable — this is the intended use of the vendor namespace | `pass` |
| Vendor field is **populated while the SD field is empty / null** | Mapping bug — backfill the SD field from the vendor value | `major` |

**Common duplication patterns to look for explicitly:**

| SD-canonical field | Common vendor mirror to check | Verdict when SD field is populated |
|---|---|---|
| `rule.name` (canonical; legacy `compliance.rule.title`) | `<vendor>.rule.name`, `<vendor>.rule.title` | Redundant (`info`) — flag as redundant, no removal required |
| `compliance.remediation.description` | `<vendor>.finding.remediation`, `<vendor>.rule.remediation_instructions` | Redundant (`info`) — flag as redundant, no removal required |
| `rule.description` (canonical; legacy `compliance.rule.description`) | `<vendor>.rule.description` | Redundant (`info`) — flag as redundant, no removal required |
| `finding.severity` | `<vendor>.finding.severity` | Redundant (`info`) — flag as redundant, no removal required |
| `finding.title` | `<vendor>.finding.title`, `<vendor>.finding.name` | Redundant (`info`) — flag as redundant, no removal required |
| `finding.time.created` | `<vendor>.finding.last_seen_at`, `<vendor>.finding.updated_at`, `<vendor>.finding.updateDate` | Redundant (`info`) — flag as redundant, no removal required. Note: `<vendor>.finding.created_at` / `<vendor>.finding.first_seen_at` carry a **different semantic** (initial creation date) — do not flag them as duplicates of `finding.time.created`, and do not use them as its source. |
| `vulnerability.cvss.base_score` | `<vendor>.cvss_base_score` | Redundant (`info`) — flag as redundant, no removal required |
| `object.id`, `object.name` | `<vendor>.resource.id`, `<vendor>.resource.name` | Redundant (`info`) — flag as redundant, no removal required |

**For all rows above:** if the SD field is **empty or absent** while the vendor field is populated, flag as **major** (missed mapping — backfill the SD field from the vendor value).

**Output expectation:** the validation report must include a **Vendor Namespace Duplication** subsection listing each vendor-namespace field alongside its SD counterpart and whether the SD field is populated. When both are populated with the same value, flag the vendor field as **redundant** (`info`) — no removal required, but the redundancy should be noted. The only actionable finding is when the SD field is empty or absent while the vendor field is populated — flag that as **major**. If no vendor-namespace fields are present, state that explicitly.

**How to apply (static inspection — works on any sample event):**

Enumerate the top-level vendor-namespace keys in the event (from `dt.raw_data`, the mapping table, or a pasted payload). For each key whose prefix matches a vendor namespace (e.g., `wiz.*`, `snyk.*`, `qualys.*`), look up the corresponding SD-canonical field in the *Common duplication patterns* table above. Compare the value of the vendor field against the value of the SD field in the same event. Apply the verdict table to classify each pair.

This check is a **static field-comparison** on a single sample event. It does not require a live environment connection — it applies equally to:
- A mapping table or pasted sample payload (Workflow B1 static validation).
- A sample event fetched from the live environment (Workflow B2 runtime validation, after Q11/Q12).

For optional **scale confirmation** across many live events, see `runtime-validation.md § Vendor Namespace Duplication Check`.

---

## Value and Type Checks

Flag these:

1. `dt.security.risk.score` provided as string instead of number → **major**
2. Timestamps not in RFC3339 / ISO8601 format → **major**
3. Required ID fields that are empty or null → **critical**
4. Arrays mapped to scalar targets without explicit transformation → **major**
5. Object/record values mapped directly to string fields → **major**
6. Enum values outside known sets (`dt.security.risk.level`, `event.type`) → **critical**
7. `vulnerability.remediation.fix_version` (singular) used instead of `vulnerability.remediation.fix_versions` → **major**
8. `vulnerability.remediation.fix_versions` present but not an array of strings → **major**
9. `vulnerability.remediation.fix_versions` present as empty array or null → **minor** (remove field instead)
10. `vulnerability.external_url` must be a single string URL; arrays or multi-value encodings in this field → **major**
11. `vulnerability.cvss.version` must be version number only (e.g. `3.1`, `4.0`); prefixed/text variants like `CVSSv3`, `Cvss3`, `v3.1` → **major**
12. `vulnerability.cvss.*` fields must describe a **single CVSS version per finding** — the version the vendor uses as the authoritative source for the finding's severity. When the vendor exposes multiple CVSS versions in parallel (e.g. CVSS3 and CVSS4), select the version the vendor itself relies on for that finding (typically the latest available), and populate `vulnerability.cvss.version`, `vulnerability.cvss.base_score`, and `vulnerability.cvss.vector` from that version only. Do **not** introduce version-suffixed fields such as `vulnerability.cvss.v3.vector` or `vulnerability.cvss.v4.vector` → **major**. The non-authoritative CVSS version's data should be dropped, not preserved alongside.
13. Vendor-namespace field whose value is identical (or a trivial transform) of an SD-canonical field's value → **info** (redundant — SD field is populated with the same value; vendor field adds nothing new but may be kept for query familiarity). Escalate to **major** if the SD field is empty while the vendor field is populated — that is a missed mapping. See *Vendor Namespace Duplication Check*.
14. `product.vendor` and `event.provider` refer to the same vendor but differ only by casing or punctuation normalization (for example `Crowdstrike` vs `CrowdStrike`) → **minor** normalization inconsistency. Keep semantic value stable, but normalize to a single canonical spelling for reliable grouping/filtering.
15. For final ingested events with `event.original_content` populated: compare `finding.severity` against the vendor's own severity field inside `event.original_content` (typically `severity`, `issue_severity`, or equivalent). If the values differ semantically (e.g. vendor says `"Medium"` but `finding.severity` = `"LOW"`), flag as **major** — the mapped field disagrees with the vendor's own classification. Verify the correct source field and backfill `finding.severity`; re-derive `dt.security.risk.level` and `dt.security.risk.score` from the corrected value. Note: case-only differences (e.g. `"medium"` vs `"MEDIUM"`) are **minor** normalization; semantic differences in risk band are **major**.
16. IP-typed SD fields mapped or received as plain `string` instead of `ipAddress` (or `ipAddress[]` for arrays) → **major** (type mismatch). Affected fields: `actor.ips` (`ipAddress[]`), `host.ip` (`ipAddress[]`), `client.ip` (`ipAddress`). Arrays of IP strings are not automatically equivalent to `ipAddress[]`; the mapping must explicitly target the correct SD type. The OpenPipeline-valid cast is the `ip()` network function (see `openpipeline-constraints.md § Producing ipAddress-typed values`).
17. A suggested or provided **transform relies on a DQL construct not available in OpenPipeline processors** — most commonly `jsonPath()` for nested-JSON extraction → **major**. Transforms run as OpenPipeline processors at ingest, which support a restricted DQL subset. Flag the unavailable construct and suggest the OpenPipeline-valid alternative (for `jsonPath()`: `parse` with a JSON matcher → `fieldsFlatten`/subscript access). See `openpipeline-constraints.md`.

### Provider-Vendor Canonicalization Check

Run this in static validation outputs whenever both fields are present:

- Compare `lower(product.vendor)` vs `lower(event.provider)`.
- If equal but raw strings differ, classify as a **case-only mismatch** (`minor`).
- If not equal, classify as a **semantic mismatch** (`major`) unless the mapping contract explicitly documents different intended meanings for provider vs vendor.

Expected validation output:

| Condition | Verdict | Severity | Action |
|---|---|---|---|
| Exact match (`product.vendor == event.provider`) | pass | `pass` | none |
| Same semantic value after normalization (`lower(...)` equal), raw values differ | normalization mismatch | `minor` | normalize canonical spelling |
| Different semantic values (`lower(...)` differ) | mapping mismatch | `major` | align mapping or document intentional divergence |

---

## Cross-Integration Comparison

Consult `samples/` for cross-integration confirmation **only when the primary references leave a specific mapping choice uncertain** — an unfamiliar field, a suspicious value pattern, or weak evidence on an optional namespace. Do not run this check unconditionally on every mapping.

When samples are consulted:

1. Detect target field usage not seen in any local sample — flag as a candidate unknown and verify against the live SD before classifying.
2. Detect weak mappings where richer SD fields are populated in comparable integrations.
3. Detect value-pattern contradictions across providers (e.g. mixed case on enum-like fields).

---

## Validation Input Mode And Raw Content Fields

Workflow B validations must first identify input mode:

1. **Final ingested event validation**
	- `dt.raw_data` is **always** populated by OpenPipeline at ingest with the full raw event envelope as received. Its presence is platform behavior, not a mapping signal — do **not** flag dual presence with `event.original_content` as a discrepancy, and do not recommend dropping `dt.raw_data` from the integration.
	- `event.original_content` is set by **extension-based / pull integrations** to carry the original vendor API response payload separately from the SD-mapped fields.
	- Canonical raw-content source for comparison:
	  - **Extension-based / pull integrations:** prefer `event.original_content` (it carries vendor-raw content, distinct from the SD-mapped envelope that lives in `dt.raw_data`).
	  - **Push-based integrations:** use `dt.raw_data` — the envelope is the raw ingested vendor payload in this case.
	- For extension-based / pull integrations, `event.original_content` must be populated on **every event the integration emits**, including scan events (`VULNERABILITY_SCAN`, `COMPLIANCE_SCAN`). The scan-event `event.original_content` should carry the raw vendor content that the scan event was derived from — for example, the journal / scan-completion payload, the assessment summary, or the equivalent vendor record. Missing `event.original_content` on a scan event from an extension-based integration is a **major** mapping gap.
	- If no raw vendor payload is recoverable from either field, flag as **major** (insufficient evidence for final-ingested validation).

2. **Theoretical mapping validation**
	- Validate mapping table/output directly against vendor API samples.
	- Do not require `dt.raw_data` or `event.original_content`; absence is expected and should not be flagged.
	- Do not fail validation for missing explicit mappings of ingest-generated fields (`event.id`, `timestamp`).

---

## Optional Runtime Validation Checks

When tenant-backed validation is requested, run query checks from `runtime-validation.md`.

Minimum runtime checks:

1. Findings exist for requested `event.provider`.
2. Scans exist for the same provider (when scans are expected); if not, raise a `warning` and continue.
3. Findings-to-scan linkage (`scan.id`) has no unexplained orphan findings; non-zero orphan counts raise a `warning`.
4. Scan reference coverage on `VULNERABILITY_FINDING` and `COMPLIANCE_FINDING` rows is present or explained; missing coverage raises a `warning`.
5. `dt.security.risk.level` values are valid SD values.
6. `object.type` distribution is plausible for integration scope.
7. `dt.security.risk.score` aligns with expected risk level thresholds.
8. Sample events are fetched with `| limit 1` for relevant `object.type` values and checked for required semantic field structure.
9. Vendor-namespace fields do not duplicate SD-canonical field values (see *Vendor Namespace Duplication Check*); duplicate pairs raise a `warning` (or a missed-mapping `fail` if the SD field is empty while the vendor field is populated).

---

## Discrepancy Severity

| Severity | Criteria |
|---|---|
| `critical` | Missing required field that cannot be auto-derived; invalid `event.type`; null required ID; invalid risk level enum |
| `major` | Missing object-type namespace; missing finding.type namespace; missing scan reference for V/C in static mapping validation; missing `component.name` for vulnerability; unknown field; type mismatch; weak risk mapping |
| `minor` | Missing optional enrichment; `scan.name` absent; optional CVE reference absent; minor naming inconsistency; optional remediation field present but empty |
| `info` | SD divergence that is already on the known-discrepancies list |

---

## Acceptance Criteria

A mapping passes validation when:

1. All required semantic fields are present or auto-derivable.
2. No critical discrepancies remain unresolved.
3. All major discrepancies have either been fixed or carry explicit documented justification.
4. `object.type` namespace checks pass for all observed object types.
5. `finding.type` namespace checks pass for all observed finding types.
6. Static mapping includes scan references for vulnerability and compliance findings.
7. Non-vendor-namespace unknown fields have been explained and accepted or removed. **Vendor-namespace fields** (e.g., `wiz.*`, `snyk.*`) do not require explanation — they are valued context and are not counted as "unknown".
8. Validation input mode is explicitly documented (final ingested vs theoretical), and raw-content source is identified when applicable.
9. If runtime validation is enabled, failed runtime checks are documented with remediation actions.
10. Runtime warnings (for example missing scans or orphan findings) are documented with probable causes and follow-up actions; warnings alone do not fail the mapping.
11. Runtime validation output should use a `Validation Summary` table with statuses `🟢 pass`, `🟡 warn`, `🔴 fail` (not a bullet-list summary).
12. Unknown fields have been explained and accepted or removed.
