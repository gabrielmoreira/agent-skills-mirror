# SwiftlyS2 Shared API Template

Official docs sections:
- `Shared API`
- `Dependency Injection`

Suitable for: exposing shared services across plugins, consuming other plugins’ interfaces, and designing contract DLLs.

## Minimal provider / consumer structure

- Contracts DLL: defines interfaces used by both provider and consumer
- Provider: registers the interface implementation in `ConfigureSharedInterface`
- Consumer: detects and retrieves the shared interface in `UseSharedInterface`

## Contracts example

```csharp
namespace MyPlugin.Contracts;

public interface IEconomyService : IDisposable
{
    int GetPlayerBalance(int playerId);
    void AddPlayerBalance(int playerId, int amount);
    bool RemovePlayerBalance(int playerId, int amount);
}
```

## Provider example

```csharp
using MyPlugin.Contracts;
using SwiftlyS2.Shared;
using SwiftlyS2.Shared.Plugins;

public sealed class EconomyPlugin(ISwiftlyCore core) : BasePlugin(core)
{
    public override void ConfigureSharedInterface(IInterfaceManager interfaceManager)
    {
        var economyService = new EconomyService();
        interfaceManager.AddSharedInterface<IEconomyService, EconomyService>(
            "Economy.Service.v1",
            economyService);
    }
}
```

## Consumer example

```csharp
using MyPlugin.Contracts;
using SwiftlyS2.Shared;
using SwiftlyS2.Shared.Plugins;

public sealed class ShopPlugin(ISwiftlyCore core) : BasePlugin(core)
{
    private IEconomyService? _economyService;

    public override void UseSharedInterface(IInterfaceManager interfaceManager)
    {
        if (!interfaceManager.HasSharedInterface("Economy.Service.v1"))
        {
            Core.Logger.LogWarning("Economy.Service.v1 is not loaded yet.");
            return;
        }

        _economyService = interfaceManager.GetSharedInterface<IEconomyService>("Economy.Service.v1");
    }
}
```

## Checklist

- Is the interface placed in a separate contracts DLL?
- Does the key use clear naming and consider versioning?
- Does the consumer call `HasSharedInterface(...)` before fetching?
- Should the interface inherit from `IDisposable`?
- Do provider and consumer both have cleanup closure during unload?

## Delayed-initialization guard pattern

When a consumer’s core behavior strongly depends on a shared interface, do not initialize that business logic in `Load()`; delay it until `UseSharedInterface()` instead:

```csharp
public sealed class MyPlugin(ISwiftlyCore core) : BasePlugin(core)
{
    private bool _servicesInitialized;

    public override void Load(bool hotReload)
    {
        // Do not initialize shared-interface-dependent logic here
        Core.Logger.LogInformation("MyPlugin loading...");
    }

    public override void UseSharedInterface(IInterfaceManager interfaceManager)
    {
        if (_servicesInitialized) return;

        if (!interfaceManager.HasSharedInterface("Economy.Service.v1"))
        {
            Core.Logger.LogWarning("Economy.Service.v1 is not available yet; delaying initialization.");
            return;
        }

        var economyService = interfaceManager.GetSharedInterface<IEconomyService>("Economy.Service.v1");
        InitializeServices(economyService);
        _servicesInitialized = true;
    }

    private void InitializeServices(IEconomyService economyService)
    {
        // Initialize the DI container, register services, start the scheduler, and so on here
    }
}
```

**Key points**:
- `UseSharedInterface` may be called multiple times (whenever a new plugin registers an interface)
- Use the `_servicesInitialized` boolean guard to avoid duplicate initialization
- When the dependency is unavailable, log a warning and return early instead of throwing
- Only start persistent work such as schedulers or workers after delayed initialization completes

## Two-phase cross-plugin dependency

When two plugins depend on each other (for example, Plugin A provides a trigger and Plugin B consumes it while injecting its own manager back), use a two-phase pattern:

1. **Phase 1 (`ConfigureSharedInterface`)**: Plugin A registers the interface
2. **Phase 2 (`UseSharedInterface`)**: Plugin B gets A’s interface and injects its own dependency back into A

```csharp
// Plugin B (consumer + reverse injection)
public override void UseSharedInterface(IInterfaceManager interfaceManager)
{
    if (!interfaceManager.HasSharedInterface("PluginA.FeatureTrigger"))
        return;

    var trigger = interfaceManager.GetSharedInterface<IFeatureTrigger>(
        "PluginA.FeatureTrigger");

    // Inject the manager back into the trigger
    if (trigger is IFeatureTriggerInitializable initializable)
    {
        initializable.SetManager(_featureManager);
    }
}
```
