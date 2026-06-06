# Data Binding in Spark Charts

## Overview

Data binding connects your sparkline to a data source. Three binding path properties handle all data flow:

| Property | Purpose | Example |
|----------|---------|---------|
| `ItemsSource` | The data collection | ObservableCollection<SalesData> |
| `YBindingPath` | Property containing Y-axis values | "Amount" |
| `XBindingPath` | Property containing X-axis labels/dates | "Month" (optional) |

---

## Supported Data Sources

### 1. ObservableCollection (Reactive Updates)

**Best for:** Dynamic data that changes during app runtime

```csharp
using System.Collections.ObjectModel;

public class SalesViewModel
{
    public ObservableCollection<SalesData> Data { get; set; }
    
    public SalesViewModel()
    {
        Data = new ObservableCollection<SalesData>
        {
            new SalesData { Month = "Jan", Amount = 100 },
            new SalesData { Month = "Feb", Amount = 150 },
            new SalesData { Month = "Mar", Amount = 120 }
        };
    }
    
    // Method to add new data dynamically
    public void AddNewSale(SalesData sale)
    {
        Data.Add(sale);  // Chart updates automatically
    }
}

public class SalesData
{
    public string Month { get; set; }
    public double Amount { get; set; }
}
```

**XAML:**
```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Amount">
</sparkchart:SfSparkLineChart>
```

**Advantages:**
- ✅ Chart auto-updates when items are added/removed
- ✅ Best for real-time dashboards
- ✅ Supports MVVM pattern

---

### 2. List<T> (Static Collections)

**Best for:** Fixed data that doesn't change

```csharp
public class SalesViewModel
{
    public List<SalesData> Data { get; set; }
    
    public SalesViewModel()
    {
        Data = new List<SalesData>
        {
            new SalesData { Month = "Jan", Amount = 100 },
            new SalesData { Month = "Feb", Amount = 150 },
            new SalesData { Month = "Mar", Amount = 120 }
        };
    }
}

public class SalesData
{
    public double Amount { get; set; }
}
```

**XAML:**
```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}" 
    YBindingPath="Amount">
</sparkchart:SfSparkLineChart>
```

**Advantages:**
- ✅ Simple setup
- ✅ Good performance for static data
- ❌ No automatic updates (reload required)

---

### 3. IEnumerable (LINQ Queries)

**Best for:** Filtered or transformed data from LINQ

```csharp
public class SalesViewModel
{
    private List<SalesData> AllSales { get; set; }
    
    public IEnumerable<SalesData> FilteredData 
    { 
        get 
        { 
            return AllSales.Where(s => s.Amount > 100);  // Filter: > 100
        } 
    }
    
    public SalesViewModel()
    {
        AllSales = new List<SalesData>
        {
            new SalesData { Amount = 80 },
            new SalesData { Amount = 150 },  // Included
            new SalesData { Amount = 120 }   // Included
        };
    }
}
```

**XAML:**
```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding FilteredData}" 
    YBindingPath="Amount">
</sparkchart:SfSparkLineChart>
```

**Use Cases:**
- Filter data above/below thresholds
- Sort data chronologically
- Project specific properties
- Aggregate data from multiple sources

---

## Binding Path Properties

### YBindingPath (Required)

Specifies which property contains Y-axis values. Must be numeric.

```csharp
public class DataPoint
{
    public double Value { get; set; }      // ✅ Can be used
    public decimal Price { get; set; }     // ✅ Can be used
    public int Count { get; set; }         // ✅ Can be used
    public string Name { get; set; }       // ❌ Cannot be used (not numeric)
}
```

**XAML:**
```xaml
<!-- Correct: numeric property -->
<sparkchart:SfSparkLineChart 
    YBindingPath="Value"
    ItemsSource="{Binding Data}"/>

<!-- Wrong: string property -->
<sparkchart:SfSparkLineChart 
    YBindingPath="Name"  <!-- Error: Name is not numeric -->
    ItemsSource="{Binding Data}"/>
```

### XBindingPath (Optional)

Specifies which property contains X-axis values. Used with categories or dates.

```csharp
public class SalesData
{
    public string Category { get; set; }  // Category axis
    public DateTime Date { get; set; }    // DateTime axis
    public int Quarter { get; set; }      // Numeric axis
    public double Amount { get; set; }    // Y values
}
```

**Categorical Example:**
```xaml
<sparkchart:SfSparkColumnChart 
    ItemsSource="{Binding Data}"
    YBindingPath="Amount"
    XBindingPath="Category"
    AxisType="Category">
</sparkchart:SfSparkColumnChart>
```

**DateTime Example:**
```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Data}"
    YBindingPath="Amount"
    XBindingPath="Date"
    AxisType="DateTime">
</sparkchart:SfSparkLineChart>
```

---

## Dynamic Data Updates

### ObservableCollection Reactivity

When using ObservableCollection, chart updates automatically:

```csharp
public class DashboardViewModel
{
    public ObservableCollection<SalesData> Data { get; set; }
    
    public DashboardViewModel()
    {
        Data = new ObservableCollection<SalesData>
        {
            new SalesData { Amount = 100 },
            new SalesData { Amount = 150 }
        };
    }
    
    // User clicks button to add new sale
    public void OnNewSaleDetected(double amount)
    {
        Data.Add(new SalesData { Amount = amount });
        // Chart automatically updates!
    }
    
    // Clear old data
    public void ClearData()
    {
        Data.Clear();
        // Chart becomes empty automatically
    }
}
```

### Real-Time Dashboard Example

```csharp
public class StockTickerViewModel
{
    private ObservableCollection<StockData> Prices { get; set; }
    
    public StockTickerViewModel()
    {
        Prices = new ObservableCollection<StockData>();
        
        // Simulate real-time price updates
        _ = UpdatePricesAsync();
    }
    
    private async Task UpdatePricesAsync()
    {
        while (true)
        {
            double newPrice = GetLatestPrice();  // From API
            Prices.Add(new StockData { Price = newPrice });
            
            // Keep only last 60 prices
            if (Prices.Count > 60)
                Prices.RemoveAt(0);
            
            await Task.Delay(1000);  // Update every second
        }
    }
}

public class StockData
{
    public double Price { get; set; }
}
```

**XAML:**
```xaml
<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding Prices}"
    YBindingPath="Price"
    Height="60"
    Width="200"/>
```

---

## Common Binding Patterns

### Pattern 1: Simple ListView with Sparklines

```xaml
<CollectionView ItemsSource="{Binding Products}">
    <CollectionView.ItemTemplate>
        <DataTemplate>
            <VerticalStackLayout Padding="10">
                <Label Text="{Binding Name}" FontAttributes="Bold"/>
                
                <sparkchart:SfSparkColumnChart 
                    ItemsSource="{Binding MonthlySales}"
                    YBindingPath="Amount"/>
                
                <Label Text="{Binding TotalRevenue, StringFormat='Total: ${0}'}" 
                       FontSize="12" TextColor="Gray"/>
            </VerticalStackLayout>
        </DataTemplate>
    </CollectionView.ItemTemplate>
</CollectionView>
```

**ViewModel:**
```csharp
public class ProductsViewModel
{
    public ObservableCollection<Product> Products { get; set; }
    
    public ProductsViewModel()
    {
        Products = new ObservableCollection<Product>
        {
            new Product 
            { 
                Name = "Widget A",
                MonthlySales = new ObservableCollection<SalesData> { ... }
            },
            new Product 
            { 
                Name = "Widget B",
                MonthlySales = new ObservableCollection<SalesData> { ... }
            }
        };
    }
}
```

### Pattern 2: Filtered Data with LINQ

```csharp
public class ReportsViewModel : INotifyPropertyChanged
{
    private List<TransactionData> AllTransactions { get; set; }
    private string _selectedCategory = "All";
    
    public string SelectedCategory
    {
        get => _selectedCategory;
        set
        {
            if (_selectedCategory != value)
            {
                _selectedCategory = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(FilteredTransactions));
            }
        }
    }
    
    public IEnumerable<TransactionData> FilteredTransactions
    {
        get
        {
            return SelectedCategory == "All"
                ? AllTransactions
                : AllTransactions.Where(t => t.Category == SelectedCategory);
        }
    }
    
    public event PropertyChangedEventHandler PropertyChanged;
    
    private void OnPropertyChanged([CallerMemberName] string name = "")
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }
}
```

**XAML:**
```xaml
<Picker Title="Filter" 
        ItemsSource="{Binding Categories}"
        SelectedItem="{Binding SelectedCategory}"/>

<sparkchart:SfSparkLineChart 
    ItemsSource="{Binding FilteredTransactions}"
    YBindingPath="Amount"/>
```

### Pattern 3: Data Aggregation

```csharp
public class AggregatedViewModel
{
    private List<DailyData> DetailedData { get; set; }
    
    public IEnumerable<AggregatedData> WeeklyData
    {
        get
        {
            return DetailedData
                .GroupBy(d => d.Date.AddDays(-(int)d.Date.DayOfWeek))  // Group by week
                .Select(g => new AggregatedData 
                { 
                    Week = g.Key, 
                    Total = g.Sum(d => d.Amount) 
                });
        }
    }
}
```

Aggregates daily data into weekly summaries for visualization.

---

## Data Binding Best Practices

### DO ✅

- **Use ObservableCollection for dynamic data** that needs real-time updates
- **Validate data before binding** - ensure YBindingPath values are numeric
- **Keep data models simple** - focus on properties used by the chart
- **Implement INotifyPropertyChanged** for computed properties (filtered data)
- **Use async operations** for large data loads (don't block UI)
- **Limit data points** for performance - consider data aggregation

### DON'T ❌

- **Don't use List<T> for dynamic data** - chart won't update automatically
- **Don't set invalid YBindingPath** - must point to numeric property
- **Don't bind to string properties** for Y-axis values
- **Don't load massive datasets** without filtering (> 10,000 points)
- **Don't recreate ItemsSource** constantly - reuse collections
- **Don't forget to set YBindingPath** - chart won't render without it

---

## Troubleshooting Binding Issues

### Issue: Chart is Empty

**Checklist:**
1. ✅ Is ItemsSource populated? (Check with breakpoint)
2. ✅ Is YBindingPath correct? (Must match property name exactly, case-sensitive)
3. ✅ Is YBindingPath property numeric? (not string, not null)
4. ✅ Is BindingContext set? (MainPage sets it in code-behind)

**Debug Code:**
```csharp
// In page code-behind
var viewModel = new MyViewModel();
Debug.WriteLine($"Data count: {viewModel.Data.Count}");
Debug.WriteLine($"First value: {viewModel.Data.FirstOrDefault()?.Amount}");
BindingContext = viewModel;
```

### Issue: Chart Not Updating When Data Changes

**Causes:**
- Using List<T> instead of ObservableCollection<T>
- ItemsSource reference changed (rather than items added/removed)
- Binding path incorrect

**Solution:**
```csharp
// ❌ Wrong: Chart won't update
public List<SalesData> Data { get; set; } = new();
Data = new List<SalesData> { ... };  // New reference

// ✅ Correct: Chart updates automatically
public ObservableCollection<SalesData> Data { get; set; } = new();
Data.Add(new SalesData { ... });  // Same collection, new item
```

### Issue: Null Reference in YBindingPath

**Cause:** Data values are null

**Solution:**
```csharp
// Ensure all items have valid numeric values
public class SalesData
{
    public double Amount { get; set; } = 0;  // Default value
}

// Or validate before adding
public void AddSale(double amount)
{
    if (amount < 0) amount = 0;  // Validate
    Data.Add(new SalesData { Amount = amount });
}
```

---

## Complete Binding Example

Full working example combining all patterns:

```csharp
// ViewModel with dynamic, filtered data
public class SalesAnalysisViewModel : INotifyPropertyChanged
{
    private ObservableCollection<SalesData> AllSales { get; set; }
    private string _selectedRegion = "All";
    
    public string SelectedRegion
    {
        get => _selectedRegion;
        set
        {
            if (_selectedRegion != value)
            {
                _selectedRegion = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(RegionalSales));
            }
        }
    }
    
    // Filtered data using IEnumerable
    public IEnumerable<SalesData> RegionalSales
    {
        get
        {
            return SelectedRegion == "All"
                ? AllSales
                : AllSales.Where(s => s.Region == SelectedRegion);
        }
    }
    
    public SalesAnalysisViewModel()
    {
        AllSales = new ObservableCollection<SalesData>
        {
            new SalesData { Region = "North", Amount = 100, Date = DateTime.Now.AddDays(-5) },
            new SalesData { Region = "South", Amount = 150, Date = DateTime.Now.AddDays(-4) },
            new SalesData { Region = "North", Amount = 120, Date = DateTime.Now.AddDays(-3) },
            new SalesData { Region = "East", Amount = 200, Date = DateTime.Now.AddDays(-2) },
            new SalesData { Region = "South", Amount = 180, Date = DateTime.Now.AddDays(-1) }
        };
    }
    
    public event PropertyChangedEventHandler PropertyChanged;
    
    private void OnPropertyChanged([CallerMemberName] string name = "")
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }
}

public class SalesData
{
    public string Region { get; set; }
    public double Amount { get; set; }
    public DateTime Date { get; set; }
}
```

**XAML:**
```xaml
<VerticalStackLayout>
    <Picker Title="Region" 
            SelectedItem="{Binding SelectedRegion}"
            ItemsSource="{Binding Regions}"/>
    
    <sparkchart:SfSparkLineChart 
        ItemsSource="{Binding RegionalSales}"
        YBindingPath="Amount"/>
</VerticalStackLayout>
```

This example demonstrates:
- ✅ ObservableCollection for reactive updates
- ✅ IEnumerable for filtered data
- ✅ INotifyPropertyChanged for dynamic filtering
- ✅ Proper MVVM binding pattern
