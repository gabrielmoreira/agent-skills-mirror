# Configuring Drawer Content

## Table of Contents
1. [Drawer Structure](#drawer-structure)
2. [Header Content](#header-content)
3. [Main Drawer Content](#main-drawer-content)
4. [Footer Content](#footer-content)
5. [Complete Example](#complete-example)
6. [Dynamic Content Switching](#dynamic-content-switching)
7. [Styling Drawer Content](#styling-drawer-content)

---

## Drawer Structure

The drawer pane consists of three optional sections:

```
┌─────────────────────┐
│  DrawerHeaderView   │ (Optional)
│  (DrawerHeaderHeight)
├─────────────────────┤
│ DrawerContentView   │ (Mandatory - allocates space)
│ (Flexible height)   │
├─────────────────────┤
│  DrawerFooterView   │ (Optional)
│  (DrawerFooterHeight)
└─────────────────────┘
```

- **Header:** Top section, typically user profile or title
- **Content:** Middle section, main menu items (list, buttons, etc.)
- **Footer:** Bottom section, logout button or app info

---

## Header Content

The header is displayed at the top of the drawer pane. Use the `DrawerHeaderView` property.

### Basic Header

```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer">
    <navigationDrawer:SfNavigationDrawer.DrawerSettings>
        <navigationDrawer:DrawerSettings DrawerHeaderHeight="160">
            <navigationDrawer:DrawerSettings.DrawerHeaderView>
                <Grid BackgroundColor="#6750A4" Padding="10">
                    <VerticalStackLayout Spacing="10" VerticalOptions="Center" HorizontalOptions="Center">
                        <Image Source="user_profile.png" 
                               HeightRequest="80" 
                               WidthRequest="80"/>
                        <Label Text="John Doe" 
                               FontSize="16" 
                               TextColor="White"
                               HorizontalTextAlignment="Center"/>
                        <Label Text="john@example.com" 
                               FontSize="12" 
                               TextColor="#E0E0E0"
                               HorizontalTextAlignment="Center"/>
                    </VerticalStackLayout>
                </Grid>
            </navigationDrawer:DrawerSettings.DrawerHeaderView>
        </navigationDrawer:DrawerSettings>
    </navigationDrawer:SfNavigationDrawer.DrawerSettings>
</navigationDrawer:SfNavigationDrawer>
```

### Header in C#

```csharp
var drawerSettings = new DrawerSettings()
{
    DrawerHeaderHeight = 160,
};

var headerGrid = new Grid 
{ 
    BackgroundColor = Color.FromArgb("#6750A4"),
    Padding = 10
};

var stackLayout = new VerticalStackLayout 
{ 
    Spacing = 10,
    VerticalOptions = LayoutOptions.Center,
    HorizontalOptions = LayoutOptions.Center
};

var profileImage = new Image
{
    Source = "user_profile.png",
    HeightRequest = 80,
    WidthRequest = 80
};

var nameLabel = new Label
{
    Text = "John Doe",
    FontSize = 16,
    TextColor = Colors.White,
    HorizontalTextAlignment = TextAlignment.Center
};

var emailLabel = new Label
{
    Text = "john@example.com",
    FontSize = 12,
    TextColor = Color.FromArgb("#E0E0E0"),
    HorizontalTextAlignment = TextAlignment.Center
};

stackLayout.Children.Add(profileImage);
stackLayout.Children.Add(nameLabel);
stackLayout.Children.Add(emailLabel);

headerGrid.Children.Add(stackLayout);
drawerSettings.DrawerHeaderView = headerGrid;

navigationDrawer.DrawerSettings = drawerSettings;
```

### Adjusting Header Height

The `DrawerHeaderHeight` property controls header height:

```csharp
// Small header - 80 pixels
drawerSettings.DrawerHeaderHeight = 80;

// Large header - 200 pixels
drawerSettings.DrawerHeaderHeight = 200;

// Remove header by setting to 0
drawerSettings.DrawerHeaderHeight = 0;
```

---

## Main Drawer Content

The drawer content view is the main area between header and footer. It's **mandatory** to allocate space for the drawer pane.

### Content with ListView

```xaml
<navigationDrawer:DrawerSettings.DrawerContentView>
    <ListView x:Name="menuListView" ItemSelected="OnMenuItemSelected">
        <ListView.ItemTemplate>
            <DataTemplate>
                <ViewCell>
                    <VerticalStackLayout HeightRequest="50" Padding="15,10">
                        <Label Text="{Binding MenuName}" 
                               FontSize="16" 
                               TextColor="Black"/>
                    </VerticalStackLayout>
                </ViewCell>
            </DataTemplate>
        </ListView.ItemTemplate>
    </ListView>
</navigationDrawer:DrawerSettings.DrawerContentView>
```

### Binding Data to Drawer

```csharp
public class MenuItemModel
{
    public string MenuName { get; set; }
    public string MenuIcon { get; set; }
}

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        
        var menuItems = new List<MenuItemModel>
        {
            new MenuItemModel { MenuName = "Home", MenuIcon = "home_icon.png" },
            new MenuItemModel { MenuName = "Profile", MenuIcon = "profile_icon.png" },
            new MenuItemModel { MenuName = "Settings", MenuIcon = "settings_icon.png" },
            new MenuItemModel { MenuName = "About", MenuIcon = "about_icon.png" }
        };
        
        var listView = this.FindByName<ListView>("menuListView");
        listView.ItemsSource = menuItems;
    }

    private void OnMenuItemSelected(object sender, SelectedItemChangedEventArgs e)
    {
        var selectedItem = e.SelectedItem as MenuItemModel;
        // Handle menu item selection
        navigationDrawer.ToggleDrawer();
    }
}
```

### Content with Grid and Buttons

```xaml
<navigationDrawer:DrawerSettings.DrawerContentView>
    <VerticalStackLayout Padding="10" Spacing="5">
        <Button Text="Home" Clicked="OnHomeClicked"/>
        <Button Text="Profile" Clicked="OnProfileClicked"/>
        <Button Text="Settings" Clicked="OnSettingsClicked"/>
        <Button Text="Help" Clicked="OnHelpClicked"/>
    </VerticalStackLayout>
</navigationDrawer:DrawerSettings.DrawerContentView>
```

---

## Footer Content

The footer is displayed at the bottom of the drawer pane, useful for logout or app information.

### Footer with Logout Button

```xaml
<navigationDrawer:DrawerSettings.DrawerFooterView>
    <Grid BackgroundColor="#F5F5F5" Padding="10">
        <Button Text="Logout" 
                Clicked="OnLogoutClicked"
                BackgroundColor="#FF3B30"
                TextColor="White"/>
    </Grid>
</navigationDrawer:DrawerSettings.DrawerFooterView>
```

### Footer in C#

```csharp
var footerGrid = new Grid 
{ 
    BackgroundColor = Color.FromArgb("#F5F5F5"),
    Padding = 10
};

var logoutButton = new Button
{
    Text = "Logout",
    BackgroundColor = Color.FromArgb("#FF3B30"),
    TextColor = Colors.White
};

logoutButton.Clicked += async (sender, e) => 
{
    await DisplayAlert("Logout", "You have been logged out", "OK");
};

footerGrid.Children.Add(logoutButton);
drawerSettings.DrawerFooterView = footerGrid;
drawerSettings.DrawerFooterHeight = 60;
```

### Adjusting Footer Height

```csharp
// Small footer - 60 pixels
drawerSettings.DrawerFooterHeight = 60;

// Large footer - 120 pixels
drawerSettings.DrawerFooterHeight = 120;

// Remove footer by setting to 0
drawerSettings.DrawerFooterHeight = 0;
```

---

## Complete Example

Here's a complete implementation with header, content, and footer:

```xaml
<navigationDrawer:SfNavigationDrawer x:Name="navigationDrawer">
    <navigationDrawer:SfNavigationDrawer.DrawerSettings>
        <navigationDrawer:DrawerSettings DrawerWidth="250"
                                         DrawerHeaderHeight="160"
                                         DrawerFooterHeight="70">
            <!-- Header -->
            <navigationDrawer:DrawerSettings.DrawerHeaderView>
                <Grid BackgroundColor="#6750A4" Padding="10">
                    <VerticalStackLayout Spacing="10" 
                                        VerticalOptions="Center" 
                                        HorizontalOptions="Center">
                        <Image Source="user.png" 
                               HeightRequest="80" 
                               WidthRequest="80"/>
                        <Label Text="James Pollock" 
                               FontSize="16" 
                               TextColor="White"
                               HorizontalTextAlignment="Center"/>
                    </VerticalStackLayout>
                </Grid>
            </navigationDrawer:DrawerSettings.DrawerHeaderView>
            
            <!-- Main Content -->
            <navigationDrawer:DrawerSettings.DrawerContentView>
                <ListView x:Name="menuListView" ItemSelected="OnMenuItemSelected">
                    <ListView.ItemTemplate>
                        <DataTemplate>
                            <ViewCell>
                                <VerticalStackLayout HeightRequest="45" Padding="15,10">
                                    <Label Text="{Binding}" 
                                           FontSize="14" 
                                           TextColor="Black"/>
                                </VerticalStackLayout>
                            </ViewCell>
                        </DataTemplate>
                    </ListView.ItemTemplate>
                </ListView>
            </navigationDrawer:DrawerSettings.DrawerContentView>
            
            <!-- Footer -->
            <navigationDrawer:DrawerSettings.DrawerFooterView>
                <Grid BackgroundColor="#F5F5F5" Padding="10">
                    <Button Text="Logout" 
                            Clicked="OnLogoutClicked"
                            BackgroundColor="#FF3B30"
                            TextColor="White"/>
                </Grid>
            </navigationDrawer:DrawerSettings.DrawerFooterView>
        </navigationDrawer:DrawerSettings>
    </navigationDrawer:SfNavigationDrawer.DrawerSettings>
    
    <!-- Main Content Area -->
    <navigationDrawer:SfNavigationDrawer.ContentView>
        <Grid BackgroundColor="White" RowDefinitions="Auto,*">
            <HorizontalStackLayout Spacing="10" Padding="5,0,0,0" BackgroundColor="#6750A4">
                <ImageButton x:Name="hamburgerButton"
                             HeightRequest="50"
                             WidthRequest="50"
                             HorizontalOptions="Start"
                             Source="hamburger.png"
                             BackgroundColor="#6750A4"
                             Clicked="OnHamburgerClicked"/>
                <Label Text="Home" 
                       HeightRequest="50" 
                       FontSize="16" 
                       TextColor="White"
                       VerticalOptions="Center"/>
            </HorizontalStackLayout>
            <Label Grid.Row="1" 
                   x:Name="contentLabel" 
                   Text="Main Content Area" 
                   FontSize="18"
                   HorizontalOptions="Center"
                   VerticalOptions="Center"/>
        </Grid>
    </navigationDrawer:SfNavigationDrawer.ContentView>
</navigationDrawer:SfNavigationDrawer>
```

---

## Dynamic Content Switching

Update ContentView based on menu selection:

```csharp
private void OnMenuItemSelected(object sender, SelectedItemChangedEventArgs e)
{
    var selectedItem = e.SelectedItem?.ToString();
    
    switch (selectedItem)
    {
        case "Home":
            UpdateMainContent("Home Page", "Welcome to Home");
            break;
        case "Profile":
            UpdateMainContent("Profile", "Your profile information");
            break;
        case "Settings":
            UpdateMainContent("Settings", "Adjust your preferences");
            break;
        case "About":
            UpdateMainContent("About", "About this application");
            break;
    }
    
    navigationDrawer.ToggleDrawer();
}

private void UpdateMainContent(string title, string content)
{
    var contentLabel = this.FindByName<Label>("contentLabel");
    contentLabel.Text = content;
    
    var headerLabel = this.FindByName<Label>("headerLabel");
    headerLabel.Text = title;
}
```

---

## Styling Drawer Content

### Background Colors

```csharp
var drawerSettings = new DrawerSettings
{
    ContentBackground = Color.FromArgb("#FFFFFF")
};
```

### Custom Content Layout

```csharp
// Use StackLayout for organized menu
var contentStack = new VerticalStackLayout { Spacing = 10, Padding = 10 };

foreach (var item in menuItems)
{
    var button = new Button { Text = item.MenuName };
    button.Clicked += (s, e) => HandleMenuSelection(item);
    contentStack.Children.Add(button);
}

drawerSettings.DrawerContentView = contentStack;
```

