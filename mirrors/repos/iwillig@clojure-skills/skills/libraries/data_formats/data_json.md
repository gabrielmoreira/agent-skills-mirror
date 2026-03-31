---
name: clojure_data_json_parsing
description: JSON parsing and generation for Clojure.
---

# data.json

Clojure's official library for reading and writing JSON data.

## Overview

org.clojure/data.json provides functions for parsing JSON strings into Clojure data structures and converting Clojure data back to JSON.

## Core Concepts

**Reading JSON**: Parse JSON strings into Clojure data.

```clojure
(require '[clojure.data.json :as json])

(json/read-str "{\"name\": \"Alice\", \"age\": 30}")
; => {"name" "Alice", "age" 30}

; With keyword keys
(json/read-str "{\"name\": \"Alice\", \"age\": 30}" :key-fn keyword)
; => {:name "Alice", :age 30}
```

**Writing JSON**: Convert Clojure data to JSON strings.

```clojure
(json/write-str {:name "Alice" :age 30})
; => "{\"name\":\"Alice\",\"age\":30}"

; Pretty printing
(json/write-str {:name "Alice" :age 30} :value-fn identity)
```

## Key Features

- Simple read/write API
- Customizable key conversion (strings to keywords)
- Custom value handling
- Streaming support
- Performance optimized

## When to Use

- Parsing JSON from HTTP responses
- Sending JSON in HTTP requests
- Serializing Clojure data to JSON
- Working with APIs

## When NOT to Use

- For complex transformations (use a data transformation library)
- When you need advanced features (consider other JSON libraries)

## Common Patterns

```clojure
; Reading API response
(require '[clojure.data.json :as json])

(def api-response "{\"users\": [{\"id\": 1, \"name\": \"Alice\"}]}")
(def data (json/read-str api-response :key-fn keyword))
; => {:users [{:id 1, :name "Alice"}]}

; Writing JSON response
(def user-data {:id 1 :name "Alice" :email "alice@example.com"})
(json/write-str user-data)
; => "{\"id\":1,\"name\":\"Alice\",\"email\":\"alice@example.com\"}"
```

## Related Libraries

- cheshire/cheshire - Alternative JSON library with more features
- hiccup/hiccup - HTML generation (often paired with JSON APIs)

## Resources

- Official Documentation: https://github.com/clojure/data.json
- API Documentation: https://cljdoc.org/d/org.clojure/data.json

## Notes

This project uses data.json for JSON serialization in HTTP responses and parsing incoming JSON data.
