# Getting Started with Syncfusion .NET MAUI NumericEntry

This guide covers the initial setup and basic implementation of the SfNumericEntry control, from installation to your first working numeric input field.

## Table of Contents
1. [Installation and Setup](#installation-and-setup)
2. [Handler Registration](#handler-registration)
3. [Namespace Configuration](#namespace-configuration)
4. [Basic NumericEntry Implementation](#basic-numericentry-implementation)
5. [Understanding Value Editing and Validation](#understanding-value-editing-and-validation)
6. [Number Format Basics](#number-format-basics)
7. [Null Value Handling](#null-value-handling)
8. [Complete Working Example](#complete-working-example)

---

## Installation and Setup

### Step 1: Create a .NET MAUI Project

If you don't have a project yet:
1. Go to **File > New > Project** in Visual Studio
2. Choose the **.NET MAUI App** template
3. Name the project and choose a location
4. Click **Next**
5. Select the .NET framework version and click **Create**

### Step 2: Install the Syncfusion MAUI Toolkit NuGet Package

**Via NuGet Package Manager:**
1. In **Solution Explorer**, right-click the project
2. Choose **Manage NuGet Packages**
3. Search for `Syncfusion.Maui.Toolkit`
4. Install the latest version
5. Ensure all dependencies are installed and the project is restored

**Via Package Manager Console:**
```powershell
Install-Package Syncfusion.Maui.Toolkit
```

**Via .NET CLI:**
```bash
dotnet add package Syncfusion.Maui.Toolkit
```

**Why this matters:** The Syncfusion.Maui.Toolkit package contains all Syncfusion controls including SfNumericEntry. Without this package, the control won't be available.

---

## Handler Registration

### Register Syncfusion Toolkit Handler in MauiProgram.cs

**This step is mandatory.** You must register the Syncfusion handler before using any Syncfusion controls.

**MauiProgram.cs:**
```csharp
using Syncfusion.Maui.Toolkit.Hosting;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .ConfigureSyncfusionToolkit()  // Register Syncfusion handler
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        return builder.Build();
    }
}
```

**Key Points:**
- Add `using Syncfusion.Maui.Toolkit.Hosting;` at the top
- Call `.ConfigureSyncfusionToolkit()` on the builder
- This must be done before `.UseMauiApp<App>()`

**Why this is required:** The handler registration initializes the Syncfusion controls and ensures they render correctly on all platforms (iOS, Android, Windows, macOS).

---

## Namespace Configuration

### XAML Namespace Declaration

To use SfNumericEntry in XAML, declare the namespace:

```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:editors="clr-namespace:Syncfusion.Maui.Toolkit.NumericEntry;assembly=Syncfusion.Maui.Toolkit"
             x:Class="MyApp.MainPage">
    
    <!-- Now you can use editors:SfNumericEntry -->
    
</ContentPage>
```

**Namespace breakdown:**
- `xmlns:editors` - The prefix you'll use (can be any name, but "editors" is conventional)
- `clr-namespace:Syncfusion.Maui.Toolkit.NumericEntry` - The .NET namespace
- `assembly=Syncfusion.Maui.Toolkit` - The assembly name

### C# Using Statement

For code-behind or pure C# implementations:

```csharp
using Syncfusion.Maui.Toolkit.NumericEntry;
```

Add this at the top of your C# files when working with NumericEntry programmatically.

---

## Basic NumericEntry Implementation

### Minimal XAML Implementation

The simplest possible NumericEntry:

```xml
<editors:SfNumericEntry x:Name="numericEntry" />
```

This creates a basic numeric input field with default settings:
- Allows null values
- No formatting applied
- Black border
- Clear button visible when focused
- Validation on lost focus (OnLostFocus mode)

### Setting an Initial Value

```xml
<editors:SfNumericEntry x:Name="numericEntry" 
                        Value="100" />
```

The `Value` property is of type `double?` (nullable double), so it can hold numeric values or null.

### Basic C# Implementation

```csharp
using Syncfusion.Maui.Toolkit.NumericEntry;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        
        SfNumericEntry sfNumericEntry = new SfNumericEntry();
        sfNumericEntry.Value = 100;
        sfNumericEntry.HorizontalOptions = LayoutOptions.Center;
        sfNumericEntry.VerticalOptions = LayoutOptions.Center;
        
        Content = sfNumericEntry;
    }
}
```

### Practical Example with Styling

```xml
<editors:SfNumericEntry x:Name="priceInput"
                        Value="99.99"
                        Placeholder="Enter price"
                        WidthRequest="250"
                        HeightRequest="50"
                        HorizontalOptions="Center"
                        VerticalOptions="Center" />
```

**Result:** A centered numeric input field, 250x50 pixels, showing "99.99" with placeholder text "Enter price" when cleared.

---

## Understanding Value Editing and Validation

NumericEntry has two validation modes that control when the entered value is validated and formatted.

### OnLostFocus Mode (Default)

The value is validated and formatted when:
- The control loses focus (user taps elsewhere)
- The Enter key is pressed
- Focus moves to the next control

**Example:**
```xml
<editors:SfNumericEntry Value="50"
                        ValueChangeMode="OnLostFocus"
                        CustomFormat="C2" />
```

**When to use:**
- Forms where users fill out multiple fields
- When you want to minimize interruption during typing
- When validation should happen after complete entry

**User Experience:** User types freely, sees unformatted input during typing, formatted result appears on blur or Enter.

### OnKeyFocus Mode (Real-Time)

The value is validated immediately with each key press.

**Example:**
```xml
<editors:SfNumericEntry Value="50"
                        ValueChangeMode="OnKeyFocus"
                        CustomFormat="C2" />
```

**When to use:**
- Calculators or real-time computation scenarios
- Live preview of formatted values
- When immediate feedback is critical (e.g., price calculators)

**User Experience:** Value updates and formats with every keystroke, providing instant visual feedback.

### Comparison Example

```xml
<VerticalStackLayout Spacing="10" Padding="20">
    
    <!-- OnLostFocus: Updates when user leaves field -->
    <Label Text="OnLostFocus Mode:" FontAttributes="Bold" />
    <editors:SfNumericEntry ValueChangeMode="OnLostFocus"
                            CustomFormat="C2"
                            Value="100" />
    
    <!-- OnKeyFocus: Updates with each keystroke -->
    <Label Text="OnKeyFocus Mode:" FontAttributes="Bold" />
    <editors:SfNumericEntry ValueChangeMode="OnKeyFocus"
                            CustomFormat="C2"
                            Value="100" />
    
</VerticalStackLayout>
```

**Try both modes** to understand the user experience difference.

---

## Number Format Basics

The `CustomFormat` property controls how the numeric value is displayed.

### Currency Formatting

Use the **C** format specifier for currency:

```xml
<!-- Currency with 2 decimal places -->
<editors:SfNumericEntry Value="1250.50"
                        CustomFormat="C2" />
```

**Output:** $1,250.50 (or currency symbol based on culture)

**Format variations:**
- `C` or `C2` → 2 decimal places (default)
- `C0` → No decimal places (whole currency)
- `C3` → 3 decimal places

**Example:**
```csharp
stockPrice.CustomFormat = "C2";  // $12.50
wholeDollars.CustomFormat = "C0";  // $12
```

### Percentage Formatting

Use the **P** format specifier for percentages:

```xml
<!-- Percentage with 2 decimal places -->
<editors:SfNumericEntry Value="15"
                        CustomFormat="P2" />
```

**Output:** 1,500.00% (because 15 × 100 = 1500%)

**Important:** By default, percentage formatting multiplies the value by 100. To display the raw value, see the formatting guide for `PercentDisplayMode`.

**Format variations:**
- `P` or `P2` → 2 decimal places
- `P0` → No decimal places (whole percentages)
- `P3` → 3 decimal places

**Example:**
```csharp
discount.CustomFormat = "P0";  // 15%
taxRate.CustomFormat = "P2";   // 15.00%
```

### Decimal Formatting

Use the **N** format specifier for standard decimal numbers:

```xml
<!-- Decimal with 2 decimal places -->
<editors:SfNumericEntry Value="1234.5678"
                        CustomFormat="N2" />
```

**Output:** 1,234.57 (with thousand separators)

**Format variations:**
- `N` or `N2` → 2 decimal places
- `N0` → No decimal places (whole numbers with separators)
- `N4` → 4 decimal places

**Example:**
```csharp
quantity.CustomFormat = "N0";  // 1,234
measurement.CustomFormat = "N4";  // 1,234.5678
```

### Complete Format Example

```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <!-- Currency Input -->
    <Label Text="Stock Price:" FontSize="16" />
    <editors:SfNumericEntry Value="99.99"
                            CustomFormat="C2"
                            Placeholder="$0.00" />
    
    <!-- Percentage Input -->
    <Label Text="Product Discount:" FontSize="16" />
    <editors:SfNumericEntry Value="15"
                            CustomFormat="P2"
                            Placeholder="0%" />
    
    <!-- Decimal Input -->
    <Label Text="Hours Worked:" FontSize="16" />
    <editors:SfNumericEntry Value="40.5"
                            CustomFormat="N2"
                            Placeholder="0.00" />
    
</VerticalStackLayout>
```

**Why formatting matters:** Users expect numbers to appear in familiar formats. Currency symbols, thousand separators, and percentage signs improve readability and reduce input errors.

---

## Null Value Handling

### AllowNull Property (Default: true)

By default, NumericEntry allows null values. When the user clears the input or clicks the clear button, the value becomes `null`.

**Allowing Null (Default):**
```xml
<editors:SfNumericEntry Value="100"
                        AllowNull="True" />
```

**Behavior:** 
- Clicking clear button → Value becomes `null`
- Placeholder text is shown (if configured)
- Value property is `null` until user enters a number

**When to allow null:**
- Optional form fields
- When "no value" is a valid state
- When you need to distinguish between 0 and "not entered"

### Preventing Null Values

```xml
<editors:SfNumericEntry Value="100"
                        AllowNull="False" />
```

**Behavior:**
- Clicking clear button → Value becomes `0` (or `Minimum` if set)
- Value property is never `null`
- Control always has a numeric value

**When to prevent null:**
- Required form fields
- When a default value (0) is acceptable
- When calculations depend on a non-null value

### Null vs Minimum Value

**Important edge case:** When `AllowNull="False"` and `Minimum` is set:

```xml
<editors:SfNumericEntry Minimum="10"
                        AllowNull="False" />
```

**Behavior when cleared:**
- Value becomes `10` (the Minimum), not `0`
- This prevents invalid states where value < Minimum

**Example with null allowed:**
```xml
<editors:SfNumericEntry Minimum="10"
                        AllowNull="True" />
```

**Behavior when cleared:**
- Value becomes `null`
- User can leave field empty
- On entering a value, it must be ≥ 10

### Practical Example

```xml
<VerticalStackLayout Spacing="20" Padding="20">
    
    <!-- Optional Field (Null Allowed) -->
    <Label Text="Middle Initial (Optional):" />
    <editors:SfNumericEntry Value="{x:Null}"
                            AllowNull="True"
                            Placeholder="Leave blank if none"
                            CustomFormat="N0" />
    
    <!-- Required Field (No Null) -->
    <Label Text="Age (Required):" />
    <editors:SfNumericEntry Value="18"
                            AllowNull="False"
                            Minimum="18"
                            Placeholder="Enter your age"
                            CustomFormat="N0" />
    
</VerticalStackLayout>
```

---

## Complete Working Example

Here's a complete, copy-paste ready example demonstrating all getting-started concepts:

### XAML (MainPage.xaml)

```xml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:editors="clr-namespace:Syncfusion.Maui.Toolkit.NumericEntry;assembly=Syncfusion.Maui.Toolkit"
             x:Class="NumericEntryDemo.MainPage">

    <ScrollView>
        <VerticalStackLayout Spacing="20" 
                           Padding="30">

            <Label Text="Product Entry Form"
                   FontSize="24"
                   FontAttributes="Bold"
                   HorizontalOptions="Center"
                   Margin="0,0,0,20" />

            <!-- Price Input -->
            <Label Text="Price:" FontSize="16" />
            <editors:SfNumericEntry x:Name="priceInput"
                                    Value="99.99"
                                    CustomFormat="C2"
                                    Placeholder="Enter price"
                                    Minimum="0"
                                    Maximum="10000"
                                    AllowNull="False"
                                    ValueChangeMode="OnLostFocus"
                                    ValueChanged="OnPriceChanged" />

            <!-- Discount Input -->
            <Label Text="Discount %:" FontSize="16" />
            <editors:SfNumericEntry x:Name="discountInput"
                                    Value="10"
                                    CustomFormat="P0"
                                    Placeholder="Enter discount"
                                    Minimum="0"
                                    Maximum="100"
                                    ValueChangeMode="OnKeyFocus" />

            <!-- Quantity Input -->
            <Label Text="Quantity:" FontSize="16" />
            <editors:SfNumericEntry x:Name="quantityInput"
                                    Value="1"
                                    CustomFormat="N0"
                                    Placeholder="Enter quantity"
                                    Minimum="1"
                                    AllowNull="False" />

            <!-- Total (Read-Only Display) -->
            <Label Text="Total:" FontSize="16" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="totalDisplay"
                                    Value="89.99"
                                    CustomFormat="C2"
                                    IsEditable="False"
                                    ShowClearButton="False"
                                    TextColor="Green"
                                    FontSize="20"
                                    FontAttributes="Bold" />

        </VerticalStackLayout>
    </ScrollView>

</ContentPage>
```

### Code-Behind (MainPage.xaml.cs)

```csharp
using Syncfusion.Maui.Toolkit.NumericEntry;

namespace NumericEntryDemo;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        
        // Wire up events for calculations
        priceInput.ValueChanged += CalculateTotal;
        discountInput.ValueChanged += CalculateTotal;
        quantityInput.ValueChanged += CalculateTotal;
        
        // Initial calculation
        CalculateTotal(null, null);
    }

    private void OnPriceChanged(object sender, NumericEntryValueChangedEventArgs e)
    {
        // Log price changes
        if (e.NewValue.HasValue)
        {
            System.Diagnostics.Debug.WriteLine($"Price changed from {e.OldValue} to {e.NewValue}");
        }
    }

    private void CalculateTotal(object sender, NumericEntryValueChangedEventArgs e)
    {
        // Get values (with null safety)
        double price = priceInput.Value ?? 0;
        double discountPercent = discountInput.Value ?? 0;
        double quantity = quantityInput.Value ?? 1;
        
        // Calculate: (Price × Quantity) - (Price × Quantity × Discount%)
        // Note: discount value is already in % format (10 = 10%)
        double subtotal = price * quantity;
        double discountAmount = subtotal * (discountPercent / 100);
        double total = subtotal - discountAmount;
        
        // Update total display
        totalDisplay.Value = total;
    }
}
```

### MauiProgram.cs (Required Setup)

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

namespace NumericEntryDemo;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .ConfigureSyncfusionToolkit()  // Essential: Register Syncfusion
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        return builder.Build();
    }
}
```

### What This Example Demonstrates

1. **Installation:** Uses Syncfusion.Maui.Toolkit package
2. **Handler Registration:** ConfigureSyncfusionToolkit() in MauiProgram.cs
3. **Namespace Declaration:** xmlns:editors for XAML usage
4. **Currency Formatting:** CustomFormat="C2" for price and total
5. **Percentage Formatting:** CustomFormat="P0" for discount
6. **Decimal Formatting:** CustomFormat="N0" for quantity
7. **Null Handling:** AllowNull="False" for required fields
8. **Value Restrictions:** Minimum and Maximum properties
9. **Validation Modes:** OnLostFocus vs OnKeyFocus
10. **Events:** ValueChanged for real-time calculations
11. **Read-Only Display:** IsEditable="False" for calculated total

### Expected Behavior

- Enter price: Value validates on blur, shows currency format
- Enter discount: Updates immediately (OnKeyFocus mode), shows percentage
- Enter quantity: Must be ≥ 1, whole numbers only
- Total calculates automatically with each change
- All fields enforce constraints (min/max, no null)

---

## Next Steps

Now that you have a working NumericEntry:

- **Explore advanced styling:** See basic-features.md for placeholder, borders, fonts, and clear button customization
- **Learn formatting options:** See formatting.md for culture support, custom patterns, and decimal precision
- **Add validation:** See restrictions.md for advanced min/max scenarios and null handling
- **Handle events:** See events-and-methods.md for ValueChanged, Completed, Focus events

---

## Common Getting-Started Issues

**Problem:** "SfNumericEntry" name not found
- **Solution:** Ensure xmlns:editors namespace is declared and points to correct assembly

**Problem:** Control not rendering
- **Solution:** Verify ConfigureSyncfusionToolkit() is called in MauiProgram.cs

**Problem:** NuGet package not found
- **Solution:** Check NuGet sources, ensure Syncfusion.Maui.Toolkit is spelled correctly

**Problem:** Value not updating
- **Solution:** Check ValueChangeMode, ensure ValueChanged event is wired up correctly

**Problem:** Format not applied
- **Solution:** CustomFormat only applies after validation (on blur or Enter key in OnLostFocus mode)
