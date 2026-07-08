# Known Acceptable Discrepancies

Documented deviations between the Semantic Dictionary (SD) definition for
`security.events` and the fields observed in real integration sample payloads.

**This list defines the acceptance baseline.** When validating a new mapping:

- Fields on this list that are absent or divergent are **acceptable** — do not
  raise a critical or major discrepancy for them.
- Fields that appear in **both** this list and the candidate mapping confirm
  alignment with existing integrations.
- Fields that are **not** on this list, not in the SD, and not in any local
  sample in `samples/` must be **questioned** (see `validation-rules.md §7`).

Reference: https://docs.dynatrace.com/docs/semantic-dictionary/model/security-events

---
## Vendor-Specific Namespaces (Expected & Valued)

Vendor-namespace fields (e.g., `wiz.*`, `snyk.*`, `qualys.*`, `tenable.*`, `sonatype.*`, `gitlab.*`, `github.*`) are **not** considered discrepancies or "unknown" fields.

They represent an **expected and valued** extension pattern across all finding types:

- **Detection findings**: `dt.security.rap.*` (DT RAP internal), `rule.id` / `rule.name` (SIEM/WAF)
- **Vulnerability findings**: `snyk.*`, `qualys.*`, `tenable.*`, `sonatype.*`, `github.*`, `gitlab.*`
- **Compliance findings**: `wiz.*`, `qualys.*`, `crowdstrike.*`

**Vendor namespace fields should appear in mappings** to preserve valuable vendor-specific context and provide audit traceability back to source systems.

When validating mappings, do not flag vendor-namespace fields as "unknown" — confirm they are:
1. Properly namespaced (lowercase vendor prefix + field name)
2. Sourced from documented vendor API fields
3. Values are well-formed and meaningful

---

## TOC

- [All Finding Types](#all-finding-types)
- [Detection Findings](#detection-findings)
- [Vulnerability Findings](#vulnerability-findings)
- [Compliance Findings](#compliance-findings)

---

## All Finding Types

| Field | SD Status | Sample Status | Acceptable? | Notes |
|---|---|---|---|---|
| `object.type` (vendor-reported value) | Required | Vendor-extensible | ✅ Yes | `object.type` accepts whatever the vendor reports (e.g. `AWS::EC2::Instance`, `AWS::IAM::Role`, vendor-specific resource taxonomies). Smartscape-style canonical enum (`AwsEc2Instance`) is required ONLY when the integration opts into runtime contextualization for an officially supported type. See `object-type-expectations.md § Vendor-Reported object.type Values Are Accepted` |
| `event.start` | Required | Absent | ✅ Yes | SD requires earliest activity timestamp; `timestamp` / `finding.time.created` used instead |
| `event.end` | Required | Absent | ✅ Yes | SD requires latest activity timestamp; same rationale as `event.start` |
| `event.name` | Absent | Present (all) | ✅ Yes | User-friendly label for the `event.type` value; set as a constant per integration following the pattern `"<Type> event"` — e.g. `DETECTION_FINDING` → `"Detection finding event"`, `VULNERABILITY_FINDING` → `"Vulnerability finding event"`, `COMPLIANCE_FINDING` → `"Compliance finding event"`, `VULNERABILITY_SCAN` → `"Vulnerability scan event"`, `COMPLIANCE_SCAN` → `"Compliance scan event"` |
| `event.description` | Absent | Present (most) | ✅ Yes | Free-text description; common enrichment extension |
| `event.category` | Absent | Present (most) | ✅ Yes | High-level category (e.g. `VULNERABILITY_MANAGEMENT`); not in SD |
| `event.version` | Optional | Present (most) | ✅ Yes | Schema/format version from external providers |
| `finding.severity` | Absent | Present (all) | ✅ Yes | Vendor-reported severity string. SD normalised equivalent is `dt.security.risk.level`; both coexist |
| `finding.score` | Absent | Present (many) | ✅ Yes | Vendor numeric score. SD equivalent is `dt.security.risk.score` |
| `finding.description` | Absent | Present (many) | ✅ Yes | Extended description; acceptable extension |
| `finding.url` | Absent | Present (most) | ✅ Yes | Deep-link to finding in source system |
| `finding.status` | Absent | Present (some) | ✅ Yes | Open/closed/detected status from external providers |
| `finding.tags[]` | Absent | Present (some) | ✅ Yes | Freeform classification tags (e.g. CodeQL categories) |
| `dt.security.risk.score` | Absent on DETECTION | Present (all) | ✅ Yes | Normalised numeric score; not in SD for Detection Finding |
| `dt.openpipeline.source` | Absent | Present (all) | ✅ Yes | Platform ingestion metadata |
| `dt.openpipeline.pipelines[]` | Absent | Present (all) | ✅ Yes | Pipeline processing metadata |
| `dt.security_context` | Absent | Present (some) | ✅ Yes | Cost/security context metadata |
| `dt.cost.*` | Absent | Present (some) | ✅ Yes | Cost attribution metadata |

---

## Detection Findings

Fields observed in `samples/external-detections.json`, `samples/dynatrace-detections-rap.json`, `samples/dynatrace-detections-automated.json`.

| Field / Namespace | SD Status | Acceptable? | Notes |
|---|---|---|---|
| `actor.ips[]` | Absent | ✅ Yes | Source IP addresses; DT RAP, Automated K8s, external. SD type: `ipAddress[]` |
| `actor.geo.*` | Absent | ✅ Yes | Geo-enrichment from external providers (city, country, continent, region, lat/lon) |
| `actor.fqdns` | Absent | ✅ Yes | Reverse-DNS resolved hostname(s) — AWS Security Hub |
| `detection.id` / `.title` / `.description` | Absent | ✅ Yes | DT Automated Detections internal rule metadata |
| `detection.owner.id` | Absent | ✅ Yes | DT detection rule ownership |
| `detection.mitre.ids[]` | Absent | ⚠ Legacy | Older DT detection rule definition pattern. **Do NOT use for new mappings** — emit `threat.attack.*` instead (see row below). Existing integrations may keep `detection.mitre.ids[]` for backward compatibility. |
| `detection.action` / `detection.type` | Absent | ✅ Yes | Action / rule-type from external providers |
| `threat.attack.*` | **SD-canonical** | ✅ Yes — **canonical SD pattern** | The canonical SD namespace for MITRE ATT&CK enrichment on detection findings (defined in `source/fields/signal_fields/threat.yaml` in the SD repo). Use this for ALL new detection mappings. Key fields: `threat.attack.tactic.ids[]` (TA-prefixed), `threat.attack.tactic.names[]`, `threat.attack.technique.ids[]` (T-prefixed), `threat.attack.technique.names[]`, `threat.attack.subtechnique.ids[]` (dotted, e.g. `T1059.003`), `threat.attack.subtechnique.names[]`, `threat.attack.version`. Supersedes `detection.mitre.ids[]`. Note: `mitre.attack.enterprise.*` does **not** exist in the SD — do not use or suggest it. |
| `entry_point.*` / `user_controlled_input.*` | Absent | ✅ Yes | DT RAP attack entry-point detail; flat namespace vs SD structured array |
| `dt.security.rap.target.*` | Absent | ✅ Yes | DT RAP target type/name |
| `dt.security.evidence.*` | Absent | ✅ Yes | DT evidence DQL query data |
| `http.request.*` / `http.response.*` | Absent | ✅ Yes | WAF / SIEM HTTP context; not in SD security-events model |
| `url.*` / `client.ip` | Absent | ✅ Yes | URL components and client IP from network layer. `client.ip` SD type: `ipAddress` (scalar) |
| `rule.id` / `rule.name` / `rule.description` / `rule.type` | Absent | ✅ Yes | Generic rule-identity namespace; SIEM/WAF rule identifiers from external providers. Use `rule.name`, **not** `rule.title`. Legacy `rule.title` still appears on current detection events (e.g. `samples/external-detections.json`) — accept it on ingested/live events, recommend migration to `rule.name`. See `data-model-notes.md § Rule Identity Namespace` |
| `execution.id` / `execution.actor.id` | Absent | ✅ Yes | DT AutomationEngine workflow execution context |
| `span.id` / `trace.id` / `trace.is_sampled` | Absent | ✅ Yes | DT RAP distributed tracing context |
| `dt.agent.module.*` | Absent | ✅ Yes | OneAgent module metadata |
| `dt.smartscape.*` | Not in SD | ✅ Yes — post-ingest enrichment | Platform enrichment populated by OpenPipeline at ingest. NOT an integration-emitted field — do not include in mapping; check at runtime only. **Canonical / preferred namespace** (`dt.entity.*` is its deprecated alias). See `object-type-expectations.md § Smartscape Enrichment Fields Are Post-Ingest`. |
| `dt.entity.*` | Not in SD | ✅ Yes — post-ingest enrichment, deprecated alias | Same as `dt.smartscape.*` but the **deprecated** namespace. Existing rows that carry `dt.entity.*` are valid; new mappings/queries should prefer `dt.smartscape.*`. A row with `dt.smartscape.*` populated and no `dt.entity.*` is completely OK — do NOT flag the missing legacy alias. |
| `event.original_content` | Absent | ✅ Yes | Raw original event payload; WAF / SIEM integrations |
| `server.address` | Absent | ✅ Yes | Akamai SIEM server address |

---

## Vulnerability Findings

Fields observed in `samples/external-vulnerabilities-*.json`.

| Field / Namespace | SD Status | Acceptable? | Notes |
|---|---|---|---|
| `vulnerability.exploit.status` | SD optional | ✅ Yes | Exploit availability; present in some integrations |
| `vulnerability.remediation.*` | SD optional | ✅ Yes | Remediation status, fix versions, description |
| `vulnerability.cvss.*` | SD optional | ✅ Yes | CVSS base score and vector |
| `vulnerability.references.cwe` | Absent | ✅ Yes | CWE references alongside CVE |
| `code.*` | Absent (SD optional for CODE_ARTIFACT) | ✅ Yes | Source file path and line numbers; expected for CODE_ISSUE / CODE_VULNERABILITY |
| `artifact.*` | Absent from SD | ✅ Yes | Code artifact identity; expected for `CODE_ARTIFACT` object type. Also acceptable on `CONTAINER_IMAGE` findings and scans when a specific file within the image is the discovery source — for example, a Helm chart template, Dockerfile, or dependency manifest that references or contains the vulnerable package. In this case `artifact.*` describes the source file that led to the finding, not the scanned image itself. Do not flag `artifact.*` on `CONTAINER_IMAGE` events as a namespace mismatch when this discovery-path context is present. |
| `container_image.*` | Absent | ✅ Yes | Only for CONTAINER_IMAGE findings |
| `software_component.*` | SD optional | ✅ Yes | Vulnerable component details; expected for DEPENDENCY_VULNERABILITY |
| Vendor namespaces (`snyk.*`, `sonatype.*`, `gitlab.*`, `github.*`, `qualys.*`, `tenable.*`) | Absent | ✅ Yes | Vendor-specific context; acceptable extension pattern |
| `finding.status` | Absent | ✅ Yes | Open/detected/fixed status from source (GitLab, SonarQube) |
| `finding.tags[]` | Absent | ✅ Yes | Category tags from CodeQL / GitHub scanning |
| `finding.time.created` mapped to scan/analysis date or vendor `last_updated`/`updateDate`/`updated_at` field | SD required | ✅ Yes — general pattern | `finding.time.created` represents the **detection occurrence timestamp** — when the finding was detected in the current scan run. Vendor fields named `creationDate`, `created_at`, or `first_seen_at` are **not** the correct source: they capture only the initial issue creation and are not updated on subsequent scans. Map from the vendor's `last_updated`, `updateDate`, `updated_at`, `last_seen`, or the scan/analysis date instead. Do not flag this mapping choice as a discrepancy. |
| `dt.security.risk.score` diverging from `vulnerability.cvss.base_score` | — | ✅ Yes — **recommended pattern** | Vendor post-assessment scoring (e.g. JFrog applicability-adjusted severity, Snyk effective severity, Qualys QDS) augments the raw CVSS base score by factoring in exploit context, applicability, and reachability — intentionally lowering scores on theoretical vulnerabilities to deprioritize noise. `dt.security.risk.score` SHOULD reflect the vendor's adjusted score; `vulnerability.cvss.base_score` SHOULD preserve the original CVSS for reference. Both fields coexisting with different values is correct and expected. **Do NOT flag score divergence between these two fields as a discrepancy.** Only flag if (a) `dt.security.risk.score` is identical to `vulnerability.cvss.base_score` for all events while the vendor is known to provide an adjusted score, or (b) the score-to-level mapping is internally inconsistent (Q6 mismatch > 0). |

---

## Compliance Findings

Fields observed in `samples/external-compliance.json`, `samples/dynatrace-compliance.json`.

**Key convention:** rule identity uses the generic `rule.*` namespace for **all** compliance findings — external and SPM alike (`rule.id` / `rule.name` / `rule.description` / `rule.type`; use `rule.name`, **not** `rule.title`). `compliance.result.*` and `compliance.standard.*` remain SPM-internal; external integrations use `finding.*` for result status. See `data-model-notes.md § Rule Identity Namespace` and `validation-rules.md § External Compliance Integration — Field Conventions` for the full rule set.

| Field / Namespace | SD Status | Acceptable? | Notes |
|---|---|---|---|
| `rule.id` / `rule.name` / `rule.description` / `rule.type` | Absent from SD (proposed, experimental) | ✅ Yes — **cross-integration standard** | The correct targets for rule identity and context on compliance findings (external and SPM). `rule.name` is the canonical rule-name field — do **not** use `rule.title`. Legacy `compliance.rule.id` / `compliance.rule.title` migrate here. |
| `finding.result` | Absent from SD | ✅ Yes — **cross-integration standard** | Per-finding PASS/FAIL/MANUAL result status on external compliance findings. Source from vendor `result` field. |
| `finding.status` | Absent | ✅ Yes | Workflow state (e.g. `OPEN`, `RESOLVED`); acceptable alongside `finding.result` |
| `compliance.status` | Absent | ✅ Yes | Legacy parallel status field; acceptable |
| `compliance.control` | Absent | ✅ Yes — cross-integration extension | Vendor rule short-ID or control reference (e.g. Wiz `shortId`). Present across multiple integrations; do not flag as unknown. |
| `compliance.standards` | Absent | ✅ Yes — cross-integration extension | Array of compliance framework names. Present across multiple integrations; do not flag as unknown. |
| `compliance.requirements` | Absent | ✅ Yes — cross-integration extension | Array of requirement/sub-category references within the frameworks. Present across multiple integrations; do not flag as unknown. |
| `scan.id` / `scan.name` | Absent from SD core | Required by this skill | Static mapping requirement: both vulnerability and compliance findings should carry scan reference; runtime gaps are warning-tier when caused by time-window/linkage limits |
| `compliance.rule.id` / `compliance.rule.title` | Legacy SPM rule identity | ⚠ Legacy — migrate to `rule.*` | Superseded by generic `rule.id` / `rule.name`. Accept on current ingested/live events (still emitted in runtime), but recommend migration. On a **new external mapping**, propose `rule.id` / `rule.name` instead — do not introduce `compliance.rule.id` / `compliance.rule.title`. |
| `compliance.rule.severity.*` | Present for DT SPM | SPM-only | No `rule.*` equivalent in the proposal; stays compliance-namespaced. Flag as **major** on an external integration event. |
| `compliance.result.*` namespace | Present for DT SPM | ❌ Must be absent for external integrations | SPM-only. Flag as **major** on any external integration event. Replace with `finding.result` / `finding.severity`. |
| `compliance.standard.*` namespace (`compliance.standard.name`, `.short_name`, `.url`) | Present for DT SPM | ❌ Must be absent for external integrations | SPM-only. Flag as **major** on any external integration event. |
