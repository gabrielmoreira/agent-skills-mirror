# Getting Started with Spark Charts

## Installation and Setup

### Prerequisites
- .NET 8 SDK or later
- Visual Studio 2026 (v18.0.0 or later) with .NET MAUI support
- Syncfusion.Maui.Toolkit NuGet package

### Step 1: Install NuGet Package

In Solution Explorer, right-click your project and select **Manage NuGet Packages**. Search for `Syncfusion.Maui.Toolkit` and install the latest version.

The package includes all Syncfusion MAUI components including SparkCharts.

### Step 2: Register Handler in MauiProgram.cs

Add the Syncfusion toolkit handler to your app configuration:

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .ConfigureSyncfusionToolkit()  // Add this line
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

The `ConfigureSyncfusionToolkit()` method registers all Syncfusion component handlers, including SparkChart controls.

## Basic Implementation

### Step 1: Import Namespace

Add the SparkCharts namespace to your XAML:

```xaml
xmlns:sparkchart="clr-namespace:Syncfusion.Maui.Toolkit.SparkCharts;assembly=Syncfusion.Maui.Toolkit"
```

### Step 2: Add SparkLineChart to Page

The simplest implementation requires three properties:

```xaml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:sparkchart="clr-namespace:Syncfusion.Maui.Toolkit.SparkCharts;assembly=Syncfusion.Maui.Toolkit"
             x:Class="SparkChartDemo.MainPage">

    <sparkchart:SfSparkLineChart 
                       ItemsSource="{Binding Data}" 
                       YBindingPath="Value">
    </sparkchart:SfSparkLineChart>

</ContentPage>
```

**Required Properties:**
- `ItemsSource` - Your data collection
- `YBindingPath` - Property name containing numeric values

### Step 3: Create Data Model

Create a simple data model with numeric values:

```csharp
public class SalesData
{
    public double Value { get; set; }
    public string Month { get; set; }
}
```

### Step 4: Populate Data in ViewModel

```csharp
using System.Collections.ObjectModel;

public class SalesViewModel
{
    public ObservableCollection<SalesData> Data { get; set; }
    
    public SalesViewModel()
    {
        Data = new ObservableCollection<SalesData>
        {
            new SalesData { Month = "Jan", Value = 10 },
            new SalesData { Month = "Feb", Value = 15 },
            new SalesData { Month = "Mar", Value = 12 },
            new SalesData { Month = "Apr", Value = 20 },
            new SalesData { Month = "May", Value = 18 },
            new SalesData { Month = "Jun", Value = 25 }
        };
    }
}
```

### Step 5: Bind to Page

Set the binding context in your page code-behind:

```csharp
namespace SparkChartDemo;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        BindingContext = new SalesViewModel();
    }
}
```

## Minimal Working Example

Here's a complete, copy-paste-ready example:

**MainPage.xaml:**
```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:sparkchart="clr-namespace:Syncfusion.Maui.Toolkit.SparkCharts;assembly=Syncfusion.Maui.Toolkit"
             x:Class="SparkChartDemo.MainPage"
             Title="Spark Chart Demo">

    <VerticalStackLayout Padding="20" Spacing="20">
        <Label Text="Sales Trend" FontSize="18" FontAttributes="Bold"/>
        
        <sparkchart:SfSparkLineChart 
            ItemsSource="{Binding Data}" 
            YBindingPath="Value"
            ShowMarkers="True"/>
    </VerticalStackLayout>

</ContentPage>
```

**MainPage.xaml.cs:**
```csharp
namespace SparkChartDemo;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        BindingContext = new SalesViewModel();
    }
}
```

**ViewModel (SalesViewModel.cs):**
```csharp
using System.Collections.ObjectModel;

public class SalesViewModel
{
    public ObservableCollection<SalesData> Data { get; set; }
    
    public SalesViewModel()
    {
        Data = new ObservableCollection<SalesData>
        {
            new SalesData { Value = 2 },
            new SalesData { Value = 6 },
            new SalesData { Value = 8 },
            new SalesData { Value = 5 },
            new SalesData { Value = 10 },
            new SalesData { Value = 7 }
        };
    }
}

public class SalesData
{
    public double Value { get; set; }
}
```

## First Render

Run the application. You should see a small line chart showing your data trend with 6 points connected by a line.

**What you're seeing:**
- Line connecting all data points
- Data points marked with small dots when `ShowMarkers="True"`

## Common Variations

### Using C# Code-Behind Only (No XAML Binding)

```csharp
var viewModel = new SalesViewModel();

SfSparkLineChart sparkchart = new SfSparkLineChart()
{
    ItemsSource = viewModel.Data,
    YBindingPath = "Value",
    ShowMarkers = true
};

Content = sparkchart;
```

## Next: Choose Your Chart Type

After your first successful sparkline, explore [chart types](chart-types.md) to find the best visualization for your data:
- **SparkLineChart** - Current choice; great for trends
- **SparkAreaChart** - For emphasizing magnitude of change
- **SparkColumnChart** - For comparing discrete values
- **SparkWinLossChart** - For win/loss scenarios
