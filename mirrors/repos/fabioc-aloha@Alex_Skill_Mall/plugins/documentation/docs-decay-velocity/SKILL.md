---
type: skill
lifecycle: stable
inheritance: inheritable
name: docs-decay-velocity
description: Documentation decay rates by content type — hardcoded numbers and version pins rot fastest
tier: standard
applyTo: '**/*docs*,**/*decay*,**/*velocity*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Documentation Decay Velocity

**Category**: Documentation
**Time Saved**: 2+ hours per documentation audit
**Battle-tested**: Yes — observed across dozens of projects

---

## The Problem

Your README says "47 unit tests" but you now have 89. Your docs say "requires Node 16" but the project uses Node 22. Your architecture diagram shows a service that was removed 6 months ago.

## Why It Happens

Documentation decays at a rate proportional to how fast the code changes. Hardcoded numbers and specific versions rot fastest because they change with every release.

## The Decay Hierarchy

**Fastest decay (highest risk):**

| Content Type | Example | Decay Rate |
|--------------|---------|------------|
| Counts | "47 tests", "12 endpoints" | Every commit |
| Version numbers | "requires Node 16" | Every upgrade |
| File paths | "see `src/old/path.ts`" | Every refactor |
| Screenshots | UI screenshots | Every design change |

**Slower decay (lower risk):**

| Content Type | Example | Decay Rate |
|--------------|---------|------------|
| Architecture concepts | "uses microservices" | Major pivots |
| API patterns | "REST with JSON" | Rare |
| Installation steps | "npm install" | Package manager changes |

## The Rule

**Prefer runtime reads or dated stamps over hardcoded values.**

### Instead of Hardcoded Counts

```markdown
<!-- ❌ WRONG — hardcoded count -->
This project has 47 unit tests ensuring quality.

<!-- ✅ BETTER — script-generated or dated -->
This project has comprehensive test coverage.
See test results: `npm test`

<!-- ✅ ACCEPTABLE — dated stamp -->
As of April 2026, we have 89 unit tests.
```

### Instead of Version Requirements

```markdown
<!-- ❌ WRONG — hardcoded version -->
Requires Node.js 16 or higher.

<!-- ✅ BETTER — point to source -->
See `engines` in package.json for version requirements.

<!-- ✅ ACCEPTABLE — checked at runtime -->
Requires Node.js (see .nvmrc for specific version).
```

### Instead of Path References

```markdown
<!-- ❌ WRONG — hardcoded path -->
Configuration is in `src/config/settings.ts`

<!-- ✅ BETTER — pattern description -->
Configuration files are in `src/config/`

<!-- ✅ EVEN BETTER — searchable hint -->
Search for `CONFIG_` constants for all settings.
```

## Automation Strategies

### 1. Generate Docs from Source

```javascript
// Read real count from test output
const testCount = execSync('npm test -- --json')
  .toString()
  .match(/(\d+) tests/)[1];

// Inject into template
const readme = template.replace('{{TEST_COUNT}}', testCount);
```

### 2. CI/CD Doc Validation

```yaml
# .github/workflows/docs.yml
- name: Check doc freshness
  run: |
    # Fail if README mentions wrong version
    EXPECTED=$(node -p "require('./package.json').engines.node")
    grep -q "Node.js $EXPECTED" README.md
```

### 3. Dated Stamps for Manual Content

```markdown
## Performance Benchmarks

*Last updated: April 2026*

| Operation | Time |
|-----------|------|
| Startup | 1.2s |
| Query | 45ms |
```

## Red Flags to Grep For

```bash
# Find hardcoded numbers in docs
grep -rn '\b[0-9]\+ tests\b' docs/
grep -rn '\b[0-9]\+ endpoints\b' docs/
grep -rn 'Node\s*[0-9]\+' docs/

# Find likely-stale paths
grep -rn 'src/' docs/ | while read line; do
  path=$(echo "$line" | grep -oP 'src/[^\s`]+')
  [ ! -e "$path" ] && echo "STALE: $line"
done
```

## Content Categories

| Category | Strategy |
|----------|----------|
| Counts, stats | Generate from source or use dated stamps |
| Version requirements | Point to package.json/engines |
| File paths | Use patterns, not specific files |
| Screenshots | Date them, regenerate on UI changes |
| Architecture diagrams | Review quarterly |
| API docs | Generate from OpenAPI spec |

## Verification Checklist

- [ ] Search docs for hardcoded numbers
- [ ] Verify version requirements match package.json
- [ ] Check file path references still exist
- [ ] Add dated stamps to manually-maintained sections
- [ ] Set calendar reminder for quarterly doc review

## Related Skills

- `mermaid-mode-fragility` — Diagram maintenance
- `universal-audit-pattern` — Documentation audits
