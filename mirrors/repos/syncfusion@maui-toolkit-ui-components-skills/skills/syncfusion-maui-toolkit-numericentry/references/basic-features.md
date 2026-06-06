# Basic Features and Configuration

This guide covers the appearance, interaction, and customization features of SfNumericEntry that enhance user experience and visual design.

## Table of Contents
1. [Placeholder Configuration](#placeholder-configuration)
2. [Clear Button Customization](#clear-button-customization)
3. [Value Change Modes](#value-change-modes)
4. [Border and Stroke Styling](#border-and-stroke-styling)
5. [Text Alignment](#text-alignment)
6. [Font Customization](#font-customization)
7. [Keyboard and Return Configuration](#keyboard-and-return-configuration)
8. [Text Selection and Cursor Control](#text-selection-and-cursor-control)

---

## Placeholder Configuration

Placeholder text guides users on what to enter and appears when the control's value is null.

### Setting Placeholder Text

The `Placeholder` property displays instructional text when the value is null and `AllowNull="True"`.

**XAML:**
```xml
<editors:SfNumericEntry Placeholder="Enter input here..."
                        AllowNull="True" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Placeholder = "Enter input here...";
sfNumericEntry.AllowNull = true;
sfNumericEntry.HorizontalOptions = LayoutOptions.Center;
sfNumericEntry.VerticalOptions = LayoutOptions.Center;
```

**Key Points:**
- Placeholder only shows when `Value` is `null`
- If `AllowNull="False"`, placeholder never appears (control always has a value)
- Default value is `string.Empty` (no placeholder)

**When to use placeholders:**
- Provide format examples ("$0.00", "Enter age", "0-100")
- Give usage hints ("Optional", "Required")
- Show units or measurement types ("Weight in kg", "Price in USD")

### Customizing Placeholder Color

The `PlaceholderColor` property controls the color of placeholder text.

**XAML:**
```xml
<editors:SfNumericEntry Placeholder="Enter input here..."
                        PlaceholderColor="Gray"
                        AllowNull="True" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Placeholder = "Enter input here...";
sfNumericEntry.PlaceholderColor = Colors.Gray;
```

**Best practices:**
- Use muted colors (gray, light colors) to distinguish from actual values
- Ensure sufficient contrast for accessibility
- Match your app's design system

### Practical Examples

```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <!-- Currency placeholder -->
    <editors:SfNumericEntry Placeholder="$0.00"
                            PlaceholderColor="DarkGray"
                            CustomFormat="C2"
                            AllowNull="True" />
    
    <!-- Percentage placeholder -->
    <editors:SfNumericEntry Placeholder="Enter discount (0-100%)"
                            PlaceholderColor="Gray"
                            CustomFormat="P0"
                            AllowNull="True" />
    
    <!-- Measurement placeholder -->
    <editors:SfNumericEntry Placeholder="Enter weight in kg"
                            PlaceholderColor="LightGray"
                            CustomFormat="N2"
                            AllowNull="True" />
    
</VerticalStackLayout>
```

---

## Clear Button Customization

The clear button allows users to quickly reset the input value.

### Showing and Hiding the Clear Button

The `ShowClearButton` property controls visibility. By default, it's `True`.

**XAML:**
```xml
<editors:SfNumericEntry ShowClearButton="True"
                        IsEditable="True"
                        Value="10" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 10;
sfNumericEntry.ShowClearButton = true;
sfNumericEntry.IsEditable = true;
```

**Important conditions:**
- Clear button appears **only when control is focused**
- Clear button appears **only when IsEditable="True"**
- If either condition is false, button is hidden

**When IsEditable="True":**
The clear button is visible when the control has focus.

**When IsEditable="False":**
The clear button is always hidden (read-only mode).

### Customizing Clear Button Color

The `ClearButtonColor` property changes the clear button icon color.

**XAML:**
```xml
<editors:SfNumericEntry ShowClearButton="True"
                        IsEditable="True"
                        Value="10"
                        ClearButtonColor="Red" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 10;
sfNumericEntry.ShowClearButton = true;
sfNumericEntry.IsEditable = true;
sfNumericEntry.ClearButtonColor = Colors.Red;
```

**Use cases:**
- Match clear button to your brand colors
- Use warning colors (red, orange) to emphasize destructive action
- Adapt to light/dark themes

### Custom Clear Button Icon

The `ClearButtonPath` property allows complete customization with a custom vector path.

**XAML:**
```xml
<editors:SfNumericEntry x:Name="numericEntry"
                        ShowClearButton="True"
                        IsEditable="True"
                        Value="10">
    <editors:SfNumericEntry.ClearButtonPath>
        <Path Data="M1.70711 0.292893C1.31658 -0.097631 0.683417 -0.097631 0.292893 0.292893C-0.097631 0.683417 -0.097631 1.31658 0.292893 1.70711L5.58579 7L0.292893 12.2929C-0.097631 12.6834 -0.097631 13.3166 0.292893 13.7071C0.683417 14.0976 1.31658 14.0976 1.70711 13.7071L7 8.41421L12.2929 13.7071C12.6834 14.0976 13.3166 14.0976 13.7071 13.7071C14.0976 13.3166 14.0976 12.6834 13.7071 12.2929L8.41421 7L13.7071 1.70711C14.0976 1.31658 14.0976 0.683417 13.7071 0.292893C13.3166 -0.097631 12.6834 -0.097631 12.2929 0.292893L7 5.58579L1.70711 0.292893Z"
              Fill="Red"
              Stroke="Red" />
    </editors:SfNumericEntry.ClearButtonPath>
</editors:SfNumericEntry>
```

**C#:**
```csharp
private string _customPath = "M1.70711 0.292893C1.31658 -0.097631 0.683417 -0.097631 0.292893 0.292893C-0.097631 0.683417 -0.097631 1.31658 0.292893 1.70711L5.58579 7L0.292893 12.2929C-0.097631 12.6834 -0.097631 13.3166 0.292893 13.7071C0.683417 14.0976 1.31658 14.0976 1.70711 13.7071L7 8.41421L12.2929 13.7071C12.6834 14.0976 13.3166 14.0976 13.7071 13.7071C14.0976 13.3166 14.0976 12.6834 13.7071 12.2929L8.41421 7L13.7071 1.70711C14.0976 1.31658 14.0976 0.683417 13.7071 0.292893C13.3166 -0.097631 12.6834 -0.097631 12.2929 0.292893L7 5.58579L1.70711 0.292893Z";

var converter = new PathGeometryConverter();
var path = new Path()
{
    Data = (PathGeometry)converter.ConvertFromInvariantString(_customPath),
    Fill = Colors.Red,
    Stroke = Colors.Red
};

SfNumericEntry numericEntry = new SfNumericEntry();
numericEntry.Value = 10;
numericEntry.ShowClearButton = true;
numericEntry.IsEditable = true;
numericEntry.ClearButtonPath = path;
```

**When to customize the icon:**
- Consistent iconography across your app
- Brand-specific design requirements
- Unique UX patterns (trash icon, reset icon, etc.)

---

## Value Change Modes

Value change modes determine when the entered value is validated and when events are fired.

### OnLostFocus Mode (Default)

Value updates when the control loses focus or Enter key is pressed.

**XAML:**
```xml
<editors:SfNumericEntry x:Name="numericEntry"
                        ValueChangeMode="OnLostFocus"
                        Value="50"
                        CustomFormat="C2" />
```

**Characteristics:**
- User types freely without interruption
- Validation happens on blur or Enter key
- ValueChanged event fires on blur/Enter
- Best for forms with multiple fields

**When to use OnLostFocus:**
- Multi-field forms where users tab between inputs
- When format display shouldn't interrupt typing
- When you want to minimize event firing
- Standard data entry scenarios

### OnKeyFocus Mode (Real-Time)

Value updates with every keystroke.

**XAML:**
```xml
<editors:SfNumericEntry x:Name="numericEntry"
                        ValueChangeMode="OnKeyFocus"
                        Value="50"
                        CustomFormat="C2" />
```

**Characteristics:**
- Validates and formats with each key press
- ValueChanged event fires on every keystroke
- Immediate visual feedback
- Best for calculators, live previews

**When to use OnKeyFocus:**
- Real-time calculations (price calculators, tip calculators)
- Live preview scenarios
- When immediate feedback is critical
- Dashboard or monitoring displays

### Comparison Example with Live Display

**XAML:**
```xml
<VerticalStackLayout Spacing="10" VerticalOptions="Center" Padding="20">
    
    <Label Text="Type a value and see the difference:" FontSize="18" FontAttributes="Bold" />
    
    <!-- OnKeyFocus: Updates live -->
    <Label Text="OnKeyFocus Mode (Live Updates):" FontSize="14" />
    <editors:SfNumericEntry x:Name="liveNumericEntry"
                            WidthRequest="200"
                            HeightRequest="40"
                            ValueChangeMode="OnKeyFocus"
                            Value="50"
                            CustomFormat="C2" />
    <HorizontalStackLayout Spacing="5">
        <Label Text="Current Value:" />
        <Label x:Name="liveDisplay"
               Text="{Binding Path=Value, Source={x:Reference liveNumericEntry}, StringFormat='${0:F2}'}"
               TextColor="Green"
               FontAttributes="Bold" />
    </HorizontalStackLayout>
    
    <!-- OnLostFocus: Updates on blur -->
    <Label Text="OnLostFocus Mode (Updates on Blur):" FontSize="14" Margin="0,20,0,0" />
    <editors:SfNumericEntry x:Name="blurNumericEntry"
                            WidthRequest="200"
                            HeightRequest="40"
                            ValueChangeMode="OnLostFocus"
                            Value="50"
                            CustomFormat="C2" />
    <HorizontalStackLayout Spacing="5">
        <Label Text="Current Value:" />
        <Label x:Name="blurDisplay"
               Text="{Binding Path=Value, Source={x:Reference blurNumericEntry}, StringFormat='${0:F2}'}"
               TextColor="Blue"
               FontAttributes="Bold" />
    </HorizontalStackLayout>
    
</VerticalStackLayout>
```

**Try it:** Type in both fields and observe when the bound labels update.

---

## Border and Stroke Styling

Customize the border appearance to match your app's design.

### Changing Border Color (Stroke)

The `Stroke` property controls the border color. Default is `Black`.

**XAML:**
```xml
<editors:SfNumericEntry Stroke="Red"
                        Value="100" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Stroke = Colors.Red;
sfNumericEntry.Value = 100;
```

**Use cases:**
- Match brand colors
- Indicate validation states (green for valid, red for error)
- Differentiate input types visually

### Showing and Hiding the Border

The `ShowBorder` property controls border visibility. Default is `True`.

**XAML:**
```xml
<editors:SfNumericEntry ShowBorder="False"
                        WidthRequest="200"
                        HeightRequest="40"
                        Value="100" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.WidthRequest = 200;
sfNumericEntry.HeightRequest = 40;
sfNumericEntry.ShowBorder = false;
```

**When to hide borders:**
- Minimalist UI designs
- Custom layouts where borders conflict with styling
- Read-only displays that shouldn't look like input fields
- When using background colors instead of borders

### Border Styling Examples

```xml
<VerticalStackLayout Spacing="20" Padding="20">
    
    <!-- Default border -->
    <editors:SfNumericEntry Value="100"
                            Placeholder="Default border" />
    
    <!-- Custom color border -->
    <editors:SfNumericEntry Value="100"
                            Stroke="Blue"
                            Placeholder="Blue border" />
    
    <!-- No border -->
    <editors:SfNumericEntry Value="100"
                            ShowBorder="False"
                            BackgroundColor="LightGray"
                            Placeholder="No border, gray background" />
    
    <!-- Success state (green border) -->
    <editors:SfNumericEntry Value="100"
                            Stroke="Green"
                            Placeholder="Valid input" />
    
    <!-- Error state (red border) -->
    <editors:SfNumericEntry Value="100"
                            Stroke="Red"
                            Placeholder="Invalid input" />
    
</VerticalStackLayout>
```

---

## Text Alignment

Control how text is positioned within the NumericEntry control.

### Horizontal Text Alignment

The `HorizontalTextAlignment` property aligns text horizontally. Options: `Start`, `Center`, `End`.

**XAML:**
```xml
<editors:SfNumericEntry WidthRequest="200"
                        HeightRequest="50"
                        Value="12345"
                        HorizontalTextAlignment="Center" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.WidthRequest = 200;
sfNumericEntry.HeightRequest = 50;
sfNumericEntry.Value = 12345;
sfNumericEntry.HorizontalTextAlignment = TextAlignment.Center;
```

**Note:** Dynamic changes to HorizontalTextAlignment may not work on Android platform due to platform limitations.

### Vertical Text Alignment

The `VerticalTextAlignment` property aligns text vertically. Options: `Start`, `Center`, `End`.

**XAML:**
```xml
<editors:SfNumericEntry WidthRequest="200"
                        HeightRequest="50"
                        Value="12345"
                        VerticalTextAlignment="Start" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.WidthRequest = 200;
sfNumericEntry.HeightRequest = 50;
sfNumericEntry.Value = 12345;
sfNumericEntry.VerticalTextAlignment = TextAlignment.Start;
```

### Combined Alignment Example

```xml
<Grid RowDefinitions="Auto,Auto,Auto,Auto"
      ColumnDefinitions="*,*,*"
      Padding="20"
      RowSpacing="15"
      ColumnSpacing="15">
    
    <!-- Headers -->
    <Label Grid.Row="0" Grid.Column="0" Text="Start" HorizontalOptions="Center" FontAttributes="Bold" />
    <Label Grid.Row="0" Grid.Column="1" Text="Center" HorizontalOptions="Center" FontAttributes="Bold" />
    <Label Grid.Row="0" Grid.Column="2" Text="End" HorizontalOptions="Center" FontAttributes="Bold" />
    
    <!-- Top alignment -->
    <editors:SfNumericEntry Grid.Row="1" Grid.Column="0"
                            Value="123"
                            HorizontalTextAlignment="Start"
                            VerticalTextAlignment="Start"
                            HeightRequest="60" />
    <editors:SfNumericEntry Grid.Row="1" Grid.Column="1"
                            Value="123"
                            HorizontalTextAlignment="Center"
                            VerticalTextAlignment="Start"
                            HeightRequest="60" />
    <editors:SfNumericEntry Grid.Row="1" Grid.Column="2"
                            Value="123"
                            HorizontalTextAlignment="End"
                            VerticalTextAlignment="Start"
                            HeightRequest="60" />
    
    <!-- Center alignment -->
    <editors:SfNumericEntry Grid.Row="2" Grid.Column="0"
                            Value="123"
                            HorizontalTextAlignment="Start"
                            VerticalTextAlignment="Center"
                            HeightRequest="60" />
    <editors:SfNumericEntry Grid.Row="2" Grid.Column="1"
                            Value="123"
                            HorizontalTextAlignment="Center"
                            VerticalTextAlignment="Center"
                            HeightRequest="60" />
    <editors:SfNumericEntry Grid.Row="2" Grid.Column="2"
                            Value="123"
                            HorizontalTextAlignment="End"
                            VerticalTextAlignment="Center"
                            HeightRequest="60" />
    
    <!-- Bottom alignment -->
    <editors:SfNumericEntry Grid.Row="3" Grid.Column="0"
                            Value="123"
                            HorizontalTextAlignment="Start"
                            VerticalTextAlignment="End"
                            HeightRequest="60" />
    <editors:SfNumericEntry Grid.Row="3" Grid.Column="1"
                            Value="123"
                            HorizontalTextAlignment="Center"
                            VerticalTextAlignment="End"
                            HeightRequest="60" />
    <editors:SfNumericEntry Grid.Row="3" Grid.Column="2"
                            Value="123"
                            HorizontalTextAlignment="End"
                            VerticalTextAlignment="End"
                            HeightRequest="60" />
    
</Grid>
```

**When to use specific alignments:**
- **Center:** Calculator displays, prominent single values
- **End (Right):** Currency and financial data (traditional alignment)
- **Start (Left):** Form fields, general numeric input

---

## Font Customization

Personalize the appearance of the numeric text with font properties.

### Text Color

The `TextColor` property sets the color of the value text.

**XAML:**
```xml
<editors:SfNumericEntry Value="100"
                        TextColor="Blue" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 100;
sfNumericEntry.TextColor = Colors.Blue;
```

### Font Size

The `FontSize` property controls text size.

**XAML:**
```xml
<editors:SfNumericEntry Value="100"
                        FontSize="20" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 100;
sfNumericEntry.FontSize = 20;
```

### Font Family

The `FontFamily` property sets the font typeface.

**XAML:**
```xml
<editors:SfNumericEntry Value="100"
                        FontFamily="OpenSansRegular" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 100;
sfNumericEntry.FontFamily = "OpenSansRegular";
```

**Note:** Ensure the font is registered in MauiProgram.cs.

### Font Attributes

The `FontAttributes` property controls font style. Options: `Bold`, `Italic`, `None`.

**XAML:**
```xml
<editors:SfNumericEntry Value="100"
                        FontAttributes="Bold" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 100;
sfNumericEntry.FontAttributes = FontAttributes.Bold;
```

### Complete Font Customization Example

```xml
<VerticalStackLayout Spacing="20" Padding="20">
    
    <!-- Default styling -->
    <Label Text="Default:" />
    <editors:SfNumericEntry Value="12345" />
    
    <!-- Large, bold, blue -->
    <Label Text="Large Bold Blue:" />
    <editors:SfNumericEntry Value="12345"
                            FontSize="24"
                            FontAttributes="Bold"
                            TextColor="Blue" />
    
    <!-- Custom font, italic -->
    <Label Text="Custom Font Italic:" />
    <editors:SfNumericEntry Value="12345"
                            FontFamily="OpenSansSemibold"
                            FontAttributes="Italic"
                            FontSize="18" />
    
    <!-- Subtle, small, gray (read-only display) -->
    <Label Text="Subtle Display:" />
    <editors:SfNumericEntry Value="12345"
                            FontSize="14"
                            TextColor="Gray"
                            IsEditable="False"
                            ShowBorder="False" />
    
    <!-- Prominent total display -->
    <Label Text="Total Display:" />
    <editors:SfNumericEntry Value="1234567.89"
                            CustomFormat="C2"
                            FontSize="28"
                            FontAttributes="Bold"
                            TextColor="Green"
                            HorizontalTextAlignment="Center"
                            IsEditable="False"
                            ShowClearButton="False" />
    
</VerticalStackLayout>
```

---

## Keyboard and Return Configuration

Configure keyboard behavior for better form flow and user experience.

### Return Type

The `ReturnType` property specifies the keyboard's action button label.

**Options:** `Default`, `Done`, `Go`, `Next`, `Search`, `Send`

**XAML:**
```xml
<editors:SfNumericEntry x:Name="numericEntry"
                        ReturnType="Next"
                        WidthRequest="200" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.ReturnType = ReturnType.Next;
```

**When to use each type:**
- **Next:** Multi-step forms, move to next field
- **Done:** Last field in form, dismiss keyboard
- **Go:** Submit search or navigation
- **Send:** Message or email submission
- **Search:** Search forms

### Return Command

Execute a command when the return key is pressed.

**ViewModel:**
```csharp
public class CommandDemoViewModel
{
    public ICommand AlertCommand => new Command<string>(OnAlertCommandExecuted);

    private async void OnAlertCommandExecuted(string parameter)
    {
        await Application.Current.MainPage.DisplayAlert("Alert", parameter, "OK");
    }
}
```

**XAML:**
```xml
<ContentPage.BindingContext>
    <local:CommandDemoViewModel/>
</ContentPage.BindingContext>

<editors:SfNumericEntry x:Name="numericEntry"
                        ReturnCommand="{Binding AlertCommand}"
                        ReturnCommandParameter="Return key is pressed" />
```

**C#:**
```csharp
var viewModel = new CommandDemoViewModel();
SfNumericEntry numericEntry = new SfNumericEntry();
numericEntry.ReturnCommand = viewModel.AlertCommand;
numericEntry.ReturnCommandParameter = "Return key is pressed";
```

### Multi-Field Form Navigation Example

```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Multi-Field Form" FontSize="20" FontAttributes="Bold" />
    
    <!-- Field 1: Next -->
    <Label Text="Price:" />
    <editors:SfNumericEntry x:Name="priceField"
                            CustomFormat="C2"
                            ReturnType="Next"
                            Completed="OnPriceCompleted" />
    
    <!-- Field 2: Next -->
    <Label Text="Quantity:" />
    <editors:SfNumericEntry x:Name="quantityField"
                            CustomFormat="N0"
                            ReturnType="Next"
                            Completed="OnQuantityCompleted" />
    
    <!-- Field 3: Done (last field) -->
    <Label Text="Discount %:" />
    <editors:SfNumericEntry x:Name="discountField"
                            CustomFormat="P0"
                            ReturnType="Done"
                            Completed="OnDiscountCompleted" />
    
    <Button Text="Submit" Clicked="OnSubmitClicked" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnPriceCompleted(object sender, EventArgs e)
{
    quantityField.Focus();  // Move to next field
}

private void OnQuantityCompleted(object sender, EventArgs e)
{
    discountField.Focus();  // Move to next field
}

private void OnDiscountCompleted(object sender, EventArgs e)
{
    // Last field - dismiss keyboard or submit
    OnSubmitClicked(sender, e);
}

private async void OnSubmitClicked(object sender, EventArgs e)
{
    // Process form submission
    await DisplayAlert("Success", "Form submitted!", "OK");
}
```

---

## Text Selection and Cursor Control

Programmatically control cursor position and text selection.

### Cursor Position

The `CursorPosition` property gets or sets the cursor index. Index starts at 0.

**XAML:**
```xml
<editors:SfNumericEntry Value="12345"
                        CursorPosition="3" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 12345;
sfNumericEntry.CursorPosition = 3;  // Cursor after "123"
```

**Use cases:**
- Set cursor to end of field on focus
- Position cursor for editing specific digits
- Implement custom navigation logic

### Selection Length

The `SelectionLength` property selects a portion of the text.

**XAML:**
```xml
<editors:SfNumericEntry Value="12345"
                        CursorPosition="1"
                        SelectionLength="3" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 12345;
sfNumericEntry.CursorPosition = 1;     // Start at position 1
sfNumericEntry.SelectionLength = 3;    // Select 3 characters (234)
```

**Result:** Characters at positions 1-3 ("234") are selected.

### Practical Selection Example

**Select all text on focus:**

```xml
<editors:SfNumericEntry x:Name="numericEntry"
                        Value="12345"
                        Focused="OnNumericEntryFocused" />
```

**Code-Behind:**
```csharp
private void OnNumericEntryFocused(object sender, FocusEventArgs e)
{
    var entry = sender as SfNumericEntry;
    if (entry != null && entry.Value.HasValue)
    {
        // Select all text
        string valueText = entry.Value.Value.ToString();
        entry.CursorPosition = 0;
        entry.SelectionLength = valueText.Length;
    }
}
```

**Why this is useful:**
- Users can immediately replace the value by typing
- Common pattern in calculator and numeric entry apps
- Improves data entry speed

---

## Complete Customization Example

Here's a comprehensive example combining multiple basic features:

**XAML:**
```xml
<ScrollView>
    <VerticalStackLayout Spacing="25" Padding="30">
        
        <Label Text="Customized NumericEntry Examples"
               FontSize="24"
               FontAttributes="Bold"
               HorizontalOptions="Center"
               Margin="0,0,0,20" />
        
        <!-- Example 1: Colorful currency input -->
        <Label Text="Colorful Currency Input:" FontSize="16" />
        <editors:SfNumericEntry Value="1234.56"
                                CustomFormat="C2"
                                Placeholder="$0.00"
                                PlaceholderColor="LightGray"
                                TextColor="Green"
                                FontSize="20"
                                FontAttributes="Bold"
                                Stroke="Green"
                                ClearButtonColor="Green"
                                HorizontalTextAlignment="End"
                                ValueChangeMode="OnKeyFocus" />
        
        <!-- Example 2: Minimalist no-border input -->
        <Label Text="Minimalist No-Border:" FontSize="16" />
        <editors:SfNumericEntry Value="42"
                                CustomFormat="N0"
                                ShowBorder="False"
                                BackgroundColor="WhiteSmoke"
                                TextColor="DarkSlateGray"
                                FontSize="18"
                                HorizontalTextAlignment="Center"
                                Placeholder="Enter number" />
        
        <!-- Example 3: Error state input -->
        <Label Text="Error State (Red Border):" FontSize="16" />
        <editors:SfNumericEntry Value="999"
                                Minimum="0"
                                Maximum="100"
                                Stroke="Red"
                                ClearButtonColor="Red"
                                TextColor="Red"
                                Placeholder="Value must be 0-100"
                                PlaceholderColor="IndianRed" />
        
        <!-- Example 4: Large display field -->
        <Label Text="Large Display Field:" FontSize="16" />
        <editors:SfNumericEntry Value="987654.32"
                                CustomFormat="C2"
                                FontSize="32"
                                FontAttributes="Bold"
                                TextColor="DarkBlue"
                                HorizontalTextAlignment="Center"
                                VerticalTextAlignment="Center"
                                HeightRequest="80"
                                IsEditable="False"
                                ShowClearButton="False"
                                ShowBorder="True"
                                Stroke="DarkBlue" />
        
        <!-- Example 5: Form-style with Next button -->
        <Label Text="Form Field with Next:" FontSize="16" />
        <editors:SfNumericEntry Value="25"
                                CustomFormat="N0"
                                Placeholder="Enter age"
                                ReturnType="Next"
                                Minimum="18"
                                Maximum="100"
                                AllowNull="False" />
        
    </VerticalStackLayout>
</ScrollView>
```

**This example demonstrates:**
- Custom colors (text, border, clear button)
- Various font sizes and attributes
- Border show/hide
- Text alignment options
- Placeholder customization
- Value change modes
- Keyboard return types
- Read-only display styling

---

## Best Practices

1. **Use descriptive placeholders** that show format or expected range
2. **Match placeholder color** to your design system (typically gray tones)
3. **Choose ValueChangeMode** based on use case (OnKeyFocus for calculators, OnLostFocus for forms)
4. **Hide clear button** on read-only displays (IsEditable="False")
5. **Use consistent border colors** for validation states (green=valid, red=error)
6. **Set appropriate text alignment** (right-align for currency/financial data)
7. **Consider font size accessibility** (minimum 14-16 for readability)
8. **Use ReturnType="Next"** in multi-field forms for better UX
9. **Select all text on focus** for quick value replacement in appropriate scenarios
10. **Test alignment on Android** as HorizontalTextAlignment has platform limitations

---