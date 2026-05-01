# Vite + Azure Static Web Apps Scaffold

A production-ready Vite SPA scaffold with all Azure SWA gotchas pre-solved.

---

## What You Get

| Feature | Status |
|---------|--------|
| Vite 5.x with optimized build | ✅ |
| Azure SWA config with correct route ordering | ✅ |
| Auth routes configured for Entra ID | ✅ |
| CORS and security headers set | ✅ |
| GitHub Actions deployment workflow | ✅ |
| AbortController for API calls | ✅ |
| Self-hosted fallback fonts | ✅ |
| TypeScript configured | ✅ |

---

## Prerequisites

- Node.js 20+
- Azure subscription
- GitHub account
- Azure CLI installed

---

## Quick Start

### 1. Copy the Scaffold

```bash
cp -r scaffolds/vite-azure-swa/ /path/to/my-new-app/
cd /path/to/my-new-app/
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create --name my-app-rg --location eastus

# Create Static Web App
az staticwebapp create \
  --name my-app \
  --resource-group my-app-rg \
  --source https://github.com/YOUR_ORG/my-app \
  --branch main \
  --app-location "/" \
  --output-location "dist" \
  --login-with-github
```

### 4. Configure Secrets

Add to GitHub repository secrets:
- `AZURE_STATIC_WEB_APPS_API_TOKEN` — From Azure portal

### 5. Push and Deploy

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_ORG/my-app.git
git push -u origin main
```

GitHub Actions will build and deploy automatically.

---

## What's Pre-Configured

### staticwebapp.config.json

```json
{
  "routes": [
    { "route": "/.auth/*", "allowedRoles": ["anonymous"] },
    { "route": "/api/*", "allowedRoles": ["authenticated"] },
    { "route": "/*", "allowedRoles": ["anonymous"] }
  ],
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/api/*", "/.auth/*"]
  },
  "globalHeaders": {
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff"
  }
}
```

**Why this ordering**: Auth routes MUST come before wildcards. See [azure-swa-gotchas](../../skills/cloud/azure-swa-gotchas/).

### API Utility with AbortController

```typescript
// src/lib/api.ts
export async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout = 180000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}
```

**Why**: Long API calls drop silently without explicit timeout.

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Azure SWA

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          
      - run: npm ci
      - run: npm run build
      
      - uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/"
          output_location: "dist"
          skip_app_build: true  # We already built
```

**Why GitHub Actions over SWA CLI**: CLI v2.0.8 has a silent failure bug.

---

## Customization Points

| File | What to Change |
|------|----------------|
| `staticwebapp.config.json` | Add routes for your API, adjust auth requirements |
| `vite.config.ts` | Add plugins, configure build output |
| `src/lib/api.ts` | Adjust timeout, add retry logic |
| `.github/workflows/deploy.yml` | Add tests, change triggers |

---

## Adding Entra ID Authentication

### 1. Create App Registration

```bash
az ad app create --display-name "my-app-auth"
```

### 2. Add Redirect URIs

In Azure Portal, add BOTH:
- `https://YOUR-APP.azurestaticapps.net/.auth/login/aad/callback`
- `https://your-custom-domain.com/.auth/login/aad/callback` (if using custom domain)

### 3. Update Config

```json
{
  "auth": {
    "identityProviders": {
      "azureActiveDirectory": {
        "registration": {
          "openIdIssuer": "https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0",
          "clientIdSettingName": "AAD_CLIENT_ID",
          "clientSecretSettingName": "AAD_CLIENT_SECRET"
        }
      }
    }
  }
}
```

---

## Known Limitations

- No server-side rendering (SPA only)
- Embedded Functions not included (use linked backend)
- No preview environments configured (add if needed)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Deploy succeeds but site unchanged | Check `output_location` matches Vite output |
| Auth redirect loop | Verify route ordering and redirect URIs |
| API returns 404 | Ensure no `api_location` in workflow if using linked backend |
| Long API calls fail | AbortController already configured; check Azure timeouts |

See [azure-swa-gotchas](../../skills/cloud/azure-swa-gotchas/) for comprehensive troubleshooting.
