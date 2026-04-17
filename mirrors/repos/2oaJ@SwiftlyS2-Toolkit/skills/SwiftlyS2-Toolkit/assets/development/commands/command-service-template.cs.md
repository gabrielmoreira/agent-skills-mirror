# SwiftlyS2 Service-Owned Command Template

Official docs sections:
- `Commands`
- `Dependency Injection`
- `Thread Safety`

Suitable for: scenarios where a service owns the lifecycle of commands, aliases, client-chat hooks, or client-command hooks itself.

## Usage principles

- The root should assemble the service, not manage local command handles on its behalf.
- Whatever the service registers must be unregistered by that same service.
- Prefer this pattern when dynamic start / stop, stored `Guid` values, or conditional install / uninstall are required.

## Example skeleton

```csharp
using System;
using SwiftlyS2.Shared;
using SwiftlyS2.Shared.Commands;
using SwiftlyS2.Shared.Misc;

namespace MyNamespace.Impl;

public sealed class MyCommandService(ISwiftlyCore core) : IMyCommandService
{
    private Guid _commandGuid;
    private Guid _clientChatHookGuid;
    private bool _installed;

    public void Install()
    {
        if (_installed)
        {
            return;
        }

        _commandGuid = core.Command.RegisterCommand(
            "mycommand",
            OnMyCommand,
            registerRaw: false,
            permission: "myplugin.commands.use",
            helpText: "My module command");

        core.Command.RegisterCommandAlias("mycommand", "mc");
        _clientChatHookGuid = core.Command.HookClientChat(OnClientChat);
        _installed = true;
    }

    public void Uninstall()
    {
        if (!_installed)
        {
            return;
        }

        core.Command.UnregisterCommand(_commandGuid);
        core.Command.UnhookClientChat(_clientChatHookGuid);
        _installed = false;
    }

    private void OnMyCommand(ICommandContext context)
    {
        context.Reply("[Plugin] Command triggered.");
    }

    private HookResult OnClientChat(int playerId, string text, bool teamonly)
    {
        return HookResult.Continue;
    }
}
```

## Checklist

- Does the owning service store the `Guid` values and reclaim them precisely in `Uninstall()`?
- Is an independent lifecycle or dynamic start / stop actually required?
- Are command implementation and command registration closed within the same service?
- Does it distinguish the different uninstall paths of `RegisterCommandAlias`, `HookClientChat`, and `HookClientCommand`?
