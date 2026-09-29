---
name: api-discovery
description: API endpoint discovery including OpenAPI/Swagger detection, GraphQL, versioned routes, and API surface mapping from multiple sources
---

# API Discovery

## When to Use
When the target shows API signals: JSON responses, `/api/` paths, JavaScript with API calls, or an OpenAPI/Swagger spec.

## Important
OpenAPI/Swagger files are ONE high-confidence discovery source — NOT the complete API surface. Specs can be stale, incomplete, filtered, version-specific, or a public subset only. Always merge spec data with runtime evidence (JavaScript, browser traffic, error messages).

## Methodology

### OpenAPI/Swagger Detection
```bash
for path in swagger.json swagger/v1/swagger.json openapi.json api-docs api/docs \
  swagger-ui.html api/swagger api/swagger.json v1/api-docs v2/api-docs v3/api-docs \
  .well-known/openapi docs api/documentation redoc; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" "https://TARGET/$path")
  [ "$code" != "404" ] && [ "$code" != "000" ] && echo "[$code] /$path"
done
```

### Spec Parsing (when found)
```bash
# Extract all paths and methods
cat tmp/openapi.json | jq -r '.paths | keys[]' > tmp/api_paths.txt

# Extract parameters per path
cat tmp/openapi.json | jq -r '.paths | to_entries[] | "\(.key): \(.value | keys | join(", "))"'

# Extract request body schemas
cat tmp/openapi.json | jq -r '.paths | to_entries[] | .value | to_entries[] | .value.requestBody.content["application/json"].schema.properties | keys' 2>/dev/null

# Resolve $ref chains
cat tmp/openapi.json | jq -r '.. | .["$ref"]? // empty' | sort -u
```

### GraphQL Discovery
```bash
# Common GraphQL endpoints
for path in graphql graphql/v1 api/graphql query; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" -X POST "https://TARGET/$path" \
    -H "Content-Type: application/json" -d '{"query":"{__typename}"}')
  [ "$code" = "200" ] && echo "[GRAPHQL] /$path"
done

# Introspection query (if endpoint found)
curl -sk -X POST https://TARGET/graphql -H "Content-Type: application/json" \
  -d '{"query":"{__schema{types{name fields{name}}}}"}' | jq -r '.data.__schema.types[] | select(.name | test("^[a-z]")) | .name as $t | .fields[] | "\($t).\(.name)"'
```

### API Versioning Enumeration
```bash
for v in v1 v2 v3 v4 api/v1 api/v2 api/v3; do
  curl -sk "https://TARGET/$v/" -H "Accept: application/json" -o /dev/null -w "[\($v)] %{http_code} %{size_download}\n"
done
```

### Alternate API Hosts
```bash
# Check JavaScript and configs for API hostnames that differ from the main target
cat tmp/js/*.js | grep -oP 'https?://[a-zA-Z0-9.-]+\.[a-z]+/api' | sort -u
```

### Error-Message API Discovery
```bash
# Send malformed requests — error messages often reveal route structure
curl -sk "https://TARGET/api/nonexistent" -H "Accept: application/json" | head -20
curl -sk -X POST "https://TARGET/api/users" -H "Content-Type: application/json" -d '{}' | head -20
```

## Stopping Criteria
- OpenAPI/Swagger checked at common paths
- GraphQL checked (if any API signals exist)
- API versioning probed
- JS-derived API references merged with spec data
- Error-message-derived routes recorded

## Common Misses
- API endpoints on alternate ports or subdomains
- Internal/admin APIs not in the public spec
- WebSocket and gRPC-Web endpoints
- JSON-RPC endpoints
- SOAP endpoints (check for ?wsdl on /api paths)
