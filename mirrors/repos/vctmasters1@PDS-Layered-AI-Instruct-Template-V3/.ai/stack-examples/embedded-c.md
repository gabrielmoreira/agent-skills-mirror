# Stack Example — Embedded C / C++ (Cortex-M, ESP-IDF, Zephyr-style)

> Reference snippet. Copy into a real module's `.ai/instruct.md` and tune.

## Contents

| Section | What's here |
|---|-------------|
| [Code Organization](#code-organization) | Layering: app / drivers / HAL |
| [C / C++ conventions](#c--c-conventions) | Standards, naming, allocation |
| [Concurrency & ISRs](#concurrency--isrs) | ISR discipline and shared state |
| [Build & flash](#build--flash) | Build system, version stamps |
| [Testing](#testing) | Host unit tests + on-target integration |

## Code Organization

- **Three layers, top depends on bottom only**:
  - `app/` — application logic, state machines, business behavior.
  - `drivers/` — chip-specific peripheral drivers (UART, SPI, GPIO, ADC).
  - `hal/` — Hardware Abstraction Layer; the **only** place that touches MCU registers directly.
- `hal/` **never** depends on `app/`. A bidirectional dependency between HAL and app is the #1 sign the layering has rotted — refactor immediately.
- One driver per peripheral, one `.c` + `.h` pair. Public surface lives in the `.h`; everything else is `static`.

## C / C++ conventions

- C: ISO C11 or C17. C++: C++17 (or C++20 if the toolchain supports it cleanly).
- File names `snake_case.c` / `snake_case.h`. Public functions prefix with the module: `uart_init`, `uart_write`, `uart_read`.
- All public functions are documented in the header (one-line purpose + ownership of returned pointers).
- No dynamic allocation on the hot path. `malloc`/`new` are reviewed line-by-line; prefer static pools or stack allocation.
- Global state lives in `static` module-scoped variables — never extern-globals strewn across translation units.

## Concurrency & ISRs

- ISRs do the **minimum**: timestamp + push to a queue + clear flag + exit. Heavy lifting happens in a task.
- Data shared between ISR and task is `volatile` **and** guarded by either a critical section or a lock-free queue. Document which in a one-line comment.
- No blocking calls inside an ISR — ever. The AI must refuse to add one.

## Build & flash

- The build system (CMake / Make / PlatformIO) is committed; per-developer paths live in `*.local.*` overrides (see [.gitignore Decisions](../conventions.md#gitignore-decisions)).
- **Never flash production firmware from a dev machine.** Flashing scripts that target production refuse to run unless `RELEASE=1` is set and the artifact is signed.
- Firmware version is stamped from git: `<semver>+<short-sha>`. Loose binaries without a version banner are not accepted.

## Testing

- Unit-testable code (parsers, state machines, math) is split out of `app/` into pure modules and tested on the host with Unity or Catch2.
- Integration tests run on the actual board via a CI-attached debugger; firmware that has never run on real silicon is not "tested."
