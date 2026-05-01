# OLS/CLS remediate Guide

Diagnostic workflow for Object-Level Security and Column-Level Security issues in Microsoft Fabric Power BI.

## Table of Contents

- [Overview](#overview)
- [Common Symptoms](#common-symptoms)
- [Diagnostic Workflow](#diagnostic-workflow)
- [Configuring OLS with Tabular Editor](#configuring-ols-with-tabular-editor)
- [CLS in SQL Analytics Endpoint](#cls-in-sql-analytics-endpoint)
- [Restrictions and Limitations](#restrictions-and-limitations)
- [Composite Model Considerations](#composite-model-considerations)

## Overview

**Object-Level Security (OLS)** restricts access to specific tables or columns and their metadata. Unauthorized users see the secured objects as if they do not exist.

**Column-Level Security (CLS)** is a subset of OLS focused on restricting individual column access, particularly used in SQL analytics endpoints and Fabric data warehouses.

| Security Type | Defined In | Applies To | Tool Required |
|--------------|-----------|------------|---------------|
| OLS (Semantic Model) | Tabular Editor | Viewers only | Tabular Editor |
| OLS (SQL Endpoint) | T-SQL GRANT/DENY | SQL queries | SSMS or SQL client |
| CLS (SQL Endpoint) | T-SQL GRANT/DENY | SQL queries | SSMS or SQL client |
| CLS (Semantic Model) | Tabular Editor | Viewers only | Tabular Editor |

## Common Symptoms

| Symptom | Probable Cause |
|---------|---------------|
| "The field cannot be found" error in visuals | OLS hiding the column/table from user's role |
| Measure returns error | Measure references a secured column (auto-restricted) |
| Q&A visual not working | OLS does not support Q&A visualizations |
| Quick Insights unavailable | OLS does not support Quick Insights |
| Different users see different schema | OLS roles applied correctly (expected behavior) |
| Query-time error with combined roles | RLS and OLS combined from different roles |

## Diagnostic Workflow

### Step 1: Identify the Secured Object

1. Open the report as the affected user (or use "Test as role")
2. Note which visuals show errors — the field name in the error message identifies the secured object
3. The error message: *"The field [FieldName] cannot be found or may not be used in this expression"*

### Step 2: Inspect Roles in Tabular Editor

1. Open the semantic model in Power BI Desktop
2. Launch **Tabular Editor** from the External Tools ribbon
3. Expand **Roles** → select the user's role
4. Check **Table Permissions**:
   - `None` = Table/column is hidden from this role
   - `Read` = Table/column is visible to this role

### Step 3: Verify User Role Assignment

Same as RLS — check that the user is assigned to the **correct** role in the Power BI service via the semantic model's Security page.

### Step 4: Check for Role Combination Conflicts

**Critical Rule**: RLS and OLS **cannot** be combined from different roles. If a user is a member of:
- Role A (has RLS rules)
- Role B (has OLS rules)

This combination causes a **query-time error**. Both security types must be defined within the **same role**.

### Step 5: Verify Workspace Role

OLS only applies to users with the **Viewer** role. Admin, Member, and Contributor roles bypass OLS.

## Configuring OLS with Tabular Editor

### Secure an Entire Table

1. In Tabular Editor, select the role
2. Under **Table Permissions**, set the target table to `None`
3. Save and publish

### Secure a Specific Column

1. In Tabular Editor, select the role
2. Expand the table under **Table Permissions**
3. Set the target column's **Object Level Security** to `None`
4. Save and publish

### Secure Column Metadata

To also hide the column name (not just data):

```json
{
  "roles": [
    {
      "name": "RestrictedUsers",
      "modelPermission": "read",
      "tablePermissions": [
        {
          "name": "Employee",
          "columnPermissions": [
            {
              "name": "Salary",
              "metadataPermission": "none"
            }
          ]
        }
      ]
    }
  ]
}
```

## CLS in SQL Analytics Endpoint

For Fabric Warehouse and SQL Analytics Endpoint, use T-SQL:

```sql
-- Grant SELECT on specific columns only
GRANT SELECT ON dbo.Employee (EmployeeId, FirstName, LastName, Department) TO [RestrictedRole];

-- Deny access to sensitive column
DENY SELECT ON dbo.Employee (Salary) TO [RestrictedRole];
```

**Impact on DirectLake**: If CLS/OLS is configured on the SQL analytics endpoint, DirectLake falls back to DirectQuery mode for affected tables.

## Restrictions and Limitations

### Table-Level Security Chain Rule

You **cannot** secure a table that sits in the middle of a relationship chain. If tables A → B → C have relationships:
- Securing table B breaks the chain between A and C
- A separate direct relationship between A and C is required

### Unsupported Features with OLS

When OLS is configured on a semantic model, these Power BI features are **not supported**:

- Q&A visualizations
- Quick Insights visualizations
- Smart Narrative visualizations
- Excel Data Types gallery
- Copilot in Power BI

### Automatic Measure Restriction

Measures are implicitly secured if they reference a secured column. There is no way to explicitly secure a measure — update the measure expression to reference a secured column if restriction is needed.

### Relationship Constraints

Relationships that reference a secured column work **only if** the table containing the column is not itself secured.

## Composite Model Considerations

When building composite models on OLS-protected sources via DirectQuery:

1. **Schema copy depends on the author's permissions**: The composite model copies only what the author can see in the source model
2. **OLS is not inherited**: The composite model itself is not secured by source OLS rules
3. **Consumer visibility mismatch**: A consumer may see objects in the composite model that are hidden from them in the source (because the author could see them), or miss objects the consumer can see in the source (because the author couldn't)

**Mitigation**: Always define OLS in the composite model separately if security is required, or restrict composite model creation to authorized users.
