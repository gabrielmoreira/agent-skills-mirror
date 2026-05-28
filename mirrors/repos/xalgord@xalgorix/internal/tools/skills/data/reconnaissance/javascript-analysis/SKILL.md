---
name: javascript-analysis
description: JavaScript file analysis for API endpoint extraction, hardcoded secrets, DOM source-sink mapping, and source map exploitation
---

# JavaScript Analysis

## Methodology

### Endpoint and Secret Extraction

```bash
# Download all JS files
cat urls.txt | grep -E "\.js$" | sort -u > js_files.txt

# Extract API endpoints
cat js_files.txt | while read url; do
  curl -sk "$url" | grep -oP '["'\''](/api/[^"'\''\\s]+)' | sort -u
done

# Extract secrets and tokens
cat js_files.txt | while read url; do
  curl -sk "$url" | grep -oiP '(api[_-]?key|secret|token|password|auth|bearer|aws|firebase)["\s:=]+["\s]*[a-zA-Z0-9_\-\.]{10,}' | head -20
done

# Extract full URLs
cat js_files.txt | while read url; do
  curl -sk "$url" | grep -oP 'https?://[^"'\''\\s<>]+' | sort -u
done
```

### Source Map Analysis

```bash
# Find source maps
cat js_files.txt | while read url; do
  curl -sk "$url" | grep -oP '//# sourceMappingURL=\K.*' | while read map; do
    echo "[SOURCEMAP] $url -> $map"
    curl -sk "${url%/*}/$map" -o /tmp/sourcemap.json 2>/dev/null
    # Extract original source code
    python3 -c "import json;d=json.load(open('/tmp/sourcemap.json'));[print(s) for s in d.get('sources',[])]" 2>/dev/null
  done
done
```

### DOM Source/Sink Mapping

```bash
# Search for dangerous sinks in JS files
for sink in "innerHTML" "outerHTML" "document.write" "eval(" "setTimeout(" "setInterval(" "Function(" ".html(" ".append(" "v-html" "dangerouslySetInnerHTML" "bypassSecurity"; do
  grep -rn "$sink" ./js_files/ 2>/dev/null | head -5
done

# Search for sources
for source in "location.hash" "location.search" "document.referrer" "window.name" "postMessage" "localStorage" "sessionStorage"; do
  grep -rn "$source" ./js_files/ 2>/dev/null | head -5
done
```

## Pro Tips

1. Source maps (`.js.map`) expose original unminified source code — always check
2. Search for `process.env`, `config`, `settings` objects — they reference secrets
3. Webpack chunk files (`1.chunk.js`, `vendor.js`) contain dependency code with known CVEs
4. React/Vue/Angular build artifacts contain route definitions revealing all endpoints
5. Look for commented-out debug code, TODO notes, and test credentials
