# How to improve below-A skills

**Date:** 2026-08-14  
**Tree:** public `skills/<name>/SKILL.md` in this repo  
**Does not restamp** [quality-ranking.csv](quality-ranking.csv) July grades. Leftover wave refreshed **structural** columns only (487 rows).

Related: [QUALITY.md](QUALITY.md) · [VALUE_FRAMEWORK.md](VALUE_FRAMEWORK.md) · [WORKS_VERIFIED.md](WORKS_VERIFIED.md) · [INCLUSION.md](INCLUSION.md#works-bar-executability) · description rules in [`skills/create-skill`](../skills/create-skill/SKILL.md)

Rule for this work: read each unit, research live products from official docs, edit that file, verify that unit. Inventory scripts only. Do not author SKILL.md (or this playbook) from a shard rewriter.

## 1. Definition

**Below A** = `independent_grade` is **not** in `{A+, A}`. **A- is below A.**

Empty independent columns (33 v1 chairs with no July row) are ungraded, not a stamped 0. They are a later structural wave, not “below A” in the July sense.

## 2. Counts (verified on `docs/quality-ranking.csv`, leftover wave 487 rows)

| Band | n |
|------|--:|
| A+ | 61 |
| A | 236 |
| **A-** | **149** (below A) |
| **B or worse** | **10** (B+ 3, B- 1, C+ 3, C 1, D 2) |
| MISSING (v1, no July row) | 33 |

A- structural snapshot (pre-this-wave scan in QUALITY.md):

- **148** `has_when_not_for=no`
- **0** missing numbered procedure
- **22** `claimed_paths_ok=no`

“Below A” in the lock = the 149 A- plus the 10 B-or-worse. Do **not** stamp 149 A- descriptions from one template. This wave: playbook + the 10 + **3 gold A-** description/path examples.

## 3. How we know what’s wrong

Three layers (same as QUALITY.md). They are not interchangeable.

| Layer | What it is | What it is not |
|-------|------------|----------------|
| July independent `q1`–`q7` / `independent_grade` | 2026-07-17 private-library re-grade, joined by folder name | A 2026-08-14 reread of this public tree |
| Structural columns today | `has_when_not_for`, `has_numbered_procedure`, `claimed_paths_ok`, lean lines, YAML `name` vs folder | Works overlay; not a model score |
| Works overlay | N=24 Read sample; overlay 12 WORKS / 5 WEAK; 2 FAIL already cut; 5 extra WORKS in INCLUSION only | Untested ≠ fail |

Map to [VALUE_FRAMEWORK.md](VALUE_FRAMEWORK.md) via the QUALITY.md q-map:

| VALUE_FRAMEWORK | Independent subscore | Typical public failure |
|-----------------|----------------------|------------------------|
| Clarity | q4_trigger | YAML `description` missing when + not-for (148 A-) |
| Actionability | q3_procedure | Encyclopedia / zero execute path (July D on some chairs; public tree often already has numbered steps) |
| Completeness | q2_utility | Ghost `references/` / `scripts/` (`claimed_paths_ok=no`) |
| Uniqueness | q5_unique | Twin of a v1 chair; two owners for one capability |
| Demand | *(no 1:1)* | — |
| Safe-to-publish | q7_publish + q1_truth | Profile paths, invented CLI flags |
| Maint | q6_fresh | Stale July D on a rebuilt public body |

**HERO:** A- is mostly a **description gap** (when + not-for must be in YAML, not only the body). B/C/D are real procedure / truth / uniqueness holes — some rebuild, some drop, not all “polish.”

**Stale-grade rule:** Re-Read the public tree before trusting July. If scripts exist and run, say so. Example: July D on `svg-quality-audit` dinged missing scripts; this public folder now has `scripts/structure_scan.py` and `scripts/render_vision_judge.py`.

## 4. Playbook by failure mode

| Gap | How to improve |
|-----|----------------|
| YAML missing when/not-for (148 A-) | Expand `description` with trigger + not-for; third person; ≤1024 chars ([create-skill](../skills/create-skill/SKILL.md)). Re-run structural scan on **that file**. Do not stamp 149 from one sentence. |
| No numbered procedure | Add 5–12 numbered steps with real commands/APIs; anti-patterns. (A- cohort already has numbered procedure = yes.) |
| `claimed_paths_ok=no` | Copy missing `references/` `scripts/` **or** stop claiming them. Ghosts score 0. Root `reference.md` does not count. |
| q1 truth / hallucinated CLI | Verify vs official docs; delete invented flags; portable `~/` or env. Never invent Godot/Comfy/Ollama/Vercel APIs. |
| q5 uniqueness | One capability owner; point at the sibling that owns the rest. |
| q3 procedure=encyclopedia | Cut theory; keep execute path; depth in companions. Lean window is 40–700 lines. |
| LIBRARY_ONLY / machine paths | Public sanitize target: no profile paths; rewrite remaining machine-ops to env / `~/`. Never write a Windows user-profile path into public files. |
| DROP / MERGE_OR_DROP | Rebuild to the [works-bar](INCLUSION.md#works-bar-executability) **or** remove from public git (maintainer gate). Do not “wordsmith” a DROP into an A. Do not delete folders in an improve wave unless the lock says so. |
| Stale July D on a rebuilt v1 chair | Re-Read public tree; if scripts exist and run, document **stale-grade**. Do not blindly trust July. |

### Description recipe (A- → A **structural** lift)

Signals must be **in YAML `description`**, not only the body ([QUALITY.md](QUALITY.md) structural scan).

- **when-signal** (case-insensitive): `\bwhen\b` OR `use for` OR `trigger`
- **not-for-signal:** `not for` OR `do not use` OR `not a ` OR `never ` OR `not /`
- **Length:** ≥ 80 characters (stripped unfolded description) **and** both signals → `description_points=30`
- Third person. WHAT + WHEN + NOT-FOR. Max 1024 chars.
- Unique per skill. Gold 3 (`3d-image-to-model`, `bug-hunter`, `remotion-video`) stayed as calibration. Remaining A- YAML when+not-for is **done** (leftover **0**). A/A+ YAML without those signals is a **different** lock, not this leftover.

A description-only tweak raises **structural PQI**, not July `my_grade` / `independent_grade`. That would need a re-grade.

### Structural point table (re-extract edited files only)

Same rules as QUALITY.md:

| Bucket | Points | Rule |
|--------|-------:|------|
| description | 0 / 15 / 30 | 30 if len≥80 AND when-signal AND not-for-signal |
| procedure | 0 / 30 | ≥3 numbered step lines **or** ≥3 `Step N` / `N.` headings |
| claimed_paths | 0 / 20 | Any `references/` or `scripts/` mention; missing file → 0; none claimed → 20 |
| lean | 0 / 10 | SKILL.md lines 40–700 inclusive |
| name | 0 / 10 | YAML `name` == folder |

`structural_now` = sum (0–100).

## 5. Priority queue

1. **The 10 B-or-worse** (prior wave) — truth, uniqueness, ghosts, machine paths. Rebuild or recommend-cut. Not all polish.
2. **A- description wave** — gold 3 (`3d-image-to-model`, `bug-hunter`, `remotion-video`); remaining 145 unique YAML descriptions **done** this leftover wave.
3. **Ungraded v1** (33, no July row) — structural when+not-for and claimed paths **done**; do not invent independent scores.

## 6. What “A” means here

A public chair can be called **A-capable after improve** only if:

- independent grade is already A/A+, **or**
- after improve: `structural_now=100` **and** works=`WORKS` on a Read (INCLUSION works-bar).

This wave does **not** claim 149 (or even the 10) are a new independent A. Description fix ≠ re-grade. Honest report: structural PQI moved; July `independent_grade` unchanged.

Works-bar (stay if): unique owner **and** numbered procedure with real commands/files/APIs **and** not a stale encyclopedia/twin/flood **and** every claimed `references/` / `scripts/` path exists.

## 7. This wave

HEAD at start: `632b203`. No git commit/push. Folders not deleted.

### The 10 (B or worse)

| Skill | July | Disposition | What changed | structural_now | flags now |
|-------|------|-------------|--------------|----------------:|-----------|
| `godot-gdscript-patterns` | D DROP 53.3 | **recommend-cut → git rm leftover wave** | Twin of v1 `godot-gdscript-mastery`. Removed from public git this leftover wave. | 85 → 100 then **cut** | — |
| `svg-quality-audit` | D DROP 57.8 | **stale-grade** | July dinged missing scripts. Public **has** `scripts/structure_scan.py` + `scripts/render_vision_judge.py` + `references/`. `structure_scan.py` smoke: 1 SVG, exit 0. Description when+not-for only. Body already A-capable on Read. | 85 → **100** | when+not-for yes; claimed paths exist |
| `chrome-browser-automation` | C LIBRARY_ONLY 63.3 | **improved** | Zero profile paths. Portable Playwright `connectOverCDP("http://127.0.0.1:9222")` is the public default (`browser-connection` hub is **not** in this repo). Hub scripts optional via `$env:BROWSER_HUB`. | 100 → **100** | already 100; still yes/yes/yes |
| `illustration-direction` | C+ MERGE_OR_DROP 65.6 | **recommend-cut → git rm leftover wave** | Capability owned by `svg-creator` / `svg-quality-audit`. Removed from public git this leftover wave. | 55 → 100 then **cut** | — |
| `context-optimization` | C+ LIBRARY_ONLY 66.7 | **improved** | Cut encyclopedia 747 → 201 lines; execute path uses shipped `scripts/compaction.py` (demo exit 0). | 90 → **100** | lean now in 40–700 |
| `senior-frontend` | C+ MERGE_OR_DROP 67.8 | **improved** | July missing-scripts ding is stale — `scripts/` + `references/` exist. Description when+not-for. Unique owner: scaffold / generators / bundle analyzer. Points at `emil-design-eng` (motion) and `web-interface-guidelines` (Vercel a11y/CLS). | 85 → **100** | when+not-for yes |
| `comfyui-workflow-builder` | B- LIBRARY_ONLY 74.4 | **improved** | Stopped claiming unshipped `references/*.md`. Portable inventory: user-named files or `GET /object_info`; do not require unshipped `state/inventory.json`. Owner: API-format JSON vs `comfyui` runtime. Official format: [docs.comfy.org workflow API](https://docs.comfy.org/development/api-development/workflow-api-format). | 80 → **100** | claimed_paths yes (none claimed) |
| `game-godot` | B+ KEEP 81.1 | **improved** | Deleted invented `vercel deploy --csp` ([no such flag](https://vercel.com/docs/cli/deploy)). Deleted invented Godot `html/security/csp_enabled`. GdUnit CLI aligned to official `-a` / `-rd` / `--ignoreHeadlessMode` ([GdUnitTestCIRunner](https://github.com/godot-gdunit-labs/gdUnit4)). PlayGodot: `Godot.launch` + automation fork; no `GodotConfig`, no fictional `playgodot>=3.0.0`. Claimed paths retargeted to files on disk. Distinct from `godot-ui` / `godot-gdscript-mastery`. | 65 → **100** | when+not-for yes; paths yes |
| `ollama` | B+ KEEP 81.1 | **improved** | One capability: Ollama **Cloud** (`https://ollama.com/api/chat` and `/v1/chat/completions`), model `glm-5.2`, never `localhost:11434`, never print `OLLAMA_API_KEY`. Local GPU → `ollama-local-setup`. Optional helper via `$env:LOCALAPPDATA` only if the file exists. | 85 → **100** | when+not-for yes |
| `web-interface-guidelines` | B+ KEEP 81.1 | **improved** | Description when+not-for. Unique vs `senior-frontend` (scaffold/scripts) and `emil-design-eng` (motion taste). Execute path: eslint jsx-a11y + Lighthouse + keyboard/reduced-motion. | 85 → **100** | when+not-for yes |

### Gold A- (exactly 3; unique descriptions; no shared template)

| Skill | tag | Disposition | What changed | structural_now | when+not-for |
|-------|-----|-------------|--------------|----------------:|--------------|
| `3d-image-to-model` | svg-and-design | **improved** (description + ghosts) | Unique when+not-for. Stopped claiming unshipped `scripts/*.py` (“Save as scripts/…”). Still 798 lines → lean_points 0. | 55 → **90** | **yes** |
| `bug-hunter` | testing-qa | **improved** | Unique when+not-for. Stopped claiming `references/debug-patterns.md` / `regression-test-templates.md`. | 65 → **100** | **yes** |
| `remotion-video` | video | **improved** | Unique when+not-for. Stopped claiming unshipped `references/rendering-guide.md` etc.; point at remotion.dev. | 65 → **100** | **yes** |

### Leftover

**0.** This leftover wave closed:

- **145 A- YAML descriptions** (149 − 3 gold − 1 already-passing) — unique when+not-for; gold 3 unchanged as calibration.
- **29 ungraded v1** descriptions (4 already passed: `better`, `goal`, `grokimagine`, `localvideo`). `godot-ui` WORKS only needed YAML not-for.
- **claimed_paths_ok=no → 0** (live scan). Library copies almost never existed; claims rephrased or retargeted to files on disk (`shadcn` `rules/` copied from library).
- **Twins `git rm`:** `godot-gdscript-patterns`, `illustration-direction`. Inventory **489 → 487**.

**Keep hop (this pass):** the five July leftovers still in tree (`chrome-browser-automation`, `comfyui-workflow-builder`, `context-optimization`, `senior-frontend`, `svg-quality-audit`) were **kept**, not restamped. Works-bar pass / stale-grade. July `independent_grade` / `independent_score` / `independent_decision` **unchanged**. See [QUALITY.md](QUALITY.md) leftover section.

July `independent_grade` **unchanged**. Honest report: structural PQI / works-bar only; not a re-grade to A.

`3d-image-to-model` still over 700 lines (lean 0). `inspire-quote-effects` remains a short stub (lean 0).

**A/A+ YAML wave (2026-08-14, user “go for it”):** **273** A/A+ chairs that lacked YAML when+not-for now pass the same unique-description bar as gold (`bug-hunter` / `remotion-video`). Live scan: **487/487** have both signals. No exact-duplicate descriptions. July `independent_grade` still unchanged. Structural PQI moved (PQI ≥90: 352 → 434).

### This leftover wave (counts, not 146 essays)

| Item | n |
|------|--:|
| A- descriptions unique-rewritten | 145 |
| v1 descriptions unique-rewritten | 29 |
| Ghost-only path honesty (A/A+) | 58 |
| Twin folders removed | 2 |
| Remaining A-/v1 `has_when_not_for=no` | **0** |
| A/A+ descriptions unique-rewritten | 273 |
| Remaining A/A+ `has_when_not_for=no` | **0** |
| Remaining claimed missing paths | **0** |

### Verify notes (leftover wave)

- Live scan: A- when+not-for fail **0**; v1 fail **0**; ghosts **0**.
- Folder count = catalog rows = ranking rows = **487**.
- No Windows user-profile paths in public `skills/**`.
- Twins absent from git.
