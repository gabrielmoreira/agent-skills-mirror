---
name: event-contracts
description: "Design and inspect structured ETW, EventSource, and TraceLogging event contracts with typed dimensions, activity correlation, retry and failure semantics, and explicit missing-value handling. Use when diagnostic events lose fields, duplicate errors, misrepresent outcomes, or cannot be correlated."
---

# Structured event contracts and activity correlation

Use public diagnostic APIs to make events queryable; do not assume the rendered
message is the contract. EventSource can feed ETW on Windows, EventPipe, and
in-process listeners. Native TraceLogging is another self-describing ETW producer.
An `ILogger` template's final encoding depends on its provider, formatter and
export path, not merely on using `ILogger`.

## Define the contract before the message

For each event record the provider, event ID/name, version, level, task/opcode,
field names/types, required fields, and activity/related-activity semantics.
Avoid baking arbitrary object dumps or serialized exception text into the schema.

| Dimension | Example and invariant |
|---|---|
| Operation | Stable logical operation ID across all attempts; do not allocate a new operation for every retry. |
| Attempt | Distinct child activity ID and monotonically increasing attempt number; correlate it to the operation. |
| Outcome | Bounded values such as `Succeeded`, `Failed`, `Cancelled`, or `Partial`; log one terminal outcome per attempt and one per operation. |
| Progress | Typed completed/total counters; a nonzero completed count does not imply overall success. |
| Error | Error category plus native code **availability** and value; unavailable is not code zero meaning success. |
| Timing | Event timestamp plus appropriately measured duration if needed; do not infer duration from formatted prose. |

Choose representations supported by the actual event encoder. A boolean
`HasNativeCode` plus `NativeCode` can represent missing values in a manifest
contract without inventing success; consumers **must** gate on the boolean.
Null/default values in a high-level API may be normalized during encoding.
Inspect what the consumer really receives.

Keep event IDs and names stable. Do not change the meaning/type/order of fields
under an existing version. Use the producer's supported schema-versioning
mechanism (for manifest EventSource, `EventAttribute.Version`) or a new event
identity for an incompatible contract. Confirm older consumers handle the
change; versioning is not a guarantee that they understand it.

## Correlate activity, retries, and terminal results

1. Allocate one operation activity and a distinct activity for each attempt.
2. Emit an operation-to-attempt transfer with a related activity ID, or record
   explicit application-level parent IDs with clearly documented semantics.
   Payload IDs and ETW header ActivityId/RelatedActivityId are not interchangeable.
3. An attempt failure that will be retried is not yet the operation's terminal
   failure. Preserve the retry relationship and reason rather than emitting
   indistinguishable duplicate error events.
4. Have one boundary own detailed exception reporting. Lower layers may return
   structured context; the operation boundary reports its terminal outcome
   without logging the same exception stack repeatedly.
5. Restore activity state after synchronous emission. Thread-local activity IDs
   do not automatically describe asynchronous continuations; use supported
   async activity propagation or explicit IDs, and test concurrent operations.

The bundled [contract example](examples/EventContractExample.csproj) uses a
fictional two-attempt import: the first fails with an unavailable native code;
the second fails after two items; the operation reports `Partial`. No import,
network call or real file migration occurs.

It explicitly sets thread activity only around **synchronous** emission and
restores it in `finally`. This is a bounded example, not a general async tracing
helper. `AttemptLinked` is a transfer event (Send opcode), not a Start event.
Tools need its documented relationship semantics rather than assuming every
event name ending in "Begin" drives automatic activity tracking.

## Run the local fixture

With a .NET 8 or later SDK capable of targeting .NET 8:

```powershell
dotnet run --project .\examples\EventContractExample.csproj --configuration Release
```

Resolve the example relative to this installed skill. Its EventListener checks
decoded event names, versions, field types/values, native header correlation,
partial outcomes, and absence of EventSource error events. This checks the
managed emission contract, **not** ETW session enablement, loss, or a downstream
logging sink. Output lists the inspected events with their fields.

## Inspect the collected contract, not only console text

For an authorized local Windows diagnostic session, use public PerfView:

1. Start the example with `-- --wait-for-enter` so its provider exists before the
   scenario emits. The console prints the PID and waits for Enter.
2. In PerfView's collection UI enable only `*Fabrikam-Synthetic-Import` in
   Additional Providers (EventSource provider-name syntax), select an output
   path and the required collection privileges. Do not start system-wide
   collection merely because this skill loaded.
3. Start collection, press Enter in the example, then stop collection.
4. Open the trace's **Events** view; filter by provider and the printed PID.
   Inspect event IDs/names/versions, ActivityID/RelatedActivityID, and individual
   payload columns, not just formatted text. Compare the attempt links and
   terminal records against the fixture assertions.
5. Inspect provider enablement, level/keyword filters and lost-event statistics
   if records are absent. A missing event is not proof an operation never ran.
   Retain only a sanitized synthetic trace; real traces can contain sensitive
   system information even when your own fields do not.

EventPipe tools such as `dotnet-trace` provide another .NET collection path,
not proof of a Windows ETW contract. Native TraceLogging tooling and `ILogger`
exporters may present different metadata; validate the exact chosen path
instead of extrapolating from an in-process listener.

## Failure-oriented review

| Case | Required inspection |
|---|---|
| Retry then terminal failure | Two distinct attempts linked to one operation, each with a terminal outcome. |
| Missing native code | Availability is false; queries do not aggregate placeholder zero as success. |
| Partial work | Completed count remains visible while outcome is not `Succeeded`. |
| Concurrent/async work | Correlation stays with the logical operation, not whatever thread last ran. |
| Duplicate exception logs | One owner records detail; attempt and operation summaries remain distinguishable. |
| Schema change | Consumer field names/types and old-version behavior remain explicit. |
| Sink flattening | Inspect exported fields first; do not claim all structured `ILogger` providers flatten dimensions. |

References: [EventSource guidance](https://learn.microsoft.com/dotnet/core/diagnostics/eventsource-instrumentation),
[related activity writes](https://learn.microsoft.com/dotnet/api/system.diagnostics.tracing.eventsource.writeeventwithrelatedactivityid),
[EventListener](https://learn.microsoft.com/dotnet/api/system.diagnostics.tracing.eventlistener),
[TraceLogging](https://learn.microsoft.com/windows/win32/tracelogging/trace-logging-about),
and [PerfView](https://github.com/microsoft/perfview).
