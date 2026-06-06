# Formatting & Display Options

## Table of Contents
- [Number Format Specifiers](#number-format-specifiers)
- [Standard Format Patterns](#standard-format-patterns)
- [Custom Format Examples](#custom-format-examples)
- [Placeholder Text](#placeholder-text)
- [Culture-Aware Formatting](#culture-aware-formatting)
- [Decimal Digit Management](#decimal-digit-management)
- [Percentage Display Modes](#percentage-display-modes)

## Number Format Specifiers

The `CustomFormat` property uses .NET standard numeric format specifiers. Use format codes to customize how numbers display.

### Standard Format Codes

| Code | Name | Example | Output |
|------|------|---------|--------|
| `C` | Currency | `C2` | $1,234.57 |
| `P` | Percent | `P2` | 123.46% |
| `N` | Number | `N2` | 1,234.57 |
| `F` | Fixed-point | `F2` | 1234.57 |
| `E` | Scientific | `E2` | 1.23E+003 |
| `G` | General | `G` | 1234.57 |
| `X` | Hexadecimal | `X` | 4D2 |

### Format Specifier Syntax

Format specifier consists of:
1. **Format character** (C, P, N, etc.)
2. **Precision specifier** (number of decimal places, 0-28)

**Examples:**
- `C2` = Currency with 2 decimal places
- `P1` = Percentage with 1 decimal place
- `N0` = Number with 0 decimal places

## Standard Format Patterns

### Currency Formatting

**Display prices in the current culture:**

```xaml
<!-- Default culture currency (e.g., US: $1,234.57) -->
<editors:SfNumericUpDown 
    Value="1234.57"
    CustomFormat="C2" />

<!-- Currency with specific precision -->
<editors:SfNumericUpDown 
    Value="99.99"
    CustomFormat="C3" />  <!-- Output: $99.990 -->
```

**Real-world examples:**

```xaml
<!-- Stock Price -->
<editors:SfNumericUpDown 
    Value="150.75"
    CustomFormat="C2"
    Placeholder="Stock Price" />

<!-- Product Price (no decimals for certain currencies) -->
<editors:SfNumericUpDown 
    Value="2999"
    CustomFormat="C0"
    Placeholder="Price" />
```

### Percentage Formatting

**Display percentages:**

```xaml
<editors:SfNumericUpDown 
    Value="25"
    CustomFormat="P2" />
```

**Output:** `25.00%`

```xaml
<!-- Discount percentage with 0 decimals -->
<editors:SfNumericUpDown 
    Value="15"
    CustomFormat="P0" />
```

**Output:** `15%`

### Decimal Number Formatting

**General numeric formatting:**

```xaml
<!-- 2 decimal places with thousands separator -->
<editors:SfNumericUpDown 
    Value="1234.5"
    CustomFormat="N2" />
```

**Output:** `1,234.50`

```xaml
<!-- No decimal places -->
<editors:SfNumericUpDown 
    Value="1234.5"
    CustomFormat="N0" />
```

**Output:** `1,235` (rounded)

## Custom Format Examples

### Using Format Specifiers (0 and #)

- **`0`** (Zero placeholder): Always shows the digit; pads with zeros if needed
- **`#`** (Digit placeholder): Shows the digit only if present; no padding

### Example 1: Phone Number Format
```csharp
// Note: NumericUpDown works with numbers, not strings
// For phone numbers, consider TextBox with InputMask

// But for numeric IDs padded with zeros:
var id = new SfNumericUpDown
{
    Value = 123,
    CustomFormat = "000000"  // Output: 000123
};
```

### Example 2: Currency with Custom Symbol
```xaml
<!-- Custom currency format with $ symbol -->
<editors:SfNumericUpDown 
    Value="1500.50"
    CustomFormat="$##,##0.00" />
```

**Output:** `$1,500.50`

```xaml
<!-- Euro currency -->
<editors:SfNumericUpDown 
    Value="1500.50"
    CustomFormat="€##,##0.00" />
```

**Output:** `€1,500.50`

### Example 3: Fixed Decimal Places
```xaml
<!-- Always show exactly 3 decimal places -->
<editors:SfNumericUpDown 
    Value="10.5"
    CustomFormat="0.000" />
```

**Output:** `10.500`

```xaml
<!-- Minimum 2, maximum 4 decimal places -->
<editors:SfNumericUpDown 
    Value="10.123"
    CustomFormat="0.00##" />
```

**Output:** `10.123`

### Example 4: Percentage with Symbol
```xaml
<!-- Percentage format with custom symbol -->
<editors:SfNumericUpDown 
    Value="75"
    CustomFormat="0.00%" />
```

**Output:** `75.00%`

### Example 5: Large Numbers with Grouping
```xaml
<!-- Million/Thousand formatting -->
<editors:SfNumericUpDown 
    Value="1234567.89"
    CustomFormat="#,##0.00" />
```

**Output:** `1,234,567.89`

## Placeholder Text

### Basic Placeholder
Display helpful hint text when field is empty:

```xaml
<editors:SfNumericUpDown 
    AllowNull="True"
    Placeholder="Enter amount..." />
```

### Placeholder with Color
Customize placeholder text appearance:

```xaml
<editors:SfNumericUpDown 
    AllowNull="True"
    Placeholder="Optional value"
    PlaceholderColor="Gray" />
```

### Practical Placeholder Examples

```xaml
<!-- Currency input -->
<editors:SfNumericUpDown 
    Placeholder="$0.00"
    CustomFormat="C2"
    AllowNull="True" />

<!-- Percentage input -->
<editors:SfNumericUpDown 
    Placeholder="0-100%"
    CustomFormat="P0"
    Minimum="0"
    Maximum="100" />

<!-- Age input -->
<editors:SfNumericUpDown 
    Placeholder="Age (0-150)"
    Minimum="0"
    Maximum="150" />

<!-- Rating input -->
<editors:SfNumericUpDown 
    Placeholder="1-5 stars"
    Minimum="1"
    Maximum="5"
    IsEditable="False"
    SmallChange="1" />
```

## Culture-Aware Formatting

Display numbers according to specific cultural conventions:

### Using System Culture
```csharp
using System.Globalization;

var numericUpDown = new SfNumericUpDown
{
    Value = 1234.56,
    CustomFormat = "C2",
    Culture = new CultureInfo("en-US")  // US: $1,234.56
};
```

### Different Culture Examples
```csharp
// German (Germany): 1.234,56 €
var germanic = new SfNumericUpDown
{
    Value = 1234.56,
    CustomFormat = "C2",
    Culture = new CultureInfo("de-DE")
};

// French (France): 1 234,56 €
var french = new SfNumericUpDown
{
    Value = 1234.56,
    CustomFormat = "C2",
    Culture = new CultureInfo("fr-FR")
};

// Japanese: ￥1,235
var japanese = new SfNumericUpDown
{
    Value = 1234.56,
    CustomFormat = "C0",
    Culture = new CultureInfo("ja-JP")
};
```

### XAML with Culture Binding
```xaml
<editors:SfNumericUpDown 
    Value="1234.56"
    CustomFormat="C2"
    Culture="{Binding CurrentCulture}" />
```

**ViewModel:**
```csharp
public class MainViewModel
{
    public CultureInfo CurrentCulture { get; set; } = 
        CultureInfo.CurrentCulture;
}
```

## Decimal Digit Management

### MaximumNumberDecimalDigits Property

Limit the number of decimal places displayed (only works without `CustomFormat`):

```xaml
<!-- Allow max 3 decimal places -->
<editors:SfNumericUpDown 
    Value="1000.23232"
    MaximumNumberDecimalDigits="3" />
```

**Output:** `1000.232`

**Important:** 
- Only applies when `CustomFormat` is `null`
- Default value: `2`
- Must be positive (0-28)
- If `CustomFormat` is set, `MaximumNumberDecimalDigits` is ignored

### Comparison: MaximumNumberDecimalDigits vs CustomFormat

```xaml
<!-- Using MaximumNumberDecimalDigits -->
<editors:SfNumericUpDown 
    Value="10.123456"
    MaximumNumberDecimalDigits="2" />
<!-- Output: 10.12 -->

<!-- Using CustomFormat (more flexible) -->
<editors:SfNumericUpDown 
    Value="10.123456"
    CustomFormat="N2" />
<!-- Output: 10.12 -->

<!-- CustomFormat with variable decimals -->
<editors:SfNumericUpDown 
    Value="10.123456"
    CustomFormat="0.00##" />
<!-- Output: 10.1235 (min 2, max 4 decimals) -->
```

### When to Use Which?

| Use Case | Recommendation |
|----------|-----------------|
| Simple decimal limit | `MaximumNumberDecimalDigits` |
| Currency/percentage | `CustomFormat` |
| Custom symbols/groups | `CustomFormat` |
| Culture-aware format | `CustomFormat` + `Culture` |

## Percentage Display Modes

Control how percentage values are displayed:

### PercentDisplayMode.Value (Default)
Display the actual numeric value with % symbol:

```xaml
<editors:SfNumericUpDown 
    Value="1000"
    CustomFormat="P"
    PercentDisplayMode="Value" />
```

**Output:** `1000%`

**Use when:** Storing actual percentage values (e.g., 25% stored as 25)

### PercentDisplayMode.Compute
Display the computed percentage value with % symbol:

```xaml
<editors:SfNumericUpDown 
    Value="1000"
    CustomFormat="P"
    PercentDisplayMode="Compute" />
```

**Output:** `100000%` (1000 × 100 = 100,000%)

**Use when:** Converting decimal values to percentages (e.g., 0.25 stored as 25%)

### Practical Percentage Examples

**Example 1: Discount Percentage**
```xaml
<!-- User enters discount % directly (25 = 25%) -->
<editors:SfNumericUpDown 
    Value="25"
    Minimum="0"
    Maximum="100"
    CustomFormat="P0"
    PercentDisplayMode="Value" />
```

**Example 2: Probability/Ratio**
```xaml
<!-- User enters ratio (0.5 = 50%) -->
<editors:SfNumericUpDown 
    Value="0.5"
    Minimum="0"
    Maximum="1"
    CustomFormat="P2"
    PercentDisplayMode="Compute" />
```

**Example 3: Interest Rate**
```xaml
<!-- Bank interest rate (3.5 = 3.5%) -->
<editors:SfNumericUpDown 
    Value="3.5"
    CustomFormat="0.00%"
    PercentDisplayMode="Value" />
```

---
