# Routes Through the Salesforce MCP

Use this file when you reach the org through the Salesforce MCP. If you are in a terminal or IDE and can run the `sf` CLI, the CLI routes work as well.

Grounding itself is covered in `platform-metadata-grounding-get`. This file covers the routes the skill body sends to the CLI.

## How to Call

Use `dispatch_readonly` with `method: GET`. Pass the path as `url` and the SOQL as the `q` query parameter, not appended to the URL.

| Route | `url` | Query parameters |
|---|---|---|
| Standard SOQL | `/services/data/v66.0/query` | `q`: the SOQL |
| Tooling SOQL | `/services/data/v66.0/tooling/query` | `q`: the SOQL |
| Describe one object | `/services/data/v66.0/sobjects/<Type>/describe` | None |

The rows are in `body.records`. For a `COUNT()` query the number is in `body.totalSize` and `records` is empty. Every pattern in `scoped-soql.md` works through these paths.

## Route by Intent

| Intent | Through this server |
|---|---|
| Check names, types, or picklist values you know. Every field on one object. Data records | Standard SOQL. Use Tooling SOQL for `CustomField` and `ValidationRule`. |
| Full shape of one object, only when you need all of it | Describe one object. It is very large. |
| Every object in the org | Standard SOQL on `EntityDefinition`, for example `SELECT QualifiedApiName, Label FROM EntityDefinition WHERE QualifiedApiName LIKE '%__c'` for custom objects. Never call `/sobjects` for the full object list. It returned about 1.8 million characters in one test org. |
| Every member of a type, or a count | Tooling SOQL for Tooling types, for example `SELECT COUNT() FROM FlowDefinition`, or `ApexClass` and `ValidationRule`. To list flows with labels, use Standard SOQL on `FlowDefinitionView`. Other types cannot be listed through this server. Tell the user it needs the `sf` CLI in a terminal or IDE. |
| Source to edit or deploy | Not available through this server. Load `platform-metadata-retrieve` if it is available. Otherwise tell the user it needs the `sf` CLI in a terminal or IDE. |
| Compare orgs, find drift, or a whole-org overview | Not available through this server. Tell the user it needs the `sf` CLI. |

If a call fails with an authentication or session error, tell the user to reconnect the Salesforce MCP. If it fails as not found or not allowed, say so, and tell the user the lookup may need the `sf` CLI in a terminal or IDE.
