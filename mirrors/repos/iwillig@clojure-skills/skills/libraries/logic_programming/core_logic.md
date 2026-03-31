---
name: core_logic
description: |
  Logic programming library for Clojure & ClojureScript providing relational programming, 
  constraint logic programming (CLP), and nominal logic. Use when solving constraint 
  satisfaction problems, logic puzzles, type inference, declarative queries, pattern 
  matching, or when the user mentions Prolog, miniKanren, relational programming, 
  unification, logic variables, constraint solving, sudoku solver, or declarative logic.
---

# core.logic

A logic programming library for Clojure and ClojureScript that provides Prolog-like relational programming, constraint logic programming, and nominal logic programming. At its heart is an implementation of miniKanren with extensions for constraint domains and nominal logic.

## Quick Start

```clojure
;; Add dependency
{:deps {org.clojure/core.logic {:mvn/version "1.1.0"}}}

;; Require and exclude == to use core.logic's unification operator
(require '[clojure.core.logic :refer [run* fresh == conde]])

;; Simple query: find values where q unifies with true
(run* [q]
  (== q true))
;; => (true)

;; Multiple solutions with conde (logical or)
(run* [q]
  (conde
    [(== q 1)]
    [(== q 2)]
    [(== q 3)]))
;; => (1 2 3)

;; Fresh variables and relationships
(run* [q]
  (fresh [x y]
    (== x 1)
    (== y 2)
    (== q [x y])))
;; => ([1 2])
```

**Key benefits:**
- Declarative logic programming in Clojure
- Solves constraint satisfaction problems
- Works with Clojure and ClojureScript
- Extensible to custom constraint domains
- Supports tabling for termination guarantees

## Core Concepts

### Logic Variables and Unification

Logic variables (lvars) are placeholders that can unify with values or other variables:

```clojure
(require '[clojure.core.logic :refer [run* fresh == !=]])

;; Fresh introduces new logic variables
(run* [q]
  (fresh [x y]
    (== x 1)        ; x unifies with 1
    (== y x)        ; y unifies with x (and thus 1)
    (== q [x y])))  ; q unifies with [x y]
;; => ([1 1])

;; Unification works with complex data structures
(run* [q]
  (fresh [x]
    (== [1 x 3] [1 2 3])  ; Pattern matching via unification
    (== q x)))
;; => (2)
```

**Note:** Must exclude `clojure.core/==` when using core.logic's unification operator:
```clojure
(ns my-app
  (:refer-clojure :exclude [==])
  (:require [clojure.core.logic :refer [== run* fresh]]))
```

### Goals and Goal Composition

Goals are predicates that succeed or fail. They compose to form logic programs:

```clojure
(require '[clojure.core.logic :refer [run* fresh == conde succeed fail]])

;; succeed and fail are primitive goals
(run* [q]
  succeed)    ; Always succeeds
;; => (_0)  ; One solution (unbound variable)

(run* [q]
  fail)       ; Always fails
;; => ()    ; No solutions

;; conde creates disjunction (logical OR)
(run* [q]
  (conde
    [(== q 'olive)]
    [(== q 'oil)]))
;; => (olive oil)

;; Multiple goals in sequence create conjunction (logical AND)
(run* [q]
  (fresh [x y]
    (== x 1)
    (== y 2)
    (== q [x y])))
;; => ([1 2])
```

### Constraint Logic Programming (CLP)

core.logic supports multiple constraint domains:

**CLP(Tree) - Disequality Constraints:**
```clojure
(require '[clojure.core.logic :refer [run* fresh == !=]])

;; != ensures terms never unify
(run* [q]
  (!= q 1))
;; => ((_0 :- (!= _0 1)))  ; Any value except 1

(run* [q]
  (fresh [x y]
    (!= [1 x] [y 2])  ; "NOT (x=2 AND y=1)"
    (== x 2)
    (== q [x y])))
;; => ([2 _0])  ; y can be anything except 1 when x is 2
```

**CLP(FD) - Finite Domain Constraints:**
```clojure
(require '[clojure.core.logic :refer [run* fresh ==]]
         '[clojure.core.logic.fd :as fd])

;; Declare finite domains
(run* [q]
  (fd/in q (fd/interval 1 5)))
;; => (1 2 3 4 5)

;; Arithmetic constraints
(run* [q]
  (fresh [x y]
    (fd/in x y (fd/interval 1 10))
    (fd/+ x y 10)
    (== q [x y])))
;; => ([1 9] [2 8] [3 7] [4 6] [5 5] [6 4] [7 3] [8 2] [9 1])

;; distinct ensures all variables take different values
(run* [q]
  (fresh [x y]
    (fd/in x y (fd/interval 1 10))
    (fd/+ x y 10)
    (fd/distinct [x y])
    (== q [x y])))
;; => ([1 9] [2 8] [3 7] [4 6] [6 4] [7 3] [8 2] [9 1])
;; Note: [5 5] excluded by distinct
```

### defne and Pattern Matching

`defne` defines relations with pattern matching on arguments:

```clojure
(require '[clojure.core.logic :refer [run* defne conde]])

(defne moveo [before action after]
  ([[:middle :onbox :middle :hasnot]
    :grasp
    [:middle :onbox :middle :has]])
  
  ([[pos :onfloor pos has]
    :climb
    [pos :onbox pos has]])
  
  ([[pos1 :onfloor pos1 has]
    :push
    [pos2 :onfloor pos2 has]])
  
  ([[pos1 :onfloor box has]
    :walk
    [pos2 :onfloor box has]]))

;; Query valid moves
(run* [q]
  (moveo [:middle :onbox :middle :hasnot] :grasp q))
;; => ([:middle :onbox :middle :has])
```

## Common Workflows

### Workflow 1: Solving Logic Puzzles

Solve constraint satisfaction problems like Sudoku:

```clojure
(require '[clojure.core.logic :refer [run* fresh == everyg]]
         '[clojure.core.logic.fd :as fd])

(defn get-square [rows x y]
  (for [x (range x (+ x 3))
        y (range y (+ y 3))]
    (get-in rows [x y])))

(defn sudoku [hints]
  (let [vars (repeatedly 81 lvar)
        rows (->> vars (partition 9) (map vec) (into []))
        cols (apply map vector rows)
        sqs  (for [x (range 0 9 3)
                   y (range 0 9 3)]
               (get-square rows x y))]
    (run 1 [q]
      (== q vars)
      ;; All cells are digits 1-9
      (everyg #(fd/in % (fd/domain 1 2 3 4 5 6 7 8 9)) vars)
      ;; Bind hints
      (everyg (fn [[var hint]]
                (if (zero? hint)
                  succeed
                  (== var hint)))
              (map vector vars hints))
      ;; All rows, columns, and squares distinct
      (everyg fd/distinct rows)
      (everyg fd/distinct cols)
      (everyg fd/distinct sqs))))

(def puzzle
  [2 0 7 0 1 0 5 0 8
   0 0 0 6 7 8 0 0 0
   8 0 0 0 0 0 0 0 6
   0 7 0 9 0 6 0 5 0
   4 9 0 0 0 0 0 1 3
   0 3 0 4 0 1 0 2 0
   5 0 0 0 0 0 0 0 1
   0 0 0 2 9 4 0 0 0
   3 0 6 0 8 0 4 0 9])

(sudoku puzzle)
;; => ((2 6 7 3 1 9 5 4 8
;;      9 5 4 6 7 8 1 3 2
;;      ...))
```

### Workflow 2: Finite Domain Equations

Use `fd/eq` macro for complex arithmetic constraints:

```clojure
(require '[clojure.core.logic :refer [run* fresh ==]]
         '[clojure.core.logic.fd :as fd])

;; Solve system of equations
(run* [q]
  (fresh [x y]
    (fd/in x y (fd/interval 0 9))
    (fd/eq
      (= (+ x y) 9)
      (= (+ (* x 2) (* y 4)) 24))
    (== q [x y])))
;; => ([6 3])

;; fd/eq creates intermediate vars and operators automatically
(run* [q]
  (fresh [a b c]
    (fd/in a b c (fd/interval 1 10))
    (fd/eq
      (= (+ a b c) 15)
      (= (* a b) c))
    (== q [a b c])))
;; => ([3 4 12] [4 3 12] [5 2 10] [2 5 10])
```

### Workflow 3: In-Memory Database Queries

Use `pldb` (Prolog-like database) for relational queries:

```clojure
(require '[clojure.core.logic :refer [run* fresh ==]]
         '[clojure.core.logic.pldb :as pldb])

;; Define relations
(pldb/db-rel man p)
(pldb/db-rel woman p)
(pldb/db-rel likes p1 p2)
(pldb/db-rel fun p)

;; Create database of facts
(def facts
  (pldb/db
   [man 'Bob]
   [man 'John]
   [woman 'Mary]
   [woman 'Lucy]
   [likes 'Bob 'Mary]
   [likes 'John 'Lucy]
   [fun 'Lucy]))

;; Query the database
(pldb/with-db facts
  (run* [q]
    (fresh [x y]
      (fun y)
      (likes x y)
      (== q [x y]))))
;; => ([John Lucy])

;; Add indexes for performance
(pldb/db-rel likes ^:index p1 ^:index p2)
```

### Workflow 4: Recursive Relations with Tabling

Use tabling to ensure termination for recursive relations:

```clojure
(require '[clojure.core.logic :refer [run* fresh defne conde tabled]])

;; Define graph edges
(defne arco [x y]
  ([:a :b])
  ([:b :a])
  ([:b :d]))

;; Without tabling, path search might not terminate
;; With tabling, it will terminate
(def patho
  (tabled [x y]
    (conde
     [(arco x y)]
     [(fresh [z]
        (arco x z)
        (patho z y))])))

;; Find all paths from :a
(run* [q]
  (patho :a q))
;; => (:b :a :d)
```

### Workflow 5: Nominal Logic for Binding and Scope

Use nominal logic programming for reasoning about variable binding:

```clojure
(require '[clojure.core.logic :refer [run* fresh == conde]]
         '[clojure.core.logic.nominal :as nom])

;; Substitution without variable capture
(defn substo [e new a out]
  (conde
    [(== ['var a] e) (== new out)]
    
    [(fresh [y]
       (== ['var y] e)
       (== ['var y] out)
       (nom/hash a y))]
    
    [(fresh [rator rand rator-res rand-res]
       (== ['app rator rand] e)
       (== ['app rator-res rand-res] out)
       (substo rator new a rator-res)
       (substo rand new a rand-res))]
    
    [(fresh [body body-res]
       (nom/fresh [c]
         (== ['lam (nom/tie c body)] e)
         (== ['lam (nom/tie c body-res)] out)
         (nom/hash c a)
         (nom/hash c new)
         (substo body new a body-res)))]))

;; Substitute b for a in lambda expression
(run* [q]
  (nom/fresh [a b]
    (substo ['lam (nom/tie a ['app ['var a] ['var b]])]
            ['var b]
            a
            q)))
;; => ([lam (nom/tie a_0 (app (var a_0) (var a_1)))])
```

### Workflow 6: Type Inference

Build a simple type inferencer:

```clojure
(require '[clojure.core.logic :refer [run* fresh == matche conde lvaro]]
         '[clojure.core.logic.pldb :as pldb])

(defn findo [x l o]
  (conde
    [(fresh [[y _ o-val] tail]
       (== [[y :- o-val] . tail] l)
       (== x y)
       (== o o-val))]
    [(fresh [head tail]
       (== [head . tail] l)
       (findo x tail o))]))

(defn typedo [context expr type]
  (conde
    ;; Variable lookup
    [(lvaro expr)
     (findo expr context type)]
    
    ;; Lambda abstraction
    [(fresh [arg body arg-type body-type]
       (== [arg :>> body] expr)
       (== [arg-type :> body-type] type)
       (fresh [new-context]
         (== [[arg :- arg-type] . context] new-context)
         (typedo new-context body body-type)))]
    
    ;; Application
    [(fresh [fn arg fn-type]
       (== [:apply fn arg] expr)
       (fresh [arg-type]
         (== [arg-type :> type] fn-type)
         (typedo context fn fn-type)
         (typedo context arg arg-type)))]))

;; Infer types
(run* [q]
  (fresh [f g a b t]
    (typedo [[f :- a] [g :- b]]
            [:apply f g]
            t)
    (== q a)))
;; => ([_0 :> _1])
```

### Workflow 7: Pattern Matching with defne

Define relations using pattern matching syntax:

```clojure
(require '[clojure.core.logic :refer [run* defne]])

(defne appendo [l1 l2 out]
  ([() _ out]
     (== l2 out))
  ([[head . tail] _ [head . rest]]
     (appendo tail l2 rest)))

(run* [q]
  (appendo [1 2] [3 4] q))
;; => ([1 2 3 4])

(run* [q]
  (appendo q [3 4] [1 2 3 4]))
;; => ([1 2])

(run* [q]
  (fresh [x y]
    (appendo x y [1 2 3 4])
    (== q [x y])))
;; => ([() [1 2 3 4]]
;;     [[1] [2 3 4]]
;;     [[1 2] [3 4]]
;;     [[1 2 3] [4]]
;;     [[1 2 3 4] ()])
```

## When to Use Each Approach

**Use run* when:**
- You want all solutions
- Solution space is known to be finite

**Use run N when:**
- You want a specific number of solutions
- Solution space might be infinite
- Example: `(run 5 [q] ...)`

**Use conde when:**
- Creating logical disjunction (OR)
- Multiple alternative paths to solutions

**Use fresh when:**
- Introducing new logic variables
- Need local scope for variables

**Use defne when:**
- Defining relations with pattern matching
- Complex multi-clause relations
- Cleaner syntax than nested conde

**Use CLP(FD) when:**
- Solving constraint satisfaction problems
- Working with integer arithmetic
- Need finite domain constraints

**Use tabling when:**
- Recursive relations might not terminate
- Need memoization of subgoals

**Use nominal logic when:**
- Reasoning about variable binding
- Implementing interpreters or compilers
- Need to handle variable capture correctly

## Best Practices

**DO:**
- Exclude `clojure.core/==` when using core.logic
- Use `fresh` to introduce logic variables
- Use `fd/in` to declare finite domains before arithmetic
- Use indexes with `pldb` relations for better performance
- Use tabling for recursive relations
- Think declaratively about relationships, not procedures
- Test with `run*` first, then limit with `run N` if needed

**DON'T:**
- Mix core.logic's `==` with `clojure.core/==` without exclusion
- Forget to declare domains for CLP(FD) variables
- Use CLP(FD) operators on unbounded domains
- Create deeply recursive relations without tabling
- Overuse `project` (indicates non-relational thinking)
- Expect Prolog semantics exactly (core.logic differs in search strategy)

## Common Issues

### Issue: "Unable to resolve symbol: =="

**Problem:** Conflict between `clojure.core/==` and `core.logic/==`

```clojure
;; Wrong: ambiguous ==
(ns my-app
  (:require [clojure.core.logic :refer [run* fresh ==]]))

(run* [q]
  (== q 1))  ; Which == is this?
```

**Solution:** Exclude `clojure.core/==`

```clojure
;; Correct: exclude core's ==
(ns my-app
  (:refer-clojure :exclude [==])
  (:require [clojure.core.logic :refer [run* fresh ==]]))

(run* [q]
  (== q 1))  ; Now unambiguous
;; => (1)
```

### Issue: CLP(FD) operators fail with "no domain"

**Problem:** Using FD operators without declaring domains

```clojure
(require '[clojure.core.logic :refer [run* fresh]]
         '[clojure.core.logic.fd :as fd])

(run* [q]
  (fresh [x y]
    (fd/+ x y 10)  ; Error: x and y have no domains
    (== q [x y])))
```

**Solution:** Declare domains with `fd/in`

```clojure
(run* [q]
  (fresh [x y]
    (fd/in x y (fd/interval 1 10))  ; Declare domains first
    (fd/+ x y 10)
    (== q [x y])))
;; => ([1 9] [2 8] [3 7] [4 6] [5 5] [6 4] [7 3] [8 2] [9 1])
```

### Issue: Infinite recursion with path search

**Problem:** Recursive relation doesn't terminate

```clojure
(defne arco [x y]
  ([:a :b])
  ([:b :a]))

(defn patho [x y]
  (conde
   [(arco x y)]
   [(fresh [z]
      (arco x z)
      (patho z y))]))

(run* [q]
  (patho :a q))  ; Infinite loop!
```

**Solution:** Use tabling

```clojure
(def patho
  (tabled [x y]
    (conde
     [(arco x y)]
     [(fresh [z]
        (arco x z)
        (patho z y))])))

(run* [q]
  (patho :a q))
;; => (:b :a)  ; Terminates!
```

### Issue: Pattern matching with defne doesn't work

**Problem:** Incorrect defne syntax

```clojure
(defne membero [x l]
  ([x [x . _]])      ; Wrong: can't repeat variable
  ([x [_ . tail]]
     (membero x tail)))
```

**Solution:** Use fresh for pattern variables

```clojure
(defne membero [x l]
  ([_ [x . _]])      ; Use _ for ignored positions
  ([_ [head . tail]]
     (membero x tail)))

;; Or use explicit fresh
(defne membero [x l]
  ([_ l]
     (fresh [head tail]
       (== l [head . tail])
       (== x head)))
  ([_ l]
     (fresh [head tail]
       (== l [head . tail])
       (membero x tail))))
```

## Advanced Topics

### Custom Constraint Domains

Extend core.logic with custom constraint domains. See the [Extending core.logic wiki](https://github.com/clojure/core.logic/wiki/Extending-core.logic-(Datomic-example)) for details.

### Definite Clause Grammars

core.logic supports DCG syntax for parsing (experimental):

```clojure
(require '[clojure.core.logic.dcg :refer [def-->e]])

(def-->e noun [n]
  ([[:n 'bat]] '[bat])
  ([[:n 'cat]] '[cat]))

(def-->e verb [v]
  ([[:v 'eats]] '[eats]))

(run* [parse-tree]
  (sentence parse-tree '[the bat eats a cat] []))
```

### Search Customization

Customize search strategy and instrumentation. See [Search customization wiki](https://github.com/clojure/core.logic/wiki/Search-customization-&-instrumentation).

## Resources

- [GitHub Repository](https://github.com/clojure/core.logic)
- [Wiki Documentation](https://github.com/clojure/core.logic/wiki)
- [Core.logic Primer](https://github.com/clojure/core.logic/wiki/A-Core.logic-Primer)
- [Differences from The Reasoned Schemer](https://github.com/clojure/core.logic/wiki/Differences-from-The-Reasoned-Schemer)
- [The Reasoned Schemer (book)](https://mitpress.mit.edu/books/reasoned-schemer-second-edition)
- [miniKanren website](http://minikanren.org/)
- [William Byrd's dissertation](https://www.proquest.com/docview/304903505/E30282E6EF13453CPQ/1)

## Summary

core.logic brings logic programming to Clojure:

1. **Relational programming** - Declare relationships, not procedures
2. **Unification** - Pattern matching and variable binding with `==`
3. **Constraint solving** - CLP(FD) for finite domains, CLP(Tree) for disequality
4. **Pattern matching** - `defne` for clean multi-clause relations
5. **Tabling** - Ensures termination for recursive relations
6. **Nominal logic** - Reasoning about binding and scope
7. **In-memory DB** - Prolog-like database with `pldb`

Think declaratively about what relationships hold rather than how to compute answers. Use constraints to prune search spaces and tabling to ensure termination.
