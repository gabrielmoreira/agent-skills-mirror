---
name: syncfusion-maui-toolkit-migration
description: Migrate from Syncfusion® .NET MAUI to Syncfusion® Toolkit for .NET MAUI. Covers namespace updates, API changes, configuration methods, and step-by-step migration patterns with minimal code modifications for 20+ components.
compatibility: .NET MAUI 8.0+, Visual Studio 2022+
metadata:
  author: "Syncfusion Inc"
  version: "1.0.0"
---

# Migration Guide: Syncfusion® .NET MAUI to Syncfusion® Toolkit for .NET MAUI

The Syncfusion® Toolkit for .NET MAUI represents the next generation of Syncfusion® components for MAUI applications. While most APIs and functionality remain the same, components have been consolidated into a single toolkit with updated namespaces. This guide helps you migrate existing Syncfusion® .NET MAUI projects to the new toolkit with minimal code modifications.

## Table of Contents

- [Overview](#overview)
- [Documentation and Navigation Guide](#documentation-and-navigation-guide)
- [Quick Start Example](#quick-start-example)
- [Common Migration Patterns](#common-migration-patterns)
- [Key Migration Principles](#key-migration-principles)

## Overview

The migration from **Syncfusion® .NET MAUI** to **Syncfusion® Toolkit for .NET MAUI** involves three primary changes:

1. **Namespace Updates** - Component namespaces are reorganized under `Syncfusion.Maui.Toolkit.*`
2. **Assembly Consolidation** - Individual component assemblies consolidated into `Syncfusion.Maui.Toolkit`
3. **Configuration Method** - `ConfigureSyncfusionCore()` renamed to `ConfigureSyncfusionToolkit()`

**Good news:** Your existing component implementations work nearly identically. The primary effort is updating namespaces and the initialization method.

## Documentation and Navigation Guide

Choose your migration path based on where you are in the process:

### Getting Started
📄 **Read:** [references/getting-started.md](references/getting-started.md)

Start here if you:
- Are new to the migration process
- Need to understand migration scope and benefits
- Want prerequisites and an overview of what changes
- Are planning your migration timeline

**Covers:**
- Why migrate to the toolkit
- Prerequisites and requirements
- What components are affected
- High-level change summary

### Namespace Updates
📄 **Read:** [references/namespace-updates.md](references/namespace-updates.md)

Read this when you need to:
- Update XAML namespace declarations
- Modify C# using statements
- Find exact namespace mappings for specific components
- Understand assembly changes from NuGet packages
- Get search & replace patterns for your IDE

**Covers:**
- Complete XAML namespace reference (20+ controls)
- Complete C# namespace reference (20+ controls)
- Assembly changes and package structure
- Real-world migration examples with before/after code
- Troubleshooting namespace-related build errors

### Configuration Method Migration
📄 **Read:** [references/method-migration.md](references/method-migration.md)

Use this when you need to:
- Update your MauiProgram.cs initialization
- Change `ConfigureSyncfusionCore()` to `ConfigureSyncfusionToolkit()`
- Understand AppHostBuilder configuration
- See code-behind changes
- Review method signature changes

**Covers:**
- Step-by-step initialization update
- Old vs. new configuration code
- Complete MauiProgram.cs example
- Advanced configuration options
- Troubleshooting initialization issues

### Migration Checklist
📄 **Read:** [references/migration-checklist.md](references/migration-checklist.md)

Use this as your:
- Pre-migration verification checklist
- Step-by-step migration process guide
- Post-migration validation checklist
- Troubleshooting reference for common issues
- Performance validation guide

**Covers:**
- Pre-migration steps and backup procedures
- Component inventory preparation
- Step-by-step numbered migration process
- Build and test verification
- Common issues and solutions with fixes
- Migration completion checklist

## Quick Start Example

Here's how a typical XAML migration looks. The component usage itself doesn't change—only the namespace:

### Before (Syncfusion® .NET MAUI)

**XAML:**
```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons">
    <VerticalStackLayout>
        <button:SfButton Text="Click Me" Clicked="OnButtonClicked" />
    </VerticalStackLayout>
</ContentPage>
```

**C# (MauiProgram.cs):**
```csharp
using Syncfusion.Maui.Core.Hosting;

var builder = MauiApp.CreateBuilder();
builder
    .UseMauiApp<App>()
    .ConfigureFonts(fonts => fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular"))
    .ConfigureSyncfusionCore();

return builder.Build();
```

**C# (Code-Behind):**
```csharp
using Syncfusion.Maui.Buttons;

namespace MigrationApp;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void OnButtonClicked(object sender, EventArgs e)
    {
        DisplayAlert("Success", "Button clicked!", "OK");
    }
}
```

### After (Syncfusion® Toolkit for .NET MAUI)

**XAML:**
```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit">
    <VerticalStackLayout>
        <button:SfButton Text="Click Me" Clicked="OnButtonClicked" />
    </VerticalStackLayout>
</ContentPage>
```

**C# (MauiProgram.cs):**
```csharp
using Syncfusion.Maui.Toolkit.Hosting;

var builder = MauiApp.CreateBuilder();
builder
    .UseMauiApp<App>()
    .ConfigureFonts(fonts => fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular"))
    .ConfigureSyncfusionToolkit();

return builder.Build();
```

**C# (Code-Behind):**
```csharp
using Syncfusion.Maui.Toolkit.Buttons;

namespace MigrationApp;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void OnButtonClicked(object sender, EventArgs e)
    {
        DisplayAlert("Success", "Button clicked!", "OK");
    }
}
```

**Summary of Changes:**
- ✅ XAML namespace: `Syncfusion.Maui.Buttons` → `Syncfusion.Maui.Toolkit.Buttons`
- ✅ XAML assembly: `Syncfusion.Maui.Buttons` → `Syncfusion.Maui.Toolkit`
- ✅ C# using: `Syncfusion.Maui.Buttons` → `Syncfusion.Maui.Toolkit.Buttons`
- ✅ Configuration: `ConfigureSyncfusionCore()` → `ConfigureSyncfusionToolkit()`
- ✅ MauiProgram.cs using: `Syncfusion.Maui.Core.Hosting` → `Syncfusion.Maui.Toolkit.Hosting`
- ✅ Component usage: **No changes** - `SfButton` behavior is identical

## Common Migration Patterns

### Pattern 1: Multiple Components in One Page

When your page uses multiple Syncfusion® components, update all namespace declarations:

**Before:**
```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons"
             xmlns:calendar="clr-namespace:Syncfusion.Maui.Calendar;assembly=Syncfusion.Maui.Calendar"
             xmlns:cards="clr-namespace:Syncfusion.Maui.Cards;assembly=Syncfusion.Maui.Cards">
```

**After:**
```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:button="clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit"
             xmlns:calendar="clr-namespace:Syncfusion.Maui.Toolkit.Calendar;assembly=Syncfusion.Maui.Toolkit"
             xmlns:cards="clr-namespace:Syncfusion.Maui.Toolkit.Cards;assembly=Syncfusion.Maui.Toolkit">
```

### Pattern 2: Code-Behind Multi-Component Usage

When using components in code-behind, update all using statements:

**Before:**
```csharp
using Syncfusion.Maui.Buttons;
using Syncfusion.Maui.Calendar;
using Syncfusion.Maui.Cards;

namespace MyApp;

public partial class ComplexPage : ContentPage
{
    public ComplexPage()
    {
        InitializeComponent();
        var button = new SfButton { Text = "Dynamic" };
        var calendar = new SfCalendar();
    }
}
```

**After:**
```csharp
using Syncfusion.Maui.Toolkit.Buttons;
using Syncfusion.Maui.Toolkit.Calendar;
using Syncfusion.Maui.Toolkit.Cards;

namespace MyApp;

public partial class ComplexPage : ContentPage
{
    public ComplexPage()
    {
        InitializeComponent();
        var button = new SfButton { Text = "Dynamic" };
        var calendar = new SfCalendar();
    }
}
```

### Pattern 3: Conditional Component Usage

When using components conditionally or in view models, ensure all namespace declarations are updated:

**Before:**
```csharp
using Syncfusion.Maui.Buttons;

namespace MyApp.ViewModels;

public class ButtonViewModel
{
    public SfButton CreateButton()
    {
        return new SfButton 
        { 
            Text = "Action",
            BackgroundColor = Colors.Blue
        };
    }
}
```

**After:**
```csharp
using Syncfusion.Maui.Toolkit.Buttons;

namespace MyApp.ViewModels;

public class ButtonViewModel
{
    public SfButton CreateButton()
    {
        return new SfButton 
        { 
            Text = "Action",
            BackgroundColor = Colors.Blue
        };
    }
}
```

## Key Migration Principles

### 1. Namespace-Based Migration
All changes center around namespaces. Component APIs, properties, and event signatures remain virtually identical.

### 2. Single Assembly Consolidation
Instead of installing individual component packages (Syncfusion.Maui.Buttons, Syncfusion.Maui.Calendar, etc.), you install the single **Syncfusion.Maui.Toolkit** NuGet package.

### 3. Minimal Code Changes
Existing code logic and implementation patterns require no changes. Only namespace declarations and assembly references are updated.

### 4. One-Time Initialization Update
Update `MauiProgram.cs` once at application startup. All components then use the new toolkit automatically.

### 5. Complete Backward Compatibility
Component functionality, properties, events, and behaviors are fully preserved. No feature changes required.

## Getting Help & Resources

- **Step-by-Step Guide:** Start with [references/migration-checklist.md](references/migration-checklist.md) for numbered steps
- **Namespace Reference:** Use [references/namespace-updates.md](references/namespace-updates.md) for component lookups
- **Troubleshooting:** Check [references/migration-checklist.md](references/migration-checklist.md#common-issues--solutions) for common problems
- **Configuration Help:** See [references/method-migration.md](references/method-migration.md) for initialization details

**Next Steps:**
1. Read [references/getting-started.md](references/getting-started.md) for prerequisites
2. Use [references/namespace-updates.md](references/namespace-updates.md) to identify all components in your project
3. Follow [references/migration-checklist.md](references/migration-checklist.md) for step-by-step migration
4. Reference [references/method-migration.md](references/method-migration.md) for MauiProgram.cs update
5. Test your application thoroughly post-migration

Good luck with your migration! The process is straightforward, and most developers complete it in 30-60 minutes depending on project size.