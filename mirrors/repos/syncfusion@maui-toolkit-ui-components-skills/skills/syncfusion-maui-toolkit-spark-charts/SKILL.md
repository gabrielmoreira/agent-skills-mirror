---
name: syncfusion-maui-toolkit-spark-charts
description: Use this skill ALWAYS when the user needs to implement Syncfusion MAUI Spark Charts. Triggers on spark chart, sparkline, micro-chart, trend visualization, data visualization in small spaces, chart types (line, area, column, win/loss), markers, range bands, axis configuration, data point styling. Also use immediately for chart customization, performance optimization, marker configuration, data binding patterns, accessibility needs.
metadata:
  author: "Syncfusion Inc"
  version: "1.0.0"
---

# Implementing Syncfusion .NET MAUI Spark Charts

## When to Use This Skill

Use this skill when implementing the **SfSparkChart** control in .NET MAUI applications. Spark Charts are lightweight, micro-visualization controls ideal for displaying data trends in compact spaces like dashboards, grids, and reports.

**Key Scenarios:**
- Displaying quick data trends without consuming significant UI space
- Visualizing sales trends, stock performance, or time-series data
- Showing positive/negative values in Win/Loss scenarios
- Creating dashboard components with multiple micro-charts
- Highlighting specific data points (first, last, high, low, negative values)

---

## Component Overview

The **SfSparkChart** is a compact charting control with four built-in chart types:

| Chart Type | Use Case | Best For |
|-----------|----------|----------|
| **SparkLineChart** | Line-based visualization | Identifying trends and patterns |
| **SparkAreaChart** | Filled area visualization | Emphasizing magnitude of change |
| **SparkColumnChart** | Vertical bar visualization | Comparing different data values |
| **SparkWinLossChart** | Win/Loss representation | Showing positive/negative scenarios |

**Core Features:**
- Data binding to ObservableCollection, List, or IEnumerable
- Four chart types for different visualization needs
- Marker display and customization (Line/Area charts only)
- Data point styling (first, last, high, low, negative)
- Axis display and origin customization
- Range band highlighting for value regions
- Lightweight and performance-optimized for micro-visualizations

---

## Documentation and Navigation Guide

### Getting Started
📄 **Read:** [references/getting-started.md](references/getting-started.md)
- Installation and NuGet package setup
- Project configuration (MauiProgram.cs handler registration)
- Basic SparkLineChart implementation
- Namespace imports and first render
- Data binding setup
- Copy-paste-ready starter code

### Chart Types
📄 **Read:** [references/chart-types.md](references/chart-types.md)
- Choosing the right chart type for your data
- SparkLineChart: Line-based trend visualization
- SparkAreaChart: Filled area representation
- SparkColumnChart: Vertical bar comparison
- SparkWinLossChart: Win/Loss scenarios
- When to use each type with code examples
- Common type selection patterns

### Markers and Labels
📄 **Read:** [references/markers-and-labels.md](references/markers-and-labels.md)
- Enabling markers on Line and Area charts
- Marker shape types and customization
- Marker styling properties (Fill, Stroke, StrokeWidth, Height, Width)
- Marker positioning and visibility
- Common marker patterns (highlighting endpoints, data points)
- Performance considerations for marker display

### Styling and Appearance
📄 **Read:** [references/styling-and-appearance.md](references/styling-and-appearance.md)
- Data point styling and color customization
- First, last, high, and low point highlighting
- Negative value styling for Column and WinLoss charts
- Brush and color properties
- Padding and spacing configuration
- Size customization and layout control
- Advanced styling examples

### Data Binding
📄 **Read:** [references/data-binding.md](references/data-binding.md)
- Binding to ObservableCollection for reactive updates
- Binding to List<T> for static data
- Binding to IEnumerable for LINQ queries
- XBindingPath and YBindingPath configuration
- Dynamic data source updates
- Common binding patterns and best practices

### Axis and Ranges
📄 **Read:** [references/axis-and-ranges.md](references/axis-and-ranges.md)
- Enabling axis display (ShowAxis property)
- Axis origin configuration for baseline reference
- Axis types (Numeric, Category, DateTime)
- XBindingPath property for category/time-based axes
- Range band visualization (RangeBandStart, RangeBandEnd, RangeBandFill)
- Axis line styling and customization
- Highlighting value regions and thresholds

---

## Quick Start Example

```csharp
// Step 1: Configure handler in MauiProgram.cs
using Syncfusion.Maui.Toolkit.Hosting;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .ConfigureSyncfusionToolkit()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
            });
        return builder.Build();
    }
}

// Step 2: Create basic SparkLineChart in XAML
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:sparkchart="clr-namespace:Syncfusion.Maui.Toolkit.SparkCharts;assembly=Syncfusion.Maui.Toolkit"
             x:Class="SparkChartDemo.MainPage">

    <sparkchart:SfSparkLineChart 
        ItemsSource="{Binding Data}" 
        YBindingPath="Value"
        ShowMarkers="True"
        HeightRequest="100"
        WidthRequest="150">
    </sparkchart:SfSparkLineChart>

</ContentPage>

// Step 3: Bind data from ViewModel
public class SparkDataViewModel
{
    public ObservableCollection<DataPoint> Data { get; set; }
    
    public SparkDataViewModel()
    {
        Data = new ObservableCollection<DataPoint>
        {
            new DataPoint { Value = 10 },
            new DataPoint { Value = 15 },
            new DataPoint { Value = 12 },
            new DataPoint { Value = 20 },
            new DataPoint { Value = 18 }
        };
    }
}

public class DataPoint
{
    public double Value { get; set; }
}
```

---

## Common Patterns

### Pattern 1: Dashboard Summary Card
```csharp
// Show quick sales trend in a card
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding MonthlySales}" 
    YBindingPath="Amount"
    ShowMarkers="False"
    FirstPointFill="Blue"
    LastPointFill="Red">
</sparkchart:SfSparkLineChart>
```

### Pattern 2: Performance Indicator with Threshold
```csharp
// Highlight data within acceptable range using RangeBand
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding PerformanceMetrics}" 
    YBindingPath="Value"
    ShowAxis="True"
    RangeBandStart="50"
    RangeBandEnd="100"
    RangeBandFill="LightGreen">
</sparkchart:SfSparkLineChart>
```

### Pattern 3: Win/Loss Visualization
```csharp
// Show positive and negative outcomes
<sparkchart:SfSparkWinLossChart 
    ItemsSource="{Binding GameResults}" 
    YBindingPath="Result"
    NegativePointsFill="Red">
</sparkchart:SfSparkWinLossChart>
```

### Pattern 4: Styled Data Points
```csharp
// Emphasize critical data points
<sparkchart:SfSparkColumnChart 
    ItemsSource="{Binding MonthlyRevenue}" 
    YBindingPath="Revenue"
    FirstPointFill="Green"
    LastPointFill="Blue"
    HighPointFill="Gold"
    LowPointFill="Red"
    NegativePointsFill="DarkRed">
</sparkchart:SfSparkColumnChart>
```

---

## Key Props Reference

### Core Properties
| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `ItemsSource` | IEnumerable | - | Data source for chart |
| `YBindingPath` | string | - | Property name for Y-axis values |
| `XBindingPath` | string | - | Property name for X-axis values |
| `Height` | double | - | Chart height in pixels |
| `Width` | double | - | Chart width in pixels |

### Display Properties
| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `ShowMarkers` | bool | false | Display markers (Line/Area only) |
| `ShowAxis` | bool | false | Display axis baseline |
| `Padding` | Thickness | 0 | Space around chart content |
| `AxisOrigin` | double | - | Y-axis value for axis line position |

### Styling Properties
| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `FirstPointFill` | Brush | - | Color of first data point |
| `LastPointFill` | Brush | - | Color of last data point |
| `HighPointFill` | Brush | - | Color of highest data point |
| `LowPointFill` | Brush | - | Color of lowest data point |
| `NegativePointsFill` | Brush | - | Color of negative values (Column/WinLoss) |

### Range Band Properties
| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `RangeBandStart` | double | - | Y-axis start value for range band |
| `RangeBandEnd` | double | - | Y-axis end value for range band |
| `RangeBandFill` | Brush | - | Color for range band region |

### Axis Properties
| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `AxisType` | SparkChartAxisType | Numeric | Axis scale type (Numeric, Category, DateTime) |
| `AxisLineStyle` | SparkChartLineStyle | - | Axis appearance (Stroke, StrokeWidth, StrokeDashArray) |

### Marker Properties (Line/Area Only)
| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `MarkerSettings` | SparkChartMarkerSettings | - | Marker customization configuration |

---

## Common Challenges & Solutions

### Issue: Chart appears empty
**Causes:** Missing ItemsSource binding, incorrect YBindingPath, data source is null  
**Solutions:**
1. Verify ItemsSource is properly bound to a populated collection
2. Confirm YBindingPath matches your data property name exactly
3. Check that data property is public and contains numeric values

### Issue: Markers not showing
**Note:** Markers only work on Line and Area charts  
**Solutions:**
1. Verify you're using SfSparkLineChart or SfSparkAreaChart
2. Set ShowMarkers="True" in XAML or code
3. Check MarkerSettings are not hiding markers (verify Height/Width > 0)

### Issue: Range band not visible
**Solutions:**
1. Verify RangeBandStart < RangeBandEnd
2. Ensure range values are within your data's Y-axis range
3. Check RangeBandFill is not transparent

### Issue: Poor performance with large datasets
**Solutions:**
1. Consider displaying only recent data points
2. Use aggregated data instead of raw values
3. Avoid excessive marker styling on large datasets
4. Disable ShowMarkers for performance-critical scenarios

---

## Next Steps

- **Ready to implement?** → Start with [Getting Started](references/getting-started.md)
- **Need specific features?** → Browse [Chart Types](references/chart-types.md), [Markers](references/markers-and-labels.md), or [Styling](references/styling-and-appearance.md)
- **Complex scenarios?** → Check [Data Binding](references/data-binding.md) and [Axis Configuration](references/axis-and-ranges.md)
