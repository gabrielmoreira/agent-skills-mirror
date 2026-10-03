---
title: PHP
category: Language
x-claim-provenance:
- claim: PHP's memory_get_usage reports memory allocated by PHP's memory manager, not the operating system's process-memory figure.
  source: https://www.php.net/memory-get-usage
- claim: Strict typing is enabled per file with declare(strict_types=1) and applies to function calls made from within that file, not to the functions declared in it; by default PHP coerces values to the expected scalar type where possible, while strict mode throws a TypeError for any value that does not match exactly, except an int passed for a float.
  source: https://www.php.net/manual/en/language.types.declarations.php
- claim: From PHP 8.0, a non-strict comparison between a number and a non-numeric string casts the number to a string and compares strings, so 0 == "foo" and 0 == "" changed from true to false, while comparisons with numeric strings are unchanged.
  source: https://www.php.net/manual/en/migration80.incompatible.php
- claim: PHP 8.2 deprecates creating dynamic properties unless the class uses the AllowDynamicProperties attribute; stdClass allows them, and __get and __set are not affected.
  source: https://www.php.net/manual/en/migration82.deprecated.php
---

The configured PHP versions, extensions, error reporting, package-manager platform settings, autoloader, framework lifecycle, deployment SAPIs, and dependency lock decide which syntax and APIs apply, and language, extension, and framework APIs exist only where the supported runtime matrix provides them. Dependency versions and transitive ownership live with the adopted package manager.

Null and missing values, weak or strict type boundaries, numeric and string coercion, equality, errors versus exceptions, resource ownership, serialization, request or worker lifetime, and concurrency assumptions are behavioral contracts, and both the version and the calling file change them. `declare(strict_types=1)` governs the calls made from the file that declares it, not the functions defined there, so the same function coerces an argument for one caller and throws `TypeError` for another. PHP 8.0 changed loose comparison between a number and a non-numeric string to compare them as strings, so `0 == "foo"` and `0 == ""` became false, and PHP 8.2 deprecated creating undeclared properties on objects, except on `stdClass` or a class marked `#[\AllowDynamicProperties]`, leaving `__get` and `__set` unaffected.

Semantics run through dynamic property and method access, magic methods, traits, late static binding, references, copy-on-write arrays, iterators and generators, closures, destructors, error handlers, and shutdown functions. Request, CLI, long-running worker, fiber, and process boundaries decide lifetime, and globals, statics, caches, database handles, output buffers, sessions, and resources can survive longer than the apparent call. Code is also referenced indirectly, through:

- Composer autoload maps and files and class aliases
- container registrations, route or annotation attributes, and reflection
- serializers, ORM metadata, generated proxies, and templates
- opcache or preload configuration and string-based callables

Behavioral evidence covers missing, null, and false distinctions, coercion under the actual strictness boundary, magic lookup, autoloading, serialization, error conversion, generator cleanup, and resource release on failure. Runtime evidence depends on the configured runtime, extensions, SAPI, dependency graph, autoloader, and framework bootstrap across supported versions, and a development server does not establish a production lifecycle contract. Database, session, filesystem, cache, timing, process, and worker state cross cases unless isolated, and repeated requests or jobs are where leaked mutable state or resources surface. A performance result holds only for the deployment SAPI, OPcache, preloading, worker, and bootstrap configuration it reproduces. PHP-managed memory and process memory are separate measurements because extensions may allocate outside PHP's memory manager, and autoload or bootstrap, array copying, serialization, database round trips, and blocking I/O are distinguishable cost sites.
