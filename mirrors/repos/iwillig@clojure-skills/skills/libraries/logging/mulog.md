---
name: mulog_event_logging
description: |
  Event-based logging library that logs structured data, not text messages. Use when 
  tracking events, distributed tracing, observability, metrics collection, or when the 
  user mentions mulog, event logging, structured events, data-driven logging, μ/log, 
  micro-logging, distributed tracing, log aggregation, event tracking, or observability.
---

# μ/log (mulog)

μ/log is a micro-logging library that logs events as data, not text messages. Designed for modern cloud-based distributed systems with centralized log aggregation.

## Quick Start

```clojure
;; Add dependency
{:deps {com.brunobonacci/mulog {:mvn/version "0.9.0"}}}

;; Require the namespace
(require '[com.brunobonacci.mulog :as μ])

;; Start a publisher (console for development)
(def publisher (μ/start-publisher! {:type :console :pretty? true}))

;; Log an event
(μ/log ::user-logged 
  :user-id "12345" 
  :remote-ip "1.2.3.4" 
  :auth-method :password-login)
;; => nil

;; Event logged:
;; {:mulog/trace-id #mulog/flake "4VTF9QBbnef57vxVy-b4uKzh7dG7r7y4",
;;  :mulog/timestamp 1587500402972,
;;  :mulog/event-name :your-ns/user-logged,
;;  :mulog/namespace "your-ns",
;;  :user-id "12345",
;;  :remote-ip "1.2.3.4",
;;  :auth-method :password-login}

;; Stop publisher when done
(publisher)
```

**Key benefits:**
- Extremely fast (under 300 nanoseconds per event)
- Logs events as data structures, not strings
- Memory-bound with no unbounded memory use
- Asynchronous processing and rendering
- Rich publisher ecosystem
- Built-in distributed tracing support

## Core Concepts

### Events as Data

μ/log treats logs as structured events with arbitrary key-value pairs:

```clojure
;; Traditional logging (string-based)
;; (log/info "User 12345 logged in from 1.2.3.4")

;; μ/log (data-based)
(μ/log ::user-logged :user-id "12345" :remote-ip "1.2.3.4")
```

**Why this matters:**
- No need to parse strings later
- Easy to query, filter, aggregate
- Natural fit for tools like Elasticsearch
- Rich dimensional data for analysis

### Event Structure

All events automatically include:
- `:mulog/trace-id` - Unique event identifier (flake ID)
- `:mulog/timestamp` - Millisecond-precision timestamp
- `:mulog/event-name` - The event name (namespaced keyword)
- `:mulog/namespace` - The namespace where event was logged

Plus any custom key-value pairs you add.

### Global Context

Global context adds properties to ALL subsequent events:

```clojure
;; Set once at application startup
(μ/set-global-context! 
  {:app-name "my-service"
   :version "1.2.3"
   :env "production"
   :host "server-01"})

;; Now all events include these properties
(μ/log ::order-created :order-id "ord-123")
;; Includes: :app-name, :version, :env, :host

;; Update global context
(μ/update-global-context! assoc :deploy-id "deploy-456")
```

**Best practice:** Set global context in your `-main` function with application-wide properties.

### Local Context

Local context is thread-local and scoped to a block:

```clojure
;; Context applies to all logs in scope
(μ/with-context {:request-id "req-789" :user-id "user-456"}
  (μ/log ::api-call :endpoint "/api/orders" :method "POST")
  (process-order)
  (μ/log ::api-response :status 200))

;; Both events include :request-id and :user-id

;; Context nests
(μ/with-context {:transaction-id "tx-098765"}
  (μ/with-context {:order-id "ord-123"}
    (μ/log ::item-processed :item-id "sku-456" :quantity 2)))
;; Event includes both :transaction-id and :order-id
```

Local context propagates through function calls in the same thread.

### Distributed Tracing with μ/trace

μ/trace automatically tracks operation duration and outcome:

```clojure
;; Wrap operations to track duration and errors
(μ/trace ::database-query
  [:table "orders" :query-type "select"]
  (db/fetch-orders))

;; Automatically logs:
;; {:mulog/trace-id #mulog/flake "...",
;;  :mulog/event-name ::database-query,
;;  :mulog/timestamp 1587504242983,
;;  :mulog/duration 254402837,  ; nanoseconds
;;  :mulog/outcome :ok,          ; or :error
;;  :mulog/root-trace #mulog/flake "...",
;;  :mulog/parent-trace #mulog/flake "...",
;;  :table "orders",
;;  :query-type "select"}
```

**μ/trace features:**
- Measures duration in nanoseconds
- Tracks `:outcome` (`:ok` or `:error`)
- Links parent/child traces
- Adds exception details on errors
- Supports result capture

## Common Workflows

### Workflow 1: Application Initialization

Set up μ/log at application startup:

```clojure
(ns my-app.core
  (:require [com.brunobonacci.mulog :as μ]))

(defn -main [& args]
  ;; Set global context first
  (μ/set-global-context!
    {:app-name "my-service"
     :version (System/getProperty "app.version" "dev")
     :env (System/getenv "ENV")
     :host (.getHostName (java.net.InetAddress/getLocalHost))
     :pid (.pid (java.lang.ProcessHandle/current))})
  
  ;; Start publisher(s)
  (def publisher
    (μ/start-publisher!
      {:type :console :pretty? true}))
  
  ;; Log startup event
  (μ/log ::application-started :init-time 250)
  
  ;; Application logic
  (start-server)
  
  ;; Shutdown hook
  (.addShutdownHook
    (Runtime/getRuntime)
    (Thread. (fn []
               (μ/log ::application-stopping)
               (publisher)))))
```

### Workflow 2: HTTP Request Logging

Track requests with contextual information:

```clojure
(require '[com.brunobonacci.mulog :as μ])

(defn wrap-logging [handler]
  (fn [request]
    (let [request-id (or (get-in request [:headers "x-request-id"])
                         (str (java.util.UUID/randomUUID)))]
      (μ/with-context
        {:request-id request-id
         :user-id (get-in request [:session :user-id])
         :remote-ip (:remote-addr request)}
        
        (μ/log ::http-request-start
          :method (:request-method request)
          :path (:uri request))
        
        (let [start (System/nanoTime)
              response (handler request)
              duration (- (System/nanoTime) start)]
          
          (μ/log ::http-request-complete
            :method (:request-method request)
            :path (:uri request)
            :status (:status response)
            :duration-ms (/ duration 1000000.0))
          
          response)))))

;; Or use μ/trace for automatic timing
(defn wrap-logging-trace [handler]
  (fn [request]
    (μ/with-context
      {:request-id (or (get-in request [:headers "x-request-id"])
                       (str (java.util.UUID/randomUUID)))
       :user-id (get-in request [:session :user-id])}
      
      (μ/trace ::http-request
        [:method (:request-method request)
         :path (:uri request)]
        (handler request)))))
```

### Workflow 3: Database Operation Tracing

Track database operations with automatic timing:

```clojure
(require '[com.brunobonacci.mulog :as μ]
         '[next.jdbc :as jdbc])

(defn fetch-user [db user-id]
  (μ/trace ::database-query
    [:table "users"
     :operation "select"
     :user-id user-id]
    (jdbc/execute-one! db ["SELECT * FROM users WHERE id = ?" user-id])))

(defn create-order [db order-data]
  (μ/trace ::database-insert
    [:table "orders"
     :operation "insert"]
    (jdbc/execute-one! db
      ["INSERT INTO orders (user_id, total) VALUES (?, ?)"
       (:user-id order-data)
       (:total order-data)]
      {:return-keys true})))

;; With error handling
(defn safe-db-operation [db f]
  (try
    (μ/trace ::database-operation
      []
      (f db))
    (catch Exception e
      (μ/log ::database-error
        :exception e
        :error-type (class e)
        :message (.getMessage e))
      (throw e))))
```

### Workflow 4: Capturing Results from Traces

Capture specific fields from operation results:

```clojure
;; Capture HTTP response status
(μ/trace ::http-call
  {:pairs [:url "https://api.example.com/users"]
   :capture (fn [response]
              {:http-status (:status response)
               :content-length (get-in response [:headers "content-length"])})}
  (http/get "https://api.example.com/users"))

;; Result includes :http-status and :content-length

;; Capture database query results
(μ/trace ::user-search
  {:pairs [:search-term "alice"]
   :capture (fn [results]
              {:result-count (count results)
               :has-results (pos? (count results))})}
  (db/search-users "alice"))
```

### Workflow 5: Nested Distributed Traces

Track operations across multiple service layers:

```clojure
(defn process-order [order-data]
  (μ/trace ::process-order
    [:order-id (:order-id order-data)]
    
    ;; Nested trace: validate
    (μ/trace ::validate-order
      []
      (validate-order-data order-data))
    
    ;; Nested trace: check inventory
    (μ/trace ::check-inventory
      [:items (count (:items order-data))]
      (check-item-availability (:items order-data)))
    
    ;; Nested trace: payment
    (μ/trace ::process-payment
      [:amount (:total order-data)]
      (charge-payment (:payment order-data)))
    
    ;; Final result
    {:status :success :order-id (:order-id order-data)}))

;; Produces trace hierarchy:
;; ::process-order (parent)
;;   └── ::validate-order (child, shares parent-trace)
;;   └── ::check-inventory (child, shares parent-trace)
;;   └── ::process-payment (child, shares parent-trace)
```

### Workflow 6: Using Multiple Publishers

Send events to multiple destinations:

```clojure
;; Multiple publishers via :multi type
(def publishers
  (μ/start-publisher!
    {:type :multi
     :publishers
     [{:type :console :pretty? true}
      {:type :simple-file :filename "/var/log/app/events.log"}
      {:type :elasticsearch
       :url "http://localhost:9200"
       :index-pattern "mulog-YYYY.MM.dd"}]}))

;; Or start separately
(def console-pub (μ/start-publisher! {:type :console}))
(def file-pub (μ/start-publisher! {:type :simple-file :filename "/tmp/events.log"}))

;; Stop all
(publishers) ; for multi
;; or
(console-pub)
(file-pub)
```

### Workflow 7: Error and Exception Logging

Properly log errors with context:

```clojure
;; Basic error logging
(try
  (risky-operation)
  (catch Exception e
    (μ/log ::operation-failed
      :exception e
      :operation "risky-operation"
      :reason (.getMessage e))))

;; With μ/trace (automatic exception capture)
(μ/trace ::risky-operation
  [:operation-type "data-import"]
  (import-data source))
;; On exception:
;; - :mulog/outcome :error
;; - :exception <exception object>
;; - Original exception is re-thrown

;; Defensive logging before throwing
(defn validate-input [input]
  (when-not (valid? input)
    (μ/log ::validation-failed
      :input input
      :reason "invalid format")
    (throw (ex-info "Invalid input" {:input input}))))
```

## Publishers

μ/log supports many publishers for different backends:

**Development:**
- `:console` - Print to stdout (development only)
- `:simple-file` - Write to file in EDN format

**Production:**
- `:elasticsearch` - Send to Elasticsearch
- `:kafka` - Send to Kafka topics
- `:kinesis` - Send to AWS Kinesis
- `:cloudwatch` - Send to AWS CloudWatch Logs
- `:zipkin` - Send traces to Zipkin
- `:prometheus` - Expose metrics endpoint
- `:slack` - Send alerts to Slack
- `:opentelemetry` - Send to OpenTelemetry collector

**Example configurations:**

```clojure
;; Console (development)
{:type :console :pretty? true}

;; Elasticsearch
{:type :elasticsearch
 :url "http://localhost:9200"
 :index-pattern "mulog-YYYY.MM.dd"}

;; Kafka
{:type :kafka
 :kafka {:bootstrap.servers "localhost:9092"}
 :topic "mulog-events"}

;; CloudWatch
{:type :cloudwatch
 :log-group-name "/aws/lambda/my-function"
 :log-stream-name "2024/11/11/my-stream"}

;; Multi-publisher
{:type :multi
 :publishers
 [{:type :console}
  {:type :elasticsearch :url "http://es:9200"}]}
```

## When to Use Each Approach

**Use μ/log when:**
- Logging discrete events (user actions, API calls, errors)
- You need rich contextual data
- Events happen at a single point in time
- You want to query and aggregate logs

**Use μ/trace when:**
- Tracking operation duration
- Need automatic error tracking
- Building distributed traces
- Want to measure performance
- Operations span time (database calls, HTTP requests)

**Use with-context when:**
- You have request-scoped data (request ID, user ID)
- Processing spans multiple function calls
- Need consistent context across operations
- Context applies to a logical unit of work

**Use set-global-context! when:**
- Application-wide properties (app name, version, environment)
- Properties valid for entire process lifetime
- Information needed in every single event

## Best Practices

**DO:**
- Use namespaced keywords for event names (`:my-ns/user-logged`)
- Log plain values, not opaque objects
- Set global context at application startup
- Use `:exception` key for exception objects
- Add dimensional data (IDs, status codes, etc.)
- Use μ/trace for operations with duration
- Track outcomes (`:status :success`, `:status :failed`)
- Log timestamps with millisecond precision (automatic)
- Use publishers appropriate for environment (console for dev, Elasticsearch for prod)

**DON'T:**
- Log deeply nested maps (hard to query)
- Log mutable objects (async rendering may see different state)
- Construct log messages as strings
- Skip global context setup
- Use println or other text logging
- Log passwords or sensitive data
- Create unbounded log volume

## Common Issues

### Issue: Events Not Appearing

**Problem:** Logged events but nothing appears.

```clojure
(μ/log ::my-event :data "value")
;; Nothing shows up
```

**Solution:** Start a publisher first.

```clojure
;; Start publisher BEFORE logging
(def publisher (μ/start-publisher! {:type :console}))

(μ/log ::my-event :data "value")
;; Now it appears
```

### Issue: Events Missing Context

**Problem:** Expected context properties don't appear in events.

```clojure
(μ/set-global-context! {:app-name "my-app"})
(μ/log ::test)
;; :app-name not in event
```

**Solution:** Global context only applies to events logged AFTER it's set.

```clojure
;; Set context FIRST
(μ/set-global-context! {:app-name "my-app"})

;; Then log
(μ/log ::test)
;; Now includes :app-name
```

### Issue: Local Context Not Propagating

**Problem:** Context doesn't appear in nested function calls.

```clojure
(defn inner-fn []
  (μ/log ::inner-event))

(μ/with-context {:request-id "123"}
  (inner-fn))
;; :request-id missing from ::inner-event
```

**Solution:** Local context only propagates in the same thread. If you spawn threads, you need to explicitly transfer context.

```clojure
;; Works (same thread)
(defn inner-fn []
  (μ/log ::inner-event))

(μ/with-context {:request-id "123"}
  (inner-fn))
;; :request-id appears

;; For new threads, capture and restore context
(let [ctx (μ/local-context)]
  (future
    (μ/with-context ctx
      (μ/log ::async-event))))
```

### Issue: Performance Impact

**Problem:** Logging too many events impacts performance.

**Solution:** μ/log is designed to be fast (under 300ns per event), but:

```clojure
;; DON'T log in tight loops
(doseq [item (range 1000000)]
  (μ/log ::processing :item item)) ; Bad!

;; DO log summary events
(μ/log ::processing-started :count 1000000)
(doseq [item (range 1000000)]
  (process item))
(μ/log ::processing-complete :count 1000000 :duration-ms elapsed)

;; Or sample events
(doseq [item (range 1000000)]
  (when (zero? (mod item 10000))
    (μ/log ::processing-checkpoint :item item)))
```

### Issue: Trace Duration in Wrong Units

**Problem:** Duration values look wrong.

```clojure
(μ/trace ::operation [] (do-work))
;; :mulog/duration 254402837
;; What unit is this?
```

**Solution:** Duration is always in **nanoseconds**. Convert to milliseconds:

```clojure
;; In your query/visualization layer
(/ duration 1000000.0) ; nanoseconds to milliseconds
(/ duration 1000000000.0) ; nanoseconds to seconds
```

## Advanced Topics

### Custom Publishers

Create custom publishers for specific needs:

```clojure
(defn custom-publisher [{:keys [config]}]
  (let [running (atom true)]
    {:publisher-fn
     (fn [events]
       (doseq [event events]
         (my-custom-handler event)))
     
     :stop-fn
     (fn []
       (reset! running false))}))

;; Register and use
(μ/start-publisher! {:type :custom :publisher custom-publisher})
```

See [custom publishers documentation](https://github.com/BrunoBonacci/mulog#custom-publishers) for details.

### Sampling and Filtering

Filter events before publishing:

```clojure
;; Only log errors
(defn error-filter [events]
  (filter #(= :error (:mulog/outcome %)) events))

;; Sample 10% of events
(defn sample-filter [events]
  (filter #(< (rand) 0.1) events))
```

## Resources

- [GitHub Repository](https://github.com/BrunoBonacci/mulog)
- [API Documentation](https://cljdoc.org/d/com.brunobonacci/mulog)
- [Publisher Documentation](https://github.com/BrunoBonacci/mulog/tree/master/doc/publishers)
- [Talk: μ/log and the Next 100 Logging Systems](https://www.youtube.com/watch?v=P1149dWnl3k)

## Summary

μ/log revolutionizes logging by treating logs as structured events rather than text messages. Key points:

1. **Events as data** - Log structured events with arbitrary key-value pairs
2. **Fast and async** - Under 300ns per event, non-blocking
3. **Rich context** - Global and local context for dimensional data
4. **Distributed tracing** - Built-in μ/trace for tracking operations
5. **Publisher ecosystem** - Send events to Elasticsearch, Kafka, CloudWatch, and more
6. **Memory safe** - Bounded memory usage, drops events before crashing

Start with console publisher for development, then use Elasticsearch or similar for production. Always set global context at startup and use local context for request-scoped data.
