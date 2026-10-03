---
title: C++
category: Language
guides:
- doxygen-cpp
x-claim-provenance:
- claim: C++17 mode is GCC's default from GCC 11 through GCC 15, and C++20 mode is the default since GCC 16; other dialects are selected with -std.
  source: https://gcc.gnu.org/projects/cxx-status.html
  scope: Page read 2026-09.
- claim: Since GCC 5.1, libstdc++ has a new library ABI with new implementations of std::string and std::list, selected by _GLIBCXX_USE_CXX11_ABI, whose default value of 1 activates the new ABI; linker errors about undefined references involving std::__cxx11 or [abi:cxx11] indicate object files compiled with different values of the macro.
  source: https://gcc.gnu.org/onlinedocs/libstdc++/manual/using_dual_abi.html
- claim: Binaries from the MSVC build tools of Visual Studio 2015 and later (v140 through v145) are binary-compatible, provided the linker is at least as recent as the most recent build tools used for any input and the Redistributable is at least as new as the latest build tools used by any component; objects compiled with /GL or linked with /LTCG must use exactly the same build tools for compile and final link.
  source: https://learn.microsoft.com/en-us/cpp/porting/binary-compat-2015-2017
  scope: Page dated 2025-10-29.
---

C++ interface changes are bound by ownership, lifetime, value category, exception guarantee, template constraints, concurrency, serialization, and source/ABI compatibility contracts. The configured language standard, compiler, standard library, build modes, and feature flags decide which library types and language features are available, and a project that does not pin its standard inherits the compiler's default: GCC compiles C++17 by default in versions 11 through 15 and C++20 from version 16, so a compiler upgrade alone can change which rules apply. RAII, value semantics, scoped synchronization, and non-owning views fit where their lifetimes are provable.

Binary compatibility is decided by the toolchain as much as by the source. Since GCC 5.1, libstdc++ has two ABIs for `std::string` and `std::list`, selected by `_GLIBCXX_USE_CXX11_ABI`, and objects compiled with different settings fail to link with undefined references to `std::__cxx11` or `[abi:cxx11]` symbols. MSVC build tools from Visual Studio 2015 onward produce binary-compatible output, but only when the final linker and the redistributable runtime are at least as new as the newest tools that built any input, and objects compiled with whole-program optimization or link-time code generation link only with exactly the same tools. Exported symbols, headers, template instantiations, overload sets, virtual layout, calling conventions, and FFI boundaries are compatibility-sensitive, and an interface hierarchy adds cost where a cohesive value type already expresses the contract.

Control flow, lifecycle, and ownership run through construction, destruction order, ownership transfer, copies and moves, references and captures, iterator invalidation, exception exits, resource cleanup, and callbacks that can outlive state. Undefined behavior, narrowing, overload resolution, argument-dependent lookup, template instantiation, alignment, atomics and memory ordering, static initialization, reflection-like registries, and conditional compilation shape observable behavior. Names and layout are also consumed indirectly, so renaming, moving, changing layout, or altering exception specifications can break:

- downstream includes and generated bindings
- serializers and dynamically discovered names
- binary consumers

Behavioral evidence covers copy and move paths, lifetime edges, iterator invalidation, allocation and exception failures, polymorphic destruction, overload selection, and supported template instantiations. Compile-time constraints and runtime behavior are separate evidence, and each speaks only for the configured compiler, standard-library, feature, sanitizer, architecture, and optimization variants. Performance evidence comes from optimized builds whose results are consumed so the measured work is not optimized away, and an optimization must preserve object lifetime, ABI, exception guarantees, synchronization, freedom from undefined behavior, and ownership, with profiler or compiler evidence read against those invariants.
