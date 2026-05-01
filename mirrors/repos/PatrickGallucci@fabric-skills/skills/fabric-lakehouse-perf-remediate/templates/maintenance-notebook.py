# Fabric Lakehouse Table Maintenance Notebook
# ============================================
# Template for comprehensive Delta table maintenance in Microsoft Fabric.
# Performs OPTIMIZE (with V-Order and optional Z-Order) and VACUUM on specified tables.
#
# Usage:
#   1. Attach this notebook to a Fabric Lakehouse
#   2. Configure the TABLES list below with your table names and settings
#   3. Run all cells to execute maintenance
#
# Schedule this notebook via Fabric Pipelines for automated maintenance.

# %% [markdown]
# ## Configuration

# %%
# === CONFIGURE THESE VALUES ===

# Tables to maintain. Each entry is a dict with:
#   - name: Full table name (schema.table or just table)
#   - vorder: Apply V-Order (True/False)
#   - zorder_cols: List of columns for Z-Order (empty list = no Z-Order)
#   - vacuum: Run VACUUM (True/False)
#   - vacuum_hours: Retention hours for VACUUM (default 169 = 7 days + 1 hour)
#   - partition_filter: Optional WHERE clause to limit OPTIMIZE scope (None = full table)

TABLES = [
    {
        "name": "sales_fact",
        "vorder": True,
        "zorder_cols": ["customer_id"],
        "vacuum": True,
        "vacuum_hours": 169,
        "partition_filter": None,
    },
    {
        "name": "dim_customer",
        "vorder": True,
        "zorder_cols": [],
        "vacuum": True,
        "vacuum_hours": 169,
        "partition_filter": None,
    },
    {
        "name": "dim_product",
        "vorder": True,
        "zorder_cols": [],
        "vacuum": True,
        "vacuum_hours": 169,
        "partition_filter": None,
    },
]

# Set to True to only print commands without executing (dry run)
DRY_RUN = False

# %% [markdown]
# ## Execute Maintenance

# %%
from datetime import datetime


def build_optimize_command(table_config):
    """Build the OPTIMIZE SQL command from configuration."""
    name = table_config["name"]
    vorder = table_config.get("vorder", True)
    zorder_cols = table_config.get("zorder_cols", [])
    partition_filter = table_config.get("partition_filter")

    cmd = f"OPTIMIZE {name}"

    if partition_filter:
        cmd += f" WHERE {partition_filter}"

    if zorder_cols:
        cols = ", ".join(zorder_cols)
        cmd += f" ZORDER BY ({cols})"

    if vorder:
        cmd += " VORDER"

    return cmd


def build_vacuum_command(table_config):
    """Build the VACUUM SQL command from configuration."""
    name = table_config["name"]
    hours = table_config.get("vacuum_hours", 169)
    return f"VACUUM {name} RETAIN {hours} HOURS"


def run_maintenance(table_config):
    """Execute maintenance for a single table."""
    name = table_config["name"]
    print(f"\n{'='*60}")
    print(f"Table: {name}")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'='*60}")

    # OPTIMIZE
    optimize_cmd = build_optimize_command(table_config)
    print(f"\n  OPTIMIZE command: {optimize_cmd}")

    if not DRY_RUN:
        try:
            start = datetime.now()
            spark.sql(optimize_cmd)
            elapsed = (datetime.now() - start).total_seconds()
            print(f"  OPTIMIZE completed in {elapsed:.1f} seconds.")
        except Exception as e:
            print(f"  OPTIMIZE FAILED: {e}")
    else:
        print("  [DRY RUN] Skipping execution.")

    # VACUUM
    if table_config.get("vacuum", False):
        vacuum_cmd = build_vacuum_command(table_config)
        print(f"\n  VACUUM command: {vacuum_cmd}")

        if not DRY_RUN:
            try:
                start = datetime.now()
                spark.sql(vacuum_cmd)
                elapsed = (datetime.now() - start).total_seconds()
                print(f"  VACUUM completed in {elapsed:.1f} seconds.")
            except Exception as e:
                print(f"  VACUUM FAILED: {e}")
        else:
            print("  [DRY RUN] Skipping execution.")

    print(f"\n  Finished: {datetime.now().isoformat()}")


# %%
# Run maintenance on all configured tables
print("=" * 60)
print("FABRIC LAKEHOUSE TABLE MAINTENANCE")
print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
print(f"Tables: {len(TABLES)}")
print(f"Started: {datetime.now().isoformat()}")
print("=" * 60)

for table in TABLES:
    run_maintenance(table)

print(f"\n{'='*60}")
print(f"ALL MAINTENANCE COMPLETE: {datetime.now().isoformat()}")
print(f"{'='*60}")
