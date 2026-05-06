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
6. Verify setup with a dry run or a small trigger prompt that should activate
   one selected skill.
7. Report the focused setup plan, files touched, commands to run, verification
   evidence, rollback notes, and remaining questions.

## Freshness Rule

Verify current official host documentation before giving exact host-specific
paths, commands, supported agents, scope behavior, or MCP config formats when
those details matter. Keep AgentSkills portfolio decisions separate from
current host installer facts.

## Decision Rules

- Do not recommend `all` unless the user explicitly wants every skill or is
  maintaining AgentSkills itself.
- Prefer the narrowest skillset that matches the repo's main job.
- Prefer atomic skills when the repo needs only a few workflows from different
  bundles.
- Keep `AGENTS.md` short: repo facts, selected AgentSkills routing, validation
  commands, and safety constraints. Put long procedures in docs or skills.
- If repo intent is unclear, ask only the missing questions that would change
  the skill selection or install scope.

## Safety Rules

- Do not run install, network, or MCP-enabling commands without explicit user
  approval.
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
- Approval-required actions
- Rollback notes
- Open questions

## References

- Read `references/onboarding-checklist.md` when creating a focused AgentSkills
  setup plan or editing project agent instructions.
