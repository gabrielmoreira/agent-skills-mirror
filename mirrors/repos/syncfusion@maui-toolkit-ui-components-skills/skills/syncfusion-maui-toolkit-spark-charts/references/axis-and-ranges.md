# Axis and Range Configuration in Spark Charts

## Overview

Axes provide context to your sparkline data:
- **Baseline reference** - Shows 0 or custom threshold
- **Value context** - Helps interpret scale
- **Range highlighting** - Emphasize acceptable value regions

---

## Axis Display

### ShowAxis Property

Enable axis display by setting `ShowAxis="True"`:

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    ShowAxis="True">
</sparkchart:SfSparkLineChart>
```

### Visual Effect

**Without Axis (Default):**
```
    /\    /\
   /  \  /  \
  /    \/    \
```

**With Axis (ShowAxis="True"):**
```
    /\    /\
   /  \  /  \
  /____\/____ \ ← Baseline at Y=0
```

The axis line appears at a baseline position, providing vertical context.

### When to Show Axis

✅ **Show axis when:**
- You want to highlight baseline (Y=0)
- Comparing values above/below zero
- Multiple sparklines need consistent reference
- Space permits (axis needs clear area)

❌ **Hide axis when:**
- Space is very limited
- All values are positive/negative (no crossing)
- Data pattern is obvious without baseline

---

## Axis Origin

### AxisOrigin Property

Position the axis at any Y-value using `AxisOrigin`:

```xaml
<!-- Default: axis at Y=0 -->
<sparkchart:SfSparkLineChart 
    ShowAxis="True"
    ItemsSource="{Binding Data}" 
    YBindingPath="Value">
</sparkchart:SfSparkLineChart>

<!-- Custom: axis at Y=50 -->
<sparkchart:SfSparkLineChart 
    ShowAxis="True"
    AxisOrigin="50"
    ItemsSource="{Binding Data}" 
    YBindingPath="Value">
</sparkchart:SfSparkLineChart>

<!-- Custom: axis at Y=100 -->
<sparkchart:SfSparkLineChart 
    ShowAxis="True"
    AxisOrigin="100"
    ItemsSource="{Binding Data}" 
    YBindingPath="Value">
</sparkchart:SfSparkLineChart>
```

### C# Code-Behind

```csharp
var chart = new SfSparkLineChart
{
    ItemsSource = viewModel.Data,
    YBindingPath = "Value",
    ShowAxis = true,
    AxisOrigin = 50  // Draw axis at Y=50
};

Content = chart;
```

### Use Cases

**Baseline at 0 (Default):**
- Performance vs. expectations
- Profit/loss calculations
- Any zero-crossing data

**Baseline at Target Value (e.g., 50):**
- Temperature monitoring (50° threshold)
- Performance targets
- Acceptable range boundaries

**Baseline at Max Value (e.g., 100):**
```csharp
double dataMax = Data.Max(d => d.Value);
chart.AxisOrigin = dataMax;
```

### Example: Temperature Monitoring

```xaml
<!-- Monitor temperature with axis at comfortable range (68°F) -->
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding TemperatureReadings}" 
    YBindingPath="Temperature"
    ShowAxis="True"
    AxisOrigin="68">
</sparkchart:SfSparkLineChart>
```

Values above 68 appear on top, values below appear on bottom—easy to spot deviation.

---

## Axis Types

### AxisType Property

The `AxisType` property determines how X-axis values are interpreted:

| AxisType | Purpose | Use Case |
|----------|---------|----------|
| **Numeric** | Numbers on X-axis | Index, sequence, quantities |
| **Category** | Category labels on X-axis | Product names, regions, zones |
| **DateTime** | Date/time values on X-axis | Time-series data, trends over time |

### Default: Numeric

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    AxisType="Numeric">
</sparkchart:SfSparkLineChart>
```

X-axis shows sequential numbers: 1, 2, 3, 4, 5...

### Category Axis

Use when X-values are category labels:

```xaml
<sparkchart:SfSparkColumnChart 
    ItemsSource="{Binding ProductData}" 
    YBindingPath="Sales"
    XBindingPath="ProductName"
    AxisType="Category">
</sparkchart:SfSparkColumnChart>
```

**Data Model:**
```csharp
public class ProductSales
{
    public string ProductName { get; set; }  // For X-axis
    public double Sales { get; set; }        // For Y-axis
}

Data = new ObservableCollection<ProductSales>
{
    new ProductSales { ProductName = "Widget A", Sales = 100 },
    new ProductSales { ProductName = "Widget B", Sales = 150 },
    new ProductSales { ProductName = "Widget C", Sales = 120 }
};
```

### DateTime Axis

Use when X-values are dates/times:

```xaml
<sparkchart:SfSparkAreaChart 
    ItemsSource="{Binding StockHistory}" 
    YBindingPath="Price"
    XBindingPath="TradeDate"
    AxisType="DateTime"
    ShowAxis="True">
</sparkchart:SfSparkAreaChart>
```

**Data Model:**
```csharp
public class StockData
{
    public DateTime TradeDate { get; set; }  // For X-axis
    public double Price { get; set; }        // For Y-axis
}

Data = new ObservableCollection<StockData>
{
    new StockData { TradeDate = DateTime.Now.AddDays(-5), Price = 100 },
    new StockData { TradeDate = DateTime.Now.AddDays(-4), Price = 105 },
    new StockData { TradeDate = DateTime.Now.AddDays(-3), Price = 98 }
};
```

**Benefit:** Chart respects time intervals and gaps.

---

## XBindingPath Property

### Purpose

The `XBindingPath` property specifies which data property to use for X-axis values.

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}"
    YBindingPath="Value"
    XBindingPath="Date">  <!-- Use "Date" property for X-axis -->
</sparkchart:SfSparkLineChart>
```

### Requirement

XBindingPath is typically used with **Category** or **DateTime** AxisType:

```xaml
<!-- Category: need product names on X-axis -->
<sparkchart:SfSparkColumnChart 
    YBindingPath="Amount"
    XBindingPath="Category"
    AxisType="Category">
</sparkchart:SfSparkColumnChart>

<!-- DateTime: need dates on X-axis -->
<sparkchart:SfSparkLineChart 
    YBindingPath="Value"
    XBindingPath="Date"
    AxisType="DateTime">
</sparkchart:SfSparkLineChart>
```

### Without XBindingPath

If you don't set XBindingPath with Numeric AxisType, X-axis shows item index:

```xaml
<!-- X-axis will show 0, 1, 2, 3... -->
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}"
    YBindingPath="Value"
    AxisType="Numeric">
</sparkchart:SfSparkLineChart>
```

---

## Axis Line Customization

### AxisLineStyle Property

Customize axis appearance with `AxisLineStyle`:

```xaml
<sparkchart:SfSparkLineChart 
    ShowAxis="True"
    ItemsSource="{Binding Data}" 
    YBindingPath="Value">
    
    <sparkchart:SfSparkLineChart.AxisLineStyle>
        <sparkchart:SparkChartLineStyle 
            Stroke="Blue"
            StrokeWidth="2"
            StrokeDashArray="4,2"/>
    </sparkchart:SfSparkLineChart.AxisLineStyle>
    
</sparkchart:SfSparkLineChart>
```

### Axis Line Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `Stroke` | Brush | Blue | Axis line color |
| `StrokeWidth` | double | 1 | Axis line thickness |
| `StrokeDashArray` | DoubleCollection | null | Dash pattern (e.g., "4,2") |

### Examples

**Solid Axis:**
```xaml
<sparkchart:SparkChartLineStyle 
    Stroke="Black"
    StrokeWidth="1"/>
```

**Dashed Axis:**
```xaml
<sparkchart:SparkChartLineStyle 
    Stroke="Gray"
    StrokeWidth="1"
    StrokeDashArray="4,2"/>  <!-- 4px line, 2px gap -->
```

**Thick Red Axis:**
```xaml
<sparkchart:SparkChartLineStyle 
    Stroke="Red"
    StrokeWidth="3"/>
```

### C# Code-Behind

```csharp
chart.AxisLineStyle = new SparkChartLineStyle
{
    Stroke = new SolidColorBrush(Colors.Blue),
    StrokeWidth = 2,
    StrokeDashArray = new DoubleCollection { 4, 2 }
};
```

---

## Range Bands

### Overview

Range bands highlight value regions along the Y-axis. Use to show:
- Acceptable value ranges
- Performance zones
- Threshold regions
- Safety limits

### RangeBand Properties

| Property | Type | Purpose |
|----------|------|---------|
| `RangeBandStart` | double | Y-axis start value for band |
| `RangeBandEnd` | double | Y-axis end value for band |
| `RangeBandFill` | Brush | Band color/fill |

### Basic Example

```xaml
<!-- Highlight the range 20-80 in light green -->
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Value"
    RangeBandStart="20"
    RangeBandEnd="80"
    RangeBandFill="LightGreen">
</sparkchart:SfSparkLineChart>
```

### C# Code-Behind

```csharp
SfSparkLineChart sparkchart = new SfSparkLineChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
    RangeBandStart = 20,
    RangeBandEnd = 80,
    RangeBandFill = new SolidColorBrush(Colors.LightGreen)
};

this.Content = sparkchart;
```

---

## Common Range Band Patterns

### Pattern 1: Performance Zone (Safe Range)

```xaml
<!-- Target range: 80-100 (e.g., performance score) -->
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding PerformanceData}" 
    YBindingPath="Score"
    RangeBandStart="80"
    RangeBandEnd="100"
    RangeBandFill="LightGreen"
    ShowAxis="True"
    AxisOrigin="50">
</sparkchart:SfSparkLineChart>
```

Values in the green zone indicate good performance.

### Pattern 2: Temperature Comfort Zone

```xaml
<!-- Comfortable temperature: 65-75°F -->
<sparkchart:SfSparkAreaChart 
    ItemsSource="{Binding TemperatureHistory}" 
    YBindingPath="Temperature"
    RangeBandStart="65"
    RangeBandEnd="75"
    RangeBandFill="#90EE90"
    ShowAxis="True"
    AxisOrigin="72">
</sparkchart:SfSparkAreaChart>
```

Visual indication of when temperature is in the comfort zone.

### Pattern 3: Alert Zone

```xaml
<!-- Alert: Values above 90 degrees -->
<sparkchart:SfSparkColumnChart 
    ItemsSource="{Binding CPUTemperature}" 
    YBindingPath="Temp"
    RangeBandStart="90"
    RangeBandEnd="110"
    RangeBandFill="LightCoral">
</sparkchart:SfSparkColumnChart>
```

Highlights critical temperature region in red.

### Pattern 4: Neutral Zone (Range for Context)

```xaml
<!-- Show acceptable range for decision support -->
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding SalesData}" 
    YBindingPath="Revenue"
    RangeBandStart="50000"
    RangeBandEnd="150000"
    RangeBandFill="#E0E0E0"
    ShowAxis="True"
    AxisOrigin="100000">
</sparkchart:SfSparkLineChart>
```

Gray band shows expected range without implying good/bad.

---

## Range Band Limitations

**Limitations:**
- ❌ Not available for **SfSparkWinLossChart**
- ❌ Only one range band per chart
- ⚠️ Range must be within data range for visibility

**Note:** To show multiple ranges, create multiple sparklines side-by-side.

---

## Complete Axis and Range Example

Full example combining all axis and range features:

```xaml
<!-- Sales performance with context axes and ranges -->
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding MonthlySales}" 
    YBindingPath="Amount"
    XBindingPath="Month"
    AxisType="Category"
    Padding="15"
    ShowAxis="True"
    AxisOrigin="5000"
    RangeBandStart="8000"
    RangeBandEnd="12000"
    RangeBandFill="LightGreen"
    FirstPointFill="Blue"
    LastPointFill="Red">
    
    <sparkchart:SfSparkLineChart.AxisLineStyle>
        <sparkchart:SparkChartLineStyle 
            Stroke="Gray"
            StrokeWidth="1.5"
            StrokeDashArray="3,3"/>
    </sparkchart:SfSparkLineChart.AxisLineStyle>
    
</sparkchart:SfSparkLineChart>
```

**Features:**
- ✅ Baseline at $5,000 (AxisOrigin)
- ✅ Target range highlighted: $8,000-$12,000 (green zone)
- ✅ Dashed gray axis line for subtle reference
- ✅ First and last months marked with colors

---

## Troubleshooting

### Issue: Axis Line Not Visible

**Causes:**
1. ShowAxis not set to True
2. Stroke color matches chart background
3. StrokeWidth too small

**Solution:**
```xaml
<sparkchart:SfSparkLineChart 
    ShowAxis="True"
    ItemsSource="{Binding Data}" 
    YBindingPath="Value">
    <sparkchart:SfSparkLineChart.AxisLineStyle>
        <sparkchart:SparkChartLineStyle 
            Stroke="Black"
            StrokeWidth="2"/>  <!-- Make it visible -->
    </sparkchart:SfSparkLineChart.AxisLineStyle>
</sparkchart:SfSparkLineChart>
```

### Issue: Range Band Not Showing

**Causes:**
1. RangeBandStart >= RangeBandEnd
2. Range is outside data bounds
3. RangeBandFill is transparent

**Solution:**
```csharp
// Verify range is valid and within data
double dataMin = Data.Min(d => d.Value);
double dataMax = Data.Max(d => d.Value);

if (rangeBandStart < dataMin) rangeBandStart = dataMin;
if (rangeBandEnd > dataMax) rangeBandEnd = dataMax;
if (rangeBandStart >= rangeBandEnd) rangeBandEnd = rangeBandStart + 10;
```
---

## Best Practices

✅ **DO:**
- Use ShowAxis="True" when baseline context is important
- Set appropriate AxisOrigin for your use case
- Use RangeBands to highlight acceptable ranges
- Combine axis and range styling for clarity
- Test range band visibility with real data

❌ **DON'T:**
- Leave AxisOrigin at zero if zero is outside data range
- Make range bands too wide (loses meaning)
- Use range bands on WinLoss charts (not supported)
- Ignore that range bands aren't available for all chart types
