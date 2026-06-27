# Agentic Setup Categories API Response Schema

## Endpoint

```text
GET /services/data/v67.0/agenticsetup/categories
GET /services/data/v67.0/agenticsetup/categories?fetchPrompts=true
```

## Response Structure

### PromptCategoryListRepresentation

Top-level response object.

| Field | Type | Description |
|-------|------|-------------|
| `categories` | array of PromptCategoryRepresentation | Categories sorted alphabetically by localized label |

### PromptCategoryRepresentation

A single prompt category.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Stable programmatic identifier (e.g., "UserManagement") |
| `label` | string | Localized display label (e.g., "User Management") |
| `prompts` | array of PromptRepresentation | Populated when `fetchPrompts=true`; empty array otherwise |

### PromptRepresentation

A single prompt entry within a category.

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | User-facing prompt text to display and pass to the LLM |
| `description` | string | Short helper description shown next to the prompt |

## Example Response (fetchPrompts=false)

```json
{
  "categories": [
    {
      "label": "Flow Management",
      "name": "FlowManagement",
      "prompts": []
    },
    {
      "label": "Identity",
      "name": "Identity",
      "prompts": []
    },
    {
      "label": "User Management",
      "name": "UserManagement",
      "prompts": []
    }
  ]
}
```

## Example Response (fetchPrompts=true)

```json
{
  "categories": [
    {
      "label": "Flow Management",
      "name": "FlowManagement",
      "prompts": [
        {
          "description": "Scaffold a new flow",
          "text": "Design a flow that [describe trigger and outcome]."
        },
        {
          "description": "List active flows",
          "text": "List all active flows in this org. Include the object, trigger type, and last modified date for each."
        }
      ]
    },
    {
      "label": "User Management",
      "name": "UserManagement",
      "prompts": [
        {
          "description": "Activate a user",
          "text": "Activate user [user]. Confirm what becomes accessible to them again and whether their license is still available."
        },
        {
          "description": "Clone a user",
          "text": "Clone [existing user] to create a new user for [new person's name and email]."
        }
      ]
    }
  ]
}
```

## Error Responses

### FUNCTIONALITY_NOT_ENABLED

Returned when the Agentic Setup Categories feature is not enabled on the org.

```json
[
  {
    "message": "This feature is not currently enabled for this user type or org: [AgenticSetupCategoriesApiFamily]",
    "errorCode": "FUNCTIONALITY_NOT_ENABLED"
  }
]
```

### Access Requirements

The endpoint uses a two-tier security model:
1. **Org-level**: `SetupCopilot.orgHasEnhancedAgenticSetup` must be true
2. **User-level**: `SetupCopilot.orgHasSetupHomePromptLibrary` must be true per request

If either check fails, the API returns `FUNCTIONALITY_NOT_ENABLED`.
