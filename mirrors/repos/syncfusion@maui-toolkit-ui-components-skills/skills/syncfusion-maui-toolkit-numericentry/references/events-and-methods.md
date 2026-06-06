# Events and Methods

This guide explains the events and methods available in NumericEntry for handling user interactions and programmatic control.

## Table of Contents
1. [ValueChanged Event](#valuechanged-event)
2. [Completed Event](#completed-event)
3. [Focus Events](#focus-events)
4. [Focus and Unfocus Methods](#focus-and-unfocus-methods)
5. [Event Handling Patterns](#event-handling-patterns)
6. [Form Navigation and Submission](#form-navigation-and-submission)

---

## ValueChanged Event

The `ValueChanged` event is raised when the `Value` property changes, either through user input or programmatic updates.

### Event Arguments

The `NumericEntryValueChangedEventArgs` provides:
- **OldValue** (`double?`): The previous value before the change (can be null)
- **NewValue** (`double?`): The current value after the change (can be null)

### Basic ValueChanged Example

**XAML:**
```xml
<editors:SfNumericEntry Value="100"
                        ValueChanged="OnValueChanged" />
```

**Code-Behind:**
```csharp
private void OnValueChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    double? oldValue = e.OldValue;
    double? newValue = e.NewValue;
    
    // Handle the value change
    Console.WriteLine($"Value changed from {oldValue} to {newValue}");
}
```

### When ValueChanged is Raised

**User Input:**
- After user types and loses focus (OnLostFocus mode)
- After each keystroke (OnKeyFocus mode)
- After pressing Enter key

**Programmatic Changes:**
- When setting `Value` property in code
- When clear button is clicked
- When validation adjusts value to Minimum or Maximum

**Important:** The event fires for both user-initiated and code-initiated changes.

### Checking for Null Values

Always check if values are null when `AllowNull="True"`:

```csharp
private void OnValueChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue)
    {
        double value = e.NewValue.Value;
        // Use the value
        Console.WriteLine($"New value: {value}");
    }
    else
    {
        Console.WriteLine("Value is null");
    }
}
```

### Calculating Totals Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Price Calculator" FontSize="20" FontAttributes="Bold" />
    
    <Label Text="Unit Price:" />
    <editors:SfNumericEntry x:Name="priceInput"
                            Value="10.00"
                            CustomFormat="C2"
                            ValueChanged="CalculateTotal" />
    
    <Label Text="Quantity:" />
    <editors:SfNumericEntry x:Name="quantityInput"
                            Value="2"
                            CustomFormat="N0"
                            ValueChanged="CalculateTotal" />
    
    <Label Text="Total:" FontAttributes="Bold" />
    <editors:SfNumericEntry x:Name="totalDisplay"
                            Value="20.00"
                            CustomFormat="C2"
                            IsEditable="False"
                            ShowBorder="False"
                            TextColor="Green"
                            FontSize="24"
                            FontAttributes="Bold" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void CalculateTotal(object sender, NumericEntryValueChangedEventArgs e)
{
    double price = priceInput.Value ?? 0;
    double quantity = quantityInput.Value ?? 0;
    double total = price * quantity;
    
    totalDisplay.Value = total;
}
```

### Conditional Behavior Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Discount Calculator" FontSize="18" FontAttributes="Bold" />
    
    <Label Text="Order Total:" />
    <editors:SfNumericEntry x:Name="orderTotalInput"
                            Value="100"
                            CustomFormat="C2"
                            ValueChanged="OnOrderTotalChanged" />
    
    <Label x:Name="discountLabel" Text="No discount" TextColor="Gray" />
    
    <Label Text="Discount Amount:" />
    <editors:SfNumericEntry x:Name="discountDisplay"
                            Value="0"
                            CustomFormat="C2"
                            IsEditable="False"
                            ShowBorder="False"
                            TextColor="Red" />
    
    <Label Text="Final Total:" />
    <editors:SfNumericEntry x:Name="finalTotalDisplay"
                            Value="100"
                            CustomFormat="C2"
                            IsEditable="False"
                            ShowBorder="False"
                            TextColor="Green"
                            FontSize="20"
                            FontAttributes="Bold" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnOrderTotalChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue)
    {
        double orderTotal = e.NewValue.Value;
        double discountPercent = 0;
        string discountMessage = "No discount";
        
        // Apply tiered discounts
        if (orderTotal >= 500)
        {
            discountPercent = 20;
            discountMessage = "20% discount (orders $500+)";
        }
        else if (orderTotal >= 200)
        {
            discountPercent = 10;
            discountMessage = "10% discount (orders $200+)";
        }
        else if (orderTotal >= 100)
        {
            discountPercent = 5;
            discountMessage = "5% discount (orders $100+)";
        }
        
        double discountAmount = orderTotal * (discountPercent / 100);
        double finalTotal = orderTotal - discountAmount;
        
        discountLabel.Text = discountMessage;
        discountLabel.TextColor = discountPercent > 0 ? Colors.Green : Colors.Gray;
        discountDisplay.Value = discountAmount;
        finalTotalDisplay.Value = finalTotal;
    }
}
```

### Validation and Formatting on Change

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Age Input with Validation" FontSize="18" FontAttributes="Bold" />
    
    <editors:SfNumericEntry x:Name="ageInput"
                            Value="18"
                            Minimum="18"
                            Maximum="100"
                            CustomFormat="N0"
                            AllowNull="False"
                            Placeholder="18-100"
                            ValueChanged="OnAgeChanged" />
    
    <Label x:Name="validationMessage"
           Text="Valid age"
           TextColor="Green"
           FontSize="14" />
    
    <Button Text="Submit"
            x:Name="submitButton"
            Clicked="OnSubmitClicked"
            IsEnabled="True" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnAgeChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue)
    {
        double age = e.NewValue.Value;
        
        // Even with Min/Max, validation provides user feedback
        if (age >= 18 && age <= 100)
        {
            validationMessage.Text = $"Age {age} is valid";
            validationMessage.TextColor = Colors.Green;
            submitButton.IsEnabled = true;
        }
        else if (age < 18)
        {
            validationMessage.Text = "Must be 18 or older";
            validationMessage.TextColor = Colors.Red;
            submitButton.IsEnabled = false;
        }
        else
        {
            validationMessage.Text = "Age seems too high";
            validationMessage.TextColor = Colors.Orange;
            submitButton.IsEnabled = true; // Still allow, but warn
        }
    }
    else
    {
        validationMessage.Text = "Age is required";
        validationMessage.TextColor = Colors.Red;
        submitButton.IsEnabled = false;
    }
}

private async void OnSubmitClicked(object sender, EventArgs e)
{
    if (ageInput.Value.HasValue)
    {
        await DisplayAlert("Success", $"Age {ageInput.Value.Value} verified", "OK");
    }
}
```

---

## Completed Event

The `Completed` event is raised when the user presses the Enter/Return key while the NumericEntry has focus.

### Basic Completed Example

**XAML:**
```xml
<editors:SfNumericEntry Value="100"
                        Completed="OnCompleted" />
```

**Code-Behind:**
```csharp
private void OnCompleted(object sender, EventArgs e)
{
    // Handle Enter key press
    Console.WriteLine("Enter key pressed");
}
```

### When to Use Completed Event

- **Form submission:** Submit form when user presses Enter on last field
- **Navigation:** Move focus to next field in sequence
- **Inline actions:** Perform action immediately (add to cart, search, etc.)
- **Validation:** Trigger validation and feedback

### Form Submission Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Quick Order Form" FontSize="20" FontAttributes="Bold" />
    
    <Label Text="Product ID:" />
    <editors:SfNumericEntry x:Name="productIdInput"
                            Value="100"
                            CustomFormat="000000"
                            ReturnType="Next" />
    
    <Label Text="Quantity:" />
    <editors:SfNumericEntry x:Name="quantityInput"
                            Value="1"
                            CustomFormat="N0"
                            Completed="OnQuantityCompleted" />
    
    <Label x:Name="statusLabel"
           Text="Enter quantity and press Enter"
           TextColor="Gray" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private async void OnQuantityCompleted(object sender, EventArgs e)
{
    // User pressed Enter after entering quantity
    if (productIdInput.Value.HasValue && quantityInput.Value.HasValue)
    {
        int productId = (int)productIdInput.Value.Value;
        int quantity = (int)quantityInput.Value.Value;
        
        statusLabel.Text = "Processing order...";
        statusLabel.TextColor = Colors.Orange;
        
        // Simulate order processing
        await Task.Delay(1000);
        
        statusLabel.Text = $"Order placed: Product {productId}, Qty {quantity}";
        statusLabel.TextColor = Colors.Green;
        
        // Reset form
        await Task.Delay(2000);
        productIdInput.Value = null;
        quantityInput.Value = 1;
        statusLabel.Text = "Enter next order";
        statusLabel.TextColor = Colors.Gray;
        
        // Move focus back to first field
        productIdInput.Focus();
    }
}
```

### Search Box Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Product Search by ID" FontSize="18" FontAttributes="Bold" />
    
    <HorizontalStackLayout Spacing="10">
        <editors:SfNumericEntry x:Name="searchInput"
                                Placeholder="Enter product ID"
                                CustomFormat="N0"
                                WidthRequest="200"
                                Completed="OnSearchCompleted"
                                ReturnType="Search" />
        <Button Text="Search"
                Clicked="OnSearchClicked" />
    </HorizontalStackLayout>
    
    <Label x:Name="searchResultLabel"
           Text="Press Enter or click Search"
           TextColor="Gray" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnSearchCompleted(object sender, EventArgs e)
{
    // User pressed Enter in search box
    PerformSearch();
}

private void OnSearchClicked(object sender, EventArgs e)
{
    // User clicked Search button
    PerformSearch();
}

private async void PerformSearch()
{
    if (searchInput.Value.HasValue)
    {
        int productId = (int)searchInput.Value.Value;
        
        searchResultLabel.Text = "Searching...";
        searchResultLabel.TextColor = Colors.Orange;
        
        // Simulate search
        await Task.Delay(800);
        
        // Mock result
        searchResultLabel.Text = $"Found: Product {productId} - $99.99";
        searchResultLabel.TextColor = Colors.Green;
    }
    else
    {
        searchResultLabel.Text = "Please enter a product ID";
        searchResultLabel.TextColor = Colors.Red;
    }
}
```

### Add to Cart Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Quick Add to Cart" FontSize="18" FontAttributes="Bold" />
    
    <Label Text="Enter quantity and press Enter:" />
    <editors:SfNumericEntry x:Name="quickQuantityInput"
                            Value="1"
                            Minimum="1"
                            Maximum="99"
                            AllowNull="False"
                            CustomFormat="N0"
                            Completed="OnQuickAddCompleted"
                            ReturnType="Done" />
    
    <Label x:Name="cartLabel"
           Text="Cart: 0 items"
           FontSize="16"
           TextColor="Gray" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private int cartItemCount = 0;

private async void OnQuickAddCompleted(object sender, EventArgs e)
{
    if (quickQuantityInput.Value.HasValue)
    {
        int quantity = (int)quickQuantityInput.Value.Value;
        cartItemCount += quantity;
        
        cartLabel.Text = $"Added {quantity} items! Cart: {cartItemCount} items";
        cartLabel.TextColor = Colors.Green;
        
        // Reset to 1 for next add
        await Task.Delay(1500);
        quickQuantityInput.Value = 1;
        cartLabel.TextColor = Colors.Gray;
    }
}
```

---

## Focus Events

NumericEntry provides events to detect when the control gains or loses focus.

### Focused Event

Raised when the control receives focus.

**XAML:**
```xml
<editors:SfNumericEntry Focused="OnFocused" />
```

**Code-Behind:**
```csharp
private void OnFocused(object sender, FocusEventArgs e)
{
    Console.WriteLine("NumericEntry gained focus");
}
```

### Unfocused Event

Raised when the control loses focus.

**XAML:**
```xml
<editors:SfNumericEntry Unfocused="OnUnfocused" />
```

**Code-Behind:**
```csharp
private void OnUnfocused(object sender, FocusEventArgs e)
{
    Console.WriteLine("NumericEntry lost focus");
}
```

### Focus State Tracking Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Focus State Demo" FontSize="18" FontAttributes="Bold" />
    
    <editors:SfNumericEntry x:Name="focusTrackInput"
                            Value="100"
                            Placeholder="Click to focus"
                            Focused="OnFocusTrackFocused"
                            Unfocused="OnFocusTrackUnfocused" />
    
    <Label x:Name="focusStatusLabel"
           Text="Focus state: Unfocused"
           FontSize="14"
           TextColor="Gray" />
    
    <Label Text="Click the field above to see focus state changes" 
           FontSize="12"
           TextColor="Gray" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnFocusTrackFocused(object sender, FocusEventArgs e)
{
    focusStatusLabel.Text = "Focus state: Focused";
    focusStatusLabel.TextColor = Colors.Green;
}

private void OnFocusTrackUnfocused(object sender, FocusEventArgs e)
{
    focusStatusLabel.Text = "Focus state: Unfocused";
    focusStatusLabel.TextColor = Colors.Gray;
}
```

### Validation on Blur Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Email Validation" FontSize="18" FontAttributes="Bold" />
    
    <Label Text="Product Count:" />
    <editors:SfNumericEntry x:Name="productCountInput"
                            Value="50"
                            Minimum="1"
                            CustomFormat="N0"
                            Unfocused="OnProductCountUnfocused" />
    
    <Label x:Name="stockWarningLabel"
           Text=""
           FontSize="14"
           TextColor="Orange"
           IsVisible="False" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnProductCountUnfocused(object sender, FocusEventArgs e)
{
    // Validate when user leaves the field
    if (productCountInput.Value.HasValue)
    {
        int count = (int)productCountInput.Value.Value;
        
        if (count < 10)
        {
            stockWarningLabel.Text = "⚠️ Low stock warning: Consider reordering";
            stockWarningLabel.IsVisible = true;
        }
        else
        {
            stockWarningLabel.IsVisible = false;
        }
    }
}
```

### Auto-Save on Blur Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="User Settings (Auto-save)" FontSize="18" FontAttributes="Bold" />
    
    <Label Text="Session Timeout (minutes):" />
    <editors:SfNumericEntry x:Name="timeoutInput"
                            Value="30"
                            Minimum="5"
                            Maximum="120"
                            CustomFormat="N0"
                            Unfocused="OnTimeoutUnfocused" />
    
    <Label x:Name="saveStatusLabel"
           Text="Last saved: Never"
           FontSize="12"
           TextColor="Gray" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private async void OnTimeoutUnfocused(object sender, FocusEventArgs e)
{
    if (timeoutInput.Value.HasValue)
    {
        saveStatusLabel.Text = "Saving...";
        saveStatusLabel.TextColor = Colors.Orange;
        
        // Simulate save operation
        await Task.Delay(500);
        
        // Save to preferences
        Preferences.Set("SessionTimeout", timeoutInput.Value.Value);
        
        saveStatusLabel.Text = $"Last saved: {DateTime.Now:HH:mm:ss}";
        saveStatusLabel.TextColor = Colors.Green;
    }
}
```

---

## Focus and Unfocus Methods

Programmatically control focus using the `Focus()` and `Unfocus()` methods.

### Focus() Method

Sets focus to the NumericEntry programmatically.

**Example:**
```csharp
// Give focus to the NumericEntry
numericEntry.Focus();
```

### Unfocus() Method

Removes focus from the NumericEntry programmatically.

**Example:**
```csharp
// Remove focus from the NumericEntry
numericEntry.Unfocus();
```

### Focus on Page Appear Example

**XAML:**
```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:editors="clr-namespace:Syncfusion.Maui.Toolkit.NumericEntry;assembly=Syncfusion.Maui.Toolkit"
             x:Class="MyApp.SearchPage"
             Appearing="OnPageAppearing">
    
    <VerticalStackLayout Spacing="15" Padding="20">
        <Label Text="Search Products" FontSize="20" FontAttributes="Bold" />
        
        <editors:SfNumericEntry x:Name="searchInput"
                                Placeholder="Enter product ID"
                                CustomFormat="N0" />
        
        <Button Text="Search" Clicked="OnSearchClicked" />
    </VerticalStackLayout>
    
</ContentPage>
```

**Code-Behind:**
```csharp
private void OnPageAppearing(object sender, EventArgs e)
{
    // Auto-focus search field when page appears
    searchInput.Focus();
}
```

### Focus Navigation Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Multi-Field Form" FontSize="18" FontAttributes="Bold" />
    
    <Label Text="Field 1:" />
    <editors:SfNumericEntry x:Name="field1"
                            ReturnType="Next"
                            Completed="OnField1Completed" />
    
    <Label Text="Field 2:" />
    <editors:SfNumericEntry x:Name="field2"
                            ReturnType="Next"
                            Completed="OnField2Completed" />
    
    <Label Text="Field 3:" />
    <editors:SfNumericEntry x:Name="field3"
                            ReturnType="Done"
                            Completed="OnField3Completed" />
    
    <Button Text="Reset Focus"
            Clicked="OnResetFocusClicked" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnField1Completed(object sender, EventArgs e)
{
    // Move to next field when Enter pressed
    field2.Focus();
}

private void OnField2Completed(object sender, EventArgs e)
{
    field3.Focus();
}

private void OnField3Completed(object sender, EventArgs e)
{
    // Last field - unfocus to dismiss keyboard
    field3.Unfocus();
    
    // Or submit form
    SubmitForm();
}

private void OnResetFocusClicked(object sender, EventArgs e)
{
    // Return focus to first field
    field1.Focus();
}

private async void SubmitForm()
{
    await DisplayAlert("Form Submitted", "All fields completed", "OK");
}
```

### Conditional Focus Example

**XAML:**
```xml
<VerticalStackLayout Spacing="15" Padding="20">
    
    <Label Text="Order Form" FontSize="18" FontAttributes="Bold" />
    
    <Label Text="Product ID:" />
    <editors:SfNumericEntry x:Name="productInput"
                            CustomFormat="N0"
                            AllowNull="False"
                            Completed="OnProductCompleted" />
    
    <Label Text="Quantity:" />
    <editors:SfNumericEntry x:Name="quantityInput"
                            Value="1"
                            Minimum="1"
                            AllowNull="False"
                            CustomFormat="N0" />
    
    <Button Text="Validate and Submit"
            Clicked="OnValidateClicked" />
    
    <Label x:Name="validationLabel"
           Text=""
           TextColor="Red" />
    
</VerticalStackLayout>
```

**Code-Behind:**
```csharp
private void OnProductCompleted(object sender, EventArgs e)
{
    // Auto-advance to quantity after entering product ID
    quantityInput.Focus();
}

private async void OnValidateClicked(object sender, EventArgs e)
{
    validationLabel.Text = "";
    
    // Validate product ID
    if (!productInput.Value.HasValue || productInput.Value.Value <= 0)
    {
        validationLabel.Text = "Please enter a valid Product ID";
        productInput.Focus(); // Focus on error field
        return;
    }
    
    // Validate quantity
    if (!quantityInput.Value.HasValue || quantityInput.Value.Value < 1)
    {
        validationLabel.Text = "Quantity must be at least 1";
        quantityInput.Focus(); // Focus on error field
        return;
    }
    
    // All valid - submit
    await DisplayAlert(
        "Order Submitted",
        $"Product: {productInput.Value}, Quantity: {quantityInput.Value}",
        "OK"
    );
    
    // Reset
    productInput.Value = null;
    quantityInput.Value = 1;
    productInput.Focus();
}
```

---

## Event Handling Patterns

Common patterns for combining multiple events.

### Pattern 1: Live Calculation with Debouncing

Handle rapid value changes efficiently:

```csharp
private CancellationTokenSource _calculationCts;

private async void OnValueChangedWithDebounce(object sender, NumericEntryValueChangedEventArgs e)
{
    // Cancel previous calculation if still running
    _calculationCts?.Cancel();
    _calculationCts = new CancellationTokenSource();
    
    try
    {
        // Wait briefly to see if more changes are coming
        await Task.Delay(300, _calculationCts.Token);
        
        // Perform expensive calculation
        PerformComplexCalculation();
    }
    catch (TaskCanceledException)
    {
        // Calculation was cancelled, ignore
    }
}

private void PerformComplexCalculation()
{
    // Your calculation logic here
}
```

### Pattern 2: Validation on Change and Blur

Combine immediate feedback with final validation:

```csharp
private void OnValueChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    // Immediate feedback during typing
    ShowLiveValidation(e.NewValue);
}

private void OnUnfocused(object sender, FocusEventArgs e)
{
    // Final validation when leaving field
    PerformFinalValidation();
}

private void ShowLiveValidation(double? value)
{
    if (value.HasValue && value < 0)
    {
        warningLabel.Text = "⚠️ Negative values not recommended";
        warningLabel.IsVisible = true;
    }
    else
    {
        warningLabel.IsVisible = false;
    }
}

private void PerformFinalValidation()
{
    // Stricter validation on blur
    if (!numericEntry.Value.HasValue)
    {
        errorLabel.Text = "❌ This field is required";
        errorLabel.IsVisible = true;
    }
    else
    {
        errorLabel.IsVisible = false;
    }
}
```

### Pattern 3: Auto-Advance Form Fields

Automatically move to next field when valid:

```csharp
private void OnField1Changed(object sender, NumericEntryValueChangedEventArgs e)
{
    // Auto-advance when value is complete
    if (IsValidProductId(e.NewValue))
    {
        field2.Focus();
    }
}

private bool IsValidProductId(double? value)
{
    return value.HasValue && value >= 100 && value <= 999999;
}
```

### Pattern 4: Submit on Enter, Save on Blur

Different actions for different events:

```csharp
private void OnCompleted(object sender, EventArgs e)
{
    // Submit form when user presses Enter
    SubmitForm();
}

private void OnUnfocused(object sender, FocusEventArgs e)
{
    // Auto-save draft when user leaves field
    SaveDraft();
}

private async void SubmitForm()
{
    await DisplayAlert("Submitted", "Form submitted successfully", "OK");
}

private void SaveDraft()
{
    // Save to local storage
    Preferences.Set("DraftValue", numericEntry.Value ?? 0);
}
```

---

## Form Navigation and Submission

Complete example combining all concepts for multi-field forms.

**XAML:**
```xml
<ScrollView>
    <VerticalStackLayout Spacing="20" Padding="30">
        
        <Label Text="Product Registration"
               FontSize="24"
               FontAttributes="Bold"
               HorizontalOptions="Center"
               Margin="0,0,0,20" />
        
        <!-- Product ID -->
        <StackLayout Spacing="5">
            <Label Text="Product ID (Required):" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="productIdInput"
                                    Placeholder="Enter 6-digit ID"
                                    CustomFormat="000000"
                                    Minimum="100000"
                                    Maximum="999999"
                                    AllowNull="False"
                                    ReturnType="Next"
                                    ValueChanged="OnProductIdChanged"
                                    Completed="OnProductIdCompleted"
                                    Unfocused="ValidateProductId" />
            <Label x:Name="productIdError"
                   TextColor="Red"
                   FontSize="12"
                   IsVisible="False" />
        </StackLayout>
        
        <!-- Unit Price -->
        <StackLayout Spacing="5">
            <Label Text="Unit Price (Required):" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="priceInput"
                                    Placeholder="$0.00"
                                    CustomFormat="C2"
                                    Minimum="0.01"
                                    AllowNull="False"
                                    ReturnType="Next"
                                    Completed="OnPriceCompleted"
                                    Unfocused="ValidatePrice" />
            <Label x:Name="priceError"
                   TextColor="Red"
                   FontSize="12"
                   IsVisible="False" />
        </StackLayout>
        
        <!-- Quantity -->
        <StackLayout Spacing="5">
            <Label Text="Initial Stock (Required):" FontAttributes="Bold" />
            <editors:SfNumericEntry x:Name="stockInput"
                                    Value="1"
                                    CustomFormat="N0"
                                    Minimum="1"
                                    AllowNull="False"
                                    ReturnType="Done"
                                    Completed="OnStockCompleted"
                                    Unfocused="ValidateStock" />
            <Label x:Name="stockError"
                   TextColor="Red"
                   FontSize="12"
                   IsVisible="False" />
            <Label x:Name="stockWarning"
                   TextColor="Orange"
                   FontSize="12"
                   IsVisible="False" />
        </StackLayout>
        
        <!-- Buttons -->
        <Button Text="Submit Registration"
                Clicked="OnSubmitClicked"
                BackgroundColor="Green"
                TextColor="White"
                Margin="0,20,0,0" />
        
        <Button Text="Clear Form"
                Clicked="OnClearClicked"
                BackgroundColor="Gray"
                TextColor="White" />
        
        <!-- Status -->
        <Label x:Name="statusLabel"
               Text=""
               FontSize="14"
               HorizontalOptions="Center"
               Margin="0,10,0,0" />
        
    </VerticalStackLayout>
</ScrollView>
```

**Code-Behind:**
```csharp
// Auto-advance when Product ID is valid
private void OnProductIdChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue.HasValue && e.NewValue >= 100000 && e.NewValue <= 999999)
    {
        productIdError.IsVisible = false;
    }
}

private void OnProductIdCompleted(object sender, EventArgs e)
{
    // Move to price when Enter pressed
    priceInput.Focus();
}

private void ValidateProductId(object sender, FocusEventArgs e)
{
    if (!productIdInput.Value.HasValue || 
        productIdInput.Value < 100000 || 
        productIdInput.Value > 999999)
    {
        productIdError.Text = "Product ID must be 6 digits (100000-999999)";
        productIdError.IsVisible = true;
    }
    else
    {
        productIdError.IsVisible = false;
    }
}

// Price field navigation
private void OnPriceCompleted(object sender, EventArgs e)
{
    stockInput.Focus();
}

private void ValidatePrice(object sender, FocusEventArgs e)
{
    if (!priceInput.Value.HasValue || priceInput.Value < 0.01)
    {
        priceError.Text = "Price must be at least $0.01";
        priceError.IsVisible = true;
    }
    else
    {
        priceError.IsVisible = false;
    }
}

// Stock field - submit on Enter
private void OnStockCompleted(object sender, EventArgs e)
{
    // Submit form when Enter pressed on last field
    OnSubmitClicked(sender, e);
}

private void ValidateStock(object sender, FocusEventArgs e)
{
    if (!stockInput.Value.HasValue || stockInput.Value < 1)
    {
        stockError.Text = "Stock must be at least 1";
        stockError.IsVisible = true;
        stockWarning.IsVisible = false;
    }
    else if (stockInput.Value < 10)
    {
        stockError.IsVisible = false;
        stockWarning.Text = "⚠️ Low stock: Consider starting with more inventory";
        stockWarning.IsVisible = true;
    }
    else
    {
        stockError.IsVisible = false;
        stockWarning.IsVisible = false;
    }
}

// Form submission
private async void OnSubmitClicked(object sender, EventArgs e)
{
    // Hide previous status
    statusLabel.Text = "";
    statusLabel.TextColor = Colors.Black;
    
    // Validate all fields
    ValidateProductId(null, null);
    ValidatePrice(null, null);
    ValidateStock(null, null);
    
    // Check if any errors visible
    if (productIdError.IsVisible || priceError.IsVisible || stockError.IsVisible)
    {
        statusLabel.Text = "❌ Please fix errors above";
        statusLabel.TextColor = Colors.Red;
        
        // Focus first error field
        if (productIdError.IsVisible)
            productIdInput.Focus();
        else if (priceError.IsVisible)
            priceInput.Focus();
        else if (stockError.IsVisible)
            stockInput.Focus();
        
        return;
    }
    
    // All valid - submit
    statusLabel.Text = "Submitting...";
    statusLabel.TextColor = Colors.Orange;
    
    // Simulate submission
    await Task.Delay(1500);
    
    await DisplayAlert(
        "Registration Complete",
        $"Product {productIdInput.Value:000000} registered\n" +
        $"Price: {priceInput.Value:C}\n" +
        $"Stock: {stockInput.Value:N0}",
        "OK"
    );
    
    statusLabel.Text = "✅ Registration successful!";
    statusLabel.TextColor = Colors.Green;
    
    // Clear form after delay
    await Task.Delay(2000);
    OnClearClicked(sender, e);
}

// Clear form
private void OnClearClicked(object sender, EventArgs e)
{
    productIdInput.Value = null;
    priceInput.Value = null;
    stockInput.Value = 1;
    
    productIdError.IsVisible = false;
    priceError.IsVisible = false;
    stockError.IsVisible = false;
    stockWarning.IsVisible = false;
    
    statusLabel.Text = "";
    
    productIdInput.Focus();
}
```

---

## Best Practices

1. **Always check HasValue** when working with nullable values in ValueChanged
2. **Use Completed event for Enter key actions** (submit, navigate, search)
3. **Combine ValueChanged and Unfocused** for comprehensive validation
4. **Auto-advance fields** when values are complete and valid
5. **Provide immediate feedback** in ValueChanged for better UX
6. **Perform expensive operations** only on Unfocused to avoid lag
7. **Use Focus() method** to guide users through forms
8. **Implement debouncing** for rapid value changes with expensive calculations
9. **Clear error messages** when values become valid
10. **Test Enter key behavior** across all form fields

---

## Troubleshooting

**Issue:** ValueChanged fires twice for one user change
- **Solution:** This is expected - once for clearing, once for new value; check OldValue vs NewValue

**Issue:** Completed event doesn't fire
- **Solution:** Ensure ReturnType is set (Next, Done, Search, etc.) and Enter key is pressed

**Issue:** Focus() method doesn't work
- **Solution:** Ensure control is visible and enabled; try calling after page load

**Issue:** Can't distinguish user input from programmatic changes in ValueChanged
- **Solution:** Use a flag variable to track programmatic changes

**Issue:** Unfocused event doesn't fire on iOS
- **Solution:** Ensure control properly loses focus; may need platform-specific testing

---
