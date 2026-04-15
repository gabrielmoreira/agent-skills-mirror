# Release Notes Templates

## Index Page Template

File: `release-notes/maui-release-notes.md`

```markdown
# .NET MAUI Workload Release Notes

> **Last Updated:** {current_date}

This page lists all .NET MAUI workload release notes. Each entry links to detailed release notes with full dependency information and installation instructions.

---

## Releases

### {MMMM D, YYYY}

📄 [Full Release Notes](maui-release-notes-{YYYYMMDD}.md)

#### .NET {major}

**Workload Set:** `{workload_set_version}` (CLI: `{cli_version}`)

| Workload | Version | Requirements |
|----------|---------|--------------|
| MAUI | {maui_version} | |
| iOS | {ios_version} | Xcode ≥ {xcode_version} |
| Mac Catalyst | {maccatalyst_version} | Xcode ≥ {xcode_version} |
| tvOS | {tvos_version} | Xcode ≥ {xcode_version} |
| macOS | {macos_version} | Xcode ≥ {xcode_version} |
| Android | {android_version} | API {android_api}, JDK {jdk_version} |

| MAUI NuGet Packages | Implicit | Latest |
|---------------------|----------|--------|
| Microsoft.Maui.Controls | {implicit_version} | {latest_version} |

---
```

**Index Entry Rules:**
- Only include .NET version sections that had updates
- Link to full notes at top for quick access
- Requirements column: Xcode for Apple platforms, API + JDK for Android, empty for MAUI
- If a dated note came from a custom/private feed, mention that source in the
  dated note header even if the index entry stays concise

---

## Dated Release Notes Template

File: `release-notes/maui-release-notes-{YYYYMMDD}.md`

### Header

```markdown
# .NET MAUI Workload Release Notes - {Month Day, Year}

> **Date:** {current_date}  
> **Source:** NuGet feeds queried at generation time ({source_summary})

This document provides version information for .NET MAUI and related platform workloads across the two most recent major .NET versions.

⬅️ [Back to Release Notes Index](maui-release-notes.md)

---
```

### Per .NET Version Section

```markdown
# .NET {major}

## Workloads

**Workload Set:** [Microsoft.NET.Workloads.{package-id-sdk-band}]  @  {cli_version}](https://www.nuget.org/packages/Microsoft.NET.Workloads.{package-id-sdk-band}/{nuget_version})

### Installation

\`\`\`bash
dotnet workload update --version {cli_version}
# Or install specific workloads
dotnet workload install maui ios maccatalyst android --version {cli_version}
\`\`\`

### Recommended Tools:
 - Xcode: {recommended_xcode_version}
 - Java JDK: recommended_java_jdk_version
 - Android API-{android_api}

<details>
<summary><h3>Workload Versions</h3></summary>

| Workload | Full ID | Version | SDK Band | Links |
|----------|---------|---------|----------|-------|
| **MAUI** | Microsoft.NET.Sdk.Maui | {version} | {band} | [NuGet]({manifest_link}) · [Release]({dotnet_maui_release_link}) |
| **iOS** | Microsoft.NET.Sdk.iOS | {version} | {band} | [NuGet]({manifest_link}) · [Release]({dotnet_macios_release_link}) |
| **Mac Catalyst** | Microsoft.NET.Sdk.MacCatalyst | {version} | {band} | [NuGet]({manifest_link}) · [Release]({dotnet_macios_release_link}) |
| **Android** | Microsoft.NET.Sdk.Android | {version} | {band} | [NuGet]({manifest_link}) · [Release]({dotnet_android_release_link}) |
| **tvOS** | Microsoft.NET.Sdk.tvOS | {version} | {band} | [NuGet]({manifest_link}) · [Release]({dotnet_macios_release_link}) |
| **macOS** | Microsoft.NET.Sdk.macOS | {version} | {band} | [NuGet]({manifest_link}) · [Release]({dotnet_macios_release_link}) |

<!-- NOTE: If the selected workload set or manifest version was discovered from a
private/internal feed, keep the package link pointed at the equivalent
NuGet.org URL and note the discovery source in the document header. -->

</details>
<details>
<summary><h3>MAUI NuGet Packages</h3></summary>

The following NuGet packages are the core .NET MAUI libraries. The **Implicit Version** is bundled with the workload, while **Latest Version** may be newer due to out-of-band releases.

| Package | Implicit Version | Latest Version |
|---------|------------------|----------------|
| **Microsoft.Maui.Controls** | [{workload_version}]({nuget_link}) | [{latest_version}]({nuget_link}) |
| **Microsoft.Maui.Controls.Compatibility** | [{workload_version}]({nuget_link}) | [{latest_version}]({nuget_link}) |
| **Microsoft.Maui.Essentials** | [{workload_version}]({nuget_link}) | [{latest_version}]({nuget_link}) |
| **Microsoft.Maui.Graphics** | [{workload_version}]({nuget_link}) | [{latest_version}]({nuget_link}) |
| **Microsoft.Maui.Maps** | [{workload_version}]({nuget_link}) | [{latest_version}]({nuget_link}) |
</details>
<details>
<summary><h3>Native Tool & SDK Compatibility</h3></summary>

#### Apple (iOS, Mac Catalyst, tvOS, macOS)

|  Tool     | Min Version.          | Recommended Version         |
|-----------|-----------------------|-----------------------------|
| **Xcode** | ≥ {min_xcode_version} | {recommended_xcode_version} |


#### Java JDK (Android)

|  Tool        | Min / Required Version                                | Recommended Version            |
|--------------|-------------------------------------------------------|--------------------------------|
| **Java JDK** | ≥ {min_java_jdk_version} and < {max_java_jdk_version} | {recommended_java_jdk_version} |


#### Android SDK Packages (Required)

| SDK Package                           | Description                                         |
|---------------------------------------|-----------------------------------------------------|
| **`build-tools;{version}`**           | Android SDK Build-Tools {major}                     |
| **`cmdline-tools;{version}`**         | Android SDK Command-line Tools {major}              |
| **`platforms;android-{android_api}`** | Android SDK Platform {android_api}                  |
| **`platform-tools`**                  | Android SDK Platform-Tools {platform_tools_version} |

#### Android SDK Packages (Optional)

| Package                           | Description                     |
|-----------------------------------|---------------------------------|
| `emulator`                        | Android Emulator                |
| `ndk-bundle`                      | NDK                             |
| `platforms;android-{preview_api}` | Android SDK Platform (Preview)  |
| System Images                     | Google APIs ARM 64 v8a / x86_64 |

#### MAUI Windows Dependencies

| Dependency | Minimum Version | Recommended |
|------------|-----------------|-------------|
| **Windows App SDK** | ≥ {version} | {version} |
| **Windows SDK Build Tools** | ≥ {version} | {version} |
| **Win2D** | ≥ {version} | {version} |
| **WebView2** | ≥ {version} | {version} |
</details>

```

### Reference Section (End of Document)

```markdown
---

# Reference

## Version Notation

| Notation | Meaning |
|----------|---------|
| `[17.0,22.0)` | ≥ 17.0 AND < 22.0 |
| `[26.2,)` | ≥ 26.2 (no upper bound) |

For more information, see the [.NET Workload Sets documentation](https://learn.microsoft.com/dotnet/core/tools/dotnet-workload-sets).

## Platform GitHub Repositories

| Platform | Repository | Releases |
|----------|------------|----------|
| MAUI | [dotnet/maui](https://github.com/dotnet/maui) | [Releases](https://github.com/dotnet/maui/releases) |
| iOS, Mac Catalyst, tvOS, macOS | [dotnet/macios](https://github.com/dotnet/macios) | [Releases](https://github.com/dotnet/macios/releases) |
| Android | [dotnet/android](https://github.com/dotnet/android) | [Releases](https://github.com/dotnet/android/releases) |

> NOTE: macios releases may not use exact versions in their name/tag... an example is: `dotnet-11.0.1xx-preview2-11425` - DO YOUR BEST to match the relevant release note link in this repo to the workload release version we are generating notes for.
```
