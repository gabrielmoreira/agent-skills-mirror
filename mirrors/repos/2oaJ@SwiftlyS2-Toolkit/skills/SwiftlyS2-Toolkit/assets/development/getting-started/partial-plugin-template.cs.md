# SwiftlyS2 Traditional Modular Plugin Template

Official docs sections:
- `Getting Started`
- `Swiftly Core`
- `Using attributes`

Suitable for: gameplay-oriented modular plugins that need `Commands / Events / Hooks / Modules / Workers`.

## Suggested directory layout

```text
MyPlugin/
├── MyPlugin.cs
├── MyPlugin.Commands.cs
├── MyPlugin.Events.cs
├── MyPlugin.GameEvents.cs
├── MyPlugin.Functions.cs
├── Modules/
├── Workers/
├── Models/
├── Players/
├── Interfaces/
└── Helpers/
```

## Basic skeleton

```csharp
using Microsoft.Extensions.Logging;
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
    public partial class MyPlugin(ISwiftlyCore core) : BasePlugin(core)
    {
        public override void Load(bool hotReload)
        {
            Core.Logger.LogInformation("MyPlugin loaded.");
        }

        public override void Unload()
        {
            Core.Logger.LogInformation("MyPlugin unloaded.");
        }
    }
}
```

## Constraints

- Do not pile business logic directly into commands, events, or hooks; prefer pushing it down into modules or services.
- Direct IO is forbidden on high-frequency paths.
- When player runtime state is involved, determine the SSOT object as early as possible.
- In small partial projects, a small number of `Events`, `GameEvents`, and `Hooks` should generally be managed directly with attributes.
- Only upgrade to a service-owned listener pattern when the listener needs independent install / uninstall, dynamic switches, or strong coupling to a DI lifecycle.
