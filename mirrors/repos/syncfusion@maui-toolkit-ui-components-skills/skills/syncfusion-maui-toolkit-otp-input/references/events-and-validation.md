# Events and Validation in OTP Input

## Table of Contents
- [ValueChanged Event](#valuechanged-event)
- [Real-Time Validation Patterns](#real-time-validation-patterns)
- [OTP Completion Detection](#otp-completion-detection)
- [Error Handling Scenarios](#error-handling-scenarios)
- [Input Sanitization](#input-sanitization)
- [Common Validation Gotchas](#common-validation-gotchas)
- [Performance Optimization](#performance-optimization)

## ValueChanged Event

The `ValueChanged` event fires whenever the OTP value changes. This is the primary mechanism for monitoring user input in real-time.

### Event Structure

**Event Handler Signature:**
```csharp
private void OnValueChanged(object sender, OtpInputValueChangedEventArgs e)
{
    // e.NewValue - The new OTP value
    // e.OldValue - The previous OTP value (if needed)
}
```

### XAML Implementation

```xml
<otpInput:SfOtpInput x:Name="OtpInput"
                     Length="6"
                     Type="Number"
                     ValueChanged="OnValueChanged" />
```

**Code-Behind:**
```csharp
private void OnValueChanged(object sender, OtpInputValueChangedEventArgs e)
{
    Console.WriteLine($"Value changed: {e.OldValue} -> {e.NewValue}");
}
```

### C# Implementation

```csharp
var otpInput = new SfOtpInput { Length = 6 };

otpInput.ValueChanged += (s, e) =>
{
    Console.WriteLine($"Current value: {e.NewValue}");
};
```

### Event Args Properties

| Property | Type | Description |
|----------|------|-------------|
| `NewValue` | string | The new OTP value after user input |
| `OldValue` | string | The previous OTP value (for comparison) |

### Complete Event Handling Example

```csharp
public class OtpEventHandlingPage : ContentPage
{
    private SfOtpInput _otpInput;
    private Label _statusLabel;

    public OtpEventHandlingPage()
    {
        InitializeComponent();

        _statusLabel = new Label { Text = "Waiting for input..." };

        _otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number
        };

        _otpInput.ValueChanged += OnOtpValueChanged;

        Content = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children = { _otpInput, _statusLabel }
        };
    }

    private void OnOtpValueChanged(object sender, OtpInputValueChangedEventArgs e)
    {
        // Track progress
        int filledCount = e.NewValue?.Length ?? 0;
        int totalCount = (int)_otpInput.Length;

        _statusLabel.Text = $"Progress: {filledCount}/{totalCount}";

        if (filledCount == totalCount)
        {
            _statusLabel.Text = $"Complete! Code: {e.NewValue}";
        }
    }
}
```

## Real-Time Validation Patterns

Implement validation logic that runs as the user types, providing immediate feedback.

### Pattern 1: Character Validation

Validate each character as it's entered:

```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number
};

otpInput.ValueChanged += (s, e) =>
{
    // Validate each character
    if (!string.IsNullOrEmpty(e.NewValue))
    {
        if (!e.NewValue.All(c => char.IsDigit(c)))
        {
            DisplayAlert("Invalid", "Only numbers allowed", "OK");
            otpInput.Value = e.OldValue;  // Revert to previous value
        }
    }
};
```

### Pattern 2: Format Validation

Validate the complete format:

```csharp
 otpInput.ValueChanged += async (s, e) =>
 {
     if (e.NewValue?.Length == 6)
     {
         // Validate format (e.g., not all same digit)
         if (e.NewValue.Distinct().Count() == 1)
         {
             await DisplayAlert("Warning", "Code appears invalid (all same digits)", "OK");
         }
     }
 };
```

### Pattern 3: Server-Side Validation

Validate against backend service as user completes entry:

```csharp
private bool _isValidating = false;

otpInput.ValueChanged += async (s, e) =>
{
    if (e.NewValue?.Length == 6 && !_isValidating)
    {
        _isValidating = true;
        otpInput.IsEnabled = false;

        try
        {
            bool isValid = await ValidateOtpAsync(e.NewValue);
            if (isValid)
            {
                await DisplayAlert("Success", "Valid code!", "OK");
            }
            else
            {
                await DisplayAlert("Error", "Invalid code", "OK");
                otpInput.Value = string.Empty;
            }
        }
        finally
        {
            _isValidating = false;
            otpInput.IsEnabled = true;
        }
    }
};
```

## OTP Completion Detection

Detect when the user has entered a complete OTP code.

### Basic Completion Detection

```csharp
otpInput.ValueChanged += (s, e) =>
{
    // Check if OTP is complete
    if (e.NewValue?.Length == otpInput.Length)
    {
        OnOtpComplete(e.NewValue);
    }
};

private async Task OnOtpComplete(string otp)
{
    Console.WriteLine($"OTP Complete: {otp}");
    // Auto-submit or wait for user action
}
```

### Auto-Submit on Completion

```csharp
private bool _isVerifying = false;

otpInput.ValueChanged += async (s, e) =>
{
    if (e.NewValue?.Length == 6 && !_isVerifying)
    {
        _isVerifying = true;
        await AutoVerifyOtp(e.NewValue);
        _isVerifying = false;
    }
};

private async Task AutoVerifyOtp(string otp)
{
    try
    {
        bool isValid = await AuthService.VerifyOtpAsync(otp);
        if (isValid)
        {
            await DisplayAlert("Success", "Verified automatically!", "OK");
            await Navigation.PopAsync();
        }
        else
        {
            await DisplayAlert("Error", "Invalid code. Please try again.", "OK");
            otpInput.Value = string.Empty;
        }
    }
    catch (Exception ex)
    {
        await DisplayAlert("Error", $"Verification failed: {ex.Message}", "OK");
    }
}
```

### Completion with Timeout

```csharp
private DateTime _completionTime;

otpInput.ValueChanged += (s, e) =>
{
    if (e.NewValue?.Length == 6)
    {
        _completionTime = DateTime.Now;
        MainThread.BeginInvokeOnMainThread(async () =>
        {
            await Task.Delay(5000);  // Wait 5 seconds before auto-submit
            if (DateTime.Now.Subtract(_completionTime).TotalSeconds <= 5.1)
            {
                // Submit if no further changes in 5 seconds
                await VerifyOtpAsync(otpInput.Value);
            }
        });
    }
};
```

## Error Handling Scenarios

Handle various error conditions gracefully.

### Scenario 1: Invalid Character Input

```csharp
otpInput.ValueChanged += async (s, e) =>
{
    if (e.NewValue != null && e.NewValue.Length > e.OldValue?.Length)
    {
        // User added a character
        char newChar = e.NewValue[^1];  // Last character

        if (otpInput.Type == OtpInputType.Number && !char.IsDigit(newChar))
        {
            // Invalid character for numeric OTP
            otpInput.Value = e.OldValue;
            await DisplayAlert("Invalid", "Only numbers allowed", "OK");
        }
    }
};
```

### Scenario 2: Network Verification Failure

```csharp
private async Task HandleVerificationFailure(Exception ex)
{
    if (ex is HttpRequestException)
    {
        await DisplayAlert("Network Error", "Unable to verify. Please check connection.", "OK");
    }
    else if (ex is TimeoutException)
    {
        await DisplayAlert("Timeout", "Verification took too long. Please try again.", "OK");
    }
    else
    {
        await DisplayAlert("Error", $"Verification failed: {ex.Message}", "OK");
    }

    // Allow user to retry
    otpInput.Value = string.Empty;
    otpInput.Focus();
}
```

### Scenario 3: Expired OTP Code

```csharp
private DateTime _otpIssuedTime;
private const int OTP_EXPIRATION_MINUTES = 5;

public void OnOtpGenerated()
{
    _otpIssuedTime = DateTime.Now;
    _otpInput.Value = string.Empty;
}

private bool IsOtpExpired()
{
    return DateTime.Now.Subtract(_otpIssuedTime).TotalMinutes > OTP_EXPIRATION_MINUTES;
}

private async void OnVerifyClicked(object sender, EventArgs e)
{
    if (IsOtpExpired())
    {
        await DisplayAlert("Expired", "OTP has expired. Please request a new code.", "OK");
        _otpInput.IsEnabled = false;
        return;
    }

    // Proceed with verification
}
```

### Scenario 4: Maximum Retry Attempts

```csharp
private int _attemptCount = 0;
private const int MAX_ATTEMPTS = 3;
private const int LOCKOUT_MINUTES = 15;
private DateTime _lastAttemptTime;

private async void OnVerifyClicked(object sender, EventArgs e)
{
    // Check if locked out
    if (_attemptCount >= MAX_ATTEMPTS)
    {
        var timeSinceLastAttempt = DateTime.Now.Subtract(_lastAttemptTime);
        if (timeSinceLastAttempt.TotalMinutes < LOCKOUT_MINUTES)
        {
            int remainingMinutes = LOCKOUT_MINUTES - (int)timeSinceLastAttempt.TotalMinutes;
            await DisplayAlert("Locked", 
                $"Too many attempts. Try again in {remainingMinutes} minutes.", 
                "OK");
            return;
        }
        
        // Reset after lockout period
        _attemptCount = 0;
    }

    _lastAttemptTime = DateTime.Now;
    _attemptCount++;

    bool isValid = await VerifyOtpAsync(_otpInput.Value);
    if (!isValid && _attemptCount >= MAX_ATTEMPTS)
    {
        _otpInput.IsEnabled = false;
        await DisplayAlert("Locked", "Too many failed attempts", "OK");
    }
}
```

## Input Sanitization

Clean and normalize input to prevent issues.

### Whitespace Removal

```csharp
otpInput.ValueChanged += (s, e) =>
{
    if (e.NewValue != null && e.NewValue.Contains(" "))
    {
        // Remove spaces if separator is used
        string sanitized = e.NewValue.Replace(" ", "");
        otpInput.Value = sanitized;
    }
};
```

### Case Normalization (for Text type)

```csharp
otpInput.ValueChanged += (s, e) =>
{
    if (otpInput.Type == OtpInputType.Text && e.NewValue != null)
    {
        // Normalize to uppercase for case-insensitive comparison
        string normalized = e.NewValue.ToUpper();
        if (normalized != e.NewValue)
        {
            otpInput.Value = normalized;
        }
    }
};
```

### Leading Zero Handling

```csharp
private string SanitizeOtp(string otp)
{
    if (string.IsNullOrEmpty(otp))
        return otp;

    // Remove non-numeric characters
    string cleaned = new string(otp.Where(char.IsDigit).ToArray());
    
    // Pad with leading zeros if needed
    return cleaned.PadLeft((int)otpInput.Length, '0');
}
```

## Common Validation Gotchas

### Gotcha 1: Event Fires During Programmatic Updates

```csharp
// PROBLEM: Setting Value triggers ValueChanged event
_updating = true;
otpInput.Value = "123456";  // Triggers ValueChanged
_updating = false;

// SOLUTION: Check flag in event handler
otpInput.ValueChanged += (s, e) =>
{
    if (_updating) return;  // Skip if programmatic update
    
    // Handle user input
};
```

### Gotcha 2: Async Operations in Event Handler

```csharp
// PROBLEM: Async operations can cause race conditions
otpInput.ValueChanged += async (s, e) =>
{
    await VerifyOtpAsync(e.NewValue);  // Long operation
    // User might change input before completion
};

// SOLUTION: Use cancellation token or flag
private CancellationTokenSource _verificationCts;

otpInput.ValueChanged += async (s, e) =>
{
    _verificationCts?.Cancel();
    _verificationCts = new CancellationTokenSource();
    
    try
    {
        await VerifyOtpAsync(e.NewValue, _verificationCts.Token);
    }
    catch (OperationCanceledException)
    {
        // Verification was cancelled (user entered new input)
    }
};
```

### Gotcha 3: Multiple Event Handlers

```csharp
// PROBLEM: Multiple handlers can interfere
otpInput.ValueChanged += Handler1;
otpInput.ValueChanged += Handler2;  // Both called on every change

// SOLUTION: Use single handler or coordinate handlers
private void OnValueChanged(object sender, OtpInputValueChangedEventArgs e)
{
    ValidateInput(e.NewValue);
    UpdateUI(e.NewValue);
    CheckCompletion(e.NewValue);
}
```

### Gotcha 4: Value Property Returns Incomplete Input

```csharp
// PROBLEM: Checking value before it's complete
otpInput.ValueChanged += (s, e) =>
{
    if (otpInput.Value.Length == 6)  // May not be true yet
    {
        VerifyOtp(otpInput.Value);
    }
};

// SOLUTION: Use event args NewValue which is already updated
otpInput.ValueChanged += async (s, e) =>
{
    if (e.NewValue?.Length == 6)  // Use e.NewValue
    {
        await VerifyOtp(e.NewValue);
    }
};
```

## Performance Optimization

Optimize event handling for better performance.

### Debounce Rapid Events

```csharp
private DateTime _lastValidationTime;
private const int VALIDATION_DELAY_MS = 300;

otpInput.ValueChanged += (s, e) =>
{
    // Skip if called too recently
    if (DateTime.Now.Subtract(_lastValidationTime).TotalMilliseconds < VALIDATION_DELAY_MS)
        return;

    _lastValidationTime = DateTime.Now;
    PerformValidation(e.NewValue);
};
```

### Batch Multiple Operations

```csharp
private void OnValueChanged(object sender, OtpInputValueChangedEventArgs e)
{
    // Perform all operations at once
    var validationResult = ValidateFormat(e.NewValue);
    var sanitized = SanitizeInput(e.NewValue);
    var displayText = FormatForDisplay(sanitized);

    // Update UI in single batch
    MainThread.BeginInvokeOnMainThread(() =>
    {
        UpdateValidationUI(validationResult);
        UpdateDisplayUI(displayText);
    });
}
```

### Minimize UI Updates

```csharp
private string _previousDisplayValue;

otpInput.ValueChanged += (s, e) =>
{
    string displayValue = FormatValue(e.NewValue);
    
    // Only update if display actually changed
    if (displayValue != _previousDisplayValue)
    {
        _statusLabel.Text = displayValue;
        _previousDisplayValue = displayValue;
    }
};
```

## Complete Validation Example

```csharp
public class CompleteValidationPage : ContentPage
{
    private SfOtpInput _otpInput;
    private Label _statusLabel;
    private Button _verifyButton;
    private int _attemptCount = 0;
    private const int MAX_ATTEMPTS = 3;

    public CompleteValidationPage()
    {
        InitializeComponent();

        _statusLabel = new Label { Text = "Enter 6-digit OTP" };
        
        _otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number,
            StylingMode = OtpInputStyle.Outlined
        };

        _verifyButton = new Button { Text = "Verify" };

        _otpInput.ValueChanged += OnOtpValueChanged;
        _verifyButton.Clicked += OnVerifyClicked;

        Content = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children = { _statusLabel, _otpInput, _verifyButton }
        };
    }

    private void OnOtpValueChanged(object sender, OtpInputValueChangedEventArgs e)
    {
        int filled = e.NewValue?.Length ?? 0;
        _statusLabel.Text = $"Progress: {filled}/6";

        if (filled == 6)
        {
            _statusLabel.Text = "Complete! Ready to verify.";
        }
    }

    private async void OnVerifyClicked(object sender, EventArgs e)
    {
        if (_attemptCount >= MAX_ATTEMPTS)
        {
            await DisplayAlert("Locked", "Too many attempts", "OK");
            return;
        }

        if (_otpInput.Value?.Length != 6)
        {
            await DisplayAlert("Error", "Please enter complete OTP", "OK");
            return;
        }

        _verifyButton.IsEnabled = false;

        try
        {
            bool isValid = await VerifyOtpAsync(_otpInput.Value);
            if (isValid)
            {
                await DisplayAlert("Success", "Verified!", "OK");
            }
            else
            {
                _attemptCount++;
                _statusLabel.Text = $"Invalid. Attempts remaining: {MAX_ATTEMPTS - _attemptCount}";
                _otpInput.Value = string.Empty;
            }
        }
        finally
        {
            _verifyButton.IsEnabled = true;
        }
    }

    private async Task<bool> VerifyOtpAsync(string otp)
    {
        return await AuthService.VerifyAsync(otp);
    }
}
```