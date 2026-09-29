---
name: sharepoint-create-sharepoint-native-skill
description: Authors a validated native SharePoint skill (SKILL.md) source package locally. Does not deploy it -- creation and deployment are separate.
---

# create-sharepoint-native-skill

## Purpose

Produces a locally validated `SKILL.md` source package from explicit parameters — name,
description, instructions, input boundary, prohibited scope. Writes only to a local output path;
never connects to a tenant.

## Input boundaries

- `-SkillName` (required) — must match the `AgentAssets/Skills/<name>/` folder-naming convention
  (lowercase, alphanumeric and hyphens).
- `-SkillDescription` (required).
- `-InstructionsPath` **or** `-Instructions` (exactly one required) — no default instruction
  content is invented; the caller must supply real content.
- `-InputBoundary`, `-ProhibitedScope` (optional) — appended as their own sections when supplied.
- `-OutputPath` (required) — local file path; `-Overwrite` required to replace an existing file.

## Prohibited scope & Chat Runtime Boundaries
 
 - Performs zero tenant I/O — no `Connect-PnPOnline` call anywhere in this script.
 - Does not deploy the produced package — use `deploy-sharepoint-native-skill` separately, as a
   distinct, explicitly invoked step.
 - Does not use `create-test-skill.ps1` as a runtime dependency.
 
 > [!IMPORTANT]
 > **SharePoint Copilot Chat Web Runtime Boundary**:
 > Native skills executed by SharePoint Copilot chat agents running in the web interface do **NOT** have direct write/create-file capabilities to create new files in document libraries. 
 > - When designing skill instructions (e.g. diagram generators, report builders), author the skill to produce **copy-paste-ready structured content** (Markdown, Mermaid, JSON).
 > - If the skill includes a saving/persistence step, instruct the agent to provide the full content and suggested filename in chat and state that file upload requires external execution (e.g. workbench publish scripts) if automated creation tools are not available.

## Scripts

- `../../scripts/create-sharepoint-native-skill.ps1`

## Tests

`../../tests/unit/test_create_sharepoint_native_skill.py` — 5 executable tests run via `pwsh`
(valid-package generation, invalid-name rejection, missing-instructions rejection,
overwrite-protection, `-Overwrite` allowing replace). No tenant connection required or attempted.

