/*
================================================================================
  Validate Row-Level Security (RLS) on Fabric Lakehouse SQL Analytics Endpoint
================================================================================

  PURPOSE:
    Template for testing RLS predicates by executing queries as different users.
    Customize the table names, predicate functions, and test users below.

  PREREQUISITES:
    - Admin, Member, or Contributor workspace role (or elevated SQL permissions)
    - Connect to the SQL analytics endpoint of the lakehouse

  USAGE:
    1. Replace placeholder values with your table, function, and user names.
    2. Run each section to validate predicate behavior.
    3. Compare results against expected row counts.

================================================================================
*/

-- ============================================================================
-- SECTION 1: Inventory existing RLS policies
-- ============================================================================

SELECT
    sp.name                          AS policy_name,
    sp.is_enabled                    AS is_enabled,
    sp.is_schema_bound               AS is_schema_bound,
    OBJECT_SCHEMA_NAME(spred.target_object_id) AS target_schema,
    OBJECT_NAME(spred.target_object_id)        AS target_table,
    spred.predicate_type_desc        AS predicate_type,
    OBJECT_NAME(spred.predicate_id)  AS predicate_function,
    OBJECT_DEFINITION(spred.predicate_id)      AS predicate_definition
FROM sys.security_policies AS sp
JOIN sys.security_predicates AS spred
    ON sp.object_id = spred.object_id
ORDER BY sp.name;
GO

-- ============================================================================
-- SECTION 2: Check current user context
-- ============================================================================

SELECT
    USER_NAME()          AS current_user_name,
    SUSER_SNAME()        AS current_login,
    ORIGINAL_LOGIN()     AS original_login;
GO

-- ============================================================================
-- SECTION 3: Count rows visible to current user (with RLS active)
-- ============================================================================

-- TODO: Replace [dbo].[YourTable] with your target table
SELECT
    COUNT(*) AS visible_row_count
FROM [dbo].[YourTable];
GO

-- ============================================================================
-- SECTION 4: Temporarily disable RLS to see full row count (Admin only)
-- ============================================================================

-- TODO: Replace YourPolicyName with the actual security policy name
-- WARNING: This temporarily exposes all rows. Re-enable immediately after testing.

/*
ALTER SECURITY POLICY [dbo].[YourPolicyName] WITH (STATE = OFF);
GO

SELECT COUNT(*) AS total_row_count FROM [dbo].[YourTable];
GO

ALTER SECURITY POLICY [dbo].[YourPolicyName] WITH (STATE = ON);
GO
*/

-- ============================================================================
-- SECTION 5: Test predicate function directly
-- ============================================================================

-- TODO: Replace with your predicate function and parameters
-- This calls the predicate function directly to see what rows it would permit.

/*
SELECT *
FROM dbo.fn_SecurityPredicate_Region('West') AS result;
GO
*/

-- ============================================================================
-- SECTION 6: Validate RLS by simulating user context with EXECUTE AS
-- ============================================================================

-- NOTE: EXECUTE AS may have limitations in the Fabric SQL analytics endpoint.
-- If unavailable, test by having the actual user run the query and compare.

/*
-- Test as a specific user
EXECUTE AS USER = 'analyst@contoso.com';
GO

SELECT
    USER_NAME() AS executing_as,
    COUNT(*)    AS visible_rows
FROM [dbo].[YourTable];
GO

REVERT;
GO

-- Test as another user
EXECUTE AS USER = 'manager@contoso.com';
GO

SELECT
    USER_NAME() AS executing_as,
    COUNT(*)    AS visible_rows
FROM [dbo].[YourTable];
GO

REVERT;
GO
*/

-- ============================================================================
-- SECTION 7: Validate expected results
-- ============================================================================

-- TODO: Fill in expected row counts for each user and compare with actual results.

/*
Expected Results:
+---------------------------+------------------+-----------------+--------+
| User                      | Expected Rows    | Actual Rows     | Status |
+---------------------------+------------------+-----------------+--------+
| admin@contoso.com         | ALL (e.g., 1000) |                 |        |
| analyst@contoso.com       | West only (250)  |                 |        |
| manager@contoso.com       | West+East (500)  |                 |        |
+---------------------------+------------------+-----------------+--------+
*/

-- ============================================================================
-- SECTION 8: Check for common RLS issues
-- ============================================================================

-- Issue: Admin users see filtered data (RLS applies to ALL users by default)
-- Fix: Add bypass logic to the predicate function:
/*
CREATE OR ALTER FUNCTION dbo.fn_SecurityPredicate_Region(@Region NVARCHAR(50))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
    SELECT 1 AS result
    WHERE
        -- Admin bypass: users with Admin/Member/Contributor role see all data
        IS_MEMBER('db_owner') = 1
        -- Regular filtering
        OR @Region IN (
            SELECT AllowedRegion
            FROM dbo.UserRegionMapping
            WHERE UserEmail = USER_NAME()
        );
GO
*/

-- Issue: New users see no data
-- Cause: User not added to any role or mapping table
-- Fix: Add user to the appropriate region mapping or OneLake security role
