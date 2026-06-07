---
name: api-discovery
description: API endpoint discovery including OpenAPI/Swagger detection, hidden versioning, REST/GraphQL enumeration, and content negotiation
---

# API Discovery

## Methodology

### OpenAPI/Swagger Detection

```bash
# Common Swagger/OpenAPI paths
for path in swagger.json swagger/v1/swagger.json openapi.json api-docs api/docs swagger-ui.html \
  swagger-ui/ api/swagger api/swagger.json v1/api-docs v2/api-docs v3/api-docs .well-known/openapi \
  docs api/documentation redoc; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" "https://TARGET/$path")
  [ "$code" != "404" ] && echo "[$code] /$path"
done
```

### API Versioning Enumeration

```bash
# Test version prefixes
for v in v1 v2 v3 v4 api/v1 api/v2 api/v3; do
  curl -sk "https://TARGET/$v/" -H "Accept: application/json" -o /dev/null -w "[$v] %{http_code} %{size_download}\n"
done

# Test version headers
curl -sk "https://TARGET/api/users" -H "Accept-Version: 1.0"
curl -sk "https://TARGET/api/users" -H "X-API-Version: 2"
curl -sk "https://TARGET/api/users" -H "Api-Version: 2023-01-01"
```

### REST Endpoint Enumeration

```bash
# Common API patterns
for endpoint in users user/1 me profile accounts auth/login auth/register \
  config settings health status debug info version metrics admin; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" "https://TARGET/api/$endpoint" -H "Accept: application/json")
  [ "$code" != "404" ] && echo "[$code] /api/$endpoint"
done

# Test all HTTP methods on discovered endpoints
for method in GET POST PUT PATCH DELETE OPTIONS HEAD; do
  curl -sk -X $method "https://TARGET/api/ENDPOINT" -o /dev/null -w "[$method] %{http_code}\n"
done
```

### GraphQL Endpoint Detection

```bash
for ep in graphql graphiql gql query api/graphql api/gql; do
  curl -sk "https://TARGET/$ep" -X POST -H "Content-Type: application/json" \
    -d '{"query":"{__typename}"}' | grep -q "data" && echo "[GRAPHQL] /$ep"
done
```

## Coverage Gaps & Validation

- Combine passive spec sources before active probing: crawl HTML/JS for `fetch`/`axios`/`XMLHttpRequest` URLs, pull historical paths from Wayback (`waybackurls`, `gau`), and search public Postman/SwaggerHub/GitHub for leaked collections — a single `swagger.json` hit is not full coverage.
- Most-missed surfaces: GraphQL introspection (`{__schema{types{name}}}`), gRPC-Web and `/*.proto` reflection, WebSocket (`wss://`) endpoints, batch/RPC routes (`/api/batch`, `_bulk`), and mobile-only hosts (`api.`, `mobile.`, `gateway.`) absent from the web app.
- Don't trust the prefix: enumerate version skew (`v1` vs `v2-internal`, date-pinned `2023-01-01`) and content negotiation (`Accept: application/json` vs `xml` vs `+protobuf`) — deprecated versions often skip authz.
- Decode `OPTIONS` responses and `Allow`/CORS headers; an endpoint returning 401/403 still confirms existence, so map auth-required routes, not just 200s.
- Validate every candidate is live AND in scope: re-request 2-3x to rule out flapping/WAF rate-limits, diff response size/timing against a known-404 baseline, and resolve the host to confirm it sits inside authorized IP ranges before logging it.
- Treat soft-404s as noise: many APIs return 200 with `{"error":"not found"}` — gate findings on body content and schema, not status code alone.

## Pro Tips

1. Swagger/OpenAPI files reveal ALL API endpoints, parameters, and data models — always check
2. API version enumeration reveals deprecated versions with weaker security
3. Test `Accept: application/json` and `Accept: application/xml` — different content negotiation may expose different responses
4. Use Postman/Insomnia collections found in repos or docs for comprehensive endpoint lists
5. Check robots.txt and sitemap.xml for hidden API paths
