---
name: ios-app-intents
description: "Implements App Intents, AppEntity, EntityQuery, AppEnum, and AppShortcutsProvider so Shortcuts, Siri, Spotlight, widgets, and controls can invoke a thin intents target. Use when exposing app actions or entities to those system surfaces. Do not use for HIG layout, 44pt targets, or Dynamic Type (ios-design-guidelines)."
version: 1.0.1
---

# iOS App Intents

## Overview

Expose the smallest useful action and entity surface to the system. Start with the verbs and objects people would actually want outside the app, then implement a narrow App Intents layer that can deep-link or hand off cleanly into the main app when needed.

Treat App Intents as system integration infrastructure, not only as a Shortcuts feature. A good first pass often includes one open-app intent, one action intent, one or two entity types, and a small `AppShortcutsProvider`.

## When to Use

Use this skill when you need to:

- Expose app actions to Shortcuts, Siri, Spotlight, widgets, or iOS controls.
- Define `AppEntity` types so the system can understand or route app content.
- Add `AppShortcutsProvider` entries for discoverable, phrase-driven shortcuts.
- Wire runtime handoff so an intent opens or routes into a specific in-app workflow.
- Power widget configuration or controls from the same entity surface.

Trigger keywords: App Intents, AppEntity, AppShortcutsProvider, EntityQuery, AppEnum, Shortcuts, Siri, Spotlight, widgets, controls, openAppWhenRun, intents target.

## Prerequisites

- A Swift / SwiftUI iOS app project (Xcode 15+ recommended).
- Familiarity with the App Intents framework (`import AppIntents`).
- Apple developer documentation as primary reference:
  - `https://developer.apple.com/documentation/appintents/making-actions-and-discoverable-and-widely-available`
  - `https://developer.apple.com/documentation/appintents/creating-your-first-app-intent`
  - `https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences`
- Use web search to consult current Apple Developer documentation when App Intents APIs or platform behavior may have changed.

### Reference files

Load these from the skill folder as needed:

- `references/first-pass-checklist.md` — load when choosing the first intent and entity surface.
- `references/example-patterns.md` — load when you need concrete example shapes to copy and adapt.
- `references/code-templates.md` — load when writing generalized App Intents code from templates.
- `references/system-surfaces.md` — load when deciding how Shortcuts, Siri, Spotlight, widgets, and other system entry points should consume your intents.

## Procedure

### 1) Start with actions, not screens

1. Identify the 1–3 highest-value actions that should work outside the app UI.
2. Prefer verbs like compose, open, find, filter, continue, inspect, or start.
3. Do not mirror the entire app navigation tree as intents. Every intent must have real user value outside the app.

### 2) Define a small entity surface

1. Add `AppEntity` types only for objects the system needs to understand or route.
2. Keep the entity shape narrower than the app's persistence model. Entities should be small and display-friendly.
3. Add `EntityQuery` (or other query types) only where disambiguation or suggestions are genuinely useful.
4. Use `AppEnum` for fixed app choices such as tabs, modes, or visibility levels before reaching for a full entity type.

### 3) Decide whether the action completes in place or opens the app

1. Use non-opening intents for actions that can complete directly from the system surface.
2. Use `openAppWhenRun` or open-style intents when the user should land in a specific in-app workflow.
3. When the app must react inside the main scene, add one clear runtime handoff path instead of scattering ad hoc routing logic.
4. If the action can work in both modes, consider shipping both an inline version and an open-app version rather than forcing one compromise.

### 4) Make the actions discoverable

1. Add `AppShortcutsProvider` entries for the first set of high-value intents.
2. Choose titles, phrases, and symbols that make sense in Shortcuts, Siri, and Spotlight.
3. Keep shortcut phrases direct and task-oriented. Avoid vague phrases or generic titles.
4. Reuse the same action model for widgets and controls when a widget configuration or intent-driven control already needs the same parameters.

### 5) Keep intent types thin

1. Prefer a dedicated intents target or module for the system-facing layer.
2. Keep intent types thin; business logic should stay in app services or domain models.
3. Prefer one predictable app-intent routing surface in the main app scene or root router.

### 6) Validate the runtime handoff

1. Build the app and confirm the intents target compiles cleanly.
2. Verify the app opens or routes to the expected place when an intent runs.
3. Summarize which actions are now exposed, which entities back them, and how the app handles invocation.

## Examples

Good example families to cover in a first pass:

- Open a destination or editor in the app (open-app intent).
- Perform a lightweight action inline without opening the app (non-opening intent).
- Choose from a fixed enum such as a tab or mode (`AppEnum`).
- Resolve one or more entities through `EntityQuery`.
- Power widget configuration or controls from the same entity surface.

## Pitfalls

- **Exposing every screen or tab as its own intent** without real user value. Each intent must justify itself outside the app.
- **Mirroring the entire model graph as `AppEntity` types.** Keep entities narrow and display-friendly.
- **Hiding runtime handoff in global side effects** with no clear app entry path. Use one predictable routing surface.
- **Adding App Shortcuts with vague phrases or generic titles.** Phrases should be direct and task-oriented.
- **Treating the first App Intents pass as a broad taxonomy project** instead of a small useful release. Ship 1–3 high-value actions first.
- **Putting business logic inside intent types.** Keep intents thin; logic belongs in app services or domain models.
- **Forgetting `AppEnum` for fixed choices.** Use `AppEnum` before reaching for a full entity type when the values are a small fixed set.

## Verification

1. **Compile check:** Build the app target and the intents target. Confirm there are no compile errors.

   ```bash
   xcodebuild -scheme "YourApp" -destination 'platform=iOS Simulator,name=iPhone 15' build
   ```

   Expected: `** BUILD SUCCEEDED **`

2. **Shortcut discovery:** On a simulator or device, open the Shortcuts app and confirm your `AppShortcutsProvider` entries appear under the app's section.

3. **Runtime handoff:** Run an intent from Shortcuts or Siri. Confirm the app either completes the action inline or opens and routes to the expected in-app workflow.

4. **Entity resolution:** If using `EntityQuery`, run an intent that requires entity disambiguation. Confirm the system presents the correct entities and that selecting one routes correctly.

5. **Summary output:** Produce a short summary listing:
   - Which actions are now exposed.
   - Which entities back them.
   - How the app handles invocation (inline vs. open-app, routing path).

## Related skills

- `ios-widgets` — widget configuration powered by App Intents.
- `ios-siri-integration` — Siri phrase tuning and donation patterns.
- `swift-deep-linking` — universal links and deep-link routing into app scenes.
