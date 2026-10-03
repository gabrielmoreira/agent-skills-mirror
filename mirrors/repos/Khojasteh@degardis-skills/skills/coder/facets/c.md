---
title: C
category: Language
x-claim-provenance:
- claim: GCC's -fstrict-aliasing lets the compiler assume the strictest aliasing rules of the language being compiled and is enabled at -O2, -O3, and -Os.
  source: https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html
- claim: GCC's -fdelete-null-pointer-checks is enabled by default on most targets (completely disabled on AVR and MSP430) and lets dataflow analyses eliminate a null check on a pointer that has already been dereferenced.
  source: https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html
- claim: The value of errno is defined only after a call to a function explicitly stated to set it, no function sets errno to 0, and errno should be examined only when a function's return value indicates it is valid.
  source: https://pubs.opengroup.org/onlinepubs/9799919799/functions/errno.html
  scope: POSIX.1-2024.
---

Interface changes in C are bound by contracts for pointer ownership, object lifetime, buffer sizes, integer ranges, error reporting, callback lifetime, thread safety, allocation and cleanup, linkage, and source or binary compatibility. The language standard, compilers, architectures, optimization modes, and conditional configurations in use are established from project evidence, and library, atomic, and diagnostic facilities exist only where those configured targets provide them.

Undefined, unspecified, and implementation-defined behavior are separate risks, and undefined behavior is the one an optimizer acts on. GCC assumes the language's strictest aliasing rules from `-O2`, so reading an object through a pointer of an incompatible type can behave differently in a debug build and an optimized one, and on most targets it treats a pointer that has already been dereferenced as non-null and removes a later null check. A program that works at one optimization level has therefore not shown that it is free of undefined behavior. Compiler or sanitizer output identifies evidence to investigate; it does not replace a concrete path through the program.

Error reporting has conventions of its own. Under POSIX, `errno` is meaningful only after a call documented to set it, no function resets it to zero, and it is examined only when the function's return value says it is valid, so reading it without that signal can report a stale error from an earlier call. Control flow, lifecycle, and ownership run through pointer provenance, ownership transfer, aliasing, lifetime, bounds, initialization, integer conversions, allocation failures, partial construction, and cleanup on every exit.

Exported symbols, headers, calling conventions, struct layout, dynamically loaded names, and foreign interfaces are compatibility-sensitive. Explicitly sized or size types, `const`, internal linkage, and a single visible cleanup discipline make those contracts easier to keep where they fit. The following are observable state as well:

- macros and conditional compilation
- packing and alignment
- callback registrations, signals, and `errno`
- volatile device access, atomics, and synchronization
- linker visibility and generated or textual registrations

Behavioral evidence covers allocation and I/O failures, ownership transfer, buffer edges, integer limits, aliasing, callbacks, error codes, signals, cleanup, and ABI-visible layout. Runtime evidence speaks only for the compiler, architecture, standard, sanitizer, and optimization variants established as supported, and one debug build establishes neither safety nor memory ordering. Performance evidence comes from optimized code whose results are observed, measured with the project's profilers and compiler reports, and an optimization must preserve lifetime, alignment, error propagation, ABI, synchronization, and freedom from undefined behavior.
