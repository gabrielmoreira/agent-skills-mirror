# Getting Started with Navigation Drawer

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Project Setup](#project-setup)
4. [Basic Implementation](#basic-implementation)
5. [Adding a Hamburger Menu](#adding-a-hamburger-menu)
6. [Common Pitfalls](#common-pitfalls)

---

## Prerequisites

- **.NET MAUI Project**: Create a new .NET MAUI App from the Visual Studio template
- **Visual Studio 2022** or later with .NET MAUI workload installed
- **NuGet Package Access**: Ensure your project can access NuGet packages

---

## Installation

### Step 1: Install Syncfusion MAUI Toolkit

1. In **Solution Explorer**, right-click your project
2. Select **Manage NuGet Packages**
3. Search for **Syncfusion.Maui.Toolkit**
4. Install the latest version
5. Let NuGet restore all dependencies

The package includes all Syncfusion MAUI components, including the Navigation Drawer.

### Step 2: Register Handler in MauiProgram.cs

Edit your `MauiProgram.cs` file to register the Syncfusion toolkit handler:

```csharp
using Syncfusion.Maui.Toolkit.Hosting;
using MyApp; // Your namespace

namespace MyApp
{
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
                .ConfigureSyncfusionToolkit(); // Add this line

            return builder.Build();
        }
    }
}
```

**Important:** The `ConfigureSyncfusionToolkit()` call must be included or the drawer won't render.

---

## Project Setup

### Import Namespace

In your XAML or code-behind, import the Navigation Drawer namespace:

**XAML:**
```xaml
xmlns:navigationDrawer="clr-namespace:Syncfusion.Maui.Toolkit.NavigationDrawer;assembly=Syncfusion.Maui.Toolkit"
```

**C#:**
```csharp
using Syncfusion.Maui.Toolkit.NavigationDrawer;
```

---

## Basic Implementation

### Minimal XAML Example

```xaml
<ContentPage
    xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
    xmlns:navigationDrawer="clr-namespace:Syncfusion.Maui.Toolkit.NavigationDrawer;assembly=Syncfusion.Maui.Toolkit"
    x:Class="NavigationDrawerApp.MainPage"
    Title="Navigation Drawer">

    <navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer">
        <navigationDrawer:SfNavigationDrawer.ContentView>
            <Grid BackgroundColor="White" RowDefinitions="Auto,*">
                <!-- Header -->
                <Label Grid.Row="0" 
                       Text="Main Content" 
                       FontSize="20" 
                       Padding="20" 
                       BackgroundColor="#6750A4"
                       TextColor="White"/>
                
                <!-- Main Content Area -->
                <Label Grid.Row="1" 
                       Text="Welcome to Navigation Drawer" 
                       HorizontalOptions="Center" 
                       VerticalOptions="Center" 
                       FontSize="18"/>
            </Grid>
        </navigationDrawer:SfNavigationDrawer.ContentView>
    </navigationDrawer:SfNavigationDrawer>

</ContentPage>
```

### Minimal C# Example

```csharp
using Syncfusion.Maui.Toolkit.NavigationDrawer;
using Microsoft.Maui.Controls;

namespace NavigationDrawerApp
{
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();

            // Create drawer
            var navigationDrawer = new SfNavigationDrawer();

            // Create main content
            var mainContent = new Grid 
            { 
                BackgroundColor = Colors.White,
                RowDefinitions = new RowDefinitionCollection
                {
                    new RowDefinition { Height = new GridLength(1, GridUnitType.Auto) },
                    new RowDefinition { Height = new GridLength(1, GridUnitType.Star) }
                }
            };

            // Add header
            var headerLabel = new Label
            {
                Text = "Main Content",
                FontSize = 20,
                Padding = 20,
                BackgroundColor = Color.FromArgb("#6750A4"),
                TextColor = Colors.White
            };
            mainContent.Add(headerLabel, 0, 0);

            // Add content
            var contentLabel = new Label
            {
                Text = "Welcome to Navigation Drawer",
                HorizontalOptions = LayoutOptions.Center,
                VerticalOptions = LayoutOptions.Center,
                FontSize = 18
            };
            mainContent.Add(contentLabel, 0, 1);

            navigationDrawer.ContentView = mainContent;
            this.Content = navigationDrawer;
        }
    }
}
```

**⚠️ Critical Requirement:** Setting `ContentView` is **mandatory**. Without it, the drawer will not display.

---

## Adding a Hamburger Menu

A hamburger menu button allows users to toggle the drawer. Here's the complete implementation:

### XAML with Hamburger Button

```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer">
    <navigationDrawer:SfNavigationDrawer.DrawerSettings>
        <navigationDrawer:DrawerSettings DrawerWidth="250"/>
    </navigationDrawer:SfNavigationDrawer.DrawerSettings>
    
    <navigationDrawer:SfNavigationDrawer.ContentView>
        <Grid BackgroundColor="White" RowDefinitions="Auto,*">
            <!-- Header with Hamburger Button -->
            <HorizontalStackLayout Grid.Row="0" 
                                   BackgroundColor="#6750A4" 
                                   Spacing="10" 
                                   Padding="5,0,0,0">
                <ImageButton x:Name="hamburgerButton"
                             HeightRequest="50"
                             WidthRequest="50"
                             HorizontalOptions="Start"
                             Source="hamburger_icon.png"
                             BackgroundColor="#6750A4"
                             Clicked="OnHamburgerClicked"/>
                <Label x:Name="headerLabel"
                       HeightRequest="50"
                       HorizontalTextAlignment="Center"
                       VerticalTextAlignment="Center"
                       Text="Home"
                       FontSize="16"
                       TextColor="White"
                       BackgroundColor="#6750A4"/>
            </HorizontalStackLayout>
            
            <!-- Main Content -->
            <Label Grid.Row="1"
                   x:Name="contentLabel"
                   VerticalOptions="Center"
                   HorizontalOptions="Center"
                   Text="Content View"
                   FontSize="14"
                   TextColor="Black"/>
        </Grid>
    </navigationDrawer:SfNavigationDrawer.ContentView>
</navigationDrawer:SfNavigationDrawer>
```

### Code-Behind for Hamburger Menu

```csharp
public partial class MainPage : ContentPage
{
    private SfNavigationDrawer navigationDrawer;

    public MainPage()
    {
        InitializeComponent();
        navigationDrawer = this.FindByName<SfNavigationDrawer>("navigationDrawer");
    }

    private void OnHamburgerClicked(object sender, EventArgs e)
    {
        // Toggle drawer open/closed
        navigationDrawer.ToggleDrawer();
    }
}
```

**Alternative using DrawerToggled property:**
```csharp
private void OnHamburgerClicked(object sender, EventArgs e)
{
    // Set to true to open, false to close
    navigationDrawer.IsOpen = !navigationDrawer.IsOpen;
}
```

---

## Common Pitfalls

### ❌ Missing ContentView

**Problem:** Drawer doesn't appear or crashes.

**Solution:** Always set `ContentView` property:
```csharp
navigationDrawer.ContentView = new Grid(); // Required
```

### ❌ Handler Not Registered

**Problem:** "Unable to resolve symbol 'SfNavigationDrawer'" or drawer not rendering.

**Solution:** Add `ConfigureSyncfusionToolkit()` in `MauiProgram.cs`:
```csharp
.ConfigureSyncfusionToolkit()
```

### ❌ Wrong Namespace

**Problem:** XAML doesn't recognize navigationDrawer prefix.

**Solution:** Ensure correct namespace in ContentPage:
```xaml
xmlns:navigationDrawer="clr-namespace:Syncfusion.Maui.Toolkit.NavigationDrawer;assembly=Syncfusion.Maui.Toolkit"
```

### ❌ Image Not Found

**Problem:** Hamburger icon doesn't show in button.

**Solution:** Place image in `Resources/Images/` folder and reference it:
```xaml
Source="hamburger_icon.png"
```

### ❌ Drawer Not Toggling

**Problem:** ToggleDrawer() method doesn't work.

**Solution:** Ensure you're calling it on the correct drawer instance:
```csharp
var drawer = this.FindByName<SfNavigationDrawer>("navigationDrawer");
drawer.ToggleDrawer(); // Use the instance, not a local variable
```

---

## Best Practices

✅ **Do:**
- Set ContentView with meaningful main content
- Use DrawerSettings for configuration
- Register handler in MauiProgram.cs
- Place images in Resources/Images folder
- Use meaningful drawer header/content layouts

❌ **Don't:**
- Forget to set ContentView
- Omit the ConfigureSyncfusionToolkit() call
- Use inconsistent drawer sizing (too narrow/wide)
- Load large images in drawer headers
- Nest drawers (one drawer per page)

