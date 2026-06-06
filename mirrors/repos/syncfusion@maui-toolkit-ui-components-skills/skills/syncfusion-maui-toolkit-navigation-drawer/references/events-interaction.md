# Events and Interaction Handling

## Table of Contents
1. [Event Lifecycle](#event-lifecycle)
2. [DrawerOpening Event](#draweropening-event)
3. [DrawerOpened Event](#draweropened-event)
4. [DrawerClosing Event](#drawerclosing-event)
5. [DrawerClosed Event](#drawerclosed-event)
6. [DrawerToggled Event](#drawertoggled-event)
7. [Event Patterns](#event-patterns)
8. [Common Workflows](#common-workflows)

---

## Event Lifecycle

The drawer fires events in a specific sequence as it opens and closes:

```
User Action (tap hamburger / swipe)
    ↓
DrawerOpening (cancelable)
    ↓
Animation plays...
    ↓
DrawerOpened
    ↓
Drawer is open and interactive
    ↓
User closes drawer
    ↓
DrawerClosing (cancelable)
    ↓
Animation plays...
    ↓
DrawerClosed
    ↓
DrawerToggled (fires after Opened or Closed)
```

---

## DrawerOpening Event

**Fires:** Before the drawer starts to open  
**Cancelable:** Yes  
**Usage:** Validate conditions before allowing drawer to open

### Basic Implementation

**XAML:**
```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer" 
                                     DrawerOpening="OnDrawerOpening"/>
```

**C#:**
```csharp
navigationDrawer.DrawerOpening += OnDrawerOpening;

private void OnDrawerOpening(object sender, CancelEventArgs e)
{
    Debug.WriteLine("Drawer is about to open");
    
    // Example: Prevent opening if user not authenticated
    if (!isUserAuthenticated)
    {
        e.Cancel = true;
        DisplayAlert("Access Denied", "Please log in first", "OK");
    }
}
```

### Conditional Opening

```csharp
private void OnDrawerOpening(object sender, CancelEventArgs e)
{
    // Only allow opening on certain pages
    if (CurrentPage == "SettingsPage")
    {
        e.Cancel = true;
        DisplayAlert("Not Allowed", "Drawer disabled on this page", "OK");
        return;
    }
    
    // Prevent opening if a dialog is already open
    if (isDialogOpen)
    {
        e.Cancel = true;
    }
}
```

---

## DrawerOpened Event

**Fires:** After the drawer has fully opened  
**Cancelable:** No  
**Usage:** Execute actions after drawer is visible

### Basic Implementation

**XAML:**
```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer" 
                                     DrawerOpened="OnDrawerOpened"/>
```

**C#:**
```csharp
navigationDrawer.DrawerOpened += OnDrawerOpened;

private void OnDrawerOpened(object sender, EventArgs e)
{
    Debug.WriteLine("Drawer opened successfully");
    
    // Focus first menu item for accessibility
    firstMenuItem?.Focus();
    
    // Load additional content
    LoadDrawerContent();
    
    // Trigger animations
    AnimateDrawerContent();
}
```

### Real-World Example

```csharp
private void OnDrawerOpened(object sender, EventArgs e)
{
    // Refresh user profile data
    Task.Run(async () =>
    {
        var userData = await LoadUserData();
        MainThread.BeginInvokeOnMainThread(() =>
        {
            UpdateUserUI(userData);
        });
    });
    
    // Highlight current page in menu
    HighlightCurrentPageInMenu();
    
    // Notify analytics
    Analytics.TrackEvent("drawer_opened");
}
```

---

## DrawerClosing Event

**Fires:** Before the drawer starts to close  
**Cancelable:** Yes  
**Usage:** Save changes or prevent closing when needed

### Basic Implementation

**XAML:**
```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer" 
                                     DrawerClosing="OnDrawerClosing"/>
```

**C#:**
```csharp
navigationDrawer.DrawerClosing += OnDrawerClosing;

private void OnDrawerClosing(object sender, CancelEventArgs e)
{
    Debug.WriteLine("Drawer is about to close");
    
    // Example: Save unsaved changes before closing
    if (HasUnsavedChanges())
    {
        e.Cancel = true;
        DisplayAlert("Unsaved Changes", "Save before closing?", "OK");
    }
}
```

### Validation Before Closing

```csharp
private void OnDrawerClosing(object sender, CancelEventArgs e)
{
    // Validate form input
    if (!IsFormValid())
    {
        e.Cancel = true;
        DisplayAlert("Invalid Input", "Please correct the form", "OK");
        return;
    }
    
    // Don't close if a long operation is in progress
    if (IsOperationInProgress)
    {
        e.Cancel = true;
        DisplayAlert("Wait", "Operation in progress", "OK");
    }
}
```

---

## DrawerClosed Event

**Fires:** After the drawer has fully closed  
**Cancelable:** No  
**Usage:** Clean up or restore focus to main content

### Basic Implementation

**XAML:**
```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer" 
                                     DrawerClosed="OnDrawerClosed"/>
```

**C#:**
```csharp
navigationDrawer.DrawerClosed += OnDrawerClosed;

private void OnDrawerClosed(object sender, EventArgs e)
{
    Debug.WriteLine("Drawer closed successfully");
    
    // Restore focus to main content
    mainContentArea?.Focus();
    
    // Clean up temporary state
    ClearDrawerSelection();
    
    // Stop background operations
    StopBackgroundSync();
}
```

### Cleanup After Closing

```csharp
private void OnDrawerClosed(object sender, EventArgs e)
{
    // Deselect any highlighted items
    MenuListView.SelectedItem = null;
    
    // Clear temporary filters
    ClearTemporaryFilters();
    
    // Release resources
    ReleaseDrawerImages();
    
    // Update main content
    RefreshMainContent();
    
    // Log analytics
    Analytics.TrackEvent("drawer_closed");
}
```

---

## DrawerToggled Event

**Fires:** After drawer opens or closes (fires once per action)  
**Cancelable:** No  
**Usage:** React to final state after drawer state changes

### Basic Implementation

**XAML:**
```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer" 
                                     DrawerToggled="OnDrawerToggled"/>
```

**C#:**
```csharp
navigationDrawer.DrawerToggled += OnDrawerToggled;

private void OnDrawerToggled(object sender, ToggledEventArgs e)
{
    if (e.IsOpen)
    {
        Debug.WriteLine("Drawer is now open");
        // Handle open state
    }
    else
    {
        Debug.WriteLine("Drawer is now closed");
        // Handle closed state
    }
}
```

### State-Based Logic

```csharp
private void OnDrawerToggled(object sender, ToggledEventArgs e)
{
    // Update UI based on drawer state
    drawerStatusLabel.Text = e.IsOpen ? "Drawer: Open" : "Drawer: Closed";
    
    // Update background dimming
    backgroundDim.IsVisible = e.IsOpen;
    backgroundDim.Opacity = e.IsOpen ? 0.5 : 0;
    
    // Toggle button appearance
    hamburgerButton.BackgroundColor = e.IsOpen 
        ? Color.FromArgb("#E0E0E0") 
        : Color.FromArgb("#FFFFFF");
}
```

---

## Event Patterns

### Pattern 1: Complete Event Handler Setup

```csharp
public partial class MainPage : ContentPage
{
    private SfNavigationDrawer navigationDrawer;

    public MainPage()
    {
        InitializeComponent();
        
        navigationDrawer = this.FindByName<SfNavigationDrawer>("navigationDrawer");
        
        // Subscribe to all events
        navigationDrawer.DrawerOpening += OnDrawerOpening;
        navigationDrawer.DrawerOpened += OnDrawerOpened;
        navigationDrawer.DrawerClosing += OnDrawerClosing;
        navigationDrawer.DrawerClosed += OnDrawerClosed;
        navigationDrawer.DrawerToggled += OnDrawerToggled;
    }

    private void OnDrawerOpening(object sender, CancelEventArgs e)
    {
        if (!CanOpenDrawer())
            e.Cancel = true;
    }

    private void OnDrawerOpened(object sender, EventArgs e)
    {
        Debug.WriteLine("Drawer opened");
    }

    private void OnDrawerClosing(object sender, CancelEventArgs e)
    {
        if (!CanCloseDrawer())
            e.Cancel = true;
    }

    private void OnDrawerClosed(object sender, EventArgs e)
    {
        Debug.WriteLine("Drawer closed");
    }

    private void OnDrawerToggled(object sender, ToggledEventArgs e)
    {
        Debug.WriteLine($"Drawer is {(e.IsOpen ? "open" : "closed")}");
    }

    private bool CanOpenDrawer() => !isProcessing;
    private bool CanCloseDrawer() => !hasUnsavedData;
}
```

### Pattern 2: Async Event Handling

```csharp
private async void OnDrawerOpened(object sender, EventArgs e)
{
    try
    {
        // Load content asynchronously
        var data = await LoadDrawerData();
        
        MainThread.BeginInvokeOnMainThread(() =>
        {
            UpdateDrawerUI(data);
        });
    }
    catch (Exception ex)
    {
        await DisplayAlert("Error", $"Failed to load: {ex.Message}", "OK");
    }
}
```

### Pattern 3: Error Handling

```csharp
private void OnDrawerOpening(object sender, CancelEventArgs e)
{
    try
    {
        // Perform validation
        ValidateDrawerPrerequisites();
    }
    catch (InvalidOperationException ex)
    {
        e.Cancel = true;
        DisplayAlert("Cannot Open", ex.Message, "OK");
    }
    catch (Exception ex)
    {
        Debug.WriteLine($"Drawer opening error: {ex}");
    }
}
```

---

## Common Workflows

### Workflow 1: Navigation on Menu Selection

```csharp
private void OnMenuItemSelected(object sender, SelectedItemChangedEventArgs e)
{
    if (e.SelectedItem == null)
        return;

    var selectedMenu = e.SelectedItem as MenuItemModel;
    
    // Navigate to the selected page
    NavigateToPage(selectedMenu.PageType);
    
    // Close the drawer
    navigationDrawer.ToggleDrawer();
}

private void OnDrawerClosed(object sender, EventArgs e)
{
    // Deselect menu item after closing
    menuListView.SelectedItem = null;
}
```

### Workflow 2: Dynamic Menu Updates

```csharp
private void OnDrawerOpening(object sender, CancelEventArgs e)
{
    // Refresh menu items when drawer opens
    Task.Run(async () =>
    {
        var menuItems = await FetchLatestMenuItems();
        
        MainThread.BeginInvokeOnMainThread(() =>
        {
            menuListView.ItemsSource = menuItems;
        });
    });
}
```

### Workflow 3: Prevent Accidental Closure

```csharp
private bool isEditingForm = false;

private void OnFormEditing()
{
    isEditingForm = true;
}

private void OnDrawerClosing(object sender, CancelEventArgs e)
{
    if (isEditingForm)
    {
        e.Cancel = true;
        
        DisplayAlert("Unsaved Changes", 
            "Save changes before closing?", 
            "Yes", "No").ContinueWith(result =>
        {
            if (result.Result)
            {
                SaveForm();
                navigationDrawer.ToggleDrawer();
            }
        });
    }
}
```

### Workflow 4: Analytics Tracking

```csharp
private void OnDrawerToggled(object sender, ToggledEventArgs e)
{
    var eventName = e.IsOpen ? "drawer_open" : "drawer_close";
    var properties = new Dictionary<string, string>
    {
        { "timestamp", DateTime.UtcNow.ToString() },
        { "page", CurrentPageName },
        { "user_id", UserId }
    };
    
    Analytics.TrackEvent(eventName, properties);
}
```

---

## Best Practices

✅ **Do:**
- Use `DrawerOpening` and `DrawerClosing` to validate state
- Always set `e.Cancel = true` with explanation to user
- Use `DrawerToggled` for UI state synchronization
- Handle events asynchronously when loading data
- Clean up resources in `DrawerClosed`

❌ **Don't:**
- Throw exceptions in event handlers (handle gracefully)
- Perform long-running operations without async/await
- Cancel drawer opening/closing without user feedback
- Leave menu items selected after drawer closes
- Subscribe to events multiple times without unsubscribing

