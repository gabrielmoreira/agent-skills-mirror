# Project Specs — Platform, Environment & Frameworks

> **AI reads this file at the start of every session.**
> In this template repository, this file starts as a template field sheet. During adoption, `/ai-onboard` should fill what it can and ask you to confirm/edit inferred values.
> Fill it in once at project setup. Check boxes with `[x]`. Fill freeform fields where marked.
> This prevents the AI from guessing your platform and making wrong assumptions about paths, shells, line endings, package managers, and tooling.

---

## Example Filled Profile (reference only)

> Keep this example as guidance. Fill the checklist template in the sections that follow with your own project values.

**Project Name:** Example SaaS API + Dashboard  
**Repo Shape:** Monorepo (API + web app + shared package)  
**Team Size:** 4 developers

| Category | Example Value |
|---|---|
| Development Platform | macOS 14 + WSL2 Ubuntu; VS Code |
| Target Platform | Dockerized Node.js services on Linux cloud VMs |
| Language & Runtime | TypeScript 5.6, Node.js 20 LTS |
| Frontend | React + Vite + Tailwind CSS |
| Backend | Fastify |
| Database | PostgreSQL + Redis |
| Package Manager | pnpm |
| Infrastructure | Docker Compose locally, GitHub Actions CI, AWS hosting |
| Testing | Vitest (unit), Playwright (E2E) |
| Architecture Pattern | Modular monolith in a monorepo |
| Notes | Prefer POSIX-style paths in docs/commands; avoid PowerShell-only snippets unless marked |

---

## Contents

| Section | What's here |
|---|-------------|
| [Development Platform](#development-platform) | Where you write code |
| [Target Platform](#target-platform) | Where the code runs |
| [Language & Runtime](#language--runtime) | Primary languages and versions |
| [Frameworks & Libraries](#frameworks--libraries) | Frontend, backend, database |
| [Package Manager](#package-manager) | Dependency management tooling |
| [Infrastructure & DevOps](#infrastructure--devops) | Containers, CI/CD, cloud |
| [Testing](#testing) | Test frameworks and strategy |
| [Architecture Pattern](#architecture-pattern) | Repo and system structure |
| [Notes](#notes) | Anything else the AI should know |

---

## Development Platform

### Developer OS

- [ ] Windows (version: _______)
- [ ] macOS (version: _______)
- [ ] Linux (distro/version: _______)
- [ ] WSL2 on Windows (Linux distro inside Windows — paths behave like Linux, but host is Windows)

### Shell / Terminal

- [ ] PowerShell (Windows native)
- [ ] Command Prompt (`cmd.exe`)
- [ ] Bash
- [ ] Zsh
- [ ] Fish
- [ ] WSL2 shell (Bash/Zsh inside WSL2)

### Editor / IDE

- [ ] VS Code
- [ ] Cursor
- [ ] JetBrains (specify: _______)
- [ ] Neovim / Vim
- [ ] Other: _______

---

## Target Platform

### Deployment / Runtime Target

- [ ] Windows desktop application
- [ ] Windows service / background process
- [ ] macOS desktop application
- [ ] Linux server / cloud VM
- [ ] Web browser (frontend SPA / PWA)
- [ ] Node.js server process
- [ ] Mobile — iOS
- [ ] Mobile — Android
- [ ] Embedded / bare-metal (architecture: _______)
- [ ] RTOS (specify: _______)
- [ ] Docker container
- [ ] Serverless / edge function (platform: _______)
- [ ] Cross-platform (check all that apply above)

### Path & Line Ending Convention

> The AI uses this to write correct paths and avoid cross-platform pitfalls.

- [ ] Windows paths (`C:\Users\...`, backslash separators)
- [ ] POSIX paths (`/home/...`, forward-slash separators)
- [ ] Mixed (dev is Windows; target is Linux/container)

---

## Language & Runtime

- [ ] TypeScript (version: _______)
- [ ] JavaScript (Node.js version: _______)
- [ ] Python (version: _______)
- [ ] Rust (edition: _______)
- [ ] C (standard: _______)
- [ ] C++ (standard: _______)
- [ ] C# / .NET (version: _______)
- [ ] Go (version: _______)
- [ ] Java (version: _______)
- [ ] Kotlin
- [ ] Swift
- [ ] Other: _______

---

## Frameworks & Libraries

### Frontend

- [ ] React
- [ ] Vue 3
- [ ] Angular
- [ ] Svelte / SvelteKit
- [ ] Next.js
- [ ] Vite (bundler)
- [ ] Webpack (bundler)
- [ ] Tailwind CSS
- [ ] None / Vanilla JS
- [ ] Not applicable (no frontend)

### Backend

- [ ] Express
- [ ] Fastify
- [ ] NestJS
- [ ] Django
- [ ] FastAPI
- [ ] Flask
- [ ] ASP.NET Core
- [ ] Axum (Rust)
- [ ] Actix-web (Rust)
- [ ] None (embedded / CLI / desktop / frontend-only)

### Database

- [ ] PostgreSQL
- [ ] MySQL / MariaDB
- [ ] SQLite
- [ ] MongoDB
- [ ] Redis
- [ ] DynamoDB
- [ ] None

### ORM / Query Layer

- [ ] TypeORM
- [ ] Prisma
- [ ] Drizzle
- [ ] SQLAlchemy
- [ ] Entity Framework (EF Core)
- [ ] None / raw SQL

---

## Package Manager

- [ ] npm
- [ ] pnpm
- [ ] yarn
- [ ] pip
- [ ] uv (Python)
- [ ] cargo (Rust)
- [ ] NuGet (.NET)
- [ ] Other: _______

---

## Infrastructure & DevOps

### Containerization

- [ ] Docker
- [ ] Docker Compose
- [ ] Kubernetes
- [ ] None

### CI/CD

- [ ] GitHub Actions
- [ ] GitLab CI
- [ ] Azure DevOps / Pipelines
- [ ] Jenkins
- [ ] Other: _______
- [ ] None

### Cloud / Hosting

- [ ] AWS
- [ ] Azure
- [ ] GCP
- [ ] Railway
- [ ] Render
- [ ] Fly.io
- [ ] Vercel / Netlify (frontend)
- [ ] Self-hosted / on-prem
- [ ] None / local only

---

## Testing

- [ ] Jest
- [ ] Vitest
- [ ] Playwright (E2E)
- [ ] Cypress (E2E)
- [ ] pytest
- [ ] xUnit / NUnit (C#)
- [ ] Unity Test Framework (C/C++ embedded)
- [ ] Catch2 / GoogleTest (C/C++)
- [ ] Rust built-in (`cargo test`)
- [ ] Other: _______
- [ ] No automated tests (yet)

---

## Architecture Pattern

### Repository Structure

- [ ] Monorepo (all modules in one repo)
- [ ] Multi-repo (separate repos per module/service)
- [ ] Polyrepo (hybrid)

### System Architecture

- [ ] Monolith
- [ ] Microservices
- [ ] Modular monolith
- [ ] CLI tool / library
- [ ] Firmware / embedded system
- [ ] Desktop application
- [ ] Browser extension

---

## Notes

> Add anything the AI should know that doesn't fit above.
> Examples: unusual constraints, legacy system integrations, hardware specifics, team size, non-standard tooling, regulatory requirements.

_(none yet)_
