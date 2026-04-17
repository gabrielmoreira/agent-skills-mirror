# SwiftlyS2 Lifecycle Checklist

Official docs sections:
- `Core Events`
- `Thread Safety`
- `Scheduler`

> Notes: this checklist uses `Core Events` as the entry point, but it covers full lifecycle closure for players, maps, workers, and services.

## Player lifecycle

- [ ] Does `OnClientPutInServer` complete attach / initialization?
- [ ] Does `OnClientDisconnected` complete detach / cleanup?
- [ ] Does any delayed logic still hold an old `IPlayer` after disconnect?
- [ ] Does state remain consistent after player state transitions?
- [ ] Are fake clients and real players routed apart early enough?

## Map lifecycle

- [ ] Does `OnMapLoad` clear map-scoped caches?
- [ ] Does `OnMapUnload` stop workers, auto-controlled entities, and runtime loops?
- [ ] Does any old-map object state remain after a map change?
- [ ] Does `OnPrecacheResource` register all custom models / sounds / particles?
- [ ] Is the map-scoped `CancellationTokenSource` bound with `StopOnMapChange`?

## Async and background work

- [ ] Does the worker provide stop / flush / cancel semantics?
- [ ] Do async callbacks reacquire player / state instead of blindly using stale references?
- [ ] Are `.Wait()`, `.Result`, and main-thread blocking avoided?
- [ ] Do async tasks started from synchronous entry points use a safe fire-and-forget wrapper (for example, capturing and logging second-level `async void` exceptions to avoid unobserved task failures)?
- [ ] Does async write-back pass generation checks or state-validity checks?

## Module / service lifecycle

- [ ] Does the plugin root own only install order and uninstall order?
- [ ] Can every Event / Hook / Command registered by an independent service be cleaned up in that service’s own `Uninstall()` / `Cleanup()`?
- [ ] Do conditional hooks use internal state markers for dynamic install / uninstall?

## High-frequency hooks / hot paths

- [ ] Are invalid players, fake clients, and dead players filtered as early as possible?
- [ ] Are logging and IO avoided on hot paths?
- [ ] Are unnecessary allocations avoided?
