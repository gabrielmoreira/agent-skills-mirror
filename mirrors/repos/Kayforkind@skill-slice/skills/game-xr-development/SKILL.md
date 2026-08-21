---
name: game-xr-development
version: 1.2.1
description: "Use when building VR/AR/XR applications in Godot 4.3+ — OpenXR setup, XROrigin3D/XRCamera3D/XRController3D rigs, session init, controller input actions, hand tracking, passthrough mixed reality, and Meta Quest deployment. Triggers on OpenXR, VR, AR, XR, XROrigin3D, XRController3D, headset, Quest, passthrough, foveated rendering. Not for general 3D rendering (use game-3d-essentials), non-XR input (use game-input-handling), or non-XR platform export (use game-export-pipeline)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# XR Development in Godot

OpenXR-based VR/AR development in Godot 4.3+ — rig setup, session lifecycle, controller and hand input, passthrough mixed reality, and standalone Quest deployment. Covers the full XR layer from project configuration through device deployment.

## When to Use

Activate this skill when the user is doing any of the following:

- Setting up an OpenXR project: XR rig scene structure, session initialization, renderer and vsync settings.
- Reading **controller input** through OpenXR action names, or **hand tracking** with controller fallback.
- Implementing **passthrough** mixed reality, XR-friendly UI (SubViewport on a mesh), or comfort locomotion.
- Deploying standalone to **Meta Quest** (or PCVR via Quest Link / SteamVR).
- Configuring foveated rendering, Application SpaceWarp, or spatial anchors on XR targets.

**Trigger keywords:** OpenXR, VR, AR, XR, XROrigin3D, XRController3D, XRCamera3D, headset, Quest, passthrough, foveated rendering, hand tracking, XR rig, XR session.

## Do Not Use

- **2D or non-XR games** — the XR rig, frame-timing rules, and export constraints don't apply.
- **Unity or Unreal XR work** — use `game-unity-engine` / `game-unreal-engine`.
- **General 3D scenes, lighting, environment** — use `game-3d-essentials`; this skill only covers the XR layer.
- **Non-XR input patterns** — use `game-input-handling`.
- **Non-XR platform export** — use `game-export-pipeline`.

### Per-target caveats to verify

- Meta Quest standalone export requires the **OpenXR Vendors plugin** version matching your Godot version.
- Foveated rendering and Application SpaceWarp are vendor/device-dependent — verify on the actual device.
- Spatial anchors need the vendor plugin's spatial entities extension (Godot 4.6+).
- visionOS export uses the Apple Embedded preset with visionOS SDK target (Godot 4.5+).

## Prerequisites

- **Godot 4.3+** (4.5+ recommended for foveated rendering, Application SpaceWarp, OpenXR Render Models, visionOS support).
- **OpenXR plugin** bundled with Godot (enabled via Project Settings).
- **OpenXR Vendors plugin** for standalone headset targets (Meta, Pico) — version must match your Godot version.
- For Meta Quest standalone: Android build template, JDK 17+, Android SDK API level 29+, arm64 target.
- For PCVR testing: a running OpenXR runtime (Meta Quest Link, SteamVR, or Windows Mixed Reality).
- **Windows host (PowerShell)** is the primary development environment. Use PowerShell for all CLI commands below.

## Procedure

### 1. Enable OpenXR in Project Settings

1. Open **Project Settings → XR → OpenXR → Enabled** → set to `true`.
2. Open **Project Settings → XR → Shaders → Enabled** → set to `true`.
3. For standalone Android headsets, install the **OpenXR Vendors plugin** and enable it under **Plugins**.

### 2. Configure Rendering

1. Use **Forward+** or **Mobile** renderer. Use **Mobile** for standalone Quest; Compatibility works for simple scenes.
2. Set **Project Settings → Display → Window → VSync Mode** to `Disabled` — the XR runtime controls frame timing, not the engine.
3. On Windows PCVR builds (Quest Link / SteamVR), consider the **D3D12 backend** if Vulkan drivers are problematic (Godot 4.5+).

### 3. Set World Scale

Build the world at **1 unit = 1 meter**. XR breaks immersion at wrong scale — player height, grab distances, and locomotion all depend on correct real-world scale.

### 4. Build the Core XR Scene Structure

```
Main (Node3D)
├── XROrigin3D                    ← Player's physical space origin
│   ├── XRCamera3D                ← Head-mounted display
│   ├── XRController3D (left)     ← Left controller
│   │   └── LeftHandModel (MeshInstance3D or hand tracking)
│   ├── XRController3D (right)    ← Right controller
│   │   └── RightHandModel
│   └── (XRBodyTracker via XRServer — optional full body tracking)
├── WorldEnvironment
└── GameWorld (Node3D)
    └── … level geometry
```

### 5. Start the XR Session

**GDScript:**

```gdscript
extends Node3D

func _ready() -> void:
    var xr_interface: XRInterface = XRServer.find_interface("OpenXR")
    if xr_interface and xr_interface.is_initialized():
        get_viewport().use_xr = true
    else:
        push_error("OpenXR not available")
```

**C#:**

```csharp
public partial class XRMain : Node3D
{
    public override void _Ready()
    {
        var xrInterface = XRServer.FindInterface("OpenXR");
        if (xrInterface != null && xrInterface.IsInitialized())
            GetViewport().UseXr = true;
        else
            GD.PushError("OpenXR not available");
    }
}
```

### 6. Read Controller Input

Set the `XRController3D.tracker` to `left_hand` / `right_hand` and read OpenXR action names. **Do not use keyboard-style `Input` actions for XR controllers** — they will not map to OpenXR action sets.

```gdscript
@onready var right: XRController3D = $XROrigin3D/RightController

func _physics_process(_delta: float) -> void:
    if right.is_button_pressed("trigger_click"):
        _fire()
    var stick: Vector2 = right.get_vector2("primary")  # thumbstick
    _move(stick)

func _ready() -> void:
    right.button_pressed.connect(_on_button)  # event-style alternative

func _on_button(action: String) -> void:
    if action == "grip_click":
        _grab()
```

### 7. Add Hand Tracking with Controller Fallback

Query the hand tracker; if absent, fall back to controller transforms so the game works on both input styles.

```gdscript
func _get_hand_transform(hand: String) -> Transform3D:
    var tracker := XRServer.get_tracker("/user/hand_tracker/%s" % hand)
    if tracker:
        return tracker.get_pose("default").transform
    return get_node("XROrigin3D/%sController" % hand.capitalize()).transform
```

### 8. Build XR UI

Screen-space `Control` UI does not work in XR. Instead:

1. Create a `SubViewport` with a `Control` UI tree inside it.
2. Display the `SubViewport`'s texture on a `MeshInstance3D` quad in the world.
3. Forward controller-ray input to the viewport so the player can interact with the UI.

### 9. Configure Passthrough (Mixed Reality)

1. Enable passthrough in the export preset's Meta XR feature flags.
2. Set the environment blend mode to **alpha**.
3. Set the viewport background to **transparent**.

### 10. Deploy to Meta Quest (Standalone)

1. Install the Android build template plus the **OpenXR Vendors plugin** (Meta module).
2. Create an export preset: platform **Android**, architecture **arm64**, API level **29+**, renderer **Mobile**.
3. Enable the Meta XR feature flags you need (hand tracking, passthrough) in the export preset.
4. For passthrough, also set environment blend mode to alpha and a transparent viewport background.

### 11. Advanced Features (Godot 4.5+)

- **Foveated rendering:** Enable via OpenXR Vendors plugin for standalone Quest/Pico targets.
- **Application SpaceWarp:** Evaluate for performance budget on Meta Quest / Pico targets.
- **OpenXR Render Models:** Use for controller visuals instead of bundled meshes where supported.
- **visionOS export:** Use the Apple Embedded preset with visionOS SDK target.

### 12. Spatial Anchors (Godot 4.6+)

Use `XRSpatialAnchor` and the vendor plugin's spatial entities extension.

## Examples

### Comfort Locomotion

Include comfort options to reduce motion sickness:

- **Snap turn** — rotate the player in fixed increments rather than smooth turn.
- **Vignette** — darken screen edges during locomotion to reduce peripheral motion.
- **Teleport** — point-and-click movement with fade transitions.

### PCVR via Quest Link / SteamVR

1. Ensure the OpenXR runtime is active (Quest Link or SteamVR).
2. Run the project from the editor — Godot will detect the active OpenXR runtime.
3. On Windows, if Vulkan drivers are problematic, switch to D3D12 backend (Godot 4.5+).

## Pitfalls

- **VSync left enabled** — if VSync is not disabled, the engine and XR runtime will fight over frame timing, causing stutter and nausea. Always set VSync Mode to `Disabled`.
- **Wrong world scale** — building at non-1:1 meter scale breaks grab distances, player height, and immersion. Verify scale early.
- **Using `Input` actions for XR controllers** — keyboard/mouse `Input` actions do not map to OpenXR action sets. Always use `XRController3D.is_button_pressed()` / `get_vector2()` with OpenXR action names.
- **No hand-tracking fallback** — if hand tracking is unavailable and no controller fallback exists, the player's hands disappear. Always implement the fallback path.
- **Screen-space UI in XR** — `Control` nodes rendered to screen do not appear in the headset. Always use SubViewport-on-mesh.
- **OpenXR Vendors plugin version mismatch** — the plugin version must match your Godot version. A mismatch causes export failures or runtime crashes.
- **Missing transparent background for passthrough** — passthrough requires alpha blend mode and transparent viewport background. Without both, passthrough shows black.
- **Bundled controller meshes** — prefer OpenXR Render Models (Godot 4.5+) over bundled meshes; bundled meshes may not match the player's actual hardware.
- **Foveated rendering / ASW assumed universal** — these are vendor/device-dependent. Verify on the actual target device before relying on them.

## Verification

Run through this checklist before shipping:

- [ ] OpenXR is enabled in Project Settings (XR → OpenXR → Enabled = true)
- [ ] XR shaders are enabled in Project Settings (XR → Shaders → Enabled = true)
- [ ] Scene uses `XROrigin3D` → `XRCamera3D` + `XRController3D` hierarchy
- [ ] XR session is started with `get_viewport().use_xr = true` after interface check
- [ ] World is built at 1 unit = 1 meter scale
- [ ] Controller input uses OpenXR action names (`trigger_click`, `grip_click`, `primary`, etc.)
- [ ] Fallback exists for hand tracking → controller tracking
- [ ] UI panels use SubViewport rendered on a 3D mesh (not screen-space)
- [ ] Locomotion includes comfort options (snap turn, vignette)
- [ ] VSync is disabled (XR runtime handles frame timing)
- [ ] Quest export uses Mobile renderer, arm64 architecture, API level 29+
- [ ] On Windows Quest Link / SteamVR builds, D3D12 backend considered if Vulkan drivers are problematic (Godot 4.5+)
- [ ] Foveated rendering enabled via OpenXR Vendors plugin for standalone Quest/Pico targets (Godot 4.5+)
- [ ] Application SpaceWarp evaluated for performance budget on Meta Quest / Pico targets (Godot 4.5+)
- [ ] OpenXR Render Models used for controller visuals instead of bundled meshes where supported (Godot 4.5+)
- [ ] visionOS export uses the Apple Embedded preset with visionOS SDK target (Godot 4.5+)
- [ ] Spatial anchors use `XRSpatialAnchor` and vendor plugin spatial entities extension (Godot 4.6+)
- [ ] Passthrough export preset has alpha blend mode and transparent viewport background

## Related Skills

- **game-3d-essentials** — 3D rendering and environment
- **game-physics-system** — 3D physics interactions (grabbing, throwing)
- **game-input-handling** — non-XR input patterns
- **game-export-pipeline** — platform export beyond the Quest specifics here
- **game-godot-platform-vr** — deeper platform-specific VR guidance
