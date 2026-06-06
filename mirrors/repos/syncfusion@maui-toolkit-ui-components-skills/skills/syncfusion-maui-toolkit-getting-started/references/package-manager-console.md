# Package Manager Console Installation

## Table of Contents
- [Overview](#overview)
- [Accessing Package Manager Console](#accessing-package-manager-console)
- [Basic Install-Package Command](#basic-install-package-command)
- [Specifying Version Parameters](#specifying-version-parameters)
- [Targeting Specific Projects](#targeting-specific-projects)
- [Installation Monitoring](#installation-monitoring)
- [Verification and Confirmation](#verification-and-confirmation)
- [Multi-Project Setup](#multi-project-setup)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **Package Manager Console** is a PowerShell-based command interface built into Visual Studio that provides advanced control over NuGet package management. It's ideal for experienced developers who are comfortable with PowerShell syntax and need fine-grained control over package installation in complex solutions with multiple projects.

---

## Accessing Package Manager Console

### Opening the Console

1. In Visual Studio, click the **Tools** menu
2. Hover over **NuGet Package Manager**
3. Select **Package Manager Console**

The Package Manager Console window will open at the bottom of Visual Studio, showing a PowerShell prompt ready for commands.

### Console Location

The Package Manager Console typically appears as a new tab or docked window at the bottom of the Visual Studio interface, next to other output panels like the Debug Console and Error List.

### PowerShell Environment

The console runs PowerShell within Visual Studio and supports standard PowerShell commands. You can run NuGet-specific cmdlets (like `Install-Package`, `Update-Package`, `Remove-Package`) directly without any prefix.

---

## Basic Install-Package Command

### Install Latest Version

In the Package Manager Console, type the following command:

```
Install-Package Syncfusion.Maui.Toolkit
```

Press **Enter** to execute the command.

**What this command does:**
- Connects to the default NuGet package source (nuget.org)
- Searches for the latest stable version of Syncfusion.Maui.Toolkit
- Downloads the package and all dependencies
- Installs the package into the active project
- Adds a `<PackageReference>` entry to the project file
- Displays installation progress and completion status

### Expected Output

You should see output similar to this:

```
Attempting to gather dependency information for package 'Syncfusion.Maui.Toolkit'
Attempting to resolve dependencies for the first time.
Retrieving package dependency information took [time]
Successfully installed 'Syncfusion.Maui.Toolkit [version]'.
```

**Green checkmark or success indicator** confirms the installation completed without errors.

---

## Specifying Version Parameters

### Installing a Specific Version

To install a specific version of the package, use the `-Version` parameter:

```
Install-Package Syncfusion.Maui.Toolkit -Version 1.0.0
```

Replace `1.0.0` with the desired version number.

### Version Parameter Syntax

The `-Version` parameter accepts multiple formats:

| Format | Example | Result |
|--------|---------|--------|
| Exact version | `-Version 1.0.0` | Installs exactly 1.0.0 |
| Prerelease | `-Version 1.0.0-beta` | Installs beta/prerelease version |
| Version range | `-Version [1.0, 2.0)` | Installs version from 1.0 to less than 2.0 |

### Finding Available Versions

To list all available versions in the console:

```
Find-Package Syncfusion.Maui.Toolkit -AllVersions
```

This displays all versions available on nuget.org, helping you choose the appropriate version for your needs.

---

## Targeting Specific Projects

### Installing into a Specific Project

In a Visual Studio solution with multiple projects, use the `-ProjectName` parameter to install into a specific project:

```
Install-Package Syncfusion.Maui.Toolkit -ProjectName MyMauiApp
```

Replace `MyMauiApp` with the exact name of your MAUI project as shown in Solution Explorer.

### Combined Version and Project Parameters

You can combine both `-Version` and `-ProjectName` parameters:

```
Install-Package Syncfusion.Maui.Toolkit -Version 1.0.0 -ProjectName MyMauiApp
```

This installs exactly version 1.0.0 into the MyMauiApp project.

### Selecting Active Project

If you don't specify a project name, the package is installed into the currently selected project in the **Package Manager Console**. You can see and change the active project using:

- **Default Project dropdown** at the top of the Package Manager Console window
- Click on the dropdown to select which project should receive the next command

---

## Installation Monitoring

### Progress Display

During installation, the console displays real-time progress information:

```
Retrieving package dependency information...
Performing nuget operations took [time] ms.
Installing NuGet package...
Successfully installed 'Syncfusion.Maui.Toolkit 1.0.0' to [ProjectName]
```

### Dependency Resolution

If the package has dependencies, you'll see messages like:

```
Attempting to gather dependency information for package 'Syncfusion.Maui.Toolkit'
Attempting to resolve dependencies for the first time.
```

This indicates the console is automatically resolving and installing any required dependencies.

### Error Messages During Installation

If issues occur, they appear immediately in the console:

```
Install-Package : Package 'Syncfusion.Maui.Toolkit' does not exist on the server.
```

or

```
Install-Package : 'Syncfusion.Maui.Toolkit 1.0.0' is not compatible with the selected project framework.
```

Refer to the [Troubleshooting](#troubleshooting) section for solutions.

---

## Verification and Confirmation

### Console Confirmation

After the command completes, the console displays:

```
Successfully installed 'Syncfusion.Maui.Toolkit 1.0.0' to [ProjectName]
```

A green checkmark or similar indicator confirms success.

### Checking Project File

1. In Solution Explorer, right-click your MAUI project
2. Select **Edit Project File**
3. Verify a `<PackageReference>` entry exists:

```xml
<ItemGroup>
  <PackageReference Include="Syncfusion.Maui.Toolkit" Version="1.0.0" />
</ItemGroup>
```

### Verifying in Solution Explorer

1. Expand your project in Solution Explorer
2. Look for **Dependencies** or **Packages** node
3. You should see **Syncfusion.Maui.Toolkit** listed with its version
4. Expand it to view included assemblies and dependencies

---

## Multi-Project Setup

### Installing into Multiple Projects

When your solution contains multiple MAUI or related projects that all need Syncfusion.Maui.Toolkit:

**Method 1: Repeat for Each Project**
```
Install-Package Syncfusion.Maui.Toolkit -ProjectName Project1
Install-Package Syncfusion.Maui.Toolkit -ProjectName Project2
Install-Package Syncfusion.Maui.Toolkit -ProjectName Project3
```

Execute each command separately by pressing Enter after each line.

**Method 2: Using Wildcard Pattern (Advanced)**

Some PowerShell patterns allow bulk operations, though this is less common with NuGet commands.

### Checking Installation Across Projects

To verify Syncfusion.Maui.Toolkit is installed in all necessary projects:

1. Open each project's `.csproj` file
2. Confirm the `<PackageReference>` exists in each project's `<ItemGroup>`
3. Or expand each project in Solution Explorer and check the Dependencies/Packages node

---

## Troubleshooting

### Command Not Recognized

**Problem:** "Install-Package : The term 'Install-Package' is not recognized"

**Solution:**
1. Ensure Package Manager Console is open (not the regular terminal)
2. Package Manager Console must be in Visual Studio
3. Restart Visual Studio if the issue persists

### Package Not Found

**Problem:** "Install-Package : Package 'Syncfusion.Maui.Toolkit' does not exist on the server"

**Solutions:**
1. Verify internet connection is active
2. Check exact package name: `Syncfusion.Maui.Toolkit` (case-insensitive)
3. Confirm nuget.org is the configured package source
4. Clear the NuGet cache:
   ```
   Update-Package -Reinstall
   ```
5. Try again

### Framework Incompatibility

**Problem:** "'Syncfusion.Maui.Toolkit 1.0.0' is not compatible with [TargetFramework]"

**Solution:**
1. Ensure your project targets a compatible .NET framework (typically .NET 8 or higher for MAUI)
2. Check your `.csproj` file for the `<TargetFramework>` element
3. Update to a compatible framework version
4. Update your project template if using an older template

### Permission Denied

**Problem:** Installation fails with permission error

**Solutions:**
1. Close all instances of the project file if open in editors
2. Restart Visual Studio with Administrator privileges
3. Ensure you have write permissions to the project directory
4. Check that project files aren't marked as read-only

### Project Name Not Found

**Problem:** "Package 'Syncfusion.Maui.Toolkit' could not be installed in project '[ProjectName]'"

**Solutions:**
1. Verify the project name exactly matches the name in Solution Explorer
2. Project names are case-sensitive in some scenarios; try exact casing
3. Use Tab completion: Type `-ProjectName ` and press Tab to cycle through available projects
4. Ensure the project is a valid .NET MAUI project

### Rollback Failed Installation

**Problem:** Installation failed partway through and you need to clean up

**Solution:**
1. Run `Update-Package -Reinstall` to attempt recovery
2. Or manually edit the `.csproj` file and remove the failed `<PackageReference>`
3. Run `Update-Package` command again to restore proper state

---

## Console Keyboard Shortcuts

**Useful shortcuts while using Package Manager Console:**

- **Tab** - Autocomplete command names and parameter names
- **Up Arrow** - Recall previous commands
- **Down Arrow** - Navigate through command history
- **Ctrl + L** - Clear console output
- **Ctrl + A** - Select all console text

---

## Next Steps

After successfully installing Syncfusion.Maui.Toolkit via Package Manager Console:

1. **Build your solution** to ensure no compilation errors:
   ```
   Rebuild-Project
   ```

2. **Verify in the IDE** - Check that IntelliSense now recognizes Syncfusion® components

3. **Start using Syncfusion® toolkit components** in your XAML or C# code

4. **Review available components** in the Syncfusion® toolkit documentation

Your MAUI application is now ready to use Syncfusion® .NET MAUI Toolkit components.
