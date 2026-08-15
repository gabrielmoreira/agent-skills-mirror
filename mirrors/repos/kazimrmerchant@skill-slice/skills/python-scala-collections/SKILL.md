---
name: python-scala-collections
version: 1.1.1
description: "Maps Python list, dict, and set operations onto Scala List, Map, and Set: typed empty creation, map/filter/foldLeft, lift/getOrElse, groupBy, zipWithIndex field order, and local ListBuffer snapshots. Use when the port's data-structure layer is the gap. Do not use for class/trait OOP, type-class or LazyList functional ports, or camelCase Pythonism cleanup."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Python to Scala Collections Translation

Python and Scala both ship rich collection libraries, but they start from opposite
defaults: Python collections are mutable and dynamically typed, whereas Scala
collections are immutable by default and statically typed. Because of that, a good
translation is never a token-for-token swap. It means picking the Scala construct
whose *semantics* match the original Python intent, and then writing the static types
down so the compiler can reject mistakes that Python would only reveal at runtime.

Keeping that goal in mind explains most of the choices in this guide: we annotate
element types, we prefer `Option` over throwing, and we reach for immutable
collections first. The sections below give side-by-side equivalents you can adapt,
along with the reasoning so you can make the right call when your case differs from
the example.

## When to Use

- Translating Python code that manipulates **lists**, **dictionaries**, **sets**, or
  performs collection transformations (map, filter, reduce, sorting, aggregations)
  into idiomatic Scala.
- When you need a side-by-side reference for equivalent collection APIs in both
  languages and want to understand *why* the idiomatic Scala form differs.
- When working on code migration, teaching, or writing interoperable libraries, where
  matching semantics matters more than matching syntax.

## Prerequisites

- A working Scala toolchain (Scala 2.13+ or Scala 3.x) for verifying snippets.
- Familiarity with Python type hints (`list[int]`, `dict[str, int]`, `set[int]`) and
  Scala basic syntax (`val`, `case class`, `Option`).
- For verification: a Scala REPL (`scala` CLI, Ammonite, or an IDE worksheet like
  Scastie) to paste and compile snippets.

## Procedure

### Conventions used throughout

Every snippet is written the way you would want it to pass code review, not as the
shortest thing that happens to run:

1. **Explicit element types.** Each Scala `val` and each Python binding is annotated
   (`val xs: List[Int] = List(1, 2, 3)`, `xs: list[int] = [1, 2, 3]`). Inference would
   compile without them, but writing the type down documents intent and stops a later
   refactor from silently widening a collection to `Any` / `object`.
2. **No `Any` / `object` element types.** A "record" that holds differently-typed fields
   (a name *and* an age) is modelled as a `case class` / `@dataclass`, never as
   `Map[String, Any]`. A `Map` should describe a *uniform* key→value relationship; a
   record should describe a *fixed* set of fields, each with its own type.
3. **`Option` instead of throwing or `null`.** Wherever Python would return `None` or
   raise, the Scala side returns `Option[A]` (`headOption`, `lastOption`, `find`, `get`,
   `lift`, `reduceOption`, `minOption`). This turns "what if it's missing?" into a
   compile-time question the caller must answer.
4. **Immutable by default.** Translations return new collections instead of mutating in
   place, because immutable values are safe to share across threads and easier to reason
   about. Mutable buffers appear only where they are local, short-lived, and never shared.

### Step 1 — Collection Creation

#### Lists

```python
# Python
empty: list[int] = []
nums: list[int] = [1, 2, 3]
repeated: list[int] = [0] * 5
from_range: list[int] = list(range(1, 11))  # 1..10 inclusive of 1, exclusive of 11
```

```scala
// Scala
val empty: List[Int] = List.empty[Int]      // List[Int]() is equivalent
val nums: List[Int] = List(1, 2, 3)
val repeated: List[Int] = List.fill(5)(0)    // five zeros
val fromRange: List[Int] = (1 to 10).toList  // `to` is inclusive on both ends
```

Why the empty list carries `[Int]`: `List.empty` with no type argument infers
`List[Nothing]`, which is rarely what you want once you start appending. Naming the
element type up front keeps the collection usable.

#### Dictionaries → Maps

A Python `dict` whose values share one type maps cleanly onto a Scala `Map`. A `dict`
whose values have *different* types (a string name next to an integer age) does not —
forcing it into a `Map` would infer `Map[String, Any]`, which throws away type safety.
Model that case as a record instead.

```python
# Python
from dataclasses import dataclass

empty: dict[str, int] = {}

# A genuine string -> int map keeps a single, explicit value type:
scores: dict[str, int] = {"math": 90, "science": 85}
from_pairs: dict[str, int] = dict([("a", 1), ("b", 2)])

# Mixed value types are a record, not a map — model them as a dataclass:
@dataclass(frozen=True)
class Person:
    name: str
    age: int

person: Person = Person(name="Alice", age=30)
```

```scala
// Scala
val empty: Map[String, Int] = Map.empty[String, Int]

// A genuine String -> Int map carries one explicit value type:
val scores: Map[String, Int] = Map("math" -> 90, "science" -> 85)
val fromPairs: Map[String, Int] = List(("a", 1), ("b", 2)).toMap

// Mixed value types are a record, not a Map[String, Any] — model them as a case class:
final case class Person(name: String, age: Int)

val person: Person = Person(name = "Alice", age = 30)
```

If you need ordered iteration (Python 3.7+ guarantees insertion order), reach for
`scala.collection.immutable.ListMap` for insertion order or `TreeMap` for sorted-by-key
order; the default `Map` makes no ordering promise.

#### Sets

```python
# Python
empty: set[int] = set()           # {} would be an empty dict, not a set
nums: set[int] = {1, 2, 3}
from_list: set[int] = set([1, 2, 2, 3])  # duplicates collapse to {1, 2, 3}
```

```scala
// Scala
val empty: Set[Int] = Set.empty[Int]
val nums: Set[Int] = Set(1, 2, 3)
val fromList: Set[Int] = List(1, 2, 2, 3).toSet  // deduplicates to Set(1, 2, 3)
```

Building a `Set` from a `List` is the idiomatic way to deduplicate, but note the default
`Set` is unordered. If you need a stable order, use `scala.collection.immutable.TreeSet`
(sorted) rather than relying on iteration order.

### Step 2 — Transformation Operations

#### Map

```python
# Python
nums: list[int] = [1, 2, 3]
doubled: list[int] = [x * 2 for x in nums]                 # comprehension is the idiom
doubled_alt: list[int] = list(map(lambda x: x * 2, nums))  # explicit map()
```

```scala
// Scala
val nums: List[Int] = List(1, 2, 3)
val doubled: List[Int] = nums.map(_ * 2)                 // `_` is the single argument
val doubledAlt: List[Int] = nums.map((x: Int) => x * 2)  // annotated for clarity
```

`map` returns a *new* `List`; the original `nums` is untouched. That immutability is why
you can safely reuse `nums` afterwards without worrying about who else mapped over it.

#### Filter

```python
# Python
evens: list[int] = [x for x in nums if x % 2 == 0]
evens_alt: list[int] = list(filter(lambda x: x % 2 == 0, nums))
```

```scala
// Scala
val evens: List[Int] = nums.filter(_ % 2 == 0)
val evensAlt: List[Int] = nums.filter((x: Int) => x % 2 == 0)
```

#### Reduce / Fold

```python
# Python
from functools import reduce

nums: list[int] = [1, 2, 3, 4]

# reduce WITHOUT an initializer raises TypeError on an empty sequence — supply one:
total: int = reduce(lambda a, b: a + b, nums, 0)  # 0 is the additive identity
total_builtin: int = sum(nums)
product: int = reduce(lambda a, b: a * b, nums, 1)  # 1 is the multiplicative identity
```

```scala
// Scala
val nums: List[Int] = List(1, 2, 3, 4)

// foldLeft takes an explicit zero, so it is TOTAL — it cannot throw on empty input:
val total: Int = nums.foldLeft(0)(_ + _)
val totalBuiltin: Int = nums.sum
val product: Int = nums.foldLeft(1)(_ * _)

// `reduce` has no zero and throws UnsupportedOperationException on an empty list.
// `reduceOption` returns None instead, which is the defensive choice at a boundary:
val maybeTotal: Option[Int] = nums.reduceOption(_ + _)
```

The recurring lesson: prefer `foldLeft` (or `reduceOption`) over bare `reduce` whenever
the collection *could* be empty, because supplying the identity value turns a runtime
exception into ordinary, total code.

#### FlatMap

```python
# Python
nested: list[list[int]] = [[1, 2], [3, 4]]
flat: list[int] = [x for sublist in nested for x in sublist]  # -> [1, 2, 3, 4]
```

```scala
// Scala
val nested: List[List[Int]] = List(List(1, 2), List(3, 4))
val flat: List[Int] = nested.flatten            // when there is no transformation
val flatAlt: List[Int] = nested.flatMap(identity)  // map-then-flatten in one pass
```

Use `flatten` when you only need to collapse one level of nesting, and `flatMap` when you
want to transform each element *and* flatten in a single traversal.

### Step 3 — Common Operations

#### Length / Size

| Python | Scala |
|--------|-------|
| `len(lst)` | `lst.length` or `lst.size` |
| `len(dct)` | `m.size` |
| `not lst` (emptiness check) | `lst.isEmpty` / `lst.nonEmpty` |

For a `List`, `length`/`size` are O(n) because the list must be traversed end to end. If
all you need is "is there anything here?", use `isEmpty` / `nonEmpty`, which are O(1) and
state the intent more clearly than `lst.size == 0`.

#### Access

Direct indexing is concise but *partial*: it throws when the index or key is missing. The
defensive column returns `Option`, which forces the caller to handle the missing case
explicitly instead of discovering it via an exception in production.

| Python | Scala (direct, may throw) | Scala (defensive, returns Option) |
|--------|---------------------------|-----------------------------------|
| `lst[0]` | `lst(0)` / `lst.head` | `lst.headOption: Option[A]` |
| `lst[-1]` | `lst.last` | `lst.lastOption: Option[A]` |
| `lst[i]` | `lst(i)` | `lst.lift(i): Option[A]` |
| `lst[1:3]` | `lst.slice(1, 3)` | `lst.slice(1, 3)` (already total) |
| `lst[:3]` | `lst.take(3)` | `lst.take(3)` (already total) |
| `lst[3:]` | `lst.drop(3)` | `lst.drop(3)` (already total) |
| `dct["key"]` | `m("key")` | `m.get("key"): Option[V]` |
| `dct.get("key")` | `m.get("key")` | already `Option[V]` |
| `dct.get("key", default)` | `m.getOrElse("key", default)` | `m.getOrElse("key", default)` |

```scala
// Scala — the difference between partial and total access
val nums: List[Int] = List(10, 20, 30)
val scores: Map[String, Int] = Map("math" -> 90)

// Partial: concise, but each of these throws NoSuchElementException on bad input.
val first: Int = nums.head           // throws if nums is empty
val mathScore: Int = scores("math")  // throws if the key is absent

// Total: prefer these at any boundary where emptiness or a missing key is possible.
val safeFirst: Option[Int] = nums.headOption        // None instead of throwing
val safeThird: Option[Int] = nums.lift(2)           // None if index 2 is out of range
val safeScore: Int = scores.getOrElse("history", 0) // a supplied default, never throws
```

#### Membership

```python
# Python
nums: list[int] = [1, 2, 3]
scores: dict[str, int] = {"math": 90, "science": 85}

x: int = 3
key: str = "math"

if x in nums:
    print(f"{x} is present in the list")

if key in scores:
    print(f"{key} maps to {scores[key]}")
```

```scala
// Scala
val nums: List[Int] = List(1, 2, 3)
val scores: Map[String, Int] = Map("math" -> 90, "science" -> 85)

val x: Int = 3
val key: String = "math"

if (nums.contains(x)) {
  println(s"$x is present in the list")
}

if (scores.contains(key)) {
  // contains() guarantees the key exists here, so scores(key) is safe.
  println(s"$key maps to ${scores(key)}")
}
```

`contains` for a `List` is O(n) (it scans), while for a `Set` or `Map` it is effectively
O(1). If you do a lot of membership tests, that is a reason to hold the data in a `Set`
rather than a `List` in the first place.

#### Concatenation

```python
# Python
list1: list[int] = [1, 2]
list2: list[int] = [3, 4]
combined: list[int] = list1 + list2

dict1: dict[str, int] = {"a": 1, "shared": 1}
dict2: dict[str, int] = {"b": 2, "shared": 2}
merged: dict[str, int] = {**dict1, **dict2}  # on conflict, dict2's value wins
```

```scala
// Scala
val list1: List[Int] = List(1, 2)
val list2: List[Int] = List(3, 4)
val combined: List[Int] = list1 ++ list2

val map1: Map[String, Int] = Map("a" -> 1, "shared" -> 1)
val map2: Map[String, Int] = Map("b" -> 2, "shared" -> 2)
val merged: Map[String, Int] = map1 ++ map2  // on conflict, the RIGHT operand wins
```

The conflict rule matches between the two languages: Python's `{**a, **b}` and Scala's
`a ++ b` both let the right-hand map override duplicate keys, so the translation is
semantically faithful and not just syntactically similar.

#### Sorting

```python
# Python
items: list[int] = [3, 1, 2]
sorted_list: list[int] = sorted(items)               # returns a new list
sorted_desc: list[int] = sorted(items, reverse=True)

people: list["Person"] = [Person("Bob", 25), Person("Alice", 30)]
sorted_by_key: list["Person"] = sorted(people, key=lambda p: p.name)

items.sort()  # in-place: this MUTATES `items` rather than returning a new list
```

```scala
// Scala
val items: List[Int] = List(3, 1, 2)
val sortedList: List[Int] = items.sorted
val sortedDesc: List[Int] = items.sorted(Ordering[Int].reverse)

val people: List[Person] = List(Person("Bob", 25), Person("Alice", 30))
val sortedByKey: List[Person] = people.sortBy(_.name)

// An immutable List has no in-place sort. `sorted` returns a NEW List and leaves
// `items` exactly as it was — which is precisely why it is safe to share `items`.
```

#### Grouping

```python
# Python
from collections import defaultdict
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    category: str
    name: str

items: list[Item] = [
    Item("fruit", "apple"),
    Item("veg", "carrot"),
    Item("fruit", "pear"),
]

# defaultdict spares you the "if key not present, create an empty list" boilerplate:
grouped: defaultdict[str, list[Item]] = defaultdict(list)
for item in items:
    grouped[item.category].append(item)
```

```scala
// Scala
final case class Item(category: String, name: String)

val items: List[Item] = List(
  Item("fruit", "apple"),
  Item("veg", "carrot"),
  Item("fruit", "pear"),
)

// groupBy does the whole job as one total expression — no mutation, no missing-key
// handling, because the resulting Map only ever contains keys that actually occurred:
val grouped: Map[String, List[Item]] = items.groupBy(_.category)
// grouped == Map("fruit" -> List(Item("fruit","apple"), Item("fruit","pear")),
//                "veg"   -> List(Item("veg","carrot")))
```

The Scala version is shorter for a reason worth internalizing: `groupBy` replaces the
imperative "look up, default, append" loop with a single declarative call, eliminating the
class of bugs that comes from forgetting to initialize a bucket.

#### Aggregations

```python
# Python
nums: list[int] = [4, 1, 7, 3]

total: int = sum(nums)
minimum: int = min(nums)  # raises ValueError on an empty list
maximum: int = max(nums)  # raises ValueError on an empty list

# Guard the division so an empty list cannot raise ZeroDivisionError:
average: float = sum(nums) / len(nums) if nums else 0.0
```

```scala
// Scala
val nums: List[Int] = List(4, 1, 7, 3)

val total: Int = nums.sum
val minimum: Option[Int] = nums.minOption  // None on empty, vs nums.min which throws
val maximum: Option[Int] = nums.maxOption  // None on empty, vs nums.max which throws

// Guard against division by zero exactly as the Python version does:
val average: Double =
  if (nums.nonEmpty) nums.sum.toDouble / nums.length else 0.0
```

`sum` is safe on an empty collection (it returns the zero of the element type), but `min`,
`max`, and the average all have a failure mode on empty input. `minOption`/`maxOption` and
the `nonEmpty` guard make those failure modes explicit instead of latent.

#### Finding Elements

```python
# Python
nums: list[int] = [1, 3, 4, 6]
first_even: int | None = next((x for x in nums if x % 2 == 0), None)  # None if no match
all_evens: bool = all(x % 2 == 0 for x in nums)
any_even: bool = any(x % 2 == 0 for x in nums)
```

```scala
// Scala
val nums: List[Int] = List(1, 3, 4, 6)
val firstEven: Option[Int] = nums.find(_ % 2 == 0)  // Option models "maybe absent"
val allEvens: Boolean = nums.forall(_ % 2 == 0)
val anyEven: Boolean = nums.exists(_ % 2 == 0)
```

`find` returns `Option[Int]` rather than a nullable sentinel, so the "no match" case is
part of the type. The caller cannot accidentally treat a missing result as a real value —
they have to unwrap the `Option` first.

#### Zipping

```python
# Python
list1: list[str] = ["a", "b", "c"]
list2: list[int] = [1, 2, 3]
pairs: list[tuple[str, int]] = list(zip(list1, list2))   # [("a",1), ("b",2), ("c",3)]
indexed: list[tuple[int, str]] = list(enumerate(list1))  # [(0,"a"), (1,"b"), (2,"c")]
```

```scala
// Scala
val list1: List[String] = List("a", "b", "c")
val list2: List[Int] = List(1, 2, 3)
val pairs: List[(String, Int)] = list1.zip(list2)        // List(("a",1), ("b",2), ("c",3))
val indexed: List[(String, Int)] = list1.zipWithIndex    // List(("a",0), ("b",1), ("c",2))
```

Watch the tuple order: Python's `enumerate` yields `(index, value)`, while Scala's
`zipWithIndex` yields `(value, index)`. They are mirror images, so a mechanical
translation that ignores this will swap the fields and produce a subtle bug.

### Step 4 — Dictionary / Map Operations

```python
# Python
def process(key: str, value: int) -> None:
    print(f"{key} -> {value}")

scores: dict[str, int] = {"math": 90, "science": 85}
keys: list[str] = list(scores.keys())
values: list[int] = list(scores.values())
items: list[tuple[str, int]] = list(scores.items())

for key, value in scores.items():
    process(key, value)

# Update — the first form mutates in place, the second returns a new dict:
scores["history"] = 88
updated: dict[str, int] = {**scores, "history": 88}
```

```scala
// Scala
def process(key: String, value: Int): Unit = println(s"$key -> $value")

val scores: Map[String, Int] = Map("math" -> 90, "science" -> 85)
val keys: List[String] = scores.keys.toList
val values: List[Int] = scores.values.toList
val entries: List[(String, Int)] = scores.toList  // List[(String, Int)]

for ((key, value) <- scores) {
  process(key, value)
}

// Update returns a NEW Map; `scores` itself is never modified:
val updated: Map[String, Int] = scores + ("history" -> 88)
val updatedAlt: Map[String, Int] = scores.updated("history", 88)
```

Because `+` and `updated` return fresh maps, you can derive `updated` without disturbing
`scores`. That is the structural reason Scala code rarely needs defensive copying: the
data was never shared mutably to begin with.

### Step 5 — Mutable vs Immutable

Python collections are mutable by default; Scala collections are immutable by default.
Immutable values are the safer starting point because they can be shared freely across
threads with no locking and cannot be changed out from under a caller. Reach for a mutable
collection only when it is genuinely local — built up inside a single method and never
escaping to other threads — and then hand back an immutable snapshot at the boundary.

```python
# Python — mutable in place
lst: list[int] = [1, 2, 3]
lst.append(4)
lst.extend([5, 6])

scores: dict[str, int] = {}
scores["key"] = 10
```

```scala
// Scala — immutable by default: each "modification" returns a new value
val lst: List[Int] = List(1, 2, 3)
val withFour: List[Int] = lst :+ 4            // append one element
val withMore: List[Int] = lst ++ List(5, 6)   // append several

val scores: Map[String, Int] = Map.empty[String, Int]
val withKey: Map[String, Int] = scores + ("key" -> 10)

// Scala — mutable, used ONLY as a local, short-lived buffer
import scala.collection.mutable

val buffer: mutable.ListBuffer[Int] = mutable.ListBuffer(1, 2, 3)
buffer += 4
buffer ++= List(5, 6)
val frozen: List[Int] = buffer.toList  // expose an immutable snapshot, not the buffer
```

A note on the older advice to "avoid `scala.collection.mutable.HashMap`": it is not
actually deprecated, and there is nothing wrong with it for single-threaded, local work.
The real guidance is about *sharing*, not about a specific class — a mutable map shared
across threads without synchronization is a data race, so prefer an immutable `Map` for
shared state and confine any mutable map to a single thread.

### Step 6 — Enum Types

Use UPPERCASE for enum members and constants in Scala, mirroring Python's enum convention.
The reason is consistency across the translation: matching member names keeps the two
sides visually aligned and signals "these are fixed constants," which is exactly what an
enum is.

```python
# Python
from enum import Enum

class TokenType(Enum):
    STRING = "string"
    NUMERIC = "numeric"
    TEMPORAL = "temporal"
    STRUCTURED = "structured"
    BINARY = "binary"
    NULL = "null"
```

```scala
// Scala 2 — a sealed trait with an explicit `value`, plus safe parsing
sealed trait BaseType {
  def value: String
}

object BaseType {
  case object STRING extends BaseType { val value: String = "string" }
  case object NUMERIC extends BaseType { val value: String = "numeric" }
  case object TEMPORAL extends BaseType { val value: String = "temporal" }
  case object STRUCTURED extends BaseType { val value: String = "structured" }
  case object BINARY extends BaseType { val value: String = "binary" }
  case object NULL extends BaseType { val value: String = "null" }

  val values: List[BaseType] =
    List(STRING, NUMERIC, TEMPORAL, STRUCTURED, BINARY, NULL)

  // Parse defensively: unknown input yields None instead of an exception.
  def fromValue(raw: String): Option[BaseType] =
    values.find(_.value == raw)
}
```

```scala
// Scala 3 — the same enum with a first-class `enum` and a constructor parameter
enum BaseType(val value: String):
  case STRING extends BaseType("string")
  case NUMERIC extends BaseType("numeric")
  case TEMPORAL extends BaseType("temporal")
  case STRUCTURED extends BaseType("structured")
  case BINARY extends BaseType("binary")
  case NULL extends BaseType("null")

object BaseType:
  def fromValue(raw: String): Option[BaseType] =
    BaseType.values.find(_.value == raw)
```

Do **not** use PascalCase for the members. The following is discouraged:

```scala
object BaseType {
  // `String` here shadows scala.Predef.String, so any later reference to the real
  // String type inside this object becomes ambiguous and confusing to read.
  case object String extends BaseType { val value: String = "string" }
}
```

The concrete reason to avoid it: a member named `String` (or `Int`, or `Map`) collides
with the standard library type of the same name, and a reader can no longer tell at a
glance whether `String` means "the type" or "this enum case."

### Step 7 — End-to-End Example

A quick end-to-end example converting a Python data-processing snippet to Scala. Note that
the dict-shaped Python records become a `@dataclass` / `case class` on both sides, so no
`Map[String, Any]` ever appears and every field keeps its precise type.

**Python**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Record:
    id: int
    value: int

data: list[Record] = [Record(id=1, value=10), Record(id=2, value=20)]
filtered: list[Record] = [d for d in data if d.value > 15]
ids: list[int] = [d.id for d in filtered]
total: int = sum(ids)  # 2
```

**Scala**

```scala
final case class Record(id: Int, value: Int)

val data: List[Record] = List(Record(1, 10), Record(2, 20))
val filtered: List[Record] = data.filter(_.value > 15)  // List(Record(2, 20))
val ids: List[Int] = filtered.map(_.id)                 // List(2)
val total: Int = ids.sum                                // 2
```

## Pitfalls

1. **Python dict ordering is a language guarantee; Scala `Map` ordering is not.**
   Since Python 3.7, `dict` preserves insertion order as a *language guarantee*. Scala's
   default immutable `Map`/`HashMap` does **not** — iteration order is unspecified. If
   order is load-bearing in the original code, translate to
   `scala.collection.immutable.ListMap` (insertion order) or `TreeMap` (sorted key order)
   instead of the default `Map`, or the behavior will silently drift.

2. **`reduce` throws on empty collections.** Python's `reduce` without an initializer
   raises `TypeError` on an empty sequence; Scala's `reduce` throws
   `UnsupportedOperationException`. Always prefer `foldLeft` with an explicit identity
   value, or `reduceOption` which returns `None` instead of throwing.

3. **`min`/`max` throw on empty collections.** Both Python (`ValueError`) and Scala
   (`UnsupportedOperationException`) raise on empty input. Use `minOption`/`maxOption`
   in Scala to get `None` instead, and guard the average computation with a `nonEmpty`
   check to avoid `ZeroDivisionError` / `ArithmeticException`.

4. **`enumerate` vs `zipWithIndex` tuple order is reversed.** Python's `enumerate` yields
   `(index, value)`, while Scala's `zipWithIndex` yields `(value, index)`. A mechanical
   translation that ignores this will swap the fields and produce a subtle bug.

5. **`List.empty` without a type argument infers `List[Nothing]`.** This is rarely what
   you want once you start appending. Always specify the element type:
   `List.empty[Int]`.

6. **PascalCase enum members shadow standard library types.** A member named `String`,
   `Int`, or `Map` collides with the standard library type of the same name. Always use
   UPPERCASE for enum members.

7. **`Map[String, Any]` throws away type safety.** A Python dict with mixed value types
   is a record, not a map. Model it as a `case class` / `@dataclass` with typed fields,
   never as `Map[String, Any]`.

8. **Mutable collections shared across threads are a data race.** `scala.collection.mutable.HashMap`
   is not deprecated, but a mutable map shared across threads without synchronization is
   unsafe. Prefer immutable `Map` for shared state; confine mutable collections to a
   single thread and expose an immutable snapshot at the boundary.

9. **Not suitable for specialized performance tuning.** This guide covers everyday
   collections (`List`, `Map`, `Set`, `ListBuffer`). If a hot path needs `Vector` for
   effectively-constant-time random access, `ArraySeq` for primitive packing, or a custom
   builder, those trade-offs deserve their own analysis rather than a generic translation.

10. **These tables are a starting point, not a replacement for understanding semantics.**
    Cardinality, ordering, and null-handling differences still need a human decision on a
    per-case basis.

## Verification

1. **Compile-check all Scala snippets** — paste them into a Scala REPL, Scastie worksheet,
   or IDE worksheet and confirm they compile with the explicit type annotations intact:

   ```bash
   # Using Scala 3 CLI (adjust for your Scala version)
   scala repl
   # Paste each snippet and confirm no type errors
   ```

   On Windows PowerShell:

   ```powershell
   scala repl
   # Paste each snippet and confirm no type errors
   ```

2. **Compare Python and Scala outputs across test cases**, including the empty-collection
   case for `reduce`/`min`/`max`/`average`. Confirm:
   - `foldLeft` on an empty `List` returns the identity value (e.g., `0` for `_ + _`).
   - `reduceOption` on an empty `List` returns `None`.
   - `minOption`/`maxOption` on an empty `List` return `None`.
   - `sum` on an empty `List[Int]` returns `0`.

3. **Validate immutability** — confirm that immutable forms leave their inputs unchanged:

   ```scala
   val original: List[Int] = List(3, 1, 2)
   val sorted: List[Int] = original.sorted
   assert(original == List(3, 1, 2))  // original is untouched
   assert(sorted == List(1, 2, 3))
   ```

4. **Exercise `foldLeft` and `reduceOption`** with both non-empty and empty inputs to
   confirm the empty case returns the identity / `None` rather than throwing.

5. **Verify sorting and grouping output**, and double-check the `enumerate` vs
   `zipWithIndex` tuple order when translating zip/index code:

   ```scala
   val list1: List[String] = List("a", "b", "c")
   val indexed: List[(String, Int)] = list1.zipWithIndex
   assert(indexed == List(("a", 0), ("b", 1), ("c", 2)))  // (value, index), NOT (index, value)
   ```

6. **Confirm `BaseType.fromValue` returns `None` for unknown input** rather than throwing:

   ```scala
   assert(BaseType.fromValue("string") == Some(BaseType.STRING))
   assert(BaseType.fromValue("unknown") == None)  // does NOT throw
   ```

## Related skills

- python-scala-syntax
- python-scala-interop
- scala-collections-overview
