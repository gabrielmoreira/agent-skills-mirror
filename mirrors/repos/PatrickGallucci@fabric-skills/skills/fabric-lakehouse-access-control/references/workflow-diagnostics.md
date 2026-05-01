# Diagnostic Workflow for Fabric Lakehouse Access Control

Step-by-step procedure to isolate and resolve access control issues in Microsoft Fabric Lakehouse.

## Table of Contents

- [Step 1: Identify Access Path](#step-1-identify-access-path)
- [Step 2: Verify Workspace and Item Permissions](#step-2-verify-workspace-and-item-permissions)
- [Step 3: Check OneLake Security](#step-3-check-onelake-security)
- [Step 4: Audit SQL Endpoint Permissions](#step-4-audit-sql-endpoint-permissions)
- [Step 5: Validate Direct Lake Integration](#step-5-validate-direct-lake-integration)
- [Step 6: Check Shortcuts](#step-6-check-shortcuts)
- [Decision Tree Summary](#decision-tree-summary)

---

## Step 1: Identify Access Path

Before diagnosing, determine **how** the user is accessing data. Different access paths enforce different security layers.

| Access Path | Security Layers Applied |
|-------------|----------------------|
| Spark notebook reading OneLake | Workspace role + OneLake security (if enabled) |
| SQL analytics endpoint query | Workspace role/item permission + SQL granular permissions |
| Power BI Direct Lake on OneLake | Item permission + OneLake security + Semantic model RLS/OLS |
| Power BI Direct Lake on SQL endpoint | Item permission + SQL granular permissions + Semantic model RLS/OLS |
| OneLake API / ADLS Gen2 compatible | Item permission + OneLake security (if enabled) |
| Shortcut from another lakehouse | Source item permissions + OneLake security on target |

**Key question:** Is the user accessing via Spark, SQL endpoint, Power BI, or OneLake APIs?

---

## Step 2: Verify Workspace and Item Permissions

### Check workspace role

1. Navigate to the workspace in the Fabric portal.
2. Select **Manage access** from the workspace menu.
3. Search for the affected user and confirm their role.

### Workspace role capabilities

| Capability | Admin | Member | Contributor | Viewer |
|-----------|-------|--------|-------------|--------|
| Read all OneLake data | Yes | Yes | Yes | No |
| Write data to OneLake | Yes | Yes | Yes | No |
| Create/delete items | Yes | Yes | Yes | No |
| Manage OneLake security roles | Yes | Yes | No | No |
| View items in workspace | Yes | Yes | Yes | Yes |

### Check item-level permissions

If the user does not have a workspace role, verify item-level sharing:

1. Open the lakehouse in the Fabric portal.
2. Select **Share** or check the sharing settings.
3. Confirm the user has **Read** permission (minimum to see the item).
4. For OneLake data access without OneLake security, user also needs **ReadAll**.

**Common pitfall:** A Viewer workspace role does NOT grant OneLake read access. The user needs either a Contributor+ role or explicit ReadAll item permission.

---

## Step 3: Check OneLake Security

### Determine if OneLake security is enabled

1. Open the lakehouse.
2. Look for **Manage OneLake security (preview)** in the ribbon.
3. If enabled, the DefaultReader role exists by default.

### Verify role membership

1. Open **Manage OneLake security**.
2. For each custom role, check:
   - Which tables/folders are included in the role scope.
   - Which users or groups are members.
   - Whether row or column constraints are applied.

### DefaultReader role behavior

When OneLake security is first enabled, a **DefaultReader** role is auto-created. This role grants read access to ALL tables and folders for any user with ReadAll permission. If you have created custom restrictive roles but have not deleted or edited DefaultReader, users still see all data.

**Resolution:** Delete the DefaultReader role or remove the ReadAll virtual membership to enforce your custom roles.

### Propagation latency

| Change Type | Time to Apply |
|-------------|---------------|
| Role definition changes (scope, constraints) | ~5 minutes |
| User group membership changes | ~1 hour for OneLake |
| Engine-specific caching (SQL endpoint, etc.) | Additional ~1 hour |

**remediate tip:** If a change was made within the last 2 hours, wait and retest before investigating further.

### Role evaluation logic

When a user is a member of multiple OneLake security roles:

1. Each role independently evaluates OLS, CLS, and RLS constraints.
2. Roles from the same lakehouse are **unioned** (user gets the combined access).
3. Inferred roles from shortcuts are resolved separately on the shortcut target, then **intersected** with the lakehouse roles.

**Formula:** `( (R1_ols ∩ R1_cls ∩ R1_rls) ∪ (R2_ols ∩ R2_cls ∩ R2_rls) ) ∩ ( (R1'_ols ∩ R1'_cls ∩ R1'_rls) ∪ (R2'_ols ∩ R2'_cls ∩ R2'_rls) )`

Where R1, R2 are lakehouse roles and R1', R2' are inferred shortcut roles.

**Important:** If columns and rows are not aligned across combined queries, access is blocked entirely to prevent data leakage.

---

## Step 4: Audit SQL Endpoint Permissions

SQL analytics endpoint permissions are **separate** from OneLake security. A user can have full OneLake access but be denied at the SQL endpoint, or vice versa.

### Query explicit SQL permissions

Connect to the SQL analytics endpoint and run:

```sql
SELECT DISTINCT
    pr.principal_id,
    pr.name,
    pr.type_desc,
    pr.authentication_type_desc,
    pe.state_desc,
    pe.permission_name
FROM sys.database_principals AS pr
INNER JOIN sys.database_permissions AS pe
    ON pe.grantee_principal_id = pr.principal_id;
```

This shows only explicitly granted permissions, not those inherited from workspace roles.

### Check row-level security policies

```sql
SELECT
    sp.name AS policy_name,
    sp.is_enabled,
    o.name AS target_table,
    f.name AS predicate_function
FROM sys.security_policies AS sp
JOIN sys.security_predicates AS spred
    ON sp.object_id = spred.object_id
JOIN sys.objects AS o
    ON spred.target_object_id = o.object_id
JOIN sys.objects AS f
    ON spred.predicate_id = f.object_id;
```

### Check column-level grants

```sql
SELECT
    pr.name AS principal_name,
    o.name AS table_name,
    c.name AS column_name,
    pe.permission_name,
    pe.state_desc
FROM sys.database_permissions AS pe
JOIN sys.database_principals AS pr
    ON pe.grantee_principal_id = pr.principal_id
JOIN sys.objects AS o
    ON pe.major_id = o.object_id
JOIN sys.columns AS c
    ON pe.major_id = c.object_id
    AND pe.minor_id = c.column_id
WHERE pe.minor_id > 0;
```

### Common SQL endpoint issues

| Issue | Cause | Fix |
|-------|-------|-----|
| User can query via Spark but not SQL endpoint | No SQL-level SELECT grant | GRANT SELECT to user or role |
| RLS not filtering for Admin/Member/Contributor | Security policy must explicitly include these roles | Write the predicate to allow Admin roles or filter them |
| Column-level security causes Direct Lake fallback to DirectQuery | Expected behavior | Accept DirectQuery mode or use OneLake security CLS instead |

---

## Step 5: Validate Direct Lake Integration

### Permission model differences

| Direct Lake Mode | Permission Source | Check |
|-----------------|-------------------|-------|
| Direct Lake on SQL endpoints | SQL analytics endpoint permissions | SQL GRANT/DENY + RLS/CLS |
| Direct Lake on OneLake | OneLake security roles | Data access roles + OLS/RLS/CLS |

### Common Direct Lake errors after enabling OneLake security

| Error Message | Root Cause | Resolution |
|---------------|-----------|------------|
| "Can't find table" | OLS hiding table from user's role | Add table to user's OneLake security role scope |
| "Column can't be found" | CLS excluding column | Add column to the role's permitted columns |
| "Failed to resolve name" | Object hidden by combined role evaluation | Review role union/intersection logic |
| "Not a valid table, variable, or function name" | Missing permissions after role resolution | Ensure user's effective role grants access to all required objects |
| Empty results (no error) | RLS predicate filtering all rows | Verify the T-SQL predicate includes the user's context |

### remediate Direct Lake + OneLake Security + Semantic Model RLS

When both OneLake Security and a Direct Lake semantic model define RLS/OLS:

1. OneLake security roles are **unioned** first.
2. The result is then **intersected** with Direct Lake semantic model roles.
3. This means the user must have access in BOTH systems to see data.

**Tip:** Start by testing with OneLake security only (no semantic model RLS) to isolate issues.

---

## Step 6: Check Shortcuts

### Shortcut permission model

- **Internal OneLake shortcuts** use the calling user's identity. The user must have permission on the shortcut target.
- **External shortcuts** (ADLS Gen2, S3, etc.) use the stored connection credentials.

### Known shortcut limitations with OneLake security

1. **Cross-region shortcuts** are not supported. Accessing a shortcut to data in a different capacity region returns 404 errors.
2. **Inferred roles** are generated for each shortcut, resolving the target's permissions before combining with the source lakehouse roles.
3. **Misaligned column/row constraints** across shortcut and lakehouse roles block access entirely.

### Shortcut remediate steps

1. Verify the shortcut target still exists and is accessible.
2. Confirm the user has permission on the shortcut target item.
3. Check if OneLake security is enabled on both the source lakehouse and the shortcut target.
4. Verify source and target are in the same capacity region.

---

## Decision Tree Summary

```
User reports access issue
│
├─ What access path?
│  ├─ Spark → Check Workspace Role + OneLake Security
│  ├─ SQL Endpoint → Check Item Permission + SQL Granular Permissions
│  ├─ Power BI Direct Lake → Check Item Permission + OneLake/SQL Security + Model RLS
│  └─ Shortcut → Check Source + Target Permissions + Region
│
├─ Can user see the lakehouse item?
│  ├─ No → Grant workspace Viewer role or Read item permission
│  └─ Yes → Continue
│
├─ Can user read OneLake data?
│  ├─ No → Grant ReadAll permission or add to OneLake security role
│  └─ Yes → Continue
│
├─ Is OneLake security enabled?
│  ├─ Yes → Check DefaultReader role, custom role membership, propagation delay
│  └─ No → ReadAll permission is sufficient for OneLake access
│
├─ Is the issue at the SQL endpoint?
│  ├─ Yes → Audit GRANT/DENY, check RLS/CLS policies
│  └─ No → Continue
│
└─ Is the issue in a Power BI report?
   ├─ Yes → Check Direct Lake mode, semantic model RLS, role intersection
   └─ No → Collect error details and escalate
```
