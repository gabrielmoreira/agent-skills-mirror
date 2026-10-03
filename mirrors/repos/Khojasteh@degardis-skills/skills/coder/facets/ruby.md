---
title: Ruby
category: Language
x-claim-provenance:
- claim: Ruby 3.0 separates positional and keyword arguments, so a Hash passed as the last positional argument is no longer implicitly converted to keyword arguments and vice versa; Ruby 2.7 warns about code that relies on the conversion.
  source: https://www.ruby-lang.org/en/news/2019/12/12/separation-of-positional-and-keyword-arguments-in-ruby-3-0/
- claim: In Ruby 3.4, string literals in files without a frozen_string_literal comment emit a deprecation warning when they are mutated, and the warning is shown with -W:deprecated or Warning[:deprecated] = true.
  source: https://www.ruby-lang.org/en/news/2024/12/25/ruby-3-4-0-released/
- claim: In a non-lambda proc, return exits the embracing method and break exits the method the block was given to, each raising LocalJumpError if that method has already returned, and missing arguments become nil, a single array argument is deconstructed, and extra arguments raise no error; in a lambda, return and break exit only the lambda and arguments are checked strictly, raising ArgumentError on a mismatch.
  source: https://docs.ruby-lang.org/en/master/Proc.html
---

The configured Ruby engines and versions, dependency manager and lockfile, load path, autoloading mode, framework lifecycle, encoding, and concurrency model decide which syntax and APIs apply, and language or library behavior exists only where the supported engines and versions provide it. Versions change call semantics outright. Ruby 3.0 stopped converting a trailing positional `Hash` into keyword arguments and back, a conversion Ruby 2.7 only warned about, and Ruby 3.4 warns when a string literal is mutated in a file without a `frozen_string_literal` comment, though only when deprecation warnings are enabled. Dependency ownership, sources, groups, platforms, and runtime constraints stay reviewable only when declared explicitly.

Nil and truthiness, equality and hashing, mutation, exceptions and non-local exits, block ownership, enumeration, resource cleanup, serialization, and thread, fiber, and process boundaries are behavioral contracts. Procs and lambdas differ in both exits and arguments: `return` in a proc exits the method that defined it and `break` exits the method the block was passed to, each raising `LocalJumpError` once that method has returned, and a proc silently tolerates missing or extra arguments, while a lambda exits only itself and checks its arguments like a method. Method lookup runs through singleton classes, ancestors, refinements, `method_missing`, visibility, blocks, procs, and lambdas, keyword arguments, constants, autoloading, and reopened classes or modules.

Lifecycle and ownership run through enumerator laziness, `ensure`, finalizers, thread and fiber locals, scheduler hooks, mutexes, ractors where configured, process forks, request-global state, and caches that outlive their owner. Code is also referenced indirectly, through:

- dynamic sends, callbacks, DSL declarations, and concern inclusion
- serializers, ORM metadata, route names, and dependency injection
- native extensions, generated code, and monkey patches
- string- or symbol-named registrations

Behavioral evidence covers nil and false distinctions, dynamic dispatch, constant and autoload resolution, keyword forwarding, block return behavior, enumeration, exception cleanup, serialization, and callback order. Runtime evidence depends on the configured Ruby engine, dependency bundle, loader or autoloader, native extensions, framework bootstrap, and supported platforms, and a bare interpreter approximates none of them. Global, class, thread or fiber, database, filesystem, timing, and cache state cross cases unless isolated, and concurrency ownership, cleanup, and repeated request or job behavior remain observable boundaries. A performance result is specific to the stated engine, JIT, and garbage-collector configuration, taken at the warmed actual entry point with the project's benchmark and profiling tools and adjusted for profiling overhead. Allocation and collection pressure, duplication, dynamic dispatch, startup or autoloading, and database or I/O round trips are separable cost sites, and an optimization must preserve mutation, enumerator, and cleanup semantics.
