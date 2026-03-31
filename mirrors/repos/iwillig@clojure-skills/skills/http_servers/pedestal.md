---
name: pedestal_web_framework
description: |
  Build production-ready web services and APIs with Pedestal's interceptor-based architecture.
  Use when building HTTP servers, REST APIs, WebSocket servers, async web applications, SSE streams,
  or when the user mentions Pedestal, web framework, interceptors, service architecture, async HTTP,
  or server-sent events. Pedestal emphasizes security by default, testability, and composable request processing.
---

# Pedestal Web Framework

High-performance, interceptor-based web framework for building secure, scalable services in Clojure.

## Quick Start

Pedestal can start tiny and scale up with your needs:

```clojure
(require '[io.pedestal.connector :as conn]
         '[io.pedestal.http.http-kit :as hk])

;; Define a handler
(defn greet-handler [_request]
  {:status 200
   :body "Hello, world!"})

;; Create and start server
(defn start []
  (-> (conn/default-connector-map 8080)
      (conn/with-default-interceptors)
      (conn/with-routes
        #{["/greet" :get greet-handler]})
      (hk/create-connector nil)
      (conn/start!)))

(def server (start))
;; Server running at http://localhost:8080/greet
```

**Key benefits:**
- **Interceptor-based** - Composable, testable request processing
- **Secure by default** - CSRF protection, secure headers built-in
- **Async-first** - Non-blocking I/O, SSE, and WebSockets
- **Multiple connectors** - Jetty, Http-Kit, Tomcat, Immutant
- **Production-ready** - Metrics, tracing, logging out of the box

## Core Concepts

### Interceptors

Interceptors are the fundamental unit of work in Pedestal. They're records with:

```clojure
{:name  :my-interceptor       ; Keyword identifier
 :enter (fn [context] ...)    ; Called on request
 :leave (fn [context] ...)    ; Called on response
 :error (fn [context ex] ...)} ; Called on errors
```

**Execution flow:**
1. Request arrives → `:enter` functions execute in order
2. Handler or interceptor adds `:response` to context
3. `:leave` functions execute in *reverse* order
4. Response sent to client

```clojure
;; Example interceptor
(def logging-interceptor
  {:name ::logging
   :enter (fn [context]
            (println "Request:" (get-in context [:request :uri]))
            context)
   :leave (fn [context]
            (println "Response:" (get-in context [:response :status]))
            context)})
```

### Context Map

The context map flows through the interceptor chain:

```clojure
{:request {...}           ; Request map (added by connector)
 :response {...}          ; Response map (added by handler/interceptor)
 :bindings {...}          ; Dynamic bindings
 :io.pedestal.interceptor.chain/queue [...]    ; Remaining interceptors
 :io.pedestal.interceptor.chain/stack [...]}   ; Executed interceptors
```

### Connectors

Pedestal supports multiple HTTP server connectors:

```clojure
;; Http-Kit (fast, simple, good for development)
(require '[io.pedestal.http.http-kit :as hk])
(hk/create-connector connector-map options)

;; Jetty 12 (production-grade, HTTP/2, WebSocket)
(require '[io.pedestal.http.jetty :as jetty])
(jetty/create-connector connector-map options)
```

## Common Workflows

### Workflow 1: REST API with Multiple Routes

```clojure
(require '[io.pedestal.connector :as conn]
         '[io.pedestal.http.http-kit :as hk]
         '[io.pedestal.http.body-params :as body-params]
         '[io.pedestal.http.route :as route])

;; Handlers
(defn list-users [_request]
  {:status 200
   :body {:users [{:id 1 :name "Alice"}
                  {:id 2 :name "Bob"}]}})

(defn get-user [request]
  (let [user-id (get-in request [:path-params :id])]
    {:status 200
     :body {:id user-id :name "Alice"}}))

(defn create-user [request]
  (let [user-data (get-in request [:json-params])]
    {:status 201
     :body {:id 3 :name (:name user-data)}}))

;; Routes using table syntax
(def routes
  #{["/api/users" :get list-users :route-name :list-users]
    ["/api/users/:id" :get get-user :route-name :get-user]
    ["/api/users" :post create-user :route-name :create-user]})

;; Create server
(defn create-server []
  (-> (conn/default-connector-map 8080)
      (conn/with-default-interceptors)
      (assoc ::conn/join? false)  ; Don't block on start
      ;; Add JSON body parsing
      (update ::conn/interceptors conj (body-params/body-params))
      (conn/with-routes routes)
      (hk/create-connector nil)))

(def server (conn/start! (create-server)))

;; Stop server
(conn/stop! server)
```

### Workflow 2: Custom Interceptors

```clojure
(require '[io.pedestal.interceptor :refer [interceptor]])

;; Authentication interceptor
(def require-auth
  (interceptor
    {:name ::require-auth
     :enter (fn [context]
              (let [token (get-in context [:request :headers "authorization"])]
                (if (valid-token? token)
                  (assoc-in context [:request :user] (decode-token token))
                  (assoc context :response {:status 401 :body "Unauthorized"}))))}))

;; Timing interceptor
(def timing
  (interceptor
    {:name ::timing
     :enter (fn [context]
              (assoc context ::start-time (System/nanoTime)))
     :leave (fn [context]
              (let [elapsed (- (System/nanoTime) (::start-time context))
                    elapsed-ms (/ elapsed 1000000.0)]
                (println "Request took" elapsed-ms "ms")
                context))}))

;; Use interceptors in routes
(def routes
  #{["/api/protected" :get 
     [timing require-auth protected-handler]
     :route-name :protected]})
```

### Workflow 3: Async Request Processing

```clojure
(require '[clojure.core.async :as async])

;; Async handler using core.async
(defn async-handler [request]
  (let [response-ch (async/chan)]
    ;; Return channel immediately
    (async/go
      ;; Do async work
      (async/<! (async/timeout 1000))  ; Simulate slow operation
      ;; Send response on channel
      (async/>! response-ch
        {:status 200
         :body "Async result"}))
    response-ch))

;; Or use interceptor
(def async-interceptor
  {:name ::async-work
   :enter (fn [context]
            (let [result-ch (async/chan)]
              (async/go
                ;; Async work here
                (let [result (async/<! (fetch-data-async))]
                  (async/>! result-ch
                    (assoc context :response
                      {:status 200 :body result}))))
              result-ch))})
```

### Workflow 4: Server-Sent Events (SSE)

```clojure
(require '[io.pedestal.http.sse :as sse])

;; Track connected clients
(def clients (atom #{}))

;; SSE handler
(defn sse-handler [request]
  (sse/start-stream
    (fn [stream]
      ;; Add client
      (swap! clients conj stream)
      
      ;; Send initial message
      (sse/send-event stream "connected" {:time (System/currentTimeMillis)})
      
      ;; Return cleanup function
      (fn []
        ;; Remove client on disconnect
        (swap! clients disj stream)))))

;; Broadcast to all clients
(defn broadcast! [event-name data]
  (doseq [stream @clients]
    (sse/send-event stream event-name data)))

;; Route
(def routes
  #{["/events" :get sse-handler :route-name :events]})

;; Usage
(broadcast! "update" {:message "Hello all clients"})
```

### Workflow 5: WebSockets

```clojure
(require '[io.pedestal.http.websockets :as ws])

;; WebSocket handlers
(def ws-handlers
  {:on-connect (fn [ws]
                 (println "Client connected:" ws))
   
   :on-text (fn [ws text]
              (println "Received:" text)
              ;; Echo back
              (ws/send-text ws (str "Echo: " text)))
   
   :on-binary (fn [ws bytes offset len]
                (println "Received binary data"))
   
   :on-close (fn [ws status-code reason]
               (println "Client disconnected:" reason))
   
   :on-error (fn [ws error]
               (println "WebSocket error:" error))})

;; Route with WebSocket upgrade
(def routes
  #{["/ws" :get (ws/websocket-handler ws-handlers)
     :route-name :websocket]})
```

### Workflow 6: Error Handling

```clojure
;; Error interceptor
(def error-handler
  {:name ::error-handler
   :error (fn [context ex]
            (let [status (case (type ex)
                          clojure.lang.ExceptionInfo 400
                          java.lang.IllegalArgumentException 400
                          500)]
              (assoc context :response
                {:status status
                 :body {:error (.getMessage ex)}})))})

;; Add to routes
(def routes
  #{["/api/*" :any error-handler :route-name :error-handler]
    ["/api/users" :get list-users :route-name :list-users]})

;; Or handle in handler
(defn safe-handler [request]
  (try
    {:status 200 :body (risky-operation)}
    (catch Exception e
      {:status 500 :body {:error (.getMessage e)}})))
```

### Workflow 7: Testing

```clojure
(require '[io.pedestal.test :refer [response-for]]
         '[clojure.test :refer [deftest is testing]])

;; Create test connector
(def test-connector
  (-> (conn/default-connector-map 8080)
      (conn/with-default-interceptors)
      (conn/with-routes routes)
      (hk/create-connector nil)))

(deftest test-api
  (testing "GET /api/users"
    (let [response (response-for test-connector :get "/api/users")]
      (is (= 200 (:status response)))
      (is (contains? (:body response) :users))))
  
  (testing "GET /api/users/:id"
    (let [response (response-for test-connector :get "/api/users/1")]
      (is (= 200 (:status response)))
      (is (= 1 (get-in response [:body :id])))))
  
  (testing "POST /api/users"
    (let [response (response-for test-connector 
                     :post "/api/users"
                     :headers {"Content-Type" "application/json"}
                     :body "{\"name\": \"Charlie\"}")]
      (is (= 201 (:status response))))))
```

## When to Use Each Approach

**Use handler functions when:**
- Simple request-response processing
- No shared state or preprocessing needed
- Quick prototypes and simple APIs

**Use interceptors when:**
- Need to share behavior across routes
- Authentication, authorization, logging
- Request preprocessing or response postprocessing
- Complex request pipelines

**Use async handlers when:**
- Long-running operations (database, external APIs)
- Don't want to block request threads
- Need high concurrency

**Use SSE when:**
- Server needs to push updates to clients
- One-way communication (server → client)
- Real-time feeds, notifications, dashboards

**Use WebSockets when:**
- Bidirectional real-time communication
- Chat applications, collaborative editing
- Game servers, live data streams

**Don't use Pedestal when:**
- Building simple static websites (use Ring directly)
- Need Rails-like conventions (use Luminus)
- Want automatic REST scaffolding

## Best Practices

**Do:**
- Name all interceptors with namespaced keywords
- Keep interceptors focused and composable
- Use async for long-running operations
- Test interceptors in isolation
- Use context map specs in development
- Leverage default interceptors (security, CORS, etc.)
- Clean up resources in :leave and WebSocket :on-close
- Use route-name for generating URLs

**Don't:**
- Block in interceptors (use async)
- Mutate the context map (return new version)
- Ignore :error handlers
- Forget to call (conn/stop! server) on shutdown
- Use handler functions for complex logic
- Skip security interceptors in production
- Store mutable state in interceptors

## Common Issues

### Issue: "Route not found"

```clojure
;; Check route definition
(def routes
  #{["/api/users" :get list-users :route-name :list-users]})

;; Ensure routes are added to connector
(conn/with-routes routes)

;; Check if path matches exactly
;; "/api/users/" is different from "/api/users"

;; Debug: print all routes
(require '[io.pedestal.http.route :as route])
(route/print-routes routes)
```

### Issue: "Context map missing :request"

```clojure
;; Wrong: accessing request directly
(defn handler [context]
  (:uri context))  ; :uri is in :request!

;; Right: access via :request key
(defn handler [context]
  (get-in context [:request :uri]))

;; Or use handler function (gets request directly)
(defn handler [request]
  (:uri request))
```

### Issue: "Interceptor not executing"

```clojure
;; Ensure interceptor is in the chain
(def routes
  #{["/api/users" :get 
     [logging-interceptor list-users]  ; Vector of interceptors
     :route-name :list-users]})

;; Check interceptor has :name
(def my-interceptor
  {:name ::my-interceptor  ; Required!
   :enter (fn [ctx] ctx)})

;; Verify interceptor returns context
(defn bad-interceptor [ctx]
  (println "Hi")
  nil)  ; Wrong! Must return context

(defn good-interceptor [ctx]
  (println "Hi")
  ctx)  ; Return context
```

### Issue: "Response not sent"

```clojure
;; Ensure :response is added to context
(def interceptor
  {:name ::my-interceptor
   :enter (fn [context]
            ;; Wrong: doesn't add :response
            context)})

;; Right: handler adds response
(defn handler [request]
  {:status 200 :body "OK"})

;; Or interceptor adds response
(def interceptor
  {:name ::my-interceptor
   :enter (fn [context]
            (assoc context :response
              {:status 200 :body "OK"}))})
```

### Issue: "WebSocket won't upgrade"

```clojure
;; Must use GET method for WebSocket
(def routes
  #{["/ws" :get (ws/websocket-handler handlers)]})
  ; Not :post or :any

;; Check headers in request
;; Connection: Upgrade
;; Upgrade: websocket

;; Ensure Jetty connector (Http-Kit doesn't support WebSockets)
(require '[io.pedestal.http.jetty :as jetty])
```

### Issue: "Async response hangs"

```clojure
;; Wrong: channel never gets value
(defn async-handler [request]
  (let [ch (async/chan)]
    ;; Forgot to put value on channel!
    ch))

;; Right: always put value on channel
(defn async-handler [request]
  (let [ch (async/chan)]
    (async/go
      (async/>! ch {:status 200 :body "OK"}))
    ch))

;; Or return response directly
(defn sync-handler [request]
  {:status 200 :body "OK"})
```

## Advanced Topics

### Route Constraints

```clojure
;; Constrain path parameters
(def routes
  #{["/api/users/:id" :get get-user
     :route-name :get-user
     :constraints {:id #"[0-9]+"}]})  ; Only numeric IDs
```

### Content Negotiation

```clojure
(require '[io.pedestal.http.content-negotiation :as content-neg])

(def negotiate-content
  (content-neg/negotiate-content
    ["application/json" "application/edn"]))

(def routes
  #{["/api/data" :get [negotiate-content data-handler]]})

(defn data-handler [request]
  (let [content-type (get-in request [:accept :field])]
    {:status 200
     :headers {"Content-Type" content-type}
     :body (case content-type
             "application/json" "{\"data\": \"value\"}"
             "application/edn" "{:data \"value\"}")}))
```

### CORS Configuration

```clojure
(require '[io.pedestal.http.cors :as cors])

(def cors-interceptor
  (cors/allow-origin
    {:allowed-origins ["http://localhost:3000"]
     :allowed-methods [:get :post :put :delete]
     :allowed-headers ["Authorization" "Content-Type"]}))

(-> connector-map
    (update ::conn/interceptors conj cors-interceptor))
```

### Metrics and Tracing

```clojure
;; Pedestal integrates with OpenTelemetry

;; Enable default metrics
(-> connector-map
    (assoc ::conn/enable-telemetry true))

;; Custom metrics interceptor
(def metrics-interceptor
  {:name ::metrics
   :enter (fn [context]
            (assoc context ::start (System/nanoTime)))
   :leave (fn [context]
            (let [duration (- (System/nanoTime) (::start context))]
              (record-metric! :request-duration duration)
              context))})
```

### Integration with Component

```clojure
(require '[com.stuartsierra.component :as component])

(defrecord PedestalComponent [config server]
  component/Lifecycle
  
  (start [this]
    (if server
      this
      (let [connector (-> (conn/default-connector-map (:port config))
                         (conn/with-default-interceptors)
                         (conn/with-routes routes)
                         (hk/create-connector nil))
            started (conn/start! connector)]
        (assoc this :server started))))
  
  (stop [this]
    (when server
      (conn/stop! server))
    (assoc this :server nil)))

(defn new-pedestal [config]
  (map->PedestalComponent {:config config}))
```

## Performance Considerations

- **Async overhead** - Only use async for truly slow operations
- **Interceptor chains** - Keep chains reasonably short (< 20 interceptors)
- **SSE connections** - Each connection holds a thread; monitor connection count
- **WebSocket messages** - Consider message size and frequency
- **Body parsing** - Parse request bodies only when needed
- **Logging** - Reduce logging in production hot paths

## Related Libraries

- `ring/ring` - Underlying HTTP abstraction
- `metosin/reitit` - Alternative routing library (can use with Pedestal)
- `http-kit/http-kit` - Fast HTTP server connector
- `stuartsierra/component` - Application lifecycle management
- `ring-cors/ring-cors` - CORS middleware

## External Resources

- [Official Documentation](https://pedestal.io)
- [GitHub Repository](https://github.com/pedestal/pedestal)
- [API Documentation](http://pedestal.io/api/0.8)
- [Pedestal Examples](https://github.com/pedestal/pedestal/tree/master/samples)
- [Clojurians Slack #pedestal](https://clojurians.slack.com/archives/C0K65B20P)

## Summary

Pedestal is a production-grade web framework with key strengths:

1. **Interceptor architecture** - Composable, testable request processing
2. **Multiple connectors** - Jetty, Http-Kit, Tomcat, Immutant
3. **Async by default** - Core.async channels, non-blocking I/O
4. **Real-time support** - SSE and WebSockets as first-class citizens
5. **Secure defaults** - CSRF protection, security headers built-in
6. **Production-ready** - Metrics, logging, tracing integrated

Use Pedestal when building services that need to scale, require security by default, or benefit from composable request processing. Its interceptor model provides exceptional flexibility and testability.
