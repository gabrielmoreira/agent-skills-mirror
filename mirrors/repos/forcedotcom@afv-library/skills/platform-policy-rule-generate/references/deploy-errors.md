# Deploy Error Reference

Create/update run over headless-360 `dispatch`/`/headless/metadata`; delete runs over the Data 360 MCP `d360_data_governance_access_policy_delete` tool (Core has no real metadata delete). There is no CLI fallback on either path. This file documents the server-side error taxonomy; the create/update/read errors below surface directly on the `dispatch` path.

---

## Headless Dispatch Errors

| Error fragment | Likely cause | Fix |
|---|---|---|
| `400 FIELD_INTEGRITY_EXCEPTION "Not available for deploy for this organization"` | Type/op is on the MD-CRUD allowlist, but the org lacks the feature/perm provisioning to deploy this metadata type | Org setup gap — surface it to the operator; do not fall back to CLI on this error alone, since the CLI path hits the same org gate. |
| `400 UNSUPPORTED_OPERATION` | The type/op is genuinely not on the MD-CRUD allowlist | Onboarding gap — surface it to the operator; there is no CLI fallback. |
| `'body' must be a JSON object, got an unexpected type` | A client/transport let a raw unescaped newline reach the JSON body, or a transient tool-arg serialization glitch (NOT the server rejecting multi-line XML — a properly-escaped multi-line `xmlRep` persists fine) | Flatten `xmlRep` to one line as a defensive default; if it still fails, retry once before concluding the shape is unsupported. |
| `404` (on GET) | Type/op is allowlisted; the named member does not exist | Expected for a not-yet-created component, not an error. |
| `405` / no-op `200` (on a `/headless/metadata` DELETE) | Core has no real metadata delete — the verb 405s, and the interim delete is a no-op 200 that removes nothing | Do not delete via `/headless/metadata`. Delete the whole policy over the Data 360 MCP `d360_data_governance_access_policy_delete` tool (removes the Access Policy and its embedded rules by developer name). |
| DC-connectivity error (on the Data 360 Access Policy delete) | The off-core Data Cloud delete path failed on DC connectivity | Provisioning gap — surface it to the operator; there is no `sf` CLI fallback. Confirm removal via `d360_data_governance_access_policy_get` by name (not-found = success). |

See `references/headless-transport.md` for the full request/response contract.

---

## Server-Side Validation Errors

These deploy-time validation errors are raised by the same metadata deploy engine behind `/headless/metadata`, so they surface directly in the `dispatch` response for `PolicyRuleDefinition` / `PolicyRuleDefinitionSet`. They are shape or org-provisioning problems, not transport problems — fix the authored XML or surface the org gap to the operator; there is no CLI to fall back to.

| Error fragment | Likely cause | Fix |
|---|---|---|
| `Not available for deploy for this organization` | Policy-rule metadata deployment is not enabled for the org | Surface the missing org capability to the operator; do not attempt to bypass the server gate. |
| `Cannot find … PolicyRuleDefinition` (older orgs) | Policy-rule metadata is unavailable, or the API version is too low | Confirm the org supports policy-rule metadata and ensure the resolved org API version meets the skill's `minApiVersion`. |
| `INVALIDFORCATEGORY` / `Resource scope … not valid for category …` | Scope × category mismatch (e.g., GOVERNANCE + RECORD scope, or TRANSFORM + ANY scope) | Match a persistence-validated combination in `policy-shapes.md`; do not infer a new category/scope pairing. |
| `Identified record category should use record field …` | Attempted to author an `IDENTIFIED_RECORD` policy with a non-`RECORDFIELD` resource path | Do not author `IDENTIFIED_RECORD` via MDAPI — use a runtime `RuleProvider` instead. |
| `Invalid resource domain - <name>` | `<resourceDomain>` references an entity that doesn't exist in the target org | Pre-deploy the DMO/entity, or remove the rule until the target is available. Namespaced DMOs (e.g. `ssot__Account__dlm`) need the namespace prefix in the XML. |
| Unexpected server error on RLS deploy | RLS rule may reference a `<valueDomain>` DMO field that exists in metadata but is not mapped in the target org's data streams | Verify each `<valueDomain>` field is mapped using a read-only Data 360 MCP / `dispatch_readonly` inspection, then re-issue the create. |
| `Metadata API received improper input. … Load of metadata from db failed for metadata of type:PolicyRuleDefinition and file name:<name>` (on **GET read-back**) | UI-saved RLS rules can fail to round-trip back through the MD-CRUD read in some org states | No clean fix. Use the UI as source of truth for that rule, or hand-author from a known-deployable RLS template. |
| `Use the principal … with external record category.` | `EXTERNAL_RECORD` rule used a non-`IS_AUTHENTICATED`/`IS_INTERNAL` `principalPath` | Switch principal path or change category |
| `Unsupported … contextPath` | Used a context path outside `RuleContextPathType.SESSION_DATASPACE` | Not authorable via MDAPI XML — use a runtime `RuleProvider` |

---

## Validate Before You Persist

There is no dry-run on the MD-CRUD path — a `POST create` persists. Front-load correctness instead: resolve every reference in the target org (Data 360 MCP, or a read-only `dispatch_readonly` sObject describe for a custom `__dlm` DMO), match a persistence-validated scope × category combination from `policy-shapes.md`, and GET the component back after the write to confirm it persisted as authored. The same deploy-time server validation (including the `IDENTIFIED_RECORD` constraint) runs inline on the create and returns in the `dispatch` response.
