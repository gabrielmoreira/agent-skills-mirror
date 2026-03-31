---
name: test_check_property_based_testing
description: Property-based testing framework for Clojure.
---

# test.check

A Clojure property-based testing library that generates random test data and verifies properties hold across many cases.

## Overview

test.check allows you to define properties that should hold true and automatically generates test cases to verify them. This approach often finds edge cases that manual tests miss.

## Core Concepts

**Properties**: Define properties that should always be true.

```clojure
(require '[clojure.test.check :as tc]
         '[clojure.test.check.generators :as gen]
         '[clojure.test.check.properties :as prop])

; Property: adding 0 should return the same number
(def add-zero-property
  (prop/for-all [n gen/int]
    (= n (+ n 0))))

; Run the property check
(tc/quick-check 100 add-zero-property)
; => {:result true, :pass-count 100, ...}
```

**Generators**: Create test data.

```clojure
(require '[clojure.test.check.generators :as gen])

; Built-in generators
gen/int                    ; Random integers
gen/string                 ; Random strings
gen/vector                 ; Random vectors
(gen/elements [1 2 3])    ; Choose from list
(gen/choose 0 100)        ; Range of integers

; Composite generators
(gen/let [a gen/int
          b gen/int]
  {:x a :y b})
```

## Key Features

- Random test data generation
- Property definition and checking
- Shrinking (finds minimal failing cases)
- Stateful testing support
- Large number of test runs
- Custom generators
- Timing and performance stats

## When to Use

- Testing mathematical properties
- Verifying invariants
- Testing edge cases
- Validating algorithms
- High confidence in correctness

## When NOT to Use

- Simple unit tests (manual tests fine)
- Testing specific known cases
- Performance-critical tests

## Common Patterns

```clojure
(require '[clojure.test :refer [deftest is]]
         '[clojure.test.check :as tc]
         '[clojure.test.check.generators :as gen]
         '[clojure.test.check.properties :as prop])

; Test sort stability
(def sort-preserves-order
  (prop/for-all [xs (gen/vector gen/int)]
    (let [sorted (sort xs)]
      (every? #(<= (first %) (second %))
              (partition 2 1 sorted)))))

; Test with custom generators
(deftest string-reverse-test
  (let [result (tc/quick-check 100
                 (prop/for-all [s gen/string]
                   (= s (-> s (clojure.string/reverse) (clojure.string/reverse)))))]
    (is (:result result))))

; Complex property
(def list-append-property
  (prop/for-all [xs (gen/vector gen/int)
                 ys (gen/vector gen/int)]
    (= (count (into xs ys))
       (+ (count xs) (count ys)))))
```

## Related Libraries

- com.gfredericks/test.chuck - test.check enhancements
- nubank/matcher-combinators - Better assertions

## Resources

- Official Documentation: https://github.com/clojure/test.check
- API Documentation: https://cljdoc.org/d/org.clojure/test.check

## Notes

This project uses test.check for property-based testing of core functionality.
