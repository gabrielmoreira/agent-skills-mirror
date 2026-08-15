---
name: fp-refactor
version: 1.1.1
description: "Migrates existing imperative TypeScript—hidden throws, nullable returns, and Node err-first callbacks—onto fp-ts Option, Either, and TaskEither so callers must handle absence and failure. Use when throws, nulls, or callbacks hide failure from the compiler and a staged conversion is justified. Not for greenfield Either snippets or profiler-hot inner loops. Never convert stable readable code solely for style, or introduce fp-ts where the team cannot maintain it."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Refactoring Imperative Code to fp-ts

This skill provides patterns and strategies for migrating existing imperative TypeScript code to fp-ts functional patterns.

The core idea: imperative code expresses failure, absence, and asynchrony *implicitly* — exceptions are thrown but not visible in a signature, `null` can appear anywhere, and callbacks bury the error channel in an argument. fp-ts moves those concerns *into the type system*. `Either<E, A>` says "this can fail with `E`", `Option<A>` says "this value may be absent", and `TaskEither<E, A>` says "this async computation can fail with `E`". Once a concern is in the type, the compiler — not a code reviewer or a production incident — forces every caller to deal with it.

## When to Use

Reach for these patterns when the *implicitness* described above is actively causing pain:

- **You are migrating an imperative TypeScript codebase toward fp-ts.** A consistent functional style across modules is what makes the patterns compose; one-off usage rarely pays for the learning curve.
- **Failure or absence is being passed around invisibly.** If functions throw, return `null`/`undefined`, or take Node-style `(err, data)` callbacks, callers have no compile-time reminder to handle the bad path. Encoding it as `Either`, `Option`, or `TaskEither` turns those silent omissions into type errors.
- **You need composition, not just one example.** When several fallible steps must be chained (parse, then validate, then fetch, then write), `pipe` with `flatMap` keeps the happy path linear and short-circuits on the first failure — replacing nested `try/catch` and `if (x === null) return` ladders.
- **You want migration guidance and tradeoffs**, not isolated snippets. The value here is knowing *when* the conversion clarifies intent versus when it only adds ceremony.

### When Not to Use

Functional abstractions are not free, so skip them when the cost outweighs the clarity they buy:

- **Performance-critical hot paths.** Every `pipe`, `map`, and `flatMap` allocates closures and intermediate wrappers. In a tight loop or a latency-sensitive inner function, that overhead can matter; measure before converting, and prefer plain code where the profiler points.
- **Error types that carry no meaning.** If the only sensible response to a failure is "log and crash", a single `try/catch` at the boundary communicates that just as well as `Either`, without asking every reader to learn the abstraction.
- **Teams unfamiliar with functional programming.** fp-ts has a steep vocabulary (`Functor`, `Monad`, `Kleisli`). Introducing it where the team cannot maintain it trades a runtime risk for a comprehension risk, which is usually a worse deal. Invest in shared understanding first.
- **Code that is already simple, readable, and stable.** Refactoring well-understood imperative code purely for stylistic consistency adds churn and review burden with no behavioural gain. Let the benefit (a clearer signature, a bug class the compiler can now catch) justify the change.

## Prerequisites

- **fp-ts fundamentals.** Comfort with `pipe`, `map`, `flatMap`/`chain`, `getOrElse`, and the difference between `Option`, `Either`, `Task`, and `TaskEither`. Without this, the converted code reads as noise rather than intent.
- **TypeScript's type system.** Discriminated unions (the `_tag` pattern), generics, and `readonly` modifiers are what give the converted code its compile-time guarantees; weak typing here undermines the whole point.
- **Refactoring discipline.** Knowing how to convert incrementally and verify behaviour is preserved at each step, so a migration does not silently change semantics while changing style.

## Procedure

### Step 1: Find the implicit failure points

Scan for `throw`, `try/catch`, `null`/`undefined` returns, and callback signatures. These are where types are currently lying about what a function can do, and therefore where encoding the failure pays off most.

### Step 2: Pick the smallest type that fits

Use `Option` for "may be absent" (no error detail needed), `Either` for synchronous "may fail with a reason", and `TaskEither` for asynchronous "may fail with a reason". Choosing the narrowest type keeps signatures honest and avoids dragging a `Task` through purely synchronous code.

### Step 3: Model errors as discriminated unions, not bare `Error`

A type such as `{ readonly _tag: 'JsonParseError'; readonly input: string; readonly cause: string }` lets callers `switch` on `_tag` and handle each case exhaustively; a bare `Error` forces brittle string-matching on `.message`. This is what makes the typed error channel actually useful downstream.

### Step 4: Compose with `pipe`, validate at the edges

Keep the happy path linear inside `pipe`, and put strict parameter validation (`fromPredicate`) at the entry of each function so bad input becomes a typed failure instead of a thrown exception deeper in the stack.

### Step 5: Test both branches

A converted function now has a success *and* a failure value; assert on both, since the compiler guarantees the shape but not that you produce the right error in the right situation.

### Step 6: Record the reasoning, not just the diff

Note *why* a given function was converted (which bug class it now prevents) so future maintainers can tell deliberate functional code from cargo-culted ceremony.

### Example: Converting try-catch to Either/TaskEither

A function typed `(input: string) => unknown` that throws is doubly dishonest — the return type hides the failure entirely, and inside the `catch` the error is typed `unknown`, so you can only stringify it. `Either<E, A>` puts failure in the return type, and a discriminated error type preserves enough structure for callers to react to specific failures.

```typescript
import * as E from 'fp-ts/Either';
import * as TE from 'fp-ts/TaskEither';
import { pipe } from 'fp-ts/function';

// A discriminated error type is more useful than a bare Error: callers can
// switch on `_tag` and handle each failure case instead of parsing messages.
interface JsonParseError {
  readonly _tag: 'JsonParseError';
  readonly input: string;
  readonly cause: string;
}

// Normalises the `unknown` thrown by JSON.parse into a typed error. Defensive,
// because a thrown value is not guaranteed to be an Error instance.
const toJsonParseError = (input: string) => (cause: unknown): JsonParseError => ({
  _tag: 'JsonParseError',
  input,
  cause: cause instanceof Error ? cause.message : String(cause),
});

// Before (imperative): the signature hides that this throws, and `error` is
// `unknown`, so the only safe thing to do with it is convert it to text.
function parseJsonImperative(input: string): unknown {
  try {
    return JSON.parse(input) as unknown;
  } catch (error) {
    throw new Error(
      `Invalid JSON: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

// After (fp-ts Either): failure is part of the return type, so every caller is
// forced by the compiler to handle the JsonParseError branch.
const parseJson = (input: string): E.Either<JsonParseError, unknown> =>
  E.tryCatch(
    () => JSON.parse(input) as unknown,
    toJsonParseError(input),
  );
```

For asynchronous work, the same idea uses `TaskEither<E, A>`: a *lazy* async value that, when run, resolves to either a typed error or a success. Nothing executes until the `TaskEither` is invoked, which keeps it referentially transparent and composable.

```typescript
import * as TE from 'fp-ts/TaskEither';
import { pipe } from 'fp-ts/function';

interface HttpError {
  readonly _tag: 'HttpError';
  readonly url: string;
  readonly status?: number;
  readonly cause: string;
}

const toHttpError = (url: string) => (cause: unknown): HttpError => ({
  _tag: 'HttpError',
  url,
  cause: cause instanceof Error ? cause.message : String(cause),
});

// Defensively turns a non-2xx response into a typed failure instead of letting
// a "successful" fetch with a 500 body flow downstream as if it were valid.
const ensureOk = (url: string) => (response: Response): TE.TaskEither<HttpError, Response> =>
  response.ok
    ? TE.right(response)
    : TE.left({
        _tag: 'HttpError' as const,
        url,
        status: response.status,
        cause: `Unexpected status ${response.status}`,
      });

// After (fp-ts TaskEither): network failure, bad status, and JSON-parse failure
// all collapse into one typed HttpError channel, chained linearly with pipe.
const fetchJson = (url: string): TE.TaskEither<HttpError, unknown> =>
  pipe(
    TE.tryCatch(() => fetch(url), toHttpError(url)),
    TE.flatMap(ensureOk(url)),
    TE.flatMap((response) =>
      TE.tryCatch(() => response.json() as Promise<unknown>, toHttpError(url)),
    ),
  );
```

### Example: Converting null checks to Option

A signature like `(config: Config) => string | null` pushes the same `if (x === null)` guard onto every caller, and it only takes one forgotten guard to ship a `Cannot read properties of null` bug. `Option<string>` makes "absent" a value you compose with `map`/`filter`/`getOrElse`; the compiler will not let you reach the inner string without first handling `None`.

```typescript
import * as O from 'fp-ts/Option';
import { pipe } from 'fp-ts/function';

interface DatabaseCredentials {
  readonly user: string;
  readonly password: string;
}

interface DatabaseConfig {
  readonly host: string;
  readonly port: number;
  readonly name: string;
  readonly credentials?: DatabaseCredentials;
}

interface Config {
  readonly database?: DatabaseConfig;
}

// Before (imperative): nested null/undefined checks that are easy to leave
// incomplete, and a `string | null` return type that re-burdens every caller.
function getDatabaseUrlImperative(config: Config): string | null {
  if (!config.database) {
    return null;
  }
  const { host, port, name, credentials } = config.database;
  if (host.length === 0 || port <= 0 || name.length === 0) {
    return null;
  }
  const auth = credentials ? `${credentials.user}:${credentials.password}@` : '';
  return `postgres://${auth}${host}:${port}/${name}`;
}

// Optional credentials become an empty auth segment when absent — Option makes
// the "with or without credentials" branch explicit and total.
const buildDatabaseUrl = (db: DatabaseConfig): string => {
  const auth: string = pipe(
    O.fromNullable(db.credentials),
    O.map((c: DatabaseCredentials) => `${c.user}:${c.password}@`),
    O.getOrElse(() => ''),
  );
  return `postgres://${auth}${db.host}:${db.port}/${db.name}`;
};

// After (fp-ts Option): O.fromNullable handles the missing-config case, O.filter
// enforces the same validation as the imperative guard, and the Option<string>
// return type makes "no URL available" impossible for a caller to ignore.
const getDatabaseUrl = (config: Config): O.Option<string> =>
  pipe(
    O.fromNullable(config.database),
    O.filter(
      (db: DatabaseConfig): boolean =>
        db.host.length > 0 && db.port > 0 && db.name.length > 0,
    ),
    O.map(buildDatabaseUrl),
  );
```

### Example: Converting callbacks to TaskEither

Node-style callbacks `(err: Error | null, data: string | null) => void` resist composition: you nest them to sequence work, you can forget to `return` after invoking the callback (running the rest of the function anyway), and TypeScript cannot force a caller to check `err` before using `data`. `TaskEither<E, A>` replaces the callback with a single composable value and makes the error path part of the type.

```typescript
import * as TE from 'fp-ts/TaskEither';
import { pipe } from 'fp-ts/function';
import * as fs from 'node:fs';

interface FileReadError {
  readonly _tag: 'FileReadError';
  readonly path: string;
  readonly cause: string;
}

const toFileReadError = (path: string) => (cause: unknown): FileReadError => ({
  _tag: 'FileReadError',
  path,
  cause: cause instanceof Error ? cause.message : String(cause),
});

// Before (imperative): callback nesting, manual error forwarding, and an easily
// forgotten `return` after the error branch. Nothing stops a caller ignoring err.
function readFileCallback(
  path: string,
  callback: (error: Error | null, data: string | null) => void,
): void {
  fs.readFile(path, 'utf-8', (err: NodeJS.ErrnoException | null, data: string) => {
    if (err !== null) {
      callback(err, null);
      return;
    }
    callback(null, data);
  });
}

// After (fp-ts TaskEither): TE.fromPredicate validates the argument up front and
// turns bad input into a typed failure; TE.tryCatch lifts the promise-based read
// into the same FileReadError channel, all composed with pipe.
const readFile = (path: string): TE.TaskEither<FileReadError, string> =>
  pipe(
    path,
    TE.fromPredicate(
      (candidate: string): boolean => candidate.trim().length > 0,
      (candidate: string) =>
        toFileReadError(candidate)(new Error('Path must be a non-empty string')),
    ),
    TE.flatMap((validPath: string) =>
      TE.tryCatch(
        () => fs.promises.readFile(validPath, 'utf-8'),
        toFileReadError(path),
      ),
    ),
  );
```

## Pitfalls

- **Performance on hot paths.** Every `pipe`, `map`, and `flatMap` allocates closures and intermediate wrappers. In tight loops or latency-sensitive inner functions, that overhead can matter. Measure before converting; prefer plain code where the profiler points.
- **Error types that carry no meaning.** If the only sensible response to a failure is "log and crash", a single `try/catch` at the boundary communicates that just as well as `Either`, without asking every reader to learn the abstraction.
- **Team unfamiliarity with functional programming.** fp-ts has a steep vocabulary (`Functor`, `Monad`, `Kleisli`). Introducing it where the team cannot maintain it trades a runtime risk for a comprehension risk. Invest in shared understanding first.
- **Refactoring stable, readable code for style alone.** Refactoring well-understood imperative code purely for stylistic consistency adds churn and review burden with no behavioural gain. Let the benefit (a clearer signature, a bug class the compiler can now catch) justify the change.
- **Swallowing errors with `getOrElse`/`fold`.** Confirm there are no `getOrElse`/`fold` calls that quietly swallow real errors — the compiler forces you to handle the bad branch, but it does not stop you from handling it badly.
- **Hidden `throw` escaping the typed channel.** Caught values are typed `unknown` and must be narrowed defensively; thrown values from third-party calls must be wrapped via `tryCatch` rather than escaping the typed channel.
- **Using `any` instead of `unknown`.** A thrown value is not guaranteed to be an `Error` instance. Always normalise via `cause instanceof Error ? cause.message : String(cause)` rather than casting to `any`.

## Verification

After a conversion, confirm the refactor actually bought something rather than just changing shape:

- [ ] **Failure and edge cases are handled in the type, not by convention.** Every fallible function returns `Option`/`Either`/`TaskEither`, and callers are forced by the compiler to handle the bad branch — confirm there are no `getOrElse`/`fold` calls that quietly swallow real errors.
- [ ] **Readability improved, or at least held.** The happy path should read as a linear `pipe`. If the functional version is harder to follow than the imperative original, reconsider whether this code belonged in the "When Not to Use" category.
- [ ] **Both branches are tested.** Assert on a success value *and* a representative failure value for each converted function, since the compiler guarantees the shape of the error but not that you emit the correct one.
- [ ] **No `any` and no hidden `throw`.** Caught values are typed `unknown` and narrowed defensively; thrown values from third-party calls are wrapped via `tryCatch` rather than escaping the typed channel.
- [ ] **Performance is acceptable on hot paths.** Where the converted code sits in a loop or latency-sensitive path, profile to confirm the added allocations from `pipe`/`flatMap` are not a regression.

## Related Skills

- **fp-ts fundamentals** — Comfort with `pipe`, `map`, `flatMap`/`chain`, `getOrElse`, and the difference between `Option`, `Either`, `Task`, and `TaskEither`.
- **TypeScript's type system** — Discriminated unions (the `_tag` pattern), generics, and `readonly` modifiers are what give the converted code its compile-time guarantees.
- **Refactoring discipline** — Knowing how to convert incrementally and verify behaviour is preserved at each step, so a migration does not silently change semantics while changing style.
