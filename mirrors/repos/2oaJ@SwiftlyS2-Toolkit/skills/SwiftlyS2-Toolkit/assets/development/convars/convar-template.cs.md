# SwiftlyS2 ConVar Template

Official docs section:
- `Convars`

Suitable for: server parameters that need to be adjustable at runtime without editing the config file.

## Choosing between ConVar and Config

| Dimension | ConVar | Config (JSONC) |
|------|--------|----------------|
| Change mechanism | Console command / rcon | Edit file and hot-reload automatically |
| Best for | Fast runtime tuning, temporary admin adjustment | Structured config, complex nesting, default-value management |
| Persistence | Requires extra handling (exec/autoexec) | The file itself is persistent |
| Type support | bool/int/float/string | Any C# object |
| Range constraints | Built-in min/max | Must be validated by business logic |

**Rule of thumb**:
- Parameters that admins may tune live in-game → ConVar
- Structured config, arrays, and nested objects → Config
- When mixed, use ConVar for runtime switches / fine-tuning and Config for structured defaults

## Declarative ConVars (partial-file organization recommended)

```csharp
// MyPlugin.ConVars.cs
namespace MyNamespace;

public partial class MyPlugin
{
    // Use required to enforce initialization during Load
    public required IConVar<bool> ConVar_EnableFeature { get; set; }
    public required IConVar<int> ConVar_MaxPlayers { get; set; }
    public required IConVar<float> ConVar_SpeedMultiplier { get; set; }

    private void InitConVars()
    {
        // Basic bool ConVar
        ConVar_EnableFeature = Core.ConVar.CreateOrFind(
            "sw_myplugin_enable",           // ConVar name
            "Enable feature",               // Description
            true,                            // Default value
            ConvarFlags.SERVER_CAN_EXECUTE   // Permission flag
        );

        // int ConVar with range constraints (-1 = unlimited, 0 = disabled, >0 = concrete value)
        ConVar_MaxPlayers = Core.ConVar.CreateOrFind(
            "sw_myplugin_max_players",
            "Maximum player limit (-1 = unlimited)",
            -1,                              // Default value
            -1, 64,                          // min, max
            ConvarFlags.SERVER_CAN_EXECUTE
        );

        // float ConVar
        ConVar_SpeedMultiplier = Core.ConVar.CreateOrFind(
            "sw_myplugin_speed_mult",
            "Speed multiplier",
            1.0f,
            0.1f, 10.0f,
            ConvarFlags.SERVER_CAN_EXECUTE
        );
    }
}
```

## Initialization timing

```csharp
public override void Load(bool hotReload)
{
    InitConVars();
    // ... later read values through ConVar_XXX.Value
}
```

## Reading in business logic

```csharp
// Read the current value directly
if (!ConVar_EnableFeature.Value)
    return;

int limit = ConVar_MaxPlayers.Value;
if (limit >= 0 && currentCount >= limit)
{
    player.SendMessage(MessageType.Chat, "Maximum player limit reached.");
    return;
}

float speed = baseSpeed * ConVar_SpeedMultiplier.Value;
```

## Conventions and range practices

- `-1 = unlimited`, `0 = disabled`, and `>0 = concrete value` are common conventions across the plugin ecosystem and fit scenarios such as purchase limits or quantity caps.

## Module-level self-registration of ConVars

In large modular plugins, each module may create and manage its own ConVars in `OnActivate()`:

```csharp
public class MyModule : IModule
{
    private IConVar<bool>? _enableConVar;

    public void OnActivate()
    {
        // CreateOrFind is idempotent and safe across module reloads
        _enableConVar = Core.ConVar.CreateOrFind(
            "sw_mymodule_enable",
            "Enable this module",
            true,
            ConvarFlags.SERVER_CAN_EXECUTE);
    }
}
```

## Checklist

- [ ] Does the ConVar name follow the `sw_plugin_feature` naming style?
- [ ] Is modification permission restricted through `ConvarFlags.SERVER_CAN_EXECUTE`?
- [ ] Do numeric ConVars with ranges define reasonable min / max values?
- [ ] Is the `required` keyword used to ensure initialization?
- [ ] Are ConVars registered centrally in `Load()` or `OnActivate()`?
- [ ] Are frequent hot-path reads avoided where local caching would be better?
