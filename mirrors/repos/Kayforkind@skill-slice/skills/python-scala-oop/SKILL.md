---
name: python-scala-oop
version: 1.1.1
description: "Ports Python classes, frozen dataclasses, ABCs, mixins, properties, static and class methods, dunders, enums, factories, and singletons onto Scala 3 class, case class, trait, def_=, companion object, and enum. Use when the source is object-oriented structure rather than collection pipelines. Never a collection-transform guide, LazyList/type-class functional chair, or snake_case style pass."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Reach for this skill when you are porting Python *object-oriented* code to Scala: plain classes, `@dataclass`es, abstract base classes, inheritance hierarchies, properties, static/class methods, design patterns (factory, singleton, etc.), enums, and the dunder protocol.

**Trigger keywords:** Python class, `@dataclass`, `ABC`, `abstractmethod`, `@property`, `@staticmethod`, `@classmethod`, `__init__`, `__eq__`, `__hash__`, `__add__`, inheritance, mixin, MRO, singleton, factory, enum, dunder, port Python to Scala, translate Python OOP.

The reason a dedicated guide exists is that Python's dynamic, duck-typed object model maps onto Scala's static, compile-checked model in non-obvious ways. A line-for-line port often *compiles* but *behaves differently*: Python multiple inheritance resolves by MRO while Scala uses trait linearization; Python properties are runtime descriptors while Scala uses paired `def`/`def_=` accessors; Python `classmethod` constructors become companion-object factories. Getting these mappings right is what keeps the translated code both idiomatic and correct.

The examples target **Scala 3.3** (with Scala 2.13 equivalents called out where they differ) and assume modern tooling — sbt 1.9+, Scala CLI, and a current standard library.

### Do Not Use

These are guidelines with reasons, not absolute prohibitions — understanding *why* lets you judge the edge cases.

- **Procedural scripts, pure-functional code, or CPython-internal dependencies.** The patterns here assume class-based OO targeting the JVM. Code that leans on CPython C-extensions (Cython, NumPy's internal buffer protocol, ctypes) has no 1:1 Scala equivalent, so a naive port would be incorrect or impossible. Target a JVM-native library instead (e.g., Breeze or Spark for array math) rather than translating the internals.
- **Prefer `val`/case classes over `var` for data that does not need to change.** Immutable values can be shared across threads without locks and give you predictable equality, hashing, and `copy` semantics for free. Use `var` only when a measured hot path or an external mutable API genuinely requires in-place mutation — otherwise it is a source of accidental aliasing bugs.
- **Prefer Scala 3 `enum`/`given` over Scala 2-only idioms** (hand-written `apply` factories, raw `implicit` plumbing) *unless you must compile on 2.13*. Scala 3 enums are checked for exhaustiveness and `given`s are resolved at compile time, so whole categories of runtime errors simply cannot occur. Falling back to the older idioms throws that safety away.
- **Do not share mutable state without synchronization.** The JVM gives you no protection against data races; they are silent and non-deterministic. If state must be shared across threads, use `java.util.concurrent` atomics/concurrent collections, or an effect system (Cats Effect, ZIO) that makes concurrency explicit and checkable.
- **Do not drop input validation when porting.** Python frequently relies on exceptions raised deep in dynamic code. If you omit the equivalent `require` guard or `Either`/`Try` result in Scala, an illegal value silently produces a corrupt object that fails much later with a confusing `NullPointerException` or `ClassCastException`. Validate at the boundary (construction time) so an invalid instance can never exist in the first place.

## Prerequisites

- **Scala 3.3+** (Scala 2.13 equivalents noted where they differ)
- **sbt 1.9+** or **Scala CLI** for compilation and testing
- **JDK 11+** (JDK 17 recommended for Scala 3.3)
- On Windows (PowerShell), verify tooling:

```powershell
scala -version
sbt --version
scala-cli version
```

- Static analysis tools recommended: `scalafmt`, `scalafix`, `wartremover`

## Procedure

### Step 1 — Identify the Python Construct

Classify each Python construct before translating. The right Scala target depends on this classification:

| Python Construct | Scala Target |
|---|---|
| Plain `class` with `__init__` | `class` with constructor params |
| `@dataclass(frozen=True)` | `final case class` |
| `@dataclass` (mutable) | `case class` with `var` fields (prefer immutability + `copy`) |
| `ABC` + `@abstractmethod` | `trait` (or `abstract class` if constructor params needed) |
| Multiple inheritance / mixins | Traits with `with` |
| `@property` getter/setter | `def`/`def_=` pair (mutable) or `val`/derived `def` (immutable) |
| `@staticmethod` | Method on companion `object` |
| `@classmethod` constructor | Named factory on companion `object` |
| `Enum` / `auto()` | Scala 3 `enum` |
| Singleton (`__new__` + lock) | `object` |
| Dunder methods (`__eq__`, `__hash__`, `__str__`) | Case class auto-generates; `Ordered` trait for comparisons |

### Step 2 — Apply Naming and Immutability Conventions

- `camelCase` for methods and fields
- `PascalCase` for types
- `val` over `var`
- Case classes over manual `equals`/`hashCode`
- `final` on case classes to prevent subclassing that would break structural equality

### Step 3 — Translate Each Construct

#### Basic Classes

```python
# Python
class Person:
    def __init__(self, name: str, age: int) -> None:
        if not name or not name.strip():
            raise ValueError("name must be a non-empty string")
        if age < 0:
            raise ValueError("age must be non-negative")
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hello, I'm {self.name}"
```

```scala
// Scala 3
class Person(val name: String, val age: Int) {
  require(name.trim.nonEmpty, "name must be a non-empty string")
  require(age >= 0, "age must be non-negative")

  def greet: String = s"Hello, I'm $name"
}

val person = new Person("Alice", 30)  // `new` is required for a plain (non-case) class
```

`val name`/`val age` in the constructor declare immutable public fields in one line, eliminating separate field-assignment boilerplate. `require` throws `IllegalArgumentException` — the direct analogue of Python's `raise ValueError`.

#### Data Classes → Case Classes

```python
# Python
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.x) or not math.isfinite(self.y):
            raise ValueError("coordinates must be finite numbers")
```

```scala
// Scala 3 — a case class is the idiomatic translation of a frozen dataclass.
final case class Point(x: Double, y: Double) {
  require(x.isFinite && y.isFinite, "coordinates must be finite numbers")
}

val p  = Point(1.0, 2.0)     // no `new`; the generated `apply` runs `require`
val p2 = p.copy(x = 3.0)     // structural copy; `require` runs again on the new instance
```

A mutable `@dataclass` would map to `case class Point(var x: Double, var y: Double)`, but prefer immutability and derive new values with `copy` instead.

#### Properties

```python
# Python
import math

class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("radius must be non-negative")
        self._radius = value

    @property
    def area(self) -> float:
        return math.pi * self._radius ** 2
```

```scala
// Option A — mutable version mirroring Python's getter/setter property.
class MutableCircle(initialRadius: Double) {
  require(initialRadius >= 0, "radius must be non-negative")
  private var _radius: Double = initialRadius

  def radius: Double = _radius
  def radius_=(value: Double): Unit = {
    require(value >= 0, "radius must be non-negative")
    _radius = value
  }

  def area: Double = math.Pi * _radius * _radius
}

// Option B — preferred immutable version.
final case class Circle(radius: Double) {
  require(radius >= 0, "radius must be non-negative")
  def area: Double = math.Pi * radius * radius
}
```

#### Inheritance

```scala
// Scala 3 — use an `abstract class` when the base needs constructor parameters.
abstract class Animal(val name: String) {
  require(name.trim.nonEmpty, "name must be a non-empty string")
  def speak: String   // abstract member
}

class Dog(name: String) extends Animal(name) {
  override def speak: String = s"$name says woof!"
}

class Cat(name: String) extends Animal(name) {
  override def speak: String = s"$name says meow!"
}
```

`override` is mandatory and compiler-checked, so a typo in the method name becomes a compile error instead of silently shadowing nothing.

#### Abstract Classes and Interfaces

```scala
// Scala 3 — a `trait` is the idiomatic translation of a pure interface / ABC.
trait Shape {
  def area: Double          // abstract
  def perimeter: Double     // abstract
  def describe: String = f"Area: ${area}%.4f, Perimeter: ${perimeter}%.4f"
}

final case class Rectangle(width: Double, height: Double) extends Shape {
  require(width >= 0 && height >= 0, "width and height must be non-negative")
  def area: Double = width * height
  def perimeter: Double = 2 * (width + height)
}
```

Prefer a trait when you only need abstract members plus optional defaults and no constructor parameters; reach for an `abstract class` only when you need constructor params or tighter Java interop.

#### Multiple Inheritance → Traits

```scala
trait Flyable {
  def fly: String = "Flying!"
}

trait Swimmable {
  def swim: String = "Swimming!"
}

class Duck(name: String) extends Animal(name) with Flyable with Swimmable {
  override def speak: String = "Quack!"
}

val duck = new Duck("Donald")
duck.fly    // "Flying!"
duck.swim   // "Swimming!"
```

Scala resolves conflicts via deterministic *linearization* order (right-most `with` wins), which is the type-checked equivalent of Python's MRO.

#### Static Methods and Class Methods → Companion Objects

```scala
final class Temperature private (val celsius: Double)

object Temperature {
  val AbsoluteZeroC: Double = -273.15

  def apply(celsius: Double): Temperature = {
    require(celsius >= AbsoluteZeroC, s"temperature below absolute zero: $celsius")
    new Temperature(celsius)
  }

  def isFreezing(celsius: Double): Boolean = celsius <= 0.0

  def fromFahrenheit(fahrenheit: Double): Temperature =
    apply((fahrenheit - 32.0) * 5.0 / 9.0)
}

// Usage
Temperature.isFreezing(-4.0)
val boiling = Temperature.fromFahrenheit(212.0)  // 100.0 °C
val floor = Temperature.AbsoluteZeroC            // -273.15
```

Making the class constructor `private` forces every instance through the validated `apply` entry point.

#### Factory Pattern

```scala
import scala.util.Try

sealed trait Shape {
  def area: Double
}

final case class Circle(radius: Double) extends Shape {
  require(radius >= 0, "radius must be non-negative")
  def area: Double = math.Pi * radius * radius
}

final case class Rectangle(width: Double, height: Double) extends Shape {
  require(width >= 0 && height >= 0, "width and height must be non-negative")
  def area: Double = width * height
}

object Shape {
  def fromSpec(shapeType: String, params: Map[String, Double]): Either[String, Shape] =
    shapeType.trim.toLowerCase match {
      case "circle" =>
        for {
          r     <- params.get("radius").toRight("missing parameter: radius")
          shape <- Try(Circle(r)).toEither.left.map(_.getMessage)
        } yield shape
      case "rectangle" =>
        for {
          w     <- params.get("width").toRight("missing parameter: width")
          h     <- params.get("height").toRight("missing parameter: height")
          shape <- Try(Rectangle(w, h)).toEither.left.map(_.getMessage)
        } yield shape
      case other =>
        Left(s"Unknown shape type: $other")
    }
}
```

`sealed` means every subtype lives in this file, so the compiler checks that a `match` is exhaustive.

#### Enums

```scala
// Scala 3
enum Color:
  case Red, Green, Blue

enum Status(val value: String):
  case Pending  extends Status("pending")
  case Approved extends Status("approved")
  case Rejected extends Status("rejected")

object Status:
  def fromValue(value: String): Option[Status] =
    Status.values.find(_.value == value)
```

Scala 2.13 equivalent (still supported): a sealed trait with case objects — more verbose, and you lose built-in `.values`/parameter support.

#### Singleton

```scala
// Scala — an `object` IS a singleton. JVM guarantees lazy, thread-safe init.
object Counter {
  private val count = new java.util.concurrent.atomic.AtomicLong(0L)

  def increment(): Long = count.incrementAndGet()
  def current: Long     = count.get()
}

Counter.increment()   // 1
Counter.increment()   // 2
Counter.current       // 2
```

None of Python's double-checked-locking ceremony is needed.

#### Special Methods (Dunder Methods)

| Python | Scala |
|--------|-------|
| `__init__` | Primary constructor |
| `__str__` | `toString` |
| `__repr__` | `toString` (case classes auto-generate) |
| `__eq__` | `equals` (case classes auto-generate) |
| `__hash__` | `hashCode` (case classes auto-generate) |
| `__len__` | `length` or `size` method |
| `__getitem__` | `apply` method |
| `__setitem__` | `update` method |
| `__iter__` | Extend `Iterable` trait |
| `__add__` | `+` method |
| `__lt__`, `__le__`, etc. | Extend `Ordered` trait |

```scala
// Case class earns toString, equals, hashCode, and copy for free.
final case class Vector(x: Double, y: Double) {
  require(x.isFinite && y.isFinite, "vector components must be finite")

  def +(other: Vector): Vector = Vector(x + other.x, y + other.y)
}

val sum = Vector(1.0, 2.0) + Vector(3.0, 4.0)   // Vector(4.0, 6.0)
println(sum)                                     // Vector(4.0,6.0)
Vector(1.0, 2.0) == Vector(1.0, 2.0)             // true
```

### Step 4 — Run the Verification Checklist

Validation guards and error handling are the parts most often lost in translation. Confirm each Python `raise` has a corresponding Scala `require`/`Either`/`Try`.

## Pitfalls

1. **Dropped validation is the #1 porting defect.** Python raises `ValueError` at construction; if you forget the `require` guard in Scala, an illegal value silently produces a corrupt object that fails later with `NullPointerException` or `ClassCastException`. Always map every `raise` to `require`, `IllegalArgumentException`, or `Either`/`Try`.

2. **MRO vs. trait linearization.** Python multiple inheritance resolves by MRO; Scala uses trait linearization where right-most `with` wins. A line-for-line port compiles but may call the wrong superclass method. Test diamond hierarchies explicitly.

3. **`@property` setter duplication.** In Python, assigning through the property setter in `__init__` shares a single validation path. In Scala, if you use a mutable backing field with `def_=` you must either call the setter from the constructor body or duplicate the check — otherwise construction bypasses validation.

4. **`__post_init__` runs after generated `__init__`.** In Scala case classes, `require` in the class body runs *during* construction (before fields are observable), which is actually safer. But if you ported a `__post_init__` that mutated fields post-construction, there is no direct equivalent — restructure to validate at construction or use a factory method.

5. **`NotImplemented` vs. compile error.** Python's `__add__` returns `NotImplemented` for unsupported operand types so Python can try `__radd__`. In Scala, the parameter type is `Vector`, so a non-Vector operand is a *compile error* — no runtime guard needed, but it means you lose Python's dynamic fallback behavior.

6. **Mutable `var` in case classes breaks `hashCode` consistency.** If a `case class` has `var` fields and you mutate them after inserting into a `HashSet`/`HashMap`, the entry becomes unfindable. Prefer immutable `val` fields and `copy`.

7. **Scala 2.13 vs. 3.3 enum syntax.** Scala 3 `enum` is not available in 2.13. If you must cross-compile, use `sealed trait` + `case object` and hand-write `values`. Do not attempt to use Scala 3 enum syntax with `-scala-2.13`.

8. **`new` required for plain classes, not for case classes.** `new Person("Alice", 30)` requires `new`; `Point(1.0, 2.0)` does not (case class `apply` is generated). Mixing this up is a common compile error.

9. **Shared mutable state without synchronization.** The JVM provides no protection against data races. An `object` singleton with a `var` field is not thread-safe by default. Use `java.util.concurrent.atomic` or effect systems.

10. **Deprecated Scala APIs.** Avoid `Predef.any2stringadd`, `return` statements in lambdas, and `asInstanceOf` casts. Run `scalafix` to catch these automatically.

## Verification

Run each of these checks after translating:

```powershell
# 1. Compile the translated Scala code
sbt compile
# or with Scala CLI:
scala-cli compile .

# 2. Run the test suite — behavioral parity, not just compilation
sbt test
# or:
scala-cli test .

# 3. Cross-compile if targeting both Scala 2.13 and 3.3
sbt +test

# 4. Static analysis — catch unsafe patterns
scalafmt --test
sbt scalafix
# wartremover (in build.sbt): wartremoverWarnings := true

# 5. Check for deprecated APIs
sbt scalafix --rules=RemoveUnused
```

**Checklist:**

- [ ] Every Python construct in the source has an equivalent Scala implementation (missing `classmethod` or property is easy to overlook).
- [ ] Every Python `raise` has a matching guard in Scala (`require`, `IllegalArgumentException`, or `Either`/`Try` result).
- [ ] If supporting both, compiles under Scala 2.13 *and* Scala 3.3 (enum/`given` syntax and trait-parameter rules differ).
- [ ] No `asInstanceOf` casts, `null` literals, or mutable globals flagged by static analysis.
- [ ] No deprecated Scala APIs remain (e.g., `Predef.any2stringadd`).
- [ ] `scalafmt --test` passes (formatting is consistent).
- [ ] Diamond/multiple-inheritance hierarchies tested for correct method resolution.

## Related Skills

- `python-to-scala-syntax` — syntax-level Python → Scala translation
- `scala-idioms` — idiomatic Scala patterns beyond direct translation
- `object-oriented-design-patterns` — general OOP design pattern reference
