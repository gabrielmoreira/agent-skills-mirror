---
name: fp-react
description: "Applies fp-ts in React 18/19 and Next.js 14/15: Option state, Either form validation, TaskEither fetches, RemoteData UI, and React 19 use/useActionState/useOptimistic with functional patterns. Use when building React apps that already use or should adopt fp-ts instead of null flags. Not for Redux or Zustand without fp-ts, or category-theory lectures with no UI code."
version: 2.0.1
tags: [fp-ts, react, typescript, hooks, state-management, forms, data-fetching, remote-data, react-19, next-js]
---

## Overview
Practical patterns for React apps using fp-ts. No jargon, just code that works.

## When to Use
Use this skill when:
- Building React 18/19 or Next.js 14/15 applications with `fp-ts`.
- Handling optional values (`Option`), form validation (`Either`), or async operations (`TaskEither`).
- Managing async UI states with `RemoteData` instead of boolean flags.
- Implementing dependency injection or React 19 features (`use`, `useActionState`, `useOptimistic`) with functional programming patterns.

## Prerequisites
- React 18 or 19
- Next.js 14 or 15 (if using Next.js)
- `fp-ts` installed (`npm install fp-ts`)
- Optional: `fp-ts-react-stable-hooks` for referential stability (`npm install fp-ts-react-stable-hooks`)
- Optional: `@devexperts/remote-data-ts` for RemoteData types

## Procedure

### 1. State with Option (Maybe It's There, Maybe Not)
Use `Option` instead of `null | undefined` for clearer intent.

```typescript
import { useState } from 'react'
import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'

interface User {
  id: string
  name: string
  email: string
}

function UserProfile() {
  const [user, setUser] = useState<O.Option<User>>(O.none)

  const handleLogin = (userData: User) => setUser(O.some(userData))
  const handleLogout = () => setUser(O.none)

  return pipe(
    user,
    O.match(
      () => <button onClick={() => handleLogin({ id: '1', name: 'Alice', email: 'alice@example.com' })}>
        Log In
      </button>,
      (u) => (
        <div>
          <p>Welcome, {u.name}!</p>
          <button onClick={handleLogout}>Log Out</button>
        </div>
      )
    )
  )
}
```

To chain optional values:
```typescript
import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'

interface Profile {
  user: O.Option<{
    name: string
    settings: O.Option<{
      theme: string
    }>
  }>
}

function getTheme(profile: Profile): string {
  return pipe(
    profile.user,
    O.flatMap(u => u.settings),
    O.map(s => s.theme),
    O.getOrElse(() => 'light')
  )
}
```

### 2. Form Validation with Either
`Either` is perfect for validation: `Left` = errors, `Right` = valid data.

```typescript
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'

const validateEmail = (email: string): E.Either<string, string> =>
  email.includes('@') ? E.right(email) : E.left('Invalid email address')

const validatePassword = (password: string): E.Either<string, string> =>
  password.length >= 8 ? E.right(password) : E.left('Password must be at least 8 characters')
```

To collect all errors (not just the first one):
```typescript
import * as E from 'fp-ts/Either'
import { sequenceS } from 'fp-ts/Apply'
import { getSemigroup } from 'fp-ts/NonEmptyArray'
import { pipe } from 'fp-ts/function'

const validateAll = sequenceS(E.getApplicativeValidation(getSemigroup<string>()))

interface SignupForm { name: string; email: string; password: string }
interface ValidatedForm { name: string; email: string; password: string }

function validateForm(form: SignupForm): E.Either<string[], ValidatedForm> {
  return pipe(
    validateAll({
      name: pipe(validateName(form.name), E.mapLeft(e => [e])),
      email: pipe(validateEmail(form.email), E.mapLeft(e => [e])),
      password: pipe(validatePassword(form.password), E.mapLeft(e => [e])),
    })
  )
}
```

### 3. Data Fetching with TaskEither
`TaskEither` = async operation that might fail. Perfect for API calls.

```typescript
import { useState, useEffect } from 'react'
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'

const fetchJson = <T>(url: string): TE.TaskEither<Error, T> =>
  TE.tryCatch(
    async () => {
      const res = await fetch(url)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res.json()
    },
    (err) => err instanceof Error ? err : new Error(String(err))
  )

function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setError(null)
    pipe(
      fetchJson<T>(url),
      TE.match(
        (err) => { setError(err); setLoading(false) },
        (result) => { setData(result); setLoading(false) }
      )
    )()
  }, [url])

  return { data, error, loading }
}
```

### 4. RemoteData Pattern (The Right Way to Handle Async State)
Stop using `{ data, loading, error }` booleans. Use a proper state machine.

```typescript
type RemoteData<E, A> =
  | { _tag: 'NotAsked' }
  | { _tag: 'Loading' }
  | { _tag: 'Failure'; error: E }
  | { _tag: 'Success'; data: A }

const notAsked = <E, A>(): RemoteData<E, A> => ({ _tag: 'NotAsked' })
const loading = <E, A>(): RemoteData<E, A> => ({ _tag: 'Loading' })
const failure = <E, A>(error: E): RemoteData<E, A> => ({ _tag: 'Failure', error })
const success = <E, A>(data: A): RemoteData<E, A> => ({ _tag: 'Success', data })

function fold<E, A, R>(
  rd: RemoteData<E, A>,
  onNotAsked: () => R,
  onLoading: () => R,
  onFailure: (e: E) => R,
  onSuccess: (a: A) => R
): R {
  switch (rd._tag) {
    case 'NotAsked': return onNotAsked()
    case 'Loading': return onLoading()
    case 'Failure': return onFailure(rd.error)
    case 'Success': return onSuccess(rd.data)
  }
}
```

### 5. Referential Stability (Preventing Re-renders)
fp-ts values like `O.some(1)` create new objects each render. React sees them as "changed".

Solution 1: `useMemo`
```typescript
function GoodComponent() {
  const [rawValue, setRawValue] = useState<number | null>(1)
  const value = useMemo(() => O.fromNullable(rawValue), [rawValue])
  useEffect(() => { console.log('value changed') }, [rawValue])
}
```

Solution 2: `fp-ts-react-stable-hooks`
```bash
npm install fp-ts-react-stable-hooks
```
```typescript
import { useStableO, useStableEffect } from 'fp-ts-react-stable-hooks'
import * as O from 'fp-ts/Option'
import * as Eq from 'fp-ts/Eq'

function StableComponent() {
  const [value, setValue] = useStableO(O.some(1))
  useStableEffect(
    () => { console.log('value changed') },
    [value],
    Eq.tuple(O.getEq(Eq.eqNumber))
  )
}
```

### 6. Dependency Injection with Context
Use `ReaderTaskEither` for testable components with injected dependencies.

```typescript
import * as RTE from 'fp-ts/ReaderTaskEither'
import { pipe } from 'fp-ts/function'
import { createContext, useContext, ReactNode } from 'react'

interface AppDependencies {
  api: { getUser: (id: string) => Promise<User>; updateUser: (id: string, data: Partial<User>) => Promise<User> }
  analytics: { track: (event: string, data?: object) => void }
}

const DepsContext = createContext<AppDependencies | null>(null)

function AppProvider({ deps, children }: { deps: AppDependencies; children: ReactNode }) {
  return <DepsContext.Provider value={deps}>{children}</DepsContext.Provider>
}

function useDeps(): AppDependencies {
  const deps = useContext(DepsContext)
  if (!deps) throw new Error('Missing AppProvider')
  return deps
}
```

### 7. React 19 Patterns
Use `use()` for Promises:
```typescript
import { use, Suspense } from 'react'

function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise)
  return <div>{user.name}</div>
}
```

Use `useActionState` for Forms:
```typescript
import { useActionState } from 'react'
import * as E from 'fp-ts/Either'

async function submitForm(prevState: FormState, formData: FormData): Promise<FormState> {
  const data = { email: formData.get('email') as string, password: formData.get('password') as string }
  return pipe(
    validateForm(data),
    E.match(
      (errors) => ({ errors, success: false }),
      async (valid) => { await saveToServer(valid); return { errors: [], success: true } }
    )
  )
}
```

Use `useOptimistic` for Instant Feedback:
```typescript
import { useOptimistic } from 'react'

function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, { ...newTodo, pending: true }]
  )
  // ...
}
```

## Pitfalls
- **Impossible States with Booleans**: Using `{ data, loading, error }` can lead to impossible combinations like `{ data: user, loading: true, error: someError }`. Use `RemoteData` to ensure only valid states exist.
- **Referential Instability**: `O.some(1)` creates a new object every render. If passed to `useEffect` dependencies, it will trigger the effect every render. Use `useMemo` or `fp-ts-react-stable-hooks` to maintain referential stability.
- **Missing Provider**: When using Context for dependency injection, forgetting to wrap components in the Provider will cause `useDeps()` to throw. Always ensure the Provider is at the root of your app.

## Verification
1. **Type Checking**: Run `npx tsc --noEmit` to ensure all fp-ts types align correctly with your React components.
2. **Unit Testing**: Use mock dependencies with `AppProvider` to test components in isolation.
```typescript
const mockDeps: AppDependencies = {
  api: {
    getUser: jest.fn().mockResolvedValue({ id: '1', name: 'Test User' }),
    updateUser: jest.fn().mockResolvedValue({ id: '1', name: 'Updated' }),
  },
  analytics: { track: jest.fn() },
}

test('loads user on mount', async () => {
  render(
    <AppProvider deps={mockDeps}>
      <UserProfile userId="1" />
    </AppProvider>
  )
  await screen.findByText('Test User')
  expect(mockDeps.api.getUser).toHaveBeenCalledWith('1')
})
```
3. **Render Output**: Verify that `Option`, `Either`, and `RemoteData` pattern matching renders the correct UI states (e.g., loading spinners, error messages, success data).
