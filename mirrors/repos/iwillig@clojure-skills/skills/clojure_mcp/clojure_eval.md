---
name: clojure-eval
description: |
  Evaluate Clojure expressions in the REPL for instant feedback and validation. 
  Use when testing code, exploring libraries, validating logic, debugging issues, 
  or prototyping solutions. Essential for REPL-driven development, verifying code 
  works before file edits, and discovering functions/namespaces.
---

# Clojure REPL Evaluation

## Quick Start

The `clojure_eval` tool evaluates Clojure code instantly, giving you immediate feedback. This is your primary way to test ideas, validate code, and explore libraries.

```clojure
; Simple evaluation
(+ 1 2 3)
; => 6

; Test a function
(defn greet [name]
  (str "Hello, " name "!"))

(greet "Alice")
; => "Hello, Alice!"

; Multiple expressions evaluated in sequence
(def x 10)
(* x 2)
(+ x 5)
; => 10, 20, 15
```

**Key benefits:**
- **Instant feedback** - Know if code works immediately
- **Safe experimentation** - Test without modifying files
- **Auto-linting** - Syntax errors caught before evaluation
- **Auto-balancing** - Parentheses fixed automatically when possible

## Core Workflows

### Workflow 1: Test Before You Commit to Files

Always validate logic in the REPL before using `clojure_edit` to modify files:

```clojure
; 1. Develop and test in REPL
(defn valid-email? [email]
  (and (string? email)
       (re-matches #".+@.+\..+" email)))

; 2. Test with various inputs
(valid-email? "alice@example.com")  ; => true
(valid-email? "invalid")            ; => false
(valid-email? nil)                  ; => false

; 3. Once validated, use clojure_edit to add to files
; 4. Reload and verify
(require '[my.namespace :reload])
(my.namespace/valid-email? "test@example.com")
```

### Workflow 2: Explore Libraries and Namespaces

Use built-in helper functions to discover what's available:

```clojure
; Find all namespaces
(clj-mcp.repl-tools/list-ns)

; List functions in a namespace
(clj-mcp.repl-tools/list-vars 'clojure.string)

; Get documentation
(clj-mcp.repl-tools/doc-symbol 'map)

; View source code
(clj-mcp.repl-tools/source-symbol 'clojure.string/join)

; Find functions by pattern
(clj-mcp.repl-tools/find-symbols "seq")

; Get completions
(clj-mcp.repl-tools/complete "clojure.string/j")

; Show all available helpers
(clj-mcp.repl-tools/help)
```

**When to use each helper:**
- `list-ns` - "What namespaces are available?"
- `list-vars` - "What functions does this namespace have?"
- `doc-symbol` - "How do I use this function?"
- `source-symbol` - "How is this implemented?"
- `find-symbols` - "What functions match this pattern?"
- `complete` - "I know part of the function name..."

### Workflow 3: Debug with Incremental Testing

Break complex problems into small, testable steps:

```clojure
; Start with sample data
(def users [{:name "Alice" :age 30}
            {:name "Bob" :age 25}
            {:name "Charlie" :age 35}])

; Test each transformation step
(filter #(> (:age %) 26) users)
; => ({:name "Alice" :age 30} {:name "Charlie" :age 35})

(map :name (filter #(> (:age %) 26) users))
; => ("Alice" "Charlie")

(clojure.string/join ", " (map :name (filter #(> (:age %) 26) users)))
; => "Alice, Charlie"
```

Each step is validated before adding the next transformation.

### Workflow 4: Reload After File Changes

After modifying files with `clojure_edit`, always reload and test:

```clojure
; Reload the namespace to pick up file changes
(require '[my.app.core :reload])

; Test the updated function
(my.app.core/my-new-function "test input")

; If there's an error, debug in the REPL
(my.app.core/helper-function "debug this")
```

**Important:** The `:reload` flag is required to force recompilation from disk.

## When to Use Each Approach

### Use `clojure_eval` When:
- Testing if code works before committing to files
- Exploring libraries and discovering functions
- Debugging issues with small test cases
- Validating assumptions about data
- Prototyping solutions quickly
- Learning how functions behave

### Use `clojure_edit` When:
- You've validated code works in the REPL
- Making permanent changes to source files
- Adding new functions or modifying existing ones
- Code is ready to be part of the codebase

### Combined Workflow:
1. **Explore** with `clojure_eval` and helper functions
2. **Prototype** solution in REPL
3. **Validate** it works with test cases
4. **Edit files** with `clojure_edit`
5. **Reload and verify** with `clojure_eval`

## Best Practices

**Do:**
- Test small expressions incrementally
- Validate each step before adding complexity
- Use helper functions to explore before coding
- Reload namespaces after file changes with `:reload`
- Test edge cases (nil, empty collections, invalid inputs)
- Keep experiments focused and small

**Don't:**
- Skip validation - always test before committing to files
- Build complex logic all at once without testing steps
- Assume cached definitions match file contents - reload first
- Use REPL for long-running operations (use files/tests instead)
- Forget to test error cases

## Common Issues

### Issue: "Undefined symbol or namespace"

```clojure
; Problem
(clojure.string/upper-case "hello")
; => Error: Could not resolve symbol: clojure.string/upper-case

; Solution: Require the namespace first
(require '[clojure.string :as str])
(str/upper-case "hello")
; => "HELLO"
```

### Issue: "Changes not appearing after file edit"

```clojure
; Problem: Modified file but function still has old behavior

; Solution: Use :reload to force recompilation
(require '[my.namespace :reload])

; Now test the updated function
(my.namespace/my-function)
```

### Issue: "NullPointerException"

```clojure
; Problem: Calling method on nil
(.method nil)

; Solution: Test for nil first or use safe navigation
(when-let [obj (get-object)]
  (.method obj))

; Or provide a default
(-> obj (or {}) :field)
```

## Advanced Topics

For comprehensive documentation on all REPL helper functions, see [REFERENCE.md](REFERENCE.md)

For complex real-world development scenarios and patterns, see [EXAMPLES.md](EXAMPLES.md)

## Summary

`clojure_eval` is your feedback loop for REPL-driven development:

1. **Test before committing** - Validate in REPL, then use `clojure_edit`
2. **Explore intelligently** - Use helper functions to discover
3. **Debug incrementally** - Break problems into small testable steps
4. **Always reload** - Use `:reload` after file changes
5. **Validate everything** - Never skip testing, even simple code

Master the REPL workflow and you'll write better code faster.
