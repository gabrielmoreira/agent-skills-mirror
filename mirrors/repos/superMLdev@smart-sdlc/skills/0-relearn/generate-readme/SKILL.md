---
name: generate-readme
description: "Generate a complete, accurate README.md for an existing project by reading the actual code — not guessing. Use when the project has no README, an outdated README, or a minimal README that needs to be expanded."
---

# Generate README

Generate a comprehensive, accurate README.md by reading the codebase directly.

## When to Use

- Project has no README
- README says "TODO" or is mostly empty
- README describes a different version of the project
- User says "create docs", "write a README", "document how to run this"

## Strategy

**Read in this order:**
1. `package.json` / `pyproject.toml` / `go.mod` — name, description, scripts, version
2. `.env.example` — required environment variables
3. `docker-compose.yml` — service dependencies (database, cache, etc.)
4. Main entry point — to understand what the server actually does
5. Existing README if present — extract anything still accurate, discard the rest

**Do NOT invent:**
- Configuration instructions not found in config files
- Features not visible in code
- Commands not in package.json scripts or Makefile

## Output: README.md

```markdown
# {project_name}

{1–3 sentences. What does this do? Who uses it? Answer from: package.json description, 
main entry point purpose, route definitions.}

## Features

{Extract from: route files, service files, package description. Only list confirmed features.}

- Feature 1
- Feature 2

## Tech Stack

| Layer       | Technology              |
|-------------|------------------------|
| Runtime     | {Node 20 / Python 3.12} |
| Framework   | {Express / FastAPI}     |
| Database    | {PostgreSQL via Prisma} |
| Cache       | {Redis}                 |

## Prerequisites

{List only what's actually required based on config files found}

- {Node.js ≥ 20}
- {Docker and Docker Compose (for local database)}
- {PostgreSQL 14+ (if no docker-compose)}

## Quick Start

```bash
# 1. Clone
git clone {repo-url}
cd {project-name}

# 2. Install dependencies
{exact command from package.json "install" or standard for language}

# 3. Configure environment
cp .env.example .env
# Open .env and fill in required values (see below)

# 4. Start dependencies
{docker compose up -d   ← if docker-compose.yml exists}

# 5. Run migrations
{exact command from package.json scripts or migration tool config}

# 6. Start
{exact dev command from package.json / Makefile / pyproject.toml}
```

Server starts at: `http://localhost:{PORT}` ← read from .env.example or default

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
{For each variable in .env.example}

## Running Tests

```bash
{exact test command}
```

## Project Structure

```
{Top-level directory listing with one-line descriptions}
```

## API Overview

{If routes were found: brief list of resource groups. Link to full API_REFERENCE.md if present.}

## Contributing

{CONTRIBUTING.md summary if found. Otherwise: "Open a pull request."}

## License

{From LICENSE file or package.json "license" field. If not found: "License not specified."}
```

## Handling Missing Information

If a required piece of information cannot be found in the code:
- Write `<!-- TODO: {what is needed} -->` as a comment in the README
- List all TODOs at the end before saving so the user knows what to fill in

## Output Location

Default: `{project-root}/README.md`

If one already exists:
- Read it first
- Keep sections that are still accurate
- Replace or extend sections that are wrong or missing
- Add a note at the top: `> Last updated by Scout on {date}.`

⏸️ **STOP before writing** — show a draft outline and ask for confirmation: "Here's what I'll include. Anything to add or remove?"
