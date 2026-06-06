# Value Formatting with .NET MAUI NumericEntry

This guide explains how to format numeric values using the CustomFormat property, including currency, percentage, decimal, and custom patterns, along with culture support and precision control.

## Table of Contents
1. [CustomFormat Overview](#customformat-overview)
2. [Currency Formatting](#currency-formatting)
3. [Percentage Formatting](#percentage-formatting)
4. [Decimal Formatting](#decimal-formatting)
5. [Integer Digits Control](#integer-digits-control)
6. [Fractional Digits Control](#fractional-digits-control)
7. [Custom Format Patterns](#custom-format-patterns)
8. [Culture Support and Localization](#culture-support-and-localization)
9. [Percentage Display Modes](#percentage-display-modes)
10. [Maximum Decimal Digits](#maximum-decimal-digits)

---

## CustomFormat Overview

The `CustomFormat` property controls how numeric values are displayed in the NumericEntry control. By default, the value is `null`, which displays the raw number without formatting.

**Key Concepts:**
- CustomFormat affects **display only**, not the underlying value
- Format is applied after validation (on blur or Enter in OnLostFocus mode)
- Supports standard .NET format strings for `double` type
- Can use culture-specific formatting

**Standard Format Specifiers:**
- **C** or **c**: Currency format
- **P** or **p**: Percentage format
- **N** or **n**: Number (decimal) format with thousand separators
- **Custom patterns**: Using 0 and # placeholders

---

## Currency Formatting

Use the **C** format specifier to display values as currency with the appropriate symbol and formatting.

### Basic Currency Formatting

**XAML:**
```xml
<!-- Currency with 2 decimal places (default) -->
<editors:SfNumericEntry Value="1234.56"
                        CustomFormat="C2" />
```

**C#:**
```csharp
SfNumericEntry stockPrice = new SfNumericEntry();
stockPrice.CustomFormat = "C2";
stockPrice.Value = 1234.56;
```

**Output:** `$1,234.56` (in US culture)

**Why C2:**
- C = Currency format
- 2 = Two decimal places (cents)
- Automatically adds currency symbol and thousand separators

### Currency Format Variations

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <!-- No decimal places (whole currency) -->
    <Label Text="C0 - Whole Dollars:" />
    <editors:SfNumericEntry Value="1234.56"
                            CustomFormat="C0" />
    <!-- Output: $1,235 (rounded) -->
    
    <!-- 2 decimal places (standard) -->
    <Label Text="C2 - Standard Currency:" />
    <editors:SfNumericEntry Value="1234.56"
                            CustomFormat="C2" />
    <!-- Output: $1,234.56 -->
    
    <!-- 3 decimal places (precise) -->
    <Label Text="C3 - Precise Currency:" />
    <editors:SfNumericEntry Value="1234.567"
                            CustomFormat="C3" />
    <!-- Output: $1,234.567 -->
    
</VerticalStackLayout>
```

**C#:**
```csharp
// Format stock price in currency with 2 decimals
stockPrice.CustomFormat = "C2";

// Format product discount in currency without decimals
productDiscount.CustomFormat = "C0";

// Format precise financial calculation
preciseAmount.CustomFormat = "C3";
```

### Practical Currency Examples

**E-commerce Product Pricing:**
```xml
<StackLayout Spacing="10">
    <Label Text="Product Price:" />
    <editors:SfNumericEntry x:Name="priceInput"
                            Value="99.99"
                            CustomFormat="C2"
                            Placeholder="$0.00"
                            Minimum="0"
                            Maximum="99999.99" />
</StackLayout>
```

**Budget Allocation:**
```xml
<Grid RowDefinitions="Auto,Auto,Auto,Auto"
      ColumnDefinitions="*,*"
      RowSpacing="10"
      ColumnSpacing="10"
      Padding="20">
    
    <Label Grid.Row="0" Grid.Column="0" Text="Food:" />
    <editors:SfNumericEntry Grid.Row="0" Grid.Column="1"
                            Value="500"
                            CustomFormat="C2" />
    
    <Label Grid.Row="1" Grid.Column="0" Text="Transport:" />
    <editors:SfNumericEntry Grid.Row="1" Grid.Column="1"
                            Value="200"
                            CustomFormat="C2" />
    
    <Label Grid.Row="2" Grid.Column="0" Text="Entertainment:" />
    <editors:SfNumericEntry Grid.Row="2" Grid.Column="1"
                            Value="150"
                            CustomFormat="C2" />
    
    <Label Grid.Row="3" Grid.Column="0" Text="Total:" FontAttributes="Bold" />
    <editors:SfNumericEntry Grid.Row="3" Grid.Column="1"
                            Value="850"
                            CustomFormat="C2"
                            IsEditable="False"
                            TextColor="Green"
                            FontAttributes="Bold" />
</Grid>
```

---

## Percentage Formatting

Use the **P** format specifier to display values as percentages.

### Basic Percentage Formatting

**XAML:**
```xml
<!-- Percentage with 2 decimal places (default) -->
<editors:SfNumericEntry Value="0.1556"
                        CustomFormat="P2" />
```

**C#:**
```csharp
SfNumericEntry productDiscount = new SfNumericEntry();
productDiscount.CustomFormat = "P2";
productDiscount.Value = 0.1556;
```

**Output:** `15.56%` (value × 100)

**Important:** By default, percentage formatting **multiplies the value by 100**. So 0.15 displays as 15%. See [Percentage Display Modes](#percentage-display-modes) to change this behavior.

### Percentage Format Variations

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <!-- No decimal places (whole percentages) -->
    <Label Text="P0 - Whole Percent:" />
    <editors:SfNumericEntry Value="0.1556"
                            CustomFormat="P0" />
    <!-- Output: 16% (rounded) -->
    
    <!-- 2 decimal places (standard) -->
    <Label Text="P2 - Standard Percent:" />
    <editors:SfNumericEntry Value="0.1556"
                            CustomFormat="P2" />
    <!-- Output: 15.56% -->
    
    <!-- 3 decimal places (precise) -->
    <Label Text="P3 - Precise Percent:" />
    <editors:SfNumericEntry Value="0.15567"
                            CustomFormat="P3" />
    <!-- Output: 15.567% -->
    
</VerticalStackLayout>
```

**C#:**
```csharp
// Format product discount without decimals
productDiscount.CustomFormat = "P0";  // 15%

// Format interest rate with precision
interestRate.CustomFormat = "P2";     // 15.56%

// Format precise tax rate
taxRate.CustomFormat = "P3";          // 15.567%
```

### Practical Percentage Examples

**Discount Calculator:**
```xml
<StackLayout Spacing="15" Padding="20">
    <Label Text="Original Price:" />
    <editors:SfNumericEntry x:Name="originalPrice"
                            Value="100"
                            CustomFormat="C2" />
    
    <Label Text="Discount Percentage:" />
    <editors:SfNumericEntry x:Name="discountPercent"
                            Value="0.15"
                            CustomFormat="P0"
                            Minimum="0"
                            Maximum="1"
                            ValueChanged="CalculateDiscount" />
    
    <Label Text="Final Price:" FontAttributes="Bold" />
    <editors:SfNumericEntry x:Name="finalPrice"
                            Value="85"
                            CustomFormat="C2"
                            IsEditable="False"
                            TextColor="Green" />
</StackLayout>
```

**Progress Indicator:**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Task Completion:" />
    <editors:SfNumericEntry Value="0.75"
                            CustomFormat="P0"
                            IsEditable="False"
                            TextColor="Green"
                            FontSize="24"
                            FontAttributes="Bold"
                            HorizontalTextAlignment="Center" />
</StackLayout>
```

---

## Decimal Formatting

Use the **N** format specifier for decimal numbers with thousand separators.

### Basic Decimal Formatting

**XAML:**
```xml
<!-- Decimal with 2 decimal places and thousand separator -->
<editors:SfNumericEntry Value="1234567.89"
                        CustomFormat="N2" />
```

**C#:**
```csharp
SfNumericEntry hoursWorked = new SfNumericEntry();
hoursWorked.CustomFormat = "N2";
hoursWorked.Value = 1234567.89;
```

**Output:** `1,234,567.89` (with thousand separators)

### Decimal Format Variations

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <!-- No decimal places (whole numbers) -->
    <Label Text="N0 - Whole Number:" />
    <editors:SfNumericEntry Value="1234567.89"
                            CustomFormat="N0" />
    <!-- Output: 1,234,568 (rounded) -->
    
    <!-- 2 decimal places (standard) -->
    <Label Text="N2 - Standard Decimal:" />
    <editors:SfNumericEntry Value="1234567.89"
                            CustomFormat="N2" />
    <!-- Output: 1,234,567.89 -->
    
    <!-- 4 decimal places (precise) -->
    <Label Text="N4 - Precise Decimal:" />
    <editors:SfNumericEntry Value="1234567.8912"
                            CustomFormat="N4" />
    <!-- Output: 1,234,567.8912 -->
    
</VerticalStackLayout>
```

**C#:**
```csharp
// Format quantity as whole number
quantity.CustomFormat = "N0";  // 1,234

// Format measurement with precision
measurement.CustomFormat = "N2";  // 1,234.56

// Format scientific data
scientificValue.CustomFormat = "N4";  // 1,234.5678
```

### Practical Decimal Examples

**Inventory Management:**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Stock Quantity:" />
    <editors:SfNumericEntry Value="1500"
                            CustomFormat="N0"
                            Minimum="0"
                            AllowNull="False"
                            Placeholder="Enter quantity" />
</StackLayout>
```

**Scientific Measurement:**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Measurement (mm):" />
    <editors:SfNumericEntry Value="123.4567"
                            CustomFormat="N4"
                            Placeholder="0.0000" />
</StackLayout>
```

---

## Integer Digits Control

Control the minimum number of integer digits displayed using the **0** placeholder.

### Zero Placeholder (0)

The **0** placeholder ensures a minimum number of digits. If the value has fewer digits, zeros are added to the left.

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <!-- Currency with minimum 5 integer digits -->
    <Label Text="$00000.00 Format:" />
    <editors:SfNumericEntry Value="123.45"
                            CustomFormat="$00000.00" />
    <!-- Output: $00123.45 -->
    
    <!-- Percentage with minimum 5 integer digits -->
    <Label Text="00000.00% Format:" />
    <editors:SfNumericEntry Value="123.45"
                            CustomFormat="00000.00%" />
    <!-- Output: 00123.45% -->
    
    <!-- Decimal with minimum 5 integer digits -->
    <Label Text="00000.00 Format:" />
    <editors:SfNumericEntry Value="123.45"
                            CustomFormat="00000.00" />
    <!-- Output: 00123.45 -->
    
</VerticalStackLayout>
```

**C#:**
```csharp
// Format stock price with leading zeros
stockPrice.CustomFormat = "$00000.00";  // $00123.45

// Format product discount with leading zeros
productDiscount.CustomFormat = "00000.00%";  // 00123.45%

// Format hours worked with leading zeros
hoursWorked.CustomFormat = "00000.00";  // 00123.45
```

**When to use integer digit control:**
- Fixed-width displays (tabular data alignment)
- Serial numbers or IDs
- Time formatting (00:00:00)
- Enforcing consistent visual width

### Practical Example with Alignment

```xml
<Grid RowDefinitions="Auto,Auto,Auto"
      ColumnDefinitions="Auto,*"
      RowSpacing="5"
      ColumnSpacing="10"
      Padding="20">
    
    <Label Grid.Row="0" Grid.Column="0" Text="ID:" />
    <editors:SfNumericEntry Grid.Row="0" Grid.Column="1"
                            Value="1"
                            CustomFormat="00000"
                            IsEditable="False"
                            FontFamily="Courier New" />
    <!-- Output: 00001 -->
    
    <Label Grid.Row="1" Grid.Column="0" Text="ID:" />
    <editors:SfNumericEntry Grid.Row="1" Grid.Column="1"
                            Value="123"
                            CustomFormat="00000"
                            IsEditable="False"
                            FontFamily="Courier New" />
    <!-- Output: 00123 -->
    
    <Label Grid.Row="2" Grid.Column="0" Text="ID:" />
    <editors:SfNumericEntry Grid.Row="2" Grid.Column="1"
                            Value="98765"
                            CustomFormat="00000"
                            IsEditable="False"
                            FontFamily="Courier New" />
    <!-- Output: 98765 -->
</Grid>
```

**Result:** All IDs are aligned and have the same visual width.

---

## Fractional Digits Control

Control the number of fractional (decimal) digits using **0** and **#** placeholders.

### Zero Placeholder for Fractional Digits

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <!-- 3 fractional digits (minimum) -->
    <Label Text="$000.000 Format:" />
    <editors:SfNumericEntry Value="12.5"
                            CustomFormat="$000.000" />
    <!-- Output: $012.500 (zeros added) -->
    
    <!-- 3 fractional digits for percentage -->
    <Label Text="00.000% Format:" />
    <editors:SfNumericEntry Value="12.5"
                            CustomFormat="00.000%" />
    <!-- Output: 12.500% -->
    
    <!-- 3 fractional digits for decimal -->
    <Label Text="00.000 Format:" />
    <editors:SfNumericEntry Value="12.5"
                            CustomFormat="00.000" />
    <!-- Output: 12.500 -->
    
</VerticalStackLayout>
```

**C#:**
```csharp
// Ensure 3 decimal places
stockPrice.CustomFormat = "$000.000";  // $012.500
productDiscount.CustomFormat = "00.000%";  // 12.500%
hoursWorked.CustomFormat = "00.000";  // 12.500
```

**Why fractional digit control matters:**
- Consistent decimal places across inputs
- Scientific precision requirements
- Financial calculations requiring specific decimals
- UI consistency in data tables

---

## Custom Format Patterns

Create custom format patterns using **0** (zero placeholder) and **#** (digit placeholder).

### Understanding Placeholders

**0 (Zero Placeholder):**
- Replaces with the corresponding digit if present
- Adds zero if no digit is present
- Forces display of the position

**# (Digit Placeholder):**
- Replaces with the corresponding digit if present
- Does not display anything if no digit is present
- Optional display of the position

### Minimum and Maximum Fractional Digits

Combine **0** and **#** to control decimal precision:

**Format: `#.00##`**
- Minimum 2 fractional digits (00)
- Maximum 4 fractional digits (##)

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <!-- Currency: Min 2, Max 4 decimals -->
    <Label Text="$00.00## Format:" />
    <editors:SfNumericEntry Value="12.5"
                            CustomFormat="$00.00##" />
    <!-- Output: $12.50 (2 decimals minimum) -->
    
    <editors:SfNumericEntry Value="12.5678"
                            CustomFormat="$00.00##" />
    <!-- Output: $12.5678 (all 4 shown) -->
    
    <editors:SfNumericEntry Value="12.56789"
                            CustomFormat="$00.00##" />
    <!-- Output: $12.5679 (rounded to 4) -->
    
    <!-- Percentage: Min 2, Max 4 decimals -->
    <Label Text="00.00##% Format:" />
    <editors:SfNumericEntry Value="12.5"
                            CustomFormat="00.00##%" />
    <!-- Output: 12.50% -->
    
    <!-- Decimal: Min 2, Max 4 decimals -->
    <Label Text="00.00## Format:" />
    <editors:SfNumericEntry Value="12.567"
                            CustomFormat="00.00##" />
    <!-- Output: 12.567 (3 decimals shown) -->
    
</VerticalStackLayout>
```

**C#:**
```csharp
// Flexible decimal places: 2-4 digits
stockPrice.CustomFormat = "$00.00##";  // $12.50 to $12.5678
productDiscount.CustomFormat = "00.00##%";  // 12.50% to 12.5678%
hoursWorked.CustomFormat = "00.00##";  // 12.50 to 12.5678
```

### Advanced Custom Patterns

**Thousands separator without decimals:**
```xml
<editors:SfNumericEntry Value="1234567"
                        CustomFormat="#,##0" />
<!-- Output: 1,234,567 -->
```

**Currency with optional cents:**
```xml
<editors:SfNumericEntry Value="1234.5"
                        CustomFormat="$#,##0.##" />
<!-- Output: $1,234.5 (no trailing zero) -->
```

**Fixed-width with padding:**
```xml
<editors:SfNumericEntry Value="42"
                        CustomFormat="00000.00" />
<!-- Output: 00042.00 -->
```

### Practical Custom Format Example

**Financial Report Display:**
```xml
<Grid RowDefinitions="Auto,Auto,Auto,Auto"
      ColumnDefinitions="*,Auto"
      RowSpacing="10"
      ColumnSpacing="15"
      Padding="20">
    
    <Label Grid.Row="0" Grid.Column="0" Text="Revenue:" FontSize="16" />
    <editors:SfNumericEntry Grid.Row="0" Grid.Column="1"
                            Value="1234567.89"
                            CustomFormat="$#,##0.00"
                            IsEditable="False"
                            HorizontalTextAlignment="End" />
    
    <Label Grid.Row="1" Grid.Column="0" Text="Expenses:" FontSize="16" />
    <editors:SfNumericEntry Grid.Row="1" Grid.Column="1"
                            Value="987654.32"
                            CustomFormat="$#,##0.00"
                            IsEditable="False"
                            HorizontalTextAlignment="End" />
    
    <Label Grid.Row="2" Grid.Column="0" Text="Profit:" FontSize="16" FontAttributes="Bold" />
    <editors:SfNumericEntry Grid.Row="2" Grid.Column="1"
                            Value="246913.57"
                            CustomFormat="$#,##0.00"
                            IsEditable="False"
                            TextColor="Green"
                            FontAttributes="Bold"
                            HorizontalTextAlignment="End" />
    
    <Label Grid.Row="3" Grid.Column="0" Text="Margin:" FontSize="16" FontAttributes="Bold" />
    <editors:SfNumericEntry Grid.Row="3" Grid.Column="1"
                            Value="0.2"
                            CustomFormat="0.00%"
                            IsEditable="False"
                            TextColor="Green"
                            FontAttributes="Bold"
                            HorizontalTextAlignment="End" />
</Grid>
```

---

## Culture Support and Localization

NumericEntry supports culture-specific number formatting for international applications.

### Setting Culture

Use the `Culture` property to specify a culture for formatting.

**C#:**
```csharp
using System.Globalization;

SfNumericEntry numericEntry = new SfNumericEntry();
numericEntry.Value = 1234.56;
numericEntry.CustomFormat = "C2";

// US culture
CultureInfo usCulture = new CultureInfo("en-US");
numericEntry.Culture = usCulture;
// Output: $1,234.56

// European culture (Germany)
CultureInfo deCulture = new CultureInfo("de-DE");
numericEntry.Culture = deCulture;
// Output: 1.234,56 € (period for thousands, comma for decimal)

// Japanese culture
CultureInfo jpCulture = new CultureInfo("ja-JP");
numericEntry.Culture = jpCulture;
// Output: ¥1,234

// Indian culture
CultureInfo inCulture = new CultureInfo("hi-IN");
numericEntry.Culture = inCulture;
// Output: ₹1,234.56
```

### Culture-Specific Formatting Examples

**Multi-Currency Display:**
```csharp
public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        
        var layout = new VerticalStackLayout { Spacing = 15, Padding = 20 };
        
        // USD
        layout.Children.Add(new Label { Text = "US Dollar (en-US):" });
        var usdEntry = new SfNumericEntry
        {
            Value = 1234.56,
            CustomFormat = "C2",
            Culture = new CultureInfo("en-US")
        };
        layout.Children.Add(usdEntry);
        
        // EUR
        layout.Children.Add(new Label { Text = "Euro (de-DE):" });
        var eurEntry = new SfNumericEntry
        {
            Value = 1234.56,
            CustomFormat = "C2",
            Culture = new CultureInfo("de-DE")
        };
        layout.Children.Add(eurEntry);
        
        // GBP
        layout.Children.Add(new Label { Text = "British Pound (en-GB):" });
        var gbpEntry = new SfNumericEntry
        {
            Value = 1234.56,
            CustomFormat = "C2",
            Culture = new CultureInfo("en-GB")
        };
        layout.Children.Add(gbpEntry);
        
        // JPY
        layout.Children.Add(new Label { Text = "Japanese Yen (ja-JP):" });
        var jpyEntry = new SfNumericEntry
        {
            Value = 1234,
            CustomFormat = "C0",
            Culture = new CultureInfo("ja-JP")
        };
        layout.Children.Add(jpyEntry);
        
        Content = new ScrollView { Content = layout };
    }
}
```

**Expected Output:**
- US: $1,234.56
- Germany: 1.234,56 €
- UK: £1,234.56
- Japan: ¥1,234

**Why culture support matters:**
- International applications
- Multi-region e-commerce
- Financial applications with currency conversion
- Compliance with regional number formats

---

## Percentage Display Modes

Control how percentage values are displayed using the `PercentDisplayMode` property.

### Value Mode

Displays the actual value with a percentage symbol (no multiplication by 100).

**XAML:**
```xml
<editors:SfNumericEntry Value="1000"
                        CustomFormat="P"
                        PercentDisplayMode="Value" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 1000;
sfNumericEntry.CustomFormat = "P";
sfNumericEntry.PercentDisplayMode = PercentDisplayMode.Value;
```

**Output:** `1000%` (raw value displayed)

**When to use Value mode:**
- User enters values already in percentage form (10 = 10%)
- Percentage input fields where users type the actual percentage
- Avoiding confusion with decimal-to-percentage conversion

### Compute Mode (Default)

Multiplies the value by 100 and displays as percentage.

**XAML:**
```xml
<editors:SfNumericEntry Value="1000"
                        CustomFormat="P"
                        PercentDisplayMode="Compute" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 1000;
sfNumericEntry.CustomFormat = "P";
sfNumericEntry.PercentDisplayMode = PercentDisplayMode.Compute;
```

**Output:** `100000%` (1000 × 100 = 100000%)

**When to use Compute mode:**
- Working with decimal values (0.15 = 15%)
- Standard .NET percentage formatting behavior
- Scientific or financial calculations using decimals

### Comparison Example

```xml
<VerticalStackLayout Spacing="20" Padding="20">
    
    <Label Text="Same Value (15), Different Modes" FontSize="18" FontAttributes="Bold" />
    
    <!-- Value Mode: Shows 15% -->
    <Label Text="Value Mode (PercentDisplayMode=Value):" />
    <editors:SfNumericEntry Value="15"
                            CustomFormat="P2"
                            PercentDisplayMode="Value" />
    <!-- Output: 15.00% -->
    
    <!-- Compute Mode: Shows 1500% -->
    <Label Text="Compute Mode (PercentDisplayMode=Compute):" />
    <editors:SfNumericEntry Value="15"
                            CustomFormat="P2"
                            PercentDisplayMode="Compute" />
    <!-- Output: 1,500.00% (15 × 100) -->
    
</VerticalStackLayout>
```

### Practical Percentage Mode Example

**Discount Input (Value Mode):**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Enter Discount Percentage (0-100):" />
    <editors:SfNumericEntry Value="15"
                            CustomFormat="P0"
                            PercentDisplayMode="Value"
                            Minimum="0"
                            Maximum="100"
                            Placeholder="0%" />
    <!-- User types: 15 → Displays: 15% -->
</StackLayout>
```

**Interest Rate Calculation (Compute Mode):**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Interest Rate (as decimal):" />
    <editors:SfNumericEntry Value="0.0425"
                            CustomFormat="P2"
                            PercentDisplayMode="Compute"
                            Placeholder="0.00%" />
    <!-- User types: 0.0425 → Displays: 4.25% -->
</StackLayout>
```

---

## Maximum Decimal Digits

Control the maximum number of decimal digits using the `MaximumNumberDecimalDigits` property.

### Setting Maximum Decimal Digits

**XAML:**
```xml
<editors:SfNumericEntry Value="1000.23232"
                        MaximumNumberDecimalDigits="3" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 1000.23232;
sfNumericEntry.MaximumNumberDecimalDigits = 3;
```

**Output:** `1000.232` (rounded to 3 decimal places)

**Key Points:**
- Must be a positive integer
- Default value is `2`
- **Does not work** when `CustomFormat` is specified
- Rounds the value to the specified decimal places

### MaximumNumberDecimalDigits vs CustomFormat

**Important:** These properties are mutually exclusive. Use one or the other, not both.

**Using MaximumNumberDecimalDigits (no CustomFormat):**
```xml
<editors:SfNumericEntry Value="123.456789"
                        MaximumNumberDecimalDigits="4" />
<!-- Output: 123.4568 -->
```

**Using CustomFormat (MaximumNumberDecimalDigits ignored):**
```xml
<editors:SfNumericEntry Value="123.456789"
                        CustomFormat="N4"
                        MaximumNumberDecimalDigits="2" />
<!-- Output: 123.4568 (MaximumNumberDecimalDigits is ignored) -->
```

### Practical Examples

**Scientific Measurement:**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Temperature (°C):" />
    <editors:SfNumericEntry Value="36.756789"
                            MaximumNumberDecimalDigits="2"
                            Placeholder="0.00" />
    <!-- Output: 36.76 -->
</StackLayout>
```

**GPS Coordinates:**
```xml
<StackLayout Spacing="15" Padding="20">
    <Label Text="Latitude:" />
    <editors:SfNumericEntry Value="37.7749295"
                            MaximumNumberDecimalDigits="6"
                            Placeholder="0.000000" />
    
    <Label Text="Longitude:" />
    <editors:SfNumericEntry Value="-122.4194155"
                            MaximumNumberDecimalDigits="6"
                            Placeholder="0.000000" />
</StackLayout>
```

---

## Best Practices

1. **Use standard format specifiers** (C, P, N) for common formats before creating custom patterns
2. **Choose PercentDisplayMode** based on how users think about percentages (Value mode for "type 15 for 15%")
3. **Set culture explicitly** for international applications to ensure correct symbol and separator display
4. **Use MaximumNumberDecimalDigits** for simple precision control without custom formats
5. **Combine 0 and # placeholders** for flexible decimal display (minimum/maximum digits)
6. **Test rounding behavior** with MaximumNumberDecimalDigits to ensure expected precision
7. **Use CustomFormat="C0"** for whole currency amounts (no cents)
8. **Right-align currency fields** (HorizontalTextAlignment="End") for traditional financial displays
9. **Consider user input expectations** when choosing between Value and Compute modes for percentages
10. **Document format patterns** in placeholder text to guide users (e.g., "$0.00", "0-100%")

---