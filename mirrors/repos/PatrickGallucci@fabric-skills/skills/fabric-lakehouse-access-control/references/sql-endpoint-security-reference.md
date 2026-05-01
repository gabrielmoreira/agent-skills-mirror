# SQL Analytics Endpoint Security Reference

Granular permissions, row-level security, column-level security, and dynamic data masking for the Fabric Lakehouse SQL analytics endpoint.

## Table of Contents

- [Overview](#overview)
- [SQL Endpoint Access Model](#sql-endpoint-access-model)
- [Object-Level Security](#object-level-security)
- [Row-Level Security](#row-level-security)
- [Column-Level Security](#column-level-security)
- [Dynamic Data Masking](#dynamic-data-masking)
- [Auditing Permissions](#auditing-permissions)
- [Common Pitfalls](#common-pitfalls)

---

## Overview

The SQL analytics endpoint provides a read-only SQL interface over lakehouse Delta tables. It uses the Fabric Data Warehouse engine and supports T-SQL constructs for granular access control.

**Key constraint:** The SQL analytics endpoint is read-only for Delta tables. You can create views, functions, and security objects, but cannot modify Delta table data. Use Spark for data writes.

**Scope:** SQL endpoint security rules ONLY apply to queries run through the SQL analytics endpoint. They do NOT apply to Spark, OneLake APIs, or Direct Lake on OneLake. To restrict access via other paths, use workspace roles, item permissions, or OneLake security.

---

## SQL Endpoint Access Model

### Permissions from workspace roles

| Workspace Role | SQL Endpoint Access |
|---------------|-------------------|
| Admin | Full control, all SQL permissions |
| Member | Full control, all SQL permissions |
| Contributor | Full control, all SQL permissions |
| Viewer | Can run SELECT queries on permitted objects |

### Permissions from item sharing

When a lakehouse is shared with a user (no workspace role), the user can connect to the SQL analytics endpoint and query objects they have been explicitly granted access to via T-SQL.

---

## Object-Level Security

Control access to specific tables, views, or schemas using GRANT, DENY, and REVOKE:

```sql
-- Grant SELECT on a specific table
GRANT SELECT ON [dbo].[Sales] TO [user@domain.com];

-- Deny access to a sensitive table
DENY SELECT ON [dbo].[EmployeeSalary] TO [user@domain.com];

-- Grant access to all tables in a schema
GRANT SELECT ON SCHEMA::[analytics] TO [AnalystRole];
```

**Important:** Object-level security at the SQL endpoint does NOT affect OneLake direct access. A user with ReadAll can still read the underlying Parquet files via Spark or OneLake APIs.

---

## Row-Level Security

RLS uses security predicates to filter rows based on user context.

### Implementation steps

1. Create a predicate function:

```sql
CREATE FUNCTION dbo.fn_SecurityPredicate_Region(@Region AS NVARCHAR(50))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
    SELECT 1 AS result
    WHERE @Region = 'West'
       OR USER_NAME() IN ('admin@domain.com');
```

2. Create and enable a security policy:

```sql
CREATE SECURITY POLICY dbo.RegionFilter
ADD FILTER PREDICATE dbo.fn_SecurityPredicate_Region(Region) ON dbo.Sales
WITH (STATE = ON, SCHEMABINDING = ON);
```

### Key behaviors

- Security policies apply to ALL users, including dbo and Admin/Member/Contributor roles.
- To allow admins to see all data for remediate, the predicate function must explicitly include them.
- With `SCHEMABINDING = ON` (default), users don't need EXECUTE on the predicate function.
- With `SCHEMABINDING = OFF`, users need EXECUTE on the function and SELECT on referenced objects.

### Audit existing RLS policies

```sql
SELECT
    sp.name AS policy_name,
    sp.is_enabled,
    sp.is_schema_bound,
    o.name AS target_table,
    spred.predicate_type_desc,
    OBJECT_NAME(spred.predicate_id) AS predicate_function
FROM sys.security_policies AS sp
JOIN sys.security_predicates AS spred
    ON sp.object_id = spred.object_id
JOIN sys.objects AS o
    ON spred.target_object_id = o.object_id;
```

---

## Column-Level Security

Restrict access to specific columns using GRANT:

```sql
-- Grant access to only non-sensitive columns
GRANT SELECT ON dbo.Employees (EmployeeId, Name, Department) TO [analyst@domain.com];
```

### Behavior with Direct Lake

Column-level security at the SQL endpoint causes Direct Lake semantic models to **fall back to DirectQuery mode**. If DirectQuery fallback is disabled, the query fails.

**Recommendation:** If using Direct Lake, prefer OneLake security CLS over SQL endpoint CLS to avoid DirectQuery fallback.

---

## Dynamic Data Masking

Mask sensitive data for non-admin users without changing the actual data:

```sql
-- Apply default mask to email column
ALTER TABLE dbo.Customers
ALTER COLUMN Email ADD MASKED WITH (FUNCTION = 'email()');

-- Apply partial mask to phone number
ALTER TABLE dbo.Customers
ALTER COLUMN Phone ADD MASKED WITH (FUNCTION = 'partial(0, "XXX-XXX-", 4)');

-- Grant UNMASK to privileged users
GRANT UNMASK ON dbo.Customers TO [manager@domain.com];
```

---

## Auditing Permissions

### View all explicit grants

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

**Note:** This query shows only explicitly granted permissions. Permissions inherited from workspace roles are not visible in these system views.

### View column-level grants

```sql
SELECT
    pr.name AS principal_name,
    OBJECT_SCHEMA_NAME(pe.major_id) AS schema_name,
    OBJECT_NAME(pe.major_id) AS table_name,
    c.name AS column_name,
    pe.permission_name,
    pe.state_desc
FROM sys.database_permissions AS pe
JOIN sys.database_principals AS pr
    ON pe.grantee_principal_id = pr.principal_id
JOIN sys.columns AS c
    ON pe.major_id = c.object_id
    AND pe.minor_id = c.column_id
WHERE pe.minor_id > 0
ORDER BY pr.name, table_name, column_name;
```

---

## Common Pitfalls

| Pitfall | Explanation | Resolution |
|---------|-------------|------------|
| SQL security does not protect OneLake access | SQL permissions only apply at the SQL endpoint | Use OneLake security or restrict OneLake access via item permissions |
| RLS blocks admin users | Security policies apply to ALL users by default | Include admin bypass logic in predicate functions |
| CLS causes Direct Lake fallback | Expected behavior with SQL endpoint CLS | Use OneLake security CLS instead, or accept DirectQuery mode |
| DENY overrides GRANT | T-SQL DENY always takes precedence | Review DENY statements carefully; remove unintended denies |
| Dynamic data masking visible in raw OneLake access | Masking only applies at the SQL endpoint | Combine with OneLake security for comprehensive protection |
| Shared lakehouse inherits no SQL permissions | Sharing grants item access, not SQL grants | Explicitly GRANT SELECT after sharing |
