# Getting Started with Migration

## Table of Contents

- [Understanding the Migration](#understanding-the-migration)
- [Prerequisites and Requirements](#prerequisites-and-requirements)
- [Scope of This Guide](#scope-of-this-guide)
- [What's Changing](#whats-changing)
- [Why Migrate](#why-migrate)

## Understanding the Migration

The **Syncfusion® Toolkit for .NET MAUI** is the evolved platform for building modern MAUI applications with Syncfusion® components. While the previous **Syncfusion® .NET MAUI** package contained individual component assemblies, the new toolkit consolidates all components into a single, unified package.

### Key Point
Migration is **not** a breaking change. Your application logic, component functionality, and API usage patterns remain exactly the same. You're primarily updating namespaces and package references.

## Prerequisites and Requirements

Before starting migration, ensure your development environment meets these requirements:

### System Requirements
- **Visual Studio 2022** (Version 17.0 or later)
- **.NET MAUI 8.0** or later
- **Windows 10/11** for development
- Target platforms: iOS, Android, macOS, Windows

### Project Requirements
- Existing Syncfusion® .NET MAUI application
- All projects should target .NET 8.0 or later
- No custom component derivations with complex inheritance chains
- Standard component usage patterns (no reflection-based dynamic component instantiation)

### Knowledge Prerequisites
- Basic understanding of .NET MAUI project structure
- Familiarity with XAML namespace declarations
- Comfort editing C# code files and XAML
- Basic knowledge of NuGet package management

### Estimated Time
- **Small projects** (1-5 pages): 15-30 minutes
- **Medium projects** (6-15 pages): 30-60 minutes
- **Large projects** (15+ pages): 60-120 minutes

## Scope of This Guide

This guide covers:

### ✅ Included in Migration
- Namespace updates for 20+ Syncfusion® components
- NuGet package reference updates
- C# using statement changes
- XAML namespace declaration changes
- MauiProgram.cs initialization update
- Search & replace patterns for bulk updates
- Common issues and troubleshooting
- Post-migration validation

### ❌ Out of Scope
- Updating component API usage (components themselves haven't changed)
- Refactoring application architecture
- Performance optimization beyond toolkit defaults
- Custom theme creation (covered in toolkit documentation)
- Advanced styling with CSS modules

## What's Changing

The migration involves changes in three main areas:

### 1. NuGet Packages
**Before:**
```
Syncfusion.Maui.Buttons
Syncfusion.Maui.Calendar
Syncfusion.Maui.Cards
Syncfusion.Maui.Carousel
...and ~15 more individual packages
```

**After:**
```
Syncfusion.Maui.Toolkit (single package replaces all)
```

### 2. Namespaces (XAML)
**Pattern Before:**
```
xmlns:button="clr-namespace:Syncfusion.Maui.Buttons;assembly=Syncfusion.Maui.Buttons"
```

**Pattern After:**
```
xmlns:button="clr-namespace:Syncfusion.Maui.Toolkit.Buttons;assembly=Syncfusion.Maui.Toolkit"
```

### 3. Namespaces (C#)
**Pattern Before:**
```csharp
using Syncfusion.Maui.Buttons;
```

**Pattern After:**
```csharp
using Syncfusion.Maui.Toolkit.Buttons;
```

### 4. Configuration Method
**Before (MauiProgram.cs):**
```csharp
.ConfigureSyncfusionCore()
```

**After (MauiProgram.cs):**
```csharp
.ConfigureSyncfusionToolkit()
```

### 5. Hosting Namespace
**Before:**
```csharp
using Syncfusion.Maui.Core.Hosting;
```

**After:**
```csharp
using Syncfusion.Maui.Toolkit.Hosting;
```

## Why Migrate

### Benefits of Toolkit
- **Unified Package Management**: Single NuGet package instead of managing 20+ individual packages
- **Simpler Dependencies**: Fewer assembly references and cleaner project structure
- **Modern Development**: Access to latest component features and bug fixes
- **Better Performance**: Optimized in single compiled assembly
- **Consistent API**: All components follow unified design patterns
- **Future-Proof**: Toolkit is the forward-looking platform for Syncfusion® MAUI components

### Migration Value
- **Quick Migration**: Most projects complete in under 1 hour
- **Minimal Code Changes**: Primarily namespace updates
- **Full Compatibility**: No functional changes to components
- **Better Support**: Toolkit version receives priority support and updates
- **Active Development**: New features added to toolkit regularly

## Component Coverage

This migration covers the following 20+ components:

| Component | Status |
|-----------|--------|
| SfButton | ✅ Migrated |
| SfCalendar | ✅ Migrated |
| SfCards | ✅ Migrated |
| SfCarousel | ✅ Migrated |
| SfCartesianChart | ✅ Migrated |
| SfCircularChart | ✅ Migrated |
| SfCircularProgressBar | ✅ Migrated |
| SfChip | ✅ Migrated |
| SfEffectsView | ✅ Migrated |
| SfExpander | ✅ Migrated |
| SfFunnelChart | ✅ Migrated |
| SfLinearProgressBar | ✅ Migrated |
| SfNavigationDrawer | ✅ Migrated |
| SfNumericEntry | ✅ Migrated |
| SfNumericUpDown | ✅ Migrated |
| SfPicker | ✅ Migrated |
| SfPopup | ✅ Migrated |
| SfPullToRefresh | ✅ Migrated |
| SfSegmentedControl | ✅ Migrated |
| SfShimmer | ✅ Migrated |
| SfSunburstChart | ✅ Migrated |
| SfTabView | ✅ Migrated |
| SfTextInputLayout | ✅ Migrated |
| SfPolarChart | ✅ Migrated |
| SfPyramidChart | ✅ Migrated |
| SfAccordion | ✅ Migrated |

All of these components work identically after migration—only namespaces change.

## Next Steps

1. **Document Current Setup**: Note which components your project uses (refer to the [Component Coverage](#component-coverage) table above)
2. **Backup Your Project**: Create a git commit or backup your entire project folder
3. **Review Timeline**: Estimate migration time based on project size (see [Estimated Time](#estimated-time) section)
4. **Read Namespace Guide**: Head to [references/namespace-updates.md](namespace-updates.md) to understand exact namespace mappings
5. **Follow Migration Steps**: Use [references/migration-checklist.md](migration-checklist.md) for step-by-step numbered process

The migration process is straightforward. Most developers find it to be a smooth, routine update.