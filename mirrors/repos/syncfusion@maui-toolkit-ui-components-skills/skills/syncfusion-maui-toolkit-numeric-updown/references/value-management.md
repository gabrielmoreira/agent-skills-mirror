# Value Management & Constraints

## Table of Contents
- [Setting Initial Values](#setting-initial-values)
- [Binding Values](#binding-values)
- [Minimum and Maximum Constraints](#minimum-and-maximum-constraints)
- [AllowNull Property](#allownull-property)
- [Preventing Manual Text Editing](#preventing-manual-text-editing)
- [Handling Null Values](#handling-null-values)

## Setting Initial Values

### Static Value
Set the initial value directly in XAML or C#:

```xaml
<editors:SfNumericUpDown Value="50" />
```

```csharp
var numericUpDown = new SfNumericUpDown { Value = 50 };
```

### Default Behavior
- If `Value` is not specified: `null` (or `0` if `AllowNull` is `false`)
- The control displays an empty field

### Real-World Example
```xaml
<editors:SfNumericUpDown 
    x:Name="ageInput"
    Value="25"
    Placeholder="Age" />
```

## Binding Values

### MVVM Data Binding
Connect NumericUpDown to ViewModel properties using two-way binding:

**XAML:**
```xaml
<editors:SfNumericUpDown 
    Value="{Binding UserAge, Mode=TwoWay}" />
```

**ViewModel (C#):**
```csharp
public class UserViewModel : INotifyPropertyChanged
{
    private double _userAge;
    
    public double UserAge
    {
        get => _userAge;
        set
        {
            if (_userAge != value)
            {
                _userAge = value;
                OnPropertyChanged();
            }
        }
    }
    
    public event PropertyChangedEventHandler PropertyChanged;
    
    private void OnPropertyChanged([CallerMemberName] string propertyName = "")
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
}
```

**Code-Behind:**
```csharp
public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        BindingContext = new UserViewModel { UserAge = 25 };
    }
}
```

**Result:** When user changes the value in NumericUpDown, `UserAge` property updates automatically, and vice versa.

### String Formatting in Binding
Display the numeric value with custom formatting:

```xaml
<Label Text="{Binding Value, Source={x:Reference priceInput}, StringFormat='${0:F2}'}" />

<editors:SfNumericUpDown 
    x:Name="priceInput"
    CustomFormat="N2" />
```

## Minimum and Maximum Constraints

### Setting Range Limits
Restrict input to a specific numerical range:

```xaml
<editors:SfNumericUpDown 
    Value="50"
    Minimum="0"
    Maximum="100" />
```

```csharp
var numericUpDown = new SfNumericUpDown
{
    Value = 50,
    Minimum = 0,
    Maximum = 100
};
```

### Default Range
- `Minimum` = `double.MinValue` (approximately -1.79E+308)
- `Maximum` = `double.MaxValue` (approximately 1.79E+308)
- User can enter any numeric value within these bounds

### Behavior When User Exceeds Limits
- **During input:** Non-numeric characters are automatically filtered
- **On validation (OnLostFocus):** If value exceeds limits, it's automatically clamped:
  - Input: `150` with Maximum=`100` → Value becomes `100`
  - Input: `-10` with Minimum=`0` → Value becomes `0`

### Practical Examples

**Age Input (0-150):**
```xaml
<editors:SfNumericUpDown 
    Value="25"
    Minimum="0"
    Maximum="150"
    Placeholder="Enter age"
    CustomFormat="N0" />
```

**Price Input ($0-$10,000):**
```xaml
<editors:SfNumericUpDown 
    Value="99.99"
    Minimum="0"
    Maximum="10000"
    CustomFormat="C2" />
```

**Discount Percentage (0%-100%):**
```xaml
<editors:SfNumericUpDown 
    Value="25"
    Minimum="0"
    Maximum="100"
    CustomFormat="P0" />
```

**Temperature Range (-50°C to 50°C):**
```xaml
<editors:SfNumericUpDown 
    Value="20"
    Minimum="-50"
    Maximum="50"
    CustomFormat="N1"
    Placeholder="°C" />
```

## AllowNull Property

Controls whether the control accepts `null` values when cleared.

### AllowNull = true (Default)
When user clears the field, the value becomes `null`:

```xaml
<editors:SfNumericUpDown 
    AllowNull="True"
    Placeholder="Optional value" />
```

**Behavior:**
- User clears field → Value is `null`
- Field displays placeholder text (if set)
- `Value` property is `null` (not `0`)

**Best for:** Optional form fields

### AllowNull = false
When user clears the field, value defaults to:
- `0` (if no minimum is set)
- `Minimum` value (if minimum > 0)

```xaml
<editors:SfNumericUpDown 
    AllowNull="False"
    Minimum="10"
    Value="10" />
```

**Behavior:**
- User clears field → Value becomes `10` (the Minimum)
- Field is never empty
- Useful for ensuring a valid default

**Best for:** Required numeric fields with sensible defaults

### Important Interaction with Minimum

| AllowNull | Minimum | Clear Result |
|-----------|---------|--------------|
| `true` | Any | `null` |
| `false` | 0 | `0` |
| `false` | 15 | `15` |

**Example:**
```csharp
// Scenario 1: Optional field
var optional = new SfNumericUpDown 
{ 
    AllowNull = true,
    Value = null,
    Placeholder = "Optional quantity"
};

// Scenario 2: Required field with minimum
var required = new SfNumericUpDown
{
    AllowNull = false,
    Minimum = 1,
    Value = 1,
    Placeholder = "At least 1 item required"
};
```

## Preventing Manual Text Editing

Use the `IsEditable` property to restrict users to using only the up/down buttons:

### IsEditable = true (Default)
Users can:
- Type directly in the field
- Use up/down buttons
- Use arrow keys (↑↓)
- Use Page Up/Down keys
- Use mouse scroll wheel

```xaml
<editors:SfNumericUpDown 
    IsEditable="True"
    Value="50" />
```

### IsEditable = false
Users can ONLY:
- Click up/down buttons
- Use arrow keys (↑↓)
- Use Page Up/Down keys
- Use mouse scroll wheel

**Direct typing is DISABLED.**

```xaml
<editors:SfNumericUpDown 
    IsEditable="False"
    Value="50"
    Minimum="0"
    Maximum="100"
    SmallChange="5"
    Placeholder="Use arrows to adjust" />
```

### Practical Use Cases

**Button-Only Input (e.g., Rating):**
```xaml
<editors:SfNumericUpDown 
    IsEditable="False"
    Value="5"
    Minimum="1"
    Maximum="10"
    SmallChange="1"
    UpDownPlacementMode="Inline"
    Placeholder="Rating (1-10)" />
```

**Quantity Selector:**
```xaml
<editors:SfNumericUpDown 
    IsEditable="False"
    Value="1"
    Minimum="1"
    Maximum="999"
    SmallChange="1"
    LargeChange="10"
    Placeholder="Qty" />
```

### Why Use IsEditable=false?

- **Data integrity:** Prevents accidental typing errors
- **Guided input:** Forces users to use controlled increments
- **Accessibility:** Better for touch interfaces
- **Compliance:** Ensures values stay within defined ranges

## Handling Null Values

### Checking for Null
```csharp
var numericUpDown = new SfNumericUpDown { AllowNull = true };

// Check if value is null
if (numericUpDown.Value == null)
{
    // Handle null case
}

// Safe access with null coalescing
double value = numericUpDown.Value ?? 0.0;
```

### Event Handling with Null Values
```csharp
private void OnValueChanged(object sender, NumericEntryValueChangedEventArgs e)
{
    if (e.NewValue == null)
    {
        Console.WriteLine("Field cleared");
    }
    else
    {
        Console.WriteLine($"New value: {e.NewValue}");
    }
}
```

### Display Null Values
```xaml
<!-- Bind with fallback value -->
<Label Text="{Binding Path=Value, Source={x:Reference numInput}, StringFormat='Value: {0:N2}', TargetNullValue='No value'}" />
```

### Data Validation Pattern
```csharp
public bool ValidateInput(SfNumericUpDown control)
{
    if (control.AllowNull && control.Value == null)
    {
        // Optional field - null is valid
        return true;
    }
    
    if (!control.AllowNull && control.Value == null)
    {
        // Required field - null is invalid
        return false;
    }
    
    // Check range
    if (control.Value < control.Minimum || control.Value > control.Maximum)
    {
        return false;
    }
    
    return true;
}
```

---
