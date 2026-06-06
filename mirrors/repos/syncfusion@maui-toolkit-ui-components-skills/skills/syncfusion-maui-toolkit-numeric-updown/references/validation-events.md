# Validation & Events

## Table of Contents
- [ValueChangeMode](#valuechangemode)
- [ValueChanged Event](#valuechanged-event)
- [Completed Event](#completed-event)
- [Focused and Unfocused Events](#focused-and-unfocused-events)
- [Return Key Commands](#return-key-commands)
- [Programmatic Focus Control](#programmatic-focus-control)

## ValueChangeMode

Controls **when** the value is validated and updated. Two modes available:

### OnLostFocus (Default)

Value updates **only** when:
- User clicks outside the control
- User presses Enter key
- Tab or Shift+Tab navigation moves focus away

```xaml
<editors:SfNumericUpDown 
    ValueChangeMode="OnLostFocus"
    Placeholder="Enter amount..." />
```

**Behavior:**
```
User types:  "abc123xyz"
Display:     "abc123xyz"  (unchanged during input)
On blur:     "123"        (non-numerics removed, value updates)
```

**Best for:**
- Final form validation
- Bulk data entry (review after complete input)
- Reducing frequent event firing
- Better performance

### OnKeyFocus

Value updates **immediately** with each keystroke:

```xaml
<editors:SfNumericUpDown 
    ValueChangeMode="OnKeyFocus"
    Placeholder="Quantity..." />
```

**Behavior:**
```
User types:  "5"
Display:     "5"          (updated immediately)
User types:  "0"
Display:     "50"         (updated immediately)
```

**Best for:**
- Real-time feedback/calculations
- Currency entry with live preview
- Percentage calculations
- Dynamic UI updates

### Switching Modes Programmatically

```csharp
var numericUpDown = new SfNumericUpDown();

// Start with OnKeyFocus for immediate feedback
numericUpDown.ValueChangeMode = ValueChangeMode.OnKeyFocus;

// Switch to OnLostFocus for batch processing
if (isInBatchMode)
    numericUpDown.ValueChangeMode = ValueChangeMode.OnLostFocus;
```

## ValueChanged Event

Triggered when the `Value` property changes (after validation).

### Event Handler Signature

```csharp
private void OnValueChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    double? oldValue = e.OldValue;  // Previous value
    double? newValue = e.NewValue;  // New value
}
```

### XAML Event Registration

```xaml
<editors:SfNumericUpDown 
    ValueChanged="OnNumericValueChanged" />
```

### C# Event Registration

```csharp
var numericUpDown = new SfNumericUpDown();
numericUpDown.ValueChanged += OnNumericValueChanged;

private void OnNumericValueChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    Console.WriteLine($"Value changed: {e.OldValue} → {e.NewValue}");
}
```

### Practical Examples

**Example 1: Live Calculation**
```csharp
private void OnPriceChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue)
    {
        double price = e.NewValue.Value;
        double tax = price * 0.1;
        double total = price + tax;
        
        priceLabel.Text = price.ToString("C2");
        taxLabel.Text = tax.ToString("C2");
        totalLabel.Text = total.ToString("C2");
    }
}
```

**Example 2: Validation with Visual Feedback**
```csharp
private void OnQuantityChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue == null)
    {
        quantityStatus.Text = "Please enter a quantity";
        quantityStatus.TextColor = Colors.Red;
    }
    else if (e.NewValue < 1)
    {
        quantityStatus.Text = "Quantity must be at least 1";
        quantityStatus.TextColor = Colors.Orange;
    }
    else if (e.NewValue > 1000)
    {
        quantityStatus.Text = "Quantity exceeds maximum (1000)";
        quantityStatus.TextColor = Colors.Red;
    }
    else
    {
        quantityStatus.Text = "Valid quantity";
        quantityStatus.TextColor = Colors.Green;
    }
}
```

**Example 3: Conditional Formatting**
```csharp
private void OnScoreChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue)
    {
        Color scoreColor = e.NewValue.Value >= 70 
            ? Colors.Green 
            : Colors.Red;
        
        scoreIndicator.BackgroundColor = scoreColor;
    }
}
```

**Example 4: Two-Way Calculations**
```csharp
// When price changes, update total
private void OnPriceChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue && quantityField.Value.HasValue)
    {
        double total = e.NewValue.Value * quantityField.Value.Value;
        totalField.Value = total;
    }
}

// When quantity changes, update total
private void OnQuantityChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue && priceField.Value.HasValue)
    {
        double total = priceField.Value.Value * e.NewValue.Value;
        totalField.Value = total;
    }
}
```

## Completed Event

Triggered when user presses the return/enter key, signaling completion of input.

### Event Handler Signature

```csharp
private void OnCompleted(object sender, EventArgs e)
{
    // User pressed Enter - handle completion
}
```

### XAML Event Registration

```xaml
<editors:SfNumericUpDown 
    Completed="OnInputCompleted"
    ReturnType="Done" />
```

### C# Event Registration

```csharp
var numericUpDown = new SfNumericUpDown();
numericUpDown.Completed += OnInputCompleted;

private void OnInputCompleted(object sender, EventArgs e)
{
    Console.WriteLine("User pressed Enter - input complete");
}
```

### Practical Examples

**Example 1: Move to Next Field**
```csharp
private void OnQuantityCompleted(object sender, EventArgs e)
{
    // Move focus to next field
    priceField.Focus();
}
```

**Example 2: Auto-Submit Form**
```csharp
private int _completedFields = 0;

private void OnFieldCompleted(object sender, EventArgs e)
{
    _completedFields++;
    
    if (_completedFields == totalRequiredFields)
    {
        // All fields completed - auto-submit
        SubmitForm();
    }
}
```

**Example 3: Confirm High Value Entry**
```csharp
private async void OnPriceCompleted(object sender, EventArgs e)
{
    if (priceField.Value.HasValue && priceField.Value.Value > 10000)
    {
        bool confirmed = await DisplayAlert(
            "Confirm", 
            $"Price is ${priceField.Value:F2}. Confirm?", 
            "Yes", 
            "No"
        );
        
        if (!confirmed)
        {
            priceField.Value = null;
            priceField.Focus();
        }
    }
}
```

**Example 4: Save Draft on Enter**
```csharp
private void OnDataCompleted(object sender, EventArgs e)
{
    SaveDraft();
    statusLabel.Text = "Draft saved";
}
```

## Focused and Unfocused Events

### Focused Event

Triggered when control receives keyboard focus.

```csharp
private void OnFocused(object sender, FocusEventArgs e)
{
    // Control now has focus
}
```

**Practical uses:**
- Highlight the control
- Show help text
- Select all text
- Change background color

```csharp
private void OnInputFocused(object sender, FocusEventArgs e)
{
    inputFrame.BorderColor = Colors.Blue;
    helpLabel.IsVisible = true;
}
```

### Unfocused Event

Triggered when control loses keyboard focus.

```csharp
private void OnUnfocused(object sender, FocusEventArgs e)
{
    // Control lost focus
}
```

**Practical uses:**
- Final validation
- Formatting confirmation
- Hide help text
- Restore normal appearance

```csharp
private void OnInputUnfocused(object sender, FocusEventArgs e)
{
    inputFrame.BorderColor = Colors.Gray;
    helpLabel.IsVisible = false;
    
    // Validate on blur
    ValidateInput();
}
```

### Complete Focus Pattern

```xaml
<Frame x:Name="inputFrame" BorderColor="Gray" HasShadow="True">
    <VerticalStackLayout Spacing="5">
        <editors:SfNumericUpDown 
            x:Name="amountInput"
            Placeholder="Enter amount"
            Focused="OnFocused"
            Unfocused="OnUnfocused"
            ValueChanged="OnValueChanged" />
        <Label x:Name="helpLabel" IsVisible="False" Text="Focused" TextColor="Blue" FontSize="12" />
    </VerticalStackLayout>
</Frame>
```

```csharp
private void OnFocused(object sender, FocusEventArgs e)
{
    inputFrame.BorderColor = Colors.Blue;
    helpLabel.IsVisible = true;
    helpLabel.Text = $"Enter amount (0-10000)";
}

private void OnUnfocused(object sender, FocusEventArgs e)
{
    inputFrame.BorderColor = Colors.Gray;
    helpLabel.IsVisible = false;
}

private void OnValueChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (amountInput.IsFocused && e.NewValue.HasValue)
    {
        helpLabel.Text = $"Entered: ${e.NewValue:F2}";
    }
}
```

## Return Key Commands

Execute custom commands when the Enter/Return key is pressed.

### ReturnCommand and ReturnCommandParameter

```xaml
<editors:SfNumericUpDown 
    ReturnCommand="{Binding SubmitCommand}"
    ReturnCommandParameter="{Binding Value, Source={x:Reference numericInput}}" />
```

**ViewModel:**
```csharp
public class MyViewModel
{
    public ICommand SubmitCommand => new Command<double?>(OnSubmit);
    
    private void OnSubmit(double? value)
    {
        if (value.HasValue)
        {
            Console.WriteLine($"Submitted: {value}");
        }
    }
}
```

### ReturnType (Keyboard Button)

Control the label on the Return key:

```xaml
<!-- Default Return button -->
<editors:SfNumericUpDown ReturnType="Default" />

<!-- "Done" button -->
<editors:SfNumericUpDown ReturnType="Done" />

<!-- "Go" button (for search) -->
<editors:SfNumericUpDown ReturnType="Go" />

<!-- "Next" button (for form navigation) -->
<editors:SfNumericUpDown ReturnType="Next" />

<!-- "Send" button -->
<editors:SfNumericUpDown ReturnType="Send" />
```

### Return Type Examples

```csharp
// Navigation through form
var quantityField = new SfNumericUpDown { ReturnType = ReturnType.Next };
var priceField = new SfNumericUpDown { ReturnType = ReturnType.Next };
var totalField = new SfNumericUpDown { ReturnType = ReturnType.Done };

// Search query entry
var searchInput = new SfNumericUpDown { ReturnType = ReturnType.Go };
```

## Programmatic Focus Control

### Setting Focus

Use the `Focus()` method to programmatically set focus:

```csharp
// Set focus to the control
numericUpDown.Focus();
```

**Common scenarios:**

```csharp
// Focus on error
if (!ValidateInput(ageField))
{
    ageField.Focus();
    errorLabel.Text = "Invalid age";
}

// Focus on first empty field
if (nameField.Text.IsNullOrEmpty)
    nameField.Focus();
else if (ageField.Value == null)
    ageField.Focus();
```

### Removing Focus

Use the `Unfocus()` method:

```csharp
// Remove focus
numericUpDown.Unfocus();
```

**Common scenarios:**

```csharp
// Hide keyboard after submission
private void OnSubmit()
{
    quantityField.Unfocus();
    priceField.Unfocus();
    
    // Keyboard now hidden
}
```

### Focus Management Pattern

```csharp
public class FormNavigationPage : ContentPage
{
    private void OnNextClicked()
    {
        if (ValidateCurrentField())
        {
            MoveToNextField();
        }
        else
        {
            ShowError();
            currentField.Focus();
        }
    }
    
    private void MoveToNextField()
    {
        if (currentField == quantityField)
        {
            currentField.Unfocus();
            currentField = priceField;
            priceField.Focus();
        }
        else if (currentField == priceField)
        {
            currentField.Unfocus();
            currentField = discountField;
            discountField.Focus();
        }
    }
}
```

---
