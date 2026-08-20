# Quality ranking

**Date:** 2026-08-14  
**Generation SHA:** `9d3ca366946d8f4a7b68def0c2c7b9274f6b8958` (`9d3ca36`) — parent of this keep/front-door hop. Ranking refresh after leftover keep + N=24 sample overlay. July `independent_*` columns **unchanged**.  
**Inventory:** 496 sibling folders under `skills/<name>/SKILL.md`  
**Structural refresh:** leftover below-A, then A/A+ YAML when+not-for (273 unique descriptions). This hop: leftover **kept** (works-bar pass / stale-grade), not restamped. July `independent_*` columns **unchanged**.

This sheet is **method first**, then ranks. Rate the 12 works-verified chairs before treating a high PQI as a “it works” claim.

- Full 496 rows (machine-readable): [quality-ranking.csv](quality-ranking.csv)
- Full 496 rows (GitHub-renderable, by works band): [quality-ranking.md](quality-ranking.md)
- Works-verified subset: [WORKS_VERIFIED.md](WORKS_VERIFIED.md)
- Inclusion / works-bar: [INCLUSION.md](INCLUSION.md)
- Scorecard dimensions: [VALUE_FRAMEWORK.md](VALUE_FRAMEWORK.md)
- What/how catalog (not ranks): [CATALOG.md](CATALOG.md)
- **How to improve below-A skills:** [QUALITY_IMPROVE.md](QUALITY_IMPROVE.md) (playbook + leftover A-/v1 + A/A+ YAML when+not-for). Description fixes raise structural PQI; they are not a new independent A grade.

## Rate / install first

These **12 WORKS** are ranks **1–12** after the works-first sort (Read sample 2026-08-14). Install and rate this set before treating any high PQI as a works claim.

| rank | skill | tag | pqi | Read sample 2026-08-14 |
| --- | --- | --- | ---: | --- |
| 1 | `better` | agent-os | 100.0 | Numbered 0–5 polish loop (`BETTER:` report). |
| 2 | `godot-ui` | godot | 100.0 | Godot 4.3+ Control/Theme/focus GDScript; layout ref present. |
| 3 | `ollama-local-setup` | ai-ml | 98.9 | Numbered Windows Ollama install; `scripts/verify-ollama.ps1` exists. |
| 4 | `stable-diffusion` | ai-ml | 97.8 | Numbered HuggingFace Diffusers pipelines (txt2img, ControlNet, LoRA). |
| 5 | `mcp-server-authoring` | agent-os | 97.2 | Numbered MCP transport/tool-design; inspector + templates. |
| 6 | `chroma` | ai-ml | 96.1 | Numbered chromadb `create_collection` / `add` / `query`. |
| 7 | `git-workflow` | agent-os | 96.1 | Numbered PowerShell git/gh; companions present. |
| 8 | `threejs-fundamentals` | threejs | 96.1 | Numbered scene/camera/renderer/Object3D scaffold. |
| 9 | `weights-and-biases` | ai-ml | 96.1 | Numbered `wandb.init` / `log` / `sweep`; refs present. |
| 10 | `github-actions-advanced` | git-github | 95.2 | PowerShell discovery then SHA-pinned workflow YAML. |
| 11 | `docker-management` | devops | 95.0 | Numbered `docker` / `compose` lifecycle. |
| 12 | `emil-design-eng` | frontend | 94.5 | Numbered animation craft with real CSS/JS APIs. |

### WEAK (ranks 13–17) — caveats, not install-first

Kept in the Read sample with caveats. **Not** an install-first set. Evidence: [INCLUSION.md](INCLUSION.md#works-bar-executability). Extra sample WORKS are **not** in this band (INCLUSION only).

| rank | skill | tag | pqi | Caveat |
| --- | --- | --- | ---: | --- |
| 13 | `shadcn` | frontend | 83.2 | CLI procedure is real; companions live at skill root (`cli.md`, `rules/`). |
| 14 | `angular-state-management` | frontend | 82.6 | Snippets miss imports; injects `HttpClient` then uses `fetch`. |
| 15 | `browser-automation` | browser | 82.6 | Playwright E2E procedure is real; body also ships stealth/anti-bot scraping vs YAML never-CAPTCHA. |
| 16 | `glassmorphism` | frontend | 81.5 | Copy-paste CSS; labels itself a `design-it` child, not a direct trigger. |
| 17 | `energy-procurement` | ai-ml | 80.4 | Domain C&I playbook with real formulas; not a shell procedure. |

## How assessed

Three layers. They are not interchangeable.

1. **Independent (July 2026).** `independent_score` / `independent_grade` / `independent_decision` are the 2026-07-17 `qwen36_27b` re-grade of the **private** library (2,540 skills, mean **69.2**). Joined here by folder name = CSV `skill`. The public tree is mostly the `QUALITY_KEEP` slice of that re-grade, plus v1 chairs. **This wave did not re-score 487 bodies with a model.** A high independent score is a July library grade, not a 2026-08-14 reread.
2. **Structural (today).** `structural_now` is a 2026-08-14 mechanical scan of **this repo’s** `SKILL.md` files (frontmatter length/signals, numbered procedure, claimed `references/` / `scripts/` paths on disk, lean line count, YAML `name` vs folder). No LLM. Thresholds below are falsifiable.
3. **Works overlay (Read sample only).** Ranking `works` is the **overlay**: **12 WORKS**, **5 WEAK**, **479 untested**. Read sample is **N=24** (18 prior + 6 extra 2026-08-14): **17 WORKS** in INCLUSION (12 overlay + 5 extra, not padded onto WORKS_VERIFIED), **5 WEAK**, **2 FAIL** (already cut from git). Everyone else is never-Read. Untested ≠ fail. Untested ≠ works. **Do not claim all 496 are verified-works.**

PQI blends those layers with the formula below. It is **not** “we re-read 487 today.” It is **not** an agy/encyclopedia CLI label. It is **not** a VALUE_FRAMEWORK rescore of this week’s bodies.

### How to read ranks

Rank 1 = highest recommended under the **sort below**. PQI is compared **inside** a works band, not above it.

- **Ranks 1–12** are the overlay **WORKS**, sorted by PQI inside that band (then independent_score, then name). This is the install/rate-first set.
- **Ranks 13–17** are the overlay **WEAK** (keep with caveats; not install-first). Includes `browser-automation` from the extra sample.
- **Ranks 18–496** are **untested** in the overlay — **not an install order**. That band includes five extra-sample WORKS (INCLUSION only) plus never-Read chairs. PQI there is the July independent score plus today’s structural scan only. Untested ≠ fail. Untested ≠ works.

This wave did **not** re-score 487 bodies with a model.

- `WORKS` — Read-sample pass (procedure an agent can execute).
- `WEAK` — Read-sample keep with caveats (see INCLUSION).
- `untested` — not in the overlay WORKS/WEAK bands. High PQI here is structure and/or the July score. Five extra-sample WORKS stay here on purpose (not padded into the 12).

v1 chairs with **no** CSV row have empty `independent_*` (displayed as —), **not** a stamped `0`.

Untested PQI = 100 means `structural_now` = 100 (no July row), **not** a works claim — those rows now sit **after** the WORKS and WEAK bands.

## VALUE_FRAMEWORK ↔ independent q-map

Document mapping only. This is **not** a new 2026-08-14 reread of 487 files. Independent subscores are the July `q1`–`q7` fields from that private re-grade.

| VALUE_FRAMEWORK | Independent subscore |
|-----------------|----------------------|
| Clarity | q4_trigger |
| Actionability | q3_procedure |
| Completeness | q2_utility |
| Uniqueness | q5_unique |
| Demand | *(no 1:1; leave blank)* |
| Safe-to-publish | q7_publish + q1_truth |
| Maint | q6_fresh |

## Structural scan (falsifiable)

`structural_now` = `description_points` + `procedure_points` + `claimed_paths_points` + `lean_points` + `name_points` (0–100). Current public `SKILL.md` only.

**description_points (0 / 15 / 30)**

- Parse YAML frontmatter `description` (handle `>` folded and `|` and quoted). Char count = stripped unfolded text length.
- when-signal (case-insensitive, in description): `\bwhen\b` OR `use for` OR `trigger`
- not-for-signal (case-insensitive, in description): `not for` OR `do not use` OR `not a ` OR `never ` OR `not /`
- +30 if len ≥ 80 AND when-signal AND not-for-signal
- +15 if description len ≥ 1 but not both length+signals
- +0 if empty/missing description

Signals are **description-only**. A body “When / Do not use” table does not count. After the 2026-08-14 A/A+ YAML wave plus later unique adds, **496/496** chairs have both signals in the YAML `description` (live scan). Historical example: `git-workflow` once had when in YAML and not-for only in a body table → `has_when_not_for=no`, description_points = 15. That chair now has both in YAML.

**procedure_points (0 / 30)**

- +30 if SKILL.md has **≥ 3** lines matching (multiline):
  `^\s*(?:\d+[\.\)]\s+\S|\*\*\d+[\.\)]\*\*|\d+\.\s+\S)`
  OR ≥ 3 headings matching `(?im)^#{2,4}\s+(?:\d+[\.\)]|step\s+\d+)`
- else 0

**claimed_paths_points (0 / 20)**

- From SKILL.md, collect unique relative paths matching `(?:references|scripts)/[A-Za-z0-9._/-]+` (strip trailing punctuation/` )`). Ignore http(s) URLs.
- Resolve each against the skill folder. If **any** claimed file/dir is missing → **0**. If none claimed, or all exist → **20**.
- Root-level `reference.md` / `examples.md` (no `references/` prefix) are **not** this check. Vacuous 20 is OK.

This flag is **not** the works overlay. Lean copies often mention companions that were not copied. After the leftover wave, `claimed_paths_ok=no` is **0**. Root-level files such as `cli.md` are outside this regex.

**lean_points (0 / 10)**

- +10 if SKILL.md line count (splitlines) is **40–700 inclusive**, else 0

**name_points (0 / 10)**

- +10 if YAML `name` equals folder name (strip quotes). Else 0.
- This wave: only `transformers.js` misses (YAML `name` is `transformers-js`).

## PQI formula

Round PQI to 1 decimal.

```
independent = my_score if CSV hit else null

works_overlay:
  WORKS = 100
  WEAK = 55
  untested = omitted from this term (do not treat as 50)

If CSV hit AND untested:
  PQI = 0.70 * independent + 0.30 * structural_now
If CSV hit AND WORKS:
  PQI = 0.50 * independent + 0.20 * structural_now + 0.30 * 100
If CSV hit AND WEAK:
  PQI = 0.50 * independent + 0.20 * structural_now + 0.30 * 55
If no CSV (v1 chairs) AND WORKS:
  PQI = 0.40 * structural_now + 0.60 * 100
If no CSV AND WEAK:
  PQI = 0.40 * structural_now + 0.60 * 55
If no CSV AND untested:
  PQI = structural_now
```

**Sort (rank 1 = highest recommended):**

1. works: **WORKS**, then **WEAK**, then **untested**
2. PQI descending
3. independent_score descending (nulls last)
4. skill name A-Z

Tags come from [CATALOG.md](CATALOG.md) section headers `## <tag> (N)` and the first-column skill names — **not** the private CSV `pack` column (polluted). Every public folder has exactly one tag.

## Columns (what they are / are not)

| Column | Is | Is not |
|--------|----|--------|
| `rank` | Sort order under the keys above | A claim the body was re-read this week |
| `skill` | Folder name | |
| `tag` | CATALOG section | CSV `pack` |
| `pqi` | Blend of layers; 1 decimal | A new model score |
| `independent_score` | July `my_score`, or empty | Invented for v1 misses; empty ≠ 0 |
| `independent_grade` | July `my_grade`, or empty | |
| `independent_decision` | July `my_decision`, or empty | A 2026-08-14 keep/drop |
| `works` | Read-sample overlay | Structural `claimed_paths_ok` |
| `skill_md_lines` | `splitlines()` count | Token count |
| `description_chars` | Stripped unfolded YAML description length | Body length |
| `has_when_not_for` | Both description signals | Body tables |
| `has_numbered_procedure` | Procedure rule above | “Looks procedural” |
| `claimed_paths_ok` | All matched `references/` / `scripts/` exist, or none claimed | Root `reference.md` |
| `name_matches_folder` | YAML `name` == folder | Display title |
| `structural_now` | Sum of point rules | Independent score |
| `notes` | v1 miss / non-KEEP still in tree | |

## Coverage

**454 / 33** — 454 folders matched a July CSV `skill` row; **33** v1 chairs have no independent row (no invented `my_score`). Two July-hit twins were cut this leftover wave (`godot-gdscript-patterns`, `illustration-direction`).

Hit independent scores: min **57.8** / mean **91.1** / max **97.8** (public set is the KEEP-heavy slice; the 2,540-row private mean was **69.2**).

**Misses (independent columns empty):**  
`addvalue`, `better`, `goal`, `godot-2d-animation`, `godot-2d-physics`, `godot-3d-lighting`, `godot-3d-materials`, `godot-3d-world-building`, `godot-animation-player`, `godot-animation-tree-mastery`, `godot-audio-systems`, `godot-autoload-architecture`, `godot-camera-systems`, `godot-characterbody-2d`, `godot-combat-system`, `godot-composition`, `godot-debugging-profiling`, `godot-dialogue-system`, `godot-export-builds`, `godot-gdscript-mastery`, `godot-save-load-systems`, `godot-state-machine-advanced`, `godot-ui`, `grokimagine`, `inspire-quote-effects`, `local-media-router`, `localimage-stills`, `localvideo`, `quality-at-scale`, `review-results`, `threejs-skill-router`, `transition`, `yt-shorts-flow-director`

Spot-check vs July CSV: `git-workflow` 92.2 A QUALITY_KEEP; `chroma` 92.2 A; `glassmorphism` 90.0 A; `stable-diffusion` 95.6 A+; `better` has no independent row.

## Independent non-KEEP still in tree

July `independent_decision` was **not** `QUALITY_KEEP`; still in tree **kept, works-bar pass / stale-grade**. Do not hide them. July `independent_grade` / `independent_score` / `independent_decision` are **unchanged**.

| Skill | Decision | Grade | independent_score | Why kept |
|-------|----------|-------|------------------:|----------|
| `chrome-browser-automation` | LIBRARY_ONLY | C | 63.3 | Claimed companions exist (`reference.md`, `playwright-cdp-recipes.md`, `examples.md`, `safety-rules.md`). Numbered portable CDP uses real Playwright `connectOverCDP("http://127.0.0.1:9222")`. Unique vs `browser-automation` (agent drive vs E2E tests). Hub scripts optional, not claimed as shipped. |
| `comfyui-workflow-builder` | LIBRARY_ONLY | B- | 74.4 | Unique vs `comfyui` (API JSON vs runtime). `eval/` assets exist. Official API format cited. |
| `context-optimization` | LIBRARY_ONLY | C+ | 66.7 | `scripts/compaction.py` + `references/optimization_techniques.md` exist. Demo `python scripts/compaction.py` exit 0. |
| `senior-frontend` | MERGE_OR_DROP | C+ | 67.8 | Unique owner: scaffold/generators/bundle vs `emil-design-eng` / `web-interface-guidelines`. `scripts/frontend_scaffolder.py`, `component_generator.py`, `bundle_analyzer.py` exist; `--list-features` / `--dry-run` / `--help` exit 0. |
| `svg-quality-audit` | DROP | D | 57.8 | July dinged missing scripts. Public has `scripts/structure_scan.py` + `render_vision_judge.py` + `references/`. `structure_scan.py` smoke exit 0. Stale-grade. |

July D on `svg-quality-audit` is **stale-grade**: scripts exist and the structure scan runs. See [QUALITY_IMPROVE.md](QUALITY_IMPROVE.md). Do not restamp the independent grade from a description-only pass.

This leftover wave **cut** `godot-gdscript-patterns` and `illustration-direction` from git (recommend-cut executed). This hop **kept** the five above (works-bar pass / stale-grade), not restamped. Remaining KEEP B+ chairs (`game-godot`, `ollama`, `web-interface-guidelines`) were improved in the prior wave. Details: [QUALITY_IMPROVE.md](QUALITY_IMPROVE.md).

## Summary histograms

**Independent grade** (— = the 33 misses):

| Grade | Count |
|-------|------:|
| A+ | 61 |
| A | 236 |
| A- | 149 |
| B+ | 3 |
| B- | 1 |
| C+ | 2 |
| C | 1 |
| D | 1 |
| — | 33 |

**Works overlay (CSV `works`):** WORKS 12 · WEAK 5 · untested 479. Read sample N=24 · sampled kept 22 · never-Read 474 (496−22).

**PQI bands:**

| Band | Count |
|------|------:|
| ≥ 90 | 434 |
| 80–89.9 | 49 |
| 70–79.9 | 4 |
| < 70 | 1 |

**Structural (this scan):** numbered procedure 493/496; both description when+not-for signals **496/496**; `claimed_paths_ok=no` **0**; YAML name mismatch 1 (`transformers.js`).

## Ranked tables

Ranks **1–50** (works-first) and bottom **25** here. Full **496**: [quality-ranking.csv](quality-ranking.csv) and [quality-ranking.md](quality-ranking.md).

This is **not** a 50-item install list. Ranks 1–12 WORKS (install/rate first), 13–17 WEAK (caveats), **18–50 untested** (July score + structure only — not an install order).

### Ranks 1–50 (works-first; 18+ not install order)

| rank | skill | tag | pqi | independent_score | independent_grade | independent_decision | works | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `better` | agent-os | 100.0 | — | — | — | WORKS | v1 chair; no independent CSV row |
| 2 | `godot-ui` | godot | 100.0 | — | — | — | WORKS | v1 chair; no independent CSV row |
| 3 | `ollama-local-setup` | ai-ml | 98.9 | 97.8 | A+ | QUALITY_KEEP | WORKS | — |
| 4 | `stable-diffusion` | ai-ml | 97.8 | 95.6 | A+ | QUALITY_KEEP | WORKS | — |
| 5 | `mcp-server-authoring` | agent-os | 97.2 | 94.4 | A | QUALITY_KEEP | WORKS | — |
| 6 | `chroma` | ai-ml | 96.1 | 92.2 | A | QUALITY_KEEP | WORKS | — |
| 7 | `git-workflow` | agent-os | 96.1 | 92.2 | A | QUALITY_KEEP | WORKS | — |
| 8 | `threejs-fundamentals` | threejs | 96.1 | 92.2 | A | QUALITY_KEEP | WORKS | — |
| 9 | `weights-and-biases` | ai-ml | 96.1 | 92.2 | A | QUALITY_KEEP | WORKS | — |
| 10 | `github-actions-advanced` | git-github | 95.2 | 94.4 | A | QUALITY_KEEP | WORKS | — |
| 11 | `docker-management` | devops | 95.0 | 90.0 | A | QUALITY_KEEP | WORKS | — |
| 12 | `emil-design-eng` | frontend | 94.5 | 88.9 | A- | QUALITY_KEEP | WORKS | — |
| 13 | `shadcn` | frontend | 83.2 | 93.3 | A | QUALITY_KEEP | WEAK | — |
| 14 | `angular-state-management` | frontend | 82.6 | 92.2 | A | QUALITY_KEEP | WEAK | — |
| 15 | `browser-automation` | browser | 82.6 | 92.2 | A | QUALITY_KEEP | WEAK | — |
| 16 | `glassmorphism` | frontend | 81.5 | 90.0 | A | QUALITY_KEEP | WEAK | — |
| 17 | `energy-procurement` | ai-ml | 80.4 | 87.8 | A- | QUALITY_KEEP | WEAK | — |
| 18 | `addvalue` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 19 | `goal` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 20 | `godot-2d-animation` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 21 | `godot-2d-physics` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 22 | `godot-3d-lighting` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 23 | `godot-3d-materials` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 24 | `godot-3d-world-building` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 25 | `godot-animation-player` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 26 | `godot-animation-tree-mastery` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 27 | `godot-audio-systems` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 28 | `godot-autoload-architecture` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 29 | `godot-camera-systems` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 30 | `godot-characterbody-2d` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 31 | `godot-combat-system` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 32 | `godot-composition` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 33 | `godot-debugging-profiling` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 34 | `godot-dialogue-system` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 35 | `godot-export-builds` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 36 | `godot-gdscript-mastery` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 37 | `godot-save-load-systems` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 38 | `godot-state-machine-advanced` | godot | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 39 | `grokimagine` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 40 | `local-media-router` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 41 | `localimage-stills` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 42 | `localvideo` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 43 | `quality-at-scale` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 44 | `review-results` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 45 | `threejs-skill-router` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 46 | `transition` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 47 | `yt-shorts-flow-director` | agent-os | 100.0 | — | — | — | untested | v1 chair; no independent CSV row |
| 48 | `academic-pdf-redaction` | research | 98.5 | 97.8 | A+ | QUALITY_KEEP | untested | — |
| 49 | `agents-sdk` | agents | 98.5 | 97.8 | A+ | QUALITY_KEEP | untested | — |
| 50 | `audio-whisper-transcription` | video | 98.5 | 97.8 | A+ | QUALITY_KEEP | untested | — |

### Bottom 25

| rank | skill | tag | pqi | independent_score | independent_grade | independent_decision | works | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 463 | `text-to-speech` | video | 89.9 | 85.6 | A- | QUALITY_KEEP | untested | — |
| 464 | `uncle-bob-craft` | architecture | 89.9 | 85.6 | A- | QUALITY_KEEP | untested | — |
| 465 | `uniprot-database` | python-backend | 89.9 | 85.6 | A- | QUALITY_KEEP | untested | — |
| 466 | `web-vitals-analyzer` | automation | 89.9 | 85.6 | A- | QUALITY_KEEP | untested | — |
| 467 | `godot-component-system` | godot-extra | 89.2 | 88.9 | A- | QUALITY_KEEP | untested | — |
| 468 | `os-scripting` | testing-qa | 89.2 | 88.9 | A- | QUALITY_KEEP | untested | — |
| 469 | `python-scala-collections` | python-backend | 89.2 | 88.9 | A- | QUALITY_KEEP | untested | — |
| 470 | `radar-vital-signs` | science | 89.2 | 88.9 | A- | QUALITY_KEEP | untested | — |
| 471 | `readme` | content | 89.2 | 88.9 | A- | QUALITY_KEEP | untested | — |
| 472 | `sqlite-map-parser` | data-databases | 89.2 | 88.9 | A- | QUALITY_KEEP | untested | — |
| 473 | `3d-image-to-model` | svg-and-design | 88.5 | 87.8 | A- | QUALITY_KEEP | untested | — |
| 474 | `python-scala-functional` | python-backend | 88.5 | 87.8 | A- | QUALITY_KEEP | untested | — |
| 475 | `workflow-automation` | automation | 88.5 | 87.8 | A- | QUALITY_KEEP | untested | — |
| 476 | `ffmpeg-video-filters` | video | 87.1 | 94.4 | A | QUALITY_KEEP | untested | — |
| 477 | `transformers.js` | image-vision | 86.9 | 85.6 | A- | QUALITY_KEEP | untested | — |
| 478 | `game-godot` | godot | 86.8 | 81.1 | B+ | QUALITY_KEEP | untested | — |
| 479 | `ollama` | agent-os | 86.8 | 81.1 | B+ | QUALITY_KEEP | untested | — |
| 480 | `web-interface-guidelines` | agent-os | 86.8 | 81.1 | B+ | QUALITY_KEEP | untested | — |
| 481 | `trl-fine-tuning` | ai-ml | 84.0 | 90.0 | A | QUALITY_KEEP | untested | — |
| 482 | `comfyui-workflow-builder` | agent-os | 82.1 | 74.4 | B- | LIBRARY_ONLY | untested | kept; works-bar pass / stale-grade (July LIBRARY_ONLY unchanged) |
| 483 | `senior-frontend` | agent-os | 77.5 | 67.8 | C+ | MERGE_OR_DROP | untested | kept; works-bar pass / stale-grade (July MERGE_OR_DROP unchanged) |
| 484 | `context-optimization` | agent-os | 76.7 | 66.7 | C+ | LIBRARY_ONLY | untested | kept; works-bar pass / stale-grade (July LIBRARY_ONLY unchanged) |
| 485 | `chrome-browser-automation` | agent-os | 74.3 | 63.3 | C | LIBRARY_ONLY | untested | kept; works-bar pass / stale-grade (July LIBRARY_ONLY unchanged) |
| 486 | `svg-quality-audit` | agent-os | 70.5 | 57.8 | D | DROP | untested | kept; works-bar pass / stale-grade (July DROP unchanged) |
| 487 | `inspire-quote-effects` | agent-os | 60.0 | — | — | — | untested | v1 chair; no independent CSV row |
