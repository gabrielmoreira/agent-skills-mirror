# Validation Rules

## TOC

- [Required Fields](#required-fields)
- [content Field Rules](#content-field-rules)
- [loglevel and status Rules](#loglevel-and-status-rules)
- [Audit Namespace Rules](#audit-namespace-rules)
- [Content Burial Rules](#content-burial-rules)
- [Type and Value Rules](#type-and-value-rules)
- [Discrepancy Severity Reference](#discrepancy-severity-reference)
- [Acceptance Criteria](#acceptance-criteria)

---

## Required Fields

| Field | Severity if absent | Notes |
|---|---|---|
| `timestamp` | critical | Auto-set on ingest — not required in pre-ingest draft validation |
| `log.source` | critical | Must be non-null |
| `content` | critical | Must be a string (not an object) on final ingested events |
| `loglevel` | critical | Must be a valid enum value |
| `audit.action` | major | Required when action is identifiable from the payload |
| `audit.identity` | major | Required when a user or service account is identifiable |

---

## content Field Rules

| Rule | Severity |
|---|---|
| `content` is not a string on a final ingested event | critical |
| `content` is a JSON object on a pre-ingest draft | major — remind to serialize before ingest |
| `content` is absent entirely | critical |
| `content` cannot be parsed as JSON when it appears to be JSON | minor — note in report, use raw string analysis |

---

## loglevel and status Rules

| Rule | Severity |
|---|---|
| `loglevel` absent | critical |
| `loglevel` value outside `ERROR/WARN/INFO/DEBUG/TRACE/NONE` | critical |
| `loglevel` set to un-normalized vendor value (e.g. `critical`, `fatal`) | major |
| `status` absent | minor |
| `status` value outside `INFO/WARN/ERROR/NONE` | major |
| `loglevel` and `status` semantically inconsistent | minor — flag and document intent |

---

## Audit Namespace Rules

| Rule | Severity |
|---|---|
| `audit.action` absent when action is derivable from payload (audit log classes only) | major |
| `audit.identity` absent when user/service is in payload (audit log classes only) | major |
| `audit.result` absent when outcome (success/failure) is in payload | major |
| `audit.result` value not using title-case convention (`Succeeded`/`Failed`) | minor |
| `audit.status` set to a `loglevel` value (e.g. `"INFO"`, `"ERROR"`) | major — mapping error; valid values are `Started`, `In Progress`, `Succeeded`, `Failed`, `Active`, `Resolved` |
| `audit.status` value outside SD enum (`Started/In Progress/Succeeded/Failed/Active/Resolved`) | major |
| `audit.time` missing timezone offset (e.g. `"2026-05-08T15:37:05"` without Z) | minor |

---

## Content Burial Rules

A field is "buried" when it exists in parsed `content` JSON but has no top-level semantic counterpart.

| Buried fields | Severity |
|---|---|
| 0 promotable buried fields | pass |
| 1–2 promotable buried fields | minor |
| 3+ promotable buried fields | major |
| Buried required field (`audit.identity`, `audit.action`) | major per field |

For each buried field: state the source path, the target SD field, the transform, and the OpenPipeline extraction rule.

---

## Type and Value Rules

| Rule | Severity |
|---|---|
| `actor.ips` is a plain string instead of `ipAddress[]` | major |
| `result.code` is a string (SD type is `long`) | major — coerce to long; non-numeric codes (e.g. `"SUCCESS"`, `"IDP2013"`) belong in `result.message` instead |
| `result.details` (plural) used instead of `result.detail` (singular) | minor — rename to `result.detail` |
| `http.response.status_code` is a string instead of integer | major — coerce to integer |
| `http.response.body.size` is a string instead of long | minor — coerce to long |
| `actor.geo.location.lat/lon` as string instead of float | minor — prefer float for correct geo-query behavior |
| `http.request.header.<Name>` or `http.response.header.<Name>` uses mixed/Pascal case header name | minor — rename to lowercase (e.g. `user-agent` not `User-Agent`) |
| Field value is a string sentinel (`"UNKNOWN"`, `"N/A"`, `"-"`, `"null"`) | minor — omit field; do not promote sentinel strings to top-level semantic attributes |
| `timestamp` mapped from vendor payload | major — `timestamp` is Dynatrace ingest time; vendor event time belongs in `audit.time` |
| `log.source` set to raw vendor identifier instead of integration name | minor — use human-readable integration name constant (e.g. `"JFrog"` not `"jfrog_artifactory"`) |
| `host.*` fields populated from connector/shipper metadata (not target host) | minor — move to vendor namespace (e.g. `<vendor>.instance.*`) |
| Vendor-namespace field populated while its SD-canonical counterpart is null | major — backfill the SD field |
| Vendor-namespace field is an exact duplicate of an SD-canonical field value | minor — remove vendor field |
| More than ~5 vendor-namespace fields extracted | minor — review and retain only highest-value fields not covered by SD |

---

## Discrepancy Severity Reference

| Severity | Criteria |
|---|---|
| `critical` | Missing required field; `content` not a string; invalid `loglevel` enum |
| `major` | Missing `audit.action`/`audit.identity`/`audit.result` when derivable; 3+ buried promotable fields; `audit.status` contains a `loglevel` value; type mismatch on required fields |
| `minor` | 1–2 buried promotable fields; missing `audit.time` timezone; `audit.result` not title-case; `loglevel`/`status` inconsistency; vendor-namespace duplication |
| `info` | Deviation already documented in `data-model-notes.md § Known Discrepancies` |

---

## Acceptance Criteria

A mapping passes when:

1. All required fields are present or auto-derivable.
2. No critical discrepancies unresolved.
3. All major discrepancies fixed or documented.
4. `loglevel` and `status` use valid SD enum values.
5. `audit.action` and `audit.identity` populated.
6. `content` is a string (or will be on ingest).
7. Content burial score is 0, or remaining buried fields are documented as intentional.
