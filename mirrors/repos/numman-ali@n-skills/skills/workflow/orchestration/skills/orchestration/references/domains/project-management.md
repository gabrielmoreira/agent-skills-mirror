# Project Management Orchestration Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Complex projects, clearly decomposed.                     │
│   Dependencies tracked. Progress visible. Team aligned.     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Load when**: Epic breakdown, sprint planning, progress tracking, dependency management, team coordination
> **Common patterns**: Hierarchical Decomposition, Capacity-Based Planning, Multi-Dimension Status

## Table of Contents

1. [Epic Breakdown](#epic-breakdown)
2. [Sprint Planning](#sprint-planning)
3. [Progress Tracking](#progress-tracking)
4. [Dependency Management](#dependency-management)
5. [Team Coordination](#team-coordination)

---

## Epic Breakdown

### Pattern: Hierarchical Decomposition

```
User Request: "Break down the authentication epic"

Phase 1: EXPLORE
└─ Explore agent: Understand requirements, existing system

Phase 2: PLAN
└─ Plan agent: Design high-level feature breakdown

Phase 3: FAN-OUT (Parallel story creation)
├─ Agent A: User stories for login/logout
├─ Agent B: User stories for registration
├─ Agent C: User stories for password management
├─ Agent D: User stories for session management
└─ Agent E: User stories for OAuth integration

Phase 4: REDUCE
└─ General-purpose agent: Organize into coherent backlog
```

**Task Management Implementation:**

```bash
# Create epic
npx cc-mirror tasks create --subject "Epic: User Authentication" --description "Complete auth system"

# Create stories
npx cc-mirror tasks create --subject "Story: Login flow" --description "..."
npx cc-mirror tasks create --subject "Story: Registration" --description "..."
npx cc-mirror tasks create --subject "Story: Password reset" --description "..."

# Set dependencies
npx cc-mirror tasks update 3 --add-blocked-by 2
```

### Pattern: Vertical Slice Breakdown

```
Phase 1: EXPLORE
└─ Explore agent: Map feature touchpoints (UI, API, DB)

Phase 2: FAN-OUT (Slice by user value)
├─ Agent A: Define slice 1 (minimal viable feature)
├─ Agent B: Define slice 2 (enhanced feature)
└─ Agent C: Define slice 3 (complete feature)

Phase 3: PIPELINE
└─ General-purpose agent: Estimate, prioritize, sequence
```

---

## Sprint Planning

### Pattern: Capacity-Based Planning

```
User Request: "Plan the next sprint"

Phase 1: FAN-OUT (Gather context)
├─ Explore agent: Review backlog priority
├─ Explore agent: Check team capacity
├─ Explore agent: Review blockers and dependencies
└─ Explore agent: Check carryover from last sprint

Phase 2: REDUCE
└─ Plan agent: Propose sprint scope

Phase 3: FAN-OUT (Task breakdown)
├─ Agent A: Break down story 1 into tasks
├─ Agent B: Break down story 2 into tasks
└─ Agent C: Break down story 3 into tasks

Phase 4: PIPELINE
└─ General-purpose agent: Finalize sprint backlog
```

**Task Structure:**

```bash
# Sprint-level task
npx cc-mirror tasks create --subject "Sprint 14: Auth Implementation" --description "..."

# Stories within sprint
npx cc-mirror tasks create --subject "Login API endpoint" --description "..."
npx cc-mirror tasks create --subject "Login UI component" --description "..."
npx cc-mirror tasks update 3 --add-blocked-by 2

# Sub-tasks
npx cc-mirror tasks create --subject "Write login validation" --description "..."
npx cc-mirror tasks create --subject "Add rate limiting" --description "..."
```

---

## Progress Tracking

### Pattern: Multi-Dimension Status

```
User Request: "What's the project status?"

Phase 1: FAN-OUT (Parallel status gathering)
├─ Agent A: Task completion status
├─ Agent B: Blocker analysis
├─ Agent C: Timeline vs plan
├─ Agent D: Quality metrics
└─ Agent E: Risk status

Phase 2: REDUCE
└─ General-purpose agent: Executive status summary
```

**Using cc-mirror tasks:**

```bash
# Get current state
npx cc-mirror tasks --status all

# View dependency graph
npx cc-mirror tasks graph

# Update progress
npx cc-mirror tasks update 5 --add-comment "50% complete, blocked on API review"

# Mark complete
npx cc-mirror tasks update 5 --status resolved
```

### Pattern: Burndown Tracking

```
Phase 1: EXPLORE
└─ Explore agent: Calculate completed vs remaining work

Phase 2: PIPELINE
├─ General-purpose agent: Project completion trajectory
├─ General-purpose agent: Identify velocity trends
└─ General-purpose agent: Flag at-risk items

Phase 3: REDUCE
└─ General-purpose agent: Burndown report
```

---

## Dependency Management

### Pattern: Dependency Graph Construction

```
User Request: "Map project dependencies"

Phase 1: EXPLORE
└─ Explore agent: List all tasks and their relationships

Phase 2: FAN-OUT
├─ Agent A: Map technical dependencies
├─ Agent B: Map team/resource dependencies
└─ Agent C: Map external dependencies

Phase 3: REDUCE
└─ General-purpose agent: Dependency graph, critical path
```

**Implementation:**

```bash
# Create dependency chain
npx cc-mirror tasks create --subject "Database schema" --description "..."
npx cc-mirror tasks create --subject "API models" --description "..."
npx cc-mirror tasks create --subject "API endpoints" --description "..."
npx cc-mirror tasks create --subject "Frontend integration" --description "..."

npx cc-mirror tasks update 2 --add-blocked-by 1
npx cc-mirror tasks update 3 --add-blocked-by 2
npx cc-mirror tasks update 4 --add-blocked-by 3

# Cross-team dependency
npx cc-mirror tasks create --subject "External API access" --description "Waiting on partner"
npx cc-mirror tasks update 3 --add-blocked-by 5

# Visualize
npx cc-mirror tasks graph
```

### Pattern: Critical Path Analysis

```
Phase 1: EXPLORE
└─ Explore agent: Map all task dependencies

Phase 2: PIPELINE
├─ General-purpose agent: Calculate path lengths
├─ General-purpose agent: Identify critical path
└─ General-purpose agent: Find parallel opportunities

Phase 3: REDUCE
└─ General-purpose agent: Optimization recommendations
```

---

## Team Coordination

### Pattern: Work Distribution

```
User Request: "Assign work for this sprint"

Phase 1: FAN-OUT
├─ Explore agent: Analyze task requirements
├─ Explore agent: Review team skills/capacity
└─ Explore agent: Check current assignments

Phase 2: REDUCE
└─ Plan agent: Optimal assignment recommendations

Phase 3: FAN-OUT (Parallel task assignment)
├─ Agent A: Create task assignments for dev 1
├─ Agent B: Create task assignments for dev 2
└─ Agent C: Create task assignments for dev 3
```

### Pattern: Multi-Team Sync

```
Phase 1: FAN-OUT
├─ Agent A: Gather Team A status
├─ Agent B: Gather Team B status
└─ Agent C: Identify cross-team dependencies

Phase 2: REDUCE
└─ General-purpose agent: Cross-team status, blockers, needs
```

---

## Task Management in Practice

All project management work should use cc-mirror tasks for proper tracking:

```bash
# Sprint planning example
npx cc-mirror tasks create --subject "Sprint 14 Planning" --description "Plan next sprint scope..."
npx cc-mirror tasks create --subject "Review backlog" --description "Prioritize stories..."
npx cc-mirror tasks create --subject "Break down Story A" --description "Create implementation tasks..."
npx cc-mirror tasks create --subject "Break down Story B" --description "Create implementation tasks..."
npx cc-mirror tasks create --subject "Set dependencies" --description "Wire task dependencies..."
npx cc-mirror tasks create --subject "Assign work" --description "Distribute to team..."

# Planning sequence
npx cc-mirror tasks update 2 --add-blocked-by 1
npx cc-mirror tasks update 3 --add-blocked-by 2
npx cc-mirror tasks update 4 --add-blocked-by 2
npx cc-mirror tasks update 5 --add-blocked-by 3,4
npx cc-mirror tasks update 6 --add-blocked-by 5
```

```python
# Track in session
TodoWrite([
    {"content": "Sprint 14 Planning", "status": "in_progress", "activeForm": "Planning Sprint 14"},
    {"content": "Review backlog", "status": "pending", "activeForm": "Reviewing backlog"},
    {"content": "Break down Story A", "status": "pending", "activeForm": "Breaking down Story A"},
    {"content": "Break down Story B", "status": "pending", "activeForm": "Breaking down Story B"},
    {"content": "Set dependencies", "status": "pending", "activeForm": "Setting dependencies"},
    {"content": "Assign work", "status": "pending", "activeForm": "Assigning work"}
])

# Parallel breakdown (sonnet for structured planning work)
Task(subagent_type="general-purpose", prompt="Task 3: Break down Story A...",
     model="sonnet", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Task 4: Break down Story B...",
     model="sonnet", run_in_background=True)
```

## Best Practices

1. **Break down early** - Large tasks are hard to track
2. **Set dependencies explicitly** - Prevents blocked work
3. **Update status frequently** - Real-time visibility
4. **Comment on blockers** - Context for resolution
5. **Close completed tasks immediately** - Accurate progress

---

```
─── ◈ Project Management ────────────────
```
