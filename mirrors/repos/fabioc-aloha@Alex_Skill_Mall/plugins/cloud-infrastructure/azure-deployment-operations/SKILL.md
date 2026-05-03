---
type: skill
lifecycle: stable
inheritance: inheritable
name: "azure-deployment-operations"
description: Production deployment patterns for Azure Static Web Apps, Container Apps, App Service, and infrastructure
tier: standard
applyTo: '**/*azure*,**/*deployment*,**/*operations*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Azure Deployment Operations


> Battle-tested patterns for deploying and operating Azure services in production.

**Scope**: Inheritable skill. Covers SWA, Container Apps, App Service, security posture, rate limiting, production checklists, and multi-subscription management.

## Azure Static Web Apps (SWA)

### Deployment Method

**Prefer GitHub Actions over SWA CLI.** SWA CLI v2.0.8 silently fails deploys (reports success, uploads nothing). Use `Azure/static-web-apps-deploy@v1`:

```yaml
- uses: Azure/static-web-apps-deploy@v1
  with:
    azure_static_web_apps_api_token: ${{ secrets.SWA_DEPLOY_TOKEN }}
    repo_token: ${{ secrets.GITHUB_TOKEN }}
    action: upload
    app_location: dist          # adjust to your output folder
    skip_app_build: true        # if pre-built
    skip_api_build: true        # if using linked backend
```

**Critical**: If the SWA has a linked backend (Azure Functions via `az staticwebapp backends link`), do NOT include `api_location` — it creates embedded functions that override the linked backend.

Get the deploy token: `az staticwebapp secrets list --name <name> --query "properties.apiKey" -o tsv`

### Environment Deployment

SWA defaults to **preview** environments. Always specify production explicitly in any CLI fallback:

```bash
swa deploy --env production
```

### Custom Domain Registration

Custom domains require a two-step process:

| Step | Action | Validates |
|------|--------|----------|
| 1. **CNAME record** | Point domain to SWA default hostname | DNS ownership |
| 2. **Hostname registration** | `az staticwebapp hostname set` | Azure binding |

**Common error**: Adding CNAME but forgetting hostname registration. Both steps are required.

### SWA Configuration

```json
{
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/api/*", "/assets/*"]
  },
  "routes": [
    { "route": "/api/*", "allowedRoles": ["authenticated"] }
  ],
  "globalHeaders": {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY"
  }
}
```

## Azure Container Apps

### Health Probe Configuration

Container Apps health probes have specific threshold ranges:

| Parameter | Min | Max | Recommended |
|-----------|-----|-----|-------------|
| `failureThreshold` | 1 | 48 | 3-5 for liveness, 10-30 for startup |
| `periodSeconds` | 1 | 240 | 10 for liveness, 5 for startup |
| `initialDelaySeconds` | 0 | 60 | 0 for liveness (use startup probe instead) |
| `timeoutSeconds` | 1 | 240 | 5 |

**Pattern**: Use a **startup probe** with high failure threshold (30) for slow-starting apps instead of a high `initialDelaySeconds` on the liveness probe.

### Container Apps Deployment

```bash
# Update with new image
az containerapp update \
  --name myapp \
  --resource-group myrg \
  --image myregistry.azurecr.io/myapp:v1.2.3

# Scale configuration
az containerapp update \
  --name myapp \
  --resource-group myrg \
  --min-replicas 1 \
  --max-replicas 10
```

## Azure App Service

### 11-Step Deployment Pipeline

Typical App Service deployment takes ~7 minutes:

| Step | Duration | Action |
|------|----------|--------|
| 1 | 5s | Authenticate to Azure |
| 2 | 10s | Validate resource group exists |
| 3 | 30s | Build application |
| 4 | 15s | Run tests |
| 5 | 20s | Package artifacts |
| 6 | 10s | Upload to staging slot |
| 7 | 60s | Warm up staging slot |
| 8 | 5s | Run smoke tests on staging |
| 9 | 30s | Swap staging → production |
| 10 | 10s | Validate production health |
| 11 | 5s | Tag release in source control |

**Rule**: Always use staging slots for zero-downtime deployment. Direct-to-production deployments cause cold-start downtime.

### Production Readiness Checklist

| Category | Requirement | Why |
|----------|------------|-----|
| **Compute** | P1v3 or higher | Burstable tiers have CPU throttling |
| **Networking** | VNet integration | Isolate from public internet |
| **Data** | Private endpoints for storage/DB | No public connection strings |
| **Identity** | Managed identity (no connection strings) | Eliminates secret rotation |
| **Monitoring** | Application Insights enabled | Observability |
| **Scaling** | Auto-scale rules configured | Handle load spikes |
| **Backup** | Automated backup policy | Disaster recovery |
| **SSL** | Custom domain + managed certificate | Trust and security |

## Security Posture Assessment

### Pass/Fail Matrix

Use a matrix to track security controls across all resources:

| Control | App Service | SQL DB | Storage | Key Vault |
|---------|:-----------:|:------:|:-------:|:---------:|
| Managed Identity | ✅ | ✅ | ✅ | ✅ |
| Private Endpoint | ✅ | ✅ | ❌ | ✅ |
| Diagnostic Logs | ✅ | ❌ | ✅ | ✅ |
| RBAC (no keys) | ✅ | ✅ | ❌ | ✅ |
| Encryption at Rest | ✅ | ✅ | ✅ | ✅ |

**Rule**: Any ❌ in the matrix is a tracked remediation item with a priority (P0-P3) and SLA.

## Rate Limiting

### Spread vs. Burst

For API calls and deployment operations:

| Strategy | Pattern | Use When |
|----------|---------|----------|
| **Spread** | 10 calls/sec evenly spaced | Sustained throughput |
| **Burst** | 100 calls then wait | Quick batch operations |

**Rule**: Prefer **spread** over burst for production workloads. Azure APIs throttle based on request rate, and burst patterns hit throttle limits earlier than spread patterns with the same total throughput.

### Retry Pattern

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err: any) {
      if (attempt === maxRetries) throw err;
      if (err.statusCode === 429) {
        // Use Retry-After header if available
        const delay = err.headers?.['retry-after']
          ? parseInt(err.headers['retry-after']) * 1000
          : baseDelay * Math.pow(2, attempt);
        await new Promise(r => setTimeout(r, delay));
      } else {
        throw err; // Don't retry non-throttle errors
      }
    }
  }
  throw new Error('Unreachable');
}
```

## Multi-Subscription Management

### Folder Organization

For organizations with multiple Azure subscriptions:

```
azure/
├── production/
│   ├── main.bicep
│   └── parameters.prod.json
├── staging/
│   ├── main.bicep
│   └── parameters.staging.json
├── development/
│   └── parameters.dev.json
└── shared/
    ├── modules/          # Shared Bicep modules
    └── policies/         # Azure Policy definitions
```

### Resource Inventory

Before any infrastructure changes, document what exists:

```bash
# List all resources in subscription
az resource list --subscription "My Subscription" \
  --output table \
  --query "[].{Name:name, Type:type, RG:resourceGroup, Location:location}"

# Export to JSON for diff tracking
az resource list --subscription "My Subscription" -o json > inventory.json
```

### Subscription Documentation Template

Each subscription should have a living document with:

| Section | Content |
|---------|---------|
| **Purpose** | What this subscription is for |
| **Owner** | Team/person responsible |
| **Budget** | Monthly spend limit and alerts |
| **Resources** | Link to inventory command output |
| **Access** | RBAC assignments and justification |
| **Networking** | VNet topology, peering, DNS zones |

## Known Gotchas

### Mail.Send on Corporate Tenants

Microsoft 365 corporate tenants often **block** `Mail.Send` permission for third-party apps. If your app needs to send email:

1. Check tenant admin consent policies first
2. Consider `SendMail` via Graph with delegated (not application) permissions
3. Have a fallback (SMTP, SendGrid) for blocked tenants
4. Document the limitation clearly for users

### Azure CLI Context

```bash
# Always verify which subscription is active
az account show --query "{Name:name, Id:id}" -o table

# Set explicitly before operations
az account set --subscription "Target Subscription"
```

**Rule**: Never assume the correct subscription is active. Always verify or set explicitly in scripts.

## Infrastructure as Code

### Bicep Best Practices for Deployment

| Practice | Why |
|----------|-----|
| Use modules for reusable components | DRY principle |
| Parameters file per environment | Environment isolation |
| `@secure()` decorator for secrets | Prevents logging |
| `existing` keyword for references | No accidental recreation |
| What-if before deploy | Catch unintended changes |

```bash
# Always preview changes before deploying
az deployment group what-if \
  --resource-group myrg \
  --template-file main.bicep \
  --parameters @parameters.prod.json
```
