---
name: scope_capture_repl_debugging
description: REPL debugging tool for capturing and inspecting scope at breakpoints.
---

# scope-capture

A Clojure library for capturing variable scope at specific points and inspecting them interactively in the REPL.

## Overview

scope-capture allows you to insert breakpoints that capture the local scope, then examine those captured values in the REPL without needing a debugger.

## Core Concepts

**Capturing Scope**: Insert capture points in code.

```clojure
(require '[vvvvalvalval.scope-capture :refer [defn-capture capture! letsc]])

; Capture at specific point
(defn-capture add-user [name email]
  (let [user {:name name :email email}]
    user))

; When called, captures local scope for inspection
(add-user "Alice" "alice@example.com")
```

**Inspecting Captured Scope**: View captured variables.

```clojure
(require '[vvvvalvalval.scope-capture :refer [get-captures]])

; View what was captured
(get-captures)
; => [{:locals {:name "Alice", :email "alice@example.com", ...}, ...}]

; Inspect captured locals
@(vvvvalvalval.scope-capture/get-last-capture)
```

## Key Features

- Scope capture at arbitrary points
- REPL-friendly inspection
- No external debugger required
- Low overhead capture
- Useful for debugging complex functions
- Easy integration into code

## When to Use

- Debugging complex function logic
- Investigating test failures
- Understanding intermediate values
- Interactive development

## When NOT to Use

- Production code
- High-performance code
- Long-running processes

## Common Patterns

```clojure
(require '[vvvvalvalval.scope-capture :refer [defn-capture letsc capture!]])

; Debugging a problematic function
(defn-capture process-user-data [users filter-fn transform-fn]
  (let [filtered (filter filter-fn users)
        transformed (map transform-fn filtered)]
    transformed))

; Call it and then inspect
(process-user-data users some-filter some-transform)

; In REPL:
(require '[vvvvalvalval.scope-capture :refer [get-captures]])
(get-captures)
; Examine the captured locals to understand what went wrong

; Or use letsc for inline captures
(letsc [users (fetch-users)]
  (process-users users))

; Then inspect the capture
(deref (vvvvalvalval.scope-capture/get-last-capture))
```

## Related Libraries

- com.stuartsierra/component.repl - REPL utilities

## Resources

- Official Documentation: https://github.com/vvvvalvalval/scope-capture
- API Documentation: https://cljdoc.org/d/vvvvalvalval/scope-capture

## Notes

This project uses scope-capture as a development tool for debugging during REPL-driven development.
