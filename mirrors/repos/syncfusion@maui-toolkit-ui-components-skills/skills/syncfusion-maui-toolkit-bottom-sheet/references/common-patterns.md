# Common Patterns and Real-World Scenarios

## Table of Contents
1. [Data-Driven Bottom Sheet](#data-driven-bottom-sheet)
2. [Modal Dialogs](#modal-dialogs)
3. [Partial Reveal Patterns](#partial-reveal-patterns)
4. [Dynamic Content Updates](#dynamic-content-updates)
5. [Error Handling](#error-handling)
6. [Anti-Patterns](#anti-patterns)

---

## Data-Driven Bottom Sheet

### Pattern Overview

Display detailed information when a user selects an item from a list. The sheet content updates dynamically based on the selected item.

### Complete Implementation

**Model:**
```csharp
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public decimal Price { get; set; }
    public int Rating { get; set; }
    public string ImageUrl { get; set; }
}
```

**ViewModel:**
```csharp
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;

public class ProductViewModel : INotifyPropertyChanged
{
    private ObservableCollection<Product> _products;
    private Product _selectedProduct;
    private ICommand _addToCartCommand;

    public ObservableCollection<Product> Products
    {
        get => _products;
        set => SetProperty(ref _products, value);
    }

    public Product SelectedProduct
    {
        get => _selectedProduct;
        set => SetProperty(ref _selectedProduct, value);
    }

    public ICommand AddToCartCommand
    {
        get => _addToCartCommand ??= new Command(OnAddToCart);
    }

    public ProductViewModel()
    {
        LoadProducts();
    }

    private void LoadProducts()
    {
        Products = new ObservableCollection<Product>
        {
            new Product 
            { 
                Id = 1,
                Name = "Laptop",
                Description = "High-performance laptop for professionals",
                Price = 1299.99m,
                Rating = 5,
                ImageUrl = "laptop.png"
            },
            new Product 
            { 
                Id = 2,
                Name = "Tablet",
                Description = "Portable tablet for entertainment",
                Price = 499.99m,
                Rating = 4,
                ImageUrl = "tablet.png"
            },
            new Product 
            { 
                Id = 3,
                Name = "Smartphone",
                Description = "Latest smartphone with advanced features",
                Price = 899.99m,
                Rating = 5,
                ImageUrl = "phone.png"
            }
        };
    }

    private void OnAddToCart()
    {
        if (SelectedProduct != null)
        {
            Debug.WriteLine($"Added {SelectedProduct.Name} to cart");
            // Implement cart logic
        }
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected bool SetProperty<T>(ref T backingStore, T value, 
        [CallerMemberName] string propertyName = "")
    {
        if (EqualityComparer<T>.Default.Equals(backingStore, value))
            return false;

        backingStore = value;
        OnPropertyChanged(propertyName);
        return true;
    }

    protected void OnPropertyChanged([CallerMemberName] string propertyName = "")
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

**XAML Page:**
```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:bottomSheet="clr-namespace:Syncfusion.Maui.Toolkit.BottomSheet;assembly=Syncfusion.Maui.Toolkit"
             xmlns:local="clr-namespace:BottomSheetDemo.ViewModel"
             x:Class="BottomSheetDemo.ProductPage"
             Title="Products">

    <ContentPage.BindingContext>
        <local:ProductViewModel />
    </ContentPage.BindingContext>

    <Grid RowDefinitions="*" ColumnDefinitions="*" Padding="10">
        <!-- Product List -->
        <ListView ItemsSource="{Binding Products}" 
                  ItemTapped="OnProductTapped" 
                  HasUnevenRows="True">
            <ListView.ItemTemplate>
                <DataTemplate>
                    <ViewCell>
                        <Grid ColumnDefinitions="60, *, Auto" Padding="10" RowSpacing="5">
                            <!-- Product Image -->
                            <Image Source="{Binding ImageUrl}" 
                                   Aspect="AspectFill" 
                                   WidthRequest="60" 
                                   HeightRequest="60"/>
                            
                            <!-- Product Info -->
                            <VerticalStackLayout Grid.Column="1" Padding="10,0">
                                <Label Text="{Binding Name}" 
                                       FontSize="16" 
                                       FontAttributes="Bold"/>
                                <Label Text="{Binding Description}" 
                                       FontSize="12" 
                                       TextColor="Gray"
                                       LineBreakMode="TailTruncation"/>
                            </VerticalStackLayout>
                            
                            <!-- Price -->
                            <Label Text="{Binding Price, StringFormat='${0:F2}'}" 
                                   Grid.Column="2" 
                                   FontSize="14" 
                                   TextColor="Green"
                                   FontAttributes="Bold"
                                   VerticalOptions="Center"/>
                        </Grid>
                    </ViewCell>
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>

        <!-- Bottom Sheet: Product Details -->
        <bottomSheet:SfBottomSheet x:Name="productSheet" 
                                   Grid.Row="0"
                                   HalfExpandedRatio="0.35" 
                                   CornerRadius="15, 15, 0, 0"
                                   ContentPadding="15"
                                   StateChanged="OnSheetStateChanged">
            <bottomSheet:SfBottomSheet.BottomSheetContent>
                <ScrollView>
                    <VerticalStackLayout Spacing="15" Padding="5">
                        <!-- Product Name -->
                        <Label Text="{Binding SelectedProduct.Name}" 
                               FontSize="24" 
                               FontAttributes="Bold"/>
                        
                        <!-- Rating -->
                        <StackLayout Orientation="Horizontal" Spacing="5">
                            <Label Text="★" FontSize="18" TextColor="Gold"/>
                            <Label Text="{Binding SelectedProduct.Rating, StringFormat='{0}/5'}" 
                                   FontSize="14" 
                                   VerticalOptions="Center"/>
                        </StackLayout>
                        
                        <!-- Description -->
                        <VerticalStackLayout Spacing="3">
                            <Label Text="Description" FontSize="14" FontAttributes="Bold"/>
                            <Label Text="{Binding SelectedProduct.Description}" 
                                   FontSize="12" 
                                   TextColor="Gray"
                                   LineBreakMode="WordWrap"/>
                        </VerticalStackLayout>
                        
                        <!-- Price -->
                        <Frame BorderColor="LightGray" Padding="10" CornerRadius="5">
                            <Grid ColumnDefinitions="Auto, *">
                                <Label Text="Price:" FontAttributes="Bold"/>
                                <Label Text="{Binding SelectedProduct.Price, StringFormat='${0:F2}'}" 
                                       Grid.Column="1" 
                                       TextColor="Green" 
                                       FontAttributes="Bold"
                                       HorizontalOptions="End"/>
                            </Grid>
                        </Frame>
                        
                        <!-- Add to Cart Button -->
                        <Button Text="Add to Cart" 
                                Command="{Binding AddToCartCommand}"
                                BackgroundColor="#007AFF" 
                                TextColor="White"
                                CornerRadius="5"
                                Padding="10"/>
                    </VerticalStackLayout>
                </ScrollView>
            </bottomSheet:SfBottomSheet.BottomSheetContent>
        </bottomSheet:SfBottomSheet>
    </Grid>
</ContentPage>
```

**Code-Behind:**
```csharp
public partial class ProductPage : ContentPage
{
    public ProductPage()
    {
        InitializeComponent();
    }

    private void OnProductTapped(object? sender, ItemTappedEventArgs e)
    {
        if (e.Item is Product product)
        {
            var viewModel = this.BindingContext as ProductViewModel;
            if (viewModel != null)
            {
                viewModel.SelectedProduct = product;
                productSheet.Show();
            }
        }
    }

    private void OnSheetStateChanged(object sender, StateChangedEventArgs e)
    {
        Debug.WriteLine($"Sheet state: {e.NewState}");
    }
}
```

---

## Modal Dialogs

### Pattern Overview

Create modal dialogs that require user confirmation before proceeding. The dialog blocks background interaction and forces explicit user action.

### Confirmation Dialog Example

```csharp
public class ConfirmationDialogService
{
    public async Task<bool> ShowConfirmation(string title, string message,
        string confirmText = "Confirm", string cancelText = "Cancel")
    {
        var tcs = new TaskCompletionSource<bool>();

        var dialog = new SfBottomSheet
        {
            State = BottomSheetState.FullExpanded,
            AllowedState = BottomSheetAllowedState.FullExpanded,
            IsModal = true,
            CollapseOnOverlayTap = false,
            CornerRadius = new CornerRadius(20, 20, 0, 0),
            ContentPadding = new Thickness(20)
        };

        var content = new VerticalStackLayout { Spacing = 20, Padding = 20 };

        // Title
        content.Children.Add(new Label
        {
            Text = title,
            FontSize = 22,
            FontAttributes = FontAttributes.Bold
        });

        // Message
        content.Children.Add(new Label
        {
            Text = message,
            FontSize = 14,
            TextColor = Colors.Gray,
            LineBreakMode = LineBreakMode.WordWrap
        });

        // Button Grid
        var buttonGrid = new Grid
        {

            ColumnDefinitions =
            {
                new ColumnDefinition { Width = GridLength.Star },
                new ColumnDefinition { Width = GridLength.Star }
            },
            ColumnSpacing = 10,
            Margin = new Thickness(0, 20, 0, 0)
        };

        var cancelBtn = new Button
        {
            Text = cancelText,
            BackgroundColor = Colors.LightGray,
            TextColor = Colors.Black
        };
        cancelBtn.Clicked += (s, e) =>
        {
            dialog.Close();
            tcs.SetResult(false);
        };

        var confirmBtn = new Button
        {
            Text = confirmText,
            BackgroundColor = Colors.Green,
            TextColor = Colors.White,
        };
        Grid.SetColumn(confirmBtn, 1);
        confirmBtn.Clicked += (s, e) =>
        {
            dialog.Close();
            tcs.SetResult(true);
        };

        buttonGrid.Children.Add(cancelBtn);
        buttonGrid.Children.Add(confirmBtn);

        content.Children.Add(buttonGrid);
        dialog.BottomSheetContent = content;

        dialog.Show();

        return await tcs.Task;
    }

}
// Usage:
private async void OnDeleteClicked(object sender, EventArgs e)
{
    var service = new ConfirmationDialogService();
    bool confirmed = await service.ShowConfirmation(
        "Delete Item",
        "Are you sure you want to delete this item?",
        "Delete",
        "Cancel"
    );

    if (confirmed)
    {
        // Perform delete action
        Debug.WriteLine("Item deleted");
    }
}
```

---

## Partial Reveal Patterns

### Pattern Overview

Show a preview of content in collapsed state, with full content available when expanded. Users can progressively explore information.

### Implementation

```xaml
<bottomSheet:SfBottomSheet x:Name="previewSheet"
                           State="Collapsed"
                           CollapsedHeight="120"
                           HalfExpandedRatio="0.4"
                           AllowedState="HalfExpanded"
                           EnableSwiping="True">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <VerticalStackLayout Spacing="10" Padding="15">
            <!-- Always Visible: Title (in collapsed state) -->
            <Label Text="{Binding Article.Title}" 
                   FontSize="18" 
                   FontAttributes="Bold"/>
            
            <!-- Visible when expanded: Excerpt -->
            <Label x:Name="excerptLabel"
                   Text="{Binding Article.Excerpt}" 
                   FontSize="14"
                   TextColor="Gray"
                   LineBreakMode="WordWrap"
                   IsVisible="False"/>
            
            <!-- Fully visible: Full content -->
            <Label x:Name="fullContentLabel"
                   Text="{Binding Article.FullContent}" 
                   FontSize="14"
                   LineBreakMode="WordWrap"
                   IsVisible="False"/>
        </VerticalStackLayout>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

```csharp
private void OnPreviewStateChanged(object sender, StateChangedEventArgs e)
{
    switch (e.NewState)
    {
        case BottomSheetState.Collapsed:
            // Show title only
            excerptLabel.IsVisible = false;
            fullContentLabel.IsVisible = false;
            break;

        case BottomSheetState.HalfExpanded:
            // Show title + excerpt
            excerptLabel.IsVisible = true;
            fullContentLabel.IsVisible = false;
            break;

        case BottomSheetState.FullExpanded:
            // Show all content
            excerptLabel.IsVisible = true;
            fullContentLabel.IsVisible = true;
            break;
    }
}
```

---

## Dynamic Content Updates

### Pattern Overview

Update sheet content dynamically based on user interactions or data changes.

### Implementation

```csharp
public partial class DynamicContentPage : ContentPage
{
    private List<string> cartItems = new();

    public DynamicContentPage()
    {
        InitializeComponent();
    }

    private void OnAddItemClicked(object sender, EventArgs e)
    {
        string newItem = itemEntry.Text;
        if (!string.IsNullOrEmpty(newItem))
        {
            cartItems.Add(newItem);
            UpdateCartSheet();
            itemEntry.Text = string.Empty;
        }
    }

    private void UpdateCartSheet()
    {
        // Create dynamic content
        var content = new VerticalStackLayout { Spacing = 10, Padding = 15 };

        content.Children.Add(new Label
        {
            Text = $"Cart ({cartItems.Count} items)",
            FontSize = 18,
            FontAttributes = FontAttributes.Bold
        });

        foreach (var item in cartItems)
        {
            var itemGrid = new Grid
            {

                ColumnDefinitions =
                {
                    new ColumnDefinition { Width = GridLength.Star },
                    new ColumnDefinition { Width = GridLength.Auto }
                },
                Padding = new Thickness(0, 5)
            };

            itemGrid.Children.Add(new Label { Text = item });

            var removeBtn = new Button
            {
                Text = "✕",
                FontSize = 14,
                Padding = new Thickness(5),
                
            };
            Grid.SetColumn(removeBtn, 1);
            removeBtn.Clicked += (s, e) =>
            {
                cartItems.Remove(item);
                UpdateCartSheet();
            };

            itemGrid.Children.Add(removeBtn);
            content.Children.Add(itemGrid);
        }

        cartSheet.BottomSheetContent = content;
    }
}
```

---

## Error Handling

### Pattern Overview

Handle errors gracefully and present error information to users through the Bottom Sheet.

### Implementation

```csharp
public class ErrorHandlingPattern
{
    public async Task<T> TryWithErrorHandling<T>(Func<Task<T>> operation, 
        SfBottomSheet errorSheet)
    {
        try
        {
            return await operation();
        }
        catch (HttpRequestException ex)
        {
            ShowError(errorSheet, "Network Error", 
                "Unable to connect. Please check your internet connection.");
            Debug.WriteLine($"Network error: {ex.Message}");
            return default;
        }
        catch (TimeoutException ex)
        {
            ShowError(errorSheet, "Timeout", 
                "The request took too long. Please try again.");
            Debug.WriteLine($"Timeout: {ex.Message}");
            return default;
        }
        catch (Exception ex)
        {
            ShowError(errorSheet, "Error", 
                "An unexpected error occurred. Please try again later.");
            Debug.WriteLine($"Error: {ex.Message}");
            return default;
        }
    }

    private void ShowError(SfBottomSheet sheet, string title, string message)
    {
        sheet.State = BottomSheetState.FullExpanded;
        
        var content = new VerticalStackLayout { Spacing = 15, Padding = 20 };
        
        content.Children.Add(new Label 
        { 
            Text = title, 
            FontSize = 20, 
            FontAttributes = FontAttributes.Bold,
            TextColor = Colors.Red
        });
        
        content.Children.Add(new Label 
        { 
            Text = message, 
            FontSize = 14,
            TextColor = Colors.Gray
        });
        
        var closeBtn = new Button 
        { 
            Text = "Close",
            BackgroundColor = Colors.Red,
            TextColor = Colors.White
        };
        closeBtn.Clicked += (s, e) => sheet.Close();
        
        content.Children.Add(closeBtn);
        sheet.BottomSheetContent = content;
        
        sheet.Show();
    }
}
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Modal Without Close Button

```csharp
// DON'T: Users can't close the sheet
var trap = new SfBottomSheet
{
    IsModal = true,
    CollapseOnOverlayTap = false,  // No close on tap
    ShowGrabber = false,            // No drag handle
    AllowedState = BottomSheetAllowedState.FullExpanded
};
// Users are trapped and can't exit!
```

### ❌ Anti-Pattern 2: Ignoring State Changes

```csharp
// DON'T: Content doesn't react to state changes
private void OnStateChanged(object sender, StateChangedEventArgs e)
{
    // Empty handler - content never updates
}
// Users see same content at all states, confusing UX
```

### ❌ Anti-Pattern 3: Excessive State Changes

```csharp
// DON'T: Constantly changing state
private void OnPropertyChanged(object sender, PropertyChangedEventArgs e)
{
    bottomSheet.State = (bottomSheet.State == BottomSheetState.FullExpanded) 
        ? BottomSheetState.Collapsed 
        : BottomSheetState.FullExpanded;
}
// Jarring UI that's hard to use
```

### ❌ Anti-Pattern 4: Too Small Content Area

```csharp
// DON'T: Collapsed height too small to be useful
var sheet = new SfBottomSheet
{
    CollapsedHeight = 20  // Invisible/unusable
};
```

### ❌ Anti-Pattern 5: No Loading Feedback

```csharp
// DON'T: User doesn't know content is loading
private async void OnItemTapped(object? sender, ItemTappedEventArgs e)
{
    sheet.Show();
    await LoadData();  // No loading indicator!
}
```

### ✅ Correct: Show Loading State

```csharp
// DO: Provide visual feedback
private async void OnItemTapped(object? sender, ItemTappedEventArgs e)
{
    sheet.Show();
    
    var content = new VerticalStackLayout { Padding = 20 };
    content.Children.Add(new ActivityIndicator { IsRunning = true });
    content.Children.Add(new Label { Text = "Loading..." });
    sheet.BottomSheetContent = content;
    
    await LoadData();
    
    // Update content after loading
    UpdateSheetContent();
}
```

---

## Best Practices Summary

### ✅ DO:

1. **Provide clear content** that responds to sheet state
2. **Enable swiping** for better user control
3. **Always provide a close mechanism** (button or overlay tap)
4. **Use meaningful heights** (CollapsedHeight > 50px)
5. **Give feedback** during loading/processing
6. **Handle errors gracefully** with user-friendly messages
7. **Test with real data** to ensure layout works

### ❌ DON'T:

1. **Trap users** in modal dialogs without close button
2. **Ignore state changes** - update content accordingly
3. **Create confusing UX** with rapid state changes
4. **Make collapsed state unusable** - too small
5. **Hide important content** in full state only
6. **Perform heavy operations** on state changes
7. **Forget about accessibility** - provide alternatives to gestures

---