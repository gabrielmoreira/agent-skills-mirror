---
name: backend-developer
description: "Use this skill when working on backend microservices — implementing GraphQL APIs with HotChocolate, writing MassTransit consumers/publishers, building MongoDB data access layers, configuring service startup, integrating data pipelines, or adding observability with OpenTelemetry. Triggers on: GraphQL resolvers, ObjectType, TypeExtensions, QueryRewriter, field middleware, DataLoaders, MassTransit IConsumer, Azure Service Bus, MongoDB repositories, data pipeline sender/receiver, service startup configuration, or any backend domain service work."
---

# Backend Developer

Guide for developing backend microservices. Covers domain-specific patterns, conventions, and internal libraries that the AI agent does not inherently know.

> **Scope**: This skill covers project-specific patterns and conventions only. For general C# best practices, refer to the CSharpExpert agent. For testing conventions, follow `tests.instructions.md`.

## Architecture Quick Reference

Architecture, layer definitions, dependency rules, and coding standards are defined in `general.instructions.md` (always loaded). The following covers domain-specific patterns only.

**Known domains**: <!-- TODO: List your domain services here, e.g., Contract, Consultation, Profile, Document, etc. -->

### API Stitching Layer

`src/Api/` is the HotChocolate Stitching gateway. It stitches domain GraphQL schemas together and uses `QueryDelegationRewriterBase` to transform queries between schemas.

```csharp
// Example: src/Api/src/Host/Addresses/AddressQueryRewriter.cs
public class AddressQueryRewriter : QueryDelegationRewriterBase
{
    // Rewrites delegated queries for the stitched schema
}
```

Never add business logic to the Api layer — it only delegates and rewrites.

## HotChocolate GraphQL Patterns

### ObjectType Definitions

Use class-based type definitions extending `ObjectType<T>`:

```csharp
public class MyEntityType : ObjectType<MyEntity>
{
    protected override void Configure(IObjectTypeDescriptor<MyEntity> descriptor)
    {
        descriptor.Field(x => x.Id).Type<NonNullType<IdType>>();
    }
}
```

### TypeExtensions

Extend existing types without modifying their original definition. Use `[ExtendObjectType]`:

```csharp
[ExtendObjectType(typeof(ParentEntity))]
public class ChildTypeExtensions
{
    public async Task<ChildResult> GetChildData(
        [Parent] ParentEntity parent,
        [Service] IChildService service,
        CancellationToken cancellationToken)
    {
        return await service.GetByParentIdAsync(parent.Id, cancellationToken);
    }
}
```

### Field Middleware

Chain middleware on fields using `FieldDelegate` and `IMiddlewareContext`:

```csharp
public static class ComputeMiddleware
{
    public static FieldDelegate Create(FieldDelegate next)
    {
        return async context =>
        {
            await next(context);
            object? result = context.Result;
            // Transform result
            context.Result = transformed;
        };
    }
}
```

Pass data between middleware/resolvers via `ScopedContextData` with `IImmutableStack<object>`.

### DataLoaders

Use GreenDonut `BatchDataLoader<TKey, TValue>` for batching and caching. Naming convention: `{Entity}By{Key}DataLoader`. Inject `IMyRepository` + `IBatchScheduler` in the constructor, call `base(batchScheduler, options)`, and override `LoadBatchAsync`.

### Translation & Localization

Consultation domain uses `HotChocolate.Extensions.Translation` with `HeaderLocalization`:

```csharp
services.AddTranslation()
    .AddHeaderLocalization(options => { /* configure */ });
```

### Mutation Conventions

Use HotChocolate's built-in mutation conventions. Prefer implementation-first over schema-first. Use dedicated Input/Output types rather than separate parameters.

## MassTransit Consumer Patterns

### Standard Consumer

Mark consumers `sealed`. Use primary constructors for DI. Every consumer **must** include OpenTelemetry tracing and source-generated logging:

```csharp
public sealed class ContractDeletedConsumer(
    IConsultationUpdater updater) : IConsumer<ContractDeleted>
{
    public async Task Consume(ConsumeContext<ContractDeleted> context)
    {
        using Activity? activity = App.ActivitySource.StartActivity();

        App.Log.ConsumingContractDeleted(context.Message.ContractId);

        await updater.DeleteByContractIdAsync(
            context.Message.ContractId,
            context.CancellationToken);
    }
}
```

### Abstract Base Consumer

For shared consumer logic across message types, use a generic abstract base:

```csharp
public abstract class CustomerUpdateMessageConsumerBase<TMessage>
    : IConsumer<TMessage> where TMessage : class
{
    public async Task Consume(ConsumeContext<TMessage> context)
    {
        using Activity? activity = App.ActivitySource.StartActivity();
        // Shared processing logic
        await ProcessAsync(context.Message, context.CancellationToken);
    }

    protected abstract Task ProcessAsync(TMessage message, CancellationToken cancellationToken);
}
```

### Consumer Organization

Organize consumers in `Core/Messaging/Consumers/` by category:
- `E2E/CustomerUpdates/` — End-to-end customer update events
- `Fuse/` — Fuse-specific events (invites, codes)
- `FusionIdentity/` — Identity events
- `Integration/` — External integration events

### Request-Response Pattern

For consumers that need to respond:

```csharp
await context.RespondAsync(new AdminResponse { /* ... */ });
```

### Consumer Anti-Patterns

- Never catch and swallow exceptions in consumers — let MassTransit handle retries
- Never use `ILogger` directly — use source-generated `App.Log` methods
- Never skip `App.ActivitySource.StartActivity()` — it breaks distributed tracing
- Never add business logic outside `Core/` layer — consumers orchestrate, not implement

### Publisher Testing

Test publishers with MassTransit `InMemoryTestHarness` + Snapshooter:

```csharp
public class ProfilePublisherTests
{
    private readonly InMemoryTestHarness _harness;

    [Fact]
    public async Task Publish_ShouldSendMessage()
    {
        // Arrange + Act
        await _publisher.PublishAsync(data);

        // Assert
        IPublishedMessage<ProfileUpdated>? message =
            _harness.Published.Select<ProfileUpdated>().FirstOrDefault();
        message.Should().NotBeNull();
        message!.Context.Message.MatchSnapshot();
    }
}
```

## Observability

### OpenTelemetry Tracing

Use a centralized activity source for all tracing. Start activities in every consumer/service method:

```csharp
using Activity? activity = App.ActivitySource.StartActivity();
```

Record exceptions on the activity:

```csharp
catch (Exception ex)
{
    activity?.RecordException(ex);
    throw;
}
```

### Source-Generated Logging

Use the `[LoggerMessage]` attribute with `App.Log` — never use `ILogger` directly for structured log messages:

```csharp
internal static partial class Log
{
    [LoggerMessage(Level = LogLevel.Information,
        Message = "Consuming contract deleted for {ContractId}")]
    public static partial void ConsumingContractDeleted(
        this ILogger logger, string contractId);
}

// Usage:
App.Log.ConsumingContractDeleted(contractId);
```

## Service Startup Configuration

### Standard Host Setup

Domain services use a consistent startup pattern:

```csharp
public class StartUp
{
    public void ConfigureServices(IServiceCollection services)
    {
        // Authentication
        services.AddJwtBearerAuthentication(Configuration);

        // GraphQL
        services.AddGraphQLServer()
            .AddTypes()
            .AddTranslation();

        // MongoDB
        services.AddMongoDataAccess(Configuration);

        // Health checks
        services.AddHealthChecks()
            .AddMongoHealthCheck();

        // MassTransit / Service Bus
        services.AddMassTransitServiceBus(Configuration);
    }
}
```

### Internal Libraries

<!-- TODO: Replace with your organization's internal libraries -->
| Library | Purpose |
|---|---|
| `YourOrg.Security.Authentication.JwtBearer` | JWT Bearer auth setup |
| `YourOrg.Health.*` | Health check extensions (Mongo, etc.) |
| `YourOrg.Observability.*` | Activity sources and structured logging |
| `YourOrg.{ProjectName}.*` | Domain-specific shared code |

### Authentication & Authorization

- Use `AddJwtBearerAuthentication(Configuration)` for auth setup
- Define authorization policies for specific endpoints (e.g., Invites, NeoInvites, MyLifeInvites)
- Swagger UI configured with Bearer token support

### REST + GraphQL Coexistence

Some services expose both REST (controllers + Swagger) and GraphQL. DocConnector and Onboarding use this pattern:

```csharp
services.AddControllers()
    .AddNewtonsoftJson(o => o.SerializerSettings.Converters.Add(new StringEnumConverter()));
services.AddSwaggerGen(c => { /* Bearer auth config */ });

services.AddGraphQLServer()
    .AddTypes();
```

### NSwag-Generated Clients

External API clients live in `ServiceReferences/Generated/`. Never edit generated files. Register via DI and consume through the generated client interfaces.

### Data Pipeline Integration

### API Host

```csharp
DataPipelineApi.Create<Startup>(SetupConfiguration, args);
```

### Worker Host

```csharp
DataPipelineHost.Create<DomainsReference>(SetupConfiguration, configureServices, args);
```

### Messaging

Register sender/receiver in DI:

```csharp
services.AddDataPipelineReceiver<MyWorker>();
services.AddDataPipelineSender();
```

Use `IMessageSender<T>` and `IMessageSenderFactory` for sending messages.

### Tenant Structure

The data pipeline uses tenant-based organization:
<!-- TODO: Replace with your actual tenant names -->
- `src/Tenants/TenantA/` — Primary tenant (Api + Host)
- `src/Tenants/TenantB/` — Secondary tenant

### Partial Program Pattern

Environment-specific config via partial classes:
- `Program.cs` — Shared entry point
- `Program.Dev.cs` — Development configuration
- `Program.Prod.cs` — Production configuration

### Shared Config

Shared appsettings live in `_Links/` directories, e.g., `_Links/{TenantName}.Domains/appsettings.shared.json`.

## MongoDB Data Access

### Repository Pattern

Repositories implement interfaces from `Abstractions` and use `IMongoCollection<T>` directly. Follow existing patterns in the domain you are working in.

### Health Checks

Always register MongoDB health checks:

```csharp
services.AddHealthChecks()
    .AddMongoHealthCheck();
```

## Testing Domain-Specific Code

Follow `tests.instructions.md` for general testing conventions. Additional domain-specific patterns:

### HotChocolate Middleware Testing

Use `DummyMiddlewareContext` / `DummyContext` implementing `IMiddlewareContext` / `IResolverContext`:

```csharp
DummyMiddlewareContext context = new();
context.SetResult(testData);
context.SetScopedContextData("key", value);

await middleware.Invoke(context);

context.Result.Should().BeEquivalentTo(expected);
```

### MassTransit Consumer Testing

Use `InMemoryTestHarness` for integration-style tests. Combine with `Snapshooter` for complex message assertions.

### Time-Dependent Logic

Use `FakeTimeProvider` to control time in tests instead of `DateTime.Now` or `DateTimeOffset.UtcNow`.