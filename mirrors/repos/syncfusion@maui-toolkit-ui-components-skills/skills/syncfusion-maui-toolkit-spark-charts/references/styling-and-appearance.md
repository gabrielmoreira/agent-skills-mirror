# Styling and Appearance in Spark Charts

## Table of Contents
- [Overview](#overview)
- [Data Point Styling](#data-point-styling)
- [Color Properties Reference](#color-properties-reference)
- [Size and Spacing](#size-and-spacing)
- [Common Styling Patterns](#common-styling-patterns)
- [Complete Styling Example](#complete-styling-example)

## Overview

Customize your spark charts through:
- **Data Point Styling** - Highlight specific values (first, last, high, low, negative)
- **Color Customization** - Use Brush properties for precise control
- **Size & Spacing** - Adjust chart dimensions and padding
- **Appearance Properties** - Brush types and color formats

---

## Data Point Styling

### Concept

Data point styling allows you to apply different colors to specific data points based on their position or value:

- **FirstPointFill** - Color the first data point
- **LastPointFill** - Color the last data point
- **HighPointFill** - Color the highest value point
- **LowPointFill** - Color the lowest value point
- **NegativePointsFill** - Color negative values (Column and WinLoss charts only)

### Why Use Data Point Styling?

Visual emphasis without cluttering the chart:
- Highlight starting value (entry price for stocks)
- Highlight ending value (current price)
- Highlight peaks (best performance)
- Highlight valleys (worst performance)
- Highlight losses (negative values)

### Basic XAML Example

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    FirstPointFill="Green"
    LastPointFill="Red"
    HighPointFill="Gold"
    LowPointFill="Purple">
</sparkchart:SfSparkLineChart>
```

### Basic C# Example

```csharp
SfSparkLineChart sparkchart = new SfSparkLineChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
    FirstPointFill = new SolidColorBrush(Colors.Green),
    LastPointFill = new SolidColorBrush(Colors.Red),
    HighPointFill = new SolidColorBrush(Colors.Gold),
    LowPointFill = new SolidColorBrush(Colors.Purple)
};

this.Content = sparkchart;
```

---

## Color Properties Reference

### Supported Color Formats

#### Named Colors
```xaml
<sparkchart:SfSparkLineChart FirstPointFill="Green"/>
<sparkchart:SfSparkLineChart FirstPointFill="Red"/>
<sparkchart:SfSparkLineChart FirstPointFill="Blue"/>
```

#### Hex Colors (XAML)
```xaml
<sparkchart:SfSparkLineChart FirstPointFill="#FF0000"/>  <!-- Red -->
<sparkchart:SfSparkLineChart FirstPointFill="#00FF00"/>  <!-- Green -->
<sparkchart:SfSparkLineChart FirstPointFill="#0000FF"/>  <!-- Blue -->
```

#### SolidColorBrush (C#)
```csharp
sparkchart.FirstPointFill = new SolidColorBrush(Colors.Green);
sparkchart.FirstPointFill = new SolidColorBrush(Color.FromArgb("#FF0000"));
```

### All Data Point Color Properties

| Property | Type | Applies To | Purpose |
|----------|------|-----------|---------|
| `FirstPointFill` | Brush | All chart types | First data point color |
| `LastPointFill` | Brush | All chart types | Last data point color |
| `HighPointFill` | Brush | Line, Area, Column | Highest value point color |
| `LowPointFill` | Brush | Line, Area, Column | Lowest value point color |
| `NegativePointsFill` | Brush | Column, WinLoss | Negative values color |

---

## Size and Spacing

### Padding Property

Add space around chart content:

```xaml
<!-- No padding (default) -->
<sparkchart:SfSparkLineChart 
    Padding="0"
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"/>

<!-- Uniform padding -->
<sparkchart:SfSparkLineChart 
    Padding="10"
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"/>

<!-- Directional padding -->
<sparkchart:SfSparkLineChart 
    Padding="10,5,10,5"
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"/>
```

**Padding Values:**
- `"10"` - 10 pixels on all sides
- `"10,5"` - 10px left/right, 5px top/bottom
- `"10,5,15,20"` - left, top, right, bottom (in pixels)

### Why Use Padding?

- **Visual breathing room** - Prevents data from touching chart edges
- **Marker space** - Ensures markers don't get cut off
- **Axis clearance** - Provides space for axis display
- **Label area** - Reserves space for future labels

---

## Common Styling Patterns

### Pattern 1: Dashboard Summary Card

Minimal styling, compact display:

```xaml
<VerticalStackLayout Padding="10">
    <Label Text="Monthly Revenue" FontSize="14" FontAttributes="Bold"/>
    
    <sparkchart:SfSparkLineChart 
        ItemsSource="{Binding MonthlySales}" 
        YBindingPath="Amount"
        LastPointFill="Blue">
    </sparkchart:SfSparkLineChart>
    
    <Label Text="$1,250,000" FontSize="12" TextColor="Gray"/>
</VerticalStackLayout>
```

**Visual Effect:** Shows trend with last value highlighted in blue.

### Pattern 2: Performance Indicator

Emphasize performance extremes:

```csharp
SfSparkColumnChart sparkchart = new SfSparkColumnChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
    FirstPointFill = new SolidColorBrush(Colors.Green),
    LastPointFill = new SolidColorBrush(Colors.Blue),
    HighPointFill = new SolidColorBrush(Colors.Gold),
    LowPointFill = new SolidColorBrush(Colors.Red)
};

this.Content = sparkchart;
```

**Visual Effect:** Each significant point gets its own color for at-a-glance insight.

### Pattern 3: Stock Ticker

Show price movement with start/end emphasis:

```xaml
<sparkchart:SfSparkAreaChart 
    ItemsSource="{Binding DailyPrices}" 
    YBindingPath="Price"
    FirstPointFill="Blue"
    LastPointFill="Green">
</sparkchart:SfSparkAreaChart>
```

**Visual Effect:** Area chart shows trend magnitude; colors indicate opening (blue) and closing (green) prices.

### Pattern 4: Risk Visualization

Highlight negative values:

```xaml
<sparkchart:SfSparkColumnChart 
    ItemsSource="{Binding ProfitAndLoss}" 
    YBindingPath="Value"
    NegativePointsFill="Red"
    FirstPointFill="Green">
</sparkchart:SfSparkColumnChart>
```

**Visual Effect:** Losses show as red, start point as green. Quickly identifies risk.

### Pattern 5: Trend with Padding

High-visibility chart with breathing room:

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    Padding="15"
    ShowMarkers="True"
    FirstPointFill="Green"
    LastPointFill="Red">
    
    <sparkchart:SfSparkLineChart.MarkerSettings>
        <sparkchart:SparkChartMarkerSettings 
            Fill="LightBlue" 
            Height="5" 
            Width="5"/>
    </sparkchart:SfSparkLineChart.MarkerSettings>
    
</sparkchart:SfSparkLineChart>
```

**Visual Effect:** Large, padded chart with markers and colored endpoints for clarity.

---

## Data Point Styling Rules

### Precedence and Overlap

When a point matches multiple criteria, colors apply in this order:

```
1. NegativePointsFill (if value ≤ 0)
2. HighPointFill (if value is highest)
3. LowPointFill (if value is lowest)
4. FirstPointFill (if point is first in sequence)
5. LastPointFill (if point is last in sequence)
```

**Example:**
```
Data: [10, 20, 5]
├─ FirstPointFill = Green  (point: 10)
├─ HighPointFill = Gold    (point: 20) ← Highest
├─ LowPointFill = Red      (point: 5)  ← Lowest
└─ LastPointFill = Blue    (point: 5)  ← Also last

Result: Point 5 is colored RED (LowPointFill wins because it's the lowest)
        Point 20 is colored GOLD (HighPointFill)
        Point 10 is colored GREEN (FirstPointFill)
        (LastPointFill doesn't apply because LowPointFill takes precedence)
```

### Important: FirstPointFill Limitation

FirstPointFill colors the first point even if it's also the highest or lowest. However, if the first point is the highest, HighPointFill may override it. Test with your data to confirm behavior.

---

## Styling SparkWinLossChart

Win/Loss charts support FirstPointFill, LastPointFill, and NegativePointsFill:

```csharp
SfSparkWinLossChart sparkchart = new SfSparkWinLossChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Result",
    FirstPointFill = new SolidColorBrush(Colors.Orange),  // First result
    LastPointFill = new SolidColorBrush(Colors.Blue),     // Last result
    NegativePointsFill = new SolidColorBrush(Colors.Red)  // Losses
};

this.Content = sparkchart;
```

**Note:** HighPointFill and LowPointFill don't apply to WinLoss charts (data is binary).

---

## Performance Considerations

### Styling Impact

**Low impact:** FirstPointFill, LastPointFill
- Minimal rendering cost
- Use freely on any dataset size

**Moderate impact:** HighPointFill, LowPointFill
- Requires value comparison
- Acceptable for datasets < 1000 points

**Styling best practices:**
- Use point styling instead of markers for large datasets
- Avoid excessive brush creation in code-behind
- Create brushes once, reuse them

---

## Complete Styling Example

Full chart with all styling options:

```xaml
<sparkchart:SfSparkColumnChart 
    ItemsSource="{Binding QuarterlyData}" 
    YBindingPath="Revenue"
    Padding="15,10,15,10"
    FirstPointFill="Green"
    LastPointFill="Blue"
    HighPointFill="Gold"
    LowPointFill="Red"
    NegativePointsFill="DarkRed">
</sparkchart:SfSparkColumnChart>
```

**Result:**
- First quarter: Green column
- Last quarter: Blue column
- Best performing quarter: Gold column
- Worst performing quarter: Red column
- Any loss/negative values: Dark red columns
- Chart has 15px left/right and 10px top/bottom padding

---

## Color Selection Tips

### Best Practices

✅ **DO:**
- Use contrasting colors for different point types
- Test colors on target device/platform
- Use semantic colors (Green = good, Red = bad)
- Limit palette to 4-5 colors max
- Consider colorblind accessibility

❌ **DON'T:**
- Use similar colors for different point types
- Use very light colors on light backgrounds
- Overuse bright/neon colors
- Make styling more important than data clarity
- Ignore accessibility guidelines

### Color Accessibility

**Colorblind-friendly palette:**
```
Good: #0173B2 (blue), #DE8F05 (orange), #CC78BC (purple), #CA9161 (brown)
Avoid: Red-Green only combinations
Avoid: Light colors as only differentiation method
```

Consider using shape variation (for markers) + color for redundant encoding.

---

## Responsive Styling

Adjust styling based on device size:

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    Height="{OnPlatform iOS=80, Android=80, WinUI=100}"
    Width="{OnPlatform iOS=200, Android=200, WinUI=300}"
    Padding="{OnPlatform iOS=5, Android=5, WinUI=10}"
    FirstPointFill="Green"
    LastPointFill="Red">
</sparkchart:SfSparkLineChart>
```

Adapt chart size and padding for different screen sizes and platforms.
