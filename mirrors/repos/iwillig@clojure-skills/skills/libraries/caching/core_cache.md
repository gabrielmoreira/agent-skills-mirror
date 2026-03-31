---
name: core-cache
description: |
  In-memory caching library implementing various cache strategies (FIFO, LRU, LU, TTL, LIRS).
  Use when implementing caching, memoization, performance optimization, in-memory storage, or
  when the user mentions cache, caching strategies, cache eviction, LRU, FIFO, TTL, memoization,
  performance tuning, or temporary data storage.
---

# clojure.core.cache

A Clojure contrib library providing pluggable in-memory caching with various eviction strategies.

## Quick Start

core.cache provides immutable cache implementations with multiple eviction strategies.

```clojure
;; Add dependency
{:deps {org.clojure/core.cache {:mvn/version "1.1.234"}}}

;; Immutable API - manage caches yourself
(require '[clojure.core.cache :as cache])

(def C (cache/lru-cache-factory {:a 1 :b 2} :threshold 3))

;; Check if key exists
(cache/has? C :a)
;; => true

;; Lookup value
(cache/lookup C :a)
;; => 1

;; Add to cache (returns new cache)
(def C' (cache/miss C :c 42))
;; => {:a 1, :b 2, :c 42}

;; Or use wrapped API with atoms (recommended for most use cases)
(require '[clojure.core.cache.wrapped :as w])

;; Cache automatically wrapped in atom
(def cache (w/lru-cache-factory {:a 1 :b 2} :threshold 3))

;; Lookup with automatic miss handling
(w/lookup-or-miss cache :c (constantly 42))
;; => 42

@cache
;; => {:a 1, :b 2, :c 42}
```

**Key benefits:**
- Multiple eviction strategies (FIFO, LRU, LU, TTL, LIRS)
- Immutable by default with wrapped API for convenience
- Protocol-based for custom implementations
- Thread-safe when used with atoms
- No external dependencies

## Core Concepts

### Immutable vs Wrapped API

**Immutable API (`clojure.core.cache`):**
- Caches are immutable data structures
- Operations return new cache instances
- You manage storage (typically with atoms)
- Full control over state management

**Wrapped API (`clojure.core.cache.wrapped`):**
- Caches wrapped in atoms automatically
- Operations modify the atom and return values
- More convenient for typical use cases
- Includes `lookup-or-miss` to prevent cache stampede

**When to use each:**
- Use **wrapped API** for most applications (simpler, safer)
- Use **immutable API** when you need custom state management or to compose with other stateful abstractions

### Cache Strategies

core.cache provides several cache eviction strategies:

**BasicCache** - No eviction, grows unbounded:
```clojure
(def basic (cache/basic-cache-factory {:a 1 :b 2}))
```

**FIFOCache** - First In, First Out eviction:
```clojure
;; Evicts oldest entries when threshold reached
(def fifo (cache/fifo-cache-factory {} :threshold 100))
```

**LRUCache** - Least Recently Used eviction:
```clojure
;; Evicts least recently accessed entries
(def lru (cache/lru-cache-factory {} :threshold 100))
```

**LUCache** - Least Used (Least Frequently Used) eviction:
```clojure
;; Evicts entries with lowest access count
(def lu (cache/lu-cache-factory {} :threshold 100))
```

**TTLCacheQ** - Time To Live eviction:
```clojure
;; Evicts entries after time expires
(def ttl (cache/ttl-cache-factory {} :ttl 5000)) ; 5 seconds
```

**LIRSCache** - Low Inter-Reference Recency Set:
```clojure
;; Advanced algorithm balancing recency and frequency
(def lirs (cache/lirs-cache-factory {}
            :s-history-limit 100
            :q-history-limit 100))
```

**SoftCache** - Garbage collection managed:
```clojure
;; Entries evicted by JVM GC when memory pressure occurs
(def soft (cache/soft-cache-factory {}))
```

### Cache Operations

**Core operations:**
- `has?` - Check if key exists
- `lookup` - Get value for key
- `hit` - Called when cache contains key (updates access tracking)
- `miss` - Called when cache doesn't contain key (adds value)
- `evict` - Manually remove entry
- `seed` - Initialize with new base map

## Common Workflows

### Workflow 1: Basic Caching with Wrapped API

The wrapped API is recommended for most use cases:

```clojure
(require '[clojure.core.cache.wrapped :as w])

;; Create cache
(def user-cache (w/lru-cache-factory {} :threshold 1000))

;; Lookup with automatic miss handling
(defn get-user [user-id]
  (w/lookup-or-miss user-cache user-id
    (fn [id]
      ;; This function only called on cache miss
      ;; and guaranteed to run at most once even with retries
      (fetch-user-from-db id))))

;; Use the cache
(get-user 123)
;; => {:id 123, :name "Alice", :email "alice@example.com"}

;; Second call hits cache
(get-user 123)
;; => {:id 123, :name "Alice", :email "alice@example.com"}

;; Check cache contents
@user-cache
;; => {123 {:id 123, :name "Alice", :email "alice@example.com"}}

;; Manually evict
(w/evict user-cache 123)
```

### Workflow 2: Using Immutable API with Atoms

For more control over state management:

```clojure
(require '[clojure.core.cache :as cache])

;; Create cache wrapped in atom
(def C (atom (cache/lru-cache-factory {} :threshold 100)))

;; Check-hit-miss pattern (manual)
(defn get-cached [key fetch-fn]
  (if (cache/has? @C key)
    (do
      (swap! C cache/hit key)
      (cache/lookup @C key))
    (let [value (fetch-fn key)]
      (swap! C cache/miss key value)
      value)))

;; Or use through-cache helper
(swap! C cache/through-cache :user-1
  (fn [k] (fetch-user-from-db k)))

;; Get result
(cache/lookup @C :user-1)
```

### Workflow 3: TTL Cache for Temporary Data

Cache data that expires after a time period:

```clojure
(require '[clojure.core.cache.wrapped :as w])

;; Create TTL cache with 5-minute expiration
(def session-cache
  (w/ttl-cache-factory {} :ttl (* 5 60 1000)))

;; Store session
(w/lookup-or-miss session-cache "session-123"
  (constantly {:user-id 456 :created-at (System/currentTimeMillis)}))

;; Access within TTL
(w/lookup session-cache "session-123")
;; => {:user-id 456, :created-at ...}

;; After 5 minutes, lookup returns nil (expired)
;; Then lookup-or-miss would regenerate
```

### Workflow 4: FIFO Cache for Event Buffers

Keep a fixed-size buffer of recent events:

```clojure
(require '[clojure.core.cache.wrapped :as w])

;; Keep last 100 events
(def event-cache (w/fifo-cache-factory {} :threshold 100))

;; Add events (older events evicted automatically)
(doseq [event (generate-events)]
  (w/miss event-cache (:id event) event))

;; Access recent events
@event-cache
;; => {event-95 {...}, event-96 {...}, ..., event-100 {...}}
```

### Workflow 5: Composing Caches

Combine multiple cache strategies:

```clojure
;; LRU cache with TTL
;; (wrap TTL around LRU)
(def cache-atom
  (atom (cache/ttl-cache-factory
          (cache/lru-cache-factory {} :threshold 1000)
          :ttl 60000))) ; 1 minute TTL

;; Entries evicted by LRU when over threshold
;; OR by TTL when they expire
```

### Workflow 6: Custom Cache Strategies

Extend CacheProtocol for custom eviction:

```clojure
(require '[clojure.core.cache :as cache])

;; Custom cache that evicts entries with specific predicate
(cache/defcache CustomCache [cache pred]
  cache/CacheProtocol
  (lookup [_ key]
    (get cache key))
  (lookup [_ key not-found]
    (get cache key not-found))
  (has? [_ key]
    (contains? cache key))
  (hit [this key]
    this)
  (miss [_ key value]
    (let [new-cache (assoc cache key value)
          ;; Remove entries matching predicate
          filtered (into {} (remove (fn [[k v]] (pred k v)) new-cache))]
      (CustomCache. filtered pred)))
  (evict [_ key]
    (CustomCache. (dissoc cache key) pred))
  (seed [_ base]
    (CustomCache. base pred)))

;; Use custom cache
(def custom (CustomCache. {} (fn [k v] (> (count v) 100))))
```

### Workflow 7: Soft Cache for Memory-Sensitive Applications

Let JVM manage cache eviction based on memory:

```clojure
(require '[clojure.core.cache.wrapped :as w])

;; Soft cache uses SoftReferences
;; JVM can garbage collect entries when memory is low
(def image-cache (w/soft-cache-factory {}))

;; Store large objects
(w/lookup-or-miss image-cache "image-1"
  (fn [_] (load-large-image "path/to/image.png")))

;; Access normally
(w/lookup image-cache "image-1")
;; => <image data>

;; If memory pressure occurs, JVM may evict entries
;; Next lookup would return nil, triggering reload
```

## When to Use Each Cache Type

**Use BasicCache when:**
- Prototyping or testing
- Cache never needs eviction
- You control cache clearing manually

**Use FIFOCache when:**
- Order of insertion matters
- Simple eviction strategy needed
- Implementing event buffers or logs

**Use LRUCache when:**
- Access patterns follow temporal locality
- Recent items more likely to be reused
- Most common general-purpose cache
- Examples: user sessions, API responses, computed results

**Use LUCache when:**
- Frequency matters more than recency
- Popular items should stay cached longer
- Examples: page view counts, product catalogs

**Use TTLCacheQ when:**
- Data becomes stale after time period
- Need automatic expiration
- Examples: API tokens, temporary sessions, rate limiting

**Use LIRSCache when:**
- Need optimal hit rate
- Working set has both frequently and recently used items
- Willing to accept slightly higher overhead
- Examples: large databases, file systems, web caches

**Use SoftCache when:**
- Caching expensive-to-compute values
- Memory availability is unpredictable
- Acceptable for cache to be cleared by GC
- Examples: image thumbnails, parsed documents

## Best Practices

**DO:**
- Use wrapped API (`clojure.core.cache.wrapped`) for simpler code
- Use `lookup-or-miss` to prevent cache stampede
- Choose cache strategy based on access patterns
- Set appropriate threshold sizes to limit memory
- Use TTL for time-sensitive data
- Wrap LRU/FIFO/LU with TTL when you need both size and time limits
- Test cache hit rates to tune thresholds
- Use atoms or refs to manage cache state safely

**DON'T:**
- Use BasicCache in production without size limits
- Forget to handle `nil` values (cache miss vs cached `nil`)
- Mix wrapped and immutable APIs on the same cache
- Use very small thresholds (< 10) - defeats caching purpose
- Cache sensitive data without encryption
- Use SoftCache for critical data (GC may evict anytime)
- Use shared mutable state without proper synchronization

## Common Issues

### Issue: Cache Miss Returns Nil But Value Was Cached

**Problem:** TTL cache can invalidate entries on lookup.

```clojure
(def C (w/ttl-cache-factory {:a 1} :ttl 1000))

;; Wait > 1 second
(Thread/sleep 1100)

;; Lookup returns nil (entry expired)
(w/lookup C :a)
;; => nil
```

**Solution:** Use `lookup-or-miss` which handles TTL expiration correctly.

```clojure
(w/lookup-or-miss C :a (constantly 1))
;; Automatically regenerates on expiration
```

### Issue: Cache Growing Beyond Expected Size

**Problem:** Threshold not respected or misunderstood.

```clojure
;; This cache can grow beyond 100 entries temporarily
(def C (cache/lru-cache-factory {} :threshold 100))
```

**Solution:** Threshold is when eviction *starts*, not hard limit. Ensure proper understanding:
- FIFO/LRU/LU evict one entry when threshold exceeded
- Set threshold lower than absolute maximum
- Monitor cache size: `(count @cache)`

### Issue: Poor Cache Hit Rate

**Problem:** Wrong eviction strategy for access pattern.

```clojure
;; Using FIFO for frequently-accessed recent items
(def C (w/fifo-cache-factory {} :threshold 100))

;; Better: use LRU
(def C (w/lru-cache-factory {} :threshold 100))
```

**Solution:** Match strategy to access pattern:
- Random access: LRU or LIRS
- Sequential access: FIFO
- Frequency-based: LU
- Time-sensitive: TTL

### Issue: Race Condition on Cache Miss

**Problem:** Multiple threads computing same value.

```clojure
;; BAD: race condition
(if (not (cache/has? @C key))
  (let [value (expensive-computation key)]
    (swap! C cache/miss key value)))
```

**Solution:** Use `lookup-or-miss` (wrapped API) which uses delays:

```clojure
(w/lookup-or-miss C key expensive-computation)
;; Value function called at most once even with concurrent access
```

### Issue: Cache Not Evicting Old Entries

**Problem:** Forgot to call `hit` after lookup in immutable API.

```clojure
;; BAD: lookup doesn't update LRU metadata
(cache/lookup @C key)

;; GOOD: call hit to update access tracking
(when (cache/has? @C key)
  (swap! C cache/hit key)
  (cache/lookup @C key))
```

**Solution:** Use wrapped API or `through-cache` helper to handle correctly.

## Advanced Topics

### Cache Composition

Layer cache strategies for complex policies:

```clojure
;; LRU with TTL with size limit
(-> {}
    (cache/lru-cache-factory :threshold 1000)
    (cache/ttl-cache-factory :ttl 300000))
```

### Integration with Memoization

Use core.cache for smarter memoization:

```clojure
(defn memo-lru [f limit]
  (let [cache (atom (cache/lru-cache-factory {} :threshold limit))]
    (fn [& args]
      (if (cache/has? @cache args)
        (do
          (swap! cache cache/hit args)
          (cache/lookup @cache args))
        (let [result (apply f args)]
          (swap! cache cache/miss args result)
          result)))))

(def expensive-fn-cached (memo-lru expensive-fn 100))
```

### Metrics and Monitoring

Track cache performance:

```clojure
(def cache-stats (atom {:hits 0 :misses 0}))

(defn get-with-stats [cache key fetch-fn]
  (if (cache/has? @cache key)
    (do
      (swap! cache-stats update :hits inc)
      (swap! cache cache/hit key)
      (cache/lookup @cache key))
    (let [value (fetch-fn key)]
      (swap! cache-stats update :misses inc)
      (swap! cache cache/miss key value)
      value)))

;; Check hit rate
(let [{:keys [hits misses]} @cache-stats]
  (/ hits (+ hits misses)))
```

## Resources

- [GitHub Repository](https://github.com/clojure/core.cache)
- [API Documentation](https://cljdoc.org/d/org.clojure/core.cache)
- [LIRS Paper](http://citeseer.ist.psu.edu/viewdoc/summary?doi=10.1.1.116.2184) - Algorithm behind LIRSCache
- [core.cache API Blog Post](https://dev.to/dpsutton/exploring-the-core-cache-api-57al) - Why API is hard to use correctly

## Summary

clojure.core.cache provides flexible in-memory caching with multiple eviction strategies:

1. **Choose strategy** - FIFO, LRU, LU, TTL, LIRS, Soft based on access pattern
2. **Use wrapped API** - `clojure.core.cache.wrapped` for simpler, safer code
3. **Use lookup-or-miss** - Prevents cache stampede and handles edge cases
4. **Set thresholds** - Control memory usage with appropriate size limits
5. **Compose strategies** - Layer TTL with LRU/FIFO for complex policies
6. **Monitor hit rates** - Tune cache configuration based on metrics

Most common pattern:

```clojure
(require '[clojure.core.cache.wrapped :as w])

(def cache (w/lru-cache-factory {} :threshold 1000))

(defn get-cached [key]
  (w/lookup-or-miss cache key expensive-fetch-fn))
```
