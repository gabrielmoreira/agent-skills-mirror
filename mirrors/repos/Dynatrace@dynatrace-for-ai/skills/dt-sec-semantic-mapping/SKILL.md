---
name: dt-sec-semantic-mapping
description: "Suggest and validate semantic dictionary (SD) mappings for new security integrations using vendor API samples or live events. Use when: mapping a new security vendor data to Dynatrace SD; checking required fields; validating namespaces; highlighting discrepancies vs the semantic dictionary; proposing mapping improvements; running runtime validation against live tenant data."
license: Apache-2.0
---

# dt-sec-semantic-mapping

Build and validate semantic-dictionary-aligned mappings for new security integrations.

## Purpose

Use this skill when a user wants to:

- **Suggest** a mapping from vendor API output to Dynatrace `security.events` fields (Workflow A).
- **Validate** an existing mapping for completeness and quality against:
  - Local baseline samples and semantic dictionary (Workflow B1 — static, offline validation), or
  - Live tenant data via live tenant access (Workflow B2 — runtime validation)
- Highlight discrepancies vs. the Semantic Dictionary and local references.
- Get actionable mapping improvements.

## Semantic Dictionary

The Semantic Dictionary (SD) defines the canonical field set for `security.events`. See `references/semantic-dictionary.md` for the canonical reference: local-vs-live sources, queryable Grail tables, when-to-query decision matrix, and the authority rule (live SD wins on disagreement).

## Required Inputs

Always run the intake checklist in `references/intake-and-output.md` before generating or validating a mapping. If inputs are incomplete, continue with a partial draft but explicitly list missing evidence and confidence limits.

## Baseline Sources (self-contained)

All baseline material lives inside this skill:

- `samples/` — real integration payloads covering all finding types and providers. Consulted as a fallback when primary references (SD, data-model-notes, known-discrepancies, validation-rules, object-type-expectations) leave a specific question unresolved — not as a routine step on every workflow run.
- `references/data-model-notes.md` — field taxonomy, event types, provider taxonomy, entity scoping
- `references/known-discrepancies.md` — documented acceptable deviations between SD and observed samples
- `references/object-type-expectations.md` — `object.type` namespace expectations
- `references/semantic-dictionary.md` — SD reference and live-verification patterns

## Event-Type Coverage Requirements

The mapping MUST address the correct set of `event.type` values per finding class. Detection integrations are push-based and do not use scan cycles — never require scan events for detection.

See [validation-rules.md](references/validation-rules.md) § Event-Type Coverage for the full table, severity rules, and the alternative-classification path when a detection-class mapping incorrectly emits `*_SCAN` events.

## Workflows

This skill operates in three modes. Detect the mode from context:

| Mode | Input | Procedural source |
|---|---|---|
| **Workflow A** — Suggest a new mapping | Raw vendor API payloads only | `references/mapping-workflow.md § Workflow A` (Phase 1 mapping table → user approval → Phase 2 sample JSON) |
| **Workflow B1** — Static validation | Existing mapping + vendor API samples | `references/mapping-workflow.md § Workflow B` — classify input mode (final ingested / theoretical), apply rules, produce diff-highlighted table |
| **Workflow B2** — Runtime validation | Existing mapping + live tenant access | `references/runtime-validation.md` — load the security (AppSec) events supporting skill first (REQUIRED Step 0), then run the query pack, produce a Validation Summary table |

All workflows follow the output contracts in `references/intake-and-output.md` and the report templates in `references/report-format.md`. Validation rules (event-type coverage, required fields, scan references, namespace requirements, value/type checks, vendor-namespace duplication) live in `references/validation-rules.md`.

## Acceptable Discrepancy Policy

See `references/known-discrepancies.md` for the canonical list of acceptable SD deviations and vendor-namespace patterns. Do NOT raise critical/major issues for fields on that list. Genuinely unknown fields (not in local refs AND not in the live SD — see `references/semantic-dictionary.md`) must be questioned per `references/validation-rules.md § Known SD Discrepancies and Unknown Fields`.

## Scope

This skill covers:

- Mapping suggestion and refinement (Workflow A).
- Static validation against local baseline examples and semantic dictionary (Workflow B1).
- Runtime validation via live tenant access against live tenant data (Workflow B2).
- Semantic-dictionary conformance checks.
- Gap analysis and improvement recommendations.

This skill does not cover:

- Live ingestion pipeline deployment.
- Runtime DQL performance benchmarking.
- Tenant-side ingestion troubleshooting.

## References

- `references/semantic-dictionary.md` — SD reference: local sources, live (queryable) sources, DQL patterns, when-to-query decision matrix, authority rule
- A skill covering full SD access patterns and Grail-table documentation — for DQL query patterns against `security.events` and Grail tables
- [Semantic Dictionary (public docs)](https://docs.dynatrace.com/docs/semantic-dictionary/model/security-events)
- `references/data-model-notes.md` — field dictionary and event-type taxonomy
- `references/known-discrepancies.md` — acceptable SD deviations
- `references/object-type-expectations.md` — `object.type` namespace expectations
- `references/intake-and-output.md` — intake checklist and output contract
- `references/mapping-workflow.md` — how to build and refine a mapping candidate
- `references/openpipeline-constraints.md` — OpenPipeline processor chain architecture (generic → per-subcategory → cleanup), restricted DQL subset, `jsonPath()` unavailable, `ip()` cast for IP fields
- `references/validation-rules.md` — full validation rule set
- [references/report-format.md](references/report-format.md) — discrepancy report templates
- `references/runtime-validation.md` — optional real-environment query validation pack
