---
type: skill
lifecycle: stable
inheritance: inheritable
name: azure-identity-msi
description: Time Saved: 1-2 hours debugging identity and RBAC
tier: standard
applyTo: '**/*azure*,**/*identity*,**/*msi*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Azure Managed Identity (MSI) Concepts

**Category**: Azure
**Time Saved**: 1-2 hours debugging identity and RBAC
**Battle-tested**: Yes — multiple Azure deployments

---

## The Problem

You're configuring RBAC for an Azure resource's managed identity. You see `principalId` in one place, `servicePrincipal` in another, and `objectId` elsewhere. Documentation uses these terms interchangeably and you're not sure if they're the same thing.

## Why It's Confusing

A Managed Identity **is** a Service Principal — they're the same object viewed from different angles:

- **Managed Identity**: The Azure resource perspective ("my VM has an identity")
- **Service Principal**: The Entra ID perspective ("there's an app registration")
- **Principal ID / Object ID**: The unique identifier (same value, different names)

## The Rule

**A Managed Identity IS a Service Principal in Entra ID. The `principalId` from the resource matches the Service Principal's Object ID in role assignments.**

## Identity Flow

```
Azure Resource (VM, Function, Container App)
        │
        ▼ creates
Managed Identity
        │
        ▼ which IS
Service Principal in Entra ID
        │
        ▼ gets assigned
RBAC Role on Target Resource
```

## Verification Pattern

When debugging RBAC issues, verify the chain:

### Step 1: Get principalId from Source Resource

```bash
# For a Container App
az containerapp show \
  --name myapp \
  --resource-group myrg \
  --query identity.principalId

# For a Function App
az functionapp show \
  --name myfunc \
  --resource-group myrg \
  --query identity.principalId

# For a VM
az vm show \
  --name myvm \
  --resource-group myrg \
  --query identity.principalId
```

### Step 2: Verify Service Principal Exists

```bash
# The principalId should match an SP's objectId
az ad sp show --id <principalId> --query objectId
```

### Step 3: Check Role Assignments on Target

```bash
# List role assignments on the target resource
az role assignment list \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{resource} \
  --query "[].{principal:principalId,role:roleDefinitionName}"
```

### Step 4: Confirm Match

```bash
# Principal from resource should appear in role assignments
# with the expected role (Reader, Contributor, etc.)
```

## Common RBAC Roles

| Role | When to Use |
|------|-------------|
| Reader | Read-only access to resources |
| Contributor | Full access except RBAC management |
| Owner | Full access including RBAC |
| Storage Blob Data Reader | Read blobs (not just management) |
| Key Vault Secrets User | Read secrets from Key Vault |

**Note**: Management roles (Reader, Contributor) don't grant data plane access. For blob storage, you need "Storage Blob Data *" roles.

## Assignment Script

```bash
# Assign role to managed identity
PRINCIPAL_ID=$(az containerapp show \
  --name myapp \
  --resource-group myrg \
  --query identity.principalId -o tsv)

az role assignment create \
  --assignee-object-id $PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account}
```

## System vs User Assigned

| Type | Creation | Lifecycle | Use Case |
|------|----------|-----------|----------|
| System-assigned | With resource | Deleted with resource | Single-resource identity |
| User-assigned | Separately | Independent | Shared across resources |

```bash
# Enable system-assigned identity
az containerapp identity assign \
  --name myapp \
  --resource-group myrg \
  --system-assigned

# Create user-assigned identity
az identity create \
  --name myidentity \
  --resource-group myrg

# Assign user-assigned to resource
az containerapp identity assign \
  --name myapp \
  --resource-group myrg \
  --user-assigned myidentity
```

## Verification Checklist

- [ ] Resource has managed identity enabled
- [ ] principalId is populated (not null)
- [ ] Service Principal exists in Entra ID
- [ ] Role assignment exists on target resource
- [ ] Correct role (data plane vs management plane)
- [ ] Role assigned at correct scope

## Common Symptoms

- "Authorization failed" after enabling managed identity
- Role assignment exists but access denied
- "Principal does not exist" in role assignment
- Works with Contributor, fails with custom role

## Related Skills

- `azure-subscription-context` — Subscription issues
- `azure-swa-gotchas` — SWA-specific identity issues
