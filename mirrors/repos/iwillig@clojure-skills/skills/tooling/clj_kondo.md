---
name: clj_kondo_linter
description: |
  Fast static analysis and linting for Clojure code. Use when linting code, catching 
  errors early, static analysis, code quality checks, pre-commit hooks, or when the 
  user mentions linting, clj-kondo, code quality, style checking, error detection, 
  or static analysis.
---

# clj-kondo

A fast, static analysis tool and linter for Clojure and ClojureScript.

## Overview

clj-kondo detects common errors and style issues in your code without running it. It provides fast feedback on code quality with minimal configuration.

## Core Concepts

**Running clj-kondo**: Lint your code.

```clojure
; In terminal:
; clj-kondo --lint src/

; Output:
; src/my/app.clj:5:1: error: Unresolved symbol: undefined-func
; src/my/app.clj:10:5: warning: Unused binding: x
```

**Configuration**: Customize linting rules.

```clojure
; In .clj-kondo/config.edn:
{:linters
 {:unresolved-symbol {:level :error}
  :unused-binding {:level :warning}
  :missing-docstring {:level :off}}}
```

## Key Features

- Fast, incremental linting
- Unresolved symbol detection
- Unused variable detection
- Code style checking
- Custom configuration
- IDE integration
- Performance optimized

## When to Use

- Development (catch errors early)
- CI/CD pipelines
- Pre-commit hooks
- Code review automation

## When NOT to Use

- Runtime behavior checking (use tests)

## Common Patterns

```clojure
; In bb.edn:
{:tasks
 {:lint
  {:doc "Lint code with clj-kondo"
   :task (shell "clj-kondo --lint src test")}}}

; In Makefile:
; lint:
; 	clj-kondo --lint src test

; Common issues caught:
; 1. Unresolved symbols
(foo bar)  ; Error if foo not defined

; 2. Unused variables
(let [x 1 y 2]
  y)  ; Warning: x is unused

; 3. Wrong arity
(map inc [1 2 3] [4 5 6])  ; Error: map expects 2 args
```

## Related Libraries

- io.github.tonsky/clj-reload - Hot code reloading

## Resources

- Official Documentation: https://github.com/clj-kondo/clj-kondo
- API Documentation: https://cljdoc.org/d/clj-kondo/clj-kondo

## Notes

This project uses clj-kondo for static analysis and style checking. Run with `bb lint`.
