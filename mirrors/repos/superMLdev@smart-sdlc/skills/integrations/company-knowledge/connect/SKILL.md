---
name: company-knowledge-connect
description: "Register company-internal knowledge sources (internal frameworks, platform docs, Spring Boot wrappers, etc.) accessible via URL or MCP server. Use when the user says 'add company docs', 'register internal framework', 'connect knowledge source', or 'add company knowledge'."
---

# Company Knowledge — Connect a Knowledge Source

## Goal

Register one or more company-internal knowledge sources so AI agents can fetch examples, documentation, and guidelines directly in chat — without needing to leave the IDE.

Examples of what this covers:
- Internal Spring Boot wrapper / platform library docs
- Company-specific framework guidelines and examples
- Internal API catalogs or developer portals
- Architecture decision records hosted on an internal server
- Design system component libraries

Sources can be fetched in two ways:
- **Direct URL** — HTTP endpoint returning JSON, Markdown, HTML, or plain text
- **MCP Server** — a company-hosted or npm-based MCP server exposing knowledge as tools

---

## Security Check First

Confirm `_superml/config.yml` is in `.gitignore`:
```bash
cat {project-root}/.gitignore | grep _superml
```

If not present: `echo "_superml/config.yml" >> {project-root}/.gitignore`

⏸️ **STOP** — confirm before collecting any internal URLs or tokens.

---

## Step 1: How Many Sources?

Ask:
> "How many company knowledge sources would you like to register? (you can add more later)"

Then for each source, run Steps 2–4.

---

## Step 2: Name and Describe the Source

Ask:
1. **Short name** (used in config and skill commands): e.g., `spring-platform`, `design-system`, `internal-api-catalog`
2. **Display name**: e.g., `Company Spring Boot Platform`
3. **Description** (one line — what it contains): e.g., `Internal Spring Boot wrapper with custom starters, annotations, and security modules`
4. **Which personas use this most?**
   - `all` — every persona (default)
   - Specific roles: `architect`, `developer`, `modernization`, `product`, `team_lead`

---

## Step 3: Choose Access Method

Ask:
> "How is this knowledge source accessed?
> 1. **Direct URL** — HTTP endpoint you can call to get docs or examples
> 2. **MCP Server** — a company-hosted or npm-based MCP server
>
> Which? (1 or 2)"

### Path A: Direct URL

Ask:
1. **Base URL**: the root endpoint (e.g., `https://internal-dev-portal.corp/api/docs`)
2. **Auth type**: None / Bearer token / Basic auth / Custom header
   - If Bearer: ask for token
   - If Basic: ask for username + password
   - If Custom: ask for header name and value
3. **Response format**: JSON / Markdown / HTML / Plain text
4. **Notes for AI** (optional): e.g., "Append `?format=markdown` to get Markdown output" or "Use the `?component={name}` param to fetch specific component docs"

Test the endpoint:
```bash
curl -s {auth_flags} "{base_url}" | head -50
```

Show the first 50 lines and ask: "Does this look right? (y/n)"

⏸️ **STOP** — confirm before saving.

Save to config:
```yaml
company_knowledge:
  sources:
    - key: "{short_name}"
      name: "{display_name}"
      description: "{description}"
      personas: [{personas_list}]   # all | architect | developer | etc.
      access:
        type: url
        base_url: "{base_url}"
        auth:
          type: "{none | bearer | basic | header}"
          token: "{token_if_bearer}"           # omit if not bearer
          username: "{username_if_basic}"      # omit if not basic
          password: "{password_if_basic}"      # omit if not basic
          header_name: "{name_if_custom}"      # omit if not custom
          header_value: "{value_if_custom}"    # omit if not custom
        response_format: "{json | markdown | html | text}"
        notes: "{ai_usage_notes_if_any}"
```

### Path B: MCP Server

Ask:
1. **MCP server type**:
   - `npm_package` — runs locally via npx
   - `url` — hosted MCP endpoint (HTTP or SSE)
   - `command` — arbitrary shell command that speaks MCP

2. **Server name** (key in `.vscode/mcp.json`): e.g., `company-docs`

**If `npm_package`:**

Ask:
- Package name: e.g., `@corp/knowledge-mcp-server`
- Any env vars needed (name + value pairs)

Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "{server_name}": {
      "command": "npx",
      "args": ["-y", "{package_name}"],
      "env": {
        "{ENV_VAR_NAME}": "{env_var_value}"
      }
    }
  }
}
```

**If `url`:**

Ask:
- MCP endpoint URL
- Auth header (if any)

Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "{server_name}": {
      "url": "{mcp_url}",
      "headers": {
        "{auth_header}": "{auth_value}"
      }
    }
  }
}
```

**If `command`:**

Ask:
- Full command string (e.g., `/usr/local/bin/corp-mcp-server`)
- Any args
- Any env vars

⚠️ **Security**: `.vscode/mcp.json` may contain credentials:
```bash
echo ".vscode/mcp.json" >> {project-root}/.gitignore
```

Test the MCP server:
> "In a Copilot chat, type: `@{server_name} help` or ask it to describe available tools.
> Confirm it responds with tool descriptions."

⏸️ **STOP** — confirm test passed.

Save to config:
```yaml
company_knowledge:
  sources:
    - key: "{short_name}"
      name: "{display_name}"
      description: "{description}"
      personas: [{personas_list}]
      access:
        type: mcp
        server_name: "{server_name}"   # matches key in .vscode/mcp.json
        notes: "{any_usage_notes}"
```

---

## Step 4: Add More Sources?

Ask: "Would you like to add another knowledge source? (y/n)"

If yes, repeat Steps 2–4 and append to `company_knowledge.sources[]`.

---

## Step 5: Confirm and Summary

Show all registered sources:

```
✅ Company Knowledge sources registered:

  1. {display_name}  [{short_name}]
     Access: {url | mcp}  — {base_url or server_name}
     Personas: {all | list}
     Description: {description}

  2. ...

Use `/company-knowledge-fetch` to pull a source into your AI context.
```

Remind the user to run `npx @supermldev/smart-sdlc init` again if they want these sources available in the `/sml-help` skill index, **or** simply add the source config entries to `_superml/config.yml` manually.
