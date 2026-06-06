# Configuration Method Migration

## Table of Contents

- [ConfigureSyncfusionCore() → ConfigureSyncfusionToolkit()](#configuresyncfusioncore--configuresyncfusiontoolkit)
- [Hosting Namespace Changes](#hosting-namespace-changes)
- [MauiProgram.cs Complete Example](#mauiprogramcs-complete-example)
- [AppHostBuilder Configuration](#apphostbuilder-configuration)
- [Troubleshooting Initialization Issues](#troubleshooting-initialization-issues)

## ConfigureSyncfusionCore() → ConfigureSyncfusionToolkit()

The primary configuration method change occurs in your `MauiProgram.cs` file during application startup. This single change enables all toolkit components to work properly.

### What Changed

| Aspect | Before | After |
|--------|--------|-------|
| **Method Name** | `ConfigureSyncfusionCore()` | `ConfigureSyncfusionToolkit()` |
| **Using Statement** | `Syncfusion.Maui.Core.Hosting` | `Syncfusion.Maui.Toolkit.Hosting` |
| **File Location** | `MauiProgram.cs` | `MauiProgram.cs` |
| **Installation Point** | After `.UseMauiApp<App>()` | After `.UseMauiApp<App>()` |

### Why This Change

- **Namespace Consolidation**: All toolkit services now use the unified `Syncfusion.Maui.Toolkit.Hosting` namespace
- **Service Registration**: The new method registers all toolkit component handlers correctly
- **API Clarity**: Method name accurately reflects the toolkit platform
- **Future Updates**: Simpler to add new toolkit features without namespace confusion

## Hosting Namespace Changes

Update the using statement at the top of your `MauiProgram.cs` file.

### Before
```csharp
using Syncfusion.Maui.Core.Hosting;
```

### After
```csharp
using Syncfusion.Maui.Toolkit.Hosting;
```

## MauiProgram.cs Complete Example

### Before Migration

```csharp
using Syncfusion.Maui.Core.Hosting;

namespace MigrationApp;

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
            .ConfigureSyncfusionCore();

        return builder.Build();
    }
}
```

### After Migration

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

namespace MigrationApp;

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
            .ConfigureSyncfusionToolkit();

        return builder.Build();
    }
}
```

### Key Changes
1. ✅ Line 1: `using Syncfusion.Maui.Core.Hosting;` → `using Syncfusion.Maui.Toolkit.Hosting;`
2. ✅ Line 20: `.ConfigureSyncfusionCore()` → `.ConfigureSyncfusionToolkit()`

## AppHostBuilder Configuration

The `MauiAppBuilder` extension method handles registering all Syncfusion® toolkit component handlers and services needed for your application.

### What Gets Configured

When you call `.ConfigureSyncfusionToolkit()`, the following are automatically registered:

- All component handlers (Button, Calendar, Charts, Popup, etc.)
- Event handling infrastructure
- Resource management
- Theme and styling support
- Data binding support
- Platform-specific optimizations

### Extension Method Signature

```csharp
public static class AppHostBuilderExtensions
{
    public static MauiAppBuilder ConfigureSyncfusionToolkit(
        this MauiAppBuilder builder)
    {
        // Registers all toolkit component handlers and services
        return builder;
    }
}
```

### Why Call It Once

- **Application Scope**: Configuration happens at app startup in `MauiProgram.cs`
- **Global Registration**: All handlers are registered for entire application lifecycle
- **Single Point**: No need to configure components individually
- **Automatic Discovery**: All toolkit components automatically work after this call

## Configuration in Complex Applications

### Multi-Project Solutions

If your application spans multiple projects (e.g., separate UI and business logic projects), ensure `MauiProgram.cs` is only in your main MAUI app project:

```csharp
// Main MAUI App Project only
using Syncfusion.Maui.Toolkit.Hosting;

namespace MyApp.Maui;

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
            .ConfigureSyncfusionToolkit();  // Call once here

        return builder.Build();
    }
}
```

### Dependency Injection Setup

If you're using dependency injection, the toolkit configuration integrates seamlessly:

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

namespace MyApp.Maui;

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
            .ConfigureSyncfusionToolkit()  // Before custom services
            .Services
                .AddSingleton<MainPage>()
                .AddSingleton<MainViewModel>();

        return builder.Build();
    }
}
```

### Environment-Specific Configuration

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

namespace MyApp.Maui;

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

        #if DEBUG
            builder.UseMauiApp<App>()
                .ConfigureDebugging();
        #endif

        return builder.Build();
    }
}
```

## Common Configuration Patterns

### Pattern 1: Basic Setup

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

namespace MyApp;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder()
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

### Pattern 2: With Additional Services

```csharp
using Syncfusion.Maui.Toolkit.Hosting;

namespace MyApp;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder()
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
            })
            .ConfigureSyncfusionToolkit()
            .Services
                .AddHttpClient()
                .AddSingleton<ApiService>();

        return builder.Build();
    }
}
```

### Pattern 3: With Platform-Specific Configuration

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

        #if WINDOWS
            builder.ConfigureLifecycle((context) => context
                .AddWindows(windows => windows
                    .UseWinUI()
                ));
        #endif

        return builder.Build();
    }
}
```

## Troubleshooting Initialization Issues

### Issue 1: Method Not Found

**Problem:**
```
Error CS1061: 'MauiAppBuilder' does not contain a definition for 'ConfigureSyncfusionToolkit'
```

**Solution:**
1. Verify NuGet package `Syncfusion.Maui.Toolkit` is installed
2. Check using statement: `using Syncfusion.Maui.Toolkit.Hosting;`
3. Rebuild solution to refresh IntelliSense
4. Check package version is 1.0.8 or later

### Issue 2: Old Method Still Exists

**Problem:**
```
Error CS0117: 'MauiAppBuilder' does not contain a definition for 'ConfigureSyncfusionCore'
```

**Solution:**
- This error means you still have the old using statement
- Replace `using Syncfusion.Maui.Core.Hosting;` with `using Syncfusion.Maui.Toolkit.Hosting;`
- Remove any old package references to `Syncfusion.Maui.Core`

### Issue 3: Components Don't Display at Runtime

**Problem:**
- Application runs but Syncfusion® components show blank or errors
- Event handlers don't trigger

**Solution:**
1. Verify `.ConfigureSyncfusionToolkit()` is called in `MauiProgram.cs`
2. Confirm it's called **after** `.UseMauiApp<App>()`
3. Check application builds without errors
4. Verify all namespace references are updated
5. Clear application cache and rebuild

### Issue 4: IntelliSense Not Showing

**Problem:**
- IDE doesn't show `.ConfigureSyncfusionToolkit()` in IntelliSense dropdown

**Solution:**
1. Close and reopen Visual Studio
2. Clean NuGet cache: `nuget locals all -clear`
3. Restore packages: `dotnet restore`
4. Rebuild solution: `dotnet build`
5. Close and reopen `MauiProgram.cs` file

### Issue 5: Multiple Versions Installed

**Problem:**
```
Error: Multiple versions of Syncfusion® packages detected
```

**Solution:**
1. Remove all old individual Syncfusion packages from `.csproj`
2. Keep only `<PackageReference Include="Syncfusion.Maui.Toolkit" />`
3. Clean NuGet cache
4. Restore and rebuild

## Verification Checklist

After updating `MauiProgram.cs`, verify:

- ✅ Using statement updated: `using Syncfusion.Maui.Toolkit.Hosting;`
- ✅ Method renamed: `.ConfigureSyncfusionToolkit()` (not `ConfigureSyncfusionCore`)
- ✅ Called after `.UseMauiApp<App>()`
- ✅ Project builds without errors
- ✅ NuGet package `Syncfusion.Maui.Toolkit` is installed
- ✅ Old package references removed from `.csproj`
- ✅ Application runs and components display
- ✅ Event handlers fire correctly