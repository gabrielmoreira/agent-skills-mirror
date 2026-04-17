# SwiftlyS2 OnPrecacheResource Template

Official docs section:
- `Core Events`

Suitable for: precaching models, sounds, particles, and similar resources so they are available at runtime.

## Why precache is needed

In Source 2, resources such as models, particles, and sound events must be precached before use.
Resources that were not precached may silently fail or crash when used through calls such as `SetModel` or `EmitSound`.

## Basic pattern

```csharp
[EventListener<OnPrecacheResource>]
public void OnPrecacheResource(IOnPrecacheResourceEvent @event)
{
    // Static resources
    @event.AddItem("characters/models/my_custom_model.vmdl");
    @event.AddItem("soundevents/soundevents_custom.vsndevts");
    @event.AddItem("particles/my_particle_effect.vpcf");
}
```

## Config-driven dynamic precache

When resource paths come from a config file or database, they need to be precached dynamically:

```csharp
[EventListener<OnPrecacheResource>]
public void OnPrecacheResource(IOnPrecacheResourceEvent @event)
{
    // Collect all model paths from config
    foreach (var skin in Config.Skins)
    {
        if (!string.IsNullOrWhiteSpace(skin.ModelPath))
            @event.AddItem(skin.ModelPath);

        if (!string.IsNullOrWhiteSpace(skin.SoundPath))
            @event.AddItem(skin.SoundPath);
    }
}
```

## Service-delegated precache

When multiple services each have resources that need to be precached:

```csharp
[EventListener<OnPrecacheResource>]
public void OnPrecacheResource(IOnPrecacheResourceEvent @event)
{
    // Shared entry resource
    @event.AddItem("soundevents/soundevents_plugin.vsndevts");

    // Delegate to services managed by the factory
    if (_serviceProvider is not null)
    {
        foreach (var service in _serviceProvider.GetServices<IMyService>())
        {
            try
            {
                service.OnPrecacheResource(@event);
            }
            catch (Exception ex)
            {
                Logger.LogError(ex, "Failed to precache resources - service: {Service}", service.GetType().Name);
            }
        }
    }
}
```

## Key points

- `OnPrecacheResource` fires early during map load, and some services may not be fully initialized yet.
- Resource path strings must exactly match the real in-game path.
- Adding the same path repeatedly is safe because the engine deduplicates it.
- When config-driven resource lists change, the change only takes effect on the next map load.
- Do not perform IO or blocking work in this event.

## Checklist

- [ ] Are all custom models used by the plugin registered in `OnPrecacheResource`?
- [ ] Are sound event files (`.vsndevts`) registered?
- [ ] Are particle effects (`.vpcf`) registered?
- [ ] Are config-driven dynamic resources iterated and registered?
- [ ] Is service-delegated precache protected against exceptions?
