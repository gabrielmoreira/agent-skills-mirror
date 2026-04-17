# SwiftlyS2 Game Events Notes

Official docs sections:
- `Game Events`
- `Core Events`

## Key reminder

- The official docs already make it clear that many game events in Source 2 are effectively obsolete and some are unreliable.
- Therefore:
  - If you only need player, map, entity, or tick lifecycle entry points, prefer `Core Events` first.
  - Use `Game Events` only when you have confirmed that the target Game Event truly exists and its behavior has been validated.

## Suitable scenarios

- typed game event fire / hook flows that have already been confirmed to work
- client or server events that still need to use an existing Game Event definition

## Unsuitable scenarios

- when you want stable lifecycle entry points
- when you want to listen to map lifecycle, player attach / disconnect, or high-frequency runtime state
- when you are unsure whether an event still works in the current Source 2 version

## Recommended path

1. Ask first: do I need a Game Event or a Core Event?
2. If you need stable lifecycle listening, go to `../core-events/lifecycle-checklist.md` first.
3. If a Game Event is truly required, then go deeper into the official `Game Events` docs and API Reference.

## Choosing between Pre and Post hooks

### `[GameEventHandler(HookMode.Pre)]`

- Fires **before** the event takes effect
- May return `HookResult.Stop` to intercept propagation
- Suitable for:
  - blocking certain behavior (for example, preventing purchase of a specific weapon)
  - performing condition checks before the event affects gameplay
  - modifying event parameters

### `[GameEventHandler(HookMode.Post)]`

- Fires **after** the event takes effect
- Suitable for:
  - statistics, logging, or rewards based on the event result
  - state updates (for example, corpse handling or visibility changes after death)
  - triggering follow-up async work

### Notes

- Entity operations inside Post hooks often need `NextTick` or `DelayBySeconds` so state can stabilize first.
- If you are unsure whether to use Pre or Post, prefer Post first because it is safer and does not affect event propagation.
- Use `HookResult.Stop` carefully in Pre hooks, because it can affect whether other plugins receive the event.

```csharp
// Pre hook example: conditional interception
[GameEventHandler(HookMode.Pre)]
public HookResult OnPlayerHurt(EventPlayerHurt @event)
{
    if (ShouldIgnore(@event))
        return HookResult.Stop;
    return HookResult.Continue;
}

// Post hook example: delayed processing
[GameEventHandler(HookMode.Post)]
public HookResult OnPlayerDeath(EventPlayerDeath @event)
{
    var victim = @event.UserIdPlayer;
    if (victim is null || !victim.IsValid) return HookResult.Continue;

    Core.Scheduler.DelayBySeconds(0.5f, () =>
    {
        // Delay until death state is stable before acting
        ProcessDeathEffects(victim);
    });
    return HookResult.Continue;
}
```
