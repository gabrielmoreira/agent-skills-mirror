---
name: bidi-routing
description: |
  Bidirectional routing library for Clojure web applications. Use when building REST APIs,
  defining URL routes, generating URIs from handlers, or when you need data-driven routing
  that's composable and introspectable. Ideal for projects requiring both route matching
  (request → handler) and reverse routing (handler → URI).
---

# Bidi - Bidirectional Routing

## Quick Start

Bidi provides bidirectional routing: match URIs to handlers AND generate URIs from handlers. Routes are pure data structures, not macros.

```clojure
(require '[bidi.bidi :as bidi])

;; Define routes as data
(def routes
  ["/" {"index.html" :index
        "about.html" :about
        "users/" {[:user-id "/profile"] :user-profile}}])

;; Match incoming request paths
(bidi/match-route routes "/index.html")
; => {:handler :index}

(bidi/match-route routes "/users/42/profile")
; => {:handler :user-profile, :route-params {:user-id "42"}}

;; Generate URIs from handlers (reverse routing)
(bidi/path-for routes :index)
; => "/index.html"

(bidi/path-for routes :user-profile :user-id "123")
; => "/users/123/profile"
```

**Key benefit**: Define routes once, use for both matching AND generation.

## Core Concepts

### Bidirectional Routing

Unlike most routing libraries, bidi works in both directions:
- **Forward**: URI + routes → handler + params
- **Reverse**: handler + params + routes → URI

This eliminates hardcoded URIs throughout your codebase.

### Routes as Data

Routes are plain Clojure data structures (vectors, maps, keywords). This means routes can be:
- Composed programmatically
- Introspected at runtime
- Transformed with standard data operations
- Tested without starting a server

### Route Structure

Basic pattern: `[path-prefix {pattern handler, ...}]`

```clojure
["/base"                      ; Path prefix (string)
 {"static" :handler-1         ; Exact string match
  ["dynamic/" :param] :h-2    ; Parameterized path
  [:id "/edit"] :h-3}]        ; Keyword parameter
```

### Pattern Types

- **Strings**: Exact matches `"users"`
- **Keywords**: Path parameters `[:user-id]` 
- **Vectors**: Concatenated patterns `["posts/" :id "/comments"]`
- **Regex**: Pattern matching `[#"\d+" :id]`
- **Maps**: Nested routes `{"admin/" {...}}`

## Common Workflows

### Workflow 1: Basic Route Matching

Match incoming request paths to handlers:

```clojure
(def routes
  ["/" {"" :home
        "about" :about
        "contact" :contact}])

(bidi/match-route routes "/")
; => {:handler :home}

(bidi/match-route routes "/about")
; => {:handler :about}

(bidi/match-route routes "/unknown")
; => nil  ; No match returns nil
```

### Workflow 2: Path Parameters

Extract dynamic values from URIs:

```clojure
(def routes
  ["/" {"users/" {[:user-id] :user
                  [:user-id "/posts/" :post-id] :post}}])

(bidi/match-route routes "/users/42")
; => {:handler :user, :route-params {:user-id "42"}}

(bidi/match-route routes "/users/123/posts/456")
; => {:handler :post, :route-params {:user-id "123", :post-id "456"}}
```

**Pattern**: Keywords in vectors become parameters. Use descriptive names.

### Workflow 3: HTTP Method Guards

Route based on HTTP method:

```clojure
(def routes
  ["/api/" 
   {:get {["users"] :list-users
          ["users/" :id] :get-user}
    :post {["users"] :create-user}
    :put {["users/" :id] :update-user}
    :delete {["users/" :id] :delete-user}}])

(bidi/match-route routes "/api/users" :request-method :get)
; => {:request-method :get, :handler :list-users, :route-params {}}

(bidi/match-route routes "/api/users" :request-method :post)
; => {:request-method :post, :handler :create-user, :route-params {}}

(bidi/match-route routes "/api/users/42" :request-method :put)
; => {:request-method :put, :handler :update-user, :route-params {:id "42"}}
```

**Pattern**: Use method keyword as top-level key, nest paths beneath.

### Workflow 4: Reverse Routing (URI Generation)

Generate URIs from handler names:

```clojure
(def routes
  ["/api/" 
   {["users"] :users
    ["users/" :user-id] :user
    ["posts/" :post-id "/comments/" :comment-id] :comment}])

;; No parameters needed
(bidi/path-for routes :users)
; => "/api/users"

;; Single parameter
(bidi/path-for routes :user :user-id 123)
; => "/api/users/123"

;; Multiple parameters
(bidi/path-for routes :comment :post-id 456 :comment-id 789)
; => "/api/posts/456/comments/789"
```

**Benefits**:
- No hardcoded URIs in templates/views
- Refactor routes without updating every reference
- Type-safe (compile-time checks if handler exists)

### Workflow 5: Nested/Composed Routes

Build routes from reusable components:

```clojure
;; Define route fragments
(def user-routes
  ["users/" {[:user-id] :user-profile
             [:user-id "/settings"] :user-settings}])

(def post-routes
  ["posts/" {[:post-id] :post-view
             [:post-id "/edit"] :post-edit}])

;; Compose into main routes
(def app-routes
  ["/" {"api/" {user-routes  ; Nested under /api/users/
                post-routes}}])  ; Nested under /api/posts/

(bidi/match-route app-routes "/api/users/42")
; => {:handler :user-profile, :route-params {:user-id "42"}}

(bidi/match-route app-routes "/api/posts/123/edit")
; => {:handler :post-edit, :route-params {:post-id "123"}}
```

**Pattern**: Define subsections separately, compose at root level.

### Workflow 6: Regex Pattern Matching

Use regex for constrained parameters:

```clojure
(def routes
  ["/files/" 
   {[#"\d+" :id] :file-by-number      ; Only digits
    [#"[a-z]+" :slug] :file-by-slug   ; Only lowercase letters
    [#".+" :path] :file-by-path}])     ; Any characters

(bidi/match-route routes "/files/12345")
; => {:handler :file-by-number, :route-params {:id "12345"}}

(bidi/match-route routes "/files/readme")
; => {:handler :file-by-slug, :route-params {:slug "readme"}}

(bidi/match-route routes "/files/path/to/file.txt")
; => {:handler :file-by-path, :route-params {:path "path/to/file.txt"}}
```

**Warning**: Order matters! More specific patterns should come before generic ones.

### Workflow 7: Integration with Ring Handlers

Convert bidi routes into Ring handler:

```clojure
(require '[bidi.ring :as bidi-ring])

(def routes
  ["/" {"" (fn [req] {:status 200 :body "Home"})
        "api/" {:get {["users"] (fn [req] {:status 200 :body "Users list"})}}}])

;; Create Ring handler from routes
(def handler (bidi-ring/make-handler routes))

;; Use with Ring server
(require '[ring.adapter.jetty :as jetty])
(jetty/run-jetty handler {:port 3000})
```

**Alternative**: Use bidi for routing only, map to handler functions separately:

```clojure
(def routes
  ["/" {"" :home
        "api/users" :list-users}])

(def handlers
  {:home (fn [req] {:status 200 :body "Home"})
   :list-users (fn [req] {:status 200 :body "Users"})})

(defn app [request]
  (let [match (bidi/match-route routes (:uri request))
        handler (get handlers (:handler match))]
    (if handler
      (handler (merge request match))
      {:status 404 :body "Not found"})))
```

## When to Use Bidi

**Use bidi when:**
- You need reverse routing (generating URIs from handlers)
- Routes should be data that's composable/introspectable
- Building REST APIs with predictable URL structures
- You want minimal dependencies and simple abstraction
- Routes need to be computed or transformed at runtime

**Use reitit when:**
- You need high-performance routing (reitit compiles routes)
- Schema validation/coercion required
- Middleware per-route needed
- Documentation generation wanted

**Use Compojure when:**
- Macro-based DSL is preferred
- Routes are static and simple
- No reverse routing needed

**Use Pedestal when:**
- Building complex interceptor-based applications
- Async processing required
- Full framework with server included needed

## Best Practices

**Do:**
- Use descriptive handler keywords (`:user-profile` not `:up`)
- Define routes as top-level `def` for easy testing
- Keep route structure flat where possible
- Use `path-for` instead of hardcoding URIs
- Test routes without starting server (routes are just data)
- Group related routes under common prefixes

```clojure
;; Good: descriptive handlers
(def routes ["/" {"users" :user-list
                  "about" :about-page}])

;; Good: test routes as data
(deftest routing-test
  (is (= :user-list 
         (:handler (bidi/match-route routes "/users")))))
```

**Don't:**
- Put handler functions directly in routes (use keywords, map separately)
- Create deeply nested route structures (hard to understand)
- Use overly generic parameter names (`:id` everywhere)
- Forget that regex order matters (specific before generic)
- Mix routing and handler logic

```clojure
;; Bad: handler in route structure
["/" {"" (fn [req] ...)}]  ; Hard to test, can't compose

;; Good: handler reference, map later
["/" {"" :home}]
```

## Common Issues

### Issue: `nil` returned from `match-route`

```clojure
(bidi/match-route routes "/users")
; => nil
```

**Causes:**
1. Path doesn't match any route pattern
2. Missing leading slash: use `"/users"` not `"users"`
3. Method guard not satisfied (forgot `:request-method` option)

**Solution**: Check path structure and method requirements:

```clojure
;; If using method guards, provide request-method
(bidi/match-route routes "/api/users" :request-method :get)
```

### Issue: "No implementation of method: :match-pattern"

```clojure
; Execution error (IllegalArgumentException)
; No implementation of method: :match-pattern of protocol: Pattern
```

**Cause**: Invalid route structure (wrong data types or nesting).

**Solution**: Check route syntax - strings should be in maps, vectors for concatenation:

```clojure
;; Wrong: character literal in path
["/" {\a :handler}]

;; Right: string for static segment
["/" {"a" :handler}]
```

### Issue: Parameters not extracted

```clojure
(bidi/match-route routes "/users/42")
; => {:handler :user-profile}  ; Missing :route-params
```

**Cause**: Parameter not defined as keyword in vector.

**Solution**: Use keyword in vector to create parameter:

```clojure
;; Wrong: keyword alone doesn't capture
["/" {"users/" {:user-id :profile}}]

;; Right: keyword in vector creates parameter
["/" {"users/" {[:user-id] :profile}}]
```

### Issue: `path-for` returns `nil`

```clojure
(bidi/path-for routes :user-profile)
; => nil
```

**Causes:**
1. Handler doesn't exist in routes
2. Missing required parameters
3. Parameter name mismatch

**Solution**: Verify handler exists and provide all required parameters:

```clojure
;; Check what handlers exist
(clojure.walk/prewalk 
  (fn [x] (when (keyword? x) (println x)) x) 
  routes)

;; Provide all parameters
(bidi/path-for routes :user-profile :user-id "42")
```

## Advanced Topics

### Custom Pattern Types

Bidi is extensible via protocols. You can define custom pattern matchers:

```clojure
(require '[bidi.bidi :as bidi])

;; See bidi documentation for protocol implementation details
;; Protocols: Pattern, Matched, ParameterEncoding
```

### Route Inspection

Since routes are data, you can introspect them:

```clojure
;; Get all routes
(bidi/route-seq routes)

;; Transform routes
(clojure.walk/postwalk 
  (fn [x] 
    (if (keyword? x) 
      (keyword (str (name x) "-v2")) 
      x))
  routes)
```

### Performance Considerations

Bidi does not compile routes. For high-traffic applications with many routes:
- Consider reitit (pre-compiles routes to efficient data structures)
- Cache `match-route` results for static paths
- Keep route structure shallow

## Related Libraries

- **bidi/ring** - Ring integration helpers
- **reitit** - High-performance routing with compilation
- **compojure** - Macro-based routing DSL
- **pedestal** - Full framework with routing

## Resources

- GitHub: https://github.com/juxt/bidi
- Documentation: https://github.com/juxt/bidi#routes
- Ring Integration: https://github.com/juxt/bidi#ring

## Summary

Bidi provides **bidirectional**, **data-driven** routing:

1. **Match routes**: `(bidi/match-route routes path)` → handler + params
2. **Generate URIs**: `(bidi/path-for routes handler params)` → path
3. **Routes as data**: Composable, introspectable, transformable
4. **Method guards**: Route by HTTP method
5. **Pattern types**: Strings, keywords (params), vectors, regex
6. **Reverse routing**: Eliminate hardcoded URIs

Perfect for REST APIs and web apps where URIs need to be generated consistently throughout the application.
