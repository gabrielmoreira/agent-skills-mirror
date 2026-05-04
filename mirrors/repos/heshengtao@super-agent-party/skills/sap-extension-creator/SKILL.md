---
name: sap-extension-creator
description: Create Super Agent Party (SAP) extensions. This skill should be used when users want to create, build, or scaffold a new extension for Super Agent Party - including static HTML extensions (pure frontend) and Node.js backend extensions. Triggers on requests like "create a new SAP extension", "build an extension for Super Agent Party", "scaffold a plugin", "make a chat UI extension", or when working with sap extension projects.
---

# SAP Extension Creator

## Overview

Create Super Agent Party extensions—self-contained packages that extend the platform with custom chat UI and tools. Two modes are supported:

- **Static extension**: Pure HTML/CSS/JS frontend, served directly by SAP from the extension folder
- **Node.js extension**: Full-stack with Express backend, auto-managed by SAP (`npm install` + `node index.js <port>`)

Both modes support MCP tool registration (the `register_node_extension_mcp` protocol message works for ANY extension via WebSocket, despite the "node" in its name).

## Quick Decision Tree

```
User wants to create an extension?
├─ Only needs UI (chat, display, simple interactions)? → Static Extension
└─ Needs backend logic (API calls, DB, file processing)? → Node.js Extension
```

## Core Files Every Extension Needs

| File | Required | Purpose |
|------|----------|---------|
| `package.json` | ✅ | Metadata, dependencies, window config |
| `index.html` | ✅ | Main UI (full HTML page, single-file app) |
| `index.js` | Node only | Node.js entry point |
| `node_modules/` | Node only | Auto-installed by SAP via `npm install` |

## Workflow

### Step 1: Gather Requirements

Ask the user:

1. **Extension name?** (hyphen-case, e.g., `my-weather-widget`)
2. **Description?** (one sentence)
3. **Static or Node.js?** (Node.js only if backend logic/server-side code is needed)
4. **For Node.js: what npm dependencies?**
5. **Should it register custom tools for the AI?** (works in both static and Node.js modes via WebSocket MCP)
6. **GitHub repository URL?** (optional, for updates)
7. **Transparent window?** (frameless, always-on-top — for mini widgets like music controllers)
8. **Default window size?** (width/height in pixels)

### Step 2: Scaffold the Extension

Use the templates in `assets/` as starting points:

- **Static**: Copy `assets/static-template/`
- **Node.js**: Copy `assets/node-template/`

Create the extension directory under the workspace (user will later install it into SAP's `extensions/` folder).

### Step 3: Write package.json

See `references/package-json-spec.md` for the complete field reference. Minimum:

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "description": "What it does",
  "author": "your-name",
  "repository": "https://github.com/user/repo",
  "backupRepository": "https://gitee.com/user/repo",
  "category": "Tools"
}
```

For Node.js extensions, also include:
```json
{
  "main": "index.js",
  "nodePort": 0,
  "dependencies": { "express": "^5.1.0" }
}
```

For transparent/frameless widgets (e.g., mini music controllers, floating panels):
```json
{
  "transparent": true,
  "width": 280,
  "height": 80
}
```

When `transparent: true`, SAP creates a frameless, transparent, always-on-top window (see main.js `open-extension-window` handler). Use this for compact overlay widgets.

### Step 4: Write index.html

The HTML page is rendered inside an Electron BrowserWindow (either directly or via an iframe). Key patterns:

- **Self-contained**: The extension is a single HTML file with all CSS/JS inlined or loaded from CDN. For Node.js extensions, static assets are served from the extension directory.
- **Font Awesome**: Use CDN to ensure reliable loading in both static and Node.js modes:
  ```html
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  ```
  Avoid relative paths like `../../fontawesome/` — these may work for static extensions but break for Node.js extensions (different serving paths).
- **Dark/Light mode**: Always support both (see "Theme & i18n" section below).
- **i18n (Chinese/English)**: Always support bilingual UI (see "Theme & i18n" section below).
- **WebSocket connection**: Connect to `ws://host/ws` for messaging and MCP.
- **Extension ID**: Parse `window.location.pathname` for `/extensions/{ext_id}/`.
- **Message rendering**: Listen for `messages_update` and `broadcast_messages` events.
- **Send user input**: Send `set_user_input` then `trigger_send_message`.

### Step 5: Write index.js (Node.js only)

See `references/node-entry-spec.md` for the full protocol. The entry point:

1. Receives a port number via `process.argv[2]`
2. Starts an Express server on that port at `127.0.0.1`
3. Serves static files from its own directory
4. Exposes a `/health` endpoint for readiness checks
5. SAP reverse-proxies requests to the extension

### Step 6: Implement Tool Registration (optional, works in both modes)

Extensions can register tools that the AI agent can call — via WebSocket in the frontend (both static and Node.js). Register via WebSocket:

```js
ws.send(JSON.stringify({
    type: 'register_node_extension_mcp',
    data: {
        ext_id: extId,
        tools: [{
            name: `${extId}_my_tool`,
            description: 'What this tool does (use the user\'s language)',
            parameters: {
                type: 'object',
                properties: {
                    param1: { type: 'string', description: '...' }
                },
                required: ['param1']
            }
        }]
    }
}));
```

Handle incoming tool calls:
```js
if (d.type === 'call_mcp_tool') {
    // Execute tool, then:
    ws.send(JSON.stringify({
        type: 'mcp_tool_result',
        data: { call_id: d.data.call_id, result: 'output' }
    }));
}
```

**Important**: Always send `unregister_node_extension_mcp` on `beforeunload`:
```js
window.addEventListener('beforeunload', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type:'unregister_node_extension_mcp', data:{ext_id:MY_EXT_ID} }));
    }
});
```

See `sap-lx-music/index.html` for a complete real-world MCP implementation example (static extension with 12+ registered tools).

---

## Theme & i18n (Dark/Light Mode + Bilingual)

Every extension should support **dark/light mode** and **Chinese/English bilingual** UI. Do NOT hardcode a single theme color scheme — use CSS variables so each extension can have its own identity.

### CSS Variable Pattern

Define light theme in `:root` and override in `body.dark`:

```css
:root {
  --bg: #ffffff;
  --bg-secondary: #f5f5f5;
  --text: #333333;
  --text-sub: #888888;
  --accent: #ec4141;        /* extension's own brand color */
  --accent-hover: #d73a3a;
  --border: rgba(0,0,0,0.08);
  --transition: 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
  --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif;
}

body.dark {
  --bg: #2b2b2b;
  --bg-secondary: #222222;
  --text: #e0e0e0;
  --text-sub: #888888;
  --border: rgba(255,255,255,0.06);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  height: 100%; font-family: var(--font);
  background: var(--bg); color: var(--text);
  transition: background var(--transition);
}
```

### Dark Mode Toggle

```js
function initTheme() {
  const saved = localStorage.getItem('myext_dark');
  if (saved === 'dark' || (!saved && matchMedia('(prefers-color-scheme:dark)').matches)) {
    document.body.classList.add('dark');
  }
}

function toggleDarkMode() {
  const isDark = document.body.classList.toggle('dark');
  localStorage.setItem('myext_dark', isDark ? 'dark' : 'light');
}
```

### i18n Pattern

```js
const i18n = {
  zh: {
    welcome: '欢迎使用我的扩展',
    send: '发送',
    // ... all UI strings
  },
  en: {
    welcome: 'Welcome to My Extension',
    send: 'Send',
    // ...
  }
};

let lang = localStorage.getItem('myext_lang') || 'zh';
function t(k) { return i18n[lang]?.[k] || i18n.zh[k] || k; }

function toggleLanguage() {
  lang = lang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('myext_lang', lang);
  updateAllTexts();  // re-render all i18n-dependent UI
}
```

When registering MCP tools, set `description` and `parameters` in the current user's language for better AI interaction.

---

## Responsive Design

Every extension should work well across different window sizes. Critical patterns:

### Viewport Meta (REQUIRED)

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
```

### CSS Media Queries

Use breakpoints to adapt layout at small sizes:

```css
@media (max-width: 900px) {
  /* stack layouts vertically, reduce padding */
}

@media (max-width: 600px) {
  /* hide secondary elements, compact controls */
}
```

Key responsive practices:
- Use `vw` units for widths as fallback (e.g., `width: 65vw; max-width: 360px`)
- Use `flex` layouts with `flex-wrap` that naturally adapt
- Hide non-essential elements on small screens (`display: none`)
- Reduce font sizes and padding at breakpoints

---

## iframe Compatibility

Extensions may be rendered inside an iframe (depending on SAP's configuration). Ensure:

- **Extension ID detection**: Use `window.location.pathname` (works in both direct and iframe contexts):
  ```js
  function getExtId() {
    try {
      const match = window.location.pathname.match(/\/extensions\/([^\/]+)/);
      return match ? match[1] : 'unknown';
    } catch(e) { return 'unknown'; }
  }
  ```
- **WebSocket connection**: Use `location.host` (not hardcoded):
  ```js
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${proto}//${location.host}/ws`);
  ```
- **Window close**: `window.close()` works in both direct and iframe contexts
- **Avoid `window.top` / `window.parent` assumptions** — your extension may be the top-level window
- **Font Awesome via CDN** ensures icons load regardless of serving path

---

## Transparent Window / Compact Mode

When `transparent: true` is set in package.json, SAP creates a frameless transparent window. The extension must implement **compact mode** to work correctly.

### How SAP Creates Transparent Windows

From `main.js`, when `extension.transparent` is true:

```js
{
  frame: false,
  transparent: true,
  alwaysOnTop: true,
  skipTaskbar: false,
  hasShadow: false,
  backgroundColor: 'rgba(0, 0, 0, 0)',
}
```

### Compact Mode CSS (REQUIRED for transparent extensions)

```css
/* Transparent backgrounds */
body.compact { background: transparent !important; }
html.compact { background: transparent !important; }

/* Drag regions — make structural elements draggable for frameless windows */
body.compact header,
body.compact footer,
body.compact #inputBar {
  -webkit-app-region: drag;
}

/* Interactive elements MUST opt-out of drag */
body.compact button,
body.compact input,
body.compact textarea,
body.compact select,
body.compact a,
body.compact .compact-close-btn {
  -webkit-app-region: no-drag;
}

/* Compact close button (red circle, top-right) */
.compact-close-btn { display: none; }
body.compact .compact-close-btn {
  display: flex;
  position: absolute;
  top: 5px; right: 5px;
  width: 20px; height: 20px;
  background: rgb(255, 57, 57);
  border: none; border-radius: 50%;
  color: #fff;
  align-items: center; justify-content: center;
  font-size: 10px; cursor: pointer;
  transition: 0.2s;
  z-index: 100;
  -webkit-app-region: no-drag;
}
body.compact .compact-close-btn:hover { background: #ec4141; }
```

### Compact Mode Detection (REQUIRED)

```js
function checkCompactMode() {
  if (window.innerHeight < 200) {
    document.documentElement.classList.add('compact');
    document.body.classList.add('compact');
  } else {
    document.documentElement.classList.remove('compact');
    document.body.classList.remove('compact');
  }
}

function closeWindow() { window.close(); }

checkCompactMode();
window.addEventListener('resize', checkCompactMode);
```

### Placing the Close Button

The close button HTML must be placed at the body level (not nested inside containers), typically right after `<body>`:

```html
<body>
  <button class="compact-close-btn" onclick="closeWindow()" title="关闭窗口">
    <i class="fa-solid fa-xmark"></i>
  </button>
  <!-- rest of content -->
</body>
```

For transparent mini-widgets, you can also place the close button inside a content container and make it visible on hover — see `sap-lx-music` for this pattern.

---

## Using iframes for Custom URL Schemes

If your extension needs to invoke custom protocol URLs (e.g., `lxmusic://`, `myapp://`), use a hidden iframe technique:

```js
function invokeScheme(url) {
  let iframe = document.getElementById('scheme-invoker');
  if (!iframe) {
    iframe = document.createElement('iframe');
    iframe.id = 'scheme-invoker';
    iframe.style.display = 'none';
    document.body.appendChild(iframe);
  }
  iframe.src = url;
}
```

This avoids `window.open()` popup blockers and works reliably inside Electron.

---

## WebSocket Protocol Reference

| Message Type | Direction | Purpose |
|---|---|---|
| `get_messages` | → SAP | Request current message history |
| `messages_update` | ← SAP | Message list updated |
| `broadcast_messages` | ← SAP | Broadcast message update |
| `set_user_input` | → SAP | Update user input text |
| `trigger_send_message` | → SAP | Send current input as user message |
| `trigger_clear_message` | → SAP | Clear all messages |
| `register_node_extension_mcp` | → SAP | Register MCP tools (works for static AND Node.js) |
| `unregister_node_extension_mcp` | → SAP | Unregister on page close |
| `mcp_registered` | ← SAP | Confirmation of registration |
| `call_mcp_tool` | ← SAP | AI agent calls a registered tool |
| `mcp_tool_result` | → SAP | Return tool execution result |
| `trigger_close_extension` | → SAP | Request extension window close |

---

## Important Notes

- **Extension ID format**: `{owner}_{repo}` (e.g., `heshengtao_sap-example`)
- **nodePort: 0** means auto-assign a free port (3100-13999 range)
- **Always register `beforeunload` handler** to send `unregister_node_extension_mcp`
- **MCP works in both static and Node.js extensions** — the `register_node_extension_mcp` message type name is historical; it works over WebSocket from any extension
- **Font Awesome**: Always use CDN (`cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`). Relative paths like `../../fontawesome/` do NOT work for Node.js extensions (they're served from Express, not from SAP's static directory)
- **Theme colors**: Each extension defines its own identity via CSS variables on `:root` and `body.dark`. Do NOT force SAP's theme colors
- **Always implement dark/light mode** and **Chinese/English i18n** as basic functionality
- **Transparent windows**: Always implement compact mode. Without `-webkit-app-region: drag`, frameless windows cannot be moved. Without `-webkit-app-region: no-drag` on interactive elements, buttons become unclickable
- **Close button**: For transparent/frameless windows, the extension MUST provide its own close button since there's no native title bar

---

## Reference Implementations

Study these real extensions for patterns:

- **sap-lx-music** — Static extension with MCP, transparent compact mode, dark/light theme, i18n, custom scheme invocation
- **sap-example** (heshengtao_sap-example) — Basic static chat UI extension
- **sap-example-with-node** (heshengtao_sap-example-with-node) — Node.js extension with Express backend

## Resources

### assets/
- `assets/static-template/` — Complete starter template for static extensions
- `assets/node-template/` — Complete starter template for Node.js extensions

### references/
- `references/package-json-spec.md` — Complete package.json field reference
- `references/node-entry-spec.md` — Node.js entry point and lifecycle specification
