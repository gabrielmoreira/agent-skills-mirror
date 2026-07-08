# OpenPipeline Transform Constraints

Mappings suggested by this skill are implemented as **OpenPipeline processors** at ingest. OpenPipeline runs a **restricted subset of DQL** — fewer commands and fewer functions than the DQL you use to *query* `security.events` in Grail. A transform that is valid in a Grail query is **not** guaranteed to be valid in an OpenPipeline processor.

Apply these constraints whenever you propose a value in the **Transform** column of a mapping table (Workflow A suggestion, Workflow B diff). A suggested transform that cannot be expressed with OpenPipeline-available DQL is not actionable.

**Authority:** the live Dynatrace documentation is the source of truth for the exact OpenPipeline command and function set. Do **not** assume a full-DQL function is available in OpenPipeline — verify against the reference below before relying on it.

- Commands: https://docs.dynatrace.com/docs/platform/openpipeline/reference/dql/openpipeline-dql-commands
- Functions: https://docs.dynatrace.com/docs/platform/openpipeline/reference/dql/openpipeline-dql-functions

---

## Supported processing commands

OpenPipeline DQL processors support this command set:

| Command | Use |
|---|---|
| `parse` | Parse a field with a DPL pattern into one or more fields |
| `fields` / `fieldsKeep` | Keep only the specified fields |
| `fieldsAdd` | Evaluate an expression and append or replace a field |
| `fieldsRename` | Rename a field |
| `fieldsRemove` | Remove fields |
| `fieldsFlatten` | Extract/flatten fields from a nested record |

Commands outside this set (e.g. `fetch`, `filter`/`summarize` as query stages, `join`, `lookup`, `makeTimeseries`) are query/aggregation constructs and are not part of the processor transform model — do not propose them as ingest transforms.

---

## `jsonPath()` is not available — extract nested JSON another way

`jsonPath()` is **not enabled** in OpenPipeline processors. Do not suggest a transform that calls `jsonPath()` to pull a value out of a nested JSON payload.

OpenPipeline-valid alternatives for getting at nested JSON values:

- **`parse` with a JSON DPL matcher** to turn a JSON-string field into a structured record, then
- **`fieldsFlatten`** to lift nested keys into top-level fields, and/or **field-access (subscript) expressions** to reference a nested key directly in `fieldsAdd`.

Describe the mechanism in the Transform column (e.g. "`parse` JSON → `fieldsFlatten`"); confirm the exact DPL pattern and subscript syntax against the commands reference above rather than improvising it.

---

## Producing `ipAddress`-typed values

IP fields must carry the SD `ipAddress` / `ipAddress[]` type (see `validation-rules.md § Value and Type Checks` rule 16 and the `host.ip` / `actor.ips` / `client.ip` rows in `known-discrepancies.md`). OpenPipeline's network function **`ip()`** parses and casts a string into the `ip` type (invalid input yields `null`, not an error) — this is the OpenPipeline-valid way to emit an IP-typed value. For array fields (`host.ip`, `actor.ips`), apply the cast per element so the result is `ipAddress[]`.

Do not leave an IP value as a plain string when the SD target is `ipAddress` — a plain string assignment fails the rule-16 type check.

---

## Processor chain architecture

An integration is **not** a single monolithic processor. Design it as an ordered chain of processors, each with a **matching criterion** that gates when it runs:

```
Processor 1 — Generic (matches: all events from this provider)
  → maps common SD fields shared across all event types
  → parses shared nested JSON once so downstream processors receive structured fields

Processor 2 — Per-subcategory (matches: e.g. object.type == "HOST")
  → adds object-type-specific namespace fields (host.*, aws.*, k8s.*, etc.)
  → can reference fields already parsed by Processor 1 directly, no re-parsing needed

Processor 3 — Per-subcategory (matches: e.g. event.type == "VULNERABILITY_FINDING")
  → adds finding-type-specific fields (software_component.*, vulnerability.*, etc.)

... (one processor per distinct sub-category that needs separate field logic)

Processor N — Cleanup (matches: all events from this provider)
  → removes intermediate fields that were created for processing but are not SD fields
     (e.g. temporary parse results, raw vendor-namespace fields the integration no longer needs)
```

**Key properties of this model:**

- **Sequential execution:** processors run in order; fields written by processor 1 are fully available (in already-parsed / structured form) to processor 2, 3, etc. Do not re-parse the same field in every processor.
- **Matching criteria gate execution:** each processor fires only for events that match its condition. Use this to scope object-type-specific or finding-type-specific logic rather than putting conditional `fieldsAdd` expressions inside a single processor.
- **Cleanup is a dedicated last processor:** non-SD intermediate fields — raw vendor keys used only as parse inputs, helper fields created mid-chain — must be removed in a terminal cleanup processor using `fieldsRemove`. Do not leave them in the ingested event.

**When suggesting a processor chain (Workflow A):**

Present the processors as an ordered list, not a flat mapping table. For each processor:
1. Name: descriptive label (e.g. `generic`, `host-namespace`, `vulnerability-namespace`, `cleanup`)
2. Matching criterion
3. Commands/fields it adds or transforms
4. Note which fields it inherits from an earlier processor in the chain (no re-parsing needed)

---

## How to apply

- **Workflow A (suggest):** propose a processor chain (generic → per-subcategory → cleanup), not a single processor. Only use transforms expressible with the commands/functions listed above. If a vendor value lives inside a nested JSON blob, parse it in the generic processor via `parse` → `fieldsFlatten`/subscript access — not `jsonPath()` — so subcategory processors receive structured fields.
- **Workflow B (validate):** flag any provided transform that relies on an OpenPipeline-unavailable construct — most commonly `jsonPath()` — as a discrepancy and suggest the OpenPipeline-valid alternative. Also flag a single-processor design when the integration has multiple `object.type` or `event.type` categories — recommend splitting per the chain architecture above. See `validation-rules.md § Value and Type Checks`.
