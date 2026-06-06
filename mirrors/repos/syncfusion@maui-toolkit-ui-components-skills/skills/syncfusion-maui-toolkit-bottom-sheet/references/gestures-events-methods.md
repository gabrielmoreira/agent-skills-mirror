# Gestures, Events, and Methods in .NET MAUI Bottom Sheet

## Table of Contents
1. [Swipe Gestures](#swipe-gestures)
2. [State Changed Event](#state-changed-event)
3. [Overlay Tap Behavior](#overlay-tap-behavior)
4. [Programmatic Control Methods](#programmatic-control-methods)
5. [Interactive Patterns](#interactive-patterns)
6. [Event Handling Examples](#event-handling-examples)

---

## Swipe Gestures

The `EnableSwiping` property allows users to interact with the Bottom Sheet via swipe gestures.

### EnableSwiping Property

| Value | Behavior | User Can | Use Case |
|-------|----------|----------|----------|
| **True** (Default) | Swipe enabled | Swipe up/down to change states | Interactive sheets, dialogs |
| **False** | Swipe disabled | Cannot swipe (only buttons work) | Fixed position sheets, locked content |

### XAML: Enable/Disable Swiping

```xaml
<!-- XAML: Swiping enabled (default) -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" EnableSwiping="True">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Swipe up or down to change state"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- XAML: Swiping disabled -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" EnableSwiping="False">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Cannot swipe - use buttons only"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

### C#: Enable/Disable Swiping

```csharp
// C#: Enable swiping (users can swipe)
var sheet = new SfBottomSheet
{
    EnableSwiping = true
};

// C#: Disable swiping (programmatic control only)
var lockedSheet = new SfBottomSheet
{
    EnableSwiping = false
};
```

### Swipe Gestures with Different States

```csharp
public class SwipeGestureExample
{
    public SfBottomSheet CreateInteractiveSheet()
    {
        var sheet = new SfBottomSheet
        {
            State = BottomSheetState.Collapsed,
            HalfExpandedRatio = 0.35,
            FullExpandedRatio = 0.9,
            CollapsedHeight = 100,
            EnableSwiping = true  // Enable swipe gestures
        };
        
        sheet.StateChanged += (s, e) =>
        {
            Debug.WriteLine($"User swiped from {e.OldState} to {e.NewState}");
        };
        
        return sheet;
    }
}
```

### Gesture Behavior by State

```
When EnableSwiping = true:

Collapsed state:
  ↑ Swipe up → HalfExpanded
  (or directly to FullExpanded if HalfExpanded not allowed)

HalfExpanded state:
  ↑ Swipe up → FullExpanded
  ↓ Swipe down → Collapsed

FullExpanded state:
  ↓ Swipe down → HalfExpanded
  (or directly to Collapsed if HalfExpanded not allowed)
```

---

## State Changed Event

The `StateChanged` event fires whenever the sheet's state changes.

### StateChanged Event Details

**Event Type:** `EventHandler<StateChangedEventArgs>`

**EventArgs Properties:**
- `OldState`: Previous state (BottomSheetState)
- `NewState`: Current state (BottomSheetState)

### XAML: Subscribe to StateChanged

```xaml
<bottomSheet:SfBottomSheet x:Name="bottomSheet" StateChanged="OnStateChanged">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label x:Name="stateLabel" Text="State: Hidden"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

### C#: Subscribe to StateChanged Event

```csharp
// Subscribe to event
bottomSheet.StateChanged += OnStateChanged;

// Unsubscribe from event
bottomSheet.StateChanged -= OnStateChanged;

// Event handler
private void OnStateChanged(object sender, StateChangedEventArgs e)
{
    var oldState = e.OldState;
    var newState = e.NewState;
    
    Debug.WriteLine($"State changed from {oldState} to {newState}");
    
    stateLabel.Text = $"State: {newState}";
}
```

### StateChanged Event Trigger Causes

The StateChanged event fires when:
1. **User swipes** the sheet (if EnableSwiping = true)
2. **User taps overlay** (if CollapseOnOverlayTap = true and IsModal = true)
3. **State property set** programmatically in code
4. **Show/Close methods called** programmatically

### Complete StateChanged Example

```csharp
public partial class MainPage : ContentPage
{
    private int stateChangeCount = 0;
    private DateTime lastStateChange = DateTime.Now;

    public MainPage()
    {
        InitializeComponent();
        
        // Subscribe to state changes
        bottomSheet.StateChanged += OnBottomSheetStateChanged;
    }

    private void OnBottomSheetStateChanged(object sender, StateChangedEventArgs e)
    {
        stateChangeCount++;
        lastStateChange = DateTime.Now;

        // Log the change
        Debug.WriteLine($"[{stateChangeCount}] State: {e.OldState} → {e.NewState}");

        // Perform actions based on new state
        HandleStateChange(e.NewState);
    }

    private void HandleStateChange(BottomSheetState newState)
    {
        switch (newState)
        {
            case BottomSheetState.Hidden:
                Debug.WriteLine("Sheet hidden - cleanup resources");
                OnSheetHidden();
                break;
                
            case BottomSheetState.Collapsed:
                Debug.WriteLine("Sheet collapsed - show summary");
                OnSheetCollapsed();
                break;
                
            case BottomSheetState.HalfExpanded:
                Debug.WriteLine("Sheet half expanded - show details");
                OnSheetHalfExpanded();
                break;
                
            case BottomSheetState.FullExpanded:
                Debug.WriteLine("Sheet fully expanded - show complete content");
                OnSheetFullExpanded();
                break;
        }
    }

    private void OnSheetHidden()
    {
        // Called when sheet becomes hidden
    }

    private void OnSheetCollapsed()
    {
        // Called when sheet is collapsed
    }

    private void OnSheetHalfExpanded()
    {
        // Called when sheet is half expanded
    }

    private void OnSheetFullExpanded()
    {
        // Called when sheet is fully expanded
    }
}
```

---

## Overlay Tap Behavior

### CollapseOnOverlayTap Property

The `CollapseOnOverlayTap` property (used with `IsModal="True"`) enables closing the sheet when tapping the overlay.

| Setting | Behavior | Use Case |
|---------|----------|----------|
| **True** | Tapping overlay collapses sheet | User-friendly dialogs |
| **False** (Default) | Tapping overlay does nothing | Critical actions requiring explicit close |

### XAML: CollapseOnOverlayTap

```xaml
<!-- XAML: Overlay tap collapses sheet -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           IsModal="True"
                           CollapseOnOverlayTap="True">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Tap overlay to close"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- XAML: Overlay tap does nothing -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           IsModal="True"
                           CollapseOnOverlayTap="False">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Must use button to close"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

### C#: CollapseOnOverlayTap

```csharp
// C#: User-friendly overlay tap
var friendlyDialog = new SfBottomSheet
{
    IsModal = true,
    CollapseOnOverlayTap = true  // Tap overlay to close
};

// C#: Strict overlay (no close on tap)
var strictDialog = new SfBottomSheet
{
    IsModal = true,
    CollapseOnOverlayTap = false  // Must click button to close
};
```

### Overlay Tap Workflow

```
IsModal = true, CollapseOnOverlayTap = true:

User taps overlay
         ↓
StateChanged event fires (if state changes)
         ↓
Sheet collapses

---

IsModal = true, CollapseOnOverlayTap = false:

User taps overlay
         ↓
Nothing happens (no state change)
         ↓
Sheet remains in same state
```

---

## Programmatic Control Methods

### Show Method

Opens the Bottom Sheet programmatically:

```csharp
// C#: Open sheet with Show method
bottomSheet.Show();

// Equivalent to setting IsOpen = true
bottomSheet.IsOpen = true;
```

### Close Method

Closes the Bottom Sheet programmatically:

```csharp
// C#: Close sheet with Close method
bottomSheet.Close();

// Equivalent to setting IsOpen = false
bottomSheet.IsOpen = false;
```

### Show/Close Example

```csharp
public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void OnOpenClicked(object sender, EventArgs e)
    {
        // Open the sheet when button clicked
        bottomSheet.Show();
    }

    private void OnCloseClicked(object sender, EventArgs e)
    {
        // Close the sheet when button clicked
        bottomSheet.Close();
    }

    private void OnToggleClicked(object sender, EventArgs e)
    {
        // Toggle sheet open/closed
        if (bottomSheet.IsOpen)
        {
            bottomSheet.Close();
        }
        else
        {
            bottomSheet.Show();
        }
    }
}
```

### XAML: Buttons with Methods

```xaml
<Grid RowDefinitions="Auto, *" ColumnDefinitions="*">
    <!-- Control buttons -->
    <Grid ColumnDefinitions="*, *, *" ColumnSpacing="5" Padding="10">
        <Button Text="Open" Clicked="OnOpenClicked"/>
        <Button Text="Close" Grid.Column="1" Clicked="OnCloseClicked"/>
        <Button Text="Toggle" Grid.Column="2" Clicked="OnToggleClicked"/>
    </Grid>

    <!-- Bottom sheet -->
    <bottomSheet:SfBottomSheet x:Name="bottomSheet" Grid.Row="1">
        <bottomSheet:SfBottomSheet.BottomSheetContent>
            <VerticalStackLayout Padding="20" Spacing="10">
                <Label Text="Bottom Sheet Content" FontSize="18" FontAttributes="Bold"/>
                <Button Text="Close Sheet" Clicked="OnCloseClicked"/>
            </VerticalStackLayout>
        </bottomSheet:SfBottomSheet.BottomSheetContent>
    </bottomSheet:SfBottomSheet>
</Grid>
```

---

## Interactive Patterns

### Pattern 1: List Item Selection Opens Sheet

```csharp
public partial class ProductPage : ContentPage
{
    private ProductViewModel viewModel;

    public ProductPage()
    {
        InitializeComponent();
        viewModel = new ProductViewModel();
        this.BindingContext = viewModel;
    }

    private void OnProductTapped(object? sender, ItemTappedEventArgs e)
    {
        if (e.Item is Product product)
        {
            // Set the selected product
            viewModel.SelectedProduct = product;
            
            // Open the sheet
            productSheet.Show();
        }
    }
}
```

### Pattern 2: Sheet State Controls Content Display

```csharp
private void OnStateChanged(object sender, StateChangedEventArgs e)
{
    switch (e.NewState)
    {
        case BottomSheetState.Collapsed:
            // Show only summary
            summaryLabel.IsVisible = true;
            detailsLabel.IsVisible = false;
            actionButton.IsVisible = false;
            break;

        case BottomSheetState.HalfExpanded:
            // Show summary and basic details
            summaryLabel.IsVisible = true;
            detailsLabel.IsVisible = true;
            actionButton.IsVisible = false;
            break;

        case BottomSheetState.FullExpanded:
            // Show all content
            summaryLabel.IsVisible = true;
            detailsLabel.IsVisible = true;
            actionButton.IsVisible = true;
            break;

        case BottomSheetState.Hidden:
            // Reset visibility
            summaryLabel.IsVisible = false;
            detailsLabel.IsVisible = false;
            actionButton.IsVisible = false;
            break;
    }
}
```

### Pattern 3: Confirmation Dialog with Callbacks

```csharp
public class ConfirmationDialog
{
    private SfBottomSheet dialogSheet;
    private Action onConfirm;
    private Action onCancel;

    public void Show(string title, string message, Action confirmCallback, Action cancelCallback)
    {
        onConfirm = confirmCallback;
        onCancel = cancelCallback;

        // Create and show dialog
        dialogSheet = new SfBottomSheet
        {
            State = BottomSheetState.FullExpanded,
            IsModal = true,
            CollapseOnOverlayTap = false
        };

        var content = new VerticalStackLayout { Padding = new Thickness(20), Spacing = 15 };
        
        content.Children.Add(new Label 
        { 
            Text = title, 
            FontSize = 20, 
            FontAttributes = FontAttributes.Bold 
        });
        content.Children.Add(new Label 
        { 
            Text = message, 
            FontSize = 14,
            TextColor = Colors.Gray
        });

        var buttonGrid = new Grid {
            ColumnDefinitions =
            {
                new ColumnDefinition { Width = GridLength.Star },
                new ColumnDefinition { Width = GridLength.Star }
            },
            ColumnSpacing = 10 };
        
        var cancelBtn = new Button { Text = "Cancel" };
        cancelBtn.Clicked += (s, e) => OnCancel();
        
        var confirmBtn = new Button 
        { 
            Text = "Confirm", 
            BackgroundColor = Colors.Green,
        };
        Grid.SetColumn(confirmBtn, 1);
        confirmBtn.Clicked += (s, e) => OnConfirm();

        buttonGrid.Children.Add(cancelBtn);
        buttonGrid.Children.Add(confirmBtn);
        
        content.Children.Add(buttonGrid);
        dialogSheet.BottomSheetContent = content;
        
        dialogSheet.Show();
    }

    private void OnConfirm()
    {
        onConfirm?.Invoke();
        dialogSheet.Close();
    }

    private void OnCancel()
    {
        onCancel?.Invoke();
        dialogSheet.Close();
    }
}
```

---

## Event Handling Examples

### Example 1: Complete Event Logging

```csharp
public partial class MainPage : ContentPage
{
    private List<string> eventLog = new();

    public MainPage()
    {
        InitializeComponent();
        
        bottomSheet.StateChanged += (s, e) => LogEvent($"StateChanged: {e.OldState} → {e.NewState}");
    }

    private void LogEvent(string eventMessage)
    {
        eventLog.Add($"[{DateTime.Now:HH:mm:ss}] {eventMessage}");
        eventListView.ItemsSource = new List<string>(eventLog);
    }
}
```

### Example 2: State-Based Animation Trigger

```csharp
private async void OnStateChanged(object sender, StateChangedEventArgs e)
{
    if (e.NewState == BottomSheetState.FullExpanded)
    {
        // Animate content when fully expanded
        await contentGrid.FadeTo(1, 300);
    }
    else if (e.OldState == BottomSheetState.FullExpanded)
    {
        // Fade out when collapsing from full
        await contentGrid.FadeTo(0.5, 300);
    }
}
```

### Example 3: Validation Before Close

```csharp
private bool CanCloseSheet()
{
    // Validate form data
    if (string.IsNullOrWhiteSpace(nameEntry.Text))
    {
        DisplayAlert("Validation", "Please enter a name", "OK");
        return false;
    }

    if (string.IsNullOrWhiteSpace(emailEntry.Text))
    {
        DisplayAlert("Validation", "Please enter an email", "OK");
        return false;
    }

    return true;
}

private void OnCloseClicked(object sender, EventArgs e)
{
    if (CanCloseSheet())
    {
        bottomSheet.Close();
    }
}
```

---

## Best Practices

### ✅ DO:

```csharp
// ✅ Enable swiping for better UX
sheet.EnableSwiping = true;

// ✅ Subscribe to StateChanged for important state transitions
sheet.StateChanged += OnStateChanged;

// ✅ Use CollapseOnOverlayTap for user-friendly dialogs
sheet.CollapseOnOverlayTap = true;

// ✅ Handle state changes appropriately
if (e.NewState == BottomSheetState.FullExpanded)
{
    LoadDetailedContent();
}

// ✅ Provide visual feedback when showing sheet
sheet.Show();
```

### ❌ DON'T:

```csharp
// ❌ Don't disable swiping without good reason
sheet.EnableSwiping = false;  // Users expect to swipe

// ❌ Don't ignore state changes if they affect other UI
// Always subscribe to StateChanged if state affects content

// ❌ Don't make sheets impossible to close
sheet.IsModal = true;
sheet.CollapseOnOverlayTap = false;
// Add close button or users are trapped

// ❌ Don't perform heavy operations on every state change
// Validate expensive operations before executing

// ❌ Don't forget to unsubscribe from events
// bottomSheet.StateChanged -= OnStateChanged;  // When no longer needed
```

---
