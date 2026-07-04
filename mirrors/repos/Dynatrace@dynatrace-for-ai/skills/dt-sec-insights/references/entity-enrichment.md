# Entity Enrichment — Map Security Findings to Dynatrace Entities

Maps external security findings from `security.events` to Dynatrace entities to
produce per-entity risk-level breakdowns (Critical / High / Medium / Low counts).

> **DT-native RVA entity rankings** ("most vulnerable hosts / workloads / components")
> live in [vulnerabilities-entities.md](vulnerabilities-entities.md) — they build on the
> RVA snapshot pipeline rather than the external-finding joins below.

> ⚠️ **"Map findings to workloads / hosts / cloud entities" REQUIRES the
> Smartscape join — grouping findings by raw name fields is NOT entity
> mapping.** Summarizing `security.events` by `k8s.namespace.name`,
> `host.name`, `object.name`, or `aws/azure/gcp.resource.id` alone skips the
> reconciliation against the tenant's actual topology: names are not unique
> across clusters/registries, stale or non-Smartscape objects are mixed in, and
> the same entity reported under different identifiers is double-counted. Use
> the canonical recipes in this file — [3-way match](#3-way-match-strategy) for
> K8s workloads, [host-by-IP](#host-enrichment-by-ip) for hosts,
> [Path 1](#cloud-entity-enrichment-path-1-only) for cloud entities — every one
> of which joins findings to `smartscapeNodes` (or classic entity tables)
> before counting. Fall back to raw-field grouping only if the pre-flight check
> shows the tenant's findings carry no resolvable identifiers, and say so
> explicitly in the answer.

> **No `dt.system.bucket` filter.** Security event data may live in any bucket;
> bucket scoping risks hiding data.

All queries in this file:

- Start with `fetch security.events` (not `smartscapeNodes`)
- Use `dedup {event.provider, finding.id, object.id, dt.security.risk.level}` to
  deduplicate findings before joining
- Output: `{Critical, High, Medium, Low}` counts grouped by entity

> **vs. [coverage.md](coverage.md)** — coverage queries start from `smartscapeNodes`
> and count entities as covered/not-covered. Enrichment queries start from
> findings and sum risk levels per matched entity.

> **Verifying external vulnerabilities with RVA:** if the user asks whether
> external vendor vulnerability findings are also detected by RVA, do not stop at
> entity enrichment. Use [vulnerabilities-external.md § Verify external
> vulnerability findings with RVA](vulnerabilities-external.md#verify-external-vulnerability-findings-with-rva): first match the same CVE via
> `vulnerability.references.cve`, then prove runtime relatedness through direct
> `dt.smartscape*` IDs, container-image digest → running container/workload, or
> host IP → Smartscape HOST.

---

## Contents

- [Entity Enrichment — Map Security Findings to Dynatrace Entities](#entity-enrichment--map-security-findings-to-dynatrace-entities)
  - [Contents](#contents)
  - [Problem → Affected Entities → Findings (two-query chain)](#problem--affected-entities--findings-two-query-chain)
    - [Step 1 — pull entity IDs from `dt.davis.problems`](#step-1--pull-entity-ids-from-dtdavisproblems)
    - [Step 2 — scope `security.events` to those entities](#step-2--scope-securityevents-to-those-entities)
  - [3-Way Match Strategy](#3-way-match-strategy)
    - [Natural-language entity name fallback](#natural-language-entity-name-fallback)
  - [Cloud Entity Enrichment (Path 1 only)](#cloud-entity-enrichment-path-1-only)
  - [K8s Workload Enrichment (Paths 1 + 2 + 3)](#k8s-workload-enrichment-paths-1--2--3)
    - [Pre-flight check — do external findings even carry K8s-resolvable identifiers?](#pre-flight-check--do-external-findings-even-carry-k8s-resolvable-identifiers)
    - [Canonical 3-way enrichment](#canonical-3-way-enrichment)
  - [Host Enrichment by IP](#host-enrichment-by-ip)
  - [Host Enrichment by Entity (Paths 1 + 2 + 3)](#host-enrichment-by-entity-paths-1--2--3)
  - [Best Practices](#best-practices)

---

## Problem → Affected Entities → Findings (two-query chain)

**Use case:** "What security findings exist for the entities affected by Davis problem P-XXX?" The prompt expects a two-step flow: pull the problem's entities first, then scope `security.events` to those IDs.

### Step 1 — pull entity IDs from `dt.davis.problems`

```dql
fetch dt.davis.problems, from:now()-7d
| filter display_id == "P-260575"
| fields affected_entity_ids,
         dt.entity.service, dt.entity.process_group, dt.entity.host,
         dt.entity.cloud_application, dt.entity.cloud_application_namespace,
         dt.entity.kubernetes_cluster
| limit 1
```

`affected_entity_ids` is Davis's canonical list (usually the root-cause entities). The `dt.entity.*` arrays add the topology context Davis traversed — process groups, hosts, clusters — which is what `security.events` actually carries on per-finding rows.

### Step 2 — scope `security.events` to those entities

`security.events` has no single `entity.id` field; different finding types put the entity ID in different places:

> **Broad entity-security questions must include external findings.** For prompts
> such as "what are the security findings of this K8s node/host/workload/cluster?",
> run the DT-native entity-scoped streams (RVA `30m`, SPM/KSPM `1h`) **and** this
> external/cross-provider `*_FINDING` branch (`24h`). Do not answer only from RVA
> and SPM. External providers may attach entity context through
> `dt.smartscape_source.id`, `dt.entity.*`, `object.*`, or `k8s.*` fields;
> include the wide OR-chain and
> report explicitly when it returns 0 rows.

| Finding type | Entity field on the row |
|---|---|
| `VULNERABILITY_STATE_REPORT_EVENT` / `VULNERABILITY_STATUS_CHANGE_EVENT` (DT RVA) | `affected_entity.id` (typically `PROCESS_GROUP-...`) |
| `VULNERABILITY_FINDING` (cross-provider) | `dt.smartscape_source.id`, `dt.entity.*`, `object.id`, or topology fallback (`k8s.cluster.name`, `k8s.namespace.name`) |
| `DETECTION_FINDING` | `dt.smartscape_source.id`, `dt.entity.*`, `object.id` |
| `COMPLIANCE_FINDING` (KSPM + external) | `object.id`; use `dt.entity.*` / `dt.smartscape_source.id` only when present |

Combine all three with `or`. Reference the [Wide Entity Scoping OR Chain](common-patterns.md#5-wide-entity-scoping-or-chain) for the broader version that also covers smartscape IDs and cloud resource IDs.

```dql-template
fetch security.events, from:now()-2h
| filter in(event.type, {"VULNERABILITY_STATE_REPORT_EVENT",
                          "VULNERABILITY_FINDING",
                          "DETECTION_FINDING",
                          "COMPLIANCE_FINDING"})
// Substitute the IDs you got from Step 1 into both DT-native and cross-provider lists
| filter in(affected_entity.id, array("SERVICE-E8BD4388A2B88105","PROCESS_GROUP-EAE7D4CE3B29873F","KUBERNETES_CLUSTER-EC20BE47C92F23E4"))
      or in(object.id,          array("SERVICE-E8BD4388A2B88105","PROCESS_GROUP-EAE7D4CE3B29873F","KUBERNETES_CLUSTER-EC20BE47C92F23E4"))
  or in(toString(dt.smartscape_source.id), array("SERVICE-E8BD4388A2B88105","PROCESS_GROUP-EAE7D4CE3B29873F","KUBERNETES_CLUSTER-EC20BE47C92F23E4"))
  or in(toString(dt.entity.host), array("SERVICE-E8BD4388A2B88105","PROCESS_GROUP-EAE7D4CE3B29873F","KUBERNETES_CLUSTER-EC20BE47C92F23E4"))
  or in(toString(dt.entity.process_group), array("SERVICE-E8BD4388A2B88105","PROCESS_GROUP-EAE7D4CE3B29873F","KUBERNETES_CLUSTER-EC20BE47C92F23E4"))
| summarize {
    findings  = count(),
    Critical  = countIf(dt.security.risk.level == "CRITICAL" or compliance.rule.severity.level == "CRITICAL"),
    High      = countIf(dt.security.risk.level == "HIGH"     or compliance.rule.severity.level == "HIGH"),
    Medium    = countIf(dt.security.risk.level == "MEDIUM"   or compliance.rule.severity.level == "MEDIUM"),
    Low       = countIf(dt.security.risk.level == "LOW"      or compliance.rule.severity.level == "LOW"),
    topTitles = arraySlice(collectDistinct(finding.title), from: 0, to: 10)
  }, by: {event.type, event.provider, product.name}
| sort Critical desc, High desc, findings desc
```

Notes:
- The compliance severity field is `compliance.rule.severity.level` (KSPM) — distinct from `dt.security.risk.level` (RVA + cross-provider findings). The `or`-coalesce above counts both.
- If the problem is service-level but vulnerabilities live on the underlying process group, you need the PG ID from Step 1's `dt.entity.process_group` array — that's why we pull all topology arrays, not just `affected_entity_ids`.
- For wider topology coverage (e.g. "all findings on any workload in the same namespace as the problem's service"), fall back to `k8s.namespace.name` / `k8s.cluster.name` matching — same idiom, broader scope.

---

## 3-Way Match Strategy

External findings link to runtime entities via three independent paths. For K8s
workloads and hosts, the three are combined with `append` to maximize match rate:

| Path | Match key | Resolution mechanism |
|---|---|---|
| 1 | `dt.smartscape_source.id` | Direct join on K8s workload / host Smartscape ID |
| 2 | `container_image.digest` | CONTAINER smartscapeNode → `references[is_part_of.*]` → parent workload (or `runs_on.host` → host) |
| 3 | `container_image.id` | `dt.entity.container_group_instance` → `belongs_to[cloud_application]` → workload (or nested lookup → host) |

> **Path 1 prerequisite — workload-level granularity.** Path 1 matches only when
> `dt.smartscape_source.id` identifies a K8s **workload** node
> (`K8S_DEPLOYMENT`, `K8S_DAEMONSET`, `K8S_STATEFULSET`, etc.). External providers
> commonly populate this field at coarser or unrelated granularity — the namespace,
> the cluster, or cloud resources (EC2, VM, S3, container registry) — in which case
> Path 1 returns 0 even though the field is non-null. Check `dt.smartscape_source.type`
> in the pre-flight (below) before interpreting a populated count as workload-resolvable.
> **Path 2 (`container_image.digest`) is the reliable container-to-workload path.**

Cloud entity enrichment is simpler — only Path 1 (`dt.smartscape_source.id`) is
needed. Host-by-IP enrichment uses IP address matching instead of any of the
three paths above.

### Natural-language entity name fallback

If a service/workload/host name cannot be resolved through an entity lookup tool,
search `security.events` directly before giving up. Security rows often preserve
names in `object.name`, `affected_entity.name`, and `related_entities.*.names`
even when a separate topology lookup misses the entity.

```dql
fetch security.events, from:now()-24h
| filter in(event.type, {"VULNERABILITY_STATE_REPORT_EVENT",
                         "VULNERABILITY_STATUS_CHANGE_EVENT",
                         "VULNERABILITY_TRACKING_LINK_CHANGE_EVENT",
                         "VULNERABILITY_FINDING",
                         "DETECTION_FINDING",
                         "COMPLIANCE_FINDING"})
| filter contains(lower(object.name), lower("unguard-profile-service"))
      OR contains(lower(affected_entity.name), lower("unguard-profile-service"))
      OR iAny(contains(lower(related_entities.services.names[]), lower("unguard-profile-service")))
      OR iAny(contains(lower(related_entities.kubernetes_workloads.names[]), lower("unguard-profile-service")))
      OR iAny(contains(lower(related_entities.hosts.names[]), lower("unguard-profile-service")))
| fieldsKeep timestamp, event.type, event.provider, product.name,
            finding.title, vulnerability.title, dt.security.risk.level,
            object.id, object.name, affected_entity.id, affected_entity.name,
            "related_entities*"
| limit 100
```

---

## Cloud Entity Enrichment (Path 1 only)

```dql
fetch security.events
| filter exists(dt.smartscape_source.id)
| dedup {event.provider, finding.id, object.id, dt.security.risk.level}, sort: {timestamp desc}
| join [
  smartscapeNodes "*", from:now()-24h
  | filter exists(cloud.provider)
], on:{left[dt.smartscape_source.id]==right[id]}, fields:{name}
| summarize {
  Critical=countIf(dt.security.risk.level=="CRITICAL"),
  High=countIf(dt.security.risk.level=="HIGH"),
  Medium=countIf(dt.security.risk.level=="MEDIUM"),
  Low=countIf(dt.security.risk.level=="LOW")
}, by:{Type=dt.smartscape_source.type, dt.smartscape_source.id, Name=name}
| sort {Critical,direction:"descending"}, {High,direction:"descending"},
       {Medium,direction:"descending"}
```

---

## K8s Workload Enrichment (Paths 1 + 2 + 3)

> **Always use the 3-way enrichment recipe below — never fall back to `object.name` alone.**
> `object.name` is not unique across clusters or namespaces; matching on it alone collapses
> findings from different workloads with the same display name and produces wrong counts.
> All three paths (Smartscape ID, container digest, container image ID) must be attempted:
> any single path misses findings that lack the identifier it keys on.

### Pre-flight check — do external findings even carry K8s-resolvable identifiers?

Before running the full 3-way K8s enrichment, run a single pre-flight to confirm
the external findings actually carry fields that can resolve to K8s topology.
External providers vary widely — many scope to cloud resources (e.g. compute /
storage / IAM), not to Kubernetes workloads. If none of the three identifier
families is populated, the 3-way append will return zero rows after considerable
work; report that upfront instead of iterating:

```dql
fetch security.events, from:now()-24h
| filterOut event.provider == "Dynatrace" or product.vendor == "Dynatrace"
| filter in(event.type, {"VULNERABILITY_FINDING", "DETECTION_FINDING", "COMPLIANCE_FINDING"})
| summarize {
    findings = count(),
    `has container_image.digest`  = countIf(isNotNull(container_image.digest)),
    `has container_image.id`      = countIf(isNotNull(container_image.id)),
    `has dt.smartscape_source.id` = countIf(isNotNull(dt.smartscape_source.id))
  }, by: {event.provider, product.name}
```

If `has dt.smartscape_source.id` is >0, run a second query to check the actual
entity granularity — a non-zero count does **not** guarantee workload-level resolution:

```dql
// Check what entity types dt.smartscape_source.id resolves to:
fetch security.events, from:now()-24h
| filterOut event.provider == "Dynatrace" or product.vendor == "Dynatrace"
| filter isNotNull(dt.smartscape_source.id)
| summarize Count=count(), by:{event.provider, dt.smartscape_source.type}
| sort Count desc
```

Path 1 yields matches only when `dt.smartscape_source.type` is a K8s workload type
(`K8S_DEPLOYMENT`, `K8S_DAEMONSET`, `K8S_STATEFULSET`, `K8S_CRONJOB`, `K8S_JOB`,
`K8S_REPLICASET`). If it resolves to a namespace, a cluster, or a cloud-resource type
(EC2, VM, S3, container registry, etc.), Path 1 returns 0 — use Path 2/3 for those providers.

If all three identifier counts are 0 across providers, the external findings
target non-K8s entities (EC2 / S3 / IAM / etc.) and no K8s workload mapping is
possible. Report this directly — "X external findings present but none carry
K8s-resolvable identifiers; the findings target {AWS::EC2::Instance,
AWS::S3::Bucket, …}" — rather than running the full enrichment to confirm zero.

When the pre-flight shows at least one identifier path populated, proceed with
the full enrichment below.

### Canonical 3-way enrichment

A final `dedup` after `append` removes duplicates introduced by multiple matching
paths.

```dql
fetch security.events, from:now()-7d
| filter exists(dt.smartscape_source.id) and isNotNull(dt.smartscape_source.id)
| dedup {event.provider, finding.id, object.id, dt.security.risk.level}, sort: {timestamp desc}
| join [
  smartscapeNodes {K8S_DEPLOYMENT, K8S_CRONJOB, K8S_DAEMONSET, K8S_JOB, K8S_STATEFULSET, K8S_REPLICASET}, from:now()-2h
], on:{left[dt.smartscape_source.id]==right[id]},
   fields:{
  containerNames=name, dt.smartscape_source.id=id, classic_entity.id=id_classic, workloadName=k8s.workload.name
   }
| append [
  fetch security.events
  | filter isNotNull(container_image.digest)
  | dedup {container_image.digest, event.provider, finding.id, object.id, dt.security.risk.level}, sort: {timestamp desc}
  | join [
    smartscapeNodes CONTAINER, from:now()-2h
    | expand dt.k8s.workload.id=coalesce(references[is_part_of.k8s_deployment],
                           coalesce(references[is_part_of.k8s_daemonset],
                             coalesce(references[is_part_of.k8s_cronjob],
                               coalesce(references[is_part_of.k8s_statefulset],
                                 coalesce(references[is_part_of.k8s_job],
                                   references[is_part_of.k8s_replicaset])))))
    | filter isNotNull(dt.k8s.workload.id)
    | fieldsAdd dt.smartscape_source.id=dt.k8s.workload.id
  ], kind:leftOuter, on:{left[container_image.digest]==right[container.image.digest]},
    fields:{
      containerNames=name, dt.smartscape_source.id, classic_entity.id=id_classic, workloadName=k8s.workload.name
    }
]
| append [
    fetch security.events
    | filter isNotNull(container_image.id)
    | join [
        fetch dt.entity.container_group_instance, from:now()-2h
        | fieldsAdd containerNames, containerImageId,
                    container_group.id=instance_of[dt.entity.container_group],
                    workload.id=belongs_to[dt.entity.cloud_application], workloadName
        | fieldsAdd classic_entity.id=coalesce(workload.id,container_group.id)
        | lookup [
          smartscapeNodes {K8S_DEPLOYMENT, K8S_CRONJOB, K8S_DAEMONSET, K8S_JOB, K8S_STATEFULSET, K8S_REPLICASET}, from:now()-2h
        ], sourceField:workload.id, lookupField:id_classic, fields:{dt.smartscape_source.id=id}
    ], kind:leftOuter, on:{left[container_image.id]==right[containerImageId]},
       fields:{containerNames, dt.smartscape_source.id, classic_entity.id, workloadName}
]
| filterOut isNull(classic_entity.id)
| dedup {dt.smartscape_source.id, classic_entity.id, containerNames, workloadName,
         container_image.digest, event.provider, finding.id, object.id, dt.security.risk.level},
        sort:{timestamp desc}
| summarize {
  Containers=arrayDistinct(arrayFlatten(collectDistinct(containerNames))),
  Critical=countIf(dt.security.risk.level=="CRITICAL"),
  High=countIf(dt.security.risk.level=="HIGH"),
  Medium=countIf(dt.security.risk.level=="MEDIUM"),
  Low=countIf(dt.security.risk.level=="LOW")
}, by:{dt.smartscape_source.id, classic_entity.id, Workload=workloadName}
| sort {Critical,direction:"descending"}, {High,direction:"descending"},
       {Medium,direction:"descending"}
```

### External findings mapped to K8s workloads — with identity preserved

This is the canonical recipe for "map external security findings to K8s workloads". It uses the full 3-way match and preserves container image identity (`object.name`, `container_image.digest`, `container_image.repository` / `artifact.repository`) alongside workload identity before ranking, so findings from different registries or image versions are never collapsed.

Run the pre-flight check first to confirm at least one identifier path is populated.

```dql
// Scope: external findings only; exclude Dynatrace-native
fetch security.events, from:now()-24h
| filterOut event.provider == "Dynatrace" OR product.vendor == "Dynatrace"
| filter in(event.type, {"VULNERABILITY_FINDING", "DETECTION_FINDING", "COMPLIANCE_FINDING"})
// SD-isNotNull guard — mandatory
| filter isNotNull(finding.id) AND isNotNull(object.id) AND isNotNull(dt.security.risk.level)
// Repository coalescing
| fieldsAdd repository = coalesce(artifact.repository, container_image.repository)

// Path 1: direct Smartscape ID match
| filter exists(dt.smartscape_source.id) AND isNotNull(dt.smartscape_source.id)
| dedup {event.provider, finding.id, object.id, dt.security.risk.level}, sort: {timestamp desc}
| join [
    smartscapeNodes {K8S_DEPLOYMENT, K8S_CRONJOB, K8S_DAEMONSET, K8S_JOB, K8S_STATEFULSET, K8S_REPLICASET}, from:now()-2h
  ], on:{left[dt.smartscape_source.id]==right[id]},
      fields:{dt.smartscape_source.id=id, classic_entity.id=id_classic, workloadName=k8s.workload.name}

// Path 2: container digest → CONTAINER node → parent workload
| append [
    fetch security.events, from:now()-24h
    | filterOut event.provider == "Dynatrace" OR product.vendor == "Dynatrace"
    | filter in(event.type, {"VULNERABILITY_FINDING", "DETECTION_FINDING", "COMPLIANCE_FINDING"})
    | filter isNotNull(container_image.digest)
    | fieldsAdd repository = coalesce(artifact.repository, container_image.repository)
    | dedup {container_image.digest, event.provider, finding.id, object.id, dt.security.risk.level}, sort: {timestamp desc}
    | join [
        smartscapeNodes CONTAINER, from:now()-2h
        | expand dt.k8s.workload.id=coalesce(references[is_part_of.k8s_deployment],
                               coalesce(references[is_part_of.k8s_daemonset],
                                 coalesce(references[is_part_of.k8s_cronjob],
                                   coalesce(references[is_part_of.k8s_statefulset],
                                     coalesce(references[is_part_of.k8s_job],
                                       references[is_part_of.k8s_replicaset])))))
        | filter isNotNull(dt.k8s.workload.id)
        | fieldsAdd dt.smartscape_source.id=dt.k8s.workload.id
      ], kind:leftOuter, on:{left[container_image.digest]==right[container.image.digest]},
        fields:{dt.smartscape_source.id, classic_entity.id=id_classic, workloadName=k8s.workload.name}
  ]

// Path 3: container image ID → dt.entity.container_group_instance → workload
| append [
    fetch security.events, from:now()-24h
    | filterOut event.provider == "Dynatrace" OR product.vendor == "Dynatrace"
    | filter in(event.type, {"VULNERABILITY_FINDING", "DETECTION_FINDING", "COMPLIANCE_FINDING"})
    | filter isNotNull(container_image.id)
    | fieldsAdd repository = coalesce(artifact.repository, container_image.repository)
    | join [
        fetch dt.entity.container_group_instance, from:now()-2h
        | fieldsAdd containerImageId, workload.id=belongs_to[dt.entity.cloud_application], workloadName
        | lookup [
            smartscapeNodes {K8S_DEPLOYMENT, K8S_CRONJOB, K8S_DAEMONSET, K8S_JOB, K8S_STATEFULSET, K8S_REPLICASET}, from:now()-2h
          ], sourceField:workload.id, lookupField:id_classic, fields:{dt.smartscape_source.id=id}
      ], kind:leftOuter, on:{left[container_image.id]==right[containerImageId]},
         fields:{dt.smartscape_source.id, classic_entity.id=workload.id, workloadName}
  ]

| filterOut isNull(classic_entity.id)
// Final dedup — same finding may match multiple paths
| dedup {dt.smartscape_source.id, classic_entity.id, event.provider, finding.id, object.id, dt.security.risk.level},
        sort:{timestamp desc}
// Preserve full identity before ranking: workload + image + repository + provider
| summarize {
    Critical = countIf(dt.security.risk.level == "CRITICAL"),
    High = countIf(dt.security.risk.level == "HIGH"),
    Medium = countIf(dt.security.risk.level == "MEDIUM"),
    Low = countIf(dt.security.risk.level == "LOW"),
    image.objects = collectDistinct(object.name),
    image.digests = collectDistinct(container_image.digest),
    repositories = collectDistinct(repository),
    providers = collectDistinct(event.provider),
    finding.titles = collectDistinct(finding.title, maxLength: 10)
  }, by: {dt.smartscape_source.id, Workload = workloadName}
| sort Critical desc, High desc
```

---

## Host Enrichment by IP

Expands the `host.ip` array field, normalizes via `ip()`, then joins HOST
smartscapeNodes on IP.

```dql
fetch security.events, from:now()-24h
| filter isNotNull(host.ip)
| dedup {event.provider, finding.id, object.id, dt.security.risk.level}, sort:{timestamp desc}
| expand host.ip
| fieldsAdd host.ip=ip(host.ip)
| join [
  smartscapeNodes HOST
  | expand ip
], on:{left[host.ip]==right[ip]}, fields:{host.id=id, host.name=name}
| sort timestamp desc
| summarize {
  `Host name`=takeLast(host.name),
  IP=collectDistinct(host.ip),
  Critical=countIf(dt.security.risk.level=="CRITICAL"),
  High=countIf(dt.security.risk.level=="HIGH"),
  Medium=countIf(dt.security.risk.level=="MEDIUM"),
  Low=countIf(dt.security.risk.level=="LOW")
}, by:{host.id}
| sort {Critical,direction:"descending"}, {High,direction:"descending"},
       {Medium,direction:"descending"}
```

---

## Host Enrichment by Entity (Paths 1 + 2 + 3)

Same 3-way structure as K8s Workload Enrichment, but resolves to HOST entities.

- **Path 2:** CONTAINER → `runs_on.host` → HOST
- **Path 3:** container_group_instance → workload → `runs_on.host` nested lookup → HOST

```dql
fetch security.events
| filter exists(dt.smartscape_source.id) and isNotNull(dt.smartscape_source.id)
| dedup {event.provider, finding.id, object.id, dt.security.risk.level}, sort: {timestamp desc}
| join [
  smartscapeNodes {HOST}, from:now()-2h
], on:{left[dt.smartscape_source.id]==right[id]},
  fields:{hostName=name, dt.smartscape_source.id=id, host.classic.id=id_classic}
| append [
  fetch security.events
  | filter isNotNull(container_image.digest)
  | dedup {container_image.digest, event.provider, finding.id, object.id, dt.security.risk.level}, sort: {timestamp desc}
  | join [
    smartscapeNodes CONTAINER, from:now()-2h
    | expand dt.host.id=references[runs_on.host]
    | filter isNotNull(dt.host.id)
    | fieldsAdd dt.smartscape_source.id=dt.host.id
    | lookup [
      smartscapeNodes {HOST}, from:now()-2h
    ], sourceField:dt.smartscape_source.id, lookupField:id,
       fields:{hostName=name, host.classic.id=id_classic}
  ], kind:leftOuter, on:{left[container_image.digest]==right[container.image.digest]},
    fields:{hostName, dt.smartscape_source.id, host.classic.id}
]
| append [
    fetch security.events
    | filter isNotNull(container_image.id)
    | join [
        fetch dt.entity.container_group_instance, from:now()-2h
        | fieldsAdd containerNames, containerImageId,
                    container_group.id=instance_of[dt.entity.container_group],
                    workload.id=belongs_to[dt.entity.cloud_application], workloadName
        | lookup [
          smartscapeNodes {K8S_DEPLOYMENT, K8S_CRONJOB, K8S_DAEMONSET, K8S_JOB, K8S_STATEFULSET, K8S_REPLICASET}, from:now()-2h
          | expand dt.host.id=references[runs_on.host]
          | filter isNotNull(dt.host.id)
          | fieldsAdd dt.smartscape_source.id=dt.host.id
          | lookup [
            smartscapeNodes {HOST}, from:now()-2h
          ], sourceField:dt.smartscape_source.id, lookupField:id,
             fields:{hostName=name, host.classic.id=id_classic}
        ], sourceField:workload.id, lookupField:id_classic,
           fields:{dt.smartscape_source.id, host.classic.id, hostName}
    ], kind:leftOuter, on:{left[container_image.id]==right[containerImageId]},
       fields:{hostName, dt.smartscape_source.id, host.classic.id}
]
| filterOut isNull(host.classic.id)
| dedup {dt.smartscape_source.id, host.classic.id, hostName,
         event.provider, finding.id, object.id, dt.security.risk.level},
        sort:{timestamp desc}
| summarize {
  Critical=countIf(dt.security.risk.level=="CRITICAL"),
  High=countIf(dt.security.risk.level=="HIGH"),
  Medium=countIf(dt.security.risk.level=="MEDIUM"),
  Low=countIf(dt.security.risk.level=="LOW")
}, by:{dt.smartscape_source.id, host.classic.id, Host=hostName}
| sort {Critical,direction:"descending"}, {High,direction:"descending"},
       {Medium,direction:"descending"}
```

---

## Best Practices

1. **Use the 3-way match for K8s and host enrichment — never fall back to `object.name` alone.**
   `dt.smartscape_source.id` alone misses findings; container image digest and image ID paths
   catch the rest. `object.name` is not unique across clusters/namespaces and produces wrong counts.
2. **Cloud entities only need Path 1** — they don't traverse the container abstraction.
3. **Dedup early** — `dedup {event.provider, finding.id, object.id, dt.security.risk.level}`
   collapses re-ingested duplicates before joins.
4. **Dedup again after `append`** — the same finding can match multiple paths;
   the post-append dedup removes those duplicates.
5. **Use `from:now()-2h` on smartscapeNodes** — Smartscape topology is relatively
   stable; a 2-hour window is enough and keeps the join cheap.
6. **Preserve repository/image/digest/object/provider identity before ranking.** For container
   images and external findings, always include `object.name` (user-friendly display),
   `container_image.digest`, `artifact.repository` / `container_image.repository` (either may be
   populated — use `coalesce`), `object.id`, `object.type`, and `event.provider` in the
   `summarize ... by:` or pre-rank projection. Do not group by `object.name` alone — pair it with
   `digest` or `repository` to distinguish findings from different registries or image versions.
