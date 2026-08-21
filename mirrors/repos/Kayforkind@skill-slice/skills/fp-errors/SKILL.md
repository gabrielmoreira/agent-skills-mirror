---
name: fp-errors
description: "Encodes TypeScript failures as fp-ts Either and TaskEither values: tryCatch at throw boundaries, chain and chainW pipelines, applicative field validation, and async orElse fallbacks. Use when callers need failure in the type, multi-field validation, or structured API error codes. Not a migration playbook for imperative modules (that is fp-refactor). Do not use for Rust Result, Python exceptions, or Zod-only schemas without fp-ts."
version: 1.0.1
source: community
risk: unknown
tags:
  - fp-ts
  - error-handling
  - either
  - task-either
  - typescript
  - validation
  - practical
---

# Practical Error Handling with fp-ts

Stop throwing everywhere. Treat errors as values that TypeScript can track through `Either` and `TaskEither`. This skill gives you pragmatic, copy-pasteable patterns for real application code — no academic jargon.

Core idea: **Errors are just data.** Return them instead of throwing them into the void.

## When to Use

- You need to replace exception-heavy code with `Either` or `TaskEither`.
- The task involves validation, domain errors, or clearer error contracts in TypeScript.
- You want pragmatic fp-ts error-handling guidance for real application code.
- You are chaining multiple fallible operations and want clean pipelines instead of nested try/catch.
- You need to collect multiple validation errors (e.g., form fields) rather than failing on the first.

## Prerequisites

- TypeScript project with `fp-ts` installed.
- Install if missing (PowerShell, Windows host):

```powershell
npm install fp-ts
```

- Imports used throughout this skill:

```typescript
import * as E from 'fp-ts/Either'
import * as TE from 'fp-ts/TaskEither'
import * as O from 'fp-ts/Option'
import * as T from 'fp-ts/Task'
import * as A from 'fp-ts/Array'
import * as NEA from 'fp-ts/NonEmptyArray'
import { sequenceS } from 'fp-ts/Apply'
import { pipe } from 'fp-ts/function'
```

## Procedure

### 1. Return Errors as Values with Either

`Either<E, A>` holds either an error (`Left`) or a value (`Right`). TypeScript now sees failure in the type signature.

```typescript
// Before: exceptions are invisible in types
function getUser(id: string): User {
  if (!id) throw new Error('ID required')
  const user = db.find(id)
  if (!user) throw new Error('User not found')
  return user
}

// After: TypeScript KNOWS this can fail
function getUser(id: string): E.Either<string, User> {
  if (!id) return E.left('ID required')
  const user = db.find(id)
  if (!user) return E.left('User not found')
  return E.right(user)
}
```

Creating and inspecting values:

```typescript
const success = E.right(42)    // Right(42)
const failure = E.left('Oops') // Left('Oops')

// Pattern match with fold
const message = pipe(
  result,
  E.fold(
    (error) => `Failed: ${error}`,
    (value) => `Got: ${value}`
  )
)
```

### 2. Convert Throwing Code to Either

Wrap any throwing function with `tryCatch`:

```typescript
const parseJSON = (json: string): E.Either<Error, unknown> =>
  E.tryCatch(
    () => JSON.parse(json),
    (e) => (e instanceof Error ? e : new Error(String(e)))
  )

parseJSON('{"valid": true}') // Right({ valid: true })
parseJSON('not json')         // Left(SyntaxError: ...)

// For reusable functions, use tryCatchK
const safeParseJSON = E.tryCatchK(
  JSON.parse,
  (e) => (e instanceof Error ? e : new Error(String(e)))
)
```

### 3. Use Common Either Operations

```typescript
// Transform the success value
const doubled = pipe(E.right(21), E.map(n => n * 2)) // Right(42)

// Transform the error
const betterError = pipe(E.left('bad'), E.mapLeft(e => `Error: ${e}`)) // Left('Error: bad')

// Provide a default for errors
const value = pipe(E.left('failed'), E.getOrElse(() => 0)) // 0

// Convert nullable to Either
const fromNullable = E.fromNullable('not found')
fromNullable(user) // Right(user) if exists, Left('not found') if null/undefined
```

### 4. Chain Fallible Operations

Each step can fail; the first error stops the chain. Replace nested try/catch with a pipeline.

```typescript
const getUser = (id: string): E.Either<string, User> => { /* ... */ }
const getProduct = (id: string): E.Either<string, Product> => { /* ... */ }
const createOrder = (user: User, product: Product): E.Either<string, Order> => { /* ... */ }

// Using chain + filterOrElse
const processUserOrder = (userId: string, productId: string): E.Either<string, Order> =>
  pipe(
    getUser(userId),
    E.filterOrElse(user => user.isActive, () => 'User not active'),
    E.chain(user =>
      pipe(
        getProduct(productId),
        E.filterOrElse(product => product.stock >= 1, () => 'Out of stock'),
        E.chain(product => createOrder(user, product))
      )
    )
  )

// Using Do notation for cleaner intermediate access
const processUserOrderDo = (userId: string, productId: string): E.Either<string, Order> =>
  pipe(
    E.Do,
    E.bind('user', () => getUser(userId)),
    E.filterOrElse(({ user }) => user.isActive, () => 'User not active'),
    E.bind('product', () => getProduct(productId)),
    E.filterOrElse(({ product }) => product.stock >= 1, () => 'Out of stock'),
    E.chain(({ user, product }) => createOrder(user, product))
  )
```

Different error types? Use `chainW` to widen:

```typescript
type ValidationError = { type: 'validation'; message: string }
type DbError = { type: 'db'; message: string }

const validateInput = (id: string): E.Either<ValidationError, string> => { /* ... */ }
const fetchFromDb = (id: string): E.Either<DbError, User> => { /* ... */ }

const process = (id: string): E.Either<ValidationError | DbError, User> =>
  pipe(
    validateInput(id),
    E.chainW(validId => fetchFromDb(validId))
  )
```

### 5. Collect Multiple Errors with Validation Applicative

For forms and batch validation, accumulate all errors instead of stopping at the first.

```typescript
type Errors = NEA.NonEmptyArray<string>

const validation = E.getApplicativeValidation(NEA.getSemigroup<string>())

const validateEmail = (email: string): E.Either<Errors, string> =>
  !email ? E.left(NEA.of('Email required'))
  : !email.includes('@') ? E.left(NEA.of('Invalid email'))
  : E.right(email)

const validatePassword = (password: string): E.Either<Errors, string> =>
  !password ? E.left(NEA.of('Password required'))
  : password.length < 8 ? E.left(NEA.of('Password too short'))
  : E.right(password)

const validateAge = (age: number | undefined): E.Either<Errors, number> =>
  age === undefined ? E.left(NEA.of('Age required'))
  : age < 18 ? E.left(NEA.of('Must be 18+'))
  : E.right(age)

const validateForm = (form: FormData) =>
  sequenceS(validation)({
    email: validateEmail(form.email),
    password: validatePassword(form.password),
    age: validateAge(form.age)
  })

validateForm({ email: '', password: '123', age: 15 })
// Left(['Email required', 'Password too short', 'Must be 18+'])

validateForm({ email: 'a@b.com', password: 'longpassword', age: 25 })
// Right({ email: 'a@b.com', password: 'longpassword', age: 25 })
```

Field-level errors for UI display:

```typescript
interface FieldError { field: string; message: string }
type FormErrors = NEA.NonEmptyArray<FieldError>

const fieldError = (field: string, message: string): FormErrors =>
  NEA.of({ field, message })

const formValidation = E.getApplicativeValidation(NEA.getSemigroup<FieldError>())

const validateEmailField = (email: string): E.Either<FormErrors, string> =>
  !email ? E.left(fieldError('email', 'Required'))
  : !email.includes('@') ? E.left(fieldError('email', 'Invalid format'))
  : E.right(email)

const getFieldError = (errors: FormErrors, field: string): string | undefined =>
  errors.find(e => e.field === field)?.message
```

### 6. Handle Async with TaskEither

`TaskEither<E, A>` is a lazy function returning `Promise<Either<E, A>>`. Nothing runs until you execute it.

```typescript
const fetchUser = (id: string): TE.TaskEither<Error, User> =>
  TE.tryCatch(
    () => fetch(`/api/users/${id}`).then(r => r.json()),
    (e) => (e instanceof Error ? e : new Error(String(e)))
  )

const getUserPosts = (userId: string): TE.TaskEither<Error, Post[]> =>
  pipe(fetchUser(userId), TE.chain(user => fetchPosts(user.id)))

// Execute when ready
const result = await getUserPosts('123')() // Returns Either<Error, Post[]>
```

Parallel fetch with `sequenceS`:

```typescript
const loadDashboard = (userId: string) =>
  pipe(
    fetchUser(userId),
    TE.chain(user =>
      pipe(
        sequenceS(TE.ApplyPar)({
          posts: fetchPosts(user.id),
          notifications: fetchNotifications(user.id),
          settings: fetchSettings(user.id)
        }),
        TE.map(data => ({ user, ...data }))
      )
    )
  )
```

Retry with exponential backoff:

```typescript
const retry = <E, A>(
  task: TE.TaskEither<E, A>,
  attempts: number,
  delayMs: number
): TE.TaskEither<E, A> =>
  pipe(
    task,
    TE.orElse((error) =>
      attempts > 1
        ? pipe(
            T.delay(delayMs)(T.of(undefined)),
            T.chain(() => retry(task, attempts - 1, delayMs * 2))
          )
        : TE.left(error)
    )
  )

const fetchWithRetry = retry(fetchUser('123'), 3, 1000)
```

Fallback chain:

```typescript
const getUserData = (id: string) =>
  pipe(
    fetchFromCache(id),
    TE.orElse(() => fetchFromApi(id)),
    TE.orElse(() => TE.right(defaultUser))
  )
```

### 7. Convert Between Patterns

From nullable to Either:

```typescript
const user = users.find(u => u.id === id) // User | undefined
const result = E.fromNullable('User not found')(user)

// From Option
const maybeUser: O.Option<User> = O.fromNullable(user)
const eitherUser = pipe(maybeUser, E.fromOption(() => 'User not found'))
```

From throwing function (e.g., Zod) to Either:

```typescript
const safeParse = <T>(schema: ZodSchema<T>) => (data: unknown): E.Either<ZodError, T> =>
  E.tryCatch(
    () => schema.parse(data),
    (e) => e as ZodError
  )
```

From Promise to TaskEither:

```typescript
const fetchJson = <T>(url: string): TE.TaskEither<Error, T> =>
  TE.tryCatch(
    () => fetch(url).then(r => r.json()),
    (e) => new Error(`Fetch failed: ${e}`)
  )

const getUserFromDb = (id: string): TE.TaskEither<DbError, User> =>
  TE.tryCatch(
    () => prisma.user.findUniqueOrThrow({ where: { id } }),
    (e) => ({ code: 'DB_ERROR', cause: e })
  )
```

Back to Promise (escape hatch for legacy APIs):

```typescript
// Option 1: Get the Either (preserves both cases)
const either: E.Either<Error, User> = await myTaskEither()

// Option 2: Throw on error (for legacy code)
const toThrowingPromise = <E, A>(te: TE.TaskEither<E, A>): Promise<A> =>
  te().then(E.fold(
    (error) => Promise.reject(error),
    (value) => Promise.resolve(value)
  ))

// Option 3: Default on error
const user = await pipe(
  fetchUser('123'),
  TE.getOrElse(() => T.of(defaultUser))
)()
```

### 8. Real Scenarios

Parse user input safely with Do notation:

```typescript
interface ParsedInput { id: number; name: string; tags: string[] }

const parseInput = (raw: unknown): E.Either<string, ParsedInput> =>
  pipe(
    E.Do,
    E.bind('obj', () =>
      typeof raw === 'object' && raw !== null
        ? E.right(raw as Record<string, unknown>)
        : E.left('Input must be an object')
    ),
    E.bind('id', ({ obj }) =>
      typeof obj.id === 'number' ? E.right(obj.id) : E.left('id must be a number')
    ),
    E.bind('name', ({ obj }) =>
      typeof obj.name === 'string' && obj.name.length > 0
        ? E.right(obj.name)
        : E.left('name must be a non-empty string')
    ),
    E.bind('tags', ({ obj }) =>
      Array.isArray(obj.tags) && obj.tags.every(t => typeof t === 'string')
        ? E.right(obj.tags as string[])
        : E.left('tags must be an array of strings')
    ),
    E.map(({ id, name, tags }) => ({ id, name, tags }))
  )
```

API call with structured error codes:

```typescript
interface ApiError { code: string; message: string; status?: number }

const createApiError = (message: string, code = 'UNKNOWN', status?: number): ApiError =>
  ({ code, message, status })

const fetchWithErrorHandling = <T>(url: string): TE.TaskEither<ApiError, T> =>
  pipe(
    TE.tryCatch(
      () => fetch(url),
      () => createApiError('Network error', 'NETWORK')
    ),
    TE.chain(response =>
      response.ok
        ? TE.tryCatch(
            () => response.json() as Promise<T>,
            () => createApiError('Invalid JSON', 'PARSE')
          )
        : TE.left(createApiError(
            `HTTP ${response.status}`,
            response.status === 404 ? 'NOT_FOUND' : 'HTTP_ERROR',
            response.status
          ))
    )
  )

const handleUserFetch = (userId: string) =>
  pipe(
    fetchWithErrorHandling<User>(`/api/users/${userId}`),
    TE.fold(
      (error) => {
        switch (error.code) {
          case 'NOT_FOUND': return T.of(showNotFoundPage())
          case 'NETWORK':  return T.of(showOfflineMessage())
          default:         return T.of(showGenericError(error.message))
        }
      },
      (user) => T.of(showUserProfile(user))
    )
  )
```

Process a list collecting successes and failures separately:

```typescript
interface ProcessResult<T> {
  successes: T[]
  failures: Array<{ item: unknown; error: string }>
}

const processAllCollectErrors = <T, R>(
  items: T[],
  process: (item: T) => E.Either<string, R>
): ProcessResult<R> => {
  const results = items.map((item, index) =>
    pipe(process(item), E.mapLeft(error => ({ item, error, index })))
  )
  return {
    successes: pipe(results, A.filterMap(E.toOption)),
    failures: pipe(
      results,
      A.filterMap(r => E.isLeft(r) ? O.some(r.left) : O.none)
    )
  }
}

parseNumbers(['1', 'abc', '3', 'def'])
// { successes: [1, 3], failures: [{ item: 'abc', error: '...', index: 1 }, ...] }
```

Bulk async with partial success report:

```typescript
interface BulkResult<T> {
  succeeded: T[]
  failed: Array<{ id: string; error: string }>
}

const bulkProcess = <T>(
  ids: string[],
  process: (id: string) => TE.TaskEither<string, T>
): T.Task<BulkResult<T>> =>
  pipe(
    ids,
    A.map(id =>
      pipe(
        process(id),
        TE.fold(
          (error) => T.of({ type: 'failed' as const, id, error }),
          (result) => T.of({ type: 'succeeded' as const, result })
        )
      )
    ),
    T.sequenceArray,
    T.map(results => ({
      succeeded: results
        .filter((r): r is { type: 'succeeded'; result: T } => r.type === 'succeeded')
        .map(r => r.result),
      failed: results
        .filter((r): r is { type: 'failed'; id: string; error: string } => r.type === 'failed')
        .map(({ id, error }) => ({ id, error }))
    }))
  )
```

## Quick Reference

| Pattern | Use When | Example |
|---------|----------|---------|
| `E.right(value)` | Creating a success | `E.right(42)` |
| `E.left(error)` | Creating a failure | `E.left('not found')` |
| `E.tryCatch(fn, onError)` | Wrapping throwing code | `E.tryCatch(() => JSON.parse(s), toError)` |
| `E.fromNullable(error)` | Converting nullable | `E.fromNullable('missing')(maybeValue)` |
| `E.map(fn)` | Transform success | `pipe(result, E.map(x => x * 2))` |
| `E.mapLeft(fn)` | Transform error | `pipe(result, E.mapLeft(addContext))` |
| `E.chain(fn)` | Chain operations | `pipe(getA(), E.chain(a => getB(a.id)))` |
| `E.chainW(fn)` | Chain with different error type | `pipe(validate(), E.chainW(save))` |
| `E.fold(onError, onSuccess)` | Handle both cases | `E.fold(showError, showData)` |
| `E.getOrElse(onError)` | Extract with default | `E.getOrElse(() => 0)` |
| `E.filterOrElse(pred, onFalse)` | Validate with error | `E.filterOrElse(x => x > 0, () => 'must be positive')` |
| `sequenceS(validation)({...})` | Collect all errors | Form validation |

TaskEither equivalents: `TE.right`, `TE.left`, `TE.tryCatch`, `TE.map`, `TE.mapLeft`, `TE.chain`, `TE.chainW`, `TE.fold`, `TE.getOrElse`, `TE.filterOrElse`, `TE.orElse`.

## Pitfalls

- **Don't throw inside Either/TaskEither pipelines.** Throwing breaks the typed contract you are trying to enforce. Use `E.tryCatch`/`TE.tryCatch` at boundaries to wrap throwing code.
- **`chain` stops at the first error.** If you need all errors (e.g., forms), use the validation applicative with `sequenceS` and `NEA.getSemigroup`, not `chain`.
- **`chain` requires identical error types.** Use `chainW` when chaining functions with different error types so TypeScript can union them.
- **TaskEither is lazy.** Nothing executes until you call the resulting function with `()`. Forgetting to invoke is a common silent bug.
- **`E.fromNullable` is curried.** Call as `E.fromNullable('error')(value)`, not `E.fromNullable('error', value)`.
- **`fold` requires both branches.** Forgetting the error branch is a compile error — that is the point, but expect friction when refactoring legacy code.
- **Don't mix `Apply` sequenceS with `chain` for validation.** `sequenceS` runs all validations and accumulates; `chain` short-circuits. Choose deliberately.
- **`TE.orElse` expects a function returning TaskEither.** Passing a raw value instead of `TE.right(value)` will fail type checking.
- **Do not treat this skill as a substitute for environment-specific validation, testing, or expert review.** Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

## Verification

1. Confirm `fp-ts` is installed:

```powershell
npm ls fp-ts
```

Expected: a version line such as `fp-ts@2.x.x` and no `UNMET DEPENDENCY`.

2. Type-check a file using these patterns:

```powershell
npx tsc --noEmit
```

Expected: zero errors. If `chainW` errors appear, verify error types are being widened correctly.

3. Quick runtime smoke test for Either:

```typescript
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'

const result = pipe(
  E.right(21),
  E.map(n => n * 2),
  E.fold(
    (e) => `Failed: ${e}`,
    (v) => `Got: ${v}`
  )
)
console.log(result) // Got: 42
```

Expected output: `Got: 42`.

4. Quick runtime smoke test for TaskEither:

```typescript
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'

const run = pipe(
  TE.right(10),
  TE.map(n => n + 1),
  TE.getOrElse(() => TE.right(0))
)
run().then(console.log) // Right(11)
```

Expected output: `{ _tag: 'Right', right: 11 }`.

5. Verify validation accumulation returns all errors:

```typescript
// Reuse validateForm from Procedure step 5
console.log(validateForm({ email: '', password: '123', age: 15 }))
```

Expected: `Left` containing a `NonEmptyArray` with three error strings.

## Related Skills

- Skills covering `fp-ts` `Option` for nullable values without error semantics.
- Skills covering `io-ts` or `zod` runtime validation integrated with `Either`.
