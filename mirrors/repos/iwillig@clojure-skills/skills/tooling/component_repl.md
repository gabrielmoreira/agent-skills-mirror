---
name: component_repl_lifecycle_management
description: REPL utilities for Component lifecycle management.
---

# component.repl

REPL utilities for managing component lifecycle during interactive development.

## Overview

component.repl provides convenient functions for starting, stopping, and resetting systems in the REPL without needing manual component management.

## Core Concepts

**System Management**: Convenient REPL commands.

```clojure
(require '[com.stuartsierra.component.repl :refer [system reset start stop]])

; Start system
(reset)

; Stop system
(stop)

; Get current system
(system)
```

**Integration with Editor**: Use from your editor.

```clojure
; In Emacs with CIDER:
; C-c C-e runs any Clojure expression
; Use to call (reset) after code changes
```

## Key Features

- Convenient REPL functions
- Automatic system management
- Clean restart capability
- Works with custom systems
- Minimal boilerplate

## When to Use

- Interactive development with components
- Testing component integration
- Rapid development feedback

## When NOT to Use

- Production code

## Common Patterns

```clojure
; In user.clj (loaded at REPL startup):
(require '[com.stuartsierra.component :as component]
         '[com.stuartsierra.component.repl :refer [system reset start stop]])
(require '[my.app.system :refer [create-system]])

(alter-var-root #'system (constantly (create-system)))

; In REPL:
(reset)          ; Restart system
(start)          ; Start system
(stop)           ; Stop system

; Access system
(def db (:database (system)))

; Interact with components
(db/query (:connection db) "SELECT * FROM users")

; Edit code, then reset
(reset)

; Use updated code
```

## Related Libraries

- com.stuartsierra/component - Lifecycle management
- io.github.tonsky/clj-reload - Hot code reloading

## Resources

- Official Documentation: https://github.com/stuartsierra/component/blob/master/src/com/stuartsierra/component/repl.clj
- API Documentation: https://cljdoc.org/d/com.stuartsierra/component

## Notes

This project uses component.repl for interactive component management in development.
