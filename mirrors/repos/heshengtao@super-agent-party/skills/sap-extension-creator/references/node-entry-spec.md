# Node.js Entry Point & Lifecycle Specification

How SAP manages Node.js extension processes.

## Launch Protocol

SAP starts the extension with:

```bash
node index.js <port>
```

Where `<port>` is the assigned port number.

## Required index.js Structure

```js
const PORT = parseInt(process.argv[2], 10);
const express = require('express');
const path = require('path');
const EXT_DIR = __dirname;

const app = express();

// 1. Serve all static files from extension directory
app.use(express.static(EXT_DIR));

// 2. Root route returns index.html
app.get('/', (req, res) => res.sendFile(path.join(EXT_DIR, 'index.html')));

// 3. Health check endpoint (SAP polls this to confirm readiness)
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// 4. Add custom API routes here
// app.get('/api/data', (req, res) => { ... });
// app.post('/api/action', (req, res) => { ... });

// 5. Listen on assigned port at loopback only
app.listen(PORT, '127.0.0.1', () => {
    console.log(`[ext] Ready at http://127.0.0.1:${PORT}`);
});
```

## Lifecycle

```
npm install (if needed)
    ↓
node index.js <port>
    ↓
SAP polls /health until 200
    ↓
Extension is LIVE — SAP proxies requests
    ↓
On shutdown: SIGTERM → process terminates
```

## Port Assignment

- `nodePort: 0` in package.json → SAP auto-assigns from available pool (3100-13999)
- `nodePort: 3000` → SAP tries port 3000 first

## npm install

- SAP runs `npm install --production` only when:
  - `node_modules/` does not exist, OR
  - `package.json` is newer than `node_modules/`
- If `dependencies` is empty/absent, npm install is skipped

## Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `NODE_EXTENSION_ID` | ext_id string | The extension's ID |
| `ELECTRON_RUN_AS_NODE` | `"1"` | Set in Electron desktop mode only |
| `npm_config_registry` | mirror URL | Set when China proxy mode is enabled |

## Reverse Proxy

SAP proxies requests through:

```
/api/extensions/{ext_id}/node/{path}
```

The proxy forwards method, headers, body, and query params to `http://127.0.0.1:{port}/{path}`.

## MCP / AI Tool Registration

MCP tool registration is done in the **frontend** (`index.html`) via WebSocket, not in the Node.js backend. The `index.js` file handles:

- Static file serving
- Custom API routes (called by the frontend)
- Backend logic (DB queries, file processing, external API calls)

The frontend registers MCP tools via WebSocket and handles `call_mcp_tool` events. Those handlers can optionally call the Node.js backend API for server-side operations. See the main SKILL.md for MCP implementation details.

## Important Notes

- **Font Awesome**: Use CDN in `index.html` (`cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`). Relative paths like `../../fontawesome/` do NOT work because the extension is served from Express on a different port, not from SAP's static file directory.
- **Static assets**: Place all CSS/JS files in the extension root directory. Express serves them via `express.static(EXT_DIR)`, so they are accessible at the same path level as `index.html`.
- **API routes**: Express JSON body parsing is NOT included by default. Add `app.use(express.json())` if your API routes need JSON request bodies.

## Cleanup

- On SAP shutdown, all extension processes receive `terminate()` signal
- Extensions should handle `SIGTERM` for graceful cleanup
- Stale ports are reclaimed automatically
