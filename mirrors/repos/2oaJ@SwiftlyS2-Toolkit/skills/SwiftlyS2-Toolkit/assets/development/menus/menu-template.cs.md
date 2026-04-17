# SwiftlyS2 Menu Template

Official docs sections:
- `Menus`
- `Thread Safety`
- `HTML Styling`

> Notes: official docs examples often use `Core.Menus`; if the current project exposes `IMenuManagerAPI` through `Core.MenusAPI`, follow the actual Core property used by the current project.

## Design highlights

- Menu entry methods should only validate and open the menu, not accumulate business details.
- Prefer splitting submenus into standalone `BuildXxxMenuAsync` / `GetXxxMenu` methods.
- `BindingText` is a high-priority capability: for dynamic text, prefer binding instead of manually refreshing `Text`.
- Treat `Click`, `ValueChanged`, and `Submenu` delegates as async-context code.
- In async contexts, prefer existing `Async` APIs instead of defaulting to `NextTick` / `NextWorldUpdate`.
- State reads and writes should be pushed down into services, modules, or runtime contexts where possible.

## Template skeleton

```csharp
using SwiftlyS2.Core.Menus;
using SwiftlyS2.Shared.Menus;

public partial class ExamplePlugin
{
    public async Task OpenSettingsMenuAsync(IPlayer player)
    {
        if (player == null || !player.IsValid)
        {
            return;
        }

        var menu = await BuildSettingsMenuAsync(player);
        if (menu == null)
        {
            return;
        }

        Core.MenusAPI.OpenMenuForPlayer(player, menu);
    }

    private async Task<IMenuAPI?> BuildSettingsMenuAsync(IPlayer player)
    {
        if (player == null || !player.IsValid)
        {
            return null;
        }

        var runtime = await _settingsService.GetPlayerSettingsAsync(player);
        if (runtime == null)
        {
            return null;
        }

        var menu = Core.MenusAPI.CreateBuilder()
            .Design.SetMenuTitle("Example Settings")
            .EnableSound()
            .SetPlayerFrozen(false)
            .Build();

        var txtSummary = new TextMenuOption
        {
            BindingText = () => $"Current style: {runtime.SelectedStyle} | Volume: {runtime.Volume} | Feature: {(runtime.Enabled ? "On" : "Off")}" 
        };
        menu.AddOption(txtSummary);

        var toggleEnable = new ToggleMenuOption("Feature Toggle", runtime.Enabled, onText: "On", offText: "Off");
        toggleEnable.ValueChanged += async (_, args) =>
        {
            if (args.Player == null || !args.Player.IsValid)
            {
                return;
            }

            await _settingsService.SetEnabledAsync(args.Player, args.NewValue);
            runtime.Enabled = args.NewValue;
            await args.Player.SendMessageAsync(MessageType.Chat, $"{{green}}[Settings]{{default}} Feature {(args.NewValue ? "enabled" : "disabled")}");
        };
        menu.AddOption(toggleEnable);

        var btnSave = new ButtonMenuOption("Save Settings") { CloseAfterClick = true };
        btnSave.Click += async (_, args) =>
        {
            if (args.Player == null || !args.Player.IsValid)
            {
                return;
            }

            await _settingsService.SaveAsync(args.Player, runtime.SelectedStyle, runtime.Volume, runtime.Enabled);
            await args.Player.SendMessageAsync(MessageType.Chat, "{green}[Settings]{default} Your settings have been saved.");
        };
        menu.AddOption(btnSave);

        return menu;
    }
}
```

## Menu implementation checkpoints

- Was `BindingText` evaluated first?
- Are callbacks handled as async-context logic?
- Is `player.IsValid` rechecked in every callback?
- Are heavy IO, blocking work, and excessive allocations avoided inside menu callbacks?
- Is actual state write-back kept inside services or runtime contexts?

## Advanced menu patterns

### Dynamic countdown with BindingText

```csharp
var btnTimer = new TextMenuOption
{
    BindingText = () =>
    {
        var remaining = _deadline - DateTime.Now;
        return remaining.TotalSeconds > 0
            ? $"Time remaining: {remaining.TotalSeconds:0.0} seconds"
            : "Expired";
    }
};
menu.AddOption(btnTimer);
```

### Tag-based data association

Use the `Tag` property to associate menu options with business data objects so callbacks and statistics are easier to implement:

```csharp
foreach (var item in availableItems)
{
    var btn = new TextMenuOption { Text = item.DisplayName, Tag = item };
    btn.Click += async (sender, args) =>
    {
        if (sender is MenuOptionBase option && option.Tag is MyItem selectedItem)
        {
            await ProcessSelection(args.Player, selectedItem);
        }
    };
    menu.AddOption(btn);
}
```

### Real-time vote-count updates

In voting scenarios, update the displayed vote count of all options after a selection:

```csharp
btn.Click += async (sender, args) =>
{
    _votes.AddOrUpdate(steamId, selectedItem, (_, __) => selectedItem);

    // Update the display text of all options
    foreach (var option in menu.Options)
    {
        if (option.Tag is MyItem tagItem)
        {
            var count = _votes.Count(x => x.Value == tagItem);
            option.Text = $"[{count}] {tagItem.DisplayName}";
        }
    }
};
```

### ConfirmMenu (confirmation dialog)

The official API achieves async waiting through `CreateBuilder()` + `OpenMenuForPlayer(player, menu, onClosed)` + `TaskCompletionSource`:

```csharp
private async Task<bool> OpenConfirmMenuAsync(IPlayer player, string message)
{
    var tcs = new TaskCompletionSource<bool>();

    var menu = Core.MenusAPI.CreateBuilder()
        .Design.SetMenuTitle("Please confirm")
        .EnableSound()
        .SetPlayerFrozen(false)
        .Build();


    menu.Tag = false; // Use Tag as the result container

    menu.AddOption(new TextMenuOption(message));

    var btnOK = new ButtonMenuOption("Confirm") { CloseAfterClick = true };
    btnOK.Click += async (sender, args) =>
    {
        if (args.Player?.IsValid == true)
            menu.Tag = true;
    };
    menu.AddOption(btnOK);

    var btnCancel = new ButtonMenuOption("Cancel") { CloseAfterClick = true };
    menu.AddOption(btnCancel);

    Core.MenusAPI.OpenMenuForPlayer(player, menu, (_player, _menu) =>
    {
        // Note: Tag must be exclusively owned by this method and must not be overwritten externally after Build()
        tcs.TrySetResult((bool)_menu.Tag!);
    });

    return await tcs.Task;
}

// Call site
var confirmed = await OpenConfirmMenuAsync(player, "Are you sure you want to perform this action?");
if (confirmed)
{
    await ExecuteDangerousAction(player);
}
```

> Tip: if timeout handling is needed, start `Task.Delay(timeoutMs)` together with the wait and race it against `tcs.Task` using `Task.WhenAny`.

### Cross-plugin menu jump

Use `ExecuteCommand` for a loosely coupled jump into another plugin’s menu:

```csharp
var btnSkin = new ButtonMenuOption("Character Skin Menu") { CloseAfterClick = true };
btnSkin.Click += async (sender, args) =>
{
    Core.Scheduler.NextWorldUpdate(() =>
    {
        args.Player.ExecuteCommand("sw_skin");
    });
};
menu.AddOption(btnSkin);
```

### InputMenuOption (text input)

Menu option that allows players to enter text:

```csharp
var inputOption = new InputMenuOption("Enter Name");
inputOption.ValueChanged += async (sender, args) =>
{
    if (args.Player is null || !args.Player.Valid()) return;
    var inputText = args.NewValue?.Trim();
    if (string.IsNullOrWhiteSpace(inputText)) return;

    await ProcessInput(args.Player, inputText);
};
menu.AddOption(inputOption);
```
