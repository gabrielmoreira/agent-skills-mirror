---
name: godot-export-builds
description: "Configures Godot 4.x export templates, presets, PCK patches, SteamCMD VDF uploads, codesign/notarytool, Android keystores, and OS.has_feature flags. Use when shipping Windows, Linux, macOS, Android, iOS, or Web binaries, or stripping debug symbols. Never ship debug templates, skip Gatekeeper notarization, or commit keystores. Distinct from GdUnit4/PlayGodot test export (game-godot)."
version: 1.0.1
---

## When to Use
- Preparing release builds for Windows, Linux, macOS, Android, iOS, or Web.
- Setting up automated CI/CD pipelines for Godot exports.
- Managing export templates, feature flags, and platform-specific configurations.
- Optimizing build sizes and stripping debug symbols.
- Implementing patching systems (PCK) or SteamPipe uploads.

## Prerequisites
- Godot 4.x installed (engine-accurate procedures apply to 4.7+).
- Export templates installed via Editor → Manage Export Templates → Download.
- Platform-specific SDKs:
  - Android: Android SDK, OpenJDK 17, Debug keystore.
  - iOS: macOS with Xcode, Apple Developer account, Provisioning profile.
  - macOS: Developer ID certificate for codesigning.
- Windows host is primary (PowerShell). Keep Windows path notes when present.

## Procedure

### 1. Basic Export Setup
1. Open Project → Export.
2. Add preset (Windows, Linux, etc.).
3. Configure settings (icon, binary format, etc.).
4. Export Project.

### 2. Command-Line Export (Headless)
Use PowerShell for command-line exports:
```powershell
# Export release build
godot --headless --export-release "Windows Desktop" builds/game.exe

# Export debug build
godot --headless --export-debug "Windows Desktop" builds/game_debug.exe

# PCK only (for patching)
godot --headless --export-pack "Windows Desktop" builds/game.pck
```

### 3. Platform-Specific Settings
- **Windows**: Format `.exe` (single file) or `.pck + .exe`. Icon: `.ico` file. Include: `*.import`, `*.tres`, `*.tscn`.
- **Web**: Export Type: Regular or GDExtension. Thread Support: For SharedArrayBuffer. VRAM Compression: Optimized for size.
- **Android**: Set SDK Path and Keystore in Editor Settings (Export → Android).
- **iOS**: Export creates `.xcodeproj`. Build in Xcode for App Store.
- **macOS**: Codesign: Developer ID certificate. Notarization: Required for distribution. Architecture: Universal (Intel + ARM).

### 4. Feature Flags
Check platform at runtime:
```gdscript
if OS.get_name() == "Windows":
    # Windows-specific code
    pass

if OS.has_feature("web"):
    # Web build
    pass

if OS.has_feature("mobile"):
    # Android or iOS
    pass
```

### 5. Build Optimization
- **Reduce Build Size**: Exclude editor-only files in export preset (e.g., `*.md`, `*.txt`, `docs/*`). Remove unused imports.
- **Strip Debug Symbols**: In export preset options, set Debugging → Debug: Off, Binary Format → Architecture: 64-bit only.
- **VRAM Compression**: Enable ASTC/ETC2 compression in Import settings for Web/Mobile. ALWAYS disable compression for Pixel Art to maintain crisp edges.
  - S3TC/BPTC: Mandatory for Desktop (Forward+). BPTC is superior for Normal Maps and HDR.
  - ETC2: Standard for older Android/iOS devices.
  - ASTC: Modern mobile standard. High quality/size ratio.

### 6. Expert Export Patterns

#### Platform-Specific-Patching (Delta Updates)
Mount external PCK archives to update game content without a full reinstall.
```gdscript
func _load_patch(patch_path: String) -> bool:
    if FileAccess.file_exists(patch_path):
        return ProjectSettings.load_resource_pack(patch_path, true) # true = replace files
    return false
```

#### Steam-Upload-Pipeline (SteamPipe)
Automate distribution to Steam branches.
```powershell
# export_steam_upload.ps1
$SteamCMD = "C:\steamcmd\steamcmd.exe"
& $SteamCMD +login $env:STEAM_USER $env:STEAM_PASS +run_app_build "res://builds/app_build.vdf" +quit
```

#### Universal-Build-Manager (One-Click Export)
Iterate through all export presets to generate a full suite of release binaries.
```gdscript
func export_all():
    var config := ConfigFile.new()
    config.load("res://export_presets.cfg")
    for section in config.get_sections():
        if section.begins_with("preset."):
            var preset_name = config.get_value(section, "name")
            var path = config.get_value(section, "export_path")
            OS.execute(OS.get_executable_path(), ["--headless", "--export-release", preset_name, path])
```

### 7. Available Scripts (Load when implementing corresponding patterns)
- **[export_headless_pipeline.ps1](scripts/export_headless_pipeline.ps1)**: Load before automating multi-platform headless exports.
- **[export_version_sync.gd](scripts/export_version_sync.gd)**: Load to sync Git tags/hashes with 'application/config/version'.
- **[export_post_process_hook.gd](scripts/export_post_process_hook.gd)**: Load when using `EditorExportPlugin` for post-build tasks (Zipping, Manifests).
- **[export_feature_flag_manager.gd](scripts/export_feature_flag_manager.gd)**: Load for runtime behavior swapping via build feature flags.
- **[export_pck_patch_loader.gd](scripts/export_pck_patch_loader.gd)**: Load for runtime patching logic (mounting external PCK archives and DLC).
- **[export_android_signing_env.ps1](scripts/export_android_signing_env.ps1)**: Load for secure environment variable setup for Android release keystores.
- **[export_custom_build_stripper.py](scripts/export_custom_build_stripper.py)**: Load for SCons configuration to strip unused Godot modules.
- **[export_macos_notarize_cmd.ps1](scripts/export_macos_notarize_cmd.ps1)**: Load for macOS code signing and notarization CLI procedure.
- **[export_build_size_report.gd](scripts/export_build_size_report.gd)**: Load to audit resource sizes and optimize build footprints.
- **[export_ci_github_actions.yml](scripts/export_ci_github_actions.yml)**: Load for professional CI/CD workflow for automated multi-platform Godot releases.
- **SteamPipe / SteamCMD**: Use the inline PowerShell in Steam-Upload-Pipeline (`steamcmd` + `+run_app_build` VDF). This folder has no dedicated SteamCMD wrapper file.
- **[export_universal_manager.gd](scripts/export_universal_manager.gd)**: Load to programmatically iterate and export all defined presets in one click.

## Pitfalls

### Platform & Validation
- **NEVER export to production without a 'Smoke Test'** — "It runs in editor" is NOT enough. Web, Mobile, and Console have unique memory/shader constraints.
- **NEVER skip macOS Notarization** — Apple's Gatekeeper will block unsigned apps. Use `notarytool` OR distribute exclusively via Steam/App Store.
- **NEVER use ad-hoc file paths** — `res://` is read-only in builds. Use `user://` for saves and logs, or paths will fail on locked file systems.

### Performance & Size
- **NEVER use 'Debug' templates for release** — Debug binaries are bloated and slow. Always use `--export-release` to strip profiling overhead.
- **NEVER include raw resources in builds** — Check your export filters. If you include `.md`, `.txt`, or `.psd` files, you're wasting player bandwidth and disk space.
- **NEVER ignore VRAM compression** — Large textures in Web/Mobile builds will crash the GPU driver. Enable ASTC/ETC2 compression in Import settings.

### Security
- **NEVER commit keystores or raw passwords to Git** — Use Environment Variables and CI Secrets (`export_android_signing_env.ps1`).
- **NEVER allow debug commands in Production** — Use `OS.has_feature("release")` to purge console/cheats from the final build.
- **NEVER bake shaders on export for Dedicated Servers** — The Shader Baker (Godot 4.5+) is for visual clients. Enabling it for headless servers is wasted build time.

### Godot 4.7+ Specifics
- `EditorSceneFormatImporter` constants moved to **ImportFlags** enum — update importer scripts.
- **Asset Store** replaces Asset Library in editor — document addon acquisition via new store UI.
- **HDR export**: verify viewport HDR settings per platform in export presets.

## Verification
1. **Check Export Output**: Verify the executable or PCK file exists in the specified `export_path`.
   ```powershell
   Test-Path "builds/game.exe"
   ```
2. **Verify Version Sync**: Ensure `application/config/version` in `project.godot` matches the Git tag.
3. **Test Feature Flags**: Run the build and verify that `OS.has_feature("release")` correctly purges debug tools.
4. **Check Build Size**: Use `export_build_size_report.gd` to ensure no raw resources (`.md`, `.txt`, `.psd`) are included.
5. **macOS Notarization**: Run `export_macos_notarize_cmd.ps1` and verify the app passes Gatekeeper checks.

## Related skills
- Master Skill: [godot-master](../godot-master/SKILL.md)
