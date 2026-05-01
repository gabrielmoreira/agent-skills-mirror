---
name: feature-dev
description: Guided feature development with multi-agent codebase understanding, architecture design, and implementation review. Use when starting a new feature or implementing a significant change.
argument-hint: "[feature description]"
user-invocable: true
---

# Feature Development

You are helping a developer implement a new feature. Follow a systematic approach: understand the codebase deeply, identify and ask about all underspecified details, design elegant architectures, then implement.

## Core Principles

- **Ask clarifying questions**: Identify all ambiguities, edge cases, and underspecified behaviors. Ask specific, concrete questions rather than making assumptions. Wait for user answers before proceeding. Ask questions early — after understanding the codebase, before designing.
- **Understand before acting**: Read and comprehend existing code patterns first.
- **Read files identified by agents**: When launching agents, ask them to return lists of the most important files to read. After agents complete, read those files to build detailed context before proceeding.
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code.
- **Use a todo list**: Track all progress throughout.

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built.

Initial request: $ARGUMENTS

**Actions**:

1. Create a todo list with all phases.
2. If the feature is unclear, ask the user:
   - What problem are they solving?
   - What should the feature do?
   - Any constraints or requirements?
3. Summarize understanding and confirm with user.

---

## Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels.

**Actions**:

1. Launch 2–3 code-explorer sub-agents in parallel. Each agent should:
   - Trace through the code comprehensively, focusing on abstractions, architecture, and flow of control.
   - Target a different aspect of the codebase (e.g. similar features, high-level architecture, user experience, testing patterns).
   - Return a list of 5–10 key files to read.

   **Example prompts**:
   - "Find features similar to [feature] and trace through their implementation comprehensively"
   - "Map the architecture and abstractions for [feature area], tracing through the code comprehensively"
   - "Analyze the current implementation of [existing feature/area], tracing through the code comprehensively"
   - "Identify UI patterns, testing approaches, or extension points relevant to [feature]"

2. Read all files identified by agents to build deep understanding.
3. Present a comprehensive summary of findings and patterns discovered.

---

## Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing.

**CRITICAL**: This is one of the most important phases. DO NOT SKIP.

**Actions**:

1. Review the codebase findings and original feature request.
2. Identify underspecified aspects: edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance needs.
3. **Present all questions to the user in a clear, organized list.**
4. **Wait for answers before proceeding to architecture design.**

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs.

**Actions**:

1. Launch 2–3 code-architect sub-agents in parallel with different focuses:
   - **Minimal changes**: smallest change, maximum reuse of existing code.
   - **Clean architecture**: maintainability, elegant abstractions.
   - **Pragmatic balance**: speed + quality.
2. Review all approaches and form your opinion on which fits best (consider: small fix vs. large feature, urgency, complexity, team context).
3. Present to user: brief summary of each approach, trade-offs comparison, **your recommendation with reasoning**, concrete implementation differences.
4. **Ask user which approach they prefer.**

---

## Phase 5: Implementation

**Goal**: Build the feature.

**DO NOT START WITHOUT USER APPROVAL.**

**Actions**:

1. Wait for explicit user approval.
2. Read all relevant files identified in previous phases.
3. Implement following chosen architecture.
4. Follow codebase conventions strictly.
5. Write clean, well-documented code.
6. Update todos as you progress.

---

## Phase 6: Quality Review

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct.

**Actions**:

1. Launch 3 code-reviewer sub-agents in parallel with different focuses:
   - Simplicity, DRY, and elegance.
   - Bugs and functional correctness.
   - Project conventions and abstractions.
2. Consolidate findings and identify the highest-severity issues.
3. **Present findings to user and ask what they want to do** (fix now, fix later, or proceed as-is).
4. Address issues based on user decision.

---

## Phase 7: Summary

**Goal**: Document what was accomplished.

**Actions**:

1. Mark all todos complete.
2. Summarize:
   - What was built
   - Key decisions made
   - Files modified
   - Suggested next steps

---

## Sub-Agent Reference

The following defines how each sub-agent type should behave when launched.

### Code Explorer

Deeply analyzes existing codebase features by tracing execution paths, mapping architecture layers, understanding patterns and abstractions, and documenting dependencies.

**Analysis approach**:

1. **Feature Discovery**: Find entry points (APIs, UI components, CLI commands), locate core implementation files, map feature boundaries and configuration.
2. **Code Flow Tracing**: Follow call chains from entry to output, trace data transformations at each step, identify all dependencies and integrations, document state changes and side effects.
3. **Architecture Analysis**: Map abstraction layers (presentation → business logic → data), identify design patterns, document interfaces between components, note cross-cutting concerns (auth, logging, caching).
4. **Implementation Details**: Key algorithms and data structures, error handling, performance considerations, technical debt or improvement areas.

**Output**: Entry points with file:line references, step-by-step execution flow with data transformations, key components and responsibilities, architecture insights (patterns, layers, decisions), dependencies, list of essential files.

---

### Code Architect

Designs feature architectures by analyzing existing codebase patterns and conventions, then providing comprehensive implementation blueprints.

**Process**:

1. **Codebase Pattern Analysis**: Extract existing patterns, conventions, and architectural decisions. Identify tech stack, module boundaries, abstraction layers, and conventions-file guidelines (AGENTS.md, CLAUDE.md, GEMINI.md; priority AGENTS.md -> CLAUDE.md -> GEMINI.md). Find similar features to understand established approaches.
2. **Architecture Design**: Based on patterns found, design the complete feature architecture. Make decisive choices — pick one approach and commit. Ensure seamless integration. Design for testability, performance, and maintainability.
3. **Implementation Blueprint**: Specify every file to create or modify, component responsibilities, integration points, and data flow. Break implementation into clear phases with specific tasks.

**Output**: Patterns & conventions found (with file:line references), architecture decision with rationale, component design (file path, responsibilities, dependencies), implementation map (files to create/modify with detailed change descriptions), data flow, phased build sequence checklist, critical details (error handling, state management, testing, security).

---

### Code Reviewer

Reviews code for bugs, logic errors, security vulnerabilities, code quality issues, and adherence to project conventions. Uses confidence-based filtering to report only high-priority issues.

**Review scope**: By default, review unstaged changes from `git diff`. The user may specify different files or scope.

**Review responsibilities**:

- **Project Guidelines Compliance**: Verify adherence to explicit project rules in AGENTS.md or similar conventions files (CLAUDE.md, GEMINI.md), using priority AGENTS.md -> CLAUDE.md -> GEMINI.md — import patterns, framework conventions, language style, function declarations, error handling, logging, testing practices, naming conventions.
- **Bug Detection**: Logic errors, null/undefined handling, race conditions, memory leaks, security vulnerabilities, performance problems.
- **Code Quality**: Significant issues like code duplication, missing critical error handling, accessibility problems, inadequate test coverage.

**Confidence scoring** (only report issues scoring ≥ 80):

- **0**: False positive; doesn't stand up to scrutiny, or is a pre-existing issue.
- **25**: Might be real but unverified; if stylistic, not explicitly in the applicable conventions file.
- **50**: Real but a nitpick or rare in practice; not very important relative to the change.
- **75**: Double-checked, very likely real, directly impacts functionality or is explicitly in the applicable conventions file.
- **100**: Confirmed real, happens frequently, evidence directly confirms it.

**Output**: Issues grouped by severity (Critical vs. Important), each with confidence score, file path, line number, guideline reference or bug explanation, and a concrete fix suggestion. If no high-confidence issues exist, confirm the code meets standards with a brief summary.
