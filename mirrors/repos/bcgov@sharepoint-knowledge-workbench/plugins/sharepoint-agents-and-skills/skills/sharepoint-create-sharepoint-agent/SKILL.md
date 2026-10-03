---
name: sharepoint-create-sharepoint-agent
plugin: sharepoint-agents-and-skills
description: Authors a validated SharePoint Copilot agent (.agent JSON) source file locally, from explicit name, description, instructions and knowledge-source parameters, or from a Markdown template. Use to produce an agent package. Does not deploy it.
allowed-tools: Bash, Read, Write
---

# Create SharePoint Agent

Produce a locally validated `.agent` JSON source file (`schemaVersion 0.2.0`). Zero tenant I/O.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O: no `Connect-PnPOnline` anywhere in the script. Do not deploy the package here.
- At least one knowledge source is required, and exactly one instruction source (`-AgentInstructionsPath` or `-AgentInstructions`). `-Overwrite` is required to replace an existing file.
- It always sets `discourage_model_knowledge = true` to force grounding on the knowledge sources.
- Custom agents are read-only RAG: they cannot create files. `items_by_url` must match the live resource (use `get-agent-resource-identifiers.ps1`).

## Quick start

```powershell
pwsh -File scripts/create-sharepoint-agent.ps1 -AgentName "Policy Helper" -AgentDescription "Answers policy questions" -AgentInstructionsPath instructions.md -KnowledgeSourcePaths @('https://tenant.sharepoint.com/sites/x/Policies') -OutputPath policy-helper.agent
```

## Workflow

1. Choose the format: Markdown (`-AgentMarkdownTemplatePath`) or parameters/JSON (`-AgentName`, `-AgentDescription`, instructions, `-KnowledgeSourcePaths`, `-AgentTemplatePath`).
2. Resolve identifiers for each knowledge folder with `get-agent-resource-identifiers.ps1`.
3. Run the script with `-OutputPath`.
4. To bind native skills, follow the binding rules in the details reference.

## Verification

The output is valid `.agent` JSON with the expected sources (a single source stays an array). Deployment is a separate step.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Agent package authoring](references/agent-package-authoring-details.md): read for both formats, native-skill binding, the grounding table, identifier rules and the single-element array fix.
