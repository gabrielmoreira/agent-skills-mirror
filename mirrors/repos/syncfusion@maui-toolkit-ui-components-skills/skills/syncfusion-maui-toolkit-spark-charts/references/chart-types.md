# Chart Types in Spark Charts

## Table of Contents
- [Overview](#overview)
- [SparkLineChart](#sparklinechart)
- [SparkAreaChart](#sparkareachart)
- [SparkColumnChart](#sparkcolumnchart)
- [SparkWinLossChart](#sparkwinlosschart)
- [Type Selection Guide](#type-selection-guide)

## Overview

Spark Charts support four distinct visualization types. Choose the type that best matches your data characteristics and visualization goals.

| Chart Type | Use Case | Best For | Data Pattern |
|-----------|----------|----------|--------------|
| **Line** | Trend identification | Time-series data, continuous trends | Sequential numeric values |
| **Area** | Magnitude emphasis | Stacked visualization, rate of change | Sequential numeric values |
| **Column** | Value comparison | Discrete categories, bar charts | Categorical or discrete data |
| **WinLoss** | Binary outcomes | Positive/negative, win/loss | Binary or discrete positive/negative |

---

## SparkLineChart

### Purpose
The most common sparkline type. Displays data as a series of connected points forming a line. Use for identifying patterns, trends, and turning points.

### When to Use
- Tracking performance metrics over time
- Showing sales trends
- Visualizing stock price movement
- Displaying temperature or weather data over time
- Highlighting seasonal effects

### XAML Implementation

```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding MonthlySales}" 
    YBindingPath="Amount">
</sparkchart:SfSparkLineChart>
```

### Code-Behind Implementation

```csharp
SfSparkLineChart sparkchart = new SfSparkLineChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
};

this.Content = sparkchart;
```

### Data Model
```csharp
public class SalesData
{
    public double Amount { get; set; }  // For YBindingPath
    public DateTime Date { get; set; }   // Optional: For visual reference
}
```

### Sample Data
```csharp
Data = new ObservableCollection<SalesData>
{
    new SalesData { Amount = 10 },
    new SalesData { Amount = 15 },
    new SalesData { Amount = 12 },
    new SalesData { Amount = 20 },
    new SalesData { Amount = 18 },
    new SalesData { Amount = 22 }
};
```

### Key Features
- ✅ Line connects all data points
- ✅ ShowMarkers property enables dot markers at each point
- ✅ Supports styling specific points (first, last, high, low, negative)
- ✅ Works with axis display and range bands

---

## SparkAreaChart

### Purpose
Similar to SparkLineChart but with the area below the line filled in. Emphasizes the magnitude of change and the overall trend.

### When to Use
- Showing cumulative data (e.g., total revenue buildup)
- Emphasizing the magnitude of metric change
- Visualizing filled visualizations for better visibility
- Creating stacked or layered area representations
- Highlighting total capacity vs usage

### XAML Implementation

```xaml
<sparkchart:SfSparkAreaChart 
    ItemsSource="{Binding RevenueData}" 
    YBindingPath="Total">
</sparkchart:SfSparkAreaChart>
```

### Code-Behind Implementation

```csharp
SfSparkAreaChart sparkchart = new SfSparkAreaChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
};

this.Content = sparkchart;
```

### Key Differences from Line Chart
- Area below line is **filled** with default brush color
- Better visual impact for magnitude comparison
- Supports same marker functionality as Line charts
- Same styling properties (FirstPointFill, LastPointFill, etc.)

---

## SparkColumnChart

### Purpose
Displays data as vertical bars. Each data point becomes a column. Use for comparing discrete values or categories.

### When to Use
- Comparing performance across different categories
- Showing inventory levels by warehouse
- Displaying sales by product category
- Visualizing frequency distribution
- Comparing values at specific points in time (not trends)

### XAML Implementation

```xaml
<sparkchart:SfSparkColumnChart 
    ItemsSource="{Binding ProductData}" 
    YBindingPath="Sales">
</sparkchart:SfSparkColumnChart>
```

### Code-Behind Implementation

```csharp
SfSparkColumnChart sparkchart = new SfSparkColumnChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Value",
};

this.Content = sparkchart;
```

### Key Features
- ✅ NegativePointsFill property colors negative values differently
- ✅ Works with Category axis types
- ✅ Supports FirstPointFill, LastPointFill, HighPointFill, LowPointFill styling
- ✅ Ideal for dashboard KPI cards

---

## SparkWinLossChart

### Purpose
Specialized chart for binary outcomes. Shows positive values as wins (one color) and negative/zero values as losses (different color). Commonly used for sports records, success rates, or binary state indicators.

### When to Use
- Showing win/loss records in sports
- Displaying success/failure patterns in tests
- Showing up/down days in stock performance
- Visualizing pass/fail results over time
- Displaying positive/negative binary outcomes

### XAML Implementation

```xaml
<sparkchart:SfSparkWinLossChart 
    ItemsSource="{Binding GameResults}" 
    YBindingPath="Result">
</sparkchart:SfSparkWinLossChart>
```

### Code-Behind Implementation

```csharp
SfSparkWinLossChart sparkchart = new SfSparkWinLossChart()
{
    ItemsSource = new SparkChartViewModel().Data,
    YBindingPath = "Result",
};

this.Content = sparkchart;
```

### Data Format

Use positive and negative/zero values to represent outcomes:
- **Positive values** → Wins (default color)
- **Zero or negative values** → Losses (NegativePointsFill color)

```csharp
public class GameResult
{
    public double Result { get; set; }  // 1 for win, 0/-1 for loss
}

Data = new ObservableCollection<GameResult>
{
    new GameResult { Result = 1 },      // Win
    new GameResult { Result = 1 },      // Win
    new GameResult { Result = 0 },      // Loss
    new GameResult { Result = 1 },      // Win
    new GameResult { Result = -1 },     // Loss
    new GameResult { Result = 1 }       // Win
};
```

### Styling for Win/Loss

```xaml
<sparkchart:SfSparkWinLossChart 
    ItemsSource="{Binding GameResults}" 
    YBindingPath="Result"
    PositivePointsFill="Green"
    NeutralPointFill="Blue"
    NegativePointsFill="Red">
</sparkchart:SfSparkWinLossChart>
```

### Key Features
- ✅ NegativePointsFill colors losses/zeros
- ✅ Compact binary visualization
- ✅ Supports PositivePointsFill and NeutralPointFill styling (only for SfSparkWinLossChart)
- ✅ No axis display available (specialized for binary data)

---

## Type Selection Guide

### Decision Tree

```
1. What's your data pattern?
   ├─ Continuous numeric trend? → SparkLineChart
   │  (Sales over time, temperature trend)
   │
   ├─ Magnitude/accumulation emphasis needed? → SparkAreaChart
   │  (Revenue buildup, capacity utilization)
   │
   ├─ Discrete categories or values to compare? → SparkColumnChart
   │  (Product sales by category, inventory levels)
   │
   └─ Binary outcomes (win/loss, success/fail)? → SparkWinLossChart
      (Game records, test results)
```

### Common Scenarios & Recommendations

**Scenario: Sales Trend Dashboard**
```
Data: Monthly sales values over 12 months
Best Choice: SparkLineChart
Why: Continuous trend showing month-to-month changes
```

**Scenario: Quarterly Performance Comparison**
```
Data: Q1, Q2, Q3, Q4 revenue
Best Choice: SparkColumnChart
Why: Discrete categories being compared, not a continuous trend
```

**Scenario: Market Share Growth**
```
Data: Cumulative revenue over time
Best Choice: SparkAreaChart
Why: Emphasizing the magnitude of growth and accumulation
```

**Scenario: Test Results Record**
```
Data: Pass/Fail results for 20 tests
Best Choice: SparkWinLossChart
Why: Binary outcomes, compact visualization of success rate
```

### Feature Availability by Type

| Feature | Line | Area | Column | WinLoss |
|---------|------|------|--------|---------|
| ShowMarkers | ✅ | ✅ | ❌ | ❌ |
| Axis Display | ✅ | ✅ | ✅ | ❌ |
| Range Bands | ✅ | ✅ | ✅ | ❌ |
| FirstPointFill | ✅ | ✅ | ✅ | ✅ |
| LastPointFill | ✅ | ✅ | ✅ | ✅ |
| HighPointFill | ✅ | ✅ | ✅ | ❌ |
| LowPointFill | ✅ | ✅ | ✅ | ❌ |
| NegativePointsFill | ✅ | ✅ | ✅ | ✅ |

---

## Switching Between Types

You can easily change chart types by substituting the control:

```csharp
// Start with Line
<sparkchart:SfSparkLineChart ItemsSource="{Binding Data}" YBindingPath="Value"/>

// Change to Area - same data, different visual
<sparkchart:SfSparkAreaChart ItemsSource="{Binding Data}" YBindingPath="Value"/>

// All bindings and properties remain compatible
```

The same data model and binding paths work across all types—just change the control name to see a different visualization.
