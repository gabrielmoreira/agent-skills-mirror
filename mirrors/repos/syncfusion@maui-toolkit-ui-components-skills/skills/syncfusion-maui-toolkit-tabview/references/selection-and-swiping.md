# Selection, Events & Swiping

## Table of Contents
1. [Tab Selection Basics](#tab-selection-basics)
2. [Selection Events](#selection-events)
3. [Event Parameters](#event-parameters)
4. [Programmatic Tab Switching](#programmatic-tab-switching)
5. [Swipe Gestures](#swipe-gestures)
6. [Selection Indicators](#selection-indicators)
7. [Disabled Tabs](#disabled-tabs)
8. [Event Handling Patterns](#event-handling-patterns)

---

## Tab Selection Basics

### SelectedIndex Property

The `SelectedIndex` property determines which tab is currently visible. It's a zero-based integer.

**XAML Example:**
```xaml
<!-- Second tab selected by default -->
<tabView:SfTabView SelectedIndex="1">
    <tabView:SfTabItem Header="Tab 1" />
    <tabView:SfTabItem Header="Tab 2" />  <!-- This tab is selected -->
    <tabView:SfTabItem Header="Tab 3" />
</tabView:SfTabView>
```

**C# Example:**
```csharp
var tabView = new SfTabView { SelectedIndex = 1 };
```

### Default Selection

If no SelectedIndex is specified, the first tab (index 0) is selected by default.

---

## Selection Events

SfTabView provides three key events for monitoring tab selection:

### 1. TabItemTapped Event

Triggers when a user **taps** a tab header.

**XAML:**
```xaml
<tabView:SfTabView TabItemTapped="OnTabItemTapped">
    <!-- Tabs -->
</tabView:SfTabView>
```

**C# Event Handler:**
```csharp
private void OnTabItemTapped(object? sender, TabItemTappedEventArgs e)
{
    if (e.TabItem != null)
    {
        Debug.WriteLine($"Tab tapped: {e.TabItem.Header}");
        
        // You can modify the tab item here
        e.TabItem.FontSize = 26;
        
        // Or cancel the selection
        // e.Cancel = true;
    }
}
```

**Subscribe in Code:**
```csharp
tabView.TabItemTapped += OnTabItemTapped;
```

### 2. SelectionChanging Event

Triggers **before** tab selection changes (when tapping or programmatically setting SelectedIndex).

**XAML:**
```xaml
<tabView:SfTabView SelectionChanging="OnSelectionChanging">
    <!-- Tabs -->
</tabView:SfTabView>
```

**C# Event Handler:**
```csharp
private void OnSelectionChanging(object? sender, SelectionChangingEventArgs e)
{
    var newIndex = e.Index;
    Debug.WriteLine($"Selection changing to index: {newIndex}");
    
    // Validate before allowing selection
    if (newIndex == 2)  // Prevent selecting tab at index 2
    {
        e.Cancel = true;
        Debug.WriteLine("Selection cancelled!");
    }
}
```

**Key Property:**
- `e.Index`: The index of the tab about to be selected
- `e.Cancel`: Set to `true` to prevent the selection

### 3. SelectionChanged Event

Triggers **after** tab selection has changed.

**XAML:**
```xaml
<tabView:SfTabView SelectionChanged="OnSelectionChanged">
    <!-- Tabs -->
</tabView:SfTabView>
```

**C# Event Handler:**
```csharp
private void OnSelectionChanged(object? sender, TabSelectionChangedEventArgs e)
{
    var newIndex = e.NewIndex;
    var oldIndex = e.OldIndex;
    
    Debug.WriteLine($"Tab changed from {oldIndex} to {newIndex}");
    
    // Perform actions after selection
    LoadTabContent(newIndex);
    
    e.Handled = true;
}
```

**Key Properties:**
- `e.NewIndex`: The index of the newly selected tab
- `e.OldIndex`: The index of the previously selected tab
- `e.Handled`: Set to `true` to indicate event was handled

---

## Event Parameters

### TabItemTappedEventArgs

```csharp
public class TabItemTappedEventArgs
{
    // The tab item that was tapped
    public SfTabItem TabItem { get; }
    
    // Set to true to cancel the selection
    public bool Cancel { get; set; }
}
```

**Usage Example:**
```csharp
tabView.TabItemTapped += (sender, e) =>
{
    if (e.TabItem != null)
    {
        var headerText = e.TabItem.Header;
        Debug.WriteLine($"Tapped tab: {headerText}");
    }
};
```

### SelectionChangingEventArgs

```csharp
public class SelectionChangingEventArgs
{
    // Index of the tab about to be selected
    public int Index { get; }
    
    // Set to true to cancel the selection
    public bool Cancel { get; set; }
}
```

### TabSelectionChangedEventArgs

```csharp
public class TabSelectionChangedEventArgs
{
    // Index of the newly selected tab
    public int NewIndex { get; }
    
    // Index of the previously selected tab
    public int OldIndex { get; }
    
    // Set to true to mark the event as handled
    public bool Handled { get; set; }
}
```

---

## Programmatic Tab Switching

### Setting SelectedIndex

Change the visible tab programmatically:

```csharp
// Switch to tab at index 2
tabView.SelectedIndex = 2;

// Switch to first tab
tabView.SelectedIndex = 0;

// Switch to last tab
tabView.SelectedIndex = tabView.Items.Count - 1;
```

### Animating Tab Switches

When you programmatically change `SelectedIndex`, the selection events fire normally with animations enabled:

```csharp
// This triggers SelectionChanging → animation → SelectionChanged
tabView.SelectedIndex = 1;
```

### Conditional Tab Switching

```csharp
private void NavigateToTab(int tabIndex)
{
    // Validate index
    if (tabIndex >= 0 && tabIndex < tabView.Items.Count)
    {
        tabView.SelectedIndex = tabIndex;
    }
}

// Usage
NavigateToTab(1);  // Safe navigation to tab 1
```

---

## Swipe Gestures

### Enabling Swiping

Allow users to switch tabs by swiping left or right:

**XAML:**
```xaml
<tabView:SfTabView EnableSwiping="True">
    <!-- Tabs -->
</tabView:SfTabView>
```

**C#:**
```csharp
tabView.EnableSwiping = true;
```

### How Swiping Works

- **Swipe Left:** Moves to the next tab (increases SelectedIndex)
- **Swipe Right:** Moves to the previous tab (decreases SelectedIndex)
- **At Boundaries:** Swiping at the first/last tab has no effect

### Swiping with Animation

Swiping automatically triggers the same selection events and animations as programmatic changes:
1. User swipes
2. `SelectionChanging` event fires
3. Content transition animation plays
4. `SelectionChanged` event fires

### Important Limitation

When child controls support horizontal interactions (e.g., ScrollView, Carousel), gesture interference may occur:

```xaml
<!-- POTENTIAL CONFLICT: ScrollView horizontal swiping vs TabView swiping -->
<tabView:SfTabView EnableSwiping="True">
    <tabView:SfTabItem Header="Images">
        <tabView:SfTabItem.Content>
            <!-- This horizontal ScrollView may interfere with tab swiping -->
            <ScrollView Orientation="Horizontal">
                <!-- Content -->
            </ScrollView>
        </tabView:SfTabItem.Content>
    </tabView:SfTabItem>
</tabView:SfTabView>
```

**Solution:** Test thoroughly on target platforms and adjust gesture recognizers if needed.

---

## Selection Indicators

### Indicator Placement

Control where the selection indicator appears:

```xaml
<!-- Top (default) -->
<tabView:SfTabView IndicatorPlacement="Top">
    <!-- Tabs -->
</tabView:SfTabView>

<!-- Bottom -->
<tabView:SfTabView IndicatorPlacement="Bottom">
    <!-- Tabs -->
</tabView:SfTabView>

<!-- Fill -->
<tabView:SfTabView IndicatorPlacement="Fill">
    <!-- Tabs -->
</tabView:SfTabView>

```

### Indicator Color

```xaml
<tabView:SfTabView IndicatorBackground="#6200EE">
    <!-- Tabs -->
</tabView:SfTabView>
```

**C#:**
```csharp
tabView.IndicatorBackground = Color.FromArgb("#6200EE");
```

### Indicator Visibility

The indicator always shows on the currently selected tab and is hidden on unselected tabs. You cannot hide it completely.

---

## Disabled Tabs

### Making Tabs Disabled

While SfTabView doesn't have a built-in `IsEnabled` property, you can achieve disabled tab behavior by:

**1. Preventing Selection with Events:**
```csharp
private void OnSelectionChanging(object? sender, SelectionChangingEventArgs e)
{
    // Prevent selection of tab at index 2
    if (e.Index == 2)
    {
        e.Cancel = true;
    }
}
```

**2. Visual Feedback for Disabled Tabs:**
```csharp
// Make tab appear disabled visually
var disabledTab = new SfTabItem
{
    Header = "Locked",
    TextColor = Colors.Gray,
    FontAttributes = FontAttributes.Italic,
    Content = new StackLayout { /* ... */ }
};
```

**3. Complete Pattern:**
```csharp
private int[] disabledTabIndices = { 2, 4 };  // Disabled tab indices

private void OnSelectionChanging(object? sender, SelectionChangingEventArgs e)
{
    if (disabledTabIndices.Contains(e.Index))
    {
        e.Cancel = true;
        DisplayAlert("Disabled", "This tab is not available", "OK");
    }
}
```

---

## Event Handling Patterns

### Pattern 1: Lazy Loading Tab Content

Load content only when a tab becomes visible:

```csharp
private Dictionary<int, bool> loadedTabs = new();

private async void OnSelectionChanged(object? sender, TabSelectionChangedEventArgs e)
{
    int tabIndex = e.NewIndex;
    
    // Check if tab content is already loaded
    if (!loadedTabs.ContainsKey(tabIndex) || !loadedTabs[tabIndex])
    {
        // Load content asynchronously
        await LoadTabContentAsync(tabIndex);
        loadedTabs[tabIndex] = true;
    }
}

private async Task LoadTabContentAsync(int tabIndex)
{
    // Simulate loading data
    await Task.Delay(500);
    Debug.WriteLine($"Loaded content for tab {tabIndex}");
}
```

### Pattern 2: Tracking Selection Changes

Log and respond to all selection events:

```csharp
private void OnTabItemTapped(object? sender, TabItemTappedEventArgs e)
{
    Debug.WriteLine("→ TabItemTapped");
}

private void OnSelectionChanging(object? sender, SelectionChangingEventArgs e)
{
    Debug.WriteLine($"→ SelectionChanging: index {e.Index}");
}

private void OnSelectionChanged(object? sender, TabSelectionChangedEventArgs e)
{
    Debug.WriteLine($"→ SelectionChanged: {e.OldIndex} → {e.NewIndex}");
}

// Subscribe to all events
public void SubscribeToEvents()
{
    tabView.TabItemTapped += OnTabItemTapped;
    tabView.SelectionChanging += OnSelectionChanging;
    tabView.SelectionChanged += OnSelectionChanged;
}
```

### Pattern 3: Validation Before Tab Switch

```csharp
private bool hasUnsavedChanges = false;

private void OnSelectionChanging(object? sender, SelectionChangingEventArgs e)
{
    if (hasUnsavedChanges)
    {
        e.Cancel = true;
        ShowSaveConfirmation();
    }
}

private async void ShowSaveConfirmation()
{
    bool result = await DisplayAlert(
        "Unsaved Changes",
        "Save changes before switching tabs?",
        "Save",
        "Discard"
    );
    
    if (result)
    {
        // Save changes
        hasUnsavedChanges = false;
        // Then allow tab switch
    }
}
```

### Pattern 4: Analytics Tracking

```csharp
private void OnSelectionChanged(object? sender, TabSelectionChangedEventArgs e)
{
    var tabName = tabView.Items[e.NewIndex].Header;
    
    // Log to analytics
    Analytics.TrackEvent("tab_viewed", new Dictionary<string, string>
    {
        { "tab_name", tabName },
        { "previous_tab", tabView.Items[e.OldIndex].Header },
        { "timestamp", DateTime.Now.ToString() }
    });
}
```

---

## Event Interaction Flow

Understanding the complete event sequence helps in designing robust tab interactions:

**When User Taps a Tab:**
1. `TabItemTapped` fires (early notification)
2. `SelectionChanging` fires (can be cancelled here)
3. If not cancelled, animation plays
4. `SelectionChanged` fires (after animation completes)

**When Programmatically Setting SelectedIndex:**
1. `SelectionChanging` fires (can be cancelled)
2. If not cancelled, animation plays
3. `SelectionChanged` fires

**When User Swipes:**
1. Same flow as programmatic setting

Use this sequence to implement proper validations, side effects, and state management in your tab-based applications.

## Events API Reference

### Event Classes

#### 1. TabItemTappedEventArgs
Fired when a tab header is tapped by the user.

\\\csharp
public class TabItemTappedEventArgs : EventArgs
{
    public SfTabItem TabItem { get; set; }    // The tapped tab item
    public bool Cancel { get; set; }          // Set true to prevent selection change
}
\\\

#### 2. SelectionChangingEventArgs
Fired before tab selection changes (can be cancelled).

\\\csharp
public class SelectionChangingEventArgs : EventArgs
{
    public int Index { get; set; }            // Index of the tab being selected
    public bool Cancel { get; set; }          // Set true to cancel selection change
}
\\\

#### 3. TabSelectionChangedEventArgs
Fired after tab selection changes (after animation completes).

\\\csharp
public class TabSelectionChangedEventArgs : EventArgs
{
    public int NewIndex { get; set; }         // Index of newly selected tab
    public int OldIndex { get; set; }         // Index of previously selected tab
    public bool Handled { get; set; }         // Set true if handled
}
\\\

## SfTabView Selection Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| \SelectedIndex\ | \int\ | 0 | Index of currently selected tab (0-based) |
| \EnableSwiping\ | \ool\ | true | Enable swipe gestures for tab switching |

## Selection Indicator Visual Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| \IndicatorPlacement\ | \TabIndicatorPlacement\ | Bottom | Where indicator appears (Top, Bottom, Fill) |
| \IndicatorBackground\ | \Brush\ | Blue | Color of the selection indicator |
| \IndicatorWidthMode\ | \IndicatorWidthMode\ | Fit | Indicator width mode (Fit or Stretch) |
