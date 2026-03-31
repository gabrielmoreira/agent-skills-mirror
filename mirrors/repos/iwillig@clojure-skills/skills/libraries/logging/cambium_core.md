---
name: cambium_structured_logging
description: Structured logging library with support for MDC and context propagation.
---

# Cambium Core

A structured logging library for Clojure built on top of SLF4J and Logback.

## Overview

Cambium provides a simple, idiomatic API for structured logging in Clojure. It supports mapped diagnostic context (MDC), structured data logging, and context propagation.

## Core Concepts

**Structured Logging**: Log messages with structured data.

```clojure
(require '[cambium.core :as log])

; Simple logging
(log/info "User created" {:user-id 1 :username "alice"})

; Different levels
(log/trace "Detailed trace" {:data "value"})
(log/debug "Debug info" {:variable 42})
(log/info "Information" {:status "ok"})
(log/warn "Warning" {:potential-issue "memory"})
(log/error "Error occurred" {:error-code 500})
(log/fatal "Fatal error" {:stopping true})
```

**Mapped Diagnostic Context**: Track request context.

```clojure
(require '[cambium.core :as log]
         '[cambium.mdc :as mdc])

; Set context
(mdc/put! :request-id "req-123")
(mdc/put! :user-id "user-456")

; Logs will include request-id and user-id automatically
(log/info "Processing request" {:action "fetch-data"})

; Clear context
(mdc/clear!)
```

## Key Features

- Structured logging with maps
- Mapped Diagnostic Context (MDC)
- Multiple log levels
- Context propagation
- Performance optimized
- SLF4J/Logback integration
- Easy to configure

## When to Use

- Production application logging
- Request tracing and correlation
- Debugging production issues
- Performance monitoring
- Audit logging

## When NOT to Use

- Simple debug prints (use pprint instead)
- When you need real-time log streaming only

## Common Patterns

```clojure
(require '[cambium.core :as log]
         '[cambium.mdc :as mdc])

; Handler middleware for setting context
(defn logging-middleware [handler]
  (fn [request]
    (let [request-id (or (get-in request [:headers "x-request-id"]) (generate-id))]
      (mdc/with-mdc {:request-id request-id :user-id (:user-id request)}
        (log/info "Request" {:method (:method request) :path (:path request)})
        (handler request)))))

; Error logging
(defn safe-operation [f]
  (try
    (f)
    (catch Exception e
      (log/error "Operation failed" {:exception (.getMessage e) :error-class (class e)})
      (throw e))))
```

## Related Libraries

- cambium/cambium.codec-cheshire - JSON codec for logs
- cambium/cambium.logback.json - Logback JSON layout

## Resources

- Official Documentation: https://github.com/cambium-clojure/cambium
- API Documentation: https://cljdoc.org/d/cambium/cambium.core

## Notes

This project uses Cambium for structured logging throughout the application.
