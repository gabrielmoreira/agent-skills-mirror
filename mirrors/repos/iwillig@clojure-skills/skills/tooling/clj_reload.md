---
name: clj_reload_hot_reloading
description: Hot code reloading library for interactive development.
---

# clj-reload

A Clojure library for hot reloading code during interactive REPL development.

## Overview

clj-reload provides smart code reloading that handles dependency order correctly, preventing errors that can occur with naive reload approaches.

## Core Concepts

**Reloading Code**: Reload updated code in REPL.

```clojure
(require '[clj-reload.core :as reload])

; Reload all modified code
(reload/reload)

; Reload specific namespace
(reload/reload 'my.app.core)
```

**Dependency Tracking**: Understands namespace dependencies.

```clojure
; clj-reload reloads in correct order:
; If ns-a depends on ns-b, ns-b is reloaded first
; This prevents "unresolved symbol" errors
```

## Key Features

- Smart dependency ordering
- Selective reloading
- REPL-friendly
- Low overhead
- No external debugger needed
- Works with component systems

## When to Use

- Interactive development
- REPL-driven development
- Avoiding REPL restarts
- Rapid feedback loop

## When NOT to Use

- Not suitable for all code changes (sometimes restart needed)

## Common Patterns

```clojure
; In REPL:
(require '[clj-reload.core :as reload]
         '[my.app :as app])

; Edit code in editor...

; Reload changes
(reload/reload)

; Continue using updated functions
(app/do-something)

; Reload specific namespace
(reload/reload 'my.app.handler)

; With component system
(require '[com.stuartsierra.component :as component])

(def system (component/start (create-system)))

; Edit code...

; Reload and restart specific component
(reload/reload)
(alter-var-root #'system component/stop)
(alter-var-root #'system (fn [_] (component/start (create-system))))
```

## Related Libraries

- com.stuartsierra/component - Lifecycle management
- com.stuartsierra/component.repl - Component REPL integration

## Resources

- Official Documentation: https://github.com/tonsky/clj-reload
- API Documentation: https://cljdoc.org/d/io.github.tonsky/clj-reload

## Notes

This project uses clj-reload for interactive development and rapid feedback loops.
