---
name: python-scala-idioms
version: 1.1.1
description: "Rewrites Python-shaped Scala toward host idioms: val over var, expression-bodied match, camelCase, Option/Either instead of null or sentinels, smart constructors, and companion apply. Trigger on Pythonisms, snake_case in Scala, or a token-for-token port that still mutates. Not for List/Map operator tables, not for HOF or type-class cookbooks, and never a dataclass-to-case-class OOP construct map."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Python to Idiomatic Scala Translation

## When to Use

Use this skill when:
- Translating existing Python logic into Scala and the goal is clean, idiomatic Scala — not a token-for-token port.
- A developer familiar with Python is writing Scala and needs to avoid "Pythonisms" (excessive mutation, `None` checks, statement-based logic, `isinstance` chains, `try/except` for control flow).
- You want maintainable, type-safe, performant Scala that leverages the language's functional core: a compiler that proves whole classes of bugs cannot happen, and data structures that are safe to share across threads.

**Trigger keywords:** "translate Python to Scala", "port Python to Scala", "idiomatic Scala from Python", "Python to Scala migration", "Scala equivalent of Python", "rewrite Python in Scala".

### Do Not Use

- **Throwaway scripts** where idiomatic style and performance are irrelevant — the discipline below costs typing effort that a five-line script will never repay.
- **Measured hot paths** where a profiler shows a specific loop is the bottleneck. Immutable collections allocate a new structure on every transformation; in a tight inner loop that allocation pressure can dominate runtime. If — and only if — a profiler confirms the bottleneck, a local `var` or a primitive `Array` is a legitimate, well-scoped optimization. The rule is "immutable by default," not "immutable at any cost." Reach for mutation because a measurement told you to, never on a hunch.

### Deprecated Libraries and Patterns

Prefer modern, actively maintained versions. Older lines stop receiving security patches and lack the language features that make the idioms below ergonomic.

| Concern | Preferred | Avoid | Reason |
|---------|-----------|-------|--------|
| Scala version | **Scala 3.x** | Scala 2.13 for new code | Scala 3 adds first-class `enum` ADTs, union types, and `opaque type`s — the tools this guide relies on to replace Python's dynamic typing. Scala 2.13 still works but gives up ergonomics and long-term support runway. |
| JVM target | **Java 17 LTS or later** | Java 8, 11 | Java 8 and 11 are reaching or past end of public updates on many distributions. |
| Actor framework | **Akka 2.7+** or **Apache Pekko** | Akka 2.6 and earlier | Older releases no longer receive the same maintenance; typed actor APIs in 2.7+ are far easier to use correctly. |
| Web framework | **Play 3.x** | Play 2.8 and earlier | 3.x targets current Scala/JVM versions and keeps you on a maintained dependency tree. |

## Prerequisites

- **Scala 3.x** toolchain (e.g., `scala-cli`, `sbt` with Scala 3 plugin, or `mill`).
- **Java 17 LTS or later** on the system `PATH`.
- Working knowledge of Python; this guide maps Python patterns to Scala equivalents.

## Procedure

Apply three habits — immutability, expression-based logic, and type safety — and let them drive the mechanical substitutions. Replace Python's dynamic patterns (`isinstance`, `None` checks, `try/except` for control flow) with Scala's static equivalents (sealed `enum`s, `Option`, `Either`/`Try`).

### Core Principles

1. **Prefer immutability** — `val` over `var`, immutable collections by default. Immutable values can be shared freely across threads with no locking and reasoned about locally, because nothing can change them out from under you.
2. **Expression-based** — almost everything returns a value; prefer expressions to statements. This removes the window where a variable is declared but not yet assigned, a classic source of bugs.
3. **Type safety** — encode invariants in the type system instead of checking them at runtime; avoid `Any`. A mistake the compiler catches never becomes a production incident.
4. **Pattern matching** — replace if-else chains keyed on one value with `match`, which is more readable and lets the compiler warn about unhandled cases.
5. **Make absence and failure explicit** — use `Option`, `Either`, and `Try` instead of `null` or sentinel returns, so callers cannot silently ignore the cases that go wrong.

### Step 1 — Replace Mutable State with Immutable Values

In Python, `self.count += 1` mutates shared state: every reference to the object sees the new value, which makes concurrent code fragile. Scala's idiomatic answer is a value that is never modified — operations return a *new* instance — so old references stay valid and the data is safe to share.

```python
# Python - mutable by default; every alias of `self` observes the change
class Counter:
    def __init__(self, count: int = 0) -> None:
        self.count = count

    def increment(self) -> int:
        self.count += 1
        return self.count
```

```scala
// Scala - an immutable value; `increment` returns a new Counter instead of mutating in place
final case class Counter(count: Int = 0):
  def increment: Counter = copy(count = count + 1)

val c1: Counter = Counter()
val c2: Counter = c1.increment // Counter(1)
val c3: Counter = c2.increment // Counter(2)
// c1 is still Counter(0) — no aliasing surprises, safe to share across threads
```

### Step 2 — Convert Statement-Based Logic to Expressions

The Python version declares `status`, then assigns it on every branch. If you ever add a branch and forget to assign, you get an `UnboundLocalError` at runtime. In Scala, `match` *is* an expression that yields the value directly, so there is no uninitialized window and the compiler guarantees every branch produces a `String`.

```python
# Python - statement-based; `status` is assigned on each branch
def get_status(code: int) -> str:
    if code == 200:
        status = "OK"
    elif code == 404:
        status = "Not Found"
    elif code == 500:
        status = "Internal Server Error"
    else:
        status = f"Unknown ({code})"
    return status
```

```scala
// Scala - expression-based; the match result is the return value, no intermediate variable
def getStatus(code: Int): String = code match
  case 200 => "OK"
  case 404 => "Not Found"
  case 500 => "Internal Server Error"
  case other => s"Unknown ($other)"
```

### Step 3 — Model Domain Variants with Sealed Hierarchies

Passing a bare `str` for the payment method has two costs: a typo like `"crdit"` compiles fine and only fails at runtime, and the code carries no record of which fields each method needs. A Scala 3 `enum` (a sealed hierarchy) closes the set of variants at compile time, attaches the right data to each one, and makes the compiler flag any `match` that forgets a case.

```python
# Python - loose typing; an unknown method only fails at runtime, and fields are implicit
def process_payment(method: str, amount: float) -> None:
    if method == "credit":
        charge_credit_card(amount)
    elif method == "debit":
        charge_debit_card(amount)
    elif method == "crypto":
        transfer_crypto(amount)
    else:
        raise ValueError(f"Unknown payment method: {method}")
```

```scala
import java.util.UUID

// Scala - a sealed enum: the set of methods is closed and each carries exactly its own data
enum PaymentMethod:
  case CreditCard(number: String, expiry: String)
  case DebitCard(number: String)
  case Crypto(walletAddress: String)

final case class PaymentError(reason: String)
final case class Receipt(transactionId: String, method: PaymentMethod, amountCents: Long)

// Validate at the boundary (positive amount), then dispatch. The compiler verifies that
// every PaymentMethod case is handled — add a new case and this stops compiling until you do.
def processPayment(method: PaymentMethod, amount: BigDecimal): Either[PaymentError, Receipt] =
  if amount <= 0 then
    Left(PaymentError(s"Amount must be positive, got: $amount"))
  else
    val amountCents: Long =
      (amount * 100).setScale(0, BigDecimal.RoundingMode.HALF_UP).toLong
    val transactionId: String = UUID.randomUUID().toString
    method match
      case PaymentMethod.CreditCard(number, _) if number.isBlank =>
        Left(PaymentError("Credit card number must not be blank"))
      case PaymentMethod.CreditCard(_, _) =>
        Right(Receipt(transactionId, method, amountCents))
      case PaymentMethod.DebitCard(number) if number.isBlank =>
        Left(PaymentError("Debit card number must not be blank"))
      case PaymentMethod.DebitCard(_) =>
        Right(Receipt(transactionId, method, amountCents))
      case PaymentMethod.Crypto(walletAddress) if walletAddress.isBlank =>
        Left(PaymentError("Wallet address must not be blank"))
      case PaymentMethod.Crypto(_) =>
        Right(Receipt(transactionId, method, amountCents))
```

### Step 4 — Replace Null Checks with Option

The Python code returns `None` at each step, and you must remember to check it every time; forget one and the next attribute access raises `AttributeError` in production. Scala's `Option` moves "might be absent" into the type, and a `for`-comprehension (or `flatMap`) short-circuits on the first `None`, so it is impossible to accidentally read a value that is not there.

```python
# Python - manual None checks at each hop; one forgotten check is a runtime crash
def find_user_email(user_id: int) -> str | None:
    user = db.get(user_id)
    if user is None:
        return None
    profile = user.get("profile")
    if profile is None:
        return None
    return profile.get("email")
```

```scala
// Scala - absence is in the type; the for-comprehension short-circuits on the first None
final case class Profile(email: Option[String])
final case class Account(id: Int, profile: Option[Profile])

trait AccountRepository:
  def get(id: Int): Option[Account]

def findUserEmail(repo: AccountRepository, id: Int): Option[String] =
  for
    account <- repo.get(id)
    profile <- account.profile
    email   <- profile.email
  yield email

// Equivalent implementation using flatMap directly — identical behavior, same guarantees
def findUserEmailFlat(repo: AccountRepository, id: Int): Option[String] =
  repo.get(id).flatMap(_.profile).flatMap(_.email)
```

### Step 5 — Replace Loops with Collection Methods

The Python loop interleaves three concerns — the filter, the transform, and the bookkeeping of appending to a result list — so you must read the whole body to recover the intent. Scala's `filter`/`map` name each step, compose left to right, and return a fresh list, so the source collection is never mutated and the pipeline reads as a description of *what*, not *how*.

```python
# Python - the loop mixes filtering, transforming, and list-building
result = []
for item in items:
    if item.active:
        result.append(item.value * 2)
```

```scala
// Scala - each step is named and composable; nothing is mutated
final case class Item(value: Int, active: Boolean)

val items: List[Item] = List(
  Item(value = 10, active = true),
  Item(value = 20, active = false),
  Item(value = 30, active = true)
)

val result: List[Int] =
  items
    .filter(_.active)
    .map(_.value * 2)
// result == List(20, 60)
```

### Step 6 — Separate Pure Transformations from Side Effects

Putting `print` inside the building loop couples *what* you compute with *how* you observe it: you cannot reuse the transformation without also triggering the I/O, and you cannot test the data pipeline without capturing stdout. Keep the pure transformation separate from the logging so each part can be tested and reused on its own.

```python
# Python - the transformation and the logging are entangled in one loop
items = []
for x in range(10):
    items.append(x * 2)
    print(f"Added {x * 2}")
```

```scala
// Scala - compute first, then observe; the pipeline is reusable and testable on its own
val doubled: List[Int] = (0 until 10).map(_ * 2).toList
doubled.foreach(value => println(s"Value: $value"))

// When you must observe mid-pipeline (e.g. debugging), `tapEach` runs a side effect per element
// without changing the values flowing through:
val doubledLogged: List[Int] =
  (0 until 10)
    .map(_ * 2)
    .tapEach(value => println(s"Value: $value"))
    .toList
```

### Step 7 — Use Named Parameters and Smart Constructors

A call like `create_user("Alice", "alice@example.com", True)` is unreadable at the call site — what does the bare `True` mean, and what stops you from swapping two same-typed arguments? Named arguments document intent and prevent positional mistakes. Pairing them with a smart constructor lets you validate inputs once, at the point of construction, and return the failure explicitly instead of building an invalid object.

```python
# Python - positional booleans are opaque at the call site
def create_user(
    name: str,
    email: str,
    admin: bool = False,
    active: bool = True,
) -> dict[str, object]:
    return {"name": name, "email": email, "admin": admin, "active": active}

user = create_user("Alice", "alice@example.com", admin=True)
```

```scala
// Scala - a case class with defaults, plus a validating smart constructor.
// Named arguments at the call site make each value self-documenting.
final case class User(
  name: String,
  email: String,
  admin: Boolean = false,
  active: Boolean = true
)

object User:
  def validated(
    name: String,
    email: String,
    admin: Boolean = false,
    active: Boolean = true
  ): Either[String, User] =
    if name.isBlank then Left("name must not be blank")
    else if !email.contains("@") then Left(s"invalid email: $email")
    else Right(User(name.trim, email.trim, admin, active))

val maybeUser: Either[String, User] =
  User.validated(name = "Alice", email = "alice@example.com", admin = true)
// maybeUser == Right(User("Alice", "alice@example.com", admin = true, active = true))
```

### Step 8 — Apply Scala Naming Conventions

Following the community conventions matters less for any single name than for consistency: code that mixes Python's `snake_case` with Scala's `camelCase` forces every reader to context-switch. Match the host language so your code looks like the rest of the ecosystem.

| Python | Scala | Notes |
|--------|-------|-------|
| `snake_case` (variables, functions) | `camelCase` | Methods and `val`/`var` names |
| `SCREAMING_SNAKE` (constants) | `UpperCamelCase` | e.g. `MaxRetryCount` |
| `PascalCase` (classes) | `PascalCase` | Classes, traits, `enum`s, objects |
| `_private` | `private` keyword | Visibility is a modifier, not a name prefix |
| `__very_private` | `private[this]` | Restricts access to the current instance only |

```python
# Python
MAX_RETRY_COUNT = 3

def calculate_total_price(items: list[Item]) -> float:
    return sum(item.price for item in items)

class ShoppingCart:
    def __init__(self) -> None:
        self._items: list[Item] = []
```

```scala
// Scala - constants in UpperCamelCase, methods in camelCase, types in PascalCase.
// Note the cart is immutable: `add` returns a new cart rather than mutating a private var,
// which keeps it consistent with the "immutability first" principle above.
final case class CartItem(name: String, price: BigDecimal)

val MaxRetryCount: Int = 3

def calculateTotalPrice(items: List[CartItem]): BigDecimal =
  items.map(_.price).sum

final case class ShoppingCart(items: List[CartItem] = Nil):
  def add(item: CartItem): ShoppingCart = copy(items = item :: items)
  def total: BigDecimal = calculateTotalPrice(items)
```

### Step 9 — Replace Unit Returns with Explicit Results

A function that returns nothing (`None` in Python, `Unit` in Scala) forces the caller to *guess* whether it succeeded — and the easy guess is "it worked." Returning `Either[Error, A]` (or `Try[A]` when integrating with code that throws) makes success and failure part of the type, so the caller has to acknowledge the failure path before the code compiles. That is the difference between a swallowed error and a handled one.

```python
# Python - returns None implicitly; the caller cannot tell whether the save succeeded
def save_user(user: User) -> None:
    db.save(user)
    # no return value means failures can only surface as exceptions the caller may not expect
```

```scala
import scala.util.Try

// Scala - return the outcome explicitly so callers must handle both branches
final case class UserId(value: Long)
final case class SaveError(message: String)

trait UserDb:
  def save(user: User): Either[SaveError, UserId]

// Enrich the error with context, but keep the explicit Either so failure can't be ignored
def saveUser(db: UserDb, user: User): Either[SaveError, UserId] =
  db.save(user).left.map(err => SaveError(s"failed to save ${user.email}: ${err.message}"))

// When wrapping a legacy/Java API that signals failure by throwing, capture it in a Try
// instead of letting the exception escape unannounced:
trait LegacyDb:
  def persist(user: User): UserId // may throw on connection or constraint errors

def saveUserTry(legacyDb: LegacyDb, user: User): Try[UserId] =
  Try(legacyDb.persist(user)) // any thrown exception becomes a Failure the caller can inspect
```

### Step 10 — Use Companion Object `apply` for Factory Methods

Python uses `@classmethod` for alternative constructors. In Scala the idiom is an `apply` method on the companion object: it lets callers write `Parser(config)` without `new`, and — more usefully — gives you one place to apply defaults or validation so callers cannot build an object in an invalid state.

```python
# Python - a classmethod provides a "default" constructor
class Parser:
    def __init__(self, config: Config) -> None:
        self.config = config

    @classmethod
    def default(cls) -> "Parser":
        return cls(Config())
```

```scala
// Scala - companion object with overloaded apply; the primary constructor stays private
// so the only way to build a Parser is through the factory methods.
final case class Config(timeoutMs: Int = 5000, retries: Int = 3)

final class Parser private (val config: Config):
  def parse(input: String): Either[String, List[String]] =
    if input.isEmpty then Left("input must not be empty")
    else Right(input.split(",").map(_.trim).toList)

object Parser:
  def apply(config: Config): Parser = new Parser(config)
  def apply(): Parser = new Parser(Config()) // the "default" equivalent

val defaultParser: Parser = Parser()                       // calls apply()
val customParser: Parser  = Parser(Config(timeoutMs = 10000))
```

## Examples

### Cheat Sheet: Common Transformations

Each Scala form on the right is preferred because it keeps absence/iteration in the type system rather than relying on runtime checks or manual loops.

| Python Pattern | Idiomatic Scala |
|---------------|-----------------|
| `if x is None` | `x.isEmpty` or pattern match |
| `if x is not None` | `x.isDefined` or `x.nonEmpty` |
| `x if x else default` | `x.getOrElse(default)` |
| `[x for x in xs if p(x)]` | `xs.filter(p)` |
| `[f(x) for x in xs]` | `xs.map(f)` |
| `any(p(x) for x in xs)` | `xs.exists(p)` |
| `all(p(x) for x in xs)` | `xs.forall(p)` |
| `next((x for x in xs if p(x)), None)` | `xs.find(p)` |
| `dict(zip(keys, values))` | `keys.zip(values).toMap` |
| `isinstance(x, Type)` | pattern match on a sealed type (preferred) or `x.isInstanceOf[Type]` |
| `try: parse(s) except ValueError: None` | `Try(parse(s)).toOption` |
| Mutable accumulator loop | `foldLeft` / `foldRight` |
| `for i, x in enumerate(xs)` | `xs.zipWithIndex` |

### Anti-Patterns to Avoid

Every "DON'T" below is a Python habit that compiles in Scala but discards a compile-time guarantee; the paired "DO" recovers it. The snippets share these illustrative inputs:

```scala
val code: Int = 2
val numbers: List[Int] = List(1, 2, 3, 4)
```

**Anti-pattern 1 — Using `null`:**

```scala
// DON'T: use null — it defeats the type system and reintroduces NullPointerException
val badName: String = null

// DO: model absence with Option, then handle both cases explicitly
val goodName: Option[String] = None
val greeting: String = goodName match
  case Some(value) => s"Name: $value"
  case None        => "No name provided"
```

**Anti-pattern 2 — Using `Any` plus unchecked cast:**

```scala
// DON'T: use Any plus an unchecked cast — asInstanceOf throws ClassCastException at runtime
def fetchData(): Any = "dynamic" // an untyped source is itself the smell
val raw: Any = fetchData()
val unsafe: String = raw.asInstanceOf[String]

// DO: model the domain with a sealed type and pattern match exhaustively
enum ApiData:
  case UserData(name: String)
  case ErrorData(code: Int)

def fetchTypedData(): ApiData = ApiData.UserData("Alice")
val data: ApiData = fetchTypedData()
val rendered: String = data match
  case ApiData.UserData(name) => s"User: $name"
  case ApiData.ErrorData(code) => s"Error code: $code"
```

**Anti-pattern 3 — Long if-else chain keyed on one value:**

```scala
// DON'T: a long if-else chain keyed on the same value — the compiler can't check completeness
val labelBad: String =
  if code == 1 then "one"
  else if code == 2 then "two"
  else if code == 3 then "three"
  else "many"

// DO: pattern match — clearer, and the compiler reasons about the cases
val labelGood: String = code match
  case 1 => "one"
  case 2 => "two"
  case 3 => "three"
  case _ => "many"
```

**Anti-pattern 4 — Mutable accumulator in a loop:**

```scala
// DON'T: accumulate into a mutable var in a loop — easy to get the initial value or update wrong
var totalBad: Int = 0
for x <- numbers do totalBad += x

// DO: use a built-in, or foldLeft when the combine step is non-trivial — no mutable state to misuse
val totalGood: Int = numbers.sum
val totalFold: Int = numbers.foldLeft(0)(_ + _)
```

## Pitfalls

1. **Literal port produces non-idiomatic Scala.** A token-for-token translation keeps Python's runtime-checked, mutable habits and throws away the two things Scala actually buys you — a compiler that proves whole classes of bugs cannot happen, and data structures that are safe to share across threads. Always translate the *intent*, not the syntax.

2. **Premature mutation in hot paths.** Immutable collections allocate a new structure on every transformation. In a tight inner loop that allocation pressure can dominate runtime. Only introduce a local `var` or primitive `Array` when a profiler confirms the bottleneck — never on a hunch. Keep mutation local and deliberate, not spread across an API.

3. **Using `null` in Scala.** `null` defeats the type system and reintroduces `NullPointerException`. Always model absence with `Option`. The compiler cannot protect you from `null` the way it protects you from `None`.

4. **Using `Any` plus `asInstanceOf`.** An untyped source is itself the smell. `asInstanceOf` throws `ClassCastException` at runtime. Model the domain with a sealed type and pattern match exhaustively instead.

5. **Forgetting to handle all sealed cases.** If you add a new case to a sealed `enum` and do not update every `match`, the compiler will warn (or error, depending on settings). This is a feature, not a bug — it prevents unhandled-variant bugs at runtime.

6. **Mixing `snake_case` and `camelCase`.** Code that mixes Python's `snake_case` with Scala's `camelCase` forces every reader to context-switch. Match the host language: `camelCase` for methods and `val`s, `UpperCamelCase` for constants, `PascalCase` for types.

7. **Returning `Unit` from operations that can fail.** A function that returns nothing forces the caller to guess whether it succeeded. Return `Either[Error, A]` or `Try[A]` so success and failure are part of the type and the caller must acknowledge the failure path.

8. **Entangling computation with side effects.** Putting `print` (or any I/O) inside a transformation loop couples *what* you compute with *how* you observe it. Keep the pure transformation separate from the logging so each part can be tested and reused on its own.

9. **Using deprecated library versions.** Scala 2.13 for new code, Java 8/11 as JVM target, Akka 2.6 and earlier, and Play 2.8 and earlier are all on declining maintenance paths. Prefer Scala 3.x, Java 17 LTS+, Akka 2.7+/Pekko, and Play 3.x.

## Verification

After translation, verify each of the following:

- [ ] No `null` literals appear in the translated code; absence is modeled with `Option`.
- [ ] `var` is used only where a measurement justifies it; everything else is `val`.
- [ ] if-else chains keyed on a single value are rewritten as `match` expressions.
- [ ] `Option`, `Either`, or `Try` is used at boundaries instead of `null`, sentinel returns, or letting exceptions escape unannounced.
- [ ] Public methods declare explicit return types, and no production path relies on `Any` or `asInstanceOf`.
- [ ] Inputs are validated at construction (smart constructors / boundary checks) so invalid objects cannot be built.
- [ ] Naming follows `camelCase` for methods and `val`s, `UpperCamelCase` for constants, and `PascalCase` for types.
- [ ] The code targets Scala 3.x on Java 17+ and avoids the deprecated libraries listed above.

### Quick Compile Check

If you have `scala-cli` available, you can smoke-test a translated snippet:

```powershell
# Windows PowerShell — save the snippet to a file and compile-check it
scala-cli compile .\MyTranslatedCode.scala
```

```bash
# Linux/macOS
scala-cli compile ./MyTranslatedCode.scala
```

A successful compile with no warnings about non-exhaustive matches or `Any` usage is the baseline. If the compiler warns about an unhandled case, add it — do not suppress the warning.

## Related skills

- `scala-functional-programming`
- `scala-type-system`
- `python-to-scala-migration`
