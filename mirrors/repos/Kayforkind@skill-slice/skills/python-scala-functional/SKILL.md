---
name: python-scala-functional
version: 1.1.1
description: "Recasts Python higher-order callables, decorators, None, match, yield, try/except, recursion, and duck typing into Scala 3 function values, Option, sealed-ADT match, LazyList or Iterator, Try/Either, @tailrec, and given/using type classes. Use for ports that must prove absence, exhaustiveness, or failure in the type. Not a List/Map API encyclopedia, not a class-inheritance mapper, and not a naming-convention style sheet."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Python to Scala Functional Programming Translation

Translating Python into functional Scala is not a mechanical syntax swap. The
deeper goal is to move logic from a dynamically typed, runtime-checked world into
a statically typed, compile-time-checked one. Every pattern below exists to
preserve the *intent* of the Python code while letting the Scala compiler prove
properties that Python can only discover at runtime: that a value's absence is
handled, that a match covers every case, that a failure is acknowledged. Read each
example as "what guarantee did we gain?" rather than "what is the equivalent
keyword?" The Scala snippets are written in Scala 3 syntax unless a block is
explicitly marked as Scala 2.

## When to Use

Reach for this skill when the Python you are porting leans on dynamic or
higher-order features, because those are exactly the places where Scala's type
system changes how the code should be shaped:

- Converting higher-order functions, decorators, or closures, where Python passes
  callables around untyped and Scala wants precise `A => B` function values.
- Replacing Python's `None` checks with `Option`, so that "might be missing"
  becomes a fact the compiler enforces instead of a convention you must remember.
- Converting Python `match` statements (3.10+) into Scala `match` expressions over
  sealed data, which unlocks compile-time exhaustiveness checking.
- Translating Python generators (`yield`) into `LazyList` or `Iterator` when you
  need lazy or potentially infinite sequences without loading everything in memory.
- Replacing `try`/`except` with `Try` or `Either` so that failure travels in the
  return type and callers cannot silently ignore it.
- Optimizing recursion with tail calls, because the JVM has no automatic
  tail-call optimization and naive recursion overflows the stack on large inputs.
- Replacing duck typing / `singledispatch` with type classes (`given`/`using`).
- Translating `functools.partial` / currying into Scala's multiple parameter lists.

### Do Not Use

These patterns are tools, not commandments. Applying them blindly produces code
that is harder to read than the imperative original, so weigh the trade-off:

- **Tight, performance-critical loops.** When you have measured that a hot loop
  matters, a local `var` and `while` can be the right call: they avoid allocation
  and let the JIT produce the fastest code. The functional style is about
  expressiveness and safety, not raw throughput in micro-benchmarked sections.
- **Trivial scripts.** For a ten-line glue script, a direct imperative
  translation is often clearer than wrapping everything in monads. Optimize for
  the reader, and the reader of a throwaway script wants the obvious version.
- **Scala 2 implicit conversions.** Prefer Scala 3's `given`/`using` for type
  classes. *Why:* implicit conversions fire invisibly and can turn a typo into a
  silent, surprising coercion, which makes bugs hard to trace. `given`/`using`
  express the same idea while keeping the intent (and the resolution) explicit.
- **`Stream` for lazy sequences.** Use `LazyList` (Scala 2.13+). *Why:* the old
  `Stream` evaluated its head eagerly, which created subtle memory and
  performance footguns; `LazyList` is lazy in both head and tail and is the
  supported type going forward.

## Prerequisites

- **Scala 3** (preferred) or **Scala 2.13+** for `LazyList` support.
- **Python 3.10+** if the source uses structural `match` statements.
- A build tool such as `sbt` or `scala-cli` for compiling and verifying snippets.
- On Windows (PowerShell), use `scala-cli` or `sbt` from a standard terminal;
  paths like `~\agent-skills\library\python-scala-functional\` are
  the primary working directory for this skill.

## Procedure

Each row below pairs a Python construct with its Scala counterpart and the reason
the counterpart is worth the change — the guarantee you buy by translating.

1. **Higher-order functions & lambdas → `A => B` function values.** Scala
   functions are typed values, so a lambda with the wrong shape fails to compile
   rather than blowing up at the call site like a mistyped Python callable.
2. **Decorators → wrapping functions, by-name parameters, or composition.** Scala
   has no decorator syntax, but a by-name parameter (`=> A`) reproduces the
   "run code around a computation" effect while keeping evaluation under the
   wrapper's control.
3. **`match` statements → `match` expressions over sealed ADTs.** Matching on a
   closed hierarchy lets the compiler verify exhaustiveness, so adding a case
   surfaces every place that forgot to handle it instead of failing in production.
4. **`None` checks → `Option` with `map`/`flatMap`/`getOrElse`.** Absence becomes
   part of the type, so the empty case cannot be forgotten and there is no
   `NullPointerException` to chase.
5. **Generators (`yield`) → `LazyList` or `Iterator`.** Both model on-demand,
   possibly infinite sequences; `LazyList` memoizes for re-traversal while
   `Iterator` is a cheaper single pass.
6. **`try`/`except` → `Try` or `Either`.** Failure moves into the return type,
   becoming visible and composable, so callers must acknowledge it rather than
   relying on an unchecked exception propagating.
7. **Recursion → `@tailrec` where the call is in tail position.** The JVM does not
   optimize tail calls automatically, so the annotation both documents intent and
   forces the compiler to prove the loop rewrite is safe.
8. **Duck typing → type classes (`given`/`using`).** Behavior attaches to types at
   compile time and can be added to types you do not own, with a missing instance
   reported as a compile error instead of a runtime `AttributeError`.
9. **`functools.partial` → multiple parameter lists.** Grouped parameter lists
   enable natural partial application and improve type inference.

## Examples

### Higher-Order Functions

Python callables are first-class but untyped at the boundary; the wrong function
shape is only caught when it is finally invoked. Scala makes the function type
explicit, so `applyTwice` can only ever be handed something that maps `A` to `A`.

```python
# Python: functions are first-class objects, typed here with Callable.
from typing import Callable, TypeVar

T = TypeVar("T")


def apply_twice(f: Callable[[T], T], x: T) -> T:
    """Apply a unary function to its own result."""
    return f(f(x))


def make_multiplier(n: int) -> Callable[[int], int]:
    """Return a closure that multiplies its argument by n."""
    return lambda x: x * n


double: Callable[[int], int] = make_multiplier(2)
result: int = apply_twice(double, 5)  # 20
```

```scala
// Scala 3: `A => B` is an ordinary value with a precise, compiler-checked type.
def applyTwice[A](f: A => A, x: A): A = f(f(x))

def makeMultiplier(factor: Int): Int => Int = x => x * factor

val double: Int => Int = makeMultiplier(2)
val result: Int = applyTwice(double, 5) // 20
```

The type parameter `A` ties the input and output of `f` together: you cannot pass
a `String => Int` where an `Int => Int` is required, so a whole class of Python
runtime errors becomes impossible.

### Decorators → Function Wrapping / By-Name Parameters

A Python decorator wraps a function to run code before and after it. Scala has no
decorator syntax, so you reproduce the effect by wrapping a function value or, more
flexibly, by taking the work as a **by-name parameter** (`=> A`) whose evaluation
is deferred until inside the wrapper. Note that both versions log on the failure
path too — a wrapper that only logs success would hide the very errors you most
want to see.

```python
# Python: a decorator that logs entry, exit, and failure.
import functools
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        try:
            result = func(*args, **kwargs)
            print(f"Finished {func.__name__}")
            return result
        except Exception as exc:
            print(f"Failed {func.__name__}: {exc}")
            raise

    return wrapper


@log_calls
def add(a: int, b: int) -> int:
    return a + b
```

```scala
// Scala 3: wrap a function value. Explicit in/out types; logs on every path.
import scala.util.control.NonFatal

def logCalls[A, B](name: String, f: A => B): A => B =
  require(name.nonEmpty, "decorated operation must have a name")
  (a: A) =>
    println(s"Calling $name")
    try
      val result = f(a)
      println(s"Finished $name")
      result
    catch
      case NonFatal(e) =>
        println(s"Failed $name: ${e.getMessage}")
        throw e

val add: (Int, Int) => Int = (a, b) => a + b
// `tupled` adapts the 2-arg function to a single tuple argument so it fits `A => B`.
val loggedAdd: ((Int, Int)) => Int = logCalls("add", add.tupled)
val sum: Int = loggedAdd((2, 3)) // logs around the call, returns 5

// Alternative: a by-name parameter defers evaluation of `block` until the
// wrapper decides to run it, which is the closest analogue to wrapping a body.
def withLogging[A](name: String)(block: => A): A =
  require(name.nonEmpty, "logged block must have a name")
  println(s"Calling $name")
  try
    val result = block
    println(s"Finished $name")
    result
  catch
    case NonFatal(e) =>
      println(s"Failed $name: ${e.getMessage}")
      throw e

val product: Int = withLogging("multiply")(6 * 7) // 42
```

Catching `NonFatal` (rather than every `Throwable`) is deliberate: fatal errors
like `OutOfMemoryError` should propagate untouched instead of being logged and
swallowed. The `require` calls reject a missing operation name up front, turning a
silent "logged as empty string" bug into an immediate, descriptive failure.

### Pattern Matching

The biggest win in translating `match` is replacing Python's structural matching
on dynamic values with matching on a **sealed** algebraic data type (ADT). Modeling
the domain as a closed `enum` means the compiler knows every possible case and
will warn you when a `match` misses one — a guarantee that is simply unavailable
when you match on an untyped `Any`.

```python
# Python (3.10+): match on a tagged union of dataclasses.
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Success:
    value: int


@dataclass(frozen=True)
class Failure:
    message: str


Result = Union[Success, Failure]


def handle(result: Result) -> str:
    match result:
        case Success(value) if value > 100:
            return f"Big success: {value}"
        case Success(value):
            return f"Success: {value}"
        case Failure(message):
            return f"Failed: {message}"
```

```scala
// Scala 3: a sealed enum. The compiler checks `handle` covers every case.
enum Result:
  case Success(value: Int)
  case Failure(message: String)

def handle(result: Result): String = result match
  case Result.Success(value) if value > 100 => s"Big success: $value"
  case Result.Success(value)                => s"Success: $value"
  case Result.Failure(message)              => s"Failed: $message"
```

For richer, nested matching, model the whole shape as a recursive ADT instead of
reaching for `Any`. The example below mirrors the classic "match on arbitrary JSON"
pattern, but every variant is enumerated, so there is no `ClassCastException` risk
and no untyped map access:

```python
# Python: a recursive JSON model with structural matching.
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class JNull:
    pass


@dataclass(frozen=True)
class JNumber:
    value: float


@dataclass(frozen=True)
class JString:
    value: str


@dataclass(frozen=True)
class JArray:
    items: list["Json"]


@dataclass(frozen=True)
class JObject:
    fields: dict[str, "Json"]


Json = Union[JNull, JNumber, JString, JArray, JObject]


def describe(value: Json) -> str:
    match value:
        case JNull():
            return "null"
        case JNumber(n) if n > 0:
            return f"positive number: {n}"
        case JNumber(n):
            return f"non-positive number: {n}"
        case JString(s):
            return f"string of length {len(s)}"
        case JArray([x, y]):
            return f"pair: {x}, {y}"
        case JArray(items):
            return f"array of {len(items)} items"
        case JObject(fields):
            name = fields.get("name")
            age = fields.get("age")
            if isinstance(name, JString) and isinstance(age, JNumber):
                return f"{name.value} is {int(age.value)}"
            return f"object with {len(fields)} fields"
```

```scala
// Scala 3: a recursive, sealed ADT — every JSON shape is enumerated up front.
enum Json:
  case JNull
  case JNumber(value: Double)
  case JString(value: String)
  case JArray(items: List[Json])
  case JObject(fields: Map[String, Json])

def describe(value: Json): String = value match
  case Json.JNull                 => "null"
  case Json.JNumber(n) if n > 0   => s"positive number: $n"
  case Json.JNumber(n)            => s"non-positive number: $n"
  case Json.JString(s)            => s"string of length ${s.length}"
  case Json.JArray(x :: y :: Nil) => s"pair: $x, $y"
  case Json.JArray(items)         => s"array of ${items.length} items"
  case Json.JObject(fields)       =>
    // Nested match keeps the lookup type-safe; no untyped Map access.
    (fields.get("name"), fields.get("age")) match
      case (Some(Json.JString(name)), Some(Json.JNumber(age))) =>
        s"$name is ${age.toInt}"
      case _ =>
        s"object with ${fields.size} fields"
```

If you later add a `JBoolean` case to the `enum`, the compiler immediately flags
`describe` as non-exhaustive. That feedback loop — change the data, get told every
place that must adapt — is the core reason to prefer a sealed ADT over `Any`.

### Option Handling (None / null Safety)

Python's `None` is invisible to the type checker unless you annotate `Optional` and
remember to test for it; a forgotten check surfaces as an `AttributeError` deep in
a call chain. `Option[T]` makes "value might be absent" part of the type, so the
compiler forces you to deal with the empty case, and `map`/`flatMap` let you chain
operations that short-circuit automatically. The example uses a concrete in-memory
repository so the snippet is complete and runnable.

```python
# Python: Optional plus explicit None checks.
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class Address:
    street: str
    city: str
    zip_code: str


@dataclass
class User:
    id: int
    name: str
    email: str
    address: Optional[Address]


class UserRepository(Protocol):
    def find(self, user_id: int) -> Optional[User]:
        raise NotImplementedError


def get_user_email(repo: UserRepository, user_id: int) -> Optional[str]:
    user = repo.find(user_id)
    if user is None:
        return None
    return user.email


def get_user_city(repo: UserRepository, user_id: int) -> Optional[str]:
    user = repo.find(user_id)
    if user is None or user.address is None:
        return None
    return user.address.city
```

```scala
// Scala 3: the same domain, with absence encoded in the types.
final case class Address(street: String, city: String, zipCode: String)
final case class User(id: Int, name: String, email: String, address: Option[Address])

trait UserRepository:
  def find(userId: Int): Option[User]

class UserService(repo: UserRepository):

  // map: transform the value inside the Option without unwrapping it.
  def userEmail(userId: Int): Option[String] =
    repo.find(userId).map(_.email)

  // flatMap: chain a step that is itself optional (address may be absent).
  def userCity(userId: Int): Option[String] =
    repo.find(userId).flatMap(_.address).map(_.city)

  // for-comprehension: the same chain read top-to-bottom; stops at the first None.
  def userCityForComp(userId: Int): Option[String] =
    for
      user    <- repo.find(userId)
      address <- user.address
    yield address.city

// A concrete repository so the example runs end to end.
val repo: UserRepository = new UserRepository:
  private val users: Map[Int, User] = Map(
    1 -> User(
      id = 1,
      name = "Ada",
      email = "ada@example.com",
      address = Some(Address("5 Analytical Way", "London", "EC1A"))
    )
  )
  def find(userId: Int): Option[User] = users.get(userId)

val service = UserService(repo)

// Getting the value out — always with a defined behaviour for the empty case:
val email: String = service.userEmail(1).getOrElse("no-email@example.com")

// fold handles both branches explicitly and returns a single type.
val greeting: String =
  service.userCity(1).fold("city unknown")(city => s"lives in $city")

// AVOID `.get`: it throws NoSuchElementException on None. Prefer getOrElse / fold /
// pattern match so the empty case is handled at compile time, not as a crash.
```

Because `userCity` returns `Option[String]`, a caller physically cannot reach the
city without first deciding what to do when it is missing. That is the same logic
as the Python `if user is None or user.address is None` guard, except the compiler
now refuses to let you skip it.

### Generators → Iterators / LazyList

A Python generator produces values lazily and can be infinite. Scala offers two
lazy translations with a meaningful trade-off: `LazyList` memoizes each element it
computes (great when you re-traverse, but holding a reference to the head retains
everything you have forced, which can leak memory for huge prefixes), while
`Iterator` is a cheaper single pass that keeps nothing.

```python
# Python: an infinite generator, sliced to the first ten values.
import itertools
from typing import Iterator


def fibonacci() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


first_ten: list[int] = list(itertools.islice(fibonacci(), 10))
```

```scala
// Scala 3: LazyList — elements computed on demand, then cached (memoized).
val fibonacci: LazyList[BigInt] =
  def loop(a: BigInt, b: BigInt): LazyList[BigInt] = a #:: loop(b, a + b)
  loop(0, 1)

// Defensive helper: validate the requested count before forcing the stream.
def firstFibonacci(count: Int): List[BigInt] =
  require(count >= 0, s"count must be non-negative, got $count")
  fibonacci.take(count).toList

val firstTen: List[BigInt] = firstFibonacci(10)

// Iterator — single pass, not memoized. `unfold` expresses the state machine
// without any mutable `var`, so there is no shared mutable state to misuse.
def fibonacciIterator: Iterator[BigInt] =
  Iterator.unfold((BigInt(0), BigInt(1))) { case (a, b) =>
    Some((a, (b, a + b)))
  }

val firstTenAgain: List[BigInt] = fibonacciIterator.take(10).toList
```

Using `BigInt` rather than `Int` is a deliberate defensive choice: Fibonacci
numbers overflow a 32-bit `Int` by the 47th term, and a silent wraparound to a
negative number is exactly the kind of bug static types should help you avoid.
Reach for `LazyList` when you will re-read the sequence, and `Iterator` when one
pass is enough.

### Try / Either for Error Handling

Replacing `try`/`except` with `Try` or `Either` moves failure into the return type.
Use `Try` when you simply want to capture a thrown exception; use `Either` with a
**sealed error type** when callers need to distinguish *why* something failed. A
typed error ADT is far more useful than a bare `String` message, because the
compiler can then check that every failure mode is handled.

```python
# Python: a total parse with a default, plus a typed error union.
from dataclasses import dataclass
from typing import Union


def parse_int(s: str) -> int:
    """Total parse with a default — never raises."""
    try:
        return int(s.strip())
    except (ValueError, AttributeError):
        return 0


@dataclass(frozen=True)
class Empty:
    pass


@dataclass(frozen=True)
class NotANumber:
    input: str


@dataclass(frozen=True)
class NotPositive:
    value: int


ParseError = Union[Empty, NotANumber, NotPositive]


def parse_positive(s: str) -> Union[ParseError, int]:
    text = s.strip()
    if not text:
        return Empty()
    try:
        n = int(text)
    except ValueError:
        return NotANumber(text)
    if n <= 0:
        return NotPositive(n)
    return n
```

```scala
// Scala 3: Try captures exceptions; Either with a sealed ADT distinguishes errors.
import scala.util.{Try, Success, Failure}

// Total parse with a default — Try captures the exception, getOrElse recovers.
def parseInt(s: String): Int =
  Try(s.strip.toInt).getOrElse(0)

// Sealed error ADT: the compiler checks every failure mode is handled.
enum ParseError:
  case Empty
  case NotANumber(input: String)
  case NotPositive(value: Int)

def parsePositive(s: String): Either[ParseError, Int] =
  val text = s.strip
  if text.isEmpty then Left(ParseError.Empty)
  else
    Try(text.toInt) match
      case Failure(_)     => Left(ParseError.NotANumber(text))
      case Success(n) if n <= 0 => Left(ParseError.NotPositive(n))
      case Success(n)     => Right(n)

// Caller must handle every error variant — no silent skip.
def describe(result: Either[ParseError, Int]): String = result match
  case Right(n)                  => s"valid: $n"
  case Left(ParseError.Empty)    => "input was empty"
  case Left(ParseError.NotANumber(input)) => s"not a number: $input"
  case Left(ParseError.NotPositive(n))    => s"not positive: $n"
```

### Currying and Partial Application

Python reaches for `functools.partial` to fix some arguments of a function. Scala
bakes the same idea into the language through multiple parameter lists: supplying
the first list returns a function awaiting the rest. Beyond ergonomics, grouped
parameter lists improve type inference — Scala can infer the type of a lambda in a
later list from arguments already supplied in an earlier one.

```python
# Python: partial application via functools.partial.
from functools import partial
from typing import Callable


def add(a: int, b: int, c: int) -> int:
    return a + b + c


add_5: Callable[[int, int], int] = partial(add, 5)
result: int = add_5(3, 2)  # 10
```

```scala
// Scala 3: multiple parameter lists make partial application natural.
def add(a: Int)(b: Int)(c: Int): Int = a + b + c

val add5: Int => Int => Int = add(5)  // first argument fixed
val result: Int = add5(3)(2)          // 10

// Convert between curried and uncurried shapes when an API needs the other form.
val uncurried: (Int, Int, Int) => Int = Function.uncurried(add)
val curriedAgain: Int => Int => Int => Int = uncurried.curried

// Grouped lists also aid inference: the compiler knows B before the lambda,
// so `_ + _` needs no type annotations.
def fold[A, B](init: B)(items: List[A])(combine: (B, A) => B): B =
  items.foldLeft(init)(combine)

val total: Int = fold(0)(List(1, 2, 3))(_ + _) // 6
```

The explicit annotation `val add5: Int => Int => Int = add(5)` documents the
partially applied type at the call site, which is clearer than relying on the
reader to infer it and guards against an accidental extra argument.

### Tail Recursion

Python has no tail-call optimization, so deep recursion overflows the stack and the
usual workaround is an explicit loop. Scala can rewrite a tail-recursive function
into a loop, but only if the recursive call is genuinely in tail position. The
`@tailrec` annotation does **not** make code tail-recursive — it asks the compiler
to *prove* it is, and fails the build if it is not. That turns "I think this is
stack-safe" into a checked fact.

```python
# Python: naive recursion overflows for large n; the iterative form is the fix.
def factorial(n: int) -> int:
    if n < 0:
        raise ValueError(f"factorial is undefined for negative n: {n}")
    if n <= 1:
        return 1
    return n * factorial(n - 1)  # not tail-call optimized


def factorial_iter(n: int) -> int:
    if n < 0:
        raise ValueError(f"factorial is undefined for negative n: {n}")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

```scala
// Scala 3: an accumulator turns the recursion tail-recursive; @tailrec proves it.
import scala.annotation.tailrec

def factorial(n: Int): BigInt =
  require(n >= 0, s"factorial is undefined for negative n: $n")
  @tailrec
  def loop(remaining: Int, acc: BigInt): BigInt =
    if remaining <= 1 then acc
    else loop(remaining - 1, remaining * acc)
  loop(n, BigInt(1))

// If `loop` were not in tail position, this would FAIL TO COMPILE — so you never
// silently ship a version that overflows the stack on large input.
@tailrec
def sum(items: List[Int], acc: Int = 0): Int = items match
  case Nil          => acc
  case head :: tail => sum(tail, acc + head)
```

Two defensive details: the `require(n >= 0, s"factorial is undefined for negative
n: $n")` guard rejects undefined input immediately with a clear, named reason, and
`BigInt` prevents factorial's rapid overflow of a machine `Int`. When recursion is
*not* in tail position — for example walking a tree where a call recurses on two
children — `@tailrec` cannot apply; reach for an explicit stack or a trampoline
(`scala.util.control.TailCalls`) instead of forcing the annotation.

### Type Classes (the principled replacement for duck typing)

Python's duck typing lets any object with the right method stand in for an
interface; the closest disciplined analog is `functools.singledispatch`, which
dispatches on a value's type and can be extended for new types after the fact.
Scala expresses this as **type classes**: behavior defined separately from the data
it operates on, resolved by the compiler. The payoff is that you can add behavior
to types you do not own, and a missing instance is a compile error rather than a
runtime surprise.

```python
# Python: singledispatch — ad-hoc polymorphism, retroactively extensible.
from functools import singledispatch


@singledispatch
def show(value: object) -> str:
    raise NotImplementedError(f"no show instance for {type(value).__name__}")


@show.register
def _(value: int) -> str:
    return f"Int: {value}"


@show.register
def _(value: str) -> str:
    return f"Str: {value}"


def display(value: object) -> str:
    return show(value)
```

```scala
// Scala 3: a type class with given instances and a `using` requirement.
trait Show[A]:
  def show(a: A): String

object Show:
  // Instances are ordinary `given` values the compiler supplies automatically.
  given Show[Int] with
    def show(a: Int): String = s"Int: $a"

  given Show[String] with
    def show(a: String): String = s"Str: $a"

// `using` requests the instance; the call site needs no explicit wiring.
def display[A](a: A)(using s: Show[A]): String = s.show(a)

val shownInt: String = display(42)   // "Int: 42"
val shownStr: String = display("hi") // "Str: hi"
```

```scala
// Scala 2: the identical pattern with `implicit` instead of `given`/`using`.
trait Show[A] {
  def show(a: A): String
}

object Show {
  implicit val intShow: Show[Int] = new Show[Int] {
    def show(a: Int): String = s"Int: $a"
  }
  implicit val stringShow: Show[String] = new Show[String] {
    def show(a: String): String = s"Str: $a"
  }
}

def display[A](a: A)(implicit s: Show[A]): String = s.show(a)
```

Call `display` on a type with no `Show` instance in scope and the Scala 3 compiler
reports a precise "no given instance of type Show[Double] was found" error at the
call site — the same mistake that `singledispatch` only catches when the unhandled
value actually flows through at runtime.

## Pitfalls

- **Never use `Stream` for lazy sequences.** Use `LazyList` (Scala 2.13+). The old
  `Stream` evaluated its head eagerly, creating subtle memory and performance
  footguns. `LazyList` is lazy in both head and tail and is the supported type.
- **Never call `.get` on `Option`.** It throws `NoSuchElementException` on `None`.
  Always use `getOrElse`, `fold`, or pattern match so the empty case is handled at
  compile time.
- **`@tailrec` does not make code tail-recursive.** It asks the compiler to *prove*
  it is. If the recursive call is not in tail position, the build fails. For
  non-tail recursion (e.g. tree walks), use a trampoline (`scala.util.control.TailCalls`)
  or an explicit stack instead.
- **Avoid Scala 2 implicit conversions.** Prefer Scala 3's `given`/`using` for type
  classes. Implicit conversions fire invisibly and can turn a typo into a silent
  coercion that makes bugs hard to trace.
- **Catch `NonFatal`, not `Throwable`.** Fatal errors like `OutOfMemoryError` should
  propagate untouched. Catching everything can swallow critical JVM errors.
- **Use `BigInt` for factorial and Fibonacci.** Factorial overflows a 32-bit `Int`
  quickly; Fibonacci overflows by the 47th term. A silent wraparound to a negative
  number is exactly the bug static types should prevent.
- **Do not match on `Any` or use `asInstanceOf`.** Model the domain as a sealed ADT
  so the compiler verifies exhaustiveness and there is no `ClassCastException` risk.
- **Do not use a bare `String` for error types in `Either`.** Use a sealed error ADT
  so the compiler can check that every failure mode is handled by callers.
- **Holding a `LazyList` head reference leaks memory.** `LazyList` memoizes forced
  elements. For huge prefixes where you only need a single pass, use `Iterator`
  instead.
- **Do not apply functional patterns blindly to hot loops.** When you have measured
  that a performance-critical loop matters, a local `var` and `while` can be the
  right call. Functional style is about expressiveness and safety, not raw
  throughput in micro-benchmarked sections.

## Verification

Treat this as a review checklist with the reasoning attached, not a set of boxes to
tick mechanically — the point of each check is the guarantee it confirms:

- [ ] **Absence is typed.** Confirm Python functions that returned `None` now
  return `Option`, so the empty case is checked by the compiler rather than left to
  a convention a caller might forget.
- [ ] **Recursion is stack-safe where it can be.** Confirm tail-position recursion
  carries `@tailrec`; for genuinely non-tail recursion (e.g. tree walks), confirm a
  trampoline or explicit stack is used instead of forcing an annotation that cannot
  apply.
- [ ] **Failure is in the type.** Confirm `try`/`except` became `Try` or `Either`,
  and that a sealed error ADT is used wherever callers must distinguish failure
  modes rather than read a free-text message.
- [ ] **Matches are exhaustive.** Confirm `match` expressions run over sealed ADTs
  (not `Any` and not `asInstanceOf`), so the compiler can verify every case is
  covered.
- [ ] **Laziness is deliberate.** Confirm `yield` generators became `LazyList`
  (when the sequence is re-traversed and memoization helps) or `Iterator` (when a
  single pass suffices), chosen on purpose rather than by habit.
- [ ] **Let the compiler talk.** Build with `-Xlint` (Scala 2) or `-Wunused` and
  `-Werror` (Scala 3) to surface unused bindings, non-exhaustive matches, and dead
  code as failures instead of warnings you might scroll past.
- [ ] **Keep style out of review.** Run Scalafmt and Scalafix so formatting and
  idiom are enforced automatically, leaving human review free to focus on logic.

### Compile-time verification commands

```powershell
# Scala 3 — compile with strict warnings as errors (scala-cli)
scala-cli compile . --scala-version 3 --scalac-opts "-Wunused,-Werror"

# Scala 2 — compile with lint flags (sbt)
sbt "set scalacOptions ++= Seq("-Xlint", "-Xfatal-warnings")" compile

# Run Scalafmt check (does not modify files)
scalafmtCheckAll

# Run Scalafix rules
sbt "scalafix --check"
```

## Related skills

- `scala-advanced-types`
- `python-to-scala-migration`
- `functional-programming-patterns`
