---
name: hotchocolate-specialist
description: "Deep HotChocolate v15 GraphQL server expertise — schema design, resolvers, filtering/sorting/projections, pagination, subscriptions, error handling, authorization, performance, persisted operations, source generators, and migration. Self-learns from official docs. Triggers on: HotChocolate, GraphQL filtering/sorting/projections, pagination, subscriptions, mutation conventions, persisted queries, cost analysis, custom scalars, GraphQL authorization, interceptors, source generator, AddTypes, HotChocolate migration, Relay node, UseProjection, UsePaging, UseFiltering, UseSorting."
---

# HotChocolate Specialist

Deep HotChocolate v15 API expertise. Complements the `backend-developer` skill (project-specific patterns) with framework-level knowledge and self-learning from official documentation.

> **Scope boundary**: Project-specific patterns (ObjectType layout, TypeExtension conventions, DataLoader naming, middleware testing, MassTransit, MongoDB) live in the `backend-developer` skill. This skill covers HotChocolate framework APIs, advanced features, and official best practices.

## Self-Learning Workflow

**Before answering any non-trivial HotChocolate question**, fetch the latest official documentation to ensure accuracy. HotChocolate evolves rapidly — never rely solely on training data.

### Step 1: Identify the Topic

Map the user's question to one or more documentation areas from the [Documentation Index](references/doc-index.md).

### Step 2: Fetch Latest Documentation

Use `fetch_webpage` to retrieve the relevant page(s):

```
Primary:   https://chillicream.com/docs/hotchocolate/v15/{topic-path}
Fallback:  https://github.com/ChilliCream/graphql-platform/blob/main/website/src/docs/hotchocolate/v15/{topic-path}/index.md
```

For bleeding-edge features or source code questions, search the GitHub repository:
```
https://github.com/ChilliCream/graphql-platform/tree/main/src/HotChocolate/{module}
```

### Step 3: Cross-Reference with Project Patterns

After fetching official docs, verify alignment with project conventions from `backend-developer` skill and `general.instructions.md`. Prefer project conventions when they intentionally diverge from defaults.

### Step 4: Apply and Cite

Implement using the latest API. Always cite the documentation URL when introducing patterns the user may not have seen before.

## Topic Quick Reference

| Area | Key APIs / Attributes | Doc Path |
|---|---|---|
| **Schema Design** | `ObjectType<T>`, `InterfaceType<T>`, `UnionType`, `EnumType`, `InputObjectType<T>`, `DirectiveType<T>` | `defining-a-schema/` |
| **Scalars** | Built-in + custom `ScalarType<TRuntimeType, TLiteral>` | `defining-a-schema/scalars` |
| **Enums** | `EnumType<T>`, `[GraphQLName]`, `[GraphQLDescription]` | `defining-a-schema/enums` |
| **Interfaces** | `InterfaceType<T>`, `[InterfaceObject]`, `implements` | `defining-a-schema/interfaces` |
| **Unions** | `UnionType`, `UnionType<T>`, annotation-based | `defining-a-schema/unions` |
| **Directives** | `DirectiveType<T>`, `[Directive]`, executable/type-system | `defining-a-schema/directives` |
| **Relay** | `[Node]`, `[ID]`, Global Object Identification, `INodeResolver` | `defining-a-schema/relay` |
| **OneOf** | `[OneOf]` input types | `defining-a-schema/input-object-types` |
| **Dynamic Schemas** | Runtime type building, `ITypeModule` | `defining-a-schema/dynamic-schemas` |
| **Versioning** | `@deprecated`, schema evolution strategies | `defining-a-schema/versioning` |
| **Resolvers** | Pure resolvers, resolver pipeline, `[Parent]`, `[Service]`, `[ScopedService]` | `fetching-data/resolvers` |
| **DataLoader** | `BatchDataLoader`, `GroupedDataLoader`, `CacheDataLoader`, source-generated | `fetching-data/dataloader` |
| **Pagination** | `[UsePaging]`, `[UseOffsetPaging]`, cursor vs offset vs keyset | `fetching-data/pagination` |
| **Filtering** | `[UseFiltering]`, `IFilterConvention`, custom filter fields | `fetching-data/filtering` |
| **Sorting** | `[UseSorting]`, `ISortConvention`, custom sort fields | `fetching-data/sorting` |
| **Projections** | `[UseProjection]`, `IProjectionConvention`, first-class MongoDB support | `fetching-data/projections` |
| **Subscriptions** | `[Subscribe]`, `[Topic]`, in-memory, Redis provider | `defining-a-schema/subscriptions` |
| **Mutations** | Mutation conventions, `MutationConventionOptions`, `[Error]`, `[UseMutationConvention]` | `defining-a-schema/mutations` |
| **Error Handling** | `IErrorFilter`, mutation error conventions, `IError`, `ErrorBuilder` | `defining-a-schema/mutations` |
| **Server Config** | Endpoints, warmup, command-line | `server/` |
| **Interceptors** | `IHttpRequestInterceptor`, `ISocketSessionInterceptor` | `server/interceptors` |
| **DI** | `[Service]`, `RegisterService`, scoped services in resolvers | `server/dependency-injection` |
| **Global State** | `IResolverContext.ContextData`, `SetGlobalState`, `GetGlobalState` | `server/global-state` |
| **Introspection** | Enable/disable, `AllowIntrospection` | `server/introspection` |
| **File Upload** | `IFile`, `Upload` scalar | `server/files` |
| **Batching** | Request batching, variable batching | `server/batching` |
| **Instrumentation** | `IExecutionDiagnosticEvents`, OpenTelemetry integration | `server/instrumentation` |
| **Auth** | `[Authorize]`, policies, roles, `@authorize` directive | `security/` |
| **Persisted Ops** | Automatic Persisted Operations (APQ), file/blob/Redis stores | `performance/` |
| **Cost Analysis** | Query cost/complexity limits, `[Cost]` | Related to CostAnalysis module |
| **Source Generators** | `[Module]`, `AddTypes()`, automatic type registration | `defining-a-schema/#automatic-type-registration` |
| **Migration** | v13→v14→v15 breaking changes and migration paths | `migrating/` |

## Advanced Patterns

### Custom Scalars

```csharp
public class UrlType : ScalarType<Uri, StringValueNode>
{
    public UrlType() : base("Url") { }

    protected override Uri ParseLiteral(StringValueNode valueSyntax)
        => new(valueSyntax.Value);

    protected override StringValueNode ParseValue(Uri runtimeValue)
        => new(runtimeValue.AbsoluteUri);

    public override IValueNode ParseResult(object? resultValue)
        => ParseValue((Uri)resultValue!);
}
```

Register: `.AddType<UrlType>()`

### Filtering — Custom Convention

```csharp
public class CustomFilterConvention : FilterConvention
{
    protected override void Configure(IFilterConventionDescriptor descriptor)
    {
        descriptor.AddDefaults();
        descriptor.Provider(new QueryableFilterProvider(p =>
            p.AddDefaultFieldHandlers()));
    }
}

// Registration
services.AddGraphQLServer()
    .AddFiltering<CustomFilterConvention>();
```

### Sorting — Custom Convention

```csharp
public class CustomSortConvention : SortConvention
{
    protected override void Configure(ISortConventionDescriptor descriptor)
    {
        descriptor.AddDefaults();
        descriptor.Provider(new QueryableSortProvider(p =>
            p.AddDefaultFieldHandlers()));
    }
}
```

### Pagination — Cursor with MongoDB

```csharp
[UsePaging(IncludeTotalCount = true, MaxPageSize = 100, DefaultPageSize = 25)]
[UseProjection]
[UseSorting]
[UseFiltering]
public IExecutable<MyEntity> GetEntities([Service] IMongoCollection<MyEntity> collection)
    => collection.AsExecutable();
```

Order matters: `[UsePaging]` → `[UseProjection]` → `[UseSorting]` → `[UseFiltering]` (outermost to innermost).

### Subscriptions

```csharp
// In mutation resolver
[UseMutationConvention]
public async Task<MyEntity> CreateEntity(
    CreateEntityInput input,
    [Service] ITopicEventSender sender,
    CancellationToken ct)
{
    MyEntity entity = /* create */;
    await sender.SendAsync(nameof(OnEntityCreated), entity, ct);
    return entity;
}

// Subscription
[Subscribe]
[Topic(nameof(OnEntityCreated))]
public MyEntity OnEntityCreated([EventMessage] MyEntity entity) => entity;
```

### Error Handling — Mutation Conventions

```csharp
// Define domain errors as classes
public class EntityNotFoundError
{
    public EntityNotFoundError(string id) => Id = id;
    public string Id { get; }
    public string Message => $"Entity '{Id}' not found.";
}

// Annotate mutation with expected errors
[Error<EntityNotFoundError>]
[Error<ValidationError>]
[UseMutationConvention]
public async Task<MyEntity> UpdateEntity(UpdateEntityInput input, ...)
{
    // throw or return error types
}
```

### Authorization — Field-Level

```csharp
[Authorize(Policy = "AdminOnly")]
public class AdminQueries
{
    [Authorize(Roles = ["superadmin"])]
    public async Task<SensitiveData> GetSensitiveData(...)
        => /* ... */;
}
```

### Interceptors

```csharp
public class CustomHttpRequestInterceptor : DefaultHttpRequestInterceptor
{
    public override ValueTask OnCreateAsync(
        HttpContext context,
        IRequestExecutor requestExecutor,
        OperationRequestBuilder requestBuilder,
        CancellationToken ct)
    {
        // Add custom context data from HTTP headers
        string? tenantId = context.Request.Headers["X-Tenant-Id"];
        requestBuilder.SetGlobalState("TenantId", tenantId);
        return base.OnCreateAsync(context, requestExecutor, requestBuilder, ct);
    }
}

// Registration
services.AddGraphQLServer()
    .AddHttpRequestInterceptor<CustomHttpRequestInterceptor>();
```

### Source Generators & Registration

HotChocolate 12.7+ source generator auto-discovers types decorated with `[QueryType]`, `[MutationType]`, `[SubscriptionType]`, `[ObjectType]`, `[ExtendObjectType]`, etc.

```csharp
// ModuleInfo.cs — triggers source generation
[assembly: Module("MyDomain")]

// Startup — register all discovered types
services.AddGraphQLServer()
    .AddTypes();  // Registers all source-generated types from the module
```

### Persisted Operations

```csharp
services.AddGraphQLServer()
    .UseAutomaticPersistedOperationPipeline()
    .AddFileSystemOperationDocumentStorage("./persisted-operations");
```

Alternative stores: Redis (`AddRedisOperationDocumentStorage`), Azure Blob Storage.

## Troubleshooting Checklist

| Symptom | Likely Cause | Action |
|---|---|---|
| `Type 'X' is not registered` | Missing `AddTypes()` or manual registration | Check `[Module]` attribute + startup config |
| Filtering/sorting not applied | Missing `[UseFiltering]`/`[UseSorting]` or wrong attribute order | Verify attribute stacking order |
| N+1 queries in resolver | Missing DataLoader | Implement `BatchDataLoader` per `backend-developer` conventions |
| Subscription not firing | `ITopicEventSender` not called or topic mismatch | Verify `SendAsync` topic matches `[Topic]` |
| Auth returning `AUTH_NOT_AUTHENTICATED` | Missing `AddAuthorization()` or JWT config | Verify auth pipeline in startup |
| Pagination returns no `totalCount` | `IncludeTotalCount = false` (default) | Set `[UsePaging(IncludeTotalCount = true)]` |
| Mutation error not in union | Missing `[Error<T>]` attribute | Add error type annotation to mutation |
| Schema export changed unexpectedly | Source generator picked up new types | Review `[Module]` scope and type visibility |

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Fix |
|---|---|---|
| Filtering/sorting on non-indexed fields | Kills DB performance at scale | Ensure MongoDB indexes match filterable/sortable fields |
| `[UseProjection]` without DB support | Projection only works with supported providers | Verify MongoDB/EF Core provider integration |
| Manual pagination implementation | Reinvents cursor/offset logic HC handles | Use `[UsePaging]` or `[UseOffsetPaging]` |
| Catching exceptions in resolvers to return errors | Bypasses HC error pipeline | Use `IErrorFilter` or mutation error conventions |
| Hardcoded `MaxPageSize` > 500 | Opens DoS vector via large queries | Keep `MaxPageSize` ≤ 100 in production |
| Introspection enabled in production | Exposes full schema to attackers | Disable via `AllowIntrospection.Never` or per-policy |
| Ignoring `[Authorize]` on mutations | All mutations default to anonymous | Add authorization explicitly |
| Using `DateTime` scalar for UTC timestamps | Ambiguous timezone semantics | Use `DateTimeOffset` or custom UTC scalar |

## Important Rules

- Always fetch latest documentation before implementing advanced HC features
- Attribute stacking order matters: `[UsePaging]` → `[UseProjection]` → `[UseSorting]` → `[UseFiltering]`
- Never duplicate patterns already defined in `backend-developer` skill — reference it instead
- Cite documentation URLs when introducing new patterns to the team
- Prefer implementation-first (annotation-based) over schema-first approach
- For project-specific conventions (naming, testing), defer to `backend-developer` skill and `tests.instructions.md`
