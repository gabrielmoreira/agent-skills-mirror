---
name: generate-prompt-request
description: This skill should be used to generate a "prompt request" one-pager that summarizes the current session for a pull request. It produces one consolidated User block folding together every ask and decision from the session, plus one Assistant block summarizing what was built. Use it when the user asks to "generate a prompt request", recap or summarize the session for a PR, or capture what was requested. Also use it automatically when opening a pull request or writing a PR description, so the PR body includes the asks and decisions behind the change. Works on the current session only and outputs inline markdown ready to paste into a PR.
---

# Generate Prompt Request

## Overview

Turn the current working session into a compact "prompt request" one-pager for a pull request:
a single `User:` block that folds together every ask and every decision made during the session,
followed by a single `Assistant:` block summarizing what was actually built or done. It is a
one-pager a reviewer can read at a glance, not a turn-by-turn transcript.

## When to use

- The user asks to "generate a prompt request", recap the session for a PR, or capture what was requested.
- Automatically while opening a pull request or writing a PR description. Generate this and include
  it in the PR body so reviewers see the asks and decisions behind the change. A repo's AGENTS.md or
  CLAUDE.md can wire this in with one line, for example: "When opening a PR, invoke the
  generate-prompt-request skill and include its output in the PR body."

## Output format

Render the result INLINE in the reply. Do not write a file. Produce exactly this shape:

```
# <Session topic> — Prompt Request

**User:**
> <one consolidated request: all the asks first, then "Decisions made along the way: ..."
> folding in every choice the user made or approved>

**Assistant:**
> <a short summary of what was actually built or done, plus status>
```

## How to build it

1. Re-read the whole current session, from the first user message to now.
2. Collect every distinct ask or requirement, and every decision the user made or approved,
   including ones that emerged mid-session (a stack choice, a "keep it simple" constraint, a
   dropped feature).
3. Write ONE `User:` block: a single natural request that compresses all of it. Lead with what
   they wanted, then end with "Decisions made along the way: ..." listing the resolved choices inline.
4. Write ONE `Assistant:` block: a tight summary of what was delivered (what got built, its key
   properties, and status). Two to four sentences.
5. Title: derive it from the session's main deliverable (for example "White-Label Template — Prompt Request").

## Rules

- Current session only. Never invent an ask, decision, or outcome that did not happen in this
  session. If something is uncertain, leave it out.
- Compress hard. One short paragraph per block. No multi-turn transcript, no separate Summary or
  Gotchas sections.
- Use bold `User:` / `Assistant:` labels with the content in a blockquote.
- No em dashes or en dashes in the prose. Use periods, commas, or rephrase.
- When invoked during PR generation, output only the block so it can be pasted straight into the PR body.

## Example

A real one-pager from a session that designed a white-label template app:

```
# White-Label Template — Prompt Request

**User:**
> I want a white-label, open-source GitHub template built on our existing B2B Agents API
> (`/v1`), a bare-bones version of our B2C dashboard that people fork and rebrand. It needs
> workspaces per user (members + shareable invite links) and the basics the API supports:
> instance lifecycle (create / list / start / stop / restart / update / resize / delete),
> budget + usage, and opening each agent's own UIs (dashboard / terminal / files) via signed
> URLs. No Stripe. Decisions made along the way: one server-side `sk_live_` key with logical
> app-level workspaces (there is no API to mint per-tenant Agent37 keys, so tenancy is enforced
> in our own layer); no in-app chat, just open the agent's real UIs in a new tab; stack is
> Next.js + Supabase (magic-link auth, Postgres, RLS); and keep it simple, no Docker (setup
> provisions a hosted Supabase project for you).

**Assistant:**
> Built it as a standalone Next.js 15 repo wrapping `/v1`: Supabase magic-link auth, logical
> workspaces with admin/viewer roles and invite links, the full instance lifecycle plus
> budget/usage, signed-url "open" actions, and a template list, backed by a Supabase `instances`
> mirror refreshed from `/v1`. Isolation is RLS plus server-side role checks, the `sk_live_` key
> stays server-side, branding is env-only, and there is no Stripe. Setup provisions a hosted
> Supabase project via an access token (no Docker); typecheck and build pass. Not pushed, the
> adopter creates the GitHub repo.
```
