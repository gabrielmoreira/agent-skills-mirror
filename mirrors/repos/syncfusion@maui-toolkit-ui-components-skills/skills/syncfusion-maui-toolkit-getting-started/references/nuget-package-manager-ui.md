# NuGet Package Manager UI Installation

## Table of Contents
- [Opening Manage NuGet Packages](#opening-manage-nuget-packages)
- [Configuring Package Source](#configuring-package-source)
- [Searching for the Package](#searching-for-the-package)
- [Installing the Package](#installing-the-package)
- [Verification Checklist](#verification-checklist)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **NuGet Package Manager UI** provides a graphical interface within Visual Studio to search, install, and manage NuGet packages. It's the most beginner-friendly method for installing Syncfusion.Maui.Toolkit and is ideal for developers who prefer visual package management.

---

## Opening Manage NuGet Packages

### Method 1: Right-Click Context Menu

1. In **Solution Explorer**, right-click on your MAUI application project
2. From the context menu, select **Manage NuGet Packages...**

The Manage NuGet Packages window will open, displaying the NuGet package management interface.

### Method 2: Tools Menu

1. In Visual Studio, click the **Tools** menu
2. Hover over **NuGet Package Manager**
3. Select **Manage NuGet Packages for Solution...**

This approach is useful when you need to manage packages across multiple projects in your solution.

---

## Configuring Package Source

### Verify nuget.org is Selected

The NuGet Package Manager needs to be pointed to the correct package source to find Syncfusion® packages.

1. In the **Manage NuGet Packages** window, locate the **Package source** dropdown (typically in the upper-right area)
2. Verify that **nuget.org** is selected as the active package source
3. If not, click the dropdown and select **nuget.org** from the available options

**Why this matters:** If the wrong package source is selected, you won't be able to find Syncfusion.Maui.Toolkit packages.

### Adding nuget.org (If Not Available)

If nuget.org is not listed as a package source:

1. Go to **Tools → Options → NuGet Package Manager → Package Sources**
2. Click the green **+** button to add a new source
3. Enter the following details:
   - **Name:** `nuget.org`
   - **Source:** `https://api.nuget.org/v3/index.json`
4. Click **OK** to save

Alternatively, follow the [Microsoft NuGet configuration instructions](https://learn.microsoft.com/en-us/nuget/consume-packages/install-use-packages-visual-studio#package-sources).

---

## Searching for the Package

### Using the Search Box

1. In the **Manage NuGet Packages** window, locate the **Search** box (typically at the top of the window)
2. Type `Syncfusion.Maui.Toolkit` exactly as shown
3. Press **Enter** or wait for auto-search to complete

The search results will display packages matching your query. You should see **Syncfusion.Maui.Toolkit** in the results list with:
- Package name: `Syncfusion.Maui.Toolkit`
- Description: Installation details and component information
- Latest version number (e.g., 1.0.0 or higher)

### Browse Tab vs. Installed Tab

- **Browse tab:** Shows available packages from the selected package source (use this to install new packages)
- **Installed tab:** Shows packages already installed in your project

Make sure you're on the **Browse** tab to find and install Syncfusion.Maui.Toolkit.

---

## Installing the Package

### Selecting the Package

1. In the search results, click on **Syncfusion.Maui.Toolkit** to select it
2. The package details pane will display on the right side, showing:
   - Package description
   - Available versions
   - Dependencies
   - Release notes

### Choosing the Version

1. In the package details pane, locate the **Version** dropdown
2. Select the appropriate version:
   - **Latest stable version** (recommended for new projects)
   - **Specific version** (if you need a particular release)

**Recommended:** Always use the latest stable version unless you have specific compatibility requirements.

### Clicking Install

1. Click the **Install** button in the package details pane
2. The installation process will begin, and you'll see progress indicators

The NuGet Package Manager will now:
- Download the Syncfusion.Maui.Toolkit package
- Resolve all dependencies
- Add the package reference to your project file

---

## Verification Checklist

### After Installation Completes

Verify the installation was successful by checking:

✓ **No error messages** appear in the NuGet Package Manager window
✓ **Package appears in Installed tab** - The Syncfusion.Maui.Toolkit now shows in the "Installed" tab
✓ **Project file updated** - Open your `.csproj` file and verify it contains a `<PackageReference>` entry for Syncfusion.Maui.Toolkit
✓ **Assemblies visible** in Solution Explorer under your project's Dependencies or Packages node

### Checking Your Project File

1. In **Solution Explorer**, right-click your MAUI project
2. Select **Edit Project File**
3. Look for an entry similar to:
   ```xml
   <ItemGroup>
     <PackageReference Include="Syncfusion.Maui.Toolkit" Version="1.0.0" />
   </ItemGroup>
   ```

This confirms the package reference has been properly added to your project.

---

## Troubleshooting

### Package Not Found in Search

**Problem:** Syncfusion.Maui.Toolkit doesn't appear in search results

**Solutions:**
1. Verify **nuget.org** is selected in Package source dropdown
2. Check your internet connection is active
3. Try clearing the search box and searching again
4. Restart Visual Studio and repeat the search
5. Confirm the exact package name: `Syncfusion.Maui.Toolkit` (case-insensitive)

### Installation Fails with Error

**Problem:** Installation shows an error message

**Common causes and solutions:**
- **"Unable to resolve dependencies"** - Ensure your MAUI project targets a supported .NET version (typically .NET 8 or higher)
- **"Package not found"** - Verify nuget.org is configured correctly as a package source
- **"Access denied"** - Check you have write permissions to the project directory

### Package Installed but References Not Visible

**Problem:** Package appears installed but you can't see the assemblies in Solution Explorer

**Solutions:**
1. Right-click the project and select **Reload Project**
2. Close and reopen your project
3. Clean and rebuild the solution (**Build → Clean Solution**, then **Build → Build Solution**)
4. Delete the `bin` and `obj` directories manually and rebuild

---

## Next Steps After Installation

Once Syncfusion.Maui.Toolkit is successfully installed:

1. **Explore the Syncfusion® toolkit documentation** for available components and controls
2. **Add your first component** to your XAML pages (e.g., SfButton, SfCard, etc.)
3. **Build and run** your application to verify the installation works
4. **Review sample projects** from Syncfusion® toolkit documentation for implementation patterns

Your MAUI application is now ready to use Syncfusion® .NET MAUI Toolkit components.
