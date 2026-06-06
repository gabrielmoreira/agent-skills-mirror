# Getting Started with NumericUpDown

## Table of Contents
- [Installation](#installation)
- [Handler Registration](#handler-registration)
- [Adding a Basic NumericUpDown](#adding-a-basic-numericupdown)
- [Validation Modes](#validation-modes)
- [First Render](#first-render)

## Installation

### Step 1: Install NuGet Package

1. **In Visual Studio:**
   - Right-click your project in Solution Explorer
   - Select **Manage NuGet Packages**
   - Search for `Syncfusion.Maui.Toolkit`
   - Click **Install** (latest version)

2. **Via Package Manager Console:**
   ```powershell
   Install-Package Syncfusion.Maui.Toolkit -Version <latest-version>
   ```

3. **Via dotnet CLI:**
   ```bash
   dotnet add package Syncfusion.Maui.Toolkit
   ```

### Verify Installation
After installation, the `Syncfusion.Maui.Toolkit` assembly should appear in your project's dependencies.

## Handler Registration

The Syncfusion toolkit handlers must be registered in your `MauiProgram.cs` file before using any Syncfusion controls.

**Step 1: Import the namespace**
```csharp
using Syncfusion.Maui.Toolkit.Hosting;
```

**Step 2: Call ConfigureSyncfusionToolkit() in CreateMauiApp()**
```csharp
public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        
        builder
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            })
            .ConfigureSyncfusionToolkit();  // ← Add this line
        
        return builder.Build();
    }
}
```

**Important:** `ConfigureSyncfusionToolkit()` must be called to register the platform-specific handlers. Without this, NumericUpDown will not render correctly.

## Adding a Basic NumericUpDown

### Method 1: XAML (Recommended)

**Step 1: Add namespace declaration**
```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:editors="clr-namespace:Syncfusion.Maui.Toolkit.NumericUpDown;assembly=Syncfusion.Maui.Toolkit"
             x:Class="MyApp.MainPage">
```

**Step 2: Add the control**
```xaml
<ContentPage.Content>
    <VerticalStackLayout Padding="20" Spacing="10">
        <Label Text="Enter a numeric value:" FontSize="16" FontAttributes="Bold" />
        
        <editors:SfNumericUpDown 
            x:Name="numericUpDown"
            HorizontalOptions="Center"
            VerticalOptions="Center"
            WidthRequest="200"
            HeightRequest="40" />
    </VerticalStackLayout>
</ContentPage.Content>
```

### Method 2: C# Code-Behind

```csharp
using Syncfusion.Maui.Toolkit.NumericUpDown;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        
        var numericUpDown = new SfNumericUpDown
        {
            HorizontalOptions = LayoutOptions.Center,
            VerticalOptions = LayoutOptions.Center,
            WidthRequest = 200,
            HeightRequest = 40
        };
        
        Content = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 10,
            Children =
            {
                new Label 
                { 
                    Text = "Enter a numeric value:", 
                    FontSize = 16,
                    FontAttributes = FontAttributes.Bold
                },
                numericUpDown
            }
        };
    }
}
```

## Validation Modes

NumericUpDown supports two validation modes controlled by the `ValueChangeMode` property:

### OnLostFocus (Default)
Value is validated and updated **only when:**
- Control loses focus (user clicks elsewhere)
- Enter key is pressed
- Control loses focus via tab navigation

**Use when:** You want to validate after the user finishes entering the complete value.

```xaml
<editors:SfNumericUpDown 
    ValueChangeMode="OnLostFocus"
    CustomFormat="0.000" />
```

**Behavior:**
- User types: `"123abc"`
- Alphabetic characters are automatically removed during typing
- Display remains unchanged: `"123abc"` (temporary)
- On focus loss or Enter: Value becomes `123` and displays as `123.000`

### OnKeyFocus
Value is validated and updated **with each key press** (real-time validation).

**Use when:** You want immediate feedback as the user types.

```xaml
<editors:SfNumericUpDown 
    ValueChangeMode="OnKeyFocus"
    CustomFormat="N2" />
```

**Behavior:**
- User types: `"5"`
- Value immediately updates to `5.00`
- User types: `"0"`
- Value immediately updates to `50.00`
- Non-numeric characters are rejected immediately

### Comparison Table

| Aspect | OnLostFocus | OnKeyFocus |
|--------|------------|-----------|
| **Validation** | On blur or Enter | Per keystroke |
| **Visual feedback** | Delayed | Immediate |
| **Performance** | Better (fewer updates) | Slightly more processing |
| **User experience** | Bulk validation | Real-time feedback |
| **Best for** | Final review | Currency/percentage input |

## First Render

### Minimal Example
```xaml
<editors:SfNumericUpDown />
```

**Output:** An empty numeric input field with up/down buttons ready for user input.

### With Initial Value
```xaml
<editors:SfNumericUpDown Value="50" />
```

**Output:** Field displays `50` with up/down buttons.

### Complete Practical Example
```xaml
<editors:SfNumericUpDown 
    x:Name="quantityInput"
    Value="1"
    Minimum="1"
    Maximum="100"
    SmallChange="1"
    LargeChange="5"
    Placeholder="Qty"
    CustomFormat="N0"
    HorizontalOptions="Center"
    WidthRequest="120"
    HeightRequest="40"
    ValueChanged="OnQuantityChanged" />
```

**C# Event Handler:**
```csharp
private void OnQuantityChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    Debug.WriteLine($"Quantity changed: {e.OldValue} → {e.NewValue}");
}
```

## Common Gotchas

**Issue 1: Control not appearing**
- ✅ **Solution:** Ensure `ConfigureSyncfusionToolkit()` is called in `MauiProgram.cs`

**Issue 2: Cannot type in the field**
- ✅ **Solution:** Check if `IsEditable` is set to `false` (it's `true` by default)

**Issue 3: Namespace not found in XAML**
- ✅ **Solution:** Ensure namespace is declared: `xmlns:editors="clr-namespace:Syncfusion.Maui.Toolkit.NumericUpDown;assembly=Syncfusion.Maui.Toolkit"`

**Issue 4: Value not updating after input**
- ✅ **Solution:** In OnLostFocus mode, press Enter or click outside the field to trigger validation

---
