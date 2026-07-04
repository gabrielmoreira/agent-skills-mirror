# Coverage Queries — Scan Events & Runtime Coverage

How to measure which processes, hosts, K8s workloads, and cloud entities are
covered by Dynatrace vulnerability scanning or by external security products.

> ⚠️ **Coverage means different things for runtime vs. non-runtime entities —
> pick the right shape first.**
>
> **Runtime entities** (hosts, processes, K8s workloads, cloud resources tracked
> in Smartscape) have a known total population, so coverage is a *percentage*
> (covered vs. not covered). These questions **REQUIRE a topology denominator —
> start from `smartscapeNodes`, never from `security.events` alone.** Compare the
> full entity population against scan/finding events via `lookup`. Scan events
> only exist for entities that *were* scanned, so summarizing them counts the
> covered set but can never reveal the uncovered set or a percentage.
>
> > **Anti-pattern for runtime-entity coverage (wrong — no denominator):**
> >
> > ```dql
> > fetch security.events, from:now()-1h
> > | filter event.type == "VULNERABILITY_SCAN"
> > | summarize scans = count(), entities = countDistinctExact(object.id),
> >     by: {event.provider, product.name}
> > ```
> >
> > For a *runtime* entity this answers "how many entities were scanned" — NOT
> > "what is my coverage". Use [§ DT Runtime Coverage Analysis](#dt-runtime-coverage-analysis-smartscapenodes)
> > instead; the scan-event-only queries in the first section are building blocks
> > for the `lookup` subquery, not standalone runtime-coverage answers.
>
> **Non-runtime entities** (container images, code artifacts, repositories) have
> **no Smartscape population to divide by**, so there is no percentage. Coverage
> here is simply a *count of distinct scanned objects* — and the scan-event
> summary above is the **correct** answer for this class (see [§ Non-Runtime
> Entity Coverage](#non-runtime-entity-coverage-images--artifacts)).
>
> **Build the "covered" set from scan events AND findings.** Scan events
> (`VULNERABILITY_SCAN` / `COMPLIANCE_SCAN`) are the preferred coverage signal,
> but some providers/features emit no scan event — in that case a *finding* on an
> entity also proves it was covered. Product coverage dashboards union the two.
> When scan events may be missing, `lookup`/`join` both scan events and findings
> and treat an entity as covered if it appears in either (the container-image
> recipe below already does this).

> **Specific-entity coverage interpretation:** when the user asks whether a
> named entity is covered by a Dynatrace security capability (for example, RVA on
> a host/process/workload, SPM/KSPM on a K8s cluster, RAP on a service/process, or
> another DT-native capability), query the capability-specific coverage signals
> and findings in the correct operational window. If **no relevant scan,
> scan-completed, coverage, or finding events** exist for that entity, answer that
> the entity is **not covered** by that capability. The likely reason is that the
> capability is not enabled, not deployed, or not configured to monitor that
> entity. Do not answer only "no findings" when the user asked about coverage.

> **`VULNERABILITY_SCAN` is the current event type for scan coverage.**
> `VULNERABILITY_COVERAGE_REPORT_EVENT` is **deprecated** — do not use in new
> queries.

> **`product.feature` distinguishes RVA modes** — `Code-level Vulnerability
> Analytics` vs. third-party VA. Filter or filterOut on this to scope.

---

## Contents

- [DT Vulnerability Scan Events](#dt-vulnerability-scan-events)
- [DT Runtime Coverage Analysis (smartscapeNodes)](#dt-runtime-coverage-analysis-smartscapenodes)
- [Non-Runtime Entity Coverage (Images & Artifacts)](#non-runtime-entity-coverage-images--artifacts)
- [External Product Coverage Analysis](#external-product-coverage-analysis)
  - [3-Way Match Strategy for Container-Based Entities](#3-way-match-strategy-for-container-based-entities)
  - [K8s Workload Coverage (count by provider/product)](#k8s-workload-coverage-count-by-providerproduct)
  - [Cloud Entity Coverage (count by provider/product)](#cloud-entity-coverage-count-by-providerproduct)
  - [Host Coverage by IP Match (count by provider/product)](#host-coverage-by-ip-match-count-by-providerproduct)
- [Best Practices](#best-practices)

---

## DT Vulnerability Scan Events

Scan events (`event.type == "VULNERABILITY_SCAN"`) mark which processes were
analyzed.

| Feature | `product.feature` filter |
|---|---|
| Third-party Vulnerability Analytics | `filterOut product.feature == "Code-level Vulnerability Analytics"` |
| Code-level Vulnerability Analytics | `filter product.feature == "Code-level Vulnerability Analytics"` |

**All Dynatrace scan coverage events for processes:**

```dql
fetch security.events
| filter event.type == "VULNERABILITY_SCAN" AND product.vendor=="Dynatrace"
| filter dt.source_entity.type == "process_group_instance"
```

**Covered processes — Third-party Vulnerability Analytics** (deduplicated per
host+process):

```dql
fetch security.events
| filter event.type == "VULNERABILITY_SCAN" AND product.vendor=="Dynatrace"
| filter dt.source_entity.type == "process_group_instance"
| filterOut product.feature == "Code-level Vulnerability Analytics"
| dedup dt.entity.host, dt.entity.process_group_instance
```

**Covered processes — Code-level Vulnerability Analytics only:**

```dql
fetch security.events
| filter event.type == "VULNERABILITY_SCAN" AND product.vendor=="Dynatrace"
| filter dt.source_entity.type == "process_group_instance"
| filter product.feature == "Code-level Vulnerability Analytics"
| dedup dt.entity.host, dt.entity.process_group_instance
```

---

## DT Runtime Coverage Analysis (smartscapeNodes)

> **Topology-start vs. events-start.** For "what's NOT covered" questions
> (entities present in topology but findings missing), **start from
> `smartscapeNodes`** and `lookup` the scan events. For "covered with what?"
> questions (findings present and you want to know which entities they map to),
> start from `security.events` and join back to topology. The wrong start
> direction produces structurally-correct queries that under- or over-count.

Start from Smartscape topology, then `lookup` scan events to classify entities as
covered vs. not covered.

> **Scan-only is sufficient for DT process/host coverage.** Dynatrace RVA emits a
> `VULNERABILITY_SCAN` event for every analyzed process, so the scan-event lookup
> below is a reliable covered-set on its own. The scan-events-**and**-findings
> union (top of file) matters for **external products** and any feature that may
> not emit a scan event — there a finding on the entity is the only proof it was
> covered (see the container-image recipe, which `lookup`s findings).

**Process coverage — Third-party Vulnerability Analytics:**

```dql
smartscapeNodes PROCESS
| lookup [
    fetch security.events
    | filter event.type == "VULNERABILITY_SCAN"
    | filter dt.source_entity.type == "process_group_instance"
    | filterOut product.feature == "Code-level Vulnerability Analytics"
    | dedup dt.entity.host, dt.entity.process_group_instance
    | fields dt.entity.process_group_instance
  ],
  sourceField: id_classic, lookupField: dt.entity.process_group_instance
| fieldsAdd coverageStatus = if(isNull(lookup.dt.entity.process_group_instance), "not covered", else: "covered")
| summarize count(), by: { coverageStatus }
```

**Host coverage — Third-party Vulnerability Analytics:**

```dql
smartscapeNodes HOST
| dedup id_classic
| lookup [
    fetch security.events
    | filter event.type == "VULNERABILITY_SCAN"
    | filter dt.source_entity.type == "process_group_instance"
    | filterOut product.feature == "Code-level Vulnerability Analytics"
    | fieldsKeep dt.entity.host
    | dedup dt.entity.host
  ],
  sourceField: id_classic, lookupField: dt.entity.host, prefix: "scan.events."
| fields id_classic,
         coverage = if(isNotNull(scan.events.dt.entity.host), "covered", else: "not covered")
| summarize hosts = count(), by: { coverage }
| fieldsKeep hosts, coverage
```

**Uncovered hosts — list form:**

```dql
smartscapeNodes HOST
| dedup id_classic
| lookup [
    fetch security.events
    | filter event.type == "VULNERABILITY_SCAN"
    | filter dt.source_entity.type == "process_group_instance"
    | filterOut product.feature == "Code-level Vulnerability Analytics"
    | fieldsKeep dt.entity.host
    | dedup dt.entity.host
  ],
  sourceField: id_classic, lookupField: dt.entity.host, prefix: "scan.events."
| fields id_classic, name,
         coverage = if(isNotNull(scan.events.dt.entity.host), "covered", else: "not covered")
| filter coverage == "not covered"
| sort name asc
```

### Interpreting `0 not covered` results

**When `not covered = 0` is returned, that is a complete answer** — every host
in the topology has a matching `VULNERABILITY_SCAN` event. Do not re-query to
sanity-check. Instead, surface the total host count from the same query
(`summarize hosts = count(), by: { coverage }`) so the answer reads
`0 of N hosts uncovered` — that's the actionable form. To confirm scan
freshness, surface scan-event timestamps separately rather than re-running the
join.

---

## Non-Runtime Entity Coverage (Images & Artifacts)

Container images, code artifacts, and repositories are **not runtime entities**
and have no Smartscape population to divide by — so there is **no coverage
percentage**. Coverage for this class is a *count of distinct scanned objects*,
optionally broken down by provider/product. Here the scan-event summary (the
"anti-pattern" for runtime coverage) is the **correct** shape, because there is
no denominator to reconcile against.

Count the covered set from scan events **and** findings (a finding on an image
also proves it was covered, and some providers emit no scan event):

```dql
fetch security.events, from:now()-24h
| filter in(event.type, {"VULNERABILITY_SCAN", "VULNERABILITY_FINDING"})
| filter isNotNull(container_image.digest) or isNotNull(container_image.id)
| summarize {
    images = countDistinctExact(coalesce(container_image.digest, container_image.id))
  }, by: {event.provider, product.name}
| sort images desc
```

There is no "not covered" row here: without an authoritative image/artifact
inventory, the uncovered set is unknown. Report this as an absolute count, not a
ratio. (To answer "which *running workloads* have images with no findings" — a
runtime question with a denominator — use [§ K8s workloads with container images
that have no security findings](#k8s-workloads-with-container-images-that-have-no-security-findings)
instead.)

---

## External Product Coverage Analysis

Count entities covered (or not) by any external security product. These queries
start from Smartscape topology (not `security.events`) and join external findings.

### 3-Way Match Strategy for Container-Based Entities

External findings link to Dynatrace entities via three independent paths — all
three are combined with `append`:

| Path | Match key | Source node |
|---|---|---|
| 1 | `dt.smartscape_source.id` (direct entity ID) | finding → workload via Smartscape ID |
| 2 | `container_image.digest` | finding → CONTAINER smartscapeNode → parent workload |
| 3 | `container_image.id` | finding → `dt.entity.container_group_instance` → parent workload |

### K8s Workload Coverage (count by provider/product)

```dql
smartscapeNodes {K8S_DEPLOYMENT, K8S_CRONJOB, K8S_DAEMONSET, K8S_JOB, K8S_STATEFULSET, K8S_REPLICASET}
| fields dt.k8s.workload.id=id, containerNames=name
| join [
  fetch security.events
  | filterOut event.provider=="Dynatrace" or product.vendor=="Dynatrace"
  | filter exists(dt.smartscape_source.id)
  | filterOut isNull(event.type) or isNull(object.id)
  | dedup dt.smartscape_source.id, event.provider, product.name
  | fields dt.smartscape_source.id, event.provider, product.name
], kind:leftouter, on:{left[dt.k8s.workload.id]==right[dt.smartscape_source.id]},
   fields:{event.provider, product.name, dt.smartscape_source.id}
| append [
  smartscapeNodes CONTAINER
  | fields container.image.digest, references
  | expand dt.k8s.workload.id=coalesce(references[is_part_of.k8s_deployment],
                           coalesce(references[is_part_of.k8s_daemonset],
                             coalesce(references[is_part_of.k8s_cronjob],
                               coalesce(references[is_part_of.k8s_statefulset],
                                 coalesce(references[is_part_of.k8s_job],
                                   references[is_part_of.k8s_replicaset])))))
  | join [
    fetch security.events
    | filterOut event.provider=="Dynatrace" or product.vendor=="Dynatrace"
    | filter isNotNull(container_image.digest)
    | filterOut isNull(event.type) or isNull(object.id)
    | dedup event.provider, product.name, container_image.digest
    | fields event.provider, product.name, container_image.digest
  ], kind:leftOuter, on:{left[container.image.digest]==right[container_image.digest]},
    fields:{event.provider, product.name, container_image.digest}
]
| append [
  fetch dt.entity.container_group_instance
  | fields containerImageId, containerNames,
           container_group.id=instance_of[dt.entity.container_group],
           workload.id=belongs_to[dt.entity.cloud_application], workloadName
  | fieldsAdd dt.k8s.workload.id=coalesce(workload.id,container_group.id)
  | join [
    fetch security.events
    | filterOut event.provider=="Dynatrace" or product.vendor=="Dynatrace"
    | filter isNotNull(container_image.id)
    | filterOut isNull(event.type) or isNull(object.id)
    | dedup event.provider, product.name, container_image.id
    | fields event.provider, product.name, container_image.id
  ], kind:leftOuter, on:{left[containerImageId]==right[container_image.id]},
    fields:{event.provider, product.name, container_image.digest=container_image.id}
]
| fieldsAdd Product=if(isNotNull(container_image.digest) or isNotNull(dt.smartscape_source.id), product.name, else:"Not covered")
| fieldsAdd Provider=if(isNotNull(container_image.digest) or isNotNull(dt.smartscape_source.id), event.provider, else:"Not covered")
| summarize {Entities=countDistinctExact(dt.k8s.workload.id)}, by:{Provider, Product}
| sort Entities desc
```

### K8s workloads with container images that have no security findings

Start from workload topology, expand container image identifiers, then anti-join
security findings. If the pre-flight in
[entity-enrichment.md § K8s Workload Enrichment](entity-enrichment.md#k8s-workload-enrichment-paths-1--2--3)
shows no container-image identifiers in external findings, report that the
tenant cannot answer this as a coverage gap rather than treating zero findings
as proof of safety.

```dql
smartscapeNodes {K8S_DEPLOYMENT, K8S_CRONJOB, K8S_DAEMONSET, K8S_JOB, K8S_STATEFULSET, K8S_REPLICASET}
| fields workload.id = id,
         workload.name = name,
         replicaCount = coalesce(k8s.deployment.replicas.desired,
                         coalesce(k8s.statefulset.replicas.desired,
                                  coalesce(k8s.daemonset.desired_scheduled_nodes, 0))),
         references
| join [
    smartscapeNodes CONTAINER
    | fields container.image.digest, container.image.id, references
    | fieldsAdd workload.id = coalesce(references[is_part_of.k8s_deployment],
                              coalesce(references[is_part_of.k8s_daemonset],
                                coalesce(references[is_part_of.k8s_cronjob],
                                  coalesce(references[is_part_of.k8s_statefulset],
                                    coalesce(references[is_part_of.k8s_job],
                                      references[is_part_of.k8s_replicaset])))))
    | filter isNotNull(workload.id)
  ], kind:leftOuter, on:{workload.id}, fields:{container.image.digest, container.image.id}
| lookup [
    fetch security.events, from:now()-24h
    | filter in(event.type, {"VULNERABILITY_FINDING","DETECTION_FINDING","COMPLIANCE_FINDING"})
    | filter isNotNull(container_image.digest) or isNotNull(container_image.id)
    | dedup container_image.digest, container_image.id, event.provider, product.name
    | fields container_image.digest, container_image.id, event.provider, product.name
  ], sourceField:container.image.digest, lookupField:container_image.digest, prefix:"finding.digest."
| lookup [
    fetch security.events, from:now()-24h
    | filter in(event.type, {"VULNERABILITY_FINDING","DETECTION_FINDING","COMPLIANCE_FINDING"})
    | filter isNotNull(container_image.id)
    | dedup container_image.id, event.provider, product.name
    | fields container_image.id, event.provider, product.name
  ], sourceField:container.image.id, lookupField:container_image.id, prefix:"finding.id."
| fieldsAdd hasFinding = isNotNull(finding.digest.event.provider) or isNotNull(finding.id.event.provider)
| summarize {
    containerImages = countDistinctExact(coalesce(container.image.digest, container.image.id)),
    matchedImages = countDistinctExact(if(hasFinding, coalesce(container.image.digest, container.image.id))),
    replicaCount = takeMax(replicaCount)
  }, by:{workload.id, workload.name}
| filter matchedImages == 0 and containerImages > 0
| sort replicaCount desc, containerImages desc
```

### Cloud Entity Coverage (count by provider/product)

Only uses `dt.smartscape_source.id` — direct match is sufficient for cloud entities.

```dql
smartscapeNodes "*"
| filter exists(cloud.provider)
| join [
  fetch security.events
  | filterOut event.provider=="Dynatrace" or product.vendor=="Dynatrace"
  | filterOut isNull(event.type) or isNull(object.id)
  | filter exists(dt.smartscape_source.id)
  | dedup dt.smartscape_source.id, event.provider, product.name
  | fields dt.smartscape_source.id, event.provider, product.name
], kind:leftOuter,
   on:{right[dt.smartscape_source.id]==left[id]},
   fields:{dt.smartscape_source.id, event.provider, product.name}
| fieldsAdd Product=if(isNotNull(dt.smartscape_source.id), product.name, else:"Not covered")
| fieldsAdd Provider=if(isNotNull(dt.smartscape_source.id), event.provider, else:"Not covered")
| summarize {Entities=countDistinctExact(id)}, by:{Provider, Product}
| sort Entities desc
```

### Host Coverage by IP Match (count by provider/product)

Matches via IP address. The inner join also counts findings/scans per IP to
enable filtering if needed.

```dql
smartscapeNodes HOST
| fields id, name, ip
| expand host.ip=ip
| join [
  fetch security.events
  | filterOut event.provider=="Dynatrace" or product.vendor=="Dynatrace"
  | filterOut isNull(event.type) or isNull(object.id)
  | filterOut isNull(host.ip)
  | expand host.ip
  | fieldsAdd host.ip=ip(host.ip)
  | summarize {
      Findings=countIf(in(event.type,{"VULNERABILITY_FINDING","DETECTION_FINDING","COMPLIANCE_FINDING"})),
      Scans=countIf(in(event.type,{"VULNERABILITY_SCAN","COMPLIANCE_SCAN"}))
    }, by:{host.ip, event.provider, product.name}
], kind:leftOuter, on:{host.ip}, fields:{event.provider, product.name}
| fieldsAdd Product=if(isNotNull(event.provider) or isNotNull(product.name), product.name, else:"Not covered")
| fieldsAdd Provider=if(isNotNull(event.provider) or isNotNull(product.name), event.provider, else:"Not covered")
| summarize {Entities=countDistinctExact(id)}, by:{Provider, Product}
| sort Entities desc
```

---

## Best Practices

1. **Use `VULNERABILITY_SCAN` not `VULNERABILITY_COVERAGE_REPORT_EVENT`** — the
   latter is deprecated.
2. **Distinguish Code-level vs Third-party VA via `product.feature`** — these
   are separate scanning modes within RVA; coverage means different things.
3. **For runtime coverage of external products**, start from `smartscapeNodes`
   not `security.events` — the question is "which entities exist," and the answer
   joins back to findings.
4. **Use the 3-way match for container-based entities** — direct Smartscape ID,
   container image digest, and container image ID. Different external scanners
   populate different paths.
5. **For cloud entities**, direct `dt.smartscape_source.id` match is sufficient
   — they don't go through the container abstraction.
6. **For hosts**, prefer IP-based matching when the external scanner doesn't
   carry Dynatrace entity IDs (most don't).
7. **No `dt.system.bucket` filter** — security event data may live in any bucket;
   bucket scoping risks hiding data.
