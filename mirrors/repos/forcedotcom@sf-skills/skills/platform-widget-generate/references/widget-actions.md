# Widget Actions

Complete `tile/button` examples for the two supported action definitions. The action table and the action-less-button rule live in SKILL.md *Actions*.

---

## `action/sendMessage` and `action/openLink`

```json
{
  "definition": "tile/button",
  "attributes": {
    "label": "Button Label",
    "variant": "primary",
    "actions": { "click": [ { "definition": "action/sendMessage", "attributes": { "content": "content" } } ] }
  }
}
```

```json
{
   "definition": "tile/button",
   "attributes": {
      "label": "Button Label",
      "variant": "primary",
      "actions": { "click": [ { "definition": "action/openLink", "attributes": { "url": "https://www.example.com" } } ] }
   }
}
```
