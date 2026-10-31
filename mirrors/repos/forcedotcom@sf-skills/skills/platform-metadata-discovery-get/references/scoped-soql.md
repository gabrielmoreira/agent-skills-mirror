# Scoped SOQL Patterns

Run each query through the Salesforce MCP with `dispatch_readonly`, as Standard or Tooling SOQL per the table. The paths are in `ref:platform-metadata-discovery-get/references/h360-routes`. In a terminal or IDE, `sf data query --json --query "<SOQL>"` works too. Add `--use-tooling-api` where the table says Tooling, and `--target-org <alias>` when the user named an org other than the default.

## Objects and Fields

| Need | Query | API |
|---|---|---|
| Does this object exist | `SELECT QualifiedApiName, Label FROM EntityDefinition WHERE QualifiedApiName = 'Loyalty_Transaction__c'` | Standard |
| Several objects at once | `SELECT QualifiedApiName, Label FROM EntityDefinition WHERE QualifiedApiName IN ('Menu__c', 'Promotion__c')` | Standard |
| Every field on one object | `SELECT QualifiedApiName, Label, DataType FROM EntityParticle WHERE EntityDefinition.QualifiedApiName = 'Contact'` | Standard |
| Custom fields only | Add `AND QualifiedApiName LIKE '%__c'` to the query above | Standard |
| Check specific fields | Add `AND QualifiedApiName IN ('Loyalty_Tier__c', 'Email')` | Standard |
| Picklist values | `SELECT Value, Label, IsDefaultValue, IsActive FROM PicklistValueInfo WHERE EntityParticle.EntityDefinition.QualifiedApiName = 'Contact' AND EntityParticle.QualifiedApiName = 'Loyalty_Tier__c'` | Standard |
| Record types on an object | `SELECT Name, DeveloperName, IsActive FROM RecordType WHERE SobjectType = 'Contact'` | Standard |

`EntityParticle` includes parts of compound fields, such as `MailingCity`. A full field list for Contact is about a tenth the size of a describe.

## Name and Label Fallback

Use these only when grounding is not available. Try two or three likely words.

| Need | Query | API |
|---|---|---|
| Objects by label | `SELECT QualifiedApiName, Label FROM EntityDefinition WHERE Label LIKE '%loyalty%'` | Standard |
| Fields on one object by label | `SELECT QualifiedApiName, Label, DataType FROM EntityParticle WHERE EntityDefinition.QualifiedApiName = 'Contact' AND Label LIKE '%tier%'` | Standard |
| Custom fields on every object by name | `SELECT DeveloperName, EntityDefinition.QualifiedApiName FROM CustomField WHERE DeveloperName LIKE '%tier%' AND NamespacePrefix = null` | Tooling |
| Flows by label | `SELECT ApiName, Label, ProcessType, IsActive FROM FlowDefinitionView WHERE Label LIKE '%order%'` | Standard |
| Permission sets by label | `SELECT Name, Label FROM PermissionSet WHERE IsOwnedByProfile = false AND Label LIKE '%loyalty%'` | Standard |

- `EntityDefinition`, `EntityParticle`, and `FieldDefinition` do not accept `OR`. The query fails with "Disjunctions not supported." Run one query per word.
- `CustomField` accepts `OR`. `DeveloperName` has no `__c`. Drop rows with no object name. They are Data Cloud fields.

## Access

| Need | Query | API |
|---|---|---|
| Who can read or edit a field | `SELECT Parent.Label, Parent.IsOwnedByProfile, Parent.Profile.Name, PermissionsRead, PermissionsEdit FROM FieldPermissions WHERE SobjectType = 'Contact' AND Field = 'Contact.Loyalty_Tier__c'` | Standard |
| Who can use an object | `SELECT Parent.Label, Parent.IsOwnedByProfile, Parent.Profile.Name, PermissionsRead, PermissionsCreate, PermissionsEdit, PermissionsDelete FROM ObjectPermissions WHERE SobjectType = 'Loyalty_Transaction__c'` | Standard |

When `Parent.IsOwnedByProfile` is true, the row belongs to a profile. Read the name from `Parent.Profile.Name`, because `Parent.Label` is an id for those rows. A field or object with no row for a profile or permission set has no access through it.

## Automation and Rules

| Need | Query | API |
|---|---|---|
| Triggers on an object | `SELECT Name, Status FROM ApexTrigger WHERE TableEnumOrId = 'Contact'` | Standard |
| Flows that run on an object | `SELECT ApiName, Label, TriggerType, IsActive FROM FlowDefinitionView WHERE TriggerObjectOrEventId = 'Contact'` | Standard |
| Validation rules on an object | `SELECT ValidationName, Active, ErrorMessage FROM ValidationRule WHERE EntityDefinition.QualifiedApiName = 'Contact'` | Tooling |
| Count of flows | `SELECT COUNT() FROM FlowDefinition` | Tooling |

These return names and status, not logic. To read what a flow, trigger, or rule does, retrieve its source.
