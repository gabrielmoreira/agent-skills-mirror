---
name: evaluate
description: >
  Evaluate the quality of any AI-generated artifact — visualizations, code, documents,
  conversations, or any skill output. Works in 3 phases: (1) Generate evaluation specs
  tailored to the artifact type, (2) Run comprehensive evaluation against those specs,
  (3) Produce a beautiful visual report using the /visualize skill. Use after any skill
  produces output, or invoke directly with /evaluate <file-or-context>. Supports
  evaluating: HTML visualizations, code projects, documents, agent conversations,
  slide decks, dashboards, or any artifact with quality dimensions.
---

# Evaluate

Comprehensive quality evaluation for any AI-generated artifact. Produces its report as a visualization.

## How It Works

```
┌──────────────────────────────────────────────┐
│                                              │
│  Phase 1: SPEC GENERATION                    │
│  Analyze the artifact type                   │
│  Generate tailored evaluation criteria       │
│  Define scoring dimensions + weights         │
│  Set quality gates                           │
│           │                                  │
│           ▼                                  │
│  Phase 2: EVALUATION                         │
│  Run automated checks (when possible)        │
│  Visual/manual inspection                    │
│  Score each dimension with evidence          │
│  Identify systemic vs local issues           │
│           │                                  │
│           ▼                                  │
│  Phase 3: REPORT (via /visualize)            │
│  Generate a beautiful HTML eval report       │
│  Scores, charts, screenshots, fix list       │
│  Radar chart of dimensions                   │
│  Before/after tracking                       │
│                                              │
└──────────────────────────────────────────────┘
```

## Phase 1: Spec Generation

For any artifact, generate evaluation specs by analyzing:

### 1. Identify Artifact Type
- **HTML Visualization** → visual design, interactivity, technical, content, shareability
- **Code/Project** → correctness, readability, architecture, test coverage, performance
- **Document/Report** → clarity, structure, accuracy, completeness, tone
- **Conversation/Agent** → helpfulness, accuracy, tone, efficiency, safety
- **Slide Deck** → all visualization dims + narrative flow, persuasion, pacing
- **Dashboard** → data accuracy, information density, scannability, actionability
- **Custom** → derive dimensions from the skill's SKILL.md and stated goals

### 2. Generate Dimensions
For each artifact type, produce 6-10 evaluation dimensions. Each dimension needs:
- **Name** — short, clear label
- **Description** — what this dimension measures
- **Weight** — percentage (all weights sum to 100%)
- **Scoring anchors** — what does a 10, 8, 6, 4 look like?
- **Automated checks** — any programmatic tests (if applicable)
- **Deductions** — specific issues and their point costs

### 3. Set Quality Gates
Define gates based on the artifact's purpose:

| Gate | Criteria | Meaning |
|------|----------|---------|
| 🚀 **EXCEPTIONAL** | Overall ≥ 9.5, all ≥ 9 | Best-in-class. Share everywhere. |
| ✅ **SHIP** | Overall ≥ 9.0, all ≥ 8 | Production-ready. |
| ⚠️ **ACCEPTABLE** | Overall ≥ 8.0, all ≥ 7 | Usable but not impressive. |
| 🔧 **NEEDS WORK** | Overall ≥ 7.0 or any < 7 | Fix before releasing. |
| ❌ **FAIL** | Overall < 7.0 or any < 5 | Major rework. |

### 4. Output Spec Document
Write the spec to `eval-spec-[artifact-name].md` for reference and reuse.

## Phase 2: Evaluation

### For HTML Visualizations

Open in browser at 3 viewports (1280×720, 768×1024, 375×667).

**Automated audit** (run in browser console):
```javascript
(function() {
  const audit = {};
  const style = [...document.querySelectorAll('style')].map(s => s.textContent).join(' ');
  const html = document.documentElement.outerHTML;

  // Structure
  audit.hasDoctype = /^<!doctype html>/i.test(html);
  audit.hasLangAttr = !!document.documentElement.lang;
  audit.hasCharset = !!document.querySelector('meta[charset]');
  audit.hasViewport = !!document.querySelector('meta[name="viewport"]');
  audit.hasTitle = document.title.length > 0;

  // Menu system
  audit.menuExists = !!document.querySelector('.viz-menu');
  audit.menuHasTheme = !!html.match(/cycleTheme|themeLabel/i);
  audit.menuHasDownload = !!html.match(/htmlToImage|html-to-image/i);
  audit.menuHasPrint = !!html.match(/window\.print/i);

  // Theme system
  audit.hasCSSVars = !!style.match(/--bg\s*:/);
  audit.hasDarkTheme = !!style.match(/(\.theme-dark|:root)[\s\S]*?--bg/);
  audit.hasLightTheme = !!style.match(/\.theme-light/);
  audit.themePersistedToStorage = !!html.match(/localStorage.*theme/i);

  // Typography
  audit.hasInterFont = !!html.match(/fonts\.googleapis.*Inter|font-family.*Inter/i);
  audit.hasFontFallback = !!style.match(/-apple-system|system-ui/);
  audit.bodyFontSize = parseFloat(getComputedStyle(document.body).fontSize);
  audit.bodyFontOK = audit.bodyFontSize >= 14;

  // Layout
  audit.usesFlexOrGrid = !!(style.match(/display\s*:\s*(flex|grid)/));
  audit.hasMaxWidth = !!style.match(/max-width/);
  audit.hasResponsiveBreakpoints = !!style.match(/@media.*max-width|@media.*min-width|sm:|md:|lg:/);

  // Print & Accessibility
  audit.hasPrintStyles = !!style.match(/@media\s*print/);
  audit.hasPrintColorAdjust = !!style.match(/print-color-adjust/);
  audit.hasReducedMotion = !!style.match(/prefers-reduced-motion/);
  audit.hasAriaLabels = !!html.match(/aria-label/);
  audit.hasSemanticHTML = !!html.match(/<(header|main|nav|section|article|footer)/);

  // Animations
  audit.hasKeyframes = !!style.match(/@keyframes/);
  audit.hasTransitions = !!style.match(/transition\s*:/);

  // Performance
  audit.fileSizeKB = Math.round(new Blob([html]).size / 1024);
  audit.fileSizeOK = audit.fileSizeKB < 200;
  audit.noExternalImages = document.querySelectorAll('img[src^="http"]').length === 0;
  audit.htmlToImageLoaded = typeof htmlToImage !== 'undefined';

  // Summary
  const bools = Object.entries(audit).filter(([k,v]) => typeof v === 'boolean');
  const passed = bools.filter(([k,v]) => v).length;
  audit._passed = passed;
  audit._total = bools.length;
  audit._percent = Math.round(passed / bools.length * 100);
  audit._failures = bools.filter(([k,v]) => !v).map(([k]) => k);

  console.table(audit);
  return audit;
})();
```

**Visual scoring** — 8 dimensions for visualizations:

| # | Dimension | Weight | 10 = | 6 = |
|---|-----------|--------|------|------|
| D1 | First Impression | 15% | Apple keynote quality | Generic template feel |
| D2 | Typography | 15% | Perfect hierarchy, Inter font, fluid sizing | All same size, no hierarchy |
| D3 | Color & Contrast | 10% | Harmonious, WCAG AA, both themes beautiful | Clashing, low contrast |
| D4 | Layout & Spacing | 15% | Consistent rhythm, responsive, generous space | Cramped, broken at mobile |
| D5 | Content Quality | 15% | Clear message in 5 seconds, zero filler | Confusing, placeholder text |
| D6 | Interactivity | 10% | Menu + theme + download + print all flawless | Missing features, broken |
| D7 | Technical | 10% | Zero errors, semantic, accessible, print-ready | Console errors, broken layout |
| D8 | Shareability | 10% | Would tweet this unprompted | Worse than Canva |

### For Code/Projects
Dimensions: Correctness, Readability, Architecture, Error Handling, Performance, Testing, Documentation, Security

### For Documents
Dimensions: Clarity, Structure, Accuracy, Completeness, Tone, Formatting, Actionability, Brevity

### For Agent Conversations
Dimensions: Helpfulness, Accuracy, Tone, Efficiency, Safety, Context Awareness, Tool Usage, Follow-through

## Phase 3: Visual Report (via /visualize)

After scoring, generate the eval report as a **beautiful HTML dashboard** using the visualize skill:

### Report Structure
1. **Hero** — artifact name, overall score (big number), quality gate badge
2. **Radar Chart** — all dimensions plotted on a radar/spider chart (Chart.js)
3. **Dimension Cards** — each dimension as a card with score, bar, key notes
4. **Automated Audit** — pass/fail checklist with percentages
5. **Screenshots** — key views embedded (if HTML artifact)
6. **Fix List** — prioritized fixes as a kanban-style layout (critical / high / medium / low)
7. **Systemic Issues** — patterns that affect all outputs (flagged for SKILL.md fixes)
8. **History** — if re-evaluating, show before/after score comparison chart

### Report Filename
`eval-report-[artifact-name]-[date].html`

### The report itself must score ≥ 9.0 on the visualize eval criteria.
This is the ultimate dogfood test — our evaluation tool produces evaluations using our visualization tool.

## The Improvement Loop

```
Generate artifact (any skill)
       ↓
/evaluate → Spec + Score + Visual Report
       ↓
Review report → identify fixes
       ↓
Fix (systemic → SKILL.md, local → artifact)
       ↓
/evaluate again → compare scores
       ↓
Ship when gate = SHIP or EXCEPTIONAL
```

**Max 3 loops per artifact.** If it can't reach SHIP in 3 loops, the problem is in the skill — update the skill's instructions, not the artifact.

## Quick Start

```
# Evaluate a visualization
/evaluate path/to/visualization.html

# Evaluate with custom context
/evaluate path/to/code-project --type code

# Re-evaluate after fixes (tracks improvement)
/evaluate path/to/visualization.html --loop 2

# Generate specs only (no scoring)
/evaluate --specs-only --type dashboard
```
