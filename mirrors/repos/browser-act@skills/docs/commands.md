# Commands

Complete BrowserAct CLI command index. For detailed usage and context, see the relevant feature chapter.

## Global Options

| Option | Description |
|--------|-------------|
| `--session <name>` | Session name (required for browser interaction commands) |
| `--format text\|json` | Output format |
| `--no-auto-dialog` | Disable automatic dialog handling |
| `--version` | Show CLI version |

## Common Tasks

| I want to... | Use these commands | See |
|--------------|--------------------|-----|
| Extract content from a protected site | `stealth-extract` | [Anti-Blocking](anti-blocking.md) |
| Create an anti-scraping browser | `browser create --type stealth ...` | [Browser Modes](browser-modes.md) |
| Manage static proxies | `proxy list` / `proxy buy-request` | [Anti-Blocking](anti-blocking.md) |
| Open a page and interact | `browser open` → `state` → `click`/`input` | [Agent Design](agent-design.md) |
| Find the API behind a page | `network requests` → `network request <id>` | [Agent Design](agent-design.md) |
| Handle CAPTCHAs | `solve-captcha` → `remote-assist` | [Anti-Blocking](anti-blocking.md) / [Better Headless](headless.md) |
| Hand off when stuck | `remote-assist --objective "..."` | [Better Headless](headless.md) |
| Run multiple accounts in parallel | Multiple browsers, each with its own `--session` | [Concurrency](concurrency.md) |
| Reuse an existing login | `browser import-profile` | [Browser Modes](browser-modes.md) |

## Command Groups

### Browser Interaction (requires `--session`)

#### Navigation
```
navigate <url> [--new-tab]    back / forward / reload
```

#### Page State
```
state                          screenshot [path] [--full]
```

Index markers in `state` output:

- `[N]` — Index of an interactive element (used with `click N` / `input N "..."` etc.)
- `*[N]` — Element added or changed since the previous `state` call. The first call marks every element with `*`; later calls mark only the deltas, helping the agent focus on what's new.

#### Interaction
```
click <index>                  hover <index>
input <index> <text>           select <index> <option>
type <text>                    keys <key_combo>
scroll up|down [--amount]      scrollintoview --selector <css>
upload <index> <path>
```

#### Data Extraction
```
get title                      get html [--selector]
get text <index>               get value <index>
get markdown
```

#### JavaScript
```
eval <js> [--stdin]
```

#### Wait
```
wait stable [--timeout]
wait selector <index> --state visible|hidden|attached|detached [--timeout]
wait selector --selector <css> --state ...
```

#### Network
```
network requests [--filter] [--type] [--method] [--status] [--clear]
network request <request_id>
network clear
network offline on|off
network har start
network har stop [path]
```

#### Tab and Dialog
```
tab list                       tab switch <tab_id>             tab close [tab_id]
dialog accept [text]           dialog dismiss                   dialog status
```

#### Cookies
```
cookies get [--url]            cookies set <name> <value> [--domain] [--path] [--secure] [--http-only]
cookies clear [--url]          cookies export <file>            cookies import <file>
```

#### CAPTCHA and Remote Assist
```
solve-captcha                  captcha-aid
remote-assist [--objective]
```

### Browser Management (no `--session` required)

```
browser list
browser open <id> [url] [--headed] [--allow-restart-chrome]
browser create --type <chrome|chrome-direct|stealth> --name <n> --desc <d> [options]
browser update <id> [options]
browser delete <id>
browser regions
browser list-profiles
browser import-profile <browser_id> <profile_id> [--allow-restart-chrome]
```

#### `browser create` Options
```bash
browser-act browser create \
  --type chrome|chrome-direct|stealth \
  --name "my-browser" \
  --desc "purpose description" \
  --source-profile <profile_id> \    # chrome only
  --dynamic-proxy <region> \         # stealth only
  --static-proxy <proxy_id> \        # stealth only
  --custom-proxy <url> \             # stealth only
  --private true|false \             # stealth only
  --confirm-before-use
```

#### `browser update` Options
```bash
browser-act browser update <id> \
  --name "new name" \
  --desc "overwrite description" \
  --desc-append "append to description" \
  --dynamic-proxy <region> \
  --static-proxy <proxy_id> \
  --custom-proxy <url> \
  --no-proxy \
  --private true|false \
  --confirm-before-use|--no-confirm-before-use
```

### Session Management

```
session list                   session close [name]
```

### Stealth Extract (standalone, no session required)

```bash
browser-act stealth-extract <url>
browser-act stealth-extract <url> --content-type html|markdown
browser-act stealth-extract <url> --dynamic-proxy <region>
browser-act stealth-extract <url> --static-proxy <proxy_id>
browser-act stealth-extract <url> --custom-proxy <proxy-url>
browser-act stealth-extract <url> --timeout 60
browser-act stealth-extract <url> --output ./result.md
```

### Authentication

```
auth login                     auth poll
auth set <api_key>             auth clear
```

### Proxy Management

```
proxy list                     proxy regions
proxy buy-request              proxy buy-status --request-id <id>
proxy rename <proxy_id> "<name>"
```

### Skill and System

```
get-skills core --skill-version <v>
get-skills advanced
get-skills main
report-log
feedback <message>
```

## Next Steps

- [Agent Design](agent-design.md) — Design philosophy and typical use behind the commands
- [Quick Start](quick-start.md) — Combine commands into working flows
