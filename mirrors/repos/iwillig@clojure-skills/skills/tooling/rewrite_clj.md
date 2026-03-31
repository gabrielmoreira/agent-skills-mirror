---
name: rewrite-clj-code-transformation
description: |
  Read, analyze, and rewrite Clojure code while preserving formatting, whitespace, 
  and comments using rewrite-clj. Use when building code formatters, refactoring tools, 
  linters, code analysis tools, automated code modification, or when the user mentions 
  rewrite-clj, code transformation, AST manipulation, preserving formatting, code 
  refactoring, or programmatic code editing.
---

# rewrite-clj - Code Transformation

## Quick Start

rewrite-clj reads and rewrites Clojure code while preserving whitespace, comments, and formatting. It uses a zipper to navigate and transform code.

```clojure
(require '[rewrite-clj.zip :as z])

;; Parse and navigate code
(def zloc (z/of-string "(defn foo [x] (+ x 1))"))

;; Find the function name
(-> zloc z/down z/right z/sexpr)
;; => foo

;; Modify and get result
(-> zloc
    z/down z/right      ; Navigate to 'foo'
    (z/replace 'bar)    ; Rename to 'bar'
    z/root-string)      ; Get modified code
;; => "(defn bar [x] (+ x 1))"
```

**Key benefits:**
- **Preserves formatting** - Whitespace and comments stay intact
- **Zipper navigation** - Powerful tree navigation and editing
- **Round-trip safe** - Parse → Modify → Write preserves structure
- **Node-level control** - Work with abstract syntax tree (AST) nodes
- **Clojure & ClojureScript** - Works in both platforms

## Core Concepts

### Zipper Navigation

rewrite-clj uses zippers (a functional data structure) to navigate and edit code:

```clojure
(require '[rewrite-clj.zip :as z])

(def code "(+ 1 2 3)")
(def zloc (z/of-string code))

;; Navigate down into the list
(z/sexpr zloc)           ;; => (+ 1 2 3)
(z/sexpr (z/down zloc))  ;; => +
(z/sexpr (z/right (z/down zloc)))  ;; => 1

;; Navigate back up
(z/up (z/down zloc))  ;; Back to root
```

**Navigation functions:**
- `down` - Move into first child
- `up` - Move to parent
- `right` - Move to next sibling
- `left` - Move to previous sibling
- `rightmost` - Move to last sibling
- `leftmost` - Move to first sibling

### Nodes vs S-expressions

rewrite-clj distinguishes between **nodes** (AST with formatting) and **s-expressions** (actual Clojure values):

```clojure
;; Get the node (preserves formatting)
(z/node zloc)
;; => #<token: +>

;; Get the s-expression (Clojure value)
(z/sexpr zloc)
;; => +

;; Check node type
(require '[rewrite-clj.node :as n])
(n/token-node? (z/node zloc))  ;; => true
```

### Editing Operations

Modify code while preserving structure:

```clojure
(def zloc (z/of-string "(defn foo [x] x)"))

;; Replace a node
(-> zloc z/down z/right
    (z/replace 'bar)
    z/root-string)
;; => "(defn bar [x] x)"

;; Insert after current position
(-> zloc z/down z/rightmost
    (z/insert-right 'y)
    z/root-string)
;; => "(defn foo [x y] x)"

;; Remove a node
(-> zloc z/down z/rightmost
    z/remove
    z/root-string)
;; => "(defn foo [x])"
```

## Common Workflows

### Workflow 1: Finding and Modifying Functions

```clojure
(require '[rewrite-clj.zip :as z])

(def code "
(defn add [a b]
  (+ a b))

(defn multiply [x y]
  (* x y))
")

;; Find all defn forms
(defn find-defns [zloc]
  (loop [loc zloc
         results []]
    (if (z/end? loc)
      results
      (if (and (z/list? loc)
               (= 'defn (z/sexpr (z/down loc))))
        (recur (z/next loc) (conj results loc))
        (recur (z/next loc) results)))))

(def zloc (z/of-string code))
(def defns (find-defns zloc))

;; Get function names
(map #(-> % z/down z/right z/sexpr) defns)
;; => (add multiply)

;; Rename a function
(defn rename-function [zloc old-name new-name]
  (loop [loc zloc]
    (if (z/end? loc)
      (z/root loc)
      (if (and (z/list? loc)
               (= 'defn (z/sexpr (z/down loc)))
               (= old-name (z/sexpr (z/right (z/down loc)))))
        (recur (-> loc z/down z/right
                   (z/replace new-name)
                   z/up
                   z/next))
        (recur (z/next loc))))))

(z/string (rename-function zloc 'add 'sum))
;; => "(defn sum [a b]\n  (+ a b))\n\n(defn multiply [x y]\n  (* x y))"
```

### Workflow 2: Adding Docstrings

```clojure
(require '[rewrite-clj.zip :as z]
         '[rewrite-clj.node :as n])

(def code "(defn add [a b] (+ a b))")
(def zloc (z/of-string code))

;; Add docstring after function name
(-> zloc
    z/down z/right z/right  ; Navigate to after [a b]
    (z/insert-left (n/string-node "Adds two numbers"))
    (z/insert-left (n/spaces 1))  ; Add space
    z/root-string)
;; => "(defn add \"Adds two numbers\" [a b] (+ a b))"
```

### Workflow 3: Formatting Preservation

```clojure
(def formatted-code "
(defn complex-function
  \"A function with nice formatting\"
  [x y z]
  ;; Important comment
  (let [result (+ x y)]
    (* result z)))
")

(def zloc (z/of-string formatted-code))

;; Rename variable 'result' to 'sum'
(defn rename-binding [zloc old-name new-name]
  (loop [loc zloc]
    (if (z/end? loc)
      loc
      (if (and (z/token? loc)
               (= old-name (z/sexpr loc)))
        (recur (-> loc (z/replace new-name) z/next))
        (recur (z/next loc))))))

(-> zloc
    (rename-binding 'result 'sum)
    z/root-string)
;; Preserves all formatting, comments, and whitespace
;; Only 'result' becomes 'sum'
```

### Workflow 4: Analyzing Code Structure

```clojure
(require '[rewrite-clj.zip :as z])

(def code "
(ns myapp.core
  (:require [clojure.string :as str]
            [clojure.set :as set]))

(defn foo [x] x)
(defn bar [y] y)
")

;; Count function definitions
(defn count-defns [code]
  (loop [loc (z/of-string code)
         count 0]
    (if (z/end? loc)
      count
      (if (and (z/list? loc)
               (= 'defn (try (z/sexpr (z/down loc)) (catch Exception _ nil))))
        (recur (z/next loc) (inc count))
        (recur (z/next loc) count)))))

(count-defns code)  ;; => 2

;; Extract require dependencies
(defn extract-requires [code]
  (let [zloc (z/of-string code)]
    (loop [loc zloc
           requires []]
      (if (z/end? loc)
        requires
        (if (and (z/list? loc)
                 (= :require (try (z/sexpr (z/down loc)) (catch Exception _ nil))))
          (recur (z/next loc)
                 (into requires
                       (map z/sexpr
                            (take-while (complement z/end?)
                                      (iterate z/next (z/right (z/down loc)))))))
          (recur (z/next loc) requires))))))

(extract-requires code)
;; => [[clojure.string :as str] [clojure.set :as set]]
```

### Workflow 5: Safe Node Manipulation

```clojure
(require '[rewrite-clj.zip :as z]
         '[rewrite-clj.node :as n])

(def zloc (z/of-string "(+ 1 2)"))

;; Check node types before manipulation
(defn safe-replace [zloc new-value]
  (when (and zloc (not (z/end? zloc)))
    (if (z/sexpr-able? zloc)
      (z/replace zloc new-value)
      zloc)))

;; Work with different node types
(defn node-type [zloc]
  (let [node (z/node zloc)]
    (cond
      (n/token-node? node) :token
      (n/list-node? node) :list
      (n/vector-node? node) :vector
      (n/map-node? node) :map
      (n/set-node? node) :set
      (n/whitespace-node? node) :whitespace
      (n/comment-node? node) :comment
      :else :other)))

(node-type (z/of-string "42"))        ;; => :token
(node-type (z/of-string "(+ 1 2)"))   ;; => :list
(node-type (z/of-string "[1 2 3]"))   ;; => :vector
```

### Workflow 6: Whitespace and Comment Handling

```clojure
(require '[rewrite-clj.zip :as z])

;; Skip whitespace during navigation
(def code "  (  +   1   2  )  ")
(def zloc (z/of-string code))

;; Regular navigation includes whitespace
(-> zloc z/down z/node)  ;; Might be whitespace node

;; Skip to next s-expression
(-> zloc z/down z/next)  ;; Skips whitespace automatically

;; Preserve comments during edits
(def code-with-comments "
(defn foo
  \"docstring\"
  ;; Important comment
  [x]
  x)
")

(-> (z/of-string code-with-comments)
    z/down z/right
    (z/replace 'bar)  ; Rename function
    z/root-string)
;; Comments and formatting preserved
```

### Workflow 7: Subedit - Working with Subforms

```clojure
(require '[rewrite-clj.zip :as z])

(def code "(let [x 1 y 2] (+ x y))")
(def zloc (z/of-string code))

;; Edit within the let binding vector
(-> zloc
    z/down z/right     ; Navigate to [x 1 y 2]
    z/down z/right z/right  ; Navigate to 'y'
    (z/replace 'z)     ; Rename y to z
    z/up z/up          ; Navigate back up
    z/rightmost        ; Go to body
    z/down z/right z/right  ; Navigate to second 'y' in body
    (z/replace 'z)     ; Rename here too
    z/root-string)
;; => "(let [x 1 z 2] (+ x z))"
```

## When to Use Each Approach

**Use rewrite-clj when:**
- Building code formatters or linters
- Creating refactoring tools
- Automated code generation/modification
- Preserving exact formatting is critical
- Need to modify code programmatically
- Building editor tooling or LSP servers

**Use simple string manipulation when:**
- Simple search-and-replace operations
- No need to preserve formatting
- Working with templates, not existing code
- Performance is critical and precision isn't

**Use clojure.tools.reader when:**
- Only need to read code (not modify)
- Don't need to preserve whitespace
- Working with EDN data

**Don't use rewrite-clj when:**
- Simple `read-string` would suffice
- Don't need round-trip preservation
- Evaluating code (use `eval` instead)

## Best Practices

**Do:**
- Use `z/next` to navigate through all nodes systematically
- Check `z/end?` when looping to avoid infinite loops
- Use `z/sexpr-able?` before calling `z/sexpr`
- Preserve comments and formatting intentionally
- Test with real code samples (edge cases matter)
- Use `z/root-string` or `z/root` to get final result
- Navigate with zipper functions, not manual tree walking

**Don't:**
- Assume all nodes have s-expressions (whitespace/comments don't)
- Modify the zipper after calling `z/root`
- Forget to handle whitespace nodes in custom navigation
- Use string manipulation alongside rewrite-clj
- Ignore the difference between nodes and s-expressions
- Navigate without checking for `nil` or end conditions

## Common Issues

### Issue: "Can't call sexpr on whitespace node"

```clojure
;; Problem: Trying to get sexpr from non-sexpr-able node
(-> (z/of-string "  42")
    z/down
    z/sexpr)  ; Error if down hits whitespace!

;; Solution: Check before calling sexpr
(let [loc (z/down (z/of-string "  42"))]
  (when (z/sexpr-able? loc)
    (z/sexpr loc)))

;; Or skip whitespace automatically
(-> (z/of-string "  42")
    z/down
    z/next  ; Skips whitespace
    z/sexpr)  ;; => 42
```

### Issue: "Lost formatting after modification"

```clojure
;; Problem: Creating nodes without whitespace
(-> (z/of-string "(defn foo [x] x)")
    z/down z/rightmost
    (z/insert-right 'y)  ; No space added!
    z/root-string)
;; => "(defn foo [x]y x)"  ; No space before 'y'

;; Solution: Insert whitespace nodes
(require '[rewrite-clj.node :as n])

(-> (z/of-string "(defn foo [x] x)")
    z/down z/rightmost
    (z/insert-right 'y)
    (z/insert-right (n/spaces 1))  ; Add space
    z/root-string)
;; => "(defn foo [x] y x)"
```

### Issue: "Infinite loop in navigation"

```clojure
;; Problem: No termination condition
(defn find-all-tokens-BAD [zloc]
  (loop [loc zloc
         results []]
    (if (z/token? loc)
      (recur (z/next loc) (conj results (z/sexpr loc)))
      (recur (z/next loc) results))))  ; Never ends!

;; Solution: Check for z/end?
(defn find-all-tokens [zloc]
  (loop [loc zloc
         results []]
    (if (z/end? loc)
      results
      (if (z/token? loc)
        (recur (z/next loc) (conj results (z/sexpr loc)))
        (recur (z/next loc) results)))))
```

### Issue: "Modified code loses original structure"

```clojure
;; Problem: Using z/replace with wrong type
(-> (z/of-string "[1 2 3]")
    z/down
    (z/replace (z/of-string "(+ 1 2)"))  ; Wrong! Created nested zloc
    z/root-string)

;; Solution: Use the value or node directly
(-> (z/of-string "[1 2 3]")
    z/down
    (z/replace '(+ 1 2))  ; Use s-expression
    z/root-string)
;; => "[(+ 1 2) 2 3]"
```

### Issue: "Can't find specific forms"

```clojure
;; Problem: Only checking direct children
(defn find-defn-BAD [code]
  (let [zloc (z/of-string code)]
    (loop [loc (z/down zloc)]
      (when loc
        (if (= 'defn (z/sexpr loc))
          loc
          (recur (z/right loc)))))))  ; Only siblings!

;; Solution: Use z/next for depth-first traversal
(defn find-defn [code]
  (loop [loc (z/of-string code)]
    (cond
      (z/end? loc) nil
      (and (z/list? loc)
           (= 'defn (try (z/sexpr (z/down loc))
                        (catch Exception _ nil))))
      loc
      :else (recur (z/next loc)))))
```

## Advanced Topics

### Custom Predicates for Find Operations

```clojure
(require '[rewrite-clj.zip :as z])

(defn find-first [zloc pred]
  "Find first location matching predicate"
  (loop [loc zloc]
    (cond
      (z/end? loc) nil
      (pred loc) loc
      :else (recur (z/next loc)))))

;; Find first map
(find-first (z/of-string "(def x {:a 1})") z/map?)

;; Find first defn
(defn defn? [loc]
  (and (z/list? loc)
       (= 'defn (try (z/sexpr (z/down loc))
                    (catch Exception _ nil)))))

(find-first (z/of-string "(defn foo [] 1)") defn?)
```

### Batch Modifications

```clojure
(defn modify-all [zloc pred f]
  "Apply function f to all locations matching predicate"
  (loop [loc zloc]
    (if (z/end? loc)
      (z/root loc)
      (if (pred loc)
        (recur (z/next (f loc)))
        (recur (z/next loc))))))

;; Replace all numbers with their double
(defn number-loc? [loc]
  (and (z/sexpr-able? loc)
       (number? (z/sexpr loc))))

(-> (z/of-string "[1 2 (+ 3 4)]")
    (modify-all number-loc? #(z/replace % (* 2 (z/sexpr %))))
    z/string)
;; => "[2 4 (+ 6 8)]"
```

### Working with Macros and Metadata

```clojure
(require '[rewrite-clj.zip :as z])

;; Parse code with metadata
(def code "^:private (defn foo [] 1)")
(def zloc (z/of-string code))

;; Navigate past metadata
(-> zloc z/down)  ; Points to metadata
(-> zloc z/down z/next)  ; Points to defn form

;; Preserve metadata during edits
(-> zloc
    z/down z/next  ; Skip metadata, get to defn
    z/down z/right
    (z/replace 'bar)
    z/root-string)
;; => "^:private (defn bar [] 1)"  ; Metadata preserved
```

## Related Libraries

- rewrite-edn - Higher-level utilities built on rewrite-clj
- clojure-lsp - Uses rewrite-clj for code actions
- cljfmt - Code formatter using rewrite-clj
- clj-kondo - Linter that uses similar parsing

## External Resources

- [Official Documentation](https://cljdoc.org/d/rewrite-clj/rewrite-clj)
- [GitHub Repository](https://github.com/clj-commons/rewrite-clj)
- [User Guide](https://cljdoc.org/d/rewrite-clj/rewrite-clj/1.2.50/doc/user-guide)
- [FAQ](https://cljdoc.org/d/rewrite-clj/rewrite-clj/1.2.50/doc/frequently-asked-questions)

## Summary

rewrite-clj provides powerful code transformation capabilities:

1. **Zipper navigation** - Functional tree navigation and editing
2. **Format preservation** - Maintains whitespace, comments, indentation
3. **Round-trip safe** - Parse → Modify → Write preserves structure
4. **Node-level control** - Work with AST while preserving formatting
5. **Clojure & ClojureScript** - Cross-platform support

Use rewrite-clj when building tools that programmatically modify Clojure code while preserving the developer's formatting and comments. Perfect for linters, formatters, refactoring tools, and code generation.
