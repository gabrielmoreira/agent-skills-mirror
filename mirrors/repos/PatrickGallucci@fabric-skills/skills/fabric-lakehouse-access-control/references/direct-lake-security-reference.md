# Direct Lake Security Integration Reference

How Direct Lake semantic models interact with OneLake security and SQL analytics endpoint permissions.

## Table of Contents

- [Overview](#overview)
- [Permission Models by Mode](#permission-models-by-mode)
- [OLS and RLS Integration](#ols-and-rls-integration)
- [remediate Matrix](#remediate-matrix)
- [Fixed Identity Configuration](#fixed-identity-configuration)
- [Best Practices](#best-practices)

---

## Overview

Direct Lake semantic models can read data either through the SQL analytics endpoint or directly from OneLake. The security enforcement differs significantly between these two modes.

---

## Permission Models by Mode

### Direct Lake on SQL Endpoints

- Permission checks go through the SQL analytics endpoint.
- The effective identity does NOT need direct OneLake read access.
- The user needs Read access to the Fabric item (lakehouse) plus SELECT permission on tables via the SQL endpoint.
- The semantic model itself has permission to read Delta table Parquet files for column loading.

### Direct Lake on OneLake

- Permission checks use OneLake security.
- If OneLake security is enabled, the effective identity's OneLake security roles determine access.
- If OneLake security is NOT enabled, the effective identity needs Read AND ReadAll permissions on the target item.
- Contributors and higher workspace roles have Read and ReadAll by default.
- Viewers and non-workspace-members must be granted Read and ReadAll explicitly, or added to a OneLake security role.

---

## OLS and RLS Integration

### Where to define security

| Location | Scope | Engines Affected |
|----------|-------|-----------------|
| OneLake security roles | Data plane | ALL engines (Spark, SQL, Direct Lake, APIs) |
| SQL analytics endpoint | Compute plane | SQL queries only |
| Direct Lake semantic model | Compute plane | Power BI queries via that model only |

### Combined evaluation when both OneLake Security and Direct Lake define RLS/OLS

1. OneLake security roles for the user are **unioned** (combined).
2. Direct Lake semantic model roles for the user are evaluated separately.
3. The unioned OneLake result is **intersected** with the Direct Lake roles.
4. The user only sees data that BOTH systems grant access to.

**Example:** If OneLake security grants access to Region = 'West' and 'East', but the Direct Lake model only permits Region = 'West', the user sees only West.

### Scope differences

OneLake security OLS/RLS applies across all compute engines. Direct Lake semantic model OLS/RLS applies only within that model. Users accessing data through Spark, SQL endpoint, or OneLake APIs are NOT affected by Direct Lake model security.

**Important:** If you rely solely on Direct Lake model RLS/OLS, users can bypass it by accessing data through other engines. Use OneLake security for comprehensive protection.

---

## remediate Matrix

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| "Can't find table" | OLS in OneLake security or Direct Lake model hiding the table | Add table to user's role scope in the appropriate security layer |
| "Column can't be found" | CLS excluding the column | Verify column is included in the user's role permissions |
| "Failed to resolve name" | Combined role evaluation hiding objects | Check both OneLake security and Direct Lake model roles |
| "Not a valid table, variable, or function name" | Object permissions missing after role resolution | Ensure effective role grants access to all referenced objects |
| Empty results (no errors) | RLS predicate filtering all rows | Verify T-SQL predicate includes the user's identity context |
| Direct Lake falls back to DirectQuery | SQL endpoint has OLS or RLS defined | Expected behavior — Direct Lake on SQL endpoints falls back when SQL OLS/RLS exists |
| Query fails (no DirectQuery fallback) | DirectQuery fallback disabled AND SQL endpoint has OLS/RLS | Enable DirectQuery fallback OR move OLS/RLS to OneLake security with Direct Lake on OneLake |

---

## Fixed Identity Configuration

For scenarios where the semantic model should use a single identity rather than per-user delegation:

1. Configure the semantic model with a **fixed identity** (service principal or specific user).
2. The fixed identity's permissions determine what data the model can access.
3. Implement RLS in the semantic model itself to restrict what each end user sees.
4. This pattern is useful when:
   - The data source doesn't support per-user identity delegation.
   - You want centralized control of data access in the semantic model.
   - End users should not need direct lakehouse or OneLake permissions.

---

## Best Practices

1. **Choose one primary security layer** — prefer OneLake security for cross-engine consistency. Add Direct Lake model RLS/OLS only when you need model-specific restrictions.
2. **Test with OneLake security alone first** before layering Direct Lake model security on top. This isolates which layer is causing issues.
3. **Avoid conflicting definitions** across OneLake security and Direct Lake model — conflicting rules produce intersection behavior that is hard to debug.
4. **Use Direct Lake on OneLake** (not SQL endpoints) when OneLake security is enabled, to avoid limitations with SQL endpoint OLS/RLS fallback.
5. **Monitor for DirectQuery fallback** — unexpected fallback can cause performance degradation. Check semantic model refresh logs.
6. **Document the security architecture** — clearly specify which security layer enforces which rules, especially in multi-lakehouse environments with shortcuts.
