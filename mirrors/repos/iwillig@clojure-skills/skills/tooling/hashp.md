---
name: hashp-debugging
description: |
  Debug Clojure code with hashp's #p reader macro for better print debugging.
  Use when debugging, troubleshooting code, inspecting values, tracing execution,
  or when the user mentions debugging, print statements, prn, tracing values,
  or needs to inspect intermediate results during development.
---

# hashp

A lightweight debugging library that provides a better alternative to `prn` for Clojure development. Hashp uses data readers to print expressions with context including the original form, namespace, function name, and line number.

## Quick Start

```clojure
;; Add dependency
{:deps {dev.weavejester/hashp {:mvn/version "0.5.1"}}}

;; Install hashp (required before any other file is loaded)
((requiring-resolve 'hashp.install/install!))

;; Use #p to debug any expression
(defn calculate [x y]
  (+ #p (* x 2) #p (/ y 3)))

(calculate 10 9)
;; Output to STDERR:
;; #p[user/calculate:2] (* x 2) => 20
;; #p[user/calculate:2] (/ y 3) => 3
;; => 23
```

**Key benefits:**
- Faster to type than `(prn ...)`
- Returns the original value unchanged
- Prints context: namespace, function, line number
- Shows original form and result
- Non-invasive - can be added/removed quickly
- Output goes to STDERR by default (doesn't mix with program output)

## Core Concepts

### The #p Reader Macro

The `#p` reader macro is the heart of hashp. It intercepts any Clojure form, prints debugging information, and returns the original value unchanged:

```clojure
;; Basic usage
#p (+ 1 2)
;; #p[user:1] (+ 1 2) => 3
;; => 3

;; The value is unchanged, so it works inline
(* 10 #p (+ 1 2))
;; #p[user:1] (+ 1 2) => 3
;; => 30
```

**What gets printed:**
- `#p` - The tag (configurable)
- `[user/my-fn:42]` - Namespace, function name, and line number
- `(+ 1 2)` - The original form
- `=> 3` - The result

### Context-Rich Output

Unlike `prn`, hashp shows WHERE the debug statement is and WHAT was evaluated:

```clojure
;; With prn (traditional)
(defn process [data]
  (prn (map inc data))
  (prn (filter even? data))
  ...)
;; Output: (2 3 4)
;;         (2 4)
;; Which is which?

;; With hashp
(defn process [data]
  #p (map inc data)
  #p (filter even? data)
  ...)
;; #p[user/process:2] (map inc data) => (2 3 4)
;; #p[user/process:3] (filter even? data) => (2 4)
;; Crystal clear!
```

### Non-Intrusive Return Values

`#p` returns the original value, so you can add it anywhere without changing program behavior:

```clojure
;; Wrap any expression
(reduce + #p (filter odd? [1 2 3 4 5]))
;; #p[user:1] (filter odd? [1 2 3 4 5]) => (1 3 5)
;; => 9

;; In threading macros
(-> data
    (assoc :x 10)
    #p
    (update :y inc)
    #p)
;; Shows value at each pipeline stage
```

## Common Workflows

### Workflow 1: Quick Debugging with #p

Add `#p` in front of any form to see its value during execution:

```clojure
(defn calculate-mean [numbers]
  (/ (double #p (reduce + numbers)) 
     #p (count numbers)))

(calculate-mean [1 4 5 2])
;; #p[user/calculate-mean:2] (reduce + numbers) => 12
;; #p[user/calculate-mean:3] (count numbers) => 4
;; => 3.0
```

**Use cases:**
- Check intermediate values in calculations
- Verify function arguments
- Trace execution flow
- Understand why results are unexpected

### Workflow 2: Debugging Threading Macros

Insert `#p` at any point in threading pipelines to see intermediate results:

```clojure
(-> {:name "Alice" :age 30}
    #p
    (assoc :role :admin)
    #p
    (update :age inc)
    #p
    (dissoc :name))

;; #p[user:1] {:name "Alice", :age 30} => {:name "Alice", :age 30}
;; #p[user:3] (assoc :role :admin) => {:name "Alice", :age 30, :role :admin}
;; #p[user:5] (update :age inc) => {:name "Alice", :age 31, :role :admin}
;; => {:age 31, :role :admin}
```

**Pattern for thread-last (->>):**

```clojure
(->> [1 2 3 4 5]
     (map inc)
     #p
     (filter even?)
     #p
     (reduce +))

;; #p[user:3] (map inc) => (2 3 4 5 6)
;; #p[user:5] (filter even?) => (2 4 6)
;; => 12
```

### Workflow 3: Debugging Function Composition

See values flowing through composed functions:

```clojure
(def process-data
  (comp
    #p
    (partial map inc)
    #p
    (partial filter odd?)))

(process-data [1 2 3 4 5])
;; #p[user:7] (partial filter odd?) => (1 3 5)
;; #p[user:5] (partial map inc) => (2 4 6)
;; => (2 4 6)
```

### Workflow 4: Debugging let Bindings

Check values in let bindings:

```clojure
(defn complex-calculation [x y]
  (let [a #p (* x 2)
        b #p (+ y 3)
        c #p (- a b)]
    (/ c 2)))

(complex-calculation 10 4)
;; #p[user/complex-calculation:2] (* x 2) => 20
;; #p[user/complex-calculation:3] (+ y 3) => 7
;; #p[user/complex-calculation:4] (- a b) => 13
;; => 13/2
```

### Workflow 5: Global Installation for Development

Install hashp globally for all your projects:

**For tools.deps (deps.edn):**

Create or edit `~/.clojure/deps.edn`:

```clojure
{:aliases
 {:dev
  {:extra-deps {dev.weavejester/hashp {:mvn/version "0.5.1"}}
   :exec-fn hashp.install/install!}}}
```

Start your REPL with:
```bash
clj -M:dev -e "((requiring-resolve 'hashp.install/install!))"
```

**For Leiningen:**

Edit `~/.lein/profiles.clj`:

```clojure
{:user
 {:dependencies [[dev.weavejester/hashp "0.5.1"]]
  :injections [((requiring-resolve 'hashp.install/install!))]}}
```

**For Babashka:**

Edit `~/.boot/profile.boot`:

```clojure
(set-env! :dependencies #(conj % '[dev.weavejester/hashp "0.5.1"]))
((requiring-resolve 'hashp.install/install!))
(boot.core/load-data-readers!)
```

### Workflow 6: Customizing Output

Configure hashp behavior with options:

```clojure
(require '[hashp.install :as hashp])

;; Disable colors
(hashp/install! :color? false)

;; Change the tag
(hashp/install! :tag 'debug)
;; Now use #debug instead of #p

;; Write to STDOUT instead of STDERR
(hashp/install! :writer *out*)

;; Custom template
(hashp/install! :template "{ns}.{fn}:{line} | {form} = {value}")

;; Disable in production
(hashp/install! :disabled? (= (System/getenv "ENV") "production"))
```

**Template variables:**
- `{tag}` - The tag symbol (default: p)
- `{ns}` - Namespace
- `{fn}` - Function name
- `{line}` - Line number
- `{form}` - Original form
- `{value}` - Evaluated result

### Workflow 7: Conditional Debugging

Use environment variables to enable/disable hashp:

```clojure
;; In your project initialization
(require '[hashp.install :as hashp])

(hashp/install!
  :disabled? (not (System/getenv "DEBUG")))

;; Enable: DEBUG=1 clj
;; Disable: clj
```

**Pattern for development vs production:**

```clojure
(defn setup-debugging []
  (require '[hashp.install :as hashp])
  (hashp/install!
    :disabled? (not (or (System/getenv "DEBUG")
                        (= (System/getenv "ENV") "development")))))
```

## When to Use Each Approach

**Use #p when:**
- Debugging during REPL-driven development
- Need to see intermediate values quickly
- Checking values in threading macros
- Tracing function arguments and returns
- Understanding unexpected behavior

**Use prn/println when:**
- Need formatted output for users
- Writing to logs with specific formatting
- Output needs to go to STDOUT
- Building debug strings with interpolation

**Use logging libraries when:**
- Production logging requirements
- Need log levels (info, warn, error)
- Structured logging to files or systems
- Performance-critical logging with filtering

**Use debuggers when:**
- Need to pause execution
- Inspecting large data structures interactively
- Stepping through code line by line
- Complex debugging scenarios

## Best Practices

**DO:**
- Install hashp at application startup before loading other code
- Use `#p` liberally during development - easy to add and remove
- Keep `#p` in REPL sessions for quick debugging
- Use descriptive variable names even with `#p` - context helps
- Remove `#p` statements before committing (or use conditional enabling)
- Configure `:disabled? true` for production environments
- Use `#p` inline in expressions for minimal code changes

**DON'T:**
- Commit `#p` statements to production code (unless conditionally disabled)
- Rely on `#p` for permanent logging (use proper logging instead)
- Use `#p` with side-effecting forms without understanding evaluation order
- Forget to install hashp before other namespaces are loaded
- Use `#p` for user-facing output (it goes to STDERR by default)
- Assume `#p` has zero performance impact in tight loops

## Common Issues

### Issue: "No reader function for tag p"

**Problem:** hashp not installed before code is evaluated

```clojure
;; This fails
(ns my-app.core)
(defn calculate [x] #p (* x 2))
;; RuntimeException: No reader function for tag p
```

**Solution:** Install hashp before any namespace loads:

```clojure
;; In your main namespace or -main function
((requiring-resolve 'hashp.install/install!))

;; Then load other namespaces
(require '[my-app.core :as core])
```

**For project-wide installation:**

```clojure
;; In deps.edn
{:deps {dev.weavejester/hashp {:mvn/version "0.5.1"}}
 :paths ["src"]}

;; Create src/user.clj
(ns user)
((requiring-resolve 'hashp.install/install!))
```

### Issue: Output Not Showing

**Problem:** Output goes to STDERR which might not be visible

```clojure
#p (+ 1 2)
;; No output visible
```

**Solution:** Check your REPL/editor configuration for STDERR output, or redirect to STDOUT:

```clojure
(require '[hashp.install :as hashp])
(hashp/install! :writer *out*)
```

### Issue: Colors Look Wrong or Broken

**Problem:** Terminal doesn't support ANSI colors

**Solution:** Disable colors:

```clojure
(require '[hashp.install :as hashp])
(hashp/install! :color? false)
```

Or set the `NO_COLOR` environment variable:
```bash
NO_COLOR=1 clj
```

### Issue: Too Much Output

**Problem:** Using `#p` in tight loops creates overwhelming output

```clojure
(defn process-many [items]
  (map #(#p (inc %)) items))

(process-many (range 1000))
;; Prints 1000 debug statements
```

**Solution:** Use `#p` selectively or debug a sample:

```clojure
(defn process-many [items]
  (map #(inc %) items))

;; Debug with a small sample first
#p (process-many (range 5))

;; Or debug just the result
#p (process-many (range 1000))
```

### Issue: Side Effects Evaluated Multiple Times

**Problem:** `#p` evaluates the form, which may have side effects

```clojure
;; This increments the atom twice
(let [counter (atom 0)]
  #p (swap! counter inc))
;; counter is now 1, not 2 - #p doesn't re-evaluate
```

**Clarification:** `#p` only evaluates the form once. This is correct behavior.

### Issue: Production Code Contains #p

**Problem:** Forgot to remove debug statements before deployment

**Solution:** Use conditional installation:

```clojure
;; In your application startup
(when (or (System/getenv "DEBUG")
          (not= "production" (System/getenv "ENV")))
  ((requiring-resolve 'hashp.install/install!)))

;; Or disable in production
((requiring-resolve 'hashp.install/install!)
  :disabled? (= "production" (System/getenv "ENV")))
```

## Advanced Topics

### Custom Tags for Different Debug Levels

Create multiple debug tags for different purposes:

```clojure
(require '[hashp.install :as hashp])

;; Install multiple tags
(hashp/install! :tag 'p)      ; General debugging
(hashp/install! :tag 'trace)  ; Detailed tracing
(hashp/install! :tag 'perf)   ; Performance checks

;; Use different tags
#p (calculate-value x)      ; General debug
#trace (detailed-step x)     ; Detailed trace
#perf (expensive-operation)  ; Performance monitoring
```

### Integration with REPL Workflow

Pattern for REPL-driven development with hashp:

```clojure
;; 1. Start REPL with hashp enabled
((requiring-resolve 'hashp.install/install!))

;; 2. Load your namespace
(require '[my-app.core :as core] :reload)

;; 3. Test a function with #p
(core/my-function #p test-data)

;; 4. See the debug output and iterate

;; 5. When satisfied, remove #p and reload
(require '[my-app.core :as core] :reload)
```

### Comparison with Spyscope

Hashp is inspired by [Spyscope](https://github.com/dgrnbrg/spyscope) but with key differences:

| Feature | hashp | Spyscope |
|---------|-------|----------|
| Basic debugging | `#p expr` | `#spy/p expr` |
| Shows form | Yes | No |
| Shows context | Yes (ns/fn:line) | Limited |
| Multiple tags | Yes | Limited |
| Configurable | Yes | Limited |
| Dependencies | None (uses reader) | More complex |
| Installation | Simple | More setup |

**When to use hashp:**
- Simple, focused debugging needs
- Want to see original form
- Need configurable output
- Prefer lightweight solution

**When to use Spyscope:**
- Need more advanced features
- Want expression transformation
- Using legacy code with Spyscope

## Performance Considerations

**Runtime impact:**
- `#p` adds minimal overhead when `:disabled? true`
- Printing to STDERR is I/O bound
- Large data structures can slow down printing
- Consider using `#p` on computed results rather than large collections

**Development tips:**
```clojure
;; Good: Debug computed values
#p (count large-collection)
#p (take 5 large-collection)

;; Avoid: Printing huge data structures
#p large-collection ; May be slow if very large
```

## Resources

- [GitHub Repository](https://github.com/weavejester/hashp)
- [Clojars Package](https://clojars.org/dev.weavejester/hashp)
- [Spyscope](https://github.com/dgrnbrg/spyscope) - Alternative debugging library
- [Scope Capture](https://github.com/vvvvalvalval/scope-capture) - Advanced REPL debugging

## Summary

Hashp provides a fast, convenient way to debug Clojure code:

1. **Install once** - `((requiring-resolve 'hashp.install/install!))`
2. **Use anywhere** - `#p` before any expression
3. **See context** - Namespace, function, line number
4. **See form** - Original code, not just value
5. **Get results** - Returns original value unchanged

**Key patterns:**
- `#p expr` - Debug any expression
- `#p` in threading macros - See pipeline stages
- `#p` in let bindings - Check intermediate values
- Conditional installation - Enable/disable for environments

**Use hashp for:** Fast REPL-driven debugging, understanding code flow, checking intermediate values, and tracing execution. Remove `#p` statements before committing or use conditional enabling for production.
