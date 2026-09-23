# Lightning Out Beta → Lightning Out 2.0 Migration Guide

## Migration Approach

This guide helps you identify and transform Lightning Out Beta code to Lightning Out 2.0. **Your existing HTML structure, styling, and custom logic remain unchanged** - we only modify Lightning Out-specific patterns.

---

## Lightning Out 2.0 Documentation

Before applying the migration steps below, internalize the complete Lightning Out 2.0 architecture, lifecycle, styling, events, and constraints documentation in the companion reference:

See [lightning-out-2-system-reference.md](lightning-out-2-system-reference.md) for the complete LO 2.0 system reference.

---

## Phase 1: Identify Lightning Out Beta Patterns

**Search for these patterns in the customer's code:**

### Pattern A: Script Tag Loading Beta Library

```html
<script src="https://[DOMAIN].lightning.force.com/lightning/lightning.out.js"></script>
```

**What to extract:**

- Domain (before `.lightning.force.com`)

### Pattern B: Configuration Variables

```javascript
const [ENDPOINT_VAR] = 'https://[DOMAIN].lightning.force.com';
const [APP_VAR] = 'c:[AuraAppName]'; // Aura app name
const [COMPONENT_VAR] = 'c:[componentName]'; // Component name
const [TOKEN_VAR] = '[AUTH_TOKEN]'; // Hardcoded token
```

**What to extract:**

- Endpoint variable name and domain value
- Aura app variable name and value
- Component variable name and value (Aura format: `c:name`)
- Token variable name

### Pattern C: $Lightning.use() Call

```javascript
$Lightning.use(
  [APP_VAR], // 1st param: Aura app (could be variable or string)
  function () {
    // Callback function body
  },
  [ENDPOINT_VAR], // 3rd param: Endpoint (could be variable or string)
  [TOKEN_VAR], // 4th param: Auth token (could be variable or string)
);
```

**What to extract:**

- The entire `$Lightning.use()` block
- First parameter value (Aura app)
- Third parameter value (endpoint)
- Fourth parameter value (token)

### Pattern D: $Lightning.createComponent() Call

```javascript
$Lightning.createComponent(
  [COMPONENT_VAR],     // 1st param: Component name (could be variable or string "c:name")
  {[ATTRIBUTES]},      // 2nd param: Attributes object (could be empty {})
  "[DOM_ID]",          // 3rd param: DOM element ID as STRING
  function(cmp) {
    // Optional callback
    [CUSTOM_LOGIC]
  }
);
```

**What to extract:**

- Component name/variable
- Attributes object (if any): `{ key: "value", anotherKey: true }`
- DOM element ID (3rd parameter - this is where component renders)
- Any custom logic inside the callback

### Pattern E: DOM Target Element

```html
<[ANY_TAG] id="[DOM_ID]">[CONTENT]</[ANY_TAG]>
```

Where `[DOM_ID]` matches the 3rd parameter in `$Lightning.createComponent()`

**What to extract:**

- Element location in HTML
- Element tag name and existing attributes

---

## Phase 2: Apply Transformations

**Note**: Examples below use generic component names like "c-lo-beta-entry-form". Replace ALL occurrences with your actual component name from Phase 1.

### Transform 1: Update Script Tag

**Find Pattern A:**

```html
<script src="https://[DOMAIN].lightning.force.com/lightning/lightning.out.js"></script>
```

**Replace with:**

```html
<script async src="https://[DOMAIN].my.salesforce.com/lightning/lightning.out.latest/index.iife.prod.js"></script>
```

**Rules:**

- Change domain: `.lightning.force.com` → `.my.salesforce.com`
- Change path: `/lightning/lightning.out.js` → `/lightning/lightning.out.latest/index.iife.prod.js`
- Add `async` attribute

### Transform 2: Convert Component Name

**From Pattern B or D, extract the component name:**

- If variable: `const component = "c:myComponent"` → extract `"c:myComponent"`
- If inline: `$Lightning.createComponent("c:myComponent", ...)` → extract `"c:myComponent"`

**Convert Aura format to kebab-case:**

- `c:myComponent` → `c-my-component`
- `c:loBetaEntryForm` → `c-lo-beta-entry-form`
- `c:userDashboard` → `c-user-dashboard`

**Conversion algorithm:**

1. Remove `c:` prefix
2. Insert hyphen before each capital letter
3. Convert to lowercase
4. Add `c-` prefix

### Transform 3: Add Component Tag to HTML

**At the location of Pattern E** (the DOM target element), add:

```html
<!-- Add these BEFORE or INSIDE the existing target element -->
<div id="[MOUNT_ID]"></div>  <!-- Choose a mount point ID -->
<[KEBAB-COMPONENT-TAG] [ATTRIBUTES]></[KEBAB-COMPONENT-TAG]>
```

**Where:**

- `[MOUNT_ID]` = Your chosen ID for the mount point (e.g., "lo2Mount", "sfAppMount")
- `[KEBAB-COMPONENT-TAG]` = converted component name from Transform 2
- `[ATTRIBUTES]` = converted attributes from Pattern D (see below)

**If Pattern D had attributes object:**

```javascript
{ recordId: "123", isActive: true, userName: "John" }
```

**Convert to HTML attributes (camelCase → kebab-case):**

```html
<c-my-component record-id="123" is-active="true" user-name="John"></c-my-component>
```

### Transform 4: Replace Beta JavaScript Block

**Delete entire Patterns C and D block:**

```javascript
// DELETE THIS ENTIRE SECTION
const [ENDPOINT_VAR] = "...";
const [APP_VAR] = "c:...";
const [COMPONENT_VAR] = "c:...";
const [TOKEN_VAR] = "...";

$Lightning.use([APP_VAR], function() {
  $Lightning.createComponent([COMPONENT_VAR], {...}, "[DOM_ID]", function(cmp) {
    [CUSTOM_LOGIC]
  });
}, [ENDPOINT_VAR], [TOKEN_VAR]);
```

**Replace with LO 2.0 pattern:**

```javascript
// Configuration (NEW - adapt names to customer's style)
const ECA_CONSUMER_KEY = '[GET_FROM_SALESFORCE_SETUP]';
const LO_APP_ID = '[GET_FROM_SALESFORCE_SETUP]'; // Optional 18-character ID (omit if not required)
const ORG_MYDOMAIN_URL = 'https://[DOMAIN].my.salesforce.com'; // Transform from extracted domain
const components = '[KEBAB-COMPONENT-NAME]'; // From Transform 2

// Helper functions (REQUIRED - copy exactly)
function readCachedResult() {
  try {
    const raw = localStorage.getItem('lo2_frontdoor_result');
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function clearCachedResult() {
  try {
    localStorage.removeItem('lo2_frontdoor_result');
  } catch {}
}

// Mount function (adapt element selection to customer's DOM)
function mountLo20(frontdoorUrl, orgUrl) {
  const [MOUNT_ELEMENT] = document.getElementById('[MOUNT_ID]'); // Customer's mount point
  if ([MOUNT_ELEMENT] && [MOUNT_ELEMENT].querySelector('lightning-out-application')) return;

  function tryMount() {
    if (!customElements?.get?.('lightning-out-application')) return false;

    const el = document.createElement('lightning-out-application');
    el.setAttribute('components', components);
    if (LO_APP_ID) el.setAttribute('app-id', LO_APP_ID);
    el.setAttribute('frontdoor-url', frontdoorUrl);

    ([MOUNT_ELEMENT] || document.body).appendChild(el);
    return true;
  }

  const start = Date.now();
  (function tick() {
    if (tryMount()) return;
    if (Date.now() - start > 15000) {
      console.error('LO 2.0 mount timeout');
      // Optionally show error in customer's error display
      return;
    }
    setTimeout(tick, 50);
  })();

  // CRITICAL: Use literal component name string (NOT variable)
  customElements.whenDefined('[LITERAL-KEBAB-COMPONENT-NAME]').then(() => {
    // Hide customer's loading indicator here
    // Example: document.getElementById('[CUSTOMER_LOADING_ID]').style.display = 'none';

    // If Pattern D had custom callback logic, add it here:
    [CUSTOM_LOGIC_FROM_CALLBACK];
  });
}

// Boot function (wrap all initialization)
function boot() {
  try {
    // Store OAuth config for callback page
    localStorage.setItem('orgMyDomainURL', ORG_MYDOMAIN_URL);
    localStorage.setItem('loAppID', LO_APP_ID);
    localStorage.setItem('loECAKey', ECA_CONSUMER_KEY);
    localStorage.setItem('lo2_returnTo', window.location.pathname);

    // OAuth callback listeners
    window.addEventListener('message', (evt) => {
      const data = evt?.data;
      if (!data || data.error || !data.frontdoorUrl) return;
      clearCachedResult();
      mountLo20(data.frontdoorUrl, data.orgUrl);
    });

    try {
      const bc = new BroadcastChannel('lo2auth');
      bc.onmessage = (evt) => {
        const data = evt?.data;
        if (!data || data.error || !data.frontdoorUrl) return;
        clearCachedResult();
        mountLo20(data.frontdoorUrl, data.orgUrl);
      };
    } catch (e) {}

    window.addEventListener('storage', (evt) => {
      if (evt.key !== 'lo2_frontdoor_result') return;
      const data = readCachedResult();
      if (!data || data.error || !data.frontdoorUrl) return;
      mountLo20(data.frontdoorUrl, data.orgUrl);
    });

    // Check for cached auth
    const cached = readCachedResult();
    if (cached?.frontdoorUrl) {
      mountLo20(cached.frontdoorUrl, cached.orgUrl);
    }

    // Wire up customer's OAuth trigger (button/link/etc)
    const [CUSTOMER_TRIGGER_ELEMENT] = document.getElementById('[CUSTOMER_TRIGGER_ID]');
    if ([CUSTOMER_TRIGGER_ELEMENT]) {
      [CUSTOMER_TRIGGER_ELEMENT].addEventListener('click', () => {
        clearCachedResult();
        window.location.assign('/frontdoor-url.html');
      });
    }
  } catch (e) {
    console.error('Boot error:', e);
  }
}

boot();
```

---

## Phase 3: Integration with Customer Code

### Preserve Customer's:

1. **HTML structure** - Don't modify layout, styling, or element hierarchy
2. **Loading indicators** - Hook into existing UI, don't create new ones
3. **Error handling** - Use existing error display mechanisms
4. **Event handlers** - Preserve any custom event listeners
5. **Business logic** - Move callback logic from Pattern D to `customElements.whenDefined().then()`

### Adapt These Elements:

1. **Element selectors** - Use customer's actual element IDs (don't hardcode "loAppMount", "connectBtn")
2. **Loading indicator** - In `customElements.whenDefined()`, hide customer's loading element
3. **OAuth trigger** - Wire up customer's existing button/link for authentication
4. **Error display** - If customer has error handling, integrate with that

### Example Integration:

**Customer's Beta code had:**

```html
<div id="myContainer">
  <div class="spinner">Loading...</div>
  <div id="lightningTarget"></div>
</div>
<button onclick="doAuth()">Login</button>
```

**After migration:**

```html
<div id="myContainer">
  <div class="spinner">Loading...</div>
  <div id="sfMount"></div>
  <!-- ADD: Choose your own ID -->
  <c-my-component></c-my-component>
  <!-- ADD -->
  <div id="lightningTarget"></div>
  <!-- KEEP if needed -->
</div>
<button id="authBtn">Login</button>
<!-- ADD id for event listener -->
```

**In JavaScript, use customer's actual IDs:**

```javascript
const sfMount = document.getElementById('sfMount'); // Use YOUR mount ID

function mountLo20(frontdoorUrl, orgUrl) {
  if (sfMount && sfMount.querySelector('lightning-out-application')) return;
  // ... rest of mount logic using sfMount
  (sfMount || document.body).appendChild(el);
}

// In boot(), hide customer's spinner when ready
customElements.whenDefined('c-my-component').then(() => {
  document.querySelector('.spinner').style.display = 'none'; // Customer's spinner
});

// Wire up customer's button
document.getElementById('authBtn').addEventListener('click', () => {
  clearCachedResult();
  window.location.assign('/frontdoor-url.html');
});
```

---

## Critical Implementation Rules

**These rules prevent runtime errors - follow exactly:**

### Rule 1: `customElements.whenDefined()` requires literal string

WRONG — Will fail:

```javascript
const components = "c-my-component";
customElements.whenDefined(components).then(...);  // Using variable
```

CORRECT:

```javascript
const components = "c-my-component";
customElements.whenDefined('c-my-component').then(...);  // Literal string
```

### Rule 2: `mountLo20()` must accept two parameters

CORRECT signature (even if orgUrl unused):

```javascript
function mountLo20(frontdoorUrl, orgUrl) {
  // Implementation
}
```

### Rule 3: Always call `clearCachedResult()` before mounting

In every OAuth listener:

```javascript
if (data?.frontdoorUrl) {
  clearCachedResult(); // Must call first
  mountLo20(data.frontdoorUrl, data.orgUrl);
}
```

### Rule 4: Pass both parameters when calling mountLo20

Always:

```javascript
mountLo20(data.frontdoorUrl, data.orgUrl); // Both parameters, even if orgUrl is undefined
```

### Rule 5: Wrap all initialization in `boot()` function

Required structure:

```javascript
function boot() {
  try {
    // All localStorage setup
    // All event listeners
    // All initialization
  } catch (e) {
    console.error('Boot error:', e);
  }
}
boot(); // Must call at end
```

### Rule 6: Component tag has no inline styles

CORRECT:

```html
<c-my-component></c-my-component>
```

WRONG:

```html
<c-my-component style="display: none"></c-my-component>
```

---

## Transformation Patterns

### 1. Domain Transformation

**Pattern**: `https://[subdomain].lightning.[pod].force.com` → `https://[subdomain].my.[pod].salesforce.com`

```javascript
// BEFORE (Beta)
const endpoint = 'https://orgfarm-5b43fe90c6.test1.lightning.pc-rnd.force.com';

// AFTER (LO 2.0)
const ORG_MYDOMAIN_URL = 'https://orgfarm-5b43fe90c6.test1.my.pc-rnd.salesforce.com';
```

### 2. Library Script Tag

```html
<!-- BEFORE (Beta) -->
<script src="https://YOUR_ORG.lightning.force.com/lightning/lightning.out.js"></script>

<!-- AFTER (LO 2.0) -->
<script async src="https://YOUR_ORG.my.salesforce.com/lightning/lightning.out.latest/index.iife.prod.js"></script>
```

### 3. Component Name Conversion

```javascript
// BEFORE (Beta): Aura-style naming
const component = 'c:loBetaEntryForm';

// AFTER (LO 2.0): Kebab-case
const components = 'c-lo-beta-entry-form';
```

### 4. Component Initialization - Complete Replacement

**REMOVE this entire Beta pattern:**

```javascript
$Lightning.use(
  'c:OrgFarmOut',
  function () {
    $Lightning.createComponent(
      'c:loBetaEntryForm',
      { contactId: '003...' }, // attributes
      'lightning-out', // DOM target
      function (cmp) {
        console.log('created');
      },
    );
  },
  'https://org.lightning.force.com',
  '00D...TOKEN...', // hardcoded token
);
```

**REPLACE with LO 2.0 pattern:**

**Step A**: Add component tag directly in HTML:

```html
<div id="loAppMount"></div>
<c-lo-beta-entry-form contact-id="003..."></c-lo-beta-entry-form>
```

_Note: Attributes converted from camelCase to kebab-case_

**Step B**: Create mounting function:

```javascript
function mountLo20(frontdoorUrl) {
  // Poll for custom element availability
  function tryMount() {
    if (!customElements?.get?.('lightning-out-application')) return false;

    const el = document.createElement('lightning-out-application');
    el.setAttribute('components', 'c-lo-beta-entry-form');
    // app-id is optional — set it only if your LO 2.0 app requires it
    // el.setAttribute('app-id', 'YOUR_18_CHAR_APP_ID');
    el.setAttribute('frontdoor-url', frontdoorUrl);

    document.getElementById('loAppMount').appendChild(el);
    return true;
  }

  // Retry with timeout
  const start = Date.now();
  (function tick() {
    if (tryMount()) return;
    if (Date.now() - start > 15000) {
      console.error('Timeout: LO 2.0 not registered');
      return;
    }
    setTimeout(tick, 50);
  })();
}
```

### 5. Authentication Replacement

**BEFORE (Beta)**: Hardcoded token

```javascript
const authToken = '<LEGACY_SESSION_TOKEN_PLACEHOLDER>'; // Remove this
```

**AFTER (LO 2.0)**: OAuth PKCE flow

**Step A**: Store OAuth config in localStorage:

```javascript
localStorage.setItem('orgMyDomainURL', 'https://YOUR_ORG.my.salesforce.com');
localStorage.setItem('loAppID', 'YOUR_18_CHAR_APP_ID');
localStorage.setItem('loECAKey', 'YOUR_ECA_CONSUMER_KEY');
localStorage.setItem('lo2_returnTo', '/your-page.html');
```

**Step B**: Trigger OAuth flow (redirect to callback page):

```javascript
// User clicks "Connect"
window.location.assign('/frontdoor-url.html');
```

**Step C**: Listen for OAuth result via multiple channels:

```javascript
// postMessage
window.addEventListener('message', (evt) => {
  if (evt.data?.frontdoorUrl) {
    mountLo20(evt.data.frontdoorUrl);
  }
});

// BroadcastChannel
const bc = new BroadcastChannel('lo2auth');
bc.onmessage = (evt) => {
  if (evt.data?.frontdoorUrl) {
    mountLo20(evt.data.frontdoorUrl);
  }
};

// localStorage (cross-tab)
window.addEventListener('storage', (evt) => {
  if (evt.key === 'lo2_frontdoor_result') {
    const data = JSON.parse(localStorage.getItem('lo2_frontdoor_result'));
    if (data?.frontdoorUrl) mountLo20(data.frontdoorUrl);
  }
});
```

### 6. Component Attribute Mapping

```javascript
// BEFORE (Beta): JS object
$Lightning.createComponent("c:myComp", {
  contactId: "003...",
  recordId: "001...",
  isActive: true,
  count: 5
}, ...);

// AFTER (LO 2.0): HTML attributes (kebab-case)
```

```html
<c-my-comp contact-id="003..." record-id="001..." is-active="true" count="5"> </c-my-comp>
```

### 7. Component Readiness Detection

```javascript
// BEFORE (Beta): Callback
$Lightning.createComponent(..., function(cmp) {
  console.log("Component ready");
});

// AFTER (LO 2.0): Web Component lifecycle
customElements.whenDefined("c-my-component").then(() => {
  console.log("Component ready");
  document.getElementById("loading").style.display = "none";
});
```

### 8. Salesforce App Mapping

```javascript
// BEFORE (Beta): Aura app name
const auraApp = 'c:OrgFarmOut'; // No longer used

// AFTER (LO 2.0): Lightning Out 2.0 app ID (optional, 18 chars)
const LO_APP_ID = '<LIGHTNING_OUT_APP_ID_PLACEHOLDER>'; // From Setup → Lightning Out Apps (omit if not required)
```

---

## Required Setup in Salesforce

### 1. Create Lightning Out 2.0 App (Optional)

- Setup → Lightning Out → New Lightning Out App
- Copy the **18-character App ID** (only needed if your deployment requires an explicit app ID)

### 2. Create External Client App (ECA)

- Setup → App Manager → New Connected App → External Client App
- Enable OAuth Settings with PKCE
- Copy the **Consumer Key**
- Add your callback URL to allowed domains

### 3. Helper Files (Assumption)

This guide assumes you have:

- `frontdoor-url.html` — OAuth callback page
- `utils/LightningOutAuth.js` — OAuth PKCE implementation

---

## Essential Code Blocks

The complete, copyable host-page implementation lives in
[`assets/lo20-host-page-template.html`](../assets/lo20-host-page-template.html).
Copy that file as your starting point and fill in the `CONFIGURATION`
constants, then replace `c-your-component` with the migrated component tag and
its kebab-case attributes (use `scripts/convert-lo-names.py` to derive them).
The template is a single self-consistent host page that already assembles every
required piece:

- **Configuration** constants (ECA consumer key, optional LO 2.0 App id, My Domain URL, `components`).
- **DOM references** declared once at the top.
- The four **helper functions**: `setLoading`, `showError`, `readCachedResult`, `clearCachedResult`.
- The two-parameter **`mountLo20(frontdoorUrl, orgUrl)`** function with a duplicate-mount guard and a literal-string `customElements.whenDefined(...)` gate.
- The **`boot()`** wrapper holding all initialization — localStorage config, the postMessage / BroadcastChannel / storage listeners, the cached-result check, and the connect-button handler — with `boot()` called once at the end.

**Do NOT** hand-reassemble these blocks into separate `initializeOAuth()` /
`setupCallbackListeners()` functions, run init code at script level outside
`boot()`, or omit the trailing `boot()` call. After filling in your copy, run
`python3 scripts/validate-lo20-page.py <file>` to confirm the six
non-negotiable rules still hold.

---

## Common Pitfalls

| Issue                                | Problem                                                  | Solution                                                                                           |
| ------------------------------------ | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **Missing boot() wrapper**           | Init code runs at script level                           | Wrap ALL init logic in `function boot() { ... }` and call `boot()` at end                          |
| **Component display logic**          | Adding `display:none` to component tag                   | Control visibility via `loadingEl.style.display`, NOT on component tag                             |
| **Missing helper functions**         | Undefined `setLoading()`, `showError()`, etc.            | Include all 4 helper functions: `setLoading`, `showError`, `readCachedResult`, `clearCachedResult` |
| **Wrong customElements.whenDefined** | Using variable: `customElements.whenDefined(components)` | Use literal string: `customElements.whenDefined('c-my-component')`                                 |
| **Missing clearCachedResult()**      | Not clearing cache before mount                          | Call `clearCachedResult()` before every `mountLo20()` call                                         |
| **BroadcastChannel not wrapped**     | BroadcastChannel creation fails in some browsers         | Wrap in try-catch: `try { const bc = new BroadcastChannel(...) } catch (e) {}`                     |
| **Domain mismatch**                  | Using `.lightning.force.com`                             | Change to `.my.salesforce.com`                                                                     |
| **Component not defined**            | Wrong kebab-case format                                  | `c:myComponent` → `c-my-component`                                                                 |
| **Missing attributes**               | Using camelCase in HTML                                  | `contactId` → `contact-id`                                                                         |
| **No component tag**                 | Only creating `<lightning-out-application>`              | Add `<c-component>` tag to HTML                                                                    |

Other pitfalls to watch for: missing defensive checks (`!data` / `data.error` /
`!data.frontdoorUrl`) in a listener; inline `document.getElementById()` calls
instead of DOM-reference constants; mount timeouts (check the `app-id` and
library URL); calling `mountLo20()` more than once without a duplicate-mount
guard; and OAuth not starting because the localStorage config was not set
before the redirect. `scripts/validate-lo20-page.py` catches the structural
ones automatically.

---

## Verification Checklist

After migration, verify:

**Script Structure:**

- [ ] All init logic wrapped in `function boot() { ... }`
- [ ] `boot()` called at the end of script
- [ ] DOM references declared as constants at top
- [ ] All 4 helper functions present: `setLoading`, `showError`, `readCachedResult`, `clearCachedResult`

**Mount Function:**

- [ ] `mountLo20(frontdoorUrl, orgUrl)` takes TWO parameters
- [ ] Duplicate mount check present
- [ ] `customElements.whenDefined()` uses literal string, not variable
- [ ] `(loAppMount || document.body).appendChild(el)` fallback present

**OAuth & Listeners:**

- [ ] `clearCachedResult()` called before every `mountLo20()` call
- [ ] All three listeners present: postMessage, BroadcastChannel, storage
- [ ] BroadcastChannel wrapped in try-catch
- [ ] Each listener checks: `!data`, `data.error`, `!data.frontdoorUrl`
- [ ] Cached result check present before any user interaction

**HTML:**

- [ ] Component tag has NO inline `display:none` style
- [ ] Both `<div id="loAppMount"></div>` and `<c-component>` tag present
- [ ] Loading indicator uses proper structure with nested divs

**Configuration:**

- [ ] Domain changed to `.my.salesforce.com`
- [ ] Library path uses `/lightning.out.latest/index.iife.prod.js`
- [ ] Component name is kebab-case
- [ ] LO 2.0 app ID is 18 characters (if used — app-id is optional)
- [ ] ECA consumer key is correct
- [ ] Component attributes are kebab-case
- [ ] `lo2_returnTo` matches current filename

---

## Quick Migration Workflow

1. **Extract from Beta page:**

   - Domain (endpoint URL)
   - Component name (Aura format)
   - Attributes object
   - Aura app name

2. **Transform:**

   - Domain: `.lightning.force.com` → `.my.salesforce.com`
   - Component: `c:name` → `c-name`
   - Attributes: `{camelCase: val}` → `kebab-case="val"`

3. **Setup in Salesforce:**

   - Create LO 2.0 App → get 18-char ID (optional)
   - Create ECA → get consumer key

4. **Update HTML:**

   - Change script src
   - Add mount point div
   - Add component tag with attributes
   - Remove `$Lightning` code

5. **Add JavaScript:**

   - Config constants
   - mountLo20() function
   - localStorage setup
   - OAuth listeners
   - Connect button handler

6. **Verify layout:**

   - Component fills the same space as the Beta version (no clipping or scrolling)
   - No fixed height on mount point or parent containers
   - All form fields visible without scrolling within the component area

7. **Test:**
   - Click "Connect to Salesforce"
   - Complete OAuth
   - Verify component renders with full content visible
   - Check browser console for errors
