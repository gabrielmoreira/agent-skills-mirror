---
name: lazytest_bdd_testing
description: |
  BDD-style testing framework for Clojure with RSpec-like syntax and composable test suites.
  Use when writing behavior-driven tests, organizing test hierarchies, or when the user mentions
  BDD testing, lazytest, describe/it syntax, RSpec-style testing, test suites, or behavior-driven
  development. Emphasizes readable test organization and composable test structures.
---

# Lazytest

BDD-style test framework for Clojure with focus on readability, composability, and REPL-driven development.

## Quick Start

Lazytest uses `describe`/`it` syntax inspired by RSpec and Mocha:

```clojure
(require '[lazytest.core :refer [defdescribe describe it expect]])

;; Define a test suite
(defdescribe math-test
  (describe "addition"
    (it "adds two numbers"
      (expect (= 3 (+ 1 2))))
    
    (it "is commutative"
      (expect (= (+ 1 2) (+ 2 1)))))
  
  (describe "multiplication"
    (it "multiplies two numbers"
      (expect (= 6 (* 2 3))))))

;; Run from CLI
;; clojure -M:test
```

**Key benefits:**
- **Readable syntax** - `describe`/`it` makes test intent clear
- **Composable suites** - Nest test contexts naturally
- **REPL-friendly** - Test at the REPL with ease
- **Watch mode** - Auto-reload and rerun on file changes
- **Flexible reporting** - Multiple output formats built-in

## Core Concepts

### Test Suites and Test Cases

Lazytest separates test organization (suites) from test execution (cases):

```clojure
;; defdescribe: Define a top-level test var
(defdescribe calculator-test
  ;; describe: Create nested test suites
  (describe "basic operations"
    ;; it: Define individual test cases
    (it "handles addition"
      (expect (= 5 (+ 2 3))))
    
    (it "handles subtraction"
      (expect (= 1 (- 3 2))))))
```

**Key point:** Test suites are data structures (maps), not executed immediately. The runner traverses them and executes test cases when appropriate.

### Expectations vs Assertions

```clojure
;; expect: Enhanced assertion with detailed failure info
(expect (= 3 (+ 1 2)))
;; On failure, shows:
;; - Expected form
;; - Actual result
;; - Evaluated arguments
;; - Source location

;; Standard assert also works
(assert (= 3 (+ 1 2)))
;; But provides less debugging information
```

### Test Structure

```clojure
(defdescribe user-service-test  ; Top-level test function
  (describe "create-user"        ; Test suite (context)
    (it "validates email"        ; Test case
      (expect ...))
    
    (it "generates UUID"
      (expect ...))
    
    (describe "with existing email"  ; Nested suite
      (it "returns error"
        (expect ...)))))
```

## Common Workflows

### Workflow 1: Basic Test Organization

```clojure
(require '[lazytest.core :refer [defdescribe describe it expect]])

(defdescribe string-utils-test
  (describe "capitalize"
    (it "capitalizes first letter"
      (expect (= "Hello" (capitalize "hello"))))
    
    (it "handles empty strings"
      (expect (= "" (capitalize ""))))
    
    (it "preserves already capitalized"
      (expect (= "Hello" (capitalize "Hello")))))
  
  (describe "reverse-words"
    (it "reverses word order"
      (expect (= "world hello" (reverse-words "hello world"))))
    
    (it "handles single word"
      (expect (= "hello" (reverse-words "hello"))))))
```

### Workflow 2: Setup and Teardown

Use context functions for test lifecycle management:

```clojure
(require '[lazytest.core :refer [defdescribe describe it expect 
                                   before before-each after after-each around]])

;; Run once before all tests in suite
(defdescribe database-test
  (let [state (atom nil)]
    (describe "with database"
      (before 
        (reset! state (create-test-db)))
      
      (after 
        (cleanup-db @state))
      
      (it "can insert records"
        (expect (insert-user! @state {:name "Alice"})))
      
      (it "can query records"
        (expect (= 1 (count (get-users @state))))))))

;; Run before/after each test case
(defdescribe session-test
  (let [session (atom nil)]
    (describe "user sessions"
      (before-each 
        (reset! session (create-session)))
      
      (after-each 
        (close-session @session))
      
      (it "starts empty"
        (expect (empty? (:data @session))))
      
      (it "can store data"
        (swap! session assoc-in [:data :user] "alice")
        (expect (= "alice" (get-in @session [:data :user])))))))

;; Wrap test execution
(defdescribe api-test
  (describe "with mock server"
    (around [f]
      (with-redefs [http/get mock-http-get]
        (f)))
    
    (it "fetches data"
      (expect (= {:status 200} (fetch-data))))))
```

### Workflow 3: Focused and Skipped Tests

Control which tests run without commenting code:

```clojure
(defdescribe feature-test
  ;; Run only focused tests
  (it "will be skipped"
    (expect (= 1 1)))
  
  (it "will run"
    {:focus true}
    (expect (= 2 2)))
  
  ;; Skip specific tests
  (it "work in progress"
    {:skip true}
    (expect (= :todo :implement)))
  
  ;; Focus entire suite
  (describe "critical feature"
    {:focus true}
    (it "must pass"
      (expect (= :important :working)))))
```

### Workflow 4: Metadata-Based Filtering

Organize tests by metadata for selective running:

```clojure
(defdescribe integration-test
  (describe "database operations"
    {:integration true}
    (it "connects to DB"
      (expect (db/connect)))
    
    (it "performs transaction"
      {:slow true}
      (Thread/sleep 1000)
      (expect (db/transaction ...))))
  
  (describe "unit tests"
    {:unit true}
    (it "pure function"
      (expect (= 4 (* 2 2))))))

;; Run from CLI:
;; clojure -M:test --include :integration  ; Only integration tests
;; clojure -M:test --exclude :slow         ; Skip slow tests
;; clojure -M:test -i :unit -e :slow      ; Unit tests but not slow
```

### Workflow 5: Var Metadata Tests

Attach tests directly to implementation functions:

```clojure
(defn add
  "Adds two numbers"
  {:lazytest/test
   (describe "addition"
     (it "handles positive numbers"
       (expect (= 5 (add 2 3))))
     
     (it "handles negative numbers"
       (expect (= -1 (add -3 2)))))}
  [a b]
  (+ a b))

;; Simple function test
(defn subtract
  {:lazytest/test #(expect (= 1 (subtract 3 2)))}
  [a b]
  (- a b))
```

### Workflow 6: Watch Mode Development

Use watch mode for TDD workflow:

```bash
# Start watch mode
clojure -M:test --watch

# Tests automatically rerun when files change
# Customize check interval (default 500ms)
clojure -M:test --watch --delay 1000

# Watch with specific output format
clojure -M:test --watch --output dots
```

### Workflow 7: REPL-Driven Testing

Test interactively at the REPL:

```clojure
(require '[lazytest.repl :as repl])

;; Run all tests in current namespace
(repl/run-tests *ns*)

;; Run specific test var
(repl/run-test-var #'my.app-test/feature-test)

;; Run all loaded tests
(repl/run-all-tests)

;; Results are returned and printed
;; => {:pass 10 :fail 0 :error 0}
```

## When to Use Each Approach

**Use `defdescribe` when:**
- Defining top-level test suites
- Organizing tests by feature or module
- Need a test var that can be run individually

**Use `describe` when:**
- Grouping related test cases
- Creating nested test contexts
- Sharing setup/teardown across tests

**Use `it` when:**
- Writing individual test cases
- Each test is a single assertion or behavior

**Use `expect` when:**
- Need detailed failure information
- Debugging test failures
- Want to see evaluated arguments

**Use `assert` when:**
- Simple pass/fail is sufficient
- Performance critical (slightly faster)

**Use setup/teardown when:**
- Need to initialize/cleanup resources
- Setting up test data or mocks
- Managing stateful dependencies

**Don't use lazytest when:**
- Need exact `clojure.test` compatibility
- Using tools that require `clojure.test` (some may work)
- Team unfamiliar with BDD syntax

## Best Practices

**Do:**
- Use descriptive test names
- Keep `it` blocks focused (one behavior per test)
- Use `describe` to group related tests
- Leverage metadata for test organization
- Use `delay` or `volatile!` for test data shared across cases
- Put context-dependent code in setup/teardown
- Name all top-level suites with `defdescribe`

**Don't:**
- Write code outside `it` blocks that has side effects
- Use `let` bindings for mutable state (use `delay`, `atom`, or `volatile!`)
- Nest `describe` too deeply (3-4 levels max)
- Mix assertion styles inconsistently
- Forget that suites are data structures, not executed immediately
- Use `with-redefs` outside `around` blocks

## Common Issues

### Issue: "State not shared between tests"

```clojure
;; Wrong: let binding evaluated once when suite is created
(defdescribe bad-test
  (let [data (fetch-data)]  ; Called during suite creation!
    (it "test 1" (expect data))
    (it "test 2" (expect data))))

;; Right: Use delay for lazy evaluation
(defdescribe good-test
  (let [data (delay (fetch-data))]  ; Called when dereferenced
    (it "test 1" (expect @data))
    (it "test 2" (expect @data))))

;; Or use atom with before
(defdescribe also-good-test
  (let [data (atom nil)]
    (before (reset! data (fetch-data)))
    (it "test 1" (expect @data))
    (it "test 2" (expect @data))))
```

### Issue: "with-redefs not working"

```clojure
;; Wrong: redefs evaluated during suite creation
(defdescribe bad-redefs
  (with-redefs [http/get mock-get]
    (it "makes request"
      (expect (fetch-url "http://example.com")))))

;; Right: Use around to apply during test execution
(defdescribe good-redefs
  (around [f]
    (with-redefs [http/get mock-get]
      (f)))
  (it "makes request"
    (expect (fetch-url "http://example.com"))))
```

### Issue: "Tests not found by runner"

```clojure
;; Ensure tests are in test/ directory
;; Or specify directory:
;; clojure -M:test --dir src --dir test

;; Check namespace is required
;; Lazytest finds tests by loading namespaces

;; Verify defdescribe is used for top-level tests
(defdescribe my-test  ; Creates var that runner finds
  (describe "feature"
    (it "works" (expect true))))
```

### Issue: "Watch mode not detecting changes"

```bash
# Check delay setting (default 500ms)
clojure -M:test --watch --delay 1000

# Ensure files are on classpath
# Check :paths and :extra-paths in deps.edn

# Watch mode requires clj-reload
# Should be automatically available
```

### Issue: "Nested describe not running"

```clojure
;; Ensure describe is actually nested
(defdescribe suite-test
  (describe "outer"
    (describe "inner"  ; Properly nested
      (it "runs" (expect true)))))

;; Not separate top-level describes
(describe "not-nested-1" ...)  ; Won't run
(describe "not-nested-2" ...)  ; Won't run
```

## Advanced Topics

### Custom Reporters

Create custom output formats:

```clojure
(ns my.reporter
  (:require [lazytest.reporters :as reporters]))

(defmulti my-reporter 
  reporters/reporter-dispatch)

(defmethod my-reporter :begin-test-case [config test-case]
  (println "Starting:" (:doc test-case)))

(defmethod my-reporter :pass [config result]
  (println "✓ Passed"))

(defmethod my-reporter :fail [config result]
  (println "✗ Failed:" (:message result)))

;; Use it:
;; clojure -M:test --output my.reporter/my-reporter
```

### Namespace-Wide Context

Set context for all tests in a namespace:

```clojure
(ns my.app-test
  (:require [lazytest.core :refer [defdescribe describe it expect 
                                     set-ns-context! around]]))

;; Define reusable context
(def with-db
  (around [f]
    (with-open [db (create-db)]
      (binding [*db* db]
        (f)))))

;; Apply to all tests in namespace
(set-ns-context! [with-db])

(defdescribe user-test
  (it "can create user"
    (create-user *db* {:name "Alice"})))

(defdescribe post-test
  (it "can create post"
    (create-post *db* {:title "Hello"})))
```

### Multiple Assertions per Test

```clojure
;; Multiple expectations in one test case
(it "validates user data"
  (let [user {:name "Alice" :age 30}]
    (expect (string? (:name user)))
    (expect (> (:age user) 0))
    (expect (contains? user :name))))

;; Or use expect-it for single assertion
(require '[lazytest.core :refer [expect-it]])

(expect-it "has valid name"
  (string? (:name user)))
```

### Doc Tests in Markdown

Test code blocks in your documentation:

````markdown
# My Library

## Usage

```clojure
(require '[my.lib :as lib])

(lib/add 2 3)
;; => 5

(lib/multiply 4 5)
;; => 20
```
````

Run with:
```bash
clojure -M:test --md README.md
```

### Integration with CI/CD

```yaml
# GitHub Actions example
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: DeLaGuardo/setup-clojure@master
        with:
          cli: latest
      - name: Run tests
        run: clojure -M:test --output clojure-test
```

## Performance Considerations

- **Suite creation** - Evaluated once, not per test
- **Context functions** - `before` runs once per suite, `before-each` per test
- **Test data** - Use `delay` for expensive setup
- **Watch mode** - Adjust `--delay` for filesystem performance
- **Focus tests** - Run subset during development

## Related Libraries

- `clojure.test` - Standard Clojure testing
- `expectations/clojure-test` - Simpler assertion syntax
- `nubank/matcher-combinators` - Rich matchers for lazytest
- `lambdaisland/kaocha` - Alternative test runner
- `midje` - Another BDD-style framework

## External Resources

- [GitHub Repository](https://github.com/NoahTheDuke/lazytest)
- [Documentation](https://cljdoc.org/d/io.github.noahtheduke/lazytest)
- [Changelog](https://github.com/NoahTheDuke/lazytest/blob/main/CHANGELOG.md)

## Summary

Lazytest is a BDD-style testing framework emphasizing:

1. **Readable syntax** - `describe`/`it` makes test structure clear
2. **Composable suites** - Tests are data structures you can manipulate
3. **REPL-friendly** - Test interactively during development
4. **Flexible execution** - Focus, skip, filter by metadata
5. **Watch mode** - Auto-reload for TDD workflow
6. **Setup/teardown** - `before`, `after`, `around` context functions
7. **Multiple reporters** - Nested, dots, clojure-test, custom

Use lazytest when you want readable, organized test suites with clear test hierarchies and prefer BDD-style syntax over `deftest`/`is`.
