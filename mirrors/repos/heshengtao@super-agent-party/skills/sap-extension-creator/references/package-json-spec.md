# package.json Field Reference

Complete reference for Super Agent Party extension `package.json`.

## All Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | ✅ | — | Extension display name |
| `version` | string | ✅ | `"1.0.0"` | Semantic version |
| `description` | string | — | `"无描述"` | Short description |
| `author` | string | — | `"未知"` | Author name |
| `systemPrompt` | string | — | `""` | Custom system prompt injected for this extension |
| `repository` | string | — | `""` | GitHub/GitLab repo URL (for updates) |
| `backupRepository` | string | — | `""` | Backup repo (e.g., Gitee), used when GitHub unreachable |
| `category` | string | — | `""` | Category for plugin marketplace |
| `transparent` | boolean | — | `false` | Whether the extension window is transparent |
| `width` | number | — | `800` | Default window width |
| `height` | number | — | `600` | Default window height |
| `enableVrmWindowSize` | boolean | — | `false` | Enable VRM-based window sizing |

## Node.js Specific Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `main` | string | ✅ | `"index.js"` | Node.js entry point |
| `nodePort` | number | — | `0` | Preferred port; `0` = auto-assign |
| `dependencies` | object | ✅ | — | npm dependencies map |

## Transparent Window Configuration

When `transparent: true`, SAP creates a **frameless, transparent, always-on-top** window. This is ideal for:

- Mini music controllers (e.g., sap-lx-music)
- Floating chat input bars
- Overlay widgets
- Desktop companion panels

### How It Works

From Electron's `main.js` (`open-extension-window` handler):

```js
if (extension.transparent) {
  windowConfig = {
    frame: false,           // No title bar / window chrome
    transparent: true,      // See-through background
    alwaysOnTop: true,      // Stay above other windows
    skipTaskbar: false,     // Still appears in taskbar
    hasShadow: false,       // No window shadow
    backgroundColor: 'rgba(0, 0, 0, 0)',  // Fully transparent
  };
}
```

### Requirements for Transparent Extensions

The extension's `index.html` MUST implement:

1. **Compact mode CSS** — detect small window size and switch layout (see template)
2. **`-webkit-app-region: drag`** — on header/footer so the frameless window can be moved
3. **`-webkit-app-region: no-drag`** — on all interactive elements (buttons, inputs, select, a, .compact-close-btn) so they remain clickable
4. **Custom close button** — since there's no native title bar, the extension must provide its own close button

### Typical Transparent Extension package.json

```json
{
  "name": "my-widget",
  "version": "1.0.0",
  "description": "A floating mini widget",
  "author": "your-name",
  "repository": "https://github.com/user/my-widget",
  "category": "Utility",
  "transparent": true,
  "width": 280,
  "height": 80
}
```

Note the small dimensions (280×80) — transparent extensions typically use compact sizes for overlay/panel use.

## Window Size & Responsive Design

The `width` and `height` fields define the **default** window size, but users can resize windows. Extensions should:

1. Work well at any size from ~200px to full screen
2. Use responsive CSS with breakpoints at 900px and 600px (see templates)
3. Hide non-essential elements at small sizes
4. Use `vw` units and flex layouts for fluid sizing

### Size Recommendations

| Extension Type | Typical width | Typical height | `transparent` |
|---------------|---------------|----------------|---------------|
| Full chat UI | 800–1000 | 600–800 | false |
| Mini widget / controller | 260–320 | 60–100 | true |
| Dashboard panel | 600–800 | 400–600 | false |
| Tool popup | 400–500 | 300–500 | false |

## MCP / AI Tool Registration

Both static and Node.js extensions can register AI tools via WebSocket using `register_node_extension_mcp`. The message type name is historical ("node" in the name) but works for any extension:

```js
ws.send(JSON.stringify({
  type: 'register_node_extension_mcp',
  data: {
    ext_id: extId,
    tools: [/* ... */]
  }
}));
```

This is done in the frontend (index.html), not in the Node.js backend. The backend (index.js) is only for server-side API routes.

## Font Awesome

Use CDN for reliable loading in both static and Node.js modes:

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

Avoid relative paths like `../../fontawesome/css/all.min.css` — they may work for static extensions (served from SAP's static directory) but break for Node.js extensions (served from Express on a different path).

## Theme & i18n

All extensions should implement:
- **Dark/Light mode** via CSS variables on `:root` and `body.dark`, persisted to localStorage
- **Chinese/English i18n** with a language toggle, also persisted to localStorage

Each extension defines its own theme colors (do NOT hardcode SAP's colors). See the templates for complete implementations.

## Examples

### Static Extension

```json
{
  "name": "sap-example",
  "version": "1.0.0",
  "description": "A chat frontend example",
  "author": "your-name",
  "systemPrompt": "你是一个智能助手",
  "repository": "https://github.com/user/sap-example",
  "backupRepository": "https://gitee.com/user/sap-example",
  "category": "Example"
}
```

### Node.js Extension

```json
{
  "name": "my-node-extension",
  "version": "1.0.0",
  "description": "Full-stack extension with Express",
  "author": "your-name",
  "systemPrompt": "你是一个智能助手",
  "repository": "https://github.com/user/my-node-extension",
  "backupRepository": "https://gitee.com/user/my-node-extension",
  "category": "Tools",
  "main": "index.js",
  "nodePort": 0,
  "dependencies": {
    "express": "^5.1.0"
  }
}
```

### Transparent Mini Widget (e.g., Music Controller)

```json
{
  "name": "sap-lx-music",
  "version": "1.0.0",
  "description": "Music player controller overlay",
  "author": "your-name",
  "repository": "https://github.com/user/sap-lx-music",
  "backupRepository": "https://gitee.com/user/sap-lx-music",
  "category": "Utility",
  "transparent": true,
  "width": 280,
  "height": 80
}
```

## How SAP Uses package.json

1. **Install**: SAP reads `dependencies` and runs `npm install --production`
2. **Tool registration**: `systemPrompt` is injected into the AI context
3. **Updates**: `repository` and `backupRepository` are used to pull new versions
4. **Marketplace**: `name`, `description`, `author`, `category` appear in the plugin list
5. **Window creation**: `width`, `height`, `transparent` control how `BrowserWindow` is created (see `main.js` `open-extension-window`)
6. **VRM sizing**: When `enableVrmWindowSize: true`, the window may be dynamically resized by VRM data
