---
name: kaocha_test_runner
description: |
  Full-featured test runner for Clojure with watch mode, coverage, and plugins. 
  Use when running tests, test-driven development (TDD), CI/CD pipelines, coverage 
  reporting, or when the user mentions testing, test runner, kaocha, watch mode, 
  continuous testing, or test automation.
---

# Kaocha

A comprehensive test runner for Clojure with support for multiple test libraries and powerful plugin system.

## Overview

Kaocha is a modern test runner that works with clojure.test, specs, and other testing frameworks. It provides detailed reporting, watch mode, and extensibility through plugins.

## Core Concepts

**Running Tests**: Execute tests with Kaocha.

```clojure
(require '[kaocha.runner :as runner])

; In terminal:
; clojure -M:test                    ; Run all tests
; clojure -M:test --watch           ; Watch mode
; clojure -M:test --focus my.test   ; Run specific test
```

**Test Files**: Kaocha automatically discovers test files.

```clojure
; tests/ directory structure
; tests/
;   my/
;     app_test.clj

; In test file:
(ns my.app-test
  (:require [clojure.test :refer :all]
            [my.app :refer [add]]))

(deftest add-test
  (is (= 3 (add 1 2)))
  (is (= 5 (add 2 3))))
```

## Key Features

- Watch mode for TDD
- Multiple test library support
- Coverage reporting with Cloverage
- JUnit XML reporting
- Detailed test output
- Plugin system
- Selective test running
- Performance reporting

## When to Use

- Running clojure.test tests
- Test-driven development (watch mode)
- CI/CD pipelines
- Coverage reports

## When NOT to Use

- Complex test orchestration (use custom runners)

## Common Patterns

```clojure
; Basic test file
(ns my.handler-test
  (:require [clojure.test :refer :all]
            [my.handler :as handler]))

(deftest handler-test
  (testing "GET request"
    (is (= 200 (:status (handler/process-request {:method :get})))))
  
  (testing "POST request"
    (is (= 201 (:status (handler/process-request {:method :post}))))))

; In terminal:
; bb test                      ; Run tests via Babashka
; bb test --watch             ; Watch mode
; bb test --reporter documentation  ; Detailed output
```

## Related Libraries

- org.clojure/test.check - Property-based testing
- nubank/matcher-combinators - Better test assertions
- lambdaisland/kaocha-cloverage - Coverage plugin

## Resources

- Official Documentation: https://github.com/lambdaisland/kaocha
- API Documentation: https://cljdoc.org/d/lambdaisland/kaocha

## Notes

This project uses Kaocha as the primary test runner. See bb.edn for test configuration.
