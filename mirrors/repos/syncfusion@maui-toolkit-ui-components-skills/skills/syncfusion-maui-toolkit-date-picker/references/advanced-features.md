# Advanced Features in .NET MAUI DatePicker

The .NET MAUI DatePicker includes advanced features for modern UI experiences, including text display modes.

## Text Display Modes

Text display modes control how date picker items are displayed relative to the selected item, creating visual effects that enhance usability and aesthetics.

### Available Modes

The `TextDisplayMode` property accepts values from the `PickerTextDisplayMode` enumeration:

- **Default** - Standard display without effects (default)
- **Fade** - Gradually decreases opacity of items away from selection
- **Shrink** - Decreases font size of items away from selection
- **FadeAndShrink** - Combines both fade and shrink effects

### Default Mode

The standard display mode without visual effects.

```xml
<picker:SfDatePicker x:Name="datePicker"
                     TextDisplayMode="Default">
</picker:SfDatePicker>
```

```csharp
SfDatePicker datePicker = new SfDatePicker()
{
    TextDisplayMode = PickerTextDisplayMode.Default
};
```

**Use Case:** When visual effects might be distracting or when maximum readability is required.

### Fade Mode

Gradually decreases the visibility (opacity) of unselected items relative to the selected item.

```xml
<picker:SfDatePicker x:Name="datePicker"
                     TextDisplayMode="Fade">
</picker:SfDatePicker>
```

```csharp
SfDatePicker datePicker = new SfDatePicker()
{
    TextDisplayMode = PickerTextDisplayMode.Fade
};
```

**Behavior:**
- Selected item: 100% opacity
- Items one position away: ~75% opacity
- Items two positions away: ~50% opacity
- Items three+ positions away: ~25% opacity

**Use Case:** Drawing focus to the selected item while keeping context visible.

### Shrink Mode

Decreases the font size of items as they move away from the selected item.

```xml
<picker:SfDatePicker x:Name="datePicker"
                     TextDisplayMode="Shrink">
</picker:SfDatePicker>
```

```csharp
SfDatePicker datePicker = new SfDatePicker()
{
    TextDisplayMode = PickerTextDisplayMode.Shrink
};
```

**Behavior:**
- Selected item: 100% font size
- Items one position away: ~85% font size
- Items two positions away: ~70% font size
- Items three+ positions away: ~60% font size

**Use Case:** Creating depth perception and emphasizing the selected value.

### FadeAndShrink Mode

Combines both fade and shrink effects for maximum visual emphasis.

```xml
<picker:SfDatePicker x:Name="datePicker"
                     TextDisplayMode="FadeAndShrink">
</picker:SfDatePicker>
```

```csharp
SfDatePicker datePicker = new SfDatePicker()
{
    TextDisplayMode = PickerTextDisplayMode.FadeAndShrink
};
```

**Behavior:**
- Applies both opacity reduction and font size reduction simultaneously
- Creates the strongest visual focus on the selected item

**Use Case:** Modern, visually appealing UIs where the selected item should stand out prominently.

### Comparison Example

```xml
<StackLayout Padding="20" Spacing="30">
    <Label Text="Text Display Modes Comparison" 
           FontSize="22" 
           FontAttributes="Bold"/>
    
    <!-- Default Mode -->
    <StackLayout>
        <Label Text="Default Mode" FontAttributes="Bold"/>
        <picker:SfDatePicker TextDisplayMode="Default" HeightRequest="200"/>
    </StackLayout>
    
    <!-- Fade Mode -->
    <StackLayout>
        <Label Text="Fade Mode" FontAttributes="Bold"/>
        <picker:SfDatePicker TextDisplayMode="Fade" HeightRequest="200"/>
    </StackLayout>
    
    <!-- Shrink Mode -->
    <StackLayout>
        <Label Text="Shrink Mode" FontAttributes="Bold"/>
        <picker:SfDatePicker TextDisplayMode="Shrink" HeightRequest="200"/>
    </StackLayout>
    
    <!-- FadeAndShrink Mode -->
    <StackLayout>
        <Label Text="Fade and Shrink Mode" FontAttributes="Bold"/>
        <picker:SfDatePicker TextDisplayMode="FadeAndShrink" HeightRequest="200"/>
    </StackLayout>
</StackLayout>
```

### Dynamic Mode Switching

```csharp
public class DatePickerPage : ContentPage
{
    private SfDatePicker datePicker;
    
    public DatePickerPage()
    {
        InitializeComponent();
        SetupPicker();
    }
    
    private void SetupPicker()
    {
        datePicker = new SfDatePicker();
        // Set initial mode
        datePicker.TextDisplayMode = PickerTextDisplayMode.FadeAndShrink;
    }
    
    private void OnModeChanged(object sender, EventArgs e)
    {
        var selectedMode = modePicker.SelectedItem as string;
        
        datePicker.TextDisplayMode = selectedMode switch
        {
            "Default" => PickerTextDisplayMode.Default,
            "Fade" => PickerTextDisplayMode.Fade,
            "Shrink" => PickerTextDisplayMode.Shrink,
            "Fade and Shrink" => PickerTextDisplayMode.FadeAndShrink,
            _ => PickerTextDisplayMode.Default
        };
    }
}
```


## Best Practices

### Text Display Modes

1. **Match UI Design Language** - Choose modes that align with your app's overall design
2. **Consider Readability** - Ensure unselected items remain readable, especially for accessibility
3. **Test on Real Devices** - Visual effects may appear differently on various devices
4. **Use Sparingly** - Not every picker needs effects; use where it enhances UX

## Troubleshooting

### Issue: TextDisplayMode not visible
**Solution:** Ensure the picker has sufficient height to display multiple items. Effects are most visible with 5+ visible items.