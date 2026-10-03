---
name: sharepoint-create-sharepoint-native-skill
plugin: sharepoint-agents-and-skills
description: Authors a validated native SharePoint skill (SKILL.md) source package locally. Use to write a skill for a site's AgentAssets library. Does not deploy it; creation and deployment are separate.
allowed-tools: Bash, Read, Write
---

# Create SharePoint Native Skill

Produce a locally validated `SKILL.md` source package from explicit parameters.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O. Deploy separately with `sharepoint-deploy-sharepoint-native-skill`.
- `-SkillName` must be lowercase alphanumerics and hyphens, matching the `AgentAssets/Skills/<name>/` folder. `-SkillDescription` is required. Supply exactly one of `-InstructionsPath` or `-Instructions`: no default instruction content is invented.
- `-OutputPath` is required; `-Overwrite` replaces an existing file.
- Native skills in the SharePoint Copilot chat web runtime cannot create files: author them to produce copy-paste-ready structured content (Markdown, Mermaid, JSON).

## Quick start

```powershell
pwsh -File scripts/create-sharepoint-native-skill.ps1 -SkillName my-skill -SkillDescription "Does X when asked Y" -InstructionsPath instructions.md -OutputPath ./my-skill/SKILL.md
```

## Workflow

1. Collect the name, a description that states purpose and trigger phrases, and the real instructions.
2. Add `-InputBoundary` and `-ProhibitedScope` if needed (appended as their own sections).
3. Run the script, then deploy with the deploy skill.

## Verification

A `SKILL.md` exists at `-OutputPath`; an invalid name, missing instructions, or an existing file without `-Overwrite` is rejected.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Native skill lifecycle](references/native-skill-lifecycle-details.md): read for the chat runtime boundary, the full lifecycle and the tests.
