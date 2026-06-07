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

## Coverage Gaps & Validation

- A single `grep` pass misses most assets: enumerate every script source first — inline `<script>`, dynamically loaded chunks, `import()` splits, service workers, and Webpack `*.chunk.js`/`runtime.js` referenced only inside other bundles. Use `getJS`, `subjs`, or `katana -jc` to walk them recursively.
- Run layered regex, not one pattern: endpoints (`(?:"|')(/[a-zA-Z0-9_?&=/.-]+)(?:"|')`), absolute URLs (`https?://`), and secrets per provider — AWS `AKIA[0-9A-Z]{16}`, Google `AIza[0-9A-Za-z_\-]{35}`, Slack `xox[baprs]-`, JWTs `eyJ[A-Za-z0-9_-]+\.`, Stripe `sk_live_`, plus generic `api[_-]?key|secret|token`.
- Most-missed sources: `.js.map` source maps (reconstruct full app source with `sourcemapper`), `process.env`/`window.__CONFIG__`/`__NEXT_DATA__` config blobs, and framework route tables (React Router, Vue Router, Angular `routes`) that expose unlinked admin paths.
- Beautify before grepping — minified one-liners hide string concatenation (`"/api/"+"v2/"+"users"`); run `js-beautify` and also reconstruct split URLs manually.
- Validate before reporting: confirm extracted endpoints actually resolve (`httpx` the candidates), and verify secrets are LIVE and in-scope — test a key against its own provider's read-only API, never against third-party prod, and confirm the secret belongs to the target org, not a bundled SDK default.
- Diff bundles across deploys; new hashes in CI builds frequently leak fresh staging/internal endpoints before they are firewalled.

## Pro Tips

1. Source maps (`.js.map`) expose original unminified source code — always check
2. Search for `process.env`, `config`, `settings` objects — they reference secrets
3. Webpack chunk files (`1.chunk.js`, `vendor.js`) contain dependency code with known CVEs
4. React/Vue/Angular build artifacts contain route definitions revealing all endpoints
5. Look for commented-out debug code, TODO notes, and test credentials
