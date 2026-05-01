---
name: database-specialist
description: "Data-pipeline implementation specialist — change-tracker/data-loader configurations, stored procedure integration, MongoDB repository code, DI registration, and Squadron-based database tests. Triggers: SqlChangeTracker, SqlDataLoader, SqlExecutionContext, IMongoCollection, MongoConventions, DomainEntityRepository, SourceRepository, Pipeline_Database, Pipeline_Connections, Squadron, new data pipeline entity setup."
---

# Database Specialist — Data Pipeline

Implement and troubleshoot data-pipeline code: change-tracker jobs, data-loader configurations, SQL stored procedure integration, MongoDB repository patterns, and database tests.

> **Scope**: data pipeline implementation only.
> - For **MongoDB analysis, indexing strategy, and query optimization** → delegate to `MongoDB Expert` agent.
> - For **SQL Server query optimization, execution plans, and schema design** → delegate to `MS-SQL Expert` agent.
> - For general backend patterns (GraphQL, MassTransit, Startup) → `backend-developer` skill.
> - For test conventions → `tests.instructions.md`.

## Architecture Overview

The data pipeline is a system that synchronizes source data (MS SQL) into a MongoDB target database:

```
SQL Server (Stored Procedures)
  → SqlChangeTracker (Quartz job, Cron)
    → Extract keys
      → MongoDB (store keys, transactions)
        → DomainProcessor (transformation)
          → MongoDB (store snapshots, hashes)
```

### Relevant Paths in the Repo

| Area | Path |
|---|---|
| SQL Client & Execution | `src/DataAccess/` |
| SQL Configurations | `src/Abstractions/Configuration/` |
| Change Tracker & Loader | `src/Core/ChangeTracker/`, `src/Core/Loader/` |
| MongoDB Repositories | `src/Repository/` |
| DI Registration | `src/Core/DataPipelineCoreCollectionExtensions.cs` |
| Domain Configuration | `src/Repository/ConfigureDomainSettings.cs` |
| Tests | `test/` |

## MS SQL Server

### SqlClient — Core SQL Execution

`SqlClient.cs` in `src/DataAccess/` uses `Microsoft.Data.SqlClient` (not `System.Data.SqlClient`). Key properties:

- `CommandType.StoredProcedure` — exclusively stored procedures, no inline SQL
- `CommandTimeout` = 10 minutes
- Polly `WaitAndRetry(3, retryAttempt => TimeSpan.FromSeconds(5))` for transient errors
- Streaming via `IAsyncEnumerable<SqlTable>` with optional batching

```csharp
// Simplified pattern from SqlClient.cs
await using SqlConnection connection = new(context.ConnectionString);
await connection.OpenAsync(cancellationToken);

await using SqlCommand command = new(context.StoredProcedure, connection)
{
    CommandType = CommandType.StoredProcedure,
    CommandTimeout = (int)TimeSpan.FromMinutes(10).TotalSeconds
};

// Add parameters
foreach (SqlParameter parameter in context.Parameters)
{
    command.Parameters.Add(parameter);
}

await using SqlDataReader reader = await command.ExecuteReaderAsync(cancellationToken);
```

### SqlExecutionContext

Internal context object for SQL calls:

```csharp
internal class SqlExecutionContext
{
    public string ConnectionString { get; set; }
    public string StoredProcedure { get; set; }
    public IList<SqlParameter> Parameters { get; set; }
    public bool UseBatching { get; set; }
    public int BatchSize { get; set; }
}
```

### Two SQL Client Types

| Client | Implements | Batching | Purpose |
|---|---|---|---|
| `SqlChangeTrackerClient` | `ISqlChangeTrackerClient` | Yes | Periodic change detection via Cron |
| `SqlDataLoaderClient` | `ISqlDataLoaderClient` | No | Full entity data loading |

Both create a `SqlExecutionContext` from their respective configuration.

### SQL Configurations

#### SqlChangeTrackerConfiguration

Implements `IChangeTrackerConfiguration`:

```csharp
public class SqlChangeTrackerConfiguration : IChangeTrackerConfiguration
{
    public string StoredProcedure { get; set; }
    public string QueryParameterName { get; set; }
    public string QueryParameterType { get; set; }
    public long InitialTransactionId { get; set; }
    public string ResultPrimaryKeyColumnName { get; set; }
    public string ResultTransactionIdColumnName { get; set; }
    public string ConnectionString { get; set; }
    public string CronSchedule { get; set; } = "0 {0} * ? * * *";
    public EntityAction EntityAction { get; set; }

    public void Resolve(ConnectionsOptions options)
    {
        // Resolves ConnectionString via ConnectionsOptions
    }
}
```

- `CronSchedule` default: `"0 {0} * ? * * *"` — placeholder `{0}` is replaced with minute value
- `Resolve(ConnectionsOptions)` — resolve connection string from named configuration

#### SqlLoaderConfiguration

Implements `ILoaderConfiguration`:

```csharp
public class SqlLoaderConfiguration : ILoaderConfiguration
{
    public string StoredProcedure { get; set; }
    public string ResultPrimaryKeyColumnName { get; set; }
    public string QueryParameterName { get; set; }
    public string QueryParameterType { get; set; }
    public string QueryParameterTypeName { get; set; }  // For TVP support
    public string ConnectionString { get; set; }

    public void Resolve(ConnectionsOptions options) { /* ... */ }
}
```

### Connection Resolution

Connection strings are **not** stored directly in configurations but resolved via `ConnectionsOptions`:

```
Config section: Pipeline_Connections
  → ConnectionsOptions (name/value pairs)
    → Loader/Tracker call Resolve(ConnectionsOptions)
```

## Change Tracker Pipeline

### SqlChangeTracker

Registers Quartz jobs with Cron scheduling:

```csharp
// Simplified pattern
JobBuilder.Create<SqlChangeTrackerJob>()
    .WithIdentity(jobKey)
    .Build();

TriggerBuilder.Create()
    .WithCronSchedule(cronExpression)
    .Build();
```

### SqlChangeTrackerJob

Attributes: `[DisallowConcurrentExecution, PersistJobDataAfterExecution]`

Extends `TrackableJob`. Pipeline flow:

1. Load domain configuration
2. Fetch current transaction ID from MongoDB
3. Execute stored procedure with transaction ID
4. Extract changed keys
5. Store keys in MongoDB (`{entity}_keys`)
6. Store new transaction ID in MongoDB (`{entity}_transactions`)
7. Trigger DomainProcessor

OpenTelemetry tracing with `Activity` and `datapipeline.changetracker.*` tags is mandatory.

### Domain Configuration

`ConfigureDomainSettings.cs` uses the `_t` discriminator field for polymorphic type resolution:

```
DomainSettings:Configurations → Array of configurations
  → _t field determines type:
    - SqlLoaderConfiguration
    - RestLoaderConfiguration
    - GraphQLLoaderConfiguration
    - SqlChangeTrackerConfiguration
    - ServiceBusChangeTrackerConfiguration
    - FieldKeyServiceBusChangeTrackerConfiguration
```

### Configuration Sections

| Section | Purpose |
|---|---|
| `Pipeline_Connections` | Named connection strings (name/value) |
| `Pipeline_Database` | MongoDB ConnectionString + DatabaseName |
| `Pipeline_Messaging` | Service Bus configuration |
| `Pipeline_Audit` | Audit settings |
| `DomainSettings:Configurations` | Loader and tracker definitions |
| `DomainSettings:HostSettings` | Host-specific settings |

## MongoDB Atlas

### MongoConventions

**Every repository** must call `MongoConventions.Init()` in its static constructor:

```csharp
public class MyRepository
{
    static MyRepository()
    {
        MongoConventions.Init();
    }
}
```

### Collection Naming Convention

Collections are dynamically named by entity type:

| Collection | Pattern | Purpose |
|---|---|---|
| `{EntityType.Name}_snapshots` | Typed (`Snapshot`) | Domain entity snapshots |
| `{EntityType.Name}_keys` | `BsonDocument` | Source entity keys queue |
| `{EntityType.Name}_transactions` | `BsonDocument` | Change tracker transactions |
| `{EntityType.Name}_audit_keys` | Typed (`PipelineAuditEntry`) | Pipeline audit entries |
| `{EntityType.Name}_hashes` | Legacy | Hash storage (legacy) |
| `__domains` | Typed (`DomainConfiguration`) | Domain configurations |
| `__settings` | Typed (`HostSettings`) | Host settings |

System collections (`__domains`, `__settings`) use double underscore prefix.

### SourceRepository — BsonDocument-Based

Works with `IMongoCollection<BsonDocument>` for `_transactions` and `_keys`:

```csharp
// Index creation
CreateIndexModel<BsonDocument> index = new(
    Builders<BsonDocument>.IndexKeys
        .Ascending("SourceIdentifier")
        .Ascending("Disabled")
        .Ascending("TransactionId"),
    new CreateIndexOptions { Background = true });

// Bulk delete operations
List<DeleteOneModel<BsonDocument>> deletes = keys
    .Select(k => new DeleteOneModel<BsonDocument>(
        Builders<BsonDocument>.Filter.Eq("_id", k)))
    .ToList();

await collection.BulkWriteAsync(deletes, new BulkWriteOptions { IsOrdered = false });

// Deserialization
BsonSerializer.Deserialize<T>(document);
```

### DomainEntityRepository — Typed + BsonDocument

Manages `_snapshots` and `_hashes` with extensive index management:

```csharp
// Standard indexes
CreateIndexModel<Snapshot>[] indexes = new[]
{
    // Key index
    new CreateIndexModel<Snapshot>(
        Builders<Snapshot>.IndexKeys.Ascending(x => x.Key)),
    // Hash index
    new CreateIndexModel<Snapshot>(
        Builders<Snapshot>.IndexKeys.Ascending(x => x.Hash)),
    // Unique Key+Version
    new CreateIndexModel<Snapshot>(
        Builders<Snapshot>.IndexKeys
            .Ascending(x => x.Key)
            .Ascending(x => x.Version),
        new CreateIndexOptions { Unique = true })
};
```

Domain-specific indexes on `Entity.*` fields are additionally created.

#### Bulk Upsert Pattern

```csharp
List<ReplaceOneModel<Snapshot>> updates = snapshots
    .Select(s => new ReplaceOneModel<Snapshot>(
        Builders<Snapshot>.Filter.Eq(x => x.Key, s.Key),
        s) { IsUpsert = true })
    .ToList();

await collection.BulkWriteAsync(updates);
```

#### IAsyncCursor for Streaming

For large data volumes:

```csharp
using IAsyncCursor<BsonDocument> cursor = await collection
    .FindAsync(filter, new FindOptions<BsonDocument> { BatchSize = 1000 });

while (await cursor.MoveNextAsync(cancellationToken))
{
    foreach (BsonDocument document in cursor.Current)
    {
        // Processing
    }
}
```

> **Compatibility note**: Avoid `$literal` syntax — not supported on MongoDB Server < 4.4 with MongoDB.Driver > 3.x.

### ConfigurationRepository — Caching

Uses `IMemoryCache` with 1-day expiration:

```csharp
_memoryCache.GetOrCreateAsync(cacheKey, entry =>
{
    entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromDays(1);
    return LoadFromMongoDB();
});
```

Unique index on domain name ensures uniqueness.

### AuditRepository

`IMongoCollection<PipelineAuditEntry>` for `_audit_keys` with compound index:

```csharp
Builders<PipelineAuditEntry>.IndexKeys
    .Ascending(x => x.Attempt)
    .Ascending(x => x.Key)
```

## DI Registration

### Core Services

```csharp
// DataPipelineCoreCollectionExtensions.cs
services.AddDataPipelineCore();  // SqlChangeTracker, ServiceBusChangeTracker, etc.

services.AddDomains<TDomainReference>();  // ConnectionsOptions, DomainsResolver
// → Registers ConnectionsOptions from Pipeline_Connections

services.AddScheduling();  // Quartz jobs: SqlChangeTrackerJob, AuditJob, DomainProcessorJob
```

### Relevant Config Bindings

```csharp
// ConnectionsOptions from named section
services.Configure<ConnectionsOptions>(
    configuration.GetSection("Pipeline_Connections"));
```

## Database Tests

### Squadron for Test Infrastructure

Use Squadron for real database instances in tests:

| Resource | Purpose |
|---|---|
| `MongoResource` | Standalone MongoDB for simple tests |
| `MongoReplicaSetResource` | MongoDB Replica Set (for transactions/change streams) |
| `SqlServerResource<SqlServerOptions>` | SQL Server container |

```csharp
// MongoDB test setup
public class MyRepositoryTests : IClassFixture<MongoResource>
{
    private readonly IMongoDatabase _database;

    public MyRepositoryTests(MongoResource mongoResource)
    {
        _database = mongoResource.CreateDatabase();
    }
}
```

```csharp
// SQL Server test setup
public class MySqlTests : IClassFixture<SqlServerResource<SqlServerOptions>>
{
    public MySqlTests(SqlServerResource<SqlServerOptions> sqlResource)
    {
        string connectionString = sqlResource.ConnectionString;
    }
}
```

### System Tests with Both Databases

```csharp
public class SystemTests
    : IClassFixture<MongoResource>,
      IClassFixture<SqlServerResource<SqlServerOptions>>
{
    // Both databases for end-to-end pipeline tests
}
```

### Loading MongoDB Fixtures

```csharp
// Create database from JSON files
mongoResource.CreateDatabase(new CreateDatabaseFromFilesOptions
{
    // Fixture files for test collections
});
```

### Test Configuration Overrides

```csharp
// Override test appsettings
configuration["Pipeline_Database:ConnectionString"] = mongoResource.ConnectionString;
configuration["Pipeline_Database:DatabaseName"] = database.DatabaseNamespace.DatabaseName;
configuration["Pipeline_Connections:Values:0:Name"] = "MyConnection";
configuration["Pipeline_Connections:Values:0:Value"] = sqlResource.ConnectionString;
```

### Snapshooter for Result Verification

Use `Snapshooter.Xunit` for deterministic snapshot comparisons:

```csharp
result.MatchSnapshot();
```

## Checklist for New Entities

When setting up a new data pipeline entity:

1. **SQL Stored Procedure** — Ensure the SP exists and returns the expected columns
2. **SqlLoaderConfiguration** — Define loader configuration with correct SP and connection
3. **SqlChangeTrackerConfiguration** — Define tracker with SP, Cron schedule, and connection
4. **ConnectionsOptions** — Register named connection string in `Pipeline_Connections`
5. **MongoDB Collections** — Created automatically, but verify indexes
6. **Domain-specific indexes** — Define on `Entity.*` fields when queries are needed
7. **Tests** — Repository tests with Squadron + Snapshooter, system tests with both DBs
