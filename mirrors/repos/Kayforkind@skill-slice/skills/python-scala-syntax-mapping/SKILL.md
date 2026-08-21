---
name: python-scala-syntax-mapping
version: 1.1.1
description: "Maps everyday Python syntax to idiomatic Scala 3 (val/var, Option vs None, for/yield, interpolation, operators, typed errors). Use when translating Python snippets into Scala a reviewer would accept. Not for Akka, Spark, Cats, or ZIO libraries, sbt/Mill builds, or treating a 1:1 token swap as finished Scala."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Python to Scala Syntax Mapping

## When to Use

Use this skill when you are migrating or translating Python code to Scala 3 and need the equivalent syntax for everyday constructs: variable bindings, control flow, comprehensions, functions, string interpolation, operators, and error handling.

The value here is not just "Python token X becomes Scala token Y." The two languages disagree about defaults — Python rebinds names freely and signals "no value" with `None` at runtime, while Scala makes immutability the default and pushes absence, failure, and choice into the *type* so the compiler can check them. Knowing the mapping plus the reason behind it lets you produce Scala that a Scala reviewer would accept, instead of Python transliterated into Scala keywords.

**Do not use** this as a substitute for learning Scala's idioms, its type system, or functional design. A literal one-to-one translation is often the *worst* Scala: a Python `for` loop that mutates an accumulator has a cleaner Scala form as `map`/`fold`, and a chain of `if value is None` checks usually collapses into one `Option` combinator. For libraries and runtimes (Akka/Pekko, Spark, Cats, ZIO), build tooling (sbt, Mill), implicits/`given` resolution, or performance tuning, this guide is intentionally out of scope — reach for the dedicated references listed under [Related skills](#related-skills).

## Overview

### Why the defaults differ (read this before the tables)

Most of the mappings below exist to bridge four philosophical gaps. Understanding them turns the tables from rules into judgement calls:

1. **Immutability is the default in Scala.** `val` creates a binding that cannot be reassigned. You reach for `var` only when an algorithm genuinely needs in-place mutation (a counter in a `while` loop, a performance-critical buffer). Immutable bindings are easier to reason about and safe to share across threads, which is why idiomatic Scala minimizes `var`. The compiler can flag never-reassigned `var`s with the `-Wunused` family of lint flags.
2. **Absence lives in the type.** Python uses the single sentinel `None` for "missing," and forgetting to check it raises `AttributeError` at runtime. Scala uses `Option[T]` (`Some(value)` or `None`), so the *compiler* forces you to handle the empty case. Reference `null` still exists for Java interop but is avoided; the opt-in `-Yexplicit-nulls` compiler flag makes reference types non-nullable unless you write `T | Null`.
3. **Almost everything is an expression.** In Scala, `if`, `match`, `for`/`yield`, and even `try` evaluate to a value. That lets you assign the result directly to a `val` instead of declaring a mutable variable and reassigning it inside branches — which removes the "I forgot to set it in one branch" class of bug.
4. **Errors can be values.** Python signals failure by throwing. Scala can do that too, but prefers `Option` (absence), `Either[Error, Value]` (a described failure), or `Try[Value]` (a caught exception) so that the possibility of failure is visible in the function signature and cannot be silently ignored.

## Procedure

Find the Python construct you are translating, read across to the Scala column, then check the "why"/notes beneath the table for the semantic differences that bite (integer division sign, modulo sign, `Option` vs `null`, value vs reference equality). Every code block below is complete and runnable Scala 3 — copy it, adjust the names, and keep the explicit type annotations and input validation rather than stripping them out.

### 1. Variable Declarations

| Python | Scala |
|--------|-------|
| `x = 5` | `val x: Int = 5` (immutable) or `var x: Int = 5` (reassignable) |
| `x: int = 5` | `val x: Int = 5` |
| `x, y = 1, 2` | `val (x, y): (Int, Int) = (1, 2)` |
| `_` (unused) | `val _: T = expr` (evaluate and discard) |

**Why:** prefer `val`. A `val` is a promise to every future reader that the binding never changes, so they don't have to trace reassignments. Reach for `var` only when the algorithm mutates in place, and keep its scope as small as possible. Annotate the type when it aids the reader or when you want the compiler to confirm your intent (it is inferred otherwise).

```scala
val maxRetries: Int = 5                 // immutable: reassigning is a compile error
var attempts: Int = 0                   // var is justified — the retry loop reassigns it
val (host, port): (String, Int) = ("localhost", 8080)  // destructuring a tuple
val _: Int = sideEffectingCompute()     // run for its effect, intentionally discard the result

def sideEffectingCompute(): Int =
  println("computing value")
  42
```

### 2. Type Mappings

| Python | Scala |
|--------|-------|
| `int` | `Int` (32-bit) or `Long` (64-bit) |
| `float` | `Double` (prefer; matches Python's 64-bit float) or `Float` |
| `str` | `String` |
| `bool` | `Boolean` |
| `None` | `None` (the empty case of `Option[T]`) |
| `list[T]` | `List[T]` (immutable, default) or `Seq[T]` (interface) |
| `dict[K, V]` | `Map[K, V]` (immutable, default) |
| `set[T]` | `Set[T]` (immutable, default) |
| `tuple[A, B]` | `(A, B)` (sugar for `Tuple2[A, B]`) |
| `Optional[T]` | `Option[T]` |
| `Union[T, U]` | `T \| U` (Scala 3 union types) |
| `Any` | `Any` — avoid; see note |

**Why `Any` is a last resort:** `Any` is the top of Scala's type hierarchy, so a value typed `Any` discards every compile-time guarantee — you cannot call domain methods on it without a cast, and casts fail at runtime. Whenever you are tempted to write `Any`, prefer one of: a concrete type, a bounded type parameter (`def f[T <: Number](x: T)`), a Scala 3 union (`Int | String`), an enum/sealed hierarchy, or a type class. The mapping is listed for completeness, not as an endorsement. Collections default to their immutable variants; import from `scala.collection.mutable` explicitly and locally on the rare occasions you need mutation.

### 3. Control Flow

#### Conditionals

```python
# Python
def classify(x: int) -> str:
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"
```

```scala
// Scala 3 — `if` is an expression, so its value is the function body.
// No mutable `result` variable is needed, and the compiler checks every branch.
def classify(x: Int): String =
  if x > 0 then "positive"
  else if x < 0 then "negative"
  else "zero"
```

#### Loops

```python
# Python
temperatures: list[float] = [18.5, 21.0, 19.7]

for index in range(len(temperatures)):
    print(f"Reading {index}: {temperatures[index]}")

for temperature in temperatures:
    record(temperature)

for index, temperature in enumerate(temperatures):
    print(f"{index}: {temperature:.1f}")


def record(reading: float) -> None:
    print(f"Recorded: {reading}")
```

```scala
// Scala 3
val temperatures: List[Double] = List(18.5, 21.0, 19.7)

// Index-based iteration. `indices` returns valid positions only, so the
// `temperatures(index)` lookup cannot go out of bounds.
for index <- temperatures.indices do
  println(s"Reading $index: ${temperatures(index)}")

def record(reading: Double): Unit =
  println(s"Recorded: $reading")

// Prefer functional iteration: it states the intent ("do this to each element")
// and avoids manual indexing, which is the usual source of off-by-one bugs.
temperatures.foreach(record)

// `zipWithIndex` pairs each element with its position — the analogue of enumerate.
for (temperature, index) <- temperatures.zipWithIndex do
  println(f"$index: $temperature%.1f")
```

#### While loops

```python
# Python
def countdown(start: int) -> None:
    if start < 0:
        raise ValueError(f"start must be non-negative, got {start}")
    remaining = start
    while remaining > 0:
        print(remaining)
        remaining -= 1
```

```scala
// Scala 3 — `while` is the one place a `var` is clearly warranted, because the
// loop mutates `remaining` in place. `require` validates the precondition up
// front and throws IllegalArgumentException with a message if it is violated.
def countdown(start: Int): Unit =
  require(start >= 0, s"start must be non-negative, got $start")
  var remaining: Int = start
  while remaining > 0 do
    println(remaining)
    remaining -= 1
```

### 4. Comprehensions

```python
# Python
squares: list[int] = [x ** 2 for x in range(10)]
numbers: list[int] = [1, 2, 3, 4, 5, 6]
evens: list[int] = [x for x in numbers if x % 2 == 0]
xs: list[int] = [1, 2]
ys: list[str] = ["a", "b"]
pairs: list[tuple[int, str]] = [(x, y) for x in xs for y in ys]
```

```scala
// Scala 3 — `map`/`filter` for the simple cases, a `for`/`yield`
// comprehension when you are combining multiple sources.
val squares: List[Int] = (0 until 10).map(x => x * x).toList

val numbers: List[Int] = List(1, 2, 3, 4, 5, 6)
val evens: List[Int] = numbers.filter(_ % 2 == 0)

val xs: List[Int] = List(1, 2)
val ys: List[String] = List("a", "b")
// A `for`/`yield` over two generators is the nested-comprehension equivalent;
// it desugars to xs.flatMap(x => ys.map(y => (x, y))).
val pairs: List[(Int, String)] =
  for
    x <- xs
    y <- ys
  yield (x, y)
```

**Why `for`/`yield`, not `for`/`do`:** the `yield` keyword is what makes the comprehension *build a collection*. The `for generators do body` form runs the body for its side effects and returns `Unit`, so it is the loop form, not the comprehension form.

### 5. Functions

```python
# Python
def add(a: int, b: int) -> int:
    return a + b

# Lambda
square = lambda x: x ** 2

# Default arguments, with a guard on the input
def greet(name: str, greeting: str = "Hello") -> str:
    if not name:
        raise ValueError("name must not be empty")
    return f"{greeting}, {name}!"
```

```scala
// Scala 3 — annotate parameter and return types explicitly. The return type is
// part of the function's contract and documents intent even where it could be inferred.
def add(a: Int, b: Int): Int = a + b

// A function value. The `Int => Int` annotation names the type so the reader
// (and the compiler) know the signature without inferring it from the body.
val square: Int => Int = x => x * x

// Default arguments work as in Python. `require` enforces the precondition,
// turning an invalid call into an immediate, well-described failure.
def greet(name: String, greeting: String = "Hello"): String =
  require(name.nonEmpty, "name must not be empty")
  s"$greeting, $name!"
```

### 6. String Formatting

| Python | Scala |
|--------|-------|
| `f"Hello, {name}!"` | `s"Hello, $name!"` |
| `f"Value: {x:.2f}"` | `f"Value: $x%.2f"` |
| `f"{x + y}"` | `s"${x + y}"` |
| `"Hello, {}".format(name)` | `"Hello, %s".format(name)` (legacy) |

**Why two interpolators:** the `s` interpolator substitutes values by calling `toString`. The `f` interpolator adds `printf`-style format specifiers (`%.2f`, `%05d`) and — crucially — *checks them against the argument types at compile time*, so `f"$count%.2f"` fails to compile if `count` is an `Int` rather than a floating-point value. Reach for `f` whenever you format numbers; reach for `s` for plain substitution.

```scala
val name: String = "Ada"
val balance: Double = 1234.5

val greeting: String = s"Hello, $name!"             // -> "Hello, Ada!"
val statement: String = f"Balance: $balance%.2f"    // -> "Balance: 1234.50"
val total: String = s"Sum is ${2 + 3}"              // -> "Sum is 5"
```

**Security note:** interpolators do **not** escape or sanitize their inputs, exactly like Python f-strings. Never assemble SQL, shell commands, or HTML from untrusted values with the `s` or `f` interpolators — that is a classic injection vector. Use parameterized/prepared statements for SQL, an argument array (not a shell string) for subprocesses, and a context-aware encoder for HTML.

### 7. Common Operators

| Python | Scala | Notes |
|--------|-------|-------|
| `**` (power) | `math.pow(x, y)` → `Double`; `BigInt(x).pow(y)` for exact integers | `Int` has no `.pow`; `math.pow` always returns `Double` |
| `//` (floor div) | `Math.floorDiv(x, y)` | Scala's `/` truncates toward zero; differs from Python on negatives |
| `%` (modulo) | `Math.floorMod(x, y)` | Scala's `%` takes the sign of the dividend; differs from Python on negatives |
| `and` / `or` / `not` | `&&` / `\|\|` / `!` | short-circuit, same semantics as Python |
| `in` | `collection.contains(x)` | O(1) for `Set`/`Map` keys, O(n) for `List` |
| `is` | `eq` (`AnyRef` only) | reference identity; not defined on value types like `Int` |
| `==` | `==` | calls `.equals`; structural equality by default, unlike Java's `==` |
| `:=` (walrus) | a plain `val` in the enclosing block | Scala has no assignment-as-expression operator |

**Why the arithmetic differs (this catches people):** Python's `//` and `%` follow the *divisor's* sign, while Scala's `/` and `%` follow the *dividend's*. So Python `-7 // 2 == -4` and `-7 % 2 == 1`, but Scala `-7 / 2 == -3` and `-7 % 2 == -1`. When you need Python's behavior — common when computing wrap-around indices or bucketing — use `Math.floorDiv` and `Math.floorMod` so the results match.

```scala
val pyFloorDiv: Int = Math.floorDiv(-7, 2)   // -4, matches Python's -7 // 2
val pyModulo: Int = Math.floorMod(-7, 2)     //  1, matches Python's -7 % 2
val powerOfTwo: Double = math.pow(2, 10)      // 1024.0 (Double)
val exactPower: BigInt = BigInt(2).pow(10)    // 1024 (exact integer)
```

### 8. Exception Handling

```python
# Python — validate, convert a low-level error into a domain error, clean up.
def parse_port(raw: str) -> int:
    try:
        port = int(raw.strip())
    except ValueError as exc:
        raise ValueError(f"Invalid port: {raw!r}") from exc
    if not 1 <= port <= 65535:
        raise ValueError(f"Port out of range: {port}")
    return port
```

```scala
// Scala 3 offers three complementary tools. Pick by what the caller needs.
import scala.util.{Try, Success, Failure, Using}

// Pattern 1 — Either: model an expected, described failure as a value.
// The signature `Either[String, Int]` tells callers failure is possible and
// forces them to handle the Left branch; nothing throws.
def parsePort(raw: String): Either[String, Int] =
  Try(raw.trim.toInt) match
    case Failure(_)    => Left(s"Invalid port: '$raw'")
    case Success(port) =>
      if port >= 1 && port <= 65535 then Right(port)
      else Left(s"Port out of range: $port")

// Pattern 2 — direct try/catch/finally: the literal translation of Python's
// try/except/finally. Catch the specific exception, never a blanket `Throwable`,
// and always release resources in `finally`.
def readFirstLineManually(path: String): Option[String] =
  require(path.nonEmpty, "path must not be empty")
  val reader = new java.io.BufferedReader(new java.io.FileReader(path))
  try Option(reader.readLine())
  catch
    case _: java.io.IOException => None
  finally reader.close()

// Pattern 3 — Using: the idiomatic resource form. It closes the reader for you
// (even on exception) and wraps the outcome in a Try, so the failure is a value.
def readFirstLine(path: String): Try[String] =
  require(path.nonEmpty, "path must not be empty")
  Using(new java.io.BufferedReader(new java.io.FileReader(path))) { reader =>
    Option(reader.readLine()).getOrElse("")
  }
```

**Why prefer `Either`/`Try` over throwing:** a thrown exception is invisible in the type signature, so a caller can forget to handle it and the program crashes in production. `Either[E, A]` and `Try[A]` make "this can fail" part of the contract the compiler enforces. Keep `try/catch` for genuinely exceptional, unrecoverable situations or thin Java-interop boundaries.

### 9. None/Null Handling

```python
# Python — a missing value plus a validity check.
def resolve_timeout(value: int | None, default: int = 30) -> int:
    if value is None:
        return default
    if value <= 0:
        raise ValueError(f"timeout must be positive, got {value}")
    return value
```

```scala
// Scala 3 — `Option[Int]` makes "might be absent" explicit, and `match`
// handles every case. The compiler warns if a case is missing.
def resolveTimeout(value: Option[Int], default: Int = 30): Int =
  value match
    case None             => default
    case Some(v) if v > 0 => v
    case Some(v)          =>
      throw new IllegalArgumentException(s"timeout must be positive, got $v")

// For the simple "use it or fall back" case, the combinators are more concise
// than a match and chain cleanly: keep the value only if it is valid, else default.
val configured: Option[Int] = Some(45)
val timeout: Int = configured.filter(_ > 0).getOrElse(30)
```

**Why `Option` instead of `null`:** dereferencing `null` throws `NullPointerException` at runtime with no compile-time warning — the same failure mode as Python's `AttributeError: 'NoneType'`. `Option` lifts that risk into the type system: you literally cannot read the inner value without first addressing the empty case, so the bug is caught while you compile rather than when a user hits it.

## Examples

The sections above each map one construct. Here is a small end-to-end translation that combines several — validation, iteration, error-as-value, and immutable collections — so you can see the idioms working together. It parses `key=value` configuration lines, skipping blanks and comments and reporting every malformed line.

```python
# Python
def parse_config(lines: list[str]) -> dict[str, str]:
    config: dict[str, str] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Malformed config line: {raw!r}")
        key, _, value = line.partition("=")
        config[key.strip()] = value.strip()
    return config
```

```scala
// Scala 3 — returns Either so the caller sees that parsing can fail, and
// collects *all* malformed lines instead of throwing on the first one.
def parseConfig(lines: List[String]): Either[String, Map[String, String]] =
  val parsed: List[Either[String, (String, String)]] =
    lines
      .map(_.trim)
      .filter(line => line.nonEmpty && !line.startsWith("#"))
      .map { line =>
        line.split("=", 2) match
          case Array(key, value) => Right(key.trim -> value.trim)
          case _                 => Left(s"Malformed config line: '$line'")
      }

  // partitionMap splits the list into (errors, successes) in one pass.
  parsed.partitionMap(identity) match
    case (Nil, entries)  => Right(entries.toMap)
    case (errors, _)     => Left(errors.mkString("; "))
```

## Pitfalls

- **Negative-number arithmetic mismatch:** Python's `//` and `%` follow the divisor's sign; Scala's `/` and `%` follow the dividend's sign. Python `-7 // 2 == -4` but Scala `-7 / 2 == -3`. Use `Math.floorDiv` and `Math.floorMod` whenever Python's flooring semantics matter (wrap-around indices, bucketing, modular arithmetic).
- **`Int` has no `.pow` method:** `math.pow` always returns `Double`. For exact integer exponentiation use `BigInt(x).pow(y)`.
- **`for`/`do` vs `for`/`yield` confusion:** `for ... yield` builds a collection; `for ... do` runs for side effects and returns `Unit`. Using `do` when you meant `yield` silently discards results.
- **String interpolation is not safe for SQL/HTML/shell:** the `s` and `f` interpolators do not escape or sanitize input, exactly like Python f-strings. Always use parameterized APIs for untrusted input.
- **`Any` as a type is a trap:** it discards all compile-time guarantees. Prefer concrete types, bounded type parameters, Scala 3 unions, sealed hierarchies, or type classes.
- **Bare `null` dereference:** using `null` instead of `Option` reproduces Python's `AttributeError: 'NoneType'` failure mode at runtime with no compile-time warning. Use `Option[T]` so the compiler enforces handling the empty case.
- **Throwing exceptions instead of returning `Either`/`Try`:** thrown exceptions are invisible in the type signature, so callers can forget to handle them. Use `Either[E, A]` or `Try[A]` to make failure part of the contract.
- **`eq` vs `==`:** `eq` tests reference identity (only on `AnyRef`); `==` calls `.equals` for structural equality. Do not use `eq` on value types like `Int`.
- **Mutable collections by accident:** Scala's default `List`, `Map`, `Set` are immutable. You must explicitly import from `scala.collection.mutable` when mutation is needed — keep that import as local as possible.
- **Never-reassigned `var`:** the compiler can flag these with `-Wunused:all`. A `var` that is never reassigned should be a `val`.

## Verification

Use this checklist to confirm a translation is faithful and idiomatic, not just syntactically valid:

- [ ] Every Python snippet has a complete Scala 3 counterpart with explicit parameter and return types — no `Any`, no untyped lambdas.
- [ ] The Scala compiles cleanly under `-Wunused:all -Werror` (no unused bindings, no never-reassigned `var`s slipping through).
- [ ] Negative-number arithmetic was checked: `//`/`%` translations use `Math.floorDiv`/`Math.floorMod` wherever Python's flooring semantics matter.
- [ ] Absence is modeled with `Option` and failure with `Either`/`Try` rather than `null` or bare throws, so the possibility is visible in each signature.
- [ ] Input preconditions are enforced (`require`/validation) at function boundaries, matching the guards in the Python source.
- [ ] String interpolation is never used to build SQL, shell, or HTML from untrusted input; parameterized APIs are used instead.

To verify a translated snippet compiles with the recommended lint flags, save it to a file and run:

```powershell
# Using scala-cli (recommended for quick checks on Windows)
scala-cli run . --scala-version 3.3.x --compiler-options "-Wunused:all,-Werror"
```

```powershell
# Or compile a single file directly
scala-cli compile MyTranslation.scala --scala-version 3.3.x --compiler-options "-Wunused:all,-Werror"
```

Expected output on success: no warnings, no errors, exit code 0.

## Related skills

- `scala-best-practices`: idiomatic Scala beyond literal syntax translation — when to fold instead of loop, how to structure error types.
- `python-to-scala-data-structures`: deeper mapping of collections and their operations (`groupBy`, `foldLeft`, mutable vs immutable trade-offs).
- `scala-functional-programming`: leveraging `Option`/`Either`/`Try`, type classes, and `for`-comprehensions for cleaner, safer code.
- `scala-3-migration`: moving from Scala 2 to Scala 3 (new control syntax, `given`/`using`, union and enum types).
