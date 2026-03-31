---
name: datascript
description: |
  Immutable in-memory database with Datalog queries for Clojure and ClojureScript. 
  Use when building client-side applications that need to track state, run complex 
  queries over data, or need time-travel debugging. Ideal for SPAs, UI state management, 
  local-first apps, or when the user mentions Datalog, EAV/triple store, entity queries, 
  or in-memory database.
---

# DataScript

## Quick Start

DataScript is an immutable in-memory database using the Entity-Attribute-Value (EAV) model with Datalog queries. It's designed to run in the browser and be as cheap to create as a HashMap.

```clojure
(require '[datascript.core :as d])

;; Create a database connection
(def conn (d/create-conn))

;; Add data
(d/transact! conn [{:name "Alice" :age 30 :email "alice@example.com"}
                   {:name "Bob" :age 25 :email "bob@example.com"}])

;; Query with Datalog
(d/q '[:find ?name ?age
       :where [?e :name ?name]
              [?e :age ?age]
              [(> ?age 26)]]
     @conn)
;; => #{["Alice" 30]}

;; Access the current database value
@conn  ; Immutable database snapshot
```

## Core Concepts

### Database as a Value

Each database is an immutable value. New databases are created on top of old ones, but old ones remain valid:

```clojure
(def db-before @conn)
(d/transact! conn [{:name "Charlie" :age 35}])
(def db-after @conn)

;; Both are valid, independent snapshots
(d/q '[:find ?name :where [?e :name ?name]] db-before)
;; => #{["Alice"] ["Bob"]}

(d/q '[:find ?name :where [?e :name ?name]] db-after)
;; => #{["Alice"] ["Bob"] ["Charlie"]}
```

### Entity-Attribute-Value (EAV) Model

DataScript stores data as facts (datoms) with structure `[entity-id attribute value transaction-id]`:

```clojure
;; This map:
{:name "Alice" :age 30}

;; Becomes datoms like:
[1 :name "Alice" 536870913]
[1 :age 30 536870913]
```

### Schema (Optional but Powerful)

Schema defines attribute properties:

```clojure
(def schema
  {:user/id      {:db/unique :db.unique/identity}
   :user/email   {:db/unique :db.unique/identity}
   :user/friends {:db/cardinality :db.cardinality/many
                  :db/valueType :db.type/ref}})

(def conn (d/create-conn schema))
```

**Schema attributes:**
- `:db/cardinality` - `:db.cardinality/one` (default) or `:db.cardinality/many`
- `:db/valueType` - `:db.type/ref` for references to other entities
- `:db/unique` - `:db.unique/identity` or `:db.unique/value`

## Common Workflows

### Workflow 1: Basic Data Operations

```clojure
(require '[datascript.core :as d])

;; Create database
(def conn (d/create-conn))

;; Add entities (returns transaction report)
(def tx-report
  (d/transact! conn [{:db/id -1
                      :name "Alice"
                      :age 30}
                     {:db/id -2
                      :name "Bob"
                      :age 25}]))

;; Temporary IDs (-1, -2) get resolved to permanent entity IDs
(:tempids tx-report)  ; {-1 1, -2 2}

;; Update entity (upsert by entity ID)
(d/transact! conn [{:db/id 1
                    :age 31}])

;; Retract attribute value
(d/transact! conn [[:db/retract 1 :age 31]])

;; Retract entire entity
(d/transact! conn [[:db.fn/retractEntity 1]])
```

### Workflow 2: Datalog Queries

```clojure
;; Basic pattern matching
(d/q '[:find ?name ?age
       :where [?e :name ?name]
              [?e :age ?age]]
     @conn)
;; => #{["Alice" 30] ["Bob" 25]}

;; Filtering with predicates
(d/q '[:find ?name
       :where [?e :name ?name]
              [?e :age ?age]
              [(>= ?age 30)]]
     @conn)
;; => #{["Alice"]}

;; Parameterized queries with :in
(d/q '[:find ?name
       :in $ ?min-age
       :where [?e :name ?name]
              [?e :age ?age]
              [(>= ?age ?min-age)]]
     @conn
     30)
;; => #{["Alice"]}

;; Return single tuple instead of set
(d/q '[:find [?name ?age]
       :where [?e :name ?name]
              [?e :age ?age]
              [(= ?name "Alice")]]
     @conn)
;; => ["Alice" 30]

;; Return maps instead of tuples
(d/q '[:find ?name ?age
       :keys name age
       :where [?e :name ?name]
              [?e :age ?age]]
     @conn)
;; => #{{:name "Alice" :age 30} {:name "Bob" :age 25}}
```

### Workflow 3: References and Joins

```clojure
;; Schema with references
(def schema
  {:person/friends {:db/cardinality :db.cardinality/many
                    :db/valueType :db.type/ref}})

(def conn (d/create-conn schema))

;; Add entities with references
(d/transact! conn
  [{:db/id -1 :name "Alice"}
   {:db/id -2 :name "Bob"}
   {:db/id -3 
    :name "Charlie"
    :person/friends [-1 -2]}])  ; References to Alice and Bob

;; Query with implicit joins
(d/q '[:find ?person-name ?friend-name
       :where [?p :name ?person-name]
              [?p :person/friends ?f]
              [?f :name ?friend-name]]
     @conn)
;; => #{["Charlie" "Alice"] ["Charlie" "Bob"]}
```

### Workflow 4: Entity API

The entity API provides a lazy, map-like view of entities:

```clojure
;; Get entity by ID
(def alice-eid 1)
(def alice (d/entity @conn alice-eid))

;; Access attributes like a map
(:name alice)      ;; => "Alice"
(:age alice)       ;; => 30
(get alice :name)  ;; => "Alice"

;; Get entity ID
(:db/id alice)     ;; => 1

;; References are auto-resolved
(def charlie (d/entity @conn 3))
(:person/friends charlie)
;; => #{#datascript/Entity{...} #datascript/Entity{...}}

(map :name (:person/friends charlie))
;; => ("Alice" "Bob")

;; Touch to realize all attributes
(d/touch alice)
;; => {:db/id 1 :name "Alice" :age 30}
```

### Workflow 5: Pull API

Pull API provides hierarchical data extraction:

```clojure
;; Pull specific attributes
(d/pull @conn [:name :age] 1)
;; => {:name "Alice" :age 30}

;; Pull all attributes
(d/pull @conn '[*] 1)
;; => {:db/id 1 :name "Alice" :age 30}

;; Pull with references (recursive)
(d/pull @conn
        '[:name {:person/friends [:name :age]}]
        3)
;; => {:name "Charlie"
;;     :person/friends [{:name "Alice" :age 30}
;;                      {:name "Bob" :age 25}]}

;; Pull multiple entities
(d/pull-many @conn [:name :age] [1 2 3])
;; => [{:name "Alice" :age 30}
;;     {:name "Bob" :age 25}
;;     {:name "Charlie"}]
```

### Workflow 6: Listening to Changes

```clojure
;; Listen for transactions
(def listener-key
  (d/listen! conn :log
    (fn [tx-report]
      (println "Transaction:" (:tx-data tx-report)))))

;; Make a change
(d/transact! conn [{:name "Dave" :age 40}])
;; Prints: Transaction: [[4 :name "Dave" 536870914 true]
;;                       [4 :age 40 536870914 true]]

;; Stop listening
(d/unlisten! conn listener-key)
```

### Workflow 7: Index Access

Direct index access for performance-critical operations:

```clojure
;; Get all datoms for an attribute (AEVT index)
(d/datoms @conn :aevt :age)
;; => [#datascript/Datom [2 :age 25 536870913]
;;     #datascript/Datom [1 :age 30 536870913]]

;; Seek to specific position in index
(d/seek-datoms @conn :aevt :age 28)
;; => datoms where age >= 28

;; Get all datoms for an entity (EAVT index)
(d/datoms @conn :eavt 1)
;; => all datoms for entity 1
```

## When to Use Each Approach

**Use DataScript when:**
- Building client-side SPAs that need complex state management
- You need time-travel debugging (keep old DB snapshots)
- Multiple components need to query the same data differently
- Building local-first applications
- You want to use the same data model client and server-side
- Complex data relationships that benefit from graph queries

**Use Datalog queries when:**
- Relationships span multiple entities (joins)
- You need recursive queries (rules)
- Complex filtering or aggregations
- You want declarative data access

**Use Entity API when:**
- Navigating relationships from a known entity
- You want lazy, on-demand attribute access
- Building UI components that render entities

**Use Pull API when:**
- You need specific shape of data (like GraphQL)
- Building APIs that return nested data
- You want to avoid over-fetching

**Use direct index access when:**
- Performance is critical
- You need range scans
- Working with large result sets

**Don't use DataScript when:**
- Simple key-value storage is sufficient (use atoms/maps)
- Data is purely hierarchical with no cross-references
- Performance overhead isn't justified (DataScript has indexing cost)
- You need persistence (use with storage library or regular DB)

## Best Practices

**Do:**
- Define schema for multi-valued attributes and references
- Use unique identity attributes for entities you'll update
- Keep connections in atoms for application state
- Use query parameters instead of building queries dynamically
- Leverage immutability - keep old DB snapshots for undo/redo
- Use Pull API for fetching hierarchical data
- Test queries in REPL before using in code
- Use temporary IDs (negative integers) for new entities

**Don't:**
- Store large binary data in DataScript (store URLs/paths instead)
- Create new connections frequently (they're meant to be long-lived)
- Forget that references need `:db/valueType :db.type/ref` in schema
- Query in tight loops - cache query results when possible
- Modify entities directly - always use transactions
- Use DataScript as durable storage without persistence layer

## Common Issues

### References Not Working

```clojure
;; Wrong: no schema for reference
(def conn (d/create-conn))
(d/transact! conn [{:db/id -1 :name "Alice"}
                   {:db/id -2 :name "Bob" :friends [-1]}])

;; :friends stores -1 as a number, not a reference!

;; Right: declare reference in schema
(def schema {:friends {:db/valueType :db.type/ref
                       :db/cardinality :db.cardinality/many}})
(def conn (d/create-conn schema))
(d/transact! conn [{:db/id -1 :name "Alice"}
                   {:db/id -2 :name "Bob" :friends [-1]}])
```

### Multi-valued Attributes Not Working

```clojure
;; Wrong: default cardinality is :db.cardinality/one
(d/transact! conn [{:name "Alice" :tags ["clojure" "datascript"]}])
;; :tags stores the vector, not multiple values

;; Right: declare many-cardinality
(def schema {:tags {:db/cardinality :db.cardinality/many}})
(def conn (d/create-conn schema))
(d/transact! conn [{:name "Alice" :tags ["clojure" "datascript"]}])
```

### Upsert Not Working

```clojure
;; Wrong: no unique attribute
(d/transact! conn [{:email "alice@example.com" :age 30}])
(d/transact! conn [{:email "alice@example.com" :age 31}])
;; Creates two separate entities!

;; Right: make email unique
(def schema {:email {:db/unique :db.unique/identity}})
(def conn (d/create-conn schema))
(d/transact! conn [{:email "alice@example.com" :age 30}])
(d/transact! conn [{:email "alice@example.com" :age 31}])
;; Updates the same entity
```

### Query Returns Empty Results

```clojure
;; Common issue: typo in attribute name
(d/q '[:find ?name
       :where [?e :name ?name]]
     @conn)
;; => #{}  (empty because you used :name instead of :user/name)

;; Debug: check what attributes exist
(d/q '[:find ?attr
       :where [_ ?attr]]
     @conn)
;; => #{[:user/name] [:user/age] ...}
```

## Advanced Topics

### Rules for Recursive Queries

```clojure
;; Define rules for transitive relationships
(def rules
  '[[(ancestor ?a ?d)
     [?a :parent ?d]]
    [(ancestor ?a ?d)
     [?a :parent ?p]
     (ancestor ?p ?d)]])

(d/q '[:find ?ancestor ?descendant
       :in $ %
       :where (ancestor ?ancestor ?descendant)]
     @conn
     rules)
```

### Aggregation

```clojure
;; Count entities
(d/q '[:find (count ?e)
       :where [?e :name]]
     @conn)

;; Average age
(d/q '[:find (avg ?age)
       :where [_ :age ?age]]
     @conn)

;; Group by with aggregation
(d/q '[:find ?category (count ?item)
       :where [?item :category ?category]]
     @conn)
```

### Transaction Functions

```clojure
;; Custom transaction function
(defn increment-age [db eid amount]
  (let [current-age (:age (d/entity db eid))]
    [[:db/add eid :age (+ current-age amount)]]))

;; Use in transaction
(d/transact! conn [[:db.fn/call increment-age 1 5]])
```

### Time-Travel / History

```clojure
;; Save snapshots
(def db-v1 @conn)
(d/transact! conn [{:name "New User"}])
(def db-v2 @conn)

;; Query any version
(d/q query db-v1)  ; Old version
(d/q query db-v2)  ; New version

;; Build undo/redo
(def history (atom [@conn]))
(d/listen! conn (fn [_] (swap! history conj @conn)))
```

## External Resources

- [Official GitHub](https://github.com/tonsky/datascript)
- [Learn Datalog Today](http://www.learndatalogtoday.org) - Interactive Datalog tutorial
- [Datomic Query Reference](https://docs.datomic.com/query/query-data-reference.html) - Most concepts apply to DataScript
- [DataScript Internals](http://tonsky.me/blog/datascript-internals/) - How it works under the hood

## Summary

DataScript is an immutable in-memory database perfect for client-side state management:

1. **Database as value** - Immutable snapshots enable time-travel and undo
2. **Datalog queries** - Powerful declarative queries with joins and recursion
3. **Flexible access** - Query, Entity, Pull, and Index APIs for different needs
4. **Schema optional** - Start simple, add constraints as needed
5. **Lightweight** - No server, no setup, just create and use

Think of DataScript as "HashMap with superpowers" - cheap to create, queryable, and perfect for managing complex application state.
# DataScript API Reference

## Database Creation and Management

### `create-conn`

```clojure
(d/create-conn)
(d/create-conn schema)
```

Creates a new database connection (atom) with optional schema.

**Parameters:**
- `schema` (optional) - Map of attribute definitions

**Returns:** Atom containing the database

**Example:**
```clojure
(def conn (d/create-conn))

(def conn (d/create-conn 
  {:user/email {:db/unique :db.unique/identity}
   :user/friends {:db/cardinality :db.cardinality/many
                  :db/valueType :db.type/ref}}))
```

### `empty-db`

```clojure
(d/empty-db)
(d/empty-db schema)
```

Creates an empty database value (not a connection).

**Returns:** Database value

### `conn-from-db`

```clojure
(d/conn-from-db db)
```

Creates a connection from a database value.

### `conn-from-datoms`

```clojure
(d/conn-from-datoms datoms schema)
```

Creates a connection from a sequence of datoms.

## Schema Attributes

### `:db/cardinality`

Controls whether an attribute can have multiple values:

- `:db.cardinality/one` (default) - Single value per entity
- `:db.cardinality/many` - Multiple values per entity

```clojure
{:user/email {:db/cardinality :db.cardinality/one}
 :user/tags  {:db/cardinality :db.cardinality/many}}
```

### `:db/valueType`

Specifies the type of value:

- `:db.type/ref` - Reference to another entity
- `:db.type/string` - String (informational only)
- `:db.type/boolean` - Boolean (informational only)
- `:db.type/long` - Long integer (informational only)
- `:db.type/bigint` - Big integer (informational only)
- `:db.type/float` - Float (informational only)
- `:db.type/double` - Double (informational only)
- `:db.type/bigdec` - Big decimal (informational only)
- `:db.type/instant` - Instant/Date (informational only)
- `:db.type/uuid` - UUID (informational only)

Only `:db.type/ref` has behavioral implications. Others are for documentation.

### `:db/unique`

Enforces uniqueness constraints:

- `:db.unique/identity` - Unique value, enables upsert
- `:db.unique/value` - Unique value, no upsert

```clojure
{:user/email {:db/unique :db.unique/identity}
 :user/username {:db/unique :db.unique/value}}
```

### `:db/isComponent`

```clojure
{:order/items {:db/valueType :db.type/ref
               :db/cardinality :db.cardinality/many
               :db/isComponent true}}
```

When `true`, the referenced entities are considered sub-components. Retracting the parent entity also retracts all component entities.

### `:db/index`

```clojure
{:user/email {:db/index true}}
```

When `true`, creates an AVET index for this attribute (enabled by default for `:db/unique` attributes).

## Transactions

### `transact!`

```clojure
(d/transact! conn tx-data)
```

Applies transaction data to the database.

**Parameters:**
- `conn` - Database connection (atom)
- `tx-data` - Vector of transaction operations

**Returns:** Transaction report map with keys:
- `:db-before` - Database value before transaction
- `:db-after` - Database value after transaction
- `:tx-data` - Vector of datoms added/retracted
- `:tempids` - Map of temp IDs to permanent IDs
- `:tx-meta` - Transaction metadata (if provided)

**Transaction operations:**

```clojure
;; Add entity as map
{:db/id -1 :name "Alice" :age 30}

;; Add entity with explicit ID
{:db/id 1 :age 31}

;; Add datom
[:db/add entity-id :attribute value]

;; Retract datom
[:db/retract entity-id :attribute value]

;; Retract entire entity
[:db.fn/retractEntity entity-id]

;; Retract all values of an attribute
[:db.fn/retractAttribute entity-id :attribute]

;; Call transaction function
[:db.fn/call function arg1 arg2 ...]
```

**Example:**
```clojure
(d/transact! conn 
  [{:db/id -1 :name "Alice" :age 30}
   {:db/id -2 :name "Bob" :age 25}
   [:db/add -1 :friend -2]])
```

### `with`

```clojure
(d/with db tx-data)
```

Like `transact!` but doesn't modify the connection. Returns same transaction report.

**Example:**
```clojure
(let [report (d/with @conn [{:name "Test"}])]
  (:db-after report))  ; New DB value, original unchanged
```

### `db-with`

```clojure
(d/db-with db tx-data)
```

Returns just the new database value (shortcut for `(:db-after (d/with db tx-data))`).

## Queries

### `q`

```clojure
(d/q query & inputs)
```

Executes a Datalog query.

**Query structure:**
```clojure
[:find ?var1 ?var2 ...
 :in $ ?param1 ?param2 ...  ; optional
 :where clause1 clause2 ...]
```

**Find specifications:**

```clojure
;; Return set of tuples (default)
[:find ?name ?age ...]

;; Return single tuple
[:find [?name ?age]]

;; Return single scalar value
[:find ?name .]

;; Return collection of single values
[:find [?name ...]]

;; Return maps instead of tuples
[:find ?name ?age
 :keys name age
 ...]
```

**Where clauses:**

```clojure
;; Pattern matching
[?e :attribute ?value]

;; Predicates
[(< ?age 30)]
[(= ?name "Alice")]

;; Function calls
[(+ ?x ?y) ?sum]
[(str ?first " " ?last) ?full-name]

;; Expression predicates
[(< ?age 30)]
[(contains? #{:a :b :c} ?tag)]

;; Bind constant
[(ground 42) ?answer]

;; Get components from tuple
[(tuple ?a ?b ?c) ?tup]
[(untuple ?tup) [?x ?y ?z]]

;; Unification
[?e1 :friend ?e2]
[?e2 :name ?name]
```

**Rules:**

```clojure
(def rules
  '[[(ancestor ?a ?d)
     [?a :parent ?d]]
    [(ancestor ?a ?d)
     [?a :parent ?p]
     (ancestor ?p ?d)]])

(d/q '[:find ?a ?d
       :in $ %
       :where (ancestor ?a ?d)]
     db
     rules)
```

**Aggregates:**

```clojure
;; Count
[:find (count ?e) :where [?e :name]]

;; Sum
[:find (sum ?age) :where [?e :age ?age]]

;; Min/max
[:find (min ?age) (max ?age) :where [?e :age ?age]]

;; Average
[:find (avg ?age) :where [?e :age ?age]]

;; Distinct
[:find (distinct ?tag) :where [?e :tags ?tag]]

;; Sample (first n)
[:find (sample 5 ?e) :where [?e :name]]

;; Median
[:find (median ?age) :where [?e :age ?age]]

;; Variance/stddev
[:find (variance ?age) :where [?e :age ?age]]
[:find (stddev ?age) :where [?e :age ?age]]

;; Random sample
[:find (rand ?e) :where [?e :name]]
```

**Negation:**

```clojure
;; not - negation
[:find ?e
 :where [?e :name]
        (not [?e :age])]

;; not-join - negation with variables
[:find ?e1
 :where [?e1 :name ?n1]
        (not-join [?e1]
          [?e1 :age ?a]
          [(< ?a 18)])]
```

**Disjunction:**

```clojure
[:find ?e
 :where (or [?e :status :active]
            [?e :status :pending])]

;; With variables
[:find ?e ?attr
 :where (or-join [?e ?attr]
          (and [?e :email ?attr]
               [(re-matches #".+@.+" ?attr)])
          [?e :phone ?attr])]
```

### Entity API

### `entity`

```clojure
(d/entity db eid)
```

Returns a lazy map-like entity for the given entity ID.

**Example:**
```clojure
(def alice (d/entity @conn 1))
(:name alice)        ;; => "Alice"
(:age alice)         ;; => 30
(:db/id alice)       ;; => 1

;; References auto-resolve
(:user/friends alice)  ;; => #{Entity{...} Entity{...}}
```

### `entity-db`

```clojure
(d/entity-db entity)
```

Returns the database that the entity came from.

### `touch`

```clojure
(d/touch entity)
```

Realizes all attributes of an entity into a map.

**Example:**
```clojure
(d/touch (d/entity @conn 1))
;; => {:db/id 1 :name "Alice" :age 30 :email "alice@example.com"}
```

## Pull API

### `pull`

```clojure
(d/pull db pattern eid)
```

Pulls data for a single entity according to a pattern.

**Pattern elements:**

```clojure
;; Specific attributes
[:name :age :email]

;; All attributes
'[*]

;; All attributes plus :db/id
'[* :db/id]

;; Attribute with default
[(:name :default "Unknown")]

;; Limit (for multi-valued attrs)
[(:tags :limit 3)]

;; As (rename attribute)
[(:name :as "Full Name")]

;; References (recursive)
[:name {:user/friends [:name :age]}]

;; Recursive limit
[:name {:user/friends ...}]  ; Unbounded recursion (careful!)
[:name {:user/friends 3}]     ; Max 3 levels

;; Wildcard in maps
[{:user/friends [*]}]

;; Reverse references (finds entities pointing to this one)
[:name :_user/friends]
```

**Example:**
```clojure
(d/pull @conn 
  '[:name :age {:user/friends [:name :email]}]
  1)
;; => {:name "Alice"
;;     :age 30
;;     :user/friends [{:name "Bob" :email "bob@example.com"}
;;                    {:name "Charlie" :email "charlie@example.com"}]}
```

### `pull-many`

```clojure
(d/pull-many db pattern eids)
```

Pulls data for multiple entities.

**Example:**
```clojure
(d/pull-many @conn [:name :age] [1 2 3])
;; => [{:name "Alice" :age 30}
;;     {:name "Bob" :age 25}
;;     {:name "Charlie" :age 35}]
```

## Index Access

### `datoms`

```clojure
(d/datoms db index & components)
```

Returns datoms from the specified index.

**Indexes:**
- `:eavt` - Entity-Attribute-Value-Transaction
- `:aevt` - Attribute-Entity-Value-Transaction
- `:avet` - Attribute-Value-Entity-Transaction (requires `:db/index true`)

**Example:**
```clojure
;; All datoms for an entity
(d/datoms @conn :eavt 1)

;; All datoms for an attribute
(d/datoms @conn :aevt :age)

;; All datoms for attribute with specific value
(d/datoms @conn :avet :age 30)

;; All datoms for entity and attribute
(d/datoms @conn :eavt 1 :name)
```

### `seek-datoms`

```clojure
(d/seek-datoms db index & components)
```

Returns datoms starting from the specified position in the index.

**Example:**
```clojure
;; All ages >= 28
(d/seek-datoms @conn :avet :age 28)

;; All entities with ID >= 5
(d/seek-datoms @conn :eavt 5)
```

### `index-range`

```clojure
(d/index-range db attr start end)
```

Returns datoms for attribute with values in range [start, end).

**Example:**
```clojure
;; Ages between 25 and 35 (exclusive)
(d/index-range @conn :age 25 35)
```

## Listeners

### `listen!`

```clojure
(d/listen! conn key callback)
```

Registers a transaction listener.

**Parameters:**
- `conn` - Database connection
- `key` - Unique identifier for this listener
- `callback` - Function receiving transaction report

**Example:**
```clojure
(d/listen! conn :logger
  (fn [tx-report]
    (println "Transaction:" (:tx-data tx-report))))
```

### `unlisten!`

```clojure
(d/unlisten! conn key)
```

Removes a transaction listener.

## Database Inspection

### `schema`

```clojure
(d/schema db)
```

Returns the schema map for the database.

### `datom`

```clojure
(d/datom e a v)
(d/datom e a v tx)
(d/datom e a v tx added)
```

Creates a datom.

### `datom-e`, `datom-a`, `datom-v`, `datom-tx`, `datom-added`

Accessor functions for datom components.

```clojure
(let [d (first (d/datoms @conn :eavt 1))]
  [(d/datom-e d)     ; Entity ID
   (d/datom-a d)     ; Attribute
   (d/datom-v d)     ; Value
   (d/datom-tx d)    ; Transaction ID
   (d/datom-added d)]) ; true if added, false if retracted
```

### `entid`

```clojure
(d/entid db eid-or-lookup-ref)
```

Resolves entity ID or lookup ref to entity ID.

**Example:**
```clojure
(d/entid @conn 1)                           ; => 1
(d/entid @conn [:user/email "alice@x.com"]) ; => 1 (if exists)
```

### `entid-strict`

```clojure
(d/entid-strict db eid-or-lookup-ref)
```

Like `entid` but throws if entity doesn't exist.

### `entid-some`

```clojure
(d/entid-some db eid-or-lookup-ref)
```

Like `entid` but returns `nil` if entity doesn't exist.

## Lookup References

Lookup refs are vectors of `[unique-attr value]` that can be used in place of entity IDs:

```clojure
;; Schema with unique attribute
(def schema {:user/email {:db/unique :db.unique/identity}})
(def conn (d/create-conn schema))

;; Add entity
(d/transact! conn [{:user/email "alice@example.com" :name "Alice"}])

;; Use lookup ref in query
(d/pull @conn [:name :age] [:user/email "alice@example.com"])
;; => {:name "Alice"}

;; Use in transaction
(d/transact! conn [{:db/id [:user/email "alice@example.com"]
                    :age 31}])
```

## Filtering Databases

### `filter`

```clojure
(d/filter db pred)
```

Returns a filtered view of the database where only datoms satisfying predicate are visible.

**Example:**
```clojure
;; Only show datoms for specific entity
(def filtered-db 
  (d/filter @conn 
    (fn [db datom]
      (= (:e datom) 1))))

(d/q '[:find ?a ?v :where [1 ?a ?v]] filtered-db)
```

### `is-filtered`

```clojure
(d/is-filtered db)
```

Returns `true` if database is filtered.

### `with-datom`

```clojure
(d/with-datom db datom)
```

Returns database with a single datom added (doesn't modify indices, for testing).

## Transaction Metadata

Attach metadata to transactions:

```clojure
(d/transact! conn 
  [{:name "Alice"}]
  {:user "admin" :timestamp (js/Date.)})

;; Access in listeners
(d/listen! conn :meta-logger
  (fn [tx-report]
    (println "Meta:" (:tx-meta tx-report))))
```

## Temporary IDs

Use negative integers for temporary entity IDs in transactions:

```clojure
(d/transact! conn
  [{:db/id -1 :name "Alice"}
   {:db/id -2 :name "Bob" :friend -1}])

;; Get permanent IDs from transaction report
(:tempids tx-report)  ; => {-1 1, -2 2}
```

## Special Transaction Attributes

### `:db.fn/retractEntity`

Retracts entire entity and (if `:db/isComponent true`) all component entities.

```clojure
[:db.fn/retractEntity entity-id]
```

### `:db.fn/retractAttribute`

Retracts all values of an attribute for an entity.

```clojure
[:db.fn/retractAttribute entity-id :attribute]
```

### `:db.fn/cas`

Compare-and-swap operation (conditional update).

```clojure
[:db.fn/cas entity-id :attribute old-value new-value]
```

Only updates if current value equals `old-value`.

## Error Handling

DataScript throws exceptions for:
- Schema violations (unique constraints, type mismatches)
- Invalid transaction data
- Malformed queries
- Non-existent entity IDs (in strict mode)

Wrap operations in try-catch:

```clojure
(try
  (d/transact! conn invalid-data)
  (catch js/Error e  ; or Exception in Clojure
    (println "Transaction failed:" (.-message e))))
```

## Performance Tips

1. **Index cardinality**: High-cardinality attributes benefit from `:db/index true`
2. **Query optimization**: Put most selective patterns first in `:where`
3. **Avoid `touch`**: Pull only needed attributes
4. **Batch transactions**: One transaction with many datoms beats many small transactions
5. **Cache query results**: Don't re-query in tight loops
6. **Use Pull API**: More efficient than multiple Entity API calls
7. **Index access**: `datoms` and `seek-datoms` are faster than queries for simple lookups

## ClojureScript Specifics

In ClojureScript, some query functions must be passed as source rather than symbols:

```clojure
;; Clojure: can reference by symbol
(d/q '[:find ?x :where [(my-fn ?x)]] db)

;; ClojureScript: must pass function source
(d/q '[:find ?x 
       :in $ ?my-fn
       :where [(?my-fn ?x)]] 
     db 
     my-fn)
```

For aggregates in ClojureScript:

```clojure
(d/q '[:find (aggregate ?my-agg ?x)
       :in $ ?my-agg
       :where ...]
     db
     my-aggregate-fn)
```
