---
name: currency-audit
description: Comprehensive brain file review — external freshness, internal consistency, semantic accuracy — stamp only after full assessment
lastReviewed: 2026-05-26
---

# Currency Audit

> Full assessment: external freshness + internal consistency + semantic accuracy. Stamp only when all pass.

brain-qa.cjs checks the **date** mechanically (the `lastReviewed` field). This skill defines the **full review** that earns that date. A re-stamp means both "content matches external reality" AND "content is internally consistent."

---

## Critical Thinking Discipline

Every audit item must pass through critical thinking — not just mechanical verification. Apply these disciplines throughout:

| Discipline | Application to Currency Audit |
|---|---|
| **Alternative hypotheses** | "This API exists" isn't enough — is the *usage* correct? Could the documented pattern be outdated even if the API isn't? |
| **Missing data** | What's NOT in the file that should be? Missing caveats, undocumented prerequisites, absent error handling? |
| **Evidence quality** | Is the file's advice based on official docs, or a single blog post from 2021? |
| **Self-report skepticism** | "Best practice" claims — verified against what source? "Works on current versions" — actually tested? |
| **Bias detection** | Anchoring on the file's current content. Challenge: would you write this the same way from scratch today? |
| **Falsifiability** | What would prove this advice wrong? If nothing could, the claim may be unfalsifiable hand-waving |
| **Materiality gate** | If this item were stale, would it cause real harm? Prioritize fixes that affect decisions over cosmetic accuracy |

**The key question at every checklist item**: "Am I verifying this is correct, or am I assuming it's correct because it looks plausible?"

---

## When to Use

- brain-qa shows files with expired or missing `lastReviewed` dates
- Before a release that ships brain files to heirs
- On a scheduled cadence (target: full audit every 90 days)
- After a major external change (new API version, deprecated pattern, VS Code update)

---

## Quick Reference

| Step | Action | Outcome |
|------|--------|---------|
| **Triage** | Run `node scripts/brain-qa.cjs`, read the stale-file output | Ordered work list |
| **Research** | Check latest docs, changelogs, releases for the file's domain | Delta list |
| **Compare** | Diff current content against latest practices | Stale advice identified |
| **Audit** | Check terminology, cross-references, claims, process logic | Internal consistency verified |
| **Update** | Fix stale content, wrong terms, broken references, contradictions | Full assessment complete |
| **Stamp** | Set `lastReviewed: YYYY-MM-DD` to today in frontmatter | Pass restored |
| **Verify** | Re-run brain-qa, confirm file passes | Clean output |

---

## Audit Process

### 1. Triage

Run brain-qa and read the stale-file output:

```bash
node scripts/brain-qa.cjs
```

brain-qa surfaces files whose `lastReviewed` exceeds the 180/365-day thresholds (warn/fail). Work the failures first, then the warnings, oldest first.

**Batch size**: 10-15 files per session. Larger batches cause quality drift.

### 2. Per-File Review Checklist

For each file, work through this checklist:

#### Frontmatter Check

- [ ] `lastReviewed` field exists and is a valid `YYYY-MM-DD` date
- [ ] `description` accurately reflects current content (not stale summary)
- [ ] For instructions: `applyTo` patterns still match the intended activation scope
- [ ] No dropped legacy fields present (`type`, `application`, `tier`, `currency`, `inheritance`, `lifecycle`) — see `scripts/brain-qa.cjs` for the canonical drop list

#### Content Freshness Check

- [ ] **API references**: Do referenced APIs still exist? Check for deprecations, renamed methods, new parameters
- [ ] **Version numbers**: Are pinned versions still current? (Node.js, VS Code API, Azure SDKs, etc.)
- [ ] **URL links**: Do referenced URLs still resolve? Are they the canonical location?
- [ ] **Best practices**: Has the community consensus changed? Check official docs, changelogs
- [ ] **Tool availability**: Are referenced CLI tools, extensions, or services still available?
- [ ] **Code examples**: Do code snippets still compile/run against current versions?

#### Semantic Consistency Check

- [ ] **Terminology**: File uses current terms, not deprecated synonyms (e.g., "skills" not "DK files", "skills/" not "domain-knowledge/")
- [ ] **Claims match reality**: Do documented features, commands, or capabilities actually exist in code?
- [ ] **Cross-references**: Links to other skills, agents, instructions, or files are correct and targets exist
- [ ] **No contradictions**: File doesn't conflict with related files covering the same topic
- [ ] **Process logic**: If the file documents a workflow, each step's prerequisites exist and outputs are real
- [ ] **Architecture alignment**: Any structural claims (counts, relationships, directory layouts) match current state

#### Structural Check

- [ ] **No token waste**: Remove Mermaid diagrams in non-teaching skills, redundant examples, excessive prose
- [ ] **Progressive disclosure**: Most important info first, advanced topics later
- [ ] **Actionable content**: Every section helps the LLM produce better output

### 3. Update and Stamp

**Stamp only after ALL checklist sections pass** — frontmatter, freshness, semantic consistency, and structural. A partial review does not earn a date stamp.

1. Make all content fixes (freshness + semantic + structural)
2. Update `lastReviewed: YYYY-MM-DD` in frontmatter to today's date
3. If the file's `description` changed meaning, update it

### 4. Verify

Re-run brain-qa to confirm the file now passes:

```bash
node scripts/brain-qa.cjs --stdout | grep "filename"
# PowerShell: node scripts/brain-qa.cjs --stdout | Select-String "filename"
```

---

## Type-Specific Guidance

### Skills

| Check | What to Verify |
|-------|---------------|
| **Domain accuracy** | Does the skill reflect current state of its domain? |
| **Trifecta link** | If workflow skill, does matching `.instructions.md` exist and align? |
| **Reference files** | Are `references/` or `scripts/` subdirectories still accurate? |
| **Examples** | Do code examples work with current tool versions? |

### Instructions

| Check | What to Verify |
|-------|---------------|
| **Routing accuracy** | Does `applyTo` glob match when this instruction should load? |
| **Skill reference** | If instruction references a skill, is the skill still current? |
| **Rule validity** | Are the rules still correct given current tooling? |

### Agents

| Check | What to Verify |
|-------|---------------|
| **Model availability** | Is the specified model still available and appropriate? |
| **Tool references** | Do referenced tools still exist in the extension? |
| **Handoff targets** | Do handoff agent names match actual agent files? |

### Prompts

| Check | What to Verify |
|-------|---------------|
| **Agent reference** | Does the `agent` field point to an existing agent? |
| **Workflow steps** | Are the prompted steps still valid for current tools? |

### Muscles

| Check | What to Verify |
|-------|---------------|
| **Runtime compatibility** | Does the script run without errors on current Node.js? |
| **Dependencies** | Are `@requires` dependencies still available? |
| **Output format** | Does the output match what consumers expect? |
| **Dead code** | Variables computed but never stored/used? Branches that can never match? Fields extracted but never displayed? |

---

## Batch Audit Workflow

For auditing many files efficiently:

1. **Sort by category**: Group files by domain (Azure, VS Code, testing, etc.) so research carries across files
2. **Research once per domain**: Check the domain's latest changelog/release notes once, apply to all files in that domain
3. **Parallel reads**: Read 5-6 files at once, note which need changes, then edit in sequence
4. **Stamp in bulk**: After verifying all changes, stamp dates. Use brain-qa to confirm all pass

---

## Common Findings

| Finding | Fix |
|---------|-----|
| Deprecated API method | Replace with current equivalent, cite migration guide |
| Stale version pin | Update to current stable version |
| Dead URL | Find new canonical URL or remove reference |
| Outdated best practice | Revise to current recommendation with rationale |
| Redundant Mermaid diagram | Replace with concise prose description |
| Missing `lastReviewed` field | Add field with today's date after completing review |
| Legacy frontmatter field (`tier`, `currency`, `type`, `application`, `inheritance`, `lifecycle`) | Drop it; see `scripts/cleanup-frontmatter.cjs` for the canonical drop list |

---

## Stale File Decision Table (AC2)

When a file's currency stamp is expired or missing, decide before acting:

| Condition | Content Changed? | Action | Stamp? |
|---|---|---|---|
| Stamp expired, content still accurate | No | Re-stamp unchanged | Yes — review confirmed validity |
| Stamp expired, minor drift (terminology, links) | Yes — minor | Edit then re-stamp | Yes — after fixes land |
| Stamp expired, material staleness (deprecated APIs, wrong patterns) | Yes — major | Full rewrite of stale sections, then stamp | Yes — after full review |
| Stamp missing, file is active and current | N/A | Add stamp with today's date | Yes — review confirms currency |
| Stamp expired, file covers a dead domain (sunset API, retired tool) | N/A | Add a `## Deprecated` section + `docs/deprecations.md` row + `supersededBy` link if a successor exists | No — deprecated files don't get stamped |
| Stamp expired, file is historical record (plan, ADR, postmortem) | N/A | Re-stamp with long `reviewEvery` (or exempt via doc-hygiene convention) | Yes — stamp means "confirmed intentionally historical" |
| Stamp expired, file documents an upstream-dependent capability (SDK, MCP server, external API) | Check upstream | Research latest upstream docs before deciding; record the pinned upstream version in the file body | Only after upstream verification |

**Rule**: Never re-stamp without reviewing. A stamp is an attestation, not a date bump.

## Related Skills

- [doc-hygiene](../doc-hygiene/SKILL.md) — Anti-drift rules for living documents
- [skill-review](../skill-review/SKILL.md) — Five-gate audit (Gate 5 Currency & Coherence is the semantic companion to this skill's mechanical re-stamp)

## Would Revise If

Revisit this skill by **2026-08-26** (90 days) or sooner if any of the following fires:

- Files stamped through this audit are flagged later by self-audit or coherence sweeps as carrying stale content the audit should have caught — ≥3 occurrences in a quarter
- Re-stamps without content change recur ≥3 times for the same file in a quarter (rubber-stamp pattern)
- Decisions on equivalent Stale File Decision Table entries diverge across audits ≥2 times in a quarter (decision table too soft)
- brain-qa.cjs changes the `lastReviewed` threshold defaults (currently 180-day warn / 365-day fail) — re-tune the 90-day audit cadence accordingly

Track these in `docs/ledgers/curation-log.md` tagged `[CURRENCY-AUDIT-DRIFT]`.
