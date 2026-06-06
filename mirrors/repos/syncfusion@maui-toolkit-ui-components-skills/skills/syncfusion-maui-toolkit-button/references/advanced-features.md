# Advanced Features in .NET MAUI Button (SfButton)

This guide covers advanced features of the SfButton including RTL support, custom content views, and event handling.

## Table of Contents
- [Right-to-Left (RTL) Support](#right-to-left-rtl-support)
- [Custom Content Views](#custom-content-views)
- [Event Handling](#event-handling)
- [Complete Examples](#complete-examples)

## Right-to-Left (RTL) Support

The SfButton supports right-to-left (RTL) layout for languages like Arabic, Hebrew, and Urdu. RTL support automatically mirrors the button layout including icon positioning.

### Enabling RTL

**Method 1: Set FlowDirection on Button**

```xml
<buttons:SfButton Text="Add to cart"
                  FlowDirection="RightToLeft"
                  ShowIcon="True"
                  ImageSource="cart_icon.png" />
```

**Method 2: Set FlowDirection on C#**

```csharp
var button = new SfButton
{
    Text = "Add to cart",
    FlowDirection = FlowDirection.RightToLeft,
    ShowIcon = true,
    ImageSource = "cart_icon.png"
};
```

**Method 3: Device-Level RTL (Automatic)**

When the device language is set to an RTL language, MAUI automatically applies RTL layout to all controls including SfButton.

### RTL Behavior

When RTL is enabled:
- **Text direction:** Text flows right-to-left
- **Icon positioning:** Icons with `ImageAlignment="Start"` appear on the right
- **Icon positioning:** Icons with `ImageAlignment="End"` appear on the left
- **Layout mirroring:** Button content is mirrored horizontally

### Example: RTL Button with Icon

```xml
<buttons:SfButton Text="حفظ"
                  FlowDirection="RightToLeft"
                  ShowIcon="True"
                  ImageSource="save_icon.png"
                  ImageAlignment="Start"
                  Background="#6200EE"
                  TextColor="White"
                  CornerRadius="8"
                  HeightRequest="44" />
```

### Forcing LTR/RTL Regardless of Device

Use `ImageAlignment="Left"` or `ImageAlignment="Right"` to force icon position regardless of flow direction:

```xml
<!-- Icon always on left, even in RTL -->
<buttons:SfButton Text="Button"
                  FlowDirection="RightToLeft"
                  ShowIcon="True"
                  ImageSource="icon.png"
                  ImageAlignment="Left" />

<!-- Icon always on right, even in LTR -->
<buttons:SfButton Text="Button"
                  FlowDirection="LeftToRight"
                  ShowIcon="True"
                  ImageSource="icon.png"
                  ImageAlignment="Right" />
```

### Testing RTL Layout

To test RTL without changing device language:

```csharp
// Apply RTL to entire page
this.FlowDirection = FlowDirection.RightToLeft;

// Or apply to specific layout
var stack = new VerticalStackLayout
{
    FlowDirection = FlowDirection.RightToLeft,
    Children = { button1, button2, button3 }
};
```

## Custom Content Views

Replace button content with custom views using the `Content` property. This allows complete control over button appearance.

### Basic Custom Content

**XAML:**
```xml
<buttons:SfButton Background="#6200EE"
                  CornerRadius="8">
    <buttons:SfButton.Content>
        <DataTemplate>
            <HorizontalStackLayout Spacing="8" Padding="12">
                <Image Source="star.png"
                       WidthRequest="24"
                       HeightRequest="24" />
                <Label Text="Custom Button"
                       TextColor="White"
                       VerticalOptions="Center" />
            </HorizontalStackLayout>
        </DataTemplate>
    </buttons:SfButton.Content>
</buttons:SfButton>
```

**C#:**
```csharp
var customTemplate = new DataTemplate(() =>
{
    var image = new Image
    {
        Source = "star.png",
        WidthRequest = 24,
        HeightRequest = 24
    };
    
    var label = new Label
    {
        Text = "Custom Button",
        TextColor = Colors.White,
        VerticalOptions = LayoutOptions.Center
    };
    
    var layout = new HorizontalStackLayout
    {
        Spacing = 8,
        Padding = new Thickness(12)
    };
    layout.Children.Add(image);
    layout.Children.Add(label);
    
    return layout;
});

var button = new SfButton
{
    Background = Color.FromArgb("#6200EE"),
    CornerRadius = 8,
    Content = customTemplate
};
```

### Loading Button with Activity Indicator

```xml
<buttons:SfButton CornerRadius="8"
                  Background="#4CAF50"
                  WidthRequest="150"
                  HeightRequest="44">
    <buttons:SfButton.Content>
        <DataTemplate>
            <HorizontalStackLayout Spacing="10" Padding="12,0">
                <ActivityIndicator Color="White"
                                   IsRunning="True"
                                   WidthRequest="20"
                                   HeightRequest="20" />
                <Label Text="Loading..."
                       TextColor="White"
                       VerticalOptions="Center" />
            </HorizontalStackLayout>
        </DataTemplate>
    </buttons:SfButton.Content>
</buttons:SfButton>
```

### Dynamic Custom Content

```csharp
public class LoadingButton : SfButton
{
    private bool _isLoading;
    
    public bool IsLoading
    {
        get => _isLoading;
        set
        {
            _isLoading = value;
            UpdateContent();
        }
    }
    
    public string LoadingText { get; set; } = "Loading...";
    public string NormalText { get; set; } = "Submit";
    
    private void UpdateContent()
    {
        if (_isLoading)
        {
            Content = new DataTemplate(() =>
            {
                var indicator = new ActivityIndicator
                {
                    Color = Colors.White,
                    IsRunning = true,
                    WidthRequest = 20,
                    HeightRequest = 20
                };
                
                var label = new Label
                {
                    Text = LoadingText,
                    TextColor = Colors.White,
                    VerticalOptions = LayoutOptions.Center
                };
                
                var stack = new HorizontalStackLayout { Spacing = 8 };
                stack.Children.Add(indicator);
                stack.Children.Add(label);
                return stack;
            });
        }
        else
        {
            Content = new DataTemplate(() =>
            {
                return new Label
                {
                    Text = NormalText,
                    TextColor = Colors.White,
                    VerticalOptions = LayoutOptions.Center,
                    HorizontalOptions = LayoutOptions.Center
                };
            });
        }
    }
}

// Usage
var loadingButton = new LoadingButton
{
    NormalText = "Submit Form",
    LoadingText = "Submitting...",
    Background = Color.FromArgb("#6200EE")
};

// Start loading
loadingButton.IsLoading = true;

// Stop loading
loadingButton.IsLoading = false;
```

### Badge Button

```xml
<buttons:SfButton Background="#6200EE"
                  CornerRadius="8"
                  WidthRequest="120"
                  HeightRequest="44">
    <buttons:SfButton.Content>
        <DataTemplate>
            <Grid Padding="12,0">
                <Label Text="Messages"
                       TextColor="White"
                       VerticalOptions="Center"
                       HorizontalOptions="Center" />
                <Border Background="Red"
                        Padding="4,2"
                        VerticalOptions="Start"
                        HorizontalOptions="End"
                        Margin="0,-8,-8,0">
                    <Border.StrokeShape>
                        <RoundRectangle CornerRadius="10" />
                    </Border.StrokeShape>
                    <Label Text="5"
                           TextColor="White"
                           FontSize="10"
                           FontAttributes="Bold" />
                </Border>
            </Grid>
        </DataTemplate>
    </buttons:SfButton.Content>
</buttons:SfButton>
```

## Event Handling

### Clicked Event

The `Clicked` event fires when the button is tapped:

**XAML:**
```xml
<buttons:SfButton x:Name="myButton"
                  Text="Click Me"
                  Clicked="OnButtonClicked" />
```

**Code-behind:**
```csharp
private void OnButtonClicked(object sender, EventArgs e)
{
    var button = sender as SfButton;
    DisplayAlert("Clicked", "Button was clicked!", "OK");
}
```

**C# Only:**
```csharp
var button = new SfButton { Text = "Click Me" };
button.Clicked += (sender, e) =>
{
    DisplayAlert("Clicked", "Button was clicked!", "OK");
};
```

### Async Event Handlers

```csharp
private async void OnButtonClicked(object sender, EventArgs e)
{
    var button = sender as SfButton;
    button.IsEnabled = false;
    button.Text = "Processing...";
    
    try
    {
        await ProcessDataAsync();
        await DisplayAlert("Success", "Operation completed!", "OK");
    }
    catch (Exception ex)
    {
        await DisplayAlert("Error", ex.Message, "OK");
    }
    finally
    {
        button.Text = "Submit";
        button.IsEnabled = true;
    }
}

private async Task ProcessDataAsync()
{
    await Task.Delay(2000); // Simulate work
}
```

### Multiple Button Handlers

```csharp
private void OnActionButton_Clicked(object sender, EventArgs e)
{
    var button = sender as SfButton;
    
    if (button == saveButton)
    {
        SaveData();
    }
    else if (button == deleteButton)
    {
        DeleteData();
    }
    else if (button == cancelButton)
    {
        Cancel();
    }
}

// Attach same handler to multiple buttons
saveButton.Clicked += OnActionButton_Clicked;
deleteButton.Clicked += OnActionButton_Clicked;
cancelButton.Clicked += OnActionButton_Clicked;
```

### Toggle Button Events

```csharp
private void OnToggleClicked(object sender, EventArgs e)
{
    var button = sender as SfButton;
    
    if (button.IsCheckable && button.IsChecked)
    {
        // Button is now checked
        EnableFeature();
    }
    else
    {
        // Button is now unchecked
        DisableFeature();
    }
}
```

## Complete Examples

### Example 1: RTL Shopping Cart Button

```xml
<buttons:SfButton Text="أضف إلى السلة"
                  FlowDirection="RightToLeft"
                  ShowIcon="True"
                  ImageSource="cart_icon.png"
                  ImageAlignment="Start"
                  Background="#FF6F00"
                  TextColor="White"
                  CornerRadius="8"
                  HeightRequest="44"
                  WidthRequest="200"
                  Clicked="OnAddToCart" />
```

### Example 2: Dynamic Loading Button

```xml
<buttons:SfButton x:Name="submitButton"
                  Background="#6200EE"
                  CornerRadius="8"
                  WidthRequest="180"
                  HeightRequest="44"
                  Clicked="OnSubmit">
    <buttons:SfButton.Content>
        <DataTemplate>
            <Label x:Name="buttonLabel"
                   Text="Submit"
                   TextColor="White"
                   HorizontalOptions="Center"
                   VerticalOptions="Center" />
        </DataTemplate>
    </buttons:SfButton.Content>
</buttons:SfButton>
```

```csharp
private async void OnSubmit(object sender, EventArgs e)
{
    // Show loading state
    submitButton.Content = new DataTemplate(() =>
    {
        var stack = new HorizontalStackLayout { Spacing = 10, Padding = new Thickness(12, 0) };
        stack.Children.Add(new ActivityIndicator 
        { 
            Color = Colors.White, 
            IsRunning = true,
            WidthRequest = 20,
            HeightRequest = 20
        });
        stack.Children.Add(new Label 
        { 
            Text = "Submitting...", 
            TextColor = Colors.White,
            VerticalOptions = LayoutOptions.Center
        });
        return stack;
    });
    submitButton.IsEnabled = false;
    
    // Perform operation
    await Task.Delay(2000);
    
    // Restore normal state
    submitButton.Content = new DataTemplate(() =>
    {
        return new Label
        {
            Text = "Submit",
            TextColor = Colors.White,
            HorizontalOptions = LayoutOptions.Center,
            VerticalOptions = LayoutOptions.Center
        };
    });
    submitButton.IsEnabled = true;
}
```

### Example 4: Multi-Language RTL/LTR

```csharp
public void SetButtonLanguage(string languageCode)
{
    if (languageCode == "ar" || languageCode == "he")
    {
        myButton.FlowDirection = FlowDirection.RightToLeft;
        myButton.Text = GetLocalizedText(languageCode);
    }
    else
    {
        myButton.FlowDirection = FlowDirection.LeftToRight;
        myButton.Text = GetLocalizedText(languageCode);
    }
}
```

## Best Practices

1. **RTL Testing:** Test with actual RTL languages, not just `FlowDirection` property
2. **Custom Content:** Keep custom content simple for better performance
3. **Event Handlers:** Always disable button during async operations to prevent double-clicks
4. **Loading States:** Provide visual feedback for long-running operations
5. **Accessibility:** Ensure custom content maintains proper semantics and labels

## Quick Reference

| Feature | Property/Method | Purpose |
|---------|----------------|---------|
| RTL Support | `FlowDirection="RightToLeft"` | Enable right-to-left layout |
| Custom Content | `Content` property | Replace button content |
| Click Event | `Clicked` event | Handle button taps |
| Toggle State | `IsCheckable`, `IsChecked` | Create toggle buttons |
