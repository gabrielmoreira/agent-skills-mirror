---
name: lentes_functional_lenses
description: Functional lens library for Clojure data structure manipulation.
---

# Lentes

A functional optics library providing lenses, prisms, and other tools for working with data structures in Clojure.

## Overview

Lentes provides lens abstractions for composable data manipulation. Lenses allow you to focus on and update nested values in immutable data structures with less boilerplate.

## Core Concepts

**Lenses**: Focus on nested values.

```clojure
(require '[funcool.lentes :as lenses])

; Define a lens for a nested path
(def user-name-lens (lenses/in [:user :name]))

; Get a value through a lens
(lenses/view user-name-lens {:user {:name "Alice"}})
; => "Alice"

; Update a value through a lens
(lenses/focus-update user-name-lens {:user {:name "Alice"}} str/upper-case)
; => {:user {:name "ALICE"}}
```

**Composition**: Combine lenses for complex paths.

```clojure
(def database-users-lens (lenses/in [:database :users]))
(def first-user-lens (lenses/compose database-users-lens (lenses/nth 0)))
(def user-email-lens (lenses/compose first-user-lens (lenses/in [:email])))

(lenses/view user-email-lens
  {:database {:users [{:name "Alice" :email "alice@example.com"}]}})
; => "alice@example.com"
```

## Key Features

- Lens composition
- Getter, setter, and updater operations
- Prisms for optional values
- Traversals for collections
- Type-safe data access
- Immutable updates

## When to Use

- Working with deeply nested data structures
- Updating multiple levels of maps
- Functional data transformation
- Readable alternative to get-in/assoc-in

## When NOT to Use

- Simple single-level updates (use assoc/get)
- When performance is critical
- Small teams unfamiliar with optics

## Common Patterns

```clojure
(require '[funcool.lentes :as lenses])

; Define frequently used lenses
(def user-profile-lens (lenses/in [:profile]))
(def user-address-lens (lenses/compose user-profile-lens (lenses/in [:address])))
(def user-city-lens (lenses/compose user-address-lens (lenses/in [:city])))

; Use lenses for updates
(def user {:profile {:address {:city "San Francisco" :state "CA"}}})

(lenses/focus-update user-city-lens user str/upper-case)
; => {:profile {:address {:city "SAN FRANCISCO" :state "CA"}}}

; Multiple updates
(-> user
    (lenses/focus-update user-city-lens str/upper-case)
    (lenses/focus-update user-address-lens assoc :zip "94102"))
```

## Related Libraries

- funcool/cuerdas - String manipulation
- clojure.core.logic - Logic programming

## Resources

- Official Documentation: https://github.com/funcool/lentes
- API Documentation: https://cljdoc.org/d/funcool/lentes

## Notes

This project uses Lentes for functional data transformation and nested structure updates.
