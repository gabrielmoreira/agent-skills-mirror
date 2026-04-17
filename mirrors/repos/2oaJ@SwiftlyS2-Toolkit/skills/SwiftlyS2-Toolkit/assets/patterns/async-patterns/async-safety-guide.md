# SwiftlyS2 Async Safety Pattern Guide

Official docs sections:
- `Thread Safety`
- `Scheduler`
- `Core Events`

Suitable for: async callbacks, delayed tasks, background write-back, generation validation, and `CancellationToken` management.

## 1. Fire-and-forget from synchronous entry points

When SwiftlyS2 uses async tasks from synchronous entry points such as commands, event callbacks, or menu callbacks, calling `_ = SomeAsync()` directly will swallow exceptions. It is recommended to define a small helper method inside the plugin:

```csharp
// Define once inside the plugin and reuse in many places
private static async void FireAndForget(Task task, ILogger logger, string context)
{
    try { await task; }
    catch (Exception ex) { logger.LogError(ex, "[{Context}] Unobserved async exception", context); }
}

// Start async work from a synchronous entry point
[Command("mycommand")]
public void OnMyCommand(ICommandContext context)
{
    FireAndForget(OnMyCommandAsync(context), Logger, "MyPlugin.OnMyCommand");
}

private async Task OnMyCommandAsync(ICommandContext context)
{
    var player = context.Sender;
    if (player is null || !player.IsValid) return;

    var data = await FetchDataAsync(player.SteamID);
    // FireAndForget will automatically log to Logger when an exception occurs
}
```

**Key points**:
- `FireAndForget` is a small helper that must be implemented by the plugin itself; the SW2 SDK does not provide it.
- The inner `async void` layer catches and logs exceptions to avoid process crashes from unobserved task exceptions.
- Do not operate on return values after `FireAndForget`.

## 2. Revalidate `IPlayer` after async callbacks

After an `await`, the `IPlayer` may already have disconnected or been replaced. Reacquire and validate it:

```csharp
private async Task HandleSomeActionAsync(IPlayer player)
{
    var steamId = player.SteamID;  // Snapshot the immutable identifier first

    var result = await SomeLongRunningCall(steamId);

    // Reacquire the player after async work completes
    var currentPlayer = Core.PlayerManager.GetPlayerBySteamId(steamId);
    if (currentPlayer is null || !currentPlayer.IsValid)
    {
        Logger.LogDebug("Player {SteamId} disconnected during async work", steamId);
        return;
    }

    await currentPlayer.SendMessageAsync(MessageType.Chat, $"Result: {result}");
}
```

## 3. StopOnMapChange + CancellationTokenSource

`Core.Scheduler.StopOnMapChange(cts)` binds a `CancellationTokenSource` to the map lifecycle:

```csharp
private CancellationTokenSource? _mapCts;

[EventListener<OnMapLoad>]
public void OnMapLoad(IOnMapLoadEvent @event)
{
    _mapCts?.Cancel();
    _mapCts?.Dispose();
    _mapCts = new CancellationTokenSource();

    // Automatically cancel when the map changes
    Core.Scheduler.StopOnMapChange(_mapCts);

    // Periodic tasks registered with Scheduler will be canceled automatically
    Core.Scheduler.RepeatBySeconds(1.0f, () => PeriodicTask(_mapCts.Token));
}

// Propagate cancellation with the token in async tasks
private async Task LoadMapDataAsync(string mapName, CancellationToken cancellationToken)
{
    var data = await FetchMapDataAsync(mapName).ConfigureAwait(false);

    cancellationToken.ThrowIfCancellationRequested();

    // Ensure work does not continue after the map has changed
    ApplyMapData(data);
}
```

## 4. Generation Counter (generation validation for async write-back)

When async tasks need to write state back, use a generation counter to prevent writing into expired slots:

```csharp
// Capture the current generation when launching async work
private async Task SavePlayerRecordAsync(int slot, int capturedGeneration, RecordData data)
{
    await DatabaseService.SaveAsync(data).ConfigureAwait(false);

    // Validate before write-back
    if (!_registry.ValidateGeneration(slot, capturedGeneration))
    {
        Logger.LogDebug("Generation invalidated (slot={Slot}); discarding write-back", slot);
        return;
    }

    // Safely write back on the main thread
    Core.Scheduler.NextWorldUpdate(() =>
    {
        // Validate again when returning to the main thread
        if (!_registry.ValidateGeneration(slot, capturedGeneration)) return;
        _registry.GetBySlot(slot)!.LastSavedRecord = data;
    });
}
```

## 5. Interlocked + Volatile (general async state invalidation)

Suitable for simple scenarios where config reload or cache reload should invalidate old results:

```csharp
private int _cacheGeneration;

private void OnConfigChanged(Config newConfig)
{
    Interlocked.Increment(ref _cacheGeneration);
    // In-flight async loads will discard their result if the generation no longer matches
}

private async Task ReloadCacheAsync()
{
    var gen = Volatile.Read(ref _cacheGeneration);
    var data = await FetchFromRemoteAsync();

    if (Volatile.Read(ref _cacheGeneration) != gen)
    {
        // Config changed again during loading; discard this result
        return;
    }

    ApplyCache(data);
}
```

## 6. Key anti-patterns

**Do not do this:**
```csharp
// ❌ Block the main thread
var result = SomethingAsync().Result;
var result2 = SomethingAsync().GetAwaiter().GetResult();
SomethingAsync().Wait();

// ❌ Swallow exceptions
_ = SomethingAsync();

// ❌ Use an old player reference after async work
await Task.Delay(1000);
player.SendMessage(MessageType.Chat, "Might already be disconnected");  // Dangerous!

// ❌ Infinite loop without a cancellation token
while (true) { await Task.Delay(1000); DoWork(); }
```

**Do this instead:**
```csharp
// ✅ fire-and-forget with logging (self-implemented FireAndForget helper; see section 1)
FireAndForget(SomethingAsync(), Logger, "MyPlugin.Context");

// ✅ Reacquire the player after async work
var currentPlayer = Core.PlayerManager.GetPlayerBySteamId(steamId);
if (currentPlayer is not null && currentPlayer.IsValid) { ... }

// ✅ Use a cancellation token
while (!token.IsCancellationRequested) { await Task.Delay(1000, token); }
```

## Checklist

- [ ] Do async tasks launched from synchronous entry points use a self-implemented `FireAndForget` wrapper (see section 1)?
- [ ] Is `IPlayer` validity rechecked after each async `await`?
- [ ] Are map-scoped async tasks bound to `StopOnMapChange`?
- [ ] Does async write-back use a generation counter or similar generation validation?
- [ ] Are `.Wait()`, `.Result`, and synchronous blocking avoided?
- [ ] Do background loops carry a `CancellationToken`?
