# Markers and Labels in Spark Charts

## Overview

Markers are visual indicators (symbols/dots) displayed at data points to highlight individual values. They enhance readability by making specific data points more prominent.

**Marker Support:**
- ✅ Available for: **SparkLineChart**, **SparkAreaChart**
- ❌ Not available for: SparkColumnChart (bars are self-explanatory), SparkWinLossChart

**Labels:**
Spark Charts are intentionally designed without traditional data labels to maintain their compact size. Use markers or styling instead to highlight specific points.

---

## Enabling Markers

### XAML
```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    ShowMarkers="True">
</sparkchart:SfSparkLineChart>
```

### C# Code-Behind
```csharp
SfSparkLineChart sparkchart = new SfSparkLineChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
    ShowMarkers = true  // Enable markers
};

this.Content = sparkchart;
```

---

## Default Marker Appearance

**Default Properties:**
- Shape: Circle
- Size: 4x4 pixels (Width: 4, Height: 4)
- Color: Blue (default brush)
- Border: No stroke by default

One marker appears at each data point. The default styling is usually sufficient for basic visualization.

---

## Marker Customization

### MarkerSettings Property

Customize marker appearance using the `MarkerSettings` property with `SparkChartMarkerSettings` class.

#### XAML Customization

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    ShowMarkers="True">
    
    <sparkchart:SfSparkLineChart.MarkerSettings>
        <sparkchart:SparkChartMarkerSettings 
            ShapeType="Diamond"
            Height="6"
            Width="6"
            Fill="Green"
            Stroke="DarkGreen"
            StrokeWidth="2"/>
    </sparkchart:SfSparkLineChart.MarkerSettings>
    
</sparkchart:SfSparkLineChart>
```

#### C# Code-Behind Customization

```csharp
SfSparkLineChart sparkchart = new SfSparkLineChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
    ShowMarkers = true,
    MarkerSettings = new SparkChartMarkerSettings
    {
        ShapeType = SparkChartMarkerShape.Diamond,
        Height = 6,
        Width = 6,
        Fill = new SolidColorBrush(Colors.Green),
        Stroke = new SolidColorBrush(Colors.DarkGreen),
        StrokeWidth = 2
    }
};

this.Content = sparkchart;
```

---

## Marker Customization Properties

### Shape Types

| Shape Type | Visual | Use Case |
|-----------|--------|----------|
| **Circle** | ● | Default, generic data points |
| **Diamond** | ◆ | Emphasis, highlighted points |
| **Square** | ■ | Data categories, distinct values |
| **Triangle** | ▲ | Trend direction, peaks |
| **Pentagon** | ⬠ | Special status, milestones |

#### Shape Selection Example

```xaml
<!-- Circle (default) -->
<sparkchart:SparkChartMarkerSettings ShapeType="Circle"/>

<!-- Diamond for emphasis -->
<sparkchart:SparkChartMarkerSettings ShapeType="Diamond"/>

<!-- Square for categorical data -->
<sparkchart:SparkChartMarkerSettings ShapeType="Square"/>
```

### Size Properties

**Width** and **Height** define marker dimensions in pixels.

```xaml
<!-- Small markers (2x2) -->
<sparkchart:SparkChartMarkerSettings Width="2" Height="2"/>

<!-- Medium markers (5x5) -->
<sparkchart:SparkChartMarkerSettings Width="5" Height="5"/>

<!-- Large markers (8x8) -->
<sparkchart:SparkChartMarkerSettings Width="8" Height="8"/>
```

**Recommendation:** Keep markers 3-6 pixels for sparklines to maintain visual balance in compact charts.

### Color Properties

#### Fill (Marker Fill Color)
```xaml
<sparkchart:SparkChartMarkerSettings Fill="Blue"/>
<sparkchart:SparkChartMarkerSettings Fill="#FF0000"/>  <!-- Red -->
```

#### Stroke (Marker Border Color)
```xaml
<sparkchart:SparkChartMarkerSettings 
    Stroke="DarkBlue"
    StrokeWidth="1"/>
```

#### Border Styling

```xaml
<sparkchart:SparkChartMarkerSettings 
    Fill="LightBlue"
    Stroke="DarkBlue"
    StrokeWidth="2"/>
```

---

## Common Marker Patterns

### Pattern 1: Subtle Markers

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    ShowMarkers="True">
    
    <sparkchart:SfSparkLineChart.MarkerSettings>
        <sparkchart:SparkChartMarkerSettings 
            ShapeType="Circle"
            Height="3"
            Width="3"
            Fill="Gray"/>
    </sparkchart:SfSparkLineChart.MarkerSettings>
    
</sparkchart:SfSparkLineChart>
```

**Use When:** You want markers for reference without dominating the visual.

### Pattern 2: Prominent Endpoint Markers

```csharp
SfSparkLineChart sparkchart = new SfSparkLineChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
    ShowMarkers = true,
    MarkerSettings = new SparkChartMarkerSettings
    {
        ShapeType = SparkChartMarkerShape.Circle,
        Height = 6,
        Width = 6,
        Fill = new SolidColorBrush(Colors.Green)
    },
    FirstPointFill = new SolidColorBrush(Colors.Green),  // Starting point
    LastPointFill = new SolidColorBrush(Colors.Red)      // Ending point
};

this.Content = sparkchart;
```

**Use When:** Highlighting the beginning and end of a trend with styled markers.

### Pattern 3: Outlined Markers

```xaml
<sparkchart:SparkChartMarkerSettings 
    ShapeType="Diamond"
    Height="5"
    Width="5"
    Fill="White"
    Stroke="Blue"
    StrokeWidth="2"/>
```

**Use When:** High contrast is needed for visibility on busy backgrounds.

### Pattern 4: Performance Indicator Markers

```xaml
<!-- Peak highlighting -->
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    ShowMarkers="True"
    HighPointFill="Gold">
    
    <sparkchart:SfSparkLineChart.MarkerSettings>
        <sparkchart:SparkChartMarkerSettings 
            ShapeType="Triangle"
            Height="6"
            Width="6"
            Fill="Gold"/>
    </sparkchart:SfSparkLineChart.MarkerSettings>
    
</sparkchart:SfSparkLineChart>
```

**Use When:** Emphasizing peaks, valleys, or trend extremes.

---

## Combining Markers with Point Styling

You can layer markers with data point styling for richer visualization:

```csharp
SfSparkLineChart sparkchart = new SfSparkLineChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
    ShowMarkers = true,
    
    // Marker customization
    MarkerSettings = new SparkChartMarkerSettings
    {
        Fill = new SolidColorBrush(Colors.LightBlue),
        Height = 4,
        Width = 4
    },
    
    // Data point styling
    FirstPointFill = new SolidColorBrush(Colors.Green),    // First point
    LastPointFill = new SolidColorBrush(Colors.Red),       // Last point
    HighPointFill = new SolidColorBrush(Colors.Gold),      // Highest value
    LowPointFill = new SolidColorBrush(Colors.Purple)      // Lowest value
};

this.Content = sparkchart;
```

**Result:** Default markers appear at every point, plus special coloring for first, last, high, and low points.

---

## Performance Considerations

### Marker Impact on Performance

**Marker rendering cost:**
- With markers: Slightly higher render time (depends on size/shape)
- Without markers: Baseline performance

**Dataset Size Guidelines:**

| Dataset Size | Recommendation |
|--------------|-----------------|
| < 50 points | Markers safe; can use large sizes (6-8px) |
| 50-200 points | Markers OK; keep smaller (3-5px) |
| 200+ points | Avoid markers; use styling instead |

### Optimization Tips

**For large datasets:**

```xaml
<!-- Instead of markers on 500 points... -->
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding LargeDataset}" 
    YBindingPath="Value"
    ShowMarkers="False"
    FirstPointFill="Green"
    LastPointFill="Red"
    HighPointFill="Gold">
</sparkchart:SfSparkLineChart>
```

Use point styling (FirstPointFill, LastPointFill, HighPointFill) instead of ShowMarkers for better performance with large datasets.

---

## Marker Visibility

### When Markers Are Hidden

Even with `ShowMarkers="True"`, markers may not be visible if:
1. **Marker size is 0:** Check Height/Width > 0
2. **Fill color matches background:** Ensure contrast
3. **Chart is too small:** Markers need space; use adequate chart dimensions
4. **Line covers markers:** Consider using outlined markers with borders

### Debugging Marker Visibility

```csharp
// Check marker settings
if (sparkchart.ShowMarkers)
{
    var settings = sparkchart.MarkerSettings;
    // Verify Height and Width are > 0
    // Verify Fill is not transparent
    // Verify chart Height/Width allow marker visibility
}
```

---

## Label Alternatives

Since traditional data labels aren't supported on sparklines (to maintain compact size), use these alternatives:

### Alternative 1: Tooltips (if framework supports)
Show values on hover (requires additional UI implementation)

### Alternative 2: Legends
Place sparkline in a card with a label above:
```xaml
<VerticalStackLayout>
    <Label Text="Monthly Sales" FontAttributes="Bold"/>
    <sparkchart:SfSparkLineChart 
        ItemsSource="{Binding Data}" 
        YBindingPath="Value"
        ShowMarkers="True"/>
</VerticalStackLayout>
```

### Alternative 3: Color Coding
Use FirstPointFill, LastPointFill, HighPointFill to indicate specific values:
```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    ShowMarkers="True"
    FirstPointFill="Green"       <!-- Start: Green -->
    LastPointFill="Red"          <!-- End: Red -->
    HighPointFill="Gold"/>       <!-- Peak: Gold -->
```

---

## Best Practices

✅ **DO:**
- Enable markers for small datasets (< 50 points)
- Keep marker size proportional to chart size
- Use contrasting colors for marker Fill and Stroke
- Combine markers with point styling for emphasis
- Test marker visibility on target devices

❌ **DON'T:**
- Enable markers on very large datasets (> 200 points)
- Use markers larger than 8x8 pixels in compact sparklines
- Make markers the same color as the line
- Add markers to WinLoss charts (not supported)
- Overcomplicate with too many marker style variations

---

## Reference: Complete Marker Customization Example

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    ShowMarkers="True"
    FirstPointFill="Green"
    LastPointFill="Red"
    HighPointFill="Gold"
    LowPointFill="Purple">
    
    <sparkchart:SfSparkLineChart.MarkerSettings>
        <sparkchart:SparkChartMarkerSettings 
            ShapeType="Circle"
            Height="5"
            Width="5"
            Fill="LightBlue"
            Stroke="DarkBlue"
            StrokeWidth="1"/>
    </sparkchart:SfSparkLineChart.MarkerSettings>
    
</sparkchart:SfSparkLineChart>
```

This displays a chart with:
- Markers at every data point (light blue circles with dark blue borders)
- Special coloring for start (green), end (red), peak (gold), and valley (purple)
