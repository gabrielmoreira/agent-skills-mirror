---
name: technical-perception
description: Discovers canonical literature for open-ended technical ideas, and extracts quantitative concepts, equations, constraints, and citations from papers, RFCs, and documents into Specification Manifests. Use when exploring technical ideas or reading literature.
license: Apache-2.0
user-invocable: false
---

# Technical Perception & Literature Grounding Skill

## Purpose
This skill transforms PDFs, diagrams, web documents, academic literature, and unstructured technical ideas into verified, machine-readable artifacts across two separated modality roles:
0. **`SOURCE_OCR.md` (`Stage 0V` — `@Scribe` Vision/PDF OCR):** Verbatim mathematical transcription of visual/PDF sources staged via [prepare_visual_sources.py](./scripts/prepare_visual_sources.py) with TEI P5 `<uncertain>` / `<illegible/>` epistemic provenance.
1. **`RESEARCH.md` (`Stage 0` — `@Researcher`):** Grounded candidate comparison brief persisted via atomic `create`.
2. **`manifest.json` (`Stage 1` — `@Researcher`):** Formal `Specification Manifest` JSON conforming to [schema.json](./schema.json) persisted via atomic `create`.

## Required Context
* **Path A (Concrete Literature / Visual Spec Provided):** Source document path (`.pdf`, `.png`/`.jpg`/`.svg` via `SOURCE_OCR.md`, Markdown, LaTeX, RFC, or text snippet).
* **Path B (Grounded Ideation / Problem Statement):** Open-ended technical problem, algorithm goal, or idea to research via approved `web_fetch` sources.

## Execution Workflow

### Mode 0: Multimodal PDF, Diagram & Web-Figure OCR (`@Scribe` -> `SOURCE_OCR.md`)
1. **Stage Visual Assets:** Execute `python3 .github/skills/technical-perception/scripts/prepare_visual_sources.py` with `--dir research --out-dir .pipeline_scratch/ocr_staging` (for a `research/` folder), `--pdf <path>`, `--image <path>`, `--html <path>`, or `--url <approved_https_url>` to stage `180 DPI` page plates and figure PNGs inside `.pipeline_scratch/ocr_staging/`.
2. **3-Tier TEI P5 Epistemic Transcription:** Inspect staged plates via `view` (images before text) and persist `SOURCE_OCR.md` via `create`:
   - **Tier 1 (Legible Math):** Normalize ligatures (`ﬁ -> fi`, `ﬂ -> fl`) and norms (`\lVert \cdot \rVert`) into clean LaTeX with **zero** XML tags.
   - **Tier 2 (Contextual Guess):** Wrap degraded/corrupted glyphs in `<uncertain raw="..." guess="..." reason="..." confidence="high|medium|low">guess</uncertain>`.
   - **Tier 3 (Irrecoverable Occlusion):** Emit `<illegible context="..." reason="occluded"/>` without inventing digits.

### Mode 1: Grounded Ideation & Academic Search (`@Researcher` -> `RESEARCH.md`)
1. **Source Precedence (`research/` & `SOURCE_OCR.md` vs. Internet-First `web_fetch`):** Local BYOK sessions expose `web_fetch(url=...)` (direct HTTP GET), not generic search-engine operators, and `@Researcher` sits behind the Vision/PDF Modality Firewall (never calling `view` on raw images/PDFs).
   - **When `SOURCE_OCR.md` or `research/` text files exist:** Read those local ground-truth documents FIRST (plus [research_template.md](./research_template.md) ONLY—never read `schema.json` during Mode 1), then supplement via `web_fetch` against **Approved Research Sources** ([approved_sources.json](../../hooks/approved_sources.json)) as needed.
   - **When no local `research/` documents exist (or the prompt lacks complete implementation formulas/citations):** Internet research takes immediate precedence—call `web_fetch(url=...)` against an Approved Research Source in **Turn 1** (alongside reading [research_template.md](./research_template.md)) before drafting any candidates in internal reasoning.
   - If a fetched HTML document embeds equations inside `<img>` or `.pdf` assets not yet transcribed in `SOURCE_OCR.md`, report `Status: CONDITIONAL_PASS` with the exact URLs so `@Orchestrator` invokes `@Scribe` (`Mode 0`) first.
   - Authoritative textbooks & compendia (e.g. *NIST DLMF*, *Burden & Faires*, *Numerical Recipes*, *CLRS*) are also valid canonical sources for foundational numerical and computing methods.
2. **Direct Verification:** Fetch official paper abstracts, standards specifications, or mathematical compendia via `web_fetch` (or `SOURCE_OCR.md` / local text files via `view`) to confirm authors, publication date, and core equations. Never propose ungrounded algorithms from internal memory alone.
3. **Persist Research Brief (`RESEARCH.md`):**
   - Persist `RESEARCH.md` directly via `create(path="<absolute_cwd>/RESEARCH.md", file_text="...")` conforming to [research_template.md](./research_template.md).
   - **Pre-Manifest Contract:** Every candidate algorithm MUST include its Canonical Literature Reference (title, authors, year, and DOI/arXiv or textbook citation) AND its governing LaTeX mathematical formula.

### Mode 2: Specification & Formula Extraction (`@Researcher` -> `manifest.json`)
1. **Defensive Formula & Verbatim Constant Extraction (`formal_specifications`):**
   * Extract equations or state rules into clean LaTeX or formal algorithmic expressions, assigning each a unique identifier `spec_id` (e.g. `SPEC-1`, `SPEC-2`).
   * **Verbatim Constant Preservation:** Preserve every rational coefficient, sign, subscript, loop bound, and tolerance from `SOURCE_OCR.md` or canonical text verbatim—never overwrite source-specific constants with memorized defaults.
   * **Epistemic Provenance Propagation:** If `SOURCE_OCR.md` contains `<uncertain>` or `<illegible/>` tags, list every item in top-level `"ambiguities"` and set `"epistemic_status": "assumption"` on every affected `SPEC-k` entry.
   * Specify `representation_format` (`latex`, `pseudocode`, `state_transition`, `bnf_grammar`, `predicate_logic`, `type_algebra`, or `text_formula`) and escape backslashes cleanly in JSON strings (`\\frac`, `\\sum`).
   * **Autonomous Grounding Fallback:** If an approved candidate from `RESEARCH.md` lacks complete formulas, execute a direct `web_fetch` against an approved research source in `<subagent_context>` or cite standard compendia (*NIST DLMF*, *Burden & Faires*, *Numerical Recipes*, *CLRS*) to populate `source_reference` and `grounding_evidence`.
2. **Establish Verification & Equivalence Contract (`verification_contract`):**
   * Specify `equivalence_mode`: `approximate_tolerance` (continuous/numerical), `exact_equality` (integers/tokens), `structural_isomorphism` (graphs/trees), `metamorphic_relation` (chaotic/stochastic), or `state_trace_equivalence` (protocols/FSMs).
   * For continuous models, explicitly define default relative tolerance (`rtol`, e.g. `1e-7`), absolute tolerance (`atol`, e.g. `1e-9`), precision, and domain bounds.
3. **Atomic Persistence & Schema Validation:**
   * Persist `manifest.json` directly via `create(path="<absolute_cwd>/manifest.json", file_text="...")` conforming to [schema.json](./schema.json). Never invoke `edit` on `manifest.json`.

## Success Criteria
* For Ideation: A completed `RESEARCH.md` citing verified arXiv links or DOIs for every candidate.
* For Extraction: A complete JSON object adhering strictly to [schema.json](./schema.json).
* Every definition contains a `spec_id` (or `id`), raw `expression`/`latex`, `grounding_evidence`, and `epistemic_status`.
* Preconditions, conservation laws, or domain bounds are captured in `constraints` and `verification_contract`.
