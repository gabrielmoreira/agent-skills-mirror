---
name: malli_schema_validation
description: |
  Validate data structures and schemas using Malli. Use when validating API 
  requests/responses, defining data contracts, building form validation, schema 
  validation, or when the user mentions schemas, validation, malli, data integrity, 
  type checking, data contracts, or runtime validation.
---

# Malli Data Validation

## Quick Start

Malli validates data against schemas. Schemas are just Clojure data structures:

```clojure
(require '[malli.core :as m])

;; Define a schema
(def user-schema
  [:map
   [:name string?]
   [:email string?]
   [:age int?]])

;; Validate data
(m/validate user-schema {:name "Alice" :email "alice@example.com" :age 30})
;; => true

(m/validate user-schema {:name "Bob" :age "thirty"})
;; => false

;; Get detailed errors
(m/explain user-schema {:name "Bob" :age "thirty"})
;; => {:errors [{:path [:email] :type :malli.core/missing-key}
;;              {:path [:age] :schema int? :value "thirty"}]}
```

**Key benefits:**
- **Data-driven** - Schemas are Clojure data, not special objects
- **Composable** - Build complex schemas from simple ones
- **Detailed errors** - Know exactly what's wrong
- **Fast** - Performance optimized with schema compilation
- **Extensible** - Add custom validators easily

## Core Concepts

### Schemas as Data

Schemas are vectors describing data structure:

```clojure
;; Simple predicates
int?        ; Any integer
string?     ; Any string
keyword?    ; Any keyword

;; Type schemas
:int        ; Integer type
:string     ; String type
:keyword    ; Keyword type

;; Constrained values
[:int {:min 0 :max 100}]           ; Integer between 0-100
[:string {:min 1 :max 50}]         ; String length 1-50
[:enum "red" "green" "blue"]       ; One of these values
```

### Validation vs Coercion

```clojure
;; Validation - Check if data matches
(m/validate [:int] 42)      ;; => true
(m/validate [:int] "42")    ;; => false

;; Coercion - Transform data to match (requires malli.transform)
(require '[malli.transform :as mt])

(m/decode [:int] "42" mt/string-transformer)
;; => 42

(m/decode [:int] "invalid" mt/string-transformer)
;; => "invalid" (can't coerce, returns original)
```

### Schema Registry

Register and reuse schemas:

```clojure
(require '[malli.core :as m])

(def registry
  {:user/id :int
   :user/email [:string {:min 3}]
   :user/user [:map
               [:id :user/id]
               [:email :user/email]]})

(def User [:schema {:registry registry} :user/user])

(m/validate User {:id 1 :email "alice@example.com"})
;; => true
```

## Common Workflows

### Workflow 1: API Request Validation

```clojure
(require '[malli.core :as m])

(def create-user-request
  [:map
   [:name [:string {:min 1 :max 100}]]
   [:email [:re #".+@.+\..+"]]
   [:age [:int {:min 0 :max 150}]]
   [:role [:enum "user" "admin" "guest"]]])

(defn validate-request [data]
  (if (m/validate create-user-request data)
    {:success true :data data}
    {:success false
     :errors (m/explain create-user-request data)}))

;; Valid request
(validate-request {:name "Alice"
                   :email "alice@example.com"
                   :age 30
                   :role "user"})
;; => {:success true :data {...}}

;; Invalid request
(validate-request {:name ""
                   :email "not-an-email"
                   :age 200
                   :role "superuser"})
;; => {:success false :errors {...}}
```

### Workflow 2: Composing Schemas

```clojure
(def address-schema
  [:map
   [:street string?]
   [:city string?]
   [:zip [:string {:pattern #"\d{5}"}]]])

(def person-schema
  [:map
   [:name string?]
   [:age int?]
   [:address address-schema]])  ; Compose schemas

(m/validate person-schema
  {:name "Bob"
   :age 25
   :address {:street "123 Main St"
             :city "Boston"
             :zip "02101"}})
;; => true
```

### Workflow 3: Optional and Default Values

```clojure
(def user-with-defaults
  [:map
   [:name string?]
   [:email string?]
   [:age [:int {:optional true}]]           ; Optional field
   [:role {:optional true} [:enum "user" "admin"]]  ; Optional with choices
   [:active {:optional true :default true} boolean?]])  ; Optional with default

;; Valid without optional fields
(m/validate user-with-defaults {:name "Alice" :email "alice@example.com"})
;; => true

;; Optional fields can be present
(m/validate user-with-defaults
  {:name "Alice" :email "alice@example.com" :age 30 :role "admin"})
;; => true
```

### Workflow 4: Collections

```clojure
;; Vector of specific type
(def user-ids [:vector :int])
(m/validate user-ids [1 2 3 4 5])  ;; => true
(m/validate user-ids [1 "2" 3])    ;; => false

;; Sequence of items (lazy)
(def lazy-ids [:sequential :int])
(m/validate lazy-ids (range 100))  ;; => true

;; Set of unique values
(def tags [:set :keyword])
(m/validate tags #{:clojure :malli :validation})  ;; => true

;; Map with specific value types
(def settings [:map-of :keyword :string])
(m/validate settings {:color "red" :theme "dark"})  ;; => true
```

### Workflow 5: Humanized Error Messages

```clojure
(require '[malli.error :as me])

(def user-schema
  [:map
   [:name [:string {:min 3}]]
   [:age [:int {:min 0 :max 150}]]])

(def invalid-data {:name "Al" :age 200})

;; Get human-readable errors
(-> user-schema
    (m/explain invalid-data)
    (me/humanize))
;; => {:name ["should be at least 3 characters"]
;;     :age ["should be at most 150"]}
```

### Workflow 6: Coercion and Transformation

```clojure
(require '[malli.transform :as mt])

(def coercible-schema
  [:map
   [:id :int]
   [:active :boolean]
   [:created :inst]])

;; Decode from string format (e.g., JSON)
(m/decode coercible-schema
  {:id "123"
   :active "true"
   :created "2024-01-01T00:00:00Z"}
  mt/string-transformer)
;; => {:id 123
;;     :active true
;;     :created #inst "2024-01-01T00:00:00.000-00:00"}

;; Encode to string format
(m/encode coercible-schema
  {:id 123
   :active true
   :created #inst "2024-01-01"}
  mt/string-transformer)
;; => {:id "123"
;;     :active "true"
;;     :created "2024-01-01T00:00:00Z"}
```

## When to Use Each Approach

**Use Malli when:**
- Validating external data (API requests, user input, config files)
- You need detailed, structured error messages
- Schemas should be data (can be stored, transmitted, generated)
- Building forms with validation
- Runtime type checking is needed
- You want to generate example data or docs from schemas

**Use clojure.spec when:**
- You need generative testing (test.check integration)
- Working with existing spec-based libraries
- Need instrumentation for development
- Prefer spec's conforming and unforming

**Use simple predicates when:**
- Validation is trivial (`string?`, `pos-int?`)
- Performance is absolutely critical
- No need for error messages
- Quick inline validation

**Don't use Malli when:**
- Static type checking is required (use typed Clojure or other language)
- Validation is too simple to justify overhead
- You only need compile-time checks

## Best Practices

**Do:**
- Define schemas as constants for reuse
- Use descriptive keys in maps
- Provide human-readable error messages with `me/humanize`
- Test schemas with valid and invalid data
- Use optional fields for non-required data
- Compose small schemas into larger ones
- Use schema registry for shared definitions
- Add `:min` and `:max` constraints where appropriate

**Don't:**
- Recreate schemas inline (define once, reuse)
- Make schemas overly strict (allow flexibility where needed)
- Ignore validation errors (always check return values)
- Skip testing edge cases
- Use validation for complex business logic (use functions)
- Validate data multiple times unnecessarily

## Common Issues

### Schema Doesn't Match Expected Structure

```clojure
;; Wrong: closed map doesn't allow extra keys
(def strict-schema [:map [:name string?]])
(m/validate strict-schema {:name "Alice" :age 30})
;; => false (age not allowed)

;; Right: allow extra keys
(def open-schema [:map {:closed false} [:name string?]])
(m/validate open-schema {:name "Alice" :age 30})
;; => true
```

### Optional Fields Not Working

```clojure
;; Wrong: field is required by default
(def schema [:map [:name string?] [:age int?]])
(m/validate schema {:name "Alice"})
;; => false (missing :age)

;; Right: mark as optional
(def schema [:map [:name string?] [:age {:optional true} int?]])
(m/validate schema {:name "Alice"})
;; => true
```

### Validation Too Slow

```clojure
;; Wrong: validating in hot path without compilation
(defn process [data]
  (when (m/validate big-schema data)  ; Validates schema each time
    (do-work data)))

;; Right: compile schema once
(def validator (m/validator big-schema))

(defn process [data]
  (when (validator data)  ; Use compiled validator
    (do-work data)))
```

### Coercion Not Working

```clojure
;; Problem: coercion requires transformer
(m/decode [:int] "42")  ; Doesn't work!

;; Solution: provide transformer
(require '[malli.transform :as mt])
(m/decode [:int] "42" mt/string-transformer)
;; => 42

;; Or create decoder once
(def decode-user (m/decoder user-schema mt/string-transformer))
(decode-user {:id "123" :name "Alice"})
```

## Advanced Topics

### Custom Validators

```clojure
(def email-regex #".+@.+\..+")

(def Email
  (m/-simple-schema
    {:type :email
     :pred (fn [x] (and (string? x) (re-matches email-regex x)))
     :type-properties {:error/message "should be a valid email"}}))

(m/validate Email "alice@example.com")  ;; => true
(m/validate Email "invalid")            ;; => false
```

### Schema Generation

```clojure
(require '[malli.generator :as mg])

;; Generate random valid data
(mg/generate user-schema)
;; => {:name "aB7x" :email "Cd@e.f" :age 42}

;; Generate multiple samples
(mg/sample user-schema {:size 3})
;; => [{:name "x" ...} {:name "yz" ...} {:name "abc" ...}]
```

### Schema Transformation

```clojure
(require '[malli.util :as mu])

;; Merge schemas
(mu/merge
  [:map [:a int?]]
  [:map [:b string?]])
;; => [:map [:a int?] [:b string?]]

;; Make all fields optional
(mu/optional-keys user-schema)

;; Make all fields required
(mu/required-keys user-schema)
```

## Related Libraries

- clojure.spec.alpha - Alternative validation approach
- metosin/reitit - Uses Malli for route data validation
- metosin/malli - Core library

## External Resources

- [Official Documentation](https://github.com/metosin/malli)
- [API Documentation](https://cljdoc.org/d/metosin/malli)
- [Malli Tutorial](https://github.com/metosin/malli#tutorial)
- [Comparison with spec](https://github.com/metosin/malli/blob/master/docs/comparisons.md)

## Summary

Malli provides data-driven schema validation for Clojure:

1. **Schemas as data** - Easy to compose, inspect, and transform
2. **Rich validation** - Predicates, constraints, collections, maps
3. **Detailed errors** - Know exactly what's invalid
4. **Coercion** - Transform data to match schemas
5. **Extensible** - Add custom validators and transformers

Use Malli for validating external data, defining contracts, and ensuring data integrity at runtime.
