# Fabric REST API Scopes Reference

## Table of Contents

- [Scope Types](#scope-types)
- [Generic Scopes](#generic-scopes)
- [Specific CRUD Scopes](#specific-crud-scopes)
- [Other Scopes](#other-scopes)
- [Performance Implications](#performance-implications)
- [Entra ID App Registration](#entra-id-app-registration)

---

## Scope Types

Fabric REST API scopes control what your authenticated application can do. There are two main categories.

**Generic scopes** apply broadly across all item types. **Specific scopes** target individual item types for more granular consent.

---

## Generic Scopes

| Scope | Permission |
|-------|-----------|
| `Item.Read.All` | Read all Fabric items the user has access to |
| `Item.ReadWrite.All` | Read and write all Fabric items |
| `Item.Execute.All` | Execute operations on all Fabric items |
| `Item.Reshare.All` | Reshare all Fabric items |

Use generic scopes when your application needs broad access across multiple item types, such as governance or monitoring tools.

---

## Specific CRUD Scopes

Format: `<itemType>.Read.All` or `<itemType>.ReadWrite.All`

| Scope Example | Permission |
|--------------|-----------|
| `Notebook.ReadWrite.All` | Read and write notebooks |
| `Notebook.Read.All` | Read notebooks only |
| `Lakehouse.ReadWrite.All` | Read and write lakehouses |
| `Report.Read.All` | Read reports only |
| `Workspace.ReadWrite.All` | Read and write workspace configuration |

Specific scopes are preferred because they create a more granular token and allow users to grant only the consent needed.

---

## Other Scopes

| Scope | Purpose |
|-------|---------|
| `Workspace.ReadWrite.All` | Manage workspace properties |
| `https://api.fabric.microsoft.com/.default` | Request all statically assigned permissions (service principal flows) |

---

## Performance Implications

Scope selection can affect API performance:

1. **Fewer scopes = faster token issuance.** Tokens with fewer permissions are generated marginally faster and are smaller in size.

2. **The `.default` scope** requests all permissions configured on the app registration. This is standard for client credentials flows but produces larger tokens.

3. **Token size** grows with scope count. Extremely large tokens (>4KB) can add overhead to every API request because the token is sent in the Authorization header.

4. **Consent delays** — Interactive flows with many scopes show a longer consent dialog, which adds perceived latency on first use.

**Recommendation:** Request only the scopes your application needs for its current operation. For service principals, configure only necessary API permissions in the Azure portal.

---

## Entra ID App Registration

To register an app for Fabric REST API access:

1. Open **Azure Portal** → **App Registrations** → **New Registration**
2. Navigate to **API Permissions** → **Add a Permission** → **Power BI Service**
3. Select the required Fabric scopes
4. Grant admin consent (if required by your organization)
5. Create a client secret or upload a certificate for authentication

**Token endpoint:**
```
POST https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token
```

**Required body parameters for client credentials:**
```
grant_type=client_credentials
client_id={clientId}
client_secret={clientSecret}
scope=https://api.fabric.microsoft.com/.default
```

For full registration instructions, see the Microsoft documentation on creating a Microsoft Entra ID app for Fabric.
