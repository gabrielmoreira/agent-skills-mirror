# clj-otel: OpenTelemetry for Clojure

An idiomatic Clojure API for adding observability telemetry using OpenTelemetry. Use when you need distributed tracing, metrics collection, observability, or when the user mentions OpenTelemetry, spans, traces, telemetry, monitoring, or distributed systems observability.

## Quick Start

clj-otel provides a small, idiomatic API for adding traces and metrics telemetry to Clojure applications:

```clojure
;; Add dependency
{:deps {com.github.steffan-westcott/clj-otel-api {:mvn/version "0.2.10"}}}

;; Basic tracing
(require '[steffan-westcott.clj-otel.api.trace.span :as span])

(defn validate-profile [profile]
  (span/with-span! ["Validating profile" {:system/profile-id (:id profile)}]
    (validate profile)))

;; Basic metrics
(require '[steffan-westcott.clj-otel.api.metrics.instrument :as instrument])

(defonce password-failure-counter
  (instrument/instrument {:name "app.set-password-failure-count"
                          :instrument-type :counter}))

(instrument/add! password-failure-counter 
                 {:value 1
                  :attributes {:reason :too-short}})
```

To export telemetry, run your application with the OpenTelemetry Java agent:

```bash
# Download opentelemetry-javaagent.jar first
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.service.name=my-service \
     -Dotel.metrics.exporter=none \
     -Dotel.logs.exporter=none \
     -jar my-app.jar
```

## Core Concepts

### Spans and Traces

**Spans** represent a unit of work with a start time and duration. **Traces** are trees of spans that show the flow of work through a system.

```clojure
;; Create a span with attributes
(span/with-span! ["Process order" {:order/id order-id}]
  (process-order order-id))

;; Access current span
(span/get-span)  ; Returns span from bound or current context

;; Add data to existing span
(span/add-event! "Validation complete" {:validation/result "passed"})
(span/add-exception! e {:attributes {:context "order-processing"}})
```

### Context

Context carries cross-cutting concerns like the current span through the call stack. clj-otel uses both bound context (via dynamic binding) and current context (thread-local).

```clojure
;; Most operations use bound or current context by default
(span/with-span! "Operation"
  ;; Span is automatically in context
  (span/add-event! "Step 1"))

;; Explicitly pass context when needed
(let [ctx (span/new-span! "Custom span")]
  (span/add-event! "Event" {:context ctx})
  (span/end-span! {:context ctx}))
```

### Metrics Instruments

Instruments are the way to record measurements:

- **Counter**: Monotonically increasing value (HTTP requests, errors)
- **UpDownCounter**: Value that can increase or decrease (active connections)
- **Histogram**: Distribution of measurements (request duration, payload size)
- **Gauge**: Snapshot of current value (CPU usage, queue size)

```clojure
;; Define instruments once, use many times
(defonce request-counter
  (instrument/instrument {:name "http.server.requests"
                          :instrument-type :counter
                          :description "Total HTTP requests"}))

(defonce request-duration
  (instrument/instrument {:name "http.server.duration"
                          :instrument-type :histogram
                          :measurement-type :double
                          :unit "ms"
                          :description "HTTP request duration"}))
```

## Common Workflows

### Workflow 1: Basic Synchronous Tracing

Use `with-span!` to wrap synchronous operations:

```clojure
(require '[steffan-westcott.clj-otel.api.trace.span :as span])

(defn fetch-user [user-id]
  (span/with-span! ["Fetch user" {:user/id user-id}]
    ;; Query database
    (let [user (db/get-user user-id)]
      (span/add-event! "User retrieved" {:user/found (some? user)})
      user)))

(defn update-profile [user-id profile-data]
  (span/with-span! ["Update profile" {:user/id user-id}]
    (let [user (fetch-user user-id)]  ; Child span created automatically
      (when user
        (span/with-span! "Validate profile"
          (validate-profile profile-data))
        (span/with-span! "Save to database"
          (db/update-user user-id profile-data))))))
```

### Workflow 2: Asynchronous Code with CompletableFuture

Use `async-bound-cf-span` for CompletableFuture-based async code:

```clojure
(require '[steffan-westcott.clj-otel.api.trace.span :as span])

(defn async-fetch-user [user-id]
  (span/async-bound-cf-span ["Async fetch user" {:user/id user-id}]
    (-> (CompletableFuture/supplyAsync 
          (bound-fn []  ; Use bound-fn to carry context
            (db/get-user user-id)))
        (.thenApply (bound-fn [user]
                      (span/add-event! "User retrieved")
                      user)))))

;; Works with libraries like promesa, auspex, whew
(require '[promesa.core :as p])

(defn promesa-fetch [user-id]
  (span/async-bound-cf-span ["Promesa fetch" {:user/id user-id}]
    (p/let [user (p/future (db/get-user user-id))]
      (span/add-event! "Fetched via promesa")
      user)))
```

### Workflow 3: core.async Channels

Use chan-span namespace for core.async:

```clojure
(require '[steffan-westcott.clj-otel.api.trace.chan-span :as chan-span]
         '[clojure.core.async :as async])

(defn process-messages []
  (let [in-ch  (async/chan 10)
        out-ch (async/chan 10)]
    
    ;; Span propagates through channel pipeline
    (async/go-loop []
      (when-let [msg (async/<! in-ch)]
        (chan-span/with-chan-span! ["Process message" {:msg/id (:id msg)}]
          (let [result (process msg)]
            (async/>! out-ch result)))
        (recur)))
    
    {:in in-ch :out out-ch}))
```

### Workflow 4: Recording Metrics

Record measurements synchronously:

```clojure
(require '[steffan-westcott.clj-otel.api.metrics.instrument :as instrument])

;; Counter - always increases
(defonce request-counter
  (instrument/instrument {:name "http.requests"
                          :instrument-type :counter}))

(instrument/add! request-counter {:value 1
                                  :attributes {:method "GET"
                                               :route "/users"}})

;; Histogram - distribution of values
(defonce duration-histogram
  (instrument/instrument {:name "http.duration"
                          :instrument-type :histogram
                          :measurement-type :double
                          :unit "ms"}))

(let [start (System/currentTimeMillis)]
  (handle-request req)
  (let [duration (- (System/currentTimeMillis) start)]
    (instrument/record! duration-histogram {:value (double duration)
                                            :attributes {:route "/users"}})))

;; Gauge - current value
(defonce memory-gauge
  (instrument/instrument {:name "jvm.memory.used"
                          :instrument-type :gauge
                          :measurement-type :long
                          :unit "bytes"}))

(instrument/set! memory-gauge {:value (.getUsed (get-memory-usage))})
```

### Workflow 5: Asynchronous Metrics

Create instruments that observe values periodically:

```clojure
;; Async gauge - automatically observed
(def active-connections-gauge
  (instrument/instrument 
    {:name "http.server.active-connections"
     :instrument-type :gauge
     :description "Current active HTTP connections"}
    (fn []
      {:value (count @active-connections)
       :attributes {:server "main"}})))

;; Multiple measurements from one observation
(def pool-metrics
  (instrument/instrument
    {:name "db.pool.connections"
     :instrument-type :gauge}
    (fn []
      [{:value (count @pool-active) :attributes {:state "active"}}
       {:value (count @pool-idle) :attributes {:state "idle"}}])))

;; Close to stop observing
(.close active-connections-gauge)
```

### Workflow 6: Error Handling with Spans

Properly record exceptions in spans:

```clojure
(defn risky-operation [data]
  (span/with-span! ["Risky operation" {:data/size (count data)}]
    (try
      (process data)
      (catch Exception e
        ;; Automatically sets span status to :error
        (span/add-exception! e {:attributes {:data/type (type data)}})
        (throw e)))))

;; Custom exception attributes
(defn custom-error-handler [e]
  (span/add-exception! e
    {:attributes (fn [ex]
                   {:error/type (.getName (class ex))
                    :error/custom-field (extract-field ex)})}))
```

### Workflow 7: Ring Middleware

Add tracing to Ring handlers:

```clojure
(require '[steffan-westcott.clj-otel.api.trace.span :as span])

(defn wrap-with-tracing [handler]
  (span/wrap-span 
    handler
    (fn [request]
      ["HTTP request" {:http/method (:request-method request)
                       :http/route  (:uri request)}])))

;; For bound context (async handlers)
(defn wrap-with-bound-tracing [handler]
  (span/wrap-bound-span
    handler
    (fn [request]
      ["HTTP request" {:http/method (:request-method request)}])))

;; Use in Ring app
(def app
  (-> handler
      wrap-with-tracing
      wrap-params
      wrap-json-response))
```

### Workflow 8: Pedestal Interceptors

Create span interceptors for Pedestal:

```clojure
(require '[steffan-westcott.clj-otel.api.trace.span :as span]
         '[io.pedestal.interceptor :as interceptor])

(def tracing-interceptor
  (span/span-interceptor
    ::context
    (fn [ctx]
      (let [request (:request ctx)]
        ["HTTP request"
         {:http/method (:request-method request)
          :http/route  (get-in ctx [:route :route-name])}]))))

;; Add to interceptor chain
(def routes
  #{["/users/:id" :get
     [tracing-interceptor get-user-handler]]})
```

## When to Use Each Approach

### Synchronous vs Asynchronous Spans

**Use `with-span!` when:**
- Code is purely synchronous
- No async operations in the body
- Simplest case with automatic cleanup

**Use `async-bound-cf-span` when:**
- Working with CompletableFuture
- Using promesa, auspex, whew libraries
- Need automatic span ending on completion

**Use `async-span` when:**
- Building custom async abstractions
- Need full control over context passing
- Working with callback-based libraries

**Use chan-span functions when:**
- Working with core.async channels
- Need context propagation through go blocks
- Building channel pipelines

### Metrics Instrument Types

**Use Counter when:**
- Value only increases
- Counting events (requests, errors, messages)
- Example: Total HTTP requests processed

**Use UpDownCounter when:**
- Value can increase or decrease
- Tracking current state changes
- Example: Active connections, items in queue

**Use Histogram when:**
- Need distribution of values
- Measuring duration, size, or other distributions
- Example: Request latency, payload sizes

**Use Gauge when:**
- Measuring current value at observation time
- Snapshot metrics
- Example: Memory usage, CPU load, queue depth

### Synchronous vs Asynchronous Instruments

**Use synchronous instruments when:**
- Taking measurements in response to events
- You control when measurements happen
- Example: Record request duration after handling

**Use asynchronous instruments when:**
- Values change independently of your code
- Need periodic sampling
- Example: Current memory usage, active threads

## Best Practices

**DO:**
- Use meaningful span names that describe the operation
- Add relevant attributes to spans (user IDs, transaction IDs, etc.)
- Create instruments once and reuse them (use `defonce`)
- Use appropriate instrument types for your metrics
- Always propagate context in async code with `bound-fn`
- Record exceptions in spans with `add-exception!`
- Use semantic conventions for attributes when available
- Keep attribute cardinality low to avoid metric explosion
- Close asynchronous instruments when no longer needed

**DON'T:**
- Create new instruments for every measurement
- Use high-cardinality attributes (like timestamps, UUIDs)
- Forget to end spans (causes memory leaks and broken traces)
- Mix synchronous and asynchronous instrument approaches
- Ignore context when working with async code
- Create spans for trivial operations (causes noise)
- Put sensitive data in span attributes
- Use span names with high cardinality

## Configuration

### Runtime Configuration with Java Agent

Configure via JVM properties or environment variables:

```bash
# JVM properties
-Dotel.service.name=my-service
-Dotel.traces.exporter=otlp
-Dotel.metrics.exporter=otlp
-Dotel.logs.exporter=none
-Dotel.exporter.otlp.endpoint=http://localhost:4318

# Or environment variables
export OTEL_SERVICE_NAME=my-service
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

### Programmatic SDK Configuration

For more control, configure the OpenTelemetry SDK programmatically:

```clojure
(require '[steffan-westcott.clj-otel.sdk.otel-sdk :as sdk])

(def otel-instance
  (sdk/build-otel-sdk
    {:service-name "my-service"
     :traces {:exporter :otlp
              :endpoint "http://localhost:4318"}
     :metrics {:exporter :otlp
               :interval-millis 30000}}))

;; Set as default
(steffan-westcott.clj-otel.api.otel/set-default-otel-sdk! otel-instance)
```

### Custom Tracer and Meter

Create custom tracer/meter for library instrumentation:

```clojure
;; Custom tracer for your library
(def my-tracer
  (span/get-tracer {:name "com.example.my-library"
                    :version "1.0.0"
                    :schema-url "https://example.com/schema"}))

(span/set-default-tracer! my-tracer)

;; Custom meter for your library
(def my-meter
  (instrument/get-meter {:name "com.example.my-library"
                         :version "1.0.0"}))

(instrument/set-default-meter! my-meter)
```

## Common Issues

### Issue: Spans Not Appearing in Backend

**Problem:** Created spans but nothing shows in Jaeger/Zipkin

**Solution:** Ensure the Java agent is loaded and exporter is configured:

```bash
# Check agent is loaded
-javaagent:path/to/opentelemetry-javaagent.jar

# Check service name is set
-Dotel.service.name=my-service

# Check exporter is configured
-Dotel.traces.exporter=otlp
-Dotel.exporter.otlp.endpoint=http://localhost:4318

# Enable debug logging
-Dotel.javaagent.debug=true
```

### Issue: Context Lost in Async Code

**Problem:** Child spans not linked to parent in async operations

**Solution:** Use `bound-fn` or appropriate async span functions:

```clojure
;; Wrong - context lost
(CompletableFuture/supplyAsync 
  #(child-operation))

;; Right - context preserved
(span/async-bound-cf-span "Parent"
  (CompletableFuture/supplyAsync 
    (bound-fn []
      (span/with-span! "Child"
        (child-operation)))))
```

### Issue: Metrics Not Updating

**Problem:** Gauge or async instrument not showing current values

**Solution:** Ensure the observe function returns correct format:

```clojure
;; Wrong - returns raw value
(instrument/instrument {...} 
  (fn [] 42))

;; Right - returns map with :value
(instrument/instrument {...}
  (fn [] {:value 42 :attributes {:type "example"}}))

;; Multiple measurements
(instrument/instrument {...}
  (fn [] [{:value 10 :attributes {:state "active"}}
          {:value 5 :attributes {:state "idle"}}]))
```

### Issue: High Cardinality Warnings

**Problem:** Backend complaining about too many unique metric combinations

**Solution:** Reduce attribute cardinality:

```clojure
;; Wrong - unbounded cardinality
(instrument/add! counter {:value 1
                          :attributes {:user-id user-id    ; Could be millions
                                       :timestamp (System/currentTimeMillis)}})

;; Right - bounded cardinality
(instrument/add! counter {:value 1
                          :attributes {:user-tier (get-tier user-id)  ; Few values
                                       :region region}})                 ; Few values
```

### Issue: Memory Leaks from Unclosed Spans

**Problem:** Memory usage grows over time, broken traces

**Solution:** Always end spans, especially with low-level API:

```clojure
;; Wrong - span never ends
(let [ctx (span/new-span! "Operation")]
  (do-work))

;; Right - explicitly end span
(let [ctx (span/new-span! "Operation")]
  (try
    (do-work)
    (finally
      (span/end-span! {:context ctx}))))

;; Better - use with-span! for automatic cleanup
(span/with-span! "Operation"
  (do-work))
```

### Issue: Spans Missing Attributes

**Problem:** Spans created but missing expected attributes

**Solution:** Check attribute format and timing:

```clojure
;; Attributes in span creation
(span/with-span! ["Operation" {:user/id user-id
                                :order/total total}]
  (process-order))

;; Add attributes after creation
(span/add-span-data! {:attributes {:result "success"
                                   :items-processed count}})
```

## Advanced Topics

For comprehensive API documentation, see [clj-otel API reference](https://cljdoc.org/d/com.github.steffan-westcott/clj-otel-api)

For detailed examples including:
- Manifold deferreds integration
- Missionary tasks integration  
- HTTP semantic conventions
- Custom propagators
- Jaeger remote sampling
- Multi-backend export

See the [examples directory](https://github.com/steffan-westcott/clj-otel/tree/master/examples) in the GitHub repository.

## Resources

- [OpenTelemetry Official Documentation](https://opentelemetry.io/docs/)
- [Semantic Conventions](https://github.com/open-telemetry/semantic-conventions)
- [clj-otel Tutorial](https://cljdoc.org/d/com.github.steffan-westcott/clj-otel-api/CURRENT/doc/tutorial)
- [clj-otel Slack Channel](https://clojurians.slack.com/messages/clj-otel)

## Summary

clj-otel provides idiomatic Clojure APIs for OpenTelemetry:

1. **Traces** - Use `with-span!` for sync, `async-bound-cf-span` for async operations
2. **Metrics** - Create instruments once with `instrument`, record measurements with `add!`, `record!`, `set!`
3. **Context** - Automatically managed in most cases, use `bound-fn` for async code
4. **Configuration** - Use Java agent properties or programmatic SDK setup
5. **Integration** - Works with Ring, Pedestal, core.async, promesa, manifold, and more

Master observability in Clojure by combining manual instrumentation with automatic Java agent instrumentation for comprehensive distributed system visibility.
