# Configuration Entry Notes

Official docs section:
- `Configuration`

Prioritize:
- `Core.Configuration`
- `InitializeJsonWithModel<T>` / `InitializeTomlWithModel<T>`
- `Configure(builder => ...)`
- `IOptionsMonitor<T>`
- `reloadOnChange`

This directory contains:
- `config-hot-reload-template.cs.md`: full template for Config + IOptionsMonitor hot reload

Configuration scenarios are commonly used together with:
- `guides/dependency-injection/di-service-plugin-template.cs.md`
- `guides/dependency-injection/service-template.cs.md`

## Division of responsibility between Config and ConVar

- **Config (JSONC)**: structured configuration, nested objects, arrays, default-value management, and file persistence
- **ConVar**: immediate runtime console tuning and temporary administrator adjustments
- When mixed: use ConVar for switches / fine-tuning, and Config for structured defaults

For ConVar-related guidance, see `../convars/convar-template.cs.md`.
