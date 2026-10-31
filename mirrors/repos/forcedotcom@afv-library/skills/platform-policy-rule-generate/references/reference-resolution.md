# Reference Resolution

Resolve exact values in the target org before generating XML. User requests may identify a reference by developer name, fully qualified name, display label, or a natural-language description. Treat those forms as lookup inputs, not as deployable values. Required references include:

- Standard tag developer names
- Standard classification names
- Custom permission developer names
- DMO / DLO / calculated-insight-object (CIO) API names
- DMO / DLO / CIO field (and measure/dimension) API names
- Principal fields selected by `principalExpression`
- ID-valued principal comparisons, including profiles
- Schemas and fields used by resource projections

Use a read-only metadata or Data 360 lookup to map every requested label or description to one exact target-org reference. This applies equally to standard and custom tags, standard and custom classifications, custom permissions, DMO/DLOs, fields, resource domains, join fields, and principal fields. If the lookup returns multiple matches, stop and ask for clarification; do not choose heuristically. If no match exists, stop and report the unresolved reference. Never shorten a dotted tag/classification name, infer a developer name from a label, reuse an ID from an evidence package, or guess a DMO/DLO field. Preserve resolved spelling exactly in `<valueReference>`, `<valueDomain>`, `<select>`, and projection elements.

## Data 360 MCP lookup operations

When a Data 360 MCP session is available, use it for read-only reference lookup only — never for policy mutation. The MCP client exposes three facade tools: `search(query)` to discover the operation, `payload_examples(toolName)` to see that operation's expected input shape, and `execute(toolName, paramsJson)` to invoke it. Resolve the concrete tool name for each operation below through `search`/`payload_examples` before calling `execute`, since the exact binding (a single generic `execute` versus a per-operation tool name) varies by client.

| Reference type | Lookup operation | Notes |
|---|---|---|
| Standard tag | `d360_data_governance_tag_list` | Filter by `searchString`/`taxonomyName`/`parentTagFullyQualifiedName` (no `limit`/`offset` beyond the schema's own paging fields — see call notes below). The record's `id` is the D360 policy-JSON reference value, not the MDAPI one — see the `<valueReference>` construction rule below. |
| Standard classification | `d360_data_governance_classification_list` | Same pattern as tags, via `parentClassificationFullyQualifiedName`. |
| **Custom / mapped / derived DMO and fields** (most `resourceDomains` targets, `__dlm` suffix) | `d360_dmo_list` / `d360_dmo_get` | **PRIMARY resource path — family `DataModelObject`** (distinct from the standard-only `DataModelObjectCatalog` below). `d360_dmo_list` lists customer-created **and derived** DMOs (custom, SQL/transform, segment-membership, calculated-insight); pass `includeFields:"true"` to return each DMO's field definitions, and optionally filter with `dataSpaceName` / `dataObjectCategory` / `isEnabled` (`limit` defaults to 50). `d360_dmo_get` takes `dataModelObjectName` and returns one DMO **with all field definitions**. Note: `isEnabled=false` does NOT mean the DMO is unusable — it can still back a policy/mapping. Confirmed live: a custom `__dlm` DMO that is absent from the sObject-describe surface resolves cleanly here. This is the correct Data 360 MCP path for the `__dlm` targets that most `resourceDomains`/`valueDomain` entries reference. |
| Standard (out-of-box / canonical) DMO and fields | `d360_data_model_objects_list` / `d360_data_model_object_get` | Family `DataModelObjectCatalog` — Salesforce-provided **standard/canonical** models only, NOT org-specific custom/derived DMOs (use `d360_dmo_list`/`d360_dmo_get` above for those). Depends on the org having the Schema Interface Connect API enabled; if it errors (`Schema Interface API is not enabled for this organization`), that is an org capability gap, not a lookup-input mistake. |
| Raw ingested DLO and fields (`__dll`) | `d360_dlo_list` / `d360_dlo_get` | Family `DataLakeObject`. `d360_dlo_list` enumerates the raw ingested source objects; `d360_dlo_get` takes `recordIdOrDeveloperName` and returns one DLO with all field API names. Use when a rule targets the **pre-mapping** `__dll` object rather than the mapped `__dlm` DMO. |
| Calculated Insight Object (CIO) and its measures/dimensions | `d360_ci_list` / `d360_ci_get` | Family `CalculatedInsight`. `d360_ci_list` enumerates calculated insights (optional `definitionType` filter: CalculatedMetric / StreamingMetric / ExternalMetric / GraphMetric / HistoryMetric); `d360_ci_get` takes `apiName` and returns the full definition including dimensions, measures, and SQL. Use to resolve a CIO name and its measure/dimension field API names before authoring a rule that targets it. |
| Custom DMO/DLO fields when the Data 360 MCP session is unreachable (last-resort fallback only) | `dispatch_readonly` sObject describe | Use ONLY when no Data 360 MCP session is available — the tools above are the preferred path. GET `/services/data/vXX/sobjects/<name>/describe` and confirm the field name from the describe output before authoring `resourceDomain`/`valueDomain`. Caveat: some custom `__dlm` DMOs are **not present** in `/services/data/vXX/sobjects` at all (confirmed live), so this fallback can miss them entirely — resolve through `d360_dmo_get` above whenever the Data 360 MCP session is reachable. Never use the `sf` CLI. |
| Dataspace | `d360_dataspace_list` / `d360_dataspace_get` | Only needed when the request names a non-default dataspace. |
| Custom permission | `dispatch_readonly` SOQL | No Data 360 MCP lookup exists for `CustomPermission`. Resolve read-only via `dispatch_readonly` GET `/services/data/vXX/query?q=SELECT+DeveloperName+FROM+CustomPermission+WHERE+…`. Never use the `sf` CLI. |
| ID-valued principal comparisons (e.g. `ProfileId`) | `dispatch_readonly` SOQL | Resolve read-only via `dispatch_readonly` GET `/services/data/vXX/query` against the owning standard object (e.g. `Profile`); these are not exposed through a Data 360 MCP lookup tool. Never use the `sf` CLI. |

The D360 policy-JSON authoring path (a separate, MCP-mutating skill) persists a tag/classification lookup's `id` as its `reference` value. This skill's MDAPI XML persists the resolved **developer/API name**, not the `id` — take the `id` only when the target field is itself ID-typed (`ProfileId` and similar), and otherwise construct the MDAPI `<valueReference>` from the lookup record as follows.

### Constructing `<valueReference>` for STANDARD_TAG / STANDARD_CLASSIFICATION

The lookup record's `fullyQualifiedName` is a Connect API path (`<taxonomy>.<tag/classification path>`) and is **not** a direct copy for the MDAPI value — it is missing the MDAPI root namespace, and (for a tag/classification with no parent) missing a category segment that MDAPI still requires. Build the value as:

1. Root literal: `DataGovernanceTags` for a tag, `DataGovernanceClassifications` for a classification. `<valueReferenceType>` is `STANDARD_TAG` or `STANDARD_CLASSIFICATION` respectively.
2. If the record has a `parentTag` (tags) or `parentClassification` (classifications) — i.e. it is nested under a category — its `fullyQualifiedName` is already `<taxonomy>.<category>.<leaf>`; the value is `<Root>.<fullyQualifiedName>`.
3. If the record has **no** parent (it sits directly under its taxonomy, `fullyQualifiedName` is only `<taxonomy>.<leaf>`) — MDAPI still requires a 3-segment path after the root, so **repeat the leaf `name` as the missing category segment**: `<Root>.<fullyQualifiedName>.<name>`.

Both shapes are confirmed against live org lookups and persisted evidence: a top-level tag (`FinancialData.AccountInfo`, no `parentTag`) persists as `DataGovernanceTags.FinancialData.AccountInfo.AccountInfo`; a top-level classification (`DataCategorization.DataSensitivity`, no `parentClassification`) persists as `DataGovernanceClassifications.DataCategorization.DataSensitivity.DataSensitivity`; a nested tag (`EthicalAiStandards.EthicalAI.Caste`, has `parentTag`) persists as-is with only the root prepended: `DataGovernanceTags.EthicalAiStandards.EthicalAI.Caste`.

`search` only accepts a `query` argument — do not pass a `limit` field to it (the live server rejects unrecognized fields); pass `limit`/`offset` to the resolved lookup tool itself (e.g. `d360_data_governance_tag_list`) if needed for paging.

Every reference above resolves through MCP only — Data 360 MCP for tags / classifications / dataspaces AND every resource-side object schema: custom/derived DMOs (`d360_dmo_list`/`d360_dmo_get`), standard DMOs (`d360_data_model_objects_list`/`d360_data_model_object_get`), DLOs (`d360_dlo_list`/`d360_dlo_get`), and calculated insight objects (`d360_ci_list`/`d360_ci_get`). Read-only headless-360 `dispatch_readonly` is used only for the references Data 360 MCP has no lookup for — custom permissions and ID-valued comparisons (SOQL `/query`) — and, strictly as a last resort when no Data 360 MCP session is reachable, a custom-DMO sObject describe (which can miss `__dlm` objects). There is no `sf` CLI resolution path. If neither MCP session can resolve a reference, stop and report the unresolved reference to the operator rather than routing around it.

Serialize XML structurally. XML-escape text values and validate developer names, API names, fields, operators, aliases, and reference types against their expected grammar or enum before interpolation.

The semantic evidence packages demonstrate exact resolved source-org values. In normal author mode, resolve every value again in the target org. In explicit evidence-recreation mode, exact fidelity to the named API 69.0 evidence package takes precedence: preserve its evidence values rather than substituting current target-org values, and do not deploy that fixture as though it were newly resolved authored output.
