---
name: datalevin
description: |
  Datalevin is a simple, fast and versatile Datalog database supporting persistent storage, 
  ACID transactions, cost-based query optimization, full-text search, and vector database features. 
  Use when building applications requiring embedded database with Datalog queries, key-value storage, 
  semantic search, or when the user mentions LMDB, EAV indexing, graph queries, durable storage, 
  production Datalog database, or alternatives to Datomic or DataScript with better performance.
---

# Datalevin

Datalevin is a simple, fast and versatile Datalog database built on LMDB with a cost-based query optimizer.

## Quick Start

Datalevin can be used as a Datalog database, key-value store, full-text search engine, or vector database.

```clojure
(require '[datalevin.core :as d])

;; Define schema (optional, supports schema-on-write)
(def schema {:aka {:db/cardinality :db.cardinality/many}
             :name {:db/valueType :db.type/string
                    :db/unique :db.unique/identity}})

;; Create connection to database
(def conn (d/get-conn "/tmp/my-db" schema))

;; Transact data
(d/transact! conn
  [{:name "Alice" :age 30 :aka ["Ali" "Al"]}
   {:name "Bob" :age 25}])

;; Query the data
(d/q '[:find ?name ?age
       :where [?e :name ?name]
              [?e :age ?age]]
     (d/db conn))
;; => #{["Alice" 30] ["Bob" 25]}

;; Close connection
(d/close conn)
```

## Core Concepts

### Durable Storage with LMDB

Unlike DataScript which stores data in memory, Datalevin persists data to disk using LMDB (Lightning Memory-Mapped Database), providing:
- ACID transaction guarantees
- Automatic memory-mapped file management  
- High read performance
- Crash-safe durability

### Cost-Based Query Optimizer

Datalevin includes a sophisticated query planner that:
- Analyzes query structure and statistics
- Generates optimal execution plans
- Significantly outperforms DataScript and Datomic in complex queries
- Competitive with PostgreSQL on join-heavy workloads

### Adaptive Asynchronous Transactions

For high-throughput writes, Datalevin offers:
- Adaptive batching that adjusts to workload
- Asynchronous transaction mode with futures
- 5-20X faster writes than SQLite in some scenarios

### Schema Flexibility

Unlike Datomic, Datalevin supports:
- Schema-on-write (attributes auto-created)
- Optional pre-defined schemas for special handling
- Runtime schema updates via `update-schema`
- Schema must be a map of maps (not vector)

## Common Workflows

### Workflow 1: Datalog Database Operations

Basic CRUD operations with Datalog:

```clojure
(require '[datalevin.core :as d])

;; Create/open database with schema
(def schema
  {:person/name {:db/valueType :db.type/string
                 :db/unique :db.unique/identity}
   :person/age {:db/valueType :db.type/long}
   :person/friends {:db/valueType :db.type/ref
                    :db/cardinality :db.cardinality/many}})

(def conn (d/create-conn "/tmp/people-db" schema))

;; Add entities
(d/transact! conn
  [{:db/id -1
    :person/name "Alice"
    :person/age 30}
   {:db/id -2
    :person/name "Bob"  
    :person/age 25
    :person/friends -1}])

;; Query relationships
(d/q '[:find ?name ?friend-name
       :where [?e :person/name ?name]
              [?e :person/friends ?f]
              [?f :person/name ?friend-name]]
     (d/db conn))
;; => #{["Bob" "Alice"]}

;; Update entity
(d/transact! conn [{:person/name "Alice" :person/age 31}])

;; Retract attribute
(d/transact! conn [[:db/retract [:person/name "Bob"] :person/age]])

;; Entity lookup
(def alice (d/entity (d/db conn) [:person/name "Alice"]))
(:person/age alice) ;; => 31

;; Pull API
(d/pull (d/db conn) 
        '[:person/name :person/age {:person/friends [:person/name]}]
        [:person/name "Bob"])
;; => #:person{:name "Bob", :friends [#:person{:name "Alice"}]}
```

### Workflow 2: Key-Value Store

Use Datalevin as a fast EDN key-value database:

```clojure
(require '[datalevin.core :as d])
(import '[java.util Date])

;; Open key-value database
(def db (d/open-kv "/tmp/my-kv-db"))

;; Open sub-databases (DBIs)
(d/open-dbi db "users")
(d/open-dbi db "sessions")

;; Store values with different data types
(d/transact-kv db
  [[:put "users" 1 {:name "Alice" :role :admin} :long :data]
   [:put "users" 2 {:name "Bob" :role :user} :long :data]
   [:put "sessions" "abc-123" (Date.) :string :instant]])

;; Get value
(d/get-value db "users" 1 :long :data)
;; => {:name "Alice", :role :admin}

;; Range query
(d/get-range db "users" [:closed 1 2] :long :data)
;; => [[1 {:name "Alice", :role :admin}] 
;;     [2 {:name "Bob", :role :user}]]

;; Count in range
(d/range-count db "users" [:all] :long)
;; => 2

;; Delete key
(d/transact-kv db [[:del "users" 1 :long]])

;; Close database
(d/close-kv db)
```

### Workflow 3: Asynchronous Transactions

High-throughput writes with adaptive batching:

```clojure
(require '[datalevin.core :as d])

(def conn (d/get-conn "/tmp/async-db"))

;; Async transactions return futures
(def future1 
  (d/transact-async conn 
    [{:name "User1" :age 20}]))

(def future2
  (d/transact-async conn
    [{:name "User2" :age 21}]))

;; Deref to get transaction report (blocks until committed)
@future1
;; => {:db-before ..., :db-after ..., :tx-data [...], :tempids {...}}

;; Or use callback (required for babashka pod)
(d/transact-async conn
  [{:name "User3" :age 22}]
  {}
  (fn [result]
    (if (instance? Exception result)
      (println "Transaction failed:" result)
      (println "Committed:" (:tx-data result)))))

;; For key-value async
(def kv-db (d/open-kv "/tmp/kv-async"))
(d/open-dbi kv-db "data")

(d/transact-kv-async kv-db
  [[:put "data" :counter 0 :keyword :long]]
  {}
  (fn [result]
    (println "KV transaction result:" result)))
```

### Workflow 4: Full-Text Search

Built-in search engine with customizable analyzers:

```clojure
(require '[datalevin.core :as d]
         '[datalevin.search-utils :as su])

;; Open database and create search engine
(def lmdb (d/open-kv "/tmp/search-db"))

(def engine 
  (d/new-search-engine lmdb
    {:index-position? true  ; Enable phrase search
     :include-text? true    ; Store original text
     :analyzer su/default-analyzer}))

;; Add documents
(d/add-doc engine :doc1 "The quick brown fox jumps over the lazy dog")
(d/add-doc engine :doc2 "The lazy cat sleeps all day")
(d/add-doc engine :doc3 "Quick reflexes help the fox")

;; Search with string query (OR semantics by default)
(d/search engine "quick fox")
;; => (:doc1 :doc3)

;; Boolean query structure
(d/search engine 
  [:and "quick" [:not "lazy"]]
  {:top 10})
;; => (:doc3)

;; Phrase search (requires :index-position? true)
(d/search engine 
  {:phrase "lazy dog"})
;; => (:doc1)

;; Get text with offsets for highlighting
(d/search engine "fox"
  {:display :texts+offsets})
;; => ([:doc1 "The quick brown fox..." [["fox" [16]]]])

;; Remove document
(d/remove-doc engine :doc2)

;; Check if indexed
(d/doc-indexed? engine :doc1) ;; => true

;; Get document count
(d/doc-count engine) ;; => 2
```

### Workflow 5: Vector Database for Semantic Search

SIMD-accelerated vector indexing with HNSW algorithm:

```clojure
(require '[datalevin.core :as d])

;; Open KV database
(def lmdb (d/open-kv "/tmp/vector-db"))

;; Create vector index
(def index
  (d/new-vector-index lmdb
    {:dimensions 128          ; Vector dimensions
     :metric-type :cosine     ; or :euclidean, :dot-product
     :quantization :float     ; or :double, :float16, :int8
     :connectivity 16         ; Graph connectivity
     :expansion-add 100       ; Candidates during add
     :expansion-search 40}))  ; Candidates during search

;; Add vectors with semantic references
(d/add-vec index :doc1 (vec (range 128)))
(d/add-vec index :doc2 (vec (range 1 129)))
(d/add-vec index :doc3 (vec (range 2 130)))

;; Search for nearest neighbors
(d/search-vec index (vec (range 128))
  {:top 3
   :display :refs})
;; => (:doc1 :doc2 :doc3)

;; Get distances too
(d/search-vec index (vec (range 128))
  {:top 2
   :display :refs+dists})
;; => ([:doc1 0.0] [:doc2 0.00784...])

;; Filter results
(d/search-vec index (vec (range 128))
  {:top 5
   :vec-filter (fn [ref] (not= ref :doc1))})
;; => (:doc2 :doc3)

;; Get index info
(d/vector-index-info index)
;; => {:size 3, :memory 524288, :dimensions 128, ...}

;; Remove vector
(d/remove-vec index :doc2)

;; Close index
(d/close-vector-index index)
```

### Workflow 6: Client/Server Mode

Run Datalevin as a networked database:

```clojure
;; Server setup (in server process)
;; Start server on port 8898 with RBAC
;; dtlv serve -d /data/db -a admin:password

;; Client connection
(require '[datalevin.core :as d])

;; Connect to remote server
(def conn 
  (d/create-conn "dtlv://admin:password@example.com:8898/mydb" 
    {:person/name {:db/valueType :db.type/string}}
    {:client-opts {:timeout 10000}}))

;; Use same API as local database
(d/transact! conn [{:person/name "Alice" :person/age 30}])

(d/q '[:find ?name :where [?e :person/name ?name]]
     (d/db conn))

;; Key-value remote access
(def kv-db 
  (d/open-kv "dtlv://admin:password@example.com:8898/mykv"))

(d/open-dbi kv-db "data")
(d/transact-kv kv-db [[:put "data" :key "value"]])
```

### Workflow 7: Advanced Query Features

Leverage Datalevin's query optimizer:

```clojure
(require '[datalevin.core :as d])

(def conn (d/get-conn "/tmp/query-db"))

;; Sample data
(d/transact! conn
  [{:db/id 1 :person/name "Alice" :person/age 30 :person/city "NYC"}
   {:db/id 2 :person/name "Bob" :person/age 25 :person/city "LA"}
   {:db/id 3 :person/name "Carol" :person/age 35 :person/city "NYC"}])

;; Order results
(d/q '[:find ?name ?age
       :where [?e :person/name ?name]
              [?e :person/age ?age]
       :order-by [?age :desc]]
     (d/db conn))
;; => (["Carol" 35] ["Alice" 30] ["Bob" 25])

;; Limit results
(d/q '[:find ?name
       :where [?e :person/name ?name]
       :limit 2]
     (d/db conn))
;; => #{["Alice"] ["Bob"]}

;; Explain query plan
(d/explain {:run? false}
  '[:find ?name ?age
    :where [?e :person/name ?name]
           [?e :person/age ?age]
           [?e :person/city "NYC"]]
  (d/db conn))
;; => {:planning-time "1.2 ms", :query-graph {...}, :plan {...}}

;; Aggregates
(d/q '[:find (max ?age) (min ?age) (avg ?age)
       :where [?e :person/age ?age]]
     (d/db conn))
;; => [[35 25 30]]

;; Rules (recursive queries)
(d/q '[:find ?ancestor
       :in $ % ?person
       :where (ancestor ?ancestor ?person)]
     (d/db conn)
     '[[(ancestor ?a ?p) [?p :person/parent ?a]]
       [(ancestor ?a ?p) [?p :person/parent ?x]
                         (ancestor ?a ?x)]]
     1)
```

## When to Use Datalevin

**Use Datalevin when you need:**
- Persistent Datalog database with ACID guarantees
- Better query performance than DataScript/Datomic
- Embedded database like SQLite but with Datalog
- Combined Datalog, key-value, full-text, and vector search
- Production-ready database with durable storage
- Server mode with role-based access control
- High write throughput with async transactions
- Graph queries and recursive rules
- EAV indexing for flexible schema

**Don't use Datalevin when:**
- You only need in-memory data (use DataScript instead)
- You need Datomic's time-travel features
- Application requires only SQL interface
- You need distributed database (Datalevin is single-node)
- Memory constraints prevent LMDB memory mapping

## Datalevin vs DataScript vs Datomic

**Datalevin advantages:**
- Durable storage (LMDB-based)
- Cost-based query optimizer (much faster complex queries)
- Async transactions with higher throughput
- Full-text search and vector database built-in
- Server mode with RBAC
- Larger dataset support
- Competitive with PostgreSQL in query performance

**DataScript advantages:**
- Pure Clojure (no native dependencies)
- Lighter weight for in-memory use
- ClojureScript compatible
- Simpler for client-side state

**Datomic advantages:**
- Time travel and historical queries
- Cloud-native scaling
- Speculative transactions
- Commercial support

**Key difference:** Datalevin prioritizes simplicity, performance, and production-readiness over Datomic's temporal features.

## Best Practices

**Do:**
- Use `get-conn` to reuse connections in the same process
- Enable `:auto-entity-time?` for automatic timestamp tracking
- Use async transactions for high write throughput
- Pre-define schema for attributes needing special handling (uniqueness, refs, cardinality-many)
- Run `analyze` periodically to update query planner statistics
- Use `:order-by` and `:limit` for large result sets
- Close connections and databases when done
- Use `with-conn` for temporary operations

**Don't:**
- Open multiple connections to same DB in one process (LMDB limitation)
- Store huge values in key-value store without chunking
- Forget to specify data types for range queries in KV store
- Use `:data` type for keys in range queries (use typed scalars)
- Ignore query `explain` output when optimizing performance
- Skip `:reload` flag when re-requiring changed namespaces

## Common Issues

### LMDB MapFullException

```clojure
;; Wrong: DB runs out of space
(def db (d/open-kv "/tmp/db")) ; Default 100MB

;; Right: Set larger initial size
(def db (d/open-kv "/tmp/db" {:mapsize 1000})) ; 1GB

;; Size auto-expands but causes temporary slowdown
;; Better to start with generous size
```

### Multiple Connections to Same DB

```clojure
;; Wrong: Multiple connections in same process
(def conn1 (d/create-conn "/tmp/db"))
(def conn2 (d/create-conn "/tmp/db")) ; Risk of corruption!

;; Right: Reuse connection
(def conn (d/get-conn "/tmp/db"))
;; Use conn throughout application

;; Or use with-conn for temporary access
(d/with-conn [conn "/tmp/db"]
  (d/transact! conn [...]))
```

### Schema Not Applied

```clojure
;; Wrong: Schema passed to query, not connection
(d/q '[:find ?e :where [?e :name "Alice"]]
     (d/db conn)
     {:name {:db/unique :db.unique/identity}})

;; Right: Pass schema when creating connection
(def conn (d/create-conn "/tmp/db"
            {:name {:db/unique :db.unique/identity}}))

;; Or update schema on existing connection
(d/update-schema conn 
  {:new/attr {:db/valueType :db.type/long}})
```

### Transaction Not Visible

```clojure
;; Wrong: Forgot to reload after transact-async
(d/transact-async conn [{:name "Alice"}])
(d/q '[:find ?e :where [?e :name "Alice"]] (d/db conn))
;; => #{} ; Not committed yet!

;; Right: Wait for commit or use sync transact
@(d/transact-async conn [{:name "Alice"}])
;; or
(d/transact! conn [{:name "Alice"}])
(d/q '[:find ?e :where [?e :name "Alice"]] (d/db conn))
;; => #{[1]}
```

### Key-Value Type Mismatch

```clojure
;; Wrong: Inconsistent data types for range query
(d/transact-kv db [[:put "nums" 1 "one"] ; :long key
                   [:put "nums" "2" "two"]]) ; :string key
(d/get-range db "nums" [:all] :long) ; Won't find string key!

;; Right: Consistent types
(d/transact-kv db [[:put "nums" 1 "one" :long :string]
                   [:put "nums" 2 "two" :long :string]])
(d/get-range db "nums" [:all] :long :string)
;; => [[1 "one"] [2 "two"]]
```

## Data Types for Key-Value Store

Datalevin supports these data types for typed keys/values:

**Scalar types:**
- `:data` - Arbitrary EDN (avoid for keys in range queries)
- `:string` - UTF-8 string
- `:long` - 64-bit integer
- `:float` - 32-bit IEEE754
- `:double` - 64-bit IEEE754
- `:bigint` - BigInteger in range [-2^1015, 2^1015-1]
- `:bigdec` - BigDecimal (unscaled in same range)
- `:bytes` - Byte array
- `:keyword` - EDN keyword
- `:symbol` - EDN symbol
- `:boolean` - true/false
- `:instant` - java.util.Date
- `:uuid` - java.util.UUID

**Composite types:**
- `[:long :string]` - Heterogeneous tuple (fixed types)
- `[:long]` - Homogeneous tuple (all elements same type)

Tuple elements max 255 bytes each. Keys max 511 bytes.

## Performance Tips

1. **Use async transactions for high write throughput:**
   ```clojure
   ;; 5-20X faster than sync in write-heavy scenarios
   (d/transact-async conn tx-data)
   ```

2. **Disable cache during bulk loading:**
   ```clojure
   (d/datalog-index-cache-limit db 0) ; Saves memory
   ;; ... bulk load ...
   (d/datalog-index-cache-limit db 256) ; Re-enable
   ```

3. **Use `:append` flag for sorted data:**
   ```clojure
   (d/transact-kv db 
     [[:put "data" 1 "a" :long :string]
      [:put "data" 2 "b" :long :string]]
     :long :string #{:append})
   ```

4. **Run analyze after bulk data changes:**
   ```clojure
   (d/analyze (d/db conn)) ; Updates query planner stats
   ```

5. **Use `range-seq` for large result sets:**
   ```clojure
   ;; Lazy loading prevents OOM
   (with-open [rng (d/range-seq db "data" [:all] :long)]
     (doseq [item rng]
       (process item)))
   ```

## External Resources

- [Official Documentation](https://cljdoc.org/d/datalevin/datalevin/CURRENT)
- [GitHub Repository](https://github.com/juji-io/datalevin)
- [Query Engine Article](https://yyhh.org/blog/2024/09/competing-for-the-job-with-a-triplestore/)
- [T-Wand Search Engine Article](https://yyhh.org/blog/2021/11/t-wand-beat-lucene-in-less-than-600-lines-of-code/)
- [Async Transaction Article](https://yyhh.org/blog/2025/02/achieving-high-throughput-and-low-latency-through-adaptive-asynchronous-transaction/)
- [LMDB Documentation](http://www.lmdb.tech/doc/)
- [Join Order Benchmark Results](https://github.com/juji-io/datalevin/blob/master/benchmarks/JOB-bench)

## Schema Attributes Reference

Common schema attribute properties:

```clojure
{:attribute/name
 {:db/valueType :db.type/string     ; :string, :long, :double, :boolean, 
                                     ; :instant, :uuid, :bytes, :ref
  :db/cardinality :db.cardinality/one ; or :many
  :db/unique :db.unique/identity     ; or :value (for uniqueness)
  :db/isComponent true                ; Cascade delete for refs
  :db/index true}}                    ; Create AVE index
```

**:db/valueType options:**
- `:db.type/string` - Text values
- `:db.type/long` - 64-bit integers  
- `:db.type/double` - Floating point
- `:db.type/boolean` - true/false
- `:db.type/instant` - Timestamps
- `:db.type/uuid` - UUIDs
- `:db.type/bytes` - Binary data
- `:db.type/ref` - References to other entities

**Special features:**
- Unspecified attributes treated as EDN blobs (`:data`)
- Schema optional (schema-on-write)
- Runtime schema updates via `update-schema`
- Entity time tracking with `:auto-entity-time?` option

## Transaction Functions

Built-in transaction functions:

```clojure
;; Add attribute to entity
[:db/add entity-id :attr value]

;; Retract specific attribute value
[:db/retract entity-id :attr value]

;; Retract attribute (all values if cardinality-many)
[:db/retract entity-id :attr]

;; Retract all attributes of entity (delete entity)
[:db.fn/retractEntity entity-id]

;; Retract specific attribute entirely
[:db.fn/retractAttribute entity-id :attr]
```

Map form for adding/updating:

```clojure
;; Creates new entity (negative tempid)
{:db/id -1
 :person/name "Alice"
 :person/friends [-2 -3]} ; Refs to other tempids

;; Updates existing (by entity id or unique attr)
{:person/name "Alice"  ; Unique attr lookup
 :person/age 31}       ; Update age

;; Nested entity creation
{:person/name "Alice"
 :person/address {:address/street "123 Main St"
                  :address/city "NYC"}}
```
