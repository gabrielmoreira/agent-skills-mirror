# Fabric Lakehouse Performance Diagnostic Notebook
# =================================================
# Template for diagnosing Delta table performance issues in Microsoft Fabric.
# Analyzes table health, Spark configuration, file layout, and provides
# actionable recommendations.
#
# Usage:
#   1. Attach this notebook to a Fabric Lakehouse
#   2. Set TABLE_NAME to the table you want to diagnose
#   3. Run all cells to generate a diagnostic report

# %% [markdown]
# ## Configuration

# %%
# === CONFIGURE THIS VALUE ===
TABLE_NAME = "my_table"  # Change to your table name (e.g., "schema.table" or "table")

# %% [markdown]
# ## Step 1: Spark Configuration Audit

# %%
print("=" * 60)
print("SPARK CONFIGURATION AUDIT")
print("=" * 60)

configs = [
    ("spark.fabric.resourceProfile", "Resource profile"),
    ("spark.sql.parquet.vorder.default", "V-Order default"),
    ("spark.databricks.delta.optimizeWrite.enabled", "Optimize Write"),
    ("spark.databricks.delta.optimizeWrite.binSize", "Optimize Write bin size"),
    ("spark.sql.shuffle.partitions", "Shuffle partitions"),
    ("spark.sql.autoBroadcastJoinThreshold", "Auto broadcast threshold"),
    ("spark.sql.files.maxPartitionBytes", "Max partition bytes"),
    ("spark.ms.autotune.enabled", "Autotune enabled"),
    ("spark.microsoft.delta.merge.lowShuffle.enabled", "Low shuffle merge"),
    ("spark.databricks.delta.retentionDurationCheck.enabled", "Retention check"),
]

print(f"\n{'Setting':<55} {'Value':<25} {'Label'}")
print("-" * 100)

for config_key, label in configs:
    try:
        val = spark.conf.get(config_key)
    except Exception:
        val = "[not set]"
    print(f"{config_key:<55} {str(val):<25} {label}")

# %% [markdown]
# ## Step 2: Delta Table Detail

# %%
from delta.tables import DeltaTable

print("=" * 60)
print(f"DELTA TABLE DETAIL: {TABLE_NAME}")
print("=" * 60)

try:
    dt = DeltaTable.forName(spark, TABLE_NAME)
    detail_df = dt.detail()
    detail_df.show(truncate=False)

    # Extract key metrics
    detail_row = detail_df.collect()[0]
    num_files = detail_row["numFiles"]
    size_bytes = detail_row["sizeInBytes"]
    size_mb = size_bytes / (1024 * 1024)
    size_gb = size_bytes / (1024 * 1024 * 1024)
    partition_cols = detail_row["partitionColumns"]

    avg_file_size_mb = size_mb / num_files if num_files > 0 else 0

    print(f"\nKey Metrics:")
    print(f"  Total files:        {num_files:,}")
    print(f"  Total size:         {size_gb:.2f} GB ({size_mb:.0f} MB)")
    print(f"  Avg file size:      {avg_file_size_mb:.1f} MB")
    print(f"  Partition columns:  {partition_cols if partition_cols else 'None'}")
except Exception as e:
    print(f"ERROR: Could not read table detail: {e}")
    num_files = None
    avg_file_size_mb = None

# %% [markdown]
# ## Step 3: Table History (Recent Operations)

# %%
print("=" * 60)
print(f"TABLE HISTORY (Last 20 Operations): {TABLE_NAME}")
print("=" * 60)

try:
    history_df = spark.sql(f"DESCRIBE HISTORY {TABLE_NAME} LIMIT 20")
    history_df.select(
        "version", "timestamp", "operation", "operationParameters"
    ).show(truncate=50)

    # Check for recent OPTIMIZE
    optimize_ops = [
        r for r in history_df.collect() if "OPTIMIZE" in str(r["operation"]).upper()
    ]
    if optimize_ops:
        last_optimize = optimize_ops[0]["timestamp"]
        print(f"\nLast OPTIMIZE: {last_optimize}")
    else:
        print("\nWARNING: No OPTIMIZE operations found in recent history!")
except Exception as e:
    print(f"ERROR: Could not read table history: {e}")

# %% [markdown]
# ## Step 4: Table Properties

# %%
print("=" * 60)
print(f"TABLE PROPERTIES: {TABLE_NAME}")
print("=" * 60)

try:
    props_df = spark.sql(f"SHOW TBLPROPERTIES {TABLE_NAME}")
    props_df.show(truncate=False)
except Exception as e:
    print(f"ERROR: Could not read table properties: {e}")

# %% [markdown]
# ## Step 5: Diagnostic Assessment

# %%
print("=" * 60)
print("DIAGNOSTIC ASSESSMENT & RECOMMENDATIONS")
print("=" * 60)

recommendations = []

if num_files is not None:
    # File count assessment
    if num_files > 10000:
        recommendations.append(
            "CRITICAL: Table has over 10,000 files. Run OPTIMIZE immediately to "
            "consolidate small files. This impacts all Fabric engines."
        )
    elif num_files > 1000:
        recommendations.append(
            "WARNING: Table has over 1,000 files. Consider running OPTIMIZE "
            "to improve read performance."
        )

    # File size assessment
    if avg_file_size_mb is not None:
        if avg_file_size_mb < 10:
            recommendations.append(
                f"CRITICAL: Average file size is only {avg_file_size_mb:.1f} MB. "
                "Target 128 MB - 1 GB per file. Run OPTIMIZE VORDER."
            )
        elif avg_file_size_mb < 128:
            recommendations.append(
                f"WARNING: Average file size is {avg_file_size_mb:.1f} MB. "
                "Run OPTIMIZE to consolidate into larger files (target 128 MB+)."
            )
        elif avg_file_size_mb > 2048:
            recommendations.append(
                f"INFO: Average file size is {avg_file_size_mb:.1f} MB (over 2 GB). "
                "Very large files may limit parallelism for some query patterns."
            )
        else:
            recommendations.append(
                f"OK: Average file size ({avg_file_size_mb:.1f} MB) is in a healthy range."
            )

# V-Order assessment
try:
    vorder_setting = spark.conf.get("spark.sql.parquet.vorder.default")
    if vorder_setting.lower() == "false":
        recommendations.append(
            "INFO: V-Order is disabled at the session level. If this table serves "
            "Power BI or SQL analytics, enable V-Order or run OPTIMIZE table VORDER."
        )
except Exception:
    recommendations.append(
        "INFO: V-Order session setting not explicitly configured. "
        "Check table properties for delta.parquet.vorder.enabled."
    )

# Autotune assessment
try:
    autotune = spark.conf.get("spark.ms.autotune.enabled")
    if autotune.lower() != "true":
        recommendations.append(
            "INFO: Autotune is not enabled. For repetitive Spark SQL queries, "
            "enable with: SET spark.ms.autotune.enabled=TRUE"
        )
except Exception:
    recommendations.append(
        "INFO: Autotune not configured. Consider enabling for Spark SQL workloads."
    )

# Resource profile assessment
try:
    profile = spark.conf.get("spark.fabric.resourceProfile")
    recommendations.append(
        f"INFO: Current resource profile is '{profile}'. "
        "Verify this matches your workload pattern (read-heavy vs write-heavy)."
    )
except Exception:
    recommendations.append(
        "INFO: No resource profile explicitly set. "
        "New workspaces default to writeHeavy."
    )

# Print recommendations
if recommendations:
    for i, rec in enumerate(recommendations, 1):
        severity = rec.split(":")[0]
        color_map = {"CRITICAL": "31", "WARNING": "33", "OK": "32", "INFO": "36"}
        color = color_map.get(severity, "0")
        print(f"\n{i}. {rec}")
else:
    print("\nNo issues detected. Table appears healthy.")

# %% [markdown]
# ## Step 6: Quick Fix Commands
#
# Based on the assessment above, run the appropriate commands below.

# %%
# Uncomment and run the commands you need:

# --- OPTIMIZE with V-Order ---
# spark.sql(f"OPTIMIZE {TABLE_NAME} VORDER")

# --- OPTIMIZE with Z-Order and V-Order ---
# spark.sql(f"OPTIMIZE {TABLE_NAME} ZORDER BY (column_name) VORDER")

# --- OPTIMIZE specific partitions ---
# spark.sql(f"OPTIMIZE {TABLE_NAME} WHERE date_key >= '2025-01-01' VORDER")

# --- VACUUM with default retention (7 days) ---
# spark.sql(f"VACUUM {TABLE_NAME}")

# --- Enable V-Order for session ---
# spark.conf.set('spark.sql.parquet.vorder.default', 'true')

# --- Enable Autotune ---
# spark.sql("SET spark.ms.autotune.enabled=TRUE")

# --- Switch resource profile ---
# spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")

# --- Set optimal file sizes for SQL analytics endpoint ---
# spark.conf.set("spark.sql.files.maxRecordsPerFile", 2000000)
