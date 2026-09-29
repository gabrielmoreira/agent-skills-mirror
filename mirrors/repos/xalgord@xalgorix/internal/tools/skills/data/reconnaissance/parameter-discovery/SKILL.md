---
name: parameter-discovery
description: Input parameter and attack surface discovery including query strings, forms, JSON fields, and hidden parameters
---

# Parameter Discovery

## When to Use
Build a complete input inventory before testing. Vulnerability coverage depends on knowing what parameters exist.

## Methodology

### Automated Discovery
```bash
arjun -u https://TARGET/endpoint --stable -o tmp/arjun_params.txt
```

### Manual Surface Extraction
```bash
# Extract from HTML forms
curl -sk https://TARGET/ | grep -oP '<form[^>]*>.*?</form>' | grep -oP 'name="[^"]*"'

# Extract from query strings in links
curl -sk https://TARGET/ | grep -oP 'href="[^"]*\?[^"]*"' | grep -oP '[?&][a-zA-Z_][a-zA-Z0-9_]*=' | sort -u

# Extract from JavaScript
cat tmp/bundle.js | grep -oP '["\x27](\?|&)[a-zA-Z_][a-zA-Z0-9_]*=' | sort -u
```

### From OpenAPI/HAR
```bash
# Parse parameters from OpenAPI spec
cat tmp/openapi.json | jq -r '.paths | to_entries[] | .value | getpath(["get","parameters"])? // [] | .[] | .name' | sort -u
```

### Parameter Pollution Probes
```bash
# Common hidden parameters worth probing
for param in debug admin internal api_key callback format output lang locale theme redirect next url; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" "https://TARGET/endpoint?${param}=test")
  [ "$code" != "404" ] && echo "[PARAM] $param ($code)"
done
```

## Stopping Criteria
- Forms, query strings, and JSON bodies from the main endpoints inventoried
- Automated parameter mining run on the primary target
- Record parameter names, types (query/body/path/header), and which endpoint they belong to

## Common Misses
- Hidden debug parameters (debug=1, admin=true)
- JSON body parameters not visible in query strings
- HTTP header parameters (X-Forwarded-For, X-Original-URL)
- Path parameters in RESTful APIs (/users/{id})
- Multipart file upload fields
- WebSocket message parameters
