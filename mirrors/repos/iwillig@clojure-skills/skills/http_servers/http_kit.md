---
name: http-kit-server
description: |
  Build high-performance async HTTP servers and WebSocket applications with http-kit. 
  Use when creating web servers, REST APIs, WebSocket servers, async HTTP responses, 
  long-polling, or when the user mentions http-kit, HTTP server, web server, WebSocket, 
  async web, or streaming responses.
---

# http-kit Server

## Quick Start

http-kit is a highly concurrent HTTP server that supports WebSockets, async responses, and long-polling out of the box.

```clojure
(require '[org.httpkit.server :as http])

;; Define a simple Ring handler
(defn handler [req]
  {:status 200
   :headers {"Content-Type" "text/html"}
   :body "Hello, World!"})

;; Start the server
(def server (http/run-server handler {:port 8080}))
;; Server running at http://localhost:8080

;; Stop the server
(server :timeout 100)  ; Waits up to 100ms for connections to close
```

**Key benefits:**
- **High performance** - Handles thousands of concurrent connections
- **WebSocket support** - Built-in WebSocket protocol support
- **Async responses** - Non-blocking I/O for scalability
- **Ring compatible** - Works with standard Ring middleware
- **Simple API** - Minimal setup, easy to use

## Core Concepts

### Ring Compatibility

http-kit implements the Ring spec, so standard Ring handlers work:

```clojure
(defn ring-handler [request]
  {:status 200
   :headers {"Content-Type" "application/json"}
   :body "{\"message\": \"Hello\"}"})

(def server (http/run-server ring-handler {:port 8080}))
```

### Async Channels

For async responses, use `as-channel` to get the underlying channel:

```clojure
(require '[org.httpkit.server :refer [as-channel send!]])

(defn async-handler [req]
  (as-channel req
    {:on-open (fn [ch]
                (future
                  (Thread/sleep 1000)  ; Simulate async work
                  (send! ch {:status 200
                            :headers {"Content-Type" "text/plain"}
                            :body "Async response"}
                        true)))}))  ; true = close after send
```

### Server Lifecycle

```clojure
;; Start server (returns HttpServer object)
(def server (http/run-server handler {:port 8080 
                                      :legacy-return-value? false}))

;; Check server status
(http/server-status server)  ; => :running

;; Get server port
(http/server-port server)    ; => 8080

;; Stop server (returns promise)
(http/server-stop! server {:timeout 100})

;; Wait for server to fully stop
@(http/server-stop! server)
```

## Common Workflows

### Workflow 1: Basic REST API

```clojure
(require '[org.httpkit.server :as http]
         '[clojure.data.json :as json])

(defn api-handler [req]
  (case (:uri req)
    "/api/health"
    {:status 200
     :headers {"Content-Type" "application/json"}
     :body (json/write-str {:status "healthy"})}
    
    "/api/users"
    {:status 200
     :headers {"Content-Type" "application/json"}
     :body (json/write-str [{:id 1 :name "Alice"}
                            {:id 2 :name "Bob"}])}
    
    ;; 404 for everything else
    {:status 404
     :headers {"Content-Type" "application/json"}
     :body (json/write-str {:error "Not found"})}))

(def server (http/run-server api-handler {:port 8080}))
```

### Workflow 2: WebSocket Server

```clojure
(require '[org.httpkit.server :refer [as-channel send! close websocket?]])

(def clients (atom #{}))

(defn ws-handler [req]
  (if (websocket? req)
    (as-channel req
      {:on-open (fn [ch]
                  (swap! clients conj ch)
                  (println "Client connected:" ch))
       
       :on-receive (fn [ch message]
                     (println "Received:" message)
                     ;; Echo back to client
                     (send! ch (str "Echo: " message)))
       
       :on-close (fn [ch status-code]
                   (swap! clients disj ch)
                   (println "Client disconnected:" status-code))})
    
    ;; Non-WebSocket requests
    {:status 200
     :body "WebSocket endpoint. Connect with ws://localhost:8080"}))

(def ws-server (http/run-server ws-handler {:port 8080}))

;; Broadcast to all connected clients
(defn broadcast! [message]
  (doseq [client @clients]
    (send! client message)))
```

### Workflow 3: Streaming Responses

```clojure
(require '[org.httpkit.server :refer [as-channel send!]])

(defn streaming-handler [req]
  (as-channel req
    {:on-open (fn [ch]
                ;; Send headers first
                (send! ch {:status 200
                          :headers {"Content-Type" "text/plain"}}
                      false)  ; false = don't close after send
                
                ;; Stream data in chunks
                (future
                  (doseq [i (range 10)]
                    (Thread/sleep 500)
                    (send! ch (str "Chunk " i "\n") false))
                  
                  ;; Close when done
                  (send! ch "Done!" true)))}))

(def stream-server (http/run-server streaming-handler {:port 8080}))
```

### Workflow 4: Server with Configuration

```clojure
(defn configured-handler [req]
  {:status 200
   :body "Configured server"})

(def server (http/run-server configured-handler
              {:ip "0.0.0.0"              ; Bind to all interfaces
               :port 8080                  ; Port
               :max-body (* 10 1024 1024)  ; 10MB max body
               :max-ws (* 4 1024 1024)     ; 4MB max WebSocket message
               :max-line (* 8 1024)        ; 8KB max header line
               :server-header "my-app"     ; Custom server header
               :legacy-return-value? false ; Return HttpServer object
               
               ;; Logging
               :error-logger (fn [msg ex] (println "ERROR:" msg ex))
               :warn-logger (fn [msg ex] (println "WARN:" msg ex))
               :event-logger (fn [event] (println "EVENT:" event))}))
```

### Workflow 5: Long-Polling

```clojure
(def pending-requests (atom []))

(defn long-poll-handler [req]
  (as-channel req
    {:on-open (fn [ch]
                (swap! pending-requests conj ch)
                
                ;; Timeout after 30 seconds
                (future
                  (Thread/sleep 30000)
                  (when (some #{ch} @pending-requests)
                    (swap! pending-requests #(remove #{ch} %))
                    (send! ch {:status 408
                              :body "Timeout"}
                          true))))}))

;; When data is available, notify all waiting clients
(defn notify-clients! [data]
  (let [clients @pending-requests]
    (reset! pending-requests [])
    (doseq [ch clients]
      (send! ch {:status 200
                :headers {"Content-Type" "application/json"}
                :body (json/write-str data)}
            true))))
```

## When to Use Each Approach

**Use synchronous Ring handlers when:**
- Building simple APIs with fast responses
- No need for streaming or WebSockets
- Standard request-response pattern
- Working with Ring middleware

**Use async channels when:**
- Responses take time (database queries, external APIs)
- Streaming data to clients
- Long-polling implementations
- Need to manage connection lifecycle

**Use WebSockets when:**
- Real-time bidirectional communication needed
- Chat applications, live updates, notifications
- Game servers or collaborative editing
- Push notifications from server to client

**Use streaming responses when:**
- Large file downloads
- Server-sent events (SSE)
- Progress updates for long operations
- Chunked transfer encoding needed

**Don't use http-kit when:**
- You need servlet container features (use Jetty)
- Application is simple and doesn't need async (use Jetty/Aleph)
- You need HTTP/2 or HTTP/3 (http-kit is HTTP/1.1 only)

## Best Practices

**Do:**
- Use `:legacy-return-value? false` to get HttpServer object
- Always specify `:timeout` when stopping servers
- Close channels when done with async responses
- Handle WebSocket disconnects properly
- Set appropriate `max-body` and `max-ws` limits
- Use connection pooling for database queries in handlers
- Test async handlers thoroughly (timing issues can hide bugs)
- Clean up resources in `:on-close` handlers

**Don't:**
- Block in handlers - use async channels for slow operations
- Forget to close channels (leads to resource leaks)
- Send after closing a channel (check with `open?`)
- Ignore server stop promises (wait for clean shutdown)
- Use mutable state without proper synchronization
- Store channels without cleaning them up
- Assume WebSocket messages arrive in order across connections

## Common Issues

### Issue: "Address already in use"

```clojure
;; Problem: Server already running on port
(def server (http/run-server handler {:port 8080}))
; => Exception: Address already in use

;; Solution: Stop the old server first or use different port
(http/server-stop! server)
@(http/server-stop! server)  ; Wait for shutdown

;; Or check if server is running
(when (= :running (http/server-status server))
  (http/server-stop! server))
```

### Issue: "Channel already closed"

```clojure
;; Problem: Trying to send after channel is closed
(as-channel req
  {:on-open (fn [ch]
              (send! ch response true)      ; Closes channel
              (send! ch another-response))}) ; Error!

;; Solution: Check if channel is open or don't close too early
(require '[org.httpkit.server :refer [open?]])

(as-channel req
  {:on-open (fn [ch]
              (send! ch response false)  ; Don't close yet
              (when (open? ch)
                (send! ch another-response true)))})
```

### Issue: "Blocking in Handler"

```clojure
;; Wrong: Blocking the handler thread
(defn slow-handler [req]
  (Thread/sleep 5000)  ; Blocks thread!
  {:status 200 :body "Slow"})

;; Right: Use async for slow operations
(defn async-slow-handler [req]
  (as-channel req
    {:on-open (fn [ch]
                (future
                  (Thread/sleep 5000)  ; Async work
                  (send! ch {:status 200 :body "Slow"} true)))}))
```

### Issue: "WebSocket Not Connecting"

```clojure
;; Check if request is WebSocket
(defn ws-handler [req]
  (println "WebSocket?" (websocket? req))
  (println "Headers:" (:headers req))
  
  (if (websocket? req)
    (as-channel req {...})
    {:status 400 :body "Not a WebSocket request"}))

;; Client must send proper WebSocket upgrade headers
;; Connection: Upgrade
;; Upgrade: websocket
;; Sec-WebSocket-Key: <key>
```

### Issue: "Memory Leak with Channels"

```clojure
;; Wrong: Storing channels without cleanup
(def all-channels (atom #{}))

(defn leaky-handler [req]
  (as-channel req
    {:on-open (fn [ch]
                (swap! all-channels conj ch))}))  ; Never removed!

;; Right: Clean up on close
(defn proper-handler [req]
  (as-channel req
    {:on-open (fn [ch]
                (swap! all-channels conj ch))
     :on-close (fn [ch _]
                 (swap! all-channels disj ch))}))  ; Cleanup
```

## Advanced Topics

### Custom Worker Pool

```clojure
;; Create custom thread pool for request handling
(def worker-pool (http/new-worker
                   {:n-min-threads 4
                    :n-max-threads 16
                    :queue-size 1000}))

(def server (http/run-server handler
              {:port 8080
               :worker-pool (:pool worker-pool)}))
```

### Graceful Shutdown

```clojure
(defn shutdown-server [server]
  ;; Stop accepting new connections
  (let [stop-promise (http/server-stop! server {:timeout 5000})]
    
    ;; Wait for existing requests to complete (up to 5 seconds)
    (println "Waiting for server to stop...")
    @stop-promise
    
    (println "Server stopped gracefully")))

;; Register shutdown hook
(.addShutdownHook (Runtime/getRuntime)
  (Thread. #(shutdown-server server)))
```

### Middleware Integration

```clojure
(require '[ring.middleware.params :refer [wrap-params]]
         '[ring.middleware.keyword-params :refer [wrap-keyword-params]]
         '[ring.middleware.json :refer [wrap-json-body wrap-json-response]])

(defn app-handler [req]
  {:status 200
   :body {:message "Hello"
          :params (:params req)}})

(def app
  (-> app-handler
      wrap-keyword-params
      wrap-params
      wrap-json-response
      (wrap-json-body {:keywords? true})))

(def server (http/run-server app {:port 8080}))
```

## Related Libraries

- ring/ring - Web application library
- metosin/reitit - Routing library
- ring/ring-json - JSON middleware
- ring/ring-defaults - Common middleware

## External Resources

- [Official Documentation](https://http-kit.github.io/)
- [GitHub Repository](https://github.com/http-kit/http-kit)
- [API Docs](https://http-kit.github.io/http-kit/)
- [WebSocket Example](https://http-kit.github.io/websocket.html)

## Summary

http-kit is a high-performance HTTP server perfect for async web applications:

1. **Ring compatible** - Works with standard Ring handlers and middleware
2. **Async by default** - Non-blocking I/O for scalability
3. **WebSocket support** - Built-in bidirectional communication
4. **Simple API** - Easy to use, minimal configuration
5. **High performance** - Handles thousands of concurrent connections

Use http-kit when you need async responses, WebSockets, or high concurrency. For simple synchronous APIs, standard Ring servers may be sufficient.
