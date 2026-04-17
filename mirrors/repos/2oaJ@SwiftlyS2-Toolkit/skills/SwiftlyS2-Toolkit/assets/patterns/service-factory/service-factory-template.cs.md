# SwiftlyS2 Service Factory / Keyed Service Pattern

Official docs section:
- `Dependency Injection`

Suitable for: plugins where one interface has multiple implementations, strategies must be selected, or services need to be resolved dynamically by key / type.

## 1. Service Factory pattern

Suitable for: one feature interface has multiple strategy implementations and selection must happen at runtime by name / type.

### Interface definition

```csharp
public interface IMyService
{
    string Key { get; }
    void Execute(IPlayer player);
    void OnPrecacheResource(IOnPrecacheResourceEvent @event);
}

public interface IMyServiceFactory
{
    IMyService? GetService(string key);
    IEnumerable<IMyService> GetAllServices();
}
```

### Factory implementation

```csharp
public class MyServiceFactory : IMyServiceFactory
{
    private readonly ConcurrentDictionary<string, IMyService> _services = new();

    public void Register(IMyService service)
    {
        _services.TryAdd(service.Key, service);
    }

    public IMyService? GetService(string key)
    {
        _services.TryGetValue(key, out var service);
        return service;
    }

    public IEnumerable<IMyService> GetAllServices() => _services.Values;
}
```

### DI registration

```csharp
var services = new ServiceCollection();
services.AddSwiftly(Core);
services.AddSingleton<IMyServiceFactory, MyServiceFactory>();
services.AddSingleton<IMyService, StrategyA>();
services.AddSingleton<IMyService, StrategyB>();

var sp = services.BuildServiceProvider();
var factory = sp.GetRequiredService<IMyServiceFactory>();
foreach (var svc in sp.GetServices<IMyService>())
{
    factory.Register(svc);
}
```

## 2. Keyed Singleton pattern

Suitable for: multiple instances of the same interface that need independent configuration (for example, multiple GameData patches or multiple fixes).

### Registration

```csharp
services.AddKeyedSingleton<IGameFixService>("FixA",
    (sp, key) => new GameDataPatchService(Core, sp.GetRequiredService<ILogger<GameDataPatchService>>(), "FixA"));
services.AddKeyedSingleton<IGameFixService>("FixB",
    (sp, key) => new GameDataPatchService(Core, sp.GetRequiredService<ILogger<GameDataPatchService>>(), "FixB"));
```

### Resolution

```csharp
var fixA = sp.GetRequiredKeyedService<IGameFixService>("FixA");
var fixB = sp.GetRequiredKeyedService<IGameFixService>("FixB");
```

### Batch management

```csharp
var allFixes = new IGameFixService[]
{
    sp.GetRequiredKeyedService<IGameFixService>("FixA"),
    sp.GetRequiredKeyedService<IGameFixService>("FixB"),
};

// Install together
foreach (var fix in allFixes)
{
    try { fix.Install(); }
    catch (Exception ex) { Logger.LogError(ex, "Failed to install {Name}", fix.ServiceName); }
}

// Uninstall together
foreach (var fix in allFixes)
{
    try { fix.Uninstall(); }
    catch (Exception ex) { Logger.LogError(ex, "Failed to uninstall {Name}", fix.ServiceName); }
}
```

## 3. Multi-implementation resolution (`GetServices<T>()`)

Suitable for: all implementations of an interface need to be invoked (for example, multiple trigger-type services).

```csharp
// Register multiple implementations under the same interface
services.AddSingleton<ITriggerTypeService, AreaTeleportService>();
services.AddSingleton<ITriggerTypeService, AreaPushService>();
services.AddSingleton<ITriggerTypeService, AirWallService>();

// Resolve all implementations
var sp = services.BuildServiceProvider();
foreach (var triggerService in sp.GetServices<ITriggerTypeService>())
{
    triggerService.Install();
    _typeIndex[triggerService.TriggerType] = triggerService;  // Build an index by trigger type
}
```

## 4. Pattern comparison

| Pattern | Best for | Resolution |
|------|---------|---------|
| Factory | choose a strategy by name / config at runtime | `factory.GetService(key)` |
| Keyed Singleton | multiple independently configured instances of the same interface | `sp.GetRequiredKeyedService(key)` |
| `GetServices<T>()` | all implementations must be traversed and invoked | `sp.GetServices<T>()` |

## Checklist

- [ ] Was the correct DI pattern chosen for multiple implementations (factory / keyed / multi-resolve)?
- [ ] Is factory registration completed after `ServiceProvider` has been built?
- [ ] Does batch management isolate exceptions so one failure does not affect others?
- [ ] Do all implementations follow the `Install() / Uninstall()` lifecycle closure?
- [ ] Do keyed services use business-meaningful keys that are unlikely to conflict?
