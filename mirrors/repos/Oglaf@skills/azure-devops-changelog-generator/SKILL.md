---
name: azure-devops-changelog-generator
title: "Azure DevOps Release Changelog Generator"
description: "Generate release notes and cards from Azure DevOps TFVC changesets or Git commits. Trigger this skill whenever the user mentions TFVC changesets, Git commits, Azure DevOps work items, 'generate changelog', 'cards.md', or 'release notes'. The skill asks for the Azure DevOps organization name, fetches work items via Azure DevOps APIs (requires $DEVOPS_PAT), analyzes descriptions and discussion, and produces cards.md and changelog.md grouped by Azure DevOps project name."
author: "Christian Fleishmann Silva (Oglaf)"
version: "2.0.0"
tags:
  - azure-devops
  - tfvc
  - git
  - changelog
  - release-notes
inputs:
  - name: version_control_type
    type: string
    description: "Type of version control: 'TFVC' for changesets or 'Git' for commits"
  - name: commits_changesets
    type: string
    description: "Text list of TFVC changesets or Git commits with messages referencing work items"
  - name: devops_pat
    type: string
    description: "Azure DevOps Personal Access Token (obtained from PowerShell variable $DEVOPS_PAT)"
outputs:
  - cards.md
  - changelog.md
---

# Skill: Azure DevOps Release Changelog Generator

## Purpose

Generate structured release documentation from **TFVC changesets** or **Git commits** by retrieving associated **Azure DevOps work items**, analyzing their full context, and producing:

1. A **complete card list**
2. A **release-style changelog grouped by Azure DevOps project**

The system must analyze the **work item description and discussion history** to produce accurate summaries.

---

# Inputs

### 1. Organization (Prompt First)

**Ask the user**: "Enter your Azure DevOps organization name (e.g., 'mycompany' from dev.azure.com/mycompany)"

Store this as `${organization}` variable.

---

### 2. Version Control Type (Prompt Second)

**Ask the user**: "Are these TFVC changesets or Git commits? (type 'TFVC' or 'Git')"

---

### 3. TFVC Changesets

A text list containing TFVC changesets with comments referencing work items.

Example:

```
4575 Developer Name 11490 - Description of changes
4565 Developer Name BUGS 9761, 11118, 11149
4567 Developer Name User Story 9975: Feature description
```

Changesets may reference **multiple cards**.

---

### 4. Git Commits

A text list containing Git commits with messages referencing work items.

Example:

```
abc1234 Fixes bug 11490 - JSON parsing error in Salesforce integration
def5678 Implements User Story 9975: Configuration maintenance
```

Commit messages follow the same patterns as changeset comments for work item references.

---

### 5. Azure DevOps Configuration

Personal Access Token (must be provided via PowerShell variable $DEVOPS_PAT)

The skill reads the Personal Access Token from the PowerShell variable $DEVOPS_PAT (process scope). Set it in PowerShell using:

```powershell
# For the current PowerShell session
$DEVOPS_PAT = 'your-personal-access-token'

# Or as an environment variable for child processes
$env:DEVOPS_PAT = 'your-personal-access-token'
```

API endpoints (replace `{organization}` with actual org name):

Work item API
```
https://dev.azure.com/{organization}/_apis/wit/workitems/{id}?api-version=7.0
```

Work item comments API
```
https://dev.azure.com/{organization}/_apis/wit/workItems/{id}/comments?api-version=7.0-preview
```

---

### Reusable Scripts

This skill includes reusable PowerShell scripts in the `scripts/` folder:

1. **fetch-workitems.ps1** - Fetches work items from Azure DevOps
2. **generate-cards.ps1** - Generates cards.md from workitems.json
3. **generate-changelog.ps1** - Generates changelog.md from workitems.json

**Usage:**

```powershell
# Set the PAT token
$env:DEVOPS_PAT = 'your-personal-access-token'

# Set the organization
$Organization = 'your-org-name'

# Step 1: Fetch work items
& "path/to/scripts/fetch-workitems.ps1" -WorkItemIds "10828, 11075, 10137, 11130, 11087" -Organization $Organization -OutputDir "C:\Temp"

# Step 2: Generate cards.md
& "path/to/scripts/generate-cards.ps1" -InputFile "C:\Temp\workitems.json" -Organization $Organization -OutputFile "C:\Temp\cards.md"

# Step 3: Generate changelog.md
& "path/to/scripts/generate-changelog.ps1" -InputFile "C:\Temp\workitems.json" -Organization $Organization -OutputFile "C:\Temp\changelog.md"
```

The scripts output:
- `workitems.json` - Raw work item data
- `cards.md` - Card list with details
- `changelog.md` - Release changelog grouped by project

---

# Processing Steps

## 1 Ask for Organization

Prompt the user: "Enter your Azure DevOps organization name (e.g., 'mycompany' from dev.azure.com/mycompany)"

Validate by checking the organization is non-empty.

---

## 2 Ask for Version Control Type

Prompt the user: "Are these TFVC changesets or Git commits? (type 'TFVC' or 'Git')"

Accept either "TFVC" or "Git" (case-insensitive).

---

## 3 Extract Work Item IDs

Parse the input (changeset comments or commit messages) and extract all numeric work item IDs.

Recognize patterns such as:

```
User Story 8413
Bug 11490
BUGS 9761, 11118
10086:
Fixes bug 12345
Implements User Story 9876
```

Rules:

* IDs are numeric
* Multiple IDs may appear in one changeset/commit
* Remove duplicates

---

# 4 Retrieve Work Item Data

For each ID retrieve:

### Core fields

* ID
* Title
* Work Item Type
* State
* Assigned To
* Description
* **Project** (System.Project) - used for team grouping

### Extended context

Also retrieve:

* Work item **discussion/comments**
* Work item **history notes**

---

# 5 Context Analysis

**IMPORTANT**: You MUST read and analyze the discussion/comments for each work item. This is the key value of using AI - the comments contain crucial context that is not in the title or description.

To generate precise changelog descriptions, analyze (in order of importance):

1. **Discussion / comments** - Read through all comments. They often contain:
   - Implementation details discussed during development
   - Testing results and validations
   - Specific requirements clarified in conversations
   - Links to specs and documentation
2. **Title**
3. **Description**
4. **Acceptance criteria if present**
5. **Changeset/Commit comment** - The original TFVC changeset or Git commit message that references the work item often contains specific change details (e.g., "Correções da integração", "Remoção do filtro", "Fixes bug 12345"). This is a primary source for understanding what specifically changed.

Use the full context to understand:

* What behavior changed
* What bug was fixed
* What functionality was added
* What integration or data change occurred

**Critical**: Do NOT just copy the title or description. Use the comments to understand the REAL change that was made. The comments often reveal what was discussed, tested, and validated.

---

# 6 Track Changeset/Commit-to-WorkItem Mapping

For each work item, track which changeset(s) or commit(s) contributed to it and what change details were mentioned:

```
Changeset/Commit abc1234: "Correções da integração com Salesforce" → Work Item 11490
Changeset/Commit def5678: "Remoção do filtro da query" → Work Item 11490
```

When generating descriptions, combine:
- The work item details (title, description)
- The specific change details from the changeset/commit comment

This is especially important when the same work item has multiple changesets/commits with different change descriptions.

---

# 7 Determine Responsible Team (by Project)

Team ownership is determined by the **Azure DevOps project name** from the work item's `System.Project` field.

Group work items by their project name:

```
## ProjectName1

## ProjectName2
```

Rules:

* Use the exact project name from Azure DevOps
* Each unique project becomes a section in the changelog
* Preserve original language in card titles and descriptions

---

# Outputs

Two files must be generated.

Save them to:

```
C:\temp\
```

---

# File 1: cards.md

Complete list of cards with metadata.

Format:

```
## {ID} – {Title} ({Work Item Type})

State: {State}
Assigned to: {AssignedTo}
Project: {ProjectName}
Link: https://dev.azure.com/{organization}/_workitems/edit/{ID}

{Short context-aware summary extracted from description + discussion}
```

Example:

```
## 11490 – Bug Title or Feature Title (Bug)

State: Resolved
Assigned to: Assignee Name
Project: ProjectName
Link: https://dev.azure.com/{organization}/_workitems/edit/11490

Fixes a bug or implements a feature described here.
```

---

# File 2: changelog.md

Must follow the **Release-Style Changelog Format** grouped by project.

Structure:

```
# Release Changelog

This release includes changes from the following Azure DevOps projects:

- ProjectName1
- ProjectName2
```

---

## {ProjectName}

Sections:

```
## New Features
## Bug Fixes
## Improvements
## Data / Scripts
```

---

# Changelog Item Format

```
- **{ID}** – {Title}
  {One concise sentence describing the change}
```

Example:

```
- **11490** – Erro Integração - Error reading JObject from JsonReader
  Fixes JSON parsing error when processing Salesforce integration responses.
```

---

# Summary Generation Rules

The changelog description must:

* Be **one sentence**
* Reflect the **actual functional impact** - what did this change DO for the user/system?
* **MUST be derived from discussion/comments** - read the comments to understand what was actually done
* Incorporate the specific change details mentioned in the changeset/commit message
* Avoid internal technical noise
* Avoid copying large blocks of text
* Focus on **what changed for the system or user**

**Key**: If a work item has comments, READ THEM. They contain the real context about what was implemented, tested, and validated. Use this to write a meaningful summary.

---

# Additional Rules

1. Deduplicate work items referenced by multiple changesets/commits.
2. Preserve original language of each card.
3. Group by project name (System.Project field) - not language.
4. Changelog must remain concise and readable for release documentation.
5. Use card discussion history to resolve ambiguous titles or incomplete descriptions.
6. Always reference the changeset/commit message to understand the specific change details that were made.

---

# Result

Transforms:

```
TFVC Changesets OR Git Commits
```

into

```
cards.md
changelog.md
```

with:

* automatic card discovery
* organization-agnostic (user provides org name)
* DevOps API enrichment
* discussion-aware summaries
* project-based grouping (instead of language-based)
* support for both TFVC and Git
* structured release notes.
