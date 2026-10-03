---
name: sharepoint-update-sharepoint-agent
plugin: sharepoint-agents-and-skills
description: Updates an existing local .agent source package's description, instructions or knowledge sources in place, without recreating the whole package. Use to change an agent you already authored. Zero tenant I/O.
allowed-tools: Bash, Read, Write
---

# Update SharePoint Agent

Change an agent's instructions or grounding sources without running create again from scratch. It operates on the local `.agent` JSON that `create-sharepoint-agent` produces.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O. Do not deploy the updated package.
- `-AgentPath` must already exist: this updates, never creates.
- Pass at least one of `-AgentDescription`, `-AgentInstructionsPath`/`-AgentInstructions`, `-KnowledgeSourcePaths`; a no-op call is rejected.
- Never silently clear all grounding: an empty `-KnowledgeSourcePaths` needs `-AllowEmptyKnowledgeSources`.

## Quick start

```powershell
pwsh -File scripts/update-sharepoint-agent.ps1 -AgentPath policy-helper.agent -AgentDescription "Updated description"
```

## Workflow

1. Confirm the `.agent` file and what changes.
2. Run the script with only the parameters to change.
3. Redeploy through a separate step.

## Verification

The changed field is updated and the others (for example instructions) are unchanged.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Agent package authoring](references/agent-package-authoring-details.md): read for update behavior and the tests.
