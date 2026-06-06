# Advanced Features

This guide covers advanced features including Right-to-Left (RTL) support, and other special capabilities.

## Right-to-Left (RTL) Support

The Segmented Control supports right-to-left rendering for languages like Arabic, Hebrew, and Persian.

### Enabling RTL

Set the `FlowDirection` property to `RightToLeft`.

**XAML:**
```xml
<buttons:SfSegmentedControl FlowDirection="RightToLeft">
    <buttons:SfSegmentedControl.ItemsSource>
        <x:Array Type="{x:Type x:String}">
            <x:String>اليوم</x:String>
            <x:String>أسبوع</x:String>
            <x:String>شهر</x:String>
            <x:String>سنة</x:String>
        </x:Array>
    </buttons:SfSegmentedControl.ItemsSource>
</buttons:SfSegmentedControl>
```

**C#:**
```csharp
var segmentedControl = new SfSegmentedControl
{
    FlowDirection = FlowDirection.RightToLeft,
    ItemsSource = new List<string> { "اليوم", "أسبوع", "شهر", "سنة" }
};
```

### Effects of RTL

When `FlowDirection` is set to `RightToLeft`:
- **Segment order:** Reversed (rightmost segment becomes first)
- **Text alignment:** Right-aligned within segments
- **Selection indicator:** Starts from right
- **Scrolling:** Scrolls from right to left

### Automatic RTL Based on Culture

Set FlowDirection based on current culture:

```csharp
public void SetSegmentedControlDirection()
{
    var currentCulture = CultureInfo.CurrentCulture;
    
    // Check if current culture is RTL
    bool isRightToLeft = currentCulture.TextInfo.IsRightToLeft;
    
    segmentedControl.FlowDirection = isRightToLeft 
        ? FlowDirection.RightToLeft 
        : FlowDirection.LeftToRight;
}
```

### RTL with Icons

Icons maintain their orientation but the segment order reverses:

```csharp
var segmentedControl = new SfSegmentedControl
{
    FlowDirection = FlowDirection.RightToLeft,
    ItemsSource = new List<SfSegmentItem>
    {
        new SfSegmentItem { Text = "الصفحة الرئيسية", ImageSource = "home.png" },
        new SfSegmentItem { Text = "بحث", ImageSource = "search.png" },
        new SfSegmentItem { Text = "الملف الشخصي", ImageSource = "profile.png" }
    }
};
```

### Testing RTL Layout

Test RTL support by:
1. Changing device language to Arabic, Hebrew, or Persian
2. Setting FlowDirection property explicitly
3. Using RTL text content
4. Verifying segment order and selection behavior

## Platform-Specific Considerations

### iOS

- **Touch targets:** Ensure minimum 44x44 points
- **Safe areas:** Account for notches and home indicators
- **Dark mode:** Test appearance in both light and dark modes

### Android

- **Touch targets:** Ensure minimum 48x48 dp
- **Material Design:** Consider Material Design guidelines for segmented buttons
- **API levels:** Test on various Android versions

### Windows

- **Mouse interaction:** Hover states may differ
- **Keyboard navigation:** Support Tab key navigation
- **High contrast:** Test with high contrast themes

### macOS

- **Native feel:** Match macOS UI conventions
- **Trackpad gestures:** Consider swipe gestures for scrolling
- **Accessibility:** Support VoiceOver

## Accessibility Features

### Screen Reader Support

Segments are automatically announced by screen readers with their text content.

**Improve accessibility:**
```csharp
var segmentedControl = new SfSegmentedControl
{
    ItemsSource = new List<SfSegmentItem>
    {
        new SfSegmentItem 
        { 
            Text = "Day",
            // Automation ID for testing
            AutomationId = "DaySegment"
        }
    }
};
```

### Keyboard Navigation

Support keyboard navigation (desktop platforms):
- **Tab:** Focus on control
- **Arrow keys:** Navigate between segments
- **Space/Enter:** Select focused segment

### High Contrast Modes

Test in high contrast modes to ensure visibility:

```csharp
public void ApplyAccessibleColors()
{
    // Check for high contrast mode
    bool isHighContrast = Application.Current.RequestedTheme == AppTheme.Light;
    
    if (isHighContrast)
    {
        segmentedControl.Stroke = Colors.Black;
        segmentedControl.SelectionIndicatorSettings = new SelectionIndicatorSettings
        {
            Background = Colors.Yellow,
            TextColor = Colors.Black
        };
    }
}
```

## Performance Optimization

### Minimize Redraws

Avoid frequent updates to ItemsSource:

```csharp
// ✗ Bad: Creates new collection on every call
segmentedControl.ItemsSource = GetSegments();

// ✓ Good: Update once
var segments = GetSegments();
segmentedControl.ItemsSource = segments;
```

### Lazy Loading for Scrollable Segments

For many segments, consider lazy loading:

```csharp
public void LoadSegmentsAsNeeded(int visibleCount)
{
    var initialSegments = allSegments.Take(visibleCount).ToList();
    segmentedControl.ItemsSource = initialSegments;
    
    // Load more as user scrolls (implement custom logic)
}
```

### Image Caching

Cache images to improve performance:

```csharp
var segmentedControl = new SfSegmentedControl
{
    ItemsSource = new List<SfSegmentItem>
    {
        new SfSegmentItem 
        { 
            ImageSource = ImageSource.FromFile("icon.png"),
            // Images are cached by default in MAUI
        }
    }
};
```

## Custom Animations

While the control provides built-in ripple animation, you can add custom animations:

```csharp
segmentedControl.SelectionChanged += async (sender, e) =>
{
    // Custom fade animation on selection
    await segmentedControl.FadeTo(0.5, 100);
    await segmentedControl.FadeTo(1.0, 100);
};
```

## Troubleshooting

### RTL Not Working

**Cause:** FlowDirection not set or overridden by parent  
**Solution:** Set FlowDirection explicitly on SfSegmentedControl

### Keyboard Navigation Not Working

**Cause:** Control not focusable or platform doesn't support  
**Solution:** Test on desktop platforms, ensure control is in visual tree

## Next Steps

- **Getting started:** See [getting-started.md](getting-started.md) for initial setup
- **Customization:** See [customization.md](customization.md) for appearance options
- **Events:** See [events.md](events.md) for handling user interactions