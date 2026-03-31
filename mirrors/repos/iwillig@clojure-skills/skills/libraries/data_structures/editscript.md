---
name: editscript_data_diff_patch
description: Diff and patch library for Clojure data structures.
---

# Editscript

A Clojure library for computing and applying diffs to data structures.

## Overview

Editscript provides efficient algorithms for computing the minimal set of changes (diff) between two data structures, and applying those changes (patch) to transform one structure into another.

## Core Concepts

**Diff**: Compute differences between data structures.

```clojure
(require '[editscript.core :as editscript])

(def v1 {:name "Alice" :age 30 :city "NYC"})
(def v2 {:name "Alice" :age 31 :city "San Francisco"})

; Compute diff
(editscript/diff v1 v2)
; => [[[:age] 30 31]
;     [[:city] "NYC" "San Francisco"]]
```

**Patch**: Apply diff to transform data.

```clojure
(def changes [[[:age] 30 31]])
(editscript/patch v1 changes)
; => {:name "Alice" :age 31 :city "NYC"}
```

## Key Features

- Efficient diff algorithms
- Minimal change sets
- Support for maps, vectors, sets
- Patch application
- Change summary statistics
- Type-aware operations

## When to Use

- Detecting changes in complex data structures
- Synchronizing distributed systems
- Change tracking and audit logs
- Data structure comparison

## When NOT to Use

- Simple value comparison (use =)
- High-frequency diff computation (performance sensitive)

## Common Patterns

```clojure
(require '[editscript.core :as editscript])

; Track changes to a record
(defn update-user-with-tracking [user-id old-user new-user]
  (let [changes (editscript/diff old-user new-user)]
    {:user-id user-id
     :before old-user
     :after new-user
     :changes changes
     :timestamp (java.time.Instant/now)}))

; Example
(def old-state {:users [{:id 1 :name "Alice" :email "alice@old.com"}
                        {:id 2 :name "Bob" :email "bob@example.com"}]})

(def new-state {:users [{:id 1 :name "Alice" :email "alice@new.com"}
                        {:id 2 :name "Bob" :email "bob@example.com"}]})

(editscript/diff old-state new-state)
; => [[[0 :email] "alice@old.com" "alice@new.com"]]
```

## Related Libraries

- clojure.data/diff - Built-in diff function
- metosin/malli - Data validation

## Resources

- Official Documentation: https://github.com/juji-io/editscript
- API Documentation: https://cljdoc.org/d/juji/editscript

## Notes

This project uses Editscript for computing and tracking changes to data structures.
