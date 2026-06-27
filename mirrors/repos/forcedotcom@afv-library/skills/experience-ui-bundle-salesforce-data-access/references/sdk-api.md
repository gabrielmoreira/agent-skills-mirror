# The Data SDK call API (`@salesforce/platform-sdk`)

The `query`/`mutate` namespace, typing, and error handling. For caching and the reactive
refresh modes see [caching.md](caching.md); for old→new conversion see [migration.md](migration.md).

## Import

```typescript
import { createDataSDK, gql, type CacheControl, type NodeOfConnection } from "@salesforce/platform-sdk";
```

`createDataSDK`, `gql`, `CacheControl`, and `NodeOfConnection` all come from
**`@salesforce/platform-sdk`**. The old `@salesforce/sdk-data` package name is dead — any
`@salesforce/sdk-data` string you see in the repo is a stale `dist/` build artifact, not the
canonical import.

## `sdk.graphql` is a NAMESPACE, not a callable

The previous SDK exposed `sdk.graphql` as a callable: `await sdk.graphql?.(query, vars)`.
That form is gone. `sdk.graphql` is now a namespace with two methods:

```typescript
const sdk = await createDataSDK();

// QUERY — reactive, cached on WebApp
const result = await sdk.graphql!.query<TData, TVariables>({
  query: MY_QUERY,        // gql-tagged string (the `query` key)
  variables,              // optional
  operationName,          // optional
  cacheControl,           // optional — see caching.md
});

// MUTATE — request/response, never cached
const { data, errors } = await sdk.graphql!.mutate<TData, TVariables>({
  mutation: MY_MUTATION,  // NOTE: the key is `mutation`, not `query`
  variables,
  operationName,
});
```

Type signatures (from `core/data.ts`):

```typescript
query<T, V>(options: QueryOptions<V>): Promise<QueryResult<T>>;
mutate<T, V>(options: MutateOptions<V>): Promise<MutationResult<T>>;
```

### `sdk.graphql!` vs guard

`sdk.graphql` may still be `undefined` on surfaces that do not support data operations, so it
is typed `graphql?: DataSDKGraphQL`. Real consumer code asserts it is present after
`createDataSDK()` with the non-null assertion:

```typescript
const result = await sdk.graphql!.query<...>({ query, variables });
```

This replaces the old optional-call `sdk.graphql?.(...)`. Do **not** reach for the dead
callable form. Which of `!` vs a guard you use is a **surface decision** (the spine's
[Surfaces](../SKILL.md#surfaces--sdkgraphql-vs-guard) table is the routing): `!` only if the
bundle is WebApp-exclusive; otherwise guard, because a bare `sdk.graphql!` that later ships to
another surface throws `Cannot read properties of undefined` at runtime — TypeScript won't catch
it because `!` silences exactly that check.

```typescript
// `!` form — WebApp-only bundles; every shipped WebApp consumer uses it.
const result = await sdk.graphql!.query<...>({ query, variables });

// Portable guard form — safe on every surface. Use when the bundle is not WebApp-exclusive.
if (!sdk.graphql) {
  // No data SDK on this surface — degrade gracefully (render empty, throw, or feature-flag off).
  return;
}
const result = await sdk.graphql.query<...>({ query, variables });
```

(The same `!`-vs-guard call applies to `sdk.fetch!`.)

## `QueryResult<T>` — the reactive query handle

`query()` resolves to a `QueryResult<T>`, which IS a snapshot AND carries two reactive methods:

```typescript
interface QuerySnapshot<T> { data: T | undefined; errors?: GraphQLError[]; }
type QuerySubscriber<T> = (snapshot: QuerySnapshot<T>) => void;
type Unsubscribe = () => void;

interface QueryResult<T> extends QuerySnapshot<T> {
  subscribe(cb: QuerySubscriber<T>): Unsubscribe;
  refresh(): Promise<void>;
}
```

- `result.data` / `result.errors` — the initial snapshot at await-time (cached value on cached
  surfaces, else the network response).
- `result.subscribe(cb)` — register a callback for every *subsequent* snapshot (a cache update,
  a stale-while-revalidate refill, or an explicit `refresh()`). Returns an `Unsubscribe`. Each
  `subscribe` is **independent** — unsubscribing one leaves the others live — and it does **not**
  fire on registration, only on later snapshots.
- `result.refresh()` — re-issue the request bypassing the cache, write the fresh result back, and
  push the new snapshot to **all** current subscribers. Returns `Promise<void>`.

*When* to reach for `subscribe`/`refresh` over the default cache, plus the uncached-surface
caveats, is a strategy call — see [caching.md](caching.md).

## `cacheControl` — the per-call cache policy

`cacheControl` is an optional field on the query options bag. It overrides the default cache
behavior for **one** call and does **not** change the cache key, so a `"no-cache"` call and a
default call read/write the *same* cache slot. The type:

```typescript
type CacheControlShorthand = "no-cache" | "only-if-cached";
interface CacheControlMaxAge { type: "max-age"; maxAge: number; }
type CacheControl = CacheControlShorthand | CacheControlMaxAge;
```

| `cacheControl` | Behavior |
|---|---|
| *(omitted)* | Default — return the cached entry if fresh (300s TTL), else fetch and write back. |
| `"no-cache"` | Skip the cache **read**, always hit the network. **Still writes the response back** for later default callers. |
| `"only-if-cached"` | Read from cache **only**. Hit → return; **miss → `DataNotFoundError` on `result.errors`** (no network, no throw). |
| `{ type: "max-age", maxAge: <seconds> }` | Custom TTL instead of 300s. `maxAge: 0` = written but immediately stale; invalid values silently fall back to 300s. |

An `only-if-cached` miss is not an exception — the Promise resolves and the miss surfaces on
`result.errors` as a `DataNotFoundError`. This is offline-first: a miss is **expected, not an
error**. Check `result.errors`, render an empty state, and **do not fall back to a network read**
— a fallback defeats the point of `only-if-cached`:

```typescript
const result = await sdk.graphql!.query({ query: GET_ACCOUNTS, variables, cacheControl: "only-if-cached" });
if (result.errors?.length) {
  // cold cache — render the empty state. Do NOT fall back to the network; that defeats offline-first.
  return renderEmptyState();
}
```

Which policy fits which goal (force-refresh button, offline-first, fast-changing data) is a
strategy call — see the decision matrix in [caching.md](caching.md).

## `MutationResult<T>` — one-shot, NO subscribe/refresh

```typescript
interface MutationResult<T> { data: T | undefined; errors?: GraphQLError[]; }
```

Mutations are request/response. The type deliberately has **no** `subscribe` and **no**
`refresh` — mutating on subscribe is incoherent, and re-running a mutation on refresh is
dangerous. To refresh data after a mutation, hold a query `result` and call `result.refresh()`
(see [caching.md](caching.md)).

## HTTP 200 ≠ success — always read `errors`

The Promise resolves even for GraphQL/parse errors; they surface on `result.errors`, never as a
thrown exception from `query()`/`mutate()`. Both shipped consumers gate on `errors` first:

```typescript
// accounts.ts pattern
if (result.errors?.length) {
  throw new Error(result.errors.map((e) => e.message).join("; "));
}
```

```typescript
// graphqlClient.ts (canonical scaffold) — strict wrapper
export async function executeGraphQL<TData, TVariables>(
  query: string,
  variables?: TVariables,
): Promise<TData> {
  const sdk = await createDataSDK();
  const result = await sdk.graphql!.query<TData, TVariables>({ query, variables });
  if (result.errors?.length) {
    throw new Error(`GraphQL Error: ${result.errors.map((e) => e.message).join("; ")}`);
  }
  if (result.data == null) {
    throw new Error("GraphQL response data is null");
  }
  return result.data;
}
```

Three error-handling stances (all read `result.errors`):

```typescript
// Strict — any errors = failure
if (result.errors?.length) throw new Error(result.errors.map((e) => e.message).join("; "));

// Tolerant — log, use whatever data came back (partial success)
if (result.errors?.length) console.warn("GraphQL partial errors:", result.errors);

// Discriminated — fail only when NO data returned
if (!result.data && result.errors?.length) {
  throw new Error(result.errors.map((e) => e.message).join("; "));
}
```

## Generated types on the call

After `npm run graphql:codegen`, import the generated `<Op>Query` / `<Op>QueryVariables` types
and pass them as the type parameters. The call shape changed — types now go on `.query()`, not
the old callable:

```typescript
import type { GetAccountsQuery, GetAccountsQueryVariables } from "../graphql-operations-types";

const result = await sdk.graphql!.query<GetAccountsQuery, GetAccountsQueryVariables>({
  query: GET_ACCOUNTS,
  variables,
});
```

`NodeOfConnection<T>` extracts a node type from a Connection for cleaner typing:

```typescript
import { type NodeOfConnection } from "@salesforce/platform-sdk";
type AccountNode = NodeOfConnection<GetAccountsQuery["uiapi"]["query"]["Account"]>;
```
