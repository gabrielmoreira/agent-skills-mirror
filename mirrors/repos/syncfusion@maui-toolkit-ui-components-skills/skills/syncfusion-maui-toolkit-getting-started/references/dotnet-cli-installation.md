# .NET CLI Installation

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Opening Command Prompt](#opening-command-prompt)
- [Basic Installation Command](#basic-installation-command)
- [Specifying Package Versions](#specifying-package-versions)
- [Verifying Installation](#verifying-installation)
- [Running dotnet restore](#running-dotnet-restore)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **.NET Command Line Interface (CLI)** provides a powerful way to manage NuGet packages without using Visual Studio. This method is ideal for automation, CI/CD pipelines, and developers who prefer command-line workflows.

The `dotnet add package` command allows you to add packages to your project while working from the terminal, making it perfect for scripting and batch installations.

---

## Prerequisites

Before using the .NET CLI to install packages, ensure you have:

✓ **.NET SDK installed** - Required to use dotnet CLI commands
  - Download from [Microsoft .NET downloads](https://dotnet.microsoft.com/download)
  - Verify installation: Open a terminal and run `dotnet --version`

✓ **MAUI project created** - A .NET MAUI application project in your solution

✓ **Terminal or Command Prompt** - Git Bash, PowerShell, Command Prompt, or similar

✓ **Project directory accessible** - Path to your MAUI application directory

---

## Opening Command Prompt

### On Windows

1. Open **File Explorer** and navigate to your MAUI project directory
2. Press **Shift + Right-click** on an empty area inside the folder
3. Select **"Open PowerShell window here"** or **"Open command window here"**

Alternatively:
1. Press **Windows Key + R** to open the Run dialog
2. Type `cmd` and press **Enter**
3. Use `cd` command to navigate to your project directory:
   ```
   cd C:\Users\YourUsername\Projects\YourMauiApp
   ```

### On Mac or Linux

1. Open **Terminal** (Command + Space, then type "Terminal")
2. Use the `cd` command to navigate to your MAUI project:
   ```
   cd ~/Projects/YourMauiApp
   ```

---

## Basic Installation Command

### Install Latest Version

Navigate to your MAUI project directory and run:

```
dotnet add package Syncfusion.Maui.Toolkit
```

**What this command does:**
- Connects to nuget.org package source
- Searches for the latest stable version of Syncfusion.Maui.Toolkit
- Downloads the package and all dependencies
- Adds a `<PackageReference>` entry to your `.csproj` file
- Installs the package into your project

**Expected output:**
```
info : Determining projects to restore...
info : Restoring NuGet packages...
info : Package 'Syncfusion.Maui.Toolkit' is compatible with all the specified frameworks in [YourProject].csproj.
info : PackageReference for package 'Syncfusion.Maui.Toolkit' version '[version]' added to file '[YourProject].csproj'.
info : Committing restore...
info : Writing assets file to disk. Path: [path to assets file]
info : Restore completed in [time] ms.
```

---

## Specifying Package Versions

### Install a Specific Version

If you need a particular version of Syncfusion.Maui.Toolkit, use the `-v` parameter:

```
dotnet add package Syncfusion.Maui.Toolkit -v 1.0.0
```

Replace `1.0.0` with the version you need.

### Finding Available Versions

To see all available versions of a package:

```
dotnet package search Syncfusion.Maui.Toolkit --exact-match
```

Or visit [nuget.org/packages/Syncfusion.Maui.Toolkit](https://www.nuget.org/packages/Syncfusion.Maui.Toolkit) to browse all released versions.

### Version String Formats

The `-v` parameter accepts various version formats:

| Format | Example | Behavior |
|--------|---------|----------|
| Exact version | `1.0.0` | Installs exactly this version |
| Patch range | `1.0.*` | Installs latest patch for 1.0.x |
| Minor range | `1.*` | Installs latest version of 1.x.x |
| Greater than | `>1.0.0` | Installs any version after 1.0.0 |

**Recommended:** Always use exact version numbers for reproducible builds.

---

## Verifying Installation

### Check Project File

After installation, verify the package was added to your project file:

1. Open your `.csproj` file with a text editor (or in Visual Studio)
2. Look for a section like this:

```xml
<ItemGroup>
  <PackageReference Include="Syncfusion.Maui.Toolkit" Version="1.0.0" />
</ItemGroup>
```

If this entry exists with the correct package name and version, installation was successful.

### Inspect Project Directory

The package files are typically stored in your system's NuGet cache directory:
- **Windows:** `C:\Users\[username]\.nuget\packages\syncfusion.maui.toolkit`
- **Mac/Linux:** `~/.nuget/packages/syncfusion.maui.toolkit/`

### Check obj/project.assets.json

Your project's lock file should contain Syncfusion® package references:

1. Navigate to `obj/project.assets.json` in your project directory
2. Search for `"Syncfusion.Maui.Toolkit"` in the file
3. Verify the version matches what you installed

---

## Running dotnet restore

The `dotnet add package` command automatically runs `dotnet restore` as part of the process. However, you can manually run it to ensure all dependencies are properly installed:

```
dotnet restore
```

**What this command does:**
- Reads package references from your `.csproj` file
- Downloads packages from NuGet.org to the NuGet cache
- Creates a lock file (`project.assets.json`)
- Validates all dependencies are compatible
- Ensures your project is ready to build

**When to use this manually:**
- After cloning a repository with existing `.csproj` files
- When package changes don't seem to take effect
- After merging conflicting `.csproj` changes
- To update all packages to their specified versions

---

## Error Handling

### Package Not Found

**Error message:**
```
error NU1101: Unable to find package Syncfusion.Maui.Toolkit
```

**Solutions:**
1. Verify internet connection is active
2. Confirm exact package name: `Syncfusion.Maui.Toolkit`
3. Check you're in the correct project directory
4. Clear NuGet cache: `dotnet nuget locals all --clear`
5. Try again: `dotnet add package Syncfusion.Maui.Toolkit`

### Version Not Found

**Error message:**
```
error NU1102: Package 'Syncfusion.Maui.Toolkit' version '9.9.9' could not be found
```

**Solution:**
- Use a valid version number
- Check available versions at [nuget.org](https://www.nuget.org/packages/Syncfusion.Maui.Toolkit)
- Try the latest version: `dotnet add package Syncfusion.Maui.Toolkit`

### Framework Incompatibility

**Error message:**
```
error NU1202: Package Syncfusion.Maui.Toolkit is not compatible with net6.0 (.NET 6.0)
```

**Solutions:**
1. Ensure your project targets a supported .NET version (typically .NET 8 or higher for MAUI)
2. Update your project's target framework in the `.csproj` file
3. Use the latest MAUI project template with supported .NET version

---

## Troubleshooting

### Command Not Recognized

**Problem:** "dotnet is not recognized as an internal or external command"

**Solution:**
1. Install .NET SDK from [dotnet.microsoft.com](https://dotnet.microsoft.com/download)
2. Add .NET SDK to PATH environment variables
3. Restart your terminal
4. Verify installation: `dotnet --version`

### Permission Denied

**Problem:** "Access denied" or "Permission denied" error

**Solutions:**
- Ensure you have write permissions to the project directory
- Run terminal as administrator (Windows) or use `sudo` (Mac/Linux)
- Check that the `.csproj` file isn't read-only

### Restore Takes Too Long

**Problem:** Installation or restore seems to hang or is very slow

**Solutions:**
1. Check your internet connection speed
2. Try using a different NuGet source
3. Clear the NuGet cache: `dotnet nuget locals all --clear`
4. Update .NET SDK: `dotnet tool update -g dotnet-cli`

### Package Installed But Build Fails

**Problem:** Installation succeeded but the project won't compile

**Solutions:**
1. Run `dotnet clean` to clear build artifacts
2. Run `dotnet build` to rebuild the solution
3. Delete `bin` and `obj` folders manually and rebuild
4. Ensure all dependencies are compatible with your .NET version
5. Check your project file for any XML syntax errors

### Multiple Project Installation Issues

**Problem:** Installing into one project affects another

**Solution:**
- When using .NET CLI, navigate to the specific project directory before running the command
- The command only affects the project in the current directory

---

## Next Steps

After successful installation using the .NET CLI:

1. **Build your project** to ensure everything compiles:
   ```
   dotnet build
   ```

2. **Run your application** to verify installation:
   ```
   dotnet run
   ```

3. **Start using Syncfusion® components** in your XAML or C# code

4. **Explore the Syncfusion® documentation** for available components and features

Your MAUI application is now ready to use Syncfusion® .NET MAUI Toolkit components.
