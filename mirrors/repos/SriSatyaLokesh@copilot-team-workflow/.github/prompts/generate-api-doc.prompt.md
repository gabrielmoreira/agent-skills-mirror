---
description: 'Generate or update an API doc for the current file or endpoint'
agent: 'ask'
---
Generate or update the API documentation for this endpoint.

Read `${file}` and identify the HTTP endpoint(s) defined.

For each endpoint:
1. Determine the HTTP method and path
2. Find the request body shape from validation schemas
3. Find all possible response shapes
4. Identify business rules from service code
5. Find related tests
6. Identify middleware applied

Then either:
- **Create** a new doc at `docs/apis/[domain]/[endpoint-name].api.md` using [api-doc-template](../docs/templates/api-doc-template.md)
- **Update** the existing doc if it already exists

File being documented: `${file}`
