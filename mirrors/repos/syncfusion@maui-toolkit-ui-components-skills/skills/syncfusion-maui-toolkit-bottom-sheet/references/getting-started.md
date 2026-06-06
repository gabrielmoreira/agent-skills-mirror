# Getting Started with .NET MAUI Bottom Sheet

## Table of Contents
1. [Project Setup](#project-setup)
2. [Install NuGet Package](#install-nuget-package)
3. [Register the Handler](#register-the-handler)
4. [Basic Initialization](#basic-initialization)
5. [First Working Example](#first-working-example)

---

## Install NuGet Package

### Using NuGet Package Manager (Visual Studio)

1. In **Solution Explorer**, right-click your project
2. Select **Manage NuGet Packages**
3. Go to the **Browse** tab
4. Search for `Syncfusion.Maui.Toolkit`
5. Select the latest version
6. Click **Install**
7. Review and accept the license terms if prompted
8. Wait for installation to complete

### Using Package Manager Console

```powershell
Install-Package Syncfusion.Maui.Toolkit -Version <latest-version>
```

### Using .NET CLI

```bash
dotnet add package Syncfusion.Maui.Toolkit
```

### Verify Installation

After installation, check your `.csproj` file contains:
```xml
<ItemGroup>
    <PackageReference Include="Syncfusion.Maui.Toolkit" Version="x.x.x" />
</ItemGroup>
```

---

## Register the Handler

### Step 1: Open MauiProgram.cs

The handler registration enables the SfBottomSheet control across all platforms (Android, iOS, Windows, macOS).

### Step 2: Add Syncfusion Namespace

```csharp
using Syncfusion.Maui.Toolkit.Hosting;
```

### Step 3: Register Handler in CreateMauiApp

Modify the `MauiProgram.CreateMauiApp()` method:

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            })
            .ConfigureSyncfusionToolkit();  // Add this line

        return builder.Build();
    }
}
```

**Important:** Call `ConfigureSyncfusionToolkit()` after other configurations for proper initialization.

---

## Basic Initialization

### XAML Declaration

Import the namespace and declare the control:

```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:bottomSheet="clr-namespace:Syncfusion.Maui.Toolkit.BottomSheet;assembly=Syncfusion.Maui.Toolkit"
             x:Class="BottomSheetDemo.MainPage">
    
    <Grid RowDefinitions="*" ColumnDefinitions="*">
        <!-- Main Content -->
        <Button Text="Open Bottom Sheet" Clicked="OnOpenClicked" />
        
        <!-- Bottom Sheet Control -->
        <bottomSheet:SfBottomSheet x:Name="bottomSheet">
            <bottomSheet:SfBottomSheet.BottomSheetContent>
                <VerticalStackLayout Padding="20" Spacing="10">
                    <Label Text="Bottom Sheet Content" 
                           FontSize="20" 
                           FontAttributes="Bold"/>
                </VerticalStackLayout>
            </bottomSheet:SfBottomSheet.BottomSheetContent>
        </bottomSheet:SfBottomSheet>
    </Grid>
</ContentPage>
```

### C# Code-Behind

```csharp
using Syncfusion.Maui.Toolkit.BottomSheet;

namespace BottomSheetDemo;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void OnOpenClicked(object sender, EventArgs e)
    {
        bottomSheet.Show();
    }
}
```

### Programmatic Creation (C#)

```csharp
using Syncfusion.Maui.Toolkit.BottomSheet;

public class BottomSheetExample
{
    public static Grid CreateBottomSheetUI()
    {
        // Create Bottom Sheet control
        var bottomSheet = new SfBottomSheet();
        
        // Create content
        var content = new VerticalStackLayout 
        { 
            Padding = new Thickness(20), 
            Spacing = 10 
        };
        
        var label = new Label 
        { 
            Text = "Bottom Sheet Content",
            FontSize = 20,
            FontAttributes = FontAttributes.Bold
        };
        
        content.Children.Add(label);
        bottomSheet.BottomSheetContent = content;
        
        // Create main layout
        var grid = new Grid();
        
        var button = new Button 
        { 
            Text = "Open Bottom Sheet",
            Command = new Command(() => bottomSheet.Show())
        };
        
        grid.Children.Add(button);
        grid.Children.Add(bottomSheet);
        
        return grid;
    }
}
```

---

## First Working Example

### Complete Working Sample

This example demonstrates a Bottom Sheet that displays book information when a user taps a ListView item.

**Model (Book.cs):**
```csharp
public class Book
{
    public string Title { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string Genre { get; set; } = string.Empty;
    public double Rating { get; set; }
    public decimal Price { get; set; }
}
```

**ViewModel (BookViewModel.cs):**
```csharp
using System.Collections.ObjectModel;

public class BookViewModel
{
    public ObservableCollection<Book> Books { get; set; }

    public BookViewModel()
    {
        Books = new ObservableCollection<Book>
        {
            new Book 
            { 
                Title = "C# Programming", 
                Author = "John Doe", 
                Genre = "Programming", 
                Rating = 4.5, 
                Price = 29.99m 
            },
            new Book 
            { 
                Title = "MAUI Essentials", 
                Author = "Jane Smith", 
                Genre = "Mobile Development", 
                Rating = 4.8, 
                Price = 39.99m 
            },
            new Book 
            { 
                Title = "Web Development", 
                Author = "Bob Johnson", 
                Genre = "Web Development", 
                Rating = 4.2, 
                Price = 34.99m 
            }
        };
    }
}
```

**XAML (MainPage.xaml):**
```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:bottomSheet="clr-namespace:Syncfusion.Maui.Toolkit.BottomSheet;assembly=Syncfusion.Maui.Toolkit"
             xmlns:local="clr-namespace:BottomSheetDemo.ViewModel"
             x:Class="BottomSheetDemo.MainPage"
             Title="Bottom Sheet Demo">

    <Grid RowDefinitions="*" ColumnDefinitions="*" Padding="10">
        <Grid.BindingContext>
            <local:BookViewModel />
        </Grid.BindingContext>

        <!-- Main Content: Book List -->
        <ListView ItemsSource="{Binding Books}" 
                  ItemTapped="OnBookTapped" 
                  HasUnevenRows="True">
            <ListView.ItemTemplate>
                <DataTemplate>
                    <ViewCell>
                        <Grid ColumnDefinitions="*, 60" Padding="10">
                            <VerticalStackLayout>
                                <Label Text="{Binding Title}" 
                                       FontSize="16" 
                                       FontAttributes="Bold"/>
                                <Label Text="{Binding Author}" 
                                       FontSize="12" 
                                       TextColor="Gray"/>
                            </VerticalStackLayout>
                            <Label Text="{Binding Rating, StringFormat='{0:F1}/5'}" 
                                   Grid.Column="1" 
                                   HorizontalOptions="Center" 
                                   VerticalOptions="Center"
                                   FontAttributes="Bold"/>
                        </Grid>
                    </ViewCell>
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>

        <!-- Bottom Sheet: Book Details -->
        <bottomSheet:SfBottomSheet x:Name="bottomSheet" 
                                   HalfExpandedRatio="0.35" 
                                   CornerRadius="15, 15, 0, 0"
                                   ContentPadding="10">
            <bottomSheet:SfBottomSheet.BottomSheetContent>
                <VerticalStackLayout Spacing="10" Padding="10" x:Name="bottomSheetContent">
                    <Label Text="{Binding Title}" 
                           FontSize="20" 
                           FontAttributes="Bold"/>
                    <Grid ColumnDefinitions="80, *" ColumnSpacing="10">
                        <Label Text="Author:" 
                               FontAttributes="Bold"/>
                        <Label Text="{Binding Author}" 
                               Grid.Column="1"/>
                    </Grid>
                    <Grid ColumnDefinitions="80, *" ColumnSpacing="10">
                        <Label Text="Genre:" 
                               FontAttributes="Bold"/>
                        <Label Text="{Binding Genre}" 
                               Grid.Column="1"/>
                    </Grid>
                    <Grid ColumnDefinitions="80, *" ColumnSpacing="10">
                        <Label Text="Rating:" 
                               FontAttributes="Bold"/>
                        <Label Text="{Binding Rating, StringFormat='{0:F1}/5'}" 
                               Grid.Column="1"/>
                    </Grid>
                    <Grid ColumnDefinitions="80, *" ColumnSpacing="10">
                        <Label Text="Price:" 
                               FontAttributes="Bold"/>
                        <Label Text="{Binding Price, StringFormat='${0:F2}'}" 
                               Grid.Column="1"
                               FontAttributes="Bold"
                               TextColor="Green"/>
                    </Grid>
                </VerticalStackLayout>
            </bottomSheet:SfBottomSheet.BottomSheetContent>
        </bottomSheet:SfBottomSheet>
    </Grid>
</ContentPage>
```

**Code-Behind (MainPage.xaml.cs):**
```csharp
using Syncfusion.Maui.Toolkit.BottomSheet;

namespace BottomSheetDemo;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void OnBookTapped(object? sender, ItemTappedEventArgs e)
    {
        // Set the tapped book as the binding context
        bottomSheetContent.BindingContext = e.Item;
        
        // Show the bottom sheet
        bottomSheet.Show();
    }
}
```

### Expected Behavior

1. **Application starts** → ListView displays 3 books
2. **User taps a book** → Bottom sheet slides up with HalfExpanded state
3. **Book details visible** → Title, Author, Genre, Rating, Price displayed
4. **User swipes up** → Bottom sheet fully expands
5. **User swipes down or taps outside** → Bottom sheet collapses

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "SfBottomSheet not found" | Namespace not imported | Add `xmlns:bottomSheet="clr-namespace:Syncfusion.Maui.Toolkit.BottomSheet;assembly=Syncfusion.Maui.Toolkit"` |
| Control not appearing | Handler not registered | Ensure `ConfigureSyncfusionToolkit()` is called in MauiProgram.cs |
| Binding not working | ViewModel not set | Set BindingContext explicitly in code-behind or XAML |
| Content not showing | BottomSheetContent not set | Verify you're using `BottomSheetContent` property, not `Content` |
| Crashes on initialization | Missing dependencies | Verify Syncfusion.Maui.Toolkit NuGet package is installed correctly |

---
