# Common Query Building Blocks

Cross-cutting patterns reused across vulnerability, compliance, detection, coverage,
and entity-enrichment queries. Each block is named so per-domain references can
point here without repeating code.

> **No `dt.system.bucket` filter unless users ask for it explicitly.** Security event data may live in any bucket;
> bucket scoping is unnecessary and can hide data.

---

## Contents

- [Common Query Building Blocks](#common-query-building-blocks)
  - [Contents](#contents)
  - [1. Risk Score → Risk Level Mapping](#1-risk-score--risk-level-mapping)
  - [5. Wide Entity Scoping OR Chain](#5-wide-entity-scoping-or-chain)
  - [6. Provider / Product Filter (case-insensitive)](#6-provider--product-filter-case-insensitive)
  - [7. Time Window Conventions](#7-time-window-conventions)
  - [8. Dynatrace-vs-External Routing Logic](#8-dynatrace-vs-external-routing-logic)
  - [12. Repository / Artifact Coalescing](#12-repository--artifact-coalescing)
  - [13. K8s Workload Resolution from CONTAINER smartscapeNode](#13-k8s-workload-resolution-from-container-smartscapenode)
  - [15. Default Summarization Recipe (cross-provider summary)](#15-default-summarization-recipe-cross-provider-summary)
  - [16. Result Limits for Top-N and Raw Listings](#16-result-limits-for-top-n-and-raw-listings)
  - [17. Entity-Identifier Preservation on Raw Listings](#17-entity-identifier-preservation-on-raw-listings)
    - [Cross-provider `*_FINDING` and scan-coverage events](#cross-provider-_finding-and-scan-coverage-events)
    - [RVA state/change events](#rva-statechange-events)
    - [When NOT to apply this](#when-not-to-apply-this)
    - [Don't double-list on RVA Stage 3 output](#dont-double-list-on-rva-stage-3-output)
  - [18. Lifecycle — what counts as "new" / "resolved" (per event family)](#18-lifecycle--what-counts-as-new--resolved-per-event-family)

---

## 1. Risk Score → Risk Level Mapping

The same thresholds apply to both score fields:

| Score field | Level field | Used in |
|---|---|---|
| `vulnerability.risk.score` | `vulnerability.risk.level` | DT RVA per-entity raw events and Stage-3 derivation |
| `dt.security.risk.score` | `dt.security.risk.level` | Cross-provider `*_FINDING` events (normalized score set at ingest) |

**Threshold table (identical for both):**

| Score | Level |
|---|---|
| ≥ 9.0 | CRITICAL |
| ≥ 7.0 | HIGH |
| ≥ 4.0 | MEDIUM |
| ≥ 0.1 | LOW |
| else | NONE |

**DT RVA (derive `vulnerability.risk.level` from score):**

```dql-snippet
| fieldsAdd vulnerability.risk.level=if(vulnerability.risk.score>=9,"CRITICAL",
                                     else:if(vulnerability.risk.score>=7,"HIGH",
                                     else:if(vulnerability.risk.score>=4,"MEDIUM",
                                     else:if(vulnerability.risk.score>=0.1,"LOW",
                                     else:"NONE"))))
```

**Cross-provider (derive `dt.security.risk.level` from score, when not already set):**

```dql-snippet
| fieldsAdd dt.security.risk.level=if(dt.security.risk.score>=9,"CRITICAL",
                                   else:if(dt.security.risk.score>=7,"HIGH",
                                   else:if(dt.security.risk.score>=4,"MEDIUM",
                                   else:if(dt.security.risk.score>=0.1,"LOW",
                                   else:"NONE"))))
```

`vulnerability.risk.score` is Dynatrace's contextual DSS (factors in exposure,
exploit availability, function usage) — never exceeds CVSS base. Prefer `risk.score`
for prioritization; report `vulnerability.cvss.base_score` only when the user asks
about CVSS. `dt.security.risk.score` is the normalized cross-provider score set at
ingest (external severity strings map to fixed values: Critical → 10.0, High → 8.9,
Medium → 6.9, Low → 3.9).

---

## 5. Wide Entity Scoping OR Chain

Match a user-supplied entity ID or name against every supported scoping field by building
a per-row array of field values and checking membership with `in()`.

**Single value (most common — inline the known ID/name):**

```dql-snippet
| filter in("<entity_id_or_name>", arrayRemoveNulls(array(
    toString(dt.smartscape_source.id),
    toString(dt.smartscape.process),
    toString(dt.smartscape.host),
    toString(dt.smartscape.k8s_cluster),
    toString(dt.smartscape.k8s_node),
    toString(dt.smartscape.k8s_pod),
    toString(dt.entity.host),
    toString(dt.entity.process_group),
    toString(dt.entity.process_group_instance),
    toString(dt.entity.kubernetes_cluster),
    toString(dt.entity.kubernetes_node),
    toString(dt.entity.cloud_application_namespace),
    toString(k8s.cluster.uid), toString(k8s.pod.uid),
    toString(aws.resource.id), toString(azure.resource.id), toString(gcp.resource.id),
    object.id, object.name, host.name,
    k8s.cluster.name, k8s.namespace.name, k8s.node.name,
    aws.resource.name, azure.resource.name, gcp.resource.name
  )))
```

**Multiple values (spread the user-supplied list):**

```dql-snippet
| filter in(array("<id1>","<id2>"), arrayRemoveNulls(array(
    toString(dt.smartscape_source.id),
    toString(dt.smartscape.process),
    toString(dt.smartscape.host),
    toString(dt.smartscape.k8s_cluster),
    toString(dt.smartscape.k8s_node),
    toString(dt.smartscape.k8s_pod),
    toString(dt.entity.host),
    toString(dt.entity.process_group),
    toString(dt.entity.process_group_instance),
    toString(dt.entity.kubernetes_cluster),
    toString(dt.entity.kubernetes_node),
    toString(dt.entity.cloud_application_namespace),
    toString(k8s.cluster.uid), toString(k8s.pod.uid),
    toString(aws.resource.id), toString(azure.resource.id), toString(gcp.resource.id),
    object.id, object.name, host.name,
    k8s.cluster.name, k8s.namespace.name, k8s.node.name,
    aws.resource.name, azure.resource.name, gcp.resource.name
  )))
```

Smartscape ID fields (`dt.smartscape.*`, `dt.smartscape_source.id`) are typed as
`SmartscapeId`; `toString()` converts them to string for uniform comparison with
user-supplied strings. `arrayRemoveNulls()` drops fields that are null on a given event
row — most events populate only a subset of these fields.

> **This OR-chain does NOT apply to RVA state/change events** (`VULNERABILITY_STATE_REPORT_EVENT`,
> `VULNERABILITY_STATUS_CHANGE_EVENT`). Those events embed entity refs in `affected_entity.*` and
> `related_entities.<group>.{ids,names}` — all §5 fields (`dt.smartscape*`, `dt.entity*`, etc.) are
> **null** on them. For entity scoping on RVA events see
> [vulnerabilities.md § Vulnerabilities on a specific entity](vulnerabilities.md#vulnerabilities-on-a-specific-entity-by-name-or-id)
> and [§17 RVA state/change events below](#rva-statechange-events).

**Trim to the relevant fields.** Omit namespaces that can't match the entity type in
question (e.g. drop `k8s.*` / cloud resource fields when searching for a host or process):

```dql-snippet
// Host/process scope only
| filter in("<entity_id_or_name>", arrayRemoveNulls(array(
    toString(dt.smartscape_source.id),
    toString(dt.smartscape.process),
    toString(dt.smartscape.host),
    toString(dt.entity.host),
    toString(dt.entity.process_group),
    toString(dt.entity.process_group_instance),
    object.id, object.name, host.name
  )))
```

---

## 6. Provider / Product Filter (case-insensitive)

Check whether the user-supplied value matches either `event.provider` (vendor name, e.g. `"crowdstrike"`), `product.vendor` or `product.name` (specific product, e.g. `"falcon"`). Lowercase both sides; the skill inlines already-lowercased string literals.

**Single value (discovery / unknown string):**

```dql-snippet
| filter in("<provider_or_product>", array(lower(event.provider), lower(product.vendor), lower(product.name)))
```

**Multiple values (discovery / unknown strings):**

```dql-snippet
| filter in(array("<p1>", "<p2>"), array(lower(event.provider), lower(product.vendor), lower(product.name)))
```

**Known provider — exact match preferred.** Once the provider string is confirmed via the discovery query (see [all-security-events.md § Providers & Products](all-security-events.md)), use exact equality to avoid false positives from providers whose names share a substring:

```dql-snippet
| filter event.provider == "<ExactProviderString>"
      OR product.name == "<ExactProductString>"
```

A provider may appear via two ingestion paths (e.g. direct integration and via AWS Security Hub). Combine both exact values with `OR` when both paths are active in the tenant.

Reserve `contains(lower(...))` for initial discovery or when the exact string is not yet known.

---

## 7. Time Window Conventions

| Pattern | Window | Why |
|---|---|---|
| DT RVA snapshots | **30m fixed** | Snapshot — captures latest 15-min state-report cycle; do not widen |
| DT KSPM snapshots | **1h fixed** | Aligned with scan-completion cycle inner-join; do not widen |
| RAP / external detection retrieval or current summary | `2h` first attempt | Event stream; matches Threats & Exploits app default — widen to `24h` only if zero rows returned |
| Cross-provider summary (aggregated count/breakdown) | **24h** | Summaries aggregate over time; broader window gives representative coverage |
| Single-finding drill-down (by id/title) | `24h` default | Point lookup |
| Coverage analysis | `7d` for discovery; `2h–24h` for recent scans | `VULNERABILITY_SCAN` events are sparse |

**Critical:** RVA and SPM are *snapshot* tools, not history. The 30m / 1h windows
are operational — they only ensure the latest state report or completed scan is
captured. They do NOT look back further. Don't widen them.

**Retrieval vs. summary distinction:** for detection queries, both retrieval and unqualified current summaries ("how many detections do I have?", "detections by severity", "show me latest detections") start at `2h` to match the Threats & Exploits app default, then widen to `24h` only when zero rows are returned. For non-detection cross-provider summaries (counts, breakdowns, "how many critical findings across providers") start at `24h` — these aggregate over time and a narrow window silently undercounts.

**DT-inclusive broad / posture-overview questions** ("which security products are integrated incl. Dynatrace-native?", posture overview, cross-category counts that include DT vulnerabilities/compliance) are **not** a single window — decompose into three streams, each on its own window (external + DT detections `24h`; DT RVA `30m`; DT KSPM `1h`), and merge. (A narrower "which external integrations are sending data?" stays a single external-only query.) See [all-security-events.md § Broad-Question Query Decomposition](all-security-events.md#broad-question-query-decomposition).

> **Detection-retrieval widen-on-empty rule:** start at `2h`; widen only when zero rows
> are returned. The authoritative fallback query and the list of intentionally-wider
> history/analytics exceptions live in
> [detections.md § Widen-on-empty fallback](detections.md).

> **Entity coverage empty-result rule:** when validating whether a **specific
> entity** is covered by a Dynatrace security capability, 0 relevant findings plus
> 0 relevant scan/scan-completed/coverage events means the entity is **not
> covered** by that capability. Explain that the capability is likely not enabled,
> not deployed, or not configured for that entity; do not present this as merely
> "no findings". See [coverage.md](coverage.md).

---

## 8. Dynatrace-vs-External Routing Logic

The cross-provider summary pattern excludes Dynatrace-native VULNERABILITY/COMPLIANCE findings (they
belong to the RVA and SPM snapshot patterns), but keeps Dynatrace-native DETECTION findings:

```dql-snippet
| filter (product.vendor != "Dynatrace" or event.type=="DETECTION_FINDING")
```

**Implication:** for full coverage of vulnerabilities or compliance, **pair**
the Dynatrace RVA snapshot pattern (vulnerabilities) or the Dynatrace SPM snapshot
pattern (compliance) with the cross-provider summary. Only `DETECTION_FINDING` is
fully covered by the cross-provider summary alone.

---

## 12. Repository / Artifact Coalescing

External container scanners use one of two repository fields. Coalesce so a single
column works for both:

```dql-snippet
| fieldsAdd repository=coalesce(artifact.repository, container_image.repository)
```

---

## 13. K8s Workload Resolution from CONTAINER smartscapeNode

A CONTAINER node is part of exactly one workload — fan out the workload reference
via nested `coalesce`:

```dql-snippet
| expand dt.k8s.workload.id=coalesce(references[is_part_of.k8s_deployment],
                            coalesce(references[is_part_of.k8s_daemonset],
                              coalesce(references[is_part_of.k8s_cronjob],
                                coalesce(references[is_part_of.k8s_statefulset],
                                  coalesce(references[is_part_of.k8s_job],
                                    references[is_part_of.k8s_replicaset])))))
```

For HOST resolution (CONTAINER → host) use `references[runs_on.host]` instead.

---

## 15. Default Summarization Recipe (cross-provider summary)

Without a user-specified summarization, the cross-provider summary pattern collapses
results by provider × product × event type × risk level. This is the safe default
for any time window:

> **Do not drop `by:` keys without an explicit user request.** The four keys —
> `{event.provider, product.name, event.type, dt.security.risk.level}` — are mandatory for any
> cross-provider count or summary. Dropping any one silently merges rows from different providers,
> products, or finding types into a single count, corrupting the result.
>
> For container images and external findings, also preserve `object.name` (user-friendly display
> name for the scanned artifact), `object.id`, and the repository/digest identity fields
> (`container_image.digest`, `coalesce(artifact.repository, container_image.repository)`) in the
> `summarize` or projection **before ranking**. Pair `object.name` with `digest` or `repository` —
> names alone are not unique across registries or providers.

```dql-snippet
| summarize {
    findings.count = count(),
    finding.ids = collectDistinct(finding.id),
    finding.titles = collectDistinct(finding.title),
    affected_object.types = collectDistinct(object.type),
    affected_object.ids = collectDistinct(object.id),
    affected_object.names = collectDistinct(object.name),
    affected_smartscape.node.ids = arrayRemoveNulls(collectArray(coalesce(dt.smartscape_source.id,
                                                                          dt.smartscape.process,
                                                                          dt.smartscape.host,
                                                                          dt.smartscape.k8s_cluster,
                                                                          dt.smartscape.k8s_node,
                                                                          dt.smartscape.k8s_pod))),
    related_entities.ids = arrayRemoveNulls(collectArray(coalesce(dt.entity.host,
                                                                  dt.entity.process_group,
                                                                  dt.entity.process_group_instance,
                                                                  dt.entity.kubernetes_cluster,
                                                                  dt.entity.kubernetes_node,
                                                                  dt.entity.cloud_application_namespace))),
    vulnerable_components = arrayRemoveNulls(collectDistinct(coalesce(software_component.name, component.name)))
  }, by: {event.provider, product.name, event.type, dt.security.risk.level}
```

For longer time ranges (>24h), **always** apply a summarization — raw field
selection past 24h hits performance limits.

---

## 16. Result Limits for Top-N and Raw Listings

Security findings can be high-volume. Any query that returns raw rows (no
`summarize` / `makeTimeseries`) must be bounded unless the user explicitly asks
for all rows or an export-style result.

**Required limit rule:**

| User intent | Required query shape |
|---|---|
| "top X" / "last X" / "first X" | `| sort <ranking fields> desc` then `| limit X` |
| "top findings" with no number | Treat as top 50: `| sort <ranking fields> desc` then `| limit 50` |
| "show/list/latest findings" with no explicit "all" | Add `| limit 50` after the final `sort` |
| Pure summary (`summarize`, `makeTimeseries`, pass-rate, counts) | No default raw-row limit required; optionally limit high-cardinality grouped rankings |
| Explicit "all" / export request | Do not silently truncate; warn about volume and prefer a summary or scoped filters |

**Placement:** apply `limit` after deduplication, enrichment, final projection, and the
final user-relevant `sort`. A limit before `summarize`, `join`, or entity enrichment
can bias counts or drop matching entities.

```dql-snippet
| fields timestamp, finding.id, finding.title, dt.security.risk.level,
         object.name, object.type, "dt.smartscape*"
| sort dt.security.risk.score desc, timestamp desc
| limit 50
```

For top-N summary tables, keep the aggregation grain first, then sort and limit:

```dql-snippet
| summarize Findings=countDistinctExact(finding.id), by:{event.provider, product.name, object.type}
| sort Findings desc
| limit 50
```

---

## 17. Entity-Identifier Preservation on Raw Listings

When a query projects raw rows for a listing (top / latest / list / drill-down — no `summarize`), keep the entity-identifier namespaces in the projection. Users asking for findings almost always want to know which entity each finding is on.

**The namespaces split by event family — they are NOT interchangeable:**

### Cross-provider `*_FINDING` and scan-coverage events

Applies to `DETECTION_FINDING`, `COMPLIANCE_FINDING`, external `VULNERABILITY_FINDING`, `VULNERABILITY_SCAN`, `COMPLIANCE_SCAN`. Post-ingest enrichment populates the generic Smartscape/entity namespaces on these events.

```dql-snippet
| fieldsKeep timestamp, "dt.smartscape*", "dt.entity*", "dt.source*",
            <finding-specific fields…>
```

What the wildcards match:

| Wildcard | Generation | Covers |
|---|---|---|
| `dt.smartscape*` | 3rd-gen (Smartscape) | `dt.smartscape_source.id` (+ `.type`/`.name` if present) and `dt.smartscape.process` / `.host` / `.k8s_cluster` / `.k8s_node` / `.k8s_pod` |
| `dt.entity*` | 2nd-gen (classic) | `dt.entity.host`, `dt.entity.process_group`, `dt.entity.process_group_instance`, `dt.entity.kubernetes_cluster`, `dt.entity.kubernetes_node`, `dt.entity.cloud_application_namespace` — deprecated for Smartscape navigation, still valid as identifiers |
| `dt.source*` | Legacy / scan fallback | `dt.source_entity` — use only when the event family documents it explicitly (for example `VULNERABILITY_SCAN` coverage); do not make it the primary cross-provider finding correlation key |

### RVA state/change events

Applies to `VULNERABILITY_STATE_REPORT_EVENT`, `VULNERABILITY_STATUS_CHANGE_EVENT`, `VULNERABILITY_TRACKING_LINK_CHANGE_EVENT`. These events embed resolved entity refs directly in the event payload; the generic `dt.smartscape*` / `dt.entity*` / `dt.source*` namespaces are **null** on RVA events — including them would produce empty columns.

```dql-snippet
| fieldsKeep timestamp, "affected_entity*", "related_entities*",
            vulnerability.display_id, vulnerability.title, vulnerability.risk.score, …
```

`affected_entity.*` carries the directly affected entity (2nd-gen ID + name + type + vulnerable-component info, resolved in-event). `related_entities.{kubernetes_workloads,kubernetes_clusters,applications,services,hosts,databases}.{ids,names}` carries the indirect blast-radius entities (classic IDs + names) as arrays. Note: `.ids` carry classic entity IDs whose type prefix may differ from the group name — see [vulnerabilities.md § Classic ID prefix gotcha](vulnerabilities.md#classic-id-prefix-gotcha).

### When NOT to apply this

Pure summary queries — counts, pass rates, breakdown-by-risk-level, "how many" questions — should not project entity fields; aggregate them into the `summarize` block instead (see §15 cross-provider summary recipe and §16 RVA Stage 2 related-entity aggregation).

### Don't double-list on RVA Stage 3 output

If the query starts from the canonical RVA Stage 3 pipeline ([vulnerabilities.md](vulnerabilities.md)), Stage 3 already `collectDistinct`'s `affected_entity.ids/names` and `arrayConcat`'s `related_entities.*` into per-vulnerability arrays. Do not re-add `fieldsKeep "affected_entity*"` on top — those columns are already present as scalars in the post-summarize result.

---

## 18. Lifecycle — what counts as "new" / "resolved" (per event family)

"New" and "resolved" are detected differently per family — use the right signal:

| Family | "New" signal | "Resolved" signal |
|---|---|---|
| External findings (one-shot `*_FINDING`) | `toTimestamp(finding.time.created) > now()-Nd` | not modeled — compare presence across periods (anti-join; see the "new-not-in-prior-period" patterns in [vulnerabilities.md](vulnerabilities.md) / [compliance.md](compliance.md)) |
| DT RVA vulnerabilities (snapshot) | newly **OPEN**: `toTimestamp(vulnerability.resolution.change_date) > now()-Nd` (no "first-ever-seen" variant — `vulnerability.first_seen` is null on this pipeline) | `vulnerability.resolution.status == "RESOLVED"` (use `resolution.change_date` for when) |
| DT SPM compliance (per-rule/object snapshot) | rule-object pair absent in the prior scan period — period-over-period anti-join (see [compliance.md](compliance.md) § Week-over-Week Config Drift) | pair present in the prior period, absent now |

Keep the RVA/SPM snapshot fetch window fixed (30m / 1h) — apply the "new" horizon as a
**post-derive filter**, never by widening the fetch (see § 7).

### Two distinct "new" intents — do not conflate them

1. **"New(ly created) in the last N days"** — a property of each finding in
   isolation. The created-time filter from the table above is the correct and
   complete answer.
2. **"Reported in this period AND NOT in the previous period"** (also: "newly
   failing", "drift vs last week", "what appeared this week that wasn't there
   before") — a **set comparison between two periods**. This REQUIRES the
   prior-period anti-join (outer join + `isNull(right.…)`); a
   `finding.time.created` filter is **not equivalent**: external providers
   re-report long-known findings on every scan, `finding.time.created` is
   unreliable or vendor-relative for many providers, and the created-time
   shortcut silently misses findings that existed before but were first
   *reported to Dynatrace* this period. Canonical anti-join templates:
   - external vulnerabilities → [vulnerabilities-external.md § Critical external vulnerabilities newly reported in the last 7d](vulnerabilities-external.md#critical-external-vulnerabilities-newly-reported-in-the-last-7d-not-in-the-prior-7d)
   - external compliance → [compliance.md § External Compliance](compliance.md)
   - DT KSPM drift → [compliance.md § Week-over-Week Config Drift](compliance.md#dt-spm-week-over-week-config-drift-newly-failing-rules)
