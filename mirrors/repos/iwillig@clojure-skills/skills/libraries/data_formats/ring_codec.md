---
name: ring-codec-encoding
description: |
  Encode and decode data for web applications using ring-codec. Provides URL encoding,
  form encoding, percent encoding, and Base64 encoding/decoding. Use when working with
  HTTP requests/responses, query parameters, form data, URLs, or when the user mentions
  encoding, decoding, URL escaping, form parameters, Base64, percent encoding, or
  www-form-urlencoded data.
---

# Ring Codec

Ring-codec is a utility library for encoding and decoding data into formats commonly used in web applications. Part of the Ring ecosystem but usable standalone.

## Quick Start

```clojure
;; Add dependency
{:deps {ring/ring-codec {:mvn/version "1.3.0"}}}

;; Require the namespace
(require '[ring.util.codec :as codec])

;; URL encoding (preserves certain characters)
(codec/url-encode "hello world")
;; => "hello%20world"

(codec/url-decode "hello%20world")
;; => "hello world"

;; Form encoding (spaces become +)
(codec/form-encode {:name "John Doe" :age 30})
;; => "name=John+Doe&age=30"

(codec/form-decode "name=John+Doe&age=30")
;; => {"name" "John Doe", "age" "30"}

;; Base64 encoding
(codec/base64-encode (.getBytes "hello" "UTF-8"))
;; => "aGVsbG8="

(String. (codec/base64-decode "aGVsbG8=") "UTF-8")
;; => "hello"
```

**Key benefits:**
- Simple, focused API for common web encoding tasks
- Handles URL encoding, form encoding, and Base64
- Supports custom character encodings
- Properly handles edge cases (nil values, special characters)
- Part of the Ring ecosystem but works standalone

## Core Concepts

### URL Encoding vs Form Encoding

Ring-codec provides two related but different encoding schemes:

**URL Encoding:**
- Encodes spaces as `%20`
- Preserves: `A-Za-z0-9_~.+-`
- Used for encoding parts of URLs (paths, query parameters)
- Use `url-encode` and `url-decode`

**Form Encoding:**
- Encodes spaces as `+`
- Used for `application/x-www-form-urlencoded` data
- Common in HTML form submissions and query strings
- Use `form-encode` and `form-decode`

```clojure
;; URL encoding - spaces become %20
(codec/url-encode "foo bar")
;; => "foo%20bar"

;; Form encoding - spaces become +
(codec/form-encode "foo bar")
;; => "foo+bar"

;; Difference is important for correct HTTP handling
```

### Percent Encoding

Percent encoding (also called URL encoding) converts bytes to `%XX` format where XX is hexadecimal:

```clojure
;; Encode every character as percent-encoded
(codec/percent-encode "hello")
;; => "%68%65%6C%6C%6F"

;; Decode percent-encoded strings
(codec/percent-decode "%68%65%6C%6C%6F")
;; => "hello"

;; Handles consecutive encoded characters
(codec/percent-decode "foo%20bar%21")
;; => "foo bar!"
```

**When to use:**
- `percent-encode`/`percent-decode` - Low-level, encodes everything
- `url-encode`/`url-decode` - High-level, preserves safe characters
- `form-encode`/`form-decode` - Application/x-www-form-urlencoded format

### Character Encoding Support

All encoding functions support custom character encodings:

```clojure
;; Default is UTF-8
(codec/url-encode "café")
;; => "caf%C3%A9"

;; Specify encoding explicitly
(codec/url-encode "café" "UTF-8")
;; => "caf%C3%A9"

;; Use different encoding
(codec/url-encode "café" "ISO-8859-1")
;; => "caf%E9"

;; Or pass Charset object
(require '[java.nio.charset Charset])
(codec/url-encode "test" (Charset/forName "UTF-16"))

;; Decoding must use same encoding
(codec/url-decode "caf%C3%A9" "UTF-8")
;; => "café"
```

### Base64 Encoding

Base64 encodes binary data as ASCII text:

```clojure
;; Encode byte array to Base64 string
(def bytes (.getBytes "Hello, World!" "UTF-8"))
(codec/base64-encode bytes)
;; => "SGVsbG8sIFdvcmxkIQ=="

;; Decode Base64 string to byte array
(def encoded "SGVsbG8sIFdvcmxkIQ==")
(String. (codec/base64-decode encoded) "UTF-8")
;; => "Hello, World!"

;; Round-trip
(-> "secret data"
    (.getBytes "UTF-8")
    codec/base64-encode
    codec/base64-decode
    (String. "UTF-8"))
;; => "secret data"
```

## Common Workflows

### Workflow 1: Encoding Query Parameters

Build query strings for HTTP requests:

```clojure
(require '[ring.util.codec :as codec])

;; Single parameter
(codec/form-encode {:q "clojure web"})
;; => "q=clojure+web"

;; Multiple parameters
(codec/form-encode {:q "clojure" :lang "en" :page 2})
;; => "q=clojure&lang=en&page=2"

;; Parameters with special characters
(codec/form-encode {:email "user@example.com"
                    :url "https://example.com/path?foo=bar"})
;; => "email=user%40example.com&url=https%3A%2F%2Fexample.com%2Fpath%3Ffoo%3Dbar"

;; Multiple values for same key
(codec/form-encode {:tags ["clojure" "web" "ring"]})
;; => "tags=clojure&tags=web&tags=ring"

;; Sets are sorted for consistent output
(codec/form-encode {:tags #{"web" "clojure" "ring"}})
;; => "tags=clojure&tags=ring&tags=web"

;; Build complete URL
(str "https://api.example.com/search?"
     (codec/form-encode {:q "clojure" :limit 10}))
;; => "https://api.example.com/search?q=clojure&limit=10"
```

### Workflow 2: Decoding Form Data

Parse incoming form data or query strings:

```clojure
;; Parse query string
(codec/form-decode "name=John+Doe&age=30")
;; => {"name" "John Doe", "age" "30"}

;; Handle multiple values
(codec/form-decode "tags=clojure&tags=web&tags=ring")
;; => {"tags" ["clojure" "web" "ring"]}

;; Decode just a string (no = sign)
(codec/form-decode "hello+world")
;; => "hello world"

;; Empty values
(codec/form-decode "name=&age=30")
;; => {"name" "", "age" "30"}

;; Keys without values
(codec/form-decode "name&age=30")
;; => {"name" "", "age" "30"}

;; Special characters
(codec/form-decode "email=user%40example.com")
;; => {"email" "user@example.com"}

;; Invalid percent encoding is handled gracefully
(codec/form-decode "invalid=%D")
;; => {} (returns empty map for invalid encoding)
```

### Workflow 3: Encoding URL Path Components

Encode individual URL path segments:

```clojure
;; Encode path segment
(def filename "My Document (Draft).pdf")
(codec/url-encode filename)
;; => "My%20Document%20%28Draft%29.pdf"

;; Build URL with encoded path
(str "https://example.com/files/" (codec/url-encode filename))
;; => "https://example.com/files/My%20Document%20%28Draft%29.pdf"

;; Encode path with slashes
(def path "2024/11/report.pdf")
(codec/url-encode path)
;; => "2024%2F11%2Freport.pdf"

;; Note: + is preserved in url-encode
(codec/url-encode "foo+bar")
;; => "foo+bar"

;; But not in form-encode
(codec/form-encode "foo+bar")
;; => "foo%2Bbar"
```

### Workflow 4: Working with Base64 for API Tokens

Encode/decode API tokens and credentials:

```clojure
;; Encode credentials for Basic Auth
(defn basic-auth-header [username password]
  (let [credentials (str username ":" password)
        encoded (codec/base64-encode (.getBytes credentials "UTF-8"))]
    (str "Basic " encoded)))

(basic-auth-header "user" "pass123")
;; => "Basic dXNlcjpwYXNzMTIz"

;; Decode Basic Auth header
(defn decode-basic-auth [header]
  (when-let [[_ encoded] (re-matches #"Basic (.+)" header)]
    (-> (codec/base64-decode encoded)
        (String. "UTF-8")
        (clojure.string/split #":" 2))))

(decode-basic-auth "Basic dXNlcjpwYXNzMTIz")
;; => ["user" "pass123"]

;; Encode binary data for embedding
(defn encode-image-data [image-bytes]
  (str "data:image/png;base64," (codec/base64-encode image-bytes)))
```

### Workflow 5: Building Form-Encoded POST Bodies

Create request bodies for form submissions:

```clojure
(require '[ring.util.codec :as codec])

;; Create form data for POST request
(def form-data
  {:username "alice"
   :password "secret123"
   :remember-me "true"})

(def body (codec/form-encode form-data))
;; => "username=alice&password=secret123&remember-me=true"

;; Use with HTTP client
(require '[clj-http.client :as http])

(http/post "https://example.com/login"
  {:headers {"Content-Type" "application/x-www-form-urlencoded"}
   :body body})

;; Or let clj-http handle encoding
(http/post "https://example.com/login"
  {:form-params {:username "alice"
                 :password "secret123"}})
;; clj-http uses ring-codec internally for form-params
```

### Workflow 6: Custom Encoding for International Text

Handle non-ASCII characters properly:

```clojure
;; Default UTF-8 handles international text
(codec/form-encode {:message "Hello 世界"})
;; => "message=Hello+%E4%B8%96%E7%95%8C"

(codec/form-decode "message=Hello+%E4%B8%96%E7%95%8C")
;; => {"message" "Hello 世界"}

;; Specify encoding explicitly
(codec/form-encode {:text "Café"} "UTF-8")
;; => "text=Caf%C3%A9"

(codec/form-encode {:text "Café"} "ISO-8859-1")
;; => "text=Caf%E9"

;; Must decode with same encoding
(codec/form-decode "text=Caf%C3%A9" "UTF-8")
;; => {"text" "Café"}

(codec/form-decode "text=Caf%E9" "ISO-8859-1")
;; => {"text" "Café"}
```

### Workflow 7: Using assoc-conj Helper

Handle multiple values for the same key:

```clojure
;; assoc-conj is a helper function used internally
;; but also useful for building parameter maps

(require '[ring.util.codec :as codec])

;; First value creates single entry
(codec/assoc-conj {} "key" "value1")
;; => {"key" "value1"}

;; Second value creates vector
(-> {}
    (codec/assoc-conj "key" "value1")
    (codec/assoc-conj "key" "value2"))
;; => {"key" ["value1" "value2"]}

;; Additional values append to vector
(-> {}
    (codec/assoc-conj "key" "value1")
    (codec/assoc-conj "key" "value2")
    (codec/assoc-conj "key" "value3"))
;; => {"key" ["value1" "value2" "value3"]}

;; Useful when parsing query strings manually
(reduce (fn [m [k v]]
          (codec/assoc-conj m k v))
        {}
        [["tag" "clojure"] ["tag" "web"] ["tag" "ring"]])
;; => {"tag" ["clojure" "web" "ring"]}
```

## When to Use Each Function

**Use `url-encode`/`url-decode` when:**
- Encoding URL path components
- Building URLs manually
- Need to preserve `+` as literal plus sign
- Working with URL fragments or paths

**Use `form-encode`/`form-decode` when:**
- Building query strings
- Encoding form data for POST requests
- Parsing `application/x-www-form-urlencoded` data
- Working with HTML form submissions
- Spaces should encode to `+`

**Use `percent-encode`/`percent-decode` when:**
- Need complete control over encoding
- Every character must be percent-encoded
- Working with custom encoding schemes
- Low-level URL manipulation

**Use `base64-encode`/`base64-decode` when:**
- Encoding binary data as text
- Working with Basic Authentication
- Embedding images/files in data URIs
- Encoding tokens or credentials
- Need safe ASCII representation of binary data

## Best Practices

**DO:**
- Use UTF-8 encoding unless you have specific requirements
- Use `form-encode` for query strings and form data
- Use `url-encode` for URL path components
- Handle nil values in maps (they encode as empty strings)
- Remember that `form-decode` returns string values (convert types as needed)
- Use `assoc-conj` when building parameter maps with duplicate keys
- Test encoding/decoding with international characters

**DON'T:**
- Mix up `url-encode` and `form-encode` (different space handling)
- Forget to decode with the same encoding used to encode
- Double-encode data (encode once, not multiple times)
- Assume decoded form values are anything but strings
- Use `percent-encode` when `url-encode` or `form-encode` would work
- Forget that Base64 works with byte arrays, not strings directly

## Common Issues

### Issue: Spaces Encoded Differently

**Problem:** Spaces are encoded as `%20` instead of `+` or vice versa.

```clojure
(codec/url-encode "foo bar")
;; => "foo%20bar"

(codec/form-encode "foo bar")
;; => "foo+bar"
```

**Solution:** Use the right function for your use case.

```clojure
;; For query strings and form data, use form-encode
(str "https://api.example.com/search?"
     (codec/form-encode {:q "hello world"}))
;; => "https://api.example.com/search?q=hello+world"

;; For URL paths, use url-encode
(str "https://api.example.com/files/"
     (codec/url-encode "my file.pdf"))
;; => "https://api.example.com/files/my%20file.pdf"
```

### Issue: Plus Signs Not Handled Correctly

**Problem:** Plus signs in data are lost or incorrectly encoded.

```clojure
;; Plus sign is preserved by url-encode
(codec/url-encode "C++")
;; => "C++"

;; But form-encode encodes it
(codec/form-encode "C++")
;; => "C%2B%2B"
```

**Solution:** Use `form-encode` when `+` should represent plus sign, not space.

```clojure
;; When encoding search query with plus
(codec/form-encode {:q "C++"})
;; => "q=C%2B%2B"

;; Decoding handles it correctly
(codec/form-decode "q=C%2B%2B")
;; => {"q" "C++"}
```

### Issue: Decoding Returns Strings, Not Types

**Problem:** All decoded values are strings, including numbers and booleans.

```clojure
(codec/form-decode "age=30&active=true")
;; => {"age" "30", "active" "true"}  ; strings, not number/boolean
```

**Solution:** Parse types after decoding.

```clojure
(defn parse-form-params [encoded]
  (let [params (codec/form-decode encoded)]
    (-> params
        (update "age" parse-long)
        (update "active" #(= "true" %)))))

(parse-form-params "age=30&active=true")
;; => {"age" 30, "active" true}

;; Or use a library like schema/malli for validation and coercion
```

### Issue: Invalid Percent Encoding

**Problem:** Malformed percent-encoded strings cause issues.

```clojure
;; Invalid encoding - incomplete escape sequence
(codec/form-decode "name=%D")
;; => {} (returns empty map)

(codec/form-decode-str "%D")
;; => nil (returns nil for invalid)
```

**Solution:** Handle invalid input gracefully.

```clojure
(defn safe-form-decode [s]
  (or (codec/form-decode s) {}))

(safe-form-decode "name=%D")
;; => {}

;; Or validate before decoding
(defn valid-percent-encoding? [s]
  (re-matches #"(?:[^%]|%[0-9A-Fa-f]{2})*" s))

(valid-percent-encoding? "foo%20bar")
;; => true

(valid-percent-encoding? "foo%2")
;; => false
```

### Issue: Encoding/Decoding Mismatch

**Problem:** Decoding with wrong encoding produces garbage.

```clojure
;; Encode with UTF-16
(def encoded (codec/form-encode {:text "café"} "UTF-16"))
;; => "text=caf%FE%FF%00%E9"

;; Decode with UTF-8 (wrong!)
(codec/form-decode encoded "UTF-8")
;; => {"text" "caf..."} (garbage)

;; Decode with UTF-16 (correct)
(codec/form-decode encoded "UTF-16")
;; => {"text" "café"}
```

**Solution:** Use consistent encoding throughout.

```clojure
;; Stick with UTF-8 unless you have specific requirements
(def params {:message "Hello 世界"})

(def encoded (codec/form-encode params "UTF-8"))
(codec/form-decode encoded "UTF-8")
;; => {"message" "Hello 世界"}

;; Or use default (UTF-8)
(-> params codec/form-encode codec/form-decode)
;; => {"message" "Hello 世界"}
```

### Issue: Base64 Padding Issues

**Problem:** Base64 strings must have proper padding.

```clojure
;; Valid Base64 (proper padding)
(codec/base64-decode "aGVsbG8=")
;; => works

;; Invalid Base64 (missing padding) - throws exception
(codec/base64-decode "aGVsbG8")
;; => IllegalArgumentException
```

**Solution:** Always use `base64-encode` to generate valid Base64.

```clojure
;; Encode properly
(def encoded (codec/base64-encode (.getBytes "hello" "UTF-8")))
;; => "aGVsbG8="

;; Decode works
(String. (codec/base64-decode encoded) "UTF-8")
;; => "hello"
```

## Integration Patterns

### With Ring Handlers

```clojure
(require '[ring.util.codec :as codec])

(defn query-params-middleware [handler]
  (fn [request]
    (let [query-string (:query-string request)
          params (when query-string
                   (codec/form-decode query-string))]
      (handler (assoc request :query-params params)))))

(defn form-params-middleware [handler]
  (fn [request]
    (if (and (= :post (:request-method request))
             (= "application/x-www-form-urlencoded"
                (get-in request [:headers "content-type"])))
      (let [body (slurp (:body request))
            params (codec/form-decode body)]
        (handler (assoc request :form-params params)))
      (handler request))))
```

### With HTTP Clients

```clojure
(require '[ring.util.codec :as codec]
         '[clj-http.client :as http])

;; Build GET request with query params
(defn api-search [query]
  (let [url (str "https://api.example.com/search?"
                (codec/form-encode {:q query :limit 10}))]
    (http/get url)))

;; POST with form data
(defn submit-form [data]
  (http/post "https://example.com/submit"
    {:headers {"Content-Type" "application/x-www-form-urlencoded"}
     :body (codec/form-encode data)}))
```

## Advanced Topics

### Custom Encoding Implementation

For special cases, you can implement custom encoding:

```clojure
(defn custom-encode [s]
  ;; Example: encode spaces as underscores
  (-> s
      (codec/url-encode)
      (clojure.string/replace "%20" "_")))

(custom-encode "hello world")
;; => "hello_world"
```

### Working with FormEncodeable Protocol

The library uses protocols internally for extensibility:

```clojure
;; The FormEncodeable protocol handles different types
;; String, Map, Object, and nil are already implemented

;; You can extend it for custom types if needed
(require '[ring.util.codec :as codec])

(defrecord User [name email])

;; Extend protocol for custom type
(extend-protocol codec/FormEncodeable
  User
  (form-encode* [user encoding]
    (codec/form-encode* {:name (:name user)
                         :email (:email user)}
                        encoding)))

(codec/form-encode (->User "Alice" "alice@example.com"))
;; => "name=Alice&email=alice%40example.com"
```

## Resources

- [GitHub Repository](https://github.com/ring-clojure/ring-codec)
- [API Documentation](http://ring-clojure.github.io/ring-codec/ring.util.codec.html)
- [Ring Documentation](https://github.com/ring-clojure/ring)
- [RFC 3986 (URI Syntax)](https://www.rfc-editor.org/rfc/rfc3986)
- [Form URL Encoding Spec](https://url.spec.whatwg.org/#urlencoded-parsing)

## Summary

Ring-codec provides essential encoding/decoding functions for web applications:

1. **URL encoding** - `url-encode`/`url-decode` for URL paths (spaces as `%20`)
2. **Form encoding** - `form-encode`/`form-decode` for query strings and forms (spaces as `+`)
3. **Percent encoding** - `percent-encode`/`percent-decode` for low-level encoding
4. **Base64** - `base64-encode`/`base64-decode` for binary data
5. **Character encoding support** - UTF-8 default, customizable
6. **Multiple values** - `assoc-conj` helper for duplicate keys

**Key distinctions:**
- `url-encode` preserves `+`, encodes spaces as `%20`
- `form-encode` encodes `+`, encodes spaces as `+`
- Both handle maps, strings, and nil values
- All decoded values are strings (parse as needed)
- Use UTF-8 unless you have specific requirements

Essential for Ring applications, HTTP clients, and any web-related data encoding.
