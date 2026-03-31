---
name: meander
description: |
  Meander is a powerful pattern matching and data transformation library for Clojure/ClojureScript.
  Use when transforming nested data structures, extracting values with pattern matching, rewriting 
  expressions, performing structural transformations, or when the user mentions pattern matching, 
  logic variables, data extraction, tree rewriting, term rewriting, substitution, unification, 
  or declarative data transformations.
---

# Meander

Meander is a Clojure/ClojureScript library for transparent data transformation through pattern matching and substitution.

## Quick Start

Meander allows you to declaratively describe both the input structure and output structure:

```clojure
(require '[meander.epsilon :as m])

;; Simple pattern matching
(m/match {:name "Alice" :age 30}
  {:name ?name :age ?age}
  {:person ?name :years ?age})
;; => {:person "Alice", :years 30}

;; Logic variables join values across the pattern
(def foods-by-name
  {:nachos {:popularity :high :calories :lots}
   :smoothie {:popularity :high :calories :less}})

(m/match {:user {:name :alice :favorite-food {:name :nachos}}
          :foods-by-name foods-by-name}
  {:user {:name ?name
          :favorite-food {:name ?food}}
   :foods-by-name {?food {:popularity ?popularity
                          :calories ?calories}}}
  {:name ?name
   :favorite {:food ?food
              :popularity ?popularity
              :calories ?calories}})
;; => {:name :alice, :favorite {:food :nachos, :popularity :high, :calories :lots}}
```

## Core Concepts

### Logic Variables and Memory Variables

**Logic variables** (prefix `?`) bind to single values and allow joining across patterns:

```clojure
(m/match [1 1]
  [?x ?x]  ; Both must be the same value
  ?x)
;; => 1

(m/match [1 2]
  [?x ?x]
  ?x)
;; => Match failure
```

**Memory variables** (prefix `!`) collect multiple values:

```clojure
(m/search [1 2 3 4]
  [!odds ...]
  (when (odd? !odds)
    !odds))
;; => (1 3)  ; Note: This is incorrect syntax, see correct usage below

(m/match {:a 1 :b 2 :c 3}
  {?k !v ...}
  [?k !v])
;; Wrong! Logic and memory variables shouldn't mix like this
```

Correct memory variable usage:

```clojure
(m/find [{:a 1} {:b 2} {:c 3}]
  [{!ks !vs} ...]
  {:keys !ks :values !vs})
;; => {:keys [:a :b :c], :values [1 2 3]}
```

### Zero-or-More Operator (`...`)

The `...` operator matches zero or more occurrences:

```clojure
(m/match [1 2 3]
  [?x ...]
  ?x)
;; => [1 2 3]

(m/match [{:name "Alice"} {:name "Bob"}]
  [{:name !names} ...]
  !names)
;; => ["Alice" "Bob"]
```

**N-or-more** operator `..n` ensures minimum matches:

```clojure
(m/match [1 2 3]
  [?x ..2]  ; At least 2 elements
  ?x)
;; => [1 2 3]

(m/match [1]
  [?x ..2]
  ?x)
;; => Match failure (need at least 2)
```

### Match vs Find vs Search

**`match`** - Returns first successful match, fails if no match:

```clojure
(m/match [1 2]
  [?x ?y] [?y ?x])
;; => [2 1]
```

**`find`** - Like match but returns `nil` instead of throwing on failure:

```clojure
(m/find [1 2 3]
  [?x ?y] [?y ?x]
  [?x ?y ?z] [?z ?y ?x])
;; => [3 2 1]
```

**`search`** - Returns lazy sequence of all possible matches:

```clojure
(m/search [1 2 3]
  [!xs ... !ys ...]
  {:xs !xs :ys !ys})
;; => ({:xs [], :ys [1 2 3]}
;;     {:xs [1], :ys [2 3]}
;;     {:xs [1 2], :ys [3]}
;;     {:xs [1 2 3], :ys []})
```

## Common Workflows

### Workflow 1: Basic Pattern Matching

Extract and transform nested data:

```clojure
(require '[meander.epsilon :as m])

;; Extract from nested structure
(def user {:personal {:name "Alice" :email "alice@example.com"}
           :prefs {:theme :dark :lang :en}})

(m/match user
  {:personal {:name ?name :email ?email}
   :prefs {:theme ?theme}}
  {:name ?name
   :email ?email
   :theme ?theme})
;; => {:name "Alice", :email "alice@example.com", :theme :dark}

;; Pattern matching with predicates
(m/match {:value 42}
  {:value (m/pred even? ?n)}
  {:even-number ?n})
;; => {:even-number 42}

;; Multiple patterns (tried in order)
(m/match [1 2 3]
  [?x] {:one ?x}
  [?x ?y] {:two [?x ?y]}
  [?x ?y ?z] {:three [?x ?y ?z]})
;; => {:three [1 2 3]}
```

### Workflow 2: Collecting Values with Memory Variables

Gather values from collections:

```clojure
(require '[meander.epsilon :as m])

;; Collect all matching values
(m/find {:foods [{:name :nachos :type :snack}
                 {:name :apple :type :fruit}
                 {:name :chips :type :snack}]}
  {:foods [{:name !names :type :snack} ...]}
  !names)
;; => [:nachos :chips]

;; Multiple memory variables
(m/match [{:id 1 :name "Alice"}
          {:id 2 :name "Bob"}]
  [{:id !ids :name !names} ...]
  (zipmap !ids !names))
;; => {1 "Alice", 2 "Bob"}

;; Gather from nested structures
(def data
  {:users [{:name "Alice" :favorite-foods [{:name :pizza} {:name :tacos}]}
           {:name "Bob" :favorite-foods [{:name :salad}]}]})

(m/find data
  {:users [{:name !user-names
            :favorite-foods [{:name !food-names} ...]} ...]}
  (map vector !user-names !food-names))
;; => (["Alice" [:pizza :tacos]] ["Bob" [:salad]])
```

### Workflow 3: Rewriting Data Structures

Transform data in place using `rewrite`:

```clojure
(require '[meander.epsilon :as m])

;; Simple transformation
(m/rewrite {:a 1 :b 2}
  {:a ?x :b ?y}
  {:x ?x :y ?y})
;; => {:x 1, :y 2}

;; Rewrite with memory variables
(m/rewrite [{:name "Alice" :age 30}
            {:name "Bob" :age 25}]
  [{:name !names :age !ages} ...]
  [{:person !names :years !ages} ...])
;; => [{:person "Alice", :years 30} {:person "Bob", :years 25}]

;; Multiple rewrite patterns
(m/rewrite [1 [2 3] [4 [5 6]]]
  [?x [?y ?z] [?a [?b ?c]]]
  {:first ?x :second [?y ?z] :third [?a ?b ?c]})
;; => {:first 1, :second [2 3], :third [4 5 6]}

;; Conditional rewrite
(defn normalize-coord [point]
  (m/rewrite point
    [?x ?y] [?x ?y 0]  ; Add z coordinate if missing
    [?x ?y ?z] [?x ?y ?z]))  ; Keep as is if complete

(normalize-coord [1 2])   ;; => [1 2 0]
(normalize-coord [1 2 3]) ;; => [1 2 3]
```

### Workflow 4: Searching for All Matches

Find all possible matches with `search`:

```clojure
(require '[meander.epsilon :as m])

;; Find all ways to split a collection
(m/search [1 2 3]
  [!xs ... !ys ...]
  {:before !xs :after !ys})
;; => ({:before [], :after [1 2 3]}
;;     {:before [1], :after [2 3]}
;;     {:before [1 2], :after [3]}
;;     {:before [1 2 3], :after []})

;; Search through nested data
(m/search {:users [{:name "Alice" :role :admin}
                   {:name "Bob" :role :user}
                   {:name "Carol" :role :admin}]}
  {:users [{:name ?name :role :admin} ...]}
  ?name)
;; => ("Alice" "Carol")

;; Multiple search clauses
(m/search {:data [{:type :a :value 1}
                  {:type :b :value 2}
                  {:type :a :value 3}]}
  {:data [{:type :a :value ?v} ...]}
  [:type-a ?v]
  
  {:data [{:type :b :value ?v} ...]}
  [:type-b ?v])
;; => ([:type-a 1] [:type-a 3] [:type-b 2])
```

### Workflow 5: Pattern Matching Operators

Use built-in operators for common patterns:

```clojure
(require '[meander.epsilon :as m])

;; scan - find subsequence anywhere in collection
(m/match [1 2 3 4 5]
  [(m/scan 3) ...]
  :found)
;; => :found

(m/find [1 2 3 4 5]
  (m/scan ?x ?y)
  [?x ?y])
;; => [1 2]  ; First consecutive pair

;; pred - predicate matching
(m/match 42
  (m/pred even? ?x)
  ?x)
;; => 42

(m/match {:value 100}
  {:value (m/pred #(> % 50) ?n)}
  {:large ?n})
;; => {:large 100}

;; guard - conditional matching
(m/match [1 2 3]
  [?x ?y ?z] (m/guard (= (+ ?x ?y) ?z))
  :sum-matches)
;; => :sum-matches

;; and - all patterns must match
(m/match 42
  (m/and (m/pred even?) (m/pred #(> % 40)) ?x)
  ?x)
;; => 42

;; or - any pattern can match  
(m/match :red
  (m/or :red :blue :green)
  :primary-color)
;; => :primary-color

;; app - apply function then match result
(m/match [1 2 3]
  (m/app count ?n)
  ?n)
;; => 3

;; gather - filter and collect
(m/match [1 2 3 4 5 6]
  (m/gather (m/pred even? !evens))
  !evens)
;; => [2 4 6]
```

### Workflow 6: Recursive Patterns with cata

Use `cata` for recursive transformations:

```clojure
(require '[meander.epsilon :as m])

;; Recursively transform nested structure
(m/match [1 [2 3] [[4 5]]]
  [(m/cata ?x) ...]
  ?x
  
  ?x
  (* 2 ?x))
;; => [2 [4 6] [[8 10]]]

;; Tree transformation
(defn double-numbers [tree]
  (m/match tree
    [(m/cata !xs) ...]
    !xs
    
    (m/pred number? ?n)
    (* 2 ?n)
    
    ?other
    ?other))

(double-numbers [1 "hi" [2 [3 "bye"] 4]])
;; => [2 "hi" [4 [6 "bye"] 8]]

;; Convert keywords to strings recursively
(defn keywords->strings [data]
  (m/match data
    {:keys [(m/cata !ks) ...] :vals [(m/cata !vs) ...]}
    (zipmap !ks !vs)
    
    [(m/cata !items) ...]
    !items
    
    (m/pred keyword? ?kw)
    (name ?kw)
    
    ?x
    ?x))

(keywords->strings {:name :alice :prefs {:theme :dark}})
;; => {"name" "alice", "prefs" {"theme" "dark"}}
```

### Workflow 7: Strategies for Term Rewriting

Use strategies for powerful rewriting systems:

```clojure
(require '[meander.epsilon :as m]
         '[meander.strategy.epsilon :as s])

;; Simplify arithmetic expressions
(def simplify-arith
  (s/rewrite
    (+ ?x 0) ?x
    (+ 0 ?x) ?x
    (* ?x 0) 0
    (* 0 ?x) 0
    (* ?x 1) ?x
    (* 1 ?x) ?x))

;; Apply strategy bottom-up (innermost first)
(def simplify-all
  (s/bottom-up (s/attempt simplify-arith)))

(simplify-all '(+ (+ 0 x) (* y 1)))
;; => (+ x y)

;; Repeated application until fixpoint
(def eliminate-zeros
  (s/rewrite
    (+ ?x 0) ?x
    (+ 0 ?x) ?x))

(def eliminate-all-zeros
  (s/bottom-up (s/attempt eliminate-zeros)))

(eliminate-all-zeros '(+ (+ 0 (+ 0 (+ 3 (+ 2 0)))) 0))
;; => (+ 3 2)

;; Top-down vs bottom-up
(def eval-arith
  (s/rewrite
    (+ ?x ?y) (+ ?x ?y)
    (* ?x ?y) (* ?x ?y)
    ?x ?x))

;; Top-down evaluates outer expressions first
((s/top-down (s/attempt eval-arith))
 '(+ (* 2 3) (* 4 5)))
;; => 26

;; Repeat until no more changes
((s/repeat (s/bottom-up (s/attempt simplify-arith)))
 '(+ (+ 0 1) (* (+ 0 2) 1)))
;; => (+ 1 2)
```

## When to Use Meander

**Use Meander when:**
- Transforming nested or complex data structures
- Extracting values from deeply nested maps/vectors
- Pattern matching with logic and constraints
- Rewriting expressions or ASTs
- Need declarative data transformations
- Working with tree structures
- Implementing DSL transformations
- Normalizing or denormalizing data
- Multiple patterns need to be tried
- Gathering scattered values into collections

**Don't use Meander when:**
- Simple `get-in` or `update-in` suffices
- Transformations are one-off and trivial
- Performance is absolutely critical (pattern compilation has overhead)
- Team unfamiliar with pattern matching concepts
- Data structure is flat and simple

## Meander vs Other Approaches

**vs core.match:**
- Meander has memory variables for collecting values
- More powerful operators (scan, cata, gather)
- Substitution/rewriting built-in
- Better for data transformation, not just matching

**vs Specter:**
- Meander is declarative (describe input/output)
- Specter is navigational (describe path)
- Meander better for whole-structure transformations
- Specter better for focused updates deep in structures

**vs manual destructuring:**
- Meander handles ambiguous patterns
- More concise for complex nested structures
- Logic variables provide value joining
- Better for searching/finding multiple matches

## Best Practices

**Do:**
- Use descriptive logic variable names (`?user-name` not `?x`)
- Leverage memory variables for collecting values
- Use `find` when you only need first match
- Use `search` when you need all matches
- Combine patterns with `and`/`or` for clarity
- Use `scan` to find subsequences anywhere
- Apply strategies for recursive transformations
- Use `cata` for recursive pattern matching
- Test patterns in REPL incrementally
- Use `pred` for runtime checks

**Don't:**
- Mix logic and memory variables carelessly
- Use `search` when `find` would suffice (performance)
- Create overly complex nested patterns (split into steps)
- Forget that `match` throws on no match (use `find` if unsure)
- Ignore the compilation cost for frequently-called code
- Use `...` without understanding it can match zero elements

## Common Issues

### Logic Variable Not Unifying

```clojure
;; Wrong: Different values can't unify
(m/match [1 2]
  [?x ?x]
  ?x)
;; => Match failure

;; Right: Use separate variables
(m/match [1 2]
  [?x ?y]
  [?x ?y])
;; => [1 2]

;; Right: Or check equality in guard
(m/match [1 2]
  [?x ?y] (m/guard (= ?x ?y))
  ?x)
;; => Match failure
```

### Memory Variable Incorrect Usage

```clojure
;; Wrong: Memory variable needs ... to collect
(m/match [1 2 3]
  [!xs]
  !xs)
;; => Match failure (expects single-element vector)

;; Right: Use ... operator
(m/match [1 2 3]
  [!xs ...]
  !xs)
;; => [1 2 3]

;; Wrong: Mixing logic and memory incorrectly
(m/match [{:a 1} {:a 2}]
  [{:a ?x} !rest ...]  ; ?x and !rest don't align
  [?x !rest])

;; Right: Use memory variables consistently
(m/match [{:a 1} {:a 2}]
  [{:a !xs} ...]
  !xs)
;; => [1 2]
```

### Match vs Find Confusion

```clojure
;; Wrong: match throws when no pattern matches
(m/match [1]
  [?x ?y]
  [?x ?y])
;; => ExceptionInfo: Non-exhaustive pattern match

;; Right: Use find for optional matching
(m/find [1]
  [?x ?y] [?x ?y]
  [?x] [?x])
;; => [1]

;; Or provide catch-all pattern
(m/match [1]
  [?x ?y] [?x ?y]
  ?other ?other)
;; => [1]
```

### Scan Not Finding Pattern

```clojure
;; Wrong: scan expects exact subsequence
(m/find [1 2 3 4]
  (m/scan 2 4)  ; 2 and 4 aren't consecutive
  :found)
;; => nil

;; Right: Elements must be consecutive
(m/find [1 2 3 4]
  (m/scan 2 3)
  :found)
;; => :found

;; Or use search for non-consecutive
(m/search [1 2 3 4]
  [_ ... 2 _ ... 4 _ ...]
  :found)
;; => (:found)
```

### Strategy Not Simplifying

```clojure
(require '[meander.strategy.epsilon :as s])

;; Wrong: Strategy only tries once
((s/rewrite (+ ?x 0) ?x)
 '(+ (+ 1 0) 0))
;; => (+ 1 0)  ; Only outer (+ ... 0) simplified

;; Right: Use repeat or bottom-up
((s/repeat (s/rewrite (+ ?x 0) ?x))
 '(+ (+ 1 0) 0))
;; => 1

;; Or use bottom-up
((s/bottom-up (s/attempt (s/rewrite (+ ?x 0) ?x)))
 '(+ (+ 1 0) 0))
;; => 1
```

## Pattern Matching Operators Reference

### Basic Operators

- **`?variable`** - Logic variable, binds to single value
- **`!variable`** - Memory variable, collects multiple values
- **`_`** - Wildcard, matches anything without binding
- **`...`** - Zero or more repetitions
- **`..n`** - N or more repetitions (e.g., `..2`)
- **`.`** - Dot operator for rest patterns (in seqable contexts)

### Matching Operators

- **`(m/scan patterns...)`** - Find consecutive subsequence
- **`(m/pred pred-fn)`** - Match if predicate true
- **`(m/pred pred-fn ?var)`** - Match predicate and bind
- **`(m/guard expr)`** - Match if expression true
- **`(m/and patterns...)`** - All patterns must match
- **`(m/or patterns...)`** - Any pattern can match
- **`(m/not pattern)`** - Pattern must not match
- **`(m/some)`** - Match non-nil value
- **`(m/some ?var)`** - Match non-nil and bind
- **`(m/app f pattern)`** - Apply function, then match result
- **`(m/cata pattern)`** - Recursive catamorphism
- **`(m/let [bindings] pattern)`** - Local bindings in pattern
- **`(m/with [%name pattern] body)`** - Named pattern references
- **`(m/gather pattern)`** - Filter and collect matches
- **`(m/separated patterns...)`** - Match separated by anything

### Type Operators

- **`(m/number)`** - Match number
- **`(m/number ?var)`** - Match number and bind
- **`(m/keyword)`** - Match keyword
- **`(m/keyword ?var)`** - Match keyword and bind
- **`(m/symbol)`** - Match symbol
- **`(m/re regex)`** - Match string against regex
- **`(m/re regex capture-pattern)`** - Match and bind captures
- **`(m/seqable patterns...)`** - Match seqable's seq
- **`(m/map-of k-pat v-pat)`** - Match all map entries
- **`(m/submap-of k-pat v-pat)`** - Match some map entries
- **`(m/set-of pattern)`** - Match all set elements
- **`(m/subset-of pattern)`** - Match some set elements

### Strategy Combinators

- **`(s/pipe s1 s2 ...)`** - Sequential composition
- **`(s/choice s1 s2 ...)`** - Try strategies in order
- **`(s/all s)`** - Apply to all direct children
- **`(s/one s)`** - Apply to one direct child
- **`(s/some s)`** - Apply to at least one child
- **`(s/repeat s)`** - Repeat until failure
- **`(s/attempt s)`** - Try strategy, return original on fail
- **`(s/bottom-up s)`** - Apply innermost-first (post-order)
- **`(s/top-down s)`** - Apply outermost-first (pre-order)
- **`(s/innermost s)`** - Repeat bottom-up until fixpoint
- **`(s/outermost s)`** - Repeat top-down until fixpoint
- **`(s/fix s)`** - Repeat until result unchanged
- **`(s/n-times n s)`** - Apply exactly n times
- **`(s/while pred s)`** - Repeat while predicate true
- **`(s/until pred s)`** - Repeat until predicate true
- **`(s/guard p s)`** - Apply s only if predicate p true

## External Resources

- [GitHub Repository](https://github.com/noprompt/meander)
- [API Documentation](https://cljdoc.org/d/meander/epsilon/CURRENT)
- [Cookbook](https://github.com/noprompt/meander/blob/epsilon/doc/cookbook.md)
- [Strategies Guide](https://github.com/noprompt/meander/blob/epsilon/doc/strategies.md)
- [Blog: Meander for Practical Data Transformation](https://jimmyhmiller.github.io/meander-practical)
- [Blog: Introduction to Term Rewriting](https://jimmyhmiller.github.io/meander-rewriting)
- [Talk: Strangeloop 2019](https://www.youtube.com/watch?v=9fhnJpCgtUw)
- [Clojurians Slack #meander](https://clojurians.slack.com/archives/CFFTD7R6Z)

## Advanced Patterns

### Custom Syntax Extensions

Define your own pattern matching extensions:

```clojure
(require '[meander.epsilon :as m])

;; Define custom pattern operator
(m/defsyntax number
  ([] `(number _#))
  ([pattern]
   (if (m/match-syntax? &env)
     `(m/pred number? ~pattern)
     &form)))

;; Use it
(m/match 42
  (number ?x)
  ?x)
;; => 42
```

### Contextual Matching with $

The `$` operator finds patterns in subtrees:

```clojure
(m/match [:A [:B 2 :C] :D]
  (m/$ (m/pred number? ?x))
  ?x)
;; => 2

;; With context for updating
(m/match [:A [:B 2 :C] :D]
  (m/$ ?context (m/pred number? ?x))
  (?context 99))
;; => [:A [:B 99 :C] :D]
```

### Substitution

Invert pattern matching with `subst`:

```clojure
(let [!xs [1 2 3]
      !ys [:a :b :c]]
  (m/subst [{:x !xs :y !ys} ...]))
;; => [{:x 1, :y :a} {:x 2, :y :b} {:x 3, :y :c}]
```
