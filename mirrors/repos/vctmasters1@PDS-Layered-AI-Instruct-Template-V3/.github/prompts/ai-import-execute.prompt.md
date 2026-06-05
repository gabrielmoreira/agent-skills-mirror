---
mode: agent
description: Import/merge external projects with full Phase 0-7 orchestration and governance validation
---

# /ai-import-execute — Orchestrated Project Import Workflow

## Purpose

This prompt routes a **complete, governed project import workflow** through `/ai-route` — from source validation through integration, modernization, and naming compliance checks. It is the **only authorized mechanism** for importing, cloning, or merging external projects into this workspace.

**This prompt invokes `/ai-route` to:**
- Resolve the authoritative scope (deepest `.ai/instruct.md` for target paths)
- Check any governance rules that apply to imports
- Route to `pds-man-imports` (import domain authority)
- Gate each phase with pass/fail/block review

## Usage

In Copilot Chat:
```
/ai-import-execute <source_path_or_url>
```

Example:
```
/ai-import-execute k:\PDS-Master-001
/ai-import-execute https://github.com/myorg/myproject.git
```

---

## Entry Point (You are here)

**Your role:** Recognize the import request and route it.

If the user has mentioned any of these keywords, this is an import task:
- "clone" + project/repo reference
- "import" + external project name
- "merge" / "consolidate" / "integrate" + projects
- "adopt" / "migrate" + codebase

**Action:** Extract the **source location** (local path or GitHub URL) and invoke `/ai-route` with task context.

---

## Routing to `/ai-route`

**Invoke the Router with:**

```
/ai-route

Task: Import external project
Source: <source_path_or_url>
Target: <affected_paths_or_"root_for_now">
Context: This is a governed import workflow. 
  Route to pds-man-imports for orchestration of Phase 0-7 pipeline.
  Apply import governance rules if registered.
  Ensure imported customizations (prompts/agents/skills) comply with template paradigm.
```

The Router will:
1. Resolve the target scope (usually root `.ai/instruct.md`, but may find a deeper scope if user specifies a module path)
2. Check for import governance rules
3. Route to `pds-man-imports` agent with routing decision
4. `pds-man-imports` then executes Phases 0-7 with scope + governance context
5. Gate output after each phase

---

## What `/ai-route` Delegation Enables

By routing through the Router + Supervisor + pds-man-imports triad:

✅ **Scope awareness** — imported artifacts respect the deepest `.ai/instruct.md` authority  
✅ **Governance integration** — any org-level import policies are applied  
✅ **Stage gating** — pass/fail/block review between phases  
✅ **AI-INSTRUCT Maintenance** — if `.ai/instruct.md` changes needed, done in same operation  
✅ **Escalation handling** — retry with guidance or escalate to user on block  

---

## Post-Import Steps

After import completes successfully (Phase 0-7 validated):

### Step 1: Adapt Imported Infrastructure

If the imported project includes prompts, agents, skills, or MCP tools, adapt them to work with your routing paradigm:

```
/ai-adapt-infrastructure
```

This will:
- Discover all imported infrastructure files
- Analyze for template compliance
- Propose routing updates (make orchestration workflows use `/ai-route`)
- Fix frontmatter issues
- Register MCP tools properly
- Report compliance score

**Why?** Imported infrastructure won't automatically use your routing gateway. This step ensures all infrastructure respects your scope-aware orchestration architecture.

### Step 2: Validate

After adaptation, run a full validation:

```
/ai-validate
```

This confirms:
- No broken links
- All instruction files are coherent
- Ports don't conflict
- Project state is consistent

---

## See Also

- [/ai-route](ai-route.prompt.md) — the routing gateway (invoked from this prompt)
- [/ai-adapt-infrastructure](ai-adapt-infrastructure.prompt.md) — post-import infrastructure adaptation (recommended next step)
- [pds-man-imports](../agents/pds-man-imports.agent.md) — import domain manager (routed to, handles Phases 0-7)
- [pds-man-infrastructure](../agents/pds-man-infrastructure.agent.md) — infrastructure domain manager
- [pds-meta-router](../agents/pds-meta-router.agent.md) — scope/governance resolution agent
- [pds-pipe-super](../agents/pds-pipe-super.agent.md) — supervisor (orchestrates worker pipeline)
