---
name: "markdown-mermaid"
description: "Author Mermaid diagrams and markdown visualizations following the mandatory init template, pastel palette, and ATACCU workflow. Use when authoring documentation with diagrams, troubleshooting Mermaid rendering, choosing diagram types, or comparing Mermaid/PlantUML/D2/Graphviz."
lastReviewed: 2026-05-26
---

# Markdown & Mermaid

> Clear documentation through visual excellence

A skill for markdown authoring, Mermaid diagramming, multi-tool visualization, VS Code integration, and cross-platform rendering consistency.

## When to Use

- Creating technical documentation with diagrams
- Choosing the right diagramming tool for your audience
- Troubleshooting Mermaid rendering issues
- Styling markdown previews in VS Code
- Converting unicode escapes to proper emojis
- Enterprise documentation with visual standards
- **Interactive diagrams in VS Code chat** (1.109+)

---

## ⚠️ MANDATORY: Start Every Diagram With This Template

**Do NOT write Mermaid code without this template.** Copy-paste first, then customize:

```text
%%{init: {'theme': 'base', 'themeVariables': {'lineColor': '#57606a', 'primaryColor': '#ddf4ff', 'primaryBorderColor': '#0969da', 'primaryTextColor': '#1f2328', 'edgeLabelBackground': '#ffffff'}}}%%
flowchart LR
    A[Input]:::blue --> B[Process]:::purple --> C[Output]:::green

    classDef blue fill:#ddf4ff,color:#0550ae,stroke:#80ccff
    classDef green fill:#d3f5db,color:#1a7f37,stroke:#6fdd8b
    classDef purple fill:#d8b9ff,color:#6639ba,stroke:#bf8aff
    classDef gold fill:#fff8c5,color:#9a6700,stroke:#d4a72c
    classDef red fill:#ffebe9,color:#cf222e,stroke:#f5a3a3
    classDef neutral fill:#eaeef2,color:#24292f,stroke:#d0d7de

    linkStyle default stroke:#57606a,stroke-width:1.5px
```

**Three required components:**

1. **Init directive** (line 1) — Sets theme, colors, white edge label background
2. **classDef** — Semantic colors for all node types
3. **linkStyle default** — Gray arrows at 1.5px width

| Color Class | Use For | Example |
| ----------- | ------- | ------- |
| `:::blue` | Input, source, start | `A[Audio]:::blue` |
| `:::green` | Output, result, data | `C[Transcript]:::green` |
| `:::purple` | Processing, model | `B[WhisperX]:::purple` |
| `:::gold` | Decision, condition | `D{Valid?}:::gold` |
| `:::red` | Error, warning | `E[Failed]:::red` |
| `:::neutral` | Context, optional | `F[Cache]:::neutral` |

---

## Mandatory Workflow: ATACCU

**Every Mermaid diagram MUST follow this 6-step protocol.** No exceptions — this prevents forgotten palettes, broken layouts, and inconsistent styling.

| Step | Action | What to Do |
| ---- | ------ | ---------- |
| **A** | **Analyze** | What data/process am I visualizing? Who is the audience? What diagram type fits? |
| **T** | **Think** | Which layout pattern? (Medallion/Lineage/Pipeline) How many nodes? Will it be too wide/tall? |
| **A** | **Apply** | **COPY THE TEMPLATE ABOVE** — init directive + classDef + linkStyle. No exceptions. |
| **C** | **Create** | Write the Mermaid code. Every node gets `:::className`. Every flowchart gets `linkStyle default`. |
| **C** | **Check** | Render the diagram. Verify: pastels (not saturated), layout (not lopsided), labels (readable), arrows (gray #57606a). |
| **U** | **Update** | Write the final diagram into the target `.md` file. Add `**Figure N:** *description*` label. |

### Pre-Flight Checklist (Steps A-T-A)

Before writing any Mermaid code, answer these:

```text
□ Diagram type selected (flowchart/sequence/gantt/quadrant/etc.)
□ Layout direction chosen (LR preferred for flow, TD for hierarchy)
□ Subgraph strategy decided (Medallion vs Lineage vs Pipeline)
□ Color assignments mapped (what color = what meaning)
□ Multi-line node labels use <br/> NOT \n
```

### Quality Gate (Steps C-C-U)

After creating the diagram, verify ALL of these:

```text
□ Init directive is FIRST line inside mermaid block
□ edgeLabelBackground is '#ffffff' (white background for edge labels)
□ ALL nodes have style/classDef (no unstyled nodes)
□ Colors are GitHub Pastel v2 (NOT saturated: no #51cf66, #339af0, #fab005)
□ linkStyle default stroke:#57606a,stroke-width:1.5px (flowcharts)
□ Node labels use <br/> for line breaks, NOT \n
□ Diagram rendered and visually inspected
□ No dimension > 3x the other (use subgroups to balance)
□ Figure label added below diagram block
□ Written to target file (not just shown in chat)
```

### Common Violations This Prevents

| Violation | ATACCU Step That Catches It |
| --------- | -------------------------- |
| Saturated colors instead of pastels | **Apply Skills** — load palette first |
| Missing init directive | **Apply Skills** — it's step 3 |
| `edgeLabelBackground: 'transparent'` used | **Apply Skills** — use `'#ffffff'` (white background) |
| `\n` in node labels (renders as literal text) | **Create** — use `<br/>` for line breaks |
| Missing linkStyle | **Create** — every flowchart needs it |
| Lopsided layout (7-way fan-out) | **Think** — choose layout pattern |
| Diagram only in chat, not in file | **Update** — write to `.md` file |
| No figure label | **Update** — add label |

---

## VS Code 1.109+ Native Chat Rendering

VS Code 1.109 introduces **native Mermaid rendering in chat** via the `renderMermaidDiagram` tool. This is a **deferred tool**: call `tool_search` for "mermaid" to load it before invocation.

### When to Use Native Rendering

When creating diagrams **in Copilot Chat** (not markdown files), use the native tool for:

- **Interactive exploration**: Pan, zoom, and full-screen viewing
- **Immediate feedback**: See diagrams without switching to markdown preview
- **Iterative refinement**: Quick edits with instant re-render
- **Copy source**: Extract the Mermaid code for documentation

### Usage Pattern

```text
User: Create a sequence diagram showing OAuth flow

Alex: [uses renderMermaidDiagram tool]
       → Interactive diagram appears in chat
       → User can pan/zoom/fullscreen
       → "Copy source" extracts code for docs
```

### When NOT to Use

- **Documentation authoring**: Use markdown code blocks for `.md` files
- **GitHub rendering**: Embed Mermaid in markdown for native GitHub support
- **Presentations**: Export to image formats or use D2

### Combined Workflow

1. **Design in chat**: Use `renderMermaidDiagram` for rapid iteration
2. **Finalize**: Copy the Mermaid source code
3. **Document**: Paste into markdown file with ` ```mermaid ` code fence

---

## Assets

| File | Purpose |
| ---- | ------- |
| `markdown-light.css` | VS Code preview styling |
| `polish-mermaid-setup.prompt.md` | Interactive Mermaid configuration helper |

**Setup:** Copy CSS to `.vscode/`, add `"markdown.styles": [".vscode/markdown-light.css"]` to settings.

**Mermaid Config:** Run the "Polish Mermaid Setup" prompt to configure Mermaid rendering for your VS Code environment.

---

## Markdown Best Practices

### Document Structure Template

```markdown
# Title

> Brief description or tagline

---

## Overview

Introductory paragraph explaining the purpose.

---

## Section 1

Content with proper formatting.

### Subsection 1.1

More detailed content.

---

## Tables

**Table N:** *Description of what the table shows*

| Column 1 | Column 2 |
| -------- | -------- |
| Data     | Data     |

---

## Diagrams

` ` `mermaid
flowchart LR
    A --> B
` ` `

**Figure N:** *Description of what the diagram shows*

---

*Footer or closing statement*
```

### Figure and Table Conventions

**Mandatory Labeling**: Every diagram and table MUST have a label:

```markdown
**Figure 1:** *Description in italics*
**Table 1:** *Description in italics*
```

- **Numbering**: Sequential within document, reset per document
- **Placement**: Label immediately follows the diagram/table block

---

## 🏷️ Shields.io Badges

Badges use [Shields.io](https://shields.io). URL structure: `https://img.shields.io/badge/{LABEL}-{MESSAGE}-{COLOR}?{OPTIONS}`

```markdown
[![Alt Text](https://img.shields.io/badge/Label-Message-color?style=for-the-badge&logo=iconname&logoColor=white)](#)
```

| Style | Parameter |
| ----- | --------- |
| Flat | `style=flat` |
| **For-the-Badge** | `style=for-the-badge` |

| Encode | As |
| ------ | -- |
| Space | `_` or `%20` |
| Dash | `--` |
| Underscore | `__` |

Icons from [Simple Icons](https://simpleicons.org/) via `logo=iconname&logoColor=white`. Colors: `blue`, `green`, `gold`, `red`, `purple`, or custom hex without `#`.

---

### Emoji Usage

**Recommended** (renders reliably across GitHub, VS Code, and terminal): Use actual emoji characters, not HTML entities or unicode escapes.

| Good ✅ | Bad ❌ |
| ------- | ------ |
| `# 🧠 Brain` | `# &#x1F9E0; Brain` |
| `**💻 Local**` | `**\ud83d\udcbb Local**` |

---


## Deep-Dive Reference

The following sections moved to [`references/mermaid-reference.md`](references/mermaid-reference.md) to keep this skill body lean. Consult on demand:

- **Diagram Tool Selection Framework** (Mermaid vs PlantUML vs D2 vs Graphviz; communication-goal + audience + platform decision tree)
- **Multi-Tool Ecosystem** (tool comparison matrix, VS Code extension setup, syntax examples per tool)
- **Mermaid Diagram Reference** (Pastel v2 template, diagram types, node shapes, edge styles, color palettes — GitHub Pastel v2, Fishbowl Pastel — per-diagram theming, classDef styles, subgraph styling, Gantt + sequence theming)
- **Visual Design Principles** (color psychology, effectiveness criteria, accessibility standards)
- **Parser Pitfalls** (P1–P9: quoted labels, HTML entities, edge-list operator, cylinder shape, stateDiagram-v2 classDef, MD060 spacing, MD056 pipes, MD028 blockquotes, MD040 language)
- **Common Pitfalls & Solutions** (Unicode escapes / broken emojis, emoji mapping table, edge label dark background, multi-line node labels, dark backgrounds, disproportionate layouts, named layout patterns, subgraph title truncation, classDiagram-specific pitfalls, architecture-beta pitfalls, cross-diagram syntax compatibility, reserved words, XY chart coloring, C4 limitations, blockquote tall boxes)
- **Diagram Audit Methodology** (4-step enumerate / categorize / batch fix / validate)
- **Quality Checklist** (before-committing + diagram-review + don't-over-simplify)
## 📚 References

### Official Documentation

- [Mermaid Documentation](https://mermaid.js.org/intro/)
- [Mermaid Live Editor](https://mermaid.live/)
- [PlantUML Documentation](https://plantuml.com/)
- [Graphviz Documentation](https://graphviz.org/documentation/)
- [D2 Documentation](https://d2lang.com/)
- [Shields.io](https://shields.io/)

### VS Code Resources

- [VS Code Markdown Guide](https://code.visualstudio.com/docs/languages/markdown)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)

### Visual Design Theory

- Tufte, E.R. - *The Visual Display of Quantitative Information*
- Cairo, A. - *The Functional Art*
- Knaflic, C.N. - *Storytelling with Data*

## Mode Fragility Reference

Several Mermaid modes fail silently on colons and special characters. Default to `flowchart` for arbitrary text content.

| Mode | Status | Constraint |
|------|--------|------------|
| `flowchart` | Safe | None — handles any content |
| `sequenceDiagram` | Safe | Standard message format |
| `classDiagram` | Safe | Standard notation |
| `erDiagram` | Safe | Standard notation |
| `stateDiagram` | Caution | Colons in state names |
| `journey` | Caution | Score format sensitive |
| `timeline` | Fragile | No colons in events; `:` is separator |
| `gitGraph` | Fragile | Long chains with quoted colon-tags break |
| `gantt` | Fragile | `dateFormat HH:mm` mis-parses task lines |

**Rule**: If your labels contain colons, times (`HH:MM`), or complex text, use `flowchart` and structure with subgraphs instead.

**Debug silent failures**: Check browser console, simplify content, test incrementally, try flowchart — if it works in flowchart, the mode is the problem.

## Falsifiability

- This skill is wrong if diagrams authored per these patterns fail to render in GitHub or VS Code preview
- The syntax guidance is stale if it conflicts with the current Mermaid.js spec (check mermaid.js.org/changelog)
- The mode-fragility warnings are not earning tokens if Mermaid resolves the documented rendering bugs in a future release
