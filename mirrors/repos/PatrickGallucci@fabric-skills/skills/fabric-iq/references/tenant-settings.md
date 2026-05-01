# Fabric IQ Tenant Settings & Prerequisites

## Table of Contents

- [Required Tenant Settings](#required-tenant-settings)
- [Optional Tenant Settings](#optional-tenant-settings)
- [Capacity Requirements](#capacity-requirements)
- [Workspace Requirements](#workspace-requirements)
- [Data Requirements](#data-requirements)
- [Enabling Settings via Admin Portal](#enabling-settings-via-admin-portal)

---

## Required Tenant Settings

These settings **must** be enabled by a Fabric administrator in the admin portal under **Tenant settings**.

### 1. Enable Ontology Item (preview)

- **Setting path**: Admin portal > Tenant settings > Ontology
- **Required for**: Creating ontology items
- **Error if missing**: "Unable to create the Ontology (preview) item"

### 2. User Can Create Graph (preview)

- **Setting path**: Admin portal > Tenant settings > Graph
- **Required for**: Graph features associated with ontology (the ontology graph, preview experience)
- **Error if missing**: "Unable to create the Ontology (preview) item. Please try again or contact support."

> **Important**: Even though Graph is a separate item, the ontology item depends on it. Without this setting, you cannot open a newly created ontology item.

---

## Optional Tenant Settings

These settings are not required for basic ontology operations but are needed for specific features.

### 3. Data Agent Item Types (preview)

- **Setting**: "Users can create and share Data agent item types (preview)"
- **Required for**: Creating data agent items and connecting them to ontology sources
- **Error if missing**: Cannot find or create data agent item type

### 4. Copilot and Azure OpenAI Service (3 settings)

Required if using ontology with a Fabric data agent:

1. **Users can use Copilot and other features powered by Azure OpenAI**
2. **Data sent to Azure OpenAI can be processed outside your capacity's geographic region, compliance boundary, or national cloud instance**
3. **Data sent to Azure OpenAI can be stored outside your capacity's geographic region, compliance boundary, or national cloud instance**

- **Error if missing**: `403 Forbidden - Disallowed` when using data agent

---

## Capacity Requirements

| Requirement | Detail |
|-------------|--------|
| **Minimum SKU** | F2 or P1 (paid SKUs only) |
| **Trial SKU** | Not supported for Copilot features |
| **Region** | Capacity must be in a supported region ([Fabric region availability](https://learn.microsoft.com/en-us/fabric/admin/region-availability)) |

---

## Workspace Requirements

| Requirement | Detail |
|-------------|--------|
| **Fabric-enabled capacity** | Workspace must be assigned to a Fabric capacity |
| **Not "My workspace"** | Ontology generation from semantic models is not supported in "My workspace" |
| **Role** | Admin or Member role required to create items |

---

## Data Requirements

### For OneLake Data Binding

| Requirement | Detail |
|-------------|--------|
| **Data location** | OneLake (lakehouse tables) or eventhouse |
| **Table type** | Managed tables only |
| **OneLake security** | Must not have OneLake security enabled on the table |
| **Column mapping** | Must not have column mapping enabled |
| **ETL** | Data should be organized and through any necessary ETL |
| **Time series format** | Columnar format with timestamped rows |

### For Semantic Model Generation

| Requirement | Detail |
|-------------|--------|
| **Model mode** | Direct Lake or DirectQuery (Import mode not supported for data binding) |
| **Table visibility** | Tables must not be hidden |
| **Relationships** | Must be defined in the semantic model |
| **Inbound access** | Backing lakehouse workspace must not have inbound public access disabled (for Direct Lake) |

---

## Enabling Settings via Admin Portal

1. Sign in to **Microsoft Fabric** as a Fabric administrator
2. Navigate to **Settings** (gear icon) > **Admin portal**
3. Select **Tenant settings** from the left navigation
4. Search for each setting by name
5. Toggle each setting to **Enabled**
6. Optionally scope to specific security groups
7. Select **Apply**

### PowerShell Verification

Use the [Validate-FabricIQPrereqs.ps1](../scripts/Validate-FabricIQPrereqs.ps1) script to check prerequisites programmatically:

```powershell
./scripts/Validate-FabricIQPrereqs.ps1 -TenantId "your-tenant-id"
```

---

## Quick Checklist

- [ ] Ontology item (preview) enabled
- [ ] Graph (preview) enabled
- [ ] Workspace on F2+ or P1+ capacity
- [ ] Workspace is not "My workspace"
- [ ] Data in OneLake or eventhouse (managed tables, no security/column mapping)
- [ ] (Optional) Data agent item types enabled
- [ ] (Optional) Copilot and Azure OpenAI settings enabled (3 settings)
