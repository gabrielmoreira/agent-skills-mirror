---
name: drawio-graph-builder
description: "Create clean Draw.io graphs via a confirmation-first SOP. Use for: workflow diagrams, architecture flowcharts, execution logic maps, mentor-report visuals, and engineering process graphs. TRIGGER PHRASES: drawio, graph, flowchart, workflow图, 框图, 程序框图, 汇报图, 工程图, 架构图, 画个图, 流程梳理, 机制图, 闭环图, 画一下, 整理成图. Default language in graph nodes: English (user can override)."
argument-hint: "report | engineering | custom"
---

# Draw.io Graph Builder

Skill Version: v1.1

## Core Principle
- No Mermaid output in this skill.
- First output must be a text-only structured graph draft.
- Draw.io file generation is allowed only after user confirms the text draft.

## Scope
Use when user asks to design or deliver graph-based artifacts for:
- report visuals (simple and concise)
- engineering visuals (detailed and standards-oriented)
- custom idea/process diagrams (not limited to project-wide workflow)

Do not use for:
- general coding fixes unrelated to diagrams
- generating slide decks or prose-only summaries without graph intent

## Mandatory Lifecycle (SOP)
1. Intent intake and disambiguation.
2. Requirement closure with >=95% confidence.
3. Template selection or template creation.
4. Text-only structured draft output for user confirmation.
5. Draw.io generation after explicit confirmation.
6. Visual cleanup pass (alignment, edge crossings, spacing).
7. Final delivery with file paths and legend summary.

## Phase 1: Requirement Closure (Must Reach >=95%)
Must ask focused questions until ambiguity is removed. At minimum, lock these fields:
- Purpose: report / engineering / custom
- Audience: mentor / PM / RD / mixed
- Diagram scope: full workflow or partial idea
- Detail level: minimal / moderate / detailed
- Node language: default English unless user overrides
- Orientation: left-to-right or top-to-bottom
- Deliverables: single or multiple diagrams
- Output location: default `assets/` unless user overrides

If confidence <95%:
- keep asking concise questions
- do not generate drawio yet

## Phase 2: Template Policy
- Reuse existing template first if it clearly matches request.
- If multiple templates fit, ask user to choose.
- If no template fits:
  - ask user whether to provide references or ask agent to research standards
  - create a new template and save it under `templates/`

## Phase 3: Standard Visual Semantics
Default standard for engineering flowcharts:
- Terminator: start/end
- Process: computation/service step
- Decision: branch condition
- Data/Input: external payload
- Data Store: persistent artifact
- External Entity: hardware/system boundary

Line semantics:
- solid arrow: implemented/active flow
- dashed arrow: planned/not active flow
- loopback arrow: retry/regeneration

Color semantics (default palette):
- Process/Terminator: blue family
- Decision: amber family
- Data/Data Store: green family
- External: gray family
- Planned branch: muted gray dashed

## Phase 4: Draft-First Contract
Before any drawio file generation, output a text draft with:
- node list (id + label + type)
- edge list (from -> to + line style + meaning)
- loops (inner/outer if any)
- assumptions (if any)
- pending confirmations list

Only proceed to drawio when user explicitly confirms draft.

## Phase 5: Draw.io Generation Rules
- Keep layout clean: minimize crossings, use consistent spacing.
- Keep naming concise and readable.
- For report diagrams: aggressively simplify while preserving essential logic.
- For engineering diagrams: include typed data artifacts and full gate/loop logic.
- If user asks concise mode, enforce low node count target.

## Phase 6: Quality Checklist (Before Final)
- [ ] Requirements confirmed (>=95%)
- [ ] Correct template selected/created
- [ ] Text draft confirmed by user
- [ ] Node language policy respected
- [ ] Loop semantics correctly represented
- [ ] Layout clean (crossings minimized)
- [ ] Output path reported clearly

## Output Contract
Final response must include:
- generated file path(s)
- one-paragraph summary of what each diagram is for
- quick legend mapping (shape/line meaning)

## Companion Templates
- `templates/intake_checklist.md`
- `templates/flowchart_legend_default.md`
- `templates/concise_report_template.md`
