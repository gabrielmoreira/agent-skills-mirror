# Common Use Cases & Patterns

## Table of Contents
1. [Settings/Preferences Interface](#settingpreferences-interface)
2. [Multi-Step Form Wizard](#multi-step-form-wizard)
3. [Data Dashboard Layout](#data-dashboard-layout)
4. [Document Viewer](#document-viewer)
5. [Best Practices](#best-practices)
6. [Anti-Patterns](#anti-patterns)
7. [Accessibility Guidelines](#accessibility-guidelines)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Settings/Preferences Interface

### Use Case
Organize application settings into logical categories (Account, Display, Notifications, Privacy).

### Implementation

```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage 
    xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
    xmlns:tabView="clr-namespace:Syncfusion.Maui.Toolkit.TabView;assembly=Syncfusion.Maui.Toolkit"
    Title="Settings">
    
    <ContentPage.BindingContext>
        <local:SettingsViewModel />
    </ContentPage.BindingContext>

    <ContentPage.Content>
            <tabView:SfTabView TabBarPlacement="Top" IndicatorPlacement="Bottom">
        <tabView:SfTabView.Items>
            <!-- Account Settings -->
            <tabView:SfTabItem Header="Account">
                <tabView:SfTabItem.Content>
                    <StackLayout Padding="20" Spacing="15">
                        <Label Text="Account Settings" FontSize="16" FontAttributes="Bold"/>
                        <Frame BorderColor="LightGray" Padding="10">
                            <StackLayout Spacing="10">
                                <Label Text="Username"/>
                                <Entry Text="{Binding Username}" Placeholder="Enter username"/>
                                <Label Text="Email"/>
                                <Entry Text="{Binding Email}" Placeholder="Enter email"/>
                                <Button Text="Save Changes" Command="{Binding SaveCommand}"/>
                            </StackLayout>
                        </Frame>
                    </StackLayout>
                </tabView:SfTabItem.Content>
            </tabView:SfTabItem>

            <!-- Display Settings -->
            <tabView:SfTabItem Header="Display">
                <tabView:SfTabItem.Content>
                    <StackLayout Padding="20" Spacing="15">
                        <Label Text="Display Settings" FontSize="16" FontAttributes="Bold"/>
                        <Frame BorderColor="LightGray" Padding="10">
                            <StackLayout Spacing="10">
                                <Label Text="Theme"/>
                                <Picker ItemsSource="{Binding Themes}" SelectedItem="{Binding SelectedTheme}"/>
                                <Label Text="Font Size"/>
                                <Slider Value="{Binding FontSize}" Minimum="10" Maximum="24"/>
                            </StackLayout>
                        </Frame>
                    </StackLayout>
                </tabView:SfTabItem.Content>
            </tabView:SfTabItem>

            <!-- Notification Settings -->
            <tabView:SfTabItem Header="Notifications">
                <tabView:SfTabItem.Content>
                    <StackLayout Padding="20" Spacing="15">
                        <Label Text="Notification Settings" FontSize="16" FontAttributes="Bold"/>
                        <Frame BorderColor="LightGray" Padding="10">
                            <Grid RowDefinitions="*,*,*" ColumnDefinitions="Auto,Auto" RowSpacing="10">
                                <CheckBox IsChecked="{Binding PushNotificationsEnabled}" Grid.Row="0" Grid.Column="0"/>
                                <Label Text="Push Notifications" Grid.Row="0" Grid.Column="1"/>
                                <CheckBox IsChecked="{Binding EmailNotificationsEnabled}" Grid.Row="1" Grid.Column="0"/>
                                <Label Text="Email Notifications" Grid.Row="1" Grid.Column="1"/>
                                <CheckBox IsChecked="{Binding SMSNotificationsEnabled}" Grid.Row="2" Grid.Column="0"/>
                                <Label Text="SMS Notifications" Grid.Row="2" Grid.Column="1"/>
                            </Grid>
                        </Frame>
                    </StackLayout>
                </tabView:SfTabItem.Content>
            </tabView:SfTabItem>

            <!-- Privacy Settings -->
            <tabView:SfTabItem Header="Privacy">
                <tabView:SfTabItem.Content>
                    <StackLayout Padding="20" Spacing="15">
                        <Label Text="Privacy Settings" FontSize="16" FontAttributes="Bold"/>
                        <Frame BorderColor="LightGray" Padding="10">
                            <Grid RowDefinitions="*,*,*" ColumnDefinitions="Auto,Auto" RowSpacing="10">
                                <CheckBox IsChecked="{Binding ProfilePublic}" Grid.Row="0" Grid.Column="0"/>
                                <Label Text="Make Profile Public" Grid.Row="0" Grid.Column="1"/>
                                <CheckBox IsChecked="{Binding DataCollection}" Grid.Row="1" Grid.Column="0"/>
                                <Label Text="Allow Data Collection" Grid.Row="1" Grid.Column="1"/>
                                <Label Text="Privacy Policy" TextDecorations="Underline" TextColor="Blue" Grid.Row="2" Grid.ColumnSpan="2"/>
                            </Grid>
                        </Frame>
                    </StackLayout>
                </tabView:SfTabItem.Content>
            </tabView:SfTabItem>
        </tabView:SfTabView.Items>
    </tabView:SfTabView>
    </ContentPage.Content>
</ContentPage>
```

### ViewModel

```csharp
public class SettingsViewModel : INotifyPropertyChanged
{
    private string username;
    private string email;
    private bool pushNotificationsEnabled;

    public string Username
    {
        get { return username; }
        set { SetProperty(ref username, value); }
    }

    public string Email
    {
        get { return email; }
        set { SetProperty(ref email, value); }
    }

    public bool PushNotificationsEnabled
    {
        get { return pushNotificationsEnabled; }
        set { SetProperty(ref pushNotificationsEnabled, value); }
    }

    public ICommand SaveCommand { get; }

    public SettingsViewModel()
    {
        SaveCommand = new Command(SaveSettings);
    }

    private async void SaveSettings()
    {
        // Save settings to storage
        await Application.Current.MainPage.DisplayAlert("Success", "Settings saved", "OK");
    }

    protected bool SetProperty<T>(ref T storage, T value, [CallerMemberName] string propertyName = null)
    {
        if (EqualityComparer<T>.Default.Equals(storage, value))
            return false;

        storage = value;
        OnPropertyChanged(propertyName);
        return true;
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

---

## Multi-Step Form Wizard

### Use Case
Guide users through a multi-step process (Registration, Payment, Confirmation).

### Implementation

```csharp
public partial class WizardPage : ContentPage
{
    private readonly WizardViewModel viewModel;
    private int currentStep = 0;

    public WizardPage()
    {
        InitializeComponent();
        viewModel = new WizardViewModel();
        this.BindingContext = viewModel;

        tabView.SelectionChanging += OnStepChanging;
        tabView.SelectionChanged += OnStepChanged;
    }

    private void OnStepChanging(object? sender, SelectionChangingEventArgs e)
    {
        // Validate current step before allowing progression
        if (!ValidateCurrentStep())
        {
            e.Cancel = true;
            DisplayAlert("Validation Error", "Please complete the current step", "OK");
        }
    }

    private void OnStepChanged(object? sender, TabSelectionChangedEventArgs e)
    {
        currentStep = e.NewIndex;
        UpdateProgressIndicator(currentStep);
    }

    private bool ValidateCurrentStep()
    {
        return currentStep switch
        {
            0 => ValidateAccountInfo(),
            1 => ValidateAddressInfo(),
            2 => ValidatePaymentInfo(),
            _ => true
        };
    }

    private bool ValidateAccountInfo() 
    { 
        // Validation logic
        return !string.IsNullOrEmpty(viewModel.Email);
    }

    private bool ValidateAddressInfo() 
    { 
        // Validation logic
        return !string.IsNullOrEmpty(viewModel.Address);
    }

    private bool ValidatePaymentInfo() 
    { 
        // Validation logic
        return !string.IsNullOrEmpty(viewModel.CardNumber);
    }

    private void UpdateProgressIndicator(int step)
    {
        progressLabel.Text = $"Step {step + 1} of 3";
    }
}
```

### XAML with Steps

```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage 
    xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
    xmlns:tabView="clr-namespace:Syncfusion.Maui.Toolkit.TabView;assembly=Syncfusion.Maui.Toolkit"
    Title="Registration Wizard">

    <VerticalStackLayout Spacing="10" Padding="20">
        <!-- Progress Indicator -->
        <Label x:Name="progressLabel" FontSize="14" FontAttributes="Bold" Text="Step 1 of 3"/>
        <ProgressBar Progress="0.33" Margin="0,5"/>

        <!-- Wizard Steps as Tabs -->
        <tabView:SfTabView x:Name="tabView" TabBarPlacement="Top">
            <tabView:SfTabView.Items>
                <!-- Step 1: Account Info -->
                <tabView:SfTabItem Header="Account">
                    <tabView:SfTabItem.Content>
                        <ScrollView>
                            <StackLayout Padding="15" Spacing="10">
                                <Entry Placeholder="Email" Keyboard="Email"/>
                                <Entry Placeholder="Password" IsPassword="True"/>
                                <Entry Placeholder="Confirm Password" IsPassword="True"/>
                            </StackLayout>
                        </ScrollView>
                    </tabView:SfTabItem.Content>
                </tabView:SfTabItem>

                <!-- Step 2: Address Info -->
                <tabView:SfTabItem Header="Address">
                    <tabView:SfTabItem.Content>
                        <ScrollView>
                            <StackLayout Padding="15" Spacing="10">
                                <Entry Placeholder="Street Address"/>
                                <Entry Placeholder="City"/>
                                <Entry Placeholder="Postal Code"/>
                                <Entry Placeholder="Country"/>
                            </StackLayout>
                        </ScrollView>
                    </tabView:SfTabItem.Content>
                </tabView:SfTabItem>

                <!-- Step 3: Payment Info -->
                <tabView:SfTabItem Header="Payment">
                    <tabView:SfTabItem.Content>
                        <ScrollView>
                            <StackLayout Padding="15" Spacing="10">
                                <Entry Placeholder="Card Number" Keyboard="Numeric"/>
                                <Entry Placeholder="Expiry Date" />
                                <Entry Placeholder="CVV" Keyboard="Numeric" IsPassword="True"/>
                                <Button Text="Complete Registration" BackgroundColor="#6200EE" TextColor="White"/>
                            </StackLayout>
                        </ScrollView>
                    </tabView:SfTabItem.Content>
                </tabView:SfTabItem>
            </tabView:SfTabView.Items>
        </tabView:SfTabView>
    </VerticalStackLayout>
</ContentPage>
```

---

## Data Dashboard Layout

### Use Case
Display multiple data visualizations in separate tabs (Sales, Analytics, Reports).

### Implementation

```xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage 
    xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
    xmlns:tabView="clr-namespace:Syncfusion.Maui.Toolkit.TabView;assembly=Syncfusion.Maui.Toolkit"
    Title="Dashboard">

    <ContentPage.BindingContext>
        <local:DashboardViewModel />
    </ContentPage.BindingContext>

    <ContentPage.Content>
        <tabView:SfTabView TabBarPlacement="Top" EnableSwiping="True">
            <tabView:SfTabView.Items>
                <!-- Sales Tab -->
                <tabView:SfTabItem Header="Sales" ImageSource="sales.png">
                    <tabView:SfTabItem.Content>
                        <StackLayout Padding="15" Spacing="10">
                            <Frame BorderColor="LightGray" CornerRadius="10" Padding="15">
                                <StackLayout Spacing="5">
                                    <Label Text="Total Revenue" FontSize="14" TextColor="Gray"/>
                                    <Label Text="$125,430" FontSize="28" FontAttributes="Bold" TextColor="Green"/>
                                    <Label Text="+12.5% from last month" FontSize="12" TextColor="Green"/>
                                </StackLayout>
                            </Frame>
                            <Frame BorderColor="LightGray" CornerRadius="10" Padding="15">
                                <StackLayout Spacing="5">
                                    <Label Text="Total Orders" FontSize="14" TextColor="Gray"/>
                                    <Label Text="1,234" FontSize="28" FontAttributes="Bold" TextColor="Blue"/>
                                    <Label Text="+8.2% from last month" FontSize="12" TextColor="Blue"/>
                                </StackLayout>
                            </Frame>
                        </StackLayout>
                    </tabView:SfTabItem.Content>
                </tabView:SfTabItem>

                <!-- Analytics Tab -->
                <tabView:SfTabItem Header="Analytics" ImageSource="analytics.png">
                    <tabView:SfTabItem.Content>
                        <ScrollView>
                            <StackLayout Padding="15" Spacing="10">
                                <!-- Add chart controls here -->
                                <Label Text="User Engagement Analytics" FontSize="16" FontAttributes="Bold"/>
                                <Frame BorderColor="LightGray" Padding="15">
                                    <StackLayout Spacing="10">
                                        <Label Text="Page Views" FontSize="12"/>
                                        <ProgressBar Progress="0.75"/>
                                        <Label Text="15,234" FontSize="14" FontAttributes="Bold"/>
                                    </StackLayout>
                                </Frame>
                            </StackLayout>
                        </ScrollView>
                    </tabView:SfTabItem.Content>
                </tabView:SfTabItem>

                <!-- Reports Tab -->
                <tabView:SfTabItem Header="Reports" ImageSource="reports.png">
                    <tabView:SfTabItem.Content>
                        <StackLayout Padding="15" Spacing="10">
                            <Label Text="Recent Reports" FontSize="16" FontAttributes="Bold"/>
                            <CollectionView ItemsSource="{Binding Reports}">
                                <CollectionView.ItemTemplate>
                                    <DataTemplate>
                                        <StackLayout Padding="10" Spacing="5">
                                            <Label Text="{Binding Name}" FontAttributes="Bold"/>
                                            <Label Text="{Binding Date}" FontSize="12" TextColor="Gray"/>
                                        </StackLayout>
                                    </DataTemplate>
                                </CollectionView.ItemTemplate>
                            </CollectionView>
                        </StackLayout>
                    </tabView:SfTabItem.Content>
                </tabView:SfTabItem>
            </tabView:SfTabView.Items>
        </tabView:SfTabView>
    </ContentPage.Content>
</ContentPage>
```

---

## Document Viewer

### Use Case
Browse document pages or sections (Table of Contents, Chapters, Index).

```xaml
<tabView:SfTabView SelectedIndex="1">
    <tabView:SfTabView.Items>
        <tabView:SfTabItem Header="Contents">
            <tabView:SfTabItem.Content>
                <StackLayout Padding="15" Spacing="10">
                    <Label Text="Table of Contents" FontSize="16" FontAttributes="Bold"/>
                    <CollectionView ItemsSource="{Binding Contents}">
                        <CollectionView.ItemTemplate>
                            <DataTemplate>
                                <Button Text="{Binding Title}" 
                                        Command="{Binding GotoPageCommand}"
                                        CommandParameter="{Binding PageNumber}"
                                        BackgroundColor="Transparent"
                                        TextColor="Blue"/>
                            </DataTemplate>
                        </CollectionView.ItemTemplate>
                    </CollectionView>
                </StackLayout>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>

        <tabView:SfTabItem Header="Document">
            <tabView:SfTabItem.Content>
                <ScrollView>
                    <StackLayout Padding="15" Spacing="10">
                        <WebView Source="{Binding CurrentDocument}"/>
                    </StackLayout>
                </ScrollView>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>

        <tabView:SfTabItem Header="Index">
            <tabView:SfTabItem.Content>
                <StackLayout Padding="15" Spacing="10">
                    <SearchBar Placeholder="Search index..." SearchCommand="{Binding SearchCommand}"/>
                    <CollectionView ItemsSource="{Binding IndexItems}">
                        <CollectionView.ItemTemplate>
                            <DataTemplate>
                                <Label Text="{Binding Term}" FontSize="14"/>
                            </DataTemplate>
                        </CollectionView.ItemTemplate>
                    </CollectionView>
                </StackLayout>
            </tabView:SfTabItem.Content>
        </tabView:SfTabItem>
    </tabView:SfTabView.Items>
</tabView:SfTabView>
```

---

## Best Practices

### ✅ Do's

**1. Keep Tab Count Reasonable**
- Limit to 3-5 tabs for mobile, 5-7 for desktop
- Use scroll buttons or nested tabs for more content

**2. Clear Tab Naming**
```xaml
<!-- Good: Descriptive, concise -->
<tabView:SfTabItem Header="Account Settings" />

<!-- Poor: Ambiguous -->
<tabView:SfTabItem Header="Options" />
```

**3. Consistent Content Structure**
```xaml
<!-- All tabs use similar layouts for predictability -->
<tabView:SfTabItem Header="Tab 1">
    <tabView:SfTabItem.Content>
        <Frame BorderColor="LightGray" Padding="15">
            <StackLayout Spacing="10">
                <!-- Consistent structure -->
            </StackLayout>
        </Frame>
    </tabView:SfTabItem.Content>
</tabView:SfTabItem>
```

**4. Visual Hierarchy with Icons**
```xaml
<tabView:SfTabItem Header="Messages" ImageSource="messages.png" ImagePosition="Left" />
```

**5. Preserve Tab State**
```csharp
private int lastSelectedTabIndex = 0;

private void OnSelectionChanged(object? sender, TabSelectionChangedEventArgs e)
{
    lastSelectedTabIndex = e.NewIndex;
    // Save state to preferences
}
```

---

## Anti-Patterns

### ❌ Don'ts

**1. Excessive Nesting (Avoid)**
```csharp
// BAD: Deep nesting (3+ levels) confuses navigation
TabView → NestedTabView → SecondNestedTabView
```

**2. Heavy Content Loading**
```csharp
// BAD: Load all content at startup
foreach (var item in largeDataSet)
{
    var tab = new SfTabItem { Content = ExpensiveLayout() };
}

// GOOD: Lazy load on selection
```

**3. Identical Tab Appearance**
```xaml
<!-- BAD: No visual distinction between active/inactive -->
<tabView:SfTabView EnableRippleAnimation="False">
```

**4. Non-Obvious Tab Order**
```xaml
<!-- BAD: Logical flow is unclear -->
<tabView:SfTabItem Header="Help" />
<tabView:SfTabItem Header="Settings" />
<tabView:SfTabItem Header="Account" />

<!-- GOOD: Logical flow -->
<tabView:SfTabItem Header="Account" />
<tabView:SfTabItem Header="Settings" />
<tabView:SfTabItem Header="Help" />
```

---

## Accessibility Guidelines

### WCAG 2.1 Compliance

**1. Color Contrast**
```xaml
<!-- Ensure 4.5:1 minimum contrast ratio -->
<tabView:SfTabItem TextColor="#333333" />  <!-- Dark text on light background -->
```

**2. Keyboard Navigation**
- Tab headers should be keyboard accessible
- Ensure focus indicators are visible

**3. Screen Reader Support**
```csharp
// Provide meaningful header text
var tab = new SfTabItem { Header = "User Account Settings" };  // Good
// Not: new SfTabItem { Header = "Tab 1" }  // Bad
```

**4. Sufficient Font Size**
```xaml
<tabView:SfTabItem FontSize="14" />  <!-- Minimum 14pt for readability -->
```

---

## Troubleshooting Common Issues

### Issue 1: Tabs Not Responding to Taps

**Problem:** Tab selection events don't fire
**Solution:**
```csharp
// Ensure events are properly subscribed
tabView.SelectionChanged += OnSelectionChanged;

// Check that SelectedIndex is valid
if (tabView.SelectedIndex >= 0 && tabView.SelectedIndex < tabView.Items.Count)
{
    // Valid
}
```

### Issue 2: Content Jumps or Flickers

**Problem:** Switching tabs causes visual jumping
**Solution:**
```xaml
<!-- Ensure consistent sizing -->
<tabView:SfTabView IsContentTransitionEnabled="True" ContentTransitionDuration="300">
```

### Issue 3: Memory Issues with Many Tabs

**Problem:** App crashes with hundreds of tabs
**Solution:**
```csharp
// Implement virtual scrolling / pagination
private const int MaxVisibleTabs = 50;

private void AddTabsInBatches(List<TabModel> allTabs)
{
    for (int i = 0; i < Math.Min(MaxVisibleTabs, allTabs.Count); i++)
    {
        tabView.Items.Add(CreateTab(allTabs[i]));
    }
}
```

### Issue 4: Swiping Conflicts

**Problem:** Tab swiping interferes with content scrolling
**Solution:**
```xaml
<!-- Disable swiping when child has horizontal scroll -->
<tabView:SfTabView EnableSwiping="False">
    <tabView:SfTabItem Header="Scrollable">
        <tabView:SfTabItem.Content>
            <ScrollView Orientation="Horizontal">
                <!-- Horizontal scrollable content -->
            </ScrollView>
        </tabView:SfTabItem.Content>
    </tabView:SfTabItem>
</tabView:SfTabView>
```

---
