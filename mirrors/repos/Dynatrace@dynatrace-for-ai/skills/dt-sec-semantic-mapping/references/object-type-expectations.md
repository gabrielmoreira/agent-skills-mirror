# Object Type Expectations

Validate `object.type` and expected companion fields and namespaces.

Baseline: local samples in `../samples/`, field taxonomy in `../references/data-model-notes.md`.

## Vendor-Reported `object.type` Values Are Accepted

`object.type` is a **vendor-extensible** field. Whatever the vendor reports as the resource type (for example `AWS::EC2::Instance`, `AWS::IAM::Role`, `AWS::ECS::Cluster`, vendor-specific resource taxonomies) is acceptable as-is. **Do not flag these as discrepancies.**

Smartscape-style canonical enum values (`AwsEc2Instance`, `AwsEksCluster`, `AwsS3Bucket`, etc.) are required **only when the integration opts into runtime contextualization** for an officially supported type — i.e., when downstream consumers (dashboards, segments, joins to `dt.smartscape.*` — or its deprecated `dt.entity.*` alias) need the canonical enum to function. For other types, leave the vendor value untouched.

Validation behavior:

| Situation | Verdict |
|---|---|
| Vendor-reported `object.type` value (e.g. `AWS::EC2::Instance`) on an integration that does not opt into Smartscape joins | ✅ accept — pass |
| Vendor-reported value where the integration explicitly intends Smartscape contextualization for an officially supported type | ⚠ recommend normalization to the canonical enum (e.g. `AwsEc2Instance`); preserve the original under a vendor-namespace field if needed |
| Officially supported type emitted with a malformed canonical value (typo, wrong case) | ⚠ minor — fix typo |
| `object.type` is null or empty | ❌ critical — required field missing |

## Smartscape Enrichment Fields Are Post-Ingest, Not Mapping Inputs

`dt.smartscape.*`, `dt.entity.*`, and `dt.source_entity` are **post-ingest runtime enrichment** fields populated by OpenPipeline after the integration has emitted the event. They are **NOT required in the initial mapping** (Workflow A) and **NOT validated as static-mapping requirements** (Workflow B1).

Where they belong:

| Workflow | Treatment |
|---|---|
| Workflow A — Suggest mapping | Do not include `dt.smartscape.*` / `dt.entity.*` / `dt.source_entity` in the suggested mapping. Integrations don't emit these — OpenPipeline writes them at ingest. |
| Workflow B1 — Static validation | Do not flag absence as a discrepancy. They are not part of the mapping contract. |
| Workflow B2 — Runtime validation | Check whether enrichment is present on ingested events. **Missing enrichment is not a blocker — it is informational.** On-ingest enrichment is the most efficient mechanism, so absence at runtime is worth noting but not failing. |

When runtime enrichment matters most:

- **K8s detection findings** — expect `dt.smartscape.k8s_cluster`, `dt.smartscape.k8s_pod`, `dt.smartscape.k8s_node`, etc. Missing → **warn** (most consumers expect K8s context).
- **Cloud detection findings** (AWS / Azure / GCP) — expect `dt.smartscape.aws_ec2_instance`, `dt.smartscape.aws_eks_cluster`, etc. Missing → **warn**.
- **Other finding types** — missing enrichment is **info** only.

`dt.entity.*` is the **deprecated** alias namespace; `dt.smartscape.*` is the canonical forward-going namespace (per `dt-dql-essentials/references/semantic-dictionary.md` § Legacy Mapping). At runtime:

| Observed | Verdict |
|---|---|
| Both `dt.smartscape.*` and `dt.entity.*` populated | ✅ pass |
| Only `dt.smartscape.*` populated (no `dt.entity.*`) | ✅ pass — completely OK; legacy namespace not required |
| Only `dt.entity.*` populated (no `dt.smartscape.*`) | 🟡 warn — recommend migrating to `dt.smartscape.*` |
| Neither populated on a K8s / cloud detection | 🟡 warn — see rule above |
| Neither populated on other finding types | ℹ info |

For the runtime DQL pack that exercises this check, see `runtime-validation.md § 14) Entity Enrichment Coverage`.

## TOC

- [CODE_ARTIFACT](#code_artifact)
- [CONTAINER_IMAGE](#container_image)
- [HOST](#host)
- [PROCESS / PROCESS_GROUP](#process--process_group)
- [CONTAINER / K8S_POD](#container--k8s_pod)
- [Cloud Types](#cloud-types)
- [URL](#url)
- [Output Format](#output-format)

---

## CODE_ARTIFACT

Seen in: `samples/external-vulnerabilities-code-artifact.json` (Snyk, SonarQube, Sonatype, GitLab, GitHub Advanced Security).

| Field | Required | Notes |
|---|---|---|
| `artifact.name` | yes | File or project name |
| `artifact.id` | yes (if object.id is not enough) | Stable artifact identity |
| `artifact.path` | yes | Relative path in repository |
| `artifact.repository` | yes | Repository identifier |
| `artifact.filename` | recommended | Just the filename without path |
| `artifact.version` | optional | Artifact version if versioned |
| `code.filepath` + `code.line.number` | required when `finding.type` is CODE_ISSUE/CODE_VULNERABILITY/EXPOSED_SECRET | Source location of the finding |

**Note:** `object.id` for CODE_ARTIFACT is often the project UUID (Snyk) or a composite path string. It must be stable across scans for deduplication.

---

## CONTAINER_IMAGE

Seen in: `samples/external-vulnerabilities-container-image.json`.

| Field | Required | Notes |
|---|---|---|
| `container_image.digest` | **yes — primary identifier** | SHA256 image digest (e.g. `sha256:01fa9ee3...`). The only immutable identifier for a container image; required for deduplication across scans and for `dt.smartscape.*` enrichment at runtime. Flag as **major** if absent. Check `event.original_content` impact paths and applicability details — vendors routinely expose digests there even when not surfaced in the top-level payload. |
| `container_image.name` | yes | Image name without tag (e.g. `online-boutique/checkoutservice`); extract from `object.name` before the colon |
| `container_image.tags` | yes | **Array** of image tags (e.g. `["1.0.0"]`); SD field is plural and array-typed. Extract from `object.name` after the colon and wrap in an array, or map directly from the vendor array if available. |
| `container_image.registry` | recommended | Registry hostname (e.g. `dtta.jfrog.io`); often derivable from `jfrog.tenant`, `object.id`, or vendor API metadata |
| `container_image.id` | optional | Vendor-internal image ID if different from digest; do not use as a substitute for `container_image.digest` |

**Note:** Container image findings often lack Smartscape entity IDs at runtime — `dt.smartscape.*` enrichment is post-ingest (see top-of-file rule) and depends on whether the image digest can be matched. Don't include `dt.smartscape.*` in the integration's emitted mapping; check coverage at runtime instead.

**Validation priority for CONTAINER_IMAGE namespace:** check `container_image.digest` first. Absence of `container_image.name`/`container_image.tags` is always flaggable, but a missing digest is the more critical gap because it blocks entity matching and scan deduplication.

---

## HOST

`HOST` is the Smartscape canonical type for generic-host findings — typically traditional vulnerability scans (Qualys, Tenable) targeting a host whose identity is its hostname/IP/FQDN.

This section documents what fields to expect **when `object.type = HOST` is the value the vendor emits or the integration chooses to use**. It is NOT a prescription that all host-shaped findings must be mapped to `HOST`. Per the vendor-reported-values rule at the top of this file, integrations preserve the value the vendor reports (e.g., `AWS::EC2::Instance`, vendor-specific resource taxonomies). Only normalize to a Smartscape canonical value when the integration explicitly opts into runtime contextualization for that officially supported type.

Seen in: `samples/external-vulnerabilities-host.json` (Qualys, Tenable on-prem hosts).

| Field | Required | Notes |
|---|---|---|
| `host.name` OR `host.ip` | at least one required | Primary host identity |
| `host.fqdn` | recommended | Fully qualified domain name |
| `host.ip` | recommended | `ipAddress[]` — list of IPv4 or IPv6 addresses |
| `os.name` | recommended | OS for vulnerability triage context |

---

## PROCESS / PROCESS_GROUP

Seen in: `samples/dynatrace-detections-rap.json`.

For mapping (Workflow A / B1):

| Field | Required | Notes |
|---|---|---|
| `host.name` | recommended | Host context |
| Vendor process identity (`process.executable.name`, `process.pid`, etc.) | recommended where vendor exposes them | OS-level process identity |

`dt.entity.process_group`, `dt.entity.process_group_instance`, `dt.entity.host`, `dt.source_entity`, `dt.smartscape.process` are **post-ingest runtime enrichment** — see top-of-file rule. Do not include them in the mapping. Validate their presence in Workflow B2 if the integration is expected to be Smartscape-correlated.

---

## CONTAINER / K8S_POD

Seen in: `samples/dynatrace-detections-automated.json` (K8s CONTAINER type).

| Field | Required | Notes |
|---|---|---|
| `k8s.cluster.name` | yes | Cluster name or ID |
| `k8s.namespace.name` | yes | Namespace |
| `k8s.pod.name` OR `k8s.pod.uid` | yes | Pod identity |
| `k8s.cluster.uid` | recommended | Stable cluster identifier |

---

## Cloud Types

### AwsEc2Instance

`AwsEc2Instance` is one of several Smartscape canonical types for AWS resources. It is **not** the universal target for every AWS-shaped finding — AWS reports many resource taxonomies (`AWS::IAM::Role`, `AWS::ECS::Cluster`, `AWS::S3::Bucket`, `AWS::Lambda::Function`, `AWS::EKS::Cluster`, `AWS::RDS::DBInstance`, etc.), and the default rule is to preserve whatever value the vendor reports.

Use `AwsEc2Instance` only when the integration explicitly opts into Smartscape runtime contextualization for EC2 instances (joins to `dt.entity.*` / `dt.smartscape.aws_ec2_instance`). For all other AWS resource types — and for EC2 findings where Smartscape correlation isn't a goal — keep the vendor-reported `object.type` value (per the vendor-reported-values rule at the top of this file).

Seen in: `samples/external-detections.json` (GuardDuty via Security Hub).

| Field | Required | Notes |
|---|---|---|
| `aws.resource.id` | yes | Instance ID or ARN |
| `aws.region` | yes | AWS region |
| `aws.account.id` | recommended | AWS account |
| `aws.arn` | recommended | Full ARN |

`dt.smartscape.aws_ec2_instance` / `dt.smartscape_source.id` are **post-ingest runtime enrichment** — see top-of-file rule. Don't include in the mapping; check at runtime.

### AwsEksCluster

Seen in: `samples/external-detections.json` (GuardDuty via Security Hub).

| Field | Required | Notes |
|---|---|---|
| `aws.resource.id` | yes | Cluster ID or ARN |
| `aws.region` | yes | AWS region |
| `aws.account.id` | recommended | AWS account |

`dt.smartscape.aws_eks_cluster` is **post-ingest runtime enrichment** — see top-of-file rule. Don't include in the mapping; check at runtime.

---

## URL

Seen in: `samples/external-detections.json` (Akamai SIEM).

| Field | Required | Notes |
|---|---|---|
| `url.domain` | yes | Domain/host |
| `url.path` | yes | Request path |
| `url.port` | recommended | Port |
| `url.scheme` | recommended | Protocol |
| HTTP context fields | optional | Enrichment for WAF detections |

**Note:** `object.id` for URL findings typically uses `domain:port/path` composite format.

---

## Output Format

Report `object.type` checks using this table:

| object.type | Sample count | Required namespace present | Missing fields | Status |
|---|---|---|---|---|
| `CODE_ARTIFACT` | 7 | artifact.* yes | none | pass |
| `CONTAINER_IMAGE` | 3 | container_image.* yes | none | pass |
| `HOST` | 5 | host.* yes | none | pass |
| `AwsEksCluster` | 2 | aws.* partial | `aws.region` | major |
