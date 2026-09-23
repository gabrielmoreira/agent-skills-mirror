Lightning Out 2.0 is **not** a simple library upgrade. It is an entirely different embedding paradigm built on Web Components and iframes. This reference captures the essential architecture, constraints, and mental model.

---

### 1. Foundational Mental Model

#### Core Principle: Dual-Context Architecture

LO 2.0 creates a **two-world system** on every host page:

| Context                | Runs on                                  | Contains                                                                              | Controlled by      |
| ---------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------- | ------------------ |
| **Host page context**  | The external (non-Salesforce) page       | LO 2.0 web components (shells), the `lightning-out-application` element, host page JS | The developer      |
| **Salesforce context** | Inside iframes within closed shadow DOMs | The actual LWC components, Salesforce platform services (LDS, Apex, etc.)             | Salesforce runtime |

**Why this matters for migration**: In Lightning Out Beta, the LWC ran directly on the host page via `$Lightning.createComponent()`. In LO 2.0, the LWC is isolated inside an iframe. This means:

- Host page JavaScript **cannot** directly access DOM inside the LWC.
- The LWC **cannot** directly access host page DOM.
- Communication must go through the event bridge (see Section 5).
- CSS from the host page does **not** cascade into the iframe (see Section 4).

#### The Three Pillars of a LO 2.0 App

Every LO 2.0 app on a host page consists of exactly three elements:

1. **The LO 2.0 JavaScript library** — A `<script>` tag that loads the LO 2.0 runtime, which registers the custom elements.
2. **The `<lightning-out-application>` element** — A non-visual web component that holds the app configuration (auth, optional app ID, component list). There should be **exactly one** per app.
3. **One or more LO 2.0 web component shells** — Elements like `<c-my-component>` that mirror the embedded LWC components. Each shell contains an iframe with a closed shadow DOM root.

```text
Host Page
├── <script src="...lightning.out.latest/index.iife.prod.js">
├── <lightning-out-application app-id="..." frontdoor-url="..." components="c-my-comp">
└── <c-my-comp style="--custom-color: blue;">
    └── #shadow-root (closed)
        └── <iframe>
            └── <html> (Salesforce context)
                └── <body>
                    └── <c-my-comp style="--custom-color: blue;">  ← actual LWC
```

---

### 2. Initialization Lifecycle (Exact Sequence)

Understanding the initialization order is critical for writing correct mount and readiness code.

#### Step-by-Step Flow

1. **End user opens host page** — The host page HTML loads.
2. **LO 2.0 library script loads** (async) — Registers `lightning-out-application` and other custom elements with the browser's `customElements` registry.
3. **Host page obtains a frontdoor URL** — Via the UI Bridge API, exchanging a Salesforce access token or Session ID. If the user is not authenticated, an OAuth flow (PKCE) is triggered first.
4. **Host page sets `frontdoor-url`** on `<lightning-out-application>` — This is done programmatically at runtime. The element must already have `components` set (and optionally `app-id`, if the app requires it).
5. **LO 2.0 establishes a session** using the frontdoor URL — The `lightning-out-application` element initiates a Salesforce session.
6. **`lo.application.ready` fires** — Indicates the Salesforce session was established successfully.
7. **LO 2.0 web component shells initialize** — Each shell creates an iframe that becomes the root of a closed shadow DOM.
8. **Inside the iframes, the actual LWC components initialize** — They run in the Salesforce context with full platform access.
9. **`lo.component.ready` fires** — Indicates the component rendered successfully inside its iframe.

#### Error Events

- **`lo.application.error`** — Session establishment failed. Has `detail.message` and `detail.originalError`.
- **`lo.component.error`** — Component render failed or runtime error in the LWC. Same detail structure.

#### Key Timing Implications

- The LO 2.0 library loads **asynchronously**. The `lightning-out-application` custom element may not be registered when your script runs. You **must** poll `customElements.get('lightning-out-application')` before creating/appending the element.
- The `frontdoor-url` attribute **must** be set dynamically at runtime. It cannot be hardcoded in HTML (the URL is session-specific and short-lived).
- Component readiness can be detected via `customElements.whenDefined('c-my-component')` — but the argument **must be a string literal**, not a variable (browsers resolve this at parse time in some implementations, and LO 2.0's internal custom element registration relies on the literal name).

---

### 3. Authentication Model

#### Beta vs. 2.0 Authentication

| Aspect           | Lightning Out Beta                                   | Lightning Out 2.0                                              |
| ---------------- | ---------------------------------------------------- | -------------------------------------------------------------- |
| Auth mechanism   | Hardcoded session token passed to `$Lightning.use()` | OAuth 2.0 PKCE flow → frontdoor URL                            |
| Token location   | In JavaScript source (insecure)                      | Never exposed in source; exchanged via UI Bridge API           |
| Session init     | `$Lightning.use(app, callback, endpoint, token)`     | Set `frontdoor-url` attribute on `<lightning-out-application>` |
| User requirement | Authenticated Salesforce user                        | Authenticated Salesforce user (unauthenticated not supported)  |

#### OAuth 2.0 PKCE Flow in LO 2.0

The typical flow involves:

1. Store OAuth config in `localStorage` (`orgMyDomainURL`, `loAppID`, `loECAKey`, `lo2_returnTo`).
2. Redirect user to OAuth callback page (e.g., `/frontdoor-url.html`).
3. Callback page completes PKCE, obtains frontdoor URL.
4. Callback page communicates the frontdoor URL back to the host page via **three redundant channels**:
   - `window.postMessage()` — For same-window communication.
   - `BroadcastChannel('lo2auth')` — For same-origin, cross-tab communication.
   - `localStorage` event (`lo2_frontdoor_result`) — Fallback for cross-tab communication.

#### Why Three Channels?

Browser support and tab lifecycle vary. `postMessage` works when the callback is in the same tab. `BroadcastChannel` works cross-tab but isn't supported everywhere. The `storage` event is the most broadly supported cross-tab mechanism. Listening on all three ensures reliable auth completion.

#### Constraint: No Client Credentials Flow

LO 2.0 does not support OAuth 2.0 client credentials flow because that flow lacks user context. Every LO 2.0 session requires an authenticated Salesforce user identity.

---

### 4. Styling System — What Crosses the iframe Boundary

#### The Fundamental Rule

**Only CSS custom properties (variables with `--` prefix) cross from the host page into the iframe.** Standard CSS properties like `font-size`, `background-color`, `font-family` are **blocked** at the iframe boundary.

#### What Works

- SLDS 1 styling hooks: `--slds-c-card-color-background`, `--slds-c-card-text-color`, etc.
- SLDS 2 global styling hooks: `--slds-g-color-brand-base-30`, `--slds-g-font-scale-3`, etc.
- Custom CSS properties: `--custom-color`, `--my-app-spacing`, etc.
- CSS custom property values with `var()` fallbacks: `var(--slds-g-color-brand-base-30, #022ac0)`.

#### What Does NOT Work

- Direct CSS properties: `font-family: cursive` — **will be ignored**.
- Direct CSS properties: `font-size: 120%` — **will be ignored**.
- Any standard CSS property that is not a custom property (no `--` prefix).

#### How to Style LO 2.0 Components

1. **In the LWC's CSS file**, declare CSS custom properties on `:host` and reference them in rules:
   ```css
   :host {
     --custom-color: #b50be3;
   }
   h1 {
     color: var(--custom-color);
   }
   ```
2. **On the host page**, override the custom properties via the `style` attribute:
   ```html
   <c-my-comp style="--custom-color: #8c23a8;"></c-my-comp>
   ```
3. Properties can also be set via JSON in the Lightning Out 2.0 App Manager or programmatically via `setAttribute('style', ...)`.

#### Supported Standard Attributes

These standard HTML attributes **are** passed through to the LWC:
`autocapitalize`, `autocorrect`, `dir`, `enterkeyhint`, `inputmode`, `lang`, `spellcheck`, `title`, `translate`.

#### Supported ARIA Attributes

`aria-disabled`, `aria-hidden`, `aria-label`, `aria-live`, `aria-modal`, `aria-pressed`, `aria-valuemax`, `aria-valuemin`, `aria-valuenow`.

#### Blocked Standard Attributes

These are **NOT** passed through:
`accesskey`, `autofocus`, `draggable`, `exportparts`, `hidden`, `inert`, `nonce`, `part`, `slot`, `tabindex`.

#### Blocked ARIA Attributes (Reference-Based)

These ARIA attributes that reference other elements by ID are blocked because IDs don't cross iframe boundaries:
`aria-activedescendant`, `aria-controls`, `aria-describedby`, `aria-details`, `aria-errormessage`, `aria-flowto`, `aria-labelledby`, `aria-owns`.

#### Custom Attributes

All custom `@api` properties exposed on the LWC are supported as HTML attributes on the LO 2.0 shell — **unless the attribute name starts with an underscore** (`_`). Attributes are passed in kebab-case (e.g., LWC property `cardBody` → HTML attribute `card-body`).

Passing an unsupported attribute silently does nothing — no compilation or runtime error is raised.

---

### 5. Event System — Cross-iframe Communication

#### How It Works Internally

LO 2.0 uses `window.postMessage()` under the hood to bridge events across the iframe boundary. However, from the developer's perspective, the standard `EventTarget` and `CustomEvent` APIs are used directly.

#### Event Mirroring

The LO 2.0 web component shell on the host page **mirrors** the embedded LWC component in the iframe. This mirroring extends to events:

- **Adding a listener** on the shell also adds it on the LWC inside the iframe.
- **Dispatching an event** on the shell also dispatches it on the LWC inside the iframe.
- Events dispatched **inside the LWC** bubble up to the shell on the host page.
- Events dispatched **on the shell** propagate down to the LWC inside the iframe.

#### Required Event Configuration

Custom events that need to cross the iframe boundary **must** set:

```javascript
new CustomEvent('myEvent', {
  detail: {
    /* payload */
  },
  bubbles: true, // Required: to cross shadow DOM boundary
  composed: true, // Required: to cross shadow DOM boundary
});
```

Without `bubbles: true` and `composed: true`, the event will not pass through the closed shadow DOM.

#### Host Page → LWC Communication

```javascript
// On the host page:
const loComponent = document.querySelector('c-my-component');
loComponent.dispatchEvent(
  new CustomEvent('sendMessageToLWC', {
    detail: { message: 'Hello from host' },
    bubbles: true,
    composed: true,
  }),
);
```

```javascript
// In the LWC (connectedCallback):
this.addEventListener('sendMessageToLWC', this.handleMessage);
```

#### LWC → Host Page Communication

```javascript
// In the LWC:
this.dispatchEvent(
  new CustomEvent('lwcMessageToHost', {
    detail: { message: 'Hello from LWC' },
    bubbles: true,
    composed: true,
  }),
);
```

```javascript
// On the host page:
const loComponent = document.querySelector('c-my-component');
loComponent.addEventListener('lwcMessageToHost', (event) => {
  console.log(event.detail.message);
});
```

#### Timing Consideration

Set event listeners on the LO 2.0 shell component **after** the application and component have loaded. For example, conditionally set listeners after the `frontdoor-url` attribute is set or after `lo.component.ready` fires.

---

### 6. Hard Constraints & Limitations

These are non-negotiable platform boundaries. No workaround exists for these limitations.

#### Component Constraints

- **Only custom LWC components** can be embedded. Standard LWC components (`lightning-button`, `lightning-card`, etc.) must be **wrapped** inside a custom LWC. Even when wrapped, they may not be fully styled or behave as documented.
- **No Aura components** — Neither custom nor standard Aura components are supported. This includes Aura apps — the `c:OrgFarmOut` Aura app pattern from Beta is replaced by the `app-id` attribute.
- **No `lightning/navigation`** — Page navigation within embedded components is not supported.

#### Security & Cookie Constraints

- **Third-party cookies required** — End users must have third-party (cross-origin) cookies enabled in their browser. Cross-domain Salesforce session cookies must also be enabled in the org.
- **No LO 2.0 library loading from LWC** — Lightning Web Security (LWS) blocks insertion of `<script>` elements. The library must be loaded from the host page directly.

#### Authentication Constraints

- **Authenticated users only** — Unauthenticated access is not supported.
- **No client credentials flow** — Requires user context (PKCE or session-based).

#### Style Constraints (Summary)

- Only CSS custom properties (`--` prefix) cross the iframe boundary.
- Standard CSS properties set on the shell are NOT applied inside the iframe.
- Blocked attributes (see Section 4) silently fail — no error raised.

---

### 7. Component Naming Conventions

#### Conversion from Aura to LO 2.0

Aura components use the `namespace:componentName` format. LO 2.0 uses kebab-case web component format.

**Algorithm:**

1. Remove `c:` prefix.
2. Insert hyphen before each uppercase letter.
3. Convert entire string to lowercase.
4. Add `c-` prefix.

**Examples:**
| Aura Format | LO 2.0 Kebab-Case |
|---|---|
| `c:myComponent` | `c-my-component` |
| `c:loBetaEntryForm` | `c-lo-beta-entry-form` |
| `c:userDashboard` | `c-user-dashboard` |

**Mixed-case namespaces** use underscores to separate namespace parts:
| Namespace/Component | LO 2.0 Format |
|---|---|
| `complexNs/lwcComponent` | `complex_ns-lwc-component` |

#### Attribute Name Conversion

LWC `@api` properties in camelCase become kebab-case HTML attributes:
| LWC Property | HTML Attribute |
|---|---|
| `contactId` | `contact-id` |
| `recordId` | `record-id` |
| `isActive` | `is-active` |

---

### 8. Domain Transformation Rules

The Salesforce domain format changes between Beta and 2.0:

| Component      | Beta                                            | 2.0                                                  |
| -------------- | ----------------------------------------------- | ---------------------------------------------------- |
| Domain suffix  | `.lightning.force.com`                          | `.my.salesforce.com`                                 |
| Full pattern   | `https://[subdomain].lightning.[pod].force.com` | `https://[subdomain].my.[pod].salesforce.com`        |
| Library path   | `/lightning/lightning.out.js`                   | `/lightning/lightning.out.latest/index.iife.prod.js` |
| Script loading | `<script src="...">`                            | `<script async src="...">` (note: `async` attribute) |

**Example transformation:**

```text
Beta:   https://orgfarm-5b43fe90c6.test1.lightning.pc-rnd.force.com
LO 2.0: https://orgfarm-5b43fe90c6.test1.my.pc-rnd.salesforce.com
```

---

### 9. Configuration Methods for Component Properties

LO 2.0 supports three ways to set component properties:

#### A. Declarative (HTML)

Set attributes directly on the LO 2.0 web component shell in the host page HTML:

```html
<c-my-comp style="--slds-c-card-color-background: var(--secondary-color);" card-body="Custom text"></c-my-comp>
```

#### B. Programmatic (JavaScript)

Use DOM API methods to create and configure the component:

```javascript
const comp = document.createElement('c-my-comp');
comp.setAttribute('style', '--custom-color: blue;');
comp.setAttribute('card-body', 'Custom text');
document.body.appendChild(comp);
```

#### C. App Manager (Setup UI)

In the Lightning Out 2.0 App Manager, properties are set as a JSON object on each component:

```json
{
  "style": "--slds-c-card-color-background: #ccc; --custom-color: blue;",
  "card-body": "Custom text"
}
```

All three methods produce the same result: attributes on the LO 2.0 shell are mirrored to the LWC inside the iframe.

---

### 10. Critical Patterns for Correct Migration Code

These patterns are derived from real migration failures and represent hard requirements for a working LO 2.0 host page.

#### Pattern 1: The `boot()` Wrapper

All initialization logic MUST be wrapped in a single `boot()` function called at the end of the script. Do NOT split initialization into separate functions like `initializeOAuth()` and `setupCallbackListeners()`.

**Why**: Consolidating init in `boot()` ensures a single error boundary, predictable execution order, and a clear entry point. Splitting it risks partial initialization on error.

#### Pattern 2: `customElements.whenDefined()` Requires a String Literal

```javascript
// WRONG — will silently fail or behave unpredictably
const components = "c-my-component";
customElements.whenDefined(components).then(() => { ... });

// CORRECT — use the literal string directly
customElements.whenDefined('c-my-component').then(() => { ... });
```

**Why**: The browser's custom elements API and LO 2.0's internal registration can behave differently when a variable is passed vs. a literal. Always use the literal.

#### Pattern 3: `mountLo20()` Must Accept Two Parameters

```javascript
function mountLo20(frontdoorUrl, orgUrl) { ... }
```

**Why**: All three OAuth callback channels (`postMessage`, `BroadcastChannel`, `storage`) may pass both `frontdoorUrl` and `orgUrl`. Even if `orgUrl` is unused, the function signature must match what callers pass.

#### Pattern 4: Always `clearCachedResult()` Before Mounting

```javascript
clearCachedResult();
mountLo20(data.frontdoorUrl, data.orgUrl);
```

**Why**: Stale cache entries can cause duplicate mounts or auth loops. Clear before every mount call.

#### Pattern 5: Validate Data in Every Listener

Every OAuth callback listener must check three conditions:

```javascript
if (!data) return;                    // No data at all
if (data.error) return showError(...); // Auth error
if (!data.frontdoorUrl) return;       // Incomplete data
```

#### Pattern 6: No Inline `display: none` on Component Tags

```html
<!-- WRONG -->
<c-my-component style="display: none"></c-my-component>

<!-- CORRECT -->
<c-my-component></c-my-component>
```

**Why**: LO 2.0 initializes the component shell and its iframe. Adding `display: none` directly on the component tag can interfere with this initialization. Instead, control visibility through a separate loading element.

#### Pattern 7: Wrap `BroadcastChannel` in try-catch

```javascript
try {
  const bc = new BroadcastChannel('lo2auth');
  bc.onmessage = (evt) => { ... };
} catch (e) {
  // Not supported in all browsers
}
```

#### Pattern 8: Poll for Custom Element Registration

The LO 2.0 library loads asynchronously. Before creating `lightning-out-application`, you must poll:

```javascript
function tryMount() {
  if (!customElements?.get?.('lightning-out-application')) return false;
  // ... create and append the element
  return true;
}

const start = Date.now();
(function tick() {
  if (tryMount()) return;
  if (Date.now() - start > 15000) {
    showError('Timeout');
    return;
  }
  setTimeout(tick, 50);
})();
```

---

### 11. What Changes During Migration (Summary)

| Aspect              | Lightning Out Beta                                         | Lightning Out 2.0                                                      |
| ------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------- |
| Library URL         | `.lightning.force.com/lightning/lightning.out.js`          | `.my.salesforce.com/lightning/lightning.out.latest/index.iife.prod.js` |
| Script loading      | Synchronous                                                | Asynchronous (`async` attribute)                                       |
| App reference       | Aura app name (`c:OrgFarmOut`)                             | Optional 18-character App ID from Setup                                |
| Component naming    | Aura format (`c:myComponent`)                              | Kebab-case (`c-my-component`)                                          |
| Component init      | `$Lightning.createComponent(name, attrs, domId, callback)` | Declarative HTML tag + `<lightning-out-application>`                   |
| Attributes          | JavaScript object passed to `createComponent`              | HTML attributes in kebab-case on the component tag                     |
| Readiness           | Callback parameter in `createComponent`                    | `customElements.whenDefined('c-my-component')`                         |
| Auth                | Hardcoded token in `$Lightning.use()`                      | OAuth PKCE → frontdoor URL set at runtime                              |
| Component isolation | Runs directly on host page                                 | Runs inside iframe within closed shadow DOM                            |
| DOM access          | Host JS can access component DOM                           | Host JS **cannot** access component DOM                                |
| CSS inheritance     | Host page CSS cascades to component                        | **Only** CSS custom properties cross the boundary                      |
| Event communication | Direct DOM events                                          | Mirrored events bridged via `postMessage` internally                   |

---

### 12. What to Preserve During Migration

When migrating a host page, the following elements from the original page **must be preserved**:

1. **HTML structure** — Layout, hierarchy, and element order. Don't restructure.
2. **Existing CSS and classes** — All host page styling remains unchanged.
3. **Loading indicators** — Hook into existing UI elements; don't create new ones.
4. **Error display mechanisms** — Use the page's existing error handling.
5. **Event handlers on non-LO elements** — Any click handlers, form logic, etc.
6. **Business logic from Beta callbacks** — Move callback logic from `$Lightning.createComponent`'s callback to `customElements.whenDefined().then()`.
7. **Element IDs and selectors** — Use the page's actual IDs, not template defaults.
