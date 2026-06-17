# Units — Types

Full field definitions: https://developer.dynatrace.com/develop/sdks/units/#types

| Type | Used by | Key fields |
|---|---|---|
| `FormatOptions` | `format`, `getFormatting` | `cascade`, `input`, `output`, `suffix`, `minimumFractionDigits`, `maximumFractionDigits`, `minimumSignificantDigits`, `maximumSignificantDigits`, `locale`, `useGrouping`, `abbreviate` |
| `AdjustFractionDigitsOptions` | `abbreviateNumber`, `adjustFractionDigits` | `minimumFractionDigits`, `maximumFractionDigits`, `minimumSignificantDigits`, `maximumSignificantDigits`, `roundingMode`, `locale`, `useGrouping` |
| `FormatCurrencyOptions` | `formatCurrency` | `locale`, `abbreviate`, `minimumFractionDigits`, `maximumFractionDigits`, `useGrouping` (+ `Intl.NumberFormat` options) |
| `FormatDateOptions` | `formatDate` | `locale`, `timeZone`, `dateStyle`, `timeStyle`, `hour12` (+ `Intl.DateTimeFormatOptions`) |
| `TimeValue` | parse/format time helpers | `type` (`'expression' \| 'iso8601'`), `value`, `absoluteDate` |
