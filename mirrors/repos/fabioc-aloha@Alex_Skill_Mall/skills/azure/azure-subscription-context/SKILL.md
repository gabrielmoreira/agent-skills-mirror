---
type: skill
lifecycle: stable
inheritance: inheritable
name: azure-subscription-context
description: Time Saved: 30 minutes - 1 hour debugging
tier: standard
applyTo: '**/*azure*,**/*subscription*,**/*context*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Azure Subscription Context

**Category**: Azure
**Time Saved**: 30 minutes - 1 hour debugging
**Battle-tested**: Yes — affects nearly every Azure CLI session

---

## The Problem

Your Azure CLI command returns empty results, "resource not found", or creates resources in the wrong location. The command syntax is correct. The resource exists. You can see it in the portal.

## Why It Happens

Azure CLI commands run against the **currently active subscription**. If you have multiple subscriptions (personal, work, client projects), you're probably in the wrong one.

## The Rule

**Always verify subscription context with `az account show` before running commands.**

```bash
# FIRST command in any Azure session
az account show --query "{name:name, id:id}" -o table
```

## Quick Reference

### Check Current Context

```bash
# Show current subscription
az account show

# Just the name and ID
az account show --query "{name:name, id:id}" -o table
```

### List All Subscriptions

```bash
# See all subscriptions you have access to
az account list --query "[].{name:name, id:id, isDefault:isDefault}" -o table
```

### Switch Subscription

```bash
# By name
az account set --subscription "My Subscription Name"

# By ID (more reliable if names have spaces)
az account set --subscription "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

## Verification Pattern

Before running any destructive or expensive command:

```bash
# 1. Verify context
az account show --query name -o tsv
# Expected: "Production Subscription"

# 2. Then run your command
az group create --name mygroup --location eastus
```

## Per-Command Override

You can specify subscription per-command without changing default:

```bash
# Query specific subscription
az vm list --subscription "Dev Subscription"

# Create in specific subscription
az group create \
  --name mygroup \
  --location eastus \
  --subscription "Production Subscription"
```

## Common Symptoms

| Symptom | Likely Cause |
|---------|--------------|
| Empty results from `az resource list` | Wrong subscription |
| "Resource not found" | Resource is in different subscription |
| Resource created in wrong subscription | Default subscription is wrong |
| "You do not have access" | Subscription requires re-auth or different account |

## Scripting Best Practice

In automation scripts, always set subscription explicitly:

```bash
#!/bin/bash
set -e

# Fail fast if subscription doesn't exist
az account set --subscription "$SUBSCRIPTION_ID"

# Verify we're in the right place
CURRENT=$(az account show --query id -o tsv)
if [ "$CURRENT" != "$SUBSCRIPTION_ID" ]; then
  echo "Failed to set subscription"
  exit 1
fi

# Now run commands...
```

## Multiple Account Scenarios

### Different Tenants

```bash
# List accounts across tenants
az account list --all

# Login to specific tenant
az login --tenant "contoso.onmicrosoft.com"
```

### Service Principal

```bash
# When using service principal, subscription is usually set at login
az login --service-principal \
  --username $CLIENT_ID \
  --password $CLIENT_SECRET \
  --tenant $TENANT_ID

az account set --subscription $SUBSCRIPTION_ID
```

## Environment Variable

For CI/CD, use environment variable:

```bash
export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Then in scripts
az account set --subscription "$AZURE_SUBSCRIPTION_ID"
```

## Verification Checklist

- [ ] Run `az account show` at start of session
- [ ] Verify subscription name/ID matches expected
- [ ] Use `--subscription` flag in scripts
- [ ] Check subscription before destructive operations
- [ ] Document required subscription in project README

## Related Skills

- `azure-identity-msi` — Identity and RBAC issues
- `azure-swa-gotchas` — SWA-specific issues
