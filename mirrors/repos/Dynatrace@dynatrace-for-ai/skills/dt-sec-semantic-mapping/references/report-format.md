# Report Format

## TOC

- [Workflow A — Phase 1 Output (Suggestion Table)](#workflow-a--phase-1-output-suggestion-table)
- [Workflow A — Phase 2 Output (Sample JSON)](#workflow-a--phase-2-output-sample-json)
- [Workflow B Output (Validation with Diff Table)](#workflow-b-output-validation-with-diff-table)
- [Shared Sections](#shared-sections)

---

## Workflow A — Phase 1 Output (Suggestion Table)

Present this block first. Do not generate Phase 2 until the user approves.

### 1. Mapping Summary

- Vendor:
- Finding types covered:
- Sample count per type:
- Confidence: `high | medium | low`

### 2. Mapping Table

| Source Field | Target Field | Transform | Required | Sample Value | Notes |
|---|---|---|---|---|---|
| `vendor.id` | `event.id` | direct | yes | `abc-123` | |
| `vendor.severity` | `dt.security.risk.level` | enum map | yes | `critical` → `CRITICAL` | |
| — | `event.kind` | constant | yes | `SECURITY_EVENT` | always required |

### 3. Gap Summary

List required fields that could not be satisfactorily mapped:

| Required Field | Status | Reason |
|---|---|---|
| `finding.time.created` | ❌ missing | not provided by vendor API |
| `scan.id` | ⚠ partial | present only in scan events, not findings |

### 4. Discrepancies

| Severity | Category | Issue | Impact | Suggested Fix |
|---|---|---|---|---|
| critical | required-field | `finding.id` not mapped | cannot deduplicate | map stable vendor finding ID |
| major | type-mismatch | score is string not number | weak sorting | cast to numeric |
| minor | enrichment | missing `product.vendor` | weaker attribution | map constant vendor name |

### 5. Additional Sample Requests

1. Payloads with null and missing fields.
2. Payloads from each finding type and severity band.
3. Payloads for each `object.type`.
4. At least one payload per product variant/version if the vendor has multiple feeds.

---

## Workflow A — Phase 2 Output (Sample JSON)

Produce only after user approves Phase 1. One block per `finding.type`.

```json
// Example: DEPENDENCY_VULNERABILITY (Snyk Open Source)
// Transforms applied:
//   vendor.severity "medium" -> dt.security.risk.level "MEDIUM"  [enum map]
//   event.kind = "SECURITY_EVENT"                                [constant]
//   scan.id copied from scan event payload                       [cross-event join]
{
  "event.id": "63f9f2e2-436c-423a-94c1-2139ed9b2fb6",
  "event.kind": "SECURITY_EVENT",
  "event.type": "VULNERABILITY_FINDING",
  "event.provider": "Snyk",
  "timestamp": "2026-04-24T13:35:45.397000000Z",
  "product.vendor": "Snyk",
  "product.name": "Snyk Open Source",
  "finding.id": "35c68ba5-cfbe-49f3-a0a3-1a9c25a05944/OpenTelemetry.Instrumentation.Http1.0.0-rc7",
  "finding.title": "Improper Removal of Sensitive Information Before Storage or Transfer",
  "finding.time.created": "2026-03-17T20:22:49.375000000Z",
  "finding.type": "DEPENDENCY_VULNERABILITY",
  "finding.severity": "medium",
  "dt.security.risk.level": "MEDIUM",
  "dt.security.risk.score": 6.9,
  "object.id": "4ed0e723-9ae9-40c4-ad19-ba217633091c",
  "object.name": "AdService.csproj",
  "object.type": "CODE_ARTIFACT",
  "artifact.name": "AdService.csproj",
  "artifact.path": "src/ad-service/AdService.csproj",
  "artifact.repository": "DynatraceAppSec/unguard",
  "component.name": "OpenTelemetry.Instrumentation.Http",
  "component.version": "1.0.0-rc7",
  "software_component.name": "OpenTelemetry.Instrumentation.Http",
  "software_component.version": "1.0.0-rc7",
  "vulnerability.references.cve": ["CVE-2024-32028"],
  "vulnerability.cvss.base_score": 4.1,
  "scan.id": "8dd82cb0-bbc8-41ea-94aa-07ff1a6f6637",
  "scan.name": "8dd82cb0-bbc8-41ea-94aa-07ff1a6f6637"
}
```

---

## Workflow B Output (Validation with Diff Table)

### 1. Mapping Summary

Same header as Workflow A Phase 1.

### 2. Diff-Highlighted Mapping Table

Marker legend: ✅ ok · ⚠ change · ➕ add · ❌ remove

| Source Field | Current Target | Suggested Target | Transform | Status | Reason |
|---|---|---|---|---|---|
| `vendor.id` | `event.id` | `event.id` | direct | ✅ ok | |
| `vendor.score` | `dt.security.risk.score` | `dt.security.risk.score` | string→number | ⚠ change | must be numeric |
| `vendor.repoName` | `artifact.name` | `artifact.repository` | direct | ⚠ change | repo belongs in `artifact.repository` |
| — | — | `component.name` | constant/map | ➕ add | required for VULNERABILITY_FINDING |
| `vendor.internalRef` | `internal.ref` | — | — | ❌ remove | unknown field, not in SD or local references |

### 3. Gap Summary

Same format as Workflow A Phase 1.

### 4. Coverage Matrices

**Event-type coverage:**

| event.type | Status |
|---|---|
| `VULNERABILITY_FINDING` | ✅ mapped |
| `VULNERABILITY_SCAN` | ❌ missing |

**Object-type namespace check:**

| object.type | Namespace | Status | Missing Fields |
|---|---|---|---|
| `CODE_ARTIFACT` | `artifact.*` | ✅ pass | — |
| `HOST` | `host.*` | ⚠ partial | `host.ip` missing |

**finding.type namespace check:**

| finding.type | Namespace | Status | Missing Fields |
|---|---|---|---|
| `DEPENDENCY_VULNERABILITY` | `software_component.*` | ✅ pass | — |
| `CODE_ISSUE` | `code.*` | ❌ fail | `code.filepath` absent |

### 5. Discrepancies

Same format as Workflow A Phase 1.

### 6. Improvement Plan

1. Immediate blockers to resolve (critical discrepancies).
2. High-value additions (major discrepancies).
3. Additional payloads requested.
4. Regression checks for future vendor schema changes.

### 7. Validation Summary (Optional Runtime Validation)

Include this section only when tenant-backed validation is requested.

Present this section as a table-driven summary. Do not replace it with bullet-list status output.

- Provider: `<event.provider>`
- Time window: `<window>`
- Execution path: live DQL execution

Status legend for runtime tables:

- `🟢 pass` — check passed
- `🟡 warn` — notable issue, but not a blocking runtime failure
- `🔴 fail` — blocking runtime failure or required-structure violation

| Runtime Check | Result | Evidence |
|---|---|---|
| Findings exist for provider | `🟢 pass` / `🔴 fail` | count + event types |
| Scans exist for provider | `🟢 pass` / `🟡 warn` | count + scan types |
| Orphan findings without scan | `🟢 pass` / `🟡 warn` | orphan count |
| Scan reference coverage on findings | `🟢 pass` / `🟡 warn` | missing `scan.id` / `scan.name` counts |
| Risk level values valid | `🟢 pass` / `🔴 fail` | invalid values (if any) |
| Risk score-level consistency | `🟢 pass` / `🔴 fail` | mismatch count |
| Object type distribution sanity | `🟢 pass` / `🟡 warn` / `🔴 fail` | grouped counts |
| Required-field null audit | `🟢 pass` / `🔴 fail` | null-count summary |
| Raw payload availability | `🟢 pass` / `🔴 fail` | missing payload count |
| Sample finding events per object.type (`| limit 1`) | `🟢 pass` / `🔴 fail` | sampled object types + query refs |
| Sample scan events per object.type (`| limit 1`) | `🟢 pass` / `🟡 warn` / `🔴 fail` | sampled scan object types or reason |
| Sample-event structure validation | `🟢 pass` / `🔴 fail` | required field checks on samples |
| Missing-field mapping suggestions | `🟢 pass` / `🟡 warn` / `🔴 fail` | candidate source paths/transforms in priority order: `dt.raw_data`, then `event.original_content`, then vendor samples |

If any check fails, add a one-line remediation action under the table.
If a check is `warn`, add a one-line likely cause and follow-up action under the table.

If required fields are missing, include a dedicated mapping-backfill table:

| Missing Target Field | Source Evidence | Candidate Source Path | Transform | Confidence | Notes |
|---|---|---|---|---|---|
| `object.name` | `dt.raw_data` | `resources[0].details.instanceName` | direct | high | fallback to `object.id` if name absent |
| `object.name` | `event.original_content` | `asset.displayName` | direct | medium | use only when `dt.raw_data` is unavailable |

---

## Shared Sections

These sections appear in both workflows when relevant.

### Confidence Assignment

- `high`: all required fields mapped, all namespace checks pass, scan refs present for V/C.
- `medium`: core mapped but gaps in type-specific namespaces or fewer than 5 samples per type.
- `low`: missing required fields, absent scan events for V/C, or too few samples.
