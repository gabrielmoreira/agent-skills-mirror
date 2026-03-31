---
name: clj-yaml
description: |
  YAML encoding and decoding for Clojure. Use when working with YAML configuration files,
  parsing YAML data, generating YAML output, or when you need human-readable config formats.
  Supports multi-document YAML, custom key transformation, position tracking, flow styles,
  and safety options. Ideal for config files, CI/CD definitions, Kubernetes manifests, and
  data exchange with YAML-based systems.
---

# clj-yaml - YAML for Clojure

## Quick Start

clj-yaml provides idiomatic YAML encoding/decoding via SnakeYAML.

```clojure
(require '[clj-yaml.core :as yaml])

;; Encode Clojure data to YAML string
(yaml/generate-string {:name "Alice" :age 30 :hobbies ["coding" "reading"]})
; => "name: Alice\nage: 30\nhobbies: [coding, reading]\n"

;; Decode YAML string to Clojure data (keyword keys by default)
(yaml/parse-string "name: Bob\nage: 25")
; => {:name "Bob", :age 25}

;; Explicit keyword conversion
(yaml/parse-string "name: Charlie\nage: 35" :keywords true)
; => {:name "Charlie", :age 35}

;; String keys
(yaml/parse-string "name: Dave\nage: 40" :keywords false)
; => {"name" "Dave", "age" 40}

;; Pretty block style (indented)
(yaml/generate-string 
  {:server {:host "localhost" :port 8080}}
  :dumper-options {:flow-style :block})
; => "server:\n  host: localhost\n  port: 8080\n"
```

**Key benefits:**
- Human-readable format (better than JSON for configs)
- Multi-document support
- Custom key transformation
- Position tracking (for error reporting)
- Flow style control (block vs. inline)
- Safety options (prevent code injection)

## Core Concepts

### Encoding vs. Decoding

**Encoding**: Clojure data → YAML string
- `generate-string` - Main encoding function
- `generate-stream` - Write YAML to stream

**Decoding**: YAML string → Clojure data
- `parse-string` - Parse YAML string
- `parse-stream` - Parse from stream

### Key Transformation

By default, clj-yaml converts YAML keys to keywords:
- **Encoding**: Clojure keywords → YAML strings (`:name` → `name:`)
- **Decoding**: YAML strings → Clojure keywords (`name:` → `:name`)

Control this behavior:
```clojure
;; Default: keyword keys
(yaml/parse-string "firstName: Alice")
; => {:firstName "Alice"}

;; String keys
(yaml/parse-string "firstName: Alice" :keywords false)
; => {"firstName" "Alice"}

;; Custom transformation
(yaml/parse-string 
  "firstName: Alice"
  :key-fn (fn [{:keys [key]}] (keyword (.toLowerCase key))))
; => {:firstname "Alice"}
```

### Flow Styles

YAML supports two formatting styles:

**Block style** (indented, human-readable):
```yaml
person:
  name: Alice
  age: 30
  hobbies:
    - reading
    - coding
```

**Flow style** (inline, compact):
```yaml
person: {name: Alice, age: 30, hobbies: [reading, coding]}
```

Control with `:dumper-options {:flow-style :block/:flow/:auto}`.

### Multi-Document YAML

YAML files can contain multiple documents separated by `---`:
```yaml
---
name: Alice
age: 30
---
name: Bob
age: 25
```

Use `:load-all true` to parse all documents.

## Common Workflows

### Workflow 1: Configuration Files

Load and generate application config files:

```clojure
(require '[clj-yaml.core :as yaml]
         '[clojure.java.io :as io])

;; Read config file
(defn load-config [path]
  (with-open [r (io/reader path)]
    (yaml/parse-stream r)))

(load-config "config.yaml")
; => {:database {:host "localhost", :port 5432}
;     :server {:port 8080, :workers 4}}

;; Write config file
(defn save-config [path config]
  (with-open [w (io/writer path)]
    (yaml/generate-stream w config 
                          :dumper-options {:flow-style :block})))

(save-config "output.yaml"
  {:database {:host "localhost" :port 5432}
   :server {:port 8080 :workers 4}})
```

**Result** (`output.yaml`):
```yaml
database:
  host: localhost
  port: 5432
server:
  port: 8080
  workers: 4
```

### Workflow 2: Multi-Document Processing

Parse YAML files with multiple documents (common in Kubernetes):

```clojure
(def k8s-yaml "---
apiVersion: v1
kind: Service
metadata:
  name: my-service
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config")

;; Parse all documents
(def resources (yaml/parse-string k8s-yaml :load-all true))
; => ({:apiVersion "v1", :kind "Service", :metadata {:name "my-service"}}
;     {:apiVersion "apps/v1", :kind "Deployment", :metadata {:name "my-deployment"}}
;     {:apiVersion "v1", :kind "ConfigMap", :metadata {:name "my-config"}})

;; Process each resource
(doseq [resource resources]
  (println (:kind resource) "-" (get-in resource [:metadata :name])))
; Service - my-service
; Deployment - my-deployment
; ConfigMap - my-config
```

### Workflow 3: Custom Key Transformation

Transform keys during parsing (e.g., camelCase ↔ kebab-case):

```clojure
;; camelCase → kebab-case
(defn camel->kebab [s]
  (clojure.string/replace s #"([A-Z])" "-$1"))

(yaml/parse-string 
  "firstName: Alice\nlastName: Smith\nemailAddress: alice@example.com"
  :key-fn (fn [{:keys [key]}]
            (keyword (clojure.string/lower-case (camel->kebab key)))))
; => {:first-name "Alice", :last-name "Smith", :email-address "alice@example.com"}

;; kebab-case → camelCase (for encoding)
;; Note: generate-string doesn't support :key-fn, transform data first
(defn kebab->camel [k]
  (let [parts (clojure.string/split (name k) #"-")]
    (keyword (apply str (first parts) 
                    (map clojure.string/capitalize (rest parts))))))

(let [data {:first-name "Alice" :last-name "Smith"}
      transformed (into {} (map (fn [[k v]] [(kebab->camel k) v]) data))]
  (yaml/generate-string transformed))
; => "firstName: Alice\nlastName: Smith\n"
```

### Workflow 4: Flow Style Control

Control YAML formatting for readability:

```clojure
(def config
  {:database {:host "localhost"
              :port 5432
              :credentials {:username "admin"
                            :password "secret"}}
   :cache {:servers ["redis-1" "redis-2" "redis-3"]}})

;; Auto (default) - mixed styles
(yaml/generate-string config)
; => "database: {host: localhost, port: 5432, credentials: {username: admin, password: secret}}\ncache: {servers: [redis-1, redis-2, redis-3]}\n"

;; Block style - fully expanded (most readable)
(yaml/generate-string config 
                      :dumper-options {:flow-style :block})
; => "database:\n  host: localhost\n  port: 5432\n  credentials:\n    username: admin\n    password: secret\ncache:\n  servers:\n  - redis-1\n  - redis-2\n  - redis-3\n"

;; Flow style - fully collapsed (most compact)
(yaml/generate-string config
                      :dumper-options {:flow-style :flow})
; => "{database: {host: localhost, port: 5432, credentials: {username: admin, password: secret}}, cache: {servers: [redis-1, redis-2, redis-3]}}\n"
```

**When to use each:**
- **Block** - Config files, documentation, human readability
- **Flow** - Logs, compact storage, single-line output
- **Auto** - Let SnakeYAML decide (uses flow for small structures)

### Workflow 5: Custom Indentation

Control indentation depth for nested structures:

```clojure
(def nested
  {:server {:http {:port 8080 :timeout 30}
            :grpc {:port 9090 :timeout 60}}})

;; Default: 2-space indent
(yaml/generate-string nested :dumper-options {:flow-style :block})
; => "server:\n  http: {port: 8080, timeout: 30}\n  grpc: {port: 9090, timeout: 60}\n"

;; Custom: 4-space indent
(yaml/generate-string nested 
                      :dumper-options {:flow-style :block :indent 4})
; => "server:\n    http: {port: 8080, timeout: 30}\n    grpc: {port: 9090, timeout: 60}\n"

;; With indicator indent (for lists)
(yaml/generate-string 
  {:items ["a" "b" "c"]}
  :dumper-options {:flow-style :block 
                   :indent 4 
                   :indicator-indent 2})
; => "items:\n    -   a\n    -   b\n    -   c\n"
```

### Workflow 6: Position Tracking (Error Reporting)

Track source positions for better error messages:

```clojure
;; Parse with position tracking
(def marked (yaml/parse-string 
              "name: Alice\nage: thirty\nlocation: NYC"
              :mark true))

;; Check if marked
(yaml/marked? marked)
; => true

;; Access position data
marked
; => {:start {:line 0, :index 0, :column 0},
;     :end {:line 2, :index 31, :column 13},
;     :unmark {:name "Alice", :age "thirty", :location "NYC"}}

;; Extract actual data
(yaml/unmark marked)
; => {:name "Alice", :age "thirty", :location "NYC"}

;; Position data helps report errors
(defn validate-age [marked-data]
  (let [data (yaml/unmark marked-data)]
    (when-not (integer? (:age data))
      (let [age-mark (get-in marked-data [:unmark :age :start])]
        (throw (ex-info 
                 (str "Invalid age at line " (:line age-mark) 
                      ", column " (:column age-mark))
                 {:line (:line age-mark)
                  :column (:column age-mark)
                  :value (:age data)}))))))
```

**Use position tracking when:**
- Building config validators
- Providing user-friendly error messages
- Creating YAML editors/linters
- Debugging complex YAML files

### Workflow 7: Safety Options

Protect against untrusted YAML input:

```clojure
;; Limit nesting depth (prevent stack overflow)
(def deep-yaml (apply str "a:\n" (repeat 100 "  b:\n")))

(try
  (yaml/parse-string deep-yaml :nesting-depth-limit 50)
  (catch Exception e
    (.getMessage e)))
; => "Nesting depth exceeded"

;; Prevent duplicate keys
(try
  (yaml/parse-string "name: Alice\nname: Bob" :allow-duplicate-keys false)
  (catch Exception e
    (.getMessage e)))
; => "found duplicate key name"

;; Limit document size (prevent DoS)
(yaml/parse-string large-yaml :code-point-limit 1000000)

;; Limit aliases (prevent billion laughs attack)
(yaml/parse-string yaml-with-aliases :max-aliases-for-collections 50)

;; NEVER use :unsafe true with untrusted input
;; :unsafe true allows arbitrary Java object instantiation
(yaml/parse-string trusted-yaml :unsafe false)  ; Always use false!
```

**Security best practices:**
- Always use `:unsafe false` (the default)
- Set `:nesting-depth-limit` for untrusted input
- Use `:allow-duplicate-keys false` for strict validation
- Set `:code-point-limit` to prevent large documents
- Validate data after parsing

## When to Use clj-yaml

**Use clj-yaml when:**
- Working with configuration files (app config, CI/CD, Kubernetes)
- Human readability matters more than parsing speed
- Multi-document YAML files needed
- YAML is the standard in your ecosystem (DevOps, k8s)
- Need comments in data files (YAML supports, JSON doesn't)

**Use Cheshire/JSON when:**
- Performance is critical (JSON is faster to parse)
- Interoperating with web APIs (most use JSON)
- Simpler data structures
- No need for human editing

**Use EDN when:**
- Communicating between Clojure systems
- Want to preserve Clojure semantics exactly
- Need rich data types (sets, symbols, tagged literals)

## Best Practices

**Do:**
- Use block style for config files (`:dumper-options {:flow-style :block}`)
- Set safety limits for untrusted input (`:nesting-depth-limit`, `:code-point-limit`)
- Use `:allow-duplicate-keys false` for strict validation
- Transform keys consistently (use `:key-fn` for custom logic)
- Use streams for large files (`parse-stream`/`generate-stream`)
- Validate data after parsing (YAML is permissive)
- Use `:load-all true` for multi-document files

```clojure
;; Good: readable config file
(yaml/generate-string config :dumper-options {:flow-style :block})

;; Good: safe parsing of untrusted input
(yaml/parse-string untrusted-yaml
                   :unsafe false
                   :nesting-depth-limit 50
                   :allow-duplicate-keys false)

;; Good: stream large files
(with-open [r (io/reader "large.yaml")]
  (yaml/parse-stream r))
```

**Don't:**
- Use `:unsafe true` with untrusted input (security risk!)
- Parse huge YAML into memory with `parse-string` (use `parse-stream`)
- Forget to use `:load-all true` for multi-document files
- Mix string and keyword keys in same codebase
- Ignore validation (YAML allows any structure)
- Use flow style for human-edited config files

```clojure
;; Bad: unsafe parsing
(yaml/parse-string untrusted-input :unsafe true)  ; DANGEROUS!

;; Bad: reading huge file into memory
(yaml/parse-string (slurp "huge.yaml"))  ; OOM risk

;; Bad: forgetting multi-document
(yaml/parse-string multi-doc-yaml)  ; Only gets first doc!

;; Good: load all documents
(yaml/parse-string multi-doc-yaml :load-all true)
```

## Common Issues

### Issue: Only first document parsed

```clojure
(def yaml "---\nname: Alice\n---\nname: Bob")
(yaml/parse-string yaml)
; => Error: expected a single document but found another
```

**Solution**: Use `:load-all true`:

```clojure
(yaml/parse-string yaml :load-all true)
; => ({:name "Alice"} {:name "Bob"})
```

### Issue: Keywords not legal Clojure keywords

```clojure
(yaml/parse-string "123: value\nfirst-name: Alice")
; => {:123 "value", :first-name "Alice"}  ; :123 is invalid keyword!
```

**Solution**: Use `:keywords false` or custom `:key-fn`:

```clojure
;; String keys
(yaml/parse-string "123: value" :keywords false)
; => {"123" "value"}

;; Custom validation
(yaml/parse-string yaml
  :key-fn (fn [{:keys [key]}]
            (if (re-matches #"^\d+$" key)
              key  ; Keep numeric keys as strings
              (keyword key))))
```

### Issue: Duplicate keys silently overwrite

```clojure
(yaml/parse-string "name: Alice\nage: 30\nname: Bob")
; => {:name "Bob", :age 30}  ; Alice lost!
```

**Solution**: Use `:allow-duplicate-keys false` for strict validation:

```clojure
(yaml/parse-string "name: Alice\nname: Bob" :allow-duplicate-keys false)
; => Exception: found duplicate key name
```

### Issue: Deep nesting causes stack overflow

```clojure
(def deep (apply str (repeat 1000 "a:\n  ")))
(yaml/parse-string deep)
; => StackOverflowError (maybe)
```

**Solution**: Set `:nesting-depth-limit`:

```clojure
(yaml/parse-string deep :nesting-depth-limit 50)
; => Throws if limit exceeded
```

### Issue: Flow style not applied consistently

```clojure
(yaml/generate-string {:a 1 :b {:c 2}} :dumper-options {:flow-style :block})
; => "a: 1\nb: {c: 2}\n"  ; Why is b: {c: 2} inline?
```

**Explanation**: SnakeYAML uses heuristics for "auto" style on nested structures. For fully block style, nested maps need multiple keys or explicit configuration.

**Workaround**: Accept mixed styles (this is normal) or generate YAML differently.

### Issue: OutOfMemoryError with large files

```clojure
(yaml/parse-string (slurp "huge.yaml"))
; => OutOfMemoryError
```

**Solution**: Use streams:

```clojure
(with-open [r (io/reader "huge.yaml")]
  (yaml/parse-stream r))
```

### Issue: Custom types don't serialize

```clojure
(yaml/generate-string {:point (my.app.Point. 10 20)})
; => Error: Can't represent class my.app.Point
```

**Solution**: Convert custom types to standard types before encoding:

```clojure
(defprotocol YAMLSerializable
  (to-yaml [this]))

(extend-type my.app.Point
  YAMLSerializable
  (to-yaml [p] {:x (.x p) :y (.y p)}))

(yaml/generate-string {:point (to-yaml (my.app.Point. 10 20))})
; => "point: {x: 10, y: 20}\n"
```

## Advanced Topics

### Unknown Tag Handling

Handle custom YAML tags:

```clojure
;; Default: throws on unknown tags
(yaml/parse-string "!custom-tag value")
; => Exception: could not determine a constructor for the tag !custom-tag

;; Custom handler
(yaml/parse-string 
  "data: !include config/database.yaml"
  :unknown-tag-fn (fn [{:keys [tag value]}]
                    (case tag
                      "!include" (yaml/parse-string (slurp value))
                      {:tag tag :value value})))
; => {:data {:host "localhost", :port 5432}}  ; Loaded from file
```

### Complex Indentation Control

Fine-tune indentation for specific needs:

```clojure
(yaml/generate-string
  {:steps ["checkout" "build" "test" "deploy"]}
  :dumper-options {:flow-style :block
                   :indent 2               ; Base indent
                   :indicator-indent 0     ; Space before '-'
                   :indent-with-indicator false})
; => "steps:\n- checkout\n- build\n- test\n- deploy\n"

;; With indicator indent
(yaml/generate-string
  {:steps ["checkout" "build" "test" "deploy"]}
  :dumper-options {:flow-style :block
                   :indent 4
                   :indicator-indent 2
                   :indent-with-indicator true})
; => "steps:\n    -   checkout\n    -   build\n    -   test\n    -   deploy\n"
```

### Combining YAML with Schema Validation

Validate YAML structure after parsing:

```clojure
(require '[malli.core :as m])

(def config-schema
  [:map
   [:database [:map
               [:host string?]
               [:port [:int {:min 1 :max 65535}]]]]
   [:server [:map
             [:port [:int {:min 1 :max 65535}]]
             [:workers pos-int?]]]])

(defn load-validated-config [path]
  (let [config (yaml/parse-string (slurp path))]
    (if (m/validate config-schema config)
      config
      (throw (ex-info "Invalid config" 
                      {:errors (m/explain config-schema config)})))))
```

## Related Libraries

- **Cheshire** - Fast JSON library (similar API)
- **clojure.data.json** - Official Clojure JSON library
- **aero** - Configuration library with environment-based loading
- **cprop** - Environment-based config management
- **environ** - Environment variable configuration

## Resources

- GitHub: https://github.com/clj-commons/clj-yaml
- User Guide: https://github.com/clj-commons/clj-yaml/blob/master/doc/01-user-guide.adoc
- API Docs: https://cljdoc.org/d/clj-commons/clj-yaml
- YAML Spec: https://yaml.org/spec/1.2/spec.html
- SnakeYAML: https://bitbucket.org/snakeyaml/snakeyaml

## Summary

clj-yaml is the standard YAML library for Clojure:

1. **Human-readable format** - Better than JSON for configs
2. **Multi-document support** - Parse multiple YAML docs in one file
3. **Custom key transformation** - `:key-fn` for camelCase/kebab-case
4. **Flow style control** - Block (readable) or flow (compact) formatting
5. **Position tracking** - Error reporting with line/column numbers
6. **Safety options** - Protect against malicious YAML
7. **Stream processing** - Handle large files efficiently

**Most common patterns:**

```clojure
;; Parse config file (keyword keys)
(with-open [r (io/reader "config.yaml")]
  (yaml/parse-stream r))

;; Generate readable YAML
(yaml/generate-string data :dumper-options {:flow-style :block})

;; Parse multi-document YAML
(yaml/parse-string yaml-str :load-all true)

;; Safe parsing of untrusted input
(yaml/parse-string untrusted
                   :unsafe false
                   :nesting-depth-limit 50
                   :allow-duplicate-keys false)

;; Custom key transformation
(yaml/parse-string yaml
                   :key-fn (fn [{:keys [key]}] 
                             (keyword (normalize-key key))))
```

Perfect for configuration files, CI/CD pipelines, Kubernetes manifests, and any system where human readability and editability matter.
