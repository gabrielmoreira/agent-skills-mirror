---
title: Python
category: Language
guides:
- python-styles
x-claim-provenance:
- claim: A free-threaded build reports Py_GIL_DISABLED through sysconfig and "free-threading build" in its version string, sys._is_gil_enabled() reports whether the GIL is disabled in the running process, and the GIL may be enabled automatically, with a warning, when importing a C-API extension module not marked as supporting free threading, unless PYTHON_GIL or -X gil overrides it.
  source: https://docs.python.org/3/howto/free-threading-python.html
- claim: Python 3.13 removed the 19 PEP 594 "dead batteries" modules deprecated in Python 3.11, including cgi, cgitb, crypt, imghdr, pipes, and telnetlib.
  source: https://docs.python.org/3/whatsnew/3.13.html
- claim: The pickle module is not secure, and unpickling malicious data can execute arbitrary code; functions and classes are pickled by fully qualified name, so the defining module must be importable and contain the named object when unpickling.
  source: https://docs.python.org/3/library/pickle.html
- claim: The asyncio event loop keeps only weak references to tasks, so a task created with create_task that is not referenced elsewhere may be garbage collected before it is done.
  source: https://docs.python.org/3/library/asyncio-task.html
---

The configured Python versions and implementations, packaging metadata, dependency and lock ownership, import layout, type-checker and lint settings, async framework, and deployment entry points decide which syntax and APIs apply, and language, standard-library, typing, packaging, and framework features exist only where the supported versions provide them. The adopted resolver, indexes, hashes, editable-install policy, and the distinction between project constraints and generated or environment-specific locks are compatibility-sensitive.

Free-threaded execution is a property of the interpreter build and configuration rather than its version. A free-threaded build reports `Py_GIL_DISABLED`, yet it re-enables the GIL, with only a warning, when it imports a C extension not marked as supporting free threading, so every loaded native extension has to support that build and `sys._is_gil_enabled()` is what reports the running state. Upgrades also remove modules outright: Python 3.13 deleted nineteen standard-library modules deprecated since 3.11, among them `cgi`, `crypt`, `imghdr`, `pipes`, and `telnetlib`, and the destination interpreter's authoritative list of removed modules, not the imports a static search happens to reach, decides what an upgrade loses.

Sentinel versus `None`, mutability and aliasing, equality and hashing, exceptions, iterator and context-manager ownership, async cancellation, serialization, and process, thread, and task boundaries are behavioral contracts, and runtime validation belongs at untrusted boundaries. Pickle stores classes and functions by qualified name, so pickled class paths and protocol versions are persisted contracts that a rename or move breaks, and unpickling untrusted data can execute arbitrary code. The event loop holds only weak references to tasks, so a task that nothing else references can be garbage-collected before it finishes. Lifecycle and ownership run through generator and async-generator finalization, context manager exits, task ownership, cancellation and exception groups, thread and process pools, signal handling, import-time side effects, and caches that outlive a request or test.

Attribute lookup runs through descriptors, properties, `__getattr__`, `__getattribute__`, metaclasses, decorators, protocols, dynamic imports, monkey patches, globals, closures, and mutable defaults. Code is also referenced indirectly, so structural changes can break:

- import hooks, namespace packages, entry points, and plugin registries
- dependency injection, serializers, pickles, and ORM metadata
- generated code and annotations inspected at runtime
- string-named callables

Behavioral evidence covers absent, `None`, and false distinctions, dynamic lookup, import and plugin discovery, iterator exhaustion and closure, context cleanup, serialization compatibility, and synchronous versus awaited failure timing. Runtime evidence depends on the project's configured interpreter, environment, dependency graph, import mode, test runner, type checker, and relevant process, thread, and async backends across supported versions. Event loops, clocks, files, environment, signals, subprocesses, and global or module state make results nondeterministic, cancellation and cleanup need explicit evidence, and static typing is not runtime validation. Deprecation and pending-deprecation warnings, optional dependencies, native extensions, and import paths that ordinary runs may not load are evidence surfaces for compatibility-sensitive changes. A performance result is specific to the actual entry point under the resolved interpreter and build and to the project's benchmark harness; a profiler supplies call-structure evidence, and allocation evidence where memory matters, and per-item interpreter work, native-extension work, allocation or copying, startup or import, and I/O are separable cost sites.
