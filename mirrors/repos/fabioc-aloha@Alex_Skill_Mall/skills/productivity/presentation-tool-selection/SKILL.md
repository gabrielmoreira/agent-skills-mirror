---
type: skill
lifecycle: stable
inheritance: inheritable
name: presentation-tool-selection
description: Best practice decision matrix for choosing between Marp, Gamma, and PptxGenJS based on use case requirements.
tier: extended
applyTo: '**/*presentation*,**/*tool*,**/*selection*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Presentation Tool Selection Skill


> Choose the right presentation tool for your use case — Slides, Pitch, or Auto.

> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

the AI assistant has three presentation generation capabilities. This skill provides the decision framework for selecting the optimal tool based on requirements.

---

## Tool Nicknames (Quick Reference)

| Nickname | Full Name | Remember As |
|----------|-----------|-------------|
| **Slides** | Marp | "Markdown slides" |
| **Pitch** | Gamma | "AI pitch deck" |
| **Auto** | PptxGenJS | "Automated reports" |

**Just say**: "use Slides", "use Pitch", or "use Auto"

---

## The Three Tools

| Nickname | Tool | Type | Best For |
|----------|------|------|----------|
| **Slides** | Marp | Markdown → Multi-format | Version-controlled technical docs |
| **Pitch** | Gamma | AI-generated | Professional pitch decks, rapid prototyping |
| **Auto** | PptxGenJS | Programmatic API | Automated reports, data-driven slides |

---

## Quick Decision Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION TOOL SELECTOR                   │
└─────────────────────────────────────────────────────────────────┘

                         START HERE
                              │
                              ▼
              ┌───────────────────────────────┐
              │   Need AI to generate content │──YES──▶ PITCH (Gamma)
              │   from a topic/prompt?        │        (AI-powered)
              └───────────────────────────────┘
                              │ NO
                              ▼
              ┌───────────────────────────────┐
              │   Need programmatic/automated  │──YES──▶ AUTO (PptxGenJS)
              │   generation from data/API?   │        (Code-based)
              └───────────────────────────────┘
                              │ NO
                              ▼
              ┌───────────────────────────────┐
              │   Need version control +      │──YES──▶ SLIDES (Marp)
              │   simple Markdown workflow?   │        (Markdown-first)
              └───────────────────────────────┘
                              │ NO
                              ▼
              ┌───────────────────────────────┐
              │   Default: Start with SLIDES  │
              │   (fastest to get started)    │
              └───────────────────────────────┘
```

---

## Detailed Comparison

| Criterion | Marp | Gamma | PptxGenJS |
|-----------|------|-------|-----------|
| **Input** | Markdown | Natural language prompt | JSON/TypeScript |
| **Output** | HTML, PDF, PPTX | Web link, exportable | Native .pptx |
| **Offline** | ✅ Yes | ❌ No | ✅ Yes |
| **AI Generation** | ❌ Manual | ✅ Built-in | ❌ Manual |
| **Version Control** | ✅ Git-friendly | ❌ Cloud-hosted | ⚠️ Code only |
| **Data Integration** | ❌ Static | ❌ Manual | ✅ API/JSON |
| **Brand Templates** | ✅ CSS themes | ✅ Auto-themed | ✅ Custom masters |
| **Learning Curve** | Low | Very Low | Medium |
| **Dependency** | VS Code extension | Web service | Node.js |

---

## Use Case Matrix

### Choose MARP When

| Scenario | Why Marp |
|----------|----------|
| Technical documentation | Markdown source = version controlled |
| Conference talks | Developer-friendly, Git-trackable |
| Internal team updates | Quick edits, no design overhead |
| Multi-format needs | Same source → HTML + PDF + PPTX |
| Offline-first | No cloud dependency |

**Marp Workflow:**

```markdown
---
marp: true
theme: default
---

# Slide Title

- Bullet point
- Another point

---

# Next Slide
```

**Export:** Use `export_marp` tool or VS Code Marp extension

---

### Choose GAMMA When

| Scenario | Why Gamma |
|----------|-----------|
| Pitch decks for stakeholders | Professional polish, AI layouts |
| Rapid prototyping | Content → deck in minutes |
| Non-technical audiences | Beautiful defaults |
| Presentations from rough notes | AI structures the narrative |
| Client-facing deliverables | Publication-quality output |

**Gamma Workflow:**

1. Provide topic/outline to the AI assistant
2. the AI assistant applies Duarte methodology (see `gamma-presentations` skill)
3. the AI assistant generates structured markdown
4. Paste into gamma.app → AI creates polished deck

**Best Practice:** Use the AI assistant as presentation consultant first (audience, goal, S.T.A.R. moments), then generate.

---

### Choose PPTXGENJS When

| Scenario | Why PptxGenJS |
|----------|---------------|
| Automated reports | Data → slides pipeline |
| Dashboard exports | Charts from live data |
| Batch generation | 100 personalized decks |
| CI/CD integration | Generate on build |
| Custom branding | Full Slide Master control |

**PptxGenJS Workflow:**

```typescript
import { generateAndSavePresentation } from './pptxGenerator';

const slides = [
  { type: 'title', title: 'Q4 Report', subtitle: 'Automated' },
  { type: 'chart', chartType: 'bar', data: quarterlyData }
];

await generateAndSavePresentation(slides, {}, 'report.pptx');
```

**Best Practice:** Define slide templates, feed data, automate export.

---

## Decision Flowchart by Context

| Context | Recommended Tool | Rationale |
|---------|------------------|-----------|
| "I have rough notes" | **Gamma** | AI structures content |
| "I have structured data" | **PptxGenJS** | Programmatic charts/tables |
| "I have Markdown content" | **Marp** | Direct conversion |
| "I need it in 5 minutes" | **Gamma** | Fastest to polished |
| "I need it repeatable monthly" | **PptxGenJS** | Automation |
| "I need Git history" | **Marp** | Plain text source |
| "Audience is executives" | **Gamma** | Professional polish |
| "Audience is developers" | **Marp** | Code-adjacent workflow |
| "Audience is data analysts" | **PptxGenJS** | Chart-heavy |

---

## Hybrid Workflows

Sometimes the best approach combines tools:

### Marp → Gamma Refinement

1. Draft slides in Marp (fast iteration)
2. Export rough content
3. Refine in Gamma for final polish

### PptxGenJS + Marp Templates

1. Use Marp themes for branding reference
2. Replicate in PptxGenJS Slide Masters
3. Automate data-driven generation

### Gamma Consulting → PptxGenJS Automation

1. Use the AI assistant/Gamma for narrative structure
2. Implement as PptxGenJS templates
3. Feed data for automated generation

---

## Anti-Patterns

| ❌ Don't | ✅ Instead |
|----------|-----------|
| Use PptxGenJS for one-off deck | Use Marp (faster) |
| Use Marp for executive pitch | Use Gamma (better polish) |
| Use Gamma for automated reports | Use PptxGenJS (data integration) |
| Manually edit Gamma exports | Re-generate or use Marp |
| Copy-paste between tools | Define shared templates |

---

## Activation Triggers

- "which presentation tool", "what tool for slides"
- "marp vs gamma", "pptx vs gamma", "slides vs pitch"
- "use slides", "use pitch", "use auto"
- "create presentation" (then assess requirements)
- "best way to make slides"
- "presentation strategy"

---
