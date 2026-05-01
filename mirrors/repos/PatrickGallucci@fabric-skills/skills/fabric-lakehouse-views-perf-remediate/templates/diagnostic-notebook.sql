-- =============================================================================
-- diagnostic-notebook.sql
-- Template: Systematic MLV remediate Notebook
--
-- Instructions:
--   1. Create a new Fabric notebook attached to the target lakehouse
--   2. Copy this template into the notebook
--   3. Replace placeholders (marked with <<PLACEHOLDER>>) with actual values
--   4. Execute each section sequentially
--   5. Document findings in the RESULTS section at the bottom
-- =============================================================================

-- =============================================================================
-- CONFIGURATION - Update these values for your environment
-- =============================================================================

-- Target schema: <<YOUR_SCHEMA>>
-- Target MLV:    <<YOUR_MLV_NAME>>
-- Source tables:  <<SOURCE_TABLE_1>>, <<SOURCE_TABLE_2>>

-- =============================================================================
-- STEP 1: Verify MLV exists and review definition
-- =============================================================================

SHOW MATERIALIZED LAKE VIEWS IN <<YOUR_SCHEMA>>;

SHOW CREATE MATERIALIZED LAKE VIEW <<YOUR_SCHEMA>>.<<YOUR_MLV_NAME>>;

-- FINDINGS:
-- [ ] MLV exists in target schema
-- [ ] Definition uses only supported SQL constructs
-- [ ] PARTITIONED BY is present (for large datasets)
-- [ ] CDF TBLPROPERTIES is set on the MLV
-- [ ] Constraints use DROP action (not FAIL)

-- =============================================================================
-- STEP 2: Validate source tables
-- =============================================================================

-- Check CDF status
DESCRIBE DETAIL <<YOUR_SCHEMA>>.<<SOURCE_TABLE_1>>;
DESCRIBE DETAIL <<YOUR_SCHEMA>>.<<SOURCE_TABLE_2>>;

-- Check recent operations (append-only vs updates/deletes)
DESCRIBE HISTORY <<YOUR_SCHEMA>>.<<SOURCE_TABLE_1>> LIMIT 10;
DESCRIBE HISTORY <<YOUR_SCHEMA>>.<<SOURCE_TABLE_2>> LIMIT 10;

-- Check row counts
SELECT '<<SOURCE_TABLE_1>>' as table_name, COUNT(*) as row_count 
FROM <<YOUR_SCHEMA>>.<<SOURCE_TABLE_1>>
UNION ALL
SELECT '<<SOURCE_TABLE_2>>', COUNT(*) 
FROM <<YOUR_SCHEMA>>.<<SOURCE_TABLE_2>>;

-- FINDINGS:
-- [ ] CDF enabled on all source tables
-- [ ] Source data is append-only (no UPDATE/DELETE/MERGE in history)
-- [ ] Source table sizes are appropriate for current environment

-- =============================================================================
-- STEP 3: Check MLV output table health
-- =============================================================================

DESCRIBE DETAIL <<YOUR_SCHEMA>>.<<YOUR_MLV_NAME>>;

SELECT COUNT(*) as mlv_row_count FROM <<YOUR_SCHEMA>>.<<YOUR_MLV_NAME>>;

-- Check for small files (too many small files degrades performance)
-- Review numFiles from DESCRIBE DETAIL output
-- If numFiles is very high relative to sizeInBytes, consider OPTIMIZE

-- FINDINGS:
-- [ ] MLV output table exists and has data
-- [ ] File count is reasonable (not excessive small files)
-- [ ] Table size aligns with expected output volume

-- =============================================================================
-- STEP 4: Enable CDF if missing (uncomment to execute)
-- =============================================================================

-- ALTER TABLE <<YOUR_SCHEMA>>.<<SOURCE_TABLE_1>> 
--   SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- ALTER TABLE <<YOUR_SCHEMA>>.<<SOURCE_TABLE_2>> 
--   SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- =============================================================================
-- STEP 5: Test refresh
-- =============================================================================

-- Option A: Force full refresh to verify the MLV definition works
-- REFRESH MATERIALIZED LAKE VIEW <<YOUR_SCHEMA>>.<<YOUR_MLV_NAME>> FULL;

-- Option B: Drop and recreate with optimizations (if needed)
-- DROP MATERIALIZED LAKE VIEW <<YOUR_SCHEMA>>.<<YOUR_MLV_NAME>>;
-- CREATE OR REPLACE MATERIALIZED LAKE VIEW <<YOUR_SCHEMA>>.<<YOUR_MLV_NAME>>
-- TBLPROPERTIES (delta.enableChangeDataFeed=true)
-- PARTITIONED BY (<<PARTITION_COLUMN>>)
-- AS
-- SELECT ... FROM ...;

-- =============================================================================
-- STEP 6: Verify refresh result
-- =============================================================================

-- After refresh completes, check the output
SELECT COUNT(*) as post_refresh_count FROM <<YOUR_SCHEMA>>.<<YOUR_MLV_NAME>>;

-- Compare with expected count from source
-- SELECT COUNT(*) FROM <<YOUR_SCHEMA>>.<<SOURCE_TABLE_1>> 
-- INNER JOIN <<YOUR_SCHEMA>>.<<SOURCE_TABLE_2>> ON ...;

-- =============================================================================
-- RESULTS SUMMARY
-- =============================================================================
-- Date:           <<DATE>>
-- MLV Name:       <<YOUR_SCHEMA>>.<<YOUR_MLV_NAME>>
-- Issue:          <<DESCRIBE THE ISSUE>>
--
-- Findings:
--   CDF Status:         [ ] Enabled / [ ] Missing
--   Source Pattern:      [ ] Append-only / [ ] Has updates/deletes
--   SQL Constructs:      [ ] All supported / [ ] Has unsupported
--   Constraints:         [ ] DROP action / [ ] FAIL action / [ ] None
--   Partition Strategy:  [ ] Partitioned / [ ] Not partitioned
--   Environment:         [ ] Default / [ ] Custom: <<ENV_NAME>>
--
-- Resolution Applied:   <<DESCRIBE WHAT WAS CHANGED>>
-- Refresh Result:       [ ] Success / [ ] Failed (see Spark logs)
-- =============================================================================
