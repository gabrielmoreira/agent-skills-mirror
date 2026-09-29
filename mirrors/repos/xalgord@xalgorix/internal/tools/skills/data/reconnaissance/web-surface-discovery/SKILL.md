---
name: web-surface-discovery
description: Web crawling and attack-surface mapping including links, forms, redirects, sitemap, and browser-derived routes
---

# Web Surface Discovery

## When to Use
Map every reachable page, route, and form on the target before vulnerability testing. This is the primary source of the Endpoint Inventory.

## Methodology

### Sitemap and Robots
```bash
curl -sk https://TARGET/robots.txt -o tmp/robots.txt
curl -sk https://TARGET/sitemap.xml -o tmp/sitemap.xml
cat tmp/robots.txt | grep -iE "^(allow|disallow|sitemap)" | head -30
```

### Link Extraction (recursive)
```bash
# First pass: extract links from main pages
for page in / /login /about /contact; do
  curl -sk "https://TARGET$page" -A "Mozilla/5.0" | grep -oP 'href="[^"]*"' | grep -v '^href="#' >> tmp/all_links.txt
done
sort -u tmp/all_links.txt > tmp/unique_links.txt
```

### Form Discovery
```bash
curl -sk https://TARGET/ | grep -oP '<form[^>]*>' | while read form; do
  echo "$form" | grep -oP 'action="[^"]*"'
  echo "$form" | grep -oP 'method="[^"]*"'
  echo "$form" | grep -oP '<input[^>]*name="[^"]*"'
done
```

### Browser-Derived Routes (for SPAs)
Use `discover_client_routes` on the live root/login page. This browser-checks AngularJS-style dynamic prefixes automatically.

### Redirect Chain Mapping
```bash
curl -skI https://TARGET/ | grep -iE "^location|^HTTP/"
# Follow redirects manually to map the full chain
curl -skIL --max-redirs 10 https://TARGET/ -o /dev/null -w "%{url_effective}\n"
```

## Stopping Criteria
- All pages reachable from the root (1-2 hops) have been visited or their URLs recorded
- Forms identified with their actions, methods, and fields
- Redirect chains mapped
- SPA routes extracted (if applicable)

## Common Misses
- Pages only reachable via JavaScript navigation (SPA routes)
- API endpoints embedded in error messages
- Hidden form fields with default values
- Pagination endpoints (?page=2, ?offset=10)
- Alternate content types (RSS feeds, vCards, iCal)
