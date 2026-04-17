# SwiftlyS2 Attribute Command Template

Official docs sections:
- `Commands`
- `Using attributes`
- `Thread Safety`

Suitable for: partial / small plugins that use `[Command]` and `[CommandAlias]` to declare fixed command entry points.

## Usage principles

- The command layer should own the entry point, permissions, argument validation, and player feedback.
- Complex business logic should be pushed down into modules or services.
- If the feature later needs dynamic install / uninstall, conditional start / stop, or precise cleanup, consider switching to programmatic registration.

## Critical constraints

### Handler return type must be `void`

The `[Command]` attribute handler signature is **`void OnMyCommand(ICommandContext context)`**. It must **not** be `async ValueTask`, `async Task`, or any other async return type. The underlying delegate type is `delegate void CommandListener(ICommandContext context);`. If you need to perform async work inside a command handler, you may fire-and-forget an async method from within the `void` handler body, but the handler entry point itself must remain `void`.

### `CommandAlias` is a shorter alias, not a prefixed variant

`[CommandAlias("mc")]` registers **an alternative name** that players can type instead of the full command (e.g., `!mc` instead of `!mycommand`). It is **not** used to add framework prefixes like `sw_` or namespace groupings. Aliases should be short, memorable abbreviations of the canonical command name.

## Example skeleton

```csharp
using SwiftlyS2.Shared.Commands;
using SwiftlyS2.Shared.Core.Attributes.Commands;

namespace MyNamespace;

public partial class MyPlugin
{
    [Command("mycommand", permission: "myplugin.commands.use")]
    [CommandAlias("mc")]
    public void OnMyCommand(ICommandContext context)
    {
        if (!context.IsSentByPlayer || context.Sender is null || !context.Sender.IsValid)
        {
            context.Reply("[Plugin] This command can only be executed by a valid player.");
            return;
        }

        var args = context.Arguments;
        if (args.Count < 2)
        {
            context.Reply("[Plugin] Invalid arguments. Please check the input format.");
            return;
        }

        var parsedArg = args[1].Trim();
        if (string.IsNullOrWhiteSpace(parsedArg))
        {
            context.Reply("[Plugin] The argument cannot be empty.");
            return;
        }

        var success = _myFeatureService.TryHandlePlayerAction(context.Sender.SteamID, parsedArg);
        if (!success)
        {
            context.Reply("[Plugin] This operation cannot be executed right now.");
            return;
        }

        context.Reply("[Plugin] Operation completed successfully.");
    }
}
```

## Checklist

- Is the handler return type `void` (not `async ValueTask`, `async Task`, or any other async return type)?
- Are `[Command]` / `[CommandAlias]` being used appropriately instead of mistakenly using programmatic registration?
- Is `[CommandAlias]` used only for short alternative names, not for framework prefixes or namespace markers?
- Are `context.IsSentByPlayer`, `context.Sender`, and `Sender.IsValid` validated first?
- Are the permission semantics and alias semantics preserved?
- Does the command entry avoid directly writing cross-module internal state?
