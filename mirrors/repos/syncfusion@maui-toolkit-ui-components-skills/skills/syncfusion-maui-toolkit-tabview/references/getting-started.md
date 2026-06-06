# Getting Started with Syncfusion MAUI TabView

## Table of Contents
1. [Installation and Setup](#installation-and-setup)
2. [Creating Your First TabView](#creating-your-first-tabview)
3. [Adding Tabs and Content](#adding-tabs-and-content)
4. [Data Binding with ItemsSource](#data-binding-with-itemssource)
5. [Custom Templates](#custom-templates)
6. [Common Setup Issues](#common-setup-issues)
---

## Installation and Setup

### Step 1: Install NuGet Package

The SfTabView component is included in the **Syncfusion.Maui.Toolkit** NuGet package.

**Visual Studio Method:**
1. Right-click your project → **Manage NuGet Packages**
2. Search for `Syncfusion.Maui.Toolkit`
3. Install the latest version

**Command Line Method:**
```bash
dotnet add package Syncfusion.Maui.Toolkit
```

### Step 2: Register the Handler

In your `MauiProgram.cs` file, register the Syncfusion handler:

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

### Step 3: Add the Required Namespace

In your XAML files, add the TabView namespace declaration:

```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage 
    xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
    xmlns:tabView="clr-namespace:Syncfusion.Maui.Toolkit.TabView;assembly=Syncfusion.Maui.Toolkit"
    Title="My App">
    <!-- Your content here -->
</ContentPage>
```

In C# code-behind, add the using statement:

```csharp
using Syncfusion.Maui.Toolkit.TabView;
```

---

## Creating Your First TabView

### XAML Approach

The simplest way to create a TabView is using XAML:

```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage 
    xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
    xmlns:tabView="clr-namespace:Syncfusion.Maui.Toolkit.TabView;assembly=Syncfusion.Maui.Toolkit"
    Title="TabView Demo">
    <ContentPage.Content>
        <tabView:SfTabView>
            <tabView:SfTabView.Items>
                <tabView:SfTabItem Header="Tab 1">
                    <tabView:SfTabItem.Content>
                        <StackLayout Padding="10">
                            <Label Text="Tab 1 Content"/>
                        </StackLayout>
                    </tabView:SfTabItem.Content>
                </tabView:SfTabItem>
            </tabView:SfTabView.Items>
        </tabView:SfTabView>
    </ContentPage.Content>
</ContentPage>
```

### C# Approach

Create a TabView programmatically in code-behind:

```csharp
using Syncfusion.Maui.Toolkit.TabView;

namespace TabViewDemo
{
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();

            // Create the TabView
            var tabView = new SfTabView();

            // Create a tab item
            var tabItem = new SfTabItem
            {
                Header = "Tab 1",
                Content = new StackLayout
                {
                    Padding = 10,
                    Children =
                    {
                        new Label { Text = "Tab 1 Content" }
                    }
                }
            };

            // Add the tab to the TabView
            tabView.Items.Add(tabItem);

            // Set as page content
            this.Content = tabView;
        }
    }
}
```

---

## Adding Tabs and Content

### Static Tab Items

You can add multiple tabs directly in XAML:

```xaml
<tabView:SfTabView>
    <tabView:SfTabView.Items>
        <tabView:SfTabItem Header="Photos">
            <tabView:SfTabItem.Content>
                <Grid BackgroundColor="LightBlue">
                    <Label Text="Photos Gallery" VerticalTextAlignment="Center" HorizontalTextAlignment="Center"/>
                </Grid>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>

        <tabView:SfTabItem Header="Videos">
            <tabView:SfTabItem.Content>
                <Grid BackgroundColor="LightGreen">
                    <Label Text="Videos Library" VerticalTextAlignment="Center" HorizontalTextAlignment="Center"/>
                </Grid>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>

        <tabView:SfTabItem Header="Audio">
            <tabView:SfTabItem.Content>
                <Grid BackgroundColor="LightPink">
                    <Label Text="Audio Playlist" VerticalTextAlignment="Center" HorizontalTextAlignment="Center"/>
                </Grid>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>
    </tabView:SfTabView.Items>
</tabView:SfTabView>
```

### Programmatic Tab Addition (C#)

```csharp
var tabView = new SfTabView();

// Add multiple tabs
for (int i = 1; i <= 3; i++)
{
    var tab = new SfTabItem
    {
        Header = $"Tab {i}",
        Content = new StackLayout
        {
            Padding = 10,
            Children =
            {
                new Label { Text = $"Content for Tab {i}", FontSize = 16 }
            }
        }
    };
    tabView.Items.Add(tab);
}

this.Content = tabView;
```

---

## Data Binding with ItemsSource

### Creating a Model

First, create a model class to represent tab data:

```csharp
public class TabItemModel : INotifyPropertyChanged
{
    private string name;
    private string description;

    public string Name
    {
        get { return name; }
        set
        {
            if (name != value)
            {
                name = value;
                OnPropertyChanged(nameof(Name));
            }
        }
    }

    public string Description
    {
        get { return description; }
        set
        {
            if (description != value)
            {
                description = value;
                OnPropertyChanged(nameof(Description));
            }
        }
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

### Creating a ViewModel

Create a ViewModel that provides the data:

```csharp
using System.Collections.ObjectModel;

public class TabViewModel : INotifyPropertyChanged
{
    private ObservableCollection<TabItemModel> tabItems;

    public ObservableCollection<TabItemModel> TabItems
    {
        get { return tabItems; }
        set
        {
            if (tabItems != value)
            {
                tabItems = value;
                OnPropertyChanged(nameof(TabItems));
            }
        }
    }

    public TabViewModel()
    {
        TabItems = new ObservableCollection<TabItemModel>
        {
            new TabItemModel { Name = "John", Description = "Software Developer" },
            new TabItemModel { Name = "Jane", Description = "Product Manager" },
            new TabItemModel { Name = "Mike", Description = "Designer" },
            new TabItemModel { Name = "Sarah", Description = "Marketing Lead" }
        };
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

### Binding to TabView

```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage 
    xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
    xmlns:local="clr-namespace:TabViewDemo"
    xmlns:tabView="clr-namespace:Syncfusion.Maui.Toolkit.TabView;assembly=Syncfusion.Maui.Toolkit"
    Title="Data-Bound TabView">
    
    <ContentPage.BindingContext>
        <local:TabViewModel />
    </ContentPage.BindingContext>

    <ContentPage.Content>
        <tabView:SfTabView ItemsSource="{Binding TabItems}" />
    </ContentPage.Content>
</ContentPage>
```

---

## Custom Templates

### Using HeaderItemTemplate

Define how tab headers are displayed:

```xaml
<tabView:SfTabView ItemsSource="{Binding TabItems}">
    <tabView:SfTabView.HeaderItemTemplate>
        <DataTemplate>
            <StackLayout Padding="10" Spacing="0">
                <Label Text="{Binding Name}" FontSize="16" FontAttributes="Bold"/>
                <Label Text="{Binding Description}" FontSize="12" TextColor="Gray"/>
            </StackLayout>
        </DataTemplate>
    </tabView:SfTabView.HeaderItemTemplate>
</tabView:SfTabView>
```

### Using ContentItemTemplate

Define how tab content is displayed:

```xaml
<tabView:SfTabView ItemsSource="{Binding TabItems}">
    <tabView:SfTabView.HeaderItemTemplate>
        <DataTemplate>
            <Label Text="{Binding Name}" Padding="10"/>
        </DataTemplate>
    </tabView:SfTabView.HeaderItemTemplate>
    
    <tabView:SfTabView.ContentItemTemplate>
        <DataTemplate>
            <StackLayout Padding="15" Spacing="10">
                <Label Text="{Binding Name}" FontSize="18" FontAttributes="Bold"/>
                <Label Text="{Binding Description}" FontSize="14" TextColor="Gray"/>
                <Button Text="View Details" Margin="0,10,0,0"/>
            </StackLayout>
        </DataTemplate>
    </tabView:SfTabView.ContentItemTemplate>
</tabView:SfTabView>
```

### C# Template Creation

```csharp
var tabView = new SfTabView();

// Header template
tabView.HeaderItemTemplate = new DataTemplate(() =>
{
    var label = new Label { Padding = new Thickness(10) };
    label.SetBinding(Label.TextProperty, "Name");
    return label;
});

// Content template
tabView.ContentItemTemplate = new DataTemplate(() =>
{
    var stack = new StackLayout { Padding = 15 };
    var label = new Label();
    label.SetBinding(Label.TextProperty, "Description");
    stack.Children.Add(label);
    return stack;
});

tabView.ItemsSource = viewModel.TabItems;
this.Content = tabView;
```

---

## Common Setup Issues

### Issue 1: TabView Not Showing

**Problem:** TabView appears blank or doesn't render
**Solution:**
- Verify `ConfigureSyncfusionToolkit()` is called in `MauiProgram.cs`
- Ensure the namespace is correctly declared
- Check that at least one tab item is added

### Issue 2: Content Not Displaying

**Problem:** Tab content doesn't appear when tab is selected
**Solution:**
- Verify `Content` property is set on each `SfTabItem`
- Ensure the content view has appropriate layout (StackLayout, Grid, etc.)
- Check layout `Padding` and `Margin` settings

### Issue 3: Data Binding Not Working

**Problem:** ItemsSource or templates don't bind correctly
**Solution:**
- Verify `INotifyPropertyChanged` is implemented on model
- Check XAML binding syntax (use `Binding`, not direct property reference)
- Ensure BindingContext is set to the ViewModel
- Verify ObservableCollection is used for ItemsSource

### Issue 4: Tabs Not Visible in Header

**Problem:** Tab headers don't appear or are cut off
**Solution:**
- Adjust `TabWidthMode` property (use `SizeToContent` or `Distributed`)
- Increase header area size or enable scroll buttons
- Check `TabHeaderPadding` settings

---
