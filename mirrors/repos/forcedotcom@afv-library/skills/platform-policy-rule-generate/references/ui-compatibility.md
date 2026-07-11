# UI Compatibility — Data Governance Policy Builder

The Data Governance Policy Builder edits a **strict subset** of the MDAPI. Anything outside that subset must be maintained via MDAPI/Tooling for the policy's lifetime — admins cannot open it in the builder without silent data loss or a hard crash.

> **Default goal**: produce UI-compatible policies. Only fall back to API-only after asking the operator and getting explicit confirmation.

---

## What the UI Can Render

**Categories** : `GOVERNANCE_POLICY_RULE_DEFINITION`, `RECORD_POLICY_RULE_DEFINITION`, `TRANSFORM_POLICY_RULE_DEFINITION` 
**Categories NOT handled** : `ACCESS_POLICY_RULE_DEFINITION` (UI forces to GOVERNANCE on save), `IDENTIFIED_RECORD_POLICY_RULE_DEFINITION`

**Effects** : `Permit`, `Forbid` (UI label "Deny"), `Transform`

**Actions** : `Read`, `TupleRead` — two real choices for OLS/FLS rules.
- `Read`: evaluates conditions against the resource itself
- `TupleRead`: cascade rewriter — expands object-level condition to also cover `resource.object.*` for fields. Use when the intent is "objects matching X AND all their fields"
- Multiple `<action>` entries: only the first is kept on save

**`<ruleConsumer>`** : only `DATACLOUD` (hardcoded on save) 
**`<principalScopeType>`** : only `ANY` (hardcoded on save) 
**`<resourceScopeType>`** : `ANY`, `RECORD`, `FIELD`, `DATASPACE`, `SPAN` 
**`<principalAuthenticationLevel>`** : `INTERNAL`, `AUTHENTICATED`, `UNIDENTIFIED`. `IDENTIFIED` not exposed. 
**`<replicated>`** : read but NOT editable. Once `true`, UI forces read-only mode. 
**`<transformPrecedence>`** : not exposed; non-zero values dropped.

---

## Conditions — Supported Shapes

**Top-level conjunction**: only `<whenPolicyRuleDefinitionClauseConjunction>`. The UI forces `<unlessPolicyRuleDefinitionClauseConjunction>` to `null` on save.

**Conjunction expression**: the UI builds `(AND …)` of up to four sections dispatched by path type. A pure flat `(OR 1 2)` at the top level triggers `// ERROR: Unsupported rule!` — rule silently dropped. `OR` only round-trips inside a single section's group.

**Path types per UI section:**

| UI Section | Recognized path |
|------------|-----------------|
| Users (Permission) | `principalPath = ASSIGNED_PERMISSIONS_PATH` |
| Resource entity-type | `resourcePath = ENTITYTYPE` with `IS` operator |
| Data space | `resourcePath = DATASPACE` or `contextPath = SESSION_DATASPACE` |
| Tag / Classification | `resourcePath = TAG` or `CLASSIFICATION` |
| RLS rule criteria | `resourcePath = RECORDFIELD` or `EXPRESSION` |

Any other path type → condition silently ignored when UI rebuilds the rule.

**Operators per path**:
- Tag/Classification: `CONTAINS_ANY`, `CONTAINS_NONE`. (`CONTAINS_ALL` exists in schema but not offered in dropdowns)
- Permission: `CONTAINS_ANY` (Permit) / `CONTAINS_NONE` (Forbid/Transform)
- RLS `RECORDFIELD`: `EQUALS`, `NOT_EQUALS`, `LIKE`, `LESS_THAN(_OR_EQUALS)`, `GREATER_THAN(_OR_EQUAL)`, `HIERARCHICALLY_ABOVE` (DLO/DMO only). **Not editable**: `HIERARCHICALLY_BELOW`, `IN`, `CONTAINS_ALL`
- RLS join (`EXPRESSION`): `EXISTS` only

**`<policyRuleValueSet>` reference types** : `CUSTOM_TAG`, `STANDARD_TAG`, `CUSTOM_CLASSIFICATION`, `STANDARD_CLASSIFICATION`, `CUSTOM_PERMISSION`. **Not editable**: `HIERARCHY`, `DATASPACE`.

---

## Implicit Defaults Injected by the UI on Save

When the UI saves, it auto-injects these — if your hand-authored XML omits them or uses different values, the first UI save rewrites them:

| Field | UI default |
|-------|-----------|
| `principalAuthenticationLevel` | `INTERNAL` |
| `principalScopeType` | `ANY` |
| `ruleConsumer` | `DATACLOUD` |
| `unlessPolicyRuleDefinitionClauseConjunction` | `null` (always) |
| `actions` | only first action kept |
| `policyRuleResourceDomains` | only first `<resourceDomain>` kept |

---

## The Non-Round-Trip Checklist

The policy will **not** round-trip through the UI without data loss or silent failure if **any** of the following is true:

- [ ] `category` is `ACCESS_POLICY_RULE_DEFINITION` or `IDENTIFIED_RECORD_POLICY_RULE_DEFINITION`
- [ ] `ruleConsumer` ≠ `DATACLOUD`
- [ ] More than one `<action>`, or action is not `Read` / `TupleRead`
- [ ] **No top-level `resourcePath=ENTITYTYPE` discriminator group** for ACCESS/GOVERNANCE rules — this causes a **hard crash** (`Cannot use 'in' operator to search for 'Permit' in undefined`), not a graceful degradation. A `TupleRead` rule without the OR-of-ENTITYTYPE clause still deploys and works at runtime — the crash is UI-only.
- [ ] **Bare top-level condition index** in `<conjunctionExpression>` (e.g. `3` instead of `(AND 3)`) — causes crash in `buildCriteria` (`param.params.map(...)` = `undefined.map()`)
- [ ] More than one `<resourceDomain>`
- [ ] An `<unlessPolicyRuleDefinitionClauseConjunction>` block present
- [ ] Any `<conditions>` uses `<clause>UNLESS</clause>`
- [ ] `<conjunctionExpression>` uses top-level `OR` (e.g. `(OR 1 2)`)
- [ ] `<principalPath>` other than `ASSIGNED_PERMISSIONS_PATH` (user ID etc. may appear only inside SOQL `${User.X}` substitutions)
- [ ] `<resourcePath>` other than `TAG`, `CLASSIFICATION`, `DATASPACE`, `RECORDFIELD`, `EXPRESSION`, `ENTITYTYPE`
- [ ] `<valuePrincipalPath>` is not one of `USER_ID`, `USER_ROLE_ID`, `ORGANIZATION_ID`, `SCALAR_ATTRIBUTE`, `PLURAL_ATTRIBUTE` (with `${User.X}` expression)
- [ ] `<contextPath>` other than `SESSION_DATASPACE`
- [ ] Operator is `HIERARCHICALLY_BELOW`, `IN`, or `CONTAINS_ALL`
- [ ] `<valueReferenceType>` is `HIERARCHY` or `DATASPACE`
- [ ] `<valueString>` is typed JSON other than `{"t":"Text","v":"FIELD"|"RECORD"|"OBJECT"}` or `{"t":"Boolean","v":…}` with a UI-recognized boolean field
- [ ] `<resourceTransform>` not in the masking-category mapped set
- [ ] `<resourceExpression>` ARGLIST has multiple arguments
- [ ] `<replicated>true</replicated>` in an org with replication frozen

If **none** of the above is true, the policy is **UI-compatible**.

> **Important**: The UI shows NO banner when it drops unsupported pieces on save (`// ERROR: Unsupported rule!` comment, no surfaced message). Operator-confirmation is the only line of defense.

---

## Operator-Confirmation Protocol

Whenever a request would produce a UI-incompatible policy:

1. **Try to make it UI-compatible first.** Mechanical rewrites:
 - `unless` → `when` with negated operator:
 | Intent | UI-compatible rewrite |
 |--------|----------------------|
 | `unless principal has permission X` | `WHEN ASSIGNED_PERMISSIONS_PATH CONTAINS_NONE X` |
 | `unless resource has tag X` | `WHEN TAG CONTAINS_NONE X` |
 | `unless record field = value` | `WHEN RECORDFIELD NOT_EQUALS value` |
 - Top-level `OR` between two tags → nest inside a tag/classification section group
 - Multiple `<action>` → split into multiple rules

2. **If a UI-compatible rewrite is not possible**, tell the operator:
 - Which traits make it incompatible (cite items from the checklist above)
 - That the Data Governance Policy Builder will silently drop unsupported pieces on save with no warning
 - That maintenance must happen through MDAPI/Tooling for the policy's lifetime

3. **Wait for explicit confirmation.** Do not write the file until confirmed.

4. **On confirmation**, add an in-source marker to `<description>` (or a comment above the rule): `# API-only: not editable in Data Governance Policy Builder. Reasons: <bullets>`. Also set `<builderCompatible>false</builderCompatible>` on the parent set.

---

## UI-Compatibility Matrix for Templates

| Template | UI-compatible? | Notes |
|----------|----------------|-------|
| Bare permit, no conditions | Partial | Single `<action>Read</action>` only; `ruleConsumer=DATACLOUD`. UI maps ACCESS → Governance on load. |
| Tag / Classification / Permission gate | Yes | `CONTAINS_ANY` / `CONTAINS_NONE` only. Tag refs must resolve in org. |
| Basic RLS (RECORDFIELD = user attribute) | Yes | `USER_ID` / `ORGANIZATION_ID` / `USER_ROLE_ID` round-trips. |
| TupleRead with OR-of-ENTITYTYPE | Yes | The canonical UI-compatible OLS/FLS shape. |
| IDENTIFIED_RECORD | Not MDAPI-authorable | Must be a runtime RuleProvider. |
| RLS via PROJECTION join | Yes | Single PROJECTION editable. |
| Scalar/plural SOQL principal | Out of MDAPI contract | `SCALAR_ATTRIBUTE`/`PLURAL_ATTRIBUTE` not in `RulePrincipalPathType`. Fixture-only. |
| TRANSFORM with permission + classification | Yes | Use masking-category-mapped transforms only. |
| `(AND 1 2)` multi-condition | Yes (if each section is one of the four UI buckets) | |
| Top-level `(OR 1 2)` | No | Triggers unsupported-rule path; silently dropped. |
| Hierarchy traversal | No | `HIERARCHICALLY_BELOW` and `HIERARCHY` not in UI dropdowns. Always API-only. |
