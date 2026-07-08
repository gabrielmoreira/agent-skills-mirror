# Semantic Dictionary — Reference & Live Verification

The Semantic Dictionary (SD) defines the canonical field set for `security.events`. This skill validates against it.

## TOC

- [Local References (Offline Summary)](#local-references-offline-summary)
- [Live (Authoritative) Sources](#live-authoritative-sources)
- [DQL Patterns for Live SD Lookup](#dql-patterns-for-live-sd-lookup)
- [When to Query the Live SD](#when-to-query-the-live-sd)
- [Authority Rule](#authority-rule)

---

## Local References (Offline Summary)

The following references in this skill are an offline summary of the SD scoped to security-events use cases:

- `data-model-notes.md` — field taxonomy, event types, provider taxonomy, entity scoping
- `known-discrepancies.md` — documented acceptable deviations between SD and observed samples
- `object-type-expectations.md` — `object.type` namespace expectations

These can drift relative to the live SD between PRs. When in doubt, verify against the live SD (below).

## Live (Authoritative) Sources

- **Patterns + queryable tables** — load the `dt-dql-essentials` skill from `knowledge-base/dynatrace/skills/dt-dql-essentials/` and read its `references/semantic-dictionary.md` for the full documentation of the queryable tables, stability levels, and global namespaces.
- **Human-facing docs** — https://docs.dynatrace.com/docs/semantic-dictionary/model/security-events.

The SD is queryable in Grail as two tables:

| Table | What it gives you |
|---|---|
| `dt.semantic_dictionary.fields` | Per-field: `name`, `type`, `stability` (`stable` / `experimental` / `deprecated`), `description`, `tags`, `unit`, `supported_values`, `examples` |
| `dt.semantic_dictionary.models` | Per data model: `name`, `description`, `data_object`, `fields[]`, `relationships[]`, `smartscape_node_name` |

These queries are read-only — always safe.

## DQL Patterns for Live SD Lookup

Run via a live DQL execution tool.

```dql-template
// Verify a single field exists; get its type / stability / supported_values / examples
fetch dt.semantic_dictionary.fields
| filter name == "<field.name>"
```

```dql-template
// List every field in a namespace (e.g. all `event.*`, `finding.*`, `vulnerability.*`, `compliance.*`, `aws.*`, `k8s.*`)
fetch dt.semantic_dictionary.fields
| filter startsWith(name, "<namespace_prefix>.")
| dedup name
| sort name asc
```

```dql
// Inspect the security-events data model (which fields belong, relationships)
fetch dt.semantic_dictionary.models
| filter name == "security_event" or contains(name, "security")
```

```dql-template
// Cross-reference: which models include a given field
fetch dt.semantic_dictionary.models
| filter in("<field.name>", fields)
```

## When to Query the Live SD

Applies to **both Workflow A** (suggesting target fields) **and Workflow B** (validating against rules).

| Scenario | What to check | Why |
|---|---|---|
| Proposing a target field that isn't in our local references | `fetch dt.semantic_dictionary.fields | filter name == "<candidate>"` | Confirm it exists, check `stability`, get correct type and `supported_values` |
| Validating an enum-typed field's value (e.g., `event.kind`, `event.type`, `dt.security.risk.level`) | check `supported_values` column | Confirm the value is in the canonical enum |
| Vendor reports an unknown field that "feels SD-shaped" | namespace lookup + filter by `tags` | Detect SD additions since the local reference was updated |
| `finding.type` / `object.type` value not documented in our local references | namespace lookup | These are vendor-extensible; live SD shows officially documented values |
| Suspicious type/format mismatch (string vs number, etc.) | check `type` column | Use as source of truth for `validation-rules.md § Value and Type Checks` |
| Cross-reference reuse of a field across data objects | `fetch dt.semantic_dictionary.models | filter in("<field.name>", fields)` | See where else (logs/spans/events) the field is used |

## Authority Rule

When local references and the live SD disagree, **the live SD wins.** Note any drift in the validation report and flag a follow-up PR to update the local references.

This rule applies to:

- Field existence (a field present in live SD but missing from local refs is **not** "unknown")
- Field type (live SD `type` is authoritative for type-check rules)
- Enum values (live SD `supported_values` is authoritative)
- Stability classification (a field listed as `deprecated` in live SD should not be proposed for new mappings even if local refs still show it)
