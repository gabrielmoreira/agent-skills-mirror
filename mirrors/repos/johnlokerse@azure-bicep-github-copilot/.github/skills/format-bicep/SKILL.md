---
name: format-bicep
description: Format Bicep code for readability and consistency.
---

# Format Bicep

This skill reformats Bicep code to enhance readability and maintainability by applying consistent styling, indentation, and organization.

## Guidelines

To format a Bicep file, follow these guidelines:

### Bicep structure

To avoid chaos keep a strict structure for Bicep files. The recommended structure is as follows:

```bicep
////////////
// Imports
////////////

////////////
// Metadata (optional)
////////////

////////////
// TargetScope (optional)
////////////

////////////
// Parameters
////////////

////////////
// Variables
////////////

////////////
// Existing resource references
////////////

////////////
// Resources / Modules
////////////

////////////
// Outputs
////////////

////////////
// User-Defined Types Types
////////////

////////////
// Functions
////////////
```

Do not add blank lines between section comment headers and the first definition in that section.

Correct:

```bicep
////////////
// Parameters
////////////
@description('The supported Azure location')
param location string
```

Wrong:

```bicep
////////////
// Parameters
////////////

@description('The supported Azure location')
param location string
```

### Property order on resource and modules

Resource definitions should follow a consistent property order:

```bicep
resource <name> '<type>@<apiVersion>' = {
  name: '<name>'
  location: '<location>'
  tags: '<tags>'
  <property>: '<otherProperties>' // other resource-specific properties in alphabetical order
  dependsOn: [
    // dependencies
  ] // optional, prefer implicit dependencies
  properties: {
    // resource-specific properties
  }
}
```

Module defitinitions should follow a consistent property order. If the module has the `name` property, it should be removed since the Azure Resource Manager handles the deployment name.

```bicep
module <name> '<path>' = {
  scope: '<scope>' // optional
  identity: {
    // identity properties
  } // optional
  dependsOn: [
    // dependencies
  ] // optional, prefer implicit dependencies
  params: {
    // module parameters
  }
}
```

## Execution steps

When formatting a Bicep file, perform these steps in order:

1. **Analyze the current structure**
   - Identify existing sections (parameters, variables, resources, etc.)
   - Note any missing required sections

2. **Reorganize sections** according to the standard structure
   - Move items to their correct section
   - Add section comment headers if missing
   - Ensure to return feedback about any significant structural changes made. DO NOT REMOVE any code, only reorganize it.

3. **Apply property ordering**
   - Reorder resource/module properties as specified
   - Ensure decorators are in the correct order

4. **Run bicep format**

   - Run command: `bicep format <.bicep file>`

5. **Remove commented code**
   - Delete any commented-out code blocks
   - Retain comments that provide context or explanations

6. **Validate the result**
   - Ensure no syntax errors were introduced
   - Verify the file compiles successfully

Use the following command to compile and validate the Bicep file:

```bash
  bicep build <.bicep file> --stdout --no-restore
```

## Examples

### Before Formatting

```bicep
param location string='eastus'
var storageAccountName='mystorageaccount'
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-09-01'={
name:storageAccountName
location:location
properties:{
accessTier:'Hot'
}
sku:{name:'Standard_LRS'}
}
```

### After Formatting

```bicep
/*
Parameters
*/

@sys.description('The Azure region for resource deployment')
param location string = 'eastus'

/*
Variables
*/

var storageAccountName = 'mystorageaccount'

/*
Resources
*/

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
  }
}
```
