---
name: implementation-approach
description: Implementation strategy selection framework. Use when planning implementation strategy, selecting development approach, or defining verification criteria.
---

# Implementation Strategy Selection Framework (Meta-cognitive Approach)

## Meta-cognitive Strategy Selection Process

### Phase 1: Comprehensive Current State Analysis

**Core Question**: "What does the existing implementation look like?"

#### Analysis Framework
```yaml
Architecture Analysis: Responsibility separation, data flow, dependencies, technical debt
Implementation Quality Assessment: Code quality, test coverage, performance, security
Historical Context Understanding: Current form rationale, past decision validity, constraint changes, requirement evolution
```

#### Meta-cognitive Question List
- What is the true responsibility of this implementation?
- Which parts are business essence and which derive from technical constraints?
- What dependencies or implicit preconditions are unclear from the code?
- What benefits and constraints does the current design bring?

### Phase 2: Strategy Exploration and Creation

**Core Question**: "When determining before → after, what implementation patterns or strategies should be referenced?"

#### Strategy Discovery Process
```yaml
Direct Strategy: Smallest repository-supported change that satisfies the accepted requirements and constraints
Repository Alternatives: Existing patterns that materially differ in migration, dependency order, or verification boundary
External Research: Official/current sources only when repository evidence cannot resolve a time-sensitive capability, compatibility, or dependency decision
```

#### Reference Strategy Patterns

**Legacy Handling Strategies**:
- Strangler Pattern: Gradual migration through phased replacement
- Facade Pattern: Complexity hiding through unified interface
- Adapter Pattern: Bridge with existing systems

**New Development Strategies**:
- Feature-driven Development: Vertical implementation prioritizing user value
- Foundation-driven Development: Foundation-first construction prioritizing stability
- Risk-driven Development: Prioritize addressing maximum risk elements

**Integration/Migration Strategies**:
- Proxy Pattern: Transparent feature extension
- Decorator Pattern: Phased enhancement of existing features
- Bridge Pattern: Flexibility through abstraction

Use these patterns only when their named migration or dependency problem exists. Start with the direct strategy. Compare an alternative when it would materially change risk, rollout, compatibility, or the early verification point; do not add a pattern or combination only to increase the option count.

### Phase 3: Risk Assessment and Control

**Core Question**: "What risks arise when applying this to existing implementation, and what's the best way to control them?"

#### Risk Analysis Matrix
```yaml
Technical Risks: System impact, data consistency, performance degradation, integration complexity
Operational Risks: Service availability, deployment downtime, process changes, rollback procedures
Project Risks: Schedule delays, learning costs, quality achievement, team coordination
```

#### Risk Control Strategies
```yaml
Preventive Measures: Phased migration, parallel operation verification, integration/regression tests, monitoring setup
Incident Response: Rollback procedures, log/metrics preparation, communication system, service continuation procedures
```

### Phase 4: Constraint Compatibility Verification

**Core Question**: "What are this project's constraints?"

#### Constraint Checklist
```yaml
Technical Constraints: Library compatibility, resource capacity, mandatory requirements, numerical targets
Temporal Constraints: Deadlines/priorities, dependencies, milestones, learning periods
Resource Constraints: Team/skills, work hours/systems, budget, external contracts
Business Constraints: Market launch timing, customer impact, regulatory compliance
```

### Phase 5: Implementation Approach Decision

Select the implementation approach that directly fits the verified dependency and delivery constraints:

#### Vertical Slice (Feature-driven)
**Characteristics**: Vertical implementation across all layers by feature unit
**Application Conditions**: Default when an end-to-end value unit can be delivered and verified independently. Sharing fewer than 2 data models or touching 3+ layers are supporting signals, not substitutes for independent deliverability
**Verification Method**: End-user value delivery at each feature completion

#### Horizontal Slice (Foundation-driven)
**Characteristics**: Phased construction by architecture layer
**Application Conditions**: Use when a common foundation blocks consumer work or must pass stability/compatibility verification before dependent slices can proceed. Three or more dependent features is a mandatory signal to evaluate this approach
**Verification Method**: Integrated operation verification when all foundation layers complete

#### Hybrid
**Characteristics**: Flexible combination according to project characteristics
**Application Conditions**: Use when a verified foundation step is required first and later work can proceed as independently verifiable value slices. Resolve blocking requirement ambiguity before selecting the implementation approach
**Verification Method**: Verify at appropriate L1/L2/L3 levels according to each phase's goals

### Phase 6: Decision Rationale Documentation

**Design Doc Documentation**: Record in the Design Doc's implementation approach section:
1. Selected strategy name and characteristics
2. A materially different alternative and reason for rejection, when one was compared
3. Risk mitigation plan (from Phase 3)
4. Constraint compliance summary (from Phase 4)
5. Verification level (L1/L2/L3) and integration point definition

## Verification Level Definitions

Priority for completion verification of each task:

- **L1: Functional Operation Verification** - Operates as end-user feature (e.g., search executable)
- **L2: Test Operation Verification** - New tests added and passing
- **L3: Build Success Verification** - Code builds/runs without errors

**Priority**: L1 > L2 > L3 in order of verifiability importance

## Integration Point Definitions

Define integration points according to selected strategy:
- **Strangler-based**: When switching between old and new systems for each feature
- **Feature-driven**: When users can actually use the feature
- **Foundation-driven**: When all architecture layers are ready and E2E tests pass
- **Hybrid**: When individual goals defined for each phase are achieved

## Quality Checks

1. Confirm Phase 1 identifies the current responsibility, dependency path, and historical constraints before selecting a strategy
2. Confirm the direct strategy satisfies every accepted requirement and constraint; when it does not, compare the smallest alternative that covers the gap
3. Confirm Phase 3 records the material risks and concrete controls before implementation starts
4. Confirm Phase 4 checks the constraints that can change strategy selection; mark non-applicable categories explicitly rather than inventing content
5. Confirm Phase 6 records the selected strategy, any materially different alternative, and the early verification point

## Guidelines for Meta-cognitive Execution

1. **Leverage Known Patterns**: Use a pattern when its problem and trade-off match the observed repository state
2. **Conditional External Research**: Use official/current sources when a time-sensitive capability, compatibility, or dependency decision remains unresolved after repository inspection
3. **Apply 5 Whys**: Pursue root causes to grasp essence
4. **Multi-perspective Evaluation**: Comprehensively evaluate from each Phase 1-4 perspective
