---
name: hiccup_html_generation
description: HTML generation library for Clojure.
---

# Hiccup

A Clojure library for rendering HTML using Clojure data structures.

## Overview

Hiccup allows you to write HTML as nested Clojure data structures (vectors and maps) instead of string templates, providing type safety and composability.

## Core Concepts

**HTML as Data**: Represent HTML with vectors and keywords.

```clojure
(require '[hiccup.core :refer [html]])

; Basic HTML
(html [:div {:class "container"}
       [:h1 "Hello World"]
       [:p "This is a paragraph"]])

; Output:
; <div class="container"><h1>Hello World</h1><p>This is a paragraph</p></div>

; Pretty print
(html {:escape-strings? true}
      [:div
       [:h1 "Title"]
       [:p "Content"]])
```

**Composable Templates**: Build templates from smaller pieces.

```clojure
(defn user-card [user]
  [:div {:class "card"}
   [:h2 (:name user)]
   [:p (:email user)]])

(defn user-list [users]
  [:div {:class "users"}
   (for [user users]
     (user-card user))])

(html (user-list [{:name "Alice" :email "alice@example.com"}
                  {:name "Bob" :email "bob@example.com"}]))
```

## Key Features

- Vector-based syntax
- Attribute maps
- Form helpers
- Escape handling
- Composable components
- Performance optimized
- CSS shorthand (classes and ids)

## When to Use

- Server-side HTML rendering
- Building HTML pages with Clojure
- Creating reusable HTML components
- Dynamic HTML generation

## When NOT to Use

- Client-side rendering (use ClojureScript)
- Complex interactive UIs (use React-based frameworks)

## Common Patterns

```clojure
(require '[hiccup.core :refer [html]]
         '[hiccup.form :as form])

; HTML with CSS selectors
(html [:div#main.container
       [:h1.title "Welcome"]
       [:p.subtitle "This is a subtitle"]])

; Forms
(html (form/form-to [:post "/users"]
        (form/text-field {:placeholder "Name"} "name")
        (form/email-field {:placeholder "Email"} "email")
        (form/submit-button "Create")))

; Conditional rendering
(html [:div
       (when logged-in?
         [:p "Welcome " username])
       (if admin?
         [:a {:href "/admin"} "Admin Panel"]
         [:a {:href "/user"} "Profile"])])
```

## Related Libraries

- metosin/reitit - Routing for web applications
- http-kit/http-kit - HTTP server

## Resources

- Official Documentation: https://github.com/weavejester/hiccup
- API Documentation: https://cljdoc.org/d/hiccup/hiccup

## Notes

This project uses Hiccup for generating HTML responses in web handlers.
