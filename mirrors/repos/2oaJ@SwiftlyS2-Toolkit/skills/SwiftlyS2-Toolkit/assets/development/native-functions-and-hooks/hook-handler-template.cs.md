# SwiftlyS2 Hook Handler Template

Official docs sections:
- `Native Functions and Hooks`
- `Thread Safety`
- `Profiler`

Suitable for: high-frequency hooks, movement sampling, engine callback dispatch, and lightweight sampling followed by module delegation.

## Usage principles

- Do fast routing first inside hooks.
- Do not perform heavy IO, heavy serialization, or heavy logging directly inside hooks.
- Hooks should own sampling and delegation, not accumulated business logic.
- When `IPlayer`, `Pawn`, or `Controller` are involved, validate first.

## Example skeleton

```csharp
using SwiftlyS2.Shared;
using SwiftlyS2.Shared.Core.Attributes.Hooks;
using SwiftlyS2.Shared.Hooks;
using SwiftlyS2.Shared.Player;

namespace MyNamespace;

public partial class MyPlugin
{
    [HookCallback("MyPlugin::OnSomeHighFrequencyHook")]
    public HookResult OnSomeHighFrequencyHook(DynamicHook hook)
    {
        var player = ResolvePlayerFromHook(hook);
        if (player is null || !player.Valid() || player.IsFakeClient)
        {
            return HookResult.Continue;
        }

        var pawn = player.PlayerPawn.Value;
        if (pawn is null || !pawn.IsValid)
        {
            return HookResult.Continue;
        }

        var snapshot = BuildMovementSnapshot(player, pawn);
        _runtimeModule.HandleMovementSnapshot(snapshot);
        return HookResult.Continue;
    }

    private IPlayer? ResolvePlayerFromHook(DynamicHook hook)
    {
        return null;
    }
}
```

## Checklist

- Are invalid players, invalid pawns, fake clients, and dead players filtered first?
- Is direct logging inside hooks avoided?
- Are IO, HTTP, DB, and JSON operations avoided inside hooks?
- Is complex logic pushed down into modules, services, or workers?
- Has the 64-tick / 15ms frame budget been considered?

## GameData patch pattern

Some fixes do not need hooks and can directly patch gamedata in memory:

```csharp
public class GameDataPatchService(ISwiftlyCore core, ILogger logger, string patchName)
    : IGameFixService
{
    public string ServiceName => patchName;

    public void Install()
    {
        core.GameData.ApplyPatch(patchName);
        logger.LogInformation("{PatchName} applied", patchName);
    }

    public void Uninstall() { }  // Patches are one-way and not reversible
}
```

## Multi-hook service pattern

When one service needs to install multiple hooks, each hook should manage its own `IUnmanagedFunction` + `Guid` pair:

```csharp
public class MultiHookService : IGameFixService
{
    private Guid? _touchHookId, _endTouchHookId, _precacheHookId;
    private IUnmanagedFunction<TouchDelegate>? _touchHook;
    private IUnmanagedFunction<EndTouchDelegate>? _endTouchHook;
    private IUnmanagedFunction<PrecacheDelegate>? _precacheHook;

    public void Install()
    {
        InstallTouchHook();
        InstallEndTouchHook();
        InstallPrecacheHook();
    }

    public void Uninstall()
    {
        if (_touchHookId.HasValue && _touchHook is not null)
            _touchHook.RemoveHook(_touchHookId.Value);
        if (_endTouchHookId.HasValue && _endTouchHook is not null)
            _endTouchHook.RemoveHook(_endTouchHookId.Value);
        if (_precacheHookId.HasValue && _precacheHook is not null)
            _precacheHook.RemoveHook(_precacheHookId.Value);
    }
}
```

**Key points**:
- Each hook has its own `Guid? + IUnmanagedFunction` pair
- Install registers them all; Uninstall removes them all
- Failure to install one hook should not affect the others that were already installed

## Hook installation timing

Not every hook should be installed in `Load()`:

- ✅ **Install in `Load()`**: core hooks needed for the full plugin lifecycle
- ✅ **Install in `OnMapLoad` / `OnActivate`**: map-scoped or conditional hooks
- ✅ **Install after specific events**: for example, install a Sellback Hook after warmup ends
- ❌ Do not repeatedly install hooks inside high-frequency callbacks

The matching uninstall must be completed in `Unload()` / `OnMapUnload` / `OnDeactivate` / the corresponding symmetrical event.
