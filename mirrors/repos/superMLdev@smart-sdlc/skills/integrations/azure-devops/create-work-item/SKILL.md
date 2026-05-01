---
name: azure-devops-create-work-item
description: "Create an Azure DevOps work item (User Story, Task, or Bug) from a Smart SDLC story or bug report. Use when the user says 'create ADO work item', 'add to ADO', or 'sync story to Azure DevOps'."
---

# Azure DevOps — Create Work Item

## Goal

Create a properly structured Azure DevOps work item from a Smart SDLC story, with full acceptance criteria, story points, and area path set correctly.

---

## Prerequisite Check

Check `integrations.azure_devops` in `_superml/config.yml`. If missing: "Run `azure-devops-connect` first."

---

## Step 1: Load Story

Ask: "Which story are you creating a work item for?" (accept S-ID or title)

Load the story file. Extract:
- Title
- Acceptance criteria
- Story points / estimate
- Priority
- Epic link (if any)

---

## Step 2: Select Work Item Type

Map story type to ADO work item type:

| Story Type | ADO Work Item Type |
|-----------|-------------------|
| Feature / user story | User Story |
| Technical task | Task |
| Bug | Bug |
| Spike | Task (with [SPIKE] prefix) |

---

## Step 3: Create Work Item

```bash
az boards work-item create \
  --title "{story_title}" \
  --type "{work_item_type}" \
  --description "{story_description}" \
  --fields \
    "Microsoft.VSTS.Scheduling.StoryPoints={points}" \
    "Microsoft.VSTS.Common.Priority={priority}" \
    "System.AreaPath={area_path}"
```

---

## Step 4: Add Acceptance Criteria

```bash
az boards work-item update \
  --id {work_item_id} \
  --fields "Microsoft.VSTS.Common.AcceptanceCriteria={formatted_acs}"
```

Format ACs as HTML list:
```html
<ul>
  <li>AC-1: ...</li>
  <li>AC-2: ...</li>
</ul>
```

---

## Step 5: Update Story File

Add ADO work item reference to story frontmatter:
```yaml
ado_id: {work_item_id}
ado_url: "https://dev.azure.com/{org}/{project}/_workitems/edit/{id}"
```

---

## Done

> ✅ Work item #{work_item_id} created: {url}
