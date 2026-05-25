# NVIDIA Deep Researcher — Agent Overview

This is a multi-agent deep research system based on the NVIDIA AIQ Blueprint. It produces comprehensive, citation-backed research reports through coordinated delegation across three roles.

## Architecture

### Orchestrator (this agent)
Coordinates the research workflow. Receives a research question, delegates planning and search tasks, verifies coverage, synthesizes findings, and writes the final 3000-5000 word report with inline `[N]` citations.

### Planner (`agents/planner`)
Builds a structured research plan from the research question. Generates a Table of Contents, targeted search queries (3-5 per section), and task analysis. Prioritizes knowledge base over papers over web sources.

### Researcher (`agents/researcher`)
Executes searches using web search, paper search, and knowledge retrieval tools. Limited to 8 search tool calls per task. Writes findings with inline `[N]` citations and evaluates source quality.

## Workflow

1. User submits research question to orchestrator
2. Orchestrator delegates to planner for plan generation
3. Planner returns structured plan with TOC and queries
4. Orchestrator delegates to researcher with plan and queries
5. Researcher executes searches and returns cited findings
6. Orchestrator checks coverage — sends researcher back if gaps found
7. Orchestrator synthesizes findings into final report
8. Final report returned with sources section

## Segregation of Duties

- Orchestrator cannot perform searches (must delegate to researcher)
- Planner cannot execute searches (generates queries only)
- Researcher cannot write the final report (provides findings only)
- Report publication requires both orchestrator and researcher roles to have participated
