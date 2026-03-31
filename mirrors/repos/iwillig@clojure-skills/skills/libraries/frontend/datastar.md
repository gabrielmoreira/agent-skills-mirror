---
name: datastar-hypermedia
description: |
  Build reactive, hypermedia-driven web applications with DataStar. Use when building
  interactive UIs with server-side rendering, implementing real-time updates via SSE,
  creating reactive forms, handling frontend state from the backend, or when the user
  mentions hypermedia systems, progressive enhancement, HTMX-like functionality, Alpine.js
  reactivity, SSE streaming, or backend-driven frontends. DataStar combines backend
  reactivity (like htmx) with frontend reactivity (like Alpine.js) in a lightweight
  framework that requires no build step or npm packages.
---

# DataStar - Hypermedia-Driven Reactive Web Applications

## Quick Start

DataStar enables backend-driven, interactive UIs using hypermedia and Server-Sent Events (SSE). It works seamlessly with Clojure, Hiccup, and any routing library.

```clojure
(ns myapp.core
  (:require [hiccup.page :refer [html5]]
            [hiccup.core :refer [html]]
            [bidi.bidi :as bidi]
            [bidi.ring :as bidi-ring]))

;; Layout with DataStar included
(defn layout [content]
  (html5
    [:head
     [:meta {:charset "UTF-8"}]
     [:title "DataStar App"]
     ;; Include DataStar from CDN
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body content]))

;; Page with DataStar attributes
(defn index-page []
  (layout
    [:div
     [:h1 "DataStar + Clojure"]
     
     ;; Button triggers backend request
     [:button {:data-on:click "@get('/api/message')"} 
      "Load Message"]
     
     ;; Target div for server response
     [:div#message "Click button to load..."]]))

;; Handler returns HTML fragment
(defn message-handler [req]
  {:status 200
   :headers {"Content-Type" "text/html"}
   :body (html [:div#message "Hello from the server!"])})

;; Bidi routes
(def routes
  ["/" [["" :index]
        ["api/message" :api-message]]])

;; Map handlers
(def handlers
  {:index (fn [req] {:status 200 :body (index-page)})
   :api-message message-handler})

;; Ring handler with Bidi
(defn app [request]
  (let [match (bidi/match-route routes (:uri request))
        handler (get handlers (:handler match))]
    (if handler
      (handler (merge request match))
      {:status 404 :body "Not Found"})))
```

**Key benefits:**
- **No build step** - Include via CDN, no npm/webpack needed
- **Backend-driven** - Server controls UI updates via HTML fragments
- **Reactive state** - Frontend state management with signals
- **SSE streaming** - Real-time updates via Server-Sent Events
- **Progressive enhancement** - Works without JavaScript, enhanced with it
- **Lightweight** - ~10KB minified, no dependencies

## Core Concepts

### data-* Attributes

DataStar uses standard HTML `data-*` attributes for reactivity and backend communication:

```clojure
;; In Hiccup, use keywords with colons for data attributes
[:button {:data-on:click "@get('/api/endpoint')"} "Click Me"]

;; Common attributes:
;; - data-on:<event>      - Event listeners
;; - data-store           - Initialize reactive state
;; - data-text            - Text binding
;; - data-model           - Two-way binding (forms)
;; - data-show            - Conditional visibility
;; - data-bind:<attr>     - Attribute binding
```

### Actions

Actions are helper functions in DataStar expressions (prefixed with `@`):

- `@get(url)` - GET request to backend
- `@post(url)` - POST request with state
- `@put(url)` - PUT request with state
- `@patch(url)` - PATCH request with state
- `@delete(url)` - DELETE request

### Patching Elements

DataStar receives HTML from the backend and patches (morphs) it into the DOM by matching element IDs:

```clojure
;; Frontend: element with ID
[:div#message "Loading..."]

;; Backend: returns HTML with same ID
(html [:div#message "Updated content!"])

;; DataStar automatically finds and updates the element
```

### Server-Sent Events (SSE)

For real-time updates, DataStar supports SSE streams. The Clojure SDK provides helpers:

```clojure
(require '[starfederation.datastar.clojure.api :as d*]
         '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])

(defn sse-handler [request]
  (->sse-response request
    {on-open
     (fn [sse]
       ;; Send HTML updates via SSE
       (d*/patch-elements! sse
         (html [:div#status "Connected!"]))
       
       ;; Send more updates
       (Thread/sleep 1000)
       (d*/patch-elements! sse
         (html [:div#status "Processing..."])))}))
```

### Reactive Signals (State)

DataStar provides frontend state management using signals (variables prefixed with `$`):

```clojure
;; Initialize state with data-store
[:div {:data-store "{count: 0, name: 'Alice'}"}
 
 ;; Display state with data-text
 [:p {:data-text "$count"}]
 
 ;; Modify state with expressions
 [:button {:data-on:click "$count++"} "Increment"]
 
 ;; Two-way binding with data-model
 [:input {:type "text" :data-model "name"}]
 [:p "Hello, " [:span {:data-text "$name"}]]]
```

## Common Workflows

### Workflow 1: Basic HTMX-Style Updates

Replace parts of the page with server-rendered HTML:

```clojure
(ns myapp.basic
  (:require [hiccup.page :refer [html5]]
            [hiccup.core :refer [html]]
            [bidi.bidi :as bidi]
            [bidi.ring :as bidi-ring]))

;; Page with clickable elements
(defn todos-page []
  (html5
    [:head
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "Todo List"]
     
     ;; Load todos button
     [:button {:data-on:click "@get('/todos/list')"} 
      "Load Todos"]
     
     ;; Target div
     [:div#todos "Click to load todos..."]]))

;; Handler returns todo list HTML
(defn todos-list-handler [req]
  {:status 200
   :headers {"Content-Type" "text/html"}
   :body (html
           [:div#todos
            [:ul
             [:li "Buy groceries"]
             [:li "Write code"]
             [:li "Deploy app"]]])})

;; Routes
(def routes
  ["/" [["todos" :todos-page]
        ["todos/list" :todos-list]]])

(def handlers
  {:todos-page (fn [req] {:status 200 :body (todos-page)})
   :todos-list todos-list-handler})

(defn app [request]
  (let [match (bidi/match-route routes (:uri request))
        handler (get handlers (:handler match))]
    (if handler
      (handler request)
      {:status 404 :body "Not Found"})))
```

### Workflow 2: Forms with State

Two-way data binding with forms:

```clojure
(defn contact-form []
  (html5
    [:head
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "Contact Form"]
     
     ;; Initialize form state
     [:div {:data-store "{name: '', email: '', message: ''}"}
      [:form
       [:div
        [:label "Name:"]
        [:input {:type "text"
                 :data-model "name"
                 :placeholder "Your name"}]]
       
       [:div
        [:label "Email:"]
        [:input {:type "email"
                 :data-model "email"
                 :placeholder "your@email.com"}]]
       
       [:div
        [:label "Message:"]
        [:textarea {:data-model "message"
                    :placeholder "Your message"}]]
       
       ;; Submit sends state to backend
       [:button {:type "button"
                 :data-on:click "@post('/contact/submit')"} 
        "Submit"]]
      
      ;; Result area
      [:div#result]]]))

;; Handler receives JSON with form state
(defn contact-submit-handler [req]
  (let [body (slurp (:body req))
        data (cheshire.core/parse-string body true)
        {:keys [name email message]} data]
    {:status 200
     :headers {"Content-Type" "text/html"}
     :body (html
             [:div#result
              [:p {:style "color: green;"}
               (str "Thanks " name "! We'll contact you at " email)]])}))

;; Routes with POST
(def routes
  ["/" [["contact" :contact-form]
        [["contact/submit" :request-method :post] :contact-submit]]])
```

### Workflow 3: Server-Sent Events (SSE) Streaming

Real-time updates via SSE:

```clojure
(require '[starfederation.datastar.clojure.api :as d*]
         '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]]
         '[org.httpkit.server :as http-kit])

(defn progress-page []
  (html5
    [:head
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "Task Progress"]
     
     ;; Trigger SSE connection
     [:button {:data-on:click "@get('/tasks/process')"} 
      "Start Task"]
     
     [:div#progress "Not started"]
     [:div#status "Ready"]]))

;; SSE handler sends multiple updates
(defn process-task-handler [request]
  (->sse-response request
    {on-open
     (fn [sse]
       ;; Step 1
       (d*/patch-elements! sse
         (html [:div#progress "0%"]
               [:div#status "Starting..."]))
       
       (Thread/sleep 1000)
       
       ;; Step 2
       (d*/patch-elements! sse
         (html [:div#progress "33%"]
               [:div#status "Processing data..."]))
       
       (Thread/sleep 1000)
       
       ;; Step 3
       (d*/patch-elements! sse
         (html [:div#progress "66%"]
               [:div#status "Finalizing..."]))
       
       (Thread/sleep 1000)
       
       ;; Complete
       (d*/patch-elements! sse
         (html [:div#progress "100%"]
               [:div#status {:style "color: green;"} "Complete!"])))}))

;; Routes with http-kit
(def routes
  ["/" [["tasks" :tasks-page]
        ["tasks/process" :tasks-process]]])

(def handlers
  {:tasks-page (fn [req] {:status 200 :body (progress-page)})
   :tasks-process process-task-handler})

(defn app [request]
  (let [match (bidi/match-route routes (:uri request))
        handler (get handlers (:handler match))]
    (if handler
      (handler request)
      {:status 404 :body "Not Found"})))

;; Start server with http-kit (required for SSE)
(defn -main []
  (http-kit/run-server app {:port 3000})
  (println "Server running on http://localhost:3000"))
```

### Workflow 4: Reactive Counter (Frontend State)

Pure frontend reactivity without backend:

```clojure
(defn counter-page []
  (html5
    [:head
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "Counter Demo"]
     
     ;; Initialize state
     [:div {:data-store "{count: 0}"}
      [:h2 "Count: " [:span {:data-text "$count"}]]
      
      ;; Buttons modify state with expressions
      [:button {:data-on:click "$count++"} "Increment"]
      [:button {:data-on:click "$count--"} "Decrement"]
      [:button {:data-on:click "$count = 0"} "Reset"]
      
      ;; Conditional rendering
      [:p {:data-show "$count > 10"}
       "Wow, that's a lot!"]]]))
```

### Workflow 5: Dynamic Lists

Render lists from state:

```clojure
(defn shopping-list []
  (html5
    [:head
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "Shopping List"]
     
     ;; Initialize with array
     [:div {:data-store "{items: ['Milk', 'Bread', 'Eggs'], newItem: ''}"}
      
      ;; Add item form
      [:div
       [:input {:type "text"
                :data-model "newItem"
                :placeholder "Add item"}]
       [:button {:data-on:click "$items.push($newItem); $newItem = ''"} 
        "Add"]]
      
      ;; Render list with template
      [:ul
       [:template {:data-for "item in $items"}
        [:li {:data-text "$item"}]]]]]))
```

### Workflow 6: CRUD with Bidi Routing

Complete CRUD example with proper routing:

```clojure
(ns myapp.crud
  (:require [hiccup.page :refer [html5]]
            [hiccup.core :refer [html]]
            [bidi.bidi :as bidi]
            [cheshire.core :as json]
            [ring.middleware.params :refer [wrap-params]]
            [ring.middleware.keyword-params :refer [wrap-keyword-params]]))

(def items-db (atom {"1" {:id "1" :name "Item One" :price 10}
                     "2" {:id "2" :name "Item Two" :price 20}}))

;; List items page
(defn items-page []
  (html5
    [:head
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "Items"]
     
     ;; Load items on page load
     [:div {:data-on:load "@get('/items/list')"}
      [:div#items-list "Loading..."]]
     
     [:hr]
     
     ;; Create new item form
     [:h2 "Add Item"]
     [:div {:data-store "{name: '', price: 0}"}
      [:input {:type "text" :data-model "name" :placeholder "Name"}]
      [:input {:type "number" :data-model "price" :placeholder "Price"}]
      [:button {:data-on:click "@post('/items/create')"} "Create"]]]))

;; List items HTML
(defn items-list-html []
  (html
    [:div#items-list
     [:table
      [:thead
       [:tr
        [:th "Name"]
        [:th "Price"]
        [:th "Actions"]]]
      [:tbody
       (for [[id item] @items-db]
         [:tr
          [:td (:name item)]
          [:td "$" (:price item)]
          [:td
           [:button {:data-on:click (str "@delete('/items/" id "')")} 
            "Delete"]]])]]]))

;; Handler: list items
(defn list-items-handler [req]
  {:status 200
   :headers {"Content-Type" "text/html"}
   :body (items-list-html)})

;; Handler: create item
(defn create-item-handler [req]
  (let [body (slurp (:body req))
        data (json/parse-string body true)
        new-id (str (inc (count @items-db)))
        new-item {:id new-id
                  :name (:name data)
                  :price (:price data)}]
    (swap! items-db assoc new-id new-item)
    {:status 200
     :headers {"Content-Type" "text/html"}
     :body (items-list-html)}))

;; Handler: delete item
(defn delete-item-handler [req]
  (let [id (get-in req [:route-params :id])]
    (swap! items-db dissoc id)
    {:status 200
     :headers {"Content-Type" "text/html"}
     :body (items-list-html)}))

;; Routes with Bidi
(def routes
  ["/" [["items" :items-page]
        ["items/list" :items-list]
        [["items/create" :request-method :post] :items-create]
        [["items/" :id :request-method :delete] :items-delete]]])

(def handlers
  {:items-page (fn [req] {:status 200 :body (items-page)})
   :items-list list-items-handler
   :items-create create-item-handler
   :items-delete delete-item-handler})

(defn app [request]
  (let [match (bidi/match-route routes (:uri request) 
                                :request-method (:request-method request))
        handler (get handlers (:handler match))]
    (if handler
      (handler (merge request match))
      {:status 404 :body "Not Found"})))

;; Wrap with middleware
(def handler
  (-> app
      wrap-keyword-params
      wrap-params))
```

### Workflow 7: Conditional Rendering and Classes

Dynamic visibility and CSS classes:

```clojure
(defn toggle-demo []
  (html5
    [:head
     [:style "
       .error { color: red; border: 2px solid red; padding: 10px; }
       .success { color: green; border: 2px solid green; padding: 10px; }
       .hidden { display: none; }"]
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "Conditional Rendering"]
     
     [:div {:data-store "{showMessage: false, isError: false}"}
      
      ;; Toggle button
      [:button {:data-on:click "$showMessage = !$showMessage"} 
       "Toggle Message"]
      
      [:button {:data-on:click "$isError = !$isError"} 
       "Toggle Error/Success"]
      
      ;; Conditional display with data-show
      [:div {:data-show "$showMessage"
             :data-class:error "$isError"
             :data-class:success "!$isError"}
       "This message appears/disappears and changes style!"]]]))
```

### Workflow 8: Loading States

Show loading indicators during backend requests:

```clojure
(defn loading-demo []
  (html5
    [:head
     [:style ".spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; 
                          border-radius: 50%; width: 40px; height: 40px; 
                          animation: spin 1s linear infinite; }
              @keyframes spin { 0% { transform: rotate(0deg); } 
                               100% { transform: rotate(360deg); } }"]
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "Loading States"]
     
     ;; Track loading state
     [:div {:data-store "{isLoading: false}"}
      
      ;; Button disabled during loading
      [:button {:data-on:click "$isLoading = true; @get('/api/slow-data')"
                :data-bind:disabled "$isLoading"} 
       "Load Data"]
      
      ;; Loading spinner
      [:div {:data-show "$isLoading" :class "spinner"}]
      
      ;; Data container
      [:div#data "No data loaded"]]]))

;; Slow endpoint that simulates delay
(defn slow-data-handler [req]
  (Thread/sleep 2000)  ; Simulate slow operation
  {:status 200
   :headers {"Content-Type" "text/html"}
   :body (html [:div#data "Data loaded!"]
               ;; Reset loading state via signal merge
               [:div {:data-signal:merge "{isLoading: false}"}])})
```

## When to Use DataStar

**Use DataStar when:**
- Building server-rendered apps with progressive enhancement
- You want hypermedia-driven architecture (HATEOAS)
- Need real-time updates via SSE
- Prefer backend-driven UI updates over client-side frameworks
- Want lightweight solution without build tools
- Building CRUD apps, admin panels, dashboards
- Team prefers backend development over frontend complexity

**Use React/ClojureScript when:**
- Building complex SPAs with heavy client-side logic
- Need offline functionality
- Require rich client-side state management
- Building mobile apps with React Native

**Use HTMX when:**
- You only need backend-driven updates (no frontend state)
- Simpler mental model sufficient
- Don't need reactive signals

**DataStar vs HTMX:**
- DataStar: Backend updates + frontend reactivity (signals)
- HTMX: Only backend updates (no frontend state management)

## Best Practices

**Do:**
- Use element IDs for patch targets (`[:div#message ...]`)
- Initialize state with `data-store` at appropriate scope
- Use SSE for real-time/multi-step operations
- Leverage Hiccup for server-side HTML generation
- Use Bidi reverse routing: `(bidi/path-for routes :handler ...)`
- Return HTML fragments (not full pages) from handlers
- Use `data-model` for form inputs
- Test without JavaScript first (progressive enhancement)

```clojure
;; Good: Element with ID for patching
[:div#status "Ready"]

;; Good: Initialize state in parent scope
[:div {:data-store "{count: 0}"}
 [:span {:data-text "$count"}]
 [:button {:data-on:click "$count++"} "+"]]

;; Good: Use Bidi for URL generation
[:button {:data-on:click 
          (str "@get('" (bidi/path-for routes :api-data) "')")} 
 "Load"]
```

**Don't:**
- Hardcode URLs (use Bidi's `path-for`)
- Return full HTML pages from fragment endpoints
- Forget element IDs on patch targets
- Mix too much logic in frontend expressions (keep simple)
- Ignore progressive enhancement
- Use DataStar for complex client-side state (use ClojureScript)

```clojure
;; Bad: Hardcoded URL
[:button {:data-on:click "@get('/api/data')"} "Load"]

;; Good: Generate URL with Bidi
[:button {:data-on:click 
          (str "@get('" (bidi/path-for routes :api-data) "')")} 
 "Load"]

;; Bad: Complex logic in expression
[:button {:data-on:click 
          "$data = processData($input); if($data.valid){save($data)}"} 
 "Save"]

;; Good: Keep expressions simple, logic on backend
[:button {:data-on:click "@post('/save')"} "Save"]
```

## Common Issues

### Issue: Element not updating after request

```clojure
;; Frontend
[:div#message "Loading..."]

;; Backend returns HTML without ID
(html [:div "New message"])  ; Missing ID!
```

**Solution**: Include matching ID in server response:

```clojure
;; Backend must include same ID
(html [:div#message "New message"])
```

### Issue: State not initializing

```clojure
;; Missing data-store initialization
[:div
 [:span {:data-text "$count"}]]  ; $count is undefined
```

**Solution**: Initialize state with `data-store`:

```clojure
[:div {:data-store "{count: 0}"}
 [:span {:data-text "$count"}]]
```

### Issue: Form data not sent to backend

```clojure
;; No data-model on inputs
[:input {:type "text" :name "username"}]
[:button {:data-on:click "@post('/submit')"} "Submit"]
```

**Solution**: Use `data-model` to bind inputs to state:

```clojure
[:div {:data-store "{username: ''}"}
 [:input {:type "text" :data-model "username"}]
 [:button {:data-on:click "@post('/submit')"} "Submit"]]
```

### Issue: SSE not working

**Problem**: Regular Ring servers don't support streaming responses.

**Solution**: Use http-kit or another server that supports async/streaming:

```clojure
(require '[org.httpkit.server :as http-kit])

;; http-kit supports SSE
(http-kit/run-server app {:port 3000})
```

### Issue: DataStar expressions not evaluating

```clojure
;; Syntax error in expression
[:button {:data-on:click "$count+++"} "Add"]  ; Three plus signs!
```

**Solution**: Use valid JavaScript expressions:

```clojure
[:button {:data-on:click "$count++"} "Add"]
```

## Advanced Topics

### Signals and Reactive State

DataStar signals are reactive variables:

```clojure
;; Initialize
[:div {:data-store "{user: {name: 'Alice', age: 30}}"}
 
 ;; Access nested properties
 [:p {:data-text "$user.name"}]
 
 ;; Computed expressions
 [:p {:data-text "'Age next year: ' + ($user.age + 1)"}]
 
 ;; Update nested
 [:button {:data-on:click "$user.age++"} "Birthday"]]
```

### Backend Signal Updates

Update frontend state from backend:

```clojure
;; Backend can send signal merges via SSE
(d*/merge-signals! sse {:count 42 :status "Updated"})

;; Or in HTML fragment
(html [:div {:data-signal:merge "{count: 42, status: 'Updated'}"}])
```

### Custom Events

Trigger custom events:

```clojure
;; Dispatch custom event
[:button {:data-on:click "@dispatch('refresh-data')"} "Refresh"]

;; Listen for custom event
[:div {:data-on:refresh-data "@get('/api/fresh-data')"}]
```

### Persist Signals to LocalStorage

Persist state across page reloads:

```clojure
[:div {:data-store "{user: {name: 'Alice'}}"
       :data-persist "user"}  ; Persists 'user' signal
 [:input {:type "text" :data-model "user.name"}]]
```

## SDK Reference

The official Clojure SDK provides helpers for SSE:

```clojure
;; Add to deps.edn
{:deps {starfederation/datastar.clojure {:git/url "https://github.com/starfederation/datastar-clojure"
                                         :sha "..."}}}

;; Core functions
(require '[starfederation.datastar.clojure.api :as d*])

;; Patch HTML elements
(d*/patch-elements! sse (html [:div#target "Content"]))

;; Merge signals (update frontend state)
(d*/merge-signals! sse {:count 10 :status "ready"})

;; Execute scripts
(d*/execute-script! sse "console.log('Hello from backend')")

;; Remove elements
(d*/remove-elements! sse "#old-element")
```

## Integration Examples

### With Ring + Compojure (Alternative)

```clojure
(require '[compojure.core :refer [defroutes GET POST DELETE]]
         '[compojure.route :as route])

(defroutes app-routes
  (GET "/" [] (items-page))
  (GET "/items/list" [] (list-items-handler))
  (POST "/items/create" req (create-item-handler req))
  (DELETE "/items/:id" [id] (delete-item-handler id))
  (route/not-found "Not Found"))
```

### With Reitit (Alternative)

```clojure
(require '[reitit.ring :as ring])

(def app
  (ring/ring-handler
    (ring/router
      [["/" {:get (fn [_] {:status 200 :body (items-page)})}]
       ["/items"
        ["/list" {:get list-items-handler}]
        ["/create" {:post create-item-handler}]
        ["/:id" {:delete delete-item-handler}]]])))
```

## Resources

- Official Site: https://data-star.dev
- Getting Started: https://data-star.dev/guide/getting_started
- Reference: https://data-star.dev/reference
- Examples: https://data-star.dev/examples
- Clojure SDK: https://github.com/starfederation/datastar-clojure
- Discord: https://discord.gg/bnRNgZjgPh

## Related Skills

- **hiccup** - HTML generation in Clojure
- **bidi** - Bidirectional routing
- **http-kit** - HTTP server with SSE support
- **ring** - Web application library
- **cheshire** - JSON encoding/decoding

## Summary

DataStar enables hypermedia-driven reactive web applications:

1. **Backend-Driven** - Server controls UI via HTML fragments
2. **Reactive Signals** - Frontend state management without framework
3. **SSE Streaming** - Real-time updates from backend
4. **No Build Step** - Include via CDN, write HTML in Hiccup
5. **Progressive Enhancement** - Works without JS, enhanced with it
6. **Bidi Integration** - Clean routing with reverse path generation

**Most common patterns:**

```clojure
;; Simple update
[:button {:data-on:click "@get('/api/data')"} "Load"]
[:div#data "Content"]

;; Form with state
[:div {:data-store "{name: ''}"}
 [:input {:data-model "name"}]
 [:button {:data-on:click "@post('/submit')"} "Submit"]]

;; SSE streaming
(->sse-response request
  {on-open
   (fn [sse]
     (d*/patch-elements! sse (html [:div#status "Done"])))})

;; Bidi routing
(def routes ["/" [["api/data" :api-data]]])
(bidi/path-for routes :api-data)  ; => "/api/data"
```

Perfect for building server-rendered, progressively-enhanced web applications with real-time capabilities and minimal frontend complexity.
