---
name: convert-loose-to-strong-type
description: Converts loosely typed Bicep parameters using object or array to strongly typed alternatives like string[], user-defined types, or resource-derived types. Use when user mentions type safety, weak typing, object parameters, array parameters, resourceInput, resourceOutput, or asks to improve parameter definitions.
---

# Converting to Strong Types

Replaces loose `object` and `array` parameter types with strong alternatives for compile-time validation and autocompletion.

## Conversion Workflow

1. **Identify loose types**
   - Search for `param <name> object` and `param <name> array` declarations.

2. **Analyze parameter usage**
   - Examine how the parameter is used in the template to determine expected structure.

3. **Choose conversion strategy**

| Pattern                           | Strategy                                     |
| --------------------------------- | -------------------------------------------- |
| Array of primitives               | `string[]`, `int[]`, `bool[]`                |
| Array with constrained values     | `('value1' \| 'value2')[]`                   |
| Object matching resource property | `resourceInput<'Type@Version'>.properties.X` |
| Custom object structure           | User-defined type with `type` keyword        |
| Array of objects                  | User-defined type with `[]` suffix           |

4. **Define types and update parameters**
   - Place type definitions above parameters.

5. **Validate**
   - Run command `bicep build <.bicep file> --stdout --no-restore` to verify syntax and type correctness.

## Quick Reference

### Simple Arrays

```bicep
// Before
param addresses array

// After
param addresses string[]
```

### Union Types (Constrained Values)

```bicep
param environments ('dev' | 'staging' | 'prod')[]
param skuName 'Standard_LRS' | 'Premium_LRS'
```

### User-Defined Types

```bicep
type subnetType = {
  name: string
  addressPrefix: string
  nsgId: string?  // Optional property
}

param subnets subnetType[]
```

## Type Best Practices

- Use `?` for optional properties: `description: string?`
- Use `@sealed()` to prevent extra properties at deployment
- Use `@description()` on types and properties
- Use constraints: `@minLength()`, `@maxLength()`, `@minValue()`, `@maxValue()`
- Compose complex types from simpler types

## MCP Tools

| Tool                                        | Purpose                             |
| ------------------------------------------- | ----------------------------------- |
| `Bicep:get_bicep_best_practices`            | Current best practices              |
| `Bicep:get_az_resource_type_schema`         | Schema for resource-derived types   |
| `Bicep:list_az_resource_types_for_provider` | Available types and API versions    |
| `Bicep:list_avm_metadata`                   | Metadata for Azure Verified Modules |

## Edge Cases

**Dynamic objects** (unknown keys): Use wildcard `{ *: string }`

**Mixed-type arrays**: Use union `(string | int | bool)[]`

**Optionality and backwards compatibility**: Use optional types `?` for new properties

## Resource-Derived Types

Use `resourceInput<>` and `resourceOutput<>` to derive types directly from Azure resource schemas. Prioritise this approach over custom user-defined types.

### Syntax

```bicep
resourceInput<'<resourceType>@<apiVersion>'>   // Writable properties
resourceOutput<'<resourceType>@<apiVersion>'>  // Readable properties (includes computed)
```

### When to Use

- Parameter must match resource property structure exactly
- Want to avoid maintaining custom types that mirror resource properties

## Examples

### Full Properties Block

```bicep
param storageAccountProps resourceInput<'Microsoft.Storage/storageAccounts@2023-01-01'>.properties = {
  accessTier: 'Hot'
  minimumTlsVersion: 'TLS1_2'
  allowBlobPublicAccess: false
  supportsHttpsTrafficOnly: true
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'mystorageacct'
  location: resourceGroup().location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: storageAccountProps
}
```

### Output Types

```bicep
output endpoints resourceOutput<'Microsoft.Storage/storageAccounts@2024-01-01'>.properties.primaryEndpoints
```

### Do not do this

Do not use a type definition for resource-derived types but define them directly in parameters or outputs.

```bicep
type managedRulesDefinitionType = resourceInput<'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2024-07-01'>.properties.managedRules
type customRulesType = resourceInput<'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2024-07-01'>.properties.customRules
type policySettingsType = resourceInput<'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2024-07-01'>.properties.policySettings
type wafPolicyTagsType = resourceInput<'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2024-07-01'>.tags
```
