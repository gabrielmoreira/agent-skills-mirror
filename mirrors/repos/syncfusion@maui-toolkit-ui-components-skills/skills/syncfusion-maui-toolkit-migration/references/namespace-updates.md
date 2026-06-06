# Namespace Updates: Complete Reference

## Table of Contents

- [XAML Namespace Changes](#xaml-namespace-changes)
- [C# Namespace Changes](#c-namespace-changes)
- [Assembly and Package Changes](#assembly-and-package-changes)
- [Search and Replace Patterns](#search-and-replace-patterns)
- [Real-World Migration Examples](#real-world-migration-examples)
- [Troubleshooting Namespace Issues](#troubleshooting-namespace-issues)

## XAML Namespace Changes

Use this table to update XAML namespace declarations in your `.xaml` files. Replace the "Old Namespace" with the "New Namespace" for each control.

| Component | Old XAML Namespace | New XAML Namespace | Example |
|-----------|-------------------|-------------------|---------|
| **SfAccordion** | `xmlns:accordion="clr-namespace:Syncfusion.Maui.Accordion;assembly=Syncfusion.Maui.Expander"` | `xmlns:accordion="clr-namespace:Syncfusion.Maui.Toolkit.Accordion;assembly=Syncfusion.Maui.Toolkit"` | `<accordion:SfAccordion>` |
| **SfButton** | `xmlns:button="clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons"` | `xmlns:button="clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit"` | `<button:SfButton>` |
| **SfCalendar** | `xmlns:calendar="clr-namespace:Syncfusion.Maui.Calendar;assembly=Syncfusion.Maui.Calendar"` | `xmlns:calendar="clr-namespace:Syncfusion.Maui.Toolkit.Calendar;assembly=Syncfusion.Maui.Toolkit"` | `<calendar:SfCalendar>` |
| **SfCards** | `xmlns:cards="clr-namespace:Syncfusion.Maui.Cards;assembly=Syncfusion.Maui.Cards"` | `xmlns:cards="clr-namespace:Syncfusion.Maui.Toolkit.Cards;assembly=Syncfusion.Maui.Toolkit"` | `<cards:SfCard>` |
| **SfCarousel** | `xmlns:carousel="clr-namespace:Syncfusion.Maui.Carousel;assembly=Syncfusion.Maui.Carousel"` | `xmlns:carousel="clr-namespace:Syncfusion.Maui.Toolkit.Carousel;assembly=Syncfusion.Maui.Toolkit"` | `<carousel:SfCarousel>` |
| **SfCartesianChart** | `xmlns:chart="clr-namespace:Syncfusion.Maui.Charts;assembly=Syncfusion.Maui.Charts"` | `xmlns:chart="clr-namespace:Syncfusion.Maui.Toolkit.Charts;assembly=Syncfusion.Maui.Toolkit"` | `<chart:SfCartesianChart>` |
| **SfCircularChart** | `xmlns:chart="clr-namespace:Syncfusion.Maui.Charts;assembly=Syncfusion.Maui.Charts"` | `xmlns:chart="clr-namespace:Syncfusion.Maui.Toolkit.Charts;assembly=Syncfusion.Maui.Toolkit"` | `<chart:SfCircularChart>` |
| **SfCircularProgressBar** | `xmlns:progressBar="clr-namespace:Syncfusion.Maui.ProgressBar;assembly=Syncfusion.Maui.ProgressBar"` | `xmlns:progressBar="clr-namespace:Syncfusion.Maui.Toolkit.ProgressBar;assembly=Syncfusion.Maui.Toolkit"` | `<progressBar:SfCircularProgressBar>` |
| **SfChip** | `xmlns:chip="clr-namespace:Syncfusion.Maui.Core;assembly=Syncfusion.Maui.Core"` | `xmlns:chip="clr-namespace:Syncfusion.Maui.Toolkit.Chips;assembly=Syncfusion.Maui.Toolkit"` | `<chip:SfChip>` |
| **SfEffectsView** | `xmlns:effectsView="clr-namespace:Syncfusion.Maui.Core;assembly=Syncfusion.Maui.Core"` | `xmlns:effectsView="clr-namespace:Syncfusion.Maui.Toolkit.EffectsView;assembly=Syncfusion.Maui.Toolkit"` | `<effectsView:SfEffectsView>` |
| **SfExpander** | `xmlns:expander="clr-namespace:Syncfusion.Maui.Expander;assembly=Syncfusion.Maui.Expander"` | `xmlns:expander="clr-namespace:Syncfusion.Maui.Toolkit.Expander;assembly=Syncfusion.Maui.Toolkit"` | `<expander:SfExpander>` |
| **SfFunnelChart** | `xmlns:chart="clr-namespace:Syncfusion.Maui.Charts;assembly=Syncfusion.Maui.Charts"` | `xmlns:chart="clr-namespace:Syncfusion.Maui.Toolkit.Charts;assembly=Syncfusion.Maui.Toolkit"` | `<chart:SfFunnelChart>` |
| **SfLinearProgressBar** | `xmlns:progressBar="clr-namespace:Syncfusion.Maui.ProgressBar;assembly=Syncfusion.Maui.ProgressBar"` | `xmlns:progressBar="clr-namespace:Syncfusion.Maui.Toolkit.ProgressBar;assembly=Syncfusion.Maui.Toolkit"` | `<progressBar:SfLinearProgressBar>` |
| **SfNavigationDrawer** | `xmlns:navigationDrawer="clr-namespace:Syncfusion.Maui.NavigationDrawer;assembly=Syncfusion.Maui.NavigationDrawer"` | `xmlns:navigationDrawer="clr-namespace:Syncfusion.Maui.Toolkit.NavigationDrawer;assembly=Syncfusion.Maui.Toolkit"` | `<navigationDrawer:SfNavigationDrawer>` |
| **SfNumericEntry** | `xmlns:numericEntry="clr-namespace:Syncfusion.Maui.Inputs;assembly=Syncfusion.Maui.Inputs"` | `xmlns:numericEntry="clr-namespace:Syncfusion.Maui.Toolkit.NumericEntry;assembly=Syncfusion.Maui.Toolkit"` | `<numericEntry:SfNumericEntry>` |
| **SfNumericUpDown** | `xmlns:numericUpDown="clr-namespace:Syncfusion.Maui.Inputs;assembly=Syncfusion.Maui.Inputs"` | `xmlns:numericUpDown="clr-namespace:Syncfusion.Maui.Toolkit.NumericUpDown;assembly=Syncfusion.Maui.Toolkit"` | `<numericUpDown:SfNumericUpDown>` |
| **SfPicker** | `xmlns:picker="clr-namespace:Syncfusion.Maui.Picker;assembly=Syncfusion.Maui.Picker"` | `xmlns:picker="clr-namespace:Syncfusion.Maui.Toolkit.Picker;assembly=Syncfusion.Maui.Toolkit"` | `<picker:SfPicker>` |
| **SfPopup** | `xmlns:popup="clr-namespace:Syncfusion.Maui.Popup;assembly=Syncfusion.Maui.Popup"` | `xmlns:popup="clr-namespace:Syncfusion.Maui.Toolkit.Popup;assembly=Syncfusion.Maui.Toolkit"` | `<popup:SfPopup>` |
| **SfPullToRefresh** | `xmlns:pullToRefresh="clr-namespace:Syncfusion.Maui.PullToRefresh;assembly=Syncfusion.Maui.PullToRefresh"` | `xmlns:pullToRefresh="clr-namespace:Syncfusion.Maui.Toolkit.PullToRefresh;assembly=Syncfusion.Maui.Toolkit"` | `<pullToRefresh:SfPullToRefresh>` |
| **SfSegmentedControl** | `xmlns:segmentedControl="clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons"` | `xmlns:segmentedControl="clr-namespace:Syncfusion.Maui.Toolkit.SegmentedControl;assembly=Syncfusion.Maui.Toolkit"` | `<segmentedControl:SfSegmentedControl>` |
| **SfShimmer** | `xmlns:shimmer="clr-namespace:Syncfusion.Maui.Shimmer;assembly=Syncfusion.Maui.Core"` | `xmlns:shimmer="clr-namespace:Syncfusion.Maui.Toolkit.Shimmer;assembly=Syncfusion.Maui.Toolkit"` | `<shimmer:SfShimmer>` |
| **SfSunburstChart** | `xmlns:sunburst="clr-namespace:Syncfusion.Maui.SunburstChart;assembly=Syncfusion.Maui.SunburstChart"` | `xmlns:sunburst="clr-namespace:Syncfusion.Maui.Toolkit.SunburstChart;assembly=Syncfusion.Maui.Toolkit"` | `<sunburst:SfSunburstChart>` |
| **SfTabView** | `xmlns:tabView="clr-namespace:Syncfusion.Maui.TabView;assembly=Syncfusion.Maui.TabView"` | `xmlns:tabView="clr-namespace:Syncfusion.Maui.Toolkit.TabView;assembly=Syncfusion.Maui.Toolkit"` | `<tabView:SfTabView>` |
| **SfTextInputLayout** | `xmlns:inputLayout="clr-namespace:Syncfusion.Maui.Core;assembly=Syncfusion.Maui.Core"` | `xmlns:inputLayout="clr-namespace:Syncfusion.Maui.Toolkit.TextInputLayout;assembly=Syncfusion.Maui.Toolkit"` | `<inputLayout:SfTextInputLayout>` |
| **SfPolarChart** | `xmlns:chart="clr-namespace:Syncfusion.Maui.Charts;assembly=Syncfusion.Maui.Charts"` | `xmlns:chart="clr-namespace:Syncfusion.Maui.Toolkit.Charts;assembly=Syncfusion.Maui.Toolkit"` | `<chart:SfPolarChart>` |
| **SfPyramidChart** | `xmlns:chart="clr-namespace:Syncfusion.Maui.Charts;assembly=Syncfusion.Maui.Charts"` | `xmlns:chart="clr-namespace:Syncfusion.Maui.Toolkit.Charts;assembly=Syncfusion.Maui.Toolkit"` | `<chart:SfPyramidChart>` |

### XAML Migration Example

**Before:**
```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons"
             xmlns:calendar="clr-namespace:Syncfusion.Maui.Calendar;assembly=Syncfusion.Maui.Calendar">
    <VerticalStackLayout>
        <button:SfButton Text="Click Me" />
        <calendar:SfCalendar />
    </VerticalStackLayout>
</ContentPage>
```

**After:**
```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit"
             xmlns:calendar="clr-namespace:Syncfusion.Maui.Toolkit.Calendar;assembly=Syncfusion.Maui.Toolkit">
    <VerticalStackLayout>
        <button:SfButton Text="Click Me" />
        <calendar:SfCalendar />
    </VerticalStackLayout>
</ContentPage>
```

## C# Namespace Changes

Update C# `using` statements in code-behind files and view models.

| Component | Old C# Using | New C# Using |
|-----------|--------------|-------------|
| **SfAccordion** | `using Syncfusion.Maui.Accordion;` | `using Syncfusion.Maui.Toolkit.Accordion;` |
| **SfButton** | `using Syncfusion.Maui.Buttons;` | `using Syncfusion.Maui.Toolkit.Buttons;` |
| **SfCalendar** | `using Syncfusion.Maui.Calendar;` | `using Syncfusion.Maui.Toolkit.Calendar;` |
| **SfCards** | `using Syncfusion.Maui.Cards;` | `using Syncfusion.Maui.Toolkit.Cards;` |
| **SfCarousel** | `using Syncfusion.Maui.Carousel;` | `using Syncfusion.Maui.Toolkit.Carousel;` |
| **Chart Controls** | `using Syncfusion.Maui.Charts;` | `using Syncfusion.Maui.Toolkit.Charts;` |
| **SfCircularProgressBar** | `using Syncfusion.Maui.ProgressBar;` | `using Syncfusion.Maui.Toolkit.ProgressBar;` |
| **SfChip** | `using Syncfusion.Maui.Core;` | `using Syncfusion.Maui.Toolkit.Chips;` |
| **SfEffectsView** | `using Syncfusion.Maui.Core;` | `using Syncfusion.Maui.Toolkit.EffectsView;` |
| **SfExpander** | `using Syncfusion.Maui.Expander;` | `using Syncfusion.Maui.Toolkit.Expander;` |
| **SfLinearProgressBar** | `using Syncfusion.Maui.ProgressBar;` | `using Syncfusion.Maui.Toolkit.ProgressBar;` |
| **SfNavigationDrawer** | `using Syncfusion.Maui.NavigationDrawer;` | `using Syncfusion.Maui.Toolkit.NavigationDrawer;` |
| **SfNumericEntry** | `using Syncfusion.Maui.Inputs;` | `using Syncfusion.Maui.Toolkit.NumericEntry;` |
| **SfNumericUpDown** | `using Syncfusion.Maui.Inputs;` | `using Syncfusion.Maui.Toolkit.NumericUpDown;` |
| **SfPicker** | `using Syncfusion.Maui.Picker;` | `using Syncfusion.Maui.Toolkit.Picker;` |
| **SfPopup** | `using Syncfusion.Maui.Popup;` | `using Syncfusion.Maui.Toolkit.Popup;` |
| **SfPullToRefresh** | `using Syncfusion.Maui.PullToRefresh;` | `using Syncfusion.Maui.Toolkit.PullToRefresh;` |
| **SfSegmentedControl** | `using Syncfusion.Maui.Buttons;` | `using Syncfusion.Maui.Toolkit.SegmentedControl;` |
| **SfShimmer** | `using Syncfusion.Maui.Shimmer;` | `using Syncfusion.Maui.Toolkit.Shimmer;` |
| **SfSunburstChart** | `using Syncfusion.Maui.SunburstChart;` | `using Syncfusion.Maui.Toolkit.SunburstChart;` |
| **SfTabView** | `using Syncfusion.Maui.TabView;` | `using Syncfusion.Maui.Toolkit.TabView;` |
| **SfTextInputLayout** | `using Syncfusion.Maui.Core;` | `using Syncfusion.Maui.Toolkit.TextInputLayout;` |
| **Common (Hosting)** | `using Syncfusion.Maui.Core.Hosting;` | `using Syncfusion.Maui.Toolkit.Hosting;` |

### C# Migration Example

**Before:**
```csharp
using Syncfusion.Maui.Buttons;
using Syncfusion.Maui.Calendar;
using Syncfusion.Maui.Popup;

namespace MigrationApp;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void OnShowPopupClicked(object sender, EventArgs e)
    {
        var popup = new SfPopup();
        popup.Show();
    }

    private void OnDateSelected(object sender, EventArgs e)
    {
        var calendar = new SfCalendar();
    }
}
```

**After:**
```csharp
using Syncfusion.Maui.Toolkit.Buttons;
using Syncfusion.Maui.Toolkit.Calendar;
using Syncfusion.Maui.Toolkit.Popup;

namespace MigrationApp;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void OnShowPopupClicked(object sender, EventArgs e)
    {
        var popup = new SfPopup();
        popup.Show();
    }

    private void OnDateSelected(object sender, EventArgs e)
    {
        var calendar = new SfCalendar();
    }
}
```

## Assembly and Package Changes

### NuGet Package Migration

**Before:** Individual component packages

```xml
<!-- Individual packages in .csproj -->
<ItemGroup>
    <PackageReference Include="Syncfusion.Maui.Buttons" Version="23.1.x" />
    <PackageReference Include="Syncfusion.Maui.Calendar" Version="23.1.x" />
    <PackageReference Include="Syncfusion.Maui.Cards" Version="23.1.x" />
    <PackageReference Include="Syncfusion.Maui.Carousel" Version="23.1.x" />
    <PackageReference Include="Syncfusion.Maui.Charts" Version="23.1.x" />
    <!-- ...more individual packages... -->
</ItemGroup>
```

**After:** Single toolkit package

```xml
<!-- Single package in .csproj -->
<ItemGroup>
    <PackageReference Include="Syncfusion.Maui.Toolkit" Version="*" />
</ItemGroup>
```

### Assembly Changes in Code

No assembly binding redirects needed. The toolkit handles everything automatically.

## Search and Replace Patterns

Use these patterns in your IDE to bulk-update namespaces. Most IDEs support regular expressions for find-and-replace operations.

### Pattern 1: XAML Namespace Declarations

**Find (Regex):**
```
xmlns:(\w+)="clr-namespace:Syncfusion\.Maui\.(\w+);assembly=Syncfusion\.Maui\.\2"
```

**Replace:**
```
xmlns:$1="clr-namespace:Syncfusion.Maui.Toolkit.$2;assembly=Syncfusion.Maui.Toolkit"
```

**Note:** This works for most components. Some special cases (like Chip, EffectsView, Shimmer, TextInputLayout from Core) need manual replacement.

### Pattern 2: C# Using Statements (Buttons)

**Find:**
```
using Syncfusion.Maui.Buttons;
```

**Replace:**
```
using Syncfusion.Maui.Toolkit.Buttons;
```

### Pattern 3: C# Using Statements (General)

**Find (Regex):**
```
using Syncfusion\.Maui\.(\w+);
```

**Replace:**
```
using Syncfusion.Maui.Toolkit.$1;
```

**Caution:** This pattern matches "Core" namespace which needs special handling (see below).

### Pattern 4: Core Namespace Special Cases

These components migrate from `Syncfusion.Maui.Core` to specific toolkit namespaces:

**Find:** `using Syncfusion.Maui.Core;` (if used for Chip, EffectsView, Shimmer, or TextInputLayout)

**Manual Replacements:**
- For **Chip**: Replace with `using Syncfusion.Maui.Toolkit.Chips;`
- For **EffectsView**: Replace with `using Syncfusion.Maui.Toolkit.EffectsView;`
- For **Shimmer**: Replace with `using Syncfusion.Maui.Toolkit.Shimmer;`
- For **TextInputLayout**: Replace with `using Syncfusion.Maui.Toolkit.TextInputLayout;`

### Pattern 5: Core.Hosting Namespace

**Find:**
```
using Syncfusion.Maui.Core.Hosting;
```

**Replace:**
```
using Syncfusion.Maui.Toolkit.Hosting;
```

## Real-World Migration Examples

### Example 1: Multi-Component Page

**Before Migration:**
```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons"
             xmlns:popup="clr-namespace:Syncfusion.Maui.Popup;assembly=Syncfusion.Maui.Popup"
             xmlns:cards="clr-namespace:Syncfusion.Maui.Cards;assembly=Syncfusion.Maui.Cards"
             Title="Dashboard">
    <VerticalStackLayout Spacing="10">
        <button:SfButton Text="Show Popup" Clicked="OnShowPopupClicked" />
        <cards:SfCard>
            <Label Text="Card Content" />
        </cards:SfCard>
        <popup:SfPopup x:Name="MyPopup">
            <VerticalStackLayout Padding="10">
                <Label Text="Popup Content" />
            </VerticalStackLayout>
        </popup:SfPopup>
    </VerticalStackLayout>
</ContentPage>
```

**After Migration:**
```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit"
             xmlns:popup="clr-namespace:Syncfusion.Maui.Toolkit.Popup;assembly=Syncfusion.Maui.Toolkit"
             xmlns:cards="clr-namespace:Syncfusion.Maui.Toolkit.Cards;assembly=Syncfusion.Maui.Toolkit"
             Title="Dashboard">
    <VerticalStackLayout Spacing="10">
        <button:SfButton Text="Show Popup" Clicked="OnShowPopupClicked" />
        <cards:SfCard>
            <Label Text="Card Content" />
        </cards:SfCard>
        <popup:SfPopup x:Name="MyPopup">
            <VerticalStackLayout Padding="10">
                <Label Text="Popup Content" />
            </VerticalStackLayout>
        </popup:SfPopup>
    </VerticalStackLayout>
</ContentPage>
```

### Example 2: Code-Behind with Multiple Components

**Before Migration:**
```csharp
using Syncfusion.Maui.Buttons;
using Syncfusion.Maui.Calendar;
using Syncfusion.Maui.Inputs;
using Syncfusion.Maui.Picker;

namespace DashboardApp;

public partial class HomePage : ContentPage
{
    public HomePage()
    {
        InitializeComponent();
    }

    private void OnDateChanged(object sender, DateTime date)
    {
        var calendar = new SfCalendar { SelectedDate = date };
        var picker = new SfPicker();
        var numericEntry = new SfNumericEntry { Value = 100 };
    }

    private void OnSubmit(object sender, EventArgs e)
    {
        var button = new SfButton { Text = "Submitted" };
    }
}
```

**After Migration:**
```csharp
using Syncfusion.Maui.Toolkit.Buttons;
using Syncfusion.Maui.Toolkit.Calendar;
using Syncfusion.Maui.Toolkit.NumericEntry;
using Syncfusion.Maui.Toolkit.Picker;

namespace DashboardApp;

public partial class HomePage : ContentPage
{
    public HomePage()
    {
        InitializeComponent();
    }

    private void OnDateChanged(object sender, DateTime date)
    {
        var calendar = new SfCalendar { SelectedDate = date };
        var picker = new SfPicker();
        var numericEntry = new SfNumericEntry { Value = 100 };
    }

    private void OnSubmit(object sender, EventArgs e)
    {
        var button = new SfButton { Text = "Submitted" };
    }
}
```

## Troubleshooting Namespace Issues

### Issue 1: "Type does not exist in namespace"

**Problem:**
```
Error: The type 'SfButton' does not exist in the namespace 'clr-namespace:Syncfusion.Maui.Buttons'
```

**Solution:**
- Verify XAML namespace is updated to `Syncfusion.Maui.Toolkit.Buttons`
- Check assembly reference is `Syncfusion.Maui.Toolkit` (not individual package name)
- Ensure NuGet package `Syncfusion.Maui.Toolkit` is installed

### Issue 2: "Cannot find type using namespace"

**Problem:**
```
Error CS0246: The type or namespace name 'SfCalendar' could not be found
```

**Solution:**
- Confirm `using Syncfusion.Maui.Toolkit.Calendar;` is in your code-behind
- Check project builds without errors
- Rebuild solution to refresh IntelliSense

### Issue 3: Ambiguous Type Reference

**Problem:**
```
Error CS0104: 'SfButton' is an ambiguous reference between two namespaces
```

**Solution:**
- Remove any remaining old `using` statements pointing to `Syncfusion.Maui.Buttons`
- Keep only the new `using Syncfusion.Maui.Toolkit.Buttons;`
- Clean and rebuild solution

### Issue 4: Assembly Load Error at Runtime

**Problem:**
```
FileNotFoundException: Could not load file or assembly 'Syncfusion.Maui.Buttons'
```

**Solution:**
- Verify `.csproj` file contains only `<PackageReference Include="Syncfusion.Maui.Toolkit">`
- Remove any old individual package references
- Clear NuGet cache: `nuget locals all -clear`
- Restore packages: `dotnet restore`
- Rebuild solution

### Issue 5: XAML Designer Shows Errors

**Problem:**
```
XAML Designer: Type 'SfButton' was not found
```

**Solution:**
- Namespaces in XAML are correctly updated to toolkit versions
- Project builds successfully from command line
- Close and reopen the XAML file to refresh designer
- Restart Visual Studio if issue persists