---
name: company-knowledge-fetch
description: "Fetch internal company documentation, framework examples, or platform guidelines into the current AI context. Use when the user says 'fetch company docs', 'load framework docs', 'get examples from internal docs', 'show me the Spring Boot platform docs', or 'use company knowledge'."
argument-hint: "optional: source key or topic — e.g. 'spring-platform', 'design-system auth component', 'internal API catalog'"
---

# Company Knowledge — Fetch Into Context

## Goal

Pull documentation, examples, or guidelines from a registered company knowledge source into the current conversation so you can reason over it, generate code from it, or answer questions about it.

---

## Step 1: Read Config Silently

Read `#file:_superml/config.yml` silently.

Check for `company_knowledge.sources[]`. If the array is empty or missing:
> "No company knowledge sources are registered yet.
> Run `company-knowledge-connect` to add your first source."

---

## Step 2: Identify the Source

If the user specified a source key or topic in the argument, match it against `company_knowledge.sources[].key` or `company_knowledge.sources[].name`.

If no argument was given, or no match found, show the available sources:

```
Available company knowledge sources:

  {i}. {display_name}  [{key}]
       {description}
       Access: {url | mcp}

Which source would you like to fetch? (enter number or key)
```

⏸️ **STOP** — wait for the user to select a source.

---

## Step 3: Fetch Based on Access Type

Read `sources[selected].access.type`.

### If `type: url`

**A. Ask what to fetch** (if the user hasn't already specified a topic):

> "What would you like to fetch from {display_name}?
> (e.g., 'getting started', 'security module', 'auth annotations', 'all examples', or leave blank to load the root endpoint)"

**B. Construct the URL**

Use `access.base_url` plus any query params or path segments from the user's topic. Apply the `notes` hint if present (e.g., append `?format=markdown`).

**C. Fetch the content**

```bash
curl -s {auth_flags} "{constructed_url}"
```

Where `{auth_flags}` depends on `access.auth.type`:
- `none` → no flags
- `bearer` → `-H "Authorization: Bearer {token}"`
- `basic` → `-u "{username}:{password}"`
- `header` → `-H "{header_name}: {header_value}"`

**D. Format for context**

- If `response_format: json` → parse and summarise key fields, then quote full JSON
- If `response_format: markdown` → render as Markdown
- If `response_format: html` → extract text (strip tags), render as plain text
- If `response_format: text` → render as-is

If the response is large (>200 lines), summarise the top-level structure first, then ask:
> "This source is {n} lines long. Should I load it all, or focus on a specific section?"

### If `type: mcp`

**A. Ask what to fetch** (if not specified):

> "What would you like to know from {display_name}?
> (e.g., 'show examples for auth module', 'list available components', 'how to use {ComponentName}')"

**B. Use MCP tool calls**

Address the server using its `server_name` from config. Example prompts to use (adapt based on user's question):

- `@{server_name} get documentation for {topic}`
- `@{server_name} show examples for {topic}`
- `@{server_name} list available modules`
- `@{server_name} search {topic}`

If the MCP server name is unknown or the tools aren't responding, suggest:
> "Check that `{server_name}` is listed in `.vscode/mcp.json` and the server is running.
> You can verify with `@{server_name} help`."

---

## Step 4: Summarise What Was Loaded

After fetching, briefly summarise what is now in context:

```
📚 Loaded: {display_name}
   Source: {url or mcp:server_name}
   Topic: {fetched_topic_or_root}
   Content: {n} lines / {n} sections / {brief description}

You can now ask questions about this content, generate code based on it,
or reference it in other skills. For example:
  - "Generate a Spring Boot service using the platform starter pattern"
  - "What annotations does the internal security module provide?"
  - "Show me an example of {framework_concept} from these docs"
```

---

## Step 5: Offer Next Actions

Suggest what the user can do with the loaded knowledge:

> "What would you like to do with this?
> 1. Generate code following these conventions
> 2. Answer a question about this content
> 3. Compare this with the existing codebase
> 4. Add examples to a story or architecture doc
> 5. Fetch a different topic from the same source"

Proceed with whichever the user selects, or free-form if they ask directly.

---

## Notes for AI

- When using URL sources, never log or display Bearer tokens or passwords — only show the constructed URL with auth headers redacted (e.g., `Authorization: Bearer ***`).
- When content is proprietary (marked with `internal` or `confidential` in the response), do not paste it verbatim into git-tracked files. Use it only for AI reasoning in the current session.
- If a URL returns an error (4xx/5xx), show the status code, suggest checking auth config, and offer to re-run `company-knowledge-connect` to update credentials.
