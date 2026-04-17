# SwiftlyS2 Service Template

Official docs sections:
- `Dependency Injection`
- `Swiftly Core`
- `Thread Safety`

Suitable for: extracting shared business logic, integrating external dependencies, reusing capabilities across modules, and building the service layer in DI / service or hybrid architectures.

## Suggested directory layout

```text
Interface/
└── IMyFeatureService.cs

Impl/
└── MyFeatureService.cs
```

## Interface example

```csharp
namespace MyNamespace.Interface;

public interface IMyFeatureService
{
    void Install();
    void Uninstall();
    bool TryHandlePlayerAction(ulong steamId);
}
```

## Implementation example

```csharp
using System;
using Microsoft.Extensions.Logging;
using MyNamespace.Interface;
using SwiftlyS2.Shared;
using SwiftlyS2.Shared.Commands;
using SwiftlyS2.Shared.Events;
using SwiftlyS2.Shared.Misc;

namespace MyNamespace.Impl;

public sealed class MyFeatureService(ISwiftlyCore core, ILogger<MyFeatureService> logger) : IMyFeatureService
{
    private readonly ISwiftlyCore _core = core;
    private readonly ILogger<MyFeatureService> _logger = logger;
    private bool _installed;
    private bool _eventHooked;
    private Guid _commandGuid;
    private Guid _clientCommandHookGuid;

    public void Install()
    {
        if (_installed)
        {
            return;
        }

        _core.Event.OnConVarValueChanged += OnConVarValueChanged;
        _commandGuid = _core.Command.RegisterCommand("myfeature", OnMyFeatureCommand, helpText: "MyFeatureService command");
        _clientCommandHookGuid = _core.Command.HookClientCommand(OnClientCommand);
        _installed = true;
        _logger.LogInformation("MyFeatureService installed.");
    }

    public void Uninstall()
    {
        if (!_installed)
        {
            return;
        }

        _core.Event.OnConVarValueChanged -= OnConVarValueChanged;
        _core.Command.UnregisterCommand(_commandGuid);
        _core.Command.UnhookClientCommand(_clientCommandHookGuid);
        UnhookRuntimeEvent();
        _installed = false;
        _logger.LogInformation("MyFeatureService uninstalled.");
    }

    public bool TryHandlePlayerAction(ulong steamId)
    {
        return _installed;
    }

    private void OnConVarValueChanged(IOnConVarValueChanged @event)
    {
        EnsureRuntimeEventHooked();
    }

    private void EnsureRuntimeEventHooked()
    {
        if (_eventHooked)
        {
            return;
        }

        _core.Event.OnClientProcessUsercmds += OnClientProcessUsercmds;
        _eventHooked = true;
    }

    private void UnhookRuntimeEvent()
    {
        if (!_eventHooked)
        {
            return;
        }

        _core.Event.OnClientProcessUsercmds -= OnClientProcessUsercmds;
        _eventHooked = false;
    }

    private void OnClientProcessUsercmds(IOnClientProcessUsercmdsEvent @event)
    {
    }

    private void OnMyFeatureCommand(ICommandContext context)
    {
    }

    private HookResult OnClientCommand(int playerId, string commandLine)
    {
        return HookResult.Continue;
    }
}
```

## Checklist

- Is there a clear interface boundary?
- Is there an `Install / Uninstall` or `Initialize / Cleanup` lifecycle closure?
- Does the owning service register and clean up its own commands, events, and hooks?
- Does it avoid holding invalidatable `IPlayer` / entity wrappers for too long?
