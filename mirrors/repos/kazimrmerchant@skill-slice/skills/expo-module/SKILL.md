---
name: expo-module
description: "Builds Expo native modules and views with the Expo Modules API (Swift, Kotlin, TypeScript), including create-expo-module, expo-module.config.json, config plugins, and lifecycle hooks. Use when adding native functionality, native views, or platform support to an Expo module. Not for Expo Router screens, JS-only Expo app features, or React Native Turbo Modules outside the Expo Modules API."
version: 1.0.1
risk: unknown
source: https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-module
source_repo: expo/skills
source_type: official
date_added: 2026-07-01
license: MIT
license_source: https://github.com/expo/skills/blob/main/LICENSE
---

# Writing Expo Modules

Complete reference for building native modules and views using the Expo Modules API. Covers Swift (iOS), Kotlin (Android), and TypeScript.

## When to Use

- Creating a new Expo native module or native view
- Adding native functionality (camera, sensors, system APIs) to an Expo app
- Wrapping platform SDKs for React Native consumption
- Building config plugins that modify native project files
- Adding Android, Apple, or web support to an existing Expo module
- Editing `expo-module.config.json`, config plugins, or lifecycle hooks

## Prerequisites

- Node.js and a package manager (npm, yarn, pnpm, bun)
- Expo SDK installed in the host app
- For iOS: macOS with Xcode and CocoaPods
- For Android: Android Studio with Android SDK
- Windows host (PowerShell) is the primary environment; commands below are PowerShell-compatible

## Procedure

### 1. Choose the scaffold type

- **Local module** — for a single app. Lives in `expo.autolinking.nativeModulesDir` when configured, otherwise in `modules/`.
- **Standalone module** — for reuse, monorepos, or publishing. Has its own package metadata, scripts, and usually an example app.

### 2. Scaffold with `create-expo-module`

Prefer `create-expo-module` over manually creating native module files and directories. The scaffold sets up the expected layout, `expo-module.config.json`, podspec or Gradle files, TypeScript bindings, and the standalone example app flow.

```powershell
npx create-expo-module@latest --platform ios,android --features Function,View --barrel my-module
```

Key flags:
- `--platform` — choose target platforms intentionally instead of relying on defaults
- `--features` — opt-in code samples: `Constant`, `Function`, `AsyncFunction`, `Event`, `View`, `ViewEvent`, `SharedObject`
- `--barrel` — generate an `index.ts` barrel (local modules do not generate one by default)
- `--package-manager` — specify npm, yarn, pnpm, or bun
- `--name` — changes the native class name, **not** the folder name
- Non-interactive mode: pass the positional slug or path explicitly

**Load `references/create-expo-module.md`** before scaffolding or extending a module. It covers local vs standalone modules, all flags, `expo.autolinking.nativeModulesDir`, and `add-platform-support` behavior and quirks.

### 3. Add a platform to an existing module

If an existing Expo module only needs another platform, use `add-platform-support` instead of manually copying native directories:

```powershell
npx create-expo-module add-platform-support --platform android
```

### 4. Replace generated example code with the real implementation

Feature examples are **opt-in**. A newly scaffolded module may be minimal if no features were selected. Replace the generated samples with your real implementation.

### 5. Write the native module definition

**Swift (iOS):**

```swift
import ExpoModulesCore

public class MyModule: Module {
  public func definition() -> ModuleDefinition {
    Name("MyModule")

    Function("hello") { (name: String) -> String in
      return "Hello \(name)!"
    }
  }
}
```

**Kotlin (Android):**

```kotlin
package expo.modules.mymodule

import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

class MyModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("MyModule")

    Function("hello") { name: String ->
      "Hello $name!"
    }
  }
}
```

**TypeScript:**

```typescript
import { requireNativeModule } from "expo";

const MyModule = requireNativeModule("MyModule");

export function hello(name: string): string {
  return MyModule.hello(name);
}
```

**Load `references/native-module.md`** when writing module definitions. It covers the full DSL: `Name`, `Function`, `AsyncFunction`, `Property`, `Constant`, `Events`, the type system, and shared objects.

**Load `references/native-view.md`** when building native view components. It covers `View`, `Prop`, `EventDispatcher`, view lifecycle, and ref-based functions.

**Load `references/lifecycle.md`** when implementing lifecycle hooks: module lifecycle, iOS app/AppDelegate listeners, and Android activity/application listeners.

**Load `references/config-plugin.md`** when building config plugins that modify `Info.plist`, `AndroidManifest.xml`, or read values in native code.

### 6. Configure `expo-module.config.json`

```json
{
  "platforms": ["android", "apple"],
  "apple": {
    "modules": ["MyModule"]
  },
  "android": {
    "modules": ["expo.modules.mymodule.MyModule"]
  }
}
```

iOS uses just the class name; Android uses the fully-qualified class name (package + class).

**Load `references/module-config.md`** when editing `expo-module.config.json`. It covers all fields, file placement, and autolinking behavior.

## Pitfalls

- **iOS vs Android class names in config**: iOS uses just the class name (`MyModule`); Android uses the fully-qualified class name (`expo.modules.mymodule.MyModule`). Mixing these up causes autolinking failures.
- **`--name` does not change the folder name**: `--name` changes the native class name only. In non-interactive local scaffolding, pass the positional slug or path explicitly to control the folder name.
- **No barrel by default for local modules**: Local modules do not generate an `index.ts` barrel by default. Use `--barrel` only if you want one.
- **`ViewEvent` implies `View`**: Selecting `ViewEvent` as a feature will also scaffold view-related code.
- **Feature examples are opt-in**: A newly scaffolded module may be minimal if no features were selected. Do not assume all DSL elements are present after scaffolding.
- **Prefer `add-platform-support` over manual copying**: Manually copying native directories can miss podspec/Gradle wiring. Always use the CLI subcommand.
- **Local vs standalone tooling**: Local modules use the host app's tooling; standalone modules have their own package metadata, scripts, and example app. Do not mix these workflows.
- **Verify against current docs**: Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes. Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.

## Verification

1. Confirm the module is autolinked:

```powershell
npx expo prebuild --clean
```

2. Build for iOS (requires macOS):

```powershell
npx expo run:ios
```

3. Build for Android:

```powershell
npx expo run:android
```

4. Verify the TypeScript binding resolves without errors:

```powershell
npx tsc --noEmit
```

5. Confirm `expo-module.config.json` is valid JSON and lists the correct class names for each platform. Check that the `platforms` array matches the platforms you scaffolded.

## References

```
references/
  create-expo-module.md      Scaffolding and add-platform-support workflow, defaults, and quirks
  native-module.md           Module definition DSL: Name, Function, AsyncFunction, Property, Constant, Events, type system, shared objects
  native-view.md             Native view components: View, Prop, EventDispatcher, view lifecycle, ref-based functions
  lifecycle.md               Lifecycle hooks: module, iOS app/AppDelegate, Android activity/application listeners
  config-plugin.md           Config plugins: modifying Info.plist, AndroidManifest.xml, reading values in native code
  module-config.md           expo-module.config.json fields, file placement, and autolinking behavior
```

Load each reference file only when the task touches its specific topic (see step-by-step guidance in the Procedure above).
