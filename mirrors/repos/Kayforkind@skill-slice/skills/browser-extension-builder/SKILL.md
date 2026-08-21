---
name: browser-extension-builder
description: "Scaffolds Manifest V3 Chrome, Firefox, and cross-browser extensions: content scripts, service workers, popups, chrome.storage, monetization, and Web Store/AMO publishing. Trigger on browser extension, chrome extension, firefox addon, MV3, or extension popup work. Do not use for Electron apps, PWAs, or ordinary websites unless the deliverable is an unpacked or store extension."
version: 1.0.1
risk: unknown
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

# Browser Extension Builder

Expert in building browser extensions that solve real problems — Chrome, Firefox, and cross-browser. Covers extension architecture, Manifest V3, content scripts, popup UIs, monetization strategies, and Chrome Web Store publishing.

**Role:** Browser Extension Architect

You extend the browser to give users superpowers. You understand the unique constraints of extension development — permissions, security, store policies. You build extensions that people install and actually use daily. You know the difference between a toy and a tool.

## When to Use

Trigger this skill when the user mentions or implies any of:
- "browser extension"
- "chrome extension"
- "firefox addon"
- "manifest v3" / "MV3"
- "content script"
- "service worker" in an extension context
- "chrome web store" / "addons.mozilla.org"
- Extension monetization, popup UI, or extension publishing

Do **not** use this skill for general web apps, Electron apps, or PWA-only tasks unless the user explicitly wants a browser extension wrapper.

## Prerequisites

- Node.js 18+ and npm (for bundling if using a framework)
- A Chromium-based browser (Chrome, Edge, Brave) for local testing
- Firefox Developer Edition or Nightly for cross-browser testing (optional)
- A text editor or Cursor
- For publishing: a Chrome Web Store developer account ($5 one-time fee) and/or an AMO (addons.mozilla.org) account
- Icons in 16×16, 48×48, and 128×128 PNG (required for store listing)

## Procedure

### 1. Scaffold the Extension Project

Create the standard MV3 directory structure:

```powershell
mkdir my-extension; cd my-extension
New-Item -ItemType Directory -Force popup, content, background, options, icons
New-Item popup\popup.html, popup\popup.css, popup\popup.js
New-Item content\content.js
New-Item background\service-worker.js
New-Item options\options.html, options\options.js
New-Item manifest.json
```

Resulting structure:

```
extension/
├── manifest.json
├── popup/
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── content/
│   └── content.js
├── background/
│   └── service-worker.js
├── options/
│   ├── options.html
│   └── options.js
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### 2. Write the Manifest V3

`manifest.json`:

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "What it does",
  "permissions": ["storage", "activeTab"],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content/content.js"]
    }
  ],
  "background": {
    "service_worker": "background/service-worker.js"
  },
  "options_page": "options/options.html"
}
```

**Hard rule:** Chrome requires Manifest V3 for all new extensions. Do not use `"manifest_version": 2` — it will be rejected by the Web Store.

### 3. Implement the Communication Pattern

```
Popup ←→ Background (Service Worker) ←→ Content Script
              ↓
        chrome.storage
```

- **Popup** sends messages to the background service worker and reads `chrome.storage`.
- **Background service worker** coordinates logic, handles events, and relays messages to content scripts.
- **Content script** runs on matched pages, reads/modifies the DOM, and responds to messages.

### 4. Write the Content Script

`content/content.js`:

```javascript
// Runs on every matched page
document.addEventListener('DOMContentLoaded', () => {
  const element = document.querySelector('.target');
  if (element) {
    element.style.backgroundColor = 'yellow';
  }
});

// Listen for messages from popup/background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getData') {
    const data = document.querySelector('.data')?.textContent;
    sendResponse({ data });
  }
  return true; // Keep channel open for async
});
```

To inject a floating UI on the page:

```javascript
function injectUI() {
  const container = document.createElement('div');
  container.id = 'my-extension-ui';
  container.innerHTML = `
    <div style="position: fixed; bottom: 20px; right: 20px;
                background: white; padding: 16px; border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 10000;">
      <h3>My Extension</h3>
      <button id="my-extension-btn">Click me</button>
    </div>
  `;
  document.body.appendChild(container);

  document.getElementById('my-extension-btn').addEventListener('click', () => {
    // Handle click
  });
}

injectUI();
```

Scope content scripts to specific sites when possible:

```json
{
  "content_scripts": [
    {
      "matches": ["https://specific-site.com/*"],
      "js": ["content.js"],
      "run_at": "document_end"
    }
  ]
}
```

### 5. Implement Storage and State

`chrome.storage` is the primary persistence layer.

```javascript
// Save data
chrome.storage.local.set({ key: 'value' }, () => {
  console.log('Saved');
});

// Get data
chrome.storage.local.get(['key'], (result) => {
  console.log(result.key);
});

// Sync storage (syncs across devices)
chrome.storage.sync.set({ setting: true });

// Watch for changes
chrome.storage.onChanged.addListener((changes, area) => {
  if (changes.key) {
    console.log('key changed:', changes.key.newValue);
  }
});
```

Storage limits:

| Type  | Limit                     |
|-------|---------------------------|
| local | 5 MB                      |
| sync  | 100 KB total, 8 KB per item |

Async/await wrapper:

```javascript
async function getStorage(keys) {
  return new Promise((resolve) => {
    chrome.storage.local.get(keys, resolve);
  });
}

async function setStorage(data) {
  return new Promise((resolve) => {
    chrome.storage.local.set(data, resolve);
  });
}

const { settings } = await getStorage(['settings']);
await setStorage({ settings: { ...settings, theme: 'dark' } });
```

### 6. Load the Extension for Local Testing (Chrome)

1. Open `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `my-extension` folder
5. The extension appears in the toolbar; click the puzzle piece icon to pin it

To reload after code changes: click the reload arrow on the extension card in `chrome://extensions/`.

### 7. Load for Local Testing (Firefox)

1. Open `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Select `manifest.json` in the project folder
4. Temporary add-ons are removed when Firefox closes

### 8. Monetization (Optional)

Revenue models:

| Model        | How It Works                |
|--------------|-----------------------------|
| Freemium     | Free basic, paid features   |
| One-time     | Pay once, use forever       |
| Subscription | Monthly/yearly access       |
| Donations    | Tip jar / Buy me a coffee   |
| Affiliate    | Recommend products          |

Chrome discontinued built-in payments. Use your own backend and redirect to an external checkout page:

```javascript
// 1. User clicks "Upgrade" in popup
// 2. Open your website with user ID
chrome.tabs.create({
  url: `https://your-site.com/upgrade?user=${userId}`
});

// 3. After payment, sync status
async function checkPremium() {
  const { userId } = await getStorage(['userId']);
  const response = await fetch(`https://your-api.com/premium/${userId}`);
  const { isPremium } = await response.json();
  await setStorage({ isPremium });
  return isPremium;
}
```

Feature gating:

```javascript
async function usePremiumFeature() {
  const { isPremium } = await getStorage(['isPremium']);
  if (!isPremium) {
    showUpgradeModal();
    return;
  }
  // Run premium feature
}
```

### 9. Publish to the Chrome Web Store

1. Zip the extension folder contents (not the parent folder):
   ```powershell
   Compress-Archive -Path .\* -DestinationPath my-extension.zip
   ```
2. Go to the [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/).
3. Pay the one-time $5 developer fee if not already paid.
4. Click **New Item**, upload `my-extension.zip`.
5. Fill in the listing: name, description, screenshots, category, privacy practices.
6. Submit for review. Review typically takes 1–3 business days.

### 10. Publish to Firefox Add-ons (AMO)

1. Zip the extension (same as above).
2. Go to [addons.mozilla.org/developers](https://addons.mozilla.org/developers/).
3. Submit a new add-on, upload the zip.
4. AMO runs automated and manual review. Firefox requires `browser_specific_settings` in the manifest for signing.

## Pitfalls

### Using Deprecated Manifest V2 — HIGH
**Problem:** Chrome requires V3 for new extensions. MV2 submissions are rejected.
**Fix:** Migrate to Manifest V3. Replace background pages with service workers. Use `"manifest_version": 3`.

### Excessive Permissions Requested — HIGH
**Problem:** Broad permissions (`<all_urls>`, `*://*/*`) trigger store rejection or scary warnings.
**Fix:** Use specific `host_permissions` and `optional_permissions`. Request permissions at runtime with `chrome.permissions.request()` when possible.

### No Error Handling in Extension — MEDIUM
**Problem:** Not checking `chrome.runtime.lastError` causes silent failures.
**Fix:** Always check `chrome.runtime.lastError` after API calls:
```javascript
chrome.storage.local.get(['key'], (result) => {
  if (chrome.runtime.lastError) {
    console.error(chrome.runtime.lastError);
    return;
  }
  // use result
});
```

### Hardcoded URLs in Extension — MEDIUM
**Problem:** Hardcoded URLs make it hard to update endpoints without re-publishing.
**Fix:** Store configuration in `chrome.storage` or fetch from a remote config endpoint.

### Missing Extension Icons — LOW
**Problem:** Missing icons affect store listing and toolbar display.
**Fix:** Add icons in 16, 48, and 128 pixel sizes. Reference them in `action.default_icon`.

### Service Worker Lifecycle
**Problem:** Service workers are terminated when idle and restarted on events. Do not rely on global state persisting.
**Fix:** Persist all state in `chrome.storage`. Use `chrome.alarms` for scheduled tasks, not `setInterval`.

### Content Script Isolation
**Problem:** Content scripts run in an isolated world and cannot directly access page JavaScript variables or functions.
**Fix:** To interact with page context, inject a `<script>` tag or use `chrome.scripting.executeScript` with `world: 'MAIN'`.

### Cross-Origin Restrictions
**Problem:** Fetching from arbitrary origins fails without host permissions.
**Fix:** Add the target origin to `host_permissions` in the manifest.

## Verification

### Manifest Validity
Check the manifest parses correctly:

```powershell
Get-Content manifest.json | ConvertFrom-Json | Select-Object manifest_version, name, version
```

Expected output:
```
manifest_version name          version
--------------- ----          -------
             3 My Extension   1.0.0
```

### Extension Loads in Chrome
1. Navigate to `chrome://extensions/`
2. Confirm the extension card appears with no error badge
3. If errors exist, click **Errors** to view console output

### Content Script Runs
1. Open a matched page (e.g., `https://specific-site.com/`)
2. Open DevTools (F12) → Console
3. Confirm content script logs or DOM modifications appear
4. Verify the injected UI element exists:
   ```javascript
   document.getElementById('my-extension-ui')
   ```

### Storage Works
1. Open the popup
2. Trigger a storage write
3. In `chrome://extensions`, click **Service worker** to open the background console
4. Run:
   ```javascript
   chrome.storage.local.get(null, console.log)
   ```
5. Confirm the saved key-value pair is present

### Message Passing
1. From the popup console, send a message:
   ```javascript
   chrome.runtime.sendMessage({ action: 'getData' }, console.log)
   ```
2. Confirm the content script responds with the expected data

### Store Readiness Checklist
- [ ] `manifest_version` is 3
- [ ] Icons present (16, 48, 128)
- [ ] No excessive permissions
- [ ] `chrome.runtime.lastError` checked in all callbacks
- [ ] Privacy policy URL provided in store listing
- [ ] Screenshots (1280×800 or 640×400) uploaded
- [ ] Extension zip contains `manifest.json` at root level

## Collaboration

### Delegation Triggers

- `react|vue|svelte` → **frontend** (Extension popup framework)
- `monetization|payment|subscription` → **micro-saas-launcher** (Extension business model)
- `personal tool|just for me` → **personal-tool-builder** (Personal extension)
- `AI|LLM|GPT` → **ai-wrapper-product** (AI-powered extension)

### Productivity Extension

Skills: `browser-extension-builder`, `frontend`, `micro-saas-launcher`

Workflow:
1. Define extension functionality
2. Build popup UI with React
3. Implement content scripts
4. Add premium features
5. Publish to Chrome Web Store
6. Market and iterate

### AI Browser Assistant

Skills: `browser-extension-builder`, `ai-wrapper-product`, `frontend`

Workflow:
1. Design AI features for browser
2. Build extension architecture
3. Integrate AI API
4. Create popup interface
5. Handle usage limits/payments
6. Publish and grow

## Related Skills

Works well with: `frontend`, `micro-saas-launcher`, `personal-tool-builder`, `ai-wrapper-product`

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
