---
name: matcher_combinators_test_assertions
description: Assertion library providing better test matchers for Clojure.
---

# matcher-combinators

A library for writing expressive test assertions with detailed mismatch explanations.

## Overview

matcher-combinators provides matchers that make test assertions more readable and generate helpful error messages when assertions fail, making debugging test failures much easier.

## Core Concepts

**Matchers**: Expressive assertion matchers.

```clojure
(require '[matcher-combinators.test])
(require '[matcher-combinators.matchers :as m])

; Simple matchers
(is (match? {:name "Alice" :age 30} actual-user))

; Partial matching
(is (match? {:name "Alice"} actual-user))  ; Only checks :name

; Collection matchers
(is (match? (m/contains [1 2 3]) (vec actual-numbers)))

; Optional keys
(is (match? {:name "Alice" :email (m/missing)} actual-user))
```

**Mismatch Reporting**: Clear error messages.

```clojure
; When match fails, shows:
; Expected:
; {:name "Alice", :email string?}
;
; Actual:
; {:name "Alice", :email nil}
;
; Mismatch:
; {:email (expected string?, was nil)}
```

## Key Features

- Expressive matcher syntax
- Partial matching
- Collection matchers
- Regex matching
- Custom matchers
- Detailed mismatch output
- Composable matchers

## When to Use

- Writing tests with complex data structures
- Debugging test failures
- Partial object matching
- Collections testing

## When NOT to Use

- Simple equality tests (use is)

## Common Patterns

```clojure
(require '[clojure.test :refer [deftest is]]
         '[matcher-combinators.test]
         '[matcher-combinators.matchers :as m])

; Testing API responses
(deftest create-user-endpoint
  (let [response (create-user {:name "Alice" :email "alice@example.com"})]
    (is (match? {:status 201
                 :body {:id pos-int?
                        :name "Alice"
                        :email "alice@example.com"}}
                response))))

; Testing collections
(deftest process-items
  (let [results (process-items items)]
    (is (match? (m/contains [item1 item2 item3])
                results))))

; Testing nested structures with optional fields
(deftest fetch-user-details
  (let [user (fetch-user 123)]
    (is (match? {:id 123
                 :name string?
                 :email (m/missing)  ; This field should not be present
                 :phone (m/optional string?)}  ; This field is optional
                user))))
```

## Related Libraries

- org.clojure/test.check - Property-based testing
- clojure.test - Built-in test library

## Resources

- Official Documentation: https://github.com/nubank/matcher-combinators
- API Documentation: https://cljdoc.org/d/nubank/matcher-combinators

## Notes

This project uses matcher-combinators for writing expressive test assertions.
