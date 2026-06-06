# Positioning and Sizing the Drawer

## Table of Contents
1. [Position Property](#position-property)
2. [Drawer Width](#drawer-width)
3. [Drawer Height](#drawer-height)
4. [Header and Footer Heights](#header-and-footer-heights)
5. [Responsive Sizing](#responsive-sizing)
6. [Position-Specific Recommendations](#position-specific-recommendations)

---

## Position Property

The `Position` property determines which edge the drawer slides from. The drawer supports all four directions.

### Left Position (Default)

The drawer slides in from the left side of the screen. This is the most common pattern for mobile apps.

**XAML:**
```xaml
<navigationDrawer:DrawerSettings Position="Left">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.Position = Position.Left;
```

**Use Cases:**
- Traditional hamburger menu navigation
- Left-aligned sidebar menu
- Mobile app navigation pattern

**Recommended Width:** 250-280 pixels

### Right Position

The drawer slides in from the right side of the screen. Useful for RTL (right-to-left) languages or additional options.

**XAML:**
```xaml
<navigationDrawer:DrawerSettings Position="Right">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.Position = Position.Right;
```

**Use Cases:**
- RTL language apps (Arabic, Hebrew)
- Secondary navigation panel
- Notifications or quick actions menu
- Settings side panel

**Recommended Width:** 250-300 pixels

### Top Position

The drawer slides down from the top of the screen. Less common but useful for specific UI patterns.

**XAML:**
```xaml
<navigationDrawer:DrawerSettings Position="Top">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.Position = Position.Top;
```

**Use Cases:**
- Top tab navigation
- Quick action toolbar
- Filter menu

**Recommended Height:** 100-200 pixels

### Bottom Position

The drawer slides up from the bottom of the screen. Popular pattern for mobile apps.

**XAML:**
```xaml
<navigationDrawer:DrawerSettings Position="Bottom">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.Position = Position.Bottom;
```

**Use Cases:**
- Bottom sheet navigation (Material Design)
- Mobile action menu
- Additional options or details
- Floating action menu

**Recommended Height:** 200-400 pixels

---

## Drawer Width

The `DrawerWidth` property controls the width of the drawer pane when positioned left or right.

### Setting Width

```csharp
var drawerSettings = new DrawerSettings
{
    Position = Position.Left,
    DrawerWidth = 250 // Width in pixels
};
```

### Width Recommendations

| Position | Recommended Width | Notes |
|----------|------------------|-------|
| Left | 250-280 | Standard sidebar width |
| Right | 250-300 | Slightly wider for RTL |
| Top/Bottom | N/A | Use DrawerHeight instead |

### Dynamic Width Based on Screen Size

```csharp
public partial class MainPage : ContentPage
{
    private SfNavigationDrawer navigationDrawer;
    private DrawerSettings drawerSettings;

    public MainPage()
    {
        InitializeComponent();
        
        navigationDrawer = new SfNavigationDrawer();
        drawerSettings = new DrawerSettings
        {
            Position = Position.Left
        };
        
        // Set width based on screen width
        if (DeviceDisplay.Current.MainDisplayInfo.Width > 600)
        {
            drawerSettings.DrawerWidth = 300; // Tablet
        }
        else
        {
            drawerSettings.DrawerWidth = 250; // Phone
        }
        
        navigationDrawer.DrawerSettings = drawerSettings;
    }
}
```

### Minimum and Maximum Width

**⚠️ Best Practices:**
- **Minimum:** 200 pixels (too narrow reduces usability)
- **Maximum:** 400 pixels (exceeds 60% of typical screen width)
- **Optimal:** 250-280 pixels for most apps

```csharp
// Ensure width is within reasonable bounds
drawerSettings.DrawerWidth = Math.Max(200, Math.Min(400, calculatedWidth));
```

---

## Drawer Height

The `DrawerHeight` property controls the height of the drawer pane when positioned top or bottom.

### Setting Height

```csharp
var drawerSettings = new DrawerSettings
{
    Position = Position.Bottom,
    DrawerHeight = 300 // Height in pixels
};
```

### Height Recommendations

| Position | Recommended Height | Notes |
|----------|-------------------|-------|
| Top | 100-200 | Don't obscure main content |
| Bottom | 200-400 | Common for bottom sheets |
| Left/Right | N/A | Use DrawerWidth instead |

### Common Heights for Bottom Sheet

```csharp
// Small bottom sheet (quick preview)
drawerSettings.DrawerHeight = 150;

// Medium bottom sheet (typical actions)
drawerSettings.DrawerHeight = 300;

// Large bottom sheet (details view)
drawerSettings.DrawerHeight = 500;

// Full screen (minus status bar)
drawerSettings.DrawerHeight = DeviceDisplay.Current.MainDisplayInfo.Height - 50;
```

---

## Header and Footer Heights

Configure the height of drawer header and footer sections.

### DrawerHeaderHeight

Controls space allocated for the drawer header (top section).

```csharp
var drawerSettings = new DrawerSettings
{
    DrawerHeaderHeight = 160 // Height in pixels
};
```

**Common Values:**
- `80`: Small header (icon only)
- `120`: Medium header (icon + name)
- `160`: Large header (icon + name + email)
- `200`: Extra large header (full profile section)

### DrawerFooterHeight

Controls space allocated for the drawer footer (bottom section).

```csharp
var drawerSettings = new DrawerSettings
{
    DrawerFooterHeight = 70 // Height in pixels
};
```

**Common Values:**
- `0`: No footer
- `50`: Small footer (single button)
- `70`: Standard footer (logout button)
- `100`: Large footer (multiple buttons)

### Removing Header/Footer

Set height to 0:

```csharp
drawerSettings.DrawerHeaderHeight = 0; // Removes header
drawerSettings.DrawerFooterHeight = 0; // Removes footer
```

---

## Responsive Sizing

Adjust drawer dimensions based on device or orientation.

### Orientation-Based Sizing

```csharp
public partial class MainPage : ContentPage
{
    private SfNavigationDrawer navigationDrawer;
    private DrawerSettings drawerSettings;

    public MainPage()
    {
        InitializeComponent();
        
        navigationDrawer = new SfNavigationDrawer();
        drawerSettings = new DrawerSettings();
        
        // Listen to orientation changes
        MainThread.BeginInvokeOnMainThread(() =>
        {
            DeviceDisplay.Current.MainDisplayInfoChanged += OnDisplayInfoChanged;
            UpdateDrawerSize();
        });
        
        navigationDrawer.DrawerSettings = drawerSettings;
    }

    private void OnDisplayInfoChanged(object sender, DisplayInfoChangedEventArgs e)
    {
        UpdateDrawerSize();
    }

    private void UpdateDrawerSize()
    {
        var displayInfo = DeviceDisplay.Current.MainDisplayInfo;
        
        if (displayInfo.Orientation == DisplayOrientation.Portrait)
        {
            // Portrait mode
            drawerSettings.Position = Position.Left;
            drawerSettings.DrawerWidth = 250;
        }
        else
        {
            // Landscape mode
            drawerSettings.Position = Position.Left;
            drawerSettings.DrawerWidth = 300; // Wider on landscape
        }
    }
}
```

### Screen Size-Based Sizing

```csharp
private void ConfigureForScreenSize()
{
    var screenWidth = DeviceDisplay.Current.MainDisplayInfo.Width;
    var screenHeight = DeviceDisplay.Current.MainDisplayInfo.Height;
    
    if (screenWidth > 1000) // Tablet
    {
        drawerSettings.Position = Position.Left;
        drawerSettings.DrawerWidth = 350;
    }
    else if (screenWidth > 600) // Large phone
    {
        drawerSettings.Position = Position.Left;
        drawerSettings.DrawerWidth = 300;
    }
    else // Small phone
    {
        drawerSettings.Position = Position.Left;
        drawerSettings.DrawerWidth = 250;
    }
}
```

---

## Position-Specific Recommendations

### Left Position Setup

Best for standard navigation:

```csharp
var drawerSettings = new DrawerSettings
{
    Position = Position.Left,
    DrawerWidth = 250,
    DrawerHeaderHeight = 160,
    DrawerFooterHeight = 70,
    Transition = Transition.Push, // Smooth content shift
    Duration = 300
};
```

### Right Position Setup

For RTL or secondary panels:

```csharp
var drawerSettings = new DrawerSettings
{
    Position = Position.Right,
    DrawerWidth = 280,
    DrawerHeaderHeight = 0, // Often omitted for right panel
    DrawerFooterHeight = 0,
    Transition = Transition.SlideOnTop,
    Duration = 300
};
```

### Top Position Setup

For filter or toolbar:

```csharp
var drawerSettings = new DrawerSettings
{
    Position = Position.Top,
    DrawerHeight = 150,
    Transition = Transition.Push,
    Duration = 250
};
```

### Bottom Position Setup

For action sheet or options:

```csharp
var drawerSettings = new DrawerSettings
{
    Position = Position.Bottom,
    DrawerHeight = 300,
    Transition = Transition.SlideOnTop,
    Duration = 300,
    EnableSwipeGesture = true,
    TouchThreshold = 150 // Larger swipe area
};
```

---

## Complete Configuration Example

```csharp
public class NavigationDrawerConfig
{
    public static DrawerSettings GetOptimalSettings(DeviceType deviceType)
    {
        return deviceType switch
        {
            DeviceType.Phone => new DrawerSettings
            {
                Position = Position.Left,
                DrawerWidth = 250,
                DrawerHeaderHeight = 160,
                DrawerFooterHeight = 70,
                Duration = 300,
                Transition = Transition.Push,
                EnableSwipeGesture = true,
                TouchThreshold = 120
            },
            
            DeviceType.Tablet => new DrawerSettings
            {
                Position = Position.Left,
                DrawerWidth = 320,
                DrawerHeaderHeight = 180,
                DrawerFooterHeight = 80,
                Duration = 300,
                Transition = Transition.Push,
                EnableSwipeGesture = true,
                TouchThreshold = 150
            },
            
            DeviceType.Desktop => new DrawerSettings
            {
                Position = Position.Left,
                DrawerWidth = 350,
                DrawerHeaderHeight = 200,
                DrawerFooterHeight = 100,
                Duration = 250,
                Transition = Transition.Push,
                EnableSwipeGesture = false
            },
            
            _ => new DrawerSettings()
        };
    }
}

public enum DeviceType
{
    Phone,
    Tablet,
    Desktop
}
```

