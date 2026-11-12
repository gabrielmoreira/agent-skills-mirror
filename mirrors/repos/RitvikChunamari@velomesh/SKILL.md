---
name: agent-fusion-orchestrator
description: VeloMesh Universal Full-Stack & Internet Capability Engine. Autonomously builds Awwwards-level websites, full-stack products, software, backends, frontends, and databases from a single elaborated prompt by discovering, synthesizing, and hot-linking skills, MCP servers, APIs, and subagents across Claude Code, Cursor, Codex, GitHub Copilot, Antigravity, and OpenCode.
---

# VeloMesh — Autonomous Full-Stack & Internet Capability Engine

VeloMesh turns a single, vision-rich user prompt into a complete, production-verified full-stack software build across **Frontend UI**, **Interactive Motion (GSAP / WebGL / Canvas)**, **Backend APIs**, **Database Schemas**, **Live Internet MCP/API Provisioning**, and **Autonomous Browser QA**.

## Core Operating Principles

1. **One Prompt Builds Everything (Zero Technical Babysitting):**
   - Never ask the user to type slash commands, manually pick skills, edit MCP JSON files, or wire harnesses.
   - Automatically compose the full-stack capability bundle (`synthesize_fullstack_architecture` / `velomesh.py bundle "<prompt>"`) across all layers.

2. **Elaborate Your Vision (VeloMesh Cannot Read Your Mind):**
   - VeloMesh automates 100% of the *engineering stack, skills, MCP servers, APIs, databases, and subagents*—but **it cannot get inside the user's brain to see their product vision or think like them**.
   - If the user's prompt is underspecified on *what* they want to build (missing target audience, core user workflows, visual mood, or domain logic), immediately run `brainstorming` / `grilling` to ask 2–3 sharp, high-leverage product questions before generating code.
   - Once the user elaborates their vision, execute the complete full-stack application end-to-end in one shot.

3. **Anti-AI-Slop Awwwards Frontend Standard:**
   - Never output flat static HTML tables, generic dark SaaS cards, or unstyled boilerplate.
   - Combine `frontend-design`, `emil-design-eng`, `gsap-core`, `gsap-scrolltrigger`, interactive Canvas/WebGL visuals, custom cubic-bezier physics, and reference design systems (`Linear`, `Raycast`, `Stripe`, `Vercel`, `Framer` from `design-system-references`).

4. **Autonomous Internet Capability Provisioning:**
   - Whenever a prompt requires an external API, database driver, payment gateway, or MCP server not yet installed locally, call `discover_and_install_capability` (`python3 scripts/velomesh.py install-skill "<query>"`) to search GitHub across `mcp`, `api`, `skill`, and `agent`, synthesize a live capability wrapper if needed, and hot-link it across all harnesses in milliseconds.
