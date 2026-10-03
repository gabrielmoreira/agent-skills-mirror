---
title: Android
category: Runtime and platform
x-claim-provenance:
- claim: By default the system destroys the host activity on a configuration change such as rotation, wiping UI state stored in it; a ViewModel survives configuration changes but is destroyed during system-initiated process death, while saved instance state survives both, limited by serialization storage and speed.
  source: https://developer.android.com/topic/libraries/architecture/saving-states
- claim: An app targeting Android 12 or higher must specify the mutability of each PendingIntent it creates and must explicitly declare android:exported on activities, services, and broadcast receivers that use intent filters; without that declaration the app cannot be installed on a device running Android 12 or higher.
  source: https://developer.android.com/about/versions/12/behavior-changes-12
- claim: Local unit tests run on the workstation's JVM against a library of the Android framework APIs whose method bodies are removed, so accessing a framework method throws unless the test mocks it, uses Robolectric shadows, or sets unitTests.returnDefaultValues, whose null or zero returns can let failing tests pass.
  source: https://developer.android.com/training/testing/local-tests
- claim: Debuggable apps incur significant and varied performance degradation and are not useful for measuring timing accurately; the profileable manifest element enables local profiling of release builds.
  source: https://developer.android.com/guide/topics/manifest/profileable-element
---

Android behavior depends on configuration the source does not show. The configured SDK levels, the Android Gradle Plugin, supported devices, and build variants decide which behavior applies, and the target SDK level opts an app into platform behavior changes. An app targeting Android 12 or higher, for example, must declare the mutability of every `PendingIntent` it creates and must declare `android:exported` explicitly on each activity, service, or receiver that has an intent filter; omitting that declaration makes the app uninstallable on devices running Android 12 or higher. Behavior supplied by Android is distinct from behavior supplied by the language, libraries, build variant, OEM, API level, or device state, and each can change independently. Lifecycle-aware collection, retained state, background-work APIs, storage models, and permission flows exist only in the SDK and library versions that provide them.

State and work ownership follow component, process, and configuration-change lifetimes, which are shorter than they look. By default a configuration change such as rotation destroys and recreates the activity, discarding any UI state held in it. A `ViewModel` survives that recreation but is destroyed when the system kills the process, while saved instance state survives both, within the size and speed limits of serialization, so the lifetime a piece of state needs decides where it can live. An `Activity` context held by a longer-lived object therefore outlives its activity and leaks it.

Control flow, lifecycle, and ownership run through activities, fragments, services, receivers, application processes, saved state, configuration changes, main-thread work, coroutine or callback ownership, permissions, storage, navigation, and background limits. Code is also referenced indirectly, so renaming, moving, or deleting it can break:

- manifests, XML resources, and navigation graphs
- intents, exported components, and `PendingIntent` flags
- reflection, dependency injection, and serializers
- generated bindings and platform callbacks

Behavioral evidence covers lifecycle transitions, process death and restoration, rotation or other configuration changes, permission denial and revocation, storage access, deep links, and background execution at the smallest credible Android boundary, whether a local JVM test, an emulator, instrumentation, or a physical device. A local unit test runs on the workstation's JVM against a copy of the framework whose method bodies are removed, so a framework call throws unless a mock, a Robolectric shadow, or a configured default of null or zero stands in for it; a local JVM result is therefore not evidence for a framework or device contract. The main looper, coroutine scheduling, device state, API level, and build variant make results nondeterministic or configuration-specific. Debuggable builds carry significant and varied performance overhead, so performance evidence comes from a release-equivalent profileable build on representative hardware, measured with the project's configured benchmark, trace, and field-vitals tooling, and an optimization must preserve lifecycle, battery, and background-execution behavior.
