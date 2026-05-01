---
type: skill
lifecycle: stable
inheritance: inheritable
name: "vscode-extension-patterns"
description: Reusable patterns for VS Code extension development.
tier: standard
applyTo: '**/*vscode*,**/*extension*,**/*patterns*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# VS Code Extension Patterns


> Reusable patterns for VS Code extension development.
> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

**Last validated:** March 2026 (VS Code 1.111+)

---

## Webview Dashboard

```typescript
const [health, knowledge] = await Promise.all([checkHealth(), getKnowledgeSummary()]);
panel.webview.html = await getWebviewContent(health, knowledge);
```

---

## TreeDataProvider for Sidebar

```typescript
class WelcomeViewProvider implements vscode.WebviewViewProvider {
  resolveWebviewView(view: vscode.WebviewView) {
    view.webview.options = { enableScripts: true };
    view.webview.html = this.getHtmlContent();
    view.webview.onDidReceiveMessage(async (msg) => {
      if (msg.command === "refresh") await this.refresh();
    });
  }
}
vscode.window.registerWebviewViewProvider("my.welcomeView", new WelcomeViewProvider());
```

---

## CSP-Compliant Webview Events

**Problem**: Inline `onclick` handlers violate CSP.

**Solution**: Use `data-cmd` with delegated listener:

```html
<button data-cmd="play">Play</button>
```

```javascript
document.addEventListener("click", (e) => {
  const cmd = e.target.closest("[data-cmd]")?.getAttribute("data-cmd");
  if (cmd === "play") audio.play();
});
```

**CSP header** (required when `enableScripts: true`):

```typescript
const nonce = crypto.randomUUID();
const csp = `default-src 'none'; script-src 'nonce-${nonce}'; style-src 'unsafe-inline';`;
return `<html><head><meta http-equiv="Content-Security-Policy" content="${csp}"></head>...`;
```

---

## Agent Hooks (1.111+)

Shell scripts at lifecycle points. Config: `.github/hooks.json`.

| Event | When | Use Cases |
|-------|------|-----------|
| `SessionStart` | Chat begins | Load context, set persona |
| `PreToolUse` | Before tool | Safety blocks, sanitization |
| `PostToolUse` | After tool | Logging, compile reminders |
| `Stop` | Session ends | Metrics, commit reminders |

```json
{
  "hooks": {
    "SessionStart": [{ "steps": [{ "hooks": [
      { "type": "command", "command": ".github/muscles/hooks/start.cjs", "timeout": 10 }
    ]}]}]
  }
}
```

**PreToolUse decisions**: `allow`, `deny` (exit 2), or `updatedInput` (modify params).

---

## Configuration Patterns

```typescript
// Safe config access with defaults
function getSetting<T>(key: string, fallback: T): T {
  return vscode.workspace.getConfiguration("myext").get<T>(key, fallback);
}

// Listen for changes
vscode.workspace.onDidChangeConfiguration(e => {
  if (e.affectsConfiguration("myext.feature")) refreshUI();
});
```

---

## SecretStorage for Tokens

**Never store secrets in settings** — use `context.secrets`:

```typescript
let cachedToken: string | null = null;

export async function initSecrets(ctx: vscode.ExtensionContext) {
  cachedToken = await ctx.secrets.get("myext.token") || null;
  // Migration from settings
  const old = vscode.workspace.getConfiguration("myext").get<string>("token");
  if (old && !cachedToken) {
    await ctx.secrets.store("myext.token", old);
    cachedToken = old;
  }
}

export function getToken(): string | null { return cachedToken; }
```

---

## Webview Sandbox

Webviews cannot access VS Code APIs directly. Communication via `postMessage`:

```typescript
// Extension
webview.postMessage({ type: "update", data });

// Webview
window.addEventListener("message", (e) => {
  if (e.data.type === "update") renderData(e.data.data);
});

// Webview → Extension
vscode.postMessage({ command: "save", payload });
```

---

## Telemetry Opt-Out

```typescript
if (vscode.env.isTelemetryEnabled) sendTelemetry(event);
```

Always check before sending. Respect user settings.

---

## Portability Rules

1. Use `vscode.Uri.joinPath()` — not string concatenation
2. Use `vscode.workspace.fs` — not Node `fs`
3. Use `path.posix.join()` for URI paths
4. Normalize paths: `uri.fsPath` for filesystem, `uri.toString()` for display

---

## Publishing Workflow

1. `npm run compile` — build
2. `npx vsce package --no-dependencies` — create VSIX
3. `npx vsce publish --packagePath <vsix>` — publish

**Pre-publish**: Verify VSCE_PAT not expired, all tests pass.

---

## Testing: Debug vs Rebuild

| Change | Method |
|--------|--------|
| TS logic | F5 (debug) |
| package.json (commands, settings) | Rebuild + reload |
| Webview HTML/CSS | Reload webview |
| activationEvents | Rebuild + restart |

---

## Asset Optimization

**Problem**: Large images inflate extension size.

```javascript
// Resize to max dimension
const sharp = require('sharp');
await sharp(input).resize(768, 768, { fit: 'inside' }).toFile(output);
```

the AI assistant extension: 553MB → 33MB (94% reduction).

---

## TDZ in Production Builds

**Problem**: esbuild minifies + hoists, causing `Cannot access 'X' before initialization`.

**Bad**:

```typescript
const handlers = { click: () => config.value };  // config hoisted below
const config = { value: 42 };
```

**Good**:

```typescript
const config = { value: 42 };  // Define before use
const handlers = { click: () => config.value };
```

---

## Agent Platform (1.109+)

| Setting | Purpose |
|---------|---------|
| `chat.agent.enabled` | Enable custom agents |
| `chat.agentSkillsLocations` | Auto-load skills |
| `chat.useAgentsMdFile` | Load AGENTS.md |
| `chat.hooks.enabled` | Lifecycle hooks |

**Agent file** (`.github/agents/my.agent.md`):

```yaml
---
name: "MyAgent"
description: "Specialized agent"
---
Instructions here.
```

**Chat participant**:

```typescript
vscode.chat.createChatParticipant("myext.agent", async (req, ctx, stream) => {
  stream.markdown("Hello!");
});
```

**Tool registration**:

```typescript
vscode.lm.registerTool("myext-search", {
  async invoke(opts) {
    return new vscode.LanguageModelToolResult([
      new vscode.LanguageModelTextPart(JSON.stringify(results))
    ]);
  }
});
```

---

## Integration Audit Checklist

| # | Category | Check |
|---|----------|-------|
| 1 | Activation | `activationEvents` match actual needs |
| 2 | Context | `subscriptions`, `secrets`, `globalState` |
| 3 | Disposables | All pushed to subscriptions |
| 4 | Commands | package.json matches registerCommand |
| 5 | Configuration | getConfiguration, onDidChangeConfiguration |
| 6 | Webview Security | CSP, nonce, enableScripts |
| 7 | LM/Chat | vscode.lm patterns, tool registration |
| 8 | Telemetry | isTelemetryEnabled respected |
| 9 | Error Handling | try/catch patterns |
| 10 | File System | vscode.workspace.fs vs Node fs |

**Scoring**: 45-50 Excellent, 40-44 Good, 35-39 Fair, <35 Needs Work
