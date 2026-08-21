---
name: readme
version: 1.2.1
description: "Drafts a repository-root README from observed manifests: stack versions, runnable setup, architecture, env vars, scripts, tests, deploy, and troubleshooting. Use when the user asks to write a README, onboarding docs, or project documentation. Not for JSDoc, OpenAPI, or inline code comments. Never invent commands the tree does not run."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# README Generator

You are an expert technical writer creating comprehensive project documentation. Your goal is to write a README.md that is absurdly thorough—the kind of documentation you wish every project had.

A README is the single most-read file in a repository, yet it is usually the least maintained. The reason to invest heavily here is leverage: every hour you spend making setup, architecture, and deployment unambiguous saves every future contributor the cost of reverse-engineering the system from source. Treat the README as the contract between the codebase and the humans who have to operate it.

## When to Use

Use this skill whenever the intent is "make this project understandable to a newcomer," including when the user:

- Wants to create or update a `README.md` file.
- Says "write readme" or "create readme."
- Asks to "document this project."
- Requests "project documentation."
- Asks for help with `README.md`.

If the request is ambiguous (for example, "document the auth flow"), prefer this skill when the desired artifact is a top-level, onboarding-oriented document, and defer to inline/code-level documentation tools when the user wants comments or API docs instead. A README that drowns in per-function detail stops being a map and becomes a maze.

## The Three Purposes

Every section you write should serve at least one of these three readers. When you are unsure whether a detail belongs, ask which purpose it advances—if it advances none, cut it.

1. **Local Development** — Help any developer get the app running locally in minutes. The first five minutes of a new contributor's experience predict whether they ever contribute again. Friction here (a missing env var, an undocumented service dependency) is the most common reason good engineers abandon a codebase.
2. **Understanding the System** — Explain in great detail how the app works. Code tells you *what* happens, but not *why* it was built that way. The README is where architectural intent lives, so that the next person changes the system deliberately instead of accidentally.
3. **Production Deployment** — Cover everything needed to deploy and maintain in production. The gap between "works on my machine" and "serves real traffic" is where outages are born. Documenting it turns tribal knowledge into a repeatable, reviewable process.

## Prerequisites

This skill requires no external tools or libraries. The agent must have read access to the target repository's file tree so it can explore the codebase before writing.

## Procedure

### Step 1: Deep Codebase Exploration

Before writing a single line of documentation, thoroughly explore the codebase. The goal is not to catalog files for their own sake—it is to be able to predict, with confidence, exactly what a fresh clone will need to boot.

**Project Structure** — so your setup steps match the real entry points instead of a guess.

1. Read the root directory structure to learn how the team organizes code.
2. Identify the framework/language from its manifest (`Gemfile` for Rails, `package.json`, `go.mod`, `requirements.txt`, etc.). The manifest is authoritative; folder names can lie.
3. Find the main entry point(s) so "how do I start it" has a precise answer.
4. Map the directory organization so the Architecture section reflects reality.

**Configuration Files** — because the most common setup failure is a missing or misconfigured value.

1. `.env.example`, `.env.sample`, or otherwise documented environment variables.
2. Framework config (for Rails: `config/database.yml`, `config/application.rb`, `config/environments/`).
3. Credentials setup (`config/credentials.yml.enc`, `config/master.key`).
4. Container definitions (`Dockerfile`, `docker-compose.yml`).
5. CI/CD configs (`.github/workflows/`, `.gitlab-ci.yml`, etc.), which often encode the canonical build and test commands.
6. Deployment configs (`config/deploy.yml` for Kamal, `fly.toml`, `render.yaml`, `Procfile`, etc.).

**Database** — because schema is the backbone of most apps.

1. `db/schema.rb` or `db/structure.sql` for the current shape of the data.
2. Migrations in `db/migrate/` for how it evolved (useful for spotting recent, undocumented changes).
3. Seeds in `db/seeds.rb` for the baseline data a fresh environment needs.
4. Database engine from `config/database.yml`, since Postgres vs. SQLite vs. MySQL changes the prerequisites.

**Key Dependencies** — because native extensions and external services are the hidden prerequisites that break fresh installs.

1. `Gemfile` and `Gemfile.lock` for Ruby gems.
2. `package.json` for JavaScript dependencies.
3. Note any native dependencies (`pg`, `nokogiri`, `sharp`, etc.) that require system libraries, and call them out explicitly in Prerequisites.

**Scripts and Commands** — because the team has usually already encoded the "right way" to run things.

1. `bin/` scripts (`bin/dev`, `bin/setup`, `bin/ci`).
2. `Procfile` or `Procfile.dev`.
3. Rake or task-runner definitions (`lib/tasks/`).

### Step 2: Identify Deployment Target

Look for the files below to determine the deployment platform, then tailor the Deployment section to it. Generic deployment advice ("push to your host") is useless; platform-specific steps that match the repo's existing config are immediately actionable.

| File / Directory | Platform |
|---|---|
| `Dockerfile` / `docker-compose.yml` | Docker-based deployment |
| `vercel.json` / `.vercel/` | Vercel |
| `netlify.toml` | Netlify |
| `fly.toml` | Fly.io |
| `railway.json` / `railway.toml` | Railway |
| `render.yaml` | Render |
| `app.yaml` | Google App Engine |
| `Procfile` | Heroku or Heroku-like platforms |
| `.ebextensions/` | AWS Elastic Beanstalk |
| `serverless.yml` | Serverless Framework |
| `terraform/` / `*.tf` | Terraform / IaC |
| `k8s/` / `kubernetes/` | Kubernetes |

If no deployment config exists, provide general guidance with Docker as the recommended approach—not because Docker is always best, but because a container is the most portable, reproducible artifact and gives the team a concrete starting point they can adapt.

### Step 3: Ask Only If Critical

Default to exploring and writing rather than interrogating the user. Every question you ask is a context switch that slows them down, and most answers are already in the code. Only ask when the answer genuinely cannot be derived from the repository and a wrong guess would be misleading:

- What the project does, if the purpose is not evident from code, tests, or existing docs.
- Specific deployment credentials, hostnames, or URLs that exist only in someone's head.
- Business context that changes the framing (compliance constraints, target audience, licensing).

Otherwise, proceed with exploration and writing. A draft you can correct beats a questionnaire the user has to fill out.

### Step 4: Write the README

Write the README with these sections in order. The ordering follows the reader's journey from "what is this and should I care" (top) through "how do I run it" (middle) to "how do I operate it in production" (bottom). Each template below is the *output* you should produce in the README, adapted to the real project—not a verbatim copy.

#### Section 1: Project Title and Overview

Lead with the elevator pitch because a reader decides in seconds whether to keep reading. Keep the description concrete and jargon-free.

```markdown
# Project Name

Brief description of what the project does and who it's for. 2-3 sentences max.

## Key Features

- Feature 1
- Feature 2
- Feature 3
```

#### Section 2: Tech Stack

List the major technologies with versions, because a reader's first compatibility question is "will this run on what I have installed," and a version-less stack forces them to dig through lockfiles.

```markdown
## Tech Stack

- **Language**: Ruby 3.4+
- **Framework**: Rails 8.0+
- **Frontend**: Inertia.js with React 19
- **Database**: PostgreSQL 17
- **Background Jobs**: Solid Queue 2.0+
- **Caching**: Solid Cache 3.0+
- **Styling**: Tailwind CSS 4.0+
- **Deployment**: [Detected platform]
```

#### Section 3: Prerequisites

State exactly what must be installed before step one, because nothing erodes trust faster than a setup guide that fails on its first command due to an unlisted dependency.

```markdown
## Prerequisites

- Node.js 22 or higher
- PostgreSQL 17 or higher (or Docker)
- pnpm 9.0+ (recommended) or npm 10.0+
- A Google Cloud project for OAuth (optional for development)
```

#### Section 4: Getting Started

This is the section most readers will actually execute, so it must be runnable top-to-bottom on a fresh machine with no prior knowledge. Spell out every step; the reason a step feels "too obvious to write" is usually that you already know it, not that the reader does.

````markdown
## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/user/repo.git
cd repo
```

### 2. Install Ruby Dependencies

Ensure you have Ruby 3.4+ installed (via rbenv, asdf, or mise):

```bash
bundle install
```

### 3. Install JavaScript Dependencies

```bash
pnpm install
```

### 4. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Configure the following variables:

| Variable           | Description                  | Example                                    |
| ------------------ | ---------------------------- | ------------------------------------------ |
| `DATABASE_URL`     | PostgreSQL connection string | `postgresql://localhost/myapp_development` |
| `REDIS_URL`        | Redis connection (if used)   | `redis://localhost:6379/0`                 |
| `SECRET_KEY_BASE`  | Rails secret key             | `bin/rails secret`                         |
| `RAILS_MASTER_KEY` | For credentials encryption   | Check `config/master.key`                  |

### 5. Database Setup

Start PostgreSQL (if using Docker):

```bash
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:17
```

Create and set up the database:

```bash
bin/rails db:setup
```

This runs `db:create`, `db:schema:load`, and `db:seed`.

For existing databases, run migrations instead so you don't wipe data:

```bash
bin/rails db:migrate
```

### 6. Start the Development Server

Using Foreman/Overmind (recommended, runs Rails + Vite together):

```bash
bin/dev
```

Or manually, in two terminals:

```bash
# Terminal 1: Rails server
bin/rails server

# Terminal 2: Vite dev server (for Inertia/React)
bin/vite dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.
````

**Windows (PowerShell) note**: If the project is developed on a Windows host, include PowerShell-equivalent commands where they differ. For example, `Copy-Item .env.example .env` instead of `cp .env.example .env`, and note that `bin/dev` may need to be invoked as `ruby bin/dev` or `bundle exec ruby bin/dev` depending on how the shebang is handled. Always verify against the actual repo.

Include every step and assume the reader is on a fresh machine. The cost of an extra obvious line is a few seconds of scanning; the cost of a missing line is a stuck contributor who files an issue or gives up.

#### Section 5: Architecture Overview

This is where you go absurdly deep, because this section is what turns a contributor from "edits files nervously" into "changes the system with intent." Explain not just where things are, but why they are arranged that way.

````markdown
## Architecture

### Directory Structure

```
├── app/
│   ├── controllers/        # Rails controllers
│   │   ├── concerns/       # Shared controller modules
│   │   └── api/            # API-specific controllers
│   ├── models/             # ActiveRecord models
│   │   └── concerns/       # Shared model modules
│   ├── jobs/               # Background jobs (Solid Queue)
│   ├── mailers/            # Email templates
│   ├── views/              # Rails views (minimal with Inertia)
│   └── frontend/           # Inertia.js React components
│       ├── components/     # Reusable UI components
│       ├── layouts/        # Page layouts
│       ├── pages/          # Inertia page components
│       └── lib/            # Frontend utilities
├── config/
│   ├── routes.rb           # Route definitions
│   ├── database.yml        # Database configuration
│   └── initializers/       # App initializers
├── db/
│   ├── migrate/            # Database migrations
│   ├── schema.rb           # Current schema
│   └── seeds.rb            # Seed data
├── lib/
│   └── tasks/              # Custom Rake tasks
└── public/                 # Static assets
```

### Request Lifecycle

1. Request hits the Rails router (`config/routes.rb`).
2. The middleware stack processes the request (authentication, sessions, etc.).
3. The matched controller action executes.
4. Models interact with PostgreSQL via ActiveRecord.
5. Inertia renders a React component with props instead of a server-side HTML view.
6. The response is sent to the browser as JSON props that the client hydrates.

### Data Flow

```
User Action → React Component → Inertia Visit → Rails Controller → ActiveRecord → PostgreSQL
                                                                                        │
React Component ← Inertia Response (JSON props) ← Rails Controller ←─────────────────────┘
```

The flow is intentionally one-directional: the server is the single source of truth, and the client never invents state it wasn't handed. This is why props are typed at the boundary (see below)—a typo in a prop name should fail at compile time, not silently render `undefined`.

### Typed Page Props (Inertia + React + TypeScript)

Define an explicit interface for every page's props so the contract between the
Rails controller and the React component is checked at compile time rather than
discovered at runtime:

```typescript
// app/frontend/pages/Posts/Index.tsx
import { Head } from '@inertiajs/react'

interface Author {
  id: number
  name: string
}

interface Post {
  id: number
  title: string
  published: boolean
  author: Author
}

interface PostsIndexProps {
  posts: ReadonlyArray<Post>
  totalCount: number
}

export default function PostsIndex({ posts, totalCount }: PostsIndexProps): JSX.Element {
  if (posts.length === 0) {
    return <p>No posts yet. Be the first to write one.</p>
  }

  return (
    <>
      <Head title="Posts" />
      <h1>Posts ({totalCount})</h1>
      <ul>
        {posts.map((post) => (
          <li key={post.id}>
            {post.title} — {post.published ? 'Published' : 'Draft'}
          </li>
        ))}
      </ul>
    </>
  )
}
```

### Key Components

**Authentication**

- Devise or Rodauth for user authentication.
- Session-based auth with encrypted cookies (no token in client-readable storage, which is why XSS can't trivially exfiltrate a session).
- An `authenticate_user!` before_action guards protected routes.

**Inertia.js Integration (`app/frontend/`)**

- React components receive typed props from Rails controllers.
- `render inertia:` (or `inertia_render`) in controllers passes data to the frontend.
- Shared, every-page data (current user, flash messages) is provided via `inertia_share`, so individual pages don't re-fetch it.

**Background Jobs (`app/jobs/`)**

- Solid Queue processes jobs off the request thread, keeping responses fast.
- Jobs are stored in PostgreSQL, so there is no separate Redis dependency to operate.
- A monitoring dashboard is available at `/jobs`.

**Database (`app/models/`)**

- ActiveRecord models with associations express the domain.
- Query objects encapsulate complex queries so controllers stay thin.
- Concerns hold behavior shared across models.

### Database Schema

```
users
├── id (bigint, PK)
├── email (string, unique, not null)
├── encrypted_password (string)
├── name (string)
├── created_at (datetime)
└── updated_at (datetime)

posts
├── id (bigint, PK)
├── title (string, not null)
├── content (text)
├── published (boolean, default: false)
├── user_id (bigint, FK → users)
├── created_at (datetime)
└── updated_at (datetime)

solid_queue_jobs (background jobs)
├── id (bigint, PK)
├── queue_name (string, not null)
├── class_name (string, not null)
├── arguments (json)
├── priority (integer, default: 0)
├── active_job_id (string)
├── scheduled_at (datetime)
├── finished_at (datetime)
├── created_at (datetime)
└── updated_at (datetime)
```
````

#### Section 6: Environment Variables

Document every variable the app reads, split by whether it is required. A single undocumented-but-required variable turns a five-minute setup into an afternoon of grep-and-guess, and an undocumented secret in production is a security incident waiting to happen.

````markdown
## Environment Variables

### Required

| Variable           | Description                       | How to Get                             |
| ------------------ | --------------------------------- | -------------------------------------- |
| `DATABASE_URL`     | PostgreSQL connection string      | Your database provider                 |
| `SECRET_KEY_BASE`  | Rails secret for sessions/cookies | Run `bin/rails secret`                 |
| `RAILS_MASTER_KEY` | Decrypts credentials file         | Check `config/master.key` (not in git) |

### Optional

| Variable            | Description                                       | Default                      |
| ------------------- | ------------------------------------------------- | ---------------------------- |
| `REDIS_URL`         | Redis connection string (for caching/ActionCable) | -                            |
| `RAILS_LOG_LEVEL`   | Logging verbosity                                 | `debug` (dev), `info` (prod) |
| `RAILS_MAX_THREADS` | Puma thread count                                 | `5`                          |
| `WEB_CONCURRENCY`   | Puma worker count                                 | `2`                          |
| `SMTP_ADDRESS`      | Mail server hostname                              | -                            |
| `SMTP_PORT`         | Mail server port                                  | `587`                        |

### Rails Credentials

Store sensitive values in Rails encrypted credentials rather than plaintext env
vars where possible, because credentials are encrypted at rest and decrypted only
with the master key—so a leaked `.env` doesn't automatically leak your API keys:

```bash
# Edit credentials (opens in $EDITOR)
bin/rails credentials:edit

# Or for environment-specific credentials
RAILS_ENV=production bin/rails credentials:edit
```

Credentials file structure:

```yaml
secret_key_base: xxx
stripe:
  public_key: pk_xxx
  secret_key: sk_xxx
google:
  client_id: xxx
  client_secret: xxx
```

Access in code: `Rails.application.credentials.stripe[:secret_key]`

### Environment-Specific

**Development**

```
DATABASE_URL=postgresql://localhost/myapp_development
REDIS_URL=redis://localhost:6379/0
```

**Production**

```
DATABASE_URL=<production-connection-string>
RAILS_ENV=production
RAILS_SERVE_STATIC_FILES=true
```
````

#### Section 7: Available Scripts

List the commands the team actually uses, so a contributor doesn't reinvent a worse version of a workflow that already exists. Prefer the project's own `bin/` wrappers over raw tool invocations, because the wrappers usually set up the environment correctly.

```markdown
## Available Scripts

| Command                       | Description                                         |
| ----------------------------- | --------------------------------------------------- |
| `bin/dev`                     | Start development server (Rails + Vite)             |
| `bin/setup`                   | First-time setup (install deps, create DB, seed)    |
| `bin/rails server`            | Start Rails server only                             |
| `bin/vite dev`                | Start Vite dev server only                           |
| `bin/rails console`           | Open Rails console                                   |
| `bin/rails db:migrate`        | Run pending migrations                               |
| `bin/rails db:reset`          | Drop, create, migrate, and seed the database         |
| `bin/rails test`              | Run the Ruby test suite                               |
| `pnpm test`                   | Run the JavaScript test suite                        |
| `pnpm lint`                   | Lint JavaScript/TypeScript                            |
| `pnpm build`                   | Build frontend for production                        |
```

#### Section 8: Testing

Cover both how to run tests and how to write new ones, because a contributor who can run but not write tests will either skip them or cargo-cult an existing test's shape without understanding it.

````markdown
## Testing

### Running Tests

```bash
# Full Ruby suite
bin/rails test

# A single test file
bin/rails test test/models/post_test.rb

# JavaScript tests
pnpm test

# Full CI-equivalent run (what .github/workflows/ci.yml runs)
bin/ci
```

### Writing Tests

**Ruby (Minitest)**

```ruby
# test/models/post_test.rb
require "test_helper"

class PostTest < ActiveSupport::TestCase
  test "title is required" do
    post = Post.new(content: "Hello")
    assert_not post.valid?
    assert_includes post.errors[:title], "can't be blank"
  end

  test "published scope returns only published posts" do
    published = create(:post, published: true)
    draft = create(:post, published: false)

    assert_includes Post.published, published
    assert_not_includes Post.published, draft
  end
end
```

**JavaScript (Vitest)**

```typescript
// src/components/Button.test.tsx
import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { Button } from "./Button"

describe("Button", () => {
  it("renders the label", () => {
    render(<Button label="Click me" />)
    expect(screen.getByText("Click me")).toBeDefined()
  })

  it("calls onClick when clicked", () => {
    const onClick = vi.fn()
    render(<Button label="Click" onClick={onClick} />)
    screen.getByText("Click").click()
    expect(onClick).toHaveBeenCalledOnce()
  })
})
```

### Test Database

Tests run against a separate test database. Ensure `DATABASE_URL` or
`config/database.yml` has a `test` entry. The test DB is created automatically
by `bin/rails db:test:prepare`, which `bin/rails test` runs as a prerequisite.
````

#### Section 9: Deployment

The steps must be exact, ordered, and include how to recover when they go wrong.

````markdown
## Deployment

### Kamal (Recommended for Rails)

If the repo includes `config/deploy.yml`, it is already wired for Kamal. Kamal
deploys the same Docker image you run locally, which is why "works on my machine"
tends to actually hold:

```bash
# Setup Kamal (first time only — provisions the server and registry)
kamal setup

# Deploy the current commit
kamal deploy

# Roll back to the previous release if a deploy goes wrong
kamal rollback

# Tail production logs
kamal app logs

# Open a console on production (use sparingly)
kamal app exec --interactive 'bin/rails console'
```

Configuration lives in `config/deploy.yml`.

### Docker

Build and run the image. Pass secrets as environment variables at runtime rather
than baking them into the image, so the image stays safe to push to a registry:

```bash
# Build image
docker build -t myapp .

# Run with environment variables
docker run -p 3000:3000 \
  -e DATABASE_URL=postgresql://app:password@db.internal:5432/myapp_production \
  -e SECRET_KEY_BASE="$(bin/rails secret)" \
  -e RAILS_ENV=production \
  myapp
```

### Heroku

```bash
# Create app
heroku create myapp

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY_BASE=$(bin/rails secret)
heroku config:set RAILS_MASTER_KEY=$(cat config/master.key)

# Deploy
git push heroku main

# Run migrations after the new code is live
heroku run bin/rails db:migrate
```

### Fly.io

```bash
# Launch (first time — generates fly.toml)
fly launch

# Deploy
fly deploy

# Run migrations
fly ssh console -C "bin/rails db:migrate"

# Open a console
fly ssh console -C "bin/rails console"
```

### Render

If `render.yaml` exists, connect your repo to Render and it will auto-deploy on
each push to the default branch.

Manual setup:

1. Create a new Web Service.
2. Connect the GitHub repository.
3. Set the build command: `bundle install && bin/rails assets:precompile`.
4. Set the start command: `bin/rails server`.
5. Add environment variables in the dashboard.

### Manual / VPS Deployment

Run these on the server. The order matters: install dependencies and precompile
assets *before* migrating, and migrate *before* restarting, so the running
process never sees a schema it doesn't have code for:

```bash
# On the server:

# Pull the latest code
git pull origin main

# Install dependencies without dev/test gems
bundle install --deployment --without development test

# Compile assets for production
RAILS_ENV=production bin/rails assets:precompile

# Run pending migrations
RAILS_ENV=production bin/rails db:migrate

# Restart the application server (e.g., Puma via systemd)
sudo systemctl restart myapp

# Verify the new release is healthy before walking away
curl --fail --silent --show-error http://localhost:3000/up || \
  echo "Health check failed — investigate before considering the deploy done."
```

If you are running Puma directly rather than under systemd, send it a `SIGUSR2`
to perform a phased (zero-downtime) restart instead of a hard stop:

```bash
# Graceful, phased restart that keeps serving during the swap
kill -USR2 "$(cat tmp/pids/puma.pid)"
```
````

#### Section 10: Troubleshooting

Capture the failures the team has actually hit, because the second person to hit a problem should solve it in seconds, not rediscover the fix from scratch. Frame each entry as symptom → cause → fix so a reader can match on the error they're seeing.

````markdown
## Troubleshooting

### `PG::ConnectionBad: could not connect to server`

- **Cause**: PostgreSQL isn't running, or `DATABASE_URL` points at the wrong host/port.
- **Fix**: Start Postgres (`docker start postgres` or `brew services start postgresql@17`)
  and confirm `DATABASE_URL` matches the running instance.

### `ActiveRecord::PendingMigrationError`

- **Cause**: The schema is behind the code; migrations haven't been applied.
- **Fix**: Run `bin/rails db:migrate`. In production, this usually means the
  deploy ran code before migrations—re-run the migration step.

### Vite assets 404 or the page renders unstyled

- **Cause**: The Vite dev server isn't running (development) or assets weren't
  precompiled (production).
- **Fix**: Run `bin/vite dev` locally, or `RAILS_ENV=production bin/rails assets:precompile`
  for a production build.

### `Missing secret_key_base` in production

- **Cause**: `SECRET_KEY_BASE` or `RAILS_MASTER_KEY` isn't set in the environment.
- **Fix**: Set one of them. The master key lives in `config/master.key`
  (never committed); copy it into the host's secret manager.
````

#### Section 11: Maintenance and Operations

Document the recurring, post-launch tasks, because an app that ships but can't be operated is a liability. This section answers "the thing is live—now what?"

````markdown
## Maintenance and Operations

### Database Backups

Schedule automated backups and test a restore at least once, because an untested
backup is just a hope:

```bash
# Create a compressed snapshot
pg_dump "$DATABASE_URL" --format=custom --file="backup-$(date +%F).dump"

# Restore into a fresh database
pg_restore --clean --no-owner --dbname="$DATABASE_URL" backup-2026-06-16.dump
```

### Monitoring and Health Checks

- Liveness/readiness endpoint: `GET /up` returns `200` when the app and database
  are reachable. Point your load balancer and uptime monitor at it.
- Background jobs: watch the Solid Queue dashboard at `/jobs` for a growing
  backlog, which signals workers are down or under-provisioned.

### Routine Upgrades

```bash
# Update Ruby gems within their version constraints
bundle update --conservative

# Update JavaScript dependencies
pnpm update

# Re-run the full test suite before shipping any upgrade
bin/rails test && pnpm test
```
````

### Step 5: Final Checklist

Run through this before declaring the README done:

- [ ] Title and overview make the project's purpose clear in under ten seconds.
- [ ] Tech stack lists versions, not just names.
- [ ] Prerequisites include every system dependency, including native ones.
- [ ] Getting Started runs cleanly on a fresh machine, in order, with no gaps.
- [ ] Architecture explains both structure and intent, with typed boundaries shown.
- [ ] Every environment variable the code reads is documented and categorized.
- [ ] Scripts reflect the team's real workflow (`bin/` wrappers where they exist).
- [ ] Testing covers how to run *and* how to write tests, including edge cases.
- [ ] Deployment matches the detected platform and includes rollback/recovery.
- [ ] Troubleshooting captures the failures people actually hit.
- [ ] No placeholder shorthand (ellipses, stub markers, or "rest unchanged" notes) remains anywhere in the file.

## Pitfalls

- **Inventing instead of observing.** Documentation that is invented rather than observed is worse than no documentation, because it actively misleads. Every command and value should be verified against the actual repo. A confidently wrong instruction is worse than an honest "unconfirmed—verify with the team" note.
- **Skipping the exploration phase.** Writing a README without first reading the codebase produces a generic document that doesn't match the real project. Always explore first.
- **Missing native dependencies.** Gems like `pg`, `nokogiri`, or `sharp` require system libraries. If you don't call these out in Prerequisites, the first `bundle install` or `pnpm install` will fail on a fresh machine.
- **Version-less tech stack.** A version-less stack forces the reader to dig through lockfiles. Always include versions from the manifest or lockfile.
- **Placeholder shorthand left in output.** Every ellipsis, stub marker, or "rest unchanged" shorthand must be replaced with the real content. A placeholder is an unfinished promise that the reader has to fulfill themselves.
- **Over-documenting per-function detail.** A README that drowns in per-function detail stops being a map and becomes a maze. Keep the README at the system level; use inline comments or API doc tools for code-level documentation.
- **Windows path/command differences.** If the project is developed on a Windows host (PowerShell), commands like `cp` become `Copy-Item`, and `bin/` scripts may need `ruby` prefix. Always verify and include PowerShell equivalents where they differ.
- **Baking secrets into Docker images.** Pass secrets as environment variables at runtime, never bake them into the image. A leaked image with baked secrets is a security incident.
- **Deploying code before migrations.** In production, the running process must never see a schema it doesn't have code for. Always migrate before restarting, and precompile assets before migrating.

## Verification

After generating the README, verify it against these checks:

1. **Structure completeness** — Confirm all 11 sections are present and in order:
   ```bash
   grep -c "^## " README.md
   ```
   Expected: at least 11 top-level sections (Title/Overview, Tech Stack, Prerequisites, Getting Started, Architecture, Environment Variables, Available Scripts, Testing, Deployment, Troubleshooting, Maintenance).

2. **No placeholders remain** — Search for common placeholder patterns:
   ```bash
   grep -nE "\.\.\.|TODO|FIXME|TBD|rest unchanged|stub" README.md
   ```
   Expected: no matches (or only matches inside legitimate code examples that use `...` as valid syntax).

3. **Versions are present** — Confirm the tech stack includes version numbers:
   ```bash
   grep -E "[0-9]+\.[0-9]+" README.md | grep -i "tech stack" -A 20
   ```

4. **Getting Started is runnable** — Every code block in Getting Started should be a valid shell command. Mentally (or actually) run them in order on a fresh machine.

5. **Environment variables match the code** — Cross-reference documented env vars against what the code actually reads:
   ```bash
   grep -rohE "ENV\[[A-Z_]+\]|ENV\.fetch\([\"'][A-Z_]+[\"']" app/ config/ lib/ | sort -u
   ```
   Every variable found here should appear in the Environment Variables section.

6. **Deployment matches detected platform** — Confirm the deployment section matches the platform config file found in the repo (e.g., if `fly.toml` exists, the Fly.io section should be present and accurate).

## Principles

When a situation isn't covered by a specific instruction above, reason from these:

- **Observed, not invented.** Every command and value should be verified against the actual repo.
- **Runnable top-to-bottom.** A new contributor should be able to copy the Getting Started block line by line and end up with a running app.
- **Explain the why, not just the what.** Anyone can read the code to see *what* happens. The README's unique value is recording *why*—the constraints, trade-offs, and intentions that the code can't express.
- **Complete over clever.** Prefer a slightly long, fully spelled-out instruction to a terse one with hidden assumptions. The reader's time matters more than the author's keystrokes.
- **No placeholders in the final output.** Every ellipsis, stub marker, or "rest unchanged" shorthand must be replaced with the real content.
