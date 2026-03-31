# Hydration Safety Rules

## Never Use Date in useState Initializer

`new Date()`, `Date.now()`, and `toLocaleTimeString()` produce different values on the server vs. the client, causing React to throw a hydration mismatch error.

### Wrong

```tsx
// Hydration error: server timestamp != client timestamp
const [events, setEvents] = useState(() => [
  { id: "1", timestamp: new Date().toLocaleTimeString() },
])

const [time, setTime] = useState(new Date().toLocaleTimeString())

const [id, setId] = useState(() => Date.now().toString())
```

### Correct

Use static/hardcoded strings for SSR-safe initial state. Move live values inside `useEffect` or `setInterval`.

```tsx
// Static initial timestamps — identical on server and client
const INITIAL_TIMESTAMPS = ["10:30:00", "10:30:04", "10:30:08"]

const [events, setEvents] = useState(() =>
  SEED_DATA.slice(0, 3).map((item, i) => ({
    ...item,
    id: `init-${i}`,
    timestamp: INITIAL_TIMESTAMPS[i],
  }))
)

// Pure function, safe to call client-side only
function nowTimeString() {
  const d = new Date()
  return [d.getHours(), d.getMinutes(), d.getSeconds()]
    .map((n) => String(n).padStart(2, "0"))
    .join(":")
}

// Live updates only in useEffect (never runs on server)
useEffect(() => {
  const interval = setInterval(() => {
    setEvents((prev) => [
      ...prev.slice(-49),
      {
        id: `evt-${Date.now()}`,
        timestamp: nowTimeString(),
        // ...rest of event
      },
    ])
  }, 2000)
  return () => clearInterval(interval)
}, [])
```

## Locale-Dependent Formatting

`toLocaleString()`, `toLocaleDateString()`, `toLocaleTimeString()` are locale-dependent — the server locale may differ from the browser locale.

```tsx
// WRONG — locale mismatch
<span>{new Date(item.createdAt).toLocaleTimeString()}</span>

// CORRECT — use fixed format string or static value
<span>{item.createdAt}</span>  // pre-formatted string, e.g. "2 hours ago"
```

## suppressHydrationWarning

Only use `suppressHydrationWarning` when the mismatch is **intentional** (e.g. a live clock that is always slightly different):

```tsx
<time suppressHydrationWarning>{liveTime}</time>
```

Do not use it to silence bugs — fix the root cause instead.
