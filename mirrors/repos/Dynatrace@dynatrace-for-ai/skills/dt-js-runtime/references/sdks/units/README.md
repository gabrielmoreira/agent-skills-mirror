# Units (`@dynatrace-sdk/units`)

> Env: ✅ Server runtime (pure functions — work anywhere)
> Status: current

Convert, format, and parse units, numbers, and dates. Part of the generic/utility layer.

## Key exports

| Function | Purpose |
|---|---|
| `convert(value, from, to)` | Convert between compatible units |
| `format(value, { input })` | Format a number with its unit |
| `formatCurrency(...)` | Currency-aware formatting (ISO codes) |
| `formatDate(...)` | Locale/timezone-aware dates |
| `abbreviateNumber(...)` | Shorten large numbers ("1.5K") |
| `parseTimeAsTimeValue(...)` | Parse "now-30m" / ISO 8601 |
| `variantUnits()` / `variantNames()` | Discover convertible units |

The `units` constant groups supported measurements (length, mass, time, temperature, data, velocity, pressure, energy, …).

Full detail: [functions.md](functions.md) (all convert/format/parse helpers + examples) · [constants.md](constants.md) (`units`, exponential levels, `timeframeTranslations`) · [types.md](types.md) (`FormatOptions`, `FormatCurrencyOptions`, `FormatDateOptions`, `TimeValue`, …). Pure functions — no clients, no scopes.

## Example

```ts
import { convert, format, units } from "@dynatrace-sdk/units";

convert(1500, units.length.meter, units.length.kilometer); // 1.5
format(1200, { input: units.data.byte }); // "1.17 KiB"
```

Canonical reference: https://developer.dynatrace.com/develop/sdks/units/
