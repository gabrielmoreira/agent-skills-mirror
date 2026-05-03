---
type: skill
lifecycle: stable
inheritance: inheritable
name: "documentation-quality-assurance"
description: Systematic documentation audit, drift detection, preflight validation, and multi-pass quality pipelines
tier: standard
applyTo: '**/*documentation*,**/*quality*,**/*assurance*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Documentation Quality Assurance


> Prevent documentation rot through systematic audits, automated validation, and pipeline-enforced quality gates.

**Scope**: Inheritable skill. Covers drift detection, preflight validation, semantic accuracy, link integrity, 5-pass quality pipeline, staleness detection, and large-project organization.

**Complements**: The Documentarian agent uses this skill as its knowledge foundation. This skill is the "what" — the agent is the "who".

## Audit Priority: Semantics Over Syntax

**The most damaging documentation errors are semantic, not syntactic.** A wrong count is annoying. A false claim about functionality is dangerous.

### Audit Priority Hierarchy

| Priority | Issue Type | Impact | Example |
|----------|-----------|--------|---------|
| **P0 Critical** | Phantom features | Users try to use something that doesn't exist | "Entra ID SSO enabled" (code never implemented) |
| **P0 Critical** | False security claims | Trust violations, compliance failures | "All data encrypted" (encryption not implemented) |
| **P1 High** | Contradictions | User confusion, decision paralysis | README says X, CHANGELOG says Y |
| **P1 High** | Stale capability claims | Users miss real features or expect removed ones | Docs describe v3 API but v5 is current |
| **P2 Medium** | Broken cross-references | Navigation friction | Link to deleted file |
| **P3 Low** | Count drift | Credibility erosion | "109 skills" when there are 123 |
| **P3 Low** | Formatting issues | Aesthetic concerns | Bad table alignment |

### Semantic Audit Questions

Before any documentation audit, ask these questions **in order**:

1. **Does this feature actually exist?** — Check if documented functionality has corresponding implementation
2. **Is this claim still true?** — Validate assertions against current codebase state
3. **Are there contradictions?** — Cross-check related documents for conflicting information
4. **Is the version current?** — Compare documented versions against package.json/CHANGELOG
5. **Do examples work?** — Test code snippets against actual API/CLI behavior
6. **Do links resolve?** — Verify internal and external references (automate this)
7. **Are counts accurate?** — Check hardcoded numbers against canonical sources (automate this)

**Rule**: Questions 1-5 require human judgment. Questions 6-7 can be automated. Never spend human attention on automatable checks at the expense of semantic review.

### Common Semantic Bugs

| Bug Pattern | Detection Method | Fix |
|-------------|------------------|-----|
| **Phantom configuration** | Grep settings docs, verify in package.json | Remove undeclared settings or add to manifest |
| **Removed feature still documented** | Search for deleted code references | Remove or archive documentation |
| **Future feature documented as shipped** | Compare roadmap "planned" vs "shipped" markers | Move to correct section |
| **Version mismatch** | Regex for version patterns, compare to source of truth | Align all occurrences |
| **Model/API hallucination** | Verify external references against official docs | Correct or remove |

## Count Drift & Docs-as-Architecture (P3)

Count elimination rules, canonical sources, and docs-as-architecture principles are defined in [doc-hygiene](../doc-hygiene/SKILL.md). Apply those rules during Pass 5 (Lint) of the quality pipeline below.

## Document Header Pattern

### Comprehensive Metadata Headers

Operational documentation (regression checklists, deployment guides, QA procedures, release workflows) should include comprehensive headers that provide complete context at-a-glance.

**Minimal Header (4 lines)** — Insufficient:

```markdown
**Date**: 2026-02-14
**Status**: In Progress
**Purpose**: Verify v5.7.1 UI features
**Method**: Install and test
```

**Enhanced Header (10+ lines)** — Comprehensive:

```markdown
**Version**: 5.7.1
**Date**: 2026-02-14
**Status**: ⚠️ PENDING UI VERIFICATION — WebP avatars regenerated, awaiting restart + testing
**Testing Mode**: CP2 Contingency (Local Install)
**VSIX Size**: 9.44 MB (426 files)
**Key Changes**: Enterprise auth removed, WebP avatars optimized (144×144, 92% reduction)

**Purpose**: Local install verification of all v5.7.1 visual identity + UI features
**Method**: Install VSIX locally, restart VS Code, test in current workspace (CP2 contingency)
**Expected Outcome**: All 9 test sections pass → DoD criterion #4 complete → Ready to publish
```

### Header Field Guidelines

| Field | Use For | Example |
|-------|---------|---------|
| **Version** | Software version being documented | `5.7.1`, `v3.2.0-beta` |
| **Date** | ISO format date of creation/update | `2026-02-14` |
| **Status** | Current state with emoji for scanning | `⚠️ PENDING`, `✅ COMPLETE`, `🚧 IN PROGRESS` |
| **Testing Mode** | Validation approach or environment | `CP2 Contingency (Local Install)`, `F5 Extension Host`, `Production` |
| **Size/Scope** | Package size, file count, or metrics | `9.44 MB (426 files)`, `3 breaking changes`, `86 tests` |
| **Key Changes** | What's different in this version | `Enterprise auth removed, WebP optimized` |
| **Purpose** | Why this document exists | One sentence explaining the goal |
| **Method** | How the task will be performed | Step-by-step approach or workflow |
| **Expected Outcome** | Success criteria | What "done" looks like |

**Rule**: Include enough metadata that anyone can understand the document's context without reading the body. Operational docs reviewed during incidents need at-a-glance clarity.

## 6-Pass Quality Pipeline

Run these passes in sequence on any document suite:

| Pass | Focus | Catches | Type |
|------|-------|---------|------|
| 1. **Semantic** | Claims match reality, features exist | Phantom features, false claims, contradictions | 🧠 Human |
| 2. **Architecture** | Structural accuracy, diagrams current | Outdated visuals, wrong relationships | 🧠 Human |
| 3. **Brand** | Voice, tone, naming consistency | "Copilot" vs "the AI assistant", passive voice, jargon | 🧠 Human |
| 4. **Cross-Reference** | Link integrity, orphan files | Broken links, unreferenced docs | 🤖 Automatable |
| 5. **Lint** | Formatting, markdown validity, counts | Bad tables, stale numbers, code blocks | 🤖 Automatable |
| 6. **Consolidation** | Redundancy, overlap, merge candidates | Two docs covering same topic | 🧠 Human |

**Rule 1**: Don't merge passes — each pass has a single focus.
**Rule 2**: Complete all semantic passes (1-3) before mechanical passes (4-5). A perfectly formatted lie is still a lie.
**Rule 3**: Never allow automated tooling to "pass" a doc suite until human semantic review is complete.

## Preflight Validation

### Automated Checks

Run before every release or documentation change:

```powershell
# Example preflight validation script
function Test-DocQuality {
    $errors = @()
    
    # Check 1: All markdown links resolve
    Get-ChildItem -Recurse -Filter "*.md" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        $links = [regex]::Matches($content, '\[([^\]]+)\]\(([^)]+)\)')
        foreach ($link in $links) {
            $target = $link.Groups[2].Value
            if ($target -notmatch '^https?://' -and $target -notmatch '^#') {
                $resolved = Join-Path (Split-Path $_.FullName) $target
                if (-not (Test-Path $resolved)) {
                    $errors += "Broken link in $($_.Name): $target"
                }
            }
        }
    }
    
    # Check 2: No orphan files in docs folder
    # Check 3: Required sections present in each doc type
    # Check 4: Version strings match package.json
    
    return $errors
}
```

### Pre-Implementation Cross-Reference Sweep

Before adding any new file, check what already references the concept:

1. Grep for the concept name across all docs
2. Identify which files will need updating
3. Create the new file AND update all references in a single commit

**Anti-pattern**: Creating a new skill/agent and updating only one reference document. Every catalog, index, and count needs updating simultaneously.

## Link Integrity

### Link Audit Protocol

| Check | How | Frequency |
|-------|-----|-----------|
| Internal links resolve | Path validation against file system | Every commit |
| Anchor links work | `#heading` matches actual heading slugs | Every commit |
| External links alive | HTTP HEAD request (batch, rate-limited) | Weekly/monthly |
| Orphan file detection | Files not referenced by any other file | Every release |
| Circular references | Graph traversal (A→B→C→A) | Quarterly |

### Orphan Detection

```powershell
# Find markdown files not referenced by any other markdown file
$allMd = Get-ChildItem -Recurse -Filter "*.md" | Select-Object -ExpandProperty Name
$referenced = @()
Get-ChildItem -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $links = [regex]::Matches($content, '\]\(([^)]+\.md)')
    foreach ($link in $links) {
        $referenced += Split-Path $link.Groups[1].Value -Leaf
    }
}
$orphans = $allMd | Where-Object { $_ -notin $referenced }
```

## Staleness Detection

### Last Validated Dates

Add validation dates to critical documents:

```markdown
<!-- Last Validated: 2026-02-12 by Documentarian audit -->
```

### Staleness Tiers

| Tier | Threshold | Action |
|------|-----------|--------|
| Fresh | < 30 days since validation | None |
| Aging | 30-90 days | Flag for review |
| Stale | 90-180 days | Mandatory review before next release |
| Expired | > 180 days | Consider archival or major rewrite |

### Drift Detection During Maintenance

During regular maintenance cycles (meditation, dream, release prep):

1. Compare document claims against current reality
2. Flag any numeric drift (counts, versions, dates)
3. Check if referenced files still exist
4. Verify code examples still compile/execute
5. Update `Last Validated` timestamp after review

## Large Project Organization

### 15+ File Threshold

When a documentation folder exceeds 15 files, introduce numbered chapter folders:

```
docs/
├── 01-getting-started/
│   ├── installation.md
│   ├── quick-start.md
│   └── configuration.md
├── 02-architecture/
│   ├── overview.md
│   ├── components.md
│   └── data-flow.md
├── 03-operations/
│   ├── deployment.md
│   ├── monitoring.md
│   └── troubleshooting.md
└── README.md              # Index/TOC
```

**Rules**:

- Numbered prefixes ensure consistent ordering across all tools
- Each chapter folder has 3-7 files (not 1, not 20)
- Root `README.md` serves as table of contents with links to all sections
- Flat structure is fine for < 15 files

## Multi-Audience Documentation

### Audience Matrix

Every doc suite serves multiple readers:

| Audience | Needs | Format Preference |
|----------|-------|-------------------|
| **New users** | Quick start, screenshots, examples | Tutorial (step-by-step) |
| **Experienced users** | Reference, API, configuration | Reference (lookup) |
| **Contributors** | Architecture, conventions, review process | How-to guides |
| **AI agents** | Structured data, clear rules, no ambiguity | JSON > prose, tables > paragraphs |

**Rule**: Each document should declare its audience. A document trying to serve all audiences well serves none of them well.

### Ship First, Document After (Threshold)

| Document Type | When to Write |
|--------------|---------------|
| User-facing README | Before release |
| API reference | With the API code |
| Architecture docs | When design stabilizes |
| Internal notes | After shipping (retrospective) |

**Anti-pattern**: Blocking a release to write perfect docs. Ship with minimal docs (README + quick start), then iterate.

## Doc Audit Checklist

Run this 10-item checklist for any documentation review. **Semantic checks first.**

### Phase 1: Semantic Accuracy (🧠 Human Required)

| # | Check | Method |
|---|-------|--------|
| 1 | **Documented features exist** | For each feature claim, verify code/config exists |
| 2 | **No false capability claims** | Check "shipped" items against actual implementation |
| 3 | **No contradictions** | Cross-check related docs for conflicting statements |
| 4 | **Examples work** | Copy-paste test critical examples |

### Phase 2: Mechanical Accuracy (🤖 Automatable)

| # | Check | Method |
|---|-------|--------|
| 5 | All links resolve | Automated link checker |
| 6 | No hardcoded counts | Grep for common count patterns |
| 7 | Version strings current | Compare against package.json/CHANGELOG |
| 8 | File references exist | Verify every referenced file path |
| 9 | No orphan files | Cross-reference scan |
| 10 | Consistent terminology | Search for variant spellings/names |

**Rule**: Never mark a doc suite "clean" based only on Phase 2 passing. Phase 1 semantic checks are non-negotiable.

## TODO Files as Self-Models

A TODO list that contains completed work is worse than no TODO list. TODO.md is a **self-model** — when read at session start, it forms a mental picture of what exists and what doesn't. Completed tasks masquerading as pending create:

1. **Rediscovery tax** — work already done gets re-investigated
2. **False urgency** — energy directed at "building" something already built

### The Fix: Done Section First

```markdown
## Done — Audited [date]
- [x] secretScanner.ts ported to shared/utils/
- [x] All 15 extension.ts files implemented

## Next
- [ ] npm run compile — verify TypeScript
- [ ] F5 smoke test in Extension Development Host
```

**Maintenance Rule**: During every meditation or sprint transition, audit TODO.md first. Move completed items to Done. A stale self-model wastes more time than the audit costs.

## CHANGELOG Best Practices

| Practice | Why |
|----------|-----|
| One entry per user-visible change | Users scan, not read |
| Link to relevant docs/issues | Traceability |
| Group by: Added, Changed, Fixed, Removed | Consistent scan pattern |
| Version header matches `package.json` | No version drift |
| Date in ISO format (YYYY-MM-DD) | Unambiguous globally |
| Most recent version at top | Users want latest first |
