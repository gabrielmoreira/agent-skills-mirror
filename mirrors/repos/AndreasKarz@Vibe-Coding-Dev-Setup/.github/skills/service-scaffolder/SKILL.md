---
name: service-scaffolder
description: "Scaffold a new backend microservice end-to-end — create Abstractions, Core, DataAccess, GraphQL, Host, Worker projects with correct layer dependencies, DI wiring, health checks, and test projects. Triggers on: new service, new microservice, scaffold service, create service, add domain service, new domain, setup service skeleton."
---

# Service Scaffolder

Scaffold a complete backend domain microservice following the established project structure and conventions.

> **Prerequisites**: Read `general.instructions.md` for architecture rules and layer definitions before scaffolding.

## Scaffold Workflow

Follow these steps in order. Confirm the service name and scope with the user before starting.

### Step 1: Gather Requirements

Ask the user:
1. **Service name** — PascalCase domain name (e.g., `Consultation`, `Invoice`)
2. **Layers needed** — default: all (Abstractions, Core, DataAccess, GraphQL, Host, Worker). Some services skip Worker.
3. **Database** — MongoDB (default), SQL Server, or both
4. **Messaging** — MassTransit consumers needed? (yes/no)
5. **GraphQL only or REST+GraphQL** — default: GraphQL only

### Step 2: Create Project Structure

```
src/{ServiceName}/
├── src/
│   ├── Abstractions/
│   │   └── {ServiceName}.Abstractions.csproj
│   ├── Core/
│   │   └── {ServiceName}.Core.csproj
│   ├── DataAccess/
│   │   └── {ServiceName}.DataAccess.csproj
│   ├── GraphQL/
│   │   └── {ServiceName}.GraphQL.csproj
│   ├── Host/
│   │   └── {ServiceName}.Host.csproj
│   └── Worker/                              ← optional
│       └── {ServiceName}.Worker.csproj
└── test/
    ├── Core.Tests/
    │   └── {ServiceName}.Core.Tests.csproj
    ├── DataAccess.Tests/
    │   └── {ServiceName}.DataAccess.Tests.csproj
    ├── GraphQL.Tests/
    │   └── {ServiceName}.GraphQL.Tests.csproj
    └── Worker.Tests/                        ← if Worker exists
        └── {ServiceName}.Worker.Tests.csproj
```

### Step 3: Configure Project References

Follow the dependency rules strictly:

| Project | References |
|---|---|
| **Abstractions** | None (leaf) |
| **Core** | → Abstractions |
| **DataAccess** | → Abstractions, Core |
| **GraphQL** | → Abstractions, Core |
| **Host** | → Abstractions, Core, DataAccess, GraphQL |
| **Worker** | → Abstractions, Core |
| **Core.Tests** | → Core, Abstractions |
| **DataAccess.Tests** | → DataAccess, Core, Abstractions |
| **GraphQL.Tests** | → GraphQL, Core, Abstractions |

### Step 4: Abstractions Layer

Create the foundational types:

```csharp
// Models/{ServiceName}Entity.cs
// TODO: Replace with your organization namespace, e.g., YourOrg.YourProject
namespace YourOrg.YourProject.{ServiceName};

public record {ServiceName}Entity(
    ID<{ServiceName}Entity> Id,
    string Name);
```

```csharp
// Interfaces/I{ServiceName}Repository.cs
// TODO: Replace with your organization namespace, e.g., YourOrg.YourProject
namespace YourOrg.YourProject.{ServiceName};

public interface I{ServiceName}Repository
{
    Task<{ServiceName}Entity?> GetByIdAsync(
        ID<{ServiceName}Entity> id,
        CancellationToken cancellationToken);
}
```

### Step 5: Core Layer

```csharp
// Services/{ServiceName}Service.cs
// TODO: Replace with your organization namespace, e.g., YourOrg.YourProject
namespace YourOrg.YourProject.{ServiceName};

public sealed class {ServiceName}Service(
    I{ServiceName}Repository _repository)
{
    public async Task<{ServiceName}Entity?> GetByIdAsync(
        ID<{ServiceName}Entity> id,
        CancellationToken cancellationToken)
    {
        return await _repository.GetByIdAsync(id, cancellationToken);
    }
}
```

```csharp
// DependencyInjection/{ServiceName}CoreServiceCollectionExtensions.cs
namespace Microsoft.Extensions.DependencyInjection;

public static class {ServiceName}CoreServiceCollectionExtensions
{
    public static IServiceCollection Add{ServiceName}Core(
        this IServiceCollection services)
    {
        services.AddScoped<{ServiceName}Service>();
        return services;
    }
}
```

### Step 6: DataAccess Layer (MongoDB)

```csharp
// Repositories/{ServiceName}Repository.cs
// TODO: Replace with your organization namespace, e.g., YourOrg.YourProject
namespace YourOrg.YourProject.{ServiceName}.DataAccess;

public sealed class {ServiceName}Repository : I{ServiceName}Repository
{
    private readonly IMongoCollection<{ServiceName}Entity> _collection;

    public {ServiceName}Repository(IMongoDatabase database)
    {
        _collection = database.GetCollection<{ServiceName}Entity>("{serviceName}s");
    }

    public async Task<{ServiceName}Entity?> GetByIdAsync(
        ID<{ServiceName}Entity> id,
        CancellationToken cancellationToken)
    {
        FilterDefinition<{ServiceName}Entity> filter =
            Builders<{ServiceName}Entity>.Filter.Eq(x => x.Id, id);

        return await _collection
            .Find(filter)
            .FirstOrDefaultAsync(cancellationToken);
    }
}
```

```csharp
// DependencyInjection/{ServiceName}DataAccessServiceCollectionExtensions.cs
namespace Microsoft.Extensions.DependencyInjection;

public static class {ServiceName}DataAccessServiceCollectionExtensions
{
    public static IServiceCollection Add{ServiceName}DataAccess(
        this IServiceCollection services, IConfiguration configuration)
    {
        services.AddMongoDataAccess(configuration);
        services.AddScoped<I{ServiceName}Repository, {ServiceName}Repository>();
        return services;
    }
}
```

### Step 7: GraphQL Layer

```csharp
// Types/{ServiceName}EntityType.cs
// TODO: Replace with your organization namespace, e.g., YourOrg.YourProject
namespace YourOrg.YourProject.{ServiceName}.GraphQL;

public class {ServiceName}EntityType : ObjectType<{ServiceName}Entity>
{
    protected override void Configure(
        IObjectTypeDescriptor<{ServiceName}Entity> descriptor)
    {
        descriptor.Field(x => x.Id).Type<NonNullType<IdType>>();
    }
}
```

```csharp
// Queries/{ServiceName}Queries.cs
[QueryType]
public static class {ServiceName}Queries
{
    public static async Task<{ServiceName}Entity?> Get{ServiceName}ByIdAsync(
        ID<{ServiceName}Entity> id,
        [Service] {ServiceName}Service service,
        CancellationToken cancellationToken)
    {
        return await service.GetByIdAsync(id, cancellationToken);
    }
}
```

### Step 8: Host Layer

```csharp
// Startup.cs
// TODO: Replace with your organization namespace, e.g., YourOrg.YourProject
namespace YourOrg.YourProject.{ServiceName}.Host;

public class Startup
{
    public IConfiguration Configuration { get; }

    public Startup(IConfiguration configuration)
    {
        Configuration = configuration;
    }

    public void ConfigureServices(IServiceCollection services)
    {
        services.AddJwtBearerAuthentication(Configuration);

        services.Add{ServiceName}Core();
        services.Add{ServiceName}DataAccess(Configuration);

        services.AddGraphQLServer()
            .AddTypes();

        services.AddHealthChecks()
            .AddMongoHealthCheck();
    }

    public void Configure(IApplicationBuilder app)
    {
        app.UseRouting();
        app.UseAuthentication();
        app.UseAuthorization();

        app.UseEndpoints(endpoints =>
        {
            endpoints.MapGraphQL();
            endpoints.MapHealthChecks("/_health/live");
            endpoints.MapHealthChecks("/_health/ready");
        });
    }
}
```

### Step 9: Test Projects

Set up test infrastructure per `tests.instructions.md`:

```csharp
// Core.Tests/{ServiceName}ServiceTests.cs
public class {ServiceName}ServiceTests
{
    private readonly Mock<I{ServiceName}Repository> _repository =
        new(MockBehavior.Strict);

    private readonly {ServiceName}Service _sut;

    public {ServiceName}ServiceTests()
    {
        _sut = new {ServiceName}Service(_repository.Object);
    }

    [Fact]
    public async Task GetByIdAsync_EntityExists_ReturnsEntity()
    {
        // Arrange
        ID<{ServiceName}Entity> id = ID<{ServiceName}Entity>.New();
        {ServiceName}Entity expected = new(id, "Test");
        _repository
            .Setup(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expected);

        // Act
        {ServiceName}Entity? result = await _sut.GetByIdAsync(id, CancellationToken.None);

        // Assert
        Assert.Equal(expected, result);
    }
}
```

### Step 10: Validate

1. Run `dotnet build` on the new service
2. Run `dotnet test` on the test projects
3. Verify layer dependencies are correct (no circular references)
4. Verify no HotChocolate packages in Core/Abstractions

## Checklist

- [ ] All projects compile
- [ ] Layer dependency rules respected
- [ ] `ID<T>` used for entity IDs
- [ ] Health checks registered (`/_health/live`, `/_health/ready`)
- [ ] MongoDB health check added
- [ ] DI extensions follow `Add{ServiceName}{Layer}()` naming
- [ ] Test projects mirror production layers
- [ ] Mocks use `MockBehavior.Strict`
- [ ] No HotChocolate references outside GraphQL layer
