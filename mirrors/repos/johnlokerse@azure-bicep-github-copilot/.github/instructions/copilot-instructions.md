---
applyTo: "**/*.bicep"
---

# Bicep coding guidelines

This document provides guidelines for writing Bicep templates, including structure.

## Security

- No hardcoded secrets or sensitive information should be included in the templates. If a parameter or output is secret mark these with `@secure()`.

## Parameters and variables

- Avoid hardcoding values; use parameters and variables instead.
- Required parameters should not have a default value, nor have a nullable definition at the type. `param parName string?` is wrong!
- Parameters that are optional are not defined with a default value. Instead, a `?` is added to the datatype. For example, if you have a parameter that is optional, you can define it like this:

```bicep
@description('Optional parameter')
param optionalParameter string?
```

- Use variables for complex expressions to keep resource/module bodies readable.

## Built-in functions

If this error arises:
`Environment URLs should not be hardcoded. Use the environment() function to ensure compatibility across clouds. Found this disallowed host: "core.windows.net" bicep core linterno-hardcoded-env-urls`

Use the built-in function `environment()` to retrieve the current environment. #fetch https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-functions-deployment#environment

## User-defined types

Prefer strong typing over loosely typed arrays/objects.

```bicep
// arrays of primitives
param allowedSubnets string[]

// typed object
type Person = {
  name: string
  age: int
}
param owner Person
```

## Template structure

```bicep
////////////
// Imports (optional)
////////////

metadata name = '{name}'
metadata description = '{<= 100 chars: purpose of this template}'

////////////
// targetScope (optional)
////////////

////////////
// Parameters
////////////

////////////
// Variables
////////////

////////////
// Resources / Modules / Azure Verified Modules
////////////

////////////
// Outputs
////////////

////////////
// User-Defined Types
////////////

////////////
// User-Defined Functions (optional)
////////////
```

## Do not do this

Do not make every parameter optional and coalesce these in the variable:

```bicep
var effectiveLocation = location ?? 'westeurope'
var effectiveSkuName = skuName ?? 'Standard_LRS'
var effectiveKind = kind ?? 'StorageV2'
var effectiveAllowBlobPublicAccess = allowBlobPublicAccess ?? false
var effectiveSupportsHttpsTrafficOnly = supportsHttpsTrafficOnly ?? true
var effectivePublicNetworkAccess = publicNetworkAccess ?? 'Disabled'
var effectiveNetworkAcls = networkAcls ?? {
  bypass: 'AzureServices'
  defaultAction: 'Deny'
}
```