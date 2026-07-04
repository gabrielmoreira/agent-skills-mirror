---
name: dt-obs-flutter
license: Apache-2.0
description: >-
  Integrate the Dynatrace Flutter Plugin into a Flutter project — dependency setup, config,
  SDK bootstrap, navigation tracking, and verification.
  Trigger: "add Dynatrace to Flutter", "Flutter plugin setup", "instrument Flutter app",
  "integrate Dynatrace Flutter", "mobile observability Flutter", "dynatrace_flutter_plugin".
  Do NOT use for: querying Flutter RUM data (use dt-obs-frontends), non-Flutter mobile setups,
  or Dynatrace server-side configuration.
---

# Dynatrace Flutter Plugin Integration Skill

## Prerequisites

- Flutter SDK installed and `flutter` available on `PATH`
- An existing Flutter project with a `pubspec.yaml` at the project root
- A Dynatrace environment with access to Experience Vitals (to obtain `applicationId` and `beaconUrl`, or to download `dynatrace.config.yaml`)
- Console access to Experience Vitals → Mobile to configure app settings (Data Privacy, Enablement and Cost Control)
- `dart` CLI available (comes with Flutter SDK; used to run the plugin configuration script)

Work through the steps below in order, interacting with the user at each decision point. Read actual project files before suggesting changes — do not assume the current state.

## Step 1 — Check for existing `dynatrace.config.yaml`

Before asking the user anything, check whether `dynatrace.config.yaml` exists at the project root.

- **File exists:** Read it, show the `applicationId` and `beaconUrl`, and confirm they match the target environment. If correct, run the `userOptIn` check below and skip to Step 3.
- **File does not exist:** Proceed to Step 2.

**`userOptIn` check:**

Inspect the file for `userOptIn` (Android) and `DTXUserOptIn` (iOS).

- **Present on both platforms:** Trust the value as-is. If `true`, flag Step 7a. If `false`, skip Step 7a.
- **Absent from either platform:** Ask the user: **"Do you have User Opt-In mode enabled or disabled?"** (If unsure: Experience Vitals → Mobile → [Your App] → Settings → Data Privacy.) Add the missing value to the relevant platform(s), then flag Step 7a if the final value is `true`.

## Step 2 — Obtain `dynatrace.config.yaml` (only if Step 1 found no file)

Ask the user which approach they prefer:

**Option A — Download from console (recommended):**

1. Open their Dynatrace environment
1. Navigate to: Experience Vitals → New Frontend → Mobile
1. Enter app name and choose **Flutter** as the platform
1. On the **Select capability and settings** screen, configure monitoring features (Crash reporting, user action monitoring, etc.). User action monitoring can be changed later via Experience Vitals → [App] → Settings → Enablement and Cost Control.
1. Download `dynatrace.config.yaml` and place it at the project root (same level as `pubspec.yaml`)

Once the file is in place, apply the `userOptIn` check from Step 1 and flag Step 7a if needed.

**Option B — Provide credentials manually:**
Read `references/config-yaml.md` for the full template and conditional blocks. Collect all required values from the user before creating any files, then apply the `userOptIn` check and flag Step 7a if needed.

## Step 3 — Add the dependency

Read `pubspec.yaml` first.

- **Not present:** Run:
  ```bash
  flutter pub add dynatrace_flutter_plugin
  ```
- **Already under `dependencies`:** No change — proceed to Step 4.
- **Under `dev_dependencies`:** Remove it from `dev_dependencies`, then run `flutter pub add dynatrace_flutter_plugin`. The plugin is required at runtime, including in release builds.

## Step 4 — Fetch dependencies

If Step 3 ran `flutter pub add`, dependencies are already fetched — skip this step.

Otherwise run:

```bash
flutter pub get
```

Confirm success before continuing.

## Step 5 — Run the Dynatrace configuration script

```bash
dart run dynatrace_flutter_plugin
```

This reads `dynatrace.config.yaml` and automatically configures Android Gradle and `ios/Runner/Info.plist`. No manual native file edits are needed.

Common mistakes to flag and correct:

- `flutter pub run dynatrace_flutter_plugin` — wrong, use `dart run dynatrace_flutter_plugin`
- Manual edits to `build.gradle` / `build.gradle.kts` or `Info.plist` — not needed

## Step 6 — Bootstrap the SDK in `main.dart`

Read `lib/main.dart`. Replace `runApp(...)` with `Dynatrace().start(...)`:

```dart
import 'package:dynatrace_flutter_plugin/dynatrace_flutter_plugin.dart';
import 'package:flutter/material.dart';

void main() {
  Dynatrace().start(const MyApp());
}
```

- `Dynatrace().start()` calls `runApp` internally — remove any separate `runApp` call
- `WidgetsFlutterBinding.ensureInitialized()` is not required by Dynatrace before `start()`, but keep it if your app needs it for other pre-start initialization (for example, plugin or platform setup)
- Do not `await` `Dynatrace().start()` itself; only use `await` for other app initialization that must complete before calling `start()`

## Step 7 — Add navigation tracking

In the root `MaterialApp` or `CupertinoApp`, add `DynatraceNavigationObserver()` to `navigatorObservers`:

```dart
MaterialApp(
  navigatorObservers: [DynatraceNavigationObserver()],
  ...
)
```

```dart
CupertinoApp(
  navigatorObservers: [DynatraceNavigationObserver()],
  ...
)
```

## Step 7a — Privacy options call (only if `userOptIn: true`)

**Skip this step if `userOptIn` was not set to `true` during Steps 1 or 2.**

Read `references/user-opt-in.md` for the full guidance on `DataCollectionLevel`, `crashReportingOptedIn`, and placement options. Ask the user the questions defined there, then apply the call to the relevant file.

## Step 8 — HTTP instrumentation (if applicable)

Check `pubspec.yaml` for the `http` package dependency. Separately, search the codebase for `import 'dart:io'` and `HttpClient` usages. If either is present, apply instrumentation:

| Package | Instrumentation |
|---|---|
| `http` | `Dynatrace().createHttpClient()` — replace `http.Client()` at the construction site |
| `dart:io HttpClient` | Manual timing via `Dynatrace().createWebRequestTiming(...)` — no drop-in wrapper exists |

`createHttpClient()` accepts an optional `client:` parameter to wrap an existing client instance. Find every `http.Client()` construction site in the project and replace it with `Dynatrace().createHttpClient()`.


If none are present, note it for when network calls are added.

## Step 9 — Post-setup summary

Confirm to the user what is active:

**Enabled by default** (when `userOptIn` is `false` or absent):

- ✅ Crash reporting
- ✅ User action tracking
- ✅ Network monitoring
- ✅ Lifecycle monitoring
- ✅ Auto-start

> When `userOptIn: true`, all data collection — including crash reporting — is gated on the `applyUserPrivacyOptions(...)` call.

**Configured during this setup:**

- Privacy mode: [userOptIn: true — consent call added / opt-out (SDK default)]
- Navigation tracking: [DynatraceNavigationObserver added]
- HTTP instrumentation: [applied / not applicable yet]

## Step 10 — Verification

Read `references/verification.md` and show the user the verification checklist. If no data appears after 5 minutes, work through the troubleshooting steps in that file.

## Reference Files

- `references/config-yaml.md` — Full `dynatrace.config.yaml` template with Grail and userOptIn conditional blocks
- `references/user-opt-in.md` — `applyUserPrivacyOptions` guidance, `DataCollectionLevel` options, placement options
- `references/verification.md` — Post-setup verification checklist and troubleshooting

## External References

- [dynatrace_flutter_plugin on pub.dev](https://pub.dev/packages/dynatrace_flutter_plugin) — package changelog, API docs, and latest version
- [Dynatrace Flutter Installation Docs](https://docs.dynatrace.com/docs/observe/digital-experience/new-rum-experience/mobile-frontends/flutter/id-01-initial-setup) — initial setup docs
