# Units — Functions

Import from `@dynatrace-sdk/units`.

## Number & unit formatting

| Function | Purpose | Example → result |
|---|---|---|
| `convert(value, input, output, unsafe?)` | Convert a value between units of the same measurement system | `convert(1500, units.length.meter, units.length.kilometer)` → `1.5` |
| `format(value, options?)` | Convert + format a number with `FormatOptions` (input/output unit, cascade, fraction/significant digits, abbreviate, locale, suffix) | `format(1500, { input: units.length.meter, maximumFractionDigits: 1 })` → `'1.5 km'` |
| `getFormatting(value, options?)` | Like `format` but returns constituent parts (`value`, `symbol`, `separator`, `symbolPrefix`) | `getFormatting(1500, { input: units.length.meter })` → `[{ value:'1.5', symbol:'km', … }]` |
| `formatUnit(unit)` | Format a unit descriptor array into a human-readable symbol | `formatUnit([{group:'meter',index:3,exponent:1}])` → `'km'` |
| `abbreviateNumber(value, levels?, options?)` | Abbreviate large numbers with metric/binary prefixes; returns `{ formattedValue, postfix }` | `abbreviateNumber(1048576, ExponentialOctalByteLevels)` → `{ formattedValue:'1', postfix:'MiB' }` |
| `adjustFractionDigits(value, options?)` | Precise decimal/significant-digit formatting; prefixes tiny values with `< `/`> ` | `adjustFractionDigits(0.0000001, { maximumFractionDigits: 3 })` → `'< 0.001'` |
| `formatLong(value, options?)` | Format large numbers / `bigint` / numeric strings precisely | `formatLong(BigInt('9007199254740991'))` → `'9,007,199,254,740,991'` |
| `formatCurrency(value, currency, options?)` | Locale-aware currency formatting | `formatCurrency(1500, 'USD')` → `'$1.50K'` |
| `mapGrailUnit(grailUnit)` | Map a Grail unit string to the units-system equivalent (`unit`, `type`, `base`) | `mapGrailUnit('BytePerSecond')` → datarate `Bps` descriptor |
| `variantNames(unit)` | Names of all units the given unit can convert to | `variantNames(units.length.meter)` → `['meter','kilometer',…]` |
| `variantUnits(unit)` | Unit descriptors the given unit can convert to (descriptor form of `variantNames`) | — |

## Date & timeframe formatting

| Function | Purpose | Example → result |
|---|---|---|
| `formatDate(date, options?)` | Format a Date / epoch-ms per locale + timezone (`FormatDateOptions`) | `formatDate(new Date(), { locale:'de-DE', dateStyle:'full' })` → `'Dienstag, 27. Mai 2025'` |
| `formatTimeframe(tf, intl, precision?)` | Human-readable timeframe from `{from,to}` strings/`TimeValue`s | `formatTimeframe({from:'now-1h',to:'now'}, intl)` → `{ displayValue:'Last 1 hour', … }` |
| `formatTimeframeToParts(from, to, intl, clampFutureToDateToNow?)` | Localized `[from, separator, to]` array; clamps future `to` to "Now" | → `["01 Jan, 2020, 00:00","to","Now"]` |
| `formatTimeValues(from, to, intl, precision, …)` | Display props for two `TimeValue`s incl. relative expressions | → `{ displayValue:'Last 5 minutes', isInvalid:false, hint:'' }` |
| `extractDisplayValueFromTimeValues(from, to, intl, precision)` | Higher-level wrapper around `formatTimeValues` that parses + validates | → `{ displayValue:'Last 1 hour', … }` |
| `parseTimeAsTimeValue(input, precision?)` | Parse ISO 8601 / relative (`now-30m`) / date / `now` into a `TimeValue` (`type`,`value`,`absoluteDate`) | — |
| `parseTime(input, precision?)` | ⚠️ Deprecated — use `parseTimeAsTimeValue`. Returns a `TimeDetails` (`normalized`,`date`,`type`) | — |

## Example

```ts
import { convert, format, formatDate, units } from "@dynatrace-sdk/units";

convert(3600, units.time.second, units.time.hour);          // 1
format(1500, { input: units.length.meter, cascade: 2 });    // '1 km 500 m'
formatDate(1621344000000, { dateStyle: "short", timeStyle: "short" }); // '5/27/25, 2:30 PM'
```
