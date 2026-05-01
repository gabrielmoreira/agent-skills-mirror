---
applyTo: "**/Worker/**/*.cs"
---

# Worker Layer Rules

These rules apply exclusively to the `Worker` project layer (background services, message handlers, batch processing).

## Consumer Design
- MassTransit consumers must be `sealed` classes
- One consumer per message type — no multi-message consumers
- Implement `IConsumer<TMessage>` explicitly

## Observability
- Start an `Activity` for every consumer/handler entry point: `App.ActivitySource.StartActivity("OperationName")`
- Record exceptions on the activity span: `activity?.RecordException(ex)`
- Use source-generated logging (`[LoggerMessage]`) — never use string interpolation with `ILogger` directly

## Error Handling
- Never swallow exceptions silently (`catch (Exception) { }`)
- Log the exception and let MassTransit's retry/error pipeline handle redelivery
- Use Polly retry policies for transient external calls (HTTP, database)
- Propagate `CancellationToken` through the entire call chain

## Quartz Jobs
- Apply `[DisallowConcurrentExecution]` on jobs that must not overlap
- Apply `[PersistJobDataAfterExecution]` when job state must survive between runs
- Verify Cron schedule expressions — placeholder `{0}` must be replaced with actual values

## Dependencies
- `Worker` → `Abstractions`, `Core` (same dependency rules as other layers)
- No direct database access — delegate to `Core` services or repository interfaces from `Abstractions`
