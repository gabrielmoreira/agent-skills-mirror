-- =============================================================================
-- check-cdf-status.sql
-- Audit Change Data Feed (CDF) status on source tables for MLV optimal refresh
-- 
-- Usage: Execute in a Fabric notebook connected to your lakehouse
-- Purpose: Identifies source tables missing the delta.enableChangeDataFeed
--          property, which is required for incremental refresh to work.
-- =============================================================================

-- Step 1: List all tables in the target schema and check CDF status
-- Replace 'bronze' with your source schema name

DESCRIBE DETAIL bronze.customers;
-- Look for delta.enableChangeDataFeed=true in the properties column

DESCRIBE DETAIL bronze.orders;
-- Repeat for each source table referenced by your MLVs

-- =============================================================================
-- Step 2: Enable CDF on tables that are missing it
-- Uncomment and modify as needed
-- =============================================================================

-- ALTER TABLE bronze.customers SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
-- ALTER TABLE bronze.orders SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- =============================================================================
-- Step 3: Verify CDF is enabled after setting
-- =============================================================================

-- DESCRIBE DETAIL bronze.customers;
-- Check that properties includes: delta.enableChangeDataFeed=true

-- =============================================================================
-- Step 4: Check MLV definitions for CDF property
-- Replace with your actual MLV names
-- =============================================================================

-- SHOW CREATE MATERIALIZED LAKE VIEW silver.customer_orders;
-- Verify TBLPROPERTIES includes delta.enableChangeDataFeed=true

-- =============================================================================
-- NOTES:
-- - CDF must be enabled on ALL source tables referenced by the MLV
-- - Enabling CDF after table creation only captures changes going forward
-- - First refresh after enabling CDF will still be a full refresh
-- - Incremental refresh only works for append-only data patterns
-- - If source has UPDATE/DELETE, full refresh occurs regardless of CDF
-- =============================================================================
