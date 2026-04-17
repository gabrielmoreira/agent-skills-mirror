# SwiftlyS2 Attribute Registration Checklist

Official docs sections:
- `Using attributes`
- `Commands`
- `Core Events`

Use this to confirm whether `[Command]`, `[CommandAlias]`, event attributes, hook attributes, and similar constructs are registered on the correct object.

## Core rules

- By default, attributes only take effect directly on the main class that inherits from `BasePlugin`.
- If attributes are used inside another class, service, or module, call:
  - `Core.Registrator.Register(this)`
- If that object can be unloaded or rebuilt, its lifecycle and registration timing must be checked for compatibility.

## Checklist

- [ ] Is the current attribute located on the plugin’s main class?
- [ ] If it is not on the main class, is `Core.Registrator.Register(this)` called explicitly after instantiation?
- [ ] Can this object be constructed repeatedly? If yes, is duplicate registration prevented?
- [ ] If the attribute is moved into a service or module, is that really more appropriate than programmatic registration?
- [ ] If dynamic start / stop, conditional unload, or precise cleanup is needed, should programmatic registration be used instead of attributes?

## When to prefer attributes

- Small partial plugins
- Commands or listeners with a fixed lifecycle and unconditional registration
- Scenarios with simple entry points and clear structure

## When to prefer programmatic registration

- You need to store `Guid` values and uninstall precisely
- You need config-driven dynamic start / stop
- A service needs to own its own lifecycle
- Registration responsibility and business responsibility should be concentrated in the same owning service
