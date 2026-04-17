# SwiftlyS2 Scheduler vs Background Worker

Official docs sections:
- `Scheduler`
- `Thread Safety`

Use this to avoid mixing up the official `Scheduler` tick/timer semantics with background `Task.Run`, queue, flush, and cancel worker semantics.

## Scenarios that should prefer Scheduler

- `NextTick` / next-tick execution
- lightweight delayed tasks
- low-frequency periodic tasks
- logic strongly tied to map lifecycle and suitable for `StopOnMapChange`

## Scenarios that should prefer background workers

- JSON serialization / deserialization
- disk IO / network IO / database batch work
- producer / consumer decoupling
- cancelable background polling
- long-running work that must not block the main thread

## Decision questions

- Is this a “next-tick semantic” or real background async work?
- Does it need to access main-thread-sensitive APIs?
- Does it need stop / flush / cancel / drain queue semantics?
- Will it handle JSON, IO, or large batch work?

## Routing suggestion

- If it is lightweight delayed work on the main thread, continue with the official `Scheduler` guidance.
- If it is background queue or batch processing, go to `../../patterns/background-workers/worker-template.cs.md`.
