# OneLake Security Reference

Comprehensive reference for OneLake security data access roles in Microsoft Fabric Lakehouse.

## Table of Contents

- [Overview](#overview)
- [Enabling OneLake Security](#enabling-onelake-security)
- [Data Access Role Structure](#data-access-role-structure)
- [Role Membership Types](#role-membership-types)
- [Row-Level Security](#row-level-security)
- [Column-Level Security](#column-level-security)
- [Limitations](#limitations)
- [Propagation Latency](#propagation-latency)
- [Git Integration and Deployment Pipelines](#git-integration-and-deployment-pipelines)
- [Best Practices](#best-practices)

---

## Overview

OneLake security is the data plane security model for Fabric Lakehouse. It provides granular role-based access control at the table, folder, row, and column level. When enabled, it enforces access consistently across all compute engines (Spark, SQL endpoint, Direct Lake, OneLake APIs).

OneLake security is currently in **preview** and is **disabled by default** on a per-item basis.

**Critical:** Once enabled on a lakehouse, OneLake security cannot be turned off.

---

## Enabling OneLake Security

1. Open the lakehouse and select **Manage OneLake security (preview)** from the ribbon.
2. Review the confirmation dialog. OneLake security is incompatible with the External Data Sharing preview.
3. Select **Continue**.
4. A **DefaultReader** role is created automatically, granting ReadAll users full read access.

**Post-enablement action:** To restrict access, delete or edit the DefaultReader role and create custom roles.

---

## Data Access Role Structure

Each data access role has four components:

| Component | Description |
|-----------|-------------|
| `id` | Unique GUID for the role |
| `name` | Display name of the role |
| `decisionRules` | Array of permission rules defining scope and constraints |
| `members` | Users, groups, or virtual members assigned to the role |

### Decision Rules

Each decision rule contains:

| Field | Description |
|-------|-------------|
| `effect` | Always `Permit` (the only supported value) |
| `permission` | Array of two PermissionScope objects: Path and Action |
| `constraints` | Optional row and column constraints |

### Permission Scope

| AttributeName | Description | Example Values |
|--------------|-------------|----------------|
| `Path` | Table or folder paths the role grants access to | `/Tables/dbo/Sales`, `/Tables/*` |
| `Action` | Operations permitted | `Read` |

---

## Role Membership Types

### Fabric Item Members (Virtual Membership)

Automatically includes users based on their existing Fabric permissions:

```json
{
  "fabricItemMembers": [
    {
      "sourcePath": "00000000-0000-0000-0000-000000000000/00000000-0000-0000-0000-000000000000",
      "itemAccess": ["ReadAll"]
    }
  ]
}
```

The `sourcePath` always references the same lakehouse using empty GUIDs. Users with the specified `itemAccess` permission are automatically included.

### Microsoft Entra Members

Directly assign Entra users or groups. Supported in the OneLake security UI but **not supported** in lakehouse item definition APIs or CICD operations.

---

## Row-Level Security

Row constraints use T-SQL predicates to filter data:

```json
{
  "constraints": {
    "rows": [
      {
        "tablePath": "/Tables/dbo/Sales",
        "value": "[Region] = 'West'"
      }
    ]
  }
}
```

The `value` field is a T-SQL WHERE clause expression. Supported functions include standard comparison operators and string functions.

**Scope:** OneLake RLS applies across ALL compute engines, unlike SQL endpoint RLS which only applies to SQL queries.

---

## Column-Level Security

Column constraints restrict which columns are visible:

```json
{
  "constraints": {
    "columns": [
      {
        "tablePath": "/Tables/dbo/Employees",
        "columnNames": ["Name", "Department", "Title"],
        "columnAction": ["Read"],
        "columnEffect": "Permit"
      }
    ]
  }
}
```

Use `"columnNames": ["*"]` to grant access to all columns. Column names are **case-sensitive**.

---

## Limitations

### Hard Limits

| Constraint | Maximum |
|-----------|---------|
| OneLake security roles per lakehouse | 250 |
| Members per role | 500 users or user groups |
| Permissions per role | 500 |

### Functional Limitations

1. **Cross-region shortcuts** not supported — returns 404 errors.
2. **Distribution lists** cannot be resolved by SQL endpoint — use security groups instead.
3. **Private link protection** not compatible with OneLake security.
4. **External Data Sharing preview** incompatible — existing shares may stop working.
5. **Azure Data Share / Purview Data Share** not compatible.
6. **Mixed-mode queries** fail if they access both OneLake-security-enabled and non-enabled data.
7. **Spark notebooks** require environment 3.5+ and Fabric runtime 1.3+.
8. **Spark SQL queries** require at least Viewer workspace access.
9. **B2B guest users** require Entra External Collaboration "Guest user access" set to "same access as members."
10. **Entra member IDs** are not tracked in git for security reasons.

---

## Propagation Latency

| Change | Approximate Delay |
|--------|-------------------|
| Role definition update (scope, constraints, permissions) | ~5 minutes |
| User group membership change | ~1 hour for OneLake |
| Engine-specific caching (SQL endpoint, Spark, etc.) | Additional ~1 hour |

**remediate:** Always allow up to 2 hours for changes to fully propagate before investigating further.

---

## Git Integration and Deployment Pipelines

### What is tracked

OneLake security data access role definitions are stored in `data-access-roles.json` under the lakehouse folder in git. Supported operations: addition, deletion, and updates.

**Requirement:** Only Admin or Member workspace roles can sync security role definitions to git.

### Deployment behavior matrix

| Source State | Target State | Git Integration | Deployment Pipeline |
|-------------|-------------|-----------------|-------------------|
| DAR + Opt-In enabled | New target (no lakehouse) | Auto-enable on target | Auto-enable on target |
| DAR + Opt-In enabled | DAR tracking disabled | Auto-enable both | Auto-enable both |
| DAR + Opt-In enabled | DAR enabled, Opt-In disabled | Prompt user to enable | Error — manual config required |
| DAR + Opt-In enabled | DAR + Opt-In enabled | Normal sync | Normal sync |

**Caution:** Entra member IDs are NOT tracked in git. During sync, members are preserved only if role names match exactly between source and target. Renaming roles with assigned members requires careful coordination.

---

## Best Practices

1. **Delete the DefaultReader role** immediately after enabling OneLake security to enforce least-privilege.
2. **Use security groups** instead of individual users or distribution lists for role membership.
3. **Start with broad roles** and narrow scope incrementally, testing at each step.
4. **Use OneLake security** rather than SQL endpoint compute permissions when possible, to ensure consistent access across all engines.
5. **Wait for propagation** — always allow 2 hours before remediate permission change failures.
6. **Test with a single user** before rolling out role changes broadly.
7. **Align column and row constraints** across all roles a user might belong to — misalignment blocks access.
8. **Document role definitions** in your team's operational runbook alongside the `data-access-roles.json` file.
