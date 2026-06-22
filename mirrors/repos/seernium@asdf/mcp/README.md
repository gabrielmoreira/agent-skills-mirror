# Secure DevTools MCP Server

A comprehensive, production-grade Model Context Protocol (MCP) server providing development, debugging, browser inspection, and screenshot tools, built with **strict security mitigations** and **strict TypeScript**.

## Key Features

- **Browser Navigation:** Click, type, hover, select, scroll, and reload.
- **DOM & Page Inspection:** Extract DOM elements, console logs, network requests, cookies, local storage, session storage, and performance metrics.
- **Headless Screenshots:** Take full-page or element-specific screenshots (PNG, JPEG, WebP).
- **Safe File System Access:** Read, write, search, copy, delete, and list directory contents.
- **Safe Terminal Execution:** Run lint checks, typecheck, test suites, builds, and custom developer scripts.
- **Utilities:** UUID generation, hashing, port checking, and HTTP health checks.

---

## Security Architecture & Mitigations

This MCP server is designed to be **safe to use** in automated environments by preventing directory traversal, arbitrary command execution, and local file exposure.

### 1. Path Traversal Protection
All filesystem tools (`file_read`, `file_write`, `file_search`, `file_delete`, `file_info`, `file_list_dir`, `file_copy`) are sandboxed to the project workspace root. 
- Paths are fully resolved and normalized using `path.resolve` and `path.normalize`.
- Any paths resolving outside the project root (such as absolute system directories like `C:\Windows` or directory traversals like `../../`) are instantly blocked and return an `Access Denied` error.

### 2. Strict Command Whitelisting
The custom command execution tool (`exec_run`) only runs commands against a strict whitelist of safe development binaries:
- `pnpm`, `npm`, `npx`, `git`, `vitest`, `eslint`, `tsc`
- **Shell Injection Blocker:** Commands containing chaining or redirection characters (`;`, `&`, `|`, `$`, `(`, `)`, `>`, `<`, `\n`, `\r`, `` ` ``) are immediately rejected.

### 3. Protocol Isolation for Browser & Health Checks
Browser navigation (`browse_navigate`) and HTTP health checks (`exec_health_check`) strictly require the URL to use `http:` or `https:` protocols.
- Access to local resources via `file://`, `data://`, or internal browser resources like `chrome://` is completely disabled to prevent exposing sensitive environment files.

---

## Installation & Build

### Prerequisites
- Node.js v22 (LTS)
- npm or pnpm package manager

### 1. Install Dependencies
Navigate to the `mcp/` directory and run:
```bash
npm install
```
*(If `pnpm` is available in your shell, you can use `pnpm install` instead).*

### 2. Build the Server
Compile the TypeScript source code to JavaScript ES Modules:
```bash
npm run build
```

---

## Configuration

To register the DevTools server with your MCP-capable client:

### 1. Claude Code
Add the server definition to your `.claude/mcp.json` configuration file:

```json
{
  "mcpServers": {
    "devtools": {
      "command": "node",
      "args": ["mcp/build/index.js"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 2. Cursor / VS Code
Add to your VS Code MCP settings file (typically `.vscode/mcp.json` or global configuration):

```json
{
  "servers": {
    "devtools": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp/build/index.js"]
    }
  }
}
```

---

## Tools Reference

### 1. Browser Navigation

| Tool | Description | Parameters |
|---|---|---|
| `browse_navigate` | Navigate to an HTTP/HTTPS URL | `url` (string, required), `timeout` (number) |
| `browse_click` | Click on a CSS selector element | `selector` (string, required) |
| `browse_type` | Type text into an input field | `selector` (string, required), `content` (string, required) |
| `browse_select` | Select a dropdown option by value | `selector` (string, required), `value` (string, required) |
| `browse_hover` | Hover over an element | `selector` (string, required) |
| `browse_scroll` | Scroll page by X and Y pixels | `x` (number), `y` (number) |
| `browse_go_back` | Navigate back in history | — |
| `browse_go_forward`| Navigate forward in history | — |
| `browse_reload` | Reload the current page | — |

### 2. Inspection

| Tool | Description | Parameters |
|---|---|---|
| `inspect_dom` | Get HTML DOM content (whole page or element) | `selector` (string), `includeAttributes` (boolean) |
| `inspect_element` | Get dimensions, position, classes, and text | `selector` (string, required) |
| `inspect_console_logs` | Retrieve console logs captured in memory | `clearAfter` (boolean, default: true) |
| `inspect_network_requests` | Retrieve network requests captured in memory | `resourceTypes` (array of strings), `limit` (number) |
| `inspect_cookies` | Get cookies for the active page | — |
| `inspect_local_storage` | Get localStorage data | — |
| `inspect_session_storage` | Get sessionStorage data | — |
| `inspect_metrics` | Get performance metrics and node counts | — |

### 3. Screenshots

| Tool | Description | Parameters |
|---|---|---|
| `screenshot_page` | Capture screenshot of page or selector | `selector` (string), `format` (`png`/`jpeg`/`webp`), `quality` (number), `fullPage` (boolean) |
| `screenshot_element` | Capture screenshot of a specific selector | `selector` (string, required), `format` (`png`/`jpeg`/`webp`) |

*Screenshots are saved inside the `mcp/screenshots/` workspace folder.*

### 4. File System (Workspace Sandboxed)

| Tool | Description | Parameters |
|---|---|---|
| `file_read` | Read content of a workspace file | `filePath` (string, required) |
| `file_write` | Write text content to a workspace file | `filePath` (string, required), `content` (string, required) |
| `file_search` | Search files matching a glob pattern | `pattern` (string, required), `basePath` (string) |
| `file_delete` | Delete file/directory inside workspace | `filePath` (string, required), `recursive` (boolean) |
| `file_info` | Get file metadata (size, dates, permissions) | `filePath` (string, required) |
| `file_list_dir` | List files and directories in path | `filePath` (string, required), `recursive` (boolean) |
| `file_copy` | Copy file from source to destination | `source` (string, required), `destination` (string, required) |

### 5. Debugging & Development

| Tool | Description | Parameters |
|---|---|---|
| `debug_lint` | Run ESLint check on file/folder | `filePath` (string, required), `fix` (boolean) |
| `debug_typecheck` | Run tsc type checking | `filePath` (string), `strict` (boolean) |
| `debug_audit` | Scan project dependencies for vulns | `cwd` (string) |
| `debug_run_tests` | Execute Vitest suites | `filePath` (string), `watch` (boolean), `coverage` (boolean) |
| `debug_build` | Run project build scripts | `cwd` (string) |

### 6. Execution & Utilities

| Tool | Description | Parameters |
|---|---|---|
| `exec_run` | Run whitelisted terminal command | `command` (string, required), `cwd` (string), `timeout` (number) |
| `exec_evaluate_javascript` | Evaluate JS code inside page context | `content` (string, required) |
| `exec_check_port` | Check process using specified port (OS agnostic) | `port` (number, required) |
| `exec_health_check` | Health check http endpoint | `endpoint` (string, required), `timeout` (number) |
| `util_wait` | Sleep execution for 100ms - 60000ms | `ms` (number, required) |
| `util_generate_id` | Generate a UUID v4 | — |
| `util_hash` | Hash a string (md5, sha1, sha256, sha512) | `content` (string, required), `algorithm` (string) |

---

## Exposed Resources

The server exposes three read-only resources dynamically synchronized with your current browser state:

1. `devtools://screenshots/latest` - Returns the base64-encoded bytes of the most recent PNG screenshot.
2. `devtools://console/logs` - Returns all captured browser console logs in structured JSON.
3. `devtools://page/dom` - Returns the raw HTML DOM string of the active browser page.

---

## Usage Example

### 1. Browser Automation Flow
1. Navigate to a server running locally:
   ```json
   { "url": "http://localhost:3000" }
   ```
2. Retrieve the page performance metrics:
   ```json
   {}
   ```
3. Type login credentials:
   ```json
   { "selector": "#username-field", "content": "admin_user" }
   ```
4. Click submit:
   ```json
   { "selector": "button[type='submit']" }
   ```
5. Capture a full scroll screenshot:
   ```json
   { "fullPage": true, "format": "png" }
   ```

### 2. Security Rejection Sample
An attempt to execute:
```json
{
  "command": "cat /etc/passwd",
  "cwd": "."
}
```
will fail with:
`Access denied: Command binary 'cat' is not in the whitelist. Allowed: pnpm, npm, npx, git, vitest, eslint, tsc`
