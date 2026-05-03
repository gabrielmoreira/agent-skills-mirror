---
type: skill
lifecycle: stable
inheritance: inheritable
name: fetch-violations
description: Query S360 Kusto for SFI-TI3.2.2 tenant isolation violations, classify by ViolationTitle, flag autofix-eligible items for downstream remediation
tier: standard
applyTo: '**/*fetch*,**/*violations*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

> **This is the primary data-fetching skill in the s360-tenant-isolation plugin.**
> It queries the S360 Kusto data source for SFI-TI3.2.2 tenant isolation violations,
> classifies them by ViolationTitle, flags autofix-eligible items, and stores
> structured results for downstream skills (e.g., `assist-sg-update`,
> `guide-cert-rehoming`, `guide-advanced-remediation`, `generate-report`).

---

## Data Source

| Property | Value |
|---|---|
| **Cluster** | `s360prodro` |
| **Database** | `service360db` |
| **Table** | `S360ExpandedActionItem_dc1c236d-e85a-413e-bdea-7fc89b096f9f` |
| **MCP** | s360-breeze MCP (registered as tool provider) |

---

## ViolationTitle Values (9 total)

| # | ViolationTitle | Autofix Eligible |
|---|---|---|
| 1 | AAD Entra Apps in Prod Tenants using certificates in Non-Prod Tenant | No |
| 2 | AAD Entra Apps cloud mismatches with Cert Cloud | No |
| 3 | AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud auth scenarios | No |
| 4 | AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud 1P scenarios | No |
| 5 | 1pApp certs Tenant mismatches the Tenant of the Security Group | Potentially¹ |
| 6 | AAD Entra apps with cross-tenant violations | No |
| 7 | 1P App with invalid security group | Yes |
| 8 | Connector domain OWNER should not use shared subjectName for authentication across tenant | No |
| 9 | Connector domain CONSUMER should not use shared subjectName for authentication across tenant | No |

> ¹ This violation needs a follow-up decision: if the Security Group should move, route to
> `assist-sg-update`; if the certificate should move, route to `guide-cert-rehoming`.

---

## MCP Runtime Fields

The s360-breeze MCP returns action item data. These are the fields available at runtime
for classification and reporting:

| MCP Path | Maps To | Description |
|---|---|---|
| `Title` | ViolationTitle | One of 9 violation types (see Step 4) |
| `TargetId` | S360 Target ID | Service-level target for the action item |
| `CustomDimensions.AppId` | AppId | Application GUID (empty for connector domain items) |
| `CustomDimensions.AppDisplayName` | AppDisplayName | App name (empty for connector domain items) |
| `CustomDimensions.AppHomeTenantId` | AppHomeTenantId | Home tenant GUID |
| `CustomDimensions.cloudType` | AppCloudType | "Public", "Fairfax", "Mooncake" |
| `SLAState` | — | "OnTime", "OutOfSla" |
| `CurrentDueDate` | — | Current due date |
| `CurrentETA` | — | Current ETA set by owner |
| `AssignedTo` | — | Assigned alias (may be a delegate) |
| `S360Dimensions.ActionOwnerAlias` | — | Action owner alias |
| `S360Dimensions.ADOWorkItemHTMLUrl` | — | ADO work item link |
| `URL` | — | TSG / remediation link |
| `KpiActionItemId` | — | Unique action item identifier |

> 📄 **Full Kusto schema reference:** The underlying Kusto table
> (`S360ExpandedActionItem_dc1c236d-...`) has 52 fields including certificate details,
> SG ownership, OneCert metadata, etc. Keep the schema reference in a shared repo or
> internal documentation location that is accessible to the whole team; do not rely on
> a user-specific local path. These fields are only accessible via direct Kusto queries,
> not the MCP API.
>
> **Normalization rule:** This skill should flatten the MCP response for downstream skills.
> For example:
> - `item.Title` → `Title` (retain the MCP field name for consistency)
> - `item.CustomDimensions.AppId` → `AppId`
> - `item.CustomDimensions.AppDisplayName` → `AppDisplayName`
> - `item.CustomDimensions.cloudType` (or `item.S360Dimensions.CloudType`) → `cloudType`
> - `item.S360Dimensions.ActionOwnerAlias` → `ActionOwnerAlias`
> - `item.S360Dimensions.ADOWorkItemHTMLUrl` → `ADOWorkItemHTMLUrl`

---

## Skill Logic

### Step 1 — Determine Query Target

Parse the user's request to determine the filter. The user may provide one or more of:

| Input Type | Example | Filter Applied |
|---|---|---|
| **Alias** | `"desantsh"` | Search using `actionOwners` first, then `assignedTo` as fallback (the `assignedTo` field may be delegated to a different person) |
| **S360 Target ID** | `"a0a46d95-..."` | `targetIds` filter on the MCP tool — note: this is the S360 TargetId, which may differ from the Service Tree ID |
| **Service Tree ID** | `"12345"` | Try it as `targetIds` via MCP. If no results, tell the user that Service Tree IDs and S360 Target IDs may differ and fall back to alias search |
| **Organization name** | `"C+AI"` | Fetch the relevant set first, then filter client-side when org information is present |
| **ViolationTitle** | `"1P App with invalid security group"` | Fetch the relevant set first, then filter client-side by `Title` |
| **"all"** or no filter | `"show all violations"` | No filter — return all violations |

If the user provides a partial ViolationTitle, fuzzy-match against the 9 known values and
confirm the match before executing the query.

---

### Step 2 — Verify s360-breeze MCP Is Available

The s360-breeze MCP is registered as a tool provider in the agent environment. Its tools
are prefixed with `s360-breeze-` (e.g., `s360-breeze-search_active_s360_kpi_action_items`,
`s360-breeze-search_s360_kpi_metadata`, etc.).

**Verification approach:** Make a lightweight probe call to any s360-breeze tool (e.g.,
`s360-breeze-search_s360_kpi_metadata` with a known KPI name search) to confirm the MCP
is connected and responding. If the tool call fails with a connection or availability
error, stop and inform the user that the s360-breeze MCP is not available.

> ℹ️ MCP connection details are runtime-managed. Do not probe or depend on a specific
> port in skill logic.

**Authentication errors:** If the MCP returns an authentication/token error, instruct the
user to re-authenticate to the `s360prodro` Kusto cluster:
```
azureauth --resource https://s360prodro.kusto.windows.net
```

---

### Step 3 — Fetch Violations via s360-breeze MCP

Use the `s360-breeze-search_active_s360_kpi_action_items` tool with the KPI ID and
the filter determined in Step 1.

**KPI ID:** `dc1c236d-e85a-413e-bdea-7fc89b096f9f`

#### By alias (action owner)

```json
{
  "request": {
    "kpiIds": ["dc1c236d-e85a-413e-bdea-7fc89b096f9f"],
    "actionOwners": ["{alias}"],
    "pageSize": 50
  }
}
```

If zero results, fall back to `assignedTo`:

```json
{
  "request": {
    "kpiIds": ["dc1c236d-e85a-413e-bdea-7fc89b096f9f"],
    "assignedTo": ["{alias}"],
    "pageSize": 50
  }
}
```

#### By S360 Target ID

```json
{
  "request": {
    "kpiIds": ["dc1c236d-e85a-413e-bdea-7fc89b096f9f"],
    "targetIds": ["{targetId}"],
    "pageSize": 50
  }
}
```

#### All violations (no filter)

```json
{
  "request": {
    "kpiIds": ["dc1c236d-e85a-413e-bdea-7fc89b096f9f"],
    "pageSize": 50
  }
}
```

> ℹ️ **Pagination:** If `nextCursor` is non-empty in the response, pass it as `cursor`
> in a follow-up request to fetch the next page.
>
> ⚠️ **Filtering by Service Tree ID, Organization, or ViolationTitle** is not directly
> supported by the MCP tool. Fetch all violations for the target/alias and filter
> client-side by matching `CustomDimensions.cloudType`, `Title`, or `TargetId`.

---

### Step 4 — Parse and Classify Results

Once results are returned, process them as follows:

#### 4a. Group by ViolationTitle

Group results by `Title` (= ViolationTitle). There are at most 9 groups
(one per known violation type). Unknown titles should be placed in an "Other" bucket
and flagged for investigation.

#### 4b. Compute per-group metrics

For each ViolationTitle group, calculate:

| Metric | Computation |
|---|---|
| **Count** | Number of violations in the group |
| **Unique Apps** | Distinct `CustomDimensions.AppId` values |
| **Autofix Eligible** | See autofix logic below |

#### 4c. Autofix eligibility classification

A violation is **autofix eligible** (via `assist-sg-update`) when:

1. `Title == "1P App with invalid security group"`
   — **always** autofix eligible.
2. `Title` contains `"certs Tenant mismatches the Tenant of the Security Group"`
   — **potentially** autofix eligible. The Breeze scenario will determine if the SG
   can be updated (Option 1) or if cert rehoming is needed (Option 2).

All other Title values are **not** autofix eligible. They require manual remediation
via `guide-cert-rehoming` or `guide-advanced-remediation`.

#### 4d. Generate summary table

Output a summary table in this format:

```markdown
## Violation Summary

| # | Violation | Count | Apps | Cloud | SLA | Autofix |
|---|---|---|---|---|---|---|
| 1 | 1P App with invalid security group | 42 | 38 | Public | OutOfSla | ✅ Yes |
| 2 | 1pApp certs Tenant mismatches... | 18 | 15 | Mixed | OutOfSla | ⚠️ Partial |
| 3 | AAD Entra Apps cloud mismatches... | 95 | 80 | Fairfax | OutOfSla | ❌ No |
| ... | ... | ... | ... | ... | ... | ... |

**Total violations: {totalCount}**
**Autofix eligible: {autofixCount} ({autofixPercent}%)**
```

If the user requested a specific filter, also show which filter was applied at the top
of the output:

```markdown
> **Filter applied:** actionOwner == "desantsh"
```

---

### Step 5 — Store Structured Data for Downstream Skills

Store the full violation dataset and the computed summary in a structured format that
downstream skills can consume:

Use a **normalized flat shape** for each violation object so downstream skills do not need
to understand the nested MCP response format.

```json
{
  "fetchedAt": "2025-01-15T10:30:00Z",
  "filterApplied": {
    "type": "actionOwner",
    "value": "desantsh"
  },
  "totalViolations": 250,
  "autofixEligible": 60,
  "summary": [
    {
      "violationTitle": "1P App with invalid security group",
      "count": 42,
      "uniqueApps": 38,
      "autofixEligible": true
    }
  ],
  "violations": [
    {
      "KpiActionItemId": "...",
      "Title": "...",
      "TargetId": "...",
      "AppId": "...",
      "AppDisplayName": "...",
      "cloudType": "...",
      "SLAState": "...",
      "CurrentETA": "...",
      "ADOWorkItemHTMLUrl": "...",
      "ActionOwnerAlias": "..."
    }
  ]
}
```

This data is passed to:

| Downstream Skill | What It Uses |
|---|---|
| `assist-sg-update` | Autofix-eligible violations (ViolationTitle #5 and #7) |
| `guide-cert-rehoming` | Cert rehoming violations (ViolationTitle #1, #2) |
| `guide-advanced-remediation` | Cross-cloud, cross-tenant, and connector violations (ViolationTitle #3, #4, #6, #8, #9) |
| `generate-report` | Full summary and violation details for executive reporting |

---

## Error Handling

| Scenario | Action |
|---|---|
| s360-breeze MCP not available | Make a probe call to any `s360-breeze-` tool. If it fails with a connection error, stop and tell the user the MCP is not connected. Do not assume a specific port. |
| MCP returns an authentication error | Instruct the user to re-authenticate: `azureauth --resource https://s360prodro.kusto.windows.net` |
| Kusto query returns zero results | Report "No violations found" with the filter applied. Suggest the user check the filter or try "all". |
| Kusto query times out | Retry once. If it times out again, suggest narrowing the filter (e.g., by ViolationTitle or ServiceId). |
| Unknown ViolationTitle in results | Include in output under an "Other / Unknown" group and flag for investigation. |
| MCP returns an authentication error | Instruct the user to re-authenticate to the s360prodro cluster. |
| Partial results (query truncated) | Warn the user that results may be incomplete and suggest adding filters to reduce result size. |

---

## Important Notes

- **S360 data refreshes every 24 hours.** Violations fetched reflect the last refresh
  cycle, not real-time state.
- **The `s360prodro` cluster is read-only.** This skill only reads data — it does not
  modify any S360 records.
- **Autofix eligibility is a classification, not an action.** This skill identifies
  which violations *can* be autofixed; the actual fix is performed by `assist-sg-update`.
- **Always display the filter applied.** Users must know whether they are looking at a
  subset or the full violation set.
- **Large result sets.** Unfiltered queries may return thousands of rows. If the result
  set exceeds 500 rows, automatically run the summary-only KQL first and offer to fetch
  full details per ViolationTitle group on request.
