---
type: skill
lifecycle: stable
inheritance: inheritable
name: msal-authentication
description: Microsoft Authentication Library (MSAL) patterns for React/SPA applications with Entra ID
tier: standard
applyTo: '**/*msal*,**/*authentication*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# MSAL Authentication


> Microsoft Authentication Library patterns for React/SPA applications with Microsoft Entra ID.
> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

**Version**: 1.0.0

---

## Core Concepts

**Microsoft Authentication Library (MSAL)** handles authentication with Microsoft Entra ID (formerly Azure Active Directory). It manages:

- Token acquisition and caching
- Silent token renewal
- Redirect/popup authentication flows
- Multi-tenant and B2B scenarios

### Package Versions

```json
{
  "@azure/msal-browser": "^5.0.0",
  "@azure/msal-react": "^3.0.0"
}
```

---

## Configuration

### Basic MSAL Configuration

```typescript
import { Configuration, PublicClientApplication, LogLevel } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_ENTRA_CLIENT_ID,
    authority: 'https://login.microsoftonline.com/common', // Multi-tenant
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: 'localStorage', // Persist across tabs
    storeAuthStateInCookie: false, // Not needed for modern browsers
  },
  system: {
    loggerOptions: {
      logLevel: import.meta.env.DEV ? LogLevel.Verbose : LogLevel.Warning,
    },
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);
```

### Redirect URI Gotchas (Azure Static Web Apps)

When using `redirectUri: window.location.origin`, you must register redirect URIs for **every hostname** the SPA is served from:

- Custom domains (e.g., `https://portal.example.com`)
- The SWA default hostname (e.g., `https://<app>.<region>.azurestaticapps.net`)

If the app loads (HTTP 200) but auth fails, verify the deployed bundle contains the real client ID (not a build-time placeholder).

### Authority Patterns

| Authority | Use Case |
|-----------|----------|
| `https://login.microsoftonline.com/{tenant-id}` | Single-tenant |
| `https://login.microsoftonline.com/common` | Multi-tenant (any Entra ID) |
| `https://login.microsoftonline.com/organizations` | Work/school accounts only |
| `https://login.microsoftonline.com/consumers` | Personal accounts only |

---

## React Integration

### Provider Setup

```tsx
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from './authConfig';

// Initialize MSAL before rendering
await msalInstance.initialize();
await msalInstance.handleRedirectPromise();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <MsalProvider instance={msalInstance}>
    <App />
  </MsalProvider>
);
```

### Authentication Hooks

```tsx
import { useIsAuthenticated, useMsal, useAccount } from '@azure/msal-react';

function UserProfile() {
  const isAuthenticated = useIsAuthenticated();
  const { instance, accounts } = useMsal();
  const account = useAccount(accounts[0] ?? {});

  if (!isAuthenticated) return <LoginButton />;

  return (
    <div>
      <p>Welcome, {account?.name}</p>
      <p>Email: {account?.username}</p>
    </div>
  );
}
```

### Conditional Rendering Components

```tsx
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';

function App() {
  return (
    <>
      <AuthenticatedTemplate>
        <Dashboard />
      </AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <LandingPage />
      </UnauthenticatedTemplate>
    </>
  );
}
```

---

## Token Acquisition

### Scopes Definition

```typescript
export const scopes = {
  graph: ['https://graph.microsoft.com/.default'],
  graphUser: ['User.Read'],
  graphReports: ['Reports.Read.All'],
  arm: ['https://management.azure.com/.default'],
  api: ['api://{api-client-id}/access_as_user'],
};
```

### Silent Token Acquisition (Preferred)

```typescript
async function getAccessToken(
  instance: IPublicClientApplication,
  account: AccountInfo,
  scopes: string[]
): Promise<string> {
  try {
    const response = await instance.acquireTokenSilent({ scopes, account });
    return response.accessToken;
  } catch (error) {
    if (error instanceof InteractionRequiredAuthError) {
      const response = await instance.acquireTokenPopup({ scopes });
      return response.accessToken;
    }
    throw error;
  }
}
```

### Token Acquisition Hook

```tsx
function useAccessToken(scopes: string[]) {
  const { instance, accounts } = useMsal();
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (accounts.length === 0) return;
    instance.acquireTokenSilent({ scopes, account: accounts[0] })
      .then(response => setToken(response.accessToken))
      .catch(setError);
  }, [instance, accounts, scopes]);

  return { token, error };
}
```

---

## Multi-Tenant Patterns

### Tenant Detection

```typescript
function getTenantFromAccount(account: AccountInfo): string {
  return account.tenantId || 'unknown';
}

function getTenantName(account: AccountInfo): string {
  const claims = account.idTokenClaims as { tenant_name?: string };
  return claims?.tenant_name || account.tenantId || 'Personal Account';
}
```

### Admin Consent Handling

```typescript
export class AdminConsentRequiredError extends Error {
  public tenantId: string;
  public requiredScopes: string[];

  constructor(tenantId: string, scopes: string[]) {
    super('Admin consent required for this tenant.');
    this.name = 'AdminConsentRequiredError';
    this.tenantId = tenantId;
    this.requiredScopes = scopes;
  }
}

function getAdminConsentUrl(clientId: string, tenantId: string): string {
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: window.location.origin,
    scope: 'https://graph.microsoft.com/.default',
  });
  return `https://login.microsoftonline.com/${tenantId}/adminconsent?${params}`;
}
```

---

## Common Pitfalls

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Auth fails on SWA | Redirect URI not registered for SWA hostname | Register all hostnames in app registration |
| Token silently fails | Account not in cache | Fallback to interactive with `acquireTokenPopup` |
| CORS error on token | Wrong authority URL | Match authority to app registration tenant |
| Build-time placeholder | `VITE_` env var not set in SWA config | Set in SWA Application Settings |
| Admin consent loop | Org policy blocks consent | Use admin consent URL flow |

---

## Activation Patterns

| Trigger | Response |
|---------|----------|
| "MSAL", "Entra ID", "authentication" | Full skill activation |
| "redirect URI", "auth fails" | Configuration + Gotchas section |
| "token", "silent", "acquireToken" | Token Acquisition section |
| "multi-tenant", "admin consent" | Multi-Tenant Patterns section |
| "React auth", "MsalProvider" | React Integration section |
