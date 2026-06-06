# Customization and Styling in .NET MAUI Bottom Sheet

## Table of Contents
1. [Popup Mode (IsModal)](#popup-mode-ismodal)
2. [Colors and Appearance](#colors-and-appearance)
3. [Dimensions and Sizing](#dimensions-and-sizing)
4. [Grabber Customization](#grabber-customization)
5. [Animation Configuration](#animation-configuration)
6. [Complete Styling Examples](#complete-styling-examples)

---

## Popup Mode (IsModal)

The `IsModal` property controls whether the Bottom Sheet acts as a modal dialog that blocks background interaction.

### IsModal Property

| IsModal | Behavior | Overlay | Background Interaction | Use Case |
|---------|----------|---------|----------------------|----------|
| **True** | Modal dialog | Gray overlay appears | Blocked | Dialogs, confirmations, alerts |
| **False** (Default) | Non-modal sheet | No overlay | Allowed | Info panels, menus, filters |

### XAML: IsModal Configuration

```xaml
<!-- Non-modal (default) - can interact with background -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" IsModal="False">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Side panel - background clickable"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- Modal - overlay blocks background -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" IsModal="True">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Modal dialog - overlay blocks background"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

### C#: IsModal Configuration

```csharp
// Non-modal (allow background interaction)
var infoSheet = new SfBottomSheet { IsModal = false };

// Modal (block background interaction)
var dialogSheet = new SfBottomSheet { IsModal = true };
```

### CollapseOnOverlayTap Property

Works with IsModal to enable overlay interaction:

```xaml
<!-- Modal that closes when user taps overlay -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           IsModal="True"
                           CollapseOnOverlayTap="True">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Tap overlay to close"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
var sheet = new SfBottomSheet
{
    IsModal = true,
    CollapseOnOverlayTap = true  // Collapse when overlay tapped
};
```

---

## Colors and Appearance

### Background Color

Set the sheet background color:

```xaml
<!-- XAML: Background color -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" Background="White">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Content on white background"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- System color -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" Background="{AppThemeBinding Light=White, Dark=#1E1E1E}">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Adaptive background"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Background color
var sheet = new SfBottomSheet
{
    Background = Colors.White
};

// C#: Theme-aware color
var adaptiveSheet = new SfBottomSheet
{
    Background = App.Current.UserAppTheme == AppTheme.Light ? Colors.White : Color.FromArgb("#1E1E1E")
};
```

### Corner Radius

Apply rounded corners to the top of the sheet:

```xaml
<!-- XAML: Corner radius -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" CornerRadius="20, 20, 0, 0">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Rounded top corners"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- Format: Top-Left, Top-Right, Bottom-Left, Bottom-Right -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" CornerRadius="15, 15, 0, 0">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="15px top corners, no bottom corners"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Corner radius
var sheet = new SfBottomSheet
{
    CornerRadius = new CornerRadius(20, 20, 0, 0)  // Only top corners
};

// C#: All corners rounded
var allRoundedSheet = new SfBottomSheet
{
    CornerRadius = new CornerRadius(15)  // All corners 15px
};
```

---

## Dimensions and Sizing

### Content Padding

Add space around the sheet content:

```xaml
<!-- XAML: Uniform padding -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" ContentPadding="15">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="15px padding on all sides"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- XAML: Different padding per side -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" ContentPadding="10, 20, 10, 15">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Top:20, Left:10, Right:10, Bottom:15"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Uniform padding
var sheet = new SfBottomSheet
{
    ContentPadding = new Thickness(15)
};

// C#: Different padding per side (Left, Top, Right, Bottom)
var customSheet = new SfBottomSheet
{
    ContentPadding = new Thickness(10, 20, 10, 15)
};
```

### Height Adjustments

#### FullExpandedRatio

Controls height when sheet is in FullExpanded state:

```xaml
<!-- XAML: Full expanded height -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           FullExpandedRatio="0.9"
                           State="FullExpanded">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Takes 90% of screen height"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Full expanded ratio
var sheet = new SfBottomSheet
{
    FullExpandedRatio = 0.9,    // 90% of screen
    State = BottomSheetState.FullExpanded
};

// Valid values: 0.1 to 1.0
var variations = new[]
{
    new SfBottomSheet { FullExpandedRatio = 0.5 },   // 50% of screen
    new SfBottomSheet { FullExpandedRatio = 0.75 },  // 75% of screen
    new SfBottomSheet { FullExpandedRatio = 1.0 }    // 100% of screen
};
```

#### HalfExpandedRatio

Controls height when sheet is in HalfExpanded state:

```xaml
<!-- XAML: Half expanded height -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           HalfExpandedRatio="0.35"
                           State="HalfExpanded">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Takes 35% of screen height"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Half expanded ratio
var sheet = new SfBottomSheet
{
    HalfExpandedRatio = 0.35,   // 35% of screen (preview)
    State = BottomSheetState.HalfExpanded
};

// Valid values: 0.1 to 0.9
var examples = new[]
{
    new SfBottomSheet { HalfExpandedRatio = 0.25 },  // Minimal preview
    new SfBottomSheet { HalfExpandedRatio = 0.35 },  // Medium preview
    new SfBottomSheet { HalfExpandedRatio = 0.5 }    // Large preview
};
```

#### CollapsedHeight

Controls height when sheet is in Collapsed state (in pixels):

```xaml
<!-- XAML: Collapsed height -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           CollapsedHeight="120"
                           State="Collapsed">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Sheet is 120 pixels tall"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Collapsed height (in pixels)
var sheet = new SfBottomSheet
{
    CollapsedHeight = 120,  // 120 pixels
    State = BottomSheetState.Collapsed
};

// Common heights
var examples = new[]
{
    new SfBottomSheet { CollapsedHeight = 80 },    // Minimal bar
    new SfBottomSheet { CollapsedHeight = 120 },   // Title + preview
    new SfBottomSheet { CollapsedHeight = 150 }    // More preview
};
```

### Width Configuration

#### ContentWidthMode

Controls whether sheet uses full width or custom width:

```xaml
<!-- XAML: Full width (default) -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" ContentWidthMode="Full">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Full screen width"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- XAML: Custom width -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           ContentWidthMode="Custom"
                           BottomSheetContentWidth="500">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="500 pixels wide"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Full width (default)
var fullSheet = new SfBottomSheet
{
    ContentWidthMode = BottomSheetContentWidthMode.Full
};

// C#: Custom width
var customSheet = new SfBottomSheet
{
    ContentWidthMode = BottomSheetContentWidthMode.Custom,
    BottomSheetContentWidth = 500  // 500 pixels
};
```

---

## Grabber Customization

The grabber is the drag handle at the top of the sheet.

### ShowGrabber

Toggle grabber visibility:

```xaml
<!-- XAML: Show grabber (default) -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" ShowGrabber="True">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Grabber visible for dragging"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- XAML: Hide grabber -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" ShowGrabber="False">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="No grabber - use buttons to control"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Show grabber (enable user dragging)
var sheet = new SfBottomSheet { ShowGrabber = true };

// C#: Hide grabber (programmatic control only)
var dialogSheet = new SfBottomSheet { ShowGrabber = false };
```

### GrabberWidth and GrabberHeight

Customize grabber dimensions:

```xaml
<!-- XAML: Grabber dimensions -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           GrabberWidth="40"
                           GrabberHeight="5">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Larger grabber handle"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Grabber dimensions (in pixels)
var sheet = new SfBottomSheet
{
    GrabberWidth = 40,      // 40 pixels wide
    GrabberHeight = 5       // 5 pixels tall
};

// Default values
var defaultSheet = new SfBottomSheet
{
    GrabberWidth = 32,      // Default width
    GrabberHeight = 4       // Default height
};
```

### GrabberCornerRadius

Round the corners of the grabber:

```xaml
<!-- XAML: Grabber corner radius -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" GrabberCornerRadius="3">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Rounded grabber"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Grabber corner radius
var sheet = new SfBottomSheet
{
    GrabberCornerRadius = new CornerRadius(3)
};
```

### GrabberBackground

Set grabber color:

```xaml
<!-- XAML: Grabber background color -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" GrabberBackground="LightGray">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Gray grabber"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>

<!-- XAML: Themed grabber -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           GrabberBackground="{AppThemeBinding Light=Gray, Dark=LightGray}">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Adaptive grabber color"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Grabber color
var sheet = new SfBottomSheet
{
    GrabberBackground = Colors.LightGray
};

// C#: Theme-aware color
var themedSheet = new SfBottomSheet
{
    GrabberBackground = App.Current.UserAppTheme == AppTheme.Light 
        ? Colors.Gray 
        : Colors.LightGray
};
```

### GrabberAreaHeight

Increase the draggable area around the grabber:

```xaml
<!-- XAML: Grabber area height -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" GrabberAreaHeight="50">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="Larger touch area for dragging"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Grabber area height (in pixels)
var sheet = new SfBottomSheet
{
    GrabberAreaHeight = 50  // 50 pixels of drag area
};
```

---

## Animation Configuration

### AnimationDuration

Control how fast the sheet opens and closes:

```xaml
<!-- XAML: Animation duration -->
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           IsOpen="True"
                           AnimationDuration="500">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <Label Text="500ms animation"/>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
// C#: Animation duration (in milliseconds)
var sheet = new SfBottomSheet
{
    AnimationDuration = 500  // 500ms = 0.5 seconds
};

// Common durations
var variations = new[]
{
    new SfBottomSheet { AnimationDuration = 300 },  // Fast (0.3s)
    new SfBottomSheet { AnimationDuration = 500 },  // Normal (0.5s)
    new SfBottomSheet { AnimationDuration = 800 }   // Slow (0.8s)
};
```

---

## Complete Styling Examples

### Example 1: Polished Modal Dialog

```csharp
var dialog = new SfBottomSheet
{
    // State and behavior
    State = BottomSheetState.FullExpanded,
    IsModal = true,
    CollapseOnOverlayTap = true,
    
    // Dimensions
    FullExpandedRatio = 0.8,
    ContentPadding = new Thickness(20),
    
    // Appearance
    Background = Colors.White,
    CornerRadius = new CornerRadius(20, 20, 0, 0),
    
    // Grabber
    ShowGrabber = true,
    GrabberBackground = Color.FromArgb("#E0E0E0"),
    GrabberCornerRadius = new CornerRadius(2),
    GrabberWidth = 40,
    GrabberHeight = 4,
    
    // Animation
    AnimationDuration = 400
};

var content = new VerticalStackLayout { Spacing = 20, Padding = 20 };
content.Children.Add(new Label 
{ 
    Text = "Confirm Action", 
    FontSize = 22, 
    FontAttributes = FontAttributes.Bold 
});
content.Children.Add(new Label 
{ 
    Text = "Are you sure you want to proceed?", 
    FontSize = 16, 
    TextColor = Colors.Gray 
});

dialog.BottomSheetContent = content;
```

### Example 2: Minimal Info Peek

```csharp
var peek = new SfBottomSheet
{
    // State and behavior
    State = BottomSheetState.Collapsed,
    IsModal = false,
    
    // Dimensions
    CollapsedHeight = 100,
    HalfExpandedRatio = 0.4,
    ContentPadding = new Thickness(15),
    
    // Appearance
    Background = Colors.White,
    CornerRadius = new CornerRadius(12, 12, 0, 0),
    
    // Grabber - minimal
    ShowGrabber = true,
    GrabberBackground = Color.FromArgb("#D0D0D0"),
    GrabberWidth = 30,
    GrabberHeight = 3,
    
    // Animation
    AnimationDuration = 350
};
```

### Example 3: Dark Theme Sheet

```csharp
var darkSheet = new SfBottomSheet
{
    // Theme colors
    Background = Color.FromArgb("#2A2A2A"),
    
    // State
    State = BottomSheetState.HalfExpanded,
    HalfExpandedRatio = 0.35,
    
    // Appearance
    CornerRadius = new CornerRadius(16, 16, 0, 0),
    ContentPadding = new Thickness(20),
    
    // Grabber for dark theme
    ShowGrabber = true,
    GrabberBackground = Color.FromArgb("#555555"),
    GrabberCornerRadius = new CornerRadius(2),
    
    // Animation
    AnimationDuration = 450
};

// Add dark-themed content
var darkContent = new VerticalStackLayout { Spacing = 10, Padding = 10 };
darkContent.Children.Add(new Label 
{ 
    Text = "Dark Mode Sheet", 
    FontSize = 18, 
    FontAttributes = FontAttributes.Bold,
    TextColor = Colors.White
});
darkContent.Children.Add(new Label 
{ 
    Text = "Content appears on dark background",
    TextColor = Color.FromArgb("#CCCCCC")
});

darkSheet.BottomSheetContent = darkContent;
```

---

## Styling Best Practices

### ✅ DO:

```csharp
// ✅ Use reasonable corner radius (typically 12-20px)
sheet.CornerRadius = new CornerRadius(16, 16, 0, 0);

// ✅ Leave padding for comfortable content (10-20px)
sheet.ContentPadding = new Thickness(15);

// ✅ Use theme-aware colors
sheet.Background = App.Current.UserAppTheme == AppTheme.Light ? Colors.White : Color.FromArgb("#1E1E1E");

// ✅ Make grabber visible for user guidance
sheet.ShowGrabber = true;

// ✅ Use smooth animations (300-500ms)
sheet.AnimationDuration = 400;

// ✅ Match CornerRadius value to your design system
sheet.CornerRadius = new CornerRadius(12, 12, 0, 0);  // Consistent with other components
```

### ❌ DON'T:

```csharp
// ❌ Don't use extreme corner radius values
sheet.CornerRadius = new CornerRadius(50, 50, 0, 0);  // Too rounded

// ❌ Don't remove padding completely
sheet.ContentPadding = new Thickness(0);  // Content touches edges

// ❌ Don't use very slow animations
sheet.AnimationDuration = 2000;  // 2 seconds is too slow

// ❌ Don't hide grabber without alternative controls
sheet.ShowGrabber = false;  // Users can't see how to drag

// ❌ Don't use conflicting colors (low contrast)
sheet.Background = Colors.LightGray;  // Gray content on light gray
sheet.GrabberBackground = Colors.LightGray;  // Can't see grabber
```

---
