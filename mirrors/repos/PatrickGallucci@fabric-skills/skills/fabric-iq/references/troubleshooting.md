# Fabric IQ remediate Guide

## Table of Contents

- [Ontology Item Creation](#ontology-item-creation)
- [Ontology Generated from Semantic Model](#ontology-generated-from-semantic-model)
- [Data Binding Issues](#data-binding-issues)
- [Relationship Type Issues](#relationship-type-issues)
- [Preview Experience and Graph](#preview-experience-and-graph)
- [Data Agent Integration](#data-agent-integration)
- [REST API Issues](#rest-api-issues)

---

## Ontology Item Creation

| Issue | Cause | Solution |
|-------|-------|----------|
| "Unable to create the Ontology (preview) item" | Required tenant settings not enabled | Enable **Ontology item (preview)** AND **Graph (preview)** in admin portal tenant settings |
| Error on opening newly created ontology | Graph setting missing | Enable **User can create Graph (preview)** tenant setting |
| Ontology creation fails silently | Workspace on trial SKU | Switch to paid F2+ or P1+ capacity |

---

## Ontology Generated from Semantic Model

| Issue | Cause | Solution |
|-------|-------|----------|
| Ontology fails to generate | Tenant settings not enabled, or workspace is "My workspace" | Enable required settings; move semantic model to a regular workspace |
| Created but no entity types | Tables hidden in semantic model, or no relationships defined | Unhide tables; define relationships in the semantic model |
| Created but no data bindings | Semantic model in Import mode | Import mode doesn't support auto data binding; use Direct Lake or DirectQuery, or bind manually |
| No data bindings with Direct Lake | Backing lakehouse workspace has inbound public access disabled | Enable inbound public access on the lakehouse workspace |
| Decimal properties return null | Fabric Graph doesn't support Decimal type | Recreate the property as **Double** type in ontology and rebind to source data |

---

## Data Binding Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Data source not available | Table is unmanaged, has OneLake security, or has column mapping | Use managed tables without OneLake security or column mapping |
| Source columns unavailable for property binding | Column data type doesn't match declared property type | Check Available vs Unavailable grouping; change property type or use a compatible column |
| Time series data not appearing | Data not in columnar format | Restructure data so each row is a timestamped observation with property value columns |
| Stale data in ontology | Upstream data source updated but ontology not refreshed | Manually refresh the graph model in the preview experience |

---

## Relationship Type Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Cannot create relationship | Source and target entity types are the same | Source and target entity types must be distinct |
| Relationship has no instances | Source columns don't match entity type keys | Verify the source column selections match the key properties defined on each entity type |
| Relationship graph looks sparse | Key mismatches between binding tables | Double-check entity type keys match the relationship source data columns |

---

## Preview Experience and Graph

| Issue | Cause | Solution |
|-------|-------|----------|
| Preview experience won't load | Graph tenant setting not enabled | Enable **User can create Graph (preview)** |
| Graph shows no data | Data bindings incomplete or keys misconfigured | Verify bindings and entity type keys |
| Query returns no results | Default query scope too narrow | Modify query builder filters or components; try broader criteria |
| Graph not reflecting recent data | Manual refresh required | Select the **Refresh** option in the preview experience |

---

## Data Agent Integration

| Issue | Cause | Solution |
|-------|-------|----------|
| Can't find data agent item type | Tenant setting not enabled | Enable **Users can create and share Data agent item types (preview)** |
| Data agent can't be created | Missing tenant settings | Enable all data agent and Copilot/OpenAI settings |
| `403 Forbidden - Disallowed` | Copilot/Azure OpenAI settings not enabled | Enable all three Azure OpenAI tenant settings |
| First queries fail | Agent still initializing | Wait a few minutes after creation, then retry |
| Aggregation queries return wrong results | Known issue with GQL aggregation | Add instruction `Support group by in GQL` to agent instructions |
| Vague or generic results | Ontology not added as source; entity names too generic | Verify ontology is a knowledge source; use meaningful entity and relationship names |

---

## REST API Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Token expired or wrong audience | Get a fresh token with `Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com"` |
| 403 Forbidden | Insufficient workspace permissions | Ensure Admin or Member role on the workspace |
| Item type not supported | Using wrong type string | Use `Ontology` as the item type |
| Create with definition fails | Payload format incorrect | Ontology supports create with payload/definition — verify the JSON schema |

---

## General Diagnostics

### Verify Tenant Settings

```powershell
# Check if you can list ontology items (indicates basic access works)
$token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token
$headers = @{ "Authorization" = "Bearer $token" }
$workspaceId = "your-workspace-id"
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items?type=Ontology"

try {
    $result = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
    Write-Host "SUCCESS: Found $($result.value.Count) ontology items" -ForegroundColor Green
}
catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
```

### Validate Data Source Compatibility

```powershell
# Check if a lakehouse table is accessible for ontology binding
$lhUri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items?type=Lakehouse"
$lakehouses = Invoke-RestMethod -Uri $lhUri -Method Get -Headers $headers
$lakehouses.value | Format-Table displayName, id
```

### Submit Feedback

If you encounter issues not covered here, submit suggestions to [Fabric Ideas](https://community.fabric.microsoft.com/t5/Fabric-Ideas/idb-p/fbc_ideas) using the label **IQ | Ontology**.
