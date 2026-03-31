---
name: failjure-error-handling
description: |
  Functional error handling without exceptions using failjure. Use when handling errors
  functionally, avoiding exceptions, building error pipelines, validating data with error
  propagation, or when the user mentions failjure, monadic error handling, failure values,
  error monad, functional error handling, attempt-all, or railway-oriented programming.
---

# Failjure - Functional Error Handling

Failjure is a lightweight library for handling errors functionally in Clojure without throwing exceptions. It provides an error monad with convenient macros for composing fallible operations.

## Quick Start

```clojure
;; Add dependency
{:deps {failjure/failjure {:mvn/version "2.3.0"}}}

;; Require core namespace
(require '[failjure.core :as f])

;; Create a failure
(f/fail "Something went wrong")
;; => #failjure.core.Failure{:message "Something went wrong"}

;; Check if something failed
(f/failed? (f/fail "error"))
;; => true

(f/failed? "ok")
;; => false

;; Chain operations that can fail
(f/attempt-all [x "ok"
                y (f/fail "error")]
  x
  (f/when-failed [e]
    (f/message e)))
;; => "error"
```

**Key benefits:**
- Functional error handling without exceptions
- Short-circuit evaluation on first failure
- Composable error handling macros
- Thread-safe and referentially transparent
- Works with ClojureScript

## Core Concepts

### HasFailed Protocol

The foundation of failjure is the `HasFailed` protocol with two functions:

```clojure
;; Check if a value represents failure
(f/failed? value)

;; Extract error message from failed value
(f/message value)
```

Failjure implements `HasFailed` for:
- `Failure` records (created with `fail`)
- Java `Exception` objects
- JavaScript `Error` objects (ClojureScript)
- All other values (not failed by default)

```clojure
;; Exceptions are treated as failures
(def ex (Exception. "Something broke"))
(f/failed? ex)
;; => true

(f/message ex)
;; => "Something broke"

;; Regular values are not failures
(f/failed? 42)
;; => false

(f/failed? "ok")
;; => false
```

### Creating Failures

Use `fail` to create failure values with formatted messages:

```clojure
;; Simple message
(f/fail "Operation failed")
;; => #failjure.core.Failure{:message "Operation failed"}

;; Formatted message (uses clojure.core/format)
(f/fail "User %s not found" "alice")
;; => #failjure.core.Failure{:message "User alice not found"}

;; Multiple format arguments
(f/fail "Expected %s but got %s" :string :int)
;; => #failjure.core.Failure{:message "Expected :string but got :int"}
```

### ok? Helper

Inverse of `failed?`:

```clojure
(f/ok? "success")
;; => true

(f/ok? (f/fail "error"))
;; => false
```

## Common Workflows

### Workflow 1: Basic Validation

Write validation functions that return success values or failures:

```clojure
(require '[failjure.core :as f])

;; Validation functions
(defn validate-email [email]
  (if (re-matches #".+@.+\..+" email)
    email
    (f/fail "Invalid email: %s" email)))

(defn validate-non-empty [s field-name]
  (if (empty? s)
    (f/fail "%s cannot be empty" field-name)
    s))

(defn validate-age [age]
  (cond
    (not (integer? age))
    (f/fail "Age must be an integer")
    
    (< age 0)
    (f/fail "Age cannot be negative")
    
    (> age 150)
    (f/fail "Age is unrealistic")
    
    :else age))

;; Test validations
(validate-email "user@example.com")
;; => "user@example.com"

(validate-email "not-an-email")
;; => #failjure.core.Failure{:message "Invalid email: not-an-email"}

(validate-age 25)
;; => 25

(validate-age -5)
;; => #failjure.core.Failure{:message "Age cannot be negative"}
```

### Workflow 2: Chaining Validations with attempt-all

Use `attempt-all` to chain operations that can fail. It short-circuits on the first failure:

```clojure
(defn validate-user-data [data]
  (f/attempt-all [email (validate-email (:email data))
                  username (validate-non-empty (:username data) "Username")
                  age (validate-age (:age data))]
    {:email email
     :username username
     :age age}
    (f/when-failed [e]
      (println "Validation failed:" (f/message e))
      e)))

;; Success case
(validate-user-data {:email "alice@example.com"
                     :username "alice"
                     :age 30})
;; => {:email "alice@example.com", :username "alice", :age 30}

;; Failure case - stops at first error
(validate-user-data {:email "bad-email"
                     :username "bob"
                     :age 25})
;; Prints: Validation failed: Invalid email: bad-email
;; => #failjure.core.Failure{:message "Invalid email: bad-email"}

;; Another failure case
(validate-user-data {:email "carol@example.com"
                     :username ""
                     :age 25})
;; Prints: Validation failed: Username cannot be empty
;; => #failjure.core.Failure{:message "Username cannot be empty"}
```

**Note:** `attempt-all` accepts a third form with `when-failed` for error handling.

### Workflow 3: Threading with ok-> and ok->>

Thread operations through success values, short-circuiting on failure:

```clojure
;; ok-> is like some-> but checks (ok? x) instead of (some? x)
(f/ok-> "hello"
        (str " world")
        (str "!"))
;; => "hello world!"

;; Short-circuits on first failure
(defn process-data [data]
  (f/ok-> data
          validate-email
          (str "@processed")
          (clojure.string/upper-case)))

(process-data "user@example.com")
;; => "USER@EXAMPLE.COM@PROCESSED"

(process-data "not-an-email")
;; => #failjure.core.Failure{:message "Invalid email: not-an-email"}

;; ok->> is the thread-last variant
(f/ok->> [1 2 3]
         (map inc)
         (filter even?)
         (reduce +))
;; => 6

;; With failure in pipeline
(defn safe-divide [x y]
  (if (zero? y)
    (f/fail "Division by zero")
    (/ x y)))

(f/ok->> 10
         (safe-divide 2)
         (safe-divide 0))
;; => #failjure.core.Failure{:message "Division by zero"}
```

### Workflow 4: Exception Handling with try*

Wrap exception-throwing code to convert exceptions into failures:

```clojure
;; try* catches exceptions and returns them as values
(f/try* (/ 10 2))
;; => 5

(f/try* (/ 10 0))
;; => #<ArithmeticException: Divide by zero>

;; Exceptions are treated as failures
(f/failed? (f/try* (/ 10 0)))
;; => true

;; Use in attempt-all for seamless exception handling
(f/attempt-all [x (f/try* (Integer/parseInt "42"))
                y (f/try* (Integer/parseInt "10"))]
  (+ x y)
  (f/when-failed [e]
    (f/message e)))
;; => 52

;; Parse failure is caught
(f/attempt-all [x (f/try* (Integer/parseInt "not-a-number"))
                y (f/try* (Integer/parseInt "10"))]
  (+ x y)
  (f/when-failed [e]
    (f/message e)))
;; => "For input string: \"not-a-number\""
```

### Workflow 5: try-all for Automatic Exception Wrapping

Use `try-all` when all operations might throw exceptions:

```clojure
;; try-all wraps each binding in try* automatically
(f/try-all [x (Integer/parseInt "42")
            y (Integer/parseInt "10")]
  (+ x y)
  (f/when-failed [e]
    (str "Parse error: " (f/message e))))
;; => 52

;; Exception caught automatically
(f/try-all [x (Integer/parseInt "not-a-number")
            y (Integer/parseInt "10")]
  (+ x y)
  (f/when-failed [e]
    (str "Parse error: " (f/message e))))
;; => "Parse error: For input string: \"not-a-number\""

;; Useful for file I/O and external API calls
(f/try-all [content (slurp "config.edn")
            config (clojure.edn/read-string content)]
  (get config :database-url)
  (f/when-failed [e]
    (println "Failed to load config:" (f/message e))
    "default-db-url"))
```

### Workflow 6: Conditional Branching with if-let-ok?

Branch based on success or failure:

```clojure
;; if-let-ok? - like if-let but checks (ok? value)
(defn handle-result [email]
  (f/if-let-ok? [v (validate-email email)]
    (str "Sending email to: " v)
    (str "Error: " (f/message v))))

(handle-result "user@example.com")
;; => "Sending email to: user@example.com"

(handle-result "bad-email")
;; => "Error: Invalid email: bad-email"

;; If no else branch provided, returns the value
(f/if-let-ok? [v (validate-email "user@example.com")]
  (str "Valid: " v))
;; => "Valid: user@example.com"

(f/if-let-ok? [v (validate-email "bad")]
  (str "Valid: " v))
;; => #failjure.core.Failure{:message "Invalid email: bad"}
```

### Workflow 7: when-let-ok? for Side Effects

Use `when-let-ok?` when you only care about the success case:

```clojure
(defn process-if-valid [email]
  (f/when-let-ok? [v (validate-email email)]
    (println "Processing:" v)
    (str "Processed: " v)))

(process-if-valid "user@example.com")
;; Prints: Processing: user@example.com
;; => "Processed: user@example.com"

;; Returns the failure on error
(process-if-valid "bad-email")
;; => #failjure.core.Failure{:message "Invalid email: bad-email"}
```

### Workflow 8: Inverse Branching with if-let-failed?

Branch on failure instead of success:

```clojure
;; if-let-failed? - like if-let-ok? but inverted
(defn log-errors [result]
  (f/if-let-failed? [e result]
    (do
      (println "ERROR:" (f/message e))
      nil)
    (do
      (println "SUCCESS:" e)
      e)))

(log-errors (validate-email "user@example.com"))
;; Prints: SUCCESS: user@example.com
;; => "user@example.com"

(log-errors (validate-email "bad"))
;; Prints: ERROR: Invalid email: bad
;; => nil

;; when-let-failed? for side effects only
(defn log-if-failed [result]
  (f/when-let-failed? [e result]
    (println "Operation failed:" (f/message e))))

(log-if-failed (f/fail "something broke"))
;; Prints: Operation failed: something broke
;; => #failjure.core.Failure{:message "something broke"}

(log-if-failed "ok")
;; => "ok"
```

### Workflow 9: Using attempt Helper

Use `attempt` to handle a potentially failed value:

```clojure
;; attempt applies a handler function if value failed
(defn handle-error [e]
  (str "Error: " (f/message e)))

(f/attempt handle-error "ok")
;; => "ok"

(f/attempt handle-error (f/fail "failure"))
;; => "Error: failure"

;; Useful with partial
(def log-and-continue
  (partial f/attempt
           (fn [e]
             (println "Warning:" (f/message e))
             :continue)))

(log-and-continue (f/fail "minor issue"))
;; Prints: Warning: minor issue
;; => :continue

(log-and-continue "success")
;; => "success"
```

### Workflow 10: as-ok-> for Named Threading

Use `as-ok->` when you need to refer to intermediate results by name:

```clojure
;; as-ok-> is like as-> but short-circuits on failure
(f/as-ok-> "hello" $
  (str $ " world")
  (str "Message: " $))
;; => "Message: hello world"

;; Short-circuits on failure
(f/as-ok-> 10 $
  (/ $ 2)
  (f/fail "error here")
  (str "Never reached: " $))
;; => #failjure.core.Failure{:message "error here"}

;; Useful for complex transformations
(defn process-number [n]
  (f/as-ok-> n $
    (if (pos? $) $ (f/fail "Must be positive"))
    (* $ 2)
    (if (< $ 100) $ (f/fail "Result too large"))
    (str "Result: " $)))

(process-number 30)
;; => "Result: 60"

(process-number -5)
;; => #failjure.core.Failure{:message "Must be positive"}

(process-number 60)
;; => #failjure.core.Failure{:message "Result too large"}
```

## Assertion Helpers

Failjure provides assertion helpers for common validation patterns:

```clojure
;; assert-with - general assertion helper
(f/assert-with pos? 5 "Must be positive")
;; => 5

(f/assert-with pos? -5 "Must be positive")
;; => #failjure.core.Failure{:message "Must be positive"}

;; Built-in assertion helpers
(f/assert-some? "value" "Must be present")
;; => "value"

(f/assert-some? nil "Must be present")
;; => #failjure.core.Failure{:message "Must be present"}

(f/assert-nil? nil "Must be nil")
;; => nil

(f/assert-not-nil? "value" "Cannot be nil")
;; => "value"

(f/assert-not-empty? "text" "Cannot be empty")
;; => "text"

(f/assert-not-empty? "" "Cannot be empty")
;; => #failjure.core.Failure{:message "Cannot be empty"}

(f/assert-number? 42 "Must be a number")
;; => 42

(f/assert-number? "42" "Must be a number")
;; => #failjure.core.Failure{:message "Must be a number"}
```

**Create custom assertion helpers:**

```clojure
;; Define custom assertions
(def assert-email? (partial f/assert-with #(re-matches #".+@.+\..+" %)))
(def assert-positive? (partial f/assert-with pos?))
(def assert-adult? (partial f/assert-with #(>= % 18)))

(assert-email? "user@example.com" "Invalid email")
;; => "user@example.com"

(assert-positive? 10 "Must be positive")
;; => 10

(assert-adult? 25 "Must be 18 or older")
;; => 25

;; Use in validation pipelines
(f/attempt-all [email (assert-email? (:email data) "Invalid email")
                age (assert-adult? (:age data) "Must be 18+")]
  {:email email :age age}
  (f/when-failed [e]
    (f/message e)))
```

## When to Use Each Approach

**Use `attempt-all` when:**
- Multiple validations need to run sequentially
- You want to stop at the first error
- Each step depends on previous results
- You need a clear error handling block

**Use `ok->` and `ok->>` when:**
- Building data transformation pipelines
- Operations naturally compose with threading macros
- You want concise pipeline syntax
- Each step can fail independently

**Use `try*` and `try-all` when:**
- Working with exception-throwing code
- Integrating third-party libraries that throw exceptions
- File I/O, network calls, or parsing operations
- You want to treat exceptions as failures

**Use `if-let-ok?` and `when-let-ok?` when:**
- Simple conditional branching
- Different logic for success vs. failure cases
- Side effects only needed on success
- Alternative to nested attempt-all

**Use assertion helpers when:**
- Simple predicate validation
- Adapting non-failjure code
- Building validation libraries
- Quick inline checks

## Best Practices

**DO:**
- Return success values directly (not wrapped)
- Return `Failure` or exceptions for errors
- Use `attempt-all` for readable sequential validation
- Use `ok->` for pipeline-style composition
- Wrap exception-throwing code with `try*`
- Create domain-specific validation functions
- Use `when-failed` to handle errors in `attempt-all`
- Check `failed?` before unwrapping values

**DON'T:**
- Throw exceptions in failjure code (return failures instead)
- Mix exception-based and failjure-based error handling
- Forget to handle the failure case
- Use failjure for exceptional control flow
- Over-nest `attempt-all` blocks (extract to functions)
- Use failjure where simple nil checks suffice
- Forget that exceptions are also treated as failures

## Common Issues

### Issue: "when-failed Not Triggering"

**Problem:** Error handler in `attempt-all` doesn't run

```clojure
(f/attempt-all [x "ok"
                y (f/fail "error")]
  x
  (println "Error:" (f/message y)))
;; Does not print error, returns failure
```

**Solution:** Use `when-failed` with binding

```clojure
(f/attempt-all [x "ok"
                y (f/fail "error")]
  x
  (f/when-failed [e]
    (println "Error:" (f/message e))))
;; Prints: Error: error
;; => nil
```

### Issue: "Short-Circuit Not Working"

**Problem:** Using `attempt->` instead of `ok->`

```clojure
;; attempt-> doesn't short-circuit if start value is a failure
(f/attempt-> (f/fail "start error")
             (str " world"))
;; => May not short-circuit as expected
```

**Solution:** Use `ok->` which properly short-circuits

```clojure
(f/ok-> (f/fail "start error")
        (str " world"))
;; => #failjure.core.Failure{:message "start error"}
```

**Note:** `attempt->` and `attempt->>` are deprecated. Use `ok->` and `ok->>` instead.

### Issue: "Exception Not Caught"

**Problem:** Forgetting to wrap exception-throwing code

```clojure
(f/attempt-all [x (Integer/parseInt "not-a-number")]
  x)
;; Throws NumberFormatException
```

**Solution:** Use `try*` or `try-all`

```clojure
(f/attempt-all [x (f/try* (Integer/parseInt "not-a-number"))]
  x
  (f/when-failed [e]
    (f/message e)))
;; => "For input string: \"not-a-number\""

;; Or use try-all
(f/try-all [x (Integer/parseInt "not-a-number")]
  x
  (f/when-failed [e]
    (f/message e)))
;; => "For input string: \"not-a-number\""
```

### Issue: "Checking Message of Non-Failed Value"

**Problem:** Calling `message` on success values

```clojure
(f/message "ok")
;; => "ok" (not very useful)
```

**Solution:** Check `failed?` before extracting message

```clojure
(defn safe-message [v]
  (when (f/failed? v)
    (f/message v)))

(safe-message "ok")
;; => nil

(safe-message (f/fail "error"))
;; => "error"
```

### Issue: "Nested attempt-all Hard to Read"

**Problem:** Too much nesting

```clojure
(f/attempt-all [a (validate-a data)]
  (f/attempt-all [b (validate-b a)]
    (f/attempt-all [c (validate-c b)]
      result)))
```

**Solution:** Flatten into single `attempt-all`

```clojure
(f/attempt-all [a (validate-a data)
                b (validate-b a)
                c (validate-c b)]
  result)
```

## Comparison with Other Libraries

**Failjure vs. Cats (Either monad):**
- Failjure: Lightweight, macro-based, idiomatic Clojure
- Cats: Full category theory, monadic composition, more complex

**Failjure vs. Exception handling:**
- Failjure: Functional, composable, no stack unwinding
- Exceptions: Imperative, side-effecting, harder to compose

**Failjure vs. nil-based error handling:**
- Failjure: Explicit failures with messages
- nil: No error information, ambiguous meaning

**Use failjure when:**
- You want functional error handling
- Errors should compose like regular values
- You need clear error messages
- You prefer Railway-Oriented Programming style

**Use cats/Either when:**
- You need full monadic abstractions
- Working with other category theory concepts
- Need monad transformers
- Type-level guarantees matter more

**Use exceptions when:**
- Truly exceptional conditions
- Working with Java libraries that throw
- Need stack traces for debugging
- Error handling is not the primary concern

## Resources

- [GitHub Repository](https://github.com/adambard/failjure)
- [Clojars](https://clojars.org/failjure)
- [Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/) - Error handling philosophy
- [Error Monad Tutorial](https://brehaut.net/blog/2011/error_monads) - Andrew Brehaut's original implementation
- [Babashka Compatible](https://github.com/babashka/babashka) - Works with bb scripts

## Summary

Failjure provides functional error handling for Clojure:

1. **Failures as values** - Errors are data, not exceptions
2. **Short-circuit composition** - `attempt-all`, `ok->`, `ok->>` stop at first failure
3. **Exception interop** - `try*` and `try-all` convert exceptions to failures
4. **Branching helpers** - `if-let-ok?`, `when-let-ok?`, `if-let-failed?`, `when-let-failed?`
5. **Assertion helpers** - Predicate-based validation with `assert-with` family
6. **Lightweight** - Simple protocol-based design, no heavy abstractions
7. **ClojureScript support** - Works in both Clojure and ClojureScript

Use failjure when you want Railway-Oriented Programming in Clojure: build pipelines where operations can fail gracefully, errors propagate automatically, and handling is explicit and composable.
