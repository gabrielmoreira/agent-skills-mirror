---
name: agentskills-project-onboarding
description: Set up AgentSkills in a new or existing repository in a focused way. Use when Codex is asked to onboard AgentSkills, choose the right skillset or skills for a repo, create or update project agent instructions, decide project vs user scope, configure focused routing, recommend MCP presets, or verify that AgentSkills works in a repository without installing unnecessary broad bundles.
license: MIT
---

# AgentSkills Project Onboarding

## Core Workflow

1. Inspect the repository before recommending anything: language, framework,
   package files, CI, test commands, docs, deployment files, existing agent
   instructions, and likely work modes.
2. Identify the smallest useful AgentSkills profile: one skillset, or 3-8
   atomic skills when a full skillset would be too broad.
3. Choose install scope: prefer project scope for repo-specific focus; use user
   scope only for durable personal workflows across many repos.
4. Plan project instructions: preserve existing `AGENTS.md`, `CLAUDE.md`,
   `GEMINI.md`, `.github/copilot-instructions.md`, and Cursor rules; propose a
   patch instead of replacing them.
5. Recommend MCP presets only when the repo workflow needs them and explain the
   tool/security implication.
6. If setup is authorized and the target scope is clear, preview and apply the
   requested install, then verify the result. Change project instructions only
   when that is also authorized. For recommendation-only requests, stop at the
   plan and preview.
7. Verify installed files separately from discovery: use a fresh host task and
   a small trigger prompt when available. Report the plan or completed setup,
   files touched, evidence, rollback notes, and remaining questions.

## Freshness Rule

Verify current official host documentation before giving exact host-specific
paths, commands, supported agents, scope behavior, or MCP config formats when
those details matter. Keep AgentSkills portfolio decisions separate from
current host installer facts.

## Decision Rules

- Do not recommend `all` unless the user explicitly wants every skill or is
  maintaining AgentSkills itself.
- Prefer the narrowest skillset that matches the repo's main job.
- For durable personal workflows, start with `global-foundation`; keep domain
  bundles in project scope. The Codex adapter installs skills only by default;
  MCP setup and project routing are separate explicit options.
- Prefer atomic skills when the repo needs only a few workflows from different
  bundles.
- Keep `AGENTS.md` short: repo facts, selected AgentSkills routing, validation
  commands, and safety constraints. Put long procedures in docs or skills.
- If repo intent is unclear, ask only the missing questions that would change
  the skill selection or install scope.

## Safety Rules

- An explicit install request authorizes that install in the stated scope;
  reuse that authorization after inspecting the source and previewing changes.
  A recommendation request does not authorize installation. Obtain approval
  for additional scope or MCP enablement not already requested, and respect
  host permissions and repository review gates.
- Do not overwrite existing project instruction files; show a patch or create a
  clearly scoped new section.
- Do not invent build, test, lint, deploy, or environment commands.
- Do not enable broad MCP access, browser automation, or network-backed tools
  without explaining why they are needed.
- Do not add secrets, credentials, private URLs, or sensitive customer/project
  data to instruction files.

## Deliverable Shape

- Repo readout
- Recommended AgentSkills profile
- Skillsets or atomic skills to install
- Host and install-scope recommendation
- Project instruction plan
- MCP preset recommendation
- Verification steps and expected trigger prompt
- Actions completed and any actions still requiring approval
- Rollback notes
- Open questions

## References

- Read `references/onboarding-checklist.md` when creating a focused AgentSkills
  setup plan or editing project agent instructions.
