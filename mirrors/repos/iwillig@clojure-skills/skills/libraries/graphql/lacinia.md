---
name: lacinia-graphql
description: |
  GraphQL implementation for Clojure. Use when building GraphQL APIs, creating flexible query
  interfaces, implementing graph-based data retrieval, or when clients need precise control
  over response shape. Supports queries, mutations, subscriptions, schema introspection,
  fragments, and custom scalars. Ideal for API gateways, microservices aggregation, mobile
  backends, and real-time applications with GraphQL subscriptions.
---

# Lacinia - GraphQL for Clojure

## Quick Start

Lacinia is a complete GraphQL implementation for Clojure, providing schema definition, query parsing, and execution.

```clojure
(require '[com.walmartlabs.lacinia :as lacinia]
         '[com.walmartlabs.lacinia.schema :as schema]
         '[com.walmartlabs.lacinia.util :refer [inject-resolvers]])

;; Define schema as EDN
(def schema-def
  {:objects
   {:User
    {:fields {:id {:type '(non-null Int)}
              :name {:type '(non-null String)}
              :email {:type 'String}}}}
   
   :queries
   {:user
    {:type :User
     :args {:id {:type '(non-null Int)}}
     :resolve :query/user}}})

;; Implement resolvers
(defn get-user [context args value]
  (let [{:keys [id]} args]
    {:id id
     :name "Alice"
     :email "alice@example.com"}))

;; Compile schema
(def compiled-schema
  (-> schema-def
      (inject-resolvers {:query/user get-user})
      schema/compile))

;; Execute query
(lacinia/execute 
  compiled-schema 
  "{ user(id: 1) { name email } }" 
  nil 
  nil)
; => {:data {:user {:name "Alice", :email "alice@example.com"}}}
```

**Key benefits:**
- Full GraphQL spec compliance
- EDN-based schema definition
- Efficient async execution
- Strong type system
- Built-in schema introspection
- Subscription support
- Backend-agnostic (use with any web framework)

## Core Concepts

### Schema Definition

Lacinia schemas are defined as EDN maps with these main sections:

**Objects**: Define types with fields
```clojure
{:objects
 {:User
  {:fields {:id {:type 'Int}
            :name {:type 'String}
            :posts {:type '(list :Post)}}}}}
```

**Queries**: Read operations
```clojure
{:queries
 {:user {:type :User
         :args {:id {:type 'Int}}
         :resolve :query/user}}}
```

**Mutations**: Write operations
```clojure
{:mutations
 {:createUser {:type :User
               :args {:name {:type 'String}}
               :resolve :mutation/create-user}}}
```

**Subscriptions**: Real-time updates
```clojure
{:subscriptions
 {:userUpdated {:type :User
                :args {:id {:type 'Int}}
                :stream :subscription/user-stream}}}
```

### Type System

**Scalar Types**: `Int`, `Float`, `String`, `Boolean`, `ID`

**Type Modifiers**:
- `(non-null Type)` - Required, cannot be null
- `(list Type)` - List of values
- `(non-null (list Type))` - Required list (can contain nulls)
- `(list (non-null Type))` - List of required values

**Example**:
```clojure
{:fields
 {:name {:type '(non-null String)}          ; Required
  :email {:type 'String}                    ; Optional
  :tags {:type '(list String)}              ; Optional list
  :items {:type '(non-null (list :Item))}}} ; Required list
```

### Field Resolvers

Resolvers are functions that fetch data:

```clojure
(defn resolve-field [context args parent-value]
  ;; context - app context (db, auth, etc.)
  ;; args - field arguments
  ;; parent-value - resolved value from parent field
  
  ;; Return value matching field type
  )
```

**Synchronous resolver**:
```clojure
(defn get-user [context args value]
  {:id 1 :name "Alice"})
```

**Async resolver** (returns ResolverResult):
```clojure
(require '[com.walmartlabs.lacinia.resolve :as resolve])

(defn get-user-async [context args value]
  (resolve/with-promise
    (fetch-user-from-db (:id args))
    (fn [user]
      (resolve/resolve-as user))))
```

### Enums and Unions

**Enums**:
```clojure
{:enums
 {:UserRole
  {:values [:ADMIN :USER :GUEST]}}}
```

**Unions** (one of several types):
```clojure
{:unions
 {:SearchResult
  {:members [:User :Post :Comment]}}}
```

### Interfaces

Define shared fields across types:

```clojure
{:interfaces
 {:Node
  {:fields {:id {:type '(non-null ID)}}}}
 
 :objects
 {:User
  {:implements [:Node]
   :fields {:id {:type '(non-null ID)}
            :name {:type 'String}}}}}
```

## Common Workflows

### Workflow 1: Building a Query API

Define schema with queries and resolvers:

```clojure
(require '[com.walmartlabs.lacinia :as lacinia]
         '[com.walmartlabs.lacinia.schema :as schema]
         '[com.walmartlabs.lacinia.util :refer [inject-resolvers]])

;; Schema definition
(def schema-def
  {:objects
   {:User
    {:fields {:id {:type '(non-null Int)}
              :name {:type '(non-null String)}
              :email {:type 'String}
              :posts {:type '(list :Post)}}}
    
    :Post
    {:fields {:id {:type '(non-null Int)}
              :title {:type '(non-null String)}
              :content {:type 'String}
              :author {:type :User}}}}
   
   :queries
   {:user
    {:type :User
     :args {:id {:type '(non-null Int)}}
     :resolve :query/user}
    
    :post
    {:type :Post
     :args {:id {:type '(non-null Int)}}
     :resolve :query/post}}})

;; Resolvers
(defn get-user [context {:keys [id]} value]
  ;; Fetch from database
  {:id id
   :name "Alice"
   :email "alice@example.com"})

(defn get-user-posts [context args user]
  ;; user is the parent value
  [{:id 1 :title "First Post" :author user}
   {:id 2 :title "Second Post" :author user}])

(defn get-post [context {:keys [id]} value]
  {:id id
   :title "My Post"
   :content "Content here..."})

(defn get-post-author [context args post]
  {:id 1 :name "Alice" :email "alice@example.com"})

;; Compile
(def schema
  (-> schema-def
      (inject-resolvers {:query/user get-user
                         :query/post get-post
                         :User/posts get-user-posts
                         :Post/author get-post-author})
      schema/compile))

;; Execute query
(lacinia/execute schema
  "{ user(id: 1) { 
      name 
      posts { 
        title 
      } 
    } }"
  nil
  nil)
; => {:data {:user {:name "Alice", 
;                    :posts [{:title "First Post"} 
;                            {:title "Second Post"}]}}}
```

### Workflow 2: Mutations (Write Operations)

Implement data modification operations:

```clojure
(def schema-def
  {:objects
   {:User
    {:fields {:id {:type '(non-null Int)}
              :name {:type '(non-null String)}
              :email {:type 'String}}}}
   
   :mutations
   {:createUser
    {:type :User
     :args {:name {:type '(non-null String)}
            :email {:type 'String}}
     :resolve :mutation/create-user}
    
    :updateUser
    {:type :User
     :args {:id {:type '(non-null Int)}
            :name {:type 'String}
            :email {:type 'String}}
     :resolve :mutation/update-user}
    
    :deleteUser
    {:type 'Boolean
     :args {:id {:type '(non-null Int)}}
     :resolve :mutation/delete-user}}})

;; Mutation resolvers
(defn create-user [context {:keys [name email]} value]
  (let [user {:id (generate-id) :name name :email email}]
    ;; Save to database
    (save-user! user)
    user))

(defn update-user [context {:keys [id name email]} value]
  (let [user (find-user id)
        updated (merge user {:name name :email email})]
    (save-user! updated)
    updated))

(defn delete-user [context {:keys [id]} value]
  (delete-user! id)
  true)

;; Execute mutation
(lacinia/execute schema
  "mutation { 
    createUser(name: \"Bob\", email: \"bob@example.com\") { 
      id 
      name 
    } 
  }"
  nil
  nil)
; => {:data {:createUser {:id 2, :name "Bob"}}}
```

### Workflow 3: Async Resolvers (Database Queries)

Handle async operations efficiently:

```clojure
(require '[com.walmartlabs.lacinia.resolve :as resolve]
         '[clojure.core.async :refer [go <!]])

;; Async resolver returning promise
(defn get-user-async [context {:keys [id]} value]
  (let [promise (resolve/resolve-promise)]
    (go
      (let [user (<! (fetch-user-from-db id))]
        (resolve/deliver! promise user)))
    promise))

;; Using with-promise helper
(defn get-user-async-2 [context {:keys [id]} value]
  (resolve/with-promise
    ;; Returns a channel
    (fetch-user-from-db id)
    ;; Delivery function
    (fn [user]
      (if user
        (resolve/resolve-as user)
        (resolve/resolve-as nil {:message "User not found"})))))

;; Parallel async resolution
(defn get-user-with-stats [context {:keys [id]} value]
  (resolve/with-promise
    ;; Fetch multiple things in parallel
    (let [user-chan (fetch-user id)
          stats-chan (fetch-user-stats id)]
      (go
        (let [user (<! user-chan)
              stats (<! stats-chan)]
          {:user user :stats stats})))
    identity))
```

**Pattern**: Lacinia automatically batches and parallelizes resolver execution where possible.

### Workflow 4: Input Objects and Arguments

Define complex input types:

```clojure
(def schema-def
  {:input-objects
   {:UserInput
    {:fields {:name {:type '(non-null String)}
              :email {:type '(non-null String)}
              :age {:type 'Int}
              :address {:type :AddressInput}}}
    
    :AddressInput
    {:fields {:street {:type 'String}
              :city {:type 'String}
              :zip {:type 'String}}}}
   
   :mutations
   {:createUser
    {:type :User
     :args {:input {:type '(non-null :UserInput)}}
     :resolve :mutation/create-user}}})

;; Resolver using input object
(defn create-user [context {:keys [input]} value]
  (let [{:keys [name email age address]} input]
    ;; input is a map with nested address map
    (save-user! {:name name 
                 :email email 
                 :age age
                 :address address})
    {:id (generate-id) :name name :email email}))

;; Execute with variables
(lacinia/execute schema
  "mutation CreateUser($user: UserInput!) {
    createUser(input: $user) {
      id name
    }
  }"
  {:user {:name "Charlie"
          :email "charlie@example.com"
          :age 30
          :address {:city "NYC" :zip "10001"}}}
  nil)
```

### Workflow 5: Schema Introspection

Query the schema itself:

```clojure
;; Query all types
(lacinia/execute schema
  "{ __schema { 
      types { 
        name 
        kind 
      } 
    } }"
  nil
  nil)

;; Query specific type
(lacinia/execute schema
  "{ __type(name: \"User\") { 
      name 
      fields { 
        name 
        type { 
          name 
          kind 
        } 
      } 
    } }"
  nil
  nil)
; => {:data {:__type {:name "User",
;                     :fields [{:name "id", :type {:name "Int", :kind "SCALAR"}}
;                              {:name "name", :type {:name "String", :kind "SCALAR"}}]}}}
```

**Use cases**:
- GraphQL Playground/GraphiQL tools
- Auto-generating documentation
- Client code generation
- Schema validation

### Workflow 6: Fragments (Code Reuse)

Use fragments to avoid repetition:

```clojure
;; Query with named fragment
(lacinia/execute schema
  "query GetUsers {
    user(id: 1) {
      ...UserFields
    }
    admin: user(id: 2) {
      ...UserFields
    }
  }
  
  fragment UserFields on User {
    id
    name
    email
  }"
  nil
  nil)
; => {:data {:user {:id 1, :name "Alice", :email "alice@example.com"}
;            :admin {:id 2, :name "Bob", :email "bob@example.com"}}}

;; Inline fragment (type-specific fields)
(lacinia/execute schema
  "{ search(query: \"test\") {
      ... on User {
        name
        email
      }
      ... on Post {
        title
        content
      }
    }
  }"
  nil
  nil)
```

### Workflow 7: Error Handling

Report errors properly:

```clojure
(require '[com.walmartlabs.lacinia.resolve :as resolve])

;; Return error from resolver
(defn get-user [context {:keys [id]} value]
  (if-let [user (find-user id)]
    user
    (resolve/resolve-as nil {:message "User not found"
                             :status 404
                             :id id})))

;; Multiple errors
(defn get-users [context {:keys [ids]} value]
  (let [results (map find-user ids)
        errors (keep-indexed 
                 (fn [idx user]
                   (when-not user
                     {:message "User not found"
                      :path [:users idx]
                      :id (nth ids idx)}))
                 results)]
    (if (seq errors)
      (resolve/resolve-as results errors)
      results)))

;; Exception handling
(defn get-user-safe [context {:keys [id]} value]
  (try
    (find-user id)
    (catch Exception e
      (resolve/resolve-as nil {:message (.getMessage e)
                               :exception-type (.getName (.getClass e))}))))
```

**Result with errors**:
```clojure
{:data {:user nil}
 :errors [{:message "User not found"
           :status 404
           :id 123
           :locations [{:line 1 :column 3}]
           :path [:user]}]}
```

## When to Use Lacinia

**Use Lacinia when:**
- Building flexible APIs where clients control response shape
- Aggregating data from multiple sources/microservices
- Mobile backends (reduce over-fetching/under-fetching)
- Real-time applications (subscriptions)
- Complex nested data structures
- Multiple clients with different data needs
- Evolving APIs (add fields without breaking clients)

**Use REST when:**
- Simple CRUD operations
- Caching is critical (HTTP caching well-understood)
- Team unfamiliar with GraphQL
- Simpler tooling/monitoring needs

**Consider alternatives**:
- **gRPC** - When performance and type safety are paramount
- **REST + JSON:API** - When REST conventions solve your problems
- **WebSockets** - For simple real-time updates without GraphQL overhead

## Best Practices

**Do:**
- Keep resolvers simple and focused (single responsibility)
- Use async resolvers for I/O operations
- Leverage DataLoader pattern for batching (via lacinia or external)
- Define clear error messages with actionable information
- Use input objects for complex mutation arguments
- Document schema with `:description` fields
- Test resolvers independently from GraphQL layer
- Use fragments to avoid duplication in queries

```clojure
;; Good: simple focused resolver
(defn get-user [context {:keys [id]} value]
  (db/find-user (:db context) id))

;; Good: async for I/O
(defn get-user-async [context {:keys [id]} value]
  (resolve/with-promise
    (db/find-user-async (:db context) id)
    identity))

;; Good: descriptive schema
{:objects
 {:User
  {:description "A registered user of the system"
   :fields {:id {:type '(non-null Int)
                 :description "Unique user identifier"}
            :name {:type '(non-null String)
                   :description "User's display name"}}}}}
```

**Don't:**
- Mix business logic into resolvers (keep in domain layer)
- Return raw database entities (transform to GraphQL types)
- Ignore null/non-null in type definitions (be explicit)
- Over-nest schema (keep it reasonably flat)
- Expose internal IDs directly (use opaque IDs or encrypt)
- Forget to handle errors (always return useful messages)
- Block on synchronous I/O in resolvers (use async)

```clojure
;; Bad: business logic in resolver
(defn create-user [context {:keys [input]} value]
  (let [user (validate-email (:email input))  ; Business logic
        hashed (hash-password (:password input))]  ; Business logic
    (db/save-user user)))

;; Good: separate concerns
(defn create-user [context {:keys [input]} value]
  (let [user (user-service/create (:user-service context) input)]
    user))

;; Bad: exposing raw database entity
(defn get-user [context {:keys [id]} value]
  (db/find-user id))  ; Returns internal DB record

;; Good: transform to GraphQL type
(defn get-user [context {:keys [id]} value]
  (when-let [db-user (db/find-user id)]
    {:id (:user_id db-user)
     :name (:full_name db-user)
     :email (:email_address db-user)}))
```

## Common Issues

### Issue: "Field cannot be resolved"

```clojure
;; Error: No resolver for User/posts
```

**Solution**: Provide resolver for the field:

```clojure
(inject-resolvers schema-def
  {:User/posts (fn [context args user]
                 (fetch-posts-for-user (:id user)))})
```

### Issue: "Cannot return null for non-null field"

```clojure
;; Schema: {:type '(non-null String)}
;; Resolver returns: nil
```

**Solution**: Either make field nullable or ensure resolver never returns nil:

```clojure
;; Option 1: Make nullable
{:type 'String}

;; Option 2: Provide default
(defn get-name [context args user]
  (or (:name user) "Unknown"))

;; Option 3: Return error
(defn get-name [context args user]
  (if-let [name (:name user)]
    name
    (resolve/resolve-as nil {:message "Name is required"})))
```

### Issue: N+1 query problem

```clojure
;; Query asks for 100 users, each with their posts
;; Naive resolver makes 100+ database queries
```

**Solution**: Use batching/DataLoader pattern:

```clojure
(require '[com.walmartlabs.lacinia.resolve :as resolve])

;; Batch loading function
(defn batch-load-posts [context user-ids]
  ;; Single query: SELECT * FROM posts WHERE user_id IN (...)
  (let [posts-by-user (db/fetch-posts-for-users user-ids)]
    ;; Return map of user-id -> posts
    posts-by-user))

;; Resolver using batch loading
(defn get-user-posts [context args user]
  (let [batch-fn (get context :batch-posts)]
    ;; Lacinia will automatically batch these calls
    (batch-fn (:id user))))
```

**Better**: Use a dedicated DataLoader library or implement request-scoped caching.

### Issue: Circular schema references

```clojure
;; User has posts, Post has author (User)
;; How to define without forward declaration?
```

**Solution**: Lacinia handles this automatically - use keywords:

```clojure
{:objects
 {:User
  {:fields {:posts {:type '(list :Post)}}}  ; Reference by keyword
  
  :Post
  {:fields {:author {:type :User}}}}}  ; Reference by keyword
```

### Issue: Resolver blocking on sync I/O

```clojure
(defn get-user [context {:keys [id]} value]
  @(http/get (str "https://api.example.com/users/" id)))  ; Blocks!
```

**Solution**: Use async resolvers:

```clojure
(defn get-user [context {:keys [id]} value]
  (resolve/with-promise
    (http/get-async (str "https://api.example.com/users/" id))
    (fn [response]
      (resolve/resolve-as (:body response)))))
```

### Issue: Variables not working

```clojure
;; Query with variable not being substituted
(lacinia/execute schema
  "query GetUser($id: Int!) { user(id: $id) { name } }"
  {:id 123}  ; Variables
  nil)
```

**This is correct!** Variables are the second argument to `execute`:

```clojure
(lacinia/execute schema query-string variables context)
                                    ^^^^^^^^^ 2nd arg
```

### Issue: Schema compilation errors

```clojure
;; Error: "Unknown type :Usr"
```

**Solution**: Fix typo in type reference:

```clojure
;; Wrong
{:fields {:author {:type :Usr}}}

;; Right
{:fields {:author {:type :User}}}
```

## Advanced Topics

### Custom Scalars

Define custom scalar types:

```clojure
(require '[com.walmartlabs.lacinia.schema :as schema])

;; Date scalar
(def parse-date
  (schema/as-conformer
    (fn [value]
      ;; Parse from GraphQL (string) to Clojure (Date)
      (try
        (java.time.LocalDate/parse value)
        (catch Exception e
          (schema/validation-error (str "Invalid date: " value)))))))

(def serialize-date
  (fn [value]
    ;; Serialize from Clojure (Date) to GraphQL (string)
    (str value)))

(def schema-def
  {:scalars
   {:Date
    {:parse parse-date
     :serialize serialize-date}}
   
   :objects
   {:User
    {:fields {:birthDate {:type :Date}}}}})
```

### Subscriptions (Real-time)

Implement GraphQL subscriptions:

```clojure
(require '[com.walmartlabs.lacinia.resolve :as resolve]
         '[clojure.core.async :as async])

;; Streamer function (returns source-stream)
(defn user-updates-stream [context {:keys [userId]} source-value]
  (let [ch (async/chan 10)]
    ;; Start listening to updates
    (start-listening-to-user-updates! userId ch)
    
    ;; Return source-stream
    (resolve/resolve-as ch)))

;; Schema with subscription
{:subscriptions
 {:userUpdated
  {:type :User
   :args {:userId {:type '(non-null Int)}}
   :stream :subscription/user-updates}}}

;; Client subscribes
;; subscription { userUpdated(userId: 123) { id name } }
```

**Note**: Requires lacinia-pedestal or custom WebSocket handling.

### Schema from GraphQL SDL

Load schema from GraphQL schema definition language:

```clojure
(require '[com.walmartlabs.lacinia.schema :as schema]
         '[com.walmartlabs.lacinia.parser.schema :as parser])

(def sdl "
  type User {
    id: Int!
    name: String!
    email: String
  }
  
  type Query {
    user(id: Int!): User
  }
")

(def schema
  (-> (parser/parse-schema sdl)
      (inject-resolvers {:Query/user get-user})
      schema/compile))
```

### Field Middleware

Transform resolver behavior:

```clojure
(defn timing-middleware [resolver]
  (fn [context args value]
    (let [start (System/currentTimeMillis)
          result (resolver context args value)
          elapsed (- (System/currentTimeMillis) start)]
      (println "Resolver took" elapsed "ms")
      result)))

;; Apply to all resolvers during compilation
(defn wrap-resolvers [schema]
  (schema/compile schema
    {:default-field-resolver timing-middleware}))
```

## Related Libraries

- **lacinia-pedestal** - HTTP server integration with Pedestal
- **duct-lacinia** - Integration with Duct framework
- **venia** - Clojure(Script) GraphQL query generation
- **graphql-builder** - Programmatic query building

## Resources

- Documentation: https://lacinia.readthedocs.io/en/latest/
- Tutorial: https://lacinia.readthedocs.io/en/latest/tutorial/
- API Docs: https://walmartlabs.github.io/apidocs/lacinia/
- GitHub: https://github.com/walmartlabs/lacinia
- GraphQL Spec: https://spec.graphql.org/

## Summary

Lacinia is the production-ready GraphQL implementation for Clojure:

1. **Full GraphQL spec** - Queries, mutations, subscriptions, introspection
2. **EDN schemas** - Define schemas as Clojure data structures
3. **Async execution** - Efficient parallel resolver execution
4. **Type safety** - Strong type system with compile-time validation
5. **Backend-agnostic** - Use with any web framework
6. **Flexible resolvers** - Sync or async, simple functions
7. **Custom scalars** - Extend type system for domain needs

**Most common patterns:**

```clojure
;; Define schema
(def schema-def
  {:objects {:User {:fields {...}}}
   :queries {:user {:type :User :args {...} :resolve :query/user}}
   :mutations {:createUser {:type :User :args {...} :resolve :mutation/create}}})

;; Implement resolvers
(defn get-user [context {:keys [id]} value]
  (fetch-user id))

;; Compile schema
(def schema
  (-> schema-def
      (inject-resolvers {:query/user get-user
                         :mutation/create create-user})
      schema/compile))

;; Execute queries
(lacinia/execute schema query-string variables context)

;; Async resolver
(defn get-user-async [context args value]
  (resolve/with-promise
    (fetch-user-async id)
    identity))
```

Perfect for flexible APIs, microservices aggregation, mobile backends, and any application where clients need precise control over data shape and real-time updates.
