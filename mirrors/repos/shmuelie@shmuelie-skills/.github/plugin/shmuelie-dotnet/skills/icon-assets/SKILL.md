---
name: icon-assets
description: Application and NuGet package icon creation — MSIX visual assets, NuGet PackageIcon, favicons, design style guidelines, and SVG-to-PNG generation
---

When creating icons, logos, or visual assets for applications or packages, apply this domain knowledge.

# Icon & Visual Asset Creation — Domain Knowledge

## Source Format Convention
- **SVG is the master format** — keep a single SVG source and generate all PNGs/ICOs from it.
- Store SVG in an `assets/` directory at the repo root (e.g., `assets/icon.svg`).
- Generated PNGs go into the project's asset directory (`Assets/`, `Images/`, or `www/`).
- ICO files are generated from the PNG set (multi-size container).

## Design Style Guidelines

### Platform-Appropriate Style
Match the icon style to the target platform:

- **Windows (Fluent Design)**:
  - Design on a **48×48 grid** for visual balance.
  - Rounded corners: 2px radius exterior, 1px interior at 48px size.
  - Monoline, geometric, minimal shapes with optional gradients and depth.
  - **Transparent background** — blends with Windows system theming (light/dark).
  - Test across both light and dark themes in Windows 11.
  - Use Windows accent color or a project-specific accent.

- **Android (Material Design)**:
  - Adaptive icons: foreground layer (108×108dp) + background layer.
  - 72×72dp safe zone — keep key visual within this area.
  - Bold geometric shapes, Material color palette.
  - Provide `mipmap-mdpi` through `mipmap-xxxhdpi` densities.

- **NuGet packages**:
  - Simple, recognizable logo — it appears at very small sizes in package managers.
  - No text in the icon (the package name appears alongside).
  - Good contrast at 32×32.

- **Web favicons**:
  - Must be clear at 16×16.
  - Provide both `.ico` (multi-size: 16, 32, 48) and `.svg` (modern browsers).

### General Design Principles
- Use **simple, centered metaphors** — avoid text, decorative elements, excessive detail.
- Icon must be **legible at the smallest required size** (16×16 for taskbar/favicon).
- **Transparent background** by default unless brand requires a plate.
- Maintain **visual weight consistency** across sizes — don't just scale down; simplify detail for small sizes.
- Color: use **platform accent colors** or a **project-specific accent** consistently.

### Generation Approaches
- **Design tools**: Figma, Inkscape, Adobe Illustrator — create SVG master, export PNGs at required sizes.
- **AI generation**: DALL-E, Midjourney, Stable Diffusion — generate concept image, then trace/recreate as clean SVG.
- **Programmatic**: Code-based SVG generation for simple geometric icons (useful for CI/automation).
- **Conversion tools**:
  - ImageMagick: `magick convert icon.svg -resize 44x44 Square44x44Logo.png`
  - Inkscape CLI: `inkscape icon.svg --export-type=png --export-width=44 --export-filename=Square44x44Logo.png`
  - `icotool` (icoutils): `icotool -c -o app.ico icon-16.png icon-32.png icon-48.png icon-256.png`
  - PowerShell with System.Drawing: for simple PNG resizing without external tools

## MSIX App Icons (Windows)

### Required Assets for Package.appxmanifest
| Asset | Size | Purpose |
|-------|------|---------|
| `Square44x44Logo.png` | 44×44 | App list, taskbar |
| `Square44x44Logo.targetsize-16.png` | 16×16 | Small taskbar |
| `Square44x44Logo.targetsize-24_altform-unplated.png` | 24×24 | Taskbar unplated |
| `Square44x44Logo.targetsize-32_altform-unplated.png` | 32×32 | Taskbar unplated |
| `Square44x44Logo.targetsize-48_altform-unplated.png` | 48×48 | Taskbar unplated |
| `Square44x44Logo.targetsize-256_altform-unplated.png` | 256×256 | Alt+Tab, high DPI |
| `Square150x150Logo.png` | 150×150 | Start menu tile |
| `Wide310x150Logo.png` | 310×150 | Wide Start tile |
| `StoreLogo.png` | 50×50 | Store listing |
| `LockScreenLogo.png` | 24×24 | Lock screen (optional) |

### Naming Conventions
- `targetsize-{N}` — exact pixel size (not scaled by DPI).
- `scale-{N}` — DPI scale factor (100, 125, 150, 200, 400).
- `altform-unplated` — no system-applied background plate (transparent).
- `altform-lightunplated` — unplated variant for light theme.

### Directory Placement
- `Assets/` (modern-meeter convention) or `Images/` (windows-tmux, modern-proxy convention).
- Whichever directory is used, reference it consistently in `Package.appxmanifest`.

### ApplicationIcon (.ico)
```xml
<!-- In .csproj PropertyGroup -->
<ApplicationIcon>Assets\app.ico</ApplicationIcon>

<!-- Include as content -->
<Content Include="Assets\app.ico" CopyToOutputDirectory="PreserveNewest" />
```
- The .ico file should contain 16, 32, 48, and 256px sizes.
- Used for Win32 window icon (title bar, taskbar, Alt+Tab).

### Manifest Wiring
```xml
<!-- Package.appxmanifest VisualElements -->
<uap:VisualElements
    DisplayName="MyApp"
    Square150x150Logo="Assets\Square150x150Logo.png"
    Square44x44Logo="Assets\Square44x44Logo.png"
    Description="My application"
    BackgroundColor="transparent">
    <uap:DefaultTile Wide310x150Logo="Assets\Wide310x150Logo.png" />
</uap:VisualElements>
```

## NuGet Package Icons

### Requirements
- **Format**: PNG or JPG only (SVG not supported by nuget.org).
- **Size**: 64×64 recommended (32×32 minimum). Max file size 1 MB.
- **Transparency**: Supported and recommended for PNG.

### csproj Wiring
```xml
<PropertyGroup>
    <PackageIcon>icon.png</PackageIcon>
</PropertyGroup>
<ItemGroup>
    <None Include="..\..\assets\icon.png" Pack="true" PackagePath="\" />
</ItemGroup>
```
- `PackagePath="\"` places the icon at the package root.
- Use a relative path from the csproj to the shared `assets/` directory.
- Convention: keep a 128×128 PNG for the package (renders well at all display sizes).

### Multiple Projects Sharing One Icon
When a repo has multiple NuGet packages, use a single icon in `assets/` and reference it from each csproj:
```xml
<None Include="$(MSBuildThisFileDirectory)..\..\assets\icon.png" Pack="true" PackagePath="\" />
```

## Web Favicons

### Files
- `favicon.ico` — multi-size ICO (16, 32, 48) for legacy browser support.
- `favicon.svg` — scalable vector for modern browsers.
- Optional: `apple-touch-icon.png` (180×180) for iOS home screen.

### HTML Wiring
```html
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
```

### Build Integration
- Place favicon files in the static assets directory (e.g., `www/`).
- Copy to output during build (gulp `copyStatic` task, or similar).
