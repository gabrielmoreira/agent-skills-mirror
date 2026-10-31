# Example confirm card (Generate)

Show this card in chat with the preview JSON. Do not put the JSON in report.md.

Intent paraphrase: Developer-edition scratch-def for a B2B Revenue Cloud
project. Features are what the helper mapped from the user's words — not
extra catalog tokens.

- Edition: Developer
- Features: CoreCpq
- Settings enriched:
  - revenueManagementSettings.enableCoreCPQ = true
- Output path (after confirm): config/project-scratch-def.json

**Required in the chat reply (not in report.md):** show the schema-valid
helper `document` as a fenced JSON block. Example:

```json
{
  "edition": "Developer",
  "features": [
    "CoreCpq"
  ],
  "settings": {
    "revenueManagementSettings": {
      "enableCoreCPQ": true
    }
  }
}
```

Write file?

Write only if they accept this preview unchanged. A first generate that says
write or skip preview still uses this card. Write + change → preview
again, do not apply. After they accept: apply, show the **final written JSON**
in chat.

Pass the user's product or cloud words in the features array as-is.

## Shape + features variant

User supplied sourceOrg (or snapshot id/name).

- sourceOrg: 00D000000000001AAA
- Features: Communities, API
- Settings: communitiesSettings.enableNetworksEnabled = true
- Output path (after confirm): config/project-scratch-def.json

**Required in chat:** fenced JSON of preview `document` (sourceOrg + features +
enriched settings).

Write file?
