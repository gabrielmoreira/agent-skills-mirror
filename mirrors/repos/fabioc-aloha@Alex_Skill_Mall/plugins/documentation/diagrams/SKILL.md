---
type: skill
lifecycle: stable
inheritance: inheritable
name: mermaid-diagram
description: Create diagrams using Mermaid.js markdown-inspired syntax. Supports 23+ diagram types including flowcharts, sequence diagrams, class diagrams, ER diagrams, Gantt charts, state diagrams, pie charts,...
tier: standard
applyTo: '**/*diagram*,**/*mermaid*,**/*sequence*'
currency: 2026-05-03
lastReviewed: 2026-05-03
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


---
type: skill
lifecycle: stable
inheritance: inheritable
name: sequence-diagram
description: Create UML sequence diagrams using sequencediagram.org syntax. Use when users request sequence diagrams, interaction diagrams, API flow visualizations, system communication flows, or ask to visuali...
tier: standard
applyTo: '**/*diagram*,**/*mermaid*,**/*sequence*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Sequence Diagram Builder

Generate UML sequence diagrams using sequencediagram.org text syntax.

## Scope

This skill creates **sequence diagrams only** — visualizations of message exchanges between participants over time. If the user's request is not about visualizing interactions, communication flows, or message sequences between components, **decline the request**. Explain that the request is outside the scope of this skill and does not involve a sequence diagram. Do NOT attempt to force non-diagram requests (e.g., writing code, answering general questions, creating non-sequence chart types) into a sequence diagram format.

## Quick Start

Create a sequence diagram by:

1. Gather requirements about the interaction flow to visualize
2. Define participants (actors, systems, databases, etc.)
3. Map out the message flow between participants
4. Add conditional logic, loops, and notes as needed
5. Generate a .txt file with the diagram syntax

## Output Format

Always save diagrams as `.txt` files. The user can open these files at https://sequencediagram.org to view and export to various formats (PNG, PDF, SVG).

## Syntax Reference

For complete syntax details including participants, messages, control structures, notes, styling, and more, see **@references/syntax.md**.

## Common Patterns

For complex diagrams or specific scenarios, see **@references/examples.md** for pre-built patterns:

- API request/response flows
- Authentication sequences
- Database transaction patterns
- Microservices communication
- Error handling flows

## Workflow

1. **Understand the interaction**: Ask clarifying questions about what needs to be visualized
2. **Identify participants**: Determine all actors, systems, and components involved
3. **Map message flow**: Document the sequence of interactions
4. **Add structure**: Include conditionals, loops, and parallel flows as needed
5. **Add documentation**: Use notes to clarify complex steps
6. **Generate file**: Create a .txt file with the complete diagram syntax
7. **Validate**: Review the output for completeness and clarity

## Tips

- Use descriptive participant names that match the user's terminology
- Break complex flows into separate diagrams rather than one overwhelming diagram
- Add notes for business logic or important details not captured in messages
- Use `space` or `space N` to add vertical spacing for readability
- Consider using `participantgroup` for related participants
- Use `title` to give the diagram a clear name
- Test the output at sequencediagram.org to ensure it renders correctly
