# SwiftlyS2 ClientCommandHookHandler Template

Official docs sections:
- `Commands`
- `Native Functions and Hooks`

Suitable for: intercepting raw commands sent by clients (such as `jointeam` or radio commands) and deciding whether to allow or block them before they enter the normal processing pipeline.

## Suitable scenarios

- Intercept and restrict `jointeam` (for example, prevent non-admins from switching to spectator)
- Intercept and replace radio commands (for example, custom `cheer`, `roger`, and similar behavior)
- Intercept purchase commands
- Any scenario that requires global interception at the command layer

## Basic pattern

```csharp
using SwiftlyS2.Shared.Hooks;

namespace MyNamespace;

public partial class MyPlugin
{
    // 1. Optional: declaratively register the command (to ensure low-level recognition)
    [Command("jointeam", registerRaw: true)]
    public void OnJoinTeamCommand(ICommandContext context) { }

    // 2. Install the global command-interception hook
    [ClientCommandHookHandler]
    public HookResult OnClientCommandHook(int playerId, string commandLine)
    {
        // Fast routing: only handle the commands you care about
        if (!commandLine.StartsWith("jointeam"))
            return HookResult.Continue;

        var player = Core.PlayerManager.GetPlayer(playerId);
        if (player is null || !player.IsValid)
            return HookResult.Continue;

        // Example: prevent non-admins from switching to spectator
        if (commandLine.StartsWith("jointeam 1")
            && !Core.Permission.PlayerHasPermission(player.SteamID, "admin.spectate"))
        {
            player.SendMessage(MessageType.Chat, "[Plugin] Non-admins cannot switch to spectator.");
            return HookResult.Stop;  // Block the command
        }

        return HookResult.Continue;  // Allow it through
    }
}
```

## Multi-command interception pattern

```csharp
private static readonly HashSet<string> InterceptedCommands =
    ["roger", "negative", "cheer", "thanks", "holdpos", "followme"];

[Command("roger", registerRaw: true)]
[CommandAlias("negative", registerRaw: true)]
[CommandAlias("cheer", registerRaw: true)]
[CommandAlias("thanks", registerRaw: true)]
[CommandAlias("holdpos", registerRaw: true)]
[CommandAlias("followme", registerRaw: true)]
public void OnRadioCommand(ICommandContext context) { }

[ClientCommandHookHandler]
public HookResult OnClientCommandHook(int playerId, string commandLine)
{
    // Extract the command name
    var spaceIndex = commandLine.IndexOf(' ');
    var commandName = spaceIndex < 0 ? commandLine : commandLine[..spaceIndex];

    if (!InterceptedCommands.Contains(commandName))
        return HookResult.Continue;

    var player = Core.PlayerManager.GetPlayer(playerId);
    if (player is null || !player.IsValid)
        return HookResult.Continue;

    // Dispatch by command name
    return commandName switch
    {
        "cheer" => HandleCheerCommand(player),
        _ => HookResult.Continue
    };
}
```

## Key points

- `registerRaw: true` ensures the command is recognized at the low level so `ClientCommandHookHandler` can intercept it correctly.
- `HookResult.Stop` completely blocks the command from propagating further.
- `HookResult.Continue` lets the command execute normally.
- `commandLine` is a raw string, so arguments must be parsed manually.
- This hook runs at the earliest stage of the command pipeline, so higher-level wrappers such as `ICommandContext` may not yet be available.
- Intercepting high-frequency commands (such as movement-related commands) requires performance awareness.

## Checklist

- [ ] Are unrelated commands filtered out as early as possible so not every command goes through the full logic?
- [ ] Does the hook validate `player is not null && player.IsValid` first?
- [ ] Have all commands that need `registerRaw: true` been declared?
- [ ] Is `HookResult.Stop` used only in scenarios that truly need interception?
- [ ] Does argument parsing safely handle empty arguments and malformed input?
