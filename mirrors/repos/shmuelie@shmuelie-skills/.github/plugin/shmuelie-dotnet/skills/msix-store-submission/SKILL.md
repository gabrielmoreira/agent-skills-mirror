---
name: msix-store-submission
description: Microsoft Store submission for MSIX apps — Partner Center identity, signing, self-contained packaging, manifest alignment, and CI/CD for Store uploads
---

When preparing an MSIX-packaged application (WinUI 3, WPF, Win32, or any other framework) for Microsoft Store submission, apply this domain knowledge.

# Microsoft Store Submission — Domain Knowledge

## Partner Center Identity Alignment

### Required Manifest Changes
When you reserve an app name in Partner Center, you receive identity values that must be set
in `Package.appxmanifest`:

```xml
<Identity
    Name="12345Publisher.AppName"
    Publisher="CN=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    Version="1.0.0.0"
    ProcessorArchitecture="neutral" />

<Properties>
    <DisplayName>App Name</DisplayName>
    <PublisherDisplayName>Publisher Name</PublisherDisplayName>
    <Logo>Assets\StoreLogo.png</Logo>
</Properties>

<mp:PhoneIdentity PhoneProductId="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
                  PhonePublisherId="00000000-0000-0000-0000-000000000000" />
```

### Key Fields
| Field | Source | Notes |
|-------|--------|-------|
| `Identity Name` | Partner Center → App identity | Format: `<PublisherId>.<AppName>` (e.g., `56889Shmuelie.ModernMeeter`) |
| `Identity Publisher` | Partner Center → App identity | CN from your publisher certificate (a GUID) |
| `PublisherDisplayName` | Partner Center → Account settings | Must match exactly (e.g., `Shmuelie`) |
| `PhoneProductId` | Partner Center → App identity | A real GUID assigned to your app |
| `Identity Version` | You set this | Must be 4-part: `x.y.z.0` |

### Common Mistakes
- Using placeholder values (`CN=MyApp`) — Store rejects packages with wrong publisher.
- Forgetting `PhoneProductId` — use the GUID from Partner Center, not a dummy.
- `PublisherDisplayName` mismatch — must be identical to your Partner Center account name.

## Signing Configuration

### For Store Submission
The Microsoft Store re-signs packages with its own certificate. Disable local signing:
```xml
<!-- In .csproj PropertyGroup -->
<AppxPackageSigningEnabled>false</AppxPackageSigningEnabled>
<GenerateTemporaryStoreCertificate>True</GenerateTemporaryStoreCertificate>
```
- `AppxPackageSigningEnabled=false` — don't sign during build (Store handles it).
- `GenerateTemporaryStoreCertificate=True` — creates a temporary cert for local dev/testing
  so the package can still be registered locally during development.

### For Sideloading (Non-Store)
If distributing outside the Store, you need to sign with your own certificate:
```xml
<AppxPackageSigningEnabled>true</AppxPackageSigningEnabled>
<PackageCertificateThumbprint>YOUR_CERT_THUMBPRINT</PackageCertificateThumbprint>
```

## Self-Contained Packaging

### Why Self-Contained
Self-contained apps bundle the .NET runtime and don't require users to install it separately.
For Store apps, this ensures the app works on any Windows machine without prerequisites.

### Configuration
```xml
<PropertyGroup>
    <SelfContained>true</SelfContained>
    <WindowsAppSDKSelfContained>true</WindowsAppSDKSelfContained>
</PropertyGroup>
```

### Framework Dependency Stripping (CRITICAL)
`WindowsAppSDKSelfContained=true` does NOT automatically remove the `PackageDependency` element
from the generated `AppxManifest.xml`. The app will still require the WinAppRuntime framework
package at install time unless you strip it.

**Fix:** Add a post-build MSBuild target:
```xml
<!--
  WindowsAppSDKSelfContained=true doesn't strip the framework PackageDependency
  from the generated manifest. This target removes it post-build so the app runs
  without the WinAppRuntime framework package installed.
-->
<Target Name="RemoveWinAppRuntimeDependency"
        AfterTargets="Build"
        Condition="'$(WindowsAppSDKSelfContained)' == 'true'"
        Inputs="$(OutputPath)AppxManifest.xml"
        Outputs="$(OutputPath)AppxManifest.xml.patched">
    <Exec Command="powershell -NoProfile -Command &quot;if (Test-Path '$(OutputPath)AppxManifest.xml') { (Get-Content '$(OutputPath)AppxManifest.xml' -Raw) -replace '&lt;PackageDependency[^/]*/&gt;','' | Set-Content '$(OutputPath)AppxManifest.xml' -NoNewline }&quot;"
          Condition="Exists('$(OutputPath)AppxManifest.xml')" />
    <Touch Files="$(OutputPath)AppxManifest.xml.patched" AlwaysCreate="true" />
</Target>
```

## Version Management

### MSIX Version Requirements
- MSIX requires a **4-part version**: `Major.Minor.Patch.0` (the 4th part must be 0 for Store).
- Keep `<Version>` in the csproj and `<Identity Version>` in the manifest in sync.
- Follow SemVer for the first 3 parts; always set the 4th to `0`.

### Where to Set Version
```xml
<!-- .csproj -->
<Version>1.2.0</Version>

<!-- Package.appxmanifest -->
<Identity Version="1.2.0.0" ... />
```

## Solution Configuration

### Platform Locking
Lock the solution to only the platforms you actually build for — don't include AnyCPU:
```xml
<!-- .slnx -->
<Solution>
    <Configurations>
        <Platform Name="x64" />
    </Configurations>
    <Project Path="src/MyApp.csproj">
        <Platform Project="x64" />
        <Deploy />
    </Project>
</Solution>
```

### ProcessorArchitecture
Set `ProcessorArchitecture="neutral"` in the manifest `<Identity>` if you want the Store to
determine architecture, or use `x64`/`arm64` for architecture-specific packages.

## CI/CD for Store Builds

### GitHub Actions Workflow
```yaml
name: Store Build
on:
  push:
    tags: ['v*']
jobs:
  build:
    runs-on: windows-latest
    strategy:
      matrix:
        platform: [x64, ARM64]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'
      - uses: microsoft/setup-msbuild@v2
      - run: msbuild MyApp.csproj -restore -p:Platform=${{ matrix.platform }} -p:Configuration=Release
      - uses: actions/upload-artifact@v4
        with:
          name: msix-${{ matrix.platform }}
          path: '**/*.msix'
```

### Key CI Notes
- **MSBuild required** — `dotnet build` doesn't support MSIX packaging tasks.
- Use `microsoft/setup-msbuild@v2` to find MSBuild.
- Build per-platform (x64, ARM64) — not AnyCPU.
- Upload `.msix` or `.msixbundle` as artifacts for Store submission.
- Tests can use `dotnet test` (MSBuild not required for test projects).

## Installer Parity (Migrating from Inno Setup / MSI to MSIX)

When converting a traditional installer (Inno Setup, MSI, NSIS) to MSIX, audit the
old installer's `[Code]`/registry sections for behaviors MSIX must replicate declaratively:

- **File-type associations**: Declare via `uap:Extension Category="windows.fileTypeAssociation"`.
  Each file type can specify its own icon (`Logo`). Generate the manifest block from a
  file-type→icon mapping rather than hand-authoring dozens of entries.
- **App Paths**: The installer's `App Paths` registry key (for launching by exe name from
  Run dialog) has no direct MSIX equivalent — the app alias comes from
  `uap3:Extension Category="windows.appExecutionAlias"`.
- **Context menus**: `windows.fileTypeAssociation` covers file/folder right-click; for
  Drive or Background context menus, use a sparse package or `desktop4:` / `desktop5:`
  context menu extensions.
- **PATH / environment**: MSIX apps can't modify the system PATH; use execution aliases
  instead.
- Verify which icon files the old installer references so each file-type association
  points at the right icon.

## VM Testing MSIX Packages

- MSIX must be **signed** or sideloaded with `Add-AppxPackage -AllowUnsigned` (dev only).
- Enable Developer Mode or the sideloading policy on the test VM.
- For unsigned test packages, either self-sign with a cert added to the VM's Trusted
  People store, or use `-AllowUnsigned` on Windows 11+.
- Insider/context-menu features may require `quality: "insider"` and a registered CLSID
  in `product.json` (relevant when building forks like packaged VS Code).

## Store Submission Checklist
1. Reserve app name in [Partner Center](https://partner.microsoft.com/dashboard)
2. Update `Package.appxmanifest` with Partner Center identity values
3. Set `AppxPackageSigningEnabled=false` and `GenerateTemporaryStoreCertificate=True`
4. Configure self-contained packaging + framework dependency stripping
5. Set version to 4-part format (`x.y.z.0`)
6. Build MSIX packages for each target platform
7. Upload to Partner Center → Packages
8. Complete Store listing (description, screenshots, age rating, etc.)
9. Submit for certification
