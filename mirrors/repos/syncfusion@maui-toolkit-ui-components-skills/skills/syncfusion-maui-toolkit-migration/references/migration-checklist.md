# Migration Checklist: Step-by-Step Process

## Table of Contents

- [Pre-Migration Steps](#pre-migration-steps)
- [Step-by-Step Migration Process](#step-by-step-migration-process)
- [Post-Migration Validation](#post-migration-validation)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Performance Validation](#performance-validation)
- [Migration Completion Checklist](#migration-completion-checklist)

## Pre-Migration Steps

### Step 0A: Backup Your Project

Before making any changes, create a backup of your project:

**Option 1: Git Backup**
```powershell
git add .
git commit -m "Pre-migration backup: Syncfusion® MAUI to Toolkit"
git branch backup/pre-migration-2026
```

**Option 2: File Backup**
```powershell
Copy-Item -Path "C:\path\to\project" -Destination "C:\path\to\project.backup" -Recurse
```

**Why:** If migration encounters issues, you can quickly revert to working state.

### Step 0B: Document Current Usage

Create a list of all Syncfusion® components used in your project. This helps with verification later.

**Find All Components:**
```powershell
# Search for Syncfusion® component usage
Get-ChildItem -Recurse -Filter "*.xaml" | Select-String "xmlns:.*Syncfusion" | Select-Object Filename, Line
```

**Record Usage:**
- [ ] List all Syncfusion® XAML namespace prefixes used
- [ ] Note which components used in code-behind
- [ ] Document any custom component derivations
- [ ] Record any event handlers or bindings

### Step 0C: Verify Project State

**Before migration, verify:**
- [ ] Project builds successfully without errors
- [ ] All tests pass (if applicable)
- [ ] Application runs correctly
- [ ] All Syncfusion® components function as expected
- [ ] No outstanding code review comments

## Step-by-Step Migration Process

### Step 1: Update NuGet Packages

**1.1 Remove Old Packages**

Edit your `.csproj` file and remove all individual Syncfusion® package references:

**Find and Remove:**
```xml
<PackageReference Include="Syncfusion.Maui.Buttons" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Calendar" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Cards" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Carousel" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Charts" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Core" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Expander" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Inputs" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.NavigationDrawer" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Picker" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.Popup" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.PullToRefresh" Version="23.1.x" />
<PackageReference Include="Syncfusion.Maui.TabView" Version="23.1.x" />
<!-- Remove all other individual Syncfusion packages -->
```

**1.2 Add New Package**

Add the single toolkit package:

```xml
<ItemGroup>
    <PackageReference Include="Syncfusion.Maui.Toolkit" Version="*" />
</ItemGroup>
```

**1.3 Restore Packages**

```powershell
dotnet restore
```

**Verification:**
- [ ] `.csproj` contains only `Syncfusion.Maui.Toolkit` reference
- [ ] No old individual package references remain
- [ ] `dotnet restore` completes without errors
- [ ] `packages.lock.json` shows only toolkit package (if using lock file)

### Step 2: Update MauiProgram.cs

**2.1 Update Using Statement**

Open `MauiProgram.cs`:

**Find:**
```csharp
using Syncfusion.Maui.Core.Hosting;
```

**Replace With:**
```csharp
using Syncfusion.Maui.Toolkit.Hosting;
```

**2.2 Update Configuration Method**

**Find:**
```csharp
.ConfigureSyncfusionCore()
```

**Replace With:**
```csharp
.ConfigureSyncfusionToolkit()
```

**Complete Example After:**
```csharp
using Syncfusion.Maui.Toolkit.Hosting;

namespace MyApp;

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
            })
            .ConfigureSyncfusionToolkit();

        return builder.Build();
    }
}
```

**Verification:**
- [ ] Using statement updated to `Syncfusion.Maui.Toolkit.Hosting`
- [ ] Method call is `.ConfigureSyncfusionToolkit()`
- [ ] Method called after `.UseMauiApp<App>()`
- [ ] File has no syntax errors

### Step 3: Update XAML Files

**3.1 Find All XAML Files**

```powershell
Get-ChildItem -Recurse -Filter "*.xaml"
```

**3.2 Update Each XAML File**

For each `.xaml` file, update namespace declarations.

**Example - Before:**
```xaml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons"
             xmlns:calendar="clr-namespace:Syncfusion.Maui.Calendar;assembly=Syncfusion.Maui.Calendar">
```

**Example - After:**
```xaml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit"
             xmlns:calendar="clr-namespace:Syncfusion.Maui.Toolkit.Calendar;assembly=Syncfusion.Maui.Toolkit">
```

**Use Find & Replace (Case-Sensitive):**

| Find | Replace |
|------|---------|
| `clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons` | `clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit` |
| `clr-namespace:Syncfusion.Maui.Calendar;assembly=Syncfusion.Maui.Calendar` | `clr-namespace:Syncfusion.Maui.Toolkit.Calendar;assembly=Syncfusion.Maui.Toolkit` |
| `clr-namespace:Syncfusion.Maui.Cards;assembly=Syncfusion.Maui.Cards` | `clr-namespace:Syncfusion.Maui.Toolkit.Cards;assembly=Syncfusion.Maui.Toolkit` |
| `clr-namespace:Syncfusion.Maui.Carousel;assembly=Syncfusion.Maui.Carousel` | `clr-namespace:Syncfusion.Maui.Toolkit.Carousel;assembly=Syncfusion.Maui.Toolkit` |
| `clr-namespace:Syncfusion.Maui.Charts;assembly=Syncfusion.Maui.Charts` | `clr-namespace:Syncfusion.Maui.Toolkit.Charts;assembly=Syncfusion.Maui.Toolkit` |
| `clr-namespace:Syncfusion.Maui.ProgressBar;assembly=Syncfusion.Maui.ProgressBar` | `clr-namespace:Syncfusion.Maui.Toolkit.ProgressBar;assembly=Syncfusion.Maui.Toolkit` |
| (See references/namespace-updates.md for complete table) | |

**Verification:**
- [ ] All `.xaml` files updated
- [ ] No old namespace references remain
- [ ] XAML designer shows components (or close/reopen to refresh)

### Step 4: Update C# Code-Behind Files

**4.1 Find All Code-Behind Files**

```powershell
Get-ChildItem -Recurse -Filter "*.xaml.cs"
Get-ChildItem -Recurse -Filter "*.cs" | Where-Object { $_ -match "ViewModel|Model|Service" }
```

**4.2 Update Using Statements**

For each file using Syncfusion components, update the using statements:

**Example - Before:**
```csharp
using Syncfusion.Maui.Buttons;
using Syncfusion.Maui.Calendar;
using Syncfusion.Maui.Inputs;
```

**Example - After:**
```csharp
using Syncfusion.Maui.Toolkit.Buttons;
using Syncfusion.Maui.Toolkit.Calendar;
using Syncfusion.Maui.Toolkit.NumericEntry;
```

**Use Find & Replace:**

| Find | Replace |
|------|---------|
| `using Syncfusion.Maui.Buttons;` | `using Syncfusion.Maui.Toolkit.Buttons;` |
| `using Syncfusion.Maui.Calendar;` | `using Syncfusion.Maui.Toolkit.Calendar;` |
| `using Syncfusion.Maui.Cards;` | `using Syncfusion.Maui.Toolkit.Cards;` |
| `using Syncfusion.Maui.Carousel;` | `using Syncfusion.Maui.Toolkit.Carousel;` |
| `using Syncfusion.Maui.Charts;` | `using Syncfusion.Maui.Toolkit.Charts;` |
| `using Syncfusion.Maui.Core.Hosting;` | `using Syncfusion.Maui.Toolkit.Hosting;` |
| (See references/namespace-updates.md for complete table) | |

**Verification:**
- [ ] All `.cs` files updated
- [ ] No old `Syncfusion.Maui.*` using statements remain (except toolkit)
- [ ] No intellisense red squiggles on component usage

### Step 5: Build and Verify

**5.1 Clean Solution**

```powershell
dotnet clean
```

**5.2 Rebuild Solution**

```powershell
dotnet build
```

**Expected Results:**
- ✅ Build completes successfully
- ✅ No errors or warnings related to namespaces
- ✅ All projects compile

**If Errors Occur:**
- Check error messages for missing namespaces
- Verify all files updated (Steps 2-4)
- Look for any remaining old namespace references
- See [Common Issues and Solutions](#common-issues-and-solutions)

**Verification:**
- [ ] Solution builds without errors
- [ ] No build warnings about Syncfusion® namespaces
- [ ] IntelliSense works correctly

## Post-Migration Validation

### Validation 1: Run Application

**1.1 Launch Application**

```powershell
dotnet run
```

Or press F5 in Visual Studio.

**1.2 Verify Functionality**

- [ ] Application launches without errors
- [ ] All UI pages display correctly
- [ ] Syncfusion® components render properly
- [ ] Navigation works
- [ ] Data bindings work

### Validation 2: Test All Components

For each Syncfusion® component used, verify:

- [ ] Component displays correctly
- [ ] Component is interactive (clicks, selections, etc.)
- [ ] Events fire properly
- [ ] Data binding works
- [ ] Styling displays correctly

### Validation 3: Test User Workflows

- [ ] Primary user workflows complete successfully
- [ ] Forms submit correctly
- [ ] Data loads and displays
- [ ] Searches/filters work
- [ ] Downloads/exports work (if applicable)

### Validation 4: Platform Testing

Test on all target platforms:

**Windows:**
- [ ] Application runs on Windows
- [ ] Components display correctly
- [ ] No platform-specific errors

**Android (if targeting):**
- [ ] Application runs on Android device/emulator
- [ ] Components display correctly
- [ ] Touch interactions work

**iOS (if targeting):**
- [ ] Application runs on iOS device/simulator
- [ ] Components display correctly
- [ ] Touch interactions work

### Validation 5: Error Scenarios

- [ ] No exceptions thrown during normal use
- [ ] Error messages display correctly
- [ ] Graceful handling of network errors (if applicable)
- [ ] No memory leaks or performance degradation

## Common Issues and Solutions

### Issue 1: Build Error - "Type does not exist"

**Error Message:**
```
Error CS0246: The type or namespace name 'SfButton' could not be found
```

**Solution:**
1. Verify `.csproj` has `Syncfusion.Maui.Toolkit` package
2. Check C# file has `using Syncfusion.Maui.Toolkit.Buttons;`
3. Rebuild solution: `dotnet clean && dotnet build`

### Issue 2: XAML Error - "Namespace not found"

**XAML Error:**
```
'clr-namespace:Syncfusion.Maui.Buttons' is not a valid namespace
```

**Solution:**
1. Verify XAML namespace: `clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit`
2. Check assembly name is `Syncfusion.Maui.Toolkit`
3. Close and reopen XAML file to refresh designer

### Issue 3: Runtime Error - "Could not load assembly"

**Runtime Error:**
```
FileNotFoundException: Could not load file or assembly 'Syncfusion.Maui.Buttons'
```

**Solution:**
1. Check `.csproj` for old package references
2. Remove all individual Syncfusion® packages
3. Keep only `Syncfusion.Maui.Toolkit`
4. Clean NuGet cache: `nuget locals all -clear`
5. Restore packages: `dotnet restore`

### Issue 4: Component Not Displaying

**Symptom:** Components are invisible or blank at runtime

**Solution:**
1. Verify `.ConfigureSyncfusionToolkit()` is called in `MauiProgram.cs`
2. Confirm it's called **after** `.UseMauiApp<App>()`
3. Check application builds and runs without errors
4. Verify XAML markup uses correct component names
5. Check namespace declarations are correct

### Issue 5: Event Handlers Not Firing

**Symptom:** Button clicks or other events don't trigger

**Solution:**
1. Verify event handler method exists in code-behind
2. Check method signature matches event type
3. Confirm component event attribute is spelled correctly
4. Verify component is properly initialized
5. Check for exception handling that might silently catch errors

### Issue 6: Data Binding Not Working

**Symptom:** Bound data doesn't appear or update

**Solution:**
1. Verify BindingContext is set correctly
2. Check property names match exactly (case-sensitive)
3. Verify INotifyPropertyChanged is implemented
4. Confirm component property names are correct in new namespace
5. Check for binding errors in VS Output window

### Issue 7: Styling Not Applied

**Symptom:** Component colors, fonts, or sizes don't apply

**Solution:**
1. Verify styles target the correct component type
2. Check toolkit version supports the styling properties
3. Confirm namespace references in styles are updated
4. Clear application cache and rebuild
5. Check for conflicting styles

## Performance Validation

### Test Application Performance

**Load Time:**
- [ ] Application launches in acceptable time (<5 seconds)
- [ ] Pages load smoothly (no visible lag)

**Memory Usage:**
- [ ] Memory usage is reasonable
- [ ] No memory leaks during normal use
- [ ] Memory released when pages close

**Responsiveness:**
- [ ] UI remains responsive during operations
- [ ] Long operations show progress indicators
- [ ] Scrolling is smooth (especially in lists)

**Component Performance:**
- [ ] Charts render in reasonable time
- [ ] Grids scroll smoothly with large datasets
- [ ] Popups open/close quickly
- [ ] Navigation is instantaneous

## Breaking Changes Documentation

Document any breaking changes encountered:

**Template for Each Issue:**
```
Component: [Name]
Issue: [Description]
Old Code: [Code snippet]
New Code: [Code snippet]
Workaround: [If applicable]
```

## Migration Completion Checklist

**Final verification before considering migration complete:**

### Code Completion
- [ ] All XAML files updated
- [ ] All C# files updated
- [ ] MauiProgram.cs updated
- [ ] `.csproj` updated with correct packages
- [ ] No compilation errors
- [ ] No compilation warnings

### Functionality Testing
- [ ] Application runs on all target platforms
- [ ] All Syncfusion® components display and work
- [ ] All event handlers fire correctly
- [ ] All data bindings work
- [ ] All user workflows complete successfully

### Performance Validation
- [ ] Application launch time acceptable
- [ ] Memory usage reasonable
- [ ] UI remains responsive
- [ ] No performance regressions

### Documentation
- [ ] Migration completed in team
- [ ] Any workarounds documented
- [ ] Team members understand new toolkit
- [ ] No outstanding questions

### Version Control
- [ ] Changes committed to git
- [ ] Commit message describes migration
- [ ] Branch merged to main/master
- [ ] Backup branch maintained

### Final Sign-Off
- [ ] Developer: _______________________ Date: _______
- [ ] QA Tester: _______________________ Date: _______
- [ ] Project Lead: _______________________ Date: _______

---

**Congratulations!** Your application has been successfully migrated from Syncfusion® .NET MAUI to Syncfusion® Toolkit for .NET MAUI. The migration is complete and your application is ready for production deployment.

For ongoing support, refer to the other reference files in this skill for troubleshooting and best practices.