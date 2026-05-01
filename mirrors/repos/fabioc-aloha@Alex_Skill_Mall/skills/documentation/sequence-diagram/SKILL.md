---
type: skill
lifecycle: stable
inheritance: inheritable
name: sequence-diagram
description: Create UML sequence diagrams using sequencediagram.org syntax. Use when users request sequence diagrams, interaction diagrams, API flow visualizations, system communication flows, or ask to visualize message exchanges between components/actors. Outputs plain text (.txt) files compatible with sequencediagram.org for viewing and exporting.
tier: standard
applyTo: '**/*sequence*,**/*diagram*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Sequence Diagram Builder

Generate UML sequence diagrams using sequencediagram.org text syntax.

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
