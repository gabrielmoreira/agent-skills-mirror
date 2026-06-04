# GUI Module — AI Instructions

**Scope**: Authoritative for all files in the `gui/` module and subdirectories
**Last Updated**: 2026-06-02

> When working in `gui/` or its subdirectories, this file is more authoritative than the workspace root `.ai/instruct.md`.
> See `.github/copilot-instructions.md` for the depth-priority hierarchy.

---

## Contents

| Section | What's here |
|---|-------------|
| [Module Overview](#module-overview) | Purpose and scope of the GUI module |
| [Code Generation Rules](#code-generation-rules) | Mandatory procedures for UI component creation |
| [Element Naming Convention](#element-naming-convention) | 2-letter prefix system for test discovery |
| [Integration with Central Controller](#integration-with-central-controller) | How to use `validation/gui_element_id.py` |
| [Validation & Discovery](#validation--discovery) | Automated testing pipeline for elements |
| [Common Patterns](#common-patterns) | Example implementations across frameworks |

---

## Module Overview

This module contains all user interface components, layouts, and UI-related logic.

**Purpose**: Build interactive, testable, discoverable UI components following metadata-driven conventions.

**Key principle**: Every interactive element gets a 2-letter prefix + snake_case ID that enables:
- Automated discovery of all UI elements in the codebase
- Routing to appropriate test strategies (existence, accessibility, functional, visual)
- Grep-based element search and analysis
- Generated test reports grouped by element type

---

## Code Generation Rules

### When Writing Any UI Component

**Use the governed tool**: `.ai/agents/tools/generate-gui-component.json`

**Order of operations** (mandatory):

1. **Determine element type** — button, input, toggle, modal, card, table, notification, badge, etc. Consult `.ai/coding-prefixes.md` for complete registry.

2. **Generate element ID** — use the central controller to enforce naming rules:
   ```bash
   python validation/gui_element_id.py --type button --name "Submit Form"
   # Output: bu_submit_form
   ```

3. **Check for conflicts** — ensure the ID is unique:
   ```bash
   python validation/gui_element_id.py --find-conflicts --name "Submit Form"
   ```

4. **Write the component** — use the generated ID as the element's `id` attribute (or data-testid in React/Vue)

5. **Scan to validate** — after component is written, update the discovery registry:
   ```bash
   python validation/discovery.py --scan-root ./gui --output gui-elements.json
   ```

6. **Run tests** — verify the new element is discoverable:
   ```bash
   python validation/test_facility.py --registry gui-elements.json
   ```

---

## Element Naming Convention

### Pattern: `{prefix}_{name_in_snake_case}`

**Examples:**
- Button submit form → `bu_submit_form`
- Email input field → `in_email_address`
- Dark mode toggle → `tg_darkmode`
- Delete confirmation modal → `md_delete_confirm`
- User profile card → `cr_user_profile`
- Data table (users) → `tb_users`
- Error notification → `nd_error_message`

### 2-Letter Prefix Registry

→ **[Master Registry](../../.ai/coding-prefixes.md)** — complete list of 30+ element types

Quick reference:
| Prefix | Element Type | Example |
|--------|--------------|---------|
| `bu_` | Button | `bu_submit` |
| `in_` | Input field | `in_password` |
| `tg_` | Toggle / Checkbox | `tg_notifications` |
| `md_` | Modal / Dialog | `md_confirm_action` |
| `cr_` | Card | `cr_product_item` |
| `tb_` | Table | `tb_user_list` |
| `nd_` | Notification | `nd_success_message` |
| `sg_` | Segment / Tab | `sg_settings_tab` |

---

## Integration with Central Controller

### The Generator CLI

```bash
# Generate element ID
python validation/gui_element_id.py --type <TYPE> --name <NAME> [--verbose]

# List all known types
python validation/gui_element_id.py --list-types

# Validate an existing ID
python validation/gui_element_id.py --validate <ID>

# Find conflicts (check if name/ID already exists)
python validation/gui_element_id.py --find-conflicts --name <NAME>
```

### Why Use the Central Controller?

- **Prevents mistakes** — enforces naming rules at creation time, not post-hoc
- **Consistent normalization** — camelCase, PascalCase, and other formats are automatically converted to snake_case
- **Conflict detection** — catches duplicate IDs before they cause issues
- **Searchability** — enables grep-based discovery of all button elements, all inputs, etc.

---

## Validation & Discovery

### Discovery Phase

Scan the GUI module to find all prefixed elements:

```bash
python validation/discovery.py --scan-root ./gui --output gui-elements.json
```

**Output**: JSON file with timestamps, element locations, types, and context

### Testing Phase

Apply test strategies to discovered elements:

```bash
# Existence checks (verify all elements are found)
python validation/test_facility.py --registry gui-elements.json

# All test strategies (existence + accessibility + functional stubs)
python validation/test_facility.py --registry gui-elements.json --all --output test-results.json
```

**Supported test strategies**:
- ✅ **Existence** — element ID recognized, location found, no duplicates
- 📋 **Accessibility** — ARIA labels, roles, screen reader support (framework-specific stubs)
- 📋 **Functional** — user interactions, state changes (framework-specific stubs)
- 📋 **Visual** — appearance, responsive behavior (framework-specific stubs)

---

## Common Patterns

### React / Vue.js

```jsx
// Button with prefixed ID
<button id="bu_submit_form" onClick={handleSubmit}>
  Submit
</button>

// Input field with prefix
<input
  id="in_email_address"
  type="email"
  placeholder="Email"
  onChange={handleChange}
/>

// Toggle/Checkbox
<input
  id="tg_darkmode"
  type="checkbox"
  checked={isDarkMode}
  onChange={toggleDarkMode}
/>

// Modal
<div id="md_delete_confirm" className="modal">
  <p>Confirm deletion?</p>
  <button id="bu_delete_yes">Yes</button>
  <button id="bu_delete_no">No</button>
</div>

// Card
<div id="cr_product_item" className="card">
  <h3>Product Name</h3>
  <p>Description</p>
</div>

// Table
<table id="tb_users">
  <thead>
    <tr>
      <th>Name</th>
      <th>Email</th>
    </tr>
  </thead>
</table>
```

### Angular

```typescript
// Component with prefixed elements
@Component({
  selector: 'app-user-form',
  template: `
    <form (submit)="onSubmit()">
      <input
        id="in_email_address"
        [(ngModel)]="email"
        name="email"
        type="email"
      />
      <button id="bu_submit_form" type="submit">
        Submit
      </button>
    </form>
  `
})
export class UserFormComponent {
  email: string;

  onSubmit() {
    // Form submission logic
  }
}
```

### HTML/CSS

```html
<!-- Prefixed IDs for all interactive elements -->
<button id="bu_subscribe">Subscribe</button>

<input id="in_search_query" type="text" placeholder="Search...">

<div id="md_help_dialog">
  <h2>Help</h2>
  <p>This is help content</p>
  <button id="bu_close_help">Close</button>
</div>

<div id="cr_featured_item">
  <img src="product.jpg" alt="Featured">
  <h3>Featured Product</h3>
</div>

<table id="tb_transactions">
  <!-- Table content -->
</table>
```

---

## Hierarchical Overrides

This module uses the workspace-level element prefix registry from `.ai/coding-prefixes.md`.

**Module-level extension** (if needed):
- Create `gui/.ai/coding-prefixes.md` to add or override prefixes specific to the GUI module
- Example: Add `gg_` for "gallery" component, `sp_` for "spinner"
- Module-level prefixes take precedence over workspace level in this module only

---

## Related Documentation

- [Element Naming Prefixes Registry](../../.ai/coding-prefixes.md) — complete prefix table
- [GUI Element ID Generator Guide](../../validation/gui-element-id-guide.md) — detailed tool usage
- [Validation System Documentation](../../validation/README.md) — testing pipeline overview
- [Governed Tool: generate-gui-component](../../.ai/agents/tools/generate-gui-component.json) — checklist and order of operations
