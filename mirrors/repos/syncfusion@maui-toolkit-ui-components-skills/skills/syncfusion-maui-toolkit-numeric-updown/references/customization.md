# Customization & UI Features

## Table of Contents
- [Border and Stroke Customization](#border-and-stroke-customization)
- [Text Appearance](#text-appearance)
- [Clear Button Customization](#clear-button-customization)
- [Cursor and Selection](#cursor-and-selection)
- [Keyboard Configuration](#keyboard-configuration)
- [Advanced Styling Patterns](#advanced-styling-patterns)
- [Accessibility Considerations](#accessibility-considerations)
- [Common Issues & Solutions](#common-issues--solutions)

## Border and Stroke Customization

### Border Visibility

Control whether the control displays a border:

```xaml
<editors:SfNumericUpDown 
    ShowBorder="True"
    Value="50" />
```

| Property | Default | Effect |
|----------|---------|--------|
| `ShowBorder=True` | Default | Display border around control |
| `ShowBorder=False` | - | No border (flat appearance) |

### Border Color (Stroke)

Change the border color:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    ShowBorder="True"
    Stroke="Red" />
```

```csharp
var numericUpDown = new SfNumericUpDown
{
    Value = 50,
    ShowBorder = true,
    Stroke = Colors.Red
};
```

### Default Stroke Color

- **Default:** `Colors.Black`
- Applied only when `ShowBorder=True`

### Practical Examples

**Example 1: Error State Border**
```csharp
private void HighlightError(SfNumericUpDown control)
{
    control.ShowBorder = true;
    control.Stroke = Colors.Red;
}

private void ClearError(SfNumericUpDown control)
{
    control.ShowBorder = true;
    control.Stroke = Colors.Gray;
}
```

**Example 2: Focus-Based Styling**
```csharp
private void OnFocused(object sender, FocusEventArgs e)
{
    var numericUpDown = (SfNumericUpDown)sender;
    numericUpDown.Stroke = Colors.Blue;
}

private void OnUnfocused(object sender, FocusEventArgs e)
{
    var numericUpDown = (SfNumericUpDown)sender;
    numericUpDown.Stroke = Colors.Gray;
}
```

**Example 3: Validation Feedback**
```xaml
<Frame BorderColor="Gray" Padding="10">
    <editors:SfNumericUpDown 
        x:Name="priceInput"
        Value="0"
        ShowBorder="True"
        Stroke="Gray"
        ValueChanged="OnPriceChanged" />
</Frame>
```

```csharp
private void OnPriceChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue && e.NewValue.Value > 10000)
    {
        priceInput.Stroke = Colors.Red;  // Invalid
    }
    else if (e.NewValue.HasValue)
    {
        priceInput.Stroke = Colors.Green;  // Valid
    }
}
```

## Text Appearance

### Text Color

Customize the color of the entered numeric value:

```xaml
<editors:SfNumericUpDown 
    Value="100"
    TextColor="Blue" />
```

**Default:** `Colors.Black`

### Font Family, Size, and Attributes

Control text typography:

```xaml
<editors:SfNumericUpDown 
    Value="100"
    FontFamily="OpenSansRegular"
    FontSize="18"
    FontAttributes="Bold" />
```

```csharp
var numericUpDown = new SfNumericUpDown
{
    Value = 100,
    FontFamily = "OpenSansRegular",
    FontSize = 18,
    FontAttributes = FontAttributes.Bold | FontAttributes.Italic
};
```

### Font Properties

| Property | Values | Default |
|----------|--------|---------|
| `FontFamily` | Font name string | System default |
| `FontSize` | Double (e.g., 14, 18, 24) | 14 |
| `FontAttributes` | Bold, Italic, None | None |

### Text Alignment

Position text horizontally and vertically within the field:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    HorizontalTextAlignment="Center"
    VerticalTextAlignment="Center" />
```

**Horizontal Options:**
- `Start` (Left) - Default
- `Center` - Center
- `End` (Right)

**Vertical Options:**
- `Start` (Top)
- `Center` - Middle
- `End` (Bottom)

### Practical Examples

**Example 1: Currency Input**
```xaml
<editors:SfNumericUpDown 
    Value="0"
    CustomFormat="C2"
    TextColor="Green"
    FontSize="20"
    FontAttributes="Bold"
    HorizontalTextAlignment="Center" />
```

**Example 2: Percentage Display**
```xaml
<editors:SfNumericUpDown 
    Value="50"
    CustomFormat="P1"
    TextColor="DodgerBlue"
    FontSize="24"
    FontAttributes="Bold"
    HorizontalTextAlignment="Center" />
```

**Example 3: Conditional Text Color**
```csharp
private void UpdateTextColor(SfNumericUpDown control, double threshold)
{
    if (control.Value.HasValue)
    {
        control.TextColor = control.Value.Value > threshold 
            ? Colors.Red      // Above threshold
            : Colors.Green;   // Below threshold
    }
}
```

**Platform Note:** Dynamic changes to `HorizontalTextAlignment` may not work correctly on Android.

## Clear Button Customization

### Clear Button Visibility

Show or hide the X button that clears the field:

```xaml
<editors:SfNumericUpDown 
    ShowClearButton="True"
    IsEditable="True"
    Value="10" />
```

**Important:** Clear button only appears when:
- `ShowClearButton=True` AND
- `IsEditable=True` AND
- **Control is focused**

**Default:** `True`

### Clear Button Color

Change the color of the clear button:

```xaml
<editors:SfNumericUpDown 
    ShowClearButton="True"
    IsEditable="True"
    Value="10"
    ClearButtonColor="Red" />
```

```csharp
var numericUpDown = new SfNumericUpDown
{
    Value = 10,
    ShowClearButton = true,
    IsEditable = true,
    ClearButtonColor = Colors.Red
};
```

**Default:** `Colors.Black`

### Custom Clear Button Appearance

Replace the default X button with a custom design:

```xaml
<editors:SfNumericUpDown 
    ShowClearButton="True"
    IsEditable="True"
    Value="10">
    
    <editors:SfNumericUpDown.ClearButtonPath>
        <Path Data="M1.70711 0.292893C1.31658 -0.097631 0.683417 -0.097631 0.292893 0.292893C-0.097631 0.683417 -0.097631 1.31658 0.292893 1.70711L5.58579 7L0.292893 12.2929C-0.097631 12.6834 -0.097631 13.3166 0.292893 13.7071C0.683417 14.0976 1.31658 14.0976 1.70711 13.7071L7 8.41421L12.2929 13.7071C12.6834 14.0976 13.3166 14.0976 13.7071 13.7071C14.0976 13.3166 14.0976 12.6834 13.7071 12.2929L8.41421 7L13.7071 1.70711C14.0976 1.31658 14.0976 0.683417 13.7071 0.292893C13.3166 -0.097631 12.6834 -0.097631 12.2929 0.292893L7 5.58579L1.70711 0.292893Z" 
              Fill="Red" 
              Stroke="Red" />
    </editors:SfNumericUpDown.ClearButtonPath>
</editors:SfNumericUpDown>
```

### Practical Examples

**Example 1: Large Input with Prominent Clear Button**
```xaml
<editors:SfNumericUpDown 
    Value="1000"
    CustomFormat="C2"
    WidthRequest="200"
    HeightRequest="50"
    FontSize="20"
    ShowClearButton="True"
    ClearButtonColor="Blue" />
```

**Example 2: Minimal UI (No Clear Button)**
```xaml
<editors:SfNumericUpDown 
    Value="50"
    ShowClearButton="False"
    IsEditable="True" />
```

## Cursor and Selection

### Cursor Position

Get or set the cursor position within the input field:

```xaml
<editors:SfNumericUpDown 
    Value="12345"
    CursorPosition="2" />
```

**Result:** Cursor positioned at index 2 (after "12")

```csharp
var numericUpDown = new SfNumericUpDown { Value = 12345 };

// Move cursor to end
numericUpDown.CursorPosition = numericUpDown.Value.ToString().Length;
```

**Default:** 0 (start of field)

### Selection Length

Select text by specifying position and length:

```xaml
<editors:SfNumericUpDown 
    Value="12345"
    CursorPosition="1"
    SelectionLength="3" />
```

**Result:** Text "234" is selected (starting at position 1, length 3)

```csharp
var numericUpDown = new SfNumericUpDown { Value = 12345 };

// Select all text
string valueStr = numericUpDown.Value.ToString();
numericUpDown.CursorPosition = 0;
numericUpDown.SelectionLength = valueStr.Length;
```

**Default:** 0 (no selection)

## Keyboard Configuration

### Return Key Type

Control the label shown on the keyboard's return/enter button:

```xaml
<!-- Default Enter button -->
<editors:SfNumericUpDown ReturnType="Default" />

<!-- "Done" button (signals completion) -->
<editors:SfNumericUpDown ReturnType="Done" />

<!-- "Go" button (for search/navigation) -->
<editors:SfNumericUpDown ReturnType="Go" />

<!-- "Next" button (for form navigation) -->
<editors:SfNumericUpDown ReturnType="Next" />

<!-- "Send" button (for messages) -->
<editors:SfNumericUpDown ReturnType="Send" />

<!-- "Search" button -->
<editors:SfNumericUpDown ReturnType="Search" />
```

### Keyboard Appearance Across Platforms

| Platform | Default | Behavior |
|----------|---------|----------|
| **iOS** | Varies | Shows appropriate label on return key |
| **Android** | Varies | Keyboard style varies by device |
| **UWP** | Varies | Standard keyboard |
| **macOS** | Default | Standard keyboard |

### Practical Examples

**Example 1: Multi-Field Form Navigation**
```xaml
<VerticalStackLayout Spacing="10">
    <!-- First field -->
    <editors:SfNumericUpDown 
        Placeholder="Quantity"
        ReturnType="Next"
        Completed="OnQuantityCompleted" />
    
    <!-- Middle field -->
    <editors:SfNumericUpDown 
        Placeholder="Unit Price"
        ReturnType="Next"
        Completed="OnPriceCompleted" />
    
    <!-- Last field -->
    <editors:SfNumericUpDown 
        Placeholder="Discount"
        ReturnType="Done"
        Completed="OnDiscountCompleted" />
</VerticalStackLayout>
```

**Example 2: Search Interface**
```xaml
<editors:SfNumericUpDown 
    Placeholder="Enter product ID"
    ReturnType="Go"
    Completed="OnSearchRequested" />
```

## Advanced Styling Patterns

### Pattern 1: Frame-Based Input

Combine NumericUpDown with Frame for enhanced styling:

```xaml
<Frame BorderColor="LightGray" 
        CornerRadius="8"
        HasShadow="True"
        Padding="10">
    
    <VerticalStackLayout Spacing="5">
        <Label Text="Amount" FontAttributes="Bold" />
        
        <editors:SfNumericUpDown 
            Value="0"
            CustomFormat="C2"
            ShowBorder="False"
            TextColor="DodgerBlue"
            FontSize="18" />
        
        <Label x:Name="errorLabel" 
               Text=""
               TextColor="Red"
               FontSize="10" />
    </VerticalStackLayout>
</Frame>
```

### Pattern 2: Labeled Input Group

Group label and input with validation feedback:

```xaml
<VerticalStackLayout Spacing="5">
    <HorizontalStackLayout Spacing="10">
        <Label Text="Age:" 
               WidthRequest="60"
               VerticalTextAlignment="Center" />
        
        <editors:SfNumericUpDown 
            x:Name="ageInput"
            Value="25"
            Minimum="0"
            Maximum="150"
            Flex="1"
            ValueChanged="OnAgeChanged" />
    </HorizontalStackLayout>
    
    <Label x:Name="ageStatus" 
           Text="Valid"
           TextColor="Green"
           FontSize="10" />
</VerticalStackLayout>
```

### Pattern 3: Icon with Input

Combine with icon or symbol:

```xaml
<HorizontalStackLayout Spacing="10" Padding="10">
    <Label Text="💰" 
           FontSize="24"
           VerticalTextAlignment="Center" />
    
    <editors:SfNumericUpDown 
        Value="0"
        CustomFormat="C2"
        Placeholder="Amount"
        Flex="1" />
</HorizontalStackLayout>
```

## Accessibility Considerations

### Screen Reader Support

NumericUpDown integrates with platform accessibility features:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    AutomationProperties.Name="Amount"
    AutomationProperties.HelpText="Enter amount between 0 and 10000" />
```

### Keyboard Navigation

- Full keyboard support (arrows, Page Up/Down, Tab, Enter)
- Tab order follows layout order
- Shift+Tab for reverse navigation

### Color Contrast

Ensure sufficient contrast for readability:

```xaml
<!-- Good contrast -->
<editors:SfNumericUpDown 
    Value="100"
    TextColor="Black"
    BackgroundColor="White" />

<!-- Poor contrast (avoid) -->
<editors:SfNumericUpDown 
    Value="100"
    TextColor="LightGray"
    BackgroundColor="WhiteSmoke" />
```

### Touch Target Size

Ensure adequate tap area on mobile:

```xaml
<!-- Minimum 44x44 points on iOS, 48x48 on Android -->
<editors:SfNumericUpDown 
    HeightRequest="44"
    WidthRequest="150"
    FontSize="16" />
```

## Common Issues & Solutions

### Issue 1: Clear Button Not Showing

**Problem:** Clear button (X) not visible

**Solutions:**
```xaml
<!-- Check all three conditions -->
<editors:SfNumericUpDown 
    ShowClearButton="True"     
    IsEditable="True"          
    Value="10" />              
```

### Issue 2: Text Not Visible

**Problem:** Text appears but is invisible

**Troubleshooting:**
```xaml
<!-- Check contrast -->
<editors:SfNumericUpDown 
    TextColor="Black"
    BackgroundColor="White" />

<!-- Check font size isn't too small -->
<editors:SfNumericUpDown 
    FontSize="14" />   <!-- Minimum recommended -->
```

### Issue 3: Buttons Not Clickable

**Problem:** Up/Down buttons don't respond to clicks

**Solutions:**
```xaml
<!-- Ensure control isn't overlaid -->
<editors:SfNumericUpDown 
    InputTransparent="False"
    IsEnabled="True" />

<!-- Check UpDownPlacementMode -->
<editors:SfNumericUpDown 
    UpDownPlacementMode="Inline" />
```

### Issue 4: Cursor Position Not Working

**Problem:** CursorPosition property has no effect

**Note:** Not supported on all platforms equally. Use `SelectionLength` for better cross-platform compatibility.

### Issue 5: Text Alignment on Android

**Problem:** `HorizontalTextAlignment` changes don't apply on Android

**Workaround:** Set in code-behind after page initialization:

```csharp
protected override void OnAppearing()
{
    base.OnAppearing();
    
    #if __ANDROID__
        numericInput.HorizontalTextAlignment = TextAlignment.Center;
    #endif
}
```

### Issue 6: Performance with Many Instances

**Problem:** Multiple NumericUpDown controls cause lag

**Solution:**
```csharp
// Disable OnKeyFocus for non-critical fields
numericUpDown.ValueChangeMode = ValueChangeMode.OnLostFocus;

// Use data virtualization for large lists
// Implement cell reuse patterns for collections
```

---
