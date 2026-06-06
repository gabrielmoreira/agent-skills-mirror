# Features and Configuration in OTP Input

## Table of Contents
- [Length Configuration](#length-configuration)
- [Separator Property](#separator-property)
- [Value Binding and Retrieval](#value-binding-and-retrieval)
- [Disabled State](#disabled-state)
- [AutoFocus Property](#autofocus-property)
- [Focus Management](#focus-management)
- [Placeholder Property](#placeholder-property)
- [InputState Property](#inputstate-property)
- [Horizontal Alignment](#horizontal-alignment)
- [Multi-Platform Considerations](#multi-platform-considerations)

## Length Configuration

The `Length` property defines the number of input fields in the OTP Input component. This directly impacts the expected OTP code length and user experience.

### Setting Length

**XAML:**
```xml
<otpInput:SfOtpInput Length="6" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6  // Creates 6 input fields
};
```

### Recommended Length Values

| Use Case | Length | Reason |
|----------|--------|--------|
| SMS OTP (standard) | 4-6 | Industry standard for SMS verification |
| Email verification | 6-8 | Longer codes for higher security |
| API tokens | 8-12 | Maximum entropy for access tokens |
| Phone confirmation | 4 | Quick PIN-like verification |
| High-security scenarios | 10+ | Extended codes for sensitive operations |

### Example: Dynamic Length Based on Code Type

```csharp
public class OtpLengthPage : ContentPage
{
    public OtpLengthPage()
    {
        InitializeComponent();
        
        var codePicker = new Picker
        {
            Title = "Select Code Type",
            ItemsSource = new List<string> 
            { 
                "SMS (6 digits)", 
                "Email (8 chars)", 
                "API Token (12 chars)" 
            }
        };

        var otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number
        };

        codePicker.SelectedIndexChanged += (s, e) =>
        {
            switch (codePicker.SelectedIndex)
            {
                case 0:
                    otpInput.Length = 6;
                    otpInput.Type = OtpInputType.Number;
                    break;
                case 1:
                    otpInput.Length = 8;
                    otpInput.Type = OtpInputType.Text;
                    break;
                case 2:
                    otpInput.Length = 12;
                    otpInput.Type = OtpInputType.Text;
                    break;
            }
            otpInput.Value = string.Empty;  // Reset on type change
        };

        Content = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children = { codePicker, otpInput }
        };
    }
}
```

### Important Considerations

- **Minimum length:** 1 (practically, at least 4 for security)
- **Maximum length:** No hard limit, but 12+ becomes tedious for manual entry
- **Performance:** Each field requires resources; keep lengths reasonable
- **Responsiveness:** Longer codes may not fit on small screens without scrolling

## Separator Property

The `Separator` property adds a visual character or symbol between input fields, improving visual organization and user comprehension.

### Setting Separator

**XAML:**
```xml
<otpInput:SfOtpInput Length="6" 
                     Separator="-" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Separator = "-"  // Display as 123-456
};
```

### Common Separator Characters

| Separator | Use Case | Example |
|-----------|----------|---------|
| `-` (hyphen) | Phone number style | 123-456 |
| ` ` (space) | Natural spacing | 123 456 |
| `-` with length 4 | PIN format | 12-34 |
| `:` | Time format | 12:34 |
| `/` | Code format | 123/456 |
| Empty string | No separator | 123456 |

### Visual Examples

**Without Separator:**
```
[1][2][3][4][5][6]
```

**With Hyphen Separator:**
```
[1][2][3] - [4][5][6]
```

**With Space Separator:**
```
[1][2][3]   [4][5][6]
```

### Implementation Examples

**Phone Verification with Hyphen:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    Separator = "-"  // Looks like: 123-456
};
```

**Time-Based Code with Colon:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    Separator = ":"  // Looks like: 12:34:56
};
```

**Alphanumeric with Space:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 8,
    Type = OtpInputType.Text,
    Separator = " "  // Looks like: ABCD 1234
};
```

### Separator with Value Retrieval

The `Value` property returns the raw value **without separators**:

```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Separator = "-"
};

// User enters: 1 2 3 4 5 6 (displayed as 123-456 with separator)
string value = otpInput.Value;  // Returns "123456" (no separator)
Console.WriteLine(value);       // Output: 123456
```

### Important Note on Separators

- Separators are **visual only** — they don't affect the stored value
- Value property always returns the raw digits/characters without separators
- Separator characters are **not** user-editable
- Use empty string `""` to remove separator

## Value Binding and Retrieval

The `Value` property stores the current OTP code. You can both read and write values programmatically.

### Reading Values

**XAML with Code-Behind:**
```xml
<otpInput:SfOtpInput x:Name="OtpInput" Length="6" />
```

**C# Code:**
```csharp
string enteredCode = OtpInput.Value;
```

### Writing Values

**Set Initial Value in XAML:**
```xml
<otpInput:SfOtpInput Length="6" 
                     Value="123456" />
```

**Set Value in C#:**
```csharp
OtpInput.Value = "123456";
```

### Value Binding Pattern

**XAML with Two-Way Binding:**
```xml
<otpInput:SfOtpInput Length="6" 
                     Value="{Binding OtpCode, Mode=TwoWay}" />
```

**ViewModel:**
```csharp
public class OtpViewModel : INotifyPropertyChanged
{
    private string _otpCode;
    
    public string OtpCode
    {
        get => _otpCode;
        set
        {
            if (_otpCode != value)
            {
                _otpCode = value;
                OnPropertyChanged(nameof(OtpCode));
            }
        }
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected void OnPropertyChanged(string name)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }
}
```

### Complete Verification Example

```csharp
public class VerificationPage : ContentPage
{
    private SfOtpInput _otpInput;

    public VerificationPage()
    {
        InitializeComponent();
        
        _otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number
        };

        var verifyButton = new Button { Text = "Verify OTP" };
        verifyButton.Clicked += OnVerifyClicked;

        Content = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children = { _otpInput, verifyButton }
        };
    }

    private async void OnVerifyClicked(object sender, EventArgs e)
    {
        // Read the entered OTP
        string enteredOtp = _otpInput.Value;

        // Validate before sending to server
        if (string.IsNullOrEmpty(enteredOtp) || enteredOtp.Length != 6)
        {
            await DisplayAlert("Error", "Please enter a complete 6-digit code", "OK");
            return;
        }

        // Verify with backend
        bool isValid = await VerifyOtpAsync(enteredOtp);
        if (isValid)
        {
            await DisplayAlert("Success", "OTP verified", "OK");
            await Navigation.PopAsync();
        }
        else
        {
            await DisplayAlert("Error", "Invalid OTP code", "OK");
            _otpInput.Value = string.Empty;  // Clear for retry
        }
    }

    private async Task<bool> VerifyOtpAsync(string otp)
    {
        return await AuthService.VerifyAsync(otp);
    }
}
```

## Disabled State

The `IsEnabled` property controls whether users can interact with the OTP Input component.

### Disabling the Component

**XAML:**
```xml
<otpInput:SfOtpInput IsEnabled="False" />
```

**C#:**
```csharp
otpInput.IsEnabled = false;
```

### Use Cases for Disabled State

1. **During verification:** Disable while checking OTP validity
2. **After maximum attempts:** Prevent further entry after failures
3. **Form submission:** Disable until prerequisites met
4. **Time-based expiration:** Disable if code has expired

### Example: Disable During Verification

```csharp
var otpInput = new SfOtpInput { Length = 6 };
var verifyButton = new Button { Text = "Verify" };

verifyButton.Clicked += async (s, e) =>
{
    // Disable input during verification
    otpInput.IsEnabled = false;
    verifyButton.IsEnabled = false;

    try
    {
        bool valid = await VerifyOtpAsync(otpInput.Value);
        if (valid)
        {
            await DisplayAlert("Success", "Verified!", "OK");
        }
    }
    finally
    {
        // Re-enable if verification failed
        otpInput.IsEnabled = true;
        verifyButton.IsEnabled = true;
    }
};
```

### Example: Disable After Failed Attempts

```csharp
private int _attemptCount = 0;
private const int MAX_ATTEMPTS = 3;

private async void OnVerifyClicked(object sender, EventArgs e)
{
    if (_attemptCount >= MAX_ATTEMPTS)
    {
        _otpInput.IsEnabled = false;
        await DisplayAlert("Locked", "Too many attempts. Please try again later.", "OK");
        return;
    }

    bool isValid = await VerifyOtpAsync(_otpInput.Value);
    if (!isValid)
    {
        _attemptCount++;
        if (_attemptCount >= MAX_ATTEMPTS)
        {
            _otpInput.IsEnabled = false;
        }
    }
}
```

## AutoFocus Property

The `AutoFocus` property automatically sets focus to the OTP Input component when it loads, improving user experience by allowing immediate input without manual focus.

### Setting AutoFocus

**XAML:**
```xml
<otpInput:SfOtpInput AutoFocus="True" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    AutoFocus = true  // Focus automatically when loaded
};
```

### Use Cases
- Single-purpose OTP verification screens
- Confirmation pages where OTP is the primary action
- Streamlined authentication flows
- Mobile apps where keyboard should appear immediately

### Example: Instant Verification Flow

```csharp
public class QuickVerificationPage : ContentPage
{
    public QuickVerificationPage()
    {
        InitializeComponent();

        var otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number,
            AutoFocus = true,  // Keyboard appears automatically
            StylingMode = OtpInputStyle.Outlined
        };

        otpInput.ValueChanged += async (s, e) =>
        {
            if (e.NewValue?.Length == 6)
            {
                // Auto-verify when complete
                bool isValid = await VerifyOtpAsync(e.NewValue);
                if (isValid)
                {
                    await DisplayAlert("Success", "Verified!", "OK");
                }
            }
        };

        Content = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children =
            {
                new Label { Text = "Enter 6-Digit Code", FontSize = 20 },
                otpInput
            }
        };
    }

    private async Task<bool> VerifyOtpAsync(string otp)
    {
        return await AuthService.VerifyAsync(otp);
    }
}
```

### Important Notes
- **AutoFocus on first load only** — Does not re-focus if focus is lost elsewhere
- **Keyboard behavior** — Keyboard automatically appears on mobile devices
- **Accessibility** — Be aware that auto-focus may bypass screen reader announcements
- **Conditional autofocus** — Only set true when OTP input is the primary action on the page

### Programmatic Focus Management

```csharp
// Manually set focus after other operations
var otpInput = new SfOtpInput { Length = 6 };

// Focus programmatically
otpInput.Focus();

// Or after an async operation
async void OnRetryClicked(object sender, EventArgs e)
{
    otpInput.Value = string.Empty;
    await Task.Delay(100);  // Brief delay for UI update
    otpInput.Focus();  // Return focus for retry
}
```

## Focus Management

Control focus behavior to improve user experience and guide input flow. Beyond AutoFocus, you can manage focus programmatically and in response to user actions.

### Setting Focus

**C#:**
```csharp
otpInput.Focus();  // Set focus to OTP input
```

### Auto-Focus Pattern

```csharp
public class OtpPage : ContentPage
{
    public OtpPage()
    {
        InitializeComponent();
        
        var otpInput = new SfOtpInput 
        { 
            Length = 6,
            AutoFocus = true  // Alternative to manual focus
        };

        // Or manually focus when page appears
        Loaded += (s, e) =>
        {
            // otpInput.Focus();  // If not using AutoFocus
        };
    }
}
```

### Focus After Error

```csharp
private async void OnVerifyClicked(object sender, EventArgs e)
{
    if (OtpInput.Value?.Length != 6)
    {
        await DisplayAlert("Error", "Please enter complete OTP", "OK");
        OtpInput.Focus();  // Return focus for correction
        return;
    }
}
```

### Focus Recovery Pattern

```csharp
var otpInput = new SfOtpInput { Length = 6 };

otpInput.ValueChanged += async (s, e) =>
{
    if (e.NewValue?.Length == 6)
    {
        bool isValid = await VerifyOtpAsync(e.NewValue);
        if (!isValid)
        {
            otpInput.Value = string.Empty;
            otpInput.Focus();  // Maintain focus for retry
        }
    }
};
```

## Placeholder Property

The `Placeholder` property shows a hint character in empty input fields, helping users understand what they need to enter.

### Setting Placeholder

**XAML:**
```xml
<otpInput:SfOtpInput Length="6"
                     Placeholder="0" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Placeholder = "0"  // Shows "0" in empty fields
};
```

### Common Placeholder Values

| Placeholder | Use Case | Display |
|------------|----------|---------|
| `"0"` | Numeric OTP | [0][0][0][0][0][0] |
| `"-"` | Visual separator hint | [-][-][-][-][-][-] |
| `"*"` | Generic character | [*][*][*][*][*][*] |
| `" "` | Space (minimal hint) | [ ][ ][ ][ ][ ][ ] |

### Example: Numeric Placeholder

```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    Placeholder = "0",  // Helps users understand numeric input
    PlaceholderColor = Colors.LightGray
};
```

## InputState Property

The `InputState` property controls the current state of the input component, allowing you to visually reflect different states like normal, focused, error, or disabled states.

### Input States

| State | Purpose | Use Case |
|-------|---------|----------|
| `Normal` | Default appearance | Standard input state |
| `Focused` | Highlighted state | When input has focus |
| `Error` | Error appearance | Invalid OTP |
| `Disabled` | Inactive state | Verification in progress or locked |

### Setting InputState

**C#:**
```csharp
var otpInput = new SfOtpInput { Length = 6 };

// Normal state (default)
otpInput.InputState = OtpInputState.Default;

// Warning state
otpInput.InputState = OtpInputState.Warning;

// Error state
otpInput.InputState = OtpInputState.Error;

// Success state
otpInput.InputState = OtpInputState.Success;
```

### Example: State Management

```csharp
public class StateManagementOtpPage : ContentPage
{
    private SfOtpInput _otpInput;

    public StateManagementOtpPage()
    {
        InitializeComponent();

        _otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number,
            InputState = OtpInputState.Default  // Initial state
        };

        var verifyButton = new Button { Text = "Verify" };
        verifyButton.Clicked += OnVerifyClicked;

        Content = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children = { _otpInput, verifyButton }
        };
    }

    private async void OnVerifyClicked(object sender, EventArgs e)
    {
        // Show loading state
        _otpInput.InputState = OtpInputState.Default;

        try
        {
            bool isValid = await VerifyOtpAsync(_otpInput.Value);

            if (isValid)
            {
                // Show success (can keep disabled or reset to normal)
                _otpInput.InputState = OtpInputState.Success;
                await DisplayAlert("Success", "Verified!", "OK");
            }
            else
            {
                // Show error state
                _otpInput.InputState = OtpInputState.Error;
                await DisplayAlert("Error", "Invalid OTP", "OK");

                // Reset for retry
                _otpInput.Value = string.Empty;
                _otpInput.InputState = OtpInputState.Default;
            }
        }
        finally
        {
            // Ensure not left in disabled state
            if (_otpInput.InputState == OtpInputState.Default)
            {
                _otpInput.InputState = OtpInputState.Default;
            }
        }
    }

    private async Task<bool> VerifyOtpAsync(string otp)
    {
        return await AuthService.VerifyAsync(otp);
    }
}
```

### Visual State Indicators

```csharp
var stackLayout = new VerticalStackLayout
{
    Spacing = 15,
    Children =
    {
        // Normal state
        new VerticalStackLayout
        {
            Children =
            {
                new Label { Text = "Default State", FontSize = 12, TextColor = Colors.Gray },
                new SfOtpInput { Length = 6, InputState = OtpInputState.Default }
            }
        },
        
        // Focused state
        new VerticalStackLayout
        {
            Children =
            {
                new Label { Text = "Success State", FontSize = 12, TextColor = Colors.Gray },
                new SfOtpInput { Length = 6, InputState = OtpInputState.Success }
            }
        },
        
        // Error state
        new VerticalStackLayout
        {
            Children =
            {
                new Label { Text = "Error State", FontSize = 12, TextColor = Colors.Red },
                new SfOtpInput { Length = 6, InputState = OtpInputState.Error }
            }
        }
    }
};
```

## Horizontal Alignment

Control the horizontal positioning of the OTP Input within its container.

### Alignment Options

**XAML:**
```xml
<!-- Center alignment -->
<otpInput:SfOtpInput HorizontalOptions="Center" />

<!-- Start (left) alignment -->
<otpInput:SfOtpInput HorizontalOptions="Start" />

<!-- End (right) alignment -->
<otpInput:SfOtpInput HorizontalOptions="End" />

<!-- Fill available space -->
<otpInput:SfOtpInput HorizontalOptions="Fill" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    HorizontalOptions = LayoutOptions.Center
};
```

## Multi-Platform Considerations

### Platform-Specific Behavior

**Windows:**
- Full feature support
- All styling modes render correctly
- Standard keyboard input

**iOS:**
- Material Design styling may vary
- Platform keyboard conventions apply
- Touch keyboard optimizations

**Android:**
- Material Design compliance
- System keyboard used
- Platform conventions followed

**macOS:**
- Similar to iOS implementation
- Standard keyboard input
- macOS design conventions

### Testing on Platforms

```csharp
public class PlatformSpecificOtpPage : ContentPage
{
    public PlatformSpecificOtpPage()
    {
        InitializeComponent();
        
        var otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number
        };

        // Adjust based on platform
        if (DeviceInfo.Platform == DevicePlatform.iOS)
        {
            otpInput.StylingMode = OtpInputStyle.Filled;
        }
        else if (DeviceInfo.Platform == DevicePlatform.Android)
        {
            otpInput.StylingMode = OtpInputStyle.Outlined;
        }

        Content = otpInput;
    }
}
```

## Complete Configuration Example

```csharp
public class FullConfiguredOtpPage : ContentPage
{
    public FullConfiguredOtpPage()
    {
        InitializeComponent();

        var otpInput = new SfOtpInput
        {
            // Length and type
            Length = 6,
            Type = OtpInputType.Number,
            
            // Styling
            StylingMode = OtpInputStyle.Outlined,
            
            // Separator
            Separator = "-",
            
            // Appearance
            HorizontalOptions = LayoutOptions.Center,
            Padding = new Thickness(10),
            
            // Interactivity
            IsEnabled = true
        };

        var verifyButton = new Button { Text = "Verify" };
        verifyButton.Clicked += async (s, e) =>
        {
            if (otpInput.Value?.Length == 6)
            {
                bool valid = await VerifyOtpAsync(otpInput.Value);
                if (valid)
                {
                    await DisplayAlert("Success", "Verified!", "OK");
                    otpInput.Value = string.Empty;
                }
                else
                {
                    await DisplayAlert("Error", "Invalid code", "OK");
                }
            }
        };

        Content = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children =
            {
                new Label { Text = "Enter 6-Digit Code", FontSize = 20 },
                otpInput,
                verifyButton
            }
        };
    }

    private async Task<bool> VerifyOtpAsync(string otp)
    {
        return await AuthService.VerifyAsync(otp);
    }
}
```
