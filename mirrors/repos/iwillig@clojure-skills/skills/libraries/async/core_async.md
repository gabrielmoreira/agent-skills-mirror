---
name: core-async-channels
description: |
  Asynchronous programming with channels and go blocks in Clojure using core.async.
  Use when building concurrent systems, CSP-style communication, async operations,
  event processing, or when the user mentions core.async, channels, go blocks, CSP,
  async/await patterns, channel operations, alts!, mult, pub/sub, pipelines, or
  asynchronous coordination.
---

# core.async - Asynchronous Programming with Channels

## Quick Start

core.async provides CSP (Communicating Sequential Processes) style concurrency with channels and go blocks.

```clojure
;; Add dependency
{:deps {org.clojure/core.async {:mvn/version "1.6.681"}}}

;; Require core.async
(require '[clojure.core.async :as async
           :refer [go go-loop <! >! <!! >!! chan close! timeout]])

;; Create a channel
(def c (chan))

;; Put and take with go blocks (non-blocking)
(go
  (>! c "hello")
  (println "Sent hello"))

(go
  (let [msg (<! c)]
    (println "Received:" msg)))
;; Prints: Sent hello
;;         Received: hello

;; Blocking operations for non-go code
(>!! c "world")  ; Block until put succeeds
(<!! c)          ; Block until take succeeds
;; => "world"

;; Timeout channels
(go
  (let [result (<! (timeout 1000))]
    (println "Waited 1 second")))
```

**Key benefits:**
- **CSP-style** - Communicate by sharing channels, not memory
- **Lightweight** - Go blocks park (don't block threads)
- **Composable** - Build complex async flows from simple operations
- **Safe** - Avoid callback hell and race conditions
- **Powerful** - Built-in patterns: pub/sub, mult, merge, pipeline

## Core Concepts

### Channels

Channels are queues for passing values between go blocks:

```clojure
(require '[clojure.core.async :as async :refer [chan]])

;; Unbuffered channel (rendezvous)
(def c (chan))

;; Buffered channel
(def bc (chan 10))  ; Holds 10 items

;; Buffer types
(def dropping (chan (async/dropping-buffer 5)))  ; Drops newest when full
(def sliding (chan (async/sliding-buffer 5)))    ; Drops oldest when full
```

### Go Blocks

Go blocks enable lightweight concurrency by parking (not blocking):

```clojure
(go
  ;; This code runs asynchronously
  (let [v (<! some-channel)]
    (println "Got:" v)
    (>! another-channel (* v 2))))

;; Go blocks return a channel with the result
(let [result-chan (go
                    (+ 1 2 3))]
  (<!! result-chan))  ; => 6
```

**Important:** Use `<!`, `>!`, `alts!` inside go blocks. Use `<!!`, `>!!`, `alts!!` outside go blocks.

### Parking vs Blocking

```clojure
;; Parking (go block) - doesn't tie up thread
(go
  (<! channel))  ; Parks the go block, thread continues

;; Blocking (regular thread) - ties up thread
(<!! channel)   ; Blocks current thread until value available
```

### Channel Operations

```clojure
;; Take: <! (go) or <!! (blocking)
(go
  (let [v (<! c)]
    (println v)))

;; Put: >! (go) or >!! (blocking)
(go
  (>! c "message"))

;; Close channel
(close! c)

;; Takes from closed channel return nil
(<!! c)  ; => nil

;; Puts to closed channel are ignored
(>!! c "ignored")  ; => false
```

## Common Workflows

### Workflow 1: Basic Producer-Consumer

```clojure
(require '[clojure.core.async :as async
           :refer [go go-loop <! >! <!! >!! chan close!]])

(defn producer [c n]
  (go
    (doseq [i (range n)]
      (println "Producing:" i)
      (>! c i)
      (<! (timeout 100)))  ; Slow down production
    (close! c)))

(defn consumer [c]
  (go-loop []
    (when-let [v (<! c)]  ; nil when channel closed
      (println "Consuming:" v)
      (<! (timeout 200))  ; Process time
      (recur))))

;; Run producer and consumer
(let [c (chan 5)]
  (producer c 10)
  (<!! (consumer c)))
;; Produces and consumes 10 items
```

### Workflow 2: Timeout and Alt Operations

```clojure
(require '[clojure.core.async :as async
           :refer [go <! >! alts! timeout chan]])

;; Wait for result or timeout
(defn fetch-with-timeout [url timeout-ms]
  (let [result-ch (chan)
        timeout-ch (timeout timeout-ms)]
    (go
      ;; Simulate fetch
      (<! (timeout 500))
      (>! result-ch {:url url :data "..."}))
    (go
      (let [[val port] (alts! [result-ch timeout-ch])]
        (if (= port timeout-ch)
          {:error "timeout"}
          val)))))

(<!! (fetch-with-timeout "http://example.com" 1000))
;; => {:url "http://example.com" :data "..."}

(<!! (fetch-with-timeout "http://slow.com" 100))
;; => {:error "timeout"}

;; Alt with multiple channels
(let [c1 (chan)
      c2 (chan)
      c3 (chan)]
  (go (>! c1 "from-c1"))
  (go (<! (timeout 100)) (>! c2 "from-c2"))
  (go (<! (timeout 200)) (>! c3 "from-c3"))
  
  ;; Take from first available
  (go
    (let [[v ch] (alts! [c1 c2 c3])]
      (println "Got" v "from" (condp = ch
                                c1 "c1"
                                c2 "c2"
                                c3 "c3")))))
;; Prints: Got from-c1 from c1
```

### Workflow 3: Pub/Sub Pattern

```clojure
(require '[clojure.core.async :as async
           :refer [go go-loop <! >! <!! >!! chan pub sub unsub close!]])

;; Create publication on :topic key
(defn make-message [topic data]
  {:topic topic :data data})

(let [source (chan)
      publication (pub source :topic)
      
      ;; Subscribers for different topics
      news-sub (chan)
      sports-sub (chan)
      all-sub (chan)]
  
  ;; Subscribe channels to topics
  (sub publication :news news-sub)
  (sub publication :sports sports-sub)
  (sub publication :all all-sub)  ; Can subscribe to any topic
  
  ;; Consumers
  (go-loop []
    (when-let [msg (<! news-sub)]
      (println "News:" (:data msg))
      (recur)))
  
  (go-loop []
    (when-let [msg (<! sports-sub)]
      (println "Sports:" (:data msg))
      (recur)))
  
  (go-loop []
    (when-let [msg (<! all-sub)]
      (println "All:" (:data msg))
      (recur)))
  
  ;; Publisher
  (go
    (>! source (make-message :news "Breaking story"))
    (>! source (make-message :sports "Team wins!"))
    (>! source (make-message :all "General update"))
    (<! (timeout 100))
    (close! source)))

;; Prints:
;; News: Breaking story
;; Sports: Team wins!
;; All: General update
```

### Workflow 4: Mult for Broadcasting

```clojure
(require '[clojure.core.async :as async
           :refer [go go-loop <! >! <!! chan mult tap untap close!]])

;; Mult broadcasts to all tapped channels
(let [source (chan)
      m (mult source)
      
      ;; Create multiple tap channels
      tap1 (chan)
      tap2 (chan)
      tap3 (chan)]
  
  ;; Tap into mult
  (tap m tap1)
  (tap m tap2)
  (tap m tap3)
  
  ;; Each tap gets all messages
  (go-loop []
    (when-let [v (<! tap1)]
      (println "Tap1:" v)
      (recur)))
  
  (go-loop []
    (when-let [v (<! tap2)]
      (println "Tap2:" v)
      (recur)))
  
  (go-loop []
    (when-let [v (<! tap3)]
      (println "Tap3:" v)
      (recur)))
  
  ;; Send messages
  (go
    (doseq [i (range 3)]
      (>! source i))
    (close! source)))

;; Each tap prints:
;; Tap1: 0, Tap2: 0, Tap3: 0
;; Tap1: 1, Tap2: 1, Tap3: 1
;; Tap1: 2, Tap2: 2, Tap3: 2
```

### Workflow 5: Pipeline for Parallel Processing

```clojure
(require '[clojure.core.async :as async
           :refer [go <! >! <!! chan close! pipeline pipeline-blocking]])

;; pipeline applies transducer with parallelism
(defn process-items [items]
  (let [input (chan 100)
        output (chan 100)
        xf (comp
            (map #(do
                   (Thread/sleep 100)  ; Simulate work
                   (* % 2)))
            (filter even?))]
    
    ;; Start pipeline with parallelism 4
    (pipeline 4 output xf input)
    
    ;; Put items
    (go
      (doseq [item items]
        (>! input item))
      (close! input))
    
    ;; Collect results
    (go-loop [results []]
      (if-let [v (<! output)]
        (recur (conj results v))
        results))))

(<!! (process-items (range 20)))
;; => [0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38]

;; pipeline-blocking for blocking operations
(defn download-urls [urls]
  (let [input (chan)
        output (chan)
        xf (map (fn [url]
                  ;; Simulate blocking HTTP request
                  (Thread/sleep 500)
                  {:url url :status 200}))]
    
    ;; Use pipeline-blocking for blocking I/O
    (pipeline-blocking 5 output xf input)
    
    (go
      (doseq [url urls]
        (>! input url))
      (close! input))
    
    (go-loop [results []]
      (if-let [v (<! output)]
        (recur (conj results v))
        results))))
```

### Workflow 6: Merge Multiple Channels

```clojure
(require '[clojure.core.async :as async
           :refer [go go-loop <! >! <!! chan merge close! timeout]])

;; Merge combines multiple channels into one
(let [c1 (chan)
      c2 (chan)
      c3 (chan)
      merged (merge [c1 c2 c3])]
  
  ;; Producers on different channels
  (go
    (doseq [i (range 3)]
      (>! c1 (str "c1-" i))
      (<! (timeout 100)))
    (close! c1))
  
  (go
    (doseq [i (range 3)]
      (>! c2 (str "c2-" i))
      (<! (timeout 150)))
    (close! c2))
  
  (go
    (doseq [i (range 3)]
      (>! c3 (str "c3-" i))
      (<! (timeout 200)))
    (close! c3))
  
  ;; Consumer of merged channel
  (go-loop [results []]
    (if-let [v (<! merged)]
      (recur (conj results v))
      (do
        (println "All messages:" results)
        results))))

;; Collects all messages from all channels
```

### Workflow 7: Split Channel by Predicate

```clojure
(require '[clojure.core.async :as async
           :refer [go go-loop <! >! <!! chan split close!]])

;; Split channel into two based on predicate
(let [source (chan)
      [evens odds] (split even? source)]
  
  ;; Consumer for evens
  (go-loop []
    (when-let [v (<! evens)]
      (println "Even:" v)
      (recur)))
  
  ;; Consumer for odds
  (go-loop []
    (when-let [v (<! odds)]
      (println "Odd:" v)
      (recur)))
  
  ;; Producer
  (go
    (doseq [i (range 10)]
      (>! source i))
    (close! source)))

;; Prints:
;; Even: 0, Even: 2, Even: 4, Even: 6, Even: 8
;; Odd: 1, Odd: 3, Odd: 5, Odd: 7, Odd: 9
```

### Workflow 8: Mix for Complex Routing

```clojure
(require '[clojure.core.async :as async
           :refer [go go-loop <! >! <!! chan mix admix unmix toggle close!]])

;; Mix provides sophisticated channel mixing with mute/pause/solo
(let [out (chan)
      m (mix out)
      
      input1 (chan)
      input2 (chan)
      input3 (chan)]
  
  ;; Add inputs to mix
  (admix m input1)
  (admix m input2)
  (admix m input3)
  
  ;; Consumer
  (go-loop []
    (when-let [v (<! out)]
      (println "Mixed:" v)
      (recur)))
  
  ;; Send on all inputs
  (go
    (doseq [i (range 3)]
      (>! input1 (str "i1-" i))
      (>! input2 (str "i2-" i))
      (>! input3 (str "i3-" i)))
    
    ;; Solo mode - only soloed channels appear in output
    (toggle m {input1 {:solo true}})
    
    (<! (timeout 100))
    (>! input1 "solo-i1")
    (>! input2 "muted-i2")  ; Won't appear
    
    ;; Mute specific channel
    (toggle m {input1 {:solo false} input2 {:mute true}})
    
    (<! (timeout 100))
    (>! input1 "unmuted-i1")
    (>! input2 "muted-i2")   ; Won't appear
    (>! input3 "active-i3")
    
    (close! input1)
    (close! input2)
    (close! input3)))
```

## When to Use Each Approach

**Use core.async when:**
- Building event-driven or reactive systems
- Coordinating multiple async operations
- Need CSP-style concurrency
- Want to avoid callback hell
- Processing streams of data
- Building async workflows

**Use go blocks when:**
- Performing non-blocking async operations
- Coordinating channel operations
- Building lightweight concurrent tasks
- Want to avoid thread overhead
- NOT performing blocking I/O (use `thread` instead)

**Use thread blocks when:**
- Performing blocking I/O operations
- Need real OS thread (not go block thread pool)
- Blocking operations are unavoidable

**Use alts! when:**
- Waiting on multiple channels
- Implementing timeouts
- Racing multiple async operations
- Need non-deterministic choice

**Use pub/sub when:**
- Broadcasting messages by topic
- Multiple consumers interested in subsets of messages
- Dynamic subscription management

**Use mult when:**
- Broadcasting all messages to all consumers
- All consumers should see all messages
- Simple fan-out pattern

**Use pipeline when:**
- Parallel processing with transducers
- Controlled parallelism
- Ordered output relative to input

**Don't use core.async when:**
- Simple sequential operations suffice
- No need for coordination between tasks
- Working with futures/promises is simpler
- Blocking operations are dominant (consider `thread`)

## Best Practices

**DO:**
- Use go blocks for non-blocking operations
- Use `thread` for blocking I/O, not go blocks
- Close channels when done producing
- Check for nil when taking (indicates closed channel)
- Use buffered channels to prevent blocking
- Use `alts!` for timeouts and racing
- Use `pipeline` for parallel processing
- Keep go block code simple and fast
- Use transducers on channels for efficiency
- Consider `offer!` and `poll!` for non-blocking put/take

**DON'T:**
- Perform blocking operations in go blocks (use `thread`)
- Put nil values on channels (not allowed)
- Forget to close channels (can cause goroutine leaks)
- Share mutable state between go blocks (use channels)
- Perform long-running computations in go blocks
- Mix `<!` and `<!!` incorrectly (parking vs blocking)
- Ignore closed channel returns (nil)
- Create unbounded channels without backpressure
- Use core.async for simple async tasks (futures may suffice)

## Common Issues

### Issue: Deadlock - No Progress

**Problem:** Go blocks wait forever

```clojure
(let [c (chan)]
  (go
    ;; Waiting for someone to put
    (println (<! c)))
  ;; Nothing ever puts to channel
  )
;; Hangs forever
```

**Solution:** Ensure producers and consumers are balanced

```clojure
(let [c (chan)]
  (go
    (>! c "hello"))  ; Producer
  (go
    (println (<! c))))  ; Consumer
;; Prints: hello
```

### Issue: Blocking Operation in Go Block

**Problem:** Blocking I/O in go block starves thread pool

```clojure
;; WRONG - blocks go thread pool
(go
  (Thread/sleep 10000)  ; Blocks thread!
  (<! some-channel))
```

**Solution:** Use `thread` for blocking operations

```clojure
;; RIGHT - uses separate thread
(async/thread
  (Thread/sleep 10000)
  (<!! some-channel))
```

### Issue: Putting nil on Channel

**Problem:** nil is reserved for closed channels

```clojure
(let [c (chan)]
  (>!! c nil))
;; AssertionError: Can't put nil on channel
```

**Solution:** Use sentinel value or wrap in container

```clojure
(let [c (chan)]
  (>!! c ::nil-value)
  ;; Or
  (>!! c {:value nil}))
```

### Issue: Channel Buffer Full

**Problem:** Puts block when buffer full

```clojure
(let [c (chan 2)]  ; Buffer size 2
  (>!! c 1)
  (>!! c 2)
  (>!! c 3))  ; Blocks - buffer full!
```

**Solution:** Use larger buffer, dropping/sliding buffer, or take from channel

```clojure
;; Option 1: Larger buffer
(let [c (chan 10)]
  ...)

;; Option 2: Dropping buffer
(let [c (chan (async/dropping-buffer 2))]
  (>!! c 1)
  (>!! c 2)
  (>!! c 3))  ; Doesn't block, drops oldest

;; Option 3: Consumer
(let [c (chan 2)]
  (future
    (println (<!! c))
    (println (<!! c))
    (println (<!! c)))
  (>!! c 1)
  (>!! c 2)
  (>!! c 3))  ; Works - consumer drains
```

### Issue: Go Block Never Completes

**Problem:** Waiting on channel that's never closed

```clojure
(defn process-all [c]
  (go-loop [results []]
    (if-let [v (<! c)]
      (recur (conj results v))
      results)))

;; Channel never closed, loop never ends
(let [c (chan)]
  (>!! c 1)
  (>!! c 2)
  (<!! (process-all c)))  ; Hangs
```

**Solution:** Always close channels when done

```clojure
(let [c (chan)]
  (future
    (>!! c 1)
    (>!! c 2)
    (close! c))  ; Signal completion
  (<!! (process-all c)))  ; Completes
```

### Issue: Race Condition with Shared State

**Problem:** Multiple go blocks modifying shared atom

```clojure
(let [counter (atom 0)
      c (chan)]
  (dotimes [_ 100]
    (go
      (swap! counter inc)  ; Race condition!
      (>! c @counter)))
  ...)
```

**Solution:** Use channels for coordination, not shared mutable state

```clojure
(defn counter-process []
  (let [in (chan)
        out (chan)]
    (go-loop [count 0]
      (when-let [_ (<! in)]
        (>! out count)
        (recur (inc count))))
    {:in in :out out}))

(let [{:keys [in out]} (counter-process)]
  (dotimes [_ 100]
    (go
      (>! in :inc)
      (println (<! out)))))
```

## Advanced Topics

### Transducers on Channels

```clojure
(require '[clojure.core.async :as async :refer [chan go >! <! <!!]])

;; Channel with transducer
(def xf-chan (chan 10 (comp
                        (map inc)
                        (filter even?))))

(go
  (doseq [i (range 10)]
    (>! xf-chan i)))

(go
  (loop []
    (when-let [v (<! xf-chan)]
      (println v)  ; Only even numbers after inc
      (recur))))
;; Prints: 2 4 6 8 10
```

### Error Handling in Go Blocks

```clojure
(defn safe-process [c]
  (go
    (try
      (let [v (<! c)]
        (if (nil? v)
          {:error "Channel closed"}
          {:result (/ 100 v)}))
      (catch Exception e
        {:error (.getMessage e)}))))

(let [c (chan)]
  (go (>! c 0))  ; Division by zero
  (<!! (safe-process c)))
;; => {:error "Divide by zero"}
```

### Promise Channels

```clojure
(require '[clojure.core.async :as async :refer [promise-chan >!! <!!]])

;; Promise channel delivers exactly one value
(def p (promise-chan))

;; Multiple takes all get same value
(future (println "Take 1:" (<!! p)))
(future (println "Take 2:" (<!! p)))
(future (println "Take 3:" (<!! p)))

;; Deliver value
(>!! p "delivered")

;; Prints:
;; Take 1: delivered
;; Take 2: delivered
;; Take 3: delivered
```

### Offer! and Poll! for Non-blocking

```clojure
(require '[clojure.core.async :as async :refer [chan offer! poll!]])

(let [c (chan 2)]
  ;; offer! - non-blocking put
  (println (offer! c 1))    ; => true
  (println (offer! c 2))    ; => true
  (println (offer! c 3))    ; => false (full)
  
  ;; poll! - non-blocking take
  (println (poll! c))       ; => 1
  (println (poll! c))       ; => 2
  (println (poll! c)))      ; => nil (empty)
```

## Resources

- [Rationale](https://clojure.github.io/core.async/rationale.html)
- [API Documentation](https://clojure.github.io/core.async/)
- [Code Walkthrough](https://github.com/clojure/core.async/blob/master/examples/walkthrough.clj)
- [Rich Hickey on core.async](https://www.youtube.com/watch?v=yJxFPoxqzWE)
- [Tim Baldridge on core.async](https://www.youtube.com/watch?v=enwIIGzhahw)
- [Go Block Internals](https://www.youtube.com/watch?v=R3PZMIwXN_g)

## Summary

core.async provides CSP-style concurrency for Clojure:

1. **Channels** - Queue values between async processes
2. **Go blocks** - Lightweight concurrent code that parks, not blocks
3. **Channel operations** - `<!`, `>!`, `alts!` for coordination
4. **Patterns** - pub/sub, mult, merge, split, pipeline for complex flows
5. **Composable** - Build sophisticated async systems from simple parts

Use core.async for event-driven systems, reactive programming, async workflows, and anywhere you need to coordinate multiple concurrent operations with channels instead of callbacks or shared mutable state.
