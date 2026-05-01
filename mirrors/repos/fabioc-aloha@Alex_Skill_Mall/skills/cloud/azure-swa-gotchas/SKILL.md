---
type: skill
lifecycle: stable
inheritance: inheritable
name: azure-swa-gotchas
description: Time saved: 2-4 hours per issue
tier: standard
applyTo: '**/*azure*,**/*swa*,**/*gotchas*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Azure Static Web Apps Gotchas

**Time saved**: 2-4 hours per issue

---

## The Problem

Azure Static Web Apps is powerful but has numerous edge cases that cause silent failures or confusing behavior. The documentation covers the happy path; these are the unhappy paths.

## Why This Is Hard to Find

- Each gotcha is documented somewhere, but scattered across GitHub issues, Stack Overflow, and blog posts
- Error messages often don't indicate the root cause
- Some behaviors are undocumented "features"
- The combination of SWA + Functions + Auth creates emergent failure modes

---

## The Gotchas

### 1. Auth Route Ordering Matters

**Symptom**: Login callbacks return 401 → infinite redirect loop

**Cause**: `/.auth/*` routes must be explicitly allowed for `anonymous` BEFORE any `/*` wildcard with `authenticated`.

**Solution**:

```json
{
  "routes": [
    { "route": "/.auth/*", "allowedRoles": ["anonymous"] },
    { "route": "/*", "allowedRoles": ["authenticated"] }
  ]
}
```

**Time saved**: 1-2 hours

---

### 2. Embedded API Overrides Linked Backend

**Symptom**: Your linked Function App returns 404, but embedded Functions work

**Cause**: If the workflow has `api_location:`, SWA deploys embedded Functions which override any linked backend.

**Solution**: Remove `api_location` from workflow to route to the linked Function App.

```yaml
# Remove this line:
# api_location: "api"
```

**Time saved**: 1-2 hours

---

### 3. SWA CLI v2.0.8 Silently Fails

**Symptom**: CLI reports success but nothing uploads

**Cause**: Known bug in v2.0.8

**Solution**: Use GitHub Actions (`Azure/static-web-apps-deploy@v1`) instead.

```yaml
- uses: Azure/static-web-apps-deploy@v1
  with:
    azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
    repo_token: ${{ secrets.GITHUB_TOKEN }}
    action: "upload"
    app_location: "/"
    output_location: "dist"
```

**Time saved**: 30-60 min

---

### 4. Custom Domain Redirect URIs Required

**Symptom**: Auth works on default hostname, fails on custom domain

**Cause**: Entra ID app registration must include callback URIs for BOTH the default SWA hostname AND any custom domain.

**Solution**: Add both to app registration:

- `https://yourapp.azurestaticapps.net/.auth/login/aad/callback`
- `https://yourdomain.com/.auth/login/aad/callback`

**Time saved**: 30-60 min

---

### 5. Embedded Functions Lack IDENTITY_HEADER

**Symptom**: `ManagedIdentityCredential` fails in embedded Functions

**Cause**: Embedded Functions don't have the managed identity environment variables.

**Solution**: Create a standalone Function App with system-assigned managed identity, link via `az staticwebapp backends link`.

```bash
az staticwebapp backends link \
  --name my-swa \
  --resource-group my-rg \
  --backend-resource-id /subscriptions/.../Microsoft.Web/sites/my-func-app \
  --backend-region eastus
```

**Time saved**: 2-3 hours

---

### 6. X-Frame-Options Blocks Iframes by Default

**Symptom**: SWA content won't load in an iframe

**Cause**: Default `X-Frame-Options` is `DENY`.

**Solution**: Set `SAMEORIGIN` in `staticwebapp.config.json`:

```json
{
  "globalHeaders": {
    "X-Frame-Options": "SAMEORIGIN"
  }
}
```

**Time saved**: 30 min

---

### 7. Vite public/ Requires Rebuild + Redeploy

**Symptom**: New file in `public/` doesn't appear on site

**Cause**: Files in `public/` are copied to `dist/` during build. Committing doesn't serve them.

**Solution**: Rebuild and redeploy:

```bash
npm run build
# Then trigger deployment
```

**Time saved**: 30 min

---

### 8. Disconnect Before Switching Deploy Methods

**Symptom**: Deployment conflicts or stale content

**Cause**: Previous deployment source still linked

**Solution**: Disconnect before moving to CLI or new workflow:

```bash
az staticwebapp disconnect --name my-swa
```

**Time saved**: 30 min

---

### 9. Azure Functions v4 Requires Main Entry

**Symptom**: Functions silently fail to deploy

**Cause**: `package.json` must have `"main"` pointing to the file that registers functions via `app.http()`.

**Solution**:

```json
{
  "main": "dist/index.js"
}
```

Where `index.js` contains:

```javascript
const { app } = require('@azure/functions');
app.http('myFunction', { ... });
```

**Time saved**: 1-2 hours

---

### 10. Verify Hostname via CLI

**Symptom**: Using wrong hostname in configuration

**Cause**: SWA hostnames can change, especially after region changes

**Solution**: Always verify:

```bash
az staticwebapp show --name my-swa --query defaultHostname -o tsv
```

**Time saved**: 15 min

---

### 11. Self-Host CDN Libraries in Enterprise

**Symptom**: CDN scripts blocked, CSP violations

**Cause**: Enterprise environments block external CDNs, tracking prevention enabled

**Solution**: Self-host all JavaScript libraries in your `public/` folder.

**Time saved**: 1-2 hours + avoids security review

---

### 12. AbortController for Streaming Endpoints

**Symptom**: Long API calls silently drop

**Cause**: Browsers may kill connections without explicit timeout

**Solution**:

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 min

try {
  const response = await fetch(url, { signal: controller.signal });
  // ...
} finally {
  clearTimeout(timeoutId);
}
```

**Time saved**: 1-2 hours debugging "random" failures

---

## Evidence

- Issue #4521: Embedded Functions override linked backend
- Issue #892: Auth route ordering
- Project: alex-portfolio (all 12 gotchas encountered)
- Azure Static Web Apps GitHub issues (various)

## Related

- [entra-redirect-uris](../entra-redirect-uris/) — More auth gotchas
- [vite-public-rebuild](../../build/vite-public-rebuild/) — Build system details
- Official docs: <https://docs.microsoft.com/azure/static-web-apps/>
