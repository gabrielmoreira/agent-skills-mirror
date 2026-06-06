# Value Restrictions and Validation

This guide explains how to restrict and validate user input in NumericEntry using null handling, range constraints, and editing controls.

## Table of Contents
1. [AllowNull Property](#allownull-property)
2. [Value Range Restrictions](#value-range-restrictions)
3. [Editing Restrictions](#editing-restrictions)
4. [Validation Behavior and Edge Cases](#validation-behavior-and-edge-cases)
5. [Combining Restrictions](#combining-restrictions)

---

## AllowNull Property

The `AllowNull` property controls whether the NumericEntry can have a null value. By default, it's `True`.

### Allowing Null Values (Default)

When `AllowNull="True"`, the control can be empty and the `Value` property can be `null`.

**XAML:**
```xml
<editors:SfNumericEntry Value="100"
                        AllowNull="True" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 100;
sfNumericEntry.AllowNull = true;
```

**Behavior:**
- Clear button sets value to `null`
- Placeholder text is displayed when value is `null`
- `Value` property can be `null` in code
- User can leave field empty

**When to allow null:**
- Optional form fields where "no value" is valid
- When you need to distinguish between 0 and "not entered"
- Fields that aren't required for form submission
- When providing default values after validation

**Example: Optional Middle Initial**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Middle Initial (Optional):" />
    <editors:SfNumericEntry Value="{x:Null}"
                            AllowNull="True"
                            Placeholder="Leave blank if none"
                            CustomFormat="N0" />
</StackLayout>
```

### Preventing Null Values

When `AllowNull="False"`, the control always has a numeric value.

**XAML:**
```xml
<editors:SfNumericEntry Value="10"
                        AllowNull="False" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 10;
sfNumericEntry.AllowNull = false;
```

**Behavior:**
- Clear button sets value to `0` (or `Minimum` if specified)
- Placeholder never displays (always has a value)
- `Value` property is never `null`
- User cannot leave field empty

**When to prevent null:**
- Required form fields
- When 0 is an acceptable default value
- Calculations that require non-null values
- When "no value" is not a valid state

**Example: Required Age Field**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Age (Required):" />
    <editors:SfNumericEntry Value="18"
                            AllowNull="False"
                            Minimum="18"
                            Placeholder="Enter your age"
                            CustomFormat="N0" />
</StackLayout>
```

### Null Handling with Clear Button

**AllowNull="True" - Value becomes null:**
```xml
<editors:SfNumericEntry Value="100"
                        AllowNull="True"
                        ShowClearButton="True"
                        Placeholder="Cleared!" />
```

**Result:** Clicking clear button → Value = `null`, Placeholder displays

**AllowNull="False" - Value becomes 0:**
```xml
<editors:SfNumericEntry Value="100"
                        AllowNull="False"
                        ShowClearButton="True" />
```

**Result:** Clicking clear button → Value = `0`

### Null vs Minimum Value (Important Edge Case)

When both `AllowNull="False"` and `Minimum` are set, the clear button sets the value to `Minimum`, not `0`.

**XAML:**
```xml
<editors:SfNumericEntry Minimum="10"
                        AllowNull="False"
                        Value="50" />
```

**Behavior:**
- Clear button clicked → Value becomes `10` (Minimum)
- Prevents invalid state where value < Minimum
- Always maintains valid value within range

**Why this matters:** This prevents the control from entering an invalid state. If Minimum is 10, setting to 0 would violate the constraint.

### Comparison Example

```xml
<VerticalStackLayout Spacing="25" Padding="20">
    
    <Label Text="AllowNull Comparison" FontSize="20" FontAttributes="Bold" />
    
    <!-- AllowNull = True -->
    <StackLayout Spacing="5">
        <Label Text="AllowNull = True (Can be empty):" FontAttributes="Bold" />
        <editors:SfNumericEntry Value="100"
                                AllowNull="True"
                                Placeholder="Click clear to see null"
                                ShowClearButton="True" />
        <Label Text="• Clears to null" FontSize="12" TextColor="Gray" />
        <Label Text="• Placeholder shows when null" FontSize="12" TextColor="Gray" />
    </StackLayout>
    
    <!-- AllowNull = False -->
    <StackLayout Spacing="5">
        <Label Text="AllowNull = False (Always has value):" FontAttributes="Bold" />
        <editors:SfNumericEntry Value="100"
                                AllowNull="False"
                                ShowClearButton="True" />
        <Label Text="• Clears to 0" FontSize="12" TextColor="Gray" />
        <Label Text="• Never shows placeholder" FontSize="12" TextColor="Gray" />
    </StackLayout>
    
    <!-- AllowNull = False with Minimum -->
    <StackLayout Spacing="5">
        <Label Text="AllowNull = False + Minimum = 10:" FontAttributes="Bold" />
        <editors:SfNumericEntry Value="100"
                                AllowNull="False"
                                Minimum="10"
                                ShowClearButton="True" />
        <Label Text="• Clears to 10 (Minimum)" FontSize="12" TextColor="Gray" />
        <Label Text="• Maintains valid range" FontSize="12" TextColor="Gray" />
    </StackLayout>
    
</VerticalStackLayout>
```

---

## Value Range Restrictions

Restrict user input to a specific numeric range using `Minimum` and `Maximum` properties.

### Setting Minimum Value

The `Minimum` property sets the lowest acceptable value. Default is `double.MinValue`.

**XAML:**
```xml
<editors:SfNumericEntry Value="50"
                        Minimum="10" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Minimum = 10;
sfNumericEntry.Value = 50;
```

**Validation Behavior:**
- User enters value < Minimum → Value resets to Minimum after validation
- Validation happens on blur or Enter key (OnLostFocus mode)
- Visual feedback may vary by platform

**Example: Minimum Age Requirement**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Age (Must be 18 or older):" />
    <editors:SfNumericEntry Value="18"
                            Minimum="18"
                            CustomFormat="N0"
                            Placeholder="Enter age" />
</StackLayout>
```

### Setting Maximum Value

The `Maximum` property sets the highest acceptable value. Default is `double.MaxValue`.

**XAML:**
```xml
<editors:SfNumericEntry Value="50"
                        Maximum="100" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Maximum = 100;
sfNumericEntry.Value = 50;
```

**Validation Behavior:**
- User enters value > Maximum → Value resets to Maximum after validation
- Validation happens on blur or Enter key (OnLostFocus mode)

**Example: Percentage Range**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Discount (0-100%):" />
    <editors:SfNumericEntry Value="10"
                            Minimum="0"
                            Maximum="100"
                            CustomFormat="P0"
                            PercentDisplayMode="Value" />
</StackLayout>
```

### Setting Both Minimum and Maximum

Constrain values to a specific range.

**XAML:**
```xml
<editors:SfNumericEntry Value="50"
                        Minimum="10"
                        Maximum="100" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Minimum = 10;
sfNumericEntry.Maximum = 100;
sfNumericEntry.Value = 50;
```

**Validation Behavior:**
- Value < Minimum → Resets to Minimum
- Value > Maximum → Resets to Maximum
- Value within range → Accepted

**Example: Temperature Range**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Room Temperature (°C):" />
    <editors:SfNumericEntry Value="22"
                            Minimum="15"
                            Maximum="30"
                            CustomFormat="N1"
                            Placeholder="15-30°C" />
</StackLayout>
```

### Out-of-Range Value Handling

When a user enters an out-of-range value, NumericEntry automatically corrects it.

**Initial value out of range:**
```xml
<editors:SfNumericEntry Value="150"
                        Minimum="10"
                        Maximum="100" />
```

**Result:** Value is automatically clamped to `100` (Maximum)

**User types out-of-range value:**
1. User types `5` (less than Minimum of 10)
2. User presses Enter or leaves field
3. Value automatically becomes `10` (Minimum)

**User types out-of-range value (high):**
1. User types `200` (greater than Maximum of 100)
2. User presses Enter or leaves field
3. Value automatically becomes `100` (Maximum)

### Range Validation Example with Feedback

```xml
<VerticalStackLayout Spacing="20" Padding="20">
    
    <Label Text="Range Validation Demo" FontSize="20" FontAttributes="Bold" />
    
    <Label Text="Try entering values outside 10-100:" FontSize="14" />
    <editors:SfNumericEntry x:Name="rangeInput"
                            Value="50"
                            Minimum="10"
                            Maximum="100"
                            CustomFormat="N0"
                            Placeholder="10-100"
                            ValueChanged="OnRangeValueChanged" />
    
    <Label x:Name="rangeLabel"
           Text="Current Value: 50 (Valid)"
           FontSize="14"
           TextColor="Green" />
    
    <Label Text="Instructions:" FontSize="12" FontAttributes="Bold" />
    <Label Text="• Type a value less than 10 and press Enter" FontSize="12" />
    <Label Text="• Watch it reset to 10 (Minimum)" FontSize="12" />
    <Label Text="• Type a value greater than 100 and press Enter" FontSize="12" />
    <Label Text="• Watch it reset to 100 (Maximum)" FontSize="12" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnRangeValueChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue)
    {
        double value = e.NewValue.Value;
        
        if (value < 10)
        {
            rangeLabel.Text = $"Value {value} < 10 → Reset to Minimum (10)";
            rangeLabel.TextColor = Colors.Red;
        }
        else if (value > 100)
        {
            rangeLabel.Text = $"Value {value} > 100 → Reset to Maximum (100)";
            rangeLabel.TextColor = Colors.Red;
        }
        else
        {
            rangeLabel.Text = $"Current Value: {value} (Valid)";
            rangeLabel.TextColor = Colors.Green;
        }
    }
    else
    {
        rangeLabel.Text = "Current Value: null";
        rangeLabel.TextColor = Colors.Gray;
    }
}
```

### Practical Range Examples

**Price Range for Products:**
```xml
<editors:SfNumericEntry Value="99.99"
                        Minimum="0.01"
                        Maximum="999999.99"
                        CustomFormat="C2"
                        Placeholder="$0.01 - $999,999.99" />
```

**Rating System (1-5 stars):**
```xml
<editors:SfNumericEntry Value="5"
                        Minimum="1"
                        Maximum="5"
                        CustomFormat="N0"
                        AllowNull="False"
                        Placeholder="1-5" />
```

**Quantity Selector:**
```xml
<editors:SfNumericEntry Value="1"
                        Minimum="1"
                        Maximum="999"
                        CustomFormat="N0"
                        AllowNull="False" />
```

**Discount Percentage (0-100%):**
```xml
<editors:SfNumericEntry Value="10"
                        Minimum="0"
                        Maximum="100"
                        CustomFormat="P0"
                        PercentDisplayMode="Value" />
```

---

## Editing Restrictions

Control whether users can edit the value using the `IsEditable` property.

### Making NumericEntry Read-Only

Set `IsEditable="False"` to prevent text editing while allowing display.

**XAML:**
```xml
<editors:SfNumericEntry Value="12345"
                        IsEditable="False" />
```

**C#:**
```csharp
SfNumericEntry sfNumericEntry = new SfNumericEntry();
sfNumericEntry.Value = 12345;
sfNumericEntry.IsEditable = false;
```

**When IsEditable="False":**
- User cannot type or modify the value
- Clear button is hidden
- Control can still receive focus
- Value can be changed programmatically in code
- Useful for displaying calculated or read-only values

**When to use read-only mode:**
- Display calculated totals or summaries
- Show system-generated values
- Present results from computations
- Display values that shouldn't be manually edited

### Read-Only Display Examples

**Order Total Display:**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Subtotal:" />
    <editors:SfNumericEntry Value="100"
                            CustomFormat="C2"
                            ValueChanged="CalculateTotal" />
    
    <Label Text="Tax (10%):" />
    <editors:SfNumericEntry Value="10"
                            CustomFormat="C2"
                            IsEditable="False"
                            ShowClearButton="False"
                            ShowBorder="False"
                            TextColor="Gray" />
    
    <Label Text="Total:" FontAttributes="Bold" />
    <editors:SfNumericEntry Value="110"
                            CustomFormat="C2"
                            IsEditable="False"
                            ShowClearButton="False"
                            TextColor="Green"
                            FontSize="24"
                            FontAttributes="Bold" />
</StackLayout>
```

**System-Generated ID:**
```xml
<StackLayout Spacing="10" Padding="20">
    <Label Text="Order ID (Auto-generated):" />
    <editors:SfNumericEntry Value="100542"
                            CustomFormat="000000"
                            IsEditable="False"
                            ShowClearButton="False"
                            ShowBorder="False"
                            TextColor="DarkGray"
                            FontFamily="Courier New" />
</StackLayout>
```

### Editable vs Read-Only Comparison

```xml
<VerticalStackLayout Spacing="20" Padding="20">
    
    <Label Text="IsEditable Comparison" FontSize="20" FontAttributes="Bold" />
    
    <!-- Editable (Default) -->
    <StackLayout Spacing="5">
        <Label Text="IsEditable = True (Default):" FontAttributes="Bold" />
        <editors:SfNumericEntry Value="12345"
                                IsEditable="True"
                                ShowClearButton="True" />
        <Label Text="• Can type and edit" FontSize="12" TextColor="Gray" />
        <Label Text="• Clear button visible on focus" FontSize="12" TextColor="Gray" />
    </StackLayout>
    
    <!-- Read-Only -->
    <StackLayout Spacing="5">
        <Label Text="IsEditable = False (Read-Only):" FontAttributes="Bold" />
        <editors:SfNumericEntry Value="12345"
                                IsEditable="False" />
        <Label Text="• Cannot edit text" FontSize="12" TextColor="Gray" />
        <Label Text="• Clear button hidden" FontSize="12" TextColor="Gray" />
        <Label Text="• Still displays value" FontSize="12" TextColor="Gray" />
    </StackLayout>
    
    <!-- Read-Only with Custom Styling -->
    <StackLayout Spacing="5">
        <Label Text="Read-Only with Custom Style:" FontAttributes="Bold" />
        <editors:SfNumericEntry Value="12345"
                                CustomFormat="C2"
                                IsEditable="False"
                                ShowClearButton="False"
                                ShowBorder="False"
                                TextColor="Green"
                                FontSize="20"
                                FontAttributes="Bold"
                                HorizontalTextAlignment="Center" />
        <Label Text="• Styled as display-only" FontSize="12" TextColor="Gray" />
        <Label Text="• No border, large font" FontSize="12" TextColor="Gray" />
    </StackLayout>
    
</VerticalStackLayout>
```

---

## Validation Behavior and Edge Cases

Understanding how validation works helps prevent unexpected behavior.

### Validation Timing

**OnLostFocus Mode (Default):**
- Validation occurs when control loses focus
- Validation occurs on Enter key press
- User can type freely without immediate validation

**OnKeyFocus Mode:**
- Validation occurs with each keystroke
- Immediate feedback on invalid input
- May interrupt typing flow

### Edge Case: Null vs Zero vs Minimum

This is a common source of confusion. Here's how different property combinations behave:

**Case 1: AllowNull=True, No Minimum**
```xml
<editors:SfNumericEntry AllowNull="True" />
```
- Clear button → Value = `null`
- Empty input → Value = `null`

**Case 2: AllowNull=False, No Minimum**
```xml
<editors:SfNumericEntry AllowNull="False" />
```
- Clear button → Value = `0`
- Empty input → Value = `0`

**Case 3: AllowNull=True, Minimum=10**
```xml
<editors:SfNumericEntry AllowNull="True" Minimum="10" />
```
- Clear button → Value = `null` (allowed)
- User enters `5` → Value resets to `10` (Minimum)
- Null is valid, but values < 10 are not

**Case 4: AllowNull=False, Minimum=10**
```xml
<editors:SfNumericEntry AllowNull="False" Minimum="10" />
```
- Clear button → Value = `10` (Minimum, not 0)
- User enters `5` → Value resets to `10` (Minimum)
- Always maintains valid value ≥ Minimum

### Edge Case Examples

**Example: Age Validation with Minimum**
```xml
<editors:SfNumericEntry Value="18"
                        Minimum="18"
                        AllowNull="False"
                        CustomFormat="N0" />
```

**Behavior:**
- Clear button sets value to `18` (not 0, not null)
- User enters `15` → Resets to `18` after validation
- Always valid for age verification

**Example: Optional Discount (Null Allowed)**
```xml
<editors:SfNumericEntry Value="{x:Null}"
                        Minimum="5"
                        Maximum="50"
                        AllowNull="True"
                        CustomFormat="P0"
                        PercentDisplayMode="Value"
                        Placeholder="5-50% or leave empty" />
```

**Behavior:**
- Clear button → Value = `null` (discount not applied)
- User enters `3` → Resets to `5` (Minimum discount)
- User enters `60` → Resets to `50` (Maximum discount)
- Null means "no discount"

### Validation State Handling

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Age Verification" FontSize="18" FontAttributes="Bold" />
    
    <editors:SfNumericEntry x:Name="ageInput"
                            Value="18"
                            Minimum="18"
                            Maximum="100"
                            AllowNull="False"
                            CustomFormat="N0"
                            Placeholder="18-100"
                            ValueChanged="OnAgeChanged" />
    
    <Label x:Name="validationLabel"
           Text="Valid age"
           FontSize="14"
           TextColor="Green" />
    
    <Button Text="Submit"
            x:Name="submitButton"
            Clicked="OnSubmitClicked" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnAgeChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue)
    {
        double age = e.NewValue.Value;
        
        if (age >= 18 && age <= 100)
        {
            validationLabel.Text = "Valid age";
            validationLabel.TextColor = Colors.Green;
            submitButton.IsEnabled = true;
        }
        else
        {
            // This shouldn't happen due to Min/Max, but good to handle
            validationLabel.Text = "Age must be 18-100";
            validationLabel.TextColor = Colors.Red;
            submitButton.IsEnabled = false;
        }
    }
    else
    {
        // Also shouldn't happen due to AllowNull=False
        validationLabel.Text = "Age is required";
        validationLabel.TextColor = Colors.Red;
        submitButton.IsEnabled = false;
    }
}

private async void OnSubmitClicked(object sender, EventArgs e)
{
    if (ageInput.Value.HasValue)
    {
        await DisplayAlert("Success", $"Age {ageInput.Value} verified", "OK");
    }
}
```

---

## Combining Restrictions

Combine multiple restriction properties for robust validation.

### Pattern 1: Required Numeric Input with Range

```xml
<editors:SfNumericEntry Value="50"
                        AllowNull="False"
                        Minimum="10"
                        Maximum="100"
                        CustomFormat="N0"
                        Placeholder="10-100" />
```

**Enforces:**
- Always has a value (not null)
- Value is between 10 and 100
- Displays as whole number

**Use case:** Required quantity input, rating systems

### Pattern 2: Optional Input with Range Constraints

```xml
<editors:SfNumericEntry Value="{x:Null}"
                        AllowNull="True"
                        Minimum="0"
                        Maximum="999.99"
                        CustomFormat="C2"
                        Placeholder="$0-$999.99 or leave empty" />
```

**Enforces:**
- Can be empty/null
- If entered, must be between 0 and 999.99
- Displays as currency

**Use case:** Optional tip amount, optional donation

### Pattern 3: Read-Only Calculated Value with Formatting

```xml
<editors:SfNumericEntry Value="1234.56"
                        IsEditable="False"
                        ShowClearButton="False"
                        CustomFormat="C2"
                        TextColor="Green"
                        FontSize="20"
                        FontAttributes="Bold" />
```

**Enforces:**
- Cannot be edited by user
- Always formatted as currency
- Styled for emphasis

**Use case:** Order totals, calculated taxes, summaries

### Pattern 4: Strict Positive Number Only

```xml
<editors:SfNumericEntry Value="1"
                        AllowNull="False"
                        Minimum="0.01"
                        CustomFormat="N2"
                        Placeholder="Must be > 0" />
```

**Enforces:**
- Always has a value
- Cannot be zero or negative
- Displays with 2 decimal places

**Use case:** Unit price, product weight, dimensions

### Complete Restriction Example

**XAML:**
```xml
<ScrollView>
    <VerticalStackLayout Spacing="20" Padding="30">
        
        <Label Text="Product Order Form"
               FontSize="24"
               FontAttributes="Bold"
               HorizontalOptions="Center"
               Margin="0,0,0,20" />
        
        <!-- Required Price (Min $0.01) -->
        <StackLayout Spacing="5">
            <Label Text="Unit Price (Required):" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="priceInput"
                                    Value="99.99"
                                    AllowNull="False"
                                    Minimum="0.01"
                                    Maximum="99999.99"
                                    CustomFormat="C2"
                                    Placeholder="$0.01+"
                                    ValueChanged="CalculateTotal" />
            <Label Text="Must be at least $0.01" FontSize="12" TextColor="Gray" />
        </StackLayout>
        
        <!-- Required Quantity (Min 1) -->
        <StackLayout Spacing="5">
            <Label Text="Quantity (Required):" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="quantityInput"
                                    Value="1"
                                    AllowNull="False"
                                    Minimum="1"
                                    Maximum="999"
                                    CustomFormat="N0"
                                    ValueChanged="CalculateTotal" />
            <Label Text="1-999 items" FontSize="12" TextColor="Gray" />
        </StackLayout>
        
        <!-- Optional Discount (0-50%) -->
        <StackLayout Spacing="5">
            <Label Text="Discount % (Optional):" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="discountInput"
                                    Value="{x:Null}"
                                    AllowNull="True"
                                    Minimum="0"
                                    Maximum="50"
                                    CustomFormat="P0"
                                    PercentDisplayMode="Value"
                                    Placeholder="0-50% or leave empty"
                                    ValueChanged="CalculateTotal" />
            <Label Text="Leave empty for no discount" FontSize="12" TextColor="Gray" />
        </StackLayout>
        
        <!-- Read-Only Subtotal -->
        <StackLayout Spacing="5">
            <Label Text="Subtotal:" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="subtotalDisplay"
                                    Value="99.99"
                                    CustomFormat="C2"
                                    IsEditable="False"
                                    ShowClearButton="False"
                                    ShowBorder="False"
                                    TextColor="DarkGray" />
        </StackLayout>
        
        <!-- Read-Only Discount Amount -->
        <StackLayout Spacing="5">
            <Label Text="Discount Amount:" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="discountAmountDisplay"
                                    Value="0"
                                    CustomFormat="C2"
                                    IsEditable="False"
                                    ShowClearButton="False"
                                    ShowBorder="False"
                                    TextColor="Red" />
        </StackLayout>
        
        <!-- Read-Only Total -->
        <StackLayout Spacing="5">
            <Label Text="Total:" FontSize="18" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="totalDisplay"
                                    Value="99.99"
                                    CustomFormat="C2"
                                    IsEditable="False"
                                    ShowClearButton="False"
                                    TextColor="Green"
                                    FontSize="28"
                                    FontAttributes="Bold"
                                    HorizontalTextAlignment="Center" />
        </StackLayout>
        
        <Button Text="Place Order"
                Clicked="OnPlaceOrderClicked"
                BackgroundColor="Green"
                TextColor="White"
                Margin="0,20,0,0" />
        
    </VerticalStackLayout>
</ScrollView>
```

**Code-Behind:**
```csharp
private void CalculateTotal(object sender, NumericEntryValueChangedEventArgs e)
{
    double price = priceInput.Value ?? 0;
    double quantity = quantityInput.Value ?? 1;
    double discountPercent = discountInput.Value ?? 0;
    
    double subtotal = price * quantity;
    double discountAmount = subtotal * (discountPercent / 100);
    double total = subtotal - discountAmount;
    
    subtotalDisplay.Value = subtotal;
    discountAmountDisplay.Value = discountAmount;
    totalDisplay.Value = total;
}

private async void OnPlaceOrderClicked(object sender, EventArgs e)
{
    // All required fields are guaranteed to have values due to AllowNull=False
    double price = priceInput.Value.Value;
    double quantity = quantityInput.Value.Value;
    double total = totalDisplay.Value.Value;
    
    await DisplayAlert(
        "Order Confirmed",
        $"Ordered {quantity} items at {price:C} each\nTotal: {total:C}",
        "OK"
    );
}
```

---

## Best Practices

1. **Use AllowNull=False for required fields** to ensure values are always present
2. **Set Minimum=0 for non-negative inputs** (prices, quantities, ages)
3. **Combine Minimum and AllowNull=False** to ensure valid defaults (e.g., Minimum=1 prevents zero)
4. **Provide clear placeholder text** indicating valid ranges
5. **Use IsEditable=False for calculated fields** (totals, taxes, derived values)
6. **Hide clear button on read-only fields** with ShowClearButton=False
7. **Consider edge cases** when combining AllowNull, Minimum, and Maximum
8. **Validate in ValueChanged event** for custom validation logic beyond range
9. **Use consistent validation patterns** across your app for predictable UX
10. **Test clear button behavior** with different property combinations

---

## Troubleshooting

**Issue:** Clear button sets value to 0 instead of null
- **Solution:** Check AllowNull property; it's set to False (default is True)

**Issue:** Value resets to Minimum instead of 0 when cleared
- **Solution:** This is correct behavior when AllowNull=False and Minimum is set

**Issue:** User can enter invalid values
- **Solution:** Validation happens on blur or Enter key (OnLostFocus mode); invalid values are corrected after validation

**Issue:** Cannot enter null value
- **Solution:** Set AllowNull=True to allow null values

**Issue:** Read-only field still shows clear button
- **Solution:** Set ShowClearButton=False on read-only fields

---