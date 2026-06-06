# Getting Started with OTP Input

## Table of Contents
- [Installation](#installation)
- [Handler Registration](#handler-registration)
- [Basic Implementation](#basic-implementation)
- [Setting Initial Values](#setting-initial-values)
- [XAML vs C# Implementation](#xaml-vs-c-implementation)

## Installation

To use the OTP Input component in your .NET MAUI application, follow these steps:

### Step 1: Install the Syncfusion MAUI Toolkit Package

1. In **Solution Explorer**, right-click your project and select **Manage NuGet Packages**
2. Search for [Syncfusion.Maui.Toolkit](https://www.nuget.org/packages/Syncfusion.Maui.Toolkit/)
3. Install the latest version
4. Ensure all dependencies are resolved correctly

## Handler Registration

The OTP Input component requires handler registration in your `MauiProgram.cs` file for proper initialization across all platforms.

### Register in MauiProgram.cs

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .ConfigureSyncfusionToolkit()  // Add this line
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        return builder.Build();
    }
}
```

**Important:** The `.ConfigureSyncfusionToolkit()` method MUST be called before `.UseMauiApp<App>()` to ensure proper initialization.

## Basic Implementation

### XAML Implementation

Add the OTP Input component to your XAML page:

```xml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:otpInput="clr-namespace:Syncfusion.Maui.Toolkit.OtpInput;assembly=Syncfusion.Maui.Toolkit"
             x:Class="OtpInputApp.MainPage"
             Title="OTP Verification">

    <VerticalStackLayout Padding="20" Spacing="20">
        <Label Text="Enter Verification Code"
               FontSize="24"
               FontAttributes="Bold" />

        <otpInput:SfOtpInput x:Name="OtpInput"
                             Length="6"
                             Type="Number"
                             StylingMode="Outlined" />

        <Button Text="Verify Code" Clicked="OnVerifyClicked" />
    </VerticalStackLayout>
</ContentPage>
```

**Key Points:**
- The XML namespace import is required: `xmlns:otpInput="clr-namespace:Syncfusion.Maui.Toolkit.OtpInput;assembly=Syncfusion.Maui.Toolkit"`
- `Length="6"` defines the number of input fields (typical for 6-digit OTP codes)
- `Type="Number"` restricts input to numeric values only
- `StylingMode="Outlined"` applies a bordered appearance

### C# Implementation

Create the OTP Input programmatically:

```csharp
using Syncfusion.Maui.Toolkit.OtpInput;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void SetupOtpInput()
    {
        // Create OTP Input component
        var otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number,
            StylingMode = OtpInputStyle.Outlined,
            HorizontalOptions = LayoutOptions.Center,
            VerticalOptions = LayoutOptions.Center
        };

        // Add to layout
        var stackLayout = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children =
            {
                new Label { Text = "Enter Verification Code", FontSize = 24 },
                otpInput,
                new Button { Text = "Verify Code" }
            }
        };

        Content = stackLayout;
    }
}
```

## Setting Initial Values

You can set the OTP value programmatically using the `Value` property:

### XAML with Initial Value

```xml
<otpInput:SfOtpInput x:Name="OtpInput"
                     Length="6"
                     Type="Number"
                     Value="123456" />
```

### C# Code

```csharp
// Set value after creation
OtpInput.Value = "123456";

// Verify the entered value
string enteredOtp = OtpInput.Value;
if (enteredOtp.Length == 6)
{
    Console.WriteLine("OTP is complete: " + enteredOtp);
}
```

## XAML vs C# Implementation

### XAML Approach (Recommended)

**Advantages:**
- Declarative and easy to read
- Better design-time support in Visual Studio
- Easier to modify layout in XAML designer
- Clear separation of UI and logic

```xml
<otpInput:SfOtpInput x:Name="OtpInput"
                     Length="6"
                     Type="Number"
                     StylingMode="Outlined"
                     ValueChanged="OnValueChanged" />
```

**Code-Behind:**
```csharp
private void OnValueChanged(object sender, OtpInputValueChangedEventArgs e)
{
    if (e.NewValue?.Length == 6)
    {
        Console.WriteLine("OTP Complete: " + e.NewValue);
    }
}
```

### C# Approach

**Advantages:**
- Fully programmatic control
- Dynamic component creation
- Complex conditional logic possible
- Useful for dynamically generated UIs

```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    StylingMode = OtpInputStyle.Outlined
};

otpInput.ValueChanged += (s, e) =>
{
    if (e.NewValue?.Length == 6)
    {
        Console.WriteLine("OTP Complete: " + e.NewValue);
    }
};

MainStackLayout.Children.Add(otpInput);
```

## Common Setup Mistakes to Avoid

### ❌ Forgetting Handler Registration
```csharp
// WRONG - Missing ConfigureSyncfusionToolkit()
builder.UseMauiApp<App>();
```

**FIX:**
```csharp
// CORRECT
builder.ConfigureSyncfusionToolkit()
       .UseMauiApp<App>();
```

### ❌ Missing XML Namespace in XAML
```xml
<!-- WRONG -->
<SfOtpInput Length="6" />
```

**FIX:**
```xml
<!-- CORRECT -->
<otpInput:SfOtpInput Length="6" 
    xmlns:otpInput="clr-namespace:Syncfusion.Maui.Toolkit.OtpInput;assembly=Syncfusion.Maui.Toolkit" />
```

### ❌ Not Checking Length Before Processing
```csharp
// WRONG - Value might be incomplete
string otp = OtpInput.Value;  // Could be "12345" instead of "123456"
VerifyOtp(otp);
```

**FIX:**
```csharp
// CORRECT - Verify completeness
if (OtpInput.Value?.Length == OtpInput.Length)
{
    VerifyOtp(OtpInput.Value);
}
```
