---
name: valtio
description: "Manages React/Next state with Valtio proxy stores, useSnapshot, derive, and subscribe - mutate the proxy; components re-render on accessed fields. Use when the user wants Valtio, mutable proxy state, or store access outside React. Not for Redux reducers, Zustand set(), or Convex useQuery as the store."
version: 1.0.1
---

# Valtio

## Overview

Valtio makes React state management feel like plain JavaScript: mutate proxy objects directly and React re-renders automatically. No reducers, no actions, no selectors. Wrap an object in `proxy()`, mutate it anywhere, and components that read the changed properties re-render. Based on JavaScript Proxy, it tracks which properties each component uses and only re-renders when those specific properties change.

## When to Use

- You want the simplest possible state management with minimal boilerplate.
- You are tired of Redux boilerplate or Zustand's `set()` function.
- You need to share state between components without prop drilling.
- State must be accessed or modified outside React (event handlers, WebSocket callbacks, timers).
- Your team prefers mutable patterns over immutable update patterns.
- The user explicitly asks for **valtio**, proxy-based state, or "mutable React state."

## Prerequisites

- A React or Next.js project with TypeScript (recommended).
- Node.js and npm installed.
- On Windows host (primary), use PowerShell for all CLI commands.

## Procedure

### 1. Install Valtio

```powershell
npm install valtio
```

### 2. Create a Proxy Store

Define state as a plain object wrapped in `proxy()`. Mutate the proxy directly—no `setState` or `set()` needed.

```typescript
// store/app.ts
import { proxy, useSnapshot } from "valtio";

export const appState = proxy({
  user: null as { name: string; email: string } | null,
  theme: "light" as "light" | "dark",
  notifications: [] as Array<{ id: string; text: string; read: boolean }>,
  sidebar: { open: true, width: 280 },
});

// Mutate directly — React components auto-update
export function login(user: { name: string; email: string }) {
  appState.user = user;
}

export function toggleTheme() {
  appState.theme = appState.theme === "light" ? "dark" : "light";
}

export function addNotification(text: string) {
  appState.notifications.push({ id: crypto.randomUUID(), text, read: false });
}

export function markAllRead() {
  appState.notifications.forEach((n) => { n.read = true; });
}

export function toggleSidebar() {
  appState.sidebar.open = !appState.sidebar.open;
}
```

### 3. Read State in Components with `useSnapshot`

`useSnapshot` creates a read-only snapshot. The component **only** re-renders when properties it accesses change.

```tsx
// components/Header.tsx
import { useSnapshot } from "valtio";
import { appState, toggleTheme, toggleSidebar } from "@/store/app";

export function Header() {
  const snap = useSnapshot(appState);

  return (
    <header className="flex items-center justify-between p-4">
      <button onClick={toggleSidebar}>☰</button>
      <span>{snap.user?.name ?? "Guest"}</span>
      <button onClick={toggleTheme}>
        {snap.theme === "light" ? "🌙" : "☀️"}
      </button>
    </header>
  );
}
```

### 4. Derived / Computed Values with `derive`

```typescript
// store/derived.ts
import { derive } from "valtio/utils";
import { appState } from "./app";

export const derived = derive({
  unreadCount: (get) => get(appState).notifications.filter((n) => !n.read).length,
  isDarkMode: (get) => get(appState).theme === "dark",
  isLoggedIn: (get) => get(appState).user !== null,
});
```

### 5. Subscribe to Changes Outside React

Use `subscribe()` for side effects: persistence, logging, WebSocket sync.

```typescript
import { subscribe } from "valtio";
import { appState } from "./store/app";

// Log every state change
subscribe(appState, () => {
  console.log("State changed:", JSON.stringify(appState));
});

// Subscribe to a specific nested object
subscribe(appState.sidebar, () => {
  localStorage.setItem("sidebar-open", String(appState.sidebar.open));
});

// Mutate from a WebSocket handler — components auto-update
socket.on("notification", (data) => {
  appState.notifications.push(data);
});
```

### 6. Enable Redux DevTools (Optional)

```typescript
import { devtools } from "valtio/utils";
import { appState } from "./store/app";

devtools(appState, { name: "appState", enabled: true });
```

## Examples

### Example 1: Shopping Cart

**User prompt:** "Build a shopping cart with add/remove/update quantity using simple state management."

1. Create a Valtio proxy for cart state (`items: CartItem[]`, `total` derived).
2. Write actions that directly mutate the array (`push`, `splice`, quantity increment).
3. Build components that read via `useSnapshot` and reactively display cart contents and total.

### Example 2: Persisted Preferences

**User prompt:** "Store user preferences (theme, language, sidebar state) that persist across page loads."

1. Create a Valtio store with preference fields.
2. Use `subscribe()` to sync each preference to `localStorage`.
3. On app init, hydrate the proxy from `localStorage` before first render.

## Guidelines

- **`proxy()` for state, `useSnapshot()` for reading** — always use the snapshot in components.
- **Mutate directly** — `state.count++` works; no `setState` or `set()` needed.
- **Automatic render optimization** — only re-renders when accessed properties change.
- **`subscribe()` for side effects** — persist to localStorage, log, sync.
- **`derive()` for computed values** — auto-recalculates when dependencies change.
- **Works outside React** — mutate from event handlers, WebSocket, timers.
- **Snapshot is read-only** — never mutate `snap`; mutate the original `proxy`.
- **Arrays work naturally** — `push`, `splice`, `filter` all trigger re-renders.
- **Nested objects tracked** — `state.user.name = "new"` triggers re-render.
- **Devtools** — `import { devtools } from "valtio/utils"` for Redux DevTools integration.

## Pitfalls

- **Mutating the snapshot instead of the proxy** — `snap.count = 5` silently fails or throws in dev. Always mutate the original `appState`, not `snap`.
- **Calling `useSnapshot` on a non-proxy** — the object must be wrapped in `proxy()` first or the hook will not track changes.
- **Over-rendering from derived filters** — if a component reads `snap.notifications` and then filters, any change to any notification re-renders it. Use `derive()` to isolate computed values when needed.
- **Forgetting `subscribe` cleanup** — `subscribe()` returns an unsubscribe function; call it on unmount or you will leak listeners.
- **Top-level replacement** — `appState = newObject` does nothing useful; you must mutate properties in place (`appState.user = newUser`), not reassign the proxy variable.
- **Class instances and non-plain objects** — Valtio proxies plain objects and arrays. Class instances may not track correctly unless you follow Valtio's guidance for custom classes.
- **SSR / Next.js hydration mismatch** — if the proxy is initialized from `localStorage` or `window` at module scope, server and client can diverge. Hydrate inside `useEffect` or a client-only provider.

## Verification

1. **Install check:**

```powershell
npm ls valtio
```

Expected output lists `valtio` with the installed version.

2. **Runtime re-render check:** Add a `console.log("render")` inside a component using `useSnapshot`. Mutate an unrelated property on the proxy and confirm the component does **not** log. Mutate an accessed property and confirm it does log.

3. **Snapshot immutability check:** In dev mode, attempt `snap.theme = "dark"`. Valtio should warn or throw that the snapshot is read-only.

4. **Subscribe check:** Register a `subscribe` listener, mutate the watched property, and confirm the callback fires. Call the returned unsubscribe function and confirm subsequent mutations no longer trigger it.

5. **Devtools check:** Open Redux DevTools in the browser; confirm the store name appears and actions are recorded on each mutation.

## Related Skills

- **zustand** — alternative minimal state library using `set()` and selectors.
- **redux-toolkit** — use when you need strict immutability, middleware, or time-travel debugging at scale.
- **react-query** — use for server/async state; pair with Valtio for UI-only state.

## References

- Valtio GitHub: https://github.com/pmndrs/valtio
- Valtio docs: https://valtio.pmnd.rs/
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material Design: https://m3.material.io/
