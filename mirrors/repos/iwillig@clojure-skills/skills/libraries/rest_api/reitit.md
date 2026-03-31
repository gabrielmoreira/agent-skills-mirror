---
name: reitit_routing_library
description: High-performance routing library for Clojure web applications.
---

# Reitit

A fast, composable router for Clojure and ClojureScript with data-driven route definitions.

## Overview

Reitit provides a modern routing solution that uses data-driven route definitions instead of macros. It compiles routes into efficient data structures and supports middleware, validation, and documentation generation.

## Core Concepts

**Route Definition**: Routes are defined as data structures.

```clojure
(require '[reitit.core :as r])

(def routes
  [["/users" {:name :users
              :get (fn [req] {:body "List users"})}]
   ["/users/:id" {:name :user
                  :get (fn [req] {:body (str "User " (get-in req [:path-params :id]))})}]])
```

**Router**: Compile routes into an efficient router.

```clojure
(def router (r/router routes))

; Match a route
(r/match-by-path router "/users")
; => {:path "/users", :result {:name :users}, ...}

(r/match-by-path router "/users/123")
; => {:path "/users/123", :path-params {:id "123"}, ...}
```

**Middleware**: Wrap routes with middleware.

```clojure
(def routes
  [["/api/users" {:name :users
                  :get {:handler (fn [req] {:body "users"})
                        :middleware [auth-middleware]}}]])
```

## Key Features

- Data-driven route definitions
- Parameter validation with schemas
- Route compilation for performance
- Middleware support
- Automatic documentation generation
- Path parameter extraction
- Query parameter parsing

## When to Use

- Building REST APIs
- Routing HTTP requests
- Creating web application routes
- Building composable routing systems

## When NOT to Use

- For simple static routing (use a simpler library)
- When you need template rendering (pair with other libraries)

## Common Patterns

```clojure
(require '[reitit.ring :as ring]
         '[reitit.core :as r])

; Complete routing setup
(def routes
  [["/api"
    ["/users"
     {:get {:handler (fn [req] {:status 200 :body "users"})}
      :post {:handler (fn [req] {:status 201 :body "created"})}}]
    ["/users/:id"
     {:get {:handler (fn [req] {:status 200 :body (str "user " (get-in req [:path-params :id]))})}}]]])

(def app (ring/ring-handler (r/router routes)))
```

## Related Libraries

- http-kit/http-kit - HTTP server
- liberator/liberator - REST resource library
- metosin/malli - Data validation for routes

## Resources

- Official Documentation: https://github.com/metosin/reitit
- API Documentation: https://cljdoc.org/d/metosin/reitit

## Notes

This project uses Reitit for URL routing and REST API definition.
