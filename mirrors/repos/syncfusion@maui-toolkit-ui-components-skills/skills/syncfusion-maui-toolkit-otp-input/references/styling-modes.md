# Styling Modes in OTP Input

## Table of Contents
- [Overview](#overview)
- [Outlined Mode](#outlined-mode)
- [Filled Mode](#filled-mode)
- [Underlined Mode](#underlined-mode)
- [Color and Visual Customization](#color-and-visual-customization)
  - [InputBackground Property](#inputbackground-property)
  - [TextColor Property](#textcolor-property)
  - [Stroke Property](#stroke-property)
  - [PlaceholderColor Property](#placeholdercolor-property)
- [Size and Spacing Customization](#size-and-spacing-customization)
  - [BoxHeight Property](#boxheight-property)
  - [BoxWidth Property](#boxwidth-property)
  - [Responsive Size Adjustment](#responsive-size-adjustment)
- [Styling Mode Selection Guide](#styling-mode-selection-guide)
- [Custom Styling Considerations](#custom-styling-considerations)

## Overview

The `StylingMode` property controls the visual appearance of OTP input fields. Three distinct styling modes are available, each providing a different visual aesthetic:

1. **Outlined** — Fields have a border around them (default)
2. **Filled** — Fields have a background fill color
3. **Underlined** — Fields have only an underline (Material Design style)

Choosing the right styling mode depends on your app's design language and user interface guidelines.

## Outlined Mode

The **Outlined** mode displays input fields with a visible border around each field. This is the default styling mode and provides clear visual separation between input fields.

### When to Use
- Material Design 3 style applications
- Designs requiring high visual contrast
- Professional/enterprise applications
- Default choice when unsure

### Implementation

**XAML:**
```xml
<otpInput:SfOtpInput x:Name="OutlinedOtp"
                     Length="6"
                     Type="Number"
                     StylingMode="Outlined" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    StylingMode = OtpInputStyle.Outlined
};
```

### Visual Characteristics
- Each field has a rectangular border
- Clear visual separation between fields
- Occupied and empty fields are visually distinct
- Focus state typically shows highlighted border
- Good accessibility with high contrast

### Example: Professional Login Form

```csharp
public class LoginPage : ContentPage
{
    public LoginPage()
    {
        InitializeComponent();

        var stackLayout = new VerticalStackLayout
        {
            Padding = 20,
            Spacing = 20,
            Children =
            {
                new Label 
                { 
                    Text = "Verify Your Identity", 
                    FontSize = 24, 
                    FontAttributes = FontAttributes.Bold 
                },
                new Label 
                { 
                    Text = "Enter the 6-digit code sent to your email", 
                    FontSize = 14,
                    TextColor = Colors.Gray
                },
                new SfOtpInput
                {
                    Length = 6,
                    Type = OtpInputType.Number,
                    StylingMode = OtpInputStyle.Outlined  // Clear borders
                },
                new Button 
                { 
                    Text = "Verify",
                    Padding = new Thickness(20, 10)
                }
            }
        };

        Content = stackLayout;
    }
}
```

### Advantages
- ✅ Clear visual boundaries
- ✅ Good for accessibility
- ✅ Professional appearance
- ✅ Default choice

### Disadvantages
- ❌ May appear more formal
- ❌ Takes more visual space due to borders

## Filled Mode

The **Filled** mode displays input fields with a background fill color. This creates a more compact, modern appearance where occupied and empty fields are distinguished by fill state.

### When to Use
- Modern, minimalist UI designs
- Apps with limited space
- Contemporary application styling
- Mobile-first designs
- Creative or playful applications

### Implementation

**XAML:**
```xml
<otpInput:SfOtpInput x:Name="FilledOtp"
                     Length="6"
                     Type="Number"
                     StylingMode="Filled" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    StylingMode = OtpInputStyle.Filled
};
```

### Visual Characteristics
- Fields have a background fill color
- No visible borders
- Occupied fields typically show filled state
- Empty fields show lighter fill or transparent background
- More compact vertical spacing
- Modern, minimal aesthetic

### Example: Modern Mobile Verification

```csharp
public class VerificationPage : ContentPage
{
    public VerificationPage()
    {
        InitializeComponent();

        var stackLayout = new VerticalStackLayout
        {
            Padding = new Thickness(20),
            Spacing = 30,
            Children =
            {
                new Label 
                { 
                    Text = "Verification Code", 
                    FontSize = 28, 
                    FontAttributes = FontAttributes.Bold 
                },
                new Label 
                { 
                    Text = "Check your SMS for a 6-digit code", 
                    FontSize = 14,
                    TextColor = Colors.Gray
                },
                new SfOtpInput
                {
                    Length = 6,
                    Type = OtpInputType.Number,
                    StylingMode = OtpInputStyle.Filled  // Modern look
                }
            }
        };

        Content = stackLayout;
    }
}
```

### Advantages
- ✅ Modern, clean appearance
- ✅ Compact layout
- ✅ Contemporary style
- ✅ Good for mobile applications

### Disadvantages
- ❌ May have lower contrast
- ❌ Less distinct field boundaries

## Underlined Mode

The **Underlined** mode displays input fields with only an underline beneath each field. This follows Material Design guidelines and provides a minimal aesthetic.

### When to Use
- Material Design compliant applications
- Text input heavy interfaces
- Minimal, flat design aesthetics
- Google Material Design style apps
- Maximum content focus

### Implementation

**XAML:**
```xml
<otpInput:SfOtpInput x:Name="UnderlinedOtp"
                     Length="6"
                     Type="Number"
                     StylingMode="Underlined" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    StylingMode = OtpInputStyle.Underlined
};
```

### Visual Characteristics
- Only underline visible beneath each field
- No borders or background fill
- Minimal visual footprint
- Clean, flat appearance
- Focus state shows highlighted underline
- Maximum space for content

### Example: Material Design 3 Authentication

```csharp
public class OtpVerificationPage : ContentPage
{
    public OtpVerificationPage()
    {
        InitializeComponent();

        var scrollView = new ScrollView
        {
            Content = new VerticalStackLayout
            {
                Padding = 24,
                Spacing = 24,
                Children =
                {
                    new Label 
                    { 
                        Text = "Enter Code", 
                        FontSize = 32, 
                        FontAttributes = FontAttributes.Bold 
                    },
                    new Label 
                    { 
                        Text = "We sent a verification code to your phone. Please enter it below.", 
                        FontSize = 14,
                        TextColor = Color.FromArgb("#66000000"),
                        LineBreakMode = LineBreakMode.WordWrap
                    },
                    new SfOtpInput
                    {
                        Length = 4,
                        Type = OtpInputType.Number,
                        StylingMode = OtpInputStyle.Underlined,  // Material Design
                        HorizontalOptions = LayoutOptions.Center
                    },
                    new Button 
                    { 
                        Text = "Verify",
                        Padding = new Thickness(20, 12),
                        CornerRadius = 20
                    }
                }
            }
        };

        Content = scrollView;
    }
}
```

### Advantages
- ✅ Minimal design
- ✅ Material Design compliance
- ✅ Maximum content visibility
- ✅ Clean, professional look

### Disadvantages
- ❌ Lower visual contrast
- ❌ May be harder to distinguish empty fields
- ❌ Less clear field boundaries

## Styling Mode Selection Guide

### Decision Matrix

| Requirement | Outlined | Filled | Underlined |
|------------|----------|--------|-----------|
| Material Design 3 | ✅ | ✅ | ✅ |
| Professional appearance | ✅✅ | ✅ | ✅ |
| Modern design | ✅ | ✅✅ | ✅ |
| Minimal aesthetic | ✓ | ✓ | ✅✅ |
| High contrast/accessibility | ✅✅ | ✓ | ✓ |
| Compact layout | ✓ | ✅ | ✅✅ |
| Clear field boundaries | ✅✅ | ✓ | ✓ |
| Enterprise applications | ✅✅ | ✓ | ✓ |

### Selection Strategy

**Choose Outlined if:**
- Building enterprise or professional applications
- Accessibility is critical
- You want maximum visual clarity
- Designing for older platforms or users

**Choose Filled if:**
- Building modern, mobile-first applications
- Space optimization is important
- Your design system uses filled components
- Creating contemporary user experiences

**Choose Underlined if:**
- Following Material Design 3 guidelines
- Creating minimal, flat UI designs
- Maximizing content area
- Building Google Material-compliant apps

## Color and Visual Customization

### InputBackground Property

The `InputBackground` property controls the background color of the input fields. This allows you to customize the appearance to match your app's color scheme.

**XAML:**
```xml
<otpInput:SfOtpInput Length="6"
                     InputBackground="LightBlue" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    InputBackground = Color.FromArgb("#E3F2FD")  // Light blue
};
```

### TextColor Property

The `TextColor` property controls the color of the input text/characters displayed in the fields.

**XAML:**
```xml
<otpInput:SfOtpInput Length="6"
                     TextColor="DarkBlue" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    TextColor = Colors.DarkBlue
};
```

**Example: Custom Color Theme**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    StylingMode = OtpInputStyle.Filled,
    InputBackground = Color.FromArgb("#F5F5F5"),  // Light gray
    TextColor = Colors.Black
};
```

### Stroke Property

The `Stroke` property controls the border color of the input fields. This is especially useful for Outlined styling mode where borders are visible.

**XAML:**
```xml
<otpInput:SfOtpInput Length="6"
                     StylingMode="Outlined"
                     Stroke="Blue" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    StylingMode = OtpInputStyle.Outlined,
    Stroke = Color.FromArgb("#2196F3")  // Material blue
};
```

**Example: Custom Stroke with Error State**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    StylingMode = OtpInputStyle.Outlined,
    Stroke = Colors.Green  // Initial color
};

// Change to red on validation error
otpInput.ValueChanged += async (s, e) =>
{
    if (e.NewValue?.Length == 6)
    {
        bool isValid = await VerifyOtpAsync(e.NewValue);
        if (!isValid)
        {
            otpInput.Stroke = Colors.Red;  // Error color
        }
        else
        {
            otpInput.Stroke = Colors.Green;  // Success color
        }
    }
};
```

### PlaceholderColor Property

The `PlaceholderColor` property controls the color of the placeholder text shown in empty fields.

**XAML:**
```xml
<otpInput:SfOtpInput Length="6"
                     Placeholder="0"
                     PlaceholderColor="LightGray" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Placeholder = "0",
    PlaceholderColor = Colors.LightGray
};
```

## Size and Spacing Customization

### BoxHeight Property

The `BoxHeight` property controls the height of each individual input field/box.

**XAML:**
```xml
<otpInput:SfOtpInput Length="6"
                     BoxHeight="50" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    BoxHeight = 50  // 50 pixels tall
};
```

**Example: Large Input Boxes**
```csharp
var otpInput = new SfOtpInput
{
    Length = 4,
    Type = OtpInputType.Number,
    BoxHeight = 60,  // Spacious boxes
    BoxWidth = 60,   // Square shaped
    StylingMode = OtpInputStyle.Filled
};
```

### BoxWidth Property

The `BoxWidth` property controls the width of each individual input field/box. Combined with `BoxHeight`, you can create square or rectangular input fields.

**XAML:**
```xml
<otpInput:SfOtpInput Length="6"
                     BoxWidth="50" />
```

**C#:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    BoxWidth = 50  // 50 pixels wide
};
```

**Example: Square Input Boxes**
```csharp
// Creates 6 square boxes, 50x50 each
var otpInput = new SfOtpInput
{
    Length = 6,
    BoxHeight = 50,
    BoxWidth = 50
};
```

**Example: Rectangular Input Boxes**
```csharp
// Creates wider boxes than tall
var otpInput = new SfOtpInput
{
    Length = 6,
    BoxHeight = 40,
    BoxWidth = 60  // Wider than tall
};
```

### Responsive Size Adjustment

```csharp
public class ResponsiveSizeOtpPage : ContentPage
{
    private SfOtpInput _otpInput;

    public ResponsiveSizeOtpPage()
    {
        InitializeComponent();
        
        _otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number
        };

        SizeChanged += (s, e) =>
        {
            // Adjust box size based on screen width
            if (Width < 400)
            {
                _otpInput.BoxHeight = 40;
                _otpInput.BoxWidth = 40;
            }
            else
            {
                _otpInput.BoxHeight = 60;
                _otpInput.BoxWidth = 60;
            }
        };
    }
}
```

## Custom Styling Considerations

### Combining Styling Modes with Other Properties

**Outlined with Custom Colors:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 4,
    Type = OtpInputType.Number,
    StylingMode = OtpInputStyle.Outlined,
    Stroke = Color.FromArgb("#2196F3"),  // Blue border
    TextColor = Colors.Black,
    BoxHeight = 50,
    BoxWidth = 50
};
```

**Filled with Custom Background:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    StylingMode = OtpInputStyle.Filled,
    InputBackground = Color.FromArgb("#F5F5F5"),
    TextColor = Colors.Black,
    BoxHeight = 55,
    BoxWidth = 55
};
```

**Underlined with Custom Separator and Colors:**
```csharp
var otpInput = new SfOtpInput
{
    Length = 6,
    Type = OtpInputType.Number,
    StylingMode = OtpInputStyle.Underlined,
    Separator = "-",
    Stroke = Color.FromArgb("#424242"),  // Dark underline
    TextColor = Colors.Black,
    PlaceholderColor = Colors.LightGray
};
```

**Complete Custom Theme:**
```csharp
var scrollView = new ScrollView
{
    Content = new VerticalStackLayout
    {
        Padding = 20,
        Spacing = 20,
        Children =
        {
            new Label { Text = "Enter Verification Code", FontSize = 24, FontAttributes = FontAttributes.Bold },
            new SfOtpInput
            {
                Length = 6,
                Type = OtpInputType.Number,
                StylingMode = OtpInputStyle.Filled,
                BoxHeight = 60,
                BoxWidth = 60,
                InputBackground = Color.FromArgb("#E8F5E9"),  // Light green
                TextColor = Colors.Black,
                Placeholder = "0",
                PlaceholderColor = Colors.LightGray
            }
        }
    }
};
```

### Platform-Specific Styling

Different platforms may render styling modes slightly differently. Test your chosen styling mode on target platforms:

- **Windows:** Full rendering support for all modes
- **iOS:** May have platform-specific spacing and colors
- **Android:** Material Design integration may influence appearance
- **macOS:** Similar to iOS with platform conventions

### Responsive Design

Adjust styling mode based on screen size:

```csharp
public class ResponsiveOtpPage : ContentPage
{
    private SfOtpInput _otpInput;

    public ResponsiveOtpPage()
    {
        InitializeComponent();
        
        _otpInput = new SfOtpInput
        {
            Length = 6,
            Type = OtpInputType.Number
        };

        SizeChanged += (s, e) =>
        {
            // Use filled on small screens, outlined on large
            if (Width < 500)
            {
                _otpInput.StylingMode = OtpInputStyle.Filled;
            }
            else
            {
                _otpInput.StylingMode = OtpInputStyle.Outlined;
            }
        };
    }
}
```

## Common Issues and Solutions

### Issue: Styling Mode Not Applying
**Problem:** StylingMode property seems to have no effect
**Solution:** Ensure the component is properly initialized after handler registration

### Issue: Inconsistent Appearance Across Platforms
**Problem:** Styling looks different on iOS vs Android
**Solution:** Platform differences are expected; test on each target platform and adjust if needed

### Issue: Poor Contrast with Filled Mode
**Problem:** Text in filled fields is hard to read
**Solution:** Switch to Outlined mode or adjust colors in app theme
