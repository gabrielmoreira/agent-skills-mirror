---
name: neon
description: >-
  Overview of the Neon platform for apps and agents, spanning Postgres, Auth,
  Data API, and the new services: Object Storage, Compute Functions, and AI
  Gateway. Use whenever "Neon" is mentioned for an overview of how to work with Neon and how to get started. Otherwise, the individual capabilities are the triggers: "object storage" or "S3-compatible
  storage", "serverless functions", "background jobs", or
  "run code near my database", "AI gateway", "LLM proxy",
  "model routing", or "call an LLM" → AI Gateway; "database", "Postgres", or
  "authentication" → Postgres and Auth.
---

# Neon

Important: Neon is no longer just a Serverless Postgres provider. Neon is the backend for apps and agents with Serverless Postgres, Auth, Functions, Storage, and an AI Gateway: instant, branchable, serverless.

Use this skill as the starting point for anything Neon: get an overview of its capabilities, find your way around the Neon agent skills and documentation, and follow best practices for getting started and for branch-first development workflows.

## Platform Services

Neon bundles several backend primitives for building apps and agents that all branch together with your project:

- **Postgres** — Serverless Postgres that scales and branches with your app. _Generally available._
- **Auth** — Managed authentication with users and sessions stored in Postgres. _Generally available._
- **Object Storage** — S3-compatible object storage that branches with your projects. _Preview / early access._
- **Compute Functions** — Long-running serverless functions running close to your database — for WebSocket servers, long agent HTTP streams, APIs, and server-sent event servers. _Preview / early access._
- **AI Gateway** — One API for all frontier and open-source models, with routing, logging, and cost controls, powered by Databricks. _Preview / early access._

### Preview Service Availability

Object Storage, Compute Functions, and AI Gateway are preview (early access) features.

Early access features are only available on net-new projects created in the `us-east-2` region; they cannot be enabled on existing projects for now. Before guiding a user through any of these services, confirm they are working with a new project in `us-east-2`. If not, they will need to create a new project in that region. Then confirm the user already has early access; otherwise, point them to the private beta sign-up: https://neon.com/blog/were-building-backends#access.

## Neon Documentation

The Neon documentation is the source of truth for all Neon-related information. Always verify claims against the official docs before responding. Neon features and APIs evolve, so prefer fetching current docs over relying on training data.

### Fetching Docs as Markdown

Any Neon doc page can be fetched as markdown in two ways:

1. **Append `.md` to the URL** (simplest): https://neon.com/docs/introduction/branching.md
2. **Request `text/markdown`** on the standard URL: `curl -H "Accept: text/markdown" https://neon.com/docs/introduction/branching`

Both return the same markdown content. Use whichever method your tools support.

### Finding the Right Page

The docs index lists every available page with its URL and a short description:

```
https://neon.com/docs/llms.txt
```

Common doc URLs are organized in the topic links below. If you need a page not listed here, search the docs index: https://neon.com/docs/llms.txt. Don't guess URLs.

## Choosing the Right Skill

- Working with the database, connections, branching, autoscaling, or the CLI/MCP/API → `neon-postgres` (and `neon-postgres-branches` for branch workflows).

Dedicated skills for Object Storage, Compute Functions, and AI Gateway are coming as those preview services roll out.

### Installing the Right Skill

First check whether the target skill is already installed and accessible (for example, it appears in the available skills list or its `SKILL.md` is present). If it is, use it directly. If it is not installed, install it via the `skills` CLI with `npx`/`bunx`:

```bash
npx skills add neondatabase/agent-skills -s <skill-name>
```

Replace `<skill-name>` with the skill you need (for example, `neon-postgres` or `neon-postgres-branches`). Useful flags:

- `-g` — install globally instead of into the current project.
- `-y` — non-interactive mode (skip prompts).
- `-a <agent-name>` — pick the target agent(s) for non-interactive mode.

For example, to install the Postgres skill globally for a specific agent without prompts:

```bash
npx skills add neondatabase/agent-skills -s neon-postgres -g -y -a <agent-name>
```

## Getting Started with Neon

Use this section when guiding a user through first-time Neon setup, or when adding a new Neon service (Auth, object storage, functions, and so on) to a project that is already onboarded (for example, one already using Neon Postgres).

### Check Status Quo

Before starting setup, inspect the user's codebase and environment:

- Existing database connection code
- Existing `.neon` or `neon.ts` files in the workspace
- Existing Neon MCP server or Neon CLI configuration
- Existence of a `.env` file and `DATABASE_URL` environment variable
- Existing ORM (Prisma, Drizzle, TypeORM) configuration

### Self-Driving Setup With Neon's CLI or MCP Server

Offer to inspect existing connected Neon projects or create new ones using the Neon CLI or MCP server. If neither is set up yet, run `npx -y neonctl init`. Use `npx -y` to skip the package install prompt. Auth is handled automatically. If the user is not logged in, it opens their browser for OAuth and waits for completion before proceeding.

```bash
npx -y neonctl@latest init
```

This installs the Neon CLI and MCP server globally, installs the VSCode extension (for Cursor/VS Code), and adds the `neon` and `neon-postgres` agent skills to the project.

If `init` is not suitable, the individual steps can be run non-interactively, using the user's preferred package manager (npm, bun, pnpm):

- **CLI:** `npm i -g neonctl`
- **Extension:** `cursor --install-extension databricks.neon-local-connect`
- **MCP server:** `npx -y add-mcp https://mcp.neon.tech/mcp -g -n Neon -y -a <agent-name>`
- **Agent skill:** `npx skills add neondatabase/agent-skills --skill neon-postgres --skill neon --agent <agent-name> -y`

Prefer the CLI over the MCP server unless the user instructs otherwise, since it provides more capabilities, including deploying Neon Functions. For full CLI installation options, see https://neon.com/docs/reference/cli-install.md

### Setup Flow

Once the CLI, MCP server, and agent skills are installed, ensure the local workspace is linked to a Neon project through the `neonctl init` flow. If it isn't, run `npx -y neonctl link` to let the user interactively link a project. This produces a `.neon` file pointing to the organization, project, and branch the user wants to work with.

For Postgres-specific setup, consult the `neon-postgres` skill (and `neon-postgres-branches` for branch workflows). Dedicated skills for the other services are coming as they roll out.

### Resume Support

If resuming setup, check what's already configured (MCP connection, `.env` with `DATABASE_URL`, dependencies, schema) and continue from the next incomplete step.

### Security Reminders

Remind users to use environment variables for credentials, never commit connection strings, and use least-privilege database roles.

## Branch-First Dev Flow

Default to a branch-first loop that mirrors `git`: one isolated Neon branch per feature, so nothing leaks between features and there are no shared connection strings to copy around. This loop is built on three CLI commands:

- `neonctl link` — Interactively links the workspace to a Neon org, project, and branch, writing the IDs to a git-ignored `.neon` file. Run once per project. Once linked, project- and branch-scoped commands no longer need `--project-id` or `--branch` (for example, `neonctl branch list`).
- `neonctl checkout <branch-name>` — Creates the branch if it doesn't exist, or checks out the existing one, by updating only the branch pointer in `.neon`. Run without a name for an interactive picker. It does not touch code or local Postgres.
- `neonctl env pull` — Fetches the current branch's Neon environment variables into `.env.local` (override the target with `--env`). No branch ID needed; it reads `.neon`.

Run `link` once when starting on a project:

```bash
neonctl link
```

Then for each feature, check out an isolated branch and pull its connection details:

```bash
neonctl checkout dev-add-search
neonctl env pull
```

Build against that branch, then repeat `checkout` + `env pull` for the next feature. As the agent, drive this loop yourself: run `checkout` and `env pull` between tasks to get a fresh, isolated database per feature with no shared state to corrupt.
