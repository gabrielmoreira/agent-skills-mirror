# Advanced Features

## Table of Contents
1. [Nested TabView](#nested-tabview)
2. [Header Placement Options](#header-placement-options)
3. [Visual State Managers](#visual-state-managers)
4. [Overflow and Scrolling](#overflow-and-scrolling)
5. [Performance Optimization](#performance-optimization)
6. [Advanced Event Handling](#advanced-event-handling)

---

## Nested TabView

### Creating Nested Tab Structure

SfTabView supports nesting multiple levels of tabs, allowing hierarchical navigation structures.

**Basic Nested Tabs:**
```xaml
<tabView:SfTabView x:Name="mainTabView" TabBarPlacement="Top">
    <tabView:SfTabView.Items>
        <!-- Main tab: Photos -->
        <tabView:SfTabItem Header="Photos">
            <tabView:SfTabItem.Content>
                <Grid BackgroundColor="LightBlue">
                    <!-- Nested TabView inside -->
                    <tabView:SfTabView x:Name="nestedTabView" 
                                      TabBarPlacement="Bottom"
                                      IndicatorBackground="#6200EE">
                        <tabView:SfTabView.Items>
                            <tabView:SfTabItem Header="Camera">
                                <tabView:SfTabItem.Content>
                                    <StackLayout Padding="10">
                                        <Label Text="Camera Photos"/>
                                    </StackLayout>
                                </tabView:SfTabItem.Content>
                            </tabView:SfTabItem>
                            
                            <tabView:SfTabItem Header="Video">
                                <tabView:SfTabItem.Content>
                                    <StackLayout Padding="10">
                                        <Label Text="Video Files"/>
                                    </StackLayout>
                                </tabView:SfTabItem.Content>
                            </tabView:SfTabItem>
                            
                            <tabView:SfTabItem Header="Screenshots">
                                <tabView:SfTabItem.Content>
                                    <StackLayout Padding="10">
                                        <Label Text="Screenshots"/>
                                    </StackLayout>
                                </tabView:SfTabItem.Content>
                            </tabView:SfTabItem>
                        </tabView:SfTabView.Items>
                    </tabView:SfTabView>
                </Grid>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>
        
        <!-- Main tab: Collections -->
        <tabView:SfTabItem Header="Collections">
            <tabView:SfTabItem.Content>
                <Grid BackgroundColor="LightGreen">
                    <Label Text="Collections Content"/>
                </Grid>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>
        
        <!-- Main tab: Explore -->
        <tabView:SfTabItem Header="Explore">
            <tabView:SfTabItem.Content>
                <Grid BackgroundColor="LightPink">
                    <Label Text="Explore Content"/>
                </Grid>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>
    </tabView:SfTabView.Items>
</tabView:SfTabView>
```

### Event Handling with Nested Tabs

Each nested TabView has its own events:

```csharp
public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        
        // Main TabView events
        mainTabView.SelectionChanged += MainTabView_SelectionChanged;
        
        // Nested TabView events
        nestedTabView.SelectionChanged += NestedTabView_SelectionChanged;
    }
    
    private void MainTabView_SelectionChanged(object? sender, TabSelectionChangedEventArgs e)
    {
        Debug.WriteLine($"Main tab changed to index: {e.NewIndex}");
    }
    
    private void NestedTabView_SelectionChanged(object? sender, TabSelectionChangedEventArgs e)
    {
        Debug.WriteLine($"Nested tab changed to index: {e.NewIndex}");
    }
}
```

### Best Practices for Nested Tabs

✅ **Do:**
- Keep nesting to 2-3 levels maximum
- Use different `TabBarPlacement` for visual distinction
- Preserve state when navigating between nested tabs
- Use unique names for event handling clarity

❌ **Avoid:**
- Deep nesting (>3 levels) - confuses navigation
- Same tab placement for nested levels
- Loading heavy content in nested tabs without lazy loading
- Identical styling - make hierarchy visually clear

### Practical Example: Multi-Level Navigation

```csharp
public class NestedTabViewModel : INotifyPropertyChanged
{
    private ObservableCollection<CategoryModel> categories;

    public ObservableCollection<CategoryModel> Categories
    {
        get { return categories; }
        set
        {
            if (categories != value)
            {
                categories = value;
                OnPropertyChanged(nameof(Categories));
            }
        }
    }

    public NestedTabViewModel()
    {
        Categories = new ObservableCollection<CategoryModel>
        {
            new CategoryModel 
            { 
                Name = "Sports",
                Items = new ObservableCollection<ItemModel>
                {
                    new ItemModel { Title = "Football", Description = "Latest football news" },
                    new ItemModel { Title = "Basketball", Description = "Latest basketball news" }
                }
            },
            new CategoryModel 
            { 
                Name = "Technology",
                Items = new ObservableCollection<ItemModel>
                {
                    new ItemModel { Title = "AI", Description = "Latest AI developments" },
                    new ItemModel { Title = "Mobile", Description = "Latest mobile tech" }
                }
            }
        };
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}

public class CategoryModel
{
    public string Name { get; set; }
    public ObservableCollection<ItemModel> Items { get; set; }
}

public class ItemModel
{
    public string Title { get; set; }
    public string Description { get; set; }
}
```

---

## Header Placement Options

### Four Placement Positions

Control where the tab bar appears relative to content:

**Top (Default):**
```xaml
<tabView:SfTabView TabBarPlacement="Top">
    <!-- Tabs display at top, content below -->
</tabView:SfTabView>
```

**Bottom:**
```xaml
<tabView:SfTabView TabBarPlacement="Bottom">
    <!-- Content displays above tabs -->
</tabView:SfTabView>
```

### Indicator Placement Sync

Ensure indicator placement complements header placement:

```xaml
<!-- Top tabs with top indicator -->
<tabView:SfTabView TabBarPlacement="Top" IndicatorPlacement="Top">
    <!-- Tabs -->
</tabView:SfTabView>

<!-- Bottom tabs with bottom indicator -->
<tabView:SfTabView TabBarPlacement="Bottom" IndicatorPlacement="Bottom">
    <!-- Tabs -->
</tabView:SfTabView>
```

---

## Visual State Managers

### MVVM-Based State Management

Use the Visual State Manager pattern for responsive tab styling based on state:

```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage 
    xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
    xmlns:tabView="clr-namespace:Syncfusion.Maui.Toolkit.TabView;assembly=Syncfusion.Maui.Toolkit">
    
     <VisualStateManager.VisualStateGroups>
        <VisualStateGroup x:Name="Selected">
            <!-- State when specific tab is selected -->
            <VisualState x:Name="SelectedTabState">
                <VisualState.Setters>
                    <Setter Property="tabView:SfTabView.IndicatorBackground" Value="#6200EE"/>
                </VisualState.Setters>
            </VisualState>

            <VisualState x:Name="Normal">
                <VisualState.Setters>
                    <Setter Property="tabView:SfTabView.IndicatorBackground" Value="Gray"/>
                </VisualState.Setters>
            </VisualState>
        </VisualStateGroup>
    </VisualStateManager.VisualStateGroups>
    
    <ContentPage.Content>
        <tabView:SfTabView x:Name="tabView">
            <!-- Tabs -->
        </tabView:SfTabView>
    </ContentPage.Content>
</ContentPage>
```

### Data Binding with View Models

```csharp
public class TabStateViewModel : INotifyPropertyChanged
{
    private int selectedTabIndex;
    private Color indicatorColor;

    public int SelectedTabIndex
    {
        get { return selectedTabIndex; }
        set
        {
            if (selectedTabIndex != value)
            {
                selectedTabIndex = value;
                OnPropertyChanged(nameof(SelectedTabIndex));
                UpdateIndicatorColor();
            }
        }
    }

    public Color IndicatorColor
    {
        get { return indicatorColor; }
        set
        {
            if (indicatorColor != value)
            {
                indicatorColor = value;
                OnPropertyChanged(nameof(IndicatorColor));
            }
        }
    }

    private void UpdateIndicatorColor()
    {
        // Change color based on selected tab
        IndicatorColor = SelectedTabIndex switch
        {
            0 => Colors.Red,
            1 => Colors.Green,
            2 => Colors.Blue,
            _ => Colors.Gray
        };
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

---

## Overflow and Scrolling

### Handling Many Tabs

When you have more tabs than available space:

**Enable Scroll Buttons:**
```xaml
<tabView:SfTabView IsScrollButtonEnabled="True">
    <tabView:SfTabItem Header="Tab 1" />
    <tabView:SfTabItem Header="Tab 2" />
    <tabView:SfTabItem Header="Tab 3" />
    <tabView:SfTabItem Header="Tab 4" />
    <tabView:SfTabItem Header="Tab 5" />
    <tabView:SfTabItem Header="Tab 6" />
    <tabView:SfTabItem Header="Tab 7" />
</tabView:SfTabView>
```

**Using SizeToContent Mode:**
```xaml
<tabView:SfTabView TabWidthMode="SizeToContent" IsScrollButtonEnabled="True">
    <!-- Many tabs -->
</tabView:SfTabView>
```

### Dynamic Tab Loading

```csharp
public async Task LoadMoreTabs()
{
    // Load tabs dynamically
    for (int i = 0; i < 10; i++)
    {
        var newTab = new SfTabItem
        {
            Header = $"Tab {tabView.Items.Count + 1}",
            Content = new StackLayout
            {
                Padding = 10,
                Children = { new Label { Text = $"Content {i}" } }
            }
        };
        
        tabView.Items.Add(newTab);
        await Task.Delay(100);  // Stagger loading
    }
}
```

---

## Performance Optimization

### 1. Lazy Loading Content

Don't load tab content until the tab becomes visible:

```csharp
private Dictionary<int, bool> isContentLoaded = new();

private async void OnSelectionChanged(object? sender, TabSelectionChangedEventArgs e)
{
    int tabIndex = e.NewIndex;
    
    if (!isContentLoaded.ContainsKey(tabIndex))
    {
        await LoadTabContentAsync(tabIndex);
    }
}

private async Task LoadTabContentAsync(int tabIndex)
{
    var tabItem = tabView.Items[tabIndex];
    
    // Replace placeholder with actual content
    var loadingLabel = new Label { Text = "Loading..." };
    tabItem.Content = loadingLabel;
    
    // Simulate loading
    await Task.Delay(1000);
    
    // Update with real content
    var realContent = new StackLayout
    {
        Padding = 10,
        Children = { new Label { Text = $"Loaded tab {tabIndex}" } }
    };
    
    tabItem.Content = realContent;
    isContentLoaded[tabIndex] = true;
}
```

### 2. Virtual Tab Lists

For very large numbers of tabs, consider pagination:

```csharp
public class VirtualTabManager
{
    private List<TabItemModel> allTabs;
    private int itemsPerPage = 10;
    private int currentPage = 0;

    public void LoadPage(int pageNumber)
    {
        currentPage = pageNumber;
        int startIndex = currentPage * itemsPerPage;
        int endIndex = Math.Min(startIndex + itemsPerPage, allTabs.Count);
        
        var visibleTabs = allTabs.GetRange(startIndex, endIndex - startIndex);
        UpdateTabView(visibleTabs);
    }

    private void UpdateTabView(List<TabItemModel> tabs)
    {
        // Clear current tabs and load new batch
        tabView.Items.Clear();
        foreach (var tab in tabs)
        {
            tabView.Items.Add(CreateTabItem(tab));
        }
    }

    private SfTabItem CreateTabItem(TabItemModel model)
    {
        // Create tab item from model
        return new SfTabItem { Header = model.Name };
    }
}
```

### 3. Resource Management

```csharp
// Reuse expensive layouts
private StackLayout templateLayout;

private void CacheLayout()
{
    templateLayout = new StackLayout
    {
        Padding = 10,
        Spacing = 5,
        Children = { new Label(), new Entry() }
    };
}

private SfTabItem CreateTabFromTemplate()
{
    var tab = new SfTabItem
    {
        Header = "New Tab",
        Content = templateLayout
    };
    return tab;
}
```

---

## Advanced Event Handling

### Multi-Event Coordination

```csharp
private class TabEventCoordinator
{
    private SfTabView tabView;
    private bool isAnimating = false;

    public TabEventCoordinator(SfTabView tabView)
    {
        this.tabView = tabView;
        
        tabView.TabItemTapped += OnTabItemTapped;
        tabView.SelectionChanging += OnSelectionChanging;
        tabView.SelectionChanged += OnSelectionChanged;
    }

    private void OnTabItemTapped(object? sender, TabItemTappedEventArgs e)
    {
        Debug.WriteLine($"[1] TabItemTapped: {e.TabItem?.Header}");
        isAnimating = true;
    }

    private void OnSelectionChanging(object? sender, SelectionChangingEventArgs e)
    {
        Debug.WriteLine($"[2] SelectionChanging: index {e.Index}");
    }

    private void OnSelectionChanged(object? sender, TabSelectionChangedEventArgs e)
    {
        Debug.WriteLine($"[3] SelectionChanged: {e.OldIndex} → {e.NewIndex}");
        isAnimating = false;
        
        // Perform post-animation actions
        OnTabAnimationComplete(e.NewIndex);
    }

    private void OnTabAnimationComplete(int tabIndex)
    {
        Debug.WriteLine($"[4] Tab animation complete for index: {tabIndex}");
    }
}
```

### Custom Event Bus

```csharp
public interface ITabEventBus
{
    void PublishTabSelected(int tabIndex);
    void SubscribeToTabEvents(Action<int> onTabSelected);
}

public class TabEventBus : ITabEventBus
{
    private List<Action<int>> subscribers = new();

    public void PublishTabSelected(int tabIndex)
    {
        foreach (var subscriber in subscribers)
        {
            subscriber?.Invoke(tabIndex);
        }
    }

    public void SubscribeToTabEvents(Action<int> onTabSelected)
    {
        subscribers.Add(onTabSelected);
    }
}

// Usage
var eventBus = new TabEventBus();
tabView.SelectionChanged += (sender, e) => eventBus.PublishTabSelected(e.NewIndex);

eventBus.SubscribeToTabEvents(tabIndex =>
{
    Debug.WriteLine($"Tab {tabIndex} selected from event bus");
});
```
