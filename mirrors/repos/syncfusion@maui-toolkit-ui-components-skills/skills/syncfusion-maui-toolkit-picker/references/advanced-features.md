# Advanced Features in .NET MAUI Picker

Explore advanced features and capabilities of the Syncfusion .NET MAUI Picker control including looping, text display modes, data template selectors.

## Table of Contents
- [Enable Looping](#enable-looping)
- [Text Display Modes](#text-display-modes)
- [DataTemplateSelector](#datatemplateselector)
- [Performance Optimization](#performance-optimization)
- [Edge Cases and Troubleshooting](#edge-cases-and-troubleshooting)

## Enable Looping

Looping allows seamless navigation from the last item back to the first item and vice versa, creating a continuous circular scroll experience.

### Basic Looping

**XAML:**
```xml
<picker:SfPicker x:Name="picker"
                 EnableLooping="True">
    <picker:SfPicker.Columns>
        <picker:PickerColumn ItemsSource="{Binding Items}" />
    </picker:SfPicker.Columns>
</picker:SfPicker>
```

**C#:**
```csharp
SfPicker picker = new SfPicker()
{
    EnableLooping = true,
};

this.Content = picker;
```

**Default value:** `false`

### When to Use Looping

**Good Use Cases:**
- Time pickers (hours 1-12 loop continuously)
- Date pickers (months wrap around)
- Circular menus
- Color wheels
- Repeating sequences

**Not Recommended For:**
- Long lists (confusing for users)
- Hierarchical data
- Filtered results
- Search results

### Example: 12-Hour Time Picker with Looping

```csharp
// Hours (1-12) with looping
ObservableCollection<int> hours = new ObservableCollection<int>();
for (int i = 1; i <= 12; i++)
{
    hours.Add(i);
}

// Minutes (00-59) with looping
ObservableCollection<string> minutes = new ObservableCollection<string>();
for (int i = 0; i < 60; i++)
{
    minutes.Add(i.ToString("D2"));
}

// AM/PM with looping
ObservableCollection<string> meridiem = new ObservableCollection<string> { "AM", "PM" };

SfPicker timePicker = new SfPicker()
{
    EnableLooping = true,
    HeightRequest = 250,
    
    Columns = new ObservableCollection<PickerColumn>()
    {
        new PickerColumn() { ItemsSource = hours, Width = 80 },
        new PickerColumn() { ItemsSource = minutes, Width = 80 },
        new PickerColumn() { ItemsSource = meridiem, Width = 80 }
    }
};
```

## Text Display Modes

Control how items appear visually in the picker using different text display modes.

### Available Modes

1. **Default**: Normal appearance, all items same size and opacity
2. **Fade**: Unselected items gradually fade in opacity
3. **Shrink**: Unselected items decrease in font size
4. **FadeAndShrink**: Combination of fade and shrink effects

### Default Mode

Standard picker appearance with uniform text.

```xml
<picker:SfPicker x:Name="picker"
                 TextDisplayMode="Default">
    <!-- Picker configuration -->
</picker:SfPicker>
```

### Fade Mode

Gradually decreases visibility of unselected items from the selected item.

**XAML:**
```xml
<picker:SfPicker x:Name="picker"
                 TextDisplayMode="Fade">
    <picker:SfPicker.Columns>
        <picker:PickerColumn ItemsSource="{Binding Items}" />
    </picker:SfPicker.Columns>
</picker:SfPicker>
```

**C#:**
```csharp
SfPicker picker = new SfPicker()
{
    TextDisplayMode = PickerTextDisplayMode.Fade
};

this.Content = picker;
```

**Effect:** Selected item is fully opaque, items further away gradually fade.

### Shrink Mode

Decreases font size of items further from the selected item.

**XAML:**
```xml
<picker:SfPicker x:Name="picker"
                 TextDisplayMode="Shrink">
    <picker:SfPicker.Columns>
        <picker:PickerColumn ItemsSource="{Binding Items}" />
    </picker:SfPicker.Columns>
</picker:SfPicker>
```

**C#:**
```csharp
SfPicker picker = new SfPicker()
{
    TextDisplayMode = PickerTextDisplayMode.Shrink
};

this.Content = picker;
```

**Effect:** Selected item is full size, items further away are progressively smaller.

### FadeAndShrink Mode

Combines both opacity and size reduction for maximum visual hierarchy.

**XAML:**
```xml
<picker:SfPicker x:Name="picker"
                 TextDisplayMode="FadeAndShrink">
    <picker:SfPicker.Columns>
        <picker:PickerColumn ItemsSource="{Binding Items}" />
    </picker:SfPicker.Columns>
</picker:SfPicker>
```

**C#:**
```csharp
SfPicker picker = new SfPicker()
{
    TextDisplayMode = PickerTextDisplayMode.FadeAndShrink
};

this.Content = picker;
```

**Effect:** Selected item is full size and fully opaque, unselected items are smaller and faded.

### Choosing the Right Mode

| Mode | Best For | Visual Impact |
|------|----------|---------------|
| **Default** | Professional forms, business apps | Minimal, clear |
| **Fade** | Modern designs, focus on selection | Subtle |
| **Shrink** | Space-constrained layouts | Moderate |
| **FadeAndShrink** | Maximum visual hierarchy, consumer apps | Strong |

## DataTemplateSelector

Apply different data templates based on item conditions.

### Basic DataTemplateSelector

**Template Selector Class:**
```csharp
public class LanguageTemplateSelector : DataTemplateSelector
{
    public DataTemplate IndianLanguages { get; set; }
    public DataTemplate OtherLanguages { get; set; }
    
    protected override DataTemplate OnSelectTemplate(object item, BindableObject container)
    {
        PickerItemDetails pickerItemDetails = item as PickerItemDetails;
        string language = pickerItemDetails.Data.ToString();
        
        if (language == "Tamil" || language == "Telugu" || language == "Hindi")
        {
            return IndianLanguages;
        }
        else
        {
            return OtherLanguages;
        }
    }
}
```

**XAML:**
```xml
<Grid>
    <Grid.Resources>
        <!-- Template for Indian languages -->
        <DataTemplate x:Key="indianLanguage">
            <Grid>
                <Label HorizontalTextAlignment="Center" 
                       BackgroundColor="#FFA500" 
                       VerticalTextAlignment="Center" 
                       Text="{Binding Data}"
                       TextColor="White"
                       FontAttributes="Bold"/>
            </Grid>
        </DataTemplate>
        
        <!-- Template for other languages -->
        <DataTemplate x:Key="otherLanguage">
            <Grid>
                <Label HorizontalTextAlignment="Center" 
                       VerticalTextAlignment="Center" 
                       BackgroundColor="#D3D3D3" 
                       Text="{Binding Data}"/>
            </Grid>
        </DataTemplate>
        
        <!-- Template selector -->
        <local:LanguageTemplateSelector x:Key="languageTemplateSelector"
                                       IndianLanguages="{StaticResource indianLanguage}" 
                                       OtherLanguages="{StaticResource otherLanguage}"/>
    </Grid.Resources>
    
    <picker:SfPicker x:Name="picker" 
                     ItemTemplate="{StaticResource languageTemplateSelector}">
        <picker:SfPicker.Columns>
            <picker:PickerColumn ItemsSource="{Binding Languages}" />
        </picker:SfPicker.Columns>
    </picker:SfPicker>

     <Grid.BindingContext>
        <local:LanguagesViewModel/>
    </Grid.BindingContext>
    
</Grid>
```

**Data Source:**
```csharp
public class LanguagesViewModel
{
    public ObservableCollection<string> Languages { get; set; }

    public LanguagesViewModel()
    {
        Languages = new ObservableCollection<string> 
        { 
            "Spanish", "French", "Tamil", "English", "German", 
            "Chinese", "Telugu", "Japanese", "Hindi", "Arabic", 
            "Russian", "Portuguese", "Italian" 
        };
    }
}
```

### Advanced DataTemplateSelector Example

**Priority-Based Selector:**
```csharp
public class PriorityTemplateSelector : DataTemplateSelector
{
    public DataTemplate HighPriority { get; set; }
    public DataTemplate MediumPriority { get; set; }
    public DataTemplate LowPriority { get; set; }
    
    protected override DataTemplate OnSelectTemplate(object item, BindableObject container)
    {
        if (item is PickerItemDetails details)
        {
            if (details.Data is TaskItem task)
            {
                return task.Priority switch
                {
                    Priority.High => HighPriority,
                    Priority.Medium => MediumPriority,
                    Priority.Low => LowPriority,
                    _ => LowPriority
                };
            }
        }
        
        return LowPriority;
    }
}

public class TaskItem
{
    public string Name { get; set; }
    public Priority Priority { get; set; }
}

public enum Priority
{
    Low,
    Medium,
    High
}
```

## Performance Optimization

### Large Data Sets

**Virtualization:** Picker automatically virtualizes items for performance.

**Best Practices:**
```csharp
// ✅ Good: Observable collection with reasonable size
ObservableCollection<string> items = new ObservableCollection<string>();
for (int i = 0; i < 1000; i++)
{
    items.Add($"Item {i}");
}

// ❌ Avoid: Excessive data
// ObservableCollection with 100,000+ items may cause lag
```

### Custom Templates

**Keep templates simple:**
```csharp
// ✅ Good: Lightweight template
DataTemplate template = new DataTemplate(() =>
{
    Label label = new Label 
    { 
        HorizontalTextAlignment = TextAlignment.Center 
    };
    label.SetBinding(Label.TextProperty, "Data");
    return label;
});

// ❌ Avoid: Complex nested layouts in templates
// Heavy layouts with multiple grids, images, and animations
```

### Memory Management

**Unsubscribe from events:**
```csharp
protected override void OnDisappearing()
{
    base.OnDisappearing();
    
    // Unsubscribe to prevent memory leaks
    picker.SelectionChanged -= Picker_SelectionChanged;
    picker.OkButtonClicked -= Picker_OkButtonClicked;
}
```

## Edge Cases and Troubleshooting

### Issue: Looping behaves unexpectedly

**Solution:**
- Verify data source has sufficient items (minimum 3 recommended)
- Check that SelectedIndex is within valid range
- Ensure ItemsSource is not null

### Issue: Text display mode not visible

**Solution:**
- Increase picker height to show more items
- Verify TextDisplayMode is set correctly
- Check that item count is sufficient to show effect

### Issue: DataTemplateSelector not triggering

**Solution:**
- Verify selector class inherits from `DataTemplateSelector`
- Check that `OnSelectTemplate` is overridden correctly
- Ensure item binding context is correct type

### Issue: Performance lag with large datasets

**Solution:**
- Limit ItemsSource to reasonable size (<1000 items)
- Use simpler item templates
- Avoid complex nested layouts
- Consider pagination or search filtering

## Best Practices Summary

1. **Enable looping** for circular data like time and dates
2. **Choose appropriate text display mode** based on design requirements
3. **Use DataTemplateSelector** for conditional styling
4. **Optimize templates** for performance
5. **Handle edge cases** with validation
6. **Unsubscribe from events** to prevent memory leaks
7. **Test with various data sizes** to ensure smooth scrolling

This combines looping, text display modes, custom templates for a modern, feature-rich picker experience.
