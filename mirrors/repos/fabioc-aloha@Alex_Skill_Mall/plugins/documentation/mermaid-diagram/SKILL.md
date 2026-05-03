---
type: skill
lifecycle: stable
inheritance: inheritable
name: mermaid-diagram
description: Create diagrams using Mermaid.js markdown-inspired syntax. Supports 23+ diagram types including flowcharts, sequence diagrams, class diagrams, ER diagrams, Gantt charts, state diagrams, pie charts, git graphs, C4 architecture, mindmaps, timelines, and more. Outputs plain text (.mmd or .md) files renderable on GitHub, GitLab, and mermaid.live, and many more clients.
tier: standard
applyTo: '**/*mermaid*,**/*diagram*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Mermaid Diagram Builder

Generate diagrams using Mermaid.js text-based syntax for comprehensive visualization needs.

## Workflow

1. **Select diagram type** - Choose from 23+ types (see below)
2. **Review syntax** - Consult **@references/diagram-types.md** for that type
3. **Build diagram** - Follow syntax patterns from **@references/syntax.md**
4. **Add configuration** - Theme/styling if needed (see **@references/configuration.md**)
5. **Follow best practices** - Accessibility, testing (see **@references/best-practices.md**)
6. **Generate file** - Create .mmd or .md file

## Diagram Types

Mermaid supports **23+ diagram types** organized into categories:

- **Flow & Process**: Flowcharts, Sequence, State, User Journey, Gantt, Kanban, Timeline
- **Software & Architecture**: Class, ER, C4, Architecture (beta), Block, Packet, Git Graphs
- **Data & Analysis**: Pie, XY, Sankey, Quadrant, Radar (beta), Treemaps (beta)
- **Conceptual**: Mindmaps, Requirements, ZenUML

**See @references/diagram-types.md** for complete syntax, features, and use cases for each type.

## Configuration & Theming

- 5 built-in themes: `default`, `neutral`, `dark`, `forest`, `base`
- Custom theming via `themeVariables` (only with `base` theme)
- Per-diagram frontmatter configuration (recommended)
- Two rendering looks: `classic`, `handDrawn`
- Multiple layout algorithms: `dagre`, `elk`, tidy tree

**See @references/configuration.md** for complete options and examples.

## Syntax Fundamentals

All diagrams share common patterns:
- Declarative syntax starting with diagram type
- Direction control: `TB`, `LR`, `RL`, `BT`
- Comments: `%%`
- Styling: frontmatter config or inline styles
- Special character handling

**See @references/syntax.md** for detailed syntax patterns.

## Best Practices

**Key principles**:
- **Always** add `accTitle` and `accDescr` for accessibility
- Use frontmatter for configuration (not deprecated directives)
- Break complex diagrams into smaller, focused ones (<15 nodes)
- Test at https://mermaid.live before finalizing
- Quote reserved words like "end"

**See @references/best-practices.md** for comprehensive guidance, common pitfalls, and optimization tips.

## Output Format

Save as `.mmd` (Mermaid) or `.md` (Markdown) files:
- View directly on GitHub and GitLab
- Edit at https://mermaid.live
- Render in VS Code, Confluence, Notion, GitBook, Docusaurus
- Integrate into CI/CD pipelines

## Resources

- **Live Editor**: https://mermaid.live (test and export)
- **Official Docs**: https://mermaid.js.org
- **Repository**: https://github.com/mermaid-js/mermaid
- **Icons**: https://icones.js.org (for mindmaps/architecture)

## References

- **@references/diagram-types.md** - Complete syntax for all 23+ diagram types
- **@references/configuration.md** - Theming, configuration, and customization
- **@references/syntax.md** - Fundamental syntax patterns across all types
- **@references/best-practices.md** - Best practices, pitfalls, and optimization
