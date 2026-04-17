# SwiftlyS2 Schema Write Checklist

Official docs sections:
- `Entity`
- `Thread Safety`
- `Porting from CounterStrikeSharp`

> Notes: this checklist is a locally derived review sheet organized from the official `Entity`, thread-safety, and CSS-porting differences. It is not a copy of a single official docs page.

## Main-thread requirements

- [ ] Does Schema write-back explicitly happen on the main thread?
- [ ] Are direct entity-field writes from background threads avoided?
- [ ] If async processing is needed, is an immutable snapshot captured first?
- [ ] If the flow involves JSON DTOs or serialization, is it separated from main-thread entity reads and writes?

## Write-back notification requirements

- [ ] Does the write-back need a follow-up call to `Updated()`?
- [ ] If the task involves CSS porting semantics, has it been confirmed whether `SetStateChanged()` is still needed?
- [ ] Has the engine / client synchronization semantics of the current field been confirmed?

## Lifecycle and validity

- [ ] Before write-back, has it been confirmed that the `IPlayer`, `Controller`, `Pawn`, or entity is still valid?
- [ ] Are writes to stale objects after disconnect, map change, or unload avoided?
- [ ] Do delayed callbacks reacquire the current object instead of reusing an old reference?
- [ ] If the entity must be tracked across ticks or delays, is `CHandle<T>` used?

## Hot-path risk

- [ ] Is this Schema write-back located inside a high-frequency hook?
- [ ] If it is on a hot path, are meaningless repeated writes avoided?
- [ ] Has the impact on the 64-tick / 15ms frame budget been evaluated?
