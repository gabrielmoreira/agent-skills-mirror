# Advanced Features in .NET MAUI Funnel Chart

This guide covers advanced customization features for `SfFunnelChart`, including orientation control, and segment spacing.

## Table of Contents
- [Orientation](#orientation)
- [Segment Spacing](#segment-spacing)

## Orientation

The `Orientation` property controls the rendering direction of funnel segments. The default is `Vertical` (bottom to top), but you can switch to `Horizontal` (right to left).

### Available Orientations
- **Vertical** (default): Segments arranged from bottom to top
- **Horizontal**: Segments arranged from right to left

### XAML
```xaml
<chart:SfFunnelChart Orientation="Horizontal"
                     ItemsSource="{Binding Data}"
                     XBindingPath="XValue"
                     YBindingPath="YValue">
    <!-- Chart configuration -->
</chart:SfFunnelChart>
```

### C#
```csharp
SfFunnelChart chart = new SfFunnelChart();
chart.ItemsSource = viewModel.Data;
chart.XBindingPath = "XValue";
chart.YBindingPath = "YValue";
chart.Orientation = ChartOrientation.Horizontal;

this.Content = chart;
```

### When to Use Each Orientation

**Vertical (Default):**
- Traditional funnel representation
- Best for top-to-bottom process flows
- Works well with bottom-placed legends
- Ideal for portrait layouts

**Horizontal:**
- Left-to-right reading patterns
- Better for landscape orientations
- Works well with left/right-placed legends
- Suitable for timeline-style visualizations

### Complete Orientation Example

```xaml
<ContentPage xmlns:chart="clr-namespace:Syncfusion.Maui.Toolkit.Charts;assembly=Syncfusion.Maui.Toolkit">
    
    <VerticalStackLayout Spacing="20" Padding="10">
        
        <!-- Vertical Funnel -->
        <Border Stroke="Gray" StrokeThickness="1" Padding="10">
            <VerticalStackLayout>
                <Label Text="Vertical Orientation" 
                       FontSize="16" 
                       FontAttributes="Bold"
                       HorizontalOptions="Center"/>
                <chart:SfFunnelChart ItemsSource="{Binding Data}"
                                     XBindingPath="Stage"
                                     YBindingPath="Value"
                                     Orientation="Vertical"
                                     HeightRequest="300">
                    <chart:SfFunnelChart.Legend>
                        <chart:ChartLegend Placement="Bottom"/>
                    </chart:SfFunnelChart.Legend>
                </chart:SfFunnelChart>
            </VerticalStackLayout>
        </Border>
        
        <!-- Horizontal Funnel -->
        <Border Stroke="Gray" StrokeThickness="1" Padding="10">
            <VerticalStackLayout>
                <Label Text="Horizontal Orientation" 
                       FontSize="16" 
                       FontAttributes="Bold"
                       HorizontalOptions="Center"/>
                <chart:SfFunnelChart ItemsSource="{Binding Data}"
                                     XBindingPath="Stage"
                                     YBindingPath="Value"
                                     Orientation="Horizontal"
                                     HeightRequest="300">
                    <chart:SfFunnelChart.Legend>
                        <chart:ChartLegend Placement="Right"/>
                    </chart:SfFunnelChart.Legend>
                </chart:SfFunnelChart>
            </VerticalStackLayout>
        </Border>
        
    </VerticalStackLayout>
    
</ContentPage>
```

## Segment Spacing

The `GapRatio` property controls the gap between funnel segments. This creates visual separation, making individual stages more distinct.

### Properties
- **GapRatio** (double): Value between `0` and `1`
  - `0`: No gap (default)
  - `1`: Maximum gap

### XAML
```xaml
<chart:SfFunnelChart GapRatio="0.2"
                     ItemsSource="{Binding Data}"
                     XBindingPath="XValue"
                     YBindingPath="YValue">
    <!-- Chart configuration -->
</chart:SfFunnelChart>
```

### C#
```csharp
SfFunnelChart chart = new SfFunnelChart();
chart.ItemsSource = viewModel.Data;
chart.XBindingPath = "XValue";
chart.YBindingPath = "YValue";
chart.GapRatio = 0.2;

this.Content = chart;
```

### Gap Ratio Examples

#### No Gap (Default)
```xaml
<chart:SfFunnelChart GapRatio="0"/>
```
- Segments touch each other
- Traditional funnel appearance
- Best for emphasizing flow

#### Small Gap
```xaml
<chart:SfFunnelChart GapRatio="0.1"/>
```
- Subtle separation
- Maintains funnel shape
- Slightly improved segment distinction

#### Medium Gap
```xaml
<chart:SfFunnelChart GapRatio="0.2"/>
```
- Noticeable separation
- Good balance between flow and distinction
- Recommended for most use cases

#### Large Gap
```xaml
<chart:SfFunnelChart GapRatio="0.5"/>
```
- Significant separation
- Individual segments stand out
- May lose funnel metaphor

### Segment Spacing with Visual Enhancements

```xaml
<chart:SfFunnelChart ItemsSource="{Binding Data}"
                     XBindingPath="Stage"
                     YBindingPath="Count"
                     GapRatio="0.15"
                     ShowDataLabels="True">
    
    <chart:SfFunnelChart.DataLabelSettings>
        <chart:FunnelDataLabelSettings LabelPlacement="Center">
            <chart:FunnelDataLabelSettings.LabelStyle>
                <chart:ChartDataLabelStyle FontSize="14"
                                          FontAttributes="Bold"
                                          TextColor="White"/>
            </chart:FunnelDataLabelSettings.LabelStyle>
        </chart:FunnelDataLabelSettings>
    </chart:SfFunnelChart.DataLabelSettings>
    
</chart:SfFunnelChart>
```
