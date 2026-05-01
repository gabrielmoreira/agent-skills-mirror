---
type: skill
lifecycle: stable
inheritance: inheritable
name: data-driven-layouts
description: Template-driven layouts require code changes for structural updates:
tier: standard
applyTo: '**/*data*,**/*driven*,**/*layouts*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Data-Driven Layouts

## The Problem

Template-driven layouts require code changes for structural updates:

```javascript
// Bad: structure embedded in code
function renderDashboard() {
  return `
    <div class="section">
      <h2>Users</h2>
      ${renderUserTable()}
    </div>
    <div class="section">
      <h2>Revenue</h2>
      ${renderRevenueChart()}
    </div>
  `;
}
// Adding a new section = code change
```

## The Solution

Define layout structure as data. Rendering is generic.

```javascript
// layouts/dashboard.json
{
  "sections": [
    { "id": "users", "title": "Users", "component": "userTable" },
    { "id": "revenue", "title": "Revenue", "component": "revenueChart" },
    { "id": "alerts", "title": "Alerts", "component": "alertList" }
  ]
}
```

```javascript
// Generic renderer
const components = {
  userTable: () => renderUserTable(),
  revenueChart: () => renderRevenueChart(),
  alertList: () => renderAlertList()
};

function renderDashboard(layout) {
  return layout.sections.map(section => `
    <div class="section" id="${section.id}">
      <h2>${section.title}</h2>
      ${components[section.component]()}
    </div>
  `).join('');
}

// Usage
const layout = require('./layouts/dashboard.json');
const html = renderDashboard(layout);
```

## Benefits

- Add sections by editing JSON, not code
- Reorder by changing array order
- Non-developers can modify layouts
- Easier to A/B test different layouts

## Schema Example

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "title", "component"],
        "properties": {
          "id": { "type": "string" },
          "title": { "type": "string" },
          "component": { "type": "string" },
          "props": { "type": "object" }
        }
      }
    }
  }
}
```

## Verification

1. Adding a section = only JSON change
2. Unknown component throws clear error
3. Layout validates against schema

## When to Apply

- Dashboards
- Forms
- Navigation menus
- Any UI with variable structure

## Tags

`build` `architecture` `layouts` `configuration`
