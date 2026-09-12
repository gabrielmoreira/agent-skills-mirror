---
name: linqpad-duckdb
description: "Reproducible LINQPad and DuckDB.NET analysis of local or Azure-hosted Delta and Parquet data, including extensions, authentication, schema mapping, pruning, and scan-cost safety."
---

Use this skill when exploring Parquet or Delta data with DuckDB.NET from
LINQPad. Start locally with synthetic data, then opt into cloud access only
after the native engine, schema, and query shape are understood.

# Pinned baseline

The verified local fixture uses:

- .NET SDK `10.0.401`, target framework `net10.0`
- `DuckDB.NET.Data.Full` `1.5.5`
- native DuckDB `v1.5.5`, included by that Full package
- Windows AMD64; DuckDB's current Delta docs also list Linux AMD64/ARM64 and
  macOS Intel/Apple Silicon

The Full package is important: `DuckDB.NET.Data` is managed-only and requires a
separately supplied compatible native library. DuckDB.NET 1.5.5's project
release notes and `DuckDbArtifactRoot` pin the bundled native artifacts to
DuckDB v1.5.5. Keep the ADO.NET package, native library, and downloaded
extensions on the same DuckDB version. Re-test after changing any of them.

# LINQPad setup

1. Create a query and intentionally select **C# Program** language mode.
2. Press **F4** (Query Properties), choose **Add NuGet**, and add the
   project-selected package `DuckDB.NET.Data.Full` at exactly `1.5.5`.
   LINQPad's package manager is available in Developer/Premium editions; saved
   queries with NuGet references can restore in the free edition.
3. Add `DuckDB.NET.Data` under **Additional Namespace Imports**.
4. Use an in-memory database for analysis unless persistence is required:

```csharp
void Main()
{
    using var db = new DuckDBConnection("Data Source=:memory:");
    db.Open();

    using var command = db.CreateCommand();
    command.CommandText = "SELECT version() AS duckdb_version";
    command.ExecuteScalar().Dump("Native DuckDB version");
}
```

This is LINQPad syntax, but the repository fixture is a console harness. Do not
claim LINQPad execution unless the query was actually run in LINQPad.

# Local-first synthetic workflow

The included `fixture` creates a unique child beneath an existing, user-owned
parent directory. It writes:

- Parquet with physical columns `col-aaaa` and `col-bbbb`
- a minimal Delta log whose logical columns are `id` and `code`
- Delta name-column-mapping metadata connecting those schemas

It verifies projection and filtering against raw Parquet. The runtime
no-network mode stops there. NuGet restore/build can still require network
access; copy `fixture` into a working directory rather than building inside an
installed plugin, then build once:

```powershell
dotnet build .\fixture\LinqPadDuckDbFixture.csproj -c Release "-bl:build-{}.binlog"
```

Run the built fixture without restoring packages:

```powershell
dotnet run --project .\fixture\LinqPadDuckDbFixture.csproj -c Release --no-build --no-restore -- `
  C:\path\to\an\existing\user-owned\scratch-parent --skip-delta
```

Omit `--skip-delta` to try a real local `delta_scan`:

```powershell
dotnet run --project .\fixture\LinqPadDuckDbFixture.csproj -c Release --no-build --no-restore -- `
  C:\path\to\an\existing\user-owned\scratch-parent
```

`INSTALL delta` may download a version/platform-specific extension from
DuckDB's public extension repository; it does not access Azure. The fixture
redirects extension storage into its unique output child.

The pinned Windows AMD64 fixture has exercised both physical Parquet reads and
local Delta logical-column reads. This is not evidence of Azure authentication,
remote pruning, or execution inside LINQPad. Extension availability and package
restore still depend on the environment.

Keep the printed output directory for inspection. Do not use clean/overwrite
operations against an existing arbitrary directory.

# Delta semantics and column mapping

A Delta table is not merely a Parquet glob. Its transaction log selects active
files and supplies the current logical schema, protocol features, deletion
vectors, partitions, and time-travel state. Use:

```sql
SELECT id, code
FROM delta_scan('C:/scratch/my-delta-table')
WHERE id >= 2
ORDER BY id;
```

Use a native absolute path for local Windows tables. With the pinned Windows
combination, a `file:///C:/...` table URI can make the scan try to open an
invalid `/C:/...` Parquet path. The executable fixture uses a normalized native
path instead; POSIX examples in upstream docs commonly use `file:///...`.

Do not replace that with `read_parquet('.../**/*.parquet')` when transaction
semantics matter. A raw Parquet scan can include removed files, miss deletion
vectors, expose physical names, and ignore Delta schema evolution.

With Delta column mapping, the log can advertise logical names such as `id` and
`code` while files store names such as `col-aaaa` and `col-bbbb`. Query logical
names through `delta_scan`; use `parquet_schema` only to diagnose physical
files. Column mapping upgrades the Delta read protocol, so compatibility is
conditional on the table's protocol/features and the exact DuckDB Delta
extension. An unsupported protocol or mapping error is a hard compatibility
failure: record the native/extension version and table protocol, reduce to a
synthetic reproducer, and upgrade/test. Do not silently fall back to raw
Parquet and claim equivalent results.

# Azure access (nonexecuted template)

Prerequisites:

- DuckDB's `azure` and `delta` extensions must exist for the exact native
  version and platform.
- The selected identity must already be available to the native Azure SDK and
  have data-plane permission such as **Storage Blob Data Reader**.
- Network, DNS, TLS trust, and storage firewall/private-endpoint routing must
  allow the intended account.
- Use only placeholders in source. Never paste tokens, connection strings, or
  client secrets into queries, logs, dumps, or screenshots.

The DuckDB `azure` extension owns its native SDK credential chain. A C#
`DefaultAzureCredential` instance is not passed through DuckDB.NET. Prefer an
explicit chain so local behavior is understandable. The following is a
template only; do not execute it during local validation:

```sql
INSTALL azure;
LOAD azure;
INSTALL delta;
LOAD delta;

CREATE SECRET azure_analysis (
    TYPE azure,
    PROVIDER credential_chain,
    CHAIN 'cli;env',
    ACCOUNT_NAME '<storage-account>'
);

SELECT event_date, category
FROM delta_scan(
  'abfss://<storage-account>.dfs.core.windows.net/<container>/<delta-table-path>'
)
WHERE event_date >= DATE '2026-01-01'
  AND event_date <  DATE '2026-02-01'
LIMIT 20;
```

In DuckDB's fully qualified ABFSS form, the storage account is in the DFS host
and the container (also called filesystem) is the first path segment. The
credential providers are attempted in the declared order. Use one unambiguous
credential source in production. The token is acquired at query time, not when
`CREATE SECRET` runs.

Delta also uses `delta-kernel-rs` and `object_store` for some network operations;
their credential inclusion/order can differ from the Azure extension's SDK.
Do not assume `CHAIN 'cli;env'` determines every Delta credential decision.
For reproducible cloud analysis, select one supported credential source and
remove ambiguity in the process environment, then verify the intended identity
without recording its credentials.

For an authentication failure:

1. Confirm `SELECT version()` and extension availability before diagnosing
   identity.
2. Distinguish missing/unloadable extension or TLS/download errors from
   `401` authentication and `403` authorization/firewall failures.
3. Check the placeholder-free account name, credential provider availability,
   tenant context, and data-plane role outside captured output.
4. Keep diagnostics sanitized; never enable verbose logs in a recording that
   might capture tokens, signed URLs, headers, or connection strings.

# Scan cost and query planning

`LIMIT 20` limits returned rows. It does **not** promise only 20 rows, one file,
or a bounded number of bytes will be read over the network. Metadata discovery,
Delta-log evaluation, file listing, footer reads, and scan work can occur before
the limit is satisfied.

Reduce likely work with all of the following:

- project only required columns; Parquet projection pushdown can avoid reading
  other columns
- filter on Delta partition columns and columns with useful file/row-group
  statistics
- use selective predicates whose types match the stored schema
- inspect `EXPLAIN` and, for Delta, `delta_list_files(...)` where supported

These are conditional optimizations, not billing guarantees. Projection
pushdown depends on the query. Parquet row-group skipping depends on zonemaps
and statistics. Delta file skipping depends on partition/statistics metadata,
supported expressions, and extension behavior. Remote listing and metadata
requests can still be substantial.

Use `EXPLAIN <query>` for a plan without executing the query; binding a remote
table may still read metadata or contact storage. `EXPLAIN ANALYZE`
is not a dry run: DuckDB executes the query and reports actual cardinalities and
timings. Treat it as real data access and real network cost.

# Failure reporting

Report each layer independently:

- restore: package version and any visible `NU1900`/TLS audit warning; do not
  disable NuGet audit, TLS validation, or all warnings
- native: `SELECT version()` and runtime identifier
- extension: install/load success or the exact availability/platform error
- Parquet: physical schema and local selection result
- Delta: logical schema, protocol/mapping result, or exact unsupported error
- Azure/LINQPad: explicitly state when these paths were not executed

# Public references

- [DuckDB Azure extension](https://duckdb.org/docs/current/core_extensions/azure)
- [DuckDB Delta extension](https://duckdb.org/docs/current/core_extensions/delta)
- [DuckDB Parquet reads and pushdown](https://duckdb.org/docs/current/data/parquet/overview)
- [DuckDB profiling](https://duckdb.org/docs/current/sql/statements/profiling)
- [DuckDB.NET packages](https://duckdb.net/docs/getting-started.html)
- [DuckDB.NET 1.5.5 native artifact pin](https://github.com/Giorgi/DuckDB.NET/blob/1.5.5/DuckDB.NET.Bindings/Bindings.csproj)
- [Delta protocol compatibility](https://docs.delta.io/versioning/)
- [Delta column mapping](https://docs.delta.io/delta-column-mapping/)
- [LINQPad FAQ: references and NuGet](https://www.linqpad.net/FAQ.aspx)
