# Security Events Data Model Notes

Source: live tenant observation and security.events schema introspection
Date: 2026-04-24

## TOC

- [Data Source](#data-source)
- [event.type Values](#eventtype-values)
- [Common Fields (All Finding Types)](#common-fields-all-finding-types-via-get-security-events-summary)
- [Entity Scoping Fields](#entity-scoping-fields)
- [Vulnerability-Specific Fields](#vulnerability-specific-fields-on-securityevents-generic-stream)
- [Compliance-Specific Fields](#compliance-specific-fields-on-securityevents-generic-stream)
- [RVA-Specific Fields](#rva-specific-fields-dynatrace-runtime-vulnerability-analytics)
- [SPM-Specific Fields](#spm-specific-fields-dynatrace-security-posture-management)
- [Object Types Observed](#object-types-observed-live-data-2026-04-24)
- [Provider Taxonomy](#provider-taxonomy-observed--documented)

---

## Data Source

All security data lives in `fetch security.events`.

Two access patterns:
1. **Event stream** — `fetch security.events, from:now()-Xh` — historical log, all event types
2. **State snapshot** — implicit in specialized tools (RVA: 30m window, SPM: 1h window)

---

## event.type Values

| value | Description | Primary tool |
|-------|-------------|--------------|
| `DETECTION_FINDING` | Behavioral detections, security alerts, threat activity | `get-security-events-summary` |
| `VULNERABILITY_FINDING` | Software vulnerability in a component/image | `get-security-events-summary` (external only) |
| `COMPLIANCE_FINDING` | Misconfiguration or policy violation | `get-dynatrace-compliance-findings` (DT), `get-security-events-summary` (external) |
| `COMPLIANCE_SCAN` | Coverage event: a compliance assessment ran | `get-security-events-summary` (eventTypes=COMPLIANCE_SCAN) |
| `VULNERABILITY_SCAN` | Coverage event: a vulnerability scan ran | `get-security-events-summary` (eventTypes=VULNERABILITY_SCAN) |
| `VULNERABILITY_STATE_REPORT_EVENT` | Dynatrace RVA: per-entity vulnerability snapshot | `get-dynatrace-vulnerabilities` (internal) |
| `VULNERABILITY_STATUS_CHANGE_EVENT` | Dynatrace RVA: state transition (open→resolved) | `get-dynatrace-vulnerabilities` (internal) |
| `VULNERABILITY_TRACKING_LINK_CHANGE_EVENT` | Dynatrace RVA: ticket/link update | `get-dynatrace-vulnerabilities` (internal) |
| `COMPLIANCE_SCAN_COMPLETED` | Dynatrace SPM: scan completed marker (used for join) | `get-dynatrace-compliance-findings` (internal join) |

**Note:** The `get-security-events-summary` `eventTypes` variable accepts comma-separated values from:
`ALL`, `VULNERABILITY_FINDING`, `DETECTION_FINDING`, `COMPLIANCE_FINDING`, `COMPLIANCE_SCAN`, `VULNERABILITY_SCAN`

The RVA/SPM internal event types are NOT accessible via `get-security-events-summary`.

---

## Common Fields (All Finding Types via `get-security-events-summary`)

| Field | Type | Notes |
|-------|------|-------|
| `event.id` | string | Unique event ID — required for semantic dictionary compliance |
| `event.type` | string | See table above |
| `event.provider` | string | Integration name: `"Dynatrace"`, `"AWS Security Hub"`, `"Amazon GuardDuty"`, `"GitHub Advanced Security"`, `"AutomationEngine"` |
| `product.name` | string | Product within provider: `"OneAgent"`, `"GuardDuty"`, `"Dependabot"`, `"Amazon GuardDuty"` |
| `product.vendor` | string | `"Dynatrace"` or external vendor name |
| `finding.id` | string | Provider-specific ID (UUID, ARN, etc.) — required |
| `finding.title` | string | Human-readable description — required |
| `finding.time.created` | timestamp | Detection occurrence timestamp — when the finding was detected in the current scan/analysis run. Map from the vendor's `last_updated`, `updateDate`, `updated_at`, `last_seen`, or scan date. Do **not** map from `creationDate`, `created_at`, or `first_seen_at` — those are set once on initial creation and are not updated on subsequent scan runs. Required. |
| `finding.type` | string | Sub-classification — required (but not always meaningful) |
| `dt.security.risk.level` | string | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NONE`, `NOT_AVAILABLE` — required |
| `object.id` | string | ID of the affected object — required |
| `object.name` | string | Name of the affected object |
| `object.type` | string | Type: `PROCESS_GROUP`, `CONTAINER`, `K8S_POD`, `AwsEc2Instance`, `AwsEksCluster`, etc. |
| `isSupportedFindingFormat` | boolean | Whether the event conforms to the semantic dictionary schema |

**Semantic dictionary compliance filter** (baked into `get-security-events-summary`):
```dql-snippet
| filter isNotNull(event.id) AND isNotNull(event.provider) AND isNotNull(finding.type)
      AND isNotNull(finding.id) AND isNotNull(finding.time.created) AND isNotNull(finding.title)
      AND isNotNull(dt.security.risk.level) AND isNotNull(object.id) AND isNotNull(object.type)
```

---

## Entity Scoping Fields

The `get-security-events-summary` tool supports scoping by entity ID or name via a wide OR chain.
These are the supported scoping fields (document them for raw DQL use):

### Smartscape / Classic entity IDs
| Field | Example value |
|-------|---------------|
| `dt.source_entity` | `PROCESS_GROUP-1234567890ABCDEF` |
| `dt.smartscape_source.id` | Smartscape node ID |
| `dt.smartscape.process` | Process node |
| `dt.smartscape.host` | Host node |
| `dt.smartscape.k8s_cluster` | K8s cluster node |
| `dt.smartscape.k8s_node` | K8s node |
| `dt.smartscape.k8s_pod` | K8s pod |

### Second-gen entity IDs
| Field | Example value |
|-------|---------------|
| `dt.entity.host` | `HOST-XXXXXXXXXXXXXXXX` |
| `dt.entity.process_group` | `PROCESS_GROUP-XXXXXXXXXXXXXXXX` |
| `dt.entity.process_group_instance` | `PROCESS_GROUP_INSTANCE-XXXXXXXXXXXXXXXX` |
| `dt.entity.kubernetes_cluster` | `KUBERNETES_CLUSTER-XXXXXXXXXXXXXXXX` |
| `dt.entity.kubernetes_node` | `KUBERNETES_NODE-XXXXXXXXXXXXXXXX` |
| `dt.entity.cloud_application_namespace` | `CLOUD_APPLICATION_NAMESPACE-XXXXXXXXXXXXXXXX` |

### Kubernetes
| Field | Example value |
|-------|---------------|
| `k8s.pod.uid` | UUID |
| `k8s.cluster.uid` | UUID |
| `k8s.cluster.name` | `"unguard"` |
| `k8s.namespace.name` | `"default"` |
| `k8s.node.name` | node hostname |

### Cloud
| Field | Example value |
|-------|---------------|
| `aws.resource.id` | `arn:aws:ec2:us-east-1:...` |
| `aws.resource.name` | friendly name |
| `azure.resource.id` | Azure resource ID |
| `azure.resource.name` | friendly name |
| `gcp.resource.id` | GCP resource ID |
| `gcp.resource.name` | friendly name |

### Object-level
| Field | Notes |
|-------|-------|
| `object.name` | Direct match on the finding's object name |
| `host.name` | Host name |

---

## Vulnerability-Specific Fields (on `security.events` generic stream)

These fields exist on external vulnerability findings accessible via `get-security-events-summary`:

| Field | Notes |
|-------|-------|
| `vulnerability.references.cve` | CVE ID, e.g. `"CVE-2021-44228"` |
| `software_component.name` | Vulnerable library/component name |
| `software_component.purl` | Package URL ([PURL spec](https://github.com/package-url/purl-spec)) providing unique vendor-agnostic package identification — e.g. `pkg:maven/org.apache.logging.log4j/log4j-core`. **SD-canonical, experimental** (added SD 1.320.0, defined in `software_component.yaml`, referenced on `vulnerability_finding.event.yaml`). Do not flag as an extension or unknown field. |
| `component.name` | Alternative component name field |

---

## Rule Identity Namespace (`rule.*`) — canonical home

The generic `rule.*` namespace is the **canonical home for rule identity and provenance across ALL security events** — detection findings, external compliance findings, SPM (internal) compliance findings, and WAF/firewall/IDS log records alike. It correlates an event with the detection logic or policy rule that triggered it.

| Field | Type | Notes |
|-------|------|-------|
| `rule.id` | string | Unique identifier of the rule that generated the event. Examples: `RULE-98765`, `30164`, `CIS-66577`. |
| `rule.name` | string | Name of the rule that generated the event. **This is the canonical rule-name field — use `rule.name`, not `rule.title`.** Examples: `Cross-platform Credential Stuffing Attempt`, `SQL injection detection`, `4.1.2 Minimize access to secrets`. |
| `rule.description` | string | Full description of the rule. |
| `rule.type` | string | Vendor-reported rule-evaluation type. Examples: `Correlation`, `Anomaly`, `Custom`, `Threshold`, `Behavioral`. |

**Stability / status:** proposed SD namespace, **experimental** — aligned to OTel `security_rule.*`, OCSF `rule`, and ECS `rule.*` (`security_rule.name`/OCSF `name`/ECS `rule.name` → `rule.name`; OCSF `uid`/ECS `rule.id` → `rule.id`; `desc`/`description` → `rule.description`; OCSF `type` → `rule.type`). `rule.name` is not yet emitted in runtime data (the legacy `rule.title` and `compliance.rule.title` are). When suggesting mappings (Workflow A), target `rule.name`. When validating ingested/live events (Workflow B), the legacy `rule.title` (detections/external) and `compliance.rule.title` (SPM) are still present in current data — accept them, but recommend migration to `rule.name`. Verify current stability via the live SD before relying on it (see `semantic-dictionary.md`).

**Migration:** compliance rule identity converges on this namespace — `compliance.rule.id` → `rule.id`, `compliance.rule.title` → `rule.name`. The remaining `compliance.*` fields (`compliance.rule.severity.*`, `compliance.result.*`, `compliance.standard.*`) have no `rule.*` equivalent in the proposal and stay compliance-namespaced.

---

## Compliance-Specific Fields (on `security.events` generic stream)

### External compliance integrations

External (non-DT) compliance integrations use the generic `rule.*` namespace (see [Rule Identity Namespace](#rule-identity-namespace-rule--canonical-home) above) and `finding.*` for result status — **not** `compliance.result.*` (SPM-only).

| Field | Notes |
|-------|-------|
| `rule.id` | Stable rule identifier (see canonical `rule.*` block) |
| `rule.name` | Rule name — **use `rule.name`, not `rule.title`** (canonical rule-identity field) |
| `rule.description` | Full rule description |
| `rule.type` | Optional rule category or type |
| `finding.severity` | Vendor severity string; drives `dt.security.risk.level` auto-mapping |
| `finding.result` | Per-finding PASS/FAIL/MANUAL result status |
| `finding.status` | Workflow state (OPEN/RESOLVED) |
| `compliance.control` | Vendor rule short-ID or control ref (cross-integration extension) |
| `compliance.standards` | Array of framework names (cross-integration extension) |
| `compliance.requirements` | Array of requirement refs (cross-integration extension) |
| `compliance.status` | Legacy/parallel status field; acceptable |

### Dynatrace SPM (internal compliance)

SPM events use `compliance.result.*` and `compliance.standard.*` (SPM-only — do not use in external integration mappings) plus the generic `rule.*` namespace for rule identity. **Rule identity is migrating off `compliance.rule.id` / `compliance.rule.title` onto the generic `rule.id` / `rule.name`** (see [Rule Identity Namespace](#rule-identity-namespace-rule--canonical-home)). `compliance.rule.severity.*` has no `rule.*` equivalent and stays compliance-namespaced.

| Field | Notes |
|-------|-------|
| `compliance.result.status.level` | `"FAILED"`, `"PASSED"`, `"MANUAL"`, `"NOT_RELEVANT"` — SPM only |
| `rule.id` ← `compliance.rule.id` | Rule identity; migrating to generic `rule.id`. `compliance.rule.id` still seen in current runtime data |
| `rule.name` ← `compliance.rule.title` | Rule name; migrating to generic `rule.name`. `compliance.rule.title` still seen in current runtime data |
| `compliance.rule.severity.level` | SPM only; no `rule.*` equivalent — stays compliance-namespaced |
| `compliance.result.description` / `.object.*` / `.status.score` | SPM only |
| `compliance.standard.name` / `.short_name` / `.url` | SPM only |

**Filter pattern** (baked into `get-security-events-summary`):
```dql-snippet
| filter (not exists(compliance.result.status.level) 
      or compliance.result.status.level == "FAILED" 
      or compliance.status == "FAILED")
```

---

## RVA-Specific Fields (Dynatrace Runtime Vulnerability Analytics)

Only available via `get-dynatrace-vulnerabilities` — NOT present in the raw `security.events` stream
when queried generically. These are computed fields from the tool's aggregation pipeline.

### Core Vulnerability Fields
| Field | Notes |
|-------|-------|
| `vulnerability.display_id` | Human-readable ID like `V-12345` |
| `vulnerability.id` | Internal UUID |
| `vulnerability.external_id` | External tracker ID |
| `vulnerability.title` | Descriptive title |
| `vulnerability.type` | Classification |
| `vulnerability.stack` | `THIRD_PARTY`, `FIRST_PARTY`, `CODE_LEVEL` |
| `vulnerability.cvss.base_score` | CVSS 3.x base score (float) |
| `vulnerability.references.cve` | CVE ID |
| `vulnerability.risk.score` | Numeric 0.0–10.0 (Dynatrace risk score, may differ from CVSS) |
| `vulnerability.risk.level` | Computed from risk.score: ≥9=CRITICAL, ≥7=HIGH, ≥4=MEDIUM, ≥0.1=LOW, else=NONE |
| `vulnerability.first_seen` | Timestamp when first detected |
| `vulnerability.resolution.change_date` | When resolution status last changed |

### State Fields
| Field | Values |
|-------|--------|
| `vulnerability.resolution.status` | `OPEN`, `RESOLVED` |
| `vulnerability.mute.status` | `MUTED`, `NOT_MUTED` |

**Important:** `get-dynatrace-vulnerabilities` returns ALL mute statuses by default.
Always separate `MUTED` vs `NOT_MUTED` in counts when asked about open vulnerabilities.

### Davis Assessment Fields
| Field | Values | Meaning |
|-------|--------|---------|
| `vulnerability.davis_assessment.vulnerable_function_status` | `IN_USE`, `NOT_IN_USE`, `NOT_AVAILABLE` | Is the vulnerable code path actually executed? |
| `vulnerability.davis_assessment.exposure_status` | `PUBLIC_NETWORK`, `NOT_DETECTED`, `NOT_AVAILABLE` | Is the affected entity reachable from public network? |
| `vulnerability.davis_assessment.exploit_status` | `AVAILABLE`, `NOT_AVAILABLE` | Is a known exploit publicly available? |
| `vulnerability.davis_assessment.data_assets_status` | `REACHABLE`, `NOT_DETECTED`, `NOT_AVAILABLE` | Can the vulnerability reach sensitive data? |

### Entity Fields (post-aggregation, arrays)
| Field | Notes |
|-------|-------|
| `affected_entity.ids` | Array of directly affected entity IDs |
| `affected_entity.names` | Array of directly affected entity names |
| `affected_entity.vulnerable_component.names` | Array of vulnerable library names on affected entities |
| `related_entities.{kubernetes_workloads,kubernetes_clusters,applications,services,hosts,reachable_data_assets}.{ids,names}` | Related context entities (arrays) |

---

## SPM-Specific Fields (Dynatrace Security Posture Management)

Only via `get-dynatrace-compliance-findings`. These are computed fields from the tool's aggregation
pipeline (summarize by compliance.rule.id + join with COMPLIANCE_SCAN_COMPLETED).

> **Field names below reflect the tool's _current_ output.** Rule identity is migrating to the generic `rule.*` namespace (`compliance.rule.id` → `rule.id`, `compliance.rule.title` → `rule.name`; see [Rule Identity Namespace](#rule-identity-namespace-rule--canonical-home)), but `get-dynatrace-compliance-findings` and the underlying runtime data still emit the `compliance.rule.*` names today. Do not rewrite live DQL to `rule.*` until the runtime emits it.

| Field | Notes |
|-------|-------|
| `compliance.rule.id` | Unique rule ID, e.g. `"CIS-66577"` — migrating to `rule.id` |
| `compliance.rule.title` | Human-readable rule name — migrating to `rule.name` |
| `compliance.rule.severity.level` | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `compliance.standard.name` | Full standard name, e.g. `"CIS Kubernetes Benchmark"` |
| `compliance.standard.short_name` | Abbreviated, e.g. `"CIS"`, `"DORA"`, `"NIST"`, `"STIG"`, `"PCI"` |
| `compliance.result.status.level` | `FAILED`, `PASSED`, `MANUAL`, `NOT_RELEVANT` (post-aggregation) |
| `compliance.result.count.passed` | Count of passed checks for this rule |
| `compliance.result.count.failed` | Count of failed checks for this rule |
| `compliance.result.count.manual` | Count of manual review checks for this rule |
| `compliance.result.object.name` | Specific sub-object that failed (e.g. pod name, namespace) |
| `scan.id` | Links finding to its parent scan (used for join) |
| `k8s.pod.name`, `k8s.workload.name`, `k8s.node.name`, `k8s.namespace.name`, `k8s.cluster.name` | K8s context |

**Note:** `NOT_RELEVANT` is pre-filtered from the query. It must NOT be counted in pass/fail totals.

---

## Object Types Observed (live data, 2026-04-24)

From `get-security-events-summary` (DETECTION_FINDING):
- `PROCESS_GROUP`
- `CONTAINER`
- `K8S_POD`
- `AwsEc2Instance`
- `AwsEksCluster`

More expected but not yet observed in this tenant:
- `HOST`, `SERVICE`, `PROCESS_GROUP_INSTANCE`
- `AwsS3Bucket`, `AwsIamRole`, `AwsLambdaFunction`
- `AzureVirtualMachine`, `AzureContainerInstance`

---

## Provider Taxonomy (observed + documented)

| `event.provider` | `product.name` | Type | Notes |
|-----------------|----------------|------|-------|
| `Dynatrace Automated Detections` | `Automated Detections` | Detection | Dynatrace RAP built-in detectors |
| `AutomationEngine` | `AutomationEngine` | Detection | Custom detection workflows via Dynatrace AutomationEngine |
| `AWS Security Hub` | `GuardDuty` | Detection | AWS GuardDuty findings via Security Hub integration |
| `Dynatrace` | `OneAgent` | Vulnerability | Dynatrace RVA (filtered out of summary tool) |
| `Dynatrace` | n/a | Compliance | Dynatrace SPM (filtered out of summary tool) |
| `GitHub Advanced Security` | `Dependabot` | Vulnerability | Example from tool description |
| `Amazon GuardDuty` | `Amazon GuardDuty` | Detection | Direct GuardDuty integration (alternative to Security Hub) |
