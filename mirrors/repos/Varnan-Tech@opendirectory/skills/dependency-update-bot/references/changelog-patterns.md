# Changelog Patterns

How to fetch and parse changelogs for npm and pip packages. Fallback strategies when the primary source has no content.

---

## Source Priority

Try sources in this order. Stop at the first that returns usable content (more than 50 characters of actual release notes).

1. GitHub Releases API (best — structured, version-tagged)
2. Raw CHANGELOG.md from GitHub (good — often more detailed than release notes)
3. npm registry README (fallback — unstructured but usually mentions recent changes)
4. PyPI project description (last resort — often just the README)

---

## Source 1: GitHub Releases API

**When it works:** The package has a GitHub repo AND publishes versioned releases with release notes.

**How to find the repo URL:**

For npm packages:
```bash
curl -s "https://registry.npmjs.org/{PACKAGE}/latest" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
repo = d.get('repository', {})
url = repo.get('url', '') if isinstance(repo, dict) else str(repo)
# Clean up git+https:// or git:// prefixes
import re
url = re.sub(r'^git\+|^git:', '', url).replace('.git', '')
print(url.strip())
"
```

For PyPI packages:
```bash
curl -s "https://pypi.org/pypi/{PACKAGE}/json" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
info = d.get('info', {})
urls = info.get('project_urls') or {}
# Try multiple URL fields in priority order
for key in ['Source', 'Homepage', 'Repository', 'Code']:
    if key in urls and 'github.com' in urls[key]:
        print(urls[key])
        break
else:
    hp = info.get('home_page', '')
    print(hp if 'github.com' in hp else '')
"
```

**Parse owner/repo from URL:**
```bash
python3 -c "
import re, sys
url = sys.argv[1]
m = re.search(r'github\.com[/:]([^/\s]+)/([^/.\s]+)', url)
if m:
    print(m.group(1), m.group(2))
else:
    print('', '')
" "URL_HERE"
```

**Fetch releases:**
```bash
curl -s ${GITHUB_TOKEN:+-H "Authorization: Bearer $GITHUB_TOKEN"} \
  "https://api.github.com/repos/{OWNER}/{REPO}/releases?per_page=10" \
  | python3 -c "
import sys, json
releases = json.load(sys.stdin)
if isinstance(releases, dict) and 'message' in releases:
    print('ERROR:', releases['message'])
else:
    for r in releases[:5]:
        body = r.get('body') or ''
        if body.strip():
            print('TAG:', r.get('tag_name', ''))
            print(body[:1500])
            print('---')
"
```

**Version matching:** Tags may be prefixed (`v4.17.21`, `4.17.21`, `release-4.17.21`). Strip non-numeric prefixes before comparing to package versions.

---

## Source 2: Raw CHANGELOG.md from GitHub

**When it works:** The repo maintains a CHANGELOG.md but does not use GitHub Releases.

```bash
curl -s "https://raw.githubusercontent.com/{OWNER}/{REPO}/main/CHANGELOG.md" \
  | head -200
```

Also try `HEAD`, `master`, `trunk` if `main` returns 404.

**Extract the relevant section** (between current version header and previous version header):
```bash
python3 -c "
import sys, re
content = sys.stdin.read()
# Find section starting with target version
pattern = r'#+\s*\[?{TARGET_VERSION}\]?.*?(?=\n#+\s*\[?[0-9]|\Z)'
m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
if m:
    print(m.group(0)[:2000])
else:
    print('Version section not found in CHANGELOG.md')
"
```

---

## Source 3: npm Registry README (Fallback)

**When it works:** Package has no GitHub repo or does not use GitHub Releases, but includes a changelog in the README.

```bash
curl -s "https://registry.npmjs.org/{PACKAGE}" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
readme = d.get('readme', '')
if readme:
    # Look for changelog section
    import re
    m = re.search(r'#+\s*(changelog|changes|release notes|history).*', readme, re.IGNORECASE | re.DOTALL)
    if m:
        print(m.group(0)[:2000])
    else:
        # Just print the first 1500 chars of README
        print(readme[:1500])
else:
    print('No README found in registry')
"
```

---

## Source 4: PyPI Project Description (Last Resort)

```bash
curl -s "https://pypi.org/pypi/{PACKAGE}/json" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
desc = d.get('info', {}).get('description', '')
print(desc[:2000] if desc else 'No description found')
"
```

---

## Handling Missing Changelogs

If all four sources fail or return less than 50 characters of useful content:

- Record: "No changelog found for {package}"
- In the PR body, write: "No changelog available for {package}. Review the diff manually before merging."
- Do NOT skip the package from the PR — still include the version bump, just with no notes

---

## Identifying Breaking Changes

Gemini handles most of this, but these patterns in raw changelog text are strong signals to flag:

```
BREAKING CHANGE:
BREAKING:
[BREAKING]
!BREAKING
Removed support for
Dropped support for
No longer supports
Migration required
Deprecated in X, removed in Y
```

If a changelog contains any of these patterns for a patch or minor update, escalate that package's risk classification to major before PR creation.

---

## Rate Limits

| Source | Rate Limit | Auth |
|--------|-----------|------|
| GitHub API (unauthenticated) | 60 requests/hour | None |
| GitHub API (with GITHUB_TOKEN) | 5,000 requests/hour | Bearer token |
| npm registry | No documented limit (generous) | None |
| PyPI API | No documented limit | None |

For most projects (under 60 outdated packages), unauthenticated GitHub API is sufficient. Set GITHUB_TOKEN if you have more than 30-40 packages to scan (2 API calls per package).
