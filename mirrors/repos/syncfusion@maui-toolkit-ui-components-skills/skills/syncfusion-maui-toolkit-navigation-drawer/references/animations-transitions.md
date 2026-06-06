# Animations and Transitions

## Table of Contents
1. [Animation Types](#animation-types)
2. [Duration Configuration](#duration-configuration)
3. [Animation Easing](#animation-easing)
4. [Transition Effects](#transition-effects)
5. [Performance Optimization](#performance-optimization)
6. [Complete Examples](#complete-examples)

---

## Animation Types

The drawer supports three transition animation types controlled by the `Transition` property.

### SlideOnTop (Default)

The drawer overlays the main content area without pushing it. The content stays in place while the drawer appears above it.

**XAML:**
```xaml
<navigationDrawer:DrawerSettings Transition="SlideOnTop">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.Transition = Transition.SlideOnTop;
```

**Characteristics:**
- Drawer appears on top of content
- Content is dimmed (usually)
- Fastest animation type
- Best for quick access menus
- Most common pattern

**Use Cases:**
- Quick access menus
- Overlay panels
- Modal-like drawers
- Settings panels

**Performance:** ⭐⭐⭐⭐⭐ (Excellent)

---

### Push

The drawer pushes the main content area away. Content moves in the opposite direction of the drawer.

**XAML:**
```xaml
<navigationDrawer:DrawerSettings Transition="Push">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.Transition = Transition.Push;
```

**Characteristics:**
- Content moves with drawer
- Creates space-sharing effect
- Requires reflow of content
- More dramatic visual feedback
- Popular in mobile apps

**Use Cases:**
- Primary navigation
- Permanent drawer appearance
- Content-aware drawers
- Tablet applications

**Performance:** ⭐⭐⭐⭐ (Good)

---

### Reveal

The drawer reveals from behind the main content. Content slides away to expose the drawer.

**XAML:**
```xaml
<navigationDrawer:DrawerSettings Transition="Reveal">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.Transition = Transition.Reveal;
```

**Characteristics:**
- Drawer appears to slide from behind
- Content slides away gradually
- Creates layered visual effect
- Unique 3D-like appearance
- Most visually interesting

**Use Cases:**
- Premium app experiences
- Content-heavy drawers
- Sophisticated UIs
- Media or creative apps

**Performance:** ⭐⭐⭐ (Moderate)

---

## Duration Configuration

Control animation speed with the `Duration` property (in milliseconds).

### Setting Duration

```csharp
drawerSettings.Duration = 300; // milliseconds
```

### Duration Recommendations

| Speed | Duration | Use Case |
|-------|----------|----------|
| Instant | 0-100 | Debug/testing |
| Very Fast | 100-200 | Snappy, responsive feel |
| Fast | 200-300 | Standard, recommended |
| Normal | 300-400 | Smooth, polished |
| Slow | 400-600 | Deliberate, attention-grabbing |

### Common Patterns

```csharp
// Responsive mobile app
drawerSettings.Duration = 250; // Quick response

// Tablet/desktop app
drawerSettings.Duration = 300; // Standard speed

// Accessibility focused
drawerSettings.Duration = 400; // Slower for visibility

// Gaming/entertainment
drawerSettings.Duration = 200; // Quick, snappy
```

### Dynamic Duration

```csharp
private void SetDurationBasedOnContent()
{
    var contentItemCount = menuItems.Count;
    
    // Longer duration for complex drawers
    drawerSettings.Duration = contentItemCount > 10 ? 400 : 300;
}
```

---

## Animation Easing

The `AnimationEasing` property controls acceleration/deceleration curves.

### Available Easing Functions

**XAML:**
```xaml
<navigationDrawer:DrawerSettings AnimationEasing="{x:Static Easing.CubicIn}">
</navigationDrawer:DrawerSettings>
```

**C#:**
```csharp
drawerSettings.AnimationEasing = Easing.CubicIn;
```

### Easing Types

| Easing | Feel | Use Case |
|--------|------|----------|
| Linear (Default) | Even speed | Standard animations |
| CubicIn | Slow start | Careful entry |
| CubicOut | Slow end | Smooth exit |
| CubicInOut | Slow both | Polished feel |
| SinIn | Gentle start | Subtle animations |
| SinOut | Gentle end | Smooth exit |
| SpringOut | Bouncy | Playful animations |

### Easing Examples

```csharp
// Fast entry, slow exit (professional)
drawerSettings.AnimationEasing = Easing.CubicInOut;

// Bouncy, playful animation
drawerSettings.AnimationEasing = Easing.SpringOut;

// Slow and deliberate
drawerSettings.AnimationEasing = Easing.SinInOut;

// Snappy and responsive
drawerSettings.AnimationEasing = Easing.Linear;
```

### Custom Easing

```csharp
// Create custom easing curve
private Easing GetCustomEasing()
{
    return new Easing(p => p < 0.5 
        ? 2 * p * p 
        : 1 - Math.Pow(-2 * p + 2, 2) / 2);
}

drawerSettings.AnimationEasing = GetCustomEasing();
```

---

## Transition Effects

Complete animation configuration combining type, duration, and easing.

### Quick Animation

For responsive, fast interactions:

```csharp
var quickSettings = new DrawerSettings
{
    Transition = Transition.SlideOnTop,
    Duration = 200,
    AnimationEasing = Easing.Linear
};
```

### Smooth Animation

For polished, professional feel:

```csharp
var smoothSettings = new DrawerSettings
{
    Transition = Transition.Push,
    Duration = 350,
    AnimationEasing = Easing.CubicInOut
};
```

### Playful Animation

For entertainment or casual apps:

```csharp
var playfulSettings = new DrawerSettings
{
    Transition = Transition.Reveal,
    Duration = 400,
    AnimationEasing = Easing.SpringOut
};
```

### Accessible Animation

For accessibility compliance:

```csharp
var accessibleSettings = new DrawerSettings
{
    Transition = Transition.SlideOnTop,
    Duration = 500, // Slower for clarity
    AnimationEasing = Easing.CubicInOut
};

// Also respect user's motion preferences
if (AppInfo.RequestedTheme == AppTheme.Light)
{
    // Reduce motion if user prefers
    accessibleSettings.Duration = 300;
}
```

---

## Performance Optimization

Optimize animations for smooth 60 FPS performance.

### Performance Guidelines

**Good Performance (60 FPS):**
- Duration: 200-400ms
- Transition: SlideOnTop or Push
- Simple content (< 50 menu items)
- Standard device (2GB+ RAM)

**Potential Issues:**
- Very long durations (> 600ms)
- Complex animations on old devices
- Too many simultaneous animations
- Heavy content rendering

### Optimization Techniques

```csharp
// Detect device capabilities
private void OptimizeForDevice()
{
    var deviceMemory = GetDeviceMemory();
    
    if (deviceMemory < 2000) // 2GB RAM
    {
        // Reduce animation complexity
        drawerSettings.Duration = 250;
        drawerSettings.Transition = Transition.SlideOnTop;
    }
    else
    {
        // Use more complex animations
        drawerSettings.Duration = 350;
        drawerSettings.Transition = Transition.Reveal;
    }
}

// Disable animations if user prefers reduced motion
private void RespectUserPreferences()
{
    if (IsReducedMotionEnabled())
    {
        drawerSettings.Duration = 0; // Instant
    }
}

// Reduce content complexity during animation
private void OnDrawerOpening(object sender, CancelEventArgs e)
{
    // Temporarily disable heavy rendering
    DisableHeavyUI();
}

private void OnDrawerOpened(object sender, EventArgs e)
{
    // Re-enable after animation
    EnableHeavyUI();
}
```

---

## Complete Examples

### Example 1: Professional App Animation

```csharp
public class ProfessionalDrawerConfig
{
    public static DrawerSettings Create()
    {
        return new DrawerSettings
        {
            Position = Position.Left,
            DrawerWidth = 280,
            Transition = Transition.Push,
            Duration = 350,
            AnimationEasing = Easing.CubicInOut,
            DrawerHeaderHeight = 160,
            DrawerFooterHeight = 70,
            EnableSwipeGesture = true,
            TouchThreshold = 100
        };
    }
}
```

### Example 2: Mobile Game Animation

```csharp
public class GameDrawerConfig
{
    public static DrawerSettings Create()
    {
        return new DrawerSettings
        {
            Position = Position.Left,
            DrawerWidth = 250,
            Transition = Transition.SlideOnTop,
            Duration = 200,
            AnimationEasing = Easing.Linear,
            DrawerHeaderHeight = 100,
            DrawerFooterHeight = 50,
            EnableSwipeGesture = true,
            TouchThreshold = 150
        };
    }
}
```

### Example 3: Accessibility-Focused Animation

```csharp
public class AccessibleDrawerConfig
{
    public static DrawerSettings Create(bool reduceMotion = false)
    {
        return new DrawerSettings
        {
            Position = Position.Left,
            DrawerWidth = 280,
            Transition = Transition.SlideOnTop,
            Duration = reduceMotion ? 100 : 400,
            AnimationEasing = reduceMotion ? Easing.Linear : Easing.CubicInOut,
            DrawerHeaderHeight = 160,
            DrawerFooterHeight = 70,
            EnableSwipeGesture = !reduceMotion,
            TouchThreshold = 120
        };
    }
}
```

### Example 4: Responsive Animation

```csharp
public class ResponsiveAnimationManager
{
    private SfNavigationDrawer navigationDrawer;
    private DrawerSettings drawerSettings;

    public void ConfigureAnimation()
    {
        var displayInfo = DeviceDisplay.Current.MainDisplayInfo;
        
        // Tablet: More complex animation
        if (displayInfo.Width > 600)
        {
            drawerSettings.Transition = Transition.Reveal;
            drawerSettings.Duration = 400;
            drawerSettings.AnimationEasing = Easing.CubicInOut;
        }
        // Phone: Simpler, faster animation
        else
        {
            drawerSettings.Transition = Transition.SlideOnTop;
            drawerSettings.Duration = 250;
            drawerSettings.AnimationEasing = Easing.Linear;
        }
    }
}
```

### Example 5: User Preference-Based Animation

```csharp
public class PreferenceAwareAnimationManager
{
    private DrawerSettings drawerSettings;

    public void ApplyUserPreferences()
    {
        var preferences = GetUserAnimationPreferences();
        
        drawerSettings.Duration = preferences.AnimationDuration;
        drawerSettings.AnimationEasing = GetEasingFromPreference(preferences.AnimationStyle);
        
        // Respect system settings for accessibility
        if (preferences.ReduceMotion)
        {
            drawerSettings.Duration = 100;
            drawerSettings.Transition = Transition.SlideOnTop;
        }
    }
}
```

### Example 6: Testing Different Animations

```csharp
public class AnimationTester
{
    private DrawerSettings drawerSettings;
    private SfNavigationDrawer navigationDrawer;

    public AnimationTester(SfNavigationDrawer drawer)
    {
        navigationDrawer = drawer;
        drawerSettings = drawer.DrawerSettings;
    }

    public async Task TestAllAnimations()
    {
        var transitions = new[]
        {
            Transition.SlideOnTop,
            Transition.Push,
            Transition.Reveal
        };

        var durations = new[] { 200, 350, 500 };

        var easings = new[]
        {
            Easing.Linear,
            Easing.CubicInOut,
            Easing.SpringOut
        };

        foreach (var transition in transitions)
        {
            foreach (var duration in durations)
            {
                foreach (var easing in easings)
                {
                    drawerSettings.Transition = transition;
                    drawerSettings.Duration = duration;
                    drawerSettings.AnimationEasing = easing;

                    navigationDrawer.ToggleDrawer();
                    await Task.Delay(duration + 200);

                    navigationDrawer.ToggleDrawer();
                    await Task.Delay(duration + 200);
                }
            }
        }
    }
}
```

---

## Best Practices

✅ **Do:**
- Use 250-350ms for standard apps
- Choose SlideOnTop for most use cases
- Respect user's reduce motion settings
- Test animations on target devices
- Use CubicInOut for polished feel
- Optimize for lower-end devices

❌ **Don't:**
- Use durations > 500ms (feels sluggish)
- Mix too many easing types
- Ignore accessibility preferences
- Over-animate (keeps animations simple)
- Test only on high-end devices
- Animate every minor interaction

