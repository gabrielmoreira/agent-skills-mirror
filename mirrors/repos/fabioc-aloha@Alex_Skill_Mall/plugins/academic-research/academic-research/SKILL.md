---
type: skill
lifecycle: stable
inheritance: inheritable
name: academic-research
description: Research project scaffolding, thesis/dissertation writing, literature reviews, publication workflows, and the AI assistant-assisted academic workflows
tier: extended
applyTo: '**/*academic*,**/*research*'
currency: 2026-04-20
lastReviewed: 2026-04-30
---

# Academic Research


> Complete research lifecycle: project setup, literature review, writing, publication, and defense.

---

## Project Structure

```
research-project/
├── .github/
│   └── copilot-instructions.md    # Research context for the AI assistant
├── docs/
│   ├── RESEARCH-PLAN.md           # Questions, timeline, milestones
│   ├── METHODOLOGY.md             # Design decisions
│   └── DECISION-LOG.md            # Key decisions with rationale
├── data/
│   ├── raw/                       # Untouched source data
│   ├── processed/                 # Cleaned/transformed
│   └── DATA-DICTIONARY.md         # Variable definitions
├── analysis/
│   ├── scripts/                   # Analysis code
│   └── outputs/                   # Figures, tables
├── writing/
│   ├── drafts/                    # Work in progress
│   └── submissions/               # Submitted versions
├── references/
│   ├── LITERATURE-MATRIX.md       # Systematic tracking
│   └── notes/                     # Reading notes
└── README.md
```

### Quick Setup

```bash
mkdir -p .github docs data/{raw,processed} analysis/{scripts,outputs} writing/{drafts,submissions} references/notes
touch docs/RESEARCH-PLAN.md docs/METHODOLOGY.md references/LITERATURE-MATRIX.md .github/copilot-instructions.md
```

---

## Research Project Types

| Type | Duration | Output | Review |
|------|----------|--------|--------|
| Master's Thesis | 1-2 years | 80-150 pages | Committee defense |
| PhD Dissertation | 3-7 years | 150-300+ pages | Committee + external |
| Journal Article | 3-12 months | 5,000-10,000 words | Peer review |
| Conference Paper | 2-6 months | 4,000-8,000 words | Peer review |

---

## Research Question Development

### PICO Framework

- **P**opulation — Who is being studied?
- **I**ntervention — What is being tested?
- **C**omparison — Against what?
- **O**utcome — What is measured?

### FINER Criteria

| Criterion | Question |
|-----------|----------|
| **F**easible | Can it be done with available resources? |
| **I**nteresting | Does anyone care? |
| **N**ovel | Does it add new knowledge? |
| **E**thical | Can it be done ethically? |
| **R**elevant | Does it matter to the field? |

---

## Literature Review

### Synthesis Approaches

| Approach | When to Use |
|----------|-------------|
| **Thematic** | Organize by concepts across sources |
| **Chronological** | Show field evolution |
| **Methodological** | Compare research approaches |
| **Concept Matrix** | Map concepts to sources in table |

### Gap Types

- **Empirical** — No studies in specific context
- **Theoretical** — Theory not applied to domain
- **Methodological** — New methods could reveal insights
- **Population** — Understudied demographic

### Literature Matrix Template

```markdown
| Citation | Year | Method | Findings | Gaps | Relevance |
|----------|------|--------|----------|------|-----------|
| Author1 et al. | 2024 | RCT | X | Y | ⭐⭐⭐ |
```

---

## Methodology

### Qualitative Methods

| Method | Best For | Sample |
|--------|----------|--------|
| Interviews | Deep understanding | 10-30 |
| Focus Groups | Group dynamics | 4-8/group |
| Case Study | Detailed exploration | 1-10 |
| Grounded Theory | Theory generation | Until saturation |

### Quantitative Methods

| Method | Best For | Sample |
|--------|----------|--------|
| Survey | Breadth, generalization | 100-1000+ |
| Experiment | Causation | Power analysis |
| Quasi-experiment | No randomization | Varies |

### Mixed Methods

- **Convergent** — Qual + quant simultaneously
- **Explanatory Sequential** — Quant → Qual
- **Exploratory Sequential** — Qual → Quant

---

## Thesis/Dissertation Structure

1. **Introduction** — Problem, significance, research questions
2. **Literature Review** — Framework, prior work, gaps
3. **Methodology** — Design, collection, analysis
4. **Results** — Data without interpretation
5. **Discussion** — Interpret, connect to literature
6. **Conclusion** — Summary, contributions, limitations

### Discipline Variations

| Discipline | Variation |
|------------|-----------|
| Sciences | Methods-heavy |
| Humanities | Multiple thematic chapters |
| Social Sciences | Separate theoretical framework |
| Engineering | Implementation + Evaluation chapters |

---

## Academic Writing

### Hedging Language

| Strong | Hedged |
|--------|--------|
| "This proves..." | "This suggests..." |
| "Always causes" | "May contribute to" |
| "Definitely shows" | "Evidence indicates" |

### CARS Model (Introductions)

1. **Establish territory** — topic importance
2. **Establish niche** — gap in knowledge
3. **Occupy niche** — your contribution

### Citation Density

| Section | Density |
|---------|---------|
| Abstract | None |
| Introduction | Medium |
| Related Work | High |
| Methods | Low-Medium |
| Results | Low |
| Discussion | Medium |

---

## Publication Workflow

### Venue Selection

| Research Type | Venue |
|---------------|-------|
| User study with metrics | ACM CHI |
| Business implications | Harvard Business Review |
| Cognitive theory | Cognitive Systems Research |
| Philosophical AI argument | Minds & Machines |

### 5-Phase Process

| Phase | Duration | Focus |
|-------|----------|-------|
| Preparation | 1-2 weeks | Literature, outline, figures |
| Rough Draft | 1-2 weeks | Write without editing |
| Revision | 1-2 weeks | Structure → Section → Paragraph → Sentence |
| Feedback | 2-4 weeks | Advisor, peers |
| Polish | 1 week | Format, citations, submit |

### Responding to Reviews

```markdown
## Response to Reviewer 1

### R1.1: "[Concern]"

We appreciate this observation. [How addressed].

Changes: Section X, paragraph Y: [new text]
```

---

## Committee Navigation

### Defense Preparation

1. Anticipate likely questions
2. Prepare 20-30 minute presentation
3. Know your limitations
4. Have backup slides
5. Practice with friendly audience

### Common Concerns

| Concern | Address With |
|---------|--------------|
| "Why this topic?" | Strong motivation |
| "What's your contribution?" | Explicit list |
| "How is this valid?" | Robust methodology |
| "What about X?" | Scope, future work |

---

## Citation Management

| Style | Discipline |
|-------|------------|
| APA 7 | Psychology, social sciences |
| MLA 9 | Humanities |
| Chicago | History |
| IEEE | Engineering, CS |
| Vancouver | Medicine |

---

## Refactoring Existing Projects

### Audit Checklist

- [ ] Has .github/copilot-instructions.md
- [ ] Data separated: raw vs processed
- [ ] Research questions documented
- [ ] Literature systematically tracked
- [ ] Methodology decisions recorded

### Migration Pattern

```bash
git mv old-data.csv data/raw/
git mv cleaned.csv data/processed/
git mv draft.docx writing/drafts/paper-v1.docx
```

---

## File Templates

### RESEARCH-PLAN.md

```markdown
# Research Plan: [Title]

## Research Questions
1. Primary: [Main question]
2. Secondary: [Supporting questions]

## Timeline
| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Literature | Weeks 1-4 | Matrix complete |
| Collection | Weeks 5-12 | Raw data |
| Analysis | Weeks 13-16 | Results |
| Writing | Weeks 17-20 | Draft |
```

### copilot-instructions.md (Research)

```markdown
# [Project] - Research Context

## Current Phase
- [x] Literature Review
- [ ] Data Collection

## the AI assistant Guidance
- Add literature to references/LITERATURE-MATRIX.md
- Log decisions in docs/DECISION-LOG.md
- Citation style: APA 7
```

---

## Pre-Submission Checklist

- [ ] Abstract stands alone
- [ ] Contributions stated explicitly
- [ ] All claims supported
- [ ] Limitations acknowledged
- [ ] References complete
- [ ] Word limit respected
- [ ] Anonymized if required

---

## Tools

| Tool | Purpose |
|------|---------|
| Zotero | Reference management |
| Overleaf | LaTeX collaboration |
| Connected Papers | Literature discovery |
| Pandoc | Markdown to Word/PDF |

---

## Related Skills

- [literature-review](../literature-review/SKILL.md) — Systematic search
- [citation-management](../citation-management/SKILL.md) — APA formatting
- [md-to-word](../md-to-word/SKILL.md) — Document conversion
- [dissertation-defense](../dissertation-defense/SKILL.md) — Defense preparation
