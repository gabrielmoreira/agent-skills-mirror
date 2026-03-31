---
name: promesa-promises-async
description: |
  Work with promises and async operations using Promesa. Use when handling asynchronous
  computations, promise chaining, concurrent operations, async/await patterns, or when
  the user mentions promises, futures, async, CompletableFuture, deferred values,
  promise composition, or non-blocking operations.
---

# Promesa

A promise library and concurrency toolkit for Clojure that provides a rich abstraction
for asynchronous operations. Built on CompletableFuture (JVM) and Promise (JS).

## Quick Start

Promesa provides a clean, composable API for working with asynchronous operations:

```clojure
;; Add dependency
{:deps {funcool/promesa {:mvn/version "11.0.678"}}}

;; Require the namespace
(require '[promesa.core :as p])

;; Create and work with promises
@(-> (p/resolved 1)
     (p/then inc)
     (p/then inc))
;; => 3

;; Use let macro for async composition
@(p/let [x (p/resolved 10)
         y (p/resolved 20)]
   (+ x y))
;; => 30
```

**Key benefits:**
- Clean async/await-style syntax with `let` macro
- Automatic error propagation and handling
- Zero runtime dependencies
- Works on both JVM and JavaScript
- Built-in executor and scheduling facilities
- Performance optimized for minimal overhead

## Core Concepts

### Promises as Abstractions

A promise represents an asynchronous computation that may succeed or fail. Promises
have three possible states:

```clojure
;; Create promises in different states
(def pending (p/deferred))          ; pending - no value yet
(def resolved (p/resolved 42))      ; resolved - has a value
(def rejected (p/rejected (ex-info "error" {})))  ; rejected - has an error

;; Inspect promise state
(p/pending? pending)   ; => true
(p/resolved? resolved) ; => true
(p/rejected? rejected) ; => true
(p/done? pending)      ; => false
(p/done? resolved)     ; => true
```

### Promise Creation

Multiple ways to create promises depending on your needs:

```clojure
;; From a value (auto-coercion)
(p/promise 42)
;; => resolved promise with value 42

(p/promise (ex-info "error" {}))
;; => rejected promise with error

;; Explicit creation
(p/resolved 42)
;; => resolved promise

(p/rejected (ex-info "error" {}))
;; => rejected promise

;; Deferred (manual resolution)
(def d (p/deferred))
(p/resolve! d 42)
;; d is now resolved with 42

;; Factory function (like JS)
@(p/create (fn [resolve reject]
             (resolve 42)))
;; => 42
```

### Blocking vs Non-blocking

On the JVM, `deref` or `@` blocks until the promise resolves. On JS, it returns
the current value without blocking:

```clojure
;; JVM - blocks until resolved
@(p/delay 100 42)
;; Waits 100ms, then => 42

;; Extract current value without blocking (works on both JVM and JS)
(p/extract pending :not-ready)
;; => :not-ready (if still pending)

(p/extract resolved :not-ready)
;; => 42 (the actual value)
```

## Common Workflows

### Workflow 1: Promise Chaining with then

Chain asynchronous operations using `then`:

```clojure
;; Basic chaining
@(-> (p/resolved 1)
     (p/then inc)
     (p/then #(* % 2))
     (p/then str))
;; => "4"

;; Automatic flattening of nested promises
@(-> (p/resolved 1)
     (p/then (fn [x] 
               (p/resolved (inc x)))))
;; => 2 (not a nested promise)

;; Multiple transformations with chain
@(-> (p/resolved 1)
     (p/chain inc inc inc))
;; => 4
```

### Workflow 2: Async/Await with let Macro

The `let` macro provides clean async/await syntax:

```clojure
;; Sequential async operations
(def result
  (p/let [user-id (fetch-user-id)
          user (fetch-user user-id)
          orders (fetch-orders (:id user))]
    {:user user
     :order-count (count orders)}))

@result
;; => {:user {...} :order-count 5}

;; Mix async and sync values
@(p/let [x (p/delay 100 10)
         y 20           ; regular value
         z (p/delay 50 5)]
   (+ x y z))
;; => 35

;; Short-circuits on error
@(p/let [x (p/resolved 10)
         y (p/rejected (ex-info "error" {}))
         z (p/resolved 5)]
   (+ x y z))
;; => ExceptionInfo: error
```

### Workflow 3: Error Handling

Comprehensive error handling with `catch` and error-aware functions:

```clojure
;; Basic error handling
@(-> (p/rejected (ex-info "database error" {:code 500}))
     (p/catch (fn [error]
                (println "Error:" (ex-message error))
                :fallback-value)))
;; => :fallback-value

;; Filter by exception type
@(-> (p/rejected (ex-info "error" {}))
     (p/catch clojure.lang.ExceptionInfo
              (fn [e] :caught-ex-info))
     (p/catch Exception
              (fn [e] :caught-exception)))
;; => :caught-ex-info

;; Filter by predicate
(defn timeout-error? [e]
  (= :timeout (:type (ex-data e))))

@(-> (p/rejected (ex-info "timeout" {:type :timeout}))
     (p/catch timeout-error?
              (fn [e] :retry)))
;; => :retry

;; Handle both success and error
@(-> (p/resolved 42)
     (p/handle (fn [result error]
                 (if error
                   :error
                   :success))))
;; => :success

;; Finally - always executes
@(-> (p/resolved 42)
     (p/finally (fn [_ _]
                  (println "Cleanup"))))
;; Prints: Cleanup
;; => 42
```

### Workflow 4: Concurrent Operations

Wait for multiple promises with `all`, `race`, and `any`:

```clojure
;; Wait for all promises
@(p/all [(p/delay 100 1)
         (p/delay 200 2)
         (p/delay 150 3)])
;; => [1 2 3]

;; Parallel let - start all operations simultaneously
@(p/plet [a (p/delay 100 1)
          b (p/delay 200 2)
          c (p/delay 150 3)]
   (+ a b c))
;; => 6

;; Race - first to complete wins
@(p/race [(p/delay 125 :slow)
          (p/delay 50 :fast)])
;; => :fast

;; Any - first successful result
@(p/any [(p/rejected (ex-info "error" {}))
         (p/delay 100 :success)
         (p/delay 200 :also-success)])
;; => :success
```

### Workflow 5: Threading Macros

Promesa provides promise-aware threading macros:

```clojure
;; Promise-aware -> threading
@(p/-> (p/resolved {:a 1 :c 3})
       (assoc :b 2)
       (dissoc :c)
       vals
       vec)
;; => [1 2]

;; Promise-aware ->> threading
@(p/->> (p/resolved [1 2 3])
        (map inc)
        (filter odd?)
        (reduce +))
;; => 8

;; Promise-aware as->
@(p/as-> (p/resolved 5) x
         (* x x)
         (+ x 10))
;; => 35
```

### Workflow 6: Functional Composition (Performance)

For performance-sensitive code, use functional style with `->>`:

```clojure
;; fmap - transform value (no auto-unwrap)
@(->> (p/resolved 1)
      (p/fmap inc)
      (p/fmap #(* % 2)))
;; => 4

;; mcat - transform and flatten (like flatMap)
@(->> (p/resolved 1)
      (p/mcat (fn [x] (p/resolved (inc x))))
      (p/mcat (fn [x] (p/resolved (* x 2)))))
;; => 4

;; merr - handle errors functionally
@(->> (p/rejected (ex-info "error" {:code 500}))
      (p/merr (fn [e]
                (p/resolved (get (ex-data e) :code)))))
;; => 500

;; hmap - handle both value and error
@(->> (p/resolved 42)
      (p/hmap (fn [value error]
                (if error
                  :error
                  (inc value)))))
;; => 43
```

### Workflow 7: Delays and Timeouts

Schedule operations and add timeouts:

```clojure
;; Delay execution
@(p/delay 1000 "done")
;; Waits 1 second, then => "done"

;; Add timeout to operation
@(-> (some-slow-operation)
     (p/timeout 5000)
     (p/catch (fn [e]
                (if (instance? java.util.concurrent.TimeoutException e)
                  :timeout
                  :other-error))))
;; => :timeout (if operation takes > 5s)

;; Timeout with default value
@(-> (p/delay 10000 "slow")
     (p/timeout 100 :too-slow))
;; => :too-slow
```

### Workflow 8: Executors and Async Tasks

Control execution threads and scheduling:

```clojure
(require '[promesa.exec :as px])

;; Submit task to executor (returns promise with result)
@(px/submit! (fn []
               (* 6 7)))
;; => 42

;; Run task (returns promise, ignores result)
@(px/run! (fn []
            (println "Running in different thread")
            42))
;; Prints: Running in different thread
;; => nil

;; Use custom executor
(def my-executor (px/fixed-executor :parallelism 4))

@(px/submit! my-executor
             (fn []
               (Thread/sleep 100)
               "done"))
;; => "done"

;; Schedule task for later
(px/schedule! 1000 
              (fn []
                (println "Delayed execution")))
;; Executes after 1 second

;; Cancel scheduled tasks
(def task (px/schedule! 5000 #(println "Won't run")))
(p/cancel! task)
;; Task is cancelled
```

### Workflow 9: Promise Loops

Recursively process with `loop` and `recur`:

```clojure
;; Async loop with promises
@(p/loop [i 0
          acc []]
   (if (< i 5)
     (p/recur (inc i)
              (conj acc i))
     (p/resolved acc)))
;; => [0 1 2 3 4]

;; Loop with async operations
@(p/loop [ids [1 2 3]
          results []]
   (if-let [id (first ids)]
     (p/let [result (fetch-data id)]
       (p/recur (rest ids)
                (conj results result)))
     (p/resolved results)))
;; Fetches data for each ID sequentially
```

### Workflow 10: Using do Blocks

Execute multiple async operations sequentially:

```clojure
;; Simple do block
@(p/do
   (println "Step 1")
   (p/delay 100 42))
;; Prints: Step 1
;; => 42

;; Multiple async steps
@(p/do
   (p/delay 50 (println "First"))
   (p/delay 50 (println "Second"))
   (p/delay 50 (println "Third"))
   "done")
;; Executes in order, waits for each
;; => "done"

;; Equivalent to let with ignored bindings
@(p/let [_ (p/delay 50 1)
         _ (p/delay 50 2)]
   (p/delay 50 3))
;; => 3
```

## When to Use Each Approach

### Use then/chain when:
- You want familiar JS promise-style chaining
- Auto-unwrapping of nested promises is convenient
- Code readability is more important than maximum performance
- Working with existing promise-based APIs

### Use let macro when:
- You need async/await style code
- Multiple sequential async operations
- Complex compositions with mixed sync/async values
- Code should look like synchronous code

### Use plet when:
- Starting multiple operations in parallel
- All operations are independent
- Need to wait for all to complete

### Use fmap/mcat when:
- Performance is critical
- You want explicit control over flattening
- Building reusable combinator-based code
- Functional composition style preferred

### Use executors when:
- Need control over execution threads
- Running CPU-intensive operations
- Want to isolate blocking operations
- Need custom thread pool configuration

## Best Practices

**DO:**
- Use `let` macro for sequential async operations
- Use `plet` for parallel independent operations
- Handle errors with `catch` or error-aware functions
- Use executors to control thread usage
- Add timeouts to external operations
- Cancel promises when operations are no longer needed
- Use functional style (`fmap`, `mcat`) for performance-critical paths
- Prefer `resolved` and `rejected` over `promise` when state is known

**DON'T:**
- Block unnecessarily on the JVM (use `extract` when appropriate)
- Ignore error handling in promise chains
- Create deeply nested promise chains (use `let` instead)
- Use `then` in tight loops (use `fmap` for performance)
- Forget that JS runtime can't block (deref doesn't wait)
- Mix blocking and non-blocking styles inconsistently
- Create executor instances without shutting them down

## Common Issues

### Issue: Promise Never Resolves

**Problem:** Promise seems to hang forever.

```clojure
;; Creating deferred but never resolving
(def p (p/deferred))
@p
;; Blocks forever
```

**Solution:** Always resolve or reject deferred promises.

```clojure
(def p (p/deferred))
(p/resolve! p 42)
@p
;; => 42

;; Or handle in factory
(p/create (fn [resolve reject]
            (resolve 42)))
```

### Issue: Error Not Caught

**Problem:** Exception escapes promise chain.

```clojure
;; Exception in chain
@(-> (p/resolved 1)
     (p/then (fn [x] 
               (throw (ex-info "error" {}))
               (inc x))))
;; => Unhandled exception
```

**Solution:** Add `catch` handler.

```clojure
@(-> (p/resolved 1)
     (p/then (fn [x]
               (throw (ex-info "error" {}))
               (inc x)))
     (p/catch (fn [e]
                (println "Caught:" (ex-message e))
                :error)))
;; Prints: Caught: error
;; => :error
```

### Issue: Nested Promises

**Problem:** Promise inside promise instead of flat value.

```clojure
;; Using fmap with promise-returning function
@(->> (p/resolved 1)
      (p/fmap (fn [x] (p/resolved (inc x)))))
;; => #<CompletableFuture...> (nested promise!)
```

**Solution:** Use `mcat` or `then` for auto-unwrapping.

```clojure
;; Use mcat
@(->> (p/resolved 1)
      (p/mcat (fn [x] (p/resolved (inc x)))))
;; => 2

;; Or use then
@(-> (p/resolved 1)
     (p/then (fn [x] (p/resolved (inc x)))))
;; => 2
```

### Issue: Race Condition with plet

**Problem:** `plet` doesn't actually run in parallel.

```clojure
;; This looks parallel but isn't
@(p/plet [x (fetch-data 1)    ; Blocks until x completes
          y (fetch-data 2)]   ; Then starts y
   [x y])
```

**Solution:** Start promises before `plet`.

```clojure
;; Start all promises first
(let [px (fetch-data 1)
      py (fetch-data 2)]
  @(p/plet [x px
            y py]
     [x y]))

;; Or use all
@(p/all [(fetch-data 1)
         (fetch-data 2)])
```

### Issue: Blocking on JavaScript

**Problem:** Expecting `@` to block on JS runtime.

```clojure
;; JS runtime - doesn't block!
@(p/delay 1000 42)
;; => nil (immediately, doesn't wait)
```

**Solution:** Use callbacks instead of blocking.

```clojure
;; Use then for async handling
(-> (p/delay 1000 42)
    (p/then (fn [x]
              (println "Got:" x))))
;; Prints after 1 second: Got: 42
```

### Issue: Executor Not Shutting Down

**Problem:** JVM doesn't exit because executor threads are running.

```clojure
(def ex (px/fixed-executor :parallelism 4))
(px/submit! ex (fn [] 42))
;; JVM won't exit
```

**Solution:** Shutdown executor when done.

```clojure
(def ex (px/fixed-executor :parallelism 4))
@(px/submit! ex (fn [] 42))
(px/shutdown! ex)
;; JVM can exit

;; Or use with-executor macro
(px/with-executor ^:shutdown (px/fixed-executor :parallelism 4)
  @(px/submit! (fn [] 42)))
;; Automatically shuts down
```

## Advanced Topics

### Virtual Threads (JDK 19+)

Use virtual threads for massive concurrency:

```clojure
;; Check if available
(px/vthread-supported?)
;; => true (on JDK 19+ with preview enabled)

;; Use virtual thread executor
@(->> (p/resolved 1)
      (p/fmap :vthread inc))

;; Or use vthread directly
(p/vthread
  (Thread/sleep 1000)
  42)
```

### Custom Executors

Create specialized executors for different workloads:

```clojure
;; CPU-bound work
(def cpu-executor (px/fixed-executor :parallelism (px/get-available-processors)))

;; I/O-bound work
(def io-executor (px/cached-executor))

;; Scheduled work
(def scheduler (px/scheduled-executor :parallelism 1))

;; Use in promise chains
@(->> (p/resolved data)
      (p/fmap cpu-executor heavy-computation)
      (p/mcat io-executor #(save-to-db %)))
```

### Performance Optimization

Choose the right execution model:

```clojure
;; Default: chain executes in same thread (fast)
@(->> (p/resolved 1)
      (p/fmap inc)
      (p/fmap inc))

;; Explicit: schedule each step separately (responsive)
@(->> (p/resolved 1)
      (p/fmap :default inc)
      (p/fmap :default inc))

;; For long chains, mix both approaches
@(->> (p/resolved 1)
      (p/fmap inc)           ; Same thread
      (p/fmap inc)           ; Same thread
      (p/fmap :default inc)  ; New thread
      (p/fmap inc)           ; Same thread
      (p/fmap inc))          ; Same thread
```

## Resources

- [Official Documentation](https://funcool.github.io/promesa/latest/)
- [GitHub Repository](https://github.com/funcool/promesa)
- [API Reference](https://funcool.github.io/promesa/latest/promesa.core.html)
- [Executors Guide](https://funcool.github.io/promesa/latest/executors.html)

## Summary

Promesa is a comprehensive promise library for Clojure providing:

- **Clean async/await syntax** with `let` and `plet` macros
- **Promise composition** with `then`, `chain`, `fmap`, and `mcat`
- **Error handling** with `catch`, `handle`, and `merr`
- **Concurrent operations** with `all`, `race`, and `any`
- **Executor control** for managing thread pools and scheduling
- **Performance optimization** with functional composition style
- **Cross-platform** support for JVM and JavaScript

Use Promesa when you need composable, maintainable async code with excellent error
handling and performance characteristics.
