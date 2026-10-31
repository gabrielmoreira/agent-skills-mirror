# What Each Route Calls

For engineers and reviewers. The skill names tools, not APIs, because the agent picks tools. Read from sf CLI 2.150.6 and jsforce source, and checked live on 2026-10-07.

| Route | API call |
|---|---|
| `sf sobject list` | REST `describeGlobal` (`GET /services/data/vXX.0/sobjects`), filtered to custom or all on the client |
| `sf sobject describe` | REST describe SObject (`GET /services/data/vXX.0/sobjects/<Type>/describe`). Tooling describe with `--use-tooling-api` |
| `sf org list metadata` | Metadata API `listMetadata` (SOAP) |
| `sf data query` | REST query resource (`GET /services/data/vXX.0/query`). Tooling query resource with `--use-tooling-api` |
| `sf project retrieve start` | Metadata API `retrieve` (SOAP) |
| Metadata grounding search | `GET /services/data/vXX.0/metadata-grounding/search` |
| Metadata grounding describe | `POST /services/data/vXX.0/metadata-grounding/schema` |
| Metadata grounding query | `POST /services/data/vXX.0/metadata-grounding/query` |

## Which Surface Reaches Which Call

| Call | `sf` CLI | Metadata Grounding MCP | Salesforce MCP |
|---|---|---|---|
| REST and Tooling query | Yes | No | Yes, `dispatch_readonly` |
| REST describe and object list | Yes | No | Yes, `dispatch_readonly` |
| Metadata API `listMetadata` and `retrieve` | Yes | No | No |
| Metadata grounding | No. The grounding paths are reachable only through an MCP server, so a direct REST call returns not found | Yes | Yes, after `describe` on the operation id |

The skills do not use the Enterprise API, the SOAP API with the org-specific WSDL. None of these tools call it.
