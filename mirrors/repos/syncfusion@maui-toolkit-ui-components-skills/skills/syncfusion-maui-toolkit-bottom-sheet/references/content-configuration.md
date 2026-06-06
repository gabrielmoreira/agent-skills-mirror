# Content Configuration in .NET MAUI Bottom Sheet

## Table of Contents
1. [Content vs. BottomSheetContent](#content-vs-bottomsheetcontent)
2. [Main Content](#main-content)
3. [Bottom Sheet Content](#bottom-sheet-content)
4. [Data Binding Patterns](#data-binding-patterns)
5. [ViewModel Integration](#viewmodel-integration)
6. [Content Layout Examples](#content-layout-examples)

---

## Content vs. BottomSheetContent

The Bottom Sheet has two distinct content areas that serve different purposes:

### Main Content (`Content` property)
- **Visibility:** Always visible
- **Purpose:** Background content that remains visible behind the sheet
- **Use Case:** Main page content, list views, information that stays in view
- **Position:** Behind the Bottom Sheet overlay

### Bottom Sheet Content (`BottomSheetContent` property)
- **Visibility:** Only visible when sheet is in FullExpanded, HalfExpanded, or Collapsed states
- **Purpose:** Additional information, actions, or interactive elements
- **Use Case:** Details, forms, menus, additional data
- **Position:** On top of the main content

### Visual Layout Diagram

```
┌─────────────────────────────────────┐
│     Content (Always visible)        │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ BottomSheetContent          │   │
│  │ (Hidden when state=Hidden)  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Main Content

### Purpose

The main content is the background UI that remains visible while the Bottom Sheet is present. Use this when you want content to stay accessible behind the sheet.

### XAML Example: With Main Content

```xaml
<bottomSheet:SfBottomSheet x:Name="bottomSheet">
    <!-- Main Content: Background UI -->
    <bottomSheet:SfBottomSheet.Content>
        <VerticalStackLayout Padding="10" Spacing="10">
            <Label Text="Main Application Content" 
                   FontSize="18" 
                   FontAttributes="Bold"/>
            <Label Text="This content remains visible behind the sheet"
                   TextColor="Gray"/>
        </VerticalStackLayout>
    </bottomSheet:SfBottomSheet.Content>

    <!-- Bottom Sheet Content: Overlay UI -->
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <VerticalStackLayout Padding="10">
            <Label Text="Sheet Content" FontSize="16"/>
        </VerticalStackLayout>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

### C# Example: With Main Content

```csharp
var bottomSheet = new SfBottomSheet();

// Main content
var mainContent = new VerticalStackLayout 
{ 
    Padding = new Thickness(10), 
    Spacing = 10 
};
mainContent.Children.Add(new Label 
{ 
    Text = "Main Application Content", 
    FontSize = 18, 
    FontAttributes = FontAttributes.Bold 
});
mainContent.Children.Add(new Label 
{ 
    Text = "This content remains visible behind the sheet",
    TextColor = Colors.Gray
});

bottomSheet.Content = mainContent;

// Bottom sheet content
var sheetContent = new VerticalStackLayout { Padding = new Thickness(10) };
sheetContent.Children.Add(new Label { Text = "Sheet Content", FontSize = 16 });
bottomSheet.BottomSheetContent = sheetContent;
```

### Important Note

If you place the main content **outside** the Bottom Sheet, ensure the Bottom Sheet is the **last element** in the Grid layout:

```xaml
<Grid RowDefinitions="*" ColumnDefinitions="*">
    <!-- Main content outside Bottom Sheet -->
    <VerticalStackLayout>
        <Label Text="Background content"/>
    </VerticalStackLayout>
    
    <!-- Bottom Sheet must be last child -->
    <bottomSheet:SfBottomSheet x:Name="bottomSheet">
        <bottomSheet:SfBottomSheet.BottomSheetContent>
            <Label Text="Sheet content"/>
        </bottomSheet:SfBottomSheet.BottomSheetContent>
    </bottomSheet:SfBottomSheet>
</Grid>
```

---

## Bottom Sheet Content

### Purpose

The Bottom Sheet content is what users see when the sheet is expanded. This is where you display detailed information, forms, or interactive elements.

### XAML Example: Bottom Sheet Content Only

```xaml
<bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                           HalfExpandedRatio="0.35"
                           CornerRadius="15, 15, 0, 0"
                           ContentPadding="15">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <VerticalStackLayout Spacing="10">
            <Label Text="Details" FontSize="20" FontAttributes="Bold"/>
            <Label Text="Item 1" FontSize="14"/>
            <Label Text="Item 2" FontSize="14"/>
            <Label Text="Item 3" FontSize="14"/>
            <Button Text="Action" CornerRadius="5" Padding="10"/>
        </VerticalStackLayout>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

### Content Types

#### 1. Simple Text Content

```xaml
<bottomSheet:SfBottomSheet.BottomSheetContent>
    <Label Text="Simple text content"
           FontSize="16"
           Padding="20"/>
</bottomSheet:SfBottomSheet.BottomSheetContent>
```

#### 2. Structured Content (Grid)

```xaml
<bottomSheet:SfBottomSheet.BottomSheetContent>
    <Grid ColumnDefinitions="Auto, *" RowSpacing="10" Padding="15">
        <Label Text="Name:" FontAttributes="Bold"/>
        <Label Text="John Doe" Grid.Column="1"/>
        
        <Label Text="Email:" Grid.Row="1" FontAttributes="Bold"/>
        <Entry Grid.Row="1" Grid.Column="1" Placeholder="Enter email"/>
        
        <Label Text="Phone:" Grid.Row="2" FontAttributes="Bold"/>
        <Entry Grid.Row="2" Grid.Column="1" Placeholder="Enter phone"/>
    </Grid>
</bottomSheet:SfBottomSheet.BottomSheetContent>
```

#### 3. Complex Layout (ScrollView + StackLayout)

```xaml
<bottomSheet:SfBottomSheet.BottomSheetContent>
    <ScrollView>
        <VerticalStackLayout Padding="15" Spacing="10">
            <Label Text="Product Details" FontSize="18" FontAttributes="Bold"/>
            <Frame BorderColor="LightGray" Padding="10">
                <Grid RowSpacing="5">
                    <Label Text="{Binding ProductName}" FontSize="16" FontAttributes="Bold"/>
                    <Label Text="{Binding Description}" Grid.Row="1" TextColor="Gray"/>
                    <Label Text="{Binding Price, StringFormat='${0:F2}'}" 
                           Grid.Row="2" 
                           FontSize="14" 
                           TextColor="Green"
                           FontAttributes="Bold"/>
                </Grid>
            </Frame>
            <Button Text="Add to Cart" Command="{Binding AddToCartCommand}"/>
        </VerticalStackLayout>
    </ScrollView>
</bottomSheet:SfBottomSheet.BottomSheetContent>
```

---

## Data Binding Patterns

### Pattern 1: Binding Context Assignment

Set the BindingContext to a model instance or ViewModel:

**XAML:**
```xaml
<bottomSheet:SfBottomSheet x:Name="bottomSheet">
    <bottomSheet:SfBottomSheet.BottomSheetContent>
        <VerticalStackLayout>
            <Label Text="{Binding Title}" FontSize="20" FontAttributes="Bold"/>
            <Label Text="{Binding Description}" FontSize="14"/>
            <Label Text="{Binding Price, StringFormat='${0:F2}'}" TextColor="Green"/>
        </VerticalStackLayout>
    </bottomSheet:SfBottomSheet.BottomSheetContent>
</bottomSheet:SfBottomSheet>
```

**Code-Behind:**
```csharp
private void OnItemTapped(object? sender, ItemTappedEventArgs e)
{
    // Set the tapped item as BindingContext
    var item = e.Item as Product;
    bottomSheet.BottomSheetContent.BindingContext = item;
    bottomSheet.Show();
}
```

### Pattern 2: Relative Binding (Parent Page)

Bind directly to page-level properties:

**XAML:**
```xaml
<ContentPage x:Name="page">
    <bottomSheet:SfBottomSheet x:Name="bottomSheet">
        <bottomSheet:SfBottomSheet.BottomSheetContent>
            <Label Text="{Binding Source={x:Reference page}, Path=BindingContext.SelectedItem.Title}"/>
        </bottomSheet:SfBottomSheet.BottomSheetContent>
    </bottomSheet:SfBottomSheet>
</ContentPage>
```

### Pattern 3: Multi-Level Binding

Access nested properties through the binding path:

```xaml
<Label Text="{Binding Author.Name}" FontSize="14"/>
<Label Text="{Binding Author.Email}" TextColor="Gray"/>
```

### Pattern 4: String Formatting

Apply format strings to bound values:

```xaml
<!-- Currency formatting -->
<Label Text="{Binding Price, StringFormat='${0:F2}'}"/>

<!-- Date formatting -->
<Label Text="{Binding PublishDate, StringFormat='{0:yyyy-MM-dd}'}"/>

<!-- Percentage formatting -->
<Label Text="{Binding Rating, StringFormat='{0:P0}'}"/>

<!-- Custom formatting -->
<Label Text="{Binding ItemCount, StringFormat='Items: {0}'}"/>
```

---

## ViewModel Integration

### Complete ViewModel Example

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
        Products = new ObservableCollection<Product>
        {
            new Product { Id = 1, Name = "Laptop", Description = "High-performance laptop", Price = 999.99m },
            new Product { Id = 2, Name = "Phone", Description = "Latest smartphone", Price = 699.99m },
            new Product { Id = 3, Name = "Tablet", Description = "Portable tablet device", Price = 449.99m }
        };
    }

    private void OnAddToCart()
    {
        if (SelectedProduct != null)
        {
            // Add to cart logic
            Debug.WriteLine($"Added {SelectedProduct.Name} to cart");
        }
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected bool SetProperty<T>(ref T backingStore, T value, [CallerMemberName] string propertyName = "")
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

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public decimal Price { get; set; }
}
```

### XAML Using ViewModel

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
        <!-- ListView with products -->
        <ListView ItemsSource="{Binding Products}" ItemTapped="OnProductTapped" HasUnevenRows="True">
            <ListView.ItemTemplate>
                <DataTemplate>
                    <ViewCell>
                        <Grid ColumnDefinitions="*, Auto" Padding="10">
                            <VerticalStackLayout>
                                <Label Text="{Binding Name}" FontSize="16" FontAttributes="Bold"/>
                                <Label Text="{Binding Description}" FontSize="12" TextColor="Gray"/>
                            </VerticalStackLayout>
                            <Label Text="{Binding Price, StringFormat='${0:F2}'}" 
                                   Grid.Column="1" 
                                   TextColor="Green" 
                                   FontAttributes="Bold"
                                   VerticalOptions="Center"/>
                        </Grid>
                    </ViewCell>
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>

        <!-- Bottom Sheet for product details -->
        <bottomSheet:SfBottomSheet x:Name="productSheet" HalfExpandedRatio="0.35">
            <bottomSheet:SfBottomSheet.BottomSheetContent>
                <VerticalStackLayout Padding="15" Spacing="10">
                    <Label Text="{Binding SelectedProduct.Name}" FontSize="20" FontAttributes="Bold"/>
                    <Label Text="{Binding SelectedProduct.Description}" FontSize="14" TextColor="Gray"/>
                    <Label Text="{Binding SelectedProduct.Price, StringFormat='Price: ${0:F2}'}" 
                           FontSize="16" 
                           TextColor="Green" 
                           FontAttributes="Bold"/>
                    <Button Text="Add to Cart" Command="{Binding AddToCartCommand}"/>
                </VerticalStackLayout>
            </bottomSheet:SfBottomSheet.BottomSheetContent>
        </bottomSheet:SfBottomSheet>
    </Grid>
</ContentPage>
```

### Code-Behind

```csharp
private void OnProductTapped(object? sender, ItemTappedEventArgs e)
{
    var viewModel = this.BindingContext as ProductViewModel;
    if (viewModel != null)
    {
        viewModel.SelectedProduct = e.Item as Product;
        productSheet.Show();
    }
}
```

---

## Content Layout Examples

### Example 1: Card-Based Detail View

```xaml
<bottomSheet:SfBottomSheet.BottomSheetContent>
    <Frame CornerRadius="10" Padding="15" Margin="10" HasShadow="True">
        <VerticalStackLayout Spacing="15">
            <Label Text="{Binding Title}" FontSize="22" FontAttributes="Bold"/>
            
            <BoxView BackgroundColor="LightGray" HeightRequest="1"/>
            
            <VerticalStackLayout Spacing="5">
                <Label Text="Category" FontSize="12" TextColor="Gray" FontAttributes="Bold"/>
                <Label Text="{Binding Category}" FontSize="14"/>
            </VerticalStackLayout>
            
            <VerticalStackLayout Spacing="5">
                <Label Text="Description" FontSize="12" TextColor="Gray" FontAttributes="Bold"/>
                <Label Text="{Binding Description}" FontSize="14" LineBreakMode="WordWrap"/>
            </VerticalStackLayout>
            
            <BoxView BackgroundColor="LightGray" HeightRequest="1"/>
            
            <Button Text="Learn More" BackgroundColor="#007AFF" TextColor="White" CornerRadius="5"/>
        </VerticalStackLayout>
    </Frame>
</bottomSheet:SfBottomSheet.BottomSheetContent>
```

### Example 2: Form Input

```xaml
<bottomSheet:SfBottomSheet.BottomSheetContent>
    <ScrollView>
        <VerticalStackLayout Padding="15" Spacing="10">
            <Label Text="Edit Profile" FontSize="20" FontAttributes="Bold"/>
            
            <VerticalStackLayout Spacing="3">
                <Label Text="Full Name" FontSize="12" FontAttributes="Bold"/>
                <Entry x:Name="nameEntry" Text="{Binding FullName}" Placeholder="Enter name"/>
            </VerticalStackLayout>
            
            <VerticalStackLayout Spacing="3">
                <Label Text="Email" FontSize="12" FontAttributes="Bold"/>
                <Entry x:Name="emailEntry" Text="{Binding Email}" Placeholder="Enter email" Keyboard="Email"/>
            </VerticalStackLayout>
            
            <VerticalStackLayout Spacing="3">
                <Label Text="Phone" FontSize="12" FontAttributes="Bold"/>
                <Entry x:Name="phoneEntry" Text="{Binding Phone}" Placeholder="Enter phone" Keyboard="Telephone"/>
            </VerticalStackLayout>
            
            <Grid ColumnDefinitions="*, *" ColumnSpacing="10" Margin="0,15,0,0">
                <Button Text="Save" BackgroundColor="Green" TextColor="White" CornerRadius="5"/>
                <Button Text="Cancel" Grid.Column="1" BackgroundColor="Gray" TextColor="White" CornerRadius="5"/>
            </Grid>
        </VerticalStackLayout>
    </ScrollView>
</bottomSheet:SfBottomSheet.BottomSheetContent>
```

### Example 3: List Content

```xaml
<bottomSheet:SfBottomSheet.BottomSheetContent>
    <VerticalStackLayout Padding="15">
        <Label Text="Options" FontSize="18" FontAttributes="Bold" Margin="0,0,0,10"/>
        
        <CollectionView ItemsSource="{Binding Options}">
            <CollectionView.ItemTemplate>
                <DataTemplate>
                    <VerticalStackLayout Padding="10" Spacing="5">
                        <Frame BorderColor="LightGray" Padding="10" HasShadow="False">
                            <Grid ColumnDefinitions="*, Auto">
                                <Label Text="{Binding Name}" FontSize="14"/>
                                <Label Text="{Binding Value}" Grid.Column="1" TextColor="Gray"/>
                            </Grid>
                        </Frame>
                    </VerticalStackLayout>
                </DataTemplate>
            </CollectionView.ItemTemplate>
        </CollectionView>
    </VerticalStackLayout>
</bottomSheet:SfBottomSheet.BottomSheetContent>
```

---
