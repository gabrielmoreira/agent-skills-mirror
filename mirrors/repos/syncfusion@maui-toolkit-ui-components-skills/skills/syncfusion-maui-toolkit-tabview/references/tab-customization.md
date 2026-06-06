# Tab Customization & Styling

## Table of Contents
1. [Tab Header Customization](#tab-header-customization)
2. [Tab Bar Appearance](#tab-bar-appearance)
3. [Image Positioning](#image-positioning)
4. [Text and Font Customization](#text-and-font-customization)
5. [Color and Styling](#color-and-styling)
6. [Animation and Transitions](#animation-and-transitions)
7. [Scroll Buttons and Overflow](#scroll-buttons-and-overflow)
8. [Performance Optimization: Enable Virtualization](#performance-optimization)
9. [Styling Best Practices](#styling-best-practices)
10. [Complete API Reference](#complete-api-Reference)

---

## Tab Header Customization

### Basic Header Setup

Every tab requires a header that identifies its content. The header can be text, icon, image, or custom content.

**Text Header:**
```xaml
<tabView:SfTabItem Header="Home" />
```

**Icon Header:**
```xaml
<tabView:SfTabItem Header="Photos" ImageSource="photo_icon.png" />
```

### Custom Header Content

Use `HeaderContent` for complete control over header layout:

```xaml
<tabView:SfTabItem>
    <tabView:SfTabItem.HeaderContent>
        <Grid ColumnSpacing="5" HorizontalOptions="Center" VerticalOptions="Center">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="Auto"/>
                <ColumnDefinition Width="*"/>
            </Grid.ColumnDefinitions>
            <Image Source="call_icon.png" HeightRequest="20" WidthRequest="20"/>
            <Label Grid.Column="1" Text="Call" VerticalTextAlignment="Center"/>
        </Grid>
    </tabView:SfTabItem.HeaderContent>
    <tabView:SfTabItem.Content>
        <!-- Tab content -->
    </tabView:SfTabItem.Content>
</tabView:SfTabItem>
```

**C# Equivalent:**
```csharp
var headerGrid = new Grid
{
    ColumnSpacing = 5,
    HorizontalOptions = LayoutOptions.Center,
    VerticalOptions = LayoutOptions.Center,
    ColumnDefinitions =
    {
        new ColumnDefinition { Width = GridLength.Auto },
        new ColumnDefinition { Width = GridLength.Star }
    }
};

var icon = new Image { Source = "call_icon.png", HeightRequest = 20, WidthRequest = 20 };
Grid.SetColumn(icon, 0);

var label = new Label 
{ 
    Text = "Call",
    VerticalTextAlignment = TextAlignment.Center
};
Grid.SetColumn(label, 1);

headerGrid.Children.Add(icon);
headerGrid.Children.Add(label);

var tabItem = new SfTabItem
{
    HeaderContent = headerGrid,
    Content = new StackLayout { /* content */ }
};
```

---

## Tab Bar Appearance

### Header Position

Control where the tab bar is positioned relative to content:

```xaml
<!-- Top (default) -->
<tabView:SfTabView TabBarPlacement="Top">
    <!-- Tabs -->
</tabView:SfTabView>

<!-- Bottom -->
<tabView:SfTabView TabBarPlacement="Bottom">
    <!-- Tabs -->
</tabView:SfTabView>

```

### Tab Width Mode

Control how tab width is calculated:

```xaml
<!-- Default: Fixed width tabs -->
<tabView:SfTabView TabWidthMode="Default">
    <!-- Tabs -->
</tabView:SfTabView>

<!-- SizeToContent: Width based on content -->
<tabView:SfTabView TabWidthMode="SizeToContent">
    <!-- Tabs -->
</tabView:SfTabView>

```

### Tab Bar Background and Colors

```xaml
<tabView:SfTabView 
    TabBarBackground="#FDF8F6"
    IndicatorBackground="#6200EE"
    IndicatorPlacement="Top">
    <!-- Tabs -->
</tabView:SfTabView>
```

**C# Equivalent:**
```csharp
var tabView = new SfTabView
{
    TabBarBackground = Color.FromArgb("#FDF8F6"),
    IndicatorBackground = Color.FromArgb("#6200EE"),
    IndicatorPlacement = TabIndicatorPlacement.Top
};
```

### Header Padding

Control spacing around header content (only works with `TabWidthMode="SizeToContent"`):

```xaml
<tabView:SfTabView TabWidthMode="SizeToContent" TabHeaderPadding="5,10,5,10">
    <tabView:SfTabItem Header="Tab 1" />
    <tabView:SfTabItem Header="Tab 2" />
</tabView:SfTabView>
```

**C# Equivalent:**
```csharp
tabView.TabWidthMode = TabWidthMode.SizeToContent;
tabView.TabHeaderPadding = new Thickness(5, 10, 5, 10);
```

---

## Image Positioning

### Image Position Options

Control the position of images relative to text in tab headers:

**Top Position:**
```xaml
<tabView:SfTabItem 
    Header="Gallery" 
    ImageSource="gallery.png" 
    ImagePosition="Top">
    <!-- Content -->
</tabView:SfTabItem>
```

**Bottom Position:**
```xaml
<tabView:SfTabItem 
    Header="Gallery" 
    ImageSource="gallery.png" 
    ImagePosition="Bottom">
    <!-- Content -->
</tabView:SfTabItem>
```

**Left Position:**
```xaml
<tabView:SfTabItem 
    Header="Gallery" 
    ImageSource="gallery.png" 
    ImagePosition="Left">
    <!-- Content -->
</tabView:SfTabItem>
```

**Right Position:**
```xaml
<tabView:SfTabItem 
    Header="Gallery" 
    ImageSource="gallery.png" 
    ImagePosition="Right">
    <!-- Content -->
</tabView:SfTabItem>
```

### Image Spacing and Size

```xaml
<tabView:SfTabItem 
    Header="Gallery" 
    ImageSource="gallery.png"
    ImagePosition="Left"
    ImageTextSpacing="10"
    ImageSize="32">
    <!-- Content -->
</tabView:SfTabItem>
```

**C# Equivalent:**
```csharp
var tabItem = new SfTabItem
{
    Header = "Gallery",
    ImageSource = "gallery.png",
    ImagePosition = TabImagePosition.Left,
    ImageTextSpacing = 10,
    ImageSize = 32
};
```

---

## Text and Font Customization

### Text Color

```xaml
<tabView:SfTabItem Header="Home" TextColor="Blue">
    <!-- Content -->
</tabView:SfTabItem>
```

**C# Equivalent:**
```csharp
var tabItem = new SfTabItem
{
    Header = "Home",
    TextColor = Colors.Blue
};
```

### Font Family

```xaml
<tabView:SfTabItem Header="Home" FontFamily="OpenSansRegular">
    <!-- Content -->
</tabView:SfTabItem>
```

### Font Size

```xaml
<tabView:SfTabItem Header="Home" FontSize="18">
    <!-- Content -->
</tabView:SfTabItem>
```

### Font Attributes (Bold, Italic)

```xaml
<tabView:SfTabItem Header="Home" FontAttributes="Bold">
    <!-- Content -->
</tabView:SfTabItem>

<tabView:SfTabItem Header="Settings" FontAttributes="Italic">
    <!-- Content -->
</tabView:SfTabItem>

<tabView:SfTabItem Header="Favorites" FontAttributes="Bold,Italic">
    <!-- Content -->
</tabView:SfTabItem>
```

**C# Equivalent:**
```csharp
var boldTab = new SfTabItem
{
    Header = "Home",
    FontAttributes = FontAttributes.Bold
};

var italicTab = new SfTabItem
{
    Header = "Settings",
    FontAttributes = FontAttributes.Italic
};

var boldItalicTab = new SfTabItem
{
    Header = "Favorites",
    FontAttributes = FontAttributes.Bold | FontAttributes.Italic
};
```

### Font Auto-Scaling

Enable automatic font scaling based on system text size settings:

```xaml
<tabView:SfTabView FontAutoScalingEnabled="True">
    <tabView:SfTabItem Header="Home" />
</tabView:SfTabView>
```

---

## Color and Styling

### Complete Styling Example

```xaml
<tabView:SfTabView 
    TabBarBackground="#F5F5F5"
    IndicatorBackground="#6200EE"
    IndicatorPlacement="Bottom">
    
    <tabView:SfTabItem 
        Header="Home"
        TextColor="#333333"
        FontFamily="OpenSansRegular"
        FontSize="14"
        FontAttributes="Bold">
        <tabView:SfTabItem.Content>
            <StackLayout Padding="15" Spacing="10">
                <Label Text="Home Content" FontSize="16"/>
            </StackLayout>
        </tabView:SfTabItem.Content>
    </tabView:SfTabItem>
    
    <tabView:SfTabItem 
        Header="Settings"
        ImageSource="settings.png"
        ImagePosition="Left"
        TextColor="#666666"
        FontSize="14">
        <tabView:SfTabItem.Content>
            <StackLayout Padding="15" Spacing="10">
                <Label Text="Settings Content" FontSize="16"/>
            </StackLayout>
        </tabView:SfTabItem.Content>
    </tabView:SfTabItem>
</tabView:SfTabView>
```

### Hover Effects

Disable hover background when mouse hovers over a tab:

```xaml
<ContentPage.Resources>
    <x:String x:Key="SfTabViewTheme">CustomTheme</x:String>
    <Color x:Key="SfTabViewHoverBackground">Transparent</Color>
</ContentPage.Resources>

<tabView:SfTabView EnableRippleAnimation="False">
    <!-- Tabs -->
</tabView:SfTabView>
```

---

## Animation and Transitions

### Content Transition Duration

Control animation speed when switching between tabs:

```xaml
<tabView:SfTabView ContentTransitionDuration="500">
    <!-- Tabs -->
</tabView:SfTabView>
```

### Animation Easing

Specify easing function for smooth transitions:

```xaml
<tabView:SfTabView 
    ContentTransitionDuration="500"
    AnimationEasing="{x:Static Easing.BounceOut}">
    <!-- Tabs -->
</tabView:SfTabView>
```

**Available Easing Options:**
- `Easing.Linear` (default)
- `Easing.SinIn`
- `Easing.SinOut`
- `Easing.SinInOut`
- `Easing.CubicIn`
- `Easing.CubicOut`
- `Easing.CubicInOut`
- `Easing.BounceOut`
- `Easing.SpringIn`
- `Easing.SpringOut`

**C# Example:**
```csharp
tabView.ContentTransitionDuration = 500;
tabView.AnimationEasing = Easing.BounceOut;
```

### Enable/Disable Transitions

```xaml
<tabView:SfTabView IsContentTransitionEnabled="True">
    <!-- Tabs -->
</tabView:SfTabView>
```

### Ripple Animation

Enable or disable ripple effect when tapping tab headers:

```xaml
<tabView:SfTabView EnableRippleAnimation="True">
    <!-- Tabs -->
</tabView:SfTabView>
```

---

## Scroll Buttons and Overflow

### Enabling Scroll Buttons

When tabs exceed container width, enable scroll buttons for navigation:

```xaml
<tabView:SfTabView IsScrollButtonEnabled="True">
    <tabView:SfTabItem Header="Tab 1" />
    <tabView:SfTabItem Header="Tab 2" />
    <tabView:SfTabItem Header="Tab 3" />
    <tabView:SfTabItem Header="Tab 4" />
    <tabView:SfTabItem Header="Tab 5" />
</tabView:SfTabView>
```

### Customizing Scroll Buttons

```xaml
<tabView:SfTabView 
    IsScrollButtonEnabled="True"
    ScrollButtonBackground="Violet"
    ScrollButtonColor="Red">
    <!-- Tabs -->
</tabView:SfTabView>
```

**C# Equivalent:**
```csharp
var tabView = new SfTabView
{
    IsScrollButtonEnabled = true,
    ScrollButtonBackground = SolidColorBrush.Violet,
    ScrollButtonColor = Colors.Red
};
```

---

## Performance Optimization

### EnableVirtualization Property

The \EnableVirtualization\ property improves performance when working with large collections of tabs by rendering only visible tab content.

\\\csharp
public class SfTabView
{
    /// <summary>
    /// Gets or sets a value indicating whether virtualization is enabled.
    /// When true, only visible tabs are rendered in memory, improving performance
    /// with large collections.
    /// </summary>
    public bool EnableVirtualization { get; set; }
}
\\\

### When to Enable Virtualization

**Enable (\	rue\) when:**
- You have **more than 20 tabs**
- Tabs contain **heavy content** (images, complex controls, data grids)
- Application is running on **low-memory devices**
- Tab switching experiences **performance lag**

**Disable (\alse\) when:**
- You have **fewer than 10 tabs**
- Tabs contain **light content** (simple text/buttons)
- All tab content needs to be **immediately accessible**
- You need **consistent memory footprint** for all tabs

### XAML Configuration

\\\xaml
<!-- Disable virtualization (default) -->
<tabView:SfTabView EnableVirtualization="False">
    <tabView:SfTabItem Header="Tab 1">
        <Label Text="Content 1" />
    </tabView:SfTabItem>
    <tabView:SfTabItem Header="Tab 2">
        <Label Text="Content 2" />
    </tabView:SfTabItem>
</tabView:SfTabView>

<!-- Enable virtualization for large collections -->
 <tabView:SfTabView EnableVirtualization="True" ItemsSource="{Binding LargeTabCollection}">
     <tabView:SfTabView.HeaderItemTemplate>
         <DataTemplate>
             <Label Padding="5,10,10,10"
                    Text="{Binding Title}" />
         </DataTemplate>
     </tabView:SfTabView.HeaderItemTemplate>
     <tabView:SfTabView.ContentItemTemplate>
         <DataTemplate>
             <Grid RowDefinitions="*,Auto,Auto">
                 <CollectionView ItemsSource="{Binding Items}" />
                 <Label Grid.Row="1" Text="{Binding Description}" />
                 <Button Grid.Row="2" Text="Load More" />
             </Grid>
         </DataTemplate>
     </tabView:SfTabView.ContentItemTemplate>
 </tabView:SfTabView>
\\\

### C# Example - Dynamic Enable/Disable

\\\csharp
// Enable virtualization for large datasets
if (tabItems.Count > 20)
{
    tabView.EnableVirtualization = true;
}

// Disable for small collections
if (tabItems.Count < 10)
{
    tabView.EnableVirtualization = false;
}

// Toggle based on memory pressure
if (DeviceInfo.Current.Idiom == DeviceIdiom.Phone)
{
    tabView.EnableVirtualization = true; // Phones have less memory
}
\\\

### Performance Impact

| Property | Without Virtualization | With Virtualization |
|----------|----------------------|----------------------|
| Memory Usage | All tabs in memory | Only visible tabs |
| Tab Switch Speed | Fast (all loaded) | Slightly slower (render) |
| Initial Load Time | Slower (load all) | Faster (load visible) |
| Ideal For | <10 light tabs | >20 heavy tabs |

### Important Notes

- **First Render:** With virtualization, the first tab renders faster, but switching to hidden tabs may have a slight delay
- **Content Stability:** Ensure tab content isn't modified during virtualization
- **Binding Updates:** Data binding continues to work normally
- **Events:** All events (SelectionChanged, TabItemTapped) fire as expected

---

## Styling Best Practices

### 1. Consistent Visual Hierarchy

Establish clear visual distinction between selected and unselected tabs:
- Use indicator color for selected state
- Adjust text color or brightness for inactive tabs
- Maintain consistent font sizing

### 2. Accessibility Considerations

- Ensure adequate color contrast (WCAG AA minimum)
- Use sufficient font sizes (minimum 14pt for readability)
- Include text labels alongside icons
- Test with accessibility tools

### 3. Performance Tips

- Avoid complex custom layouts in HeaderContent
- Use simple shapes and colors over gradients for mobile
- Limit animations on low-end devices
- Cache image resources for repeated use

### 4. Platform-Specific Styling

Consider platform guidelines:
- **iOS:** Natural, clean styling with subtle animations
- **Android:** Material Design principles with bold colors
- **Desktop:** Compact, efficient use of space

### 5. Theme Integration

For consistent theming across your app:
```csharp
// Use app theme colors
tabView.IndicatorBackground = Application.Current.Resources["PrimaryColor"] as Color;
tabView.TabBarBackground = Application.Current.Resources["BackgroundColor"] as Color;
```

For more advanced styling options and custom templates, refer to the advanced-features.md guide.

---

## Complete API Reference

### Tab Bar Layout & Appearance Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `TabBarHeight` | `double` | 48 | Height of the tab bar header area |
| `TabBarPlacement` | `TabBarPlacement` | Top | Position of tab bar (Top, Bottom, Left, Right) |
| `TabBarBackground` | `Brush` | Light gray | Background color/brush of entire tab bar |
| `TabWidthMode` | `TabWidthMode` | Distributed | How tabs size (Default or SizeToContent) |

### Header Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `TabHeaderPadding` | `Thickness` | "8,0,8,0" | Padding around each tab header content |
| `TabHeaderAlignment` | `TabHeaderAlignment` | Start | Alignment of tabs (Start, Center, End) |
| `HeaderItemSpacing` | `double` | 0 | Spacing between individual header items |
| `HeaderHorizontalTextAlignment` | `TextAlignment` | Start | Horizontal text alignment in headers |
| `HeaderDisplayMode` | `HeaderDisplayMode` | Text | Display mode (Text, Image, ImageWithText) |

### Animation & Transition Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `ContentTransitionDuration` | `double` | 250 | Animation duration in milliseconds when switching tabs |
| `IsContentTransitionEnabled` | `bool` | true | Enable/disable content transition animation |
| `AnimationEasing` | `Easing` | Linear | Easing function for animations (SinOut, CubicOut, BounceOut, etc.) |
| `EnableRippleAnimation` | `bool` | true | Show ripple effect when tapping tab headers |

### Selection Indicator Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `IndicatorPlacement` | `TabIndicatorPlacement` | Bottom | Indicator position (Top, Bottom, Fill) |
| `IndicatorBackground` | `Brush` | Blue | Color/brush of selection indicator |
| `IndicatorWidthMode` | `IndicatorWidthMode` | Fit | Indicator width (Fit to text width or Stretch full tab width) |
| `IndicatorCornerRadius` | `CornerRadius` | 0 | Corner radius for rounded indicator corners |
| `IndicatorStrokeThickness` | `double` | 0 | Border thickness of indicator (0 = no border) |

### Scroll Button Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `IsScrollButtonEnabled` | `bool` | true | Enable scroll buttons when tabs overflow container width |
| `ScrollButtonBackground` | `Brush` | Light gray | Background color of scroll button area |
| `ScrollButtonColor` | `Color` | Black | Icon color of scroll buttons |

### Tab Item Text & Font Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `TextColor` | `Color` (SfTabItem) | Black | Text color of tab header |
| `FontFamily` | `string` (SfTabItem) | System font | Font family for tab text |
| `FontSize` | `double` (SfTabItem) | 14 | Font size for tab text |
| `FontAttributes` | `FontAttributes` (SfTabItem) | None | Font style (Bold, Italic) |

### Tab Item Image Properties

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `ImageSource` | `ImageSource` (SfTabItem) | null | Image displayed in tab header |
| `ImagePosition` | `TabImagePosition` (SfTabItem) | Top | Image position relative to text (Top, Bottom, Left, Right) |
| `ImageTextSpacing` | `double` (SfTabItem) | 5 | Space between image and text |
| `ImageSize` | `Size` (SfTabItem) | 24x24 | Size of image in header |

### Performance & Virtualization

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `EnableVirtualization` | `bool` | false | Enable virtualization for large tab collections (improves performance) |
| `FontAutoScalingEnabled` | `bool` | false | Enable automatic font scaling based on system settings |

---

## Enumeration Reference

### HeaderDisplayMode
Controls what displays in the header:

```csharp
public enum TabBarDisplayMode
{
    Default,           // Text and image based on Header and ImageSource
    Text,              // Only Header text (ignores ImageSource)
    Image              // Only image from ImageSource (ignores Header text)
}
```

### TabBarPlacement
Position of tab bar relative to content:

```csharp
public enum TabBarPlacement
{
    Top,               // Tab bar above content
    Bottom,            // Tab bar below content
}
```

### TabWidthMode
How tab width is calculated:

```csharp
public enum TabWidthMode
{
    Default,           // Tabs distributed evenly across available width
    SizeToContent      // Tabs sized to fit their content (may require scrolling)
}
```

### TabImagePosition
Image placement relative to text:

```csharp
public enum TabImagePosition
{
    Top,               // Image above text
    Bottom,            // Image below text
    Left,              // Image left of text
    Right              // Image right of text
}
```

### TabIndicatorPlacement
Selection indicator position:

```csharp
public enum TabIndicatorPlacement
{
    Top,               // Indicator above tab content area
    Bottom,            // Indicator below tab content area
    Fill               // Indicator fills entire selected tab
}
```

### IndicatorWidthMode
How indicator width is determined:

```csharp
public enum IndicatorWidthMode
{
    Fit,               // Indicator sized to fit header text width
    Stretch            // Indicator spans full tab width
}
```

### TabHeaderAlignment
Tab alignment within header:

```csharp
public enum TabHeaderAlignment
{
    Start,             // Align to start (left in LTR layouts)
    Center,            // Center in header area
    End                // Align to end (right in LTR layouts)
}
```
