---
name: depot_dependency_checker
description: Tool for checking outdated dependencies in Clojure projects.
---

# Depot

A tool for detecting outdated dependencies in Clojure projects.

## Overview

Depot checks your dependencies against available versions and reports which ones have newer versions available, helping you keep your project up to date.

## Core Concepts

**Checking Dependencies**: Find outdated dependencies.

```clojure
; In terminal:
; clojure -M:outdated

; Output:
; mvn/version (current) -> (available)
; 
; metosin/malli 0.19.2 -> 0.20.0
; com.stuartsierra/component 1.1.0 -> 1.1.1
```

**Configuration**: Filter and customize checks.

```clojure
; In deps.edn:
; :outdated
; {:extra-deps {olical/depot {:mvn/version "1.8.4"}}}
```

## Key Features

- Detects outdated dependencies
- Multi-version support
- Ignore list configuration
- Pre-release version handling
- Integration with CI/CD
- JSON output format

## When to Use

- Dependency maintenance
- CI/CD pipelines (scheduled checks)
- Security updates
- Feature tracking

## When NOT to Use

- Not a dependency solver (doesn't resolve conflicts)

## Common Patterns

```clojure
; In bb.edn or Makefile:
; Check for outdated dependencies
; bb outdated

; Example workflow:
; 1. Run regularly (scheduled CI job)
; 2. Review available updates
; 3. Update deps.edn
; 4. Run tests
; 5. Commit and merge

; With deps.edn filtering:
; {:outdated {:ignore {metosin/malli "0.20.0"}}}  ; Skip specific versions
```

## Related Libraries

- org.clojure/tools.deps - Dependency management

## Resources

- Official Documentation: https://github.com/olical/depot
- API Documentation: https://cljdoc.org/d/olical/depot

## Notes

This project uses Depot to check for outdated dependencies. Run with `bb outdated`.
