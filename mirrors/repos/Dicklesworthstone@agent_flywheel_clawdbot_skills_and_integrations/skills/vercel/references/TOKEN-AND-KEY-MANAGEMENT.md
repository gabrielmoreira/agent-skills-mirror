# Token and Key Management

> **TL;DR:** Use Vercel env vars for app tokens, Wrangler secrets for Workers. For "adult" security, use OIDC to avoid long-lived credentials entirely.

---

## Table of Contents

- [Vercel Environment Variables](#vercel-environment-variables)
- [Cloudflare Secrets](#cloudflare-secrets)
- [Vault Integration](#vault-integration)
- [OIDC (Best Practice)](#oidc-best-practice)
- [Local Development](#local-development)

---

## Vercel Environment Variables

### CLI Operations

```bash
# List all env vars
vercel env ls

# Add interactively
vercel env add MY_SECRET

# Add with target
vercel env add MY_SECRET production
vercel env add MY_SECRET preview
vercel env add MY_SECRET development

# Pull to local file
vercel env pull .env.local
vercel env pull .env.production --environment=production

# Remove
vercel env rm MY_SECRET production
```

### REST API (For Agents/Automation)

**Better for bulk sync** — converge state programmatically.

```bash
# Upsert single variable
curl -X POST "https://api.vercel.com/v10/projects/$PROJECT_ID/env?upsert=true" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "DATABASE_URL",
    "value": "postgres://...",
    "target": ["production"],
    "type": "encrypted"
  }'

# Upsert with git branch scope (preview)
curl -X POST "https://api.vercel.com/v10/projects/$PROJECT_ID/env?upsert=true" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "DEBUG_MODE",
    "value": "true",
    "target": ["preview"],
    "gitBranch": "feature-x"
  }'

# List all env vars
curl "https://api.vercel.com/v10/projects/$PROJECT_ID/env" \
  -H "Authorization: Bearer $VERCEL_TOKEN"

# Delete
curl -X DELETE "https://api.vercel.com/v10/projects/$PROJECT_ID/env/$ENV_ID" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

### Target Types

| Target | When Applied |
|--------|--------------|
| `production` | Production deployments only |
| `preview` | Preview deployments |
| `development` | `vercel dev` local server |

### Variable Types

| Type | Visibility |
|------|------------|
| `plain` | Visible in dashboard, logs |
| `encrypted` | Hidden, only decrypted at runtime |
| `sensitive` | Hidden everywhere, marked sensitive |

**Best practice:** Use `encrypted` or `sensitive` for secrets.

---

## Cloudflare Secrets

### Wrangler Secrets (For Workers)

```bash
# Add secret (interactive prompt)
wrangler secret put API_KEY

# Add secret (pipe value)
echo "my-secret-value" | wrangler secret put API_KEY

# List secrets (names only, values hidden)
wrangler secret list

# Delete secret
wrangler secret delete API_KEY

# Add to specific environment
wrangler secret put API_KEY --env staging
```

**Important:** `wrangler secret put` deploys a new Worker version immediately.

### Local Development

Use `.dev.vars` for local secrets (gitignored):

```bash
# .dev.vars (never commit)
API_KEY=local-dev-key
DATABASE_URL=postgres://localhost/dev
```

Wrangler automatically reads `.dev.vars` during `wrangler dev`.

---

## Vault Integration

### Option A: HCP Vault Secrets → Vercel Sync

HashiCorp provides a managed sync integration:

1. Store secrets in HCP Vault Secrets
2. Configure sync destination: Vercel
3. Secrets auto-sync to Vercel project env vars

**Benefits:**
- Single source of truth
- Audit trail
- Rotation support

### Option B: Manual Sync Script

```bash
#!/bin/bash
# sync-secrets.sh

VAULT_ADDR="https://vault.example.com"
VERCEL_PROJECT_ID="prj_xxx"

# Read from Vault
DB_URL=$(vault kv get -field=url secret/prod/database)
API_KEY=$(vault kv get -field=key secret/prod/api)

# Sync to Vercel
for var in "DATABASE_URL:$DB_URL" "API_KEY:$API_KEY"; do
  key="${var%%:*}"
  value="${var#*:}"

  curl -X POST "https://api.vercel.com/v10/projects/$VERCEL_PROJECT_ID/env?upsert=true" \
    -H "Authorization: Bearer $VERCEL_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"key\":\"$key\",\"value\":\"$value\",\"target\":[\"production\"],\"type\":\"encrypted\"}"
done
```

---

## OIDC (Best Practice)

**The "adult" way:** Avoid storing long-lived cloud credentials in env vars entirely.

### How It Works

1. Vercel issues short-lived OIDC tokens during builds/functions
2. Your app exchanges the token for short-lived cloud credentials
3. No static secrets stored

### Vercel OIDC Token

Vercel automatically provides `VERCEL_OIDC_TOKEN` in builds.

```typescript
// In a Vercel function
const oidcToken = process.env.VERCEL_OIDC_TOKEN;

// Exchange for AWS credentials
const sts = new STSClient({});
const creds = await sts.send(new AssumeRoleWithWebIdentityCommand({
  RoleArn: 'arn:aws:iam::123456789:role/vercel-role',
  WebIdentityToken: oidcToken,
  RoleSessionName: 'vercel-build'
}));
```

### Supported Providers

| Provider | Integration |
|----------|-------------|
| AWS | AssumeRoleWithWebIdentity |
| GCP | Workload Identity Federation |
| Azure | Federated Identity |
| Vault | JWT auth method |

### Local Development

Pull the OIDC token for local use:

```bash
vercel env pull
# Creates .env.local with VERCEL_OIDC_TOKEN (if configured)
```

### Benefits

- No long-lived credentials to rotate
- Automatic expiration (typically 1 hour)
- Audit trail via cloud provider
- Works with least-privilege IAM policies

---

## Local Development

### File Structure

```
.env                 # Shared defaults (can commit)
.env.local           # Local overrides (gitignore)
.env.development     # Development target
.env.production      # Never commit this
.dev.vars            # Wrangler local secrets (gitignore)
```

### .gitignore

```gitignore
# Always ignore
.env.local
.env.*.local
.dev.vars
.vercel
```

### Sync Pattern

```bash
# Pull Vercel env to local
vercel env pull .env.local

# Pull specific environment
vercel env pull .env.production --environment=production
```

### Order of Precedence (Next.js)

1. `.env.local` (highest)
2. `.env.development` or `.env.production`
3. `.env` (lowest)

---

## Security Checklist

- [ ] Never commit secrets to git
- [ ] Use `encrypted` type for Vercel env vars
- [ ] Use `wrangler secret put` not config for Worker secrets
- [ ] Prefer OIDC over long-lived credentials
- [ ] Rotate tokens regularly
- [ ] Audit access to Vercel/Cloudflare dashboards
- [ ] Use branch-scoped preview env vars for sensitive branches
