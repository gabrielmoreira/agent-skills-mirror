# SwiftlyS2 DI / Service Plugin Template

Official docs sections:
- `Dependency Injection`
- `Swiftly Core`
- `Using attributes`

Suitable for: medium-to-large plugins in DI / service-oriented, shared-service-oriented, or hybrid architectures.

## Suggested directory layout

```text
MyPlugin/
├── MyPlugin.cs
├── Interface/
├── Impl/
├── Models/
├── Extensions.cs
└── Config.cs
```

## Basic skeleton

```csharp
using Microsoft.Extensions.DependencyInjection;
using SwiftlyS2.Shared;
using SwiftlyS2.Shared.Plugins;

namespace MyNamespace
{
    [PluginMetadata(
        Id = "MyNamespace.MyPlugin",
        Name = "My Plugin",
        Author = "YourName",
        Version = "1.0.0",
        Description = "Plugin description",
        Website = "https://example.com"
    )]
    public class MyPlugin(ISwiftlyCore core) : BasePlugin(core)
    {
        private IServiceProvider? _serviceProvider;

        public override void Load(bool hotReload)
        {
            var services = new ServiceCollection();
            services.AddSwiftly(Core);
            services.AddSingleton<IMyService, MyService>();

            _serviceProvider = services.BuildServiceProvider();
            _serviceProvider.GetRequiredService<IMyService>().Install();
        }

        public override void Unload()
        {
            if (_serviceProvider?.GetService<IMyService>() is { } service)
            {
                service.Uninstall();
            }
        }
    }
}
```

## Ownership suggestions for modular listeners

- The plugin root should only own `ServiceCollection`, installation order, and unload order.
- Registration and unregistration of `Event` / `GameEvent` / `Hook` / `Command` should preferably be owned by each service itself.
- If a hook is only needed when a specific config is enabled, the service should keep its own boolean flag and dynamically install / uninstall it, instead of leaving it installed forever and idling in the callback.
- The root only orchestrates; each service completes its own listener lifecycle closure.

## Keyed Singleton and multiple implementations

When the same interface has multiple independent instances, use Keyed Singleton:

```csharp
// Register
services.AddKeyedSingleton<IMyService>("VariantA",
    (sp, key) => new MyServiceImpl(core, "VariantA"));
services.AddKeyedSingleton<IMyService>("VariantB",
    (sp, key) => new MyServiceImpl(core, "VariantB"));

// Resolve
var a = sp.GetRequiredKeyedService<IMyService>("VariantA");
var b = sp.GetRequiredKeyedService<IMyService>("VariantB");
```

When all implementations need to be traversed, use `GetServices<T>()`:

```csharp
services.AddSingleton<IMyService, ImplA>();
services.AddSingleton<IMyService, ImplB>();

// Get all
foreach (var svc in sp.GetServices<IMyService>())
{
    svc.Install();
}
```

See also: `../../patterns/service-factory/service-factory-template.cs.md`
