---
name: sharepoint-scaffold-spfx-master-detail
plugin: sharepoint-spfx-authoring
description: Scaffolds a complete SPFx Master-Detail Web Part boilerplate (TypeScript, SCSS module, manifest) from a JSON list layout specification. Use when modernizing legacy SharePoint 2013/2016 multi-list briefing or dossier pages (e.g. Appearing_Persons_Briefing.aspx) that rely on URL parameter query filtering (?SelectedID=...).
allowed-tools: Bash, Read, Write
---

# scaffold-spfx-master-detail

## Overview

Modern SharePoint Online out-of-the-box List Web Parts do not support URL query string parameter filtering (`?SelectedID=...`). When modernizing classic ASPX pages that rely on URL-driven cross-web-part filtering, this skill generates a single, consolidated **Master-Detail SPFx Web Part** (TypeScript, SCSS module, manifest) that replaces multi-web-part classic layouts with a clean, responsive modern dashboard.

## Toolchain Requirements

- **Python**: 3.8+
- **Node.js**: LTS version (v18 or v22)
- **SPFx**: 1.20+ (using Heft / Webpack build toolchain)

## Core Workflow

### Step 0: Initialize SPFx Solution Workspace (If Starting from Scratch)

You can either:
- **Option A (Instant Template)**: Copy the pre-configured project boilerplate from `../../assets/templates/spfx-project-reference/` to your target directory.
- **Option B (Yeoman Generator)**: Run `yo @microsoft/sharepoint` selecting component type `WebPart`, template `Minimal` (Node v22/v18 LTS required).

### Step 1: Prepare the JSON Layout Specification

Create a spec JSON file (e.g. `dossier_spec.json`) describing the primary record, lookup relationships, and child event lists:

```json
{
  "webPartName": "PersonBriefing",
  "title": "Master-Detail Dossier Dashboard",
  "primaryList": "Persons",
  "lookupList": "Authors",
  "childLists": [
    {
      "title": "Upcoming Appearances",
      "listName": "All_Appearances",
      "filterField": "RelatedAuthorId"
    },
    {
      "title": "Background Information",
      "listName": "Dossier_Narratives",
      "filterField": "RelatedAuthorId"
    }
  ],
  "imageLibrary": "Images"
}
```

### Step 2: Execute Scaffolding Script

Run the generator script relative to the skill root:

```bash
python ../scripts/scaffold_spfx_master_detail.py --spec path/to/dossier_spec.json --output-dir path/to/spfx-project/src/webparts/personBriefing
```

### Step 3: Verify Output Artifacts

Confirm the generator created the 3 required files in the target directory:
1. `PersonBriefingWebPart.ts` — Parallel REST querying, URL parameter parsing (`?SelectedID=...`), dynamic HTML rendering, and action link routing.
2. `PersonBriefingWebPart.module.scss` — Fluent UI responsive grid, card layout, portrait photo box, data tables, and action buttons.
3. `PersonBriefingWebPart.manifest.json` — SPFx component definition with a unique GUID.

### Step 4: Next Steps

Once scaffolded, proceed to package the solution using the `package-spfx-solution` skill.

