---
name: plumatic-schema
description: |
  Data validation and schema definition using Plumatic Schema. Use when validating data
  structures, defining APIs, type checking at runtime, documenting data shapes, or when
  the user mentions schema, validation, prismatic schema, plumatic schema, data contracts,
  function validation, or runtime type checking.
---

# Plumatic Schema

A Clojure library for declarative data description and validation with optional runtime checking.

## Quick Start

Schema provides declarative, expressive schemas for Clojure data structures:

```clojure
;; Add dependency
{:deps {prismatic/schema {:mvn/version "1.4.1"}}}

;; Basic usage
(require '[schema.core :as s])

;; Define a schema
(def User
  {:name s/Str
   :age s/Int
   :email s/Str})

;; Validate data
(s/validate User {:name "Alice" :age 30 :email "alice@example.com"})
;; => {:name "Alice", :age 30, :email "alice@example.com"}

;; Validation failure throws exception
(s/validate User {:name "Bob" :age "not-an-int" :email "bob@example.com"})
;; ExceptionInfo Value does not match schema:
;; {:age (not (integer? "not-an-int"))}
```

**Key benefits:**
- Declarative data description
- Optional runtime validation
- Function input/output validation
- Automatic documentation
- Composable schemas
- Zero performance cost when validation disabled

## Core Concepts

### Built-in Schema Types

Schema provides predefined types for common values:

```clojure
;; Primitive types
s/Str        ; String
s/Int        ; Integer (Java long/int)
s/Num        ; Number (any numeric type)
s/Bool       ; Boolean
s/Keyword    ; Keyword
s/Symbol     ; Symbol
s/Inst       ; java.util.Date or Instant
s/Uuid       ; java.util.UUID
s/Regex      ; Regular expression pattern
s/Any        ; Any value (always validates)

;; Examples
(s/validate s/Str "hello")        ;; => "hello"
(s/validate s/Int 42)             ;; => 42
(s/validate s/Keyword :status)    ;; => :status
(s/validate s/Any {:anything 1})  ;; => {:anything 1}
```

### Map Schemas

Define schemas for maps with required and optional keys:

```clojure
;; Map with required keys
(def User
  {:name s/Str
   :age s/Int
   :email s/Str})

(s/validate User {:name "Alice" :age 30 :email "alice@example.com"})
;; => {:name "Alice", :age 30, :email "alice@example.com"}

;; Map with optional keys
(def UserWithOptional
  {:name s/Str
   :age s/Int
   (s/optional-key :email) s/Str
   (s/optional-key :phone) s/Str})

(s/validate UserWithOptional {:name "Bob" :age 25})
;; => {:name "Bob", :age 25}

(s/validate UserWithOptional {:name "Charlie" :age 35 :email "charlie@example.com"})
;; => {:name "Charlie", :age 35, :email "charlie@example.com"}

;; Allow extra keys
(def OpenMap
  {s/Keyword s/Any})  ; Any keyword keys with any values

(s/validate OpenMap {:foo 1 :bar "two" :baz [3]})
;; => {:foo 1, :bar "two", :baz [3]}
```

### Collection Schemas

Validate sequences, vectors, sets, and maps:

```clojure
;; Vector of integers
(s/validate [s/Int] [1 2 3 4])
;; => [1 2 3 4]

;; Set of strings
(s/validate #{s/Str} #{"a" "b" "c"})
;; => #{"a" "b" "c"}

;; Map with specific key/value types
(s/validate {s/Keyword s/Int} {:a 1 :b 2 :c 3})
;; => {:a 1, :b 2, :c 3}

;; Fixed-length sequence with different types
(def Pair [(s/one s/Str "first") (s/one s/Int "second")])
(s/validate Pair ["hello" 42])
;; => ["hello" 42]

;; Variable-length with optional elements
(def FlexSeq [(s/one s/Str "required") (s/optional s/Int "optional-int")])
(s/validate FlexSeq ["hello"])
;; => ["hello"]
(s/validate FlexSeq ["hello" 42])
;; => ["hello" 42]
```

### Schema Combinators

Build complex schemas by combining simpler ones:

```clojure
;; maybe - nullable value
(def MaybeStr (s/maybe s/Str))
(s/validate MaybeStr "hello")  ;; => "hello"
(s/validate MaybeStr nil)      ;; => nil

;; either - union types
(def StringOrInt (s/either s/Str s/Int))
(s/validate StringOrInt "hello")  ;; => "hello"
(s/validate StringOrInt 42)       ;; => 42

;; enum - specific values
(def Status (s/enum :active :inactive :pending))
(s/validate Status :active)  ;; => :active

;; both - intersection (all must match)
(def PositiveInt (s/both s/Int (s/pred pos? 'positive)))
(s/validate PositiveInt 5)  ;; => 5
```

## Common Workflows

### Workflow 1: Validating API Requests

Use Schema to validate incoming API data:

```clojure
(require '[schema.core :as s])

;; Define request schema
(def CreateUserRequest
  {:name s/Str
   :email s/Str
   :age s/Int
   (s/optional-key :phone) s/Str})

;; Validation function
(defn validate-request [schema data]
  (try
    {:valid? true
     :data (s/validate schema data)}
    (catch Exception e
      {:valid? false
       :errors (ex-data e)})))

;; Usage in handler
(defn create-user-handler [request-body]
  (let [validation (validate-request CreateUserRequest request-body)]
    (if (:valid? validation)
      {:status 200 :body {:user (:data validation)}}
      {:status 400 :body {:errors (:errors validation)}})))

;; Test valid request
(create-user-handler {:name "Alice" :email "alice@example.com" :age 30})
;; => {:status 200, :body {:user {:name "Alice", :email "alice@example.com", :age 30}}}

;; Test invalid request
(create-user-handler {:name "Bob" :age "not-an-int"})
;; => {:status 400, :body {:errors {...}}}
```

### Workflow 2: Function Input/Output Validation

Use `s/defn` to add schemas to function signatures:

```clojure
;; Define function with input/output schemas
(s/defn add :- s/Int
  "Add two integers"
  [x :- s/Int
   y :- s/Int]
  (+ x y))

;; Call normally (validation off by default in production)
(add 5 10)
;; => 15

;; Enable validation for development
(s/with-fn-validation
  (add 5 10))
;; => 15

;; Invalid call with validation enabled
(s/with-fn-validation
  (try
    (add "5" 10)
    (catch Exception e
      {:error (.getMessage e)})))
;; => {:error "Input to add does not match schema: [...]"}

;; Enable validation globally (typically in dev mode)
(s/set-fn-validation! true)

;; Multiple arities with different schemas
(s/defn greet :- s/Str
  ([name :- s/Str]
   (str "Hello, " name "!"))
  ([title :- s/Str
    name :- s/Str]
   (str "Hello, " title " " name "!")))

(greet "Alice")
;; => "Hello, Alice!"

(greet "Dr." "Smith")
;; => "Hello, Dr. Smith!"
```

### Workflow 3: Custom Validators with Predicates

Create schemas using predicates and constraints:

```clojure
;; Predicate schema
(def PositiveInt (s/pred pos-int? 'positive-integer))
(s/validate PositiveInt 5)   ;; => 5

;; Constrained schema (more descriptive)
(def Email
  (s/constrained s/Str
                 #(re-matches #".+@.+\..+" %)
                 'valid-email))

(s/validate Email "test@example.com")
;; => "test@example.com"

;; Multiple constraints
(def Password
  (s/constrained s/Str
                 #(>= (count %) 8)
                 'min-length-8))

;; Combining constraints
(def StrongPassword
  (s/both
    (s/constrained s/Str #(>= (count %) 8) 'min-8-chars)
    (s/constrained s/Str #(re-find #"[A-Z]" %) 'has-uppercase)
    (s/constrained s/Str #(re-find #"[0-9]" %) 'has-digit)))

(s/validate StrongPassword "SecurePass123")
;; => "SecurePass123"

;; Custom predicate with named schema
(def NonEmptyString
  (s/constrained s/Str (complement empty?) 'non-empty-string))
```

### Workflow 4: Nested and Recursive Schemas

Define schemas for nested and recursive data structures:

```clojure
;; Nested schemas
(def Address
  {:street s/Str
   :city s/Str
   :zip s/Str})

(def Person
  {:name s/Str
   :age s/Int
   :address Address})  ; Nested schema

(s/validate Person
  {:name "Alice"
   :age 30
   :address {:street "123 Main St"
             :city "Springfield"
             :zip "12345"}})
;; => Valid person map

;; Recursive schemas (tree structure)
(declare TreeSchema)
(def TreeSchema
  {:value s/Int
   :children [(s/recursive #'TreeSchema)]})

(s/validate TreeSchema
  {:value 1
   :children [{:value 2 :children []}
              {:value 3 :children [{:value 4 :children []}]}]})
;; => Valid tree

;; Recursive with maybe (for leaf nodes)
(declare NodeSchema)
(def NodeSchema
  {:id s/Str
   :data s/Any
   :next (s/maybe (s/recursive #'NodeSchema))})

(s/validate NodeSchema
  {:id "1"
   :data {:foo "bar"}
   :next {:id "2"
          :data {:baz "qux"}
          :next nil}})
;; => Valid linked list
```

### Workflow 5: Schema Introspection and Documentation

Use schemas for documentation and introspection:

```clojure
;; Explain a schema (returns human-readable description)
(s/explain User)
;; => {:name Str, :age Int, :email Str}

;; Check without throwing (returns error map or nil)
(s/check User {:name "Bob" :age "not-an-int" :email "bob@example.com"})
;; => {:age (not (integer? "not-an-int"))}

(s/check User {:name "Alice" :age 30 :email "alice@example.com"})
;; => nil (valid)

;; Use defschema for named, reusable schemas
(s/defschema UserSchema
  "A schema for user data"
  {:name s/Str
   :age (s/constrained s/Int pos? 'positive-age)
   :email Email
   (s/optional-key :phone) s/Str})

;; Access schema metadata
(s/explain UserSchema)
;; Shows complete schema structure

;; Validator function (reusable)
(def validate-user (s/validator UserSchema))

(validate-user {:name "Charlie" :age 35 :email "charlie@example.com"})
;; => true (returns boolean, throws on failure)
```

### Workflow 6: Records with Schema Validation

Define records with schema validation:

```clojure
;; Define record with schema
(s/defrecord Person
  [name :- s/Str
   age :- s/Int
   email :- (s/maybe s/Str)])

;; Create instance
(->Person "Alice" 30 "alice@example.com")
;; => #user.Person{:name "Alice", :age 30, :email "alice@example.com"}

;; Map constructor with validation
(map->Person {:name "Bob" :age 25 :email nil})
;; => #user.Person{:name "Bob", :age 25, :email nil}

;; Schema validation with records
(s/validate Person (->Person "Charlie" 35 "charlie@example.com"))
;; => #user.Person{:name "Charlie", :age 35, :email "charlie@example.com"}

;; Invalid record (caught during construction with fn validation)
(s/with-fn-validation
  (try
    (->Person "Dave" "not-an-int" "dave@example.com")
    (catch Exception e
      {:error true})))
;; => {:error true}
```

### Workflow 7: Coercion for String/JSON Data

Use coercion to transform data before validation:

```clojure
(require '[schema.coerce :as coerce])

;; Define schema
(def UserInput
  {:name s/Str
   :age s/Int
   :active s/Bool})

;; String coercion (e.g., from query params)
(def string-coercer (coerce/coercer UserInput coerce/string-coercion-matcher))

(string-coercer {:name "Alice" :age "30" :active "true"})
;; => {:name "Alice", :age 30, :active true}

;; JSON coercion (e.g., from JSON API)
(def json-coercer (coerce/coercer UserInput coerce/json-coercion-matcher))

(json-coercer {:name "Bob" :age 25 :active true})
;; => {:name "Bob", :age 25, :active true}

;; Custom coercion
(defn custom-matcher [schema]
  (or (coerce/string-coercion-matcher schema)
      (when (= schema s/Keyword)
        #(if (string? %) (keyword %) %))))

(def custom-coercer (coerce/coercer {:status s/Keyword} custom-matcher))

(custom-coercer {:status "active"})
;; => {:status :active}

;; Handle coercion errors
(defn safe-coerce [coercer data]
  (let [result (coercer data)]
    (if (schema.utils/error? result)
      {:valid? false :error (schema.utils/error-val result)}
      {:valid? true :data result})))

(safe-coerce string-coercer {:name "Eve" :age "not-a-number" :active "true"})
;; => {:valid? false, :error {...}}
```

## When to Use Schema vs Alternatives

**Use Schema when:**
- Need declarative data validation
- Want optional runtime checking
- Building APIs with clear contracts
- Need automatic documentation from schemas
- Working with existing Clojure/Java interop
- Performance with validation off is critical
- Want gradual typing approach

**Use Malli when:**
- Need advanced schema transformations
- Want better error messages out of the box
- Need schema-driven development features
- Building data-driven applications
- Want first-class schema values

**Use clojure.spec when:**
- Need generative testing
- Want spec'ed core library functions
- Building instrumentation for development
- Need detailed conformance and explanations
- Working primarily with Clojure 1.9+

**Schema advantages:**
- Simpler, more straightforward API
- Better performance (especially with validation off)
- Cleaner syntax for function schemas
- Widespread adoption and stability
- Works well with older Clojure versions

## Best Practices

**DO:**
- Use `s/defschema` for reusable, documented schemas
- Enable validation in development: `(s/set-fn-validation! true)`
- Disable validation in production (default) for performance
- Use `s/check` instead of `s/validate` when you don't want exceptions
- Use `(s/optional-key :key)` for optional map keys
- Use predicates and constraints for custom validation
- Leverage coercion for external data (APIs, forms)
- Document schemas with docstrings in `defschema`

**DON'T:**
- Leave validation on in production (performance cost)
- Use Schema for generative testing (use spec or test.check)
- Over-complicate schemas (keep them readable)
- Forget to handle validation errors gracefully
- Use `s/Any` everywhere (defeats the purpose)
- Mix validation approaches (Schema and spec) in same codebase
- Ignore coercion errors (check for `schema.utils/error?`)

## Common Issues

### Issue: Validation Not Running

**Problem:** Function validation doesn't throw errors

```clojure
(s/defn add :- s/Int
  [x :- s/Int, y :- s/Int]
  (+ x y))

(add "not-int" 5)  ; No error!
```

**Solution:** Enable validation explicitly

```clojure
;; Option 1: Wrap in with-fn-validation
(s/with-fn-validation
  (add "not-int" 5))
;; => ExceptionInfo

;; Option 2: Enable globally for development
(s/set-fn-validation! true)
(add "not-int" 5)
;; => ExceptionInfo

;; Option 3: Use validator directly
(def validate-user (s/validator User))
(validate-user {:name "Alice" :age "not-int"})
;; => ExceptionInfo
```

### Issue: Extra Keys Failing Validation

**Problem:** Map has extra keys not in schema

```clojure
(def User {:name s/Str :age s/Int})

(s/validate User {:name "Alice" :age 30 :extra "data"})
;; => ExceptionInfo: {:extra disallowed-key}
```

**Solution:** Allow extra keys explicitly

```clojure
;; Option 1: Use s/Any for any additional keys
(def UserOpen
  (assoc User s/Keyword s/Any))

(s/validate UserOpen {:name "Alice" :age 30 :extra "data"})
;; => {:name "Alice", :age 30, :extra "data"}

;; Option 2: Mark all keys as optional/open
(def UserPermissive
  (merge User {(s/optional-key s/Keyword) s/Any}))
```

### Issue: Coercion Returning Error Container

**Problem:** Coercion returns `ErrorContainer` instead of throwing

```clojure
(def coercer (coerce/coercer User coerce/json-coercion-matcher))
(coercer {:name "Alice" :age "not-int"})
;; => #schema.utils.ErrorContainer{:error {...}}
```

**Solution:** Check for errors explicitly

```clojure
(require '[schema.utils :as utils])

(defn safe-coerce [coercer data]
  (let [result (coercer data)]
    (if (utils/error? result)
      {:error (utils/error-val result)}
      {:data result})))

(safe-coerce coercer {:name "Alice" :age "not-int"})
;; => {:error {:age (not (integer? "not-int"))}}

(safe-coerce coercer {:name "Bob" :age 25})
;; => {:data {:name "Bob", :age 25}}
```

### Issue: Recursive Schema Not Working

**Problem:** Recursive schema fails to compile

```clojure
(def Tree {:value s/Int :children [Tree]})  ; Error!
```

**Solution:** Use `s/recursive` with var reference

```clojure
;; Declare var first
(declare TreeSchema)

;; Define with recursive reference
(def TreeSchema
  {:value s/Int
   :children [(s/recursive #'TreeSchema)]})

(s/validate TreeSchema {:value 1 :children []})
;; => {:value 1, :children []}
```

### Issue: Optional Keys Still Required

**Problem:** Optional keys cause validation failure when absent

```clojure
(def User {:name s/Str (s/optional-key :email) s/Str})

(s/validate User {:name "Alice"})
;; Works! (correct behavior)

;; But this might seem confusing:
(def WrongUser {:name s/Str :email (s/maybe s/Str)})
(s/validate WrongUser {:name "Alice"})
;; => ExceptionInfo: :email missing-required-key
```

**Solution:** Understand the difference between optional-key and maybe

```clojure
;; optional-key: key may be absent
(def UserOptionalKey
  {:name s/Str
   (s/optional-key :email) s/Str})

(s/validate UserOptionalKey {:name "Alice"})
;; => {:name "Alice"} (valid, :email absent)

;; maybe: key must be present but value can be nil
(def UserMaybe
  {:name s/Str
   :email (s/maybe s/Str)})

(s/validate UserMaybe {:name "Alice" :email nil})
;; => {:name "Alice", :email nil} (valid, :email present with nil)

;; Combine for truly optional nullable
(def UserOptionalMaybe
  {:name s/Str
   (s/optional-key :email) (s/maybe s/Str)})

(s/validate UserOptionalMaybe {:name "Alice"})
;; => {:name "Alice"} (valid, :email absent)

(s/validate UserOptionalMaybe {:name "Bob" :email nil})
;; => {:name "Bob", :email nil} (valid, :email present with nil)
```

## Advanced Topics

### Protocol Schemas

Validate protocol implementations:

```clojure
(defprotocol IFoo
  (foo [this]))

(s/defschema FooProtocol
  (s/protocol IFoo))

;; Validates that value implements IFoo
```

### Conditional Schemas

Use `cond-pre` for conditional validation based on structure:

```clojure
(def IntOrStringMap
  (s/cond-pre s/Int {:value s/Str}))

(s/validate IntOrStringMap 42)
;; => 42

(s/validate IntOrStringMap {:value "hello"})
;; => {:value "hello"}
```

### Schema Transformation

Transform schemas programmatically:

```clojure
;; Make all keys optional
(defn make-optional [schema]
  (into {}
    (map (fn [[k v]]
           [(if (keyword? k) (s/optional-key k) k) v])
         schema)))

(def OptionalUser (make-optional User))
```

## Resources

- [GitHub Repository](https://github.com/plumatic/schema)
- [API Documentation](https://cljdoc.org/d/prismatic/schema)
- [Wiki](https://github.com/plumatic/schema/wiki)
- [Coercion Guide](https://github.com/plumatic/schema/wiki/Coercion)

## Summary

Plumatic Schema provides declarative, runtime data validation for Clojure:

1. **Simple syntax** - Schemas are just Clojure data
2. **Optional validation** - Enable in dev, disable in prod
3. **Function schemas** - Validate inputs/outputs with s/defn
4. **Composable** - Build complex schemas from simple ones
5. **Coercion** - Transform data before validation
6. **Documentation** - Schemas serve as documentation
7. **Performance** - Zero cost when validation disabled

Use Schema for runtime data validation, API contracts, and gradual typing in Clojure applications.
