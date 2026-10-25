---
name: managing-sharepoint-copilot-agents-and-skills
description: "Author, package, deploy, verify, backup, and restore SharePoint Copilot declarative agents and native skill actions. Use when asked to 'create copilot agent', 'ground agent on library', 'prepare agentassets', 'deploy native skill', 'verify copilot skill', 'backup agents', or 'backup skills'."
---

# Managing SharePoint Copilot Agents and Skills

Use the track that matches the requested artifact. Read the linked mode
instruction before running a script; it preserves the complete parameter
contract, prompts, examples, and safety gates for that operation.

## Track A: Declarative Copilot Agents

1. **Create agent** — `references/modes/create-agent.md`
2. **Apply template** — `references/modes/apply-template.md`
3. **Configure knowledge** — `references/modes/configure-knowledge.md`
4. **Provision AgentAssets** — `references/modes/provision-agentassets.md`
5. **Backup or restore agents** — `references/modes/backup-restore-agents.md`

Supporting scripts are in `scripts/`. Agent package templates are in
`assets/templates/` when a package-authoring mode requires them.

## Track B: Native Copilot Skills

1. **Scaffold skill** — `references/modes/scaffold-skill.md`
2. **Deploy skill** — `references/modes/deploy-skill.md`
3. **Verify skill probe** — `references/modes/verify-skill-probe.md`
4. **Undeploy or roll back skill** — `references/modes/undeploy-rollback-skill.md`
5. **Backup or restore skills** — `references/modes/backup-restore-skills.md`

## Acceptance criteria

Operation-specific acceptance criteria are in `references/*-acceptance-criteria.md`.
Use the matching file as the verification contract before declaring an operation
complete.

## Safety

- Authoring is local and read-only with respect to the tenant.
- Preview deployment, restore, and undeploy operations before using `-Execute`.
- Preserve exact confirmation-token requirements documented by each mode.
- `provision-agentassets.ps1` is the documented immediate-write exception.
- Run tenant-facing PowerShell commands in the operator's terminal.
