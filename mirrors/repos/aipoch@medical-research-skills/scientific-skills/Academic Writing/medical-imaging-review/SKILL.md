---
name: medical-imaging-review
description: Write comprehensive literature reviews for medical imaging AI research. Use when writing survey papers, systematic reviews, or literature analyses on topics like segmentation, detection, classification in CT, MRI, X-ray, ultrasound, or pathology imaging. Triggers on requests f...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Medical Imaging AI Literature Review Skill

Write comprehensive literature reviews following a systematic 7-phase workflow.

## Quick Start

1. **Initialize project** with three core files:
   - `CLAUDE.md` - Writing guidelines and terminology
   - `IMPLEMENTATION_PLAN.md` - Staged execution plan
   - `manuscript_draft.md` - Main manuscript

2. **Follow the 7-phase workflow** (see [references/WORKFLOW.md](references/WORKFLOW.md))

3. **Use domain-specific templates** (see [references/DOMAINS.md](references/DOMAINS.md))

---

## Core Principles

### Writing Style
- **Hedging language**: "may", "suggests", "appears to", "has shown promising results"
- **Avoid absolutes**: Never say "X is the best method"
- **Citation support**: Every claim needs reference
- **Limitations**: Each method section needs a Limitations paragraph

### Required Elements
- **Key Points box** (3-5 bullets) after title
- **Comparison table** for each major section
- **Performance metrics**: Dice (0.XXX), HD95 (X.XX mm)
- **Figure placeholders** with detailed captions
- **References**: 80-120 typical, organized by topic

### Paragraph Structure
```
Topic sentence (main claim)
  → Supporting evidence (citations + data)
  → Analysis (critical evaluation)
  → Transition to next paragraph
```

---

## Literature Sources

Use multi-source strategy for comprehensive coverage:

| Source | Best For | Tools |
|--------|----------|-------|
| ArXiv | Latest DL methods, preprints | `search_papers`, `read_paper` |
| PubMed | Clinical validation, peer-reviewed | `pubmed_search_articles` |
| Zotero | Existing library, organized refs | `zotero_search_items` |

For MCP configuration details, see [references/MCP_SETUP.md](references/MCP_SETUP.md).

---

## Standard Review Structure

```markdown
# [Title]: State of the Art and Future Directions

## Key Points
- [3-5 bullets summarizing main findings]

## Abstract

## 1. Introduction
### 1.1 Clinical Background
### 1.2 Technical Challenges
### 1.3 Scope and Contributions

## 2. Datasets and Evaluation Metrics
### 2.1 Public Datasets (Table 1)
### 2.2 Evaluation Metrics

## 3. Deep Learning Methods
### 3.1 [Category 1]
### 3.2 [Category 2]
(Table 2: Method Comparison)

## 4. Downstream Applications

## 5. Commercial Products & Clinical Translation (Table 3)

## 6. Discussion
### 6.1 Current Limitations
### 6.2 Future Directions

## 7. Conclusion


## Input Validation

This skill accepts requests that match the documented purpose of `medical-imaging-review` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `medical-imaging-review` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References
```

---

## Method Description Template

```markdown
### 3.X [Method Category]

[1-2 paragraph introduction with motivation]

**[Method Name]:** [Author] et al. [ref] proposed [method], which [innovation]:
- [Key component 1]
- [Key component 2]
Achieves Dice of X.XX on [dataset].

**Limitations:** Despite advantages, [category] methods face:
(1) [limit 1]; (2) [limit 2].
```

---

## Citation Patterns

```markdown
# Data citation
"...achieved Dice of 0.89 [23]"

# Method citation
"Gu et al. [45] proposed..."

# Multi-citation
"Several studies demonstrated... [12, 15, 23]"

# Comparative
"While [12] focused on..., [15] addressed..."
```

---

## Reference Files

| File | Purpose |
|------|---------|
| [references/WORKFLOW.md](references/WORKFLOW.md) | Detailed 7-phase workflow |
| [references/TEMPLATES.md](references/TEMPLATES.md) | CLAUDE.md and IMPLEMENTATION_PLAN.md templates |
| [references/DOMAINS.md](references/DOMAINS.md) | Domain-specific method categories |
| [references/MCP_SETUP.md](references/MCP_SETUP.md) | MCP server configuration |
| [references/QUALITY_CHECKLIST.md](references/QUALITY_CHECKLIST.md) | Pre-submission quality checklist |

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If execution fails, report the failure point, summarize what can still be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.
