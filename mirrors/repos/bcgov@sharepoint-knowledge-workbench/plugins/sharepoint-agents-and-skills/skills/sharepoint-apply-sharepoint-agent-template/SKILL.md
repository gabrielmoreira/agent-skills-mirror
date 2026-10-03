---
name: sharepoint-apply-sharepoint-agent-template
plugin: sharepoint-agents-and-skills
description: Applies an existing agent template to a specific target, producing a concrete .agent package through create-sharepoint-agent. Use after a template exists, to produce an agent for one set of knowledge sources. Zero tenant I/O; does not deploy.
allowed-tools: Bash, Read, Write
---

# Apply SharePoint Agent Template

Fill a template's knowledge-source placeholders with real URLs, assemble the final instructions from its sections, and delegate to `create-sharepoint-agent` to write the `.agent` package.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O. Do not deploy the produced package.
- `-KnowledgeSourcePaths` must contain exactly the template's `KnowledgeSourcePlaceholderCount`; reject a mismatch rather than truncating or padding.
- `-TemplatePath` must exist; `-AgentName` and `-AgentDescription` are required because the template has no identity. `-Overwrite` is passed through to `create-sharepoint-agent.ps1`.
- Pass several `-KnowledgeSourcePaths` with `pwsh -Command` and an explicit `@(...)` array; multi-value arrays followed by more named parameters are unreliable under `-File`.

## Quick start

```powershell
pwsh -File scripts/apply-sharepoint-agent-template.ps1 -TemplatePath template.json -AgentName "Policy Helper" -AgentDescription "Answers policy questions" -KnowledgeSourcePaths "https://tenant.sharepoint.com/sites/x/Policies" -OutputPath policy-helper.agent
```

## Workflow

1. Confirm the template exists and note its `KnowledgeSourcePlaceholderCount`.
2. Collect the agent name, description and exactly that many knowledge-source URLs.
3. Run the script. It delegates to `create-sharepoint-agent.ps1` to write the package.

## Verification

A valid `.agent` file exists at `-OutputPath` and its knowledge sources match the supplied URLs. To deploy it, use a separate step.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Agent package authoring](references/agent-package-authoring-details.md): read for how templates, create and update fit together, and the tests.
