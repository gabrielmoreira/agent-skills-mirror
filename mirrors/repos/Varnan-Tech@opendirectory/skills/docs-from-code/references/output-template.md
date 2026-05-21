# Output Templates

Use these templates when generating documentation. Fill in real content from the extracted code metadata. Never invent function signatures or examples.

---

## Template 1: README.md

Use when the project has no README, or when asked to generate a fresh one.

```markdown
# [Project Name]

[1-2 sentence description of what this project does. Derived from package.json description or the main entry file's module docstring.]

## Installation

```bash
# Clone the repo
git clone <repo-url>
cd <project-name>

# Install dependencies
npm install        # or: pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values
```

## Quick Start

```[language]
[Minimal working example derived from the entry point or test files]
```

## API Reference

[Generated from routes — see API Reference template below]

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| [from .env.example or config files] | | |

## Scripts

| Command | Description |
|---------|-------------|
[from package.json scripts or Makefile]

## License

[from package.json or LICENSE file]
```

---

## Template 2: API Reference (docs/API.md)

Use for projects with HTTP routes. One entry per route.

```markdown
# API Reference

Base URL: `https://api.yourdomain.com`

Authentication: [describe auth method if detected: Bearer token, API key header, etc.]

---

## [Resource Name]

### [METHOD] [/path]

[Description from JSDoc or docstring if available; otherwise inferred from function name]

**Request**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| [from function params, Zod schema, or Pydantic model] | | | |

**Request Body** (if POST/PUT/PATCH)

```json
{
  [derived from type definitions, Pydantic model, or Zod schema]
}
```

**Response**

```json
{
  [derived from return type or response model]
}
```

**Example**

```bash
curl -X [METHOD] https://api.yourdomain.com[/path] \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[request body if applicable]'
```

---
```

---

## Template 3: README Update (Sections Only)

Use when README already exists and only specific sections need updating.
Identify which sections are stale (missing routes, outdated function signatures) and regenerate only those. Preserve the rest verbatim.

Sections commonly stale after code changes:
- `## API Reference` — when routes are added or changed
- `## Configuration` — when new env vars are added
- `## Installation` — when dependencies change
- `## Quick Start` — when the entry point changes

---

## Rules for Filling Templates

1. Document only exported functions and public routes. Skip private or internal helpers.
2. Every code example must be runnable. If you cannot produce a real working example, write `[TODO: add example]` rather than inventing fake code.
3. Route descriptions come from JSDoc or docstrings. If none exist, infer from the function or handler name only. Do not make up behaviour.
4. Types come from the extraction output. Do not guess or invent type signatures.
5. Keep descriptions factual. "Creates a user and returns the new record" is good. "Seamlessly manages your user lifecycle" is bad.
6. Flag missing information explicitly. If a route has no docstring and an unclear name, write `[Description needed]` rather than hallucinating.
