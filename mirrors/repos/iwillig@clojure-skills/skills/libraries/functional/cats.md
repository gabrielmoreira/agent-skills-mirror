---
name: cats-category-theory
description: |
  Category theory abstractions for functional programming with cats. Use when working
  with monads, functors, applicatives, monadic composition, error handling with Maybe
  and Either, state management, or when the user mentions category theory, monads,
  functors, applicatives, monadic bind, fmap, pure functions, or functional abstractions.
---

# Cats - Category Theory for Clojure

Cats is a library that provides category theory abstractions for Clojure, including functors, applicatives, monads, and more. It enables functional programming patterns with composable abstractions.

## Quick Start

```clojure
;; Add dependency
{:deps {funcool/cats {:mvn/version "2.4.2"}}}

;; Require core namespace and common monads
(require '[cats.core :as m])
(require '[cats.monad.maybe :as maybe])
(require '[cats.monad.either :as either])

;; Basic Maybe monad usage
(def result (maybe/just 42))
@result
;; => 42

;; Monadic composition with mlet
@(m/mlet [x (maybe/just 1)
          y (maybe/just 2)]
   (m/return (+ x y)))
;; => 3
```

**Key benefits:**
- Composable functional abstractions
- Type-safe error handling without exceptions
- Monadic composition for sequential computations
- Applicative composition for parallel computations
- Rich library of monads (Maybe, Either, State, etc.)

## Core Concepts

### Functors - Mapping Over Contexts

Functors allow you to apply a function to values wrapped in a context using `fmap`:

```clojure
;; fmap applies a function inside a context
@(m/fmap inc (maybe/just 1))
;; => 2

;; Works with various contexts
(m/fmap inc [1 2 3])
;; => [2 3 4]

;; Nothing values are preserved
@(m/fmap inc (maybe/nothing))
;; => nil
```

**When to use:** Transform values without leaving their monadic context.

### Applicatives - Parallel Composition

Applicatives enable applying wrapped functions to wrapped values:

```clojure
;; alet for applicative composition
@(m/alet [x (maybe/just 1)
          y (maybe/just 2)
          z (maybe/just 3)]
   (+ x y z))
;; => 6

;; ap - apply pure function to applicative values
@(m/ap + (maybe/just 1) (maybe/just 2) (maybe/just 3))
;; => 6
```

**When to use:** Combine multiple independent computations in parallel.

### Monads - Sequential Composition

Monads enable sequential composition where each step can depend on previous results:

```clojure
;; mlet - monadic let for sequential composition
@(m/mlet [x (maybe/just 1)
          y (maybe/just (inc x))
          z (maybe/just (* y 2))]
   (m/return (+ x y z)))
;; => 7

;; >>= - bind operator for chaining
@(m/>>= (maybe/just 1)
        (fn [x] (maybe/just (inc x)))
        (fn [x] (maybe/just (* x 2))))
;; => 4
```

**When to use:** Chain computations where each step depends on the previous result.

### Dereferencing Monadic Values

Most monadic values implement `IDeref`, allowing you to extract values with `@`:

```clojure
;; Extract value from Maybe
@(maybe/just 42)
;; => 42

@(maybe/nothing)
;; => nil

;; Extract value from Either
@(either/right 42)
;; => 42

@(either/left "error")
;; => "error"

;; Note: Vectors and other collection types don't use @
(m/fmap inc [1 2 3])
;; => [2 3 4]
```

## Common Workflows

### Workflow 1: Safe Computation with Maybe

Handle potentially null values without null checks:

```clojure
(require '[cats.core :as m])
(require '[cats.monad.maybe :as maybe])

;; Constructor functions
(def has-value (maybe/just 42))
(def no-value (maybe/nothing))

;; Check type
(maybe/just? has-value)     ;; => true
(maybe/nothing? no-value)   ;; => true

;; Safe computation with mlet
@(m/mlet [x (maybe/just 10)
          y (maybe/just 5)]
   (m/return (/ x y)))
;; => 2

;; Short-circuits on Nothing
@(m/mlet [x (maybe/just 10)
          y (maybe/nothing)
          z (maybe/just 5)]
   (m/return (+ x y z)))
;; => nil

;; Provide default values
(maybe/from-maybe (maybe/just 42) 0)
;; => 42

(maybe/from-maybe (maybe/nothing) 0)
;; => 0

;; Chain operations with fmap
@(-> (maybe/just 1)
     (m/fmap inc)
     (m/fmap (* 2)))
;; => 4
```

### Workflow 2: Error Handling with Either

Handle errors functionally without throwing exceptions:

```clojure
(require '[cats.monad.either :as either])

;; Right represents success
@(either/right 42)
;; => 42

;; Left represents error/failure
@(either/left "error message")
;; => "error message"

;; Pattern: safe division
(defn safe-div [x y]
  (if (zero? y)
    (either/left "Division by zero")
    (either/right (/ x y))))

;; Compose with mlet
@(m/mlet [a (either/right 10)
          b (safe-div a 2)
          c (safe-div b 5)]
   (m/return c))
;; => 1

;; Error propagates
@(m/mlet [a (either/right 10)
          b (safe-div a 0)
          c (either/right 100)]
   (m/return (+ b c)))
;; => "Division by zero"

;; Branch on Either result
(either/branch (either/right 42)
               (fn [err] (str "Error: " err))
               (fn [val] (str "Success: " val)))
;; => "Success: 42"

(either/branch (either/left "failed")
               (fn [err] (str "Error: " err))
               (fn [val] (str "Success: " val)))
;; => "Error: failed"

;; Check Either type
(either/right? (either/right 42))   ;; => true
(either/left? (either/left "err"))  ;; => true
```

### Workflow 3: Exception Handling with try-either

Convert exception-throwing code to Either monad:

```clojure
;; Wrap potentially throwing code
@(either/try-either
   (/ 10 2))
;; => 5

;; Exceptions become Left values
(def result (either/try-either (/ 10 0)))

(either/left? result)
;; => true

(.getMessage @result)
;; => "Divide by zero"

;; Compose with other Either operations
@(m/mlet [x (either/try-either (Integer/parseInt "42"))
          y (either/try-either (Integer/parseInt "10"))]
   (m/return (+ x y)))
;; => 52

;; Parse failure returns Left with exception
@(m/mlet [x (either/try-either (Integer/parseInt "not-a-number"))
          y (either/try-either (Integer/parseInt "10"))]
   (m/return (+ x y)))
;; => #<NumberFormatException ...>
```

### Workflow 4: Lifting Pure Functions

Transform regular functions to work with monadic values:

```clojure
;; lift-m - lift function to monadic context
(def m+ (m/lift-m 2 +))

@(m+ (maybe/just 1) (maybe/just 2))
;; => 3

@(m+ (maybe/just 1) (maybe/nothing))
;; => nil

;; lift-a - lift function to applicative context
(def a+ (m/lift-a 2 +))

@(a+ (maybe/just 1) (maybe/just 2))
;; => 3

;; Works with any arity
(def m-sum (m/lift-m 3 +))

@(m-sum (maybe/just 1) (maybe/just 2) (maybe/just 3))
;; => 6
```

### Workflow 5: Working with Sequences

Transform and combine sequences of monadic values:

```clojure
;; sequence - convert list of monads to monad of list
@(m/sequence [(maybe/just 1) (maybe/just 2) (maybe/just 3)])
;; => (1 2 3)

;; If any is Nothing, result is Nothing
(maybe/just? (m/sequence [(maybe/just 1) 
                           (maybe/nothing) 
                           (maybe/just 3)]))
;; => false

;; mapseq - map function and sequence
@(m/mapseq maybe/just [1 2 3])
;; => (1 2 3)

@(m/mapseq (fn [x]
             (if (even? x)
               (maybe/just x)
               (maybe/nothing)))
           [2 4])
;; => (2 4)

;; forseq - same as mapseq with flipped arguments
@(m/forseq [1 2 3] maybe/just)
;; => (1 2 3)
```

### Workflow 6: State Monad

Manage state in a pure functional way:

```clojure
(require '[cats.monad.state :as state])

;; Basic state operations
(def computation
  (m/mlet [a (state/get)         ; Get current state
           _ (state/put (inc a))] ; Update state
    (m/return a)))                ; Return old state

;; run returns Pair of [value new-state]
(state/run computation 10)
;; => #<Pair [10 11]>

;; eval returns just the value
(state/eval computation 10)
;; => 10

;; exec returns just the final state
(state/exec computation 10)
;; => 11

;; More complex state manipulation
(def counter
  (m/mlet [count (state/get)
           _ (state/put (+ count 5))
           new-count (state/get)]
    (m/return {:old count :new new-count})))

(state/eval counter 0)
;; => {:old 0, :new 5}

;; swap - apply function to state
(def increment
  (m/mlet [old (state/swap inc)]
    (m/return old)))

(state/run increment 5)
;; => #<Pair [5 6]>
```

### Workflow 7: Currying Functions

Create partially applicable functions:

```clojure
;; curry with explicit arity
(def cadd (m/curry 2 +))

;; Partial application
((cadd 5) 10)
;; => 15

;; Multiple partial applications
(((cadd) 5) 10)
;; => 15

;; Still works with all args at once
(cadd 5 10)
;; => 15

;; curry-lift-m - curry and lift to monadic context
(def mcadd (m/curry-lift-m 2 +))

@((mcadd (maybe/just 5)) (maybe/just 10))
;; => 15
```

### Workflow 8: Vector as Monad (List Comprehension)

Use vectors as non-deterministic computations:

```clojure
(require '[cats.context :as ctx])
(require '[cats.builtin])

;; Set context for vectors
(ctx/with-context cats.builtin/vector-context
  (m/mlet [x [1 2 3]
           y [10 20]]
    (m/return (+ x y))))
;; => [11 21 12 22 13 23]

;; Or use fmap directly (context inferred)
(m/fmap inc [1 2 3])
;; => [2 3 4]

;; Cartesian product with mlet
(ctx/with-context cats.builtin/vector-context
  (m/mlet [x [1 2]
           y [:a :b]
           z [true false]]
    (m/return [x y z])))
;; => [[1 :a true] [1 :a false] [1 :b true] [1 :b false]
;;     [2 :a true] [2 :a false] [2 :b true] [2 :b false]]
```

## When to Use Each Monad

**Use Maybe when:**
- Handling potentially null/absent values
- Optional configuration or parameters
- Safe navigation through nested data
- Want to avoid explicit null checks

**Use Either when:**
- Error handling without exceptions
- Need to carry error information
- Railway-oriented programming
- Validation that can fail with messages

**Use State when:**
- Managing state in pure functions
- Avoiding mutable state
- Threading state through computations
- Building interpreters or stateful computations

**Use Vector when:**
- Non-deterministic computations
- Cartesian products
- List comprehensions
- Multiple possible outcomes

## Best Practices

**DO:**
- Use `mlet` for readable sequential composition
- Prefer `alet` when operations are independent (applicative)
- Use `@` to extract values from Maybe and Either
- Provide default values with `from-maybe`
- Use `try-either` to wrap exception-throwing code
- Chain operations with `fmap` for simple transformations
- Use `sequence` to work with collections of monadic values

**DON'T:**
- Mix monadic contexts without explicit conversion
- Use `@` on vectors and collections (not supported)
- Throw exceptions in monadic code (use Either)
- Forget to handle Nothing/Left cases
- Over-nest `mlet` bindings (extract to functions)
- Use monads where plain functions suffice

## Common Issues

### Issue: "No context is set"

**Problem:** Vector operations fail without context

```clojure
(m/mlet [x [1 2]
         y [3 4]]
  (m/return (+ x y)))
;; => Error: No context is set
```

**Solution:** Use `with-context` for vectors

```clojure
(require '[cats.context :as ctx])
(require '[cats.builtin])

(ctx/with-context cats.builtin/vector-context
  (m/mlet [x [1 2]
           y [3 4]]
    (m/return (+ x y))))
;; => [4 5 5 6]
```

### Issue: "Cannot cast to Future"

**Problem:** Using `@` on non-derefable types

```clojure
@(m/fmap inc [1 2 3])
;; => Error: Cannot cast to Future
```

**Solution:** Don't use `@` with vectors and collections

```clojure
(m/fmap inc [1 2 3])
;; => [2 3 4]
```

### Issue: Print Errors with Maybe/Either

**Problem:** REPL print errors when returning Just or Right

```clojure
(maybe/just 42)
;; => Error: Multiple methods match dispatch value
```

**Solution:** Use `@` to deref, or use `str` for string representation

```clojure
@(maybe/just 42)
;; => 42

(str (maybe/just 42))
;; => "cats.monad.maybe.Just@..."
```

### Issue: Currying Without Arity

**Problem:** Curry fails with variadic or multi-arity functions

```clojure
(def add (fn [x y] (+ x y)))
(m/curry add)
;; => Error: No arity metadata
```

**Solution:** Provide explicit arity

```clojure
(def cadd (m/curry 2 +))
((cadd 5) 10)
;; => 15
```

## Advanced Topics

### Monad Transformers

Combine multiple monadic effects (see cats documentation for details).

### Custom Monads

Implement your own monads by extending cats protocols.

### Monad Laws

Cats monads follow category theory laws:
- Left identity: `(>>= (return a) f) == (f a)`
- Right identity: `(>>= m return) == m`
- Associativity: `(>>= (>>= m f) g) == (>>= m (fn [x] (>>= (f x) g)))`

## Resources

- [GitHub Repository](https://github.com/funcool/cats)
- [API Documentation](https://funcool.github.io/cats/latest/)
- [Category Theory Basics](https://en.wikipedia.org/wiki/Category_theory)
- [Learn You a Haskell for Great Good](http://learnyouahaskell.com/) - Monads explained
- [Functors, Applicatives, and Monads in Pictures](http://adit.io/posts/2013-04-17-functors,_applicatives,_and_monads_in_pictures.html)

## Summary

Cats brings category theory abstractions to Clojure:

1. **Functors** - Transform values in context with `fmap`
2. **Applicatives** - Combine independent computations with `alet` and `ap`
3. **Monads** - Chain dependent computations with `mlet` and `>>=`
4. **Maybe** - Handle optional values without null checks
5. **Either** - Error handling without exceptions
6. **State** - Pure functional state management
7. **Lifting** - Transform pure functions to work with monads

Use cats when you want composable functional abstractions, type-safe error handling, and elegant solutions to common programming problems through category theory.
