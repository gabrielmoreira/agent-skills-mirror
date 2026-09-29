---
name: javascript-analysis
description: JavaScript and source map analysis for route extraction, secret detection, framework discovery, and attack-surface mapping
---

# JavaScript Analysis

## When to Use
When the target serves JavaScript (SPAs, React/Vue/Angular apps, any page with script tags). Skip when the target has no meaningful JS surface.

## Methodology

### Collect JavaScript Bundles
```bash
# Use scan-local tmp/ (never host /tmp)
mkdir -p tmp/js
# Extract JS URLs from the main page
curl -sk https://TARGET/ -o tmp/main_page.html
grep -oP 'src="[^"]*\.js[^"]*"' tmp/main_page.html | sed 's/src="//;s/"//' | sort -u > tmp/js_urls.txt

# Download each bundle
while read url; do
  fname=$(echo "$url" | grep -oP '[^/]+$')
  curl -sk "$url" --max-time 15 -o "tmp/js/$fname"
done < tmp/js_urls.txt
```

### Route Extraction (comprehensive)
```bash
# API paths (beyond just /api/)
cat tmp/js/*.js | grep -oP '["\x27](/[a-zA-Z0-9_/.-]+)["\x27]' | sort -u > tmp/js_routes.txt

# Relative routes (framework-specific)
cat tmp/js/*.js | grep -oP '["\x27]([a-z][a-z0-9_-]+(?:/[a-z][a-z0-9_-]*)+)["\x27]' | sort -u >> tmp/js_routes.txt

# Framework route tables
# React/Next.js: look for _next/data patterns, getStaticProps, getServerSideProps
cat tmp/js/*.js | grep -oP '["\x27]/_next/[^"\x27]+' | sort -u
# Vue: router definitions
cat tmp/js/*.js | grep -oP '(?:path|component):\s*["\x27][^"\x27]+' | sort -u
# Angular: route configs
cat tmp/js/*.js | grep -oP 'path:\s*["\x27][^"\x27]+' | sort -u

# GraphQL endpoints
cat tmp/js/*.js | grep -oiP 'graphql[^"\x27\s]*' | sort -u

# WebSocket endpoints
cat tmp/js/*.js | grep -oP 'wss?://[^"\x27\s]+|["\x27]/ws[^"\x27]*' | sort -u

# Dynamically loaded chunks (split chunks, lazy imports)
cat tmp/js/*.js | grep -oP '"[^"]*chunk[^"]*\.js"|"[0-9a-f]+\.[0-9a-f]+\.js"' | tr -d '"' | sort -u > tmp/js_chunks.txt
```

### Source Map Analysis
```bash
# Check for source maps
while read f; do
  curl -sk "${f}.map" --max-time 10 -o "tmp/js/$(basename $f).map" 2>/dev/null
done < tmp/js_urls.txt

# If source maps exist, they reveal original source code paths
for map in tmp/js/*.map; do
  [ -f "$map" ] && jq -r '.sources[]' "$map" 2>/dev/null | head -50
done
```

### Secret Detection (with validation)
```bash
# Candidate secrets (broad patterns)
cat tmp/js/*.js | grep -oiP '(?:api[_-]?key|secret|token|password|auth|bearer|aws[_-]?(?:access|secret)|firebase)["\s:=]+["\s]*[a-zA-Z0-9_\-]{20,}' > tmp/js_secret_candidates.txt

# CRITICAL: These are CANDIDATES, not confirmed secrets
# Validate each: is it a real credential or just a placeholder/config key?
# Common false positives: public config, constant strings, CSS class names
```

## Stopping Criteria
- All JS bundles from the main page downloaded and analyzed
- Routes, API endpoints, and WebSocket URLs extracted
- Source maps checked (if present)
- Secret candidates identified (with note that they need validation)

## Common Misses
- Dynamically loaded chunks (webpack/code splitting)
- Inline JavaScript in HTML (not just .js files)
- Service workers and web manifest
- Environment-specific configs (staging/dev URLs in production bundles)
- Polyfill-loaded libraries that might have different behavior

## Output
Save findings to the Discovery Manifest or Endpoint Inventory note.
