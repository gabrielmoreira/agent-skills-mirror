# Synchronization Primitives

Low-level synchronization tools for protecting shared mutable state when actors
are not the right fit. All primitives discussed here are `Sendable` and safe
to use from multiple threads.

## Contents

- [Mutex](#mutex)
- [OSAllocatedUnfairLock](#osallocatedunfairlock)
- [Atomic](#atomic)
- [Locks vs Actors: When to Use Each](#locks-vs-actors-when-to-use-each)

## Mutex

**Module:** `Synchronization` · **Availability:** iOS 18.0+

`Mutex<Value>` is a synchronization primitive that protects shared mutable
state via mutual exclusion. It blocks threads attempting to acquire the lock,
ensuring only one execution context accesses the protected value at a time.

**Documentation:**
[sosumi.ai/documentation/synchronization/mutex](https://sosumi.ai/documentation/synchronization/mutex)

### Basic Usage

```swift
import Synchronization

class ImageCache: Sendable {
    let storage = Mutex<[String: UIImage]>([:])

    func image(forKey key: String) -> UIImage? {
        storage.withLock { $0[key] }
    }

    func store(_ image: UIImage, forKey key: String) {
        storage.withLock { $0[key] = image }
    }

    func removeAll() {
        storage.withLock { $0.removeAll() }
    }
}
```

### withLockIfAvailable

Use `withLockIfAvailable` to attempt acquisition without blocking. Returns
`nil` if the lock is already held.

```swift
let counter = Mutex<Int>(0)

// Non-blocking attempt — returns nil if lock is contended
if let value = counter.withLockIfAvailable({ $0 }) {
    print("Current count: \(value)")
} else {
    print("Lock was busy, skipping")
}
```

### Key Properties

- **Generic over `Value`:** The protected state is stored inside the mutex,
  making it clear what the lock protects.
- **`Sendable`:** `Mutex` conforms to `Sendable`, so it can be stored in
  `Sendable` types (classes, actors, global state).
- **Non-recursive:** Attempting to lock a `Mutex` that you already hold on the
  same thread is undefined behavior.
- **Synchronous only:** Do not `await` inside `withLock`. The lock is held for
  the duration of the closure — blocking across a suspension point will
  deadlock or starve other threads.

## OSAllocatedUnfairLock

**Module:** `os` · **Availability:** iOS 16.0+

`OSAllocatedUnfairLock<State>` wraps `os_unfair_lock` in a safe Swift API.
It heap-allocates the underlying lock, avoiding the unsound address-of
problem that makes raw `os_unfair_lock` unusable from Swift.

**Documentation:**
[sosumi.ai/documentation/os/osallocatedunfairlock](https://sosumi.ai/documentation/os/osallocatedunfairlock)

### State-Protecting Lock

```swift
import os

enum LoadState: Sendable {
    case idle
    case loading
    case complete(Data)
    case failed(Error)
}

final class ResourceLoader: Sendable {
    let state = OSAllocatedUnfairLock(initialState: LoadState.idle)

    func beginLoading() {
        state.withLock { $0 = .loading }
    }

    func completeLoading(with data: Data) {
        state.withLock { $0 = .complete(data) }
    }

    var currentState: LoadState {
        state.withLock { $0 }
    }
}
```

### Stateless Lock

When protecting external state or a code section rather than a specific value:

```swift
let lock = OSAllocatedUnfairLock()

lock.withLock {
    // Critical section — no associated state
    writeToSharedFile(data)
}
```

### Manual lock/unlock

Available but discouraged. Must unlock from the same thread that locked.
**Never** use across `await` suspension points.

```swift
lock.lock()
defer { lock.unlock() }
// Critical section
```

### Mutex vs OSAllocatedUnfairLock

| | `Mutex<Value>` | `OSAllocatedUnfairLock<State>` |
|---|---|---|
| **Availability** | iOS 18+ | iOS 16+ |
| **Module** | `Synchronization` | `os` |
| **State model** | Value stored inside lock (generic `Value`) | Optional state via `initialState:` |
| **`withLockIfAvailable`** | Returns `nil` on contention | Returns `nil` on contention |
| **Ownership assertions** | Not available | `precondition(.owner)` / `precondition(.notOwner)` |
| **Manual lock/unlock** | Not available | Available (`lock()` / `unlock()`) |
| **Recommendation** | Preferred for iOS 18+ code | Use when targeting iOS 16–17 |

**Guideline:** Use `Mutex` for new code targeting iOS 18+. Use
`OSAllocatedUnfairLock` when you need to support iOS 16–17, or when you need
ownership assertions for debugging.

## Atomic

**Module:** `Synchronization` · **Availability:** iOS 18.0+

`Atomic<Value>` provides lock-free atomic operations on values conforming to
`AtomicRepresentable`. Use atomics for simple counters, flags, and
compare-and-swap patterns where a full lock would be overkill.

**Documentation:**
[sosumi.ai/documentation/synchronization/atomic](https://sosumi.ai/documentation/synchronization/atomic)

### Counter Example

```swift
import Synchronization

final class RequestTracker: Sendable {
    let activeRequests = Atomic<Int>(0)

    func beginRequest() {
        activeRequests.wrappingAdd(1, ordering: .relaxed)
    }

    func endRequest() {
        activeRequests.wrappingSubtract(1, ordering: .relaxed)
    }

    var count: Int {
        activeRequests.load(ordering: .relaxed)
    }
}
```

### Boolean Flag

```swift
let isShutdown = Atomic<Bool>(false)

func shutdown() {
    let (exchanged, _) = isShutdown.compareExchange(
        expected: false,
        desired: true,
        ordering: .acquiringAndReleasing
    )
    guard exchanged else { return } // Already shut down
    performCleanup()
}
```

### Memory Ordering

Atomic operations require an explicit memory ordering:

| Ordering | Use case |
|---|---|
| `.relaxed` | Counters, statistics — no ordering guarantees needed |
| `.acquiring` | Read that must see all writes before a corresponding release |
| `.releasing` | Write that must be visible to a corresponding acquire |
| `.acquiringAndReleasing` | Compare-and-swap, read-modify-write |
| `.sequentiallyConsistent` | Strongest guarantee — rarely needed |

**Guideline:** Use `.relaxed` for simple counters. Use
`.acquiringAndReleasing` for compare-and-swap patterns. Avoid
`.sequentiallyConsistent` unless you have a proven need — it is the most
expensive ordering.

### When to Use Atomics vs Mutex

- **Atomics:** Simple scalar values (Int, Bool, UInt64), single-field updates,
  counters, flags. Lock-free and very fast.
- **Mutex:** Compound state (dictionaries, structs with multiple fields),
  multi-step operations that must be atomic as a group.

## Locks vs Actors: When to Use Each

### Use Actors When:

- **Async isolation is natural.** The protected state is accessed from async
  contexts and you can afford the hop.
- **Structured concurrency.** You want the compiler to enforce isolation
  boundaries and prevent data races statically.
- **Most Swift code.** Actors are the default recommendation for shared mutable
  state in Swift concurrency.
- **Complex state with multiple methods.** Actor isolation protects all
  properties and methods automatically.

```swift
// GOOD: Actor for a cache accessed from async contexts
actor ImageDownloader {
    private var cache: [URL: UIImage] = [:]

    func image(for url: URL) async throws -> UIImage {
        if let cached = cache[url] { return cached }
        let (data, _) = try await URLSession.shared.data(from: url)
        let image = UIImage(data: data)!
        cache[url] = image
        return image
    }
}
```

### Use Mutex / Locks When:

- **Synchronous access is required.** Callers cannot (or should not) be async.
  Accessing an actor from synchronous code requires `Task` and introduces
  unwanted asynchrony.
- **Performance-critical paths.** Lock acquisition is nanoseconds; actor hops
  involve task scheduling. For tight loops or high-frequency access, a lock
  may be significantly faster.
- **Bridging with C/ObjC.** C callbacks, delegate methods, or ObjC APIs that
  cannot be made async.
- **Simple counters or flags.** `Atomic<Int>` or `Atomic<Bool>` is cheaper and
  simpler than creating an actor for a single value.

```swift
// GOOD: Mutex for synchronous, high-frequency access
final class MetricsCollector: Sendable {
    let metrics = Mutex<[String: Int]>([:])

    // Called from tight loops, C callbacks, or synchronous code
    func increment(_ key: String) {
        metrics.withLock { $0[key, default: 0] += 1 }
    }

    func snapshot() -> [String: Int] {
        metrics.withLock { $0 }
    }
}
```

### Decision Guide

```text
Need shared mutable state protection?
├── Can all access be async?
│   ├── Yes → Use an actor
│   └── No → Use Mutex or OSAllocatedUnfairLock
├── Single scalar value (counter, flag)?
│   └── Use Atomic<Value>
├── Performance-critical (nanosecond-level)?
│   └── Use Mutex or Atomic
└── Bridging C/ObjC callbacks?
    └── Use Mutex or OSAllocatedUnfairLock
```

### Anti-Patterns

**Never put locks inside actors.** An actor already serializes access; adding
a lock creates double synchronization and risks deadlocks.

```swift
// WRONG: Lock inside an actor — double synchronization
actor BadCache {
    let lock = Mutex<[String: Data]>([:])  // Unnecessary!
    // The actor already protects its state
}

// CORRECT: Just use the actor's built-in isolation
actor GoodCache {
    var cache: [String: Data] = [:]

    func store(_ data: Data, key: String) {
        cache[key] = data
    }
}
```

**Never use `DispatchSemaphore` or `NSLock` in modern Swift.** Use `Mutex`
(iOS 18+) or `OSAllocatedUnfairLock` (iOS 16+) instead. Legacy lock types
have no `Sendable` conformance and are not designed for structured
concurrency.

**Never hold a lock across `await`.** This blocks the thread and can deadlock
the cooperative thread pool.

```swift
// WRONG: Holding lock across suspension point
mutex.withLock { value in
    value = await fetchData()  // DEADLOCK RISK
}

// CORRECT: Fetch first, then lock to update
let data = await fetchData()
mutex.withLock { value in
    value = data
}
```
