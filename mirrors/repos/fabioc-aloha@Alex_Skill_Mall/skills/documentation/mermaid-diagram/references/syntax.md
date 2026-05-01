# Mermaid Syntax Fundamentals

General syntax patterns and conventions that apply across all Mermaid diagram types.

**Source**: mermaid-js/mermaid repository (packages/mermaid/src/docs/intro/syntax-reference.md)

---

## Table of Contents

1. [Basic Syntax Rules](#basic-syntax-rules)
2. [Direction and Orientation](#direction-and-orientation)
3. [Comments and Annotations](#comments-and-annotations)
4. [Special Characters](#special-characters)
5. [Styling Syntax](#styling-syntax)
6. [Arrow and Link Types](#arrow-and-link-types)
7. [Text Formatting](#text-formatting)
8. [Subgraphs and Grouping](#subgraphs-and-grouping)
9. [Common Patterns](#common-patterns)

---

## Basic Syntax Rules

### Diagram Declaration

All diagrams begin with a type declaration:

```
flowchart TD
sequenceDiagram
classDiagram
stateDiagram-v2
erDiagram
gantt
pie
mindmap
timeline
sankey
gitGraph
```

### Code Block Format

```
[diagram-type] [direction?]
    [diagram content]
```

### Line Structure

- Each statement typically on its own line
- Indentation improves readability but not required (except mindmaps, treemaps)
- Unknown words break diagrams
- Parameters that fail do so silently

### Comments

Start with `%%` and ignore everything after on that line:

```
%% This is a comment
flowchart TD
    A --> B  %% Another comment
```

**Warning**: Avoid `{}` in comments as they confuse the parser.

---

## Direction and Orientation

### Flowcharts and Related Diagrams

```
flowchart TB   %% Top to Bottom (default)
flowchart TD   %% Top Down (same as TB)
flowchart BT   %% Bottom to Top
flowchart LR   %% Left to Right
flowchart RL   %% Right to Left
```

### Examples

**Vertical flow**:
```
flowchart TB
    A --> B --> C
```

**Horizontal flow**:
```
flowchart LR
    A --> B --> C
```

### Per-Subgraph Direction

```
flowchart TB
    subgraph sub1
        direction LR
        A --> B
    end
    subgraph sub2
        direction RL
        C --> D
    end
```

### ER Diagram Direction

```
%%{init: {'er': {'layoutDirection': 'LR'}}}%%
erDiagram
    CUSTOMER ||--o{ ORDER : places
```

### Git Graph Orientation

```
%%{init: {'gitGraph': {'orientation': 'TB'}}}%%
gitGraph
    commit
```

---

## Comments and Annotations

### Line Comments

```
%% Full line comment
flowchart TD
    A --> B  %% Inline comment
```

### Block Documentation

While Mermaid doesn't have multi-line comments, use multiple single-line comments:

```
%% This diagram shows the authentication flow
%% including error handling and session management
%% Last updated: 2024-01-15
flowchart TD
    A --> B
```

### Notes (Sequence Diagrams)

```
Note right of Alice: Text here
Note over Alice,Bob: Spans participants
Note left of Alice: Left side note
```

### Notes (Class Diagrams)

```
note "General note"
note for ClassName "Specific note for class"
```

---

## Special Characters

### Reserved Words

**"end"** - Must be wrapped in quotes or brackets:

```
%% WRONG - breaks diagram
flowchart TD
    start --> end

%% CORRECT
flowchart TD
    start --> "end"
    start --> [end]
    start --> End  %% Capitalized
```

### Text Escaping

**With spaces or special characters**:
```
flowchart TD
    A["Node with spaces"]
    B["Node with: special chars"]
```

**With quotes inside**:
```
flowchart TD
    A["Text with \"quotes\" inside"]
```

**With other node syntax**:
```
flowchart TD
    A["This [text] looks like a node"]
```

### Unicode Support

```
flowchart TD
    A["This ❤ Unicode 你好 🎉"]
```

### Markdown in Strings

Use backticks with escaped quotes:

```
flowchart TD
    A["\`**Bold** _italic_\`"]
```

### Special First Characters (Flowcharts)

Starting with certain characters creates edge types:

```
A---oB   %% Circle edge (o at start)
A---xB   %% Cross edge (x at start)

%% To avoid, use space or capitalize
A--- oB
A---OB
```

---

## Styling Syntax

### Frontmatter Configuration (YAML)

**Recommended** for per-diagram configuration:

```yaml
---
title: Diagram Title
config:
  theme: forest
  themeVariables:
    primaryColor: '#BB2528'
---
flowchart TD
    A --> B
```

### Inline Styles (Flowcharts)

```
style nodeId fill:#f9f,stroke:#333,stroke-width:4px
```

### CSS Classes

**Define class**:
```
classDef className fill:#f9f,stroke:#333,stroke-width:4px
```

**Apply to node**:
```
class nodeId className
class nodeId1,nodeId2 className
```

### Class in Definition

```
flowchart TD
    A:::className --> B
```

### Styling Properties

Common properties:
- `fill` - Background color
- `stroke` - Border color
- `stroke-width` - Border width
- `color` - Text color
- `stroke-dasharray` - Dashed border (e.g., "5 5")

### Examples

**Red box with thick border**:
```
style A fill:#ff0000,stroke:#000000,stroke-width:4px
```

**Dashed border**:
```
style A stroke-dasharray: 5 5
```

**Reusable class**:
```
classDef important fill:#f00,stroke:#000,stroke-width:3px
class A,B,C important
```

---

## Arrow and Link Types

### Flowchart Arrows

```
A-->B     Solid arrow
A---B     Solid line (no arrow)
A-.->B    Dotted arrow
A-.-B     Dotted line
A==>B     Thick arrow
A===B     Thick line
A~~~B     Invisible link
A--oB     Circle end
A--xB     Cross end
A<-->B    Bidirectional
Ao--oB    Circle both ends
```

### With Text

```
A-->|label| B
A-- label -->B
A-- label text -->B
```

### Sequence Diagram Arrows

```
A->>B     Solid arrow (sync)
A-->>B    Dotted arrow (async)
A-)B      Async without arrow
A-xB      Error/failure (cross)
A-->B     Return message
```

### Class Diagram Relationships

```
ClassA <|-- ClassB     Inheritance
ClassA *-- ClassB      Composition
ClassA o-- ClassB      Aggregation
ClassA --> ClassB      Association
ClassA -- ClassB       Link
ClassA ..> ClassB      Dependency
ClassA ..|> ClassB     Realization
```

### ER Diagram Relationships

```
ENTITY1 ||--o{ ENTITY2    One to zero or more
ENTITY1 ||--|| ENTITY2    One to one
ENTITY1 }o--o{ ENTITY2    Zero or more to zero or more
ENTITY1 }|--|{ ENTITY2    One or more to one or more
```

Identification:
- `--` Solid (identifying)
- `..` Dashed (non-identifying)

---

## Text Formatting

### Basic Formatting

Some diagrams support basic formatting:

```
**bold text**
*italic text*
`code text`
```

### Markdown Strings (New Syntax)

In supported diagrams (flowcharts, mindmaps):

```
flowchart TD
    A["\`**Bold** _italic_ text\`"]
```

### HTML (When Enabled)

With `htmlLabels: true`:

```
flowchart TD
    A["<b>Bold</b> <i>italic</i>"]
```

### Line Breaks

**In text**:
```
flowchart TD
    A["Line 1<br/>Line 2<br/>Line 3"]
```

**In sequence diagrams**:
```
User->System: First line\nSecond line\nThird line
```

### Special Formatting (SequenceDiagram.org syntax)

In sequence-diagram skill, not Mermaid:
```
"<color:#red>Red text</color>"
"<size:20>Large text</size>"
```

---

## Subgraphs and Grouping

### Flowchart Subgraphs

```
flowchart TB
    subgraph id1 [Title]
        A --> B
    end
    subgraph id2 [Another Group]
        C --> D
    end
    id1 --> id2
```

### Nested Subgraphs

```
flowchart TB
    subgraph outer [Outer Group]
        subgraph inner [Inner Group]
            A --> B
        end
    end
```

### Subgraph Direction

```
flowchart TB
    subgraph sub1
        direction LR
        A --> B
    end
```

### State Diagram Composite States

```
stateDiagram-v2
    state CompositeName {
        [*] --> SubState1
        SubState1 --> SubState2
        SubState2 --> [*]
    }
```

### Sections (Gantt, Timeline)

```
gantt
    section Section Name
        Task 1 :t1, 2024-01-01, 3d
    section Another Section
        Task 2 :t2, 2024-01-04, 2d
```

```
timeline
    title Timeline
    section Period 1
        2020 : Event A
    section Period 2
        2021 : Event B
```

### Participant Groups (Sequence)

Not in Mermaid syntax, but available in sequencediagram.org:
```
participantgroup #lightblue Backend
    participant ServiceA
    participant ServiceB
end
```

---

## Common Patterns

### Node Shapes (Flowcharts)

```
A[Rectangle]
B(Rounded)
C([Stadium])
D[[Subroutine]]
E[(Cylinder)]
F((Circle))
G>Asymmetric]
H{Rhombus}
I{{Hexagon}}
J[/Parallelogram/]
K[\Trapezoid\]
L[/Trapezoid Alt\]
```

### Modern Shape Syntax (v11.3.0+)

```
A@{ shape: rect, label: "Text" }
B@{ shape: circle }
C@{ shape: hexagon, label: "Hex" }
```

### Visibility Modifiers (Class Diagrams)

```
+publicMethod()     Public
-privateMethod()    Private
#protectedMethod()  Protected
~packageMethod()    Package
```

### Classifiers (Class Diagrams)

```
*abstractMethod()   Abstract
$staticMethod()     Static
```

### Cardinality (ER Diagrams, Class Diagrams)

```
Customer "1" --> "*" Order
Order "1" --> "1..5" LineItem
```

### Metadata Syntax

**Flowcharts (modern)**:
```
A@{ icon: "fa:user", img: "url" }
```

**Gantt**:
```
Task :done, t1, 2024-01-01, 3d
Task :active, crit, t2, after t1, 2d
```

**Kanban**:
```
task[Description]@{ assigned: 'user', priority: 'High' }
```

---

## Data Formats

### Dates (Gantt)

```
dateFormat YYYY-MM-DD
Task1 :2024-01-01, 3d
Task2 :2024-01-04, 2024-01-10
```

### Time (Gantt)

```
dateFormat HH:mm
Task :09:00, 2h
```

### Numbers (Pie, Sankey, XY)

```
pie
    "Category A" : 42.5
    "Category B" : 57.5
```

### CSV (Sankey)

```
sankey
Source,Target,Value
A,B,10
B,C,5
```

### Coordinates (Quadrant)

```
quadrantChart
    Item A: [0.3, 0.7]  %% x, y from 0 to 1
```

---

## Best Practices

1. **Use comments** to document complex diagrams
2. **Quote reserved words** like "end"
3. **Escape special characters** in labels
4. **Use consistent indentation** for readability
5. **Prefer frontmatter** over directives for configuration
6. **Test syntax** at mermaid.live before finalizing
7. **Use subgraphs** to organize large diagrams
8. **Apply consistent naming** conventions
9. **Add accessibility** metadata (accTitle, accDescr)
10. **Validate output** in target rendering environment

---

## Syntax Validation

### Testing

Use https://mermaid.live to:
- Test syntax before committing
- Preview rendering
- Export to various formats
- Share with collaborators

### Common Errors

**Unquoted reserved words**:
```
%% WRONG
flowchart TD
    start --> end

%% RIGHT
flowchart TD
    start --> "end"
```

**Missing spaces**:
```
%% WRONG
A-->|text|B

%% RIGHT (for clarity)
A -->|text| B
```

**Invalid characters in IDs**:
```
%% WRONG
node-with-dashes --> other

%% RIGHT
nodeWithCamelCase --> other
node_with_underscores --> other
```

---

## Examples

### Complete Flowchart

```
---
title: User Registration Flow
config:
  theme: default
---
flowchart TB
    accTitle: User Registration Process
    accDescr: Complete user registration workflow with validation

    Start([Start]) --> Input[Enter Details]
    Input --> Valid{Valid?}

    Valid -->|Yes| Check{Email Exists?}
    Valid -->|No| Error1[Show Validation Error]

    Check -->|No| Create[Create Account]
    Check -->|Yes| Error2[Email Already Registered]

    Create --> Email[Send Confirmation]
    Email --> End([Complete])

    Error1 --> Input
    Error2 --> Input

    classDef errorStyle fill:#f99,stroke:#f00
    class Error1,Error2 errorStyle
```

### Complete Sequence Diagram

```
---
config:
  theme: forest
---
sequenceDiagram
    accTitle: Payment Processing Flow

    actor User
    participant App
    participant API
    participant PaymentGW
    participant DB

    User->>App: Checkout
    App->>API: POST /payment

    activate API
    API->>PaymentGW: Process card
    PaymentGW-->>API: Success

    API->>DB: Save transaction
    DB-->>API: Confirmed

    API-->>App: Payment complete
    deactivate API

    App-->>User: Show confirmation
```

---

## Summary

**Key Concepts**:
- Declarative syntax starting with diagram type
- Direction control (TB, LR, RL, BT)
- Comments with `%%`
- Quote reserved words
- Multiple arrow/link types
- Styling via frontmatter or inline
- Subgraphs for organization
- Accessibility with accTitle/accDescr

For diagram-specific syntax, see **diagram-types.md**.
For configuration options, see **configuration.md**.
For best practices, see **best-practices.md**.
