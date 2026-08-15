---
name: page-agent
description: "Embeds alibaba/page-agent as an in-page GUI agent (DOM-as-text, OpenAI-compatible LLM) so end users drive a site with natural language. Use when adding an NL copilot inside a SaaS/admin app or evaluating page-agent against Ollama, Qwen, OpenAI, or OpenRouter. Not for an agent driving a browser from outside (Playwright/Browserbase) or screenshot/multimodal grounding. Never ship the demo CDN LLM proxy to production."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, javascript, agent, browser, gui, alibaba, embed, copilot, saas]
    category: web-development
---

# page-agent

`alibaba/page-agent` (https://github.com/alibaba/page-agent, 17k+ stars, MIT) is an in-page GUI agent written in TypeScript. It lives inside a webpage, reads the DOM as text (no screenshots, no multi-modal LLM), and executes natural-language instructions like "click the login button, then fill username as John" against the current page. Pure client-side — the host site includes a script and passes an OpenAI-compatible LLM endpoint.

## When to Use

Load this skill when a user wants to:

1. **Ship an AI copilot inside their own web app** (SaaS, admin panel, B2B tool, ERP, CRM) — e.g., "users on my dashboard should be able to type 'create invoice for Acme Corp and email it' instead of clicking through five screens."
2. **Modernize a legacy web app** without rewriting the frontend — page-agent drops on top of existing DOM.
3. **Add accessibility via natural language** — voice / screen-reader users drive the UI by describing what they want.
4. **Demo or evaluate page-agent** against a local (Ollama) or hosted (Qwen, OpenAI, OpenRouter) LLM.
5. **Build interactive training / product demos** — let an AI walk a user through "how to submit an expense report" live in the real UI.

### When NOT to use

- User wants **the agent itself to drive a browser** → use a built-in browser tool (Browserbase / Camofox). page-agent is the *opposite* direction: it runs *inside* the page.
- User wants **cross-tab automation without embedding** → use Playwright, browser-use, or the page-agent Chrome extension.
- User needs **visual grounding / screenshots** → page-agent is text-DOM only; use a multimodal browser agent instead.

## Prerequisites

- **Node 22.13+ or 24+**, npm 10+ (docs claim 11+ but npm 10.9 works fine).
- An **OpenAI-compatible LLM endpoint**: Qwen (DashScope), OpenAI, Ollama, OpenRouter, or anything speaking `/v1/chat/completions`.
- Browser with devtools (for debugging).
- On Windows, use PowerShell for all `npm` / `git` commands below. Paths like `~\project` are standard; no WSL required.

## Procedure

### Path 1 — 30-second demo via CDN (no install)

Fastest way to see it work. Uses alibaba's free testing LLM proxy — **for evaluation only**, subject to their terms.

1. Add the following `<script>` tag to any HTML page (or paste the bookmarklet into the devtools console):

```html
<script src="https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js" crossorigin="true"></script>
```

2. A floating panel appears. Type an instruction (e.g., "click the Login link"). Done.

**Bookmarklet form** (drop into bookmarks bar, click on any page):

```javascript
javascript:(function(){var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js';document.head.appendChild(s);})();
```

### Path 2 — npm install into your own web app (production use)

1. Inside an existing web project (React / Vue / Svelte / plain), install the package:

```bash
npm install page-agent
```

2. Wire it up with your own LLM endpoint — **never ship the demo CDN to real users**:

```javascript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    apiKey: process.env.LLM_API_KEY,   // never hardcode
    language: 'en-US',
})

// Show the panel for end users:
agent.panel.show()

// Or drive it programmatically:
await agent.execute('Click submit button, then fill username as John')
```

3. Choose your provider (any OpenAI-compatible endpoint works):

| Provider | `baseURL` | `model` |
|----------|-----------|---------|
| Qwen / DashScope | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen3.5-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Ollama (local) | `http://localhost:11434/v1` | `qwen3:14b` |
| OpenRouter | `https://openrouter.ai/api/v1` | `anthropic/claude-sonnet-4.6` |

4. **Key config fields** (passed to `new PageAgent({...})`):
   - `model`, `baseURL`, `apiKey` — LLM connection
   - `language` — UI language (`en-US`, `zh-CN`, etc.)
   - Allowlist and data-masking hooks exist for locking down what the agent can touch — see https://alibaba.github.io/page-agent/ for the full option list

5. **Security hardening for production:** Don't put your `apiKey` in client-side code for a real deployment — proxy LLM calls through your backend and point `baseURL` at your proxy. The demo CDN exists because alibaba runs that proxy for evaluation.

### Path 3 — clone the source repo (contributing or hacking on it)

Use this when the user wants to modify page-agent itself, test it against arbitrary sites via a local IIFE bundle, or develop the browser extension.

1. Clone and install:

```bash
git clone https://github.com/alibaba/page-agent.git
cd page-agent
npm ci              # exact lockfile install (or `npm i` to allow updates)
```

2. Create `.env` in the repo root with an LLM endpoint. Example (cloud):

```
LLM_MODEL_NAME=gpt-4o-mini
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1
```

Ollama flavor:

```
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=NA
LLM_MODEL_NAME=qwen3:14b
```

3. Common commands:

```bash
npm start           # docs/website dev server
npm run build       # build every package
npm run dev:demo    # serve IIFE bundle at http://localhost:5174/page-agent.demo.js
npm run dev:ext     # develop the browser extension (WXT + React)
npm run build:ext   # build the extension
```

4. **Test on any website** using the local IIFE bundle. Add this bookmarklet:

```javascript
javascript:(function(){var s=document.createElement('script');s.src=`http://localhost:5174/page-agent.demo.js?t=${Math.random()}`;s.onload=()=>console.log('PageAgent ready!');document.head.appendChild(s);})();
```

5. Run `npm run dev:demo`, click the bookmarklet on any page, and the local build injects. Auto-rebuilds on save.

> **HARD RULE — dev bundle key exposure:** Your `.env` `LLM_API_KEY` is inlined into the IIFE bundle during dev builds. Don't share the bundle. Don't commit it. Don't paste the URL into Slack. (Verified: grepping the public dev bundle returns the literal values from `.env`.)

### Repo layout (Path 3)

Monorepo with npm workspaces. Key packages:

| Package | Path | Purpose |
|---------|------|---------|
| `page-agent` | `packages/page-agent/` | Main entry with UI panel |
| `@page-agent/core` | `packages/core/` | Core agent logic, no UI |
| `@page-agent/mcp` | `packages/mcp/` | MCP server (beta) |
| — | `packages/llms/` | LLM client |
| — | `packages/page-controller/` | DOM ops + visual feedback |
| — | `packages/ui/` | Panel + i18n |
| — | `packages/extension/` | Chrome/Firefox extension |
| — | `packages/website/` | Docs + landing site |

## Pitfalls

1. **Demo CDN in production — don't.** It's rate-limited, uses alibaba's free proxy, and their terms forbid production use.
2. **API key exposure** — any key passed to `new PageAgent({apiKey: ...})` ships in your JS bundle. Always proxy through your own backend for real deployments.
3. **Non-OpenAI-compatible endpoints** fail silently or with cryptic errors. If your provider needs native Anthropic/Gemini formatting, use an OpenAI-compatibility proxy (LiteLLM, OpenRouter) in front.
4. **CSP blocks** — sites with strict Content-Security-Policy may refuse to load the CDN script or disallow inline eval. In that case, self-host from your origin.
5. **Restart dev server** after editing `.env` in Path 3 — Vite only reads env at startup.
6. **Node version** — the repo declares `^22.13.0 || >=24`. Node 20 will fail `npm ci` with engine errors.
7. **npm 10 vs 11** — docs say npm 11+; npm 10.9 actually works fine.
8. **Dev bundle leaks `.env` values** — see HARD RULE above. Never distribute the dev IIFE bundle publicly.

## Verification

### After Path 1 or Path 2

1. Open the page in a browser with devtools open.
2. You should see a floating panel. If not, check the console for errors (most common: CORS on the LLM endpoint, wrong `baseURL`, or a bad API key).
3. Type a simple instruction matching something visible on the page (e.g., "click the Login link").
4. Watch the Network tab — you should see a request to your `baseURL`.

### After Path 3

1. `npm run dev:demo` prints `Accepting connections at http://localhost:5174`.
2. Verify the bundle is served:

```bash
curl -I http://localhost:5174/page-agent.demo.js
```

Expected output: `HTTP/1.1 200 OK` with `Content-Type: application/javascript`.

3. Click the bookmarklet on any site; panel appears.

## Reference

- Repo: https://github.com/alibaba/page-agent
- Docs: https://alibaba.github.io/page-agent/
- License: MIT (built on browser-use's DOM processing internals, Copyright 2024 Gregor Zunic)
