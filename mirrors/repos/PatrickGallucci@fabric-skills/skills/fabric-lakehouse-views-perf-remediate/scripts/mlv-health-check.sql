-- =============================================================================
-- mlv-health-check.sql
-- Comprehensive health check for materialized lake views in a Fabric lakehouse
--
-- Usage: Execute each section in a Fabric notebook connected to your lakehouse
-- Purpose: Audit MLV configurations, identify performance issues, and validate
--          optimal refresh readiness.
-- =============================================================================

-- =============================================================================
-- SECTION 1: Inventory all MLVs across schemas
-- =============================================================================

-- List MLVs in each schema (repeat for each schema in your lakehouse)
SHOW MATERIALIZED LAKE VIEWS IN bronze;
SHOW MATERIALIZED LAKE VIEWS IN silver;
SHOW MATERIALIZED LAKE VIEWS IN gold;

-- =============================================================================
-- SECTION 2: Review MLV definitions for optimization opportunities
-- Replace mlv_name with actual MLV names from Section 1
-- =============================================================================

-- Check the CREATE statement for each MLV
-- Look for:
--   - PARTITIONED BY clause (improves parallelism for large datasets)
--   - TBLPROPERTIES with delta.enableChangeDataFeed=true
--   - CONSTRAINT definitions and their actions (DROP vs FAIL)
--   - Unsupported expressions (window functions, LEFT JOIN, non-deterministic functions)

-- SHOW CREATE MATERIALIZED LAKE VIEW silver.mlv_name;

-- =============================================================================
-- SECTION 3: Validate source table CDF status
-- For each source table referenced by your MLVs, verify CDF is enabled
-- =============================================================================

-- DESCRIBE DETAIL schema.source_table_name;
-- Check properties column for: delta.enableChangeDataFeed=true

-- =============================================================================
-- SECTION 4: Check source table data patterns
-- Incremental refresh only works with append-only data
-- =============================================================================

-- Check Delta log for recent operations on source tables
-- DESCRIBE HISTORY schema.source_table_name LIMIT 10;
-- Look for operation types: WRITE (append), MERGE, UPDATE, DELETE
-- If UPDATE/DELETE/MERGE present, incremental refresh will not be used

-- =============================================================================
-- SECTION 5: Validate partition strategy
-- Large MLVs (>10M rows) should use PARTITIONED BY
-- =============================================================================

-- Check row counts for MLV output tables
-- SELECT COUNT(*) FROM silver.mlv_name;

-- Check partition info
-- DESCRIBE DETAIL silver.mlv_name;
-- Review numFiles and sizeInBytes for partition distribution

-- =============================================================================
-- SECTION 6: Identify constraint issues
-- Known issue: FAIL constraints can cause "delta table not found"
-- =============================================================================

-- Review all MLV definitions (from Section 2) for FAIL constraints
-- If found, consider recreating with DROP action:

-- DROP MATERIALIZED LAKE VIEW schema.mlv_name;
-- CREATE MATERIALIZED LAKE VIEW schema.mlv_name (
--     CONSTRAINT constraint_name CHECK (condition) ON MISMATCH DROP
-- ) AS SELECT ...;

-- =============================================================================
-- SECTION 7: Force a test refresh
-- Use this to verify MLV is working correctly after changes
-- =============================================================================

-- Full refresh (forces complete recompute)
-- REFRESH MATERIALIZED LAKE VIEW silver.mlv_name FULL;

-- =============================================================================
-- HEALTH CHECK SUMMARY
-- After running all sections, document findings:
--
-- [ ] All MLVs inventoried across schemas
-- [ ] CDF enabled on all source tables
-- [ ] No FAIL constraints (or FAIL constraints verified safe)
-- [ ] Source data is append-only (or full refresh is acceptable)
-- [ ] Large MLVs have PARTITIONED BY
-- [ ] No unsupported SQL constructs in definitions
-- [ ] Test refresh completed successfully
-- =============================================================================
