---
title: Flutter
category: Framework and library
x-claim-provenance:
- claim: An element that uses a given widget as its configuration can be updated to use another widget if, and only if, the two widgets have runtimeType and key properties that are operator==.
  source: https://api.flutter.dev/flutter/widgets/Widget/canUpdate.html
- claim: It is an error to call State.setState after the framework calls dispose; the mounted property tells whether the call is legal, and canceling the work that might trigger setState is better practice than merely checking mounted, which wastes CPU cycles.
  source: https://api.flutter.dev/flutter/widgets/State/setState.html
- claim: For mobile apps, debug mode enables assertions and compiles for fast development cycles rather than execution speed, performance can be janky, and emulators and simulators execute only in debug mode; profile mode, used to analyze performance, is disabled on emulators and simulators because their behavior is not representative of real performance; release mode disables assertions and debugging.
  source: https://docs.flutter.dev/testing/build-modes
---

The configured Flutter and Dart versions, supported platforms, renderer and build modes, navigation model, state ownership, localization, and plugin constraints decide which framework APIs apply, and widget, restoration, platform, and generated APIs exist only in the versions that support them.

Widget identity decides which state survives a rebuild. The framework reuses an existing element, and the state attached to it, for a new widget only when the two widgets have the same runtime type and equal keys, so a missing or unstable key can move state, focus, or scroll position to the wrong item. State, controllers, focus nodes, animations, subscriptions, and asynchronous work each belong to a widget, route, application, or external owner whose lifecycle matches their use. Calling `setState` after the framework has disposed a `State` is an error, and canceling in `dispose` the work that would call it is sounder than checking `mounted` before each call, which leaves that work running.

Behavior runs through widget identity and keys, build and layout phases, inherited dependencies, route transitions, restoration, frame callbacks, app lifecycle, disposal, and async completions after unmount. Code is also referenced indirectly, through:

- generated plugin registration, platform channels, and native project files
- assets, fonts, and localization output
- routes, deep links, serializers, and code generation
- conditional platform implementations

Characteristic failures involve rebuild scope, constraints, scroll ownership, semantics, focus order, gestures, text scaling, platform adaptation, and errors whose timing crosses Dart and native boundaries.

Evidence scope can be unit, widget, integration, emulator, or physical device depending on the framework or platform boundary, and a widget test does not prove plugin or operating-system behavior. Frames, clocks, animations, gestures, navigation, app lifecycle, platform messages, text scale, locale, viewport, and teardown make results nondeterministic, and asynchronous work that completes after disposal is where updates to disposed state surface. Debug builds keep assertions and are compiled for fast iteration rather than speed, and mobile emulators and simulators run only debug builds, so performance evidence comes from profile or release builds on representative targets, which for mobile means physical devices, measured with the project's configured tracing tools, and an optimization must preserve semantics, lifecycle, responsiveness, startup, and generated or native integration.
