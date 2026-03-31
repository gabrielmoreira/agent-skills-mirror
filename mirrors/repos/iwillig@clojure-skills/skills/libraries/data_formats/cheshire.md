---
name: cheshire-json
description: |
  Fast JSON encoding and decoding for Clojure. Use when working with JSON APIs,
  parsing JSON data, generating JSON responses, or when you need to serialize/deserialize
  Clojure data structures to/from JSON. Supports custom encoders, streaming, pretty printing,
  SMILE format, and date/UUID/Set encoding. Ideal for REST APIs, web services, and data exchange.
---

# Cheshire - JSON for Clojure

## Quick Start

Cheshire provides fast, idiomatic JSON encoding/decoding with extensive Clojure type support.

```clojure
(require '[cheshire.core :as json])

;; Encode Clojure data to JSON string
(json/generate-string {:name "Alice" :age 30 :hobbies ["coding" "reading"]})
; => "{\"name\":\"Alice\",\"age\":30,\"hobbies\":[\"coding\",\"reading\"]}"

;; Decode JSON string to Clojure data
(json/parse-string "{\"name\":\"Bob\",\"age\":25}")
; => {"name" "Bob", "age" 25}  ; String keys by default

;; Decode with keyword keys
(json/parse-string "{\"name\":\"Bob\",\"age\":25}" true)
; => {:name "Bob", :age 25}  ; Keywords

;; Pretty printing
(json/generate-string {:name "Alice" :data {:x 1 :y 2}} {:pretty true})
; => {
;      "name" : "Alice",
;      "data" : {
;        "x" : 1,
;        "y" : 2
;      }
;    }
```

**Key benefits:**
- Fast performance (2x faster than data.json)
- Rich type support (dates, UUIDs, sets, ratios)
- Custom encoders for any type
- Stream encoding/decoding
- SMILE (binary JSON) support

## Core Concepts

### Encoding vs. Decoding

**Encoding**: Clojure data → JSON string
- `generate-string` - Main encoding function
- `generate-stream` - Write JSON to stream
- `generate-smile` - Binary format encoding

**Decoding**: JSON string → Clojure data
- `parse-string` - Parse JSON string
- `parse-stream` - Parse from stream
- `parsed-seq` - Lazy parsing for multiple objects

**Aliases**: `encode`/`decode` are aliases for users coming from other libraries.

### Key Transformation

By default:
- **Encoding**: Clojure keywords → JSON strings (`:name` → `"name"`)
- **Decoding**: JSON strings → Clojure strings (`"name"` → `"name"`)

Pass `true` as second argument to `parse-string` for keyword keys:

```clojure
(json/parse-string "{\"name\":\"Alice\"}" true)
; => {:name "Alice"}
```

Or provide custom key transformation function:

```clojure
;; Encoding: transform keys to UPPERCASE
(json/generate-string {:first-name "Alice"} 
                      {:key-fn (fn [k] (.toUpperCase (name k)))})
; => "{\"FIRST-NAME\":\"Alice\"}"

;; Decoding: transform keys to keywords with custom logic
(json/parse-string "{\"firstName\":\"Alice\"}" 
                   (fn [k] (keyword (.toLowerCase k))))
; => {:firstname "Alice"}
```

### Type Support

Cheshire automatically encodes:
- **Primitives**: strings, numbers, booleans, nil
- **Collections**: vectors, lists, sets, maps
- **Clojure types**: keywords, symbols, ratios
- **Java types**: Date, UUID, Timestamp
- **Custom types**: Via custom encoders

## Common Workflows

### Workflow 1: REST API JSON Responses

Generate JSON for HTTP responses:

```clojure
(require '[cheshire.core :as json])

(defn user-handler [request]
  {:status 200
   :headers {"Content-Type" "application/json"}
   :body (json/generate-string 
           {:id 42
            :name "Alice Smith"
            :email "alice@example.com"
            :created-at (java.util.Date.)})})

;; With pretty printing for debugging
(defn debug-handler [request]
  {:status 200
   :headers {"Content-Type" "application/json"}
   :body (json/generate-string 
           {:data {:users [1 2 3] :count 3}}
           {:pretty true})})
```

### Workflow 2: Parsing API Responses

Parse JSON from external APIs:

```clojure
;; Parse with string keys
(def response "{\"id\":123,\"status\":\"active\",\"items\":[1,2,3]}")
(json/parse-string response)
; => {"id" 123, "status" "active", "items" [1 2 3]}

;; Parse with keyword keys (recommended)
(json/parse-string response true)
; => {:id 123, :status "active", :items [1 2 3]}

;; Access parsed data
(let [data (json/parse-string response true)]
  {:item-count (count (:items data))
   :is-active? (= "active" (:status data))})
```

### Workflow 3: Encoding Rich Clojure Types

Cheshire handles dates, UUIDs, and sets automatically:

```clojure
(json/generate-string
  {:id (java.util.UUID/randomUUID)
   :created (java.util.Date. 0)
   :tags #{:clojure :json :fast}
   :ratio 22/7})
; => "{\"id\":\"a1b2c3...\",\"created\":\"1970-01-01T00:00:00Z\",
;      \"tags\":[\"fast\",\"json\",\"clojure\"],\"ratio\":\"22/7\"}"

;; Custom date format
(json/generate-string 
  {:timestamp (java.util.Date. 0)}
  {:date-format "yyyy-MM-dd"})
; => "{\"timestamp\":\"1970-01-01\"}"

;; More date formats
(json/generate-string 
  {:timestamp (java.util.Date. 0)}
  {:date-format "MM/dd/yyyy HH:mm"})
; => "{\"timestamp\":\"01/01/1970 00:00\"}"
```

### Workflow 4: Stream Processing

Encode/decode large data without loading everything into memory:

```clojure
(require '[clojure.java.io :as io])

;; Write JSON to file
(with-open [w (io/writer "data.json")]
  (json/generate-stream 
    {:users [{:id 1 :name "Alice"}
             {:id 2 :name "Bob"}]
     :count 2}
    w))

;; Read JSON from file
(with-open [r (io/reader "data.json")]
  (json/parse-stream r true))
; => {:users [{:id 1 :name "Alice"} {:id 2 :name "Bob"}], :count 2}

;; Lazy parsing of multiple JSON objects
(with-open [r (io/reader "stream.json")]
  (doall (json/parsed-seq r true)))
; Parses each top-level object lazily
```

**Use case**: Processing large log files, streaming APIs, batch exports.

### Workflow 5: Custom Encoders

Encode custom types with custom logic:

```clojure
(require '[cheshire.generate :as gen])

;; Example: Encode java.awt.Color as hex string
(import 'java.awt.Color)
(gen/add-encoder 
  java.awt.Color
  (fn [color json-generator]
    (.writeString json-generator 
                  (format "#%02x%02x%02x" 
                          (.getRed color)
                          (.getGreen color)
                          (.getBlue color)))))

(json/generate-string {:bg-color (Color. 255 128 64)})
; => "{\"bg-color\":\"#ff8040\"}"

;; Example: Encode java.net.URL as string (using helper)
(gen/add-encoder java.net.URL gen/encode-str)

(json/generate-string {:website (java.net.URL. "https://example.com")})
; => "{\"website\":\"https://example.com\"}"

;; Remove custom encoder
(gen/remove-encoder java.awt.Color)
```

**Available encoder helpers:**
- `encode-str` - Encode as string
- `encode-nil` - Encode as null
- `encode-number` - Encode as number
- `encode-bool` - Encode as boolean
- `encode-seq` - Encode as array
- `encode-map` - Encode as object
- `encode-date` - Encode as date string
- `encode-symbol` - Encode symbol
- `encode-ratio` - Encode ratio

### Workflow 6: Key Transformation Patterns

Transform keys during encoding/decoding:

```clojure
;; camelCase to kebab-case (decoding)
(json/parse-string 
  "{\"firstName\":\"Alice\",\"lastName\":\"Smith\"}"
  (fn [k] (keyword (clojure.string/replace k #"([A-Z])" "-$1"))))
; => {:first-Name "Alice", :last-Name "Smith"}

;; kebab-case to camelCase (encoding)
(defn ->camelCase [k]
  (let [parts (clojure.string/split (name k) #"-")]
    (apply str (first parts) 
           (map clojure.string/capitalize (rest parts)))))

(json/generate-string {:first-name "Alice" :last-name "Smith"}
                      {:key-fn ->camelCase})
; => "{\"firstName\":\"Alice\",\"lastName\":\"Smith\"}"

;; Namespace-qualified keywords
(json/generate-string {:user/id 42 :user/name "Alice"}
                      {:key-fn name})  ; Remove namespace
; => "{\"id\":42,\"name\":\"Alice\"}"
```

### Workflow 7: Working with BigDecimals

Control numeric precision for financial/scientific data:

```clojure
(require '[cheshire.parse :as parse])

;; Default: uses Double (loses precision)
(json/parse-string "111111111111111111111111111111111.111111111111111111111111111111111111")
; => 1.1111111111111112E32  ; Double approximation

;; With BigDecimal (preserves precision)
(binding [parse/*use-bigdecimals?* true]
  (json/parse-string "111111111111111111111111111111111.111111111111111111111111111111111111"))
; => 111111111111111111111111111111111.111111111111111111111111111111111111M

;; Practical use: financial calculations
(binding [parse/*use-bigdecimals?* true]
  (let [data (json/parse-string "{\"price\":9.99,\"tax\":0.08}")]
    (* (:price data) (+ 1M (:tax data)))))
; => 10.7892M  ; Exact decimal arithmetic
```

## When to Use Cheshire

**Use Cheshire when:**
- Building REST APIs that consume/produce JSON
- Parsing JSON from external services
- You need rich type support (dates, UUIDs, sets)
- Performance matters (it's fast!)
- Custom type encoding is needed
- Streaming large JSON data
- Pretty-printing for debugging

**Use data.json when:**
- Minimal dependencies required
- Only basic JSON types needed
- Performance is less critical

**Use transit when:**
- Communicating between Clojure/ClojureScript systems
- Need more efficient binary format
- Want to preserve more Clojure semantics

**Use jsonista when:**
- Need maximum performance (jsonista is slightly faster)
- Working with Jackson directly
- Prefer malli integration

## Best Practices

**Do:**
- Use `:key-fn true` when parsing to get keyword keys (more idiomatic)
- Stream large data with `generate-stream` and `parse-stream`
- Use custom date formats for consistent timestamp encoding
- Add custom encoders for domain types
- Use `{:pretty true}` for debugging/logging
- Bind `*use-bigdecimals?*` for financial calculations
- Test edge cases: `nil`, empty collections, special characters

```clojure
;; Good: keyword keys are idiomatic
(let [data (json/parse-string json-str true)]
  (:name data))

;; Good: stream large files
(with-open [r (io/reader "large.json")]
  (json/parse-stream r true))

;; Good: custom encoder for domain type
(gen/add-encoder my.app.User
  (fn [user gen]
    (.writeString gen (:username user))))
```

**Don't:**
- Parse large files into memory with `parse-string` (use `parse-stream`)
- Forget to specify date format if format matters
- Hardcode JSON strings in tests (use `generate-string` for consistency)
- Mix string and keyword keys in same codebase
- Skip custom encoders for frequently-encoded types

```clojure
;; Bad: reading huge file into string
(json/parse-string (slurp "huge.json"))  ; OOM risk

;; Good: stream it
(with-open [r (io/reader "huge.json")]
  (json/parse-stream r true))

;; Bad: inconsistent key style
(let [data (json/parse-string s)]  ; String keys
  (:name data))  ; Won't work! Keys are strings

;; Good: consistent keyword keys
(let [data (json/parse-string s true)]
  (:name data))
```

## Common Issues

### Issue: Keywords not working after parsing

```clojure
(let [data (json/parse-string "{\"name\":\"Alice\"}")]
  (:name data))
; => nil  ; Keys are strings, not keywords!
```

**Solution**: Pass `true` to get keyword keys:

```clojure
(let [data (json/parse-string "{\"name\":\"Alice\"}" true)]
  (:name data))
; => "Alice"
```

### Issue: Sets encode differently each time

```clojure
(json/generate-string {:tags #{:a :b :c}})
; => "{\"tags\":[\"b\",\"c\",\"a\"]}"  ; Order varies (sets are unordered)
```

**Solution**: This is expected (sets have no defined order). If order matters, use vectors:

```clojure
(json/generate-string {:tags (sort #{:a :b :c})})
; => "{\"tags\":[\"a\",\"b\",\"c\"]}"  ; Consistent order
```

### Issue: Dates encode in unexpected format

```clojure
(json/generate-string {:time (java.util.Date.)})
; => "{\"time\":\"2025-01-10T14:30:00Z\"}"  ; ISO format
```

**Solution**: Specify custom date format:

```clojure
(json/generate-string {:time (java.util.Date.)}
                      {:date-format "yyyy-MM-dd"})
; => "{\"time\":\"2025-01-10\"}"
```

### Issue: Large numbers lose precision

```clojure
(json/parse-string "99999999999999999999.99999999999999999")
; => 1.0E20  ; Loses precision (Double)
```

**Solution**: Use BigDecimal for precise numeric values:

```clojure
(require '[cheshire.parse :as parse])

(binding [parse/*use-bigdecimals?* true]
  (json/parse-string "99999999999999999999.99999999999999999"))
; => 99999999999999999999.99999999999999999M
```

### Issue: Special characters in strings

```clojure
(json/generate-string {:text "Line 1\nLine 2\t\"quoted\""})
; => "{\"text\":\"Line 1\\nLine 2\\t\\\"quoted\\\"\"}"  ; Properly escaped
```

**This is correct behavior.** Special characters are automatically escaped. To see unescaped:

```clojure
;; Write to file (unescapes when written)
(spit "output.json" (json/generate-string {:text "hello\nworld"}))
```

### Issue: OutOfMemoryError with large files

```clojure
;; Bad: loads entire file into memory
(json/parse-string (slurp "huge.json"))
; => OutOfMemoryError
```

**Solution**: Use streaming:

```clojure
(with-open [r (io/reader "huge.json")]
  (json/parse-stream r true))

;; Or lazy parsing for arrays of objects
(with-open [r (io/reader "large-array.json")]
  (doall (take 10 (json/parsed-seq r true))))
```

### Issue: Custom type not encoding

```clojure
(json/generate-string {:point (my.app.Point. 10 20)})
; => JsonGenerationException: Can't encode class my.app.Point
```

**Solution**: Add custom encoder:

```clojure
(require '[cheshire.generate :as gen])

(gen/add-encoder 
  my.app.Point
  (fn [point gen]
    (.writeStartObject gen)
    (.writeFieldName gen "x")
    (.writeNumber gen (.x point))
    (.writeFieldName gen "y")
    (.writeNumber gen (.y point))
    (.writeEndObject gen)))

(json/generate-string {:point (my.app.Point. 10 20)})
; => "{\"point\":{\"x\":10,\"y\":20}}"
```

## Advanced Topics

### SMILE Format (Binary JSON)

SMILE is a binary format that's more compact and faster than JSON text:

```clojure
;; Encode to SMILE
(def smile-bytes (json/generate-smile {:name "Alice" :age 30}))
; => byte array

;; Decode from SMILE
(json/parse-smile smile-bytes true)
; => {:name "Alice", :age 30}
```

**Use SMILE when:**
- Network bandwidth matters
- Storage space is limited
- Performance is critical
- Communicating between systems that support SMILE

### Custom Array Coercion

Control what collection type is used for JSON arrays:

```clojure
;; Default: arrays become vectors
(json/parse-string "{\"data\":[1,2,3]}" true)
; => {:data [1 2 3]}

;; Custom: use sets for specific fields
(json/parse-string 
  "{\"items\":[1,2,2,3],\"order\":[1,2,3]}"
  true
  (fn [field-name]
    (if (= field-name "items")
      #{}   ; Use set for "items"
      []))) ; Use vector for others
; => {:items #{1 2 3}, :order [1 2 3]}
```

### Factory Options

Customize Jackson factory for advanced use cases:

```clojure
(require '[cheshire.factory :as factory])

;; Allow NaN and Infinity
(binding [factory/*json-factory* 
          (factory/make-json-factory 
            {:allow-non-numeric-numbers true})]
  (json/parse-string "{\"value\":NaN}" true))
; => {:value NaN}
```

See `cheshire.factory/default-factory-options` for all options.

### Streaming Multiple Objects

Use `with-writer` for streaming multiple objects efficiently:

```clojure
(with-open [w (io/writer "stream.json")]
  (json/with-writer [w {}]
    (dotimes [i 5]
      (json/write {:id i :data (str "item-" i)}))))
```

This writes multiple objects without recreating generators.

## Related Libraries

- **jsonista** - Faster alternative using Jackson, malli integration
- **data.json** - Minimal JSON library from Clojure contrib
- **transit-clj** - Rich data format for Clojure/ClojureScript communication
- **clojure.data.json** - Official Clojure JSON library

## Resources

- GitHub: https://github.com/dakrone/cheshire
- Changelog: https://github.com/dakrone/cheshire/blob/master/ChangeLog.md
- SMILE Format: http://wiki.fasterxml.com/SmileFormatSpec
- API Docs: https://cljdoc.org/d/cheshire/cheshire

## Summary

Cheshire is the go-to JSON library for Clojure:

1. **Fast encoding/decoding** - 2x faster than alternatives
2. **Rich type support** - Dates, UUIDs, sets, ratios, custom types
3. **Flexible key transformation** - String/keyword keys, custom functions
4. **Stream processing** - Handle large data efficiently
5. **Custom encoders** - Encode any type with custom logic
6. **Pretty printing** - Debugging-friendly output
7. **SMILE support** - Binary JSON for performance
8. **BigDecimal precision** - Financial/scientific accuracy

**Most common patterns:**
```clojure
;; Encode to JSON
(json/generate-string {:key "value"})

;; Decode from JSON (keyword keys)
(json/parse-string json-str true)

;; Stream large files
(with-open [r (io/reader "file.json")]
  (json/parse-stream r true))

;; Pretty print
(json/generate-string data {:pretty true})

;; Custom date format
(json/generate-string data {:date-format "yyyy-MM-dd"})
```

Perfect for REST APIs, microservices, data processing, and any application working with JSON.
