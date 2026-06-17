# Events clients

Custom events and business-event ingestion. Import from `@dynatrace-sdk/client-classic-environment-v2`.

## `eventsClient`

| Method | Purpose |
|---|---|
| `createEvent` | Ingest a custom event. |
| `getEvents` | Query events (filterable, paginated). |
| `getEvent` | Get one event by id. |
| `getEventProperties` | List event properties. |
| `getEventProperty` | Get one event property. |
| `getEventTypes` | List event types. |
| `getEventType` | Get one event type. |

## `businessEventsClient`

| Method | Purpose |
|---|---|
| `ingest` | Ingest business events (CloudEvent or custom format). Max **5 MiB** payload per request. |

## Example

```ts
import { businessEventsClient } from "@dynatrace-sdk/client-classic-environment-v2";

await businessEventsClient.ingest({ body: { /* CloudEvent(s) */ }, type: "application/cloudevent+json" });
```
