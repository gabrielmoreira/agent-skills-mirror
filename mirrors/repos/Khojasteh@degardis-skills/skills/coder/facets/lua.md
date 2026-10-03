---
title: Lua
category: Language
x-claim-provenance:
- claim: Lua performance guidance identifies string creation, table use, closures, and garbage collection as measurable cost domains whose impact depends on the program.
  source: https://www.lua.org/gems/lpg.pdf
- claim: In Lua 5.4 the number type has integer and float subtypes, standard Lua uses 64-bit integers and double-precision floats unless compiled for 32-bit ones, and integer overflow wraps around according to two's complement arithmetic.
  source: https://www.lua.org/manual/5.4/manual.html
- claim: In Lua 5.1 the number type represents real, double-precision floating-point numbers.
  source: https://www.lua.org/manual/5.1/manual.html
- claim: When a table is not a sequence, the length operator can return any of its borders, depending on the table's internal representation; table traversal order is not specified, and a program should not assign to a non-existent field during a traversal, although it may modify existing fields or set them to nil.
  source: https://www.lua.org/manual/5.4/manual.html
---

The configured Lua implementation and version, numeric model, standard libraries, module search path, sandbox, host API, and coroutine scheduler decide which language and library behavior applies, and language, library, and host APIs exist only where the configured implementation exposes them. The numeric model alone differs by version: Lua 5.1 numbers are all double-precision floats, while Lua 5.4 numbers have integer and float subtypes, with 64-bit integers that wrap around on overflow in a standard build, so the same arithmetic can lose precision in one version and wrap in another.

Nil versus absence, table ownership and aliasing, indexing, metatable contracts, multiple returns, error propagation, coroutine ownership, serialization, globals, and host-managed resource lifetime are behavioral contracts, and module and global state needs an explicit owner. Tables make several of these unforgiving. A table with a hole is not a sequence, and `#t` may return any of its borders, depending on how the table was built; traversal order is unspecified, and a traversal must not add new keys, although it may change or clear existing fields. Semantics run through `__index` and `__newindex`, other metamethods, raw access, truthiness, length, iteration mutation, array holes, multiple-value adjustment, closures and upvalues, tail calls, and protected calls.

Lifecycle and ownership run through coroutine yield/resume boundaries, scheduler behavior, host thread restrictions, stack discipline in the C API, registry ownership, and references that can keep host or Lua objects alive. Code is also referenced indirectly, through:

- `require` names, `package.path` and `cpath`, preload entries, and module caches
- globals, debug hooks, and dynamically constructed keys
- serializers and C modules
- registry references, userdata finalizers, and host callbacks

Behavioral evidence covers nil and absent values, metatable fallbacks, table aliasing and mutation during iteration, multiple returns, numeric edges, errors across protected calls, module-cache state, and coroutine completion. Runtime evidence comes from each supported implementation and version through the real embedder, loader, sandbox, and native modules, and a standalone interpreter does not establish embedded behavior. Isolation depends on resetting global and module state between tests, and evidence covers host and Lua cleanup, finalization, stack balance, serialization round trips, and scheduler-specific ordering. A performance result is specific to the stated implementation, version, embedder, and measured side of the host boundary, taken at the representative entry point. Table or string allocation, concatenation, garbage collection, closure creation, and host crossings are cost candidates only where the evidence locates cost, and an optimization must preserve metatable, numeric, error, and ownership semantics.
