---
name: sharepoint-create-sharepoint-agent
description: Authors a validated SharePoint Copilot agent (.agent JSON) source file locally, from explicit name/description/instructions/knowledge-source parameters. Does not deploy it.
---

# create-sharepoint-agent

## Purpose

Produces a locally validated `.agent` JSON source file per the reverse-engineered schema
(`schemaVersion 0.2.0`, `customCopilotConfig.gptDefinition`) — new build, parameterized per the
design doc's Section 4 script parameter matrix, not extracted verbatim from any of the 5
experimental `create-*-agent.ps1`/`create-md-comparison-agent.ps1` scripts (
kept in `tools/` as research/evidence of the schema pattern this script implements generically).

## Input boundaries & Dual-Format Support

`create-sharepoint-agent.ps1` supports authoring from either format:

1. **Markdown Format (`.agent.md`):**
   - `-AgentMarkdownTemplatePath` — reads a human-friendly Markdown template (e.g. `qa-test-list-agent.agent.md` or `sharepoint-agent.template.md`), automatically parsing `# Name`, `## Purpose`, and grounding URLs.
2. **Declarative Parameter/JSON Format:**
   - `-AgentName`, `-AgentDescription`
   - `-AgentInstructionsPath` or `-AgentInstructions`
   - `-KnowledgeSourcePaths` (array of URLs)
   - `-AgentTemplatePath` — JSON structure template (`sharepoint-agent.template.json`).
3. **Target Output:**
   - `-OutputPath` (required); `-Overwrite` required to replace an existing file.

## Prohibited scope

- Zero tenant I/O — no `Connect-PnPOnline` call anywhere in this script.
- Does not deploy the produced package — agent upload is a separate, not-yet-built capability.
- Always sets `behavior_overrides.special_instructions.discourage_model_knowledge = true` to
  force grounding on knowledge sources, matching the confirmed-working reference-agent pattern.

## Scripts

- `../../scripts/create-sharepoint-agent.ps1`

## Native Skill Binding in SharePoint Agents

> [!TIP]
> **How Native Skills Bind to SharePoint Agents**:
> - The SharePoint `.agent` JSON schema contains **no documented property** (e.g. `skills`, `skillIds`) for hard-binding a native skill directly.
> - Instead, the SharePoint runtime matches skills dynamically based on:
>   1. **Skill's YAML Description**: The `description` field in `/AgentAssets/Skills/<skill-name>/SKILL.md` must clearly state its purpose and trigger phrases.
>   2. **Explicit Invocation in Conversation Starters**: Each conversation starter in `.agent` should explicitly state `"Use the <skill-name> skill to..."`.
>   3. **Unambiguous Agent Instructions**: Agent `instructions` must explicitly state `"For every request to [action], you must invoke and follow the native SharePoint skill named <skill-name>. Do not independently reproduce or substitute your own procedure."`
>   4. **Exact Folder Matching**: The skill name referenced must match `/AgentAssets/Skills/<skill-name>/SKILL.md` exactly.

## Grounding & Architecture Boundaries: Agents vs. Skills

| Layer | Artifact | Role | Grounding Enforcement | Write Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Enforced Scope** | `.agent` (`capabilities.items_by_url`) | **What to Know** | **Hard Structural Boundary**: The retrieval layer restricts access strictly to the curated list of up to 20 sources. | **Read-Only / RAG**: Generates cited responses; cannot create or write files. |
| **Site Context** | `SHAREPOINT.md` (in `AgentAssets`) | **Site Knowledge** | **Site-Level Bias**: Automatically loaded into all chat sessions on that site. | **None**: Informational context. |
| **Workflow** | `SKILL.md` (in `AgentAssets/Skills`) | **How to Act** | **Soft Procedural Bias**: Instructions steer model behavior, but cannot enforce a strict file/folder retrieval boundary. | **Read & Synthesis**: Full content generation and native file creation occur only in first-party Copilot in SharePoint. |
| **Write Extensions** | Copilot Studio / SPFx | **Actions** | **Connector/API Controlled**: Enforced by Power Platform or Graph API permissions. | **Active Writes**: Required if custom agents must write directly to SharePoint document libraries. |

## Troubleshooting & Permissions Note

> [!IMPORTANT]
> **SharePoint Copilot UI Agent Permissions & Capabilities**:
> 1. **Read-Only / No Direct Write in Custom Agents**: Custom `.agent` definitions operate in **read-only / retrieval-augmented generation (RAG)** mode and **do NOT have write/create-file capabilities**. When generating new documents, code, or diagrams, instructions must format outputs as copy-paste-ready blocks (e.g. Mermaid markdown, structured JSON) for human or pipeline upload.
> 2. **Site Owner Permissions**: Being a **Site Collection Administrator** alone is not sufficient for Microsoft 365 Copilot user grounding runtime. The user must also be an explicit **Site Owner** (or member of the SharePoint site Owners group).
> 3. **Exact GUID & Type Matching**: `items_by_url` must match the live SharePoint resource:
>    - For Custom Lists: `type: "List"`, `unique_id: "00000000-0000-0000-0000-000000000000"`, `list_id: "<real-list-guid>"`.
>    - For Document Libraries / Folders: `type: "Folder"`, `unique_id: "<real-folder-guid>"` (or `"00000000-0000-0000-0000-000000000000"` if top-level), and the library's `list_id`. Never assign another folder's GUID to an arbitrary subfolder.
>    - Use `get-agent-resource-identifiers.ps1` with `-ConfigFile` to dynamically query and resolve exact identifiers.

## Tests

`../../tests/unit/test_create_sharepoint_agent.py` — 4 executable tests via `pwsh` (valid
`.agent` JSON produced, at-least-one-knowledge-source enforced, overwrite protection, mutually-
exclusive instruction sources).

**Real bug found and fixed while writing these tests:** `ConvertTo-Json` silently unwraps a
single-element PowerShell array into a bare object — `items_by_url` with exactly one knowledge
source was serialized as `{...}` instead of `[{...}]`, which would have produced schema-invalid
output for the single-source case (the most common one). Fixed with an explicit
`[System.Object[]]` cast.

