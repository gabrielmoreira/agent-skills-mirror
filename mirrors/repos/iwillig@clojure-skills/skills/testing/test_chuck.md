---
name: test_chuck_test_check_helpers
description: Helper library and enhancements for test.check.
---

# test.chuck

A library providing additional generators and helpers for test.check property-based testing.

## Overview

test.chuck extends test.check with commonly needed generators and testing utilities, making property-based testing easier and more powerful.

## Core Concepts

**Additional Generators**: Common generators not in test.check.

```clojure
(require '[com.gfredericks.test.chuck.generators :as gen'])

; UUID generation
gen'/uuid

; Shuffled vectors
(gen'/shuffled (gen/vector gen/int))

; Partition vectors
(gen'/partition (gen/vector gen/int) gen/int)

; Subsequences
(gen'/subsequences (gen/vector gen/int))
```

**Testing Helpers**: Utilities for property testing.

```clojure
(require '[com.gfredericks.test.chuck.clojure-test :refer [checking]])

; Cleaner syntax for property testing
(checking "vector properties"
  [xs (gen/vector gen/int)]
  (is (= (count xs) (count (reverse xs)))))
```

## Key Features

- UUID and random ID generators
- Collection manipulation generators
- ASCII generators
- Sorted collection generators
- Better error reporting
- Cleaner test syntax
- Documentation generators

## When to Use

- Extended test.check usage
- Building custom generators
- Complex property testing
- Better test organization

## When NOT to Use

- Simple property testing (test.check alone sufficient)

## Common Patterns

```clojure
(require '[clojure.test :refer [deftest is]]
         '[com.gfredericks.test.chuck.clojure-test :refer [checking]]
         '[com.gfredericks.test.chuck.generators :as gen']
         '[clojure.test.check.generators :as gen])

; Using test.chuck syntax
(deftest sorting-properties
  (checking "sort is idempotent"
    [xs (gen/vector gen/int)]
    (is (= (sort xs) (sort (sort xs)))))
  
  (checking "sort increases size"
    [xs (gen/vector gen/int)]
    (is (= (count xs) (count (sort xs))))))

; UUID testing
(deftest uuid-generation
  (checking "generated UUIDs are unique"
    [ids (gen/vector gen'/uuid {:num-elements 100})]
    (is (= 100 (count (set ids))))))
```

## Related Libraries

- org.clojure/test.check - Property-based testing
- nubank/matcher-combinators - Better assertions

## Resources

- Official Documentation: https://github.com/gfredericks/test.chuck
- API Documentation: https://cljdoc.org/d/com.gfredericks/test.chuck

## Notes

This project uses test.chuck for extended property-based testing capabilities.
