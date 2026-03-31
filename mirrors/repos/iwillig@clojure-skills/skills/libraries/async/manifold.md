---
name: manifold_async_programming
description: |
  Asynchronous programming with deferreds and streams in Manifold. Use when building 
  async applications, handling futures/promises, stream processing, backpressure, 
  integrating with core.async or Java futures, or when the user mentions manifold, 
  async programming, deferreds, streams, backpressure, event-driven, or async composition.
---

# Manifold - Asynchronous Programming

## Quick Start

Manifold provides two core abstractions for asynchronous programming: **deferreds** (single async values) and **streams** (sequences of async values).

```clojure
(require '[manifold.deferred :as d]
         '[manifold.stream :as s])

;; Deferreds - like promises/futures
(def result (d/deferred))
(d/success! result 42)
@result  ;; => 42

;; Streams - async sequences
(def stream (s/stream))
(s/put! stream 1)
(s/put! stream 2)
@(s/take! stream)  ;; => 1
@(s/take! stream)  ;; => 2
```

**Key benefits:**
- **Unified abstraction** - Single API for promises, futures, channels
- **Composable** - Rich operators for async workflows
- **Compatible** - Integrates with core.async, Java futures, promises
- **Backpressure** - Built-in flow control for streams
- **Non-blocking** - Efficient async I/O without thread blocking

## Core Concepts

### Deferreds - Single Async Values

Deferreds represent a single value that will be available in the future:

```clojure
(require '[manifold.deferred :as d])

;; Create a deferred
(def d (d/deferred))

;; Resolve with success
(d/success! d :value)

;; Or resolve with error
(def d2 (d/deferred))
(d/error! d2 (Exception. "failed"))

;; Check if realized
(d/realized? d)   ;; => true

;; Block and deref (like promises)
@d  ;; => :value

;; Non-blocking callback
(d/on-realized d
  (fn [value] (println "Success:" value))
  (fn [error] (println "Error:" error)))
```

### Streams - Async Sequences

Streams are ordered sequences of asynchronous values with backpressure:

```clojure
(require '[manifold.stream :as s])

;; Create a stream
(def stream (s/stream))

;; Put values (returns deferred of success)
@(s/put! stream 1)   ;; => true
@(s/put! stream 2)   ;; => true

;; Take values (returns deferred of value)
@(s/take! stream)    ;; => 1
@(s/take! stream)    ;; => 2

;; Check if closed
(s/closed? stream)   ;; => false

;; Close the stream
(s/close! stream)
```

### Compatibility Layer

Manifold can convert between different async abstractions:

```clojure
;; Convert Java Future to deferred
(d/->deferred (future (+ 1 2)))

;; Convert core.async channel to stream
(require '[clojure.core.async :as a])
(def ch (a/chan))
(def stream (s/->source ch))

;; Convert stream to channel
(def stream (s/stream))
(s/connect stream (a/chan))
```

## Common Workflows

### Workflow 1: Async Composition with Deferreds

```clojure
(require '[manifold.deferred :as d])

;; Chain async operations
(-> (d/future (http-get "http://api.example.com"))
    (d/chain parse-json)
    (d/chain process-data)
    (d/catch (fn [e] (log/error e) {:error "Failed"})))

;; Equivalent to:
(d/chain (d/future (http-get "http://api.example.com"))
         parse-json
         process-data)

;; Multiple parallel operations
(d/zip
  (d/future (fetch-user 1))
  (d/future (fetch-user 2))
  (d/future (fetch-user 3)))
;; => deferred of [user1 user2 user3]

;; Wait for any to complete
(d/alt
  (d/future (slow-service-1))
  (d/future (slow-service-2)))
;; => deferred of first result
```

### Workflow 2: Error Handling

```clojure
(require '[manifold.deferred :as d])

;; Catch errors in chain
(-> (d/future (risky-operation))
    (d/chain process-result)
    (d/catch Exception 
             (fn [e] 
               (log/error e "Operation failed")
               :default-value)))

;; Catch specific error types
(-> (d/future (database-query))
    (d/catch java.sql.SQLException
             (fn [e] (log/error "DB error") nil))
    (d/catch Exception
             (fn [e] (log/error "Other error") nil)))

;; Finally block
(-> (d/future (with-resource))
    (d/chain process)
    (d/finally (fn [] (cleanup-resource))))
```

### Workflow 3: Stream Processing

```clojure
(require '[manifold.stream :as s])

;; Transform stream with map
(def source (s/stream))
(def transformed (s/map inc source))

(s/put! source 1)
@(s/take! transformed)  ;; => 2

;; Filter stream
(def evens (s/filter even? source))

;; Reduce over stream
(def sum (s/reduce + 0 source))
(s/put! source 1)
(s/put! source 2)
(s/put! source 3)
(s/close! source)
@sum  ;; => 6

;; Buffer stream (control backpressure)
(def buffered (s/buffer 100 source))

;; Batch messages
(def batched (s/batch 10 source))  ;; Batches of 10
@(s/take! batched)  ;; => [1 2 3 4 5 6 7 8 9 10]
```

### Workflow 4: Connecting Streams

```clojure
(require '[manifold.stream :as s])

;; Connect two streams
(def source (s/stream))
(def sink (s/stream))
(s/connect source sink)

(s/put! source 1)
@(s/take! sink)  ;; => 1

;; Connect with transformation
(s/connect-via source
               (fn [value]
                 (s/put! sink (* value 2)))
               sink)

;; Split stream
(def source (s/stream))
(def odds (s/stream))
(def evens (s/stream))

(s/connect-via source
               (fn [value]
                 (if (even? value)
                   (s/put! evens value)
                   (s/put! odds value)))
               source)
```

### Workflow 5: Backpressure and Throttling

```clojure
(require '[manifold.stream :as s]
         '[manifold.time :as t])

;; Throttle puts (max rate)
(def source (s/stream))
(def throttled (s/throttle 10 1000 source))  ;; 10 per second

;; Buffer with backpressure
(def buffered (s/buffer 100 source))

;; When buffer full, put! returns false
(dotimes [n 150]
  (when-not @(s/put! buffered n)
    (println "Backpressure at" n)))

;; Periodic stream
(def periodic (s/periodically 1000 #(System/currentTimeMillis)))
@(s/take! periodic)  ;; Yields timestamp every second

;; Timeout on take
(def result (d/timeout! (s/take! slow-stream) 1000 :timeout))
@result  ;; => :timeout if takes > 1 second
```

### Workflow 6: Converting Between Abstractions

```clojure
(require '[manifold.deferred :as d]
         '[manifold.stream :as s]
         '[clojure.core.async :as a])

;; Future -> Deferred
(def d (d/->deferred (future (expensive-calc))))

;; Deferred -> Future
(def f (d/->future d))

;; core.async channel -> Stream
(def ch (a/chan))
(def stream (s/->source ch))

;; Stream -> core.async channel
(def stream (s/stream))
(def ch (a/chan))
(s/connect stream ch)

;; Lazy seq -> Stream
(def stream (s/->source (range 100)))

;; Stream -> Lazy seq (blocking)
(def items (s/stream->seq stream))
```

### Workflow 7: Timeout and Retry

```clojure
(require '[manifold.deferred :as d]
         '[manifold.time :as t])

;; Timeout a deferred
(def result 
  (d/timeout! 
    (d/future (slow-operation))
    5000  ;; 5 seconds
    :timeout))

;; Retry with exponential backoff
(defn retry-with-backoff [f max-attempts]
  (loop [attempt 1]
    (d/catch
      (d/future (f))
      (fn [e]
        (if (< attempt max-attempts)
          (do
            (Thread/sleep (* attempt 1000))  ;; Backoff
            (retry-with-backoff f (dec max-attempts)))
          (throw e))))))

;; Schedule deferred
(def scheduled (t/in 5000 #(d/success-deferred :result)))
@scheduled  ;; Yields :result after 5 seconds
```

## When to Use Each Approach

**Use Manifold deferreds when:**
- Building async workflows with composition
- Need better error handling than futures
- Want callbacks without callback hell
- Integrating different async libraries
- Need timeout/retry/scheduling capabilities

**Use Manifold streams when:**
- Processing sequences of async data
- Need backpressure control
- Transforming/filtering async sequences
- Building data pipelines
- Need interop with core.async or queues

**Use over core.async when:**
- You want a simpler API
- Need better error propagation
- Want deferred/promise-style composition
- Need compatibility with Java futures

**Use over plain futures when:**
- Need chaining and composition
- Want non-blocking callbacks
- Need error handling in chains
- Want timeout and retry capabilities

**Don't use Manifold when:**
- Simple blocking I/O is sufficient
- You're already heavily invested in core.async
- Synchronous code is simpler and adequate

## Best Practices

**Do:**
- Use `chain` for sequential async operations
- Use `zip` for parallel async operations
- Handle errors with `catch` instead of try/catch
- Close streams when done to prevent resource leaks
- Use buffering to control memory usage
- Test timeout behavior
- Use `realized?` to check deferred status before dereferencing

**Don't:**
- Block unnecessarily with `@` - prefer callbacks
- Forget to handle errors in async chains
- Create unbounded streams without backpressure
- Mix blocking and non-blocking code carelessly
- Ignore return values from `put!` (indicates backpressure)
- Forget to close streams (causes resource leaks)

## Common Issues

### Issue: "Deferred Never Resolves"

```clojure
;; Problem: Created but never resolved
(def d (d/deferred))
@d  ;; Blocks forever!

;; Solution: Always resolve deferreds
(d/success! d :value)

;; Or use timeout
(d/timeout! d 5000 :timeout)
```

### Issue: "Stream Backpressure Not Working"

```clojure
;; Problem: Ignoring put! return value
(def stream (s/buffer 10 (s/stream)))
(dotimes [n 100]
  (s/put! stream n))  ;; May lose messages!

;; Solution: Check put! result
(dotimes [n 100]
  (let [result @(s/put! stream n)]
    (when-not result
      (println "Backpressure triggered, waiting...")
      ;; Handle backpressure
      )))
```

### Issue: "Callback Hell with Nested Chains"

```clojure
;; Wrong: Nesting callbacks
(d/chain (fetch-user)
         (fn [user]
           (d/chain (fetch-orders user)
                    (fn [orders]
                      (d/chain (process-orders orders)
                               (fn [result] result))))))

;; Right: Flat chain
(d/chain (fetch-user)
         fetch-orders
         process-orders)
```

### Issue: "Memory Leak from Unclosed Streams"

```clojure
;; Wrong: Stream never closed
(defn process-data []
  (let [stream (s/stream)]
    (s/consume process-item stream)))  ;; Stream leaks!

;; Right: Close stream when done
(defn process-data []
  (let [stream (s/stream)]
    (try
      (s/consume process-item stream)
      (finally
        (s/close! stream)))))
```

### Issue: "Errors Swallowed in Chains"

```clojure
;; Wrong: No error handling
(d/chain (risky-operation)
         process-result)  ;; Errors are silent!

;; Right: Handle errors
(-> (d/chain (risky-operation)
             process-result)
    (d/catch (fn [e]
               (log/error e "Operation failed")
               :default-value)))
```

## Advanced Topics

### Custom Stream Sources

```clojure
(require '[manifold.stream :as s])

;; Create source from generator function
(defn number-stream [start]
  (let [stream (s/stream)]
    (future
      (loop [n start]
        (when @(s/put! stream n)
          (recur (inc n)))))
    stream))

(def numbers (number-stream 0))
```

### Deferred Loops

```clojure
(require '[manifold.deferred :as d])

;; Loop asynchronously
(d/loop [acc 0, n 10]
  (if (zero? n)
    acc
    (d/chain (d/future (expensive-calc n))
             (fn [result]
               (d/recur (+ acc result) (dec n))))))
```

### Stream Multicasting

```clojure
(require '[manifold.stream :as s])

;; Multicast to multiple consumers
(def source (s/stream))
(def listeners [(s/stream) (s/stream) (s/stream)])

(doseq [listener listeners]
  (s/connect source listener))

(s/put! source :event)
;; All listeners receive :event
```

## Related Libraries

- clojure.core.async - Alternative async library
- http-kit - Often used with Manifold for async HTTP
- aleph - HTTP/TCP server using Manifold

## External Resources

- [Official Documentation](https://cljdoc.org/d/manifold/manifold)
- [GitHub Repository](https://github.com/clj-commons/manifold)
- [Rationale](https://github.com/clj-commons/manifold/blob/master/doc/rationale.md)
- [Deferred Guide](https://github.com/clj-commons/manifold/blob/master/doc/deferred.md)
- [Stream Guide](https://github.com/clj-commons/manifold/blob/master/doc/stream.md)

## Summary

Manifold provides elegant abstractions for asynchronous programming:

1. **Deferreds** - Composable single async values with error handling
2. **Streams** - Async sequences with backpressure and transformation
3. **Compatibility** - Unifies futures, promises, channels, and queues
4. **Composition** - Rich operators like `chain`, `zip`, `alt` for workflows
5. **Practical** - Built for real-world async applications

Use Manifold when you need powerful async composition, want to avoid callback hell, or need to integrate multiple async abstractions in your application.
