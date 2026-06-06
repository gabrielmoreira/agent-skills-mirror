# Up/Down Button Control

## Table of Contents
- [SmallChange and LargeChange](#smallchange-and-largechange)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Mouse Scroll Wheel](#mouse-scroll-wheel)
- [Button Placement Modes](#button-placement-modes)
- [Button Alignment](#button-alignment)
- [Button Customization](#button-customization)
- [Auto-Reverse Behavior](#auto-reverse-behavior)

## SmallChange and LargeChange

Control the increment/decrement amounts for different input methods.

### SmallChange Property

Used by:
- **Arrow keys** (↑ and ↓)
- **Mouse scroll wheel**
- **Up/Down button clicks**

Default: `1`

```xaml
<editors:SfNumericUpDown 
    Value="0"
    SmallChange="5"
    Placeholder="Arrow keys increment by 5" />
```

**Behavior:**
- User presses ↑ → Value increases by 5
- User presses ↓ → Value decreases by 5
- User scrolls wheel ↑ → Value increases by 5

### LargeChange Property

Used by:
- **Page Up key** (PageUp)
- **Page Down key** (PageDown)

Default: `10`

```xaml
<editors:SfNumericUpDown 
    Value="0"
    SmallChange="1"
    LargeChange="10"
    Placeholder="Page Up/Down by 10, Arrows by 1" />
```

**Behavior:**
- User presses PageUp → Value increases by 10
- User presses PageDown → Value decreases by 10

### Practical Configuration Examples

**Example 1: Currency with Cents**
```xaml
<editors:SfNumericUpDown 
    Value="0"
    CustomFormat="C2"
    SmallChange="0.01"
    LargeChange="1.00"
    Placeholder="Adjust with arrows (±$0.01) or Page Up/Down (±$1.00)" />
```

**Example 2: Percentage Input**
```xaml
<editors:SfNumericUpDown 
    Value="50"
    Minimum="0"
    Maximum="100"
    CustomFormat="P0"
    SmallChange="1"
    LargeChange="5"
    Placeholder="1% per arrow, 5% per Page Up/Down" />
```

**Example 3: Temperature Control**
```xaml
<editors:SfNumericUpDown 
    Value="20"
    Minimum="-50"
    Maximum="50"
    CustomFormat="N1"
    SmallChange="0.5"
    LargeChange="5.0"
    Placeholder="0.5°C per arrow, 5.0°C per Page Up/Down" />
```

**Example 4: Rating (1-5)**
```xaml
<editors:SfNumericUpDown 
    Value="3"
    Minimum="1"
    Maximum="5"
    SmallChange="1"
    LargeChange="1"
    IsEditable="False"
    Placeholder="1-5 rating" />
```

## Keyboard Shortcuts

Complete keyboard navigation for NumericUpDown:

| Key | Action | Change Amount |
|-----|--------|---------------|
| ↑ Arrow Up | Increase value | `SmallChange` |
| ↓ Arrow Down | Decrease value | `SmallChange` |
| PageUp | Increase value | `LargeChange` |
| PageDown | Decrease value | `LargeChange` |
| Enter | Submit (trigger Completed event) | None |
| Tab | Move to next control | None |
| Shift+Tab | Move to previous control | None |

### Keyboard Behavior

```xaml
<VerticalStackLayout Spacing="10">
    <Label Text="Use keyboard to adjust:" FontAttributes="Bold" />
    
    <!-- Primary input -->
    <editors:SfNumericUpDown 
        x:Name="priceInput"
        Value="100"
        CustomFormat="C2"
        SmallChange="1"
        LargeChange="10"
        Placeholder="Price"
        ReturnType="Next" />
    
    <!-- Secondary input -->
    <editors:SfNumericUpDown 
        Value="2"
        SmallChange="1"
        Placeholder="Quantity"
        ReturnType="Done" />
</VerticalStackLayout>
```

**User workflow:**
1. Click on first field → Focus
2. Press ↑ five times → Value: 105
3. Press PageDown three times → Value: 75
4. Press Tab → Move to second field
5. Press Enter → Submit/complete

## Mouse Scroll Wheel

NumericUpDown supports mouse scroll wheel for value adjustment:

### Scroll Behavior

- **Scroll up/forward** → Increase by `SmallChange`
- **Scroll down/backward** → Decrease by `SmallChange`
- Requires control to be **focused**
- Works on Windows and Mac

```xaml
<editors:SfNumericUpDown 
    Value="50"
    SmallChange="5"
    Placeholder="Scroll wheel to adjust by 5" />
```

### Disabling Scroll (Workaround)

While NumericUpDown doesn't have a built-in property to disable scrolling, you can:

1. **Use `IsEditable=False` and limit input methods:**
   ```xaml
   <editors:SfNumericUpDown 
       IsEditable="False"
       SmallChange="5"
       Placeholder="Buttons and arrows only" />
   ```

2. **Only allow button clicks by hiding focus hints:**
   ```csharp
   // Users can still scroll if they know, but UI discourages it
   numericUpDown.Placeholder = "Use up/down buttons";
   ```

## Button Placement Modes

Control the visual orientation of the up/down buttons:

### Inline (Default - Horizontal)

Buttons positioned horizontally on the right side:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    UpDownPlacementMode="Inline" />
```

**Visual:**
```
┌─────────────────────┬─┐
│       50           │↑│↓│
└─────────────────────┴─┘
```

### InlineVertical (Stacked)

Buttons positioned vertically on the right side:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    UpDownPlacementMode="InlineVertical" />
```

**Visual:**
```
┌─────────────────────┬─┐
│       50           │↑│
│                    ├─┤
│                    │↓│
└─────────────────────┴─┘
```

### When to Use Each

| Mode | Best For |
|------|----------|
| **Inline** | Compact space, horizontal layouts, desktop |
| **InlineVertical** | Limited width, mobile layouts, touch |

### Example: Responsive Placement

```csharp
public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        
        // Adjust based on screen size
        if (DeviceDisplay.MainDisplayInfo.Width < 600)
        {
            numericUpDown.UpDownPlacementMode = 
                NumericUpDownPlacementMode.InlineVertical;
        }
        else
        {
            numericUpDown.UpDownPlacementMode = 
                NumericUpDownPlacementMode.Inline;
        }
    }
}
```

## Button Alignment

Control where the up/down buttons are positioned relative to the input field:

### Left Alignment

Buttons on the **left** side:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    UpDownButtonAlignment="Left" />
```

**Visual:**
```
┌─┬─────────────────────┐
│↑│       50           │
│↓├─────────────────────┤
└─┴─────────────────────┘
```

### Right Alignment (Default)

Buttons on the **right** side:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    UpDownButtonAlignment="Right" />
```

**Visual:**
```
┌─────────────────────┬─┐
│       50           │↑│
│                    ├─┤
│                    │↓│
└─────────────────────┴─┘
```

### Both Alignment

Buttons on **both sides**:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    UpDownButtonAlignment="Both" />
```

**Visual:**
```
┌─┬─────────────────────┬─┐
│↑│       50           │↑│
│↓├─────────────────────┤↓│
└─┴─────────────────────┴─┘
```

### Use Cases

| Alignment | Use Case |
|-----------|----------|
| **Left** | Right-to-left layouts, RTL languages |
| **Right** | Standard left-to-right layouts (default) |
| **Both** | Large input field, accessibility needs |

## Button Customization

### Button Color

Change the color of the up/down buttons:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    UpDownButtonColor="Blue" />
```

```csharp
var numericUpDown = new SfNumericUpDown
{
    Value = 50,
    UpDownButtonColor = Colors.Green
};
```

### Button Templates (Custom Appearance)

Replace default buttons with custom templates:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    UpDownPlacementMode="Inline">
    
    <editors:SfNumericUpDown.UpButtonTemplate>
        <DataTemplate>
            <Label 
                Text="🔼" 
                FontSize="20"
                HorizontalTextAlignment="Center" />
        </DataTemplate>
    </editors:SfNumericUpDown.UpButtonTemplate>
    
    <editors:SfNumericUpDown.DownButtonTemplate>
        <DataTemplate>
            <Label 
                Text="🔽" 
                FontSize="20"
                HorizontalTextAlignment="Center" />
        </DataTemplate>
    </editors:SfNumericUpDown.DownButtonTemplate>
</editors:SfNumericUpDown>
```

**C# Equivalent:**
```csharp
var numericUpDown = new SfNumericUpDown { Value = 50 };

// Up button template
var upTemplate = new DataTemplate(() =>
{
    var label = new Label
    {
        Text = "▲",
        FontSize = 20,
        HorizontalTextAlignment = TextAlignment.Center,
        TextColor = Colors.Green
    };
    return label;
});

// Down button template
var downTemplate = new DataTemplate(() =>
{
    var label = new Label
    {
        Text = "▼",
        FontSize = 20,
        HorizontalTextAlignment = TextAlignment.Center,
        TextColor = Colors.Red
    };
    return label;
});

numericUpDown.UpButtonTemplate = upTemplate;
numericUpDown.DownButtonTemplate = downTemplate;
```

### Template Customization Examples

**Example 1: Font Icons**
```xaml
<editors:SfNumericUpDown>
    <editors:SfNumericUpDown.UpButtonTemplate>
        <DataTemplate>
            <Label 
            Text="&#xe71e;" 
            FontFamily="FontIcon"
            FontSize="18"
            TextColor="Blue" />
        </DataTemplate>
    </editors:SfNumericUpDown.UpButtonTemplate>
</editors:SfNumericUpDown>
```

**Example 2: Images**
```xaml
<editors:SfNumericUpDown>
    <editors:SfNumericUpDown.UpButtonTemplate>
        <DataTemplate>
            <Image 
        Source="arrow_up.png"
        Aspect="AspectFit"
        WidthRequest="24" />
        </DataTemplate>
    </editors:SfNumericUpDown.UpButtonTemplate>
</editors:SfNumericUpDown>
```

**Limitation:** Button templates only work with **Inline** placement mode.

## Auto-Reverse Behavior

Enable automatic direction reversal at min/max boundaries:

### Without Auto-Reverse (Default)

When reaching min/max, further clicks have no effect:

```xaml
<editors:SfNumericUpDown 
    Value="5"
    Minimum="1"
    Maximum="10"
    AutoReverse="False" />
```

**Behavior:**
- Click ↑ repeatedly: 5 → 6 → 7 → 8 → 9 → 10 → **stops**
- Click ↓ repeatedly: 10 → 9 → 8 → 7 → 6 → 5 → 1 → **stops**

### With Auto-Reverse (Enabled)

When reaching min/max, direction automatically reverses:

```xaml
<editors:SfNumericUpDown 
    Value="5"
    Minimum="1"
    Maximum="10"
    AutoReverse="True" />
```

**Behavior:**
- Click ↑: 5 → 6 → 7 → 8 → 9 → 10 → **auto-reverses** → 9 → 8...
- Click ↓: 5 → 4 → 3 → 2 → 1 → **auto-reverses** → 2 → 3...

### Use Cases

| Mode | Best For |
|------|----------|
| **Auto-Reverse=False** | Normal form input, quantity selection |
| **Auto-Reverse=True** | Carousel/slider-like behavior, continuous loops |

### Example: Rating Carousel

```xaml
<editors:SfNumericUpDown 
    Value="1"
    Minimum="1"
    Maximum="5"
    AutoReverse="True"
    SmallChange="1"
    IsEditable="False"
    Placeholder="Rating cycles 1→5→1..." />
```

**Interaction:**
```
User clicks ↑: 1 → 2 → 3 → 4 → 5 → 1 → 2...
User clicks ↓: 1 → 5 → 4 → 3 → 2 → 1 → 5...
```

---
