# States Management in .NET MAUI Bottom Sheet

## Table of Contents
1. [State Property Overview](#state-property-overview)
2. [AllowedState Configuration](#allowedstate-configuration)
3. [IsOpen Property](#isopen-property)
4. [State Transitions](#state-transitions)
5. [Practical Scenarios](#practical-scenarios)

---

## State Property Overview

The `State` property controls the current position and visibility of the Bottom Sheet. There are four possible states:

### State Values

| State | Description | Height | Visibility | Use Case |
|-------|-------------|--------|------------|----------|
| **Hidden** | Sheet is not visible | 0 | Not visible | Initial state, closed sheet |
| **Collapsed** | Sheet appears at bottom with custom height | CollapsedHeight | Partially visible | Peek preview (e.g., 100px bar) |
| **HalfExpanded** | Sheet takes up specified ratio of screen | HalfExpandedRatio × screen height | Large preview | Preview details (e.g., 35% of screen) |
| **FullExpanded** | Sheet fills most or all of screen | FullExpandedRatio × screen height | Full view | Complete information display |

### State Hierarchy Diagram

```
┌─────────────────────────────────────┐
│   FullExpanded (0.8 ratio)          │  ← Largest view
│   ┌──────────────────────────────┐  │
│   │ BottomSheetContent           │  │
│   │ (Full height)                │  │
│   └──────────────────────────────┘  │
│                                      │
│   HalfExpanded (0.35 ratio)          │  ← Medium view
│   ┌──────────────────────────────┐  │
│   │ BottomSheetContent           │  │
│   │ (Medium height)              │  │
│   └──────────────────────────────┘  │
│                                      │
│   Collapsed (CollapsedHeight=100)    │  ← Small view
│   ┌──────────────────────────────┐  │
│   │ Peek bar                     │  │
│   └──────────────────────────────┘  │
│                                      │
│   Hidden                             │  ← Not visible
│                                      │
└─────────────────────────────────────┘
```

---

## State Property Usage

### XAML: Set Initial State

```xaml
<!-- Hidden (Default) -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Content"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- HalfExpanded -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" State="HalfExpanded">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Content"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- FullExpanded -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" State="FullExpanded">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Content"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- Collapsed -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" State="Collapsed" CollapsedHeight="150">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Content"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

### C#: Set State Programmatically

```csharp
using Syncfusion.Maui.Toolkit.BottomSheet;

// Set state at runtime
bottomSheet.State = BottomSheetState.HalfExpanded;
bottomSheet.State = BottomSheetState.FullExpanded;
bottomSheet.State = BottomSheetState.Collapsed;
bottomSheet.State = BottomSheetState.Hidden;
```

### C#: Complete Example

```csharp
// Create and configure Bottom Sheet
var bottomSheet = new SfBottomSheet
{
    State = BottomSheetState.Hidden,           // Initial state
    HalfExpandedRatio = 0.35,                  // 35% of screen
    FullExpandedRatio = 0.9,                   // 90% of screen
    CollapsedHeight = 100                      // 100 pixels
};

// Change states based on user interaction
var expandButton = new Button { Text = "Expand" };
expandButton.Clicked += (s, e) => bottomSheet.State = BottomSheetState.HalfExpanded;

var fullButton = new Button { Text = "Full" };
fullButton.Clicked += (s, e) => bottomSheet.State = BottomSheetState.FullExpanded;

var hideButton = new Button { Text = "Hide" };
hideButton.Clicked += (s, e) => bottomSheet.State = BottomSheetState.Hidden;
```

---

## AllowedState Configuration

The `AllowedState` property restricts which states the Bottom Sheet can transition to. This controls what users can do with the sheet.

### AllowedState Values

| AllowedState | Allowed Transitions | Use Case |
|--------------|-------------------|----------|
| **All** (Default) | FullExpanded ↔ HalfExpanded ↔ Collapsed ↔ Hidden | Full flexibility, users can swipe to any state |
| **FullExpanded** | FullExpanded ↔ Collapsed ↔ Hidden (no HalfExpanded) | Two-state behavior, skip middle state |
| **HalfExpanded** | HalfExpanded ↔ Collapsed ↔ Hidden (no FullExpanded) | Limit expansion, prevent full screen |

### AllowedState Usage

```xaml
<!-- Allow all states (default) -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" AllowedState="All">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Content"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- Only allow FullExpanded and Collapsed/Hidden -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" AllowedState="FullExpanded">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Content"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- Only allow HalfExpanded and Collapsed/Hidden -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" AllowedState="HalfExpanded">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Content"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

### C#: Set AllowedState

```csharp
using Syncfusion.Maui.Toolkit.BottomSheet;

// Allow all states (maximum flexibility)
bottomSheet.AllowedState = BottomSheetAllowedState.All;

// Restrict to Full or Collapsed only
bottomSheet.AllowedState = BottomSheetAllowedState.FullExpanded;

// Restrict to Half or Collapsed only
bottomSheet.AllowedState = BottomSheetAllowedState.HalfExpanded;
```

### Real-World Example: Restrictive States

```csharp
// Modal dialog: only FullExpanded or Hidden (no peeking)
var dialogSheet = new SfBottomSheet
{
    AllowedState = BottomSheetAllowedState.FullExpanded,
    State = BottomSheetState.FullExpanded,
    IsModal = true
};

// Preview panel: only HalfExpanded or Collapsed (never full)
var previewSheet = new SfBottomSheet
{
    AllowedState = BottomSheetAllowedState.HalfExpanded,
    State = BottomSheetState.HalfExpanded,
    HalfExpandedRatio = 0.4
};
```

---

## IsOpen Property

The `IsOpen` property provides a simple boolean way to show or hide the Bottom Sheet programmatically.

### IsOpen Behavior

- **IsOpen = true:** Opens sheet (sets State based on initial configuration)
- **IsOpen = false:** Closes sheet (sets State to Hidden)

### XAML: IsOpen Binding

```xaml
<Grid>
    <Button Text="Toggle Sheet" Clicked="OnToggleClicked"/>
    
    <bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                               IsOpen="False"
                               HalfExpandedRatio="0.35">
        <bottomSheet:SfBottomSheet.BottomSheetContent>
            <VerticalStackLayout Padding="20" Spacing="10">
                <Label Text="Sheet Content" FontSize="18" FontAttributes="Bold"/>
                <Button Text="Close" Clicked="OnCloseClicked"/>
            </VerticalStackLayout>
        </bottomSheet:SfBottomSheet.BottomSheetContent>
    </bottomSheet:SfBottomSheet>
</Grid>
```

### C#: Toggle IsOpen

```csharp
private void OnToggleClicked(object sender, EventArgs e)
{
    bottomSheet.IsOpen = !bottomSheet.IsOpen;
}

private void OnCloseClicked(object sender, EventArgs e)
{
    bottomSheet.IsOpen = false;
}
```

### C#: IsOpen vs. Show/Close Methods

```csharp
// Method 1: Using IsOpen (simple boolean)
bottomSheet.IsOpen = true;   // Opens
bottomSheet.IsOpen = false;  // Closes

// Method 2: Using Show/Close methods (explicit)
bottomSheet.Show();          // Opens
bottomSheet.Close();         // Closes

// Both achieve the same result, choose based on preference
```

---

## State Transitions

### Transition Rules

**When AllowedState = All (default):**
```
Hidden ↔ Collapsed ↔ HalfExpanded ↔ FullExpanded

Possible transitions:
- Hidden → Collapsed → HalfExpanded → FullExpanded (expand up)
- FullExpanded → HalfExpanded → Collapsed → Hidden (collapse down)
- Any state → Any state (if user swipes directly)
```

**When AllowedState = FullExpanded:**
```
Hidden ↔ Collapsed ↔ FullExpanded

No HalfExpanded state:
- Skips from Collapsed directly to FullExpanded
- Cannot transition through HalfExpanded
```

**When AllowedState = HalfExpanded:**
```
Hidden ↔ Collapsed ↔ HalfExpanded

No FullExpanded state:
- Skips from HalfExpanded directly to Hidden
- Cannot reach FullExpanded
```

### Handling State Changes

```csharp
// Subscribe to state changes
bottomSheet.StateChanged += OnStateChanged;

private void OnStateChanged(object sender, StateChangedEventArgs e)
{
    var oldState = e.OldState;
    var newState = e.NewState;
    
    Debug.WriteLine($"State changed from {oldState} to {newState}");
    
    // Perform actions based on new state
    switch (newState)
    {
        case BottomSheetState.Hidden:
            Debug.WriteLine("Sheet is hidden");
            break;
        case BottomSheetState.Collapsed:
            Debug.WriteLine("Sheet is collapsed (peek state)");
            break;
        case BottomSheetState.HalfExpanded:
            Debug.WriteLine("Sheet is half expanded");
            break;
        case BottomSheetState.FullExpanded:
            Debug.WriteLine("Sheet is fully expanded");
            break;
    }
}
```

---

## Practical Scenarios

### Scenario 1: Progressive Disclosure

Users gradually expand content through multiple states.

```csharp
public class ProgressiveDisclosureExample
{
    public void SetupSheet()
    {
        var bottomSheet = new SfBottomSheet
        {
            AllowedState = BottomSheetAllowedState.All,  // All transitions allowed
            State = BottomSheetState.Collapsed,
            CollapsedHeight = 80,                         // Peek preview
            HalfExpandedRatio = 0.4,                      // More details
            FullExpandedRatio = 0.95                      // Full information
        };
        
        bottomSheet.StateChanged += (s, e) =>
        {
            switch (e.NewState)
            {
                case BottomSheetState.Collapsed:
                    Debug.WriteLine("Showing title and quick info");
                    break;
                case BottomSheetState.HalfExpanded:
                    Debug.WriteLine("Showing summary details");
                    break;
                case BottomSheetState.FullExpanded:
                    Debug.WriteLine("Showing complete information");
                    break;
            }
        };
    }
}
```

### Scenario 2: Modal Dialog

Restrict to FullExpanded only, with overlay.

```csharp
public class ModalDialogExample
{
    public SfBottomSheet CreateConfirmationDialog()
    {
        var dialog = new SfBottomSheet
        {
            State = BottomSheetState.FullExpanded,
            AllowedState = BottomSheetAllowedState.FullExpanded,  // Stay full
            IsModal = true,                                       // Show overlay
            CollapseOnOverlayTap = true                           // Close on overlay tap
        };
        
        var content = new VerticalStackLayout { Padding = new Thickness(20), Spacing = 15 };
        
        var message = new Label 
        { 
            Text = "Are you sure you want to delete?", 
            FontSize = 18 
        };
        
        var buttonGrid = new Grid 
        { 
            ColumnDefinitions =
            {
                new ColumnDefinition { Width = GridLength.Star },
                new ColumnDefinition { Width = GridLength.Star }
            },
            ColumnSpacing = 10 
        };
        
        var cancelBtn = new Button 
        { 
            Text = "Cancel",
            Command = new Command(() => dialog.Close())
        };
        
        var deleteBtn = new Button 
        { 
            Text = "Delete",
            BackgroundColor = Colors.Red,
            Command = new Command(OnDeleteConfirmed)
        };
        Grid.SetColumn(deleteBtn, 1);   
        
        buttonGrid.Children.Add(cancelBtn);
        buttonGrid.Children.Add(deleteBtn);
        
        content.Children.Add(message);
        content.Children.Add(buttonGrid);
        
        dialog.BottomSheetContent = content;
        return dialog;
    }
    
    private void OnDeleteConfirmed()
    {
        Debug.WriteLine("Delete confirmed");
    }
}
```

### Scenario 3: Info Peek

Collapsed state shows preview, half-expanded shows more.

```csharp
public class InfoPeekExample
{
    public void CreatePeekSheet()
    {
        var bottomSheet = new SfBottomSheet
        {
            State = BottomSheetState.Collapsed,
            AllowedState = BottomSheetAllowedState.HalfExpanded,  // Limit to half
            CollapsedHeight = 120,  // Show title and preview only
            HalfExpandedRatio = 0.5,  // Show full preview when expanded
            EnableSwiping = true
        };
        
        var peekContent = new VerticalStackLayout { Padding = new Thickness(15), Spacing = 10 };
        
        // Title visible in collapsed state
        var title = new Label 
        { 
            Text = "New Message",
            FontSize = 18,
            FontAttributes = FontAttributes.Bold
        };
        
        // Preview visible when expanded
        var preview = new Label 
        { 
            Text = "Swipe up to read full message...",
            FontSize = 14,
            TextColor = Colors.Gray
        };
        
        // Full content visible at half-expanded
        var fullContent = new Label 
        { 
            Text = "This is the full message content that appears when fully expanded...",
            FontSize = 14,
            LineBreakMode = LineBreakMode.WordWrap
        };
        
        peekContent.Children.Add(title);
        peekContent.Children.Add(preview);
        peekContent.Children.Add(fullContent);
        
        bottomSheet.BottomSheetContent = peekContent;
    }
}
```

---

## State Configuration Best Practices

### ✅ DO:

```csharp
// ✅ Set reasonable ratios
bottomSheet.HalfExpandedRatio = 0.35;   // Comfortable preview
bottomSheet.FullExpandedRatio = 0.9;    // Leave room for status bar
bottomSheet.CollapsedHeight = 100;      // Visible peek area

// ✅ Match AllowedState to your use case
// Modal dialog: FullExpanded only
// Info panel: HalfExpanded only
// Flexible UI: All states

// ✅ Provide feedback for state changes
bottomSheet.StateChanged += HandleStateChange;

// ✅ Use meaningful initial states
bottomSheet.State = BottomSheetState.Hidden;  // Start hidden
```

### ❌ DON'T:

```csharp
// ❌ Don't use very small ratios (confusing to users)
bottomSheet.HalfExpandedRatio = 0.05;   // Too small

// ❌ Don't exceed 100% for FullExpandedRatio
bottomSheet.FullExpandedRatio = 1.2;    // Invalid, use 1.0

// ❌ Don't use conflicting configurations
// AllowedState=FullExpanded but State=HalfExpanded won't work

// ❌ Don't forget to handle state changes if needed
// If state affects other UI, subscribe to StateChanged
```

---
