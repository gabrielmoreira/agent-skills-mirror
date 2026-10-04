---
name: sharepoint-create-agent-template
plugin: sharepoint-copilot-agents-and-skills
description: Authors a reusable SharePoint agent template (purpose, instruction structure, boundaries, refusal behavior, citation expectations, knowledge-source placeholders, governance metadata), distinct from a concrete .agent package. Use to capture a reusable agent shape. Zero tenant I/O.
allowed-tools: Bash, Read, Write
---

# Create SharePoint Agent Template

Capture the reusable shape of an agent separately from any deployment target. `create-agent-package-from-template` later fills it in.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O. This does not produce a deployable `.agent` file; use `sharepoint-create-agent-package-from-template` for that.
- Required: `-TemplateName`, `-Purpose`, `-TemplateVersion`, `-KnowledgeSourcePlaceholderCount` (>= 1), `-OutputPath`, and exactly one of `-InstructionsTemplatePath` or `-InstructionsTemplate`.
- `-AnswerBoundary`, `-RefusalBehavior` and `-CitationExpectations` are optional and appended as their own sections. `-Overwrite` replaces an existing file.

## Quick start

```powershell
pwsh -File scripts/create-sharepoint-agent-template.ps1 -TemplateName policy-helper -Purpose "Answer policy questions" -TemplateVersion 1.0 -KnowledgeSourcePlaceholderCount 2 -InstructionsTemplatePath instructions.md -OutputPath policy-helper.template.json
```

## Workflow

1. Decide the purpose, boundaries and how many knowledge sources a concrete agent will need.
2. Run the script.
3. Apply the template with `sharepoint-create-agent-package-from-template`.

## Verification

The template file exists with the intended placeholder count and the optional sections you supplied.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Agent package authoring](references/agent-package-authoring-details.md): read for templates versus agents and the tests.
