# SwiftlyS2 Config Hot-Reload Template

Official docs sections:
- `Configuration`
- `Dependency Injection`

Suitable for: any SwiftlyS2 plugin that needs runtime configuration changes to take effect automatically.

## Design highlights

- Use `Core.Configuration.InitializeJsonWithModel<T>()` to initialize configuration.
- Use `IOptionsMonitor<T>.OnChange()` to listen for changes and implement hot reload.
- It is recommended to define the config model in a separate `Config.cs` file.
- JSONC format (`config.jsonc`) supports comments and is easier to maintain.
- Hot-reload callbacks may trigger side effects such as cache refresh, scheduler restart, or state reset.

## Config definition

```csharp
namespace MyNamespace;

public class Config
{
    // Primitive types
    public bool Enabled { get; set; } = true;
    public int MaxRetries { get; set; } = 3;
    public float UpdateInterval { get; set; } = 1.0f;
    public string ServerName { get; set; } = "Default";

    // Arrays / lists
    public string[] AllowedMaps { get; set; } = [];

    // Nested objects
    public RewardConfig Reward { get; set; } = new();
}

public class RewardConfig
{
    public int BaseAmount { get; set; } = 100;
    public float Multiplier { get; set; } = 1.0f;
}
```

## Initialization and hot reload

```csharp
public partial class MyPlugin(ISwiftlyCore core) : BasePlugin(core)
{
    private Config Config { get; set; } = new();

    public override void Load(bool hotReload)
    {
        // 1. Initialize configuration (create the default file + register the change source)
        Core.Configuration.InitializeJsonWithModel<Config>("config.jsonc", "Main")
            .Configure(builder => builder.AddJsonFile("config.jsonc", optional: false, reloadOnChange: true));

        // 2. Get IOptionsMonitor
        // Prerequisite: register it first through ServiceCollection + AddOptionsWithValidateOnStart<Config>().BindConfiguration("Main")
        // For the DI plugin skeleton, see: ../../guides/dependency-injection/di-service-plugin-template.cs.md
        var monitor = ServiceProvider.GetRequiredService<IOptionsMonitor<Config>>();
        Config = monitor.CurrentValue;

        // 3. Register the hot-reload callback
        monitor.OnChange(OnConfigChanged);

        // 4. Initialize feature logic using Config
        if (Config.Enabled)
        {
            StartFeature();
        }
    }

    private void OnConfigChanged(Config newConfig)
    {
        var oldConfig = Config;
        Config = newConfig;

        // Trigger side effects as needed
        if (oldConfig.Enabled != newConfig.Enabled)
        {
            if (newConfig.Enabled)
                StartFeature();
            else
                StopFeature();
        }

        if (Math.Abs(oldConfig.UpdateInterval - newConfig.UpdateInterval) > 0.001f)
        {
            RestartScheduler(newConfig.UpdateInterval);
        }

        Core.Logger.LogInformation("Configuration hot-reloaded.");
    }
}
```

## Checklist

- [ ] Do all fields on the config model have reasonable default values?
- [ ] Is `config.jsonc` used so comments are supported?
- [ ] Are changes monitored through `IOptionsMonitor<T>.OnChange()`?
- [ ] Does the hot-reload callback correctly handle differences between old and new config values?
- [ ] Are complex side effects (such as scheduler restart or cache cleanup) triggered correctly inside the callback?
- [ ] Is blocking IO avoided inside the hot-reload callback?
