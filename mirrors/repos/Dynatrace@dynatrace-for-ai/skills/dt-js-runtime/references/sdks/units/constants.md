# Units — Constants

Import from `@dynatrace-sdk/units`. Full values: https://developer.dynatrace.com/develop/sdks/units/

| Constant | Purpose |
|---|---|
| `units` | The unit registry, grouped by measurement type — e.g. `units.length.meter`, `units.time.second`, `units.data.mebibyte`, `units.temperature.degree_celsius`. Passed to `convert`/`format`/`variantNames`. |
| `ExponentialDecimalLevels` | Decimal (base-1000) prefix levels (`k`, `M`, `G`, `T`, …) for `abbreviateNumber`. |
| `ExponentialOctalBitLevels` | Binary (base-1024) bit prefixes (`Kibit`, `Mibit`, …). |
| `ExponentialOctalByteLevels` | Binary (base-1024) byte prefixes (`KiB`, `MiB`, …). |
| `timeframeTranslations` | Localized strings used by the timeframe formatting helpers. |
