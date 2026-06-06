# Gestures and Accessibility

## Table of Contents
1. [Swipe Gesture Support](#swipe-gesture-support)
2. [Touch Threshold Configuration](#touch-threshold-configuration)
3. [Programmatic Drawer Control](#programmatic-drawer-control)
4. [Keyboard Accessibility](#keyboard-accessibility)
5. [Screen Reader Support](#screen-reader-support)
6. [Best Practices](#best-practices)
7. [Complete Implementation](#complete-implementation)

---

## Swipe Gesture Support

Enable users to open/close the drawer by swiping from the screen edge.

### Enabling Swipe Gesture

**XAML:**
```xaml
<navigationDrawer:DrawerSettings EnableSwipeGesture="True">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.EnableSwipeGesture = true;
```

### Swipe Directions

Swipe direction depends on drawer position:

| Position | Swipe Direction | How to Trigger |
|----------|-----------------|----------------|
| Left | Left ← Right | Swipe from left edge rightward |
| Right | Right → Left | Swipe from right edge leftward |
| Top | Top ↓ Down | Swipe from top edge downward |
| Bottom | Bottom ↑ Up | Swipe from bottom edge upward |

### Gesture Sensitivity

**Default:** Swipe must start within 120 pixels from screen edge

```csharp
// Increase sensitivity (easier to swipe)
drawerSettings.TouchThreshold = 200;

// Decrease sensitivity (harder to swipe)
drawerSettings.TouchThreshold = 50;
```

---

## Touch Threshold Configuration

The `TouchThreshold` property controls the area where swipe gestures are recognized.

### Understanding TouchThreshold

```
Screen Edge
    ↓
┌────────────────────────────────┐
│ ← TouchThreshold pixels wide → │
│                                │
│ Touch anywhere here to swipe   │
│                                │
│                                │
│ ← Rest of screen (no gesture) →│
└────────────────────────────────┘
```

### Setting TouchThreshold

```csharp
var drawerSettings = new DrawerSettings
{
    EnableSwipeGesture = true,
    TouchThreshold = 120 // default
};
```

### Recommended Values

| Use Case | Threshold | Notes |
|----------|-----------|-------|
| Precise (desktop) | 50-80 | Narrow swipe area |
| Standard (mobile) | 100-150 | Comfortable for touch |
| Generous (tablets) | 150-200 | Large swipe area |
| Accessibility | 200-250 | Extra large for ease |

### Device-Specific Configuration

```csharp
private void ConfigureTouchThreshold()
{
    var displayInfo = DeviceDisplay.Current.MainDisplayInfo;
    var screenWidth = displayInfo.Width;
    
    // Percentage-based threshold
    double thresholdPercentage = 0.15; // 15% of screen width
    drawerSettings.TouchThreshold = (int)(screenWidth * thresholdPercentage);
}
```

### Accessibility-Aware Configuration

```csharp
private void ConfigureForAccessibility()
{
    if (HasMotorImpairment())
    {
        // Larger touch area for easier swiping
        drawerSettings.TouchThreshold = 250;
        drawerSettings.Duration = 400; // Slower animation
    }
    else
    {
        drawerSettings.TouchThreshold = 120;
        drawerSettings.Duration = 300;
    }
}
```

---

## Programmatic Drawer Control

Control the drawer through code without user interaction.

### ToggleDrawer Method

Opens or closes the drawer, toggling its state.

```csharp
// Toggle drawer (open if closed, close if open)
navigationDrawer.ToggleDrawer();
```

### Opening Drawer from Button Click

```xaml
<Button Text="Open Menu" Clicked="OnOpenMenuClicked"/>
```

```csharp
private void OnOpenMenuClicked(object sender, EventArgs e)
{
    navigationDrawer.ToggleDrawer();
    // Or:
    // navigationDrawer.IsOpen = true;
}
```

### Programmatic Navigation

```csharp
private void OnMenuItemSelected(object sender, SelectedItemChangedEventArgs e)
{
    var selectedPage = e.SelectedItem as MenuItemModel;

    if (selectedPage != null)
    {
        // Navigate to selected page
        NavigateToPage(selectedPage.PageType);

        // Close drawer after selection
        navigationDrawer.IsOpen = false;
    }
}

private void NavigateToPage(Type pageType)
{
    var page = (Page)Activator.CreateInstance(pageType);
    Navigation.PushAsync(page);
}
```

### Conditional Opening

```csharp
private bool CanOpenDrawer()
{
    // Don't open if already processing
    if (isProcessing) return false;
    
    // Don't open on certain pages
    if (CurrentPageType == typeof(LoginPage)) return false;
    
    // Don't open if user not authenticated
    if (!isUserAuthenticated) return false;
    
    return true;
}

private void AttemptToOpenDrawer()
{
    if (CanOpenDrawer())
    {
        navigationDrawer.IsOpen = true;
    }
}
```

---

## Keyboard Accessibility

Enable keyboard navigation for keyboard users and screen readers.

### Keyboard Navigation Pattern

```csharp
public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        
        // Handle keyboard input
        this.Loaded += (s, e) =>
        {
            SetupKeyboardHandling();
        };
    }

    private void SetupKeyboardHandling()
    {
        // Handle physical keyboard events
        // Note: MAUI doesn't have direct keyboard intercept, 
        // but you can handle in platform-specific code
    }
}
```

### Using SemanticProperties for Navigation

```xaml
<ImageButton x:Name="hamburgerButton"
             Source="hamburger.png"
             SemanticProperties.Hint="Open navigation menu"
             SemanticProperties.Description="Tap to open or close the navigation drawer"
             Clicked="OnHamburgerClicked"/>
```

### Tab Order Management

```xaml
<VerticalStackLayout>
    <Button Text="Home" 
            SemanticProperties.TabIndex="1"/>
    <Button Text="Profile" 
            SemanticProperties.TabIndex="2"/>
    <Button Text="Settings" 
            SemanticProperties.TabIndex="3"/>
</VerticalStackLayout>
```

---

## Screen Reader Support

Ensure drawer content is accessible to screen readers.

### ARIA Labels and Hints

```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer"
                                     SemanticProperties.Hint="Navigation drawer"
                                     SemanticProperties.Description="Contains navigation menu">
    
    <navigationDrawer:SfNavigationDrawer.ContentView>
        <Grid>
            <!-- Provide semantic properties for all interactive elements -->
            <ImageButton Source="hamburger.png"
                        SemanticProperties.Hint="Open menu"
                        SemanticProperties.Description="Tap to open navigation drawer"/>
        </Grid>
    </navigationDrawer:SfNavigationDrawer.ContentView>
</navigationDrawer:SfNavigationDrawer>
```

### Menu Item Accessibility

```xaml
<ListView x:Name="menuListView">
    <ListView.ItemTemplate>
        <DataTemplate>
            <ViewCell>
                <VerticalStackLayout HeightRequest="45" Padding="15,10">
                    <Label Text="{Binding MenuName}"
                           SemanticProperties.Hint="{Binding MenuName}"
                           SemanticProperties.Description="{Binding MenuDescription}"/>
                </VerticalStackLayout>
            </ViewCell>
        </DataTemplate>
    </ListView.ItemTemplate>
</ListView>
```

### Announce State Changes

```csharp
private void OnDrawerToggled(object sender, ToggledEventArgs e)
{
    var announcement = e.IsOpen 
        ? "Navigation drawer opened" 
        : "Navigation drawer closed";
    
    // Announce to screen readers (platform-specific)
    AnnounceForAccessibility(announcement);
}

private void AnnounceForAccessibility(string message)
{
    #if __IOS__
    // iOS announcement
    #elif __ANDROID__
    // Android announcement
    #endif
}
```

---

## Best Practices

### ✅ Do

- Enable swipe gestures for intuitive interaction
- Provide keyboard alternatives to swipe
- Use semantic properties for screen readers
- Test with screen readers (NVDA, JAWS, VoiceOver)
- Provide clear, descriptive labels
- Use appropriate contrast ratios (WCAG 2.1 AA)
- Allow sufficient touch target sizes (44x44 minimum)
- Announce drawer state changes

### ❌ Don't

- Rely solely on swipe gestures
- Use colors alone to convey information
- Create touch targets smaller than 44x44 pixels
- Hide keyboard navigation
- Omit alt text or descriptions
- Ignore screen reader compatibility
- Use confusing gesture combinations
- Disable accessibility features

---

## Complete Implementation

### Full Accessible Drawer Setup

```csharp
public partial class AccessibleMainPage : ContentPage
{
    private SfNavigationDrawer navigationDrawer;
    private DrawerSettings drawerSettings;

    public AccessibleMainPage()
    {
        InitializeComponent();
        SetupAccessibleDrawer();
    }

    private void SetupAccessibleDrawer()
    {
        navigationDrawer = new SfNavigationDrawer();
        drawerSettings = new DrawerSettings
        {
            Position = Position.Left,
            DrawerWidth = 280,
            EnableSwipeGesture = true,
            TouchThreshold = 150, // Generous for accessibility
            Duration = 400, // Slower for clarity
            DrawerHeaderHeight = 160,
            DrawerFooterHeight = 70
        };

        navigationDrawer.DrawerSettings = drawerSettings;

        // Subscribe to events
        navigationDrawer.DrawerToggled += OnDrawerToggled;
        
        // Setup main content with hamburger button
        SetupMainContent();
    }

    private void SetupMainContent()
    {
        var mainGrid = new Grid
        {
            RowDefinitions = new RowDefinitionCollection
            {
                new RowDefinition { Height = new GridLength(60, GridUnitType.Absolute) },
                new RowDefinition { Height = new GridLength(1, GridUnitType.Star) }
            }
        };

        // Accessible hamburger button
        var hamburgerButton = new ImageButton
        {
            Source = "hamburger.png",
            HeightRequest = 50,
            WidthRequest = 50,
            HorizontalOptions = LayoutOptions.Start,
            VerticalOptions = LayoutOptions.Center,
            Padding = 10
        };

        // Add semantic properties for screen reader
        SemanticProperties.SetHint(hamburgerButton, "Open navigation menu");
        SemanticProperties.SetDescription(hamburgerButton, 
            "Tap or swipe from left edge to open the navigation drawer");

        hamburgerButton.Clicked += (s, e) => navigationDrawer.ToggleDrawer();

        var headerLabel = new Label
        {
            Text = "App Name",
            FontSize = 18,
            TextColor = Colors.White,
            BackgroundColor = Color.FromArgb("#6750A4"),
            Padding = 15,
            VerticalOptions = LayoutOptions.Center
        };

        var headerStack = new HorizontalStackLayout
        {
            Children = { hamburgerButton, headerLabel }
        };

        mainGrid.Add(headerStack, 0, 0);

        var contentLabel = new Label
        {
            Text = "Main Content Area",
            FontSize = 18,
            HorizontalOptions = LayoutOptions.Center,
            VerticalOptions = LayoutOptions.Center
        };

        mainGrid.Add(contentLabel, 0, 1);

        navigationDrawer.ContentView = mainGrid;
        this.Content = navigationDrawer;
    }

    private void OnDrawerToggled(object sender, ToggledEventArgs e)
    {
        var message = e.IsOpen 
            ? "Navigation drawer opened. Use arrow keys to navigate menu items." 
            : "Navigation drawer closed.";

        // Visual feedback
        DisplayAlert("Status", message, "OK");
        
        // Announce to screen readers
        AnnounceForAccessibility(message);
    }

    private void AnnounceForAccessibility(string message)
    {
        // Platform-specific implementation
        #if __ANDROID__
        // Use Android accessibility announcement
        #elif __IOS__
        // Use iOS VoiceOver announcement
        #endif
    }
}
```

### Responsive Gesture Configuration

```csharp
public class GestureConfigManager
{
    public static DrawerSettings GetOptimalGestureConfig(
        bool isAccessibilityMode = false)
    {
        var displayInfo = DeviceDisplay.Current.MainDisplayInfo;
        
        var settings = new DrawerSettings
        {
            Position = Position.Left,
            EnableSwipeGesture = true,
            TouchThreshold = isAccessibilityMode ? 200 : 120,
            Duration = isAccessibilityMode ? 500 : 300,
            DrawerWidth = (int)(displayInfo.Width * 0.65) // 65% of screen
        };

        return settings;
    }
}
```

### Testing Accessibility

```csharp
public class AccessibilityTester
{
    public void TestKeyboardNavigation()
    {
        // Verify all interactive elements are keyboard accessible
        // Tab through all menu items
        // Test Enter/Space activation
    }

    public void TestScreenReaderCompatibility()
    {
        // Enable screen reader (platform-specific)
        // Verify all elements are announced
        // Check semantic hierarchy
    }

    public void TestTouchTargetSizes()
    {
        // Verify hamburger button is 44x44 minimum
        // Verify menu items are 44px height minimum
        // Check spacing between touch targets
    }

    public void TestColorContrast()
    {
        // Verify text contrast ratio ≥ 4.5:1
        // Use contrast checker tools
        // Test with accessibility simulator
    }
}
```

---

## Accessibility Checklist

- [ ] Swipe gestures enabled (`EnableSwipeGesture = true`)
- [ ] Touch threshold appropriate for target users
- [ ] Semantic properties added to all interactive elements
- [ ] Screen reader hints and descriptions provided
- [ ] Tab order logical and complete
- [ ] Touch targets ≥ 44x44 pixels
- [ ] Text contrast ≥ 4.5:1 (WCAG AA)
- [ ] Keyboard navigation fully functional
- [ ] State changes announced to screen readers
- [ ] Tested with actual accessibility tools
- [ ] Supports reduced motion settings
- [ ] Works with platform accessibility features
