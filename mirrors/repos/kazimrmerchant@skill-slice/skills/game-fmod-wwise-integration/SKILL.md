---
name: game-fmod-wwise-integration
version: 1.0.1
description: "Integrates FMOD Studio or Audiokinetic Wwise: named events, parameters/RTPCs, banks, buses/snapshots/ducking, adaptive music, 3D spatialization, and Unreal/Unity/Godot plugins. Use when wiring FMOD, Wwise, RTPC, soundbanks, EventInstance, or AkAudioEvent. Not for Godot AudioStreamPlayer (godot-audio-systems), ffmpeg transcoding, or TTS. Never run both middlewares in one project or skip per-frame update()/RenderAudio()."
risk: safe
source: opus
date_added: 2026-06-27
---

# FMOD & Wwise Integration

Integrate professional audio middleware (FMOD Studio, Audiokinetic Wwise) into a game engine for event-driven, adaptive, mixed audio. This skill covers the runtime contract between code and authored banks, per-engine integration, and the common failure modes that silently break audio.

## When to Use

- Wiring **event-based audio**: trigger sounds by named events instead of raw clips.
- Driving sound with **parameters / RTPCs** (game state → audio: RPM, health, intensity).
- Managing **banks / soundbanks**: loading, streaming, and memory budgeting.
- Building **adaptive/interactive music** (transitions, stingers, layered stems).
- Setting up **bus routing, snapshots, sidechain ducking**, and runtime mixing.
- **3D spatialization** via middleware (attenuation curves, occlusion, reverb zones).
- Hooking the middleware **build pipeline** into Unreal/Unity/Godot.

## Do Not Use

| If the task is… | Use instead |
|---|---|
| Godot's built-in audio buses / `AudioStreamPlayer` | `godot-audio-systems` |
| Encoding/transcoding/normalizing raw audio files | `ffmpeg-audio-processing` |
| Generating speech / TTS | `text-to-speech` |
| Extracting audio from video | `audio-extractor` |

## FMOD vs Wwise

| | FMOD Studio | Wwise (Audiokinetic) |
|---|---|---|
| Designer tool | FMOD Studio | Wwise Authoring |
| Trigger unit | **Event** (instrument/multi) | **Event** (action list) |
| Game→audio control | **Parameter** (local/global) | **RTPC** + State/Switch |
| Asset container | **.bank** | **SoundBank** (`.bnk`) |
| Licensing | Free under revenue threshold; indie tiers | Free under a per-title sound-count cap; then licensed |
| Engine integrations | Unreal, Unity, Godot (community), C/C++ | Unreal, Unity, Godot (community), C/C++ |
| Best fit | Fast music/adaptive workflows, smaller teams | Large AAA projects, deep state/switch logic |

**HARD RULE: Pick ONE middleware per project.** Never run both — duplicate mixers and bank systems waste memory and create routing chaos.

## Core Mental Model

```
Designer authors in tool ──► builds banks ──► game loads banks
        │                                          │
   Events + Parameters/RTPCs              code triggers Event by name,
   + Buses + Snapshots                    sets Parameter/RTPC each frame
```

**HARD RULE: Code must never reference raw audio files.** Code references **event names** and **parameter names** (ideally via generated GUID headers). The designer owns everything behind that contract.

## Prerequisites

- FMOD Studio or Wwise Authoring installed; major version of the authoring tool must match the runtime integration plugin.
- Target engine plugin installed:
  - **Unreal**: FMOD UE plugin or Wwise UE plugin from the respective launcher/marketplace.
  - **Unity**: FMOD for Unity package or Wwise Unity Integration package.
  - **Godot**: Community GDExtension bindings (FMOD or Wwise).
- Banks built from the authoring tool and placed in the project's streaming-assets / content directory.
- On Windows (primary host, PowerShell), bank paths use backslashes or forward slashes — both work in the C API, but be consistent.

## Procedure

### 1. Initialize the Runtime

#### FMOD (C++ Core/Studio API)

```cpp
FMOD::Studio::System* system = nullptr;
FMOD::Studio::System::create(&system);
system->initialize(512, FMOD_STUDIO_INIT_NORMAL, FMOD_INIT_NORMAL, nullptr);
```

#### Wwise (C++)

```cpp
AkMemSettings memSettings;
AK::MemoryMgr::GetDefaultSettings(memSettings);
AK::MemoryMgr::Init(&memSettings);
// Init StreamMgr + SoundEngine + MusicEngine per Wwise SDK samples...
AK::SoundEngine::Init(nullptr, nullptr);
AK::MusicEngine::Init(nullptr);
```

### 2. Load Banks in the Correct Order

**HARD RULE: Master + Strings (FMOD) / `Init.bnk` (Wwise) must load before any content bank.** Event lookups by name fail otherwise.

#### FMOD

```cpp
FMOD::Studio::Bank* master = nullptr;
system->loadBankFile("Master.bank", FMOD_STUDIO_LOAD_BANK_NORMAL, &master);
system->loadBankFile("Master.strings.bank", FMOD_STUDIO_LOAD_BANK_NORMAL, &master);
// Now load content banks...
system->loadBankFile("SFX.bank", FMOD_STUDIO_LOAD_BANK_NORMAL, &master);
```

#### Wwise

```cpp
AK::SoundEngine::LoadBank("Init.bnk", AK_DEFAULT_POOL_ID);
AK::SoundEngine::LoadBank("Main.bnk", AK_DEFAULT_POOL_ID);
```

### 3. Trigger Events

#### FMOD — One-Shot

```cpp
FMOD::Studio::EventDescription* desc = nullptr;
system->getEvent("event:/SFX/Explosion", &desc);
FMOD::Studio::EventInstance* inst = nullptr;
desc->createInstance(&inst);
inst->setParameterByName("Size", 0.8f);
inst->start();
inst->release();   // auto-frees when the one-shot finishes
```

#### FMOD — Looping (tracked)

```cpp
// Store inst in a member; do NOT release until you stop it.
desc->createInstance(&loopInst);
loopInst->start();
// ...later...
loopInst->stop(FMOD_STUDIO_STOP_ALLOWFADEOUT);
loopInst->release();
```

#### Wwise

```cpp
AkGameObjectID player = 100;
AK::SoundEngine::RegisterGameObj(player);
AK::SoundEngine::PostEvent("Play_Explosion", player);
AK::SoundEngine::SetRTPCValue("Intensity", 75.0f, player);
```

### 4. Drive Parameters / RTPCs Every Frame

**HARD RULE: Always interpolate parameters/RTPCs — never snap.** Snapping causes audible pops and breaks music transition cross-fades.

```cpp
// Ramp intensity toward target so transitions sound musical
intensity = FMath::FInterpTo(intensity, targetIntensity, dt, 1.5f);
musicEvent->setParameterByName("Intensity", intensity);
```

### 5. Call the Per-Frame Update

**HARD RULE: `update()` (FMOD) / `RenderAudio()` (Wwise) must be called exactly once per frame.** This is the #1 integration bug — without it, audio silently never plays or never streams.

```cpp
// FMOD
system->update();

// Wwise
AK::SoundEngine::RenderAudio();
```

### 6. Adaptive Music Pattern

1. Author stems/segments in the tool:
   - **FMOD**: multi-instrument event with transition regions.
   - **Wwise**: Interactive Music hierarchy with segments + transitions.
2. Expose one or two **parameters/RTPCs** (e.g. `Intensity`, `Combat`).
3. From gameplay, smooth those values over time (see step 4).

### 7. Mixing: Buses, Snapshots, Ducking

- Route events to **buses** (Music / SFX / VO / Ambience) so volume/effects are controlled in one place.
- Use **snapshots** (FMOD) / **States** (Wwise) for mix changes: pause menu lowpasses gameplay, cutscene ducks ambience.
- **Sidechain/ducking**: duck music/ambience under VO via a compressor keyed by the VO bus — not by hand-scripting volumes in code.

### 8. Engine Integration

| Engine | FMOD | Wwise |
|---|---|---|
| Unreal | `UFMODAudioComponent`, `UFMODEvent` | `AkComponent`, `AkAudioEvent` |
| Unity | `StudioEventEmitter` | `AkGameObj`, `AkEvent` |
| Godot | Community GDExtension bindings | Community/3rd-party bindings |

**HARD RULE: In Unreal/Unity, prefer the component wrappers for 3D attenuation and auto-positioning.** Drop to the raw API only for non-spatial or globally-managed audio.

### 9. Use Generated ID Headers

**HARD RULE: Event/parameter names must come from generated GUID/ID headers, not loose string literals.** Typos in string literals fail silently.

- **FMOD**: `fmod_studio.h` GUIDs.
- **Wwise**: `Wwise_IDs.h`.

### 10. Bank Compression & Streaming

**HARD RULE: Set per-asset compression.** Mark long tracks as **streaming**, short SFX as **in-memory**. Shipping uncompressed banks blows the memory/size budget.

## Pitfalls

1. **Forgetting the per-frame `update()`/`RenderAudio()`** — audio silently never plays or never streams. #1 integration bug.
2. **Not loading the Strings bank (FMOD) / `Init.bnk` (Wwise) first** — event lookups by name fail.
3. **Leaking `EventInstance`s** — persistent (looping) events must be tracked and explicitly `stop()`+`release()`; only fire-and-forget one-shots should `release()` immediately after `start()`.
4. **Hardcoding event-path strings everywhere** — typos fail silently. Use generated GUID/ID headers.
5. **Snapping parameters/RTPCs** — causes audible pops and breaks music transitions. Always interpolate.
6. **Shipping uncompressed banks** — blows memory/size budget. Set per-asset compression; long music = streaming, short SFX = in-memory.
7. **Mismatched plugin/tool versions** — runtime and authoring tool must match major versions, or banks fail to load.
8. **Registering 3D events on an unpositioned game object** — spatialized sound plays at the origin. Update listener and emitter positions every frame.
9. **Running both FMOD and Wwise in one project** — duplicate mixers and bank systems waste memory and create routing chaos. Pick one.

## Verification

- [ ] `update()` (FMOD) / `RenderAudio()` (Wwise) is called exactly once per frame.
- [ ] Master + Strings (FMOD) / `Init.bnk` (Wwise) loads before any content bank.
- [ ] Looping events are tracked and explicitly stopped/released; one-shots released after start.
- [ ] Event/parameter names come from generated ID headers, not loose string literals.
- [ ] Parameters/RTPCs are interpolated, not snapped.
- [ ] Banks have per-asset compression; long music marked streaming.
- [ ] Listener + 3D emitter positions update each frame.
- [ ] Middleware runtime version matches the authoring-tool major version.
- [ ] Only one middleware (FMOD *or* Wwise) is integrated — never both.

### Quick Smoke-Test Checklist (PowerShell)

```powershell
# Confirm bank files exist in the expected content directory
Get-ChildItem -Path ".\Content\Audio" -Filter *.bank | Select-Object Name, Length
Get-ChildItem -Path ".\Assets\StreamingAssets" -Filter *.bnk | Select-Object Name, Length

# Verify the generated ID header is present and recent
Test-Path ".\Plugins\FMOD\Source\FMODStudio\Public\fmod_studio.h"
Test-Path ".\Assets\Wwise\API\Runtime\Generated\Wwise_IDs.h"
```

## References

This chair keeps the runtime contract, engine wrappers, and adaptive-music pattern in the procedure above. For API surface and bank-load diagnostics, use vendor docs:
- FMOD Studio API and Unreal/Unity integration documentation (fmod.com).
- Audiokinetic Wwise SDK and engine-integration documentation (audiokinetic.com).

## Related Skills

- `godot-audio-systems` — Engine-native audio when you are NOT using middleware.
- `ffmpeg-audio-processing` — Pre-processing source audio before it enters the authoring tool.
- `unreal-engine` / `unity-engine` — Host engines whose plugins surface these APIs.
