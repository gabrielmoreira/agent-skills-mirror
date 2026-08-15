---
name: game-console-porting-certification
version: 1.0.1
description: "Use when porting a game to consoles (Nintendo Switch, PlayStation, Xbox) and passing first-party certification — the platform-holder requirement categories (Nintendo Lotcheck, Sony TRC, Microsoft XR/XER), suspend/resume and constrained-mode lifecycle, controller-disconnect and user-switch handling, save-data and storage abstraction, age ratings (ESRB/PEGI/CERO/USK), age gates, and the submission/age-rating pipeline. Triggers on certification, cert, TRC, TCR, XR, XER, Lotcheck, age rating, ESRB, PEGI, CERO, suspend resume, constrained mode, controller disconnect, first-party submission, console port. Not for Godot-specific console build setup and controller-first UI (use godot-platform-console), Steam (use steamworks-sdk), or mobile store submission (use mobile-store-integration). Process/checklist only — no NDA console SDK code."
risk: safe
source: opus
date_added: 2026-06-27
---

# Console Porting & Certification

The engine-agnostic **process** of shipping a game on Nintendo Switch, PlayStation, and Xbox: the certification requirement categories every platform holder enforces, the lifecycle/UX contracts you must meet, age ratings, and the submission pipeline — so a port passes cert the first time.

> This skill is **process and checklist** only. Actual console SDKs are under NDA; it contains no proprietary SDK code. Engine-specific wiring lives in the engine skills.

## When to Use

- Planning a **port** to Switch / PlayStation / Xbox and scoping the cert work early.
- Meeting **platform requirement categories**: Nintendo **Lotcheck**, Sony **TRC**, Microsoft **XR/XER**.
- Implementing the **lifecycle contract**: suspend/resume, Xbox **constrained mode**, quick-resume, focus loss.
- Handling **controller disconnect**, user sign-out, and **user/profile switching** mid-session.
- Abstracting **save data / storage** behind the platform's storage + account model.
- Getting **age ratings** (ESRB/PEGI/CERO/USK) and building compliant age gates.
- Running the **submission pipeline** and avoiding the common cert-failure traps.

## Prerequisites

- Registered developer status with the target platform holders (Nintendo, Sony, Microsoft).
- Access to platform-specific dev kits and NDA-protected SDK documentation.
- A game architecture that supports being interrupted, suspended, and resumed at any time.

## Procedure

### 1. Scope Certification Requirements Early

Treat platform requirements as architectural constraints, not end-of-project checklists.

| Platform | Requirement set | Submission gate |
|---|---|---|
| Nintendo Switch | **Lotcheck** (compliance + content) | First-party review before release |
| PlayStation | **TRC** (Technical Requirements Checklist) | Sony cert pass required |
| Xbox | **XR** (Xbox Requirements) / XER | Microsoft cert pass required |

1. Download the latest requirement documents from the platform holder portals (under NDA).
2. Create a tracking matrix mapping each mandatory requirement to your engine's implementation status.
3. Identify architectural requirements (storage, lifecycle, account handling) and schedule them for early development.

### 2. Implement the Lifecycle Contract

Consoles own the process aggressively. Your game must handle OS interruptions gracefully.

- **Suspend / resume**: The OS can suspend the title at any moment (user hits Home, system overlay). On resume, **auto-pause** single-player, restore audio/timers, and never lose unsaved-but-savable progress.
- **Constrained / low-power mode (Xbox)**: The title keeps running with reduced resources (e.g. behind a system dialog). Don't assume full GPU/CPU.
- **Quick Resume (Xbox)**: The game can be restored from a snapshot hours/days later — re-validate network sessions, time-based state, and entitlements on resume.
- **Focus loss**: Any system overlay (store, invites, keyboard) steals focus → auto-pause and stop reading input.

### 3. Handle Input, Accounts, and Storage

- **Controller disconnect**: If the active controller drops mid-game, **pause** and show a reconnect prompt — never keep simulating with phantom input. This is a mandatory requirement on all three platforms.
- **User switch / sign-out**: Handle the active user changing or signing out mid-session per platform rules (often: pause, or return to a safe screen, and re-resolve save data for the new user).
- **Save data via the platform model**: Writes go through the platform's save-data system tied to a **user account**, often with size limits, write-completion guarantees, and "do not power off while saving" indicators. **Abstract storage** behind an interface so PC file I/O assumptions don't leak in. Never write saves to arbitrary paths.
- **Storage removal / full**: Handle removable storage and out-of-space cleanly with user-facing prompts.

### 4. Obtain Age Ratings & Content Compliance

| Region | Body | Notes |
|---|---|---|
| North America | **ESRB** | |
| Europe | **PEGI** | |
| Japan | **CERO** | |
| Germany | **USK** | Stricter content rules |
| Cross-region | **IARC** questionnaire | Feeds many digital storefront ratings |

1. Fill out the IARC questionnaire early to generate cross-region ratings.
2. Ensure game content matches the assigned rating (mismatched content fails cert).
3. Implement required **age gates / parental controls** hooks where the platform mandates them.
4. Verify localized text and legal screens meet regional cert requirements.

### 5. Meet Performance & Stability Bars

- Hold the **target frame rate** the platform requires (and a locked, stable rate generally — Switch especially is unforgiving; budget memory tightly).
- **No crashes, no hangs, no soft-locks** during cert testing — testers will exercise suspend/resume, disconnects, and storage edges deliberately.
- Respect platform UI/UX rules: correct **button-prompt glyphs** per platform, safe-area/title-safe margins, and the platform's confirm/cancel button convention (it differs by region/platform).

### 6. Run the Submission Pipeline

1. Onboard as a registered developer with each platform holder; get dev kits and SDK access (NDA).
2. Architect for cert from day one (lifecycle, storage, accounts, ratings).
3. Internal pass against the requirement checklist **before** submitting.
4. Submit the build + age-rating + metadata; first-party runs cert.
5. Fix any cert failures and resubmit (each cycle costs days/weeks — front-load compliance).
6. Plan **patches** through the same cert process; day-one patches need their own lead time.

## Pitfalls

1. **Treating cert as an end-of-project task**: Storage, lifecycle, and account handling are architectural — retrofitting them late is the top cause of slipped ship dates.
2. **PC file I/O for saves**: Writing to arbitrary paths fails cert. Go through the platform save-data + account API behind an abstraction.
3. **Ignoring suspend/resume**: Not auto-pausing or losing state on resume is an automatic fail.
4. **Phantom input on controller disconnect**: Must pause + prompt reconnect, not keep playing.
5. **Hardcoded button glyphs / wrong confirm button**: Prompts must match the platform (and the region's A/B convention).
6. **Assuming full resources**: Xbox constrained mode and Switch's tight budget break "always full GPU" assumptions.
7. **Rating mismatch**: Shipped content harsher than the assigned rating fails review; start ratings early.
8. **No patch lead time**: Patches re-enter cert; a "quick day-one fix" still needs the cycle.

## Verification

- [ ] Suspend/resume and (Xbox) constrained/quick-resume handled with auto-pause and state restore.
- [ ] Controller disconnect and user sign-out/switch pause and prompt correctly.
- [ ] Saves go through the platform save-data + account model behind a storage abstraction; full/removed storage handled.
- [ ] Target/locked frame rate met; memory within the platform budget (esp. Switch).
- [ ] No crashes/hangs/soft-locks under deliberate interruption testing.
- [ ] Button glyphs and confirm/cancel convention correct per platform/region.
- [ ] Age rating (ESRB/PEGI/CERO/USK, IARC) obtained and content matches it; age gates implemented.
- [ ] Internal pass against the platform's checklist (Lotcheck/TRC/XR) completed before submission.
- [ ] Patch/cert lead time budgeted into the schedule.

## Related skills

- `godot-platform-console` - Godot engine-side console build, controller-first UI, and in-engine services for the port.
- `unreal-engine` / `unity-engine` - Engine-side implementation of the lifecycle, input, and storage hooks this process requires.
- `steamworks-sdk` - PC ownership/online services (parallel platform, different requirements).
- `mobile-store-integration` - Mobile-store submission and services equivalent.

## References

- Platform-holder developer programs and certification documentation (Nintendo Lotcheck, Sony TRC, Microsoft XR/XER) — access under NDA. Consult these directly for specific requirement codes.
- Age-rating bodies: ESRB, PEGI, CERO, USK, and the IARC questionnaire.
