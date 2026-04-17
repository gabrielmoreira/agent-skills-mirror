# SwiftlyS2 Per-Player State Management Guide

Official docs sections:
- `Core Events`
- `Thread Safety`
- `Terminologies`

Suitable for: plugins that need to maintain runtime state for each player.

## Choosing a pattern

As plugin complexity increases, the following per-player state management patterns are common:

### Level 1: lightweight key-value state (small plugins)

Suitable for: simple state with only one or two fields.

```csharp
private readonly ConcurrentDictionary<ulong, bool> _playerEnabled = new();

[EventListener<OnClientPutInServer>]
public void OnClientPutInServer(IOnClientPutInServerEvent @event)
{
    Core.Scheduler.NextWorldUpdate(() =>
    {
        var player = Core.PlayerManager.GetPlayer(@event.PlayerId);
        if (player is null || !player.IsValid) return;
        _playerEnabled.TryAdd(player.SteamID, true);
    });
}

[EventListener<OnClientDisconnected>]
public void OnClientDisconnected(IOnClientDisconnectedEvent @event)
{
    _playerEnabled.TryRemove(@event.SteamID, out _);
}
```

### Level 2: runtime state objects (medium plugins)

Suitable for: each player has multiple fields that need to be managed together.

```csharp
public class PlayerRuntime
{
    public ulong SteamId { get; init; }
    public string? SelectedStyle { get; set; }
    public bool IsEnabled { get; set; } = true;
    public DateTime LastAction { get; set; } = DateTime.UtcNow;
}

private readonly ConcurrentDictionary<ulong, PlayerRuntime> _playerStates = new();

[EventListener<OnClientPutInServer>]
public void OnClientPutInServer(IOnClientPutInServerEvent @event)
{
    Core.Scheduler.NextWorldUpdate(() =>
    {
        var player = Core.PlayerManager.GetPlayer(@event.PlayerId);
        if (player is null || !player.IsValid) return;

        // GetOrAdd guarantees atomicity and avoids races
        _playerStates.GetOrAdd(player.SteamID, steamId => new PlayerRuntime
        {
            SteamId = steamId
        });
    });
}

[EventListener<OnClientDisconnected>]
public void OnClientDisconnected(IOnClientDisconnectedEvent @event)
{
    if (_playerStates.TryRemove(@event.SteamID, out var runtime))
    {
        // Optional: async persistence (implement FireAndForget first; see section 1 of async-safety-guide.md)
        FireAndForget(PersistPlayerStateAsync(runtime), Logger, "MyPlugin.PersistOnDisconnect");
    }
}
```

### Level 3: state objects with DB restore

Suitable for: restoring player preferences after disconnect / reconnect.

```csharp
[EventListener<OnClientPutInServer>]
public void OnClientPutInServer(IOnClientPutInServerEvent @event)
{
    if (@event.Kind != ClientKind.Player) return;

    Core.Scheduler.NextWorldUpdate(() =>
    {
        var player = Core.PlayerManager.GetPlayer(@event.PlayerId);
        if (player is null || !player.IsValid) return;

        // Restore from DB or a remote source (implement FireAndForget first; see section 1 of async-safety-guide.md)
        FireAndForget(LoadPlayerStateAsync(player), Logger, "MyPlugin.LoadPlayerState");
    });
}

private async Task LoadPlayerStateAsync(IPlayer player)
{
    var steamId = player.SteamID;
    var dbRecord = await SomeService.GetPlayerDataAsync(steamId);

    // Revalidate the player after async work completes
    var currentPlayer = Core.PlayerManager.GetPlayerBySteamId(steamId);
    if (currentPlayer is null || !currentPlayer.IsValid) return;

    var runtime = new PlayerRuntime
    {
        SteamId = steamId,
        SelectedStyle = dbRecord?.Style,
        IsEnabled = dbRecord?.Enabled ?? true
    };

    _playerStates.AddOrUpdate(steamId, runtime, (_, __) => runtime);
}
```

### Level 4: slot array + generation counter (large gameplay plugins)

Suitable for: O(1) access inside high-frequency hooks and generation validation for async write-back.

```csharp
public class PlayerRegistry
{
    private readonly PlayerState?[] _slots = new PlayerState[64];
    private readonly int[] _generations = new int[64];
    private readonly Dictionary<ulong, PlayerState> _steamIndex = new();

    public PlayerState? Attach(int slot, ulong steamId, IPlayer player)
    {
        Detach(slot);
        var generation = Interlocked.Increment(ref _generations[slot]);
        var state = new PlayerState(slot, steamId, generation, player);
        _slots[slot] = state;
        _steamIndex[steamId] = state;
        return state;
    }

    public void Detach(int slot)
    {
        if (_slots[slot] is { } old)
        {
            old.IsAttached = false;
            _steamIndex.Remove(old.SteamId);
            _slots[slot] = null;
        }
    }

    /// <summary>O(1) lookup for high-frequency hooks</summary>
    public PlayerState? GetBySlot(int slot)
    {
        return slot >= 0 && slot < 64 ? _slots[slot] : null;
    }

    /// <summary>Validate generation before async write-back</summary>
    public bool ValidateGeneration(int slot, int capturedGeneration)
    {
        return slot >= 0 && slot < 64
            && _slots[slot] is { IsAttached: true } s
            && s.Generation == capturedGeneration;
    }
}
```

## Choosing identity keys

| Scenario | Recommended key | Reason |
|------|--------|------|
| Long-term storage for real players | `SteamID` (ulong) | Stable across sessions |
| Fast runtime lookup | `SteamID` or `Slot` | Depends on hot-path needs |
| bot / fakeclient | `SessionId` | Bots have a fixed SteamID of 0, which is unreliable |
| Lookup inside high-frequency hooks | Slot array `_slots[slot]` | O(1) with no hash overhead |

## Cleanup timing

- `OnClientDisconnected`: remove runtime state
- `OnMapLoad` / `OnMapUnload`: clear map-scoped caches
- Plugin `Unload()`: clear all state

## Concurrency-safety rules

- Prefer `TryAdd`, `TryRemove`, `TryGetValue`, `GetOrAdd`, and `AddOrUpdate`.
- Avoid two-step writes such as `ContainsKey` + `Remove` or `ContainsKey` + `Add`.
- Use the merge predicate of `AddOrUpdate` to prevent state downgrade.
- Revalidate player / generation before async write-back.
- On hot paths, cache slot references to avoid dictionary lookups when appropriate.

## Checklist

- [ ] Is state initialized on connect?
- [ ] Is state cleaned up on disconnect?
- [ ] Are identity-key strategies different for real players and bots?
- [ ] Is player validity rechecked after async delays?
- [ ] Do concurrent operations use atomic APIs?
- [ ] Are map-scoped caches cleaned on map changes?
