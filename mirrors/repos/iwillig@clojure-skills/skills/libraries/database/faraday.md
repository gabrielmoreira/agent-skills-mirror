---
name: faraday-dynamodb-client
description: |
  AWS DynamoDB client for Clojure with support for tables, items, queries, scans, 
  batch operations, transactions, and streams. Use when working with DynamoDB, 
  NoSQL databases, AWS data storage, key-value stores, distributed databases, 
  or when the user mentions DynamoDB, Faraday, AWS database, NoSQL, table operations, 
  primary keys, GSI, LSI, conditional writes, transactions, or DynamoDB streams.
---

# Faraday - DynamoDB Client for Clojure

## Quick Start

Faraday provides a simple, idiomatic Clojure interface to Amazon DynamoDB with full support for Clojure data types via Nippy serialization.

```clojure
;; Add dependency
{:deps {com.taoensso/faraday {:mvn/version "1.12.0"}}}

;; Basic setup
(require '[taoensso.faraday :as far])

(def client-opts
  {:access-key "AWS_ACCESS_KEY"
   :secret-key "AWS_SECRET_KEY"
   ;; Optional: for local DynamoDB
   :endpoint "http://localhost:8000"})

;; Create a table
(far/create-table client-opts :users
  [:id :n]  ; Primary key: id (number)
  {:throughput {:read 1 :write 1}
   :block? true})

;; Put an item
(far/put-item client-opts :users
  {:id 1
   :name "Alice"
   :email "alice@example.com"
   :tags #{"clojure" "aws"}
   :metadata (far/freeze {:nested {:data "here"}})})

;; Get an item
(far/get-item client-opts :users {:id 1})
;; => {:id 1 :name "Alice" :email "alice@example.com" ...}

;; Query items
(far/query client-opts :users {:id [:eq 1]})
;; => [{:id 1 :name "Alice" ...}]
```

**Key benefits:**
- Simple, idiomatic Clojure API that abstracts AWS SDK complexity
- Full support for Clojure data types via Nippy serialization
- Support for all major DynamoDB features: tables, items, queries, scans, transactions, streams
- Zero overhead - thin wrapper over official AWS Java SDK
- Works with both local DynamoDB and AWS cloud

## Core Concepts

### Primary Keys and Key Schema

DynamoDB uses primary keys for item identification. Primary keys can be:

**Hash Key Only (Partition Key):**
```clojure
;; Simple primary key
[:id :n]  ; Single attribute "id" of type number
```

**Hash Key + Range Key (Partition Key + Sort Key):**
```clojure
;; Composite primary key
(far/create-table client-opts :posts
  [:user-id :s]  ; Hash key (partition key)
  {:range-keydef [:timestamp :n]  ; Range key (sort key)
   :throughput {:read 1 :write 1}
   :block? true})
```

**Key Types:**
- `:s` - String
- `:n` - Number
- `:b` - Binary
- `:ss` - String Set
- `:ns` - Number Set
- `:bs` - Binary Set

### Data Serialization with Freeze

Use `freeze` to store arbitrary Clojure data that DynamoDB doesn't natively support:

```clojure
(require '[taoensso.faraday :as far])

;; Store complex Clojure data
(far/put-item client-opts :users
  {:id 1
   :name "Bob"
   ;; Freeze preserves exact Clojure data structures
   :settings (far/freeze {:theme :dark
                          :notifications #{:email :sms}
                          :ratio 22/7})})

;; Retrieved data is automatically thawed
(far/get-item client-opts :users {:id 1})
;; => {:id 1 :name "Bob" :settings {:theme :dark :notifications #{:email :sms} :ratio 22/7}}
```

**When to use freeze:**
- Nested maps and vectors
- Sets (beyond string/number sets)
- Keywords as values
- Rationals, UUIDs, dates
- Any Clojure-specific data type

### Item Operations

All item operations use primary key values (`prim-kvs`):

```clojure
;; Hash key only
{:id 123}

;; Hash + range key
{:user-id "alice" :timestamp 1234567890}
```

### Conditional Operations

DynamoDB supports conditional writes using expressions:

```clojure
;; Condition expressions
(far/put-item client-opts :users
  {:id 1 :name "Alice" :version 2}
  {:cond-expr "attribute_not_exists(id) OR version < :new_version"
   :expr-attr-vals {":new_version" 2}})

;; Common conditions
"attribute_exists(id)"           ; Item must exist
"attribute_not_exists(id)"       ; Item must not exist
"#name = :value"                 ; Attribute equals value
"size(#list) < :max"            ; List size check
"contains(#tags, :tag)"          ; Set/list contains value
```

## Common Workflows

### Workflow 1: Table Management

```clojure
(require '[taoensso.faraday :as far])

;; List all tables
(far/list-tables client-opts)
;; => (:users :posts :sessions)

;; Describe a table
(far/describe-table client-opts :users)
;; => {:table {:attribute-definitions [...] :key-schema [...] ...}}

;; Create table with secondary indexes
(far/create-table client-opts :posts
  [:post-id :s]
  {:range-keydef [:timestamp :n]
   :throughput {:read 5 :write 5}
   :gsindexes [{:name "user-posts-index"
                :hash-keydef [:user-id :s]
                :range-keydef [:timestamp :n]
                :projection :all
                :throughput {:read 5 :write 5}}]
   :lsindexes [{:name "posts-by-score"
                :range-keydef [:score :n]
                :projection :keys-only}]
   :block? true})

;; Update table throughput
(far/update-table client-opts :users
  {:throughput {:read 10 :write 10}})

;; Enable on-demand billing
(far/update-table client-opts :users
  {:billing-mode :pay-per-request})

;; Delete table
(far/delete-table client-opts :old-table)

;; Create table if it doesn't exist
(far/ensure-table client-opts :users
  [:id :n]
  {:throughput {:read 1 :write 1}})
```

### Workflow 2: CRUD Operations

```clojure
(require '[taoensso.faraday :as far])

;; Create (Put)
(far/put-item client-opts :users
  {:id 1
   :name "Alice"
   :email "alice@example.com"
   :age 30
   :tags #{"clojure" "aws"}})

;; Read (Get)
(far/get-item client-opts :users {:id 1})
;; => {:id 1 :name "Alice" ...}

;; Get with projection (only specific attributes)
(far/get-item client-opts :users {:id 1}
  {:attrs [:name :email]})
;; => {:name "Alice" :email "alice@example.com"}

;; Get with consistent read
(far/get-item client-opts :users {:id 1}
  {:consistent? true})

;; Update (partial update)
(far/update-item client-opts :users {:id 1}
  {:update-expr "SET age = :new_age, #n = :new_name"
   :expr-attr-names {"#n" "name"}  ; 'name' is reserved word
   :expr-attr-vals {":new_age" 31 ":new_name" "Alice Smith"}
   :return :all-new})

;; Increment a counter
(far/update-item client-opts :users {:id 1}
  {:update-expr "ADD login_count :inc"
   :expr-attr-vals {":inc" 1}})

;; Add to a set
(far/update-item client-opts :users {:id 1}
  {:update-expr "ADD tags :new_tags"
   :expr-attr-vals {":new_tags" #{"dynamodb"}}})

;; Delete (remove item)
(far/delete-item client-opts :users {:id 1})

;; Delete with condition
(far/delete-item client-opts :users {:id 1}
  {:cond-expr "attribute_exists(id)"})
```

### Workflow 3: Querying with Primary Keys

```clojure
(require '[taoensso.faraday :as far])

;; Query by hash key
(far/query client-opts :posts
  {:user-id [:eq "alice"]})
;; => [{:user-id "alice" :timestamp 1000 ...} ...]

;; Query with range key condition
(far/query client-opts :posts
  {:user-id [:eq "alice"]
   :timestamp [:between [1000 2000]]})

;; Query with limit
(far/query client-opts :posts
  {:user-id [:eq "alice"]}
  {:limit 10})

;; Query in descending order
(far/query client-opts :posts
  {:user-id [:eq "alice"]}
  {:order :desc})

;; Query with pagination
(let [page-1 (far/query client-opts :posts
               {:user-id [:eq "alice"]}
               {:limit 10})
      last-key (:last-prim-kvs (meta page-1))]
  (when last-key
    (far/query client-opts :posts
      {:user-id [:eq "alice"]}
      {:limit 10
       :last-prim-kvs last-key})))

;; Query secondary index
(far/query client-opts :posts
  {:user-id [:eq "alice"]}
  {:index "user-posts-index"})

;; Query with filter expression
(far/query client-opts :posts
  {:user-id [:eq "alice"]}
  {:filter-expr "score > :min_score"
   :expr-attr-vals {":min_score" 100}})

;; Comparison operators for queries
;; :eq, :le, :lt, :ge, :gt, :begins-with, :between
(far/query client-opts :posts
  {:user-id [:eq "alice"]
   :timestamp [:ge 1000]})  ; Greater than or equal
```

### Workflow 4: Scanning Tables

```clojure
(require '[taoensso.faraday :as far])

;; Scan entire table (use with caution!)
(far/scan client-opts :users)
;; => [{:id 1 ...} {:id 2 ...} ...]

;; Scan with filter
(far/scan client-opts :users
  {:filter-expr "age > :min_age"
   :expr-attr-vals {":min_age" 25}})

;; Scan with attribute conditions (deprecated, use filter-expr)
(far/scan client-opts :users
  {:attr-conds {:age [:gt 25]
                :tags [:contains "clojure"]}})

;; Scan with projection
(far/scan client-opts :users
  {:proj-expr "id, #n, email"
   :expr-attr-names {"#n" "name"}})

;; Scan with limit (for rate limiting)
(far/scan client-opts :users
  {:limit 100})  ; Evaluate max 100 items

;; Scan with pagination
(let [page-1 (far/scan client-opts :users {:limit 100})
      last-key (:last-prim-kvs (meta page-1))]
  (when last-key
    (far/scan client-opts :users
      {:limit 100
       :last-prim-kvs last-key})))

;; Parallel scan (divide table into segments)
(far/scan-parallel client-opts :users 4)
;; Scans table using 4 parallel workers
;; Returns vector of 4 result sets

;; Scan comparison operators
;; :eq, :ne, :le, :lt, :ge, :gt, :begins-with, :between,
;; :not-null, :null, :contains, :not-contains, :in
```

### Workflow 5: Batch Operations

```clojure
(require '[taoensso.faraday :as far])

;; Batch get items (up to 100 items, 16MB)
(far/batch-get-item client-opts
  {:users {:prim-kvs {:id [1 2 3 4 5]}}
   :posts {:prim-kvs [{:user-id "alice" :timestamp 1000}
                      {:user-id "bob" :timestamp 2000}]
           :consistent? true
           :attrs [:user-id :timestamp :title]}})
;; => {:users [{:id 1 ...} {:id 2 ...}]
;;     :posts [{:user-id "alice" ...} {:user-id "bob" ...}]}

;; Batch write items (up to 25 items)
(far/batch-write-item client-opts
  {:users {:put [{:id 10 :name "Charlie"}
                 {:id 11 :name "Dana"}]
           :delete [{:id 5} {:id 6}]}
   :posts {:put [{:user-id "eve" :timestamp 3000 :title "Hello"}]}})

;; Handle unprocessed items
(let [result (far/batch-write-item client-opts
               {:users {:put (range 100 (fn [i] {:id i :name (str "User" i)}))}})]
  (when-let [unprocessed (:unprocessed result)]
    ;; Retry unprocessed items
    (far/batch-write-item client-opts unprocessed)))

;; Span requests to exceed throughput limits
(far/batch-get-item client-opts
  {:users {:prim-kvs {:id (range 1 1000)}}}
  {:span-reqs {:max 10         ; Max 10 requests
               :throttle-ms 100}})  ; 100ms between requests
```

### Workflow 6: Transactions

```clojure
(require '[taoensso.faraday :as far])

;; Transactional writes (all-or-nothing, up to 25 items)
(far/transact-write-items client-opts
  {:items [;; Conditional check
           [:cond-check {:table-name :accounts
                         :prim-kvs {:id "account-1"}
                         :cond-expr "balance >= :amount"
                         :expr-attr-vals {":amount" 100}}]
           
           ;; Put item
           [:put {:table-name :transactions
                  :item {:id "tx-123"
                         :from "account-1"
                         :to "account-2"
                         :amount 100}}]
           
           ;; Update items
           [:update {:table-name :accounts
                     :prim-kvs {:id "account-1"}
                     :update-expr "SET balance = balance - :amount"
                     :expr-attr-vals {":amount" 100}}]
           
           [:update {:table-name :accounts
                     :prim-kvs {:id "account-2"}
                     :update-expr "SET balance = balance + :amount"
                     :expr-attr-vals {":amount" 100}}]
           
           ;; Delete item
           [:delete {:table-name :old-transactions
                     :prim-kvs {:id "old-tx-456"}}]]})

;; Transactional reads (consistent snapshot)
(far/transact-get-items client-opts
  {:items [{:table-name :accounts :prim-kvs {:id "account-1"}}
           {:table-name :accounts :prim-kvs {:id "account-2"}}]})
;; => {:items [{:id "account-1" :balance 500} {:id "account-2" :balance 300}]}
```

### Workflow 7: TTL (Time To Live)

```clojure
(require '[taoensso.faraday :as far])

;; Describe current TTL configuration
(far/describe-ttl client-opts :sessions)

;; Enable TTL on a table
(far/update-ttl client-opts :sessions true "expires-at")

;; Ensure TTL is set (idempotent)
(far/ensure-ttl client-opts :sessions "expires-at")

;; Put item with expiration (Unix timestamp in seconds)
(far/put-item client-opts :sessions
  {:session-id "abc123"
   :user-id 42
   :expires-at (+ (quot (System/currentTimeMillis) 1000)
                  (* 60 60 24 7))})  ; Expires in 7 days

;; Disable TTL
(far/update-ttl client-opts :sessions false "expires-at")
```

### Workflow 8: DynamoDB Streams

```clojure
(require '[taoensso.faraday :as far])

;; Enable streams on table creation
(far/create-table client-opts :events
  [:event-id :s]
  {:throughput {:read 1 :write 1}
   :stream-spec {:enabled? true
                 :view-type :new-and-old-images}
   :block? true})

;; View types: :keys-only, :new-image, :old-image, :new-and-old-images

;; List streams
(far/list-streams client-opts)
;; => ({:stream-arn "arn:aws:..." :table-name :events} ...)

;; Describe stream
(let [stream-arn (:stream-arn (first (far/list-streams client-opts)))]
  (far/describe-stream client-opts stream-arn))

;; Get shard iterator
(let [stream-arn "arn:aws:dynamodb:..."
      shard-id "shardId-..."]
  (far/shard-iterator client-opts stream-arn shard-id :latest))

;; Read stream records
(let [iterator (far/shard-iterator client-opts stream-arn shard-id :latest)]
  (far/get-stream-records client-opts iterator {:limit 100}))
;; => {:records [{:event-id ... :dynamodb {...}} ...] :next-shard-iterator "..."}
```

## When to Use Each Approach

**Use Faraday when:**
- Building Clojure applications that need NoSQL database storage
- Working with AWS DynamoDB (cloud or local)
- You need full Clojure data type support with serialization
- You want a simple, idiomatic Clojure API over AWS SDK
- Working with key-value access patterns

**Use alternative AWS SDK libraries when:**
- You need raw AWS SDK access for advanced features
- Working with many AWS services beyond DynamoDB
- You prefer the official AWS SDK interface

**Use Faraday's `freeze` when:**
- Storing nested Clojure data structures
- Working with Clojure-specific types (keywords, rationals, sets)
- You need compression for large data
- Performance of native types isn't critical

**Use native DynamoDB types when:**
- Working with simple strings, numbers, and sets
- Performance is critical (no serialization overhead)
- Interoperability with other languages/services is important
- Using DynamoDB native features (e.g., atomic counters with numbers)

**Use queries when:**
- You know the partition key value
- Working with indexed data
- Need efficient, targeted data retrieval
- Accessing a single partition or range of sort keys

**Use scans when:**
- Need to examine all items in table
- Don't know partition key values
- Performing analytics or data export
- Note: Scans are expensive - use query when possible

**Use transactions when:**
- Need ACID guarantees across multiple items
- Implementing banking/accounting operations
- Ensuring consistency across tables
- All operations must succeed or fail together
- Limit: 25 items per transaction

**Use batch operations when:**
- Reading or writing many items efficiently
- Don't need transactional guarantees
- Can tolerate partial failures
- Limit: 100 items for batch-get, 25 for batch-write

## Best Practices

**DO:**
- Use `freeze` for complex Clojure data to maintain type fidelity
- Design tables with access patterns in mind (primary keys and indexes)
- Use conditional expressions for optimistic locking
- Enable DynamoDB streams for change data capture
- Use transactions for operations requiring ACID guarantees
- Paginate large result sets using `:last-prim-kvs`
- Use `:limit` in scans to control read throughput consumption
- Consider on-demand billing (`:pay-per-request`) for unpredictable workloads
- Use batch operations for bulk reads/writes
- Set appropriate throughput limits or use on-demand billing

**DON'T:**
- Use scans as primary access pattern (use queries with proper indexes)
- Forget to handle unprocessed items in batch operations
- Store large binary data directly (use S3 and store references)
- Use overly broad scans without filters or limits
- Ignore DynamoDB's 400KB item size limit
- Put hot partition keys that exceed throughput
- Use transactions for operations that don't need atomicity
- Forget that empty strings/binaries were prohibited (before 2020 update)
- Use `freeze` for simple types that DynamoDB handles natively

## Common Issues

### Issue: "Conditional check failed"

**Problem:** Conditional expression failed during put/update/delete

```clojure
(far/put-item client-opts :users {:id 1 :name "Alice"}
  {:cond-expr "attribute_not_exists(id)"})
;; ConditionalCheckFailedException if item exists
```

**Solution:** Handle the exception or adjust your condition

```clojure
(try
  (far/put-item client-opts :users {:id 1 :name "Alice"}
    {:cond-expr "attribute_not_exists(id)"})
  (catch Exception e
    (if (far/ex :conditional-check-failed)
      (println "Item already exists")
      (throw e))))

;; Or use put without condition to overwrite
(far/put-item client-opts :users {:id 1 :name "Alice"})
```

### Issue: "ValidationException: One or more parameter values were invalid"

**Problem:** Invalid primary key or missing required attributes

```clojure
;; Wrong: missing range key
(far/get-item client-opts :posts {:user-id "alice"})
;; Table has composite key but only hash key provided
```

**Solution:** Provide complete primary key

```clojure
;; Right: both hash and range key
(far/get-item client-opts :posts
  {:user-id "alice" :timestamp 1000})
```

### Issue: Empty strings or sets causing errors

**Problem:** DynamoDB (historically) didn't allow empty strings or sets

```clojure
(far/put-item client-opts :users
  {:id 1 :name "" :tags #{}})
;; May cause validation error in older DynamoDB versions
```

**Solution:** Remove empty values or use `freeze`

```clojure
;; Option 1: Remove empty values
(far/put-item client-opts :users
  (far/remove-empty-attr-vals
    {:id 1 :name "" :tags #{}}))

;; Option 2: Use freeze for complex data
(far/put-item client-opts :users
  {:id 1
   :data (far/freeze {:name "" :tags #{}})})
```

### Issue: "ProvisionedThroughputExceededException"

**Problem:** Exceeded read/write capacity units

```clojure
;; Too many requests too fast
(doseq [i (range 10000)]
  (far/put-item client-opts :users {:id i :name (str "User" i)}))
```

**Solution:** Use batch operations, span-reqs, or adjust throughput

```clojure
;; Option 1: Batch writes
(far/batch-write-item client-opts
  {:users {:put (map #(hash-map :id % :name (str "User" %))
                     (range 10000))}}
  {:span-reqs {:max 20 :throttle-ms 100}})

;; Option 2: Increase provisioned throughput
(far/update-table client-opts :users
  {:throughput {:read 100 :write 100}})

;; Option 3: Use on-demand billing
(far/update-table client-opts :users
  {:billing-mode :pay-per-request})
```

### Issue: Query returns no results but items exist

**Problem:** Query requires exact partition key match

```clojure
;; Wrong: partial match doesn't work
(far/query client-opts :users
  {:name [:begins-with "Ali"]})  ; 'name' is partition key
;; Returns empty - partition keys must match exactly
```

**Solution:** Use exact match for partition key, range key can use operators

```clojure
;; Right: exact partition key, operators on range key
(far/query client-opts :posts
  {:user-id [:eq "alice"]              ; Exact match required
   :timestamp [:begins-with "2024"]})  ; Operators allowed on range key

;; For partial matches, use scan (less efficient)
(far/scan client-opts :users
  {:filter-expr "begins_with(#n, :prefix)"
   :expr-attr-names {"#n" "name"}
   :expr-attr-vals {":prefix" "Ali"}})
```

### Issue: Item size exceeds limit

**Problem:** DynamoDB has 400KB item size limit

```clojure
(far/put-item client-opts :documents
  {:id 1 :content (slurp "large-file.txt")})  ; > 400KB
;; ItemSizeExceededException
```

**Solution:** Store large data in S3, keep reference in DynamoDB

```clojure
;; Store in S3 (using AWS SDK or library)
(let [s3-key (upload-to-s3 "large-file.txt")]
  ;; Store reference in DynamoDB
  (far/put-item client-opts :documents
    {:id 1 :s3-key s3-key :size 500000}))
```

## Advanced Topics

### Local DynamoDB for Development

```clojure
;; Start local DynamoDB with Docker
;; docker run -p 8000:8000 amazon/dynamodb-local

(def local-client-opts
  {:access-key "LOCAL"  ; Can be any value for local
   :secret-key "LOCAL"
   :endpoint "http://localhost:8000"})

(far/list-tables local-client-opts)
```

### Custom Client Configuration

```clojure
(import '[com.amazonaws.client.builder AwsClientBuilder$EndpointConfiguration]
        '[com.amazonaws.services.dynamodbv2 AmazonDynamoDBClientBuilder])

(def custom-client
  (-> (AmazonDynamoDBClientBuilder/standard)
      (.withEndpointConfiguration
        (AwsClientBuilder$EndpointConfiguration.
          "http://localhost:8000" "us-east-1"))
      (.build)))

(def client-opts
  {:client custom-client})

(far/list-tables client-opts)
```

### Using with IAM Roles (EC2, ECS, Lambda)

```clojure
;; On AWS with IAM role, no keys needed
(def client-opts {})  ; Automatically uses IAM role credentials

(far/list-tables client-opts)
```

## Resources

- [Official Faraday Documentation](https://www.taoensso.com/faraday)
- [API Reference (Codox)](http://taoensso.github.io/faraday/)
- [GitHub Repository](https://github.com/taoensso/faraday)
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [DynamoDB Data Model](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DataModel.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Nippy Serialization](https://github.com/ptaoussanis/nippy)

## Summary

Faraday provides a simple, powerful Clojure interface to AWS DynamoDB:

- **Simple API** - Idiomatic Clojure over complex AWS SDK
- **Full Clojure support** - Use any Clojure data type with `freeze`
- **Complete feature set** - Tables, items, queries, scans, batches, transactions, streams
- **Performance** - Zero overhead wrapper over official Java SDK
- **Local development** - Works with local DynamoDB for testing

Master DynamoDB access patterns (query vs scan, partition/sort keys, indexes) and use Faraday's `freeze` for Clojure data to build scalable, persistent applications.
