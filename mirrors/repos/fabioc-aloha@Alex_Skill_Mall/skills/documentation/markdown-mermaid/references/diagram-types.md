# Mermaid Diagram Type Quick Reference

Per-type syntax reference for all 23 Mermaid diagram types. Complements the main SKILL.md's ATACCU workflow and quality gates.

> **Source**: mermaid-js/mermaid v11.x documentation. Recheck: <https://mermaid.js.org/syntax/>

---

## Type Selection Guide

| Category | Types | Best For |
| -------- | ----- | -------- |
| **Flow & Process** | flowchart, sequence, state, journey, gantt, kanban, timeline | Workflows, APIs, lifecycles |
| **Software & Architecture** | class, ER, C4, architecture-beta, block, packet, gitGraph | System design, schemas |
| **Data & Analysis** | pie, xychart, sankey, quadrant, radar-beta, treemap-beta | Metrics, proportions |
| **Conceptual** | mindmap, requirements, zenuml | Brainstorming, tracing |

---

## 1. Flowchart

```mermaid
flowchart LR     %% LR, TD/TB, BT, RL
    A[Rectangle] --> B(Rounded) --> C{Decision}
    C -->|Yes| D[(Database)]
    C -->|No| E((Circle))
```

**Arrows**: `-->` solid, `-.->` dotted, `==>` thick, `~~~` invisible, `<-->` bidirectional, `--o` circle end, `--x` cross end

**Shapes**: `[rect]` `(rounded)` `([stadium])` `[[subroutine]]` `[(cylinder)]` `((circle))` `{rhombus}` `{{hexagon}}` `[/parallelogram/]`

**Gotcha**: Word "end" in lowercase at line start breaks diagrams — use `"end"` or `End`

---

## 2. Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API
    User->>+API: POST /login
    API-->>-User: 200 JWT
```

**Messages**: `->>` sync, `-->>` async/return, `-)` fire-and-forget, `-x` error

**Blocks**: `loop`, `alt/else`, `opt`, `par/else`, `critical`, `break`

**Notes**: `Note over A,B: text` or `Note right of A: text`

---

## 3. Class Diagram

```mermaid
classDiagram
    class Animal {
        +String name
        #int age
        +makeSound()* void
    }
    Animal <|-- Dog : inherits
```

**Visibility**: `+` public, `-` private, `#` protected, `~` package

**Relations**: `<|--` inheritance, `*--` composition, `o--` aggregation, `-->` association, `..|>` realization

**Generics**: `class List~T~`

---

## 4. State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    state Processing {
        [*] --> Validating
        Validating --> Executing
    }
    Processing --> [*] : done
```

**Special**: `<<choice>>` for conditionals, `<<fork>>`/`<<join>>` for concurrency, `--` separator for parallel states

---

## 5. ER Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    CUSTOMER {
        string name PK
        string email UK
    }
```

**Cardinality**: `||` exactly one, `|o` zero or one, `}|` one or more, `}o` zero or more

**Line**: `--` identifying (solid), `..` non-identifying (dashed)

---

## 6. User Journey

```mermaid
journey
    title Onboarding Flow
    section Sign Up
        Create account: 5: User
        Verify email: 2: User
    section First Use
        Complete tutorial: 4: User, Admin
```

**Scores**: 1-5 (higher = better experience)

---

## 7. Gantt Chart

```mermaid
gantt
    title Sprint 12
    dateFormat YYYY-MM-DD
    section Dev
        Feature A :done, a1, 2026-01-01, 5d
        Feature B :active, a2, after a1, 3d
    section QA
        Testing :crit, t1, after a2, 2d
        Release :milestone, m1, after t1, 0d
```

**Tags**: `done`, `active`, `crit`, `milestone`

---

## 8. Pie Chart

```mermaid
pie showData
    title Market Share
    "Chrome" : 65
    "Safari" : 19
    "Firefox" : 8
```

---

## 9. Git Graph

```mermaid
gitGraph
    commit id: "init"
    branch develop
    commit id: "feature"
    checkout main
    merge develop tag: "v1.0"
```

**Orientation**: `LR` (default), `TB`, `BT`

**Commit types**: `NORMAL`, `HIGHLIGHT`, `REVERSE`

---

## 10. C4 Diagram

```mermaid
C4Context
    Person(user, "User", "End user")
    System(app, "App", "Main system")
    System_Ext(ext, "External", "Third party")
    Rel(user, app, "Uses")
    Rel(app, ext, "Calls")
```

**Levels**: `C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`

**Boundaries**: `Enterprise_Boundary`, `System_Boundary`, `Boundary`

---

## 11. Mindmap

```mermaid
mindmap
    Root Topic
        Branch A
            Leaf 1
            Leaf 2
        Branch B
            ((Circle leaf))
            [Square leaf]
```

**Shapes**: plain (default), `[square]`, `(rounded)`, `((circle))`, `))bang((`, `)cloud(`, `{{hexagon}}`

**Important**: Hierarchy is via indentation (like Python)

---

## 12. Timeline

```mermaid
timeline
    title Project History
    section Phase 1
        2024 : Planning
             : Team formed
        2025 : Development
    section Phase 2
        2026 : Launch
```

---

## 13. Sankey

```mermaid
sankey
Source,Target,Value
"Electricity",Residential,50
"Electricity",Commercial,30
"Gas",Industrial,40
```

**Config**: `linkColor`: `source`, `target`, `gradient`, or hex color

---

## 14. XY Chart

```mermaid
xychart
    title "Revenue"
    x-axis [Q1, Q2, Q3, Q4]
    y-axis "USD (M)" 0 --> 100
    bar [25, 40, 55, 80]
    line [20, 35, 50, 75]
```

---

## 15. Block Diagram

```mermaid
block
    columns 3
    Frontend["Frontend"]:2 space
    API["API Gateway"]
    Auth["Auth"] DB[("Database")]
    Frontend --> API
    API --> Auth
    API --> DB
```

**Width**: `name:2` spans 2 columns. `space` = empty cell.

---

## 16. Packet Diagram

```mermaid
packet
    0-15: "Source Port"
    16-31: "Dest Port"
    32-63: "Sequence Number"
```

---

## 17. Quadrant Chart

```mermaid
quadrantChart
    title Priority Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Do First
    quadrant-2 Delegate
    quadrant-3 Eliminate
    quadrant-4 Schedule
    Feature A: [0.2, 0.8]
    Feature B: [0.7, 0.9]
```

---

## 18. Kanban

```mermaid
kanban
    Todo
        task1[Write docs]@{ priority: 'High' }
    In Progress
        task2[API work]@{ assigned: 'dev1' }
    Done
        task3[Setup CI]
```

---

## 19. Architecture (Beta)

```mermaid
architecture-beta
    group cloud(cloud)[AWS]
        service web(server)[Web] in cloud
        service api(server)[API] in cloud
    end
    service db(database)[PostgreSQL]
    web:R --> L:api
    api:R --> L:db
```

**Icons**: `cloud`, `database`, `disk`, `internet`, `server` (or iconify)

**Sides**: `T`, `B`, `L`, `R`

---

## 20. ZenUML

```mermaid
zenuml
    @Actor User
    @Boundary App
    @Database DB
    User->App: Request
    App.process() {
        DB.query()
        return result
    }
```

---

## 21. Requirement Diagram

```mermaid
requirementDiagram
    requirement auth {
        id: 1
        text: System shall authenticate users
        risk: High
        verifymethod: Test
    }
    element login_page { type: interface }
    login_page - satisfies -> auth
```

---

## 22. Radar Chart (Beta)

```mermaid
radar-beta
    axis "Speed", "Cost", "Quality", "UX"
    curve "Option A"{8, 5, 7, 9}
    curve "Option B"{6, 9, 8, 7}
```

---

## 23. Treemap (Beta)

```mermaid
treemap-beta
    title Budget
    "Engineering"
        "Backend": 300
        "Frontend": 200
    "Marketing": 150
```

---

## Common Pitfalls by Type

| Type | Pitfall | Fix |
| ---- | ------- | --- |
| flowchart | `end` keyword breaks parser | Quote it: `"end"` |
| sequence | Missing `autonumber` | Always add for readability |
| gantt | Wrong `dateFormat` | Match your date strings exactly |
| mindmap | Wrong indentation | Use consistent spaces (hierarchy = indent) |
| timeline | Colons in text | Wrap in quotes or rephrase |
| C4 | Wrong boundary nesting | Context → Container → Component (never skip) |
| gitGraph | `main` not named | Add `%%{init: {'gitGraph': {'mainBranchName': 'main'}}}%%` |
| sankey | Commas in labels | Wrap in double quotes |
| architecture | Missing side annotations | Always specify `:R`, `:L`, `:T`, `:B` on edges |
