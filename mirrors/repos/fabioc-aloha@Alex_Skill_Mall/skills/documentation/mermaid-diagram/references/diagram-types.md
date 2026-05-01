# Mermaid Diagram Types Reference

Complete syntax and features for all Mermaid diagram types.

**Source**: mermaid-js/mermaid repository (packages/mermaid/src/docs/syntax/)

---

## Table of Contents

1. [Flowcharts](#1-flowcharts)
2. [Sequence Diagrams](#2-sequence-diagrams)
3. [Class Diagrams](#3-class-diagrams)
4. [State Diagrams](#4-state-diagrams)
5. [Entity Relationship Diagrams](#5-entity-relationship-diagrams)
6. [User Journey Diagrams](#6-user-journey-diagrams)
7. [Gantt Charts](#7-gantt-charts)
8. [Pie Charts](#8-pie-charts)
9. [Requirement Diagrams](#9-requirement-diagrams)
10. [Git Graphs](#10-git-graphs)
11. [C4 Diagrams](#11-c4-diagrams)
12. [Mindmaps](#12-mindmaps)
13. [Timeline Diagrams](#13-timeline-diagrams)
14. [Sankey Diagrams](#14-sankey-diagrams)
15. [XY Charts](#15-xy-charts)
16. [Block Diagrams](#16-block-diagrams)
17. [Packet Diagrams](#17-packet-diagrams)
18. [Quadrant Charts](#18-quadrant-charts)
19. [Kanban Boards](#19-kanban-boards)
20. [Architecture Diagrams](#20-architecture-diagrams)
21. [ZenUML Sequence Diagrams](#21-zenuml-sequence-diagrams)
22. [Radar Charts](#22-radar-charts)
23. [Treemap Diagrams](#23-treemap-diagrams)

---

## 1. Flowcharts

**Declaration**: `flowchart` or `graph`

**Direction Options**: `LR` (Left to Right), `TD`/`TB` (Top to Bottom), `BT` (Bottom to Top), `RL` (Right to Left)

### Node Shapes

```
A[Rectangle]
B(Rounded)
C([Stadium])
D[[Subroutine]]
E[(Cylinder/Database)]
F((Circle))
G>Asymmetric]
H{Rhombus/Decision}
I{{Hexagon}}
J[/Parallelogram/]
K[\Trapezoid\]
L[/Trapezoid Alt\]
```

### Modern Syntax (v11.3.0+)

```
A@{ shape: rect, label: "Text" }
B@{ shape: circle, icon: "fa:user" }
C@{ shape: doc, img: "url" }
```

### Arrow Types

```
A-->B    Solid arrow
A---B    Solid line
A-.->B   Dotted arrow
A-.-B    Dotted line
A==>B    Thick arrow
A===B    Thick line
A~~~B    Invisible link
A--oB    Circle end
A--xB    Cross end
A<-->B   Bidirectional
```

### Text on Edges

```
A-->|Label text| B
A-- Label text -->B
```

### Subgraphs

```
flowchart TB
    subgraph id1 [Title]
        direction LR
        A-->B
    end
    subgraph id2 [Another]
        C-->D
    end
    id1 --> id2
```

### Styling

```
classDef className fill:#f9f,stroke:#333,stroke-width:4px
class nodeId className
style nodeId fill:#f9f,stroke:#333
```

### Common Use Cases

- Decision flows with diamond nodes for branching logic
- Process workflows showing sequential steps
- Data flow diagrams with specialized shapes
- System architecture visualization
- Timeline representation

### Important Notes

- Word "end" in lowercase at start breaks diagrams; use "End", "END", or quotes
- Subgraphs can be nested and have individual direction control
- Edge IDs enable individual styling and animation
- Modern syntax supports Font Awesome icons and images

**Example**:
```
flowchart LR
    Start[Start Process] --> Check{Valid Input?}
    Check -->|Yes| Process[Process Data]
    Check -->|No| Error[Show Error]
    Process --> DB[(Database)]
    DB --> End[Complete]
    Error --> End
```

---

## 2. Sequence Diagrams

**Declaration**: `sequenceDiagram`

### Participants

```
participant A
participant B as "Alias Name"
actor User
```

**Specialized Types**: `Actor`, `Boundary`, `Control`, `Entity`, `Database`, `Collections`, `Queue`

### Messages

```
A->>B: Sync message (solid arrow)
A-->>B: Async message (dotted arrow)
A-)B: Async without arrow
A-xB: Error/failure (cross)
A-->B: Return message
```

### Activation

```
activate A
A->>B: Message
deactivate A

%% Shorthand
A->>+B: Activate B
B-->>-A: Deactivate B
```

### Control Structures

```
loop Every minute
    A->>B: Check status
end

alt Success case
    A->>B: Process
else Error case
    A->>B: Handle error
end

opt Condition met
    A->>B: Optional step
end

par Parallel
    A->>B: Thread 1
else
    A->>C: Thread 2
end

critical Transaction
    A->>B: Update
end

break On error
    A->>B: Critical error
end
```

### Notes

```
Note left of A: Note text
Note right of A: Note text
Note over A: Single participant
Note over A,B: Multiple participants
```

### Actor Creation/Destruction

```
A->>+B: Create
create participant B
destroy B
```

### Common Use Cases

- API request/response flows with error handling
- Transaction processes with rollback scenarios
- Multi-actor communication with conditional logic
- Workflow lifecycle tracking
- Parallel service calls and asynchronous messaging

**Example**:
```
sequenceDiagram
    actor User
    participant App
    participant API
    participant DB

    User->>App: Login Request
    App->>API: POST /auth
    activate API
    API->>DB: Verify credentials
    DB-->>API: User found
    API-->>App: JWT Token
    deactivate API
    App-->>User: Login Success
```

---

## 3. Class Diagrams

**Declaration**: `classDiagram`

### Class Definition

```
class ClassName {
    +String attribute
    -int privateAttr
    #protectedMethod()
    ~packageMethod()
    +publicMethod()
}

%% Or inline
ClassName : +String attribute
ClassName : +method()
```

### Visibility

- `+` Public
- `-` Private
- `#` Protected
- `~` Package/Internal

### Classifiers

- `*` Abstract
- `$` Static

### Relationships

```
ClassA <|-- ClassB       Inheritance
ClassA *-- ClassB        Composition
ClassA o-- ClassB        Aggregation
ClassA --> ClassB        Association
ClassA -- ClassB         Link
ClassA ..> ClassB        Dependency
ClassA ..|> ClassB       Realization
ClassA ..* ClassB        Aggregation (dependency)
```

### Cardinality

```
Customer "1" --> "*" Order
Order "1" --> "1..5" LineItem
```

### Annotations

```
class Service {
    <<interface>>
    +method()
}

class AbstractClass {
    <<abstract>>
    +abstractMethod()*
}

class Enum {
    <<enumeration>>
    VALUE1
    VALUE2
}
```

### Generic Types

```
class List~T~ {
    +add(T item)
    +get(int idx) T
}
```

### Common Use Cases

- Software architecture modeling
- Data structure design
- API documentation
- Database schema modeling
- Design pattern implementation

**Example**:
```
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +meow()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

---

## 4. State Diagrams

**Declaration**: `stateDiagram-v2`

### Basic Syntax

```
stateDiagram-v2
    [*] --> State1
    State1 --> State2 : Transition
    State2 --> [*]
```

### State Descriptions

```
state "Long Description" as s2
```

### Composite States

```
state Active {
    [*] --> Processing
    Processing --> Complete
    Complete --> [*]
}
```

### Choice

```
state if_state <<choice>>
if_state --> StateA : condition1
if_state --> StateB : condition2
```

### Fork/Join

```
state fork_state <<fork>>
    [*] --> fork_state
    fork_state --> State1
    fork_state --> State2

state join_state <<join>>
    State1 --> join_state
    State2 --> join_state
    join_state --> [*]
```

### Concurrency

```
state Parallel {
    [*] --> Active
    --
    [*] --> NumLock
}
```

### Notes

```
note right of State1
    Important note
end note
```

### Common Use Cases

- System behavior modeling
- Conditional logic representation
- Parallel process handling
- Workflow state transitions
- UI state management

**Example**:
```
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : Start
    Processing --> Success : Complete
    Processing --> Failed : Error
    Success --> [*]
    Failed --> Idle : Retry
```

---

## 5. Entity Relationship Diagrams

**Declaration**: `erDiagram`

### Relationship Syntax

```
ENTITY1 ||--o{ ENTITY2 : "relationship label"
```

### Cardinality Markers

- `|o` Zero or one
- `||` Exactly one
- `}o` Zero or more
- `}|` One or more

### Identification

- `--` Identifying relationship (solid)
- `..` Non-identifying relationship (dashed)

### Attributes

```
CUSTOMER {
    string name PK "Primary key"
    int customerId UK "Unique key"
    string sector FK "Foreign key"
}
```

### Direction

```
%%{init: {'er': {'layoutDirection': 'LR'}}}%%
erDiagram
```

### Common Use Cases

- Database schema design
- Logical data modeling
- Physical relational database representation
- System entity relationship analysis

**Example**:
```
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {
        string name PK
        string email UK
        int customerId
    }
    ORDER {
        int orderNumber PK
        date orderDate
    }
    LINE-ITEM {
        int quantity
        decimal price
    }
```

---

## 6. User Journey Diagrams

**Declaration**: `journey`

### Syntax

```
journey
    title Working Day
    section Go to work
        Make tea: 5: Me
        Go upstairs: 3: Me
        Do work: 1: Me, Cat
    section Go home
        Go downstairs: 5: Me
        Sit down: 3: Me
```

### Score Range

1-5 (higher = better satisfaction)

### Multiple Actors

```
Task: 5: Actor1, Actor2, Actor3
```

### Common Use Cases

- User experience mapping
- Customer journey analysis
- Process improvement identification
- As-is vs. to-be workflow comparison
- Service design blueprinting

**Example**:
```
journey
    title Customer Onboarding Journey
    section Discovery
        Find website: 5: Customer
        Read reviews: 4: Customer
    section Signup
        Create account: 3: Customer
        Verify email: 2: Customer
    section First Use
        Complete tutorial: 4: Customer
        Make first purchase: 5: Customer
```

---

## 7. Gantt Charts

**Declaration**: `gantt`

### Date Format

```
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m-%d
```

### Task Syntax

```
section Section Name
    Task1 :done, t1, 2024-01-01, 3d
    Task2 :active, t2, after t1, 2d
    Task3 :crit, t3, 2024-01-04, 1d
    Milestone :milestone, m1, after t3, 0d
```

### Task Metadata

- `done` - Completed task
- `active` - In progress
- `crit` - Critical task
- `milestone` - Milestone marker

### Dependencies

```
Task2 :after Task1, 3d
Task3 :until Task4, 2024-01-10
```

### Today Marker

```
todayMarker stroke-width:5px,stroke:#0f0,opacity:0.5
```

### Common Use Cases

- Project timeline visualization
- Resource allocation tracking
- Dependency management
- Progress tracking with done/active tags
- Project planning and scheduling

**Example**:
```
gantt
    title Software Development Sprint
    dateFormat YYYY-MM-DD
    section Planning
        Sprint planning :done, plan, 2024-01-01, 1d
    section Development
        Feature A :active, featA, after plan, 5d
        Feature B :featB, after plan, 3d
    section Testing
        QA Testing :crit, qa, after featA, 2d
        Deploy :milestone, after qa, 0d
```

---

## 8. Pie Charts

**Declaration**: `pie` or `pie showData`

### Syntax

```
pie showData
    title Pets Adopted
    "Dogs" : 386
    "Cats" : 85.9
    "Rats" : 15
```

### Constraints

- Positive numbers only
- Up to 2 decimal places
- Rendered clockwise

### Configuration

```
%%{init: {'pie': {'textPosition': 0.5}}}%%
pie
    "Label" : value
```

### Common Use Cases

- Proportional distribution visualization
- Category breakdown display
- Percentage-based data relationships
- Market share representation

**Example**:
```
pie showData
    title Browser Market Share
    "Chrome" : 65
    "Safari" : 19
    "Firefox" : 8
    "Edge" : 5
    "Other" : 3
```

---

## 9. Requirement Diagrams

**Declaration**: `requirementDiagram`

### Requirement Types

- `requirement`
- `functionalRequirement`
- `interfaceRequirement`
- `performanceRequirement`
- `physicalRequirement`
- `designConstraint`

### Syntax

```
requirementDiagram

requirement test_req {
    id: 1
    text: The system shall do something
    risk: High
    verifymethod: Test
}

element test_entity {
    type: simulation
    docref: doc.pdf
}

test_entity - satisfies -> test_req
```

### Risk Levels

`Low`, `Medium`, `High`

### Verification Methods

`Analysis`, `Inspection`, `Test`, `Demonstration`

### Relationship Types

- `contains`
- `copies`
- `derives`
- `satisfies`
- `verifies`
- `refines`
- `traces`

### Common Use Cases

- Requirements tracing across hierarchies
- Test suite linkage to requirements
- Documentation relationship mapping
- Requirement dependency visualization
- Systems engineering documentation

**Example**:
```
requirementDiagram

requirement user_auth {
    id: 1
    text: System shall authenticate users
    risk: High
    verifymethod: Test
}

functionalRequirement password_reset {
    id: 2
    text: Users can reset passwords
    risk: Medium
    verifymethod: Demonstration
}

element login_page {
    type: interface
}

login_page - satisfies -> user_auth
user_auth - contains -> password_reset
```

---

## 10. Git Graphs

**Declaration**: `gitGraph`

### Basic Commands

```
gitGraph
    commit
    branch develop
    checkout develop
    commit
    checkout main
    merge develop
```

### Commit Customization

```
commit id: "v1.0.0"
commit tag: "release"
commit type: HIGHLIGHT
commit type: REVERSE
commit type: NORMAL
```

### Branch Operations

```
branch feature
checkout feature
commit
cherry-pick id: "abc123"
```

### Branch Ordering

```
branch develop order: 1
branch feature order: 2
```

### Orientation

```
%%{init: {'gitGraph': {'mainBranchName': 'main', 'orientation': 'TB'}}}%%
```

Options: `LR` (default), `TB`, `BT`

### Common Use Cases

- Git Flow visualization
- Release management with version tags
- Multiple parallel features
- Complex workflow documentation
- Branch strategy illustration

**Example**:
```
gitGraph
    commit id: "Initial"
    commit id: "Setup"
    branch develop
    checkout develop
    commit id: "Feature work"
    checkout main
    merge develop tag: "v1.0"
    commit id: "Hotfix" type: HIGHLIGHT
    checkout develop
    commit id: "New feature"
```

---

## 11. C4 Diagrams

**Declaration**: `C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`

### Element Types

**Persons**: `Person`, `Person_Ext`
**Systems**: `System`, `System_Ext`, `SystemDb`, `SystemQueue`
**Containers**: `Container`, `ContainerDb`, `ContainerQueue`, `Container_Ext`
**Components**: `Component`, `ComponentDb`, `ComponentQueue`

### Syntax

```
C4Context
    title System Context
    Person(user, "User", "Description")
    System(sys, "System", "Description")
    Rel(user, sys, "Uses")
```

### Boundaries

```
Enterprise_Boundary(b1, "Company") {
    System_Boundary(b2, "Department") {
        System(sys, "System")
    }
}
```

### Relationships

```
Rel(from, to, "label", "tech")
Rel_U(from, to, "label")    %% Up
Rel_D(from, to, "label")    %% Down
Rel_L(from, to, "label")    %% Left
Rel_R(from, to, "label")    %% Right
BiRel(from, to, "label")    %% Bidirectional
```

### Dynamic Sequences

```
C4Dynamic
    RelIndex(1, user, sys, "First action")
    RelIndex(2, sys, db, "Then query")
```

### Styling

```
UpdateElementStyle(user, $bgColor="blue", $fontColor="white")
UpdateRelStyle(user, sys, $textColor="red")
```

### Common Use Cases

- Enterprise architecture documentation
- Application structure visualization
- Component interaction mapping
- Infrastructure deployment views
- Multi-level system documentation

**Example**:
```
C4Context
    title E-commerce System Context
    Person(customer, "Customer", "Shops online")
    System(ecom, "E-commerce System", "Online store")
    System_Ext(payment, "Payment Gateway", "Processes payments")
    SystemDb_Ext(warehouse, "Warehouse System", "Manages inventory")

    Rel(customer, ecom, "Browses and purchases")
    Rel(ecom, payment, "Processes payments via")
    Rel(ecom, warehouse, "Checks inventory from")
```

---

## 12. Mindmaps

**Declaration**: `mindmap`

### Hierarchy via Indentation

```
mindmap
    Root
        Branch 1
            Leaf 1A
            Leaf 1B
        Branch 2
            Leaf 2A
```

### Node Shapes

```
[Square text]
(Rounded text)
((Circle text))
))Bang text((
)Cloud text(
{{Hexagon text}}
Plain text (default)
```

### Icons

```
mindmap
    Root
        Branch::icon(fa fa-book)
        Another::icon(mdi mdi-account)
```

### Classes

```
mindmap
    Root
        Branch:::customClass
```

### Markdown

```
mindmap
    Root
        **Bold text**
        *Italic text*
```

### Common Use Cases

- Brainstorming and ideation
- Strategic planning
- Knowledge organization
- Argument mapping
- Creative technique visualization

**Example**:
```
mindmap
    Project Planning
        Requirements
            Functional
            Non-functional
        Design
            Architecture
            UI/UX
        Development
            Frontend
            Backend
        Testing
            Unit tests
            Integration tests
```

---

## 13. Timeline Diagrams

**Declaration**: `timeline`

### Syntax

```
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook
           YouTube
    2005 : Reddit
```

### Sections

```
timeline
    title Project History
    section Phase 1
        2020 : Planning
        2021 : Design
    section Phase 2
        2022 : Development
        2023 : Launch
```

### Multiple Events

```
2020 : Event 1
     : Event 2
     : Event 3
```

### Configuration

```
%%{init: {'timeline': {'disableMulticolor': true}}}%%
timeline
```

### Common Use Cases

- Historical timelines
- Project roadmaps
- Personal milestones
- Chronological event documentation
- Company history visualization

**Example**:
```
timeline
    title Company Milestones
    section 2020
        January : Founded company
                : Hired first employee
        June : Launched MVP
    section 2021
        March : Series A funding
        October : 10,000 users
    section 2022
        January : International expansion
```

---

## 14. Sankey Diagrams

**Declaration**: `sankey`

### CSV Format

```
sankey
Source,Target,Value
A,B,10
A,C,20
B,D,5
C,D,15
```

### Quoted Text

```
"Text, with comma",Target,10
```

### Configuration

```
%%{init: {'sankey': {'width': 800, 'linkColor': 'gradient'}}}%%
```

**linkColor Options**: `source`, `target`, `gradient`, hex color

**nodeAlignment**: `justify`, `center`, `left`, `right`

### Common Use Cases

- Energy transformation visualization
- Material flow tracking
- Resource allocation
- Process conversion analysis
- Multi-stage flow representation

**Example**:
```
sankey
Agricultural waste,Bio-conversion,124
Bio-conversion,Liquid,0.6
Bio-conversion,Losses,26.9
Bio-conversion,Solid,280.5
Biofuel imports,Liquid,35
```

---

## 15. XY Charts

**Declaration**: `xychart`

### Syntax

```
xychart
    title "Sales Report"
    x-axis [Q1, Q2, Q3, Q4]
    y-axis "Revenue ($M)" 0 --> 100
    line [23, 45, 67, 89]
    bar [12, 34, 56, 78]
```

### Axes

```
x-axis "Label" min --> max
x-axis [cat1, cat2, cat3]    %% Categorical
y-axis "Label" 0 --> 100     %% Numeric
y-axis "Label"               %% Auto-range
```

### Chart Types

```
line [values]
bar [values]
```

### Configuration

```
%%{init: {'xyChart': {'width': 600, 'height': 400}}}%%
```

### Common Use Cases

- Sales tracking
- Trend analysis
- Categorical comparisons
- Multi-series overlays
- Time series visualization

**Example**:
```
xychart
    title "Quarterly Performance"
    x-axis [Q1, Q2, Q3, Q4]
    y-axis "Revenue ($K)" 0 --> 500
    line "2023" [200, 250, 300, 400]
    line "2024" [220, 280, 350, 450]
    bar "Target" [250, 300, 350, 420]
```

---

## 16. Block Diagrams

**Declaration**: `block`

### Column Layout

```
block
    columns 3
    a b c
    d e f
```

### Block Width

```
block
    columns 3
    a
    b:2    %% Spans 2 columns
    c
```

### Spaces

```
block
    columns 3
    a space b
    space:2 c    %% 2-column space
```

### Shapes

```
a["Text"]               %% Rectangle
b("Text")               %% Rounded
c(["Text"])             %% Stadium
d[("Text")]             %% Circle
e[(["Text"])]           %% Cylinder
f{{"Text"}}             %% Hexagon
g[["Text"]]             %% Subroutine
h[("Text")]             %% Double circle
i>"Text"]               %% Asymmetric
```

### Block Arrows

```
a<["Arrow left"](right)
b["Arrow right"]>(right)
c^["Arrow up"](up)
d["Arrow down"]v(down)
```

### Connections

```
a-->b
a-- "label" -->b
```

### Styling

```
style a fill:#f9f,stroke:#333,stroke-width:4px
classDef myclass fill:#0f0
class b myclass
```

### Common Use Cases

- Software architecture visualization
- Network diagrams
- Process flowcharts
- Electrical systems
- Educational materials

**Example**:
```
block
    columns 3
    Frontend["Frontend<br/>React"]:2 space
    API["API Gateway"]
    Auth["Auth<br/>Service"]
    DB[("Database")]

    Frontend-->API
    API-->Auth
    API-->DB
```

---

## 17. Packet Diagrams

**Declaration**: `packet`

### Bit Range Syntax

```
packet
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
```

### Bit Count Syntax (v11.7.0+)

```
packet
    +16: "Source Port"
    +16: "Destination Port"
    +32: "Sequence Number"
```

### Configuration

```
%%{init: {'packet': {'showBits': true}}}%%
```

### Common Use Cases

- Network packet structure documentation
- TCP/UDP packet illustration
- Protocol header visualization
- Educational network engineering materials

**Example**:
```
packet
    0-15: "Source Port"
    16-31: "Destination Port"
    +16: "Length"
    +16: "Checksum"
    +32: "Data (variable)"
```

---

## 18. Quadrant Charts

**Declaration**: `quadrantChart`

### Syntax

```
quadrantChart
    title Reach and engagement
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.7, 0.8]
```

### Point Styling

```
%%{init: {'quadrantChart': {'chartWidth': 600}}}%%
Campaign A: [0.3, 0.6] radius: 15, color: #ff0000
```

### Class-Based Styling

```
classDef high stroke:#0f0,fill:#0f0
Campaign A: [0.3, 0.6]:::high
```

### Common Use Cases

- Pattern and trend identification
- Action prioritization
- Business analysis (risk vs. reward)
- Marketing positioning
- Portfolio management

**Example**:
```
quadrantChart
    title Product Priority Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Do First
    quadrant-2 Delegate
    quadrant-3 Eliminate
    quadrant-4 Schedule
    Feature A: [0.2, 0.8]
    Feature B: [0.7, 0.9]
    Feature C: [0.3, 0.3]
```

---

## 19. Kanban Boards

**Declaration**: `kanban`

### Syntax

```
kanban
    Todo
        task1[Task description]
    In Progress
        task2[Working on this]
    Done
        task3[Completed]
```

### Metadata

```
kanban
    Todo
        task1[Write docs]@{ assigned: 'alice', priority: 'High' }
        task2[Code review]@{ ticket: 'PROJ-123', assigned: 'bob' }
```

### Priority Levels

`Very High`, `High`, `Low`, `Very Low`

### Configuration

```
---
config:
  kanban:
    ticketBaseUrl: 'https://jira.example.com/browse/#TICKET#'
---
kanban
    Todo
        task1[Description]@{ ticket: 'ABC-123' }
```

### Common Use Cases

- Project workflow visualization
- Task progression tracking
- Responsibility assignment
- Priority management
- External ticket system integration

**Example**:
```
kanban
    Backlog
        task1[User authentication]@{ priority: 'High' }
    In Progress
        task2[API endpoints]@{ assigned: 'dev1', ticket: 'PROJ-45' }
    Review
        task3[Frontend styling]@{ assigned: 'dev2' }
    Done
        task4[Setup CI/CD]
```

---

## 20. Architecture Diagrams

**Declaration**: `architecture-beta`

### Services and Groups

```
architecture-beta
    service api(server)[API Server]
    service db(database)[Database] in api
    group cloud(cloud)[Cloud Platform]
        service app(server)[App]
    end
```

### Default Icons

`cloud`, `database`, `disk`, `internet`, `server`

### Custom Icons (iconify.design)

```
architecture-beta
    icon mdi mdi-account
    service user(mdi:account)[User]
```

### Edges

```
service1:R --> L:service2
service1:T -- B:service2
group1:B --> T:service2
```

**Sides**: `T` (top), `B` (bottom), `L` (left), `R` (right)

### Arrow Direction

```
api:R --> L:cache    %% Left to right
api:R <-- L:cache    %% Right to left
api:R <--> L:cache   %% Bidirectional
```

### Common Use Cases

- Cloud deployment visualization
- CI/CD pipeline mapping
- Microservice relationships
- System component organization
- Infrastructure architecture

**Example**:
```
architecture-beta
    group cloud(cloud)[AWS]
        service web(server)[Web Servers] in cloud
        service api(server)[API] in cloud
    end
    service db(database)[PostgreSQL]
    service cache(disk)[Redis]

    web:R --> L:api
    api:R --> L:db
    api:B --> T:cache
```

---

## 21. ZenUML Sequence Diagrams

**Declaration**: `zenuml`

### Participants

```
zenuml
    Alice
    Bob
    @Actor User
    @Database DB
```

### Messages

```
Alice->Bob: Async message
Bob.syncMethod() {
    DB.query()
    return result
}
```

### Control Structures

```
if(condition) {
    Alice->Bob: Yes path
} else {
    Alice->Bob: No path
}

while(condition) {
    Alice->Bob: Loop
}

try {
    Alice->Bob: Operation
} catch {
    Alice->Bob: Handle error
}
```

### Common Use Cases

- API flows with error handling
- Booking/transaction processes
- Multi-actor communication
- Parallel service calls
- Exception handling visualization

**Example**:
```
zenuml
    @Actor User
    @Boundary WebApp
    @Control API
    @Database DB

    User->WebApp: Login request
    WebApp.authenticate() {
        API.validateUser() {
            DB.query()
            if(valid) {
                return token
            } else {
                @return "Invalid credentials"
            }
        }
    }
```

---

## 22. Radar Charts

**Declaration**: `radar-beta`

### Syntax

```
radar-beta
    axis skill1["Communication"], skill2["Problem Solving"], skill3["Leadership"]
    curve alice["Alice"]{5, 4, 3}
    curve bob["Bob"]{3, 5, 4}
```

### Key-Value Format

```
curve alice["Alice"]{skill1: 5, skill2: 4, skill3: 3}
```

### Configuration

```
%%{init: {'radar': {'max': 10, 'showLegend': true}}}%%
```

### Common Use Cases

- Performance comparison across dimensions
- Multi-criteria assessment
- Competitive analysis
- Skills evaluation
- Product feature comparison

**Example**:
```
radar-beta
    axis "Speed", "Reliability", "Cost", "Ease of Use", "Scalability"
    curve "Product A"{8, 7, 5, 9, 6}
    curve "Product B"{6, 9, 8, 7, 8}
    curve "Product C"{9, 6, 6, 8, 9}
```

---

## 23. Treemap Diagrams

**Declaration**: `treemap-beta`

### Hierarchy via Indentation

```
treemap-beta
    "Sales by Region"
        "North America": 450
        "Europe": 380
        "Asia": 290
```

### Nested Sections

```
treemap-beta
    title Financial Breakdown
    "Revenue"
        "Product Sales"
            "Product A": 150
            "Product B": 120
        "Services"
            "Consulting": 80
            "Support": 50
```

### Styling

```
classDef high fill:#0f0
treemap-beta
    "Category"
        "Item A": 100:::high
```

### Configuration

```
%%{init: {'treemap': {'valueFontSize': 16, 'showValues': true}}}%%
```

### Common Use Cases

- Financial visualization (budgets, market share)
- File system analysis
- Population demographics
- Product hierarchies
- Organizational structures

**Example**:
```
treemap-beta
    title Budget Allocation
    "Company Budget"
        "Operations"
            "Salaries": 500
            "Office": 100
        "Marketing"
            "Advertising": 200
            "Events": 50
        "Technology"
            "Infrastructure": 150
            "Software": 80
```

---

## Summary

Mermaid supports 23+ diagram types covering:

**Flow & Process**: Flowcharts, Sequence, State, User Journey, Gantt, Kanban, Timeline
**Software & Architecture**: Class, ER, C4, Architecture, Block, Packet, Git
**Data & Analysis**: Pie, XY, Sankey, Quadrant, Radar, Treemap
**Conceptual**: Mindmaps, Requirements, ZenUML

All diagrams support:
- Theme customization
- Styling options
- Accessibility features
- Configuration via frontmatter
- Comments and documentation

For configuration options, see **configuration.md**.
For syntax fundamentals, see **syntax.md**.
For best practices, see **best-practices.md**.
