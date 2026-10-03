---
title: Delphi
category: Language
x-claim-provenance:
- claim: Since Delphi 2009 the default string type is UnicodeString, with an affinity for UTF-16, instead of AnsiString in earlier versions; Char and PChar map to WideChar and PWideChar; and assignments between AnsiString and UnicodeString perform type conversions.
  source: https://www.embarcadero.com/images/dm/technical-papers/delphi-in-a-unicode-world-updated.pdf
- claim: From RAD Studio 10.4 (May 2020), Delphi object memory management is unified across mobile, desktop, and server platforms using the classic implementation instead of automatic reference counting of objects on mobile, while ARC remains for strings and interface references on all platforms.
  source: https://blogs.embarcadero.com/rad-studio-10-4-now-available-learn-more/
---

The configured Delphi compiler, target platforms, framework, Unicode model, memory-management model, and conditional symbols decide which language and RTL facilities apply, and APIs exist only where the configured compiler and target RTL support them. Two of these have changed underneath existing code. Since Delphi 2009, `string` means the UTF-16 `UnicodeString` and `Char` the two-byte `WideChar`, where earlier versions used `AnsiString` and `AnsiChar`, and an assignment between the two string families performs a conversion. Since RAD Studio 10.4, objects follow classic memory management on every platform, including the mobile platforms that previously reference-counted them, while strings and interface references remain reference-counted everywhere.

Class and interface ownership, reference counting, record initialization and finalization, exception and cleanup behavior, string and set representation, thread affinity, RTTI, and source or ABI compatibility are behavioral contracts. Form and component ownership is a lifetime model distinct from interface lifetime and manual object lifetime, and each object belongs to exactly one of them. Control flow, lifecycle, and ownership run through constructors, destructors, `try/finally`, interface reference transitions, anonymous-method captures, event-handler ownership, properties, dynamic arrays, strings, records, variants, and partial initialization.

Code is also referenced indirectly, through:

- DFM/FMX resources, published members, and RTTI
- class registration, package exports, and message handlers
- COM interfaces, serializers, and generated bindings
- conditional compilation and unit initialization/finalization order

Moving or changing declarations can expose failures in calling conventions, record packing, set size, managed-field layout, Unicode conversions, UI-thread access, and foreign boundaries.

Behavioral evidence covers ownership transfer, destruction order, interface cycles, exceptions during construction, record copying and finalization, Unicode edges, event lifetime, and UI-thread callbacks. Build and runtime evidence spans each supported compiler, target, and framework configuration whose ABI, memory management, or conditional code differs, and produced exports and resources are evidence where compatibility depends on them. Leak, race, and profiling tools supported by the configured environment supply lifetime, concurrency, and cost evidence, and an optimization must preserve resource lifetime, thread affinity, ABI layout, and initialization order.
