---
type: skill
lifecycle: stable
inheritance: inheritable
name: msal-singleton-pattern
description: Time Saved: 1+ hour debugging silent auth failures
tier: standard
applyTo: '**/*msal*,**/*singleton*,**/*pattern*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# MSAL Singleton Pattern

**Category**: Azure
**Time Saved**: 1+ hour debugging silent auth failures
**Battle-tested**: Yes — HeadstartWebsite, Next.js + Azure projects

---

## The Problem

Your React/Next.js app uses MSAL.js for Azure AD authentication. Login works, but token refresh fails silently. Sometimes users get logged out randomly. The console shows cryptic "interaction_in_progress" errors.

## Why It Happens

MSAL.js `PublicClientApplication` maintains an internal token cache and tracks in-flight auth requests. Creating multiple instances causes:

- Token cache conflicts (different instances don't share tokens)
- Race conditions on `acquireTokenSilent`
- "interaction_in_progress" errors when two instances try to redirect

## The Rule

**Initialize MSAL once, share the singleton across your entire app**

```typescript
// ❌ BROKEN — new instance on every import/render
function getAuth() {
  return new PublicClientApplication(msalConfig);
}

// ✅ CORRECT — module-level singleton with async init
let msalInstance: PublicClientApplication | null = null;
let initPromise: Promise<PublicClientApplication> | null = null;

export async function getMsalInstance(): Promise<PublicClientApplication> {
  if (msalInstance) return msalInstance;
  
  if (!initPromise) {
    initPromise = (async () => {
      const instance = new PublicClientApplication(msalConfig);
      await instance.initialize();  // Required in MSAL.js 2.x+
      msalInstance = instance;
      return instance;
    })();
  }
  
  return initPromise;
}
```

## React Integration

```typescript
// MsalProvider.tsx
import { MsalProvider } from '@azure/msal-react';
import { getMsalInstance } from './msal-singleton';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [instance, setInstance] = useState<PublicClientApplication | null>(null);

  useEffect(() => {
    getMsalInstance().then(setInstance);
  }, []);

  if (!instance) return <Loading />;

  return <MsalProvider instance={instance}>{children}</MsalProvider>;
}
```

## Next.js App Router Pattern

```typescript
// app/providers.tsx
'use client';

import { MsalProvider } from '@azure/msal-react';
import { getMsalInstance } from '@/lib/msal-singleton';

export function Providers({ children }: { children: React.ReactNode }) {
  const [instance, setInstance] = useState<IPublicClientApplication | null>(null);

  useEffect(() => {
    getMsalInstance().then(setInstance);
  }, []);

  if (!instance) return null;

  return <MsalProvider instance={instance}>{children}</MsalProvider>;
}
```

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| New instance per request | Token cache miss, re-auth required | Use singleton |
| Missing `initialize()` | Silent failures in MSAL 2.x+ | Call and await `initialize()` |
| Instance in component state | Re-created on re-render | Module-level singleton |
| Multiple `MsalProvider`s | "interaction_in_progress" | Single provider at app root |

## Verification

```typescript
// Add to singleton for debugging
export function getMsalDebugInfo() {
  return {
    instanceExists: !!msalInstance,
    accounts: msalInstance?.getAllAccounts() ?? [],
    cacheSize: Object.keys(msalInstance?.getTokenCache()?.serialize() ?? {}).length,
  };
}
```

If `accounts` is empty after login, the singleton isn't being used consistently.

---

**Source**: Promoted from AI-Memory global-knowledge.md (2026-04-27)
