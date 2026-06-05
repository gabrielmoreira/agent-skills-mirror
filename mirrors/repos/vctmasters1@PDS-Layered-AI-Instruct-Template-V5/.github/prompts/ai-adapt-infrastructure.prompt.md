---
mode: agent
description: Adapt imported infrastructure (prompts, agents, skills, MCP tools) to use routing gateway and template paradigm
---

# /ai-adapt-infrastructure

Route infrastructure adaptation through `/ai-route`, then analyze imported/new prompts, agents, skills, and MCP tools, adapt them to work with the routing gateway, and validate against template paradigm.

## Quick Start

In Copilot Chat:
```
/ai-adapt-infrastructure
```

To adapt infrastructure in a specific scope:
```
/ai-adapt-infrastructure src/api
```

---

## What This Workflow Does

When you import infrastructure from another project or create new infrastructure, it may not follow your routing paradigm. This workflow:

1. **Discovers** all prompts (`.prompt.md`), agents (`.agent.md`), skills (`SKILL.md`), and MCP tools (`.json`)
2. **Analyzes** each for routing compliance:
   - Does it use `/ai-route` as a gateway?
   - Does it have proper frontmatter (mode, description)?
   - Does it follow naming conventions?
   - Is it compatible with the template paradigm?
3. **Proposes** adaptations:
   - Add routing for orchestration workflows
   - Fix frontmatter issues
   - Register MCP tools properly
   - Update scope context
4. **Applies** approved changes
5. **Validates** all infrastructure against template paradigm

---

## Workflow: Route → Analyze → Adapt

### Step 1: Route Through `/ai-route`

**Invoke the Router:**

```
/ai-route

Task: Adapt infrastructure to routing paradigm and template compliance
Scope: root (or user-specified scope)
Context: This is an infrastructure migration workflow.
  Route to pds-man-infrastructure for infrastructure analysis, adaptation, and MCP registration.
  Ensure all prompts, agents, and skills are routing-aware.
  Validate against template paradigm (frontmatter, naming, structure).
```

The Router will:
1. Resolve the target scope (which `.ai/instruct.md` governs infrastructure?)
2. Check for infrastructure governance rules
3. Route to `pds-man-infrastructure` with scope context
4. `pds-man-infrastructure` executes adaptation pipeline

### Step 2: Infrastructure Adaptation (via pds-man-infrastructure)

Once routed, the infrastructure manager will:

#### Phase 1: Discovery

Scan the resolved scope for:
- **Prompts**: All `.prompt.md` files in `.github/prompts/`
- **Agents**: All `.agent.md` files in `.github/agents/`
- **Skills**: All `SKILL.md` files in `.github/skills/*/`
- **MCP tools**: All `.json` tool definitions in `.ai/agents/tools/` and `.ai/mcp/tools/`

#### Phase 2: Analysis

For each discovered file, check:

**Prompts (`.prompt.md`)**:
- ✓ Has valid YAML frontmatter with `mode:` and `description:` fields
- ✓ Description is at least 10 characters (clarity check)
- ✓ If `mode: agent`, is it routing through `/ai-route` first?
- ✓ Kebab-case naming convention
- ✓ Links to relevant agents/tools are correct

**Agents (`.agent.md`)**:
- ✓ Has valid YAML frontmatter with `description:` field
- ✓ Description is at least 20 characters
- ✓ If a workflow orchestrator, does it route through `/ai-route`?
- ✓ If has `tools:` list, is it valid array format?
- ✓ Kebab-case naming convention
- ✓ No tool security issues (doesn't request unnecessary tools)

**Skills (`SKILL.md`)**:
- ✓ Directory follows kebab-case naming
- ✓ Has valid YAML frontmatter with `description:` field
- ✓ Description is at least 20 characters
- ✓ Content provides actionable guidance (not just theory)
- ✓ References proper documentation links

**MCP Tools (`.json`)**:
- ✓ Valid JSON structure with required fields
- ✓ Tool name follows kebab-case convention
- ✓ Includes `checklist` and `safety_level` fields (governed tool pattern)
- ✓ Registered in appropriate registry (`.ai/agents/tools/` for built-in, `.ai/mcp/tools/` for project-specific)
- ✓ No duplicate definitions

#### Phase 3: Categorize Findings

Group issues by category:
- **ERRORS** (must fix): Invalid YAML, missing required fields, security issues
- **WARNINGS** (should fix): Non-compliant naming, incomplete descriptions, routing issues
- **INFO** (nice-to-have): Suggestions for clarity or consistency

#### Phase 4: Propose Adaptations

For each issue, propose a specific adaptation:

**Example 1: Prompt not routing**
```
Issue: /my-workflow.prompt.md doesn't use /ai-route
Proposal: Add routing step as first action
  Before: "Step 1: Recognize the task..."
  After: "Step 1: Route through /ai-route with task context..."
  References: /ai-route.prompt.md, pds-meta-router.agent.md
```

**Example 2: Agent missing frontmatter**
```
Issue: my-agent.agent.md has no description field
Proposal: Add frontmatter
  Before: (no frontmatter)
  After: 
    ---
    description: [inferred from file content + user confirmation]
    tools: [list if applicable]
    ---
```

**Example 3: MCP tool not in registry**
```
Issue: custom-tool.json exists but not in .ai/mcp/tools/
Proposal: Register tool
  Action: Move to .ai/mcp/tools/custom-tool.json
  Register: Add entry to .ai/mcp/tools/registry.json (if exists)
```

#### Phase 5: Ask for Approval

Present all proposed adaptations:
- Group by file
- Show before/after for each change
- Ask user: Apply all? Apply selected? Skip?

#### Phase 6: Apply Approved Changes

For approved changes:
- Rewrite files with adaptations
- Update frontmatter
- Register MCP tools
- Create/update tool registry files if needed
- Log all changes

#### Phase 7: Validate

Run final validation:
- Re-check all infrastructure files
- Confirm frontmatter is valid YAML
- Confirm all routing references are correct
- Confirm MCP tool registrations are complete
- Generate compliance report

#### Phase 8: Report

Show:
- Total files analyzed
- Files adapted (errors fixed)
- Files warned (non-compliant but functional)
- Compliance score (% of files meeting template paradigm)
- Any remaining issues or warnings

---

## Infrastructure Paradigm Rules

All infrastructure must follow:

| Type | Rule | Enforced By |
|------|------|-----------|
| **Prompts** | Mode field required (ask/edit/agent) | YAML validation |
| **Prompts** | Description ≥10 chars | Phase 2 analysis |
| **Prompts** | Orchestration prompts must route | Phase 2 + Phase 4 proposal |
| **Agents** | Description ≥20 chars | YAML validation |
| **Agents** | Tools list must be valid array | YAML validation |
| **Skills** | Directory is kebab-case | Phase 2 analysis |
| **Skills** | Description ≥20 chars | YAML validation |
| **MCP Tools** | Valid JSON structure | YAML validation |
| **MCP Tools** | Includes checklist + safety_level | Phase 2 analysis |
| **All** | Kebab-case naming | Phase 2 analysis |
| **All** | No duplicate definitions | Phase 1 discovery |

---

## When to Run

✅ **After importing infrastructure** from another project (run after `/ai-import-execute`)  
✅ **After creating new infrastructure** (adapt before committing)  
✅ **When adding MCP tools** (ensure proper registration)  
✅ **During refactoring** (ensure all infrastructure uses routing)  
✅ **For compliance audits** (check paradigm adherence)

---

## See Also

- [/ai-route](ai-route.prompt.md) — the routing gateway (invoked from this prompt)
- [pds-man-infrastructure](../agents/pds-man-infrastructure.agent.md) — infrastructure domain manager (routed to)
- [Routing & Orchestration Gateway](.ai/instruct.md#routing--orchestration-gateway) — why routing matters
- [AI Prompt Files](.github/copilot-instructions.md#ai-prompt-files-githubprompts) — prompt structure rules
- [Custom Agents](.github/copilot-instructions.md#custom-agents-githubagents) — agent structure rules
