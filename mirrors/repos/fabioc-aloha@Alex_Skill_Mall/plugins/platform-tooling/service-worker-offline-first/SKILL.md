---
type: skill
lifecycle: stable
inheritance: inheritable
name: service-worker-offline-first
description: Progressive Web App offline-first patterns — Service Worker lifecycle, caching strategies, background sync, and offline fallbacks for resilient web applications
tier: standard
applyTo: '**/*service*,**/*worker*,**/*offline*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Service Worker Offline-First Patterns


> Resilient web applications that work when the network doesn't.

## Caching Strategy Selection

| Strategy | Latency | Freshness | Best For |
|----------|---------|-----------|----------|
| **Cache-First** | Fastest | Stale risk | Static assets, fonts, icons |
| **Network-First** | Slower | Always fresh | API calls, dynamic content |
| **Stale-While-Revalidate** | Fast | Eventually fresh | Semi-static content, user profiles |
| **Network-Only** | Network-dependent | Always fresh | Authentication, real-time data |
| **Cache-Only** | Fastest | Frozen | App shell, offline page |

## Service Worker Lifecycle

```
Install → waitUntil(cacheStaticAssets) → skipWaiting()
   ↓
Activate → waitUntil(cleanOldCaches) → clients.claim()
   ↓
Fetch → route to strategy by request type
```

## Core Structure

```javascript
const CACHE_VERSION = 'v1';
const STATIC_CACHE = `app-static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `app-dynamic-${CACHE_VERSION}`;
const API_CACHE = `app-api-${CACHE_VERSION}`;

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
];

// Install - Cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate - Clean up old caches
self.addEventListener('activate', (event) => {
  const currentCaches = [STATIC_CACHE, DYNAMIC_CACHE, API_CACHE];
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => !currentCaches.includes(key))
            .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// Fetch - Route to appropriate strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (!url.protocol.startsWith('http')) return;

  if (isApiRequest(request)) {
    event.respondWith(networkFirstWithTimeout(request, API_CACHE, 5000));
  } else if (request.destination === 'image') {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
  } else if (request.mode === 'navigate') {
    event.respondWith(networkFirstWithTimeout(request, DYNAMIC_CACHE, 3000));
  } else {
    event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE));
  }
});
```

## Caching Strategies

### Cache-First with Expiry

```javascript
async function cacheFirstWithExpiry(request, cacheName, maxAge) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  if (cached) {
    const cachedDate = new Date(cached.headers.get('sw-cached-date') || 0);
    if (Date.now() - cachedDate.getTime() < maxAge) {
      return cached; // Fresh cache hit
    }
  }

  try {
    const response = await fetch(request);
    if (response.ok) {
      const headers = new Headers(response.headers);
      headers.append('sw-cached-date', new Date().toISOString());
      const timestamped = new Response(response.clone().body, {
        status: response.status,
        statusText: response.statusText,
        headers,
      });
      await cache.put(request, timestamped);
    }
    return response;
  } catch {
    if (cached) return cached; // Return stale on network failure
    throw new Error('Network failed and no cache available');
  }
}
```

### Network-First with Timeout

```javascript
async function networkFirstWithTimeout(request, cacheName, timeout) {
  const cache = await caches.open(cacheName);

  try {
    const response = await Promise.race([
      fetch(request),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Network timeout')), timeout)
      ),
    ]);

    if (response.ok) {
      await cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await cache.match(request);
    if (cached) return cached;

    if (request.mode === 'navigate') {
      return caches.match('/offline.html');
    }
    return new Response(
      JSON.stringify({ error: 'Offline', cached: false }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
```

### Stale-While-Revalidate

```javascript
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  });

  return cached || fetchPromise;
}
```

## Background Sync

Queue failed mutations for retry when connectivity resumes:

```javascript
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-api-calls') {
    event.waitUntil(retryFailedRequests());
  }
});

async function retryFailedRequests() {
  // Read queued requests from IndexedDB
  const queue = await getQueuedRequests();
  const results = await Promise.allSettled(
    queue.map((req) => fetch(req.url, {
      method: req.method,
      headers: new Headers(req.headers),
      body: req.body,
    }))
  );

  // Remove successful, keep failed for next sync
  const remaining = queue.filter((_, i) =>
    results[i].status !== 'fulfilled' || !results[i].value.ok
  );
  await saveQueuedRequests(remaining);

  // Notify open tabs
  const clients = await self.clients.matchAll();
  clients.forEach((client) => {
    client.postMessage({ type: 'SYNC_COMPLETE', remaining: remaining.length });
  });
}
```

## React Registration

```typescript
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker?.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              showUpdateNotification(); // New version available
            }
          });
        });
      });
  });
}
```

## Critical Rules

| Rule | Why |
|------|-----|
| Always clean old caches on activate | Storage bloats without cleanup |
| Use `skipWaiting()` + `clients.claim()` | Immediate control of pages |
| Version bump cache names on deploy | Forces fresh asset fetch |
| Only cache GET requests | Mutations need idempotency guarantees |
| Provide offline fallback for navigation | Users see blank page otherwise |
| Test in incognito | Avoids stale SW from previous sessions |

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| SW serves stale content forever | Add cache expiry or version bumping |
| Infinite redirect loops | Exclude auth endpoints from caching |
| Cache fills up device storage | Set max cache size, prune old entries |
| SW blocks updates | Use `skipWaiting()` to activate immediately |
| API data stale after offline | Show "last updated" timestamp to users |
