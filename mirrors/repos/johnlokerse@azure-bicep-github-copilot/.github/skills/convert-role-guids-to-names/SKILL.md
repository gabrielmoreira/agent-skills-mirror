---
name: convert-role-guids-to-names
description: Replaces hardcoded role definition GUIDs in Azure Bicep templates with the roleDefinitions() function and the role's display name. Use when asked to replace role GUIDs, use role names, or apply roleDefinitions() in Bicep files.
---

# Convert role definition GUIDs to roleDefinitions()

Replace hardcoded role definition GUIDs with `roleDefinitions('<Role Name>').id`.

## Workflow

1. **Find** every role definition GUID in `.bicep` and `.bicepparam` files. Check:
   - `roleDefinitionId` properties
   - `subscriptionResourceId()`, `tenantResourceId()` and `resourceId()` calls with `Microsoft.Authorization/roleDefinitions`
   - Hand-built `/providers/Microsoft.Authorization/roleDefinitions/<guid>` strings
   - Parameters, parameter files, variables and objects that map role names to GUIDs

2. **Identify** each GUID. Use a subagent running Claude Haiku 5.5 or GPT-6 Luna to look it up on https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles and return the exact built-in role name.

3. **Change** each reference to `roleDefinitions('<Role Name>').id`, using the exact display name from Microsoft Learn. When a parameter holds a role GUID, change it to hold the role name instead, and update its value in any `.bicepparam` file.

4. **Verify** by running `bicep build` on every changed `.bicep` file and `bicep build-params` on every changed `.bicepparam` file. Fix any errors.

5. **Report** when the changes are done. Give a table with file, line, GUID, role name and the new code, then list anything skipped and why.

## Rules

- Use `.id`, never `.roleDefinitionId`. The `roleDefinitionId` property expects the full resource ID.
- Do not change the `name` of existing role assignments. If a `guid()` call uses a role GUID, keep that GUID as a literal string, so redeploys don't fail with `RoleAssignmentExists`. Instead use the `roleDefinitions('<Role Name>').roleDefinitionId` property for the role assignment instead of a hardcoded guid.
- If a GUID is not on the built-in roles page, treat it as a possible custom role. Leave it unchanged and list it in the report.
- Ignore GUIDs that are not role definitions, such as principal IDs, tenant IDs and salts.
- Leave existing `roleDefinitions()` calls unchanged.
- Remove a GUID variable or object only when nothing references it any more.
- Change nothing else in the templates.

## Example

Before:

```bicep
roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')
```

After:

```bicep
roleDefinitionId: roleDefinitions('Reader').id
```
