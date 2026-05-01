---
name: odoo-17-owl
description: Complete reference for Odoo 17 OWL (Owl Web Library) 2.x components, hooks, services, registries, and patterns for building interactive JavaScript UI.
globs: "**/static/src/**/*.{js,xml,scss}"
topics:
  - OWL basics (Component, setup, template, props, state)
  - OWL hooks (useState, useRef, useEffect, useService, useSubEnv, onMounted, onWillStart, onWillUnmount)
  - Odoo services (rpc, orm, notification, dialog, action, user, router, ui)
  - QWeb templates and directives
  - Registries (category, add, get, contains, fields, views, services, main_components)
  - Patching existing classes and services
  - Assets and module structure
when_to_use:
  - Creating custom UI components
  - Writing field widgets or view renderers
  - Implementing client actions
  - Extending or patching existing components
  - Calling backend from the frontend
---

# Odoo 17 OWL Guide

Complete reference for Odoo 17 OWL (Owl Web Library) 2.x components, hooks, services, and patterns.

Odoo 17 ships with **OWL 2.8.2** (`addons/web/static/lib/owl/owl.js`). The component syntax is class-based with a `setup()` method and `static template`.

## Table of Contents

1. [OWL Basics](#owl-basics)
2. [Component Lifecycle](#component-lifecycle)
3. [OWL Hooks](#owl-hooks)
4. [Services (Odoo 17 specifics)](#services-odoo-17-specifics)
5. [QWeb Templates](#qweb-templates)
6. [Registries](#registries)
7. [Patching](#patching)
8. [Assets and File Layout](#assets-and-file-layout)
9. [Common Patterns](#common-patterns)
10. [Best Practices](#best-practices)
11. [Complete Example](#complete-example)

---

## OWL Basics

### Importing from @odoo/owl

```javascript
/** @odoo-module **/
import {
    Component,
    xml,
    useState,
    useRef,
    useEffect,
    useSubEnv,
    onMounted,
    onWillStart,
    onWillUnmount,
} from "@odoo/owl";
```

All OWL primitives come from the `@odoo/owl` package. Odoo-specific hooks live in `@web/core/utils/hooks` and `@web/core/...`.

### Basic Component Structure

```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class Counter extends Component {
    static template = "my_module.Counter";
    static props = {
        initial: { type: Number, optional: true },
        onChange: { type: Function, optional: true },
    };
    static defaultProps = { initial: 0 };

    setup() {
        this.state = useState({ value: this.props.initial });
    }

    increment() {
        this.state.value++;
        this.props.onChange?.(this.state.value);
    }
}
```

### Template in a Separate XML File (Recommended)

`my_module/static/src/counter/counter.js`:

```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class Counter extends Component {
    static template = "my_module.Counter";
    static props = { initial: { type: Number, optional: true } };

    setup() {
        this.state = useState({ value: this.props.initial || 0 });
    }

    increment() {
        this.state.value++;
    }
}
```

`my_module/static/src/counter/counter.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.Counter">
        <div class="counter">
            <button class="btn btn-primary" t-on-click="increment">
                Count: <t t-esc="state.value"/>
            </button>
        </div>
    </t>
</templates>
```

Convention: template names are `addon_name.ComponentName`. Put the XML file alongside the component.

### Inline Template with `xml` (Small Components)

```javascript
import { Component, xml, useState } from "@odoo/owl";

export class Tiny extends Component {
    static template = xml`
        <div t-on-click="onClick">
            <t t-esc="state.label"/>
        </div>
    `;

    setup() {
        this.state = useState({ label: "Click me" });
    }

    onClick() {
        this.state.label = "Clicked!";
    }
}
```

Prefer external XML files for anything non-trivial — you get proper indentation and `web-editor` support for translatable strings.

---

## Component Lifecycle

### Hooks Fired in Order

```javascript
import {
    onWillStart,
    onWillRender,
    onRendered,
    onMounted,
    onWillUpdateProps,
    onWillPatch,
    onPatched,
    onWillUnmount,
    onWillDestroy,
} from "@odoo/owl";

setup() {
    onWillStart(async () => {
        // Async setup before first render. Good for loading data.
        this.records = await this.orm.searchRead("res.partner", [], ["name"]);
    });
    onMounted(() => {
        // DOM is live. Safe to integrate third-party libs.
    });
    onWillUpdateProps((nextProps) => { /* before props change */ });
    onWillPatch(() => { /* before DOM patch */ });
    onPatched(() => { /* after DOM patch */ });
    onWillUnmount(() => {
        // Tear down listeners / timers.
    });
    onWillDestroy(() => { /* final cleanup */ });
}
```

### Always Use `setup()`, Never `constructor`

```javascript
// CORRECT
class Good extends Component {
    setup() {
        this.state = useState({ n: 0 });
    }
}

// WRONG
class Bad extends Component {
    constructor(parent, props) {
        super(parent, props);
        this.state = useState({ n: 0 });  // Breaks in subclasses and patches.
    }
}
```

`setup()` is overridable; `constructor` is not. The whole Odoo extension ecosystem relies on overriding `setup()`.

---

## OWL Hooks

### useState — Reactive State

```javascript
import { useState } from "@odoo/owl";

setup() {
    this.state = useState({
        count: 0,
        user: { name: "Alice", email: "a@x.com" },
        tags: ["a", "b"],
    });
}

// Any assignment in reactive paths triggers a re-render:
this.state.count++;
this.state.user.name = "Bob";
this.state.tags.push("c");
```

### useRef — DOM References

```javascript
import { useRef, onMounted } from "@odoo/owl";

setup() {
    this.input = useRef("input");
    onMounted(() => this.input.el?.focus());
}
```

```xml
<input t-ref="input" type="text"/>
```

Access `this.input.el` — it is `null` before mount and after unmount.

### useEffect — Side Effects

```javascript
import { useEffect } from "@odoo/owl";

setup() {
    this.state = useState({ query: "" });

    // Runs whenever state.query changes
    useEffect(
        (query) => {
            this.search(query);
            return () => this.cancelSearch();  // cleanup
        },
        () => [this.state.query],
    );
}
```

### useService — Injected Odoo Services

Defined in `@web/core/utils/hooks`:

```javascript
import { useService } from "@web/core/utils/hooks";

setup() {
    this.rpc = useService("rpc");                 // Call Python / JSON-RPC URLs
    this.orm = useService("orm");                 // High-level ORM helper
    this.notification = useService("notification");
    this.dialog = useService("dialog");
    this.action = useService("action");
    this.user = useService("user");
    this.router = useService("router");
    this.ui = useService("ui");
}
```

`useService` throws if the service is not registered. The returned object/function is automatically protected: if the component is destroyed before the promise resolves, the caller doesn't receive stale results.

### useSubEnv — Scoped Environment

```javascript
import { useSubEnv } from "@odoo/owl";

setup() {
    useSubEnv({
        model: this.props.record.resModel,
        resId: this.props.record.resId,
    });
}
```

Child components can read from `this.env.model` etc. Use sparingly — prefer props.

### Odoo-Specific Hooks

From `@web/core/utils/hooks`:

- `useAutofocus({ refName, selectAll, mobile })` — autofocus a `t-ref="autofocus"` element.
- `useBus(bus, eventName, callback)` — attach/detach a bus listener with proper cleanup.
- `useSpellCheck({ refName })` — manage the `spellcheck` attribute.
- `useChildRef()` / `useForwardRefToParent(refName)` — forward a ref to a parent.
- `useOwnedDialogs()` — like `dialog` but auto-closes open dialogs on unmount.
- `useRefListener(ref, eventName, handler)` — attach an event listener to a ref.

---

## Services (Odoo 17 specifics)

### RPC Service (Odoo 17: use `useService("rpc")`)

In Odoo 17 `rpc` is still a classical OWL service obtained with `useService`. (Starting in 18 it becomes a plain import — do not use that form here.)

```javascript
import { useService } from "@web/core/utils/hooks";

setup() {
    this.rpc = useService("rpc");
}

async load() {
    // Direct controller call; params becomes the JSON-RPC `params` object.
    const result = await this.rpc("/my_module/data", { domain: [["state", "=", "open"]] });

    // call_kw is what the ORM service wraps; usually prefer this.orm instead.
    const partners = await this.rpc("/web/dataset/call_kw/res.partner/search_read", {
        model: "res.partner",
        method: "search_read",
        args: [[["is_company", "=", true]]],
        kwargs: { fields: ["name", "email"] },
    });
}
```

### ORM Service

`@web/core/orm_service.js` exposes typed helpers over `/web/dataset/call_kw/...`.

```javascript
this.orm = useService("orm");

// searchRead(model, domain, fields?, kwargs?)
const partners = await this.orm.searchRead(
    "res.partner",
    [["customer_rank", ">", 0]],
    ["name", "email", "phone"],
    { limit: 80, offset: 0 },
);

// read(model, ids, fields?, kwargs?)
const records = await this.orm.read("res.partner", [1, 2, 3], ["name"]);

// create(model, recordsList, kwargs?) — pass a LIST of dicts, returns a list of ids.
const ids = await this.orm.create("res.partner", [
    { name: "New Partner", email: "new@x.com" },
]);

// write(model, ids, values, kwargs?)
await this.orm.write("res.partner", ids, { phone: "555" });

// unlink(model, ids, kwargs?)
await this.orm.unlink("res.partner", ids);

// readGroup(model, domain, fields, groupby, kwargs?)
const groups = await this.orm.readGroup(
    "sale.order",
    [["state", "!=", "draft"]],
    ["amount_total:sum"],
    ["state"],
);

// searchCount(model, domain, kwargs?)
const count = await this.orm.searchCount("res.partner", [["customer_rank", ">", 0]]);

// call(model, method, args?, kwargs?) — arbitrary server method
const res = await this.orm.call("my.model", "action_validate", [recordIds]);

// Silent variant — no global RPC indicator
await this.orm.silent.read("res.partner", [1], ["name"]);
```

### Notification Service

In Odoo 17 the notification API is `notification.add(message, options)` (NOT `notification.notify(...)`).

```javascript
this.notification = useService("notification");

// Simple
this.notification.add("Record saved");

// With options
this.notification.add("Something failed", {
    type: "danger",       // "success" | "info" | "warning" | "danger"
    title: "Error",
    sticky: true,
    className: "o_my_notif",
    onClose: () => console.log("closed"),
    buttons: [
        { name: "Retry", primary: true, onClick: () => this.retry() },
    ],
});

// add() returns a close function
const close = this.notification.add("Working...", { sticky: true });
// later:
close();
```

### Dialog Service

```javascript
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

this.dialog = useService("dialog");

// dialog.add(Component, props, options?)
this.dialog.add(ConfirmationDialog, {
    title: _t("Delete record"),
    body: _t("Are you sure? This cannot be undone."),
    confirmLabel: _t("Delete"),
    confirm: async () => {
        await this.orm.unlink(this.props.resModel, [this.props.resId]);
    },
    cancel: () => {},
});
```

`dialog.add` returns a `close` function. The optional third argument accepts `{ onClose }`.

Custom dialog components receive a `close` prop to dismiss themselves.

### Action Service

```javascript
this.action = useService("action");

// Open an act_window
await this.action.doAction({
    type: "ir.actions.act_window",
    name: "Partners",
    res_model: "res.partner",
    views: [[false, "list"], [false, "form"]],
    domain: [["customer_rank", ">", 0]],
    target: "current",        // "current" | "new" | "fullscreen" | "inline"
});

// Open a specific form view
await this.action.doAction({
    type: "ir.actions.act_window",
    res_model: "res.partner",
    res_id: partnerId,
    views: [[false, "form"]],
    target: "new",
});

// Run a server action or report by XML-id / database id
await this.action.doAction("my_module.action_my_report", {
    additionalContext: { default_state: "draft" },
});

// Execute a view button action descriptor
await this.action.doActionButton({
    type: "object",
    name: "action_confirm",
    resModel: "sale.order",
    resId: orderId,
    resIds: [orderId],
});
```

### User Service

Read-only snapshot of the current user/company, plus a cached `user.hasGroup(...)`.

```javascript
this.user = useService("user");

this.user.userId;        // integer
this.user.name;
this.user.context;
this.user.lang;
this.user.tz;
this.user.isAdmin;
this.user.allowedCompanies;
this.user.activeCompany;

if (await this.user.hasGroup("base.group_system")) {
    // ...
}
```

### Router Service

```javascript
this.router = useService("router");

// Read current URL state
const hash = this.router.current.hash;

// Push updates to the URL hash
this.router.pushState({ view_type: "list", action: 42 }, { replace: false });
```

### UI Service

```javascript
this.ui = useService("ui");

this.ui.isSmall;                // boolean: mobile breakpoint
this.ui.size;                   // Current SIZES enum value
this.ui.activateElement(el);    // Track a new UI active element
this.ui.block();                // Block the whole UI
this.ui.unblock();
```

---

## QWeb Templates

### Directives

```xml
<!-- Render value (escaped) -->
<t t-esc="state.value"/>

<!-- Render HTML (unescaped — dangerous) -->
<t t-out="state.htmlContent"/>

<!-- Conditionals -->
<div t-if="state.isActive">Active</div>
<div t-elif="state.isPending">Pending</div>
<div t-else="">Idle</div>

<!-- Loops (always include t-key) -->
<t t-foreach="state.records" t-as="rec" t-key="rec.id">
    <div t-esc="rec.name"/>
</t>

<!-- Dynamic attributes -->
<input t-att-value="state.value"/>
<div t-att-class="state.isActive ? 'o_active' : ''"/>
<div t-att="{'data-id': rec.id, 'data-name': rec.name}"/>
<a t-attf-href="/record/{{ rec.id }}">Open</a>

<!-- Event handlers -->
<button t-on-click="onClick">Click</button>
<button t-on-click.stop="onClick">Click (stop propagation)</button>
<button t-on-click="() => this.select(item)">Inline arrow</button>
<input t-on-input="onInput"/>

<!-- Two-way binding -->
<input t-model="state.search"/>
<input type="checkbox" t-model="state.isOn"/>

<!-- Local variable -->
<t t-set="total" t-value="state.items.reduce((a, b) => a + b.qty, 0)"/>

<!-- Call another template -->
<t t-call="my_module.SubTemplate">
    <t t-set="extra" t-value="'hi'"/>
</t>

<!-- Reference to DOM element -->
<input t-ref="searchInput"/>
```

### Slots

Parent exposes slots; children fill them:

```xml
<!-- Parent template -->
<t t-name="my_module.Card">
    <div class="card">
        <div class="card-header">
            <t t-slot="header"/>
        </div>
        <div class="card-body">
            <t t-slot="default"/>
        </div>
    </div>
</t>

<!-- Usage -->
<Card>
    <t t-set-slot="header"><h3>Title</h3></t>
    <p>Body content</p>
</Card>
```

Scoped slots pass data to the slot content:

```xml
<!-- Parent -->
<t t-foreach="items" t-as="item" t-key="item.id">
    <t t-slot="item" item="item"/>
</t>

<!-- Child -->
<MyList>
    <t t-set-slot="item" t-slot-scope="scope">
        <span t-esc="scope.item.name"/>
    </t>
</MyList>
```

### Sub-Component Usage

```javascript
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class Toolbar extends Component {
    static template = "my_module.Toolbar";
    static components = { Dropdown, DropdownItem };
}
```

```xml
<t t-name="my_module.Toolbar">
    <Dropdown>
        <button class="btn btn-primary">Actions</button>
        <t t-set-slot="content">
            <DropdownItem onSelected="() => this.save()">Save</DropdownItem>
            <DropdownItem onSelected="() => this.discard()">Discard</DropdownItem>
        </t>
    </Dropdown>
</t>
```

---

## Registries

`@web/core/registry` exposes a central registry with named categories. Registering under the right category is how Odoo discovers your widget/view/service.

```javascript
import { registry } from "@web/core/registry";
```

### Common Categories

| Category | What it holds |
|----------|---------------|
| `"services"` | OWL services (rpc, orm, notification, dialog, action, …) |
| `"main_components"` | Top-level components mounted in the webclient shell |
| `"fields"` | Field widgets (used by form/list views via `widget="..."`) |
| `"views"` | View definitions (list, form, kanban, graph, …) |
| `"actions"` | Client actions (used by `ir.actions.client`) |
| `"systray"` | Systray items |
| `"user_menuitems"` | User menu entries |
| `"formatters"` / `"parsers"` | Field formatters / parsers |

### Registering a Service

```javascript
import { registry } from "@web/core/registry";

export const myService = {
    dependencies: ["rpc", "user"],
    start(env, { rpc, user }) {
        return {
            async doStuff(id) {
                return rpc("/my/endpoint", { id });
            },
        };
    },
};

registry.category("services").add("myService", myService);
```

Then `this.myService = useService("myService");` from any component.

### Registering a Field Widget

```javascript
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ColoredBadge extends Component {
    static template = "my_module.ColoredBadge";
    static props = { ...standardFieldProps };

    get value() {
        return this.props.record.data[this.props.name];
    }
}

export const coloredBadge = {
    component: ColoredBadge,
    displayName: "Colored Badge",
    supportedTypes: ["char"],
    extractProps: ({ attrs, options }) => ({
        // Map arch attrs to component props if needed
    }),
};

registry.category("fields").add("colored_badge", coloredBadge);
```

Use in a view: `<field name="state" widget="colored_badge"/>`.

### Registering a Client Action

```javascript
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

class Dashboard extends Component {
    static template = "my_module.Dashboard";
    static props = ["*"];
}

registry.category("actions").add("my_module.dashboard", Dashboard);
```

Then create an `ir.actions.client`:

```xml
<record id="action_dashboard" model="ir.actions.client">
    <field name="name">Dashboard</field>
    <field name="tag">my_module.dashboard</field>
</record>
```

### Other Registry Operations

```javascript
const cat = registry.category("fields");

cat.add("my_widget", def);             // throws if already registered
cat.add("my_widget", def, { force: true });
cat.get("my_widget");                  // throws if missing
cat.get("my_widget", defaultValue);    // safe variant
cat.contains("my_widget");             // boolean
cat.remove("my_widget");
cat.getAll();                          // array of values
cat.getEntries();                      // array of [key, value]
```

---

## Patching

`patch` lets you add or override methods on existing classes/services without rewriting them. Import from `@web/core/utils/patch`:

```javascript
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    // Override or extend a method
    async onWillSaveRecord(record) {
        // Call the original implementation via super
        const result = await super.onWillSaveRecord(record);
        if (result && record.resModel === "sale.order") {
            console.log("Saving a sale order");
        }
        return result;
    },

    // Add a new method
    myHelper() {
        return 42;
    },
});
```

Notes:

- Pass the **prototype** when patching instance methods of a class.
- Pass the **class itself** when patching static members.
- Inside the patch, `super.method(...)` calls the previous implementation — even chained across multiple patches.
- `patch(...)` returns an unpatch function; rarely needed outside tests.

Patching a service:

```javascript
import { patch } from "@web/core/utils/patch";
import { ORM } from "@web/core/orm_service";

patch(ORM.prototype, {
    async searchRead(model, domain, fields, kwargs = {}) {
        console.log("searchRead", model, domain);
        return super.searchRead(model, domain, fields, kwargs);
    },
});
```

---

## Assets and File Layout

### File Structure

```
my_module/static/src/
├── components/
│   ├── my_widget/
│   │   ├── my_widget.js
│   │   ├── my_widget.xml
│   │   └── my_widget.scss
│   └── other_thing/
│       └── ...
├── views/
│   └── my_view/
│       └── ...
└── services/
    └── my_service.js
```

### Asset Bundles in `__manifest__.py`

```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/components/**/*',
            'my_module/static/src/services/**/*',
        ],
        'web.assets_frontend': [
            'my_module/static/src/public/**/*',
        ],
        'web.assets_qweb': [
            # Legacy — prefer including .xml in assets_backend directly
        ],
    },
}
```

Common bundles in Odoo 17:

- `web.assets_backend` — back-end webclient.
- `web.assets_frontend` — website / portal frontend.
- `web.assets_common` — shared by both.
- `web.report_assets_common` — PDF reports.
- `web.assets_tests` — QUnit tests.

XML template files included in a backend bundle are automatically registered as QWeb templates.

---

## Common Patterns

### Loading Data in `onWillStart`

```javascript
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PartnerList extends Component {
    static template = "my_module.PartnerList";
    static props = { domain: { type: Array, optional: true } };
    static defaultProps = { domain: [] };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ partners: [] });

        onWillStart(async () => {
            this.state.partners = await this.orm.searchRead(
                "res.partner",
                this.props.domain,
                ["name", "email"],
                { limit: 80 },
            );
        });
    }
}
```

### Props Validation

```javascript
static props = {
    // Required
    record: Object,

    // Optional primitive
    title: { type: String, optional: true },

    // Union
    value: { type: [String, Number], optional: true },

    // Array of strings
    tags: { type: Array, element: String, optional: true },

    // Object shape
    config: {
        type: Object,
        shape: { limit: Number, offset: Number },
        optional: true,
    },

    // Function
    onSave: { type: Function, optional: true },

    // Accept anything else (slot spec etc.)
    slots: { type: Object, optional: true },
};

static defaultProps = { tags: [] };
```

Avoid `static props = ["*"]` (accept any prop) in user code — it silently hides typos.

### Using `_t` for Translations

```javascript
import { _t } from "@web/core/l10n/translation";

this.notification.add(_t("Record saved"));
this.dialog.add(ConfirmationDialog, {
    title: _t("Confirm"),
    body: _t("Are you sure?"),
});
```

`_t` is picked up by Odoo's translation export. Do NOT concatenate translated strings — use placeholders:

```javascript
_t("Hello %s", name);          // good
_t("Hello ") + name;           // bad (not translatable)
```

### Cleaning Up

```javascript
setup() {
    const timer = setInterval(() => this.tick(), 1000);
    onWillUnmount(() => clearInterval(timer));
}
```

---

## Best Practices

### DO

1. Always use `setup()` (never `constructor`).
2. Put templates in dedicated `.xml` files named `addon.ComponentName`.
3. Load async data in `onWillStart` — components don't render until it resolves.
4. Declare `static props` explicitly; avoid `["*"]`.
5. Use services (`useService`) for cross-cutting concerns rather than imports.
6. Clean up timers / bus listeners in `onWillUnmount`.
7. Use `_t` from `@web/core/l10n/translation` for every user-visible string.
8. Use `t-key` on every `t-foreach`.
9. Interact with the DOM only through `useRef` + lifecycle hooks.
10. Patch with `patch(Cls.prototype, { ... })` and call `super.method(...)`.

### DON'T

1. Don't override `constructor` — you cannot reach it from subclass `setup()`.
2. Don't import `rpc` as a plain function — in Odoo 17 it is a service (`useService("rpc")`).
3. Don't call `notification.notify(...)` — the v17 API is `notification.add(message, options)`.
4. Don't query the DOM with `document.querySelector` — use refs.
5. Don't mutate `this.props` — props are read-only.
6. Don't store persistent state in plain object properties when you want reactivity — use `useState`.
7. Don't forget to register your service/component in the right registry category.

---

## Complete Example

A client action that lists partners with search, multi-select, and bulk archive.

`my_module/static/src/client_actions/partner_panel/partner_panel.js`:

```javascript
/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class PartnerPanel extends Component {
    static template = "my_module.PartnerPanel";
    static components = { Dropdown, DropdownItem };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");

        this.state = useState({
            partners: [],
            selected: new Set(),
            search: "",
            loading: false,
        });

        onWillStart(() => this.load());
    }

    async load() {
        this.state.loading = true;
        try {
            this.state.partners = await this.orm.searchRead(
                "res.partner",
                [["active", "=", true]],
                ["name", "email", "phone"],
                { limit: 100 },
            );
        } catch (error) {
            this.notification.add(_t("Failed to load partners"), { type: "danger" });
            throw error;
        } finally {
            this.state.loading = false;
        }
    }

    get filteredPartners() {
        const q = this.state.search.toLowerCase();
        if (!q) {
            return this.state.partners;
        }
        return this.state.partners.filter((p) => p.name.toLowerCase().includes(q));
    }

    toggle(id) {
        if (this.state.selected.has(id)) {
            this.state.selected.delete(id);
        } else {
            this.state.selected.add(id);
        }
        // Trigger reactivity on Set
        this.state.selected = new Set(this.state.selected);
    }

    onSearchInput(ev) {
        this.state.search = ev.target.value;
    }

    async archiveSelected() {
        const ids = [...this.state.selected];
        if (!ids.length) {
            this.notification.add(_t("No partners selected"), { type: "warning" });
            return;
        }
        this.dialog.add(ConfirmationDialog, {
            title: _t("Archive partners"),
            body: _t("Archive %s partner(s)?", ids.length),
            confirm: async () => {
                await this.orm.write("res.partner", ids, { active: false });
                this.state.selected = new Set();
                await this.load();
                this.notification.add(_t("Partners archived"), { type: "success" });
            },
            cancel: () => {},
        });
    }
}

registry.category("actions").add("my_module.partner_panel", PartnerPanel);
```

`my_module/static/src/client_actions/partner_panel/partner_panel.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.PartnerPanel">
        <div class="o_partner_panel p-3">
            <div class="d-flex gap-2 mb-3">
                <input
                    type="text"
                    class="form-control"
                    placeholder="Search..."
                    t-att-value="state.search"
                    t-on-input="onSearchInput"
                />
                <Dropdown>
                    <button class="btn btn-primary">Actions</button>
                    <t t-set-slot="content">
                        <DropdownItem onSelected="() => this.archiveSelected()">
                            Archive selected
                        </DropdownItem>
                    </t>
                </Dropdown>
            </div>

            <div t-if="state.loading" class="text-center text-muted">
                <i class="fa fa-spinner fa-spin"/> Loading...
            </div>

            <div class="list-group" t-else="">
                <t t-foreach="filteredPartners" t-as="p" t-key="p.id">
                    <button
                        type="button"
                        class="list-group-item list-group-item-action d-flex justify-content-between"
                        t-att-class="state.selected.has(p.id) ? 'active' : ''"
                        t-on-click="() => this.toggle(p.id)"
                    >
                        <span>
                            <strong t-esc="p.name"/>
                            <small t-if="p.email" class="text-muted ms-2" t-esc="p.email"/>
                        </span>
                        <i class="fa fa-check" t-if="state.selected.has(p.id)"/>
                    </button>
                </t>
            </div>
        </div>
    </t>
</templates>
```

`my_module/__manifest__.py` excerpt:

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/client_actions/**/*',
    ],
},
```

`my_module/views/client_action.xml`:

```xml
<odoo>
    <record id="action_partner_panel" model="ir.actions.client">
        <field name="name">Partner Panel</field>
        <field name="tag">my_module.partner_panel</field>
    </record>
</odoo>
```

---

## Base Code Reference

The APIs documented here live in the Odoo 17 source:

- `addons/web/static/lib/owl/owl.js` — OWL 2.8.2 (`Component`, `useState`, `useRef`, `useEffect`, lifecycle hooks, `xml`).
- `addons/web/static/src/core/utils/hooks.js` — `useService`, `useBus`, `useAutofocus`, `useOwnedDialogs`, etc.
- `addons/web/static/src/core/registry.js` — the registry singleton and categories.
- `addons/web/static/src/core/network/rpc_service.js` — the `rpc` service.
- `addons/web/static/src/core/orm_service.js` — the `orm` service (`ORM` class API).
- `addons/web/static/src/core/notifications/notification_service.js` — `notification.add`.
- `addons/web/static/src/core/dialog/dialog_service.js` — `dialog.add`.
- `addons/web/static/src/webclient/actions/action_service.js` — `action.doAction`, `doActionButton`.
- `addons/web/static/src/core/utils/patch.js` — `patch(obj, extension)`.
- `addons/web/static/src/core/l10n/translation.js` — `_t` helper.
